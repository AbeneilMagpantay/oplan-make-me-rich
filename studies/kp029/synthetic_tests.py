"""KP-029 premise study, stage 1: SYNTHETIC tests of the study's look-ahead guards (no real data, no network).

    .venv\\Scripts\\python.exe -I studies\\kp029\\synthetic_tests.py

A synthetic universe of 15 perpetuals (BTCUSDT among them, one 1000-prefixed) with synthetic spot rows, built with
the kernel's own test constructor (omr.upipeline.udata_from_tables), scored by the study's real path
(kp029_features, kp029_eval, run_study, the real study programs). Each test prints PASS or FAIL; the exit code is
the number of failures.

  1 ceiling        no spot month after 2022-06 (or before 2019-12) can be named; rows after 2022-06-30 23:00 are
                   dropped on load; a stored file of a later month stops the loader; a checksum mismatch stops it
  2 csv            millisecond and microsecond open times, header skip, off-hour and duplicate rows refused
  3 symbols        1000XXXUSDT -> XXXUSDT with price x1000 (and 1000000), others unchanged
  4 slots          a missing spot hour is NaN (unknown), never 0; the 50% price guard (ruling 6); S3 on spot
  5 isolation      the injection changes only the two slot columns; a perpetual-only program is bit-identical
  6 future rows    changing every perpetual and spot row after a cut T never changes a weight, raw value or known
                   flag at or before T (three cuts), while it does change rows after T
  7 truncation     the study's truncation test (kp029_eval.truncation_test) passes on the honest path and FAILS on
                   a deliberate one-hour look-ahead (so it can fail)
  8 missing hour   one missing spot hour (not an outage) makes that coin unknown (weight 0) in exactly the weekly
                   decisions whose windows hold it, the others stay known; the same hour with ZERO volume keeps it known
  9 guard          a spot close 60% away from the perpetual's makes the hour unknown like a missing one; 40% is kept
 10 pipeline       the kernel's stage 1 and every reading of kp029_eval run on a study program, and run_study's
                   evaluate-and-log appends one row (to a temporary log) with the file hashes
 11 outages        ruling 5: a 3-hour market-wide outage gives zero, known slots and loses no weekly decision; a
                   30-hour outage is unknown from its 25th hour; a pair stopped long before an outage stays unknown;
                   BTCUSDT itself at an outage hour; the truncation test passes with cuts inside and after outages
 12 coverage       run_study --coverage: outage hours, blocks and share; each tripwire (block > 24 h, guard rejects
                   on more than 5 pairs) sets the stop flag; the runner refuses on the flag and at the cap of 14
"""
from __future__ import annotations

import io
import json
import sys
import tempfile
import traceback
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
for p in (str(ROOT), str(HERE)):
    if p not in sys.path:
        sys.path.insert(0, p)

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from omr import constants as C  # noqa: E402
from omr import datasets as D  # noqa: E402
from omr import lang as L  # noqa: E402
from omr import probe  # noqa: E402
from omr import upipeline as UP  # noqa: E402

import kp029_eval as EV  # noqa: E402
import kp029_features as F  # noqa: E402
import kp029_spot as SP  # noqa: E402

PROGS = HERE / "programs"
HS1 = "kp029_hs1_share_shift"
END = C.DEV_END
RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond), detail))
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")


# ---------------------------------------------------------------- synthetic data
def synth_perp(start, end, seed, price0, scale):
    rng = np.random.default_rng(seed)
    idx = pd.date_range(pd.Timestamp(start, tz="UTC"), pd.Timestamp(end, tz="UTC"), freq="h").as_unit("ns")
    n = len(idx)
    lr = 0.012 * rng.standard_normal(n)
    close = price0 * np.exp(np.cumsum(lr))
    opn = np.r_[price0, close[:-1]]
    spread = np.abs(0.01 * rng.standard_normal(n)) * close
    vol_regime = np.exp(np.cumsum(0.02 * rng.standard_normal(n)) * 0.3)
    qv = scale * vol_regime * rng.uniform(500, 1500, n)
    kl = pd.DataFrame({"open": opn, "high": np.maximum(opn, close) + spread, "low": np.minimum(opn, close) - spread,
                       "close": close, "volume": qv / close, "quote_volume": qv,
                       "trades": rng.integers(50, 500, n).astype(float), "taker_buy_volume": 0.5 * qv / close,
                       "taker_buy_quote_volume": qv * rng.uniform(0.35, 0.65, n),
                       "is_gap": np.zeros(n, dtype=bool)}, index=idx)
    kl.index.name = "open_time"
    m = 1.0 + 0.0005 * rng.standard_normal(n)
    mo, mc = opn * m, close * m
    mk = pd.DataFrame({"open": mo, "high": np.maximum(mo, mc) + spread * 0.9, "low": np.minimum(mo, mc) - spread * 0.9,
                       "close": mc, "samples": 3600.0}, index=idx)
    mk.index.name = "open_time"
    ft = idx[idx.hour % 8 == 0]
    fu = pd.DataFrame({"rate": 0.0001 + 0.0001 * rng.standard_normal(len(ft)), "interval_hours": 8.0,
                       "offset_ms": 0.0}, index=ft)
    fu.index.name = "settle_time"
    return {"klines": kl, "funding": fu, "mark_klines": mk, "index_klines": probe.index_bars(kl)}


def synth_spot_of(kl, seed, mult):
    rng = np.random.default_rng(seed)
    n = len(kl)
    qv = kl["quote_volume"].to_numpy() * np.exp(np.cumsum(0.03 * rng.standard_normal(n)) * 0.2) * rng.uniform(0.5, 2, n)
    return pd.DataFrame({"close": kl["close"].to_numpy() / mult * (1 + 0.001 * rng.standard_normal(n)),
                         "quote_volume": qv, "trades": rng.integers(20, 300, n).astype(float),
                         "taker_buy_quote_volume": qv * rng.uniform(0.3, 0.7, n)}, index=kl.index.copy())


NAMES = ["BTCUSDT"] + [f"S{i:02d}USDT" for i in range(1, 14)] + ["1000ABCUSDT"]   # BTCUSDT: the outage reference


def world(seed=3, end=END, perturb_after=None, spot_override=None):
    """(kernel-like UData, spot tables {spot pair: rows}). perturb_after: every perpetual and spot row after it
    is changed (prices, volumes, funding)."""
    rng = np.random.default_rng(seed)
    tables, table, spot = {}, {"symbols": {}}, {}
    t0 = pd.Timestamp("2019-08-01 00:00", tz="UTC")
    for i, s in enumerate(NAMES):
        start = str(t0 + pd.Timedelta(days=3 * i))[:16]
        raw = synth_perp(start, end, seed * 100 + i, float(np.exp(rng.normal(3, 1))), float(np.exp(rng.normal(0, 1))))
        sname, mult = SP.spot_symbol(s)
        sp = synth_spot_of(raw["klines"], seed * 1000 + i, mult)
        if perturb_after is not None:
            cut = pd.Timestamp(perturb_after, tz="UTC")
            prng = np.random.default_rng(seed * 7 + i)
            kl = raw["klines"].copy()
            m = kl.index > cut
            f = np.exp(np.cumsum(0.05 * prng.standard_normal(int(m.sum()))))
            for c in ("open", "high", "low", "close"):
                kl.loc[m, c] = kl.loc[m, c].to_numpy() * f
            kl.loc[m, "quote_volume"] = kl.loc[m, "quote_volume"].to_numpy() * prng.uniform(0.2, 5, int(m.sum()))
            raw["klines"] = kl
            fu = raw["funding"].copy()
            fm = fu.index > cut
            fu.loc[fm, "rate"] = fu.loc[fm, "rate"].to_numpy() + 0.001 * prng.standard_normal(int(fm.sum()))
            raw["funding"] = fu
            raw["index_klines"] = probe.index_bars(kl)
            sm = sp.index > cut
            sp = sp.copy()
            sp.loc[sm, "quote_volume"] = sp.loc[sm, "quote_volume"].to_numpy() * prng.uniform(0.1, 10, int(sm.sum()))
            sp.loc[sm, "taker_buy_quote_volume"] = sp.loc[sm, "quote_volume"].to_numpy() * prng.uniform(0, 1, int(sm.sum()))
            sp.loc[sm, "close"] = kl.loc[sp.index[sm], "close"].to_numpy() / mult * prng.uniform(0.9, 1.1, int(sm.sum()))
        tables[s] = raw
        spot[sname] = sp
        table["symbols"][s] = {"class": "crypto_perpetual", "until": None, "n_months": 1}
    if spot_override:
        spot.update(spot_override)
    btc = D.assemble_frame(synth_perp("2019-08-01 00:00", end, seed + 99, 9000.0, 30.0), D.PROGRAM_EXTRA)
    return UP.udata_from_tables(tables, btc, end, symbols_table=table), spot


def program(stem):
    return L.parse_file(PROGS / f"{stem}.omr")


def unit_of(prog, ud, spot, **kw):
    sud = F.study_udata(ud, SP.DictSpot(spot), **kw)
    fp = UP.Blocked(sud, "top30", fields=UP.program_fields(prog))
    W, raw, kn = fp.unit(prog, L.default_params(prog))
    return {"grid": fp.grid, "W": W, "raw": raw, "known": kn, "symbols": list(fp.symbols)}


# ---------------------------------------------------------------- tests
def t1_ceiling():
    ok = True
    for y, m in ((2022, 7), (2023, 1), (2025, 6), (2019, 11)):
        try:
            SP.url("BTCUSDT", y, m)
            ok = False
        except SP.CeilingError:
            pass
    ok &= SP.url("BTCUSDT", 2022, 6).endswith("/BTCUSDT/1h/BTCUSDT-1h-2022-06.zip")
    ok &= SP.url("BTCUSDT", 2019, 12, checksum=True).endswith("BTCUSDT-1h-2019-12.zip.CHECKSUM")
    ok &= SP.months_between((2019, 1), (2030, 1))[0] == (2019, 12) and SP.months_between((2019, 1), (2030, 1))[-1] == (2022, 6)
    ok &= len(SP.months_between((2019, 12), (2022, 6))) == 31
    check("1a ceiling: no month outside 2019-12..2022-06 can be named", ok)
    with tempfile.TemporaryDirectory() as td:
        d = Path(td) / "XUSDT"
        d.mkdir()
        rows = []
        for t in pd.date_range("2022-06-30 20:00", "2022-07-01 03:00", freq="h", tz="UTC"):
            ms = int(t.value // 1_000_000)
            rows.append(f"{ms},1,1,1,1.0,10,{ms + 3599999},100,5,4,40,0")
        csv = ("\n".join(rows) + "\n").encode("ascii")
        _write_zip(d, "XUSDT", 2022, 6, csv)
        st = SP.SpotStore(Path(td))
        df = st.get("XUSDT")
        check("1b ceiling: rows after 2022-06-30 23:00 are dropped on load",
              df is not None and len(df) == 4 and df.index[-1] == SP.ROW_CEILING, f"rows kept {0 if df is None else len(df)}")
        _write_zip(d, "XUSDT", 2022, 7, csv)
        try:
            SP.SpotStore(Path(td)).get("XUSDT")
            check("1c ceiling: a stored file of 2022-07 stops the loader", False)
        except SP.CeilingError:
            check("1c ceiling: a stored file of 2022-07 stops the loader", True)
        (d / "XUSDT-1h-2022-07.zip").unlink()
        (d / "XUSDT-1h-2022-07.zip.CHECKSUM").unlink()
        (d / "XUSDT-1h-2022-06.zip.CHECKSUM").write_text("0" * 64 + "  XUSDT-1h-2022-06.zip\n", encoding="ascii")
        try:
            SP.SpotStore(Path(td)).get("XUSDT")
            check("1d hash at read: a checksum mismatch stops the loader", False)
        except ValueError:
            check("1d hash at read: a checksum mismatch stops the loader", True)


def _write_zip(d, sym, y, m, csv):
    name = SP.zip_name(sym, y, m)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr(name[:-4] + ".csv", csv)
    b = buf.getvalue()
    (d / name).write_bytes(b)
    (d / (name + ".CHECKSUM")).write_text(f"{SP.sha256_bytes(b)}  {name}\n", encoding="ascii")


def t2_csv():
    t = pd.Timestamp("2021-05-01 00:00", tz="UTC")
    ms, us = int(t.value // 1_000_000), int(t.value // 1000)
    a = SP.parse_csv_bytes(f"{ms},1,1,1,2.0,1,0,10,3,1,4,0\n".encode("ascii"))
    b = SP.parse_csv_bytes(f"open_time,o,h,l,c,v,ct,qv,n,tb,tbq,ig\n{us},1,1,1,2.0,1,0,10,3,1,4,0\n".encode("ascii"))
    ok = a.index[0] == t and b.index[0] == t and float(a["quote_volume"].iloc[0]) == 10.0
    bad1 = bad2 = False
    try:
        SP.parse_csv_bytes(f"{ms + 60000},1,1,1,2.0,1,0,10,3,1,4,0\n".encode("ascii"))
    except ValueError:
        bad1 = True
    try:
        SP.parse_csv_bytes(f"{ms},1,1,1,2.0,1,0,10,3,1,4,0\n{ms},1,1,1,2.0,1,0,10,3,1,4,0\n".encode("ascii"))
    except ValueError:
        bad2 = True
    check("2 csv: ms and us open times, header skipped, off-hour and duplicate rows refused", ok and bad1 and bad2)


def t3_symbols():
    ok = (SP.spot_symbol("1000SHIBUSDT") == ("SHIBUSDT", 1000.0) and SP.spot_symbol("1000000MOGUSDT") == ("MOGUSDT", 1e6)
          and SP.spot_symbol("BTCUSDT") == ("BTCUSDT", 1.0) and SP.spot_symbol("1INCHUSDT") == ("1INCHUSDT", 1.0)
          and SP.spot_symbol("1000XECUSDT") == ("XECUSDT", 1000.0))
    check("3 symbol map: 1000-prefixed perpetuals map to the unprefixed spot pair with price x1000", ok)


def t4_slots():
    idx = pd.date_range("2021-01-01 00:00", periods=60, freq="h", tz="UTC").as_unit("ns")
    kl = pd.DataFrame({"close": np.full(60, 100.0)}, index=idx)
    sp = pd.DataFrame({"close": np.full(60, 100.0), "quote_volume": np.arange(60, dtype=float) + 1.0,
                       "trades": np.full(60, 5.0), "taker_buy_quote_volume": np.full(60, 0.5)}, index=idx)
    sp_m = sp.drop(idx[10])
    c = F.slot_columns(kl, sp_m, 1.0)
    ok_missing = np.isnan(c["volume"][10]) and np.isnan(c["taker_buy_volume"][10]) and c["volume"][11] == 12.0
    sp_g = sp.copy()
    sp_g.loc[idx[20], "close"] = 151.0                    # ratio 1.51: unknown
    sp_g.loc[idx[21], "close"] = 149.0                    # ratio 1.49: kept
    sp_g.loc[idx[22], "close"] = 49.0                     # ratio 0.49: unknown
    sp_g.loc[idx[23], "close"] = 51.0                     # ratio 0.51: kept
    c = F.slot_columns(kl, sp_g, 1.0)
    ok_guard = (np.isnan(c["volume"][20]) and c["volume"][21] == 22.0 and np.isnan(c["volume"][22])
                and c["volume"][23] == 24.0 and F.GUARD_TOL == 0.50)
    sp_z = sp.copy()
    sp_z.loc[idx[30:55], ["trades", "quote_volume", "taker_buy_quote_volume"]] = 0.0     # 25 zero-trade hours
    c = F.slot_columns(kl, sp_z, 1.0)
    ok_s3 = (c["volume"][30] == 0.0 and c["volume"][53] == 0.0 and np.isnan(c["volume"][54])
             and c["volume"][55] == 56.0)
    kl1000 = pd.DataFrame({"close": np.full(60, 100.0)}, index=idx)
    sp1000 = sp.copy()
    sp1000["close"] = 0.1
    c1 = F.slot_columns(kl1000, sp1000, 1000.0)
    c0 = F.slot_columns(kl1000, sp1000, 1.0)
    ok_mult = c1["volume"][5] == 6.0 and np.isnan(c0["volume"][5])
    check("4a slots: a missing spot hour is NaN (unknown), never 0", ok_missing)
    check("4b slots: price guard 50% (ratios 1.51 and 0.49 unknown, 1.49 and 0.51 kept)", ok_guard)
    check("4c slots: S3 zero-trade rule (24 zero-trade hours usable as real zeros, the 25th unknown)", ok_s3)
    check("4d slots: the 1000-prefix multiplier enters the guard only; volumes unscaled", ok_mult)


def t5_isolation(ud, spot):
    s = NAMES[3]
    t = ud.tables(s)
    t2 = F.inject(t, s, SP.DictSpot(spot))
    kl, kl2 = t["klines"], t2["klines"]
    same_other = all(kl[c].equals(kl2[c]) for c in kl.columns if c not in F.SLOTS)
    changed = [c for c in kl2.columns if c in F.SLOTS]
    same_tables = all(t2[d] is t[d] for d in ("funding", "mark_klines", "index_klines"))
    check("5a isolation: only the two slot columns change; other tables untouched",
          same_other and sorted(changed) == sorted(F.SLOTS) and same_tables)
    prog = L.parse_file(ROOT / "strategies" / "gen003_w01_high_anchor.omr")
    params = L.default_params(prog)
    fpk = UP.Blocked(ud, "top30", fields=UP.program_fields(prog))
    Wk, _, kk = fpk.unit(prog, params)
    fps = UP.Blocked(F.study_udata(ud, SP.DictSpot(spot)), "top30", fields=UP.program_fields(prog))
    Ws, _, ks = fps.unit(prog, params)
    s0, e0 = fpk.pos("2020-06-01 00:00"), fpk.pos(C.DEV_END)
    rk, rs = fpk.run(Wk, s0, e0), fps.run(Ws, s0, e0)
    check("5b isolation: a perpetual-only program's weights and engine run are bit-identical through the wrapper",
          np.array_equal(Wk, Ws) and np.array_equal(kk, ks) and np.array_equal(rk.equity, rs.equity)
          and np.abs(Wk).sum() > 0)


def t6_future_rows(ud, spot, prog):
    base = unit_of(prog, ud, spot)
    grid = base["grid"]
    for cut in ("2020-09-06 23:00", "2021-03-17 05:00", "2021-11-28 22:00"):
        udp, spp = world(perturb_after=cut)
        mod = unit_of(prog, udp, spp)
        c = int(grid.get_loc(pd.Timestamp(cut, tz="UTC")))
        same = (np.array_equal(base["W"][:c + 1], mod["W"][:c + 1]) and np.array_equal(base["known"][:c + 1], mod["known"][:c + 1])
                and np.array_equal(base["raw"][:c + 1], mod["raw"][:c + 1], equal_nan=True))
        later = not np.array_equal(base["W"][c + 1:], mod["W"][c + 1:])
        live = int(base["known"][:c + 1].any(axis=1).sum())
        check(f"6 future rows: rows after {cut} changed -> rows at or before it identical", same and later and live > 0,
              f"known rows before the cut {live}; later rows changed {later}")


def t7_truncation(ud, spot, prog):
    params = L.default_params(prog)
    sp = SP.DictSpot(spot)
    base = unit_of(prog, ud, spot)
    grid = base["grid"]
    cuts = EV.truncation_cuts(grid, np.random.default_rng(1))
    r = EV.truncation_test(prog, params, ud, sp, base, cuts)
    check("7a truncation test passes on the honest path", r["pass"], f"{len(r['cuts'])} cuts")
    leak = unit_of(prog, ud, spot, shift_hours=1)
    c = int(grid.get_loc(pd.Timestamp("2021-04-11 23:00", tz="UTC")))
    r2 = EV.truncation_test(prog, params, ud, sp, leak, [c], shift_hours=1)
    check("7b truncation test FAILS on a deliberate one-hour look-ahead (it can fail)", not r2["pass"], str(r2["cuts"]))


def _first_decision_after(grid, t):
    i = int(grid.get_loc(pd.Timestamp(t, tz="UTC")))
    while not (grid[i].day_of_week == 6 and grid[i].hour == 23):
        i += 1
    return i


def t8_missing_hour(ud, spot, prog):
    A = NAMES[5]
    h = pd.Timestamp("2021-03-10 12:00", tz="UTC")
    base = unit_of(prog, ud, spot)
    j = base["symbols"].index(A)
    sp_m = dict(spot)
    sp_m[A] = spot[A].drop(h)
    miss = unit_of(prog, ud, sp_m)
    sp_z = dict(spot)
    z = spot[A].copy()
    z.loc[h, ["quote_volume", "taker_buy_quote_volume", "trades"]] = 0.0
    sp_z[A] = z
    zero = unit_of(prog, ud, sp_z)
    grid = base["grid"]
    # H-S1 at its defaults (k 7, n 28): the daily bin of 2021-03-10 is unknown; sma(qs, 7) is unknown on days
    # 03-10 .. 03-16; lag(sma(qs, 28), 7) needs sma(qs, 28) known on all of days t-7 .. t (LANGUAGE.md 6: the window
    # of lag(x, n) is rows t-n .. t), so x is unknown on days 03-10 .. 04-13; a weekly tf_last bin needs x known on
    # every hour of the bin, whose first hours still hold the previous Sunday's daily value. So the six weekly
    # decisions 03-14 .. 04-18 lose the coin and 04-25 has it back.
    d1 = _first_decision_after(grid, "2021-03-10 13:00")      # 2021-03-14 23:00: the window holds h
    d_last = int(grid.get_loc(pd.Timestamp("2021-04-18 23:00", tz="UTC")))   # the sixth and last decision without it
    d_back = int(grid.get_loc(pd.Timestamp("2021-04-25 23:00", tz="UTC")))   # every window clear of h again
    d0 = int(grid.get_loc(pd.Timestamp("2021-03-07 23:00", tz="UTC")))       # before h
    lost = [str(grid[i]) for i in range(d0, d_back + 1) if grid[i].day_of_week == 6 and grid[i].hour == 23
            and base["known"][i, j] and not miss["known"][i, j]]
    others = [k for k in range(len(base["symbols"])) if k != j]
    ok = (base["known"][d1, j] and not miss["known"][d1, j] and miss["W"][d1, j] == 0.0
          and not miss["known"][d_last, j] and miss["known"][d_back, j] and miss["known"][d0, j]
          and miss["W"][d0, j] == base["W"][d0, j] and int(miss["known"][d1, others].sum()) >= 10 and len(lost) == 6)
    check("8a missing spot hour: the coin is unknown (weight 0) in exactly the six weekly decisions whose inputs hold "
          "the hour, known before and after, the others stay known", ok,
          f"known at d1 base/missing {bool(base['known'][d1, j])}/{bool(miss['known'][d1, j])}; at d_last missing "
          f"{bool(miss['known'][d_last, j])}; at d_back missing {bool(miss['known'][d_back, j])}; decisions lost "
          f"{len(lost)}: {lost[0] if lost else None} .. {lost[-1] if lost else None}; others known "
          f"{int(miss['known'][d1, others].sum())}")
    ok_z = zero["known"][d1, j] and zero["W"][d1, j] != 0.0
    check("8b the same hour with ZERO spot volume keeps the coin known (missing is not zero)", ok_z)


def t9_guard(ud, spot, prog):
    A = NAMES[6]
    h = pd.Timestamp("2021-06-16 08:00", tz="UTC")
    base = unit_of(prog, ud, spot)
    j = base["symbols"].index(A)
    pc = float(ud.tables(A)["klines"].loc[h, "close"])                      # multiplier 1 for S06USDT
    g = spot[A].copy()
    g.loc[h, "close"] = pc * 1.6
    k = spot[A].copy()
    k.loc[h, "close"] = pc * 1.4
    gd = unit_of(prog, ud, dict(spot, **{A: g}))
    kp = unit_of(prog, ud, dict(spot, **{A: k}))
    d1 = _first_decision_after(base["grid"], "2021-06-16 09:00")
    check("9 guard: a spot close 60% from the perpetual's makes the coin unknown like a missing hour; 40% is kept",
          base["known"][d1, j] and not gd["known"][d1, j] and gd["W"][d1, j] == 0.0 and kp["known"][d1, j])


def t10_pipeline(ud, spot):
    import run_study as RS
    sp = SP.DictSpot(spot)
    with tempfile.TemporaryDirectory() as td:
        log = Path(td) / "run_log.jsonl"
        row = RS.evaluate_and_log(HS1, "default", ud, sp, log, stage1_cuts=3, check_memory=False, synthetic=True)
        rows = [json.loads(x) for x in log.read_text(encoding="ascii").splitlines() if x.strip()]
    r = row.get("readings") or {}
    ok = (len(rows) == 1 and row["status"] == "ok" and row["truncation_test"]["pass"] and row["stage1"]["ok"]
          and isinstance(r.get("dev_sharpe"), float) and r.get("next30_code") == "no_unit"
          and "W1" in row["screen"]["items"] and all(v for v in row["study_hashes"].values() if v is not None)
          and isinstance(r.get("spot_known_share_inplay"), float) and row["guard_tol"] == 0.5)
    check("10 pipeline: kernel stage 1 + every reading + the screen + one logged row with file hashes", ok,
          f"status {row.get('status')} stage1 {row.get('stage1')} dev {r.get('dev_sharpe')} next30 {r.get('next30_code')} "
          f"spot known {r.get('spot_known_share_inplay')}")


def drop_hours(spot, start, n, pairs=None):
    """A copy of the spot tables with n hours from `start` removed from the given pairs (all by default)."""
    hrs = pd.date_range(pd.Timestamp(start, tz="UTC"), periods=n, freq="h").as_unit("ns")
    return {k: (v.drop(hrs, errors="ignore") if pairs is None or k in pairs else v) for k, v in spot.items()}


def slots_of(ud, spot, perp, cut=None):
    kl = F.inject(ud.tables(perp), perp, SP.DictSpot(spot), cut=cut)["klines"]
    return kl["volume"], kl["taker_buy_volume"]


def t11_outages(ud, spot, prog):
    params = L.default_params(prog)
    base = unit_of(prog, ud, spot)
    grid = base["grid"]
    A, B = NAMES[4], NAMES[7]
    # (a) a 3-hour market-wide outage: zero and known slots, the cross-section kept, no weekly decision lost
    h3 = "2021-03-03 10:00"
    sp3 = drop_hours(spot, h3, 3)
    v, tb = slots_of(ud, sp3, A)
    hrs = pd.date_range(pd.Timestamp(h3, tz="UTC"), periods=3, freq="h")
    ok_a = bool((v.loc[hrs] == 0.0).all() and (tb.loc[hrs] == 0.0).all())
    u3 = unit_of(prog, ud, sp3)
    decs = [i for i in range(int(grid.get_loc(pd.Timestamp("2021-03-07 23:00", tz="UTC"))),
                             int(grid.get_loc(pd.Timestamp("2021-04-25 23:00", tz="UTC"))) + 1)
            if grid[i].day_of_week == 6 and grid[i].hour == 23]
    same_known = all(np.array_equal(u3["known"][i], base["known"][i]) for i in decs)
    full = all(base["known"][i].sum() == len(NAMES) for i in decs)
    check("11a outage of 3 h (every pair, BTCUSDT included): zero, known slots; the cross-section kept, no weekly "
          "decision lost", ok_a and same_known and full, f"{len(decs)} decisions compared")
    # (b) a 30-hour outage: zero for 24 hours, unknown from the 25th hour
    h30 = "2021-07-07 06:00"
    sp30 = drop_hours(spot, h30, 30)
    v, _ = slots_of(ud, sp30, A)
    hrs = pd.date_range(pd.Timestamp(h30, tz="UTC"), periods=30, freq="h")
    ok_b = bool((v.loc[hrs[:24]] == 0.0).all() and v.loc[hrs[24:]].isna().all()
                and np.isfinite(v.loc[hrs[-1] + F.HOUR]))
    check("11b outage of 30 h: zero and known for 24 hours, unknown from the 25th hour (rule S3)", ok_b)
    # (c) a pair stopped long before a later outage stays unknown; (e) BTCUSDT itself at an outage hour
    stop_at = pd.Timestamp("2021-05-01 00:00", tz="UTC")
    spc = dict(sp3)
    spc[B] = spot[B][spot[B].index < stop_at]
    spc = drop_hours(spc, "2021-06-02 10:00", 3)
    vb, _ = slots_of(ud, spc, B)
    hrs = pd.date_range(pd.Timestamp("2021-06-02 10:00", tz="UTC"), periods=3, freq="h")
    ok_c = bool(vb.loc[hrs].isna().all() and np.isnan(vb.loc[stop_at + 5 * F.HOUR]))
    check("11c a pair stopped a month before an outage gets no zero row there: unknown (S3), and unknown at "
          "ordinary hours after its stop", ok_c)
    vbtc, _ = slots_of(ud, sp3, "BTCUSDT")
    hrs = pd.date_range(pd.Timestamp(h3, tz="UTC"), periods=3, freq="h")
    check("11e BTCUSDT itself at an outage hour: a synthetic zero row, known",
          bool((vbtc.loc[hrs] == 0.0).all() and np.isfinite(vbtc.loc[hrs[0] - F.HOUR])))
    # a missing hour that is NOT an outage (BTCUSDT has its row) stays unknown
    spn = drop_hours(spot, h3, 1, pairs={A})
    vn, _ = slots_of(ud, spn, A)
    check("11f an absent hour that is not an outage hour stays unknown (BTCUSDT has its row)",
          bool(np.isnan(vn.loc[pd.Timestamp(h3, tz="UTC")])))
    # (d) the truncation test with cuts inside an outage block and just after one (3 h and 30 h blocks)
    sp_both = drop_hours(sp3, h30, 30)
    b2 = unit_of(prog, ud, sp_both)
    cut_at = ["2021-03-03 11:00", "2021-03-03 13:00", "2021-07-08 08:00", "2021-07-08 12:00", "2021-07-08 13:00"]
    cuts = [int(grid.get_loc(pd.Timestamp(c, tz="UTC"))) for c in cut_at]
    r = EV.truncation_test(prog, params, ud, SP.DictSpot(sp_both), b2, cuts)
    check("11d truncation test passes with cuts inside a 3 h and a 30 h outage block and just after each",
          r["pass"], str([(c["cut"][:16], c["equal"]) for c in r["cuts"]]))


def t12_coverage(ud, spot):
    import run_study as RS
    plan = {"symbols": [{"perp": s, "spot": SP.spot_symbol(s)[0], "mult": SP.spot_symbol(s)[1]} for s in NAMES]}
    sp3 = drop_hours(spot, "2021-03-03 10:00", 3)
    cov = RS.coverage(ud, SP.DictSpot(sp3), plan, out_path=None)
    o = cov["outage"]
    check("12a coverage: one outage block of 3 h found, share 1.0, no tripwire",
          o["n_hours"] == 3 and o["blocks"] == 1 and o["longest_block"] == 3 and o["share"] == 1.0
          and not cov["stop"] and cov["guard_rejected"] == 0, f"{o['n_hours']} h, share {o['share']}, {cov['reasons']}")
    sp25 = drop_hours(spot, "2021-03-03 10:00", 25)
    cov = RS.coverage(ud, SP.DictSpot(sp25), plan, out_path=None)
    check("12b coverage tripwire: an outage block of 25 h sets the stop flag", cov["stop"] and
          any("block" in x for x in cov["reasons"]), str(cov["reasons"]))
    spg = dict(spot)
    hrs = pd.date_range(pd.Timestamp("2021-08-02 00:00", tz="UTC"), periods=30, freq="h")
    for s in NAMES[1:7]:                                      # six pairs with 30 rejected in-play hours each
        t = spot[s].copy()
        t.loc[hrs, "close"] = t.loc[hrs, "close"] * 3.0
        spg[s] = t
    cov = RS.coverage(ud, SP.DictSpot(spg), plan, out_path=None)
    check("12c coverage tripwire: more than 5 pairs with more than 24 guard-rejected in-play hours sets the stop flag",
          cov["stop"] and len(cov["pairs_over_24_rejected"]) == 6 and any("symbol map" in x for x in cov["reasons"]),
          str(cov["reasons"]))
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "spot_coverage.json"
        p.write_text(json.dumps({"stop": True, "reasons": ["test"]}), encoding="ascii")
        try:
            RS.coverage_gate(p)
            refused = False
        except SystemExit:
            refused = True
        p.write_text(json.dumps({"stop": False, "reasons": []}), encoding="ascii")
        RS.coverage_gate(p)
        try:
            RS.coverage_gate(Path(td) / "absent.json")
            refused_absent = False
        except SystemExit:
            refused_absent = True
    rows = [{"program": "x", "label": "default", "status": "ok"} for _ in range(RS.CAP)]
    try:
        RS.budget_check(rows, HS1, "default", False)
        capped = False
    except SystemExit:
        capped = True
    check("12d the runner refuses on the stop flag, without a coverage file, and at the cap of 14 evaluations",
          refused and refused_absent and capped and RS.CAP == 14 and len([s for s in RS.REGISTERED
                                                                           if RS.REGISTERED[s]["role"] == "hypothesis"]) == 3)


def main():
    t1_ceiling()
    t2_csv()
    t3_symbols()
    t4_slots()
    ud, spot = world()
    prog = program(HS1)
    for fn, args in ((t5_isolation, (ud, spot)), (t6_future_rows, (ud, spot, prog)), (t7_truncation, (ud, spot, prog)),
                     (t8_missing_hour, (ud, spot, prog)), (t9_guard, (ud, spot, prog)), (t10_pipeline, (ud, spot)),
                     (t11_outages, (ud, spot, prog)), (t12_coverage, (ud, spot))):
        try:
            fn(*args)
        except Exception as e:                                   # a crash is a failure, shown in full
            traceback.print_exc()
            check(f"{fn.__name__} raised {type(e).__name__}", False)
    n_fail = sum(1 for _, ok, _ in RESULTS if not ok)
    print(f"{len(RESULTS) - n_fail} of {len(RESULTS)} checks passed")
    sys.exit(n_fail)


if __name__ == "__main__":
    main()
