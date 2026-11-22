"""KP-015 F + fix pass 4 (U2): the universe calibration on worlds with the REAL membership calendar (synthetic
source here, never run for real): every symbol keeps its real rows (present / absent hours, trades and volumes),
so the kernel's own membership rule reproduces the source's monthly schedule; only prices are resampled (null A:
one source day per world day shared by all symbols, personal fallback days; null B: one coin per day mirrors
every symbol); the protocol runs on the production block path; the oracle on the same worlds; the seal rule over
both units."""
import json

import numpy as np
import pandas as pd
import pytest

from omr import calibrate as CB
from omr import constants as C
from omr import datasets as D
from omr import lang as L
from omr import pipeline as PL
from omr import ucalibrate as UC
from omr import universe as U
from omr import upipeline as UP

H = U.HOUR_NS
G0 = pd.Timestamp(C.UNIVERSE_START, tz="UTC") - pd.Timedelta(days=UC.KEEP_BEFORE_DAYS)


def _real_tables():
    """A synthetic 'real' source with churn, a run of present zero-trade bars, an absent stretch and a funding
    gap in one symbol."""
    tables, table = UC.synthetic_churn_universe(seed=4, n_sym=44, early=24)
    acts = {s: U.activity_of(t["klines"]) for s, t in tables.items()}
    panel = UC.panel_symbols(acts)
    s = panel[0]
    kl = tables[s]["klines"].copy()
    z = (kl.index >= pd.Timestamp("2021-03-03 05:00", tz="UTC")) & (kl.index <= pd.Timestamp("2021-03-03 09:00", tz="UTC"))
    for c in UC.OTHER:
        kl.loc[z, c] = 0.0
    kl.loc[z, ["open", "high", "low", "close"]] = kl.loc[kl.index < pd.Timestamp("2021-03-03 05:00", tz="UTC"),
                                                         "close"].iloc[-1]
    g = (kl.index >= pd.Timestamp("2021-05-10 02:00", tz="UTC")) & (kl.index <= pd.Timestamp("2021-05-10 12:00", tz="UTC"))
    last = kl.loc[kl.index < pd.Timestamp("2021-05-10 02:00", tz="UTC"), "close"].iloc[-1]
    kl.loc[g, ["open", "high", "low", "close"]] = last
    kl.loc[g, UC.OTHER] = 0.0
    kl.loc[g, "is_gap"] = True
    tables[s] = dict(tables[s], klines=kl)
    return tables, panel, s


@pytest.fixture(scope="module")
def world_src():
    tables, panel, special = _real_tables()
    src = UC.USource.build(panel, lambda x: tables[x])
    return tables, panel, special, src


@pytest.fixture(scope="module")
def real_ud(world_src):
    tables, panel, _, src = world_src
    btc = D.assemble_frame(tables[src.meta["btc"]], D.PROGRAM_EXTRA)
    return UP.udata_from_tables({s: tables[s] for s in panel}, btc, C.VAL_END)


def test_families_are_top30_kernel_programs_within_the_lookback_limit():
    for f in UC.FAMILIES:
        p = L.parse_file(UC.family_path(f))
        assert p.unit == "top30" and p.kind == "portfolio" and p.lookback_hours <= C.LOOKBACK_MAX_HOURS
    with pytest.raises(ValueError):
        UC.family_path("gen000_donchian_ls")


@pytest.mark.parametrize("null", ["A", "B"])
def test_worlds_keep_the_real_rows_and_reproduce_the_membership(world_src, real_ud, null):
    tables, panel, special, src = world_src
    ud = UC.build_uworld(src, null, 3)
    for s in (panel[0], panel[5], panel[-1], special):
        w = ud.tables(s)["klines"]
        r = tables[s]["klines"]
        r = r[(r.index >= G0) & (r.index <= pd.Timestamp(C.VAL_END, tz="UTC"))]
        assert w.index.equals(r.index)
        for c in UC.OTHER + ["is_gap"]:
            assert np.array_equal(w[c].to_numpy(), r[c].to_numpy()), (s, c)
        fw, fr = ud.tables(s)["funding"], tables[s]["funding"]
        assert fw.index.equals(fr.index) and np.array_equal(fw["interval_hours"], fr["interval_hours"])
    g = ud.grid()
    mw, mr = ud.membership(g[0].value, g[-1].value), real_ud.membership(g[0].value, g[-1].value)
    assert [mw.members("top30", i) for i in range(len(mw.months))] == \
        [mr.members("top30", i) for i in range(len(mr.months))]
    assert len(mw.ever("top30")) > 30                                          # the calendar churns
    bw, br = UP.Blocked(ud, "top30"), UP.Blocked(real_ud, "top30")
    assert bw.symbols == br.symbols and np.array_equal(bw.inplay(), br.inplay())   # usable flags, unit sizes


def test_null_a_one_source_day_shared_and_personal_fallbacks(world_src):
    tables, panel, _, src = world_src
    w = UC.UWorld(src, "A", 7)
    shared = fallback = 0
    for s in panel[:12]:
        m = src.sym(s)
        sd = w.source_days(s)
        shift = m["sd0"] - src.D0
        full = src.arr["full"][m["full_off"]:m["full_off"] + m["nd"]]
        gd = np.arange(m["nd"]) + shift
        lp = w.pick[gd] - shift
        ok = (lp >= 0) & (lp < m["nd"]) & full[np.clip(lp, 0, m["nd"] - 1)]
        assert np.array_equal(sd[ok], w.pick[gd][ok])                         # the world's day where fully active
        assert full[sd[~ok] - shift].all()                                    # else one of its own full days
        shared += int(ok.sum())
        fallback += int((~ok).sum())
        kl = w.tables(s, trim=False)["klines"]
        real = tables[s]["klines"]
        act = (~real["is_gap"].to_numpy()) & (real["trades"].to_numpy() > 0)
        rows = np.nonzero(act)[0][::997]
        for r in rows:                                                       # close / open of the source hour
            t = real.index[r].value
            ld = t // U.DAY_NS - m["sd0"]
            srow = ((sd[ld] + src.D0) * U.DAY_NS + (t // H) % 24 * H - m["start"]) // H
            want = real["close"].to_numpy()[srow] / real["open"].to_numpy()[srow]
            assert np.isclose(kl["close"].to_numpy()[r] / kl["open"].to_numpy()[r], want, rtol=1e-12)
    assert shared > 0 and fallback > 0


def test_zero_trade_bars_are_flat_absent_bars_stay_absent_and_prices_start_at_the_real_first_open(world_src):
    tables, panel, special, src = world_src
    for null in ("A", "B"):
        kl = UC.UWorld(src, null, 2).tables(special, trim=False)["klines"]
        real = tables[special]["klines"]
        assert kl["open"].iloc[0] == real["open"].iloc[0]
        flat = ~((~real["is_gap"].to_numpy()) & (real["trades"].to_numpy() > 0))
        assert flat.sum() >= 5 + 11
        prev = np.r_[kl["open"].iloc[0], kl["close"].to_numpy()[:-1]]
        for c in ("open", "high", "low", "close"):
            assert np.array_equal(kl[c].to_numpy()[flat], prev[flat])
        assert np.array_equal(kl["is_gap"].to_numpy(), real["is_gap"].to_numpy())
        mk = UC.UWorld(src, null, 2).tables(special, trim=False)["mark_klines"]
        assert not mk.index.isin(real.index[real["is_gap"].to_numpy()]).any()


def test_null_a_funding_keeps_the_calendar_and_takes_the_source_days_rates(world_src):
    tables, panel, _, src = world_src
    w = UC.UWorld(src, "A", 9)
    s = panel[3]
    fw, fr = w._funding(s, w.source_days(s), signs=False), tables[s]["funding"]     # before the R-E sign coin
    assert fw.index.equals(fr.index)
    m = src.sym(s)
    sd = w.source_days(s)
    days = (fr.index.asi8 // U.DAY_NS) - m["sd0"]
    by_day = pd.Series(fr["rate"].to_numpy(), index=fr.index.asi8 // U.DAY_NS)
    checked = 0
    for ld in np.unique(days)[5:400:7]:
        src_rates = by_day.get(sd[ld] + src.D0)
        if src_rates is None:
            continue
        src_rates = np.atleast_1d(np.asarray(src_rates))
        got = fw["rate"].to_numpy()[days == ld]
        want = src_rates[np.arange(len(got)) % len(src_rates)]
        assert np.array_equal(got, want)
        checked += 1
    assert checked > 20
    assert not np.array_equal(fw["rate"].to_numpy(), fr["rate"].to_numpy())


def test_null_b_one_coin_per_day_mirrors_every_symbol_and_keeps_funding(world_src):
    tables, panel, _, src = world_src
    w = UC.UWorld(src, "B", 4)
    a, b = panel[1], panel[4]
    flips = {}
    for s in (a, b):
        kl = w.tables(s, trim=False)["klines"]
        real = tables[s]["klines"]
        act = (~real["is_gap"].to_numpy()) & (real["trades"].to_numpy() > 0)
        cw = (kl["close"] / kl["open"]).to_numpy()
        cr = (real["close"] / real["open"]).to_numpy()
        same = np.isclose(cw, cr, rtol=1e-12)
        mir = np.isclose(cw, 1.0 / cr, rtol=1e-12)
        assert (same | mir)[act].all()
        day = real.index.asi8 // U.DAY_NS
        for d in np.unique(day[act])[::5]:
            sel = act & (day == d) & ~(same & mir)
            if sel.any():
                flips.setdefault(int(d), set()).add(bool(mir[sel].all()))
        assert np.array_equal(w._funding(s, w.source_days(s), signs=False)["rate"], tables[s]["funding"]["rate"][
            tables[s]["funding"].index <= pd.Timestamp(C.VAL_END, tz="UTC")])          # before the R-E sign coin
    assert all(len(v) == 1 for v in flips.values())                         # one coin per day for both
    share = np.mean([next(iter(v)) for v in flips.values()])
    assert 0.35 < share < 0.65


def test_the_dev_view_is_the_same_world_under_the_dev_ceiling(world_src):
    _, panel, _, src = world_src
    full, dev = UC.build_uworld(src, "A", 5), UC.dev_view(src, "A", 5)
    assert dev.end == pd.Timestamp(C.DEV_END, tz="UTC")
    for s in panel[:6]:
        a, b = full.tables(s), dev.tables(s)
        for d in ("klines", "mark_klines"):
            cut = a[d][a[d].index <= dev.end]
            assert cut.equals(b[d]), (s, d)
    assert all(a.end <= dev.end.value for a in dev.acts.values())


def test_the_shared_source_gives_the_same_worlds(world_src):
    _, panel, _, src = world_src
    spec, blocks = src.to_shared()
    try:
        twin, mine = UC.USource.from_shared(spec)
        for k in src.arr:                                                    # hm / lm hold NaN (R-O)
            assert np.array_equal(src.arr[k], twin.arr[k], equal_nan=src.arr[k].dtype.kind == "f")
            assert src.arr[k].dtype == twin.arr[k].dtype
        for s in panel[:3]:
            a, b = UC.UWorld(src, "A", 1).tables(s), UC.UWorld(twin, "A", 1).tables(s)
            assert all(a[d].equals(b[d]) for d in a)
        for x in mine:
            x.close()
    finally:
        for x in blocks:
            x.close()
            x.unlink()


def test_one_null_world_runs_the_protocol_on_production_blocks(world_src, val_handle, monkeypatch):
    _, _, _, src = world_src
    monkeypatch.setattr(CB, "N_DRAWS", 2)
    monkeypatch.setattr(UC, "OPTS", PL.Opts(include_g8=False, keep_detail=False, u_lags=10, jitter_n=2,
                                            truncation_cuts=2, start_cuts=1, start_cuts_val=1))
    seen = []
    real = UP.Blocked.__init__

    def spy(self, ud, band, months=C.UNIVERSE_BLOCK_MONTHS, **kw):
        seen.append(months)
        return real(self, ud, band, months=months, **kw)
    monkeypatch.setattr(UP.Blocked, "__init__", spy)
    UC._W.clear()
    UC._W.update({"handle": val_handle, "src": src, "progs": {f: L.parse_file(UC.family_path(f)) for f in UC.FAMILIES}})
    rows = UC.task_null(("A", 11000))
    assert [r["family"] for r in rows] == list(UC.FAMILIES)
    sub = [r for r in rows if r["submitted"]]
    assert sub and all(r["status"] in ("evaluated", "liquidated") for r in sub)
    assert all("perm_p" in r and 0 < r["perm_p"] <= 1 for r in sub if r["status"] == "evaluated")
    ev = [r for r in sub if r["status"] == "evaluated"]                  # R-N: the row carries the speed-limit record
    assert ev and all(isinstance(r["g6_memory"], float) and r["g6_lag_step"] > 0 and
                      r["g6_memory_over_limit"] == (not r["g6_memory"] <= C.UNIVERSE_G6_MEMORY_MAX) for r in ev)
    assert all(r["perm_p"] == 1.0 for r in ev if r["g6_memory_over_limit"])
    assert all(CB.tier_at(r, 0.1) in (True, False) for r in ev)             # tier_at still reads the rows
    assert seen and all(m == C.UNIVERSE_BLOCK_MONTHS for m in seen)                # the production block path
    summ = CB.null_summary(rows, list(UC.FAMILIES))
    assert summ["n_pairs"] == 3 and summ["n_submitted"] == len(sub)


def test_the_cross_sectional_oracle_on_the_same_worlds(world_src, val_handle):
    _, _, _, src = world_src
    ud = UC.build_uworld(src, "A", 6)
    ob = UC.UOracle(ud, 1, 99)
    assert len(ob.bu.plan) > 1                                                       # production blocks
    W = ob.weights(0.6)
    rows = W[ob.rows]
    live = np.abs(rows).sum(axis=1) > 0
    assert live.mean() > 0.8
    assert np.allclose(rows[live].sum(axis=1), 0.0, atol=1e-12) and np.allclose(np.abs(rows[live]).sum(axis=1), 1.0)
    assert not np.any(rows[~ob.inplay[ob.rows]])                                     # in-play symbols only
    assert ob.val_sharpe(0.6) > ob.val_sharpe(0.0) + 1.0                             # foresight pays
    res = UP.evaluate_weights_u(W, ob.bu, 1, PL.Opts(u_lags=20, include_g8=False), val_handle, 0.1)
    assert res["status"] == "evaluated" and res["gates"]["G8"]["pass"] is None and res["gates"]["G5"]["pass"]


# ---------------------------------------------------------------- fix pass 5: R-E funding sign, R-D run


def _sign_factors(w, s):
    signed = w._funding(s, w.source_days(s))
    plain = w._funding(s, w.source_days(s), signs=False)
    return signed, plain


@pytest.mark.parametrize("null", ["A", "B"])
def test_r_e_funding_sizes_kept_signs_shared_per_settlement_time(world_src, null):
    tables, panel, _, src = world_src
    w = UC.UWorld(src, null, 13)
    per = {}
    for s in panel[:6]:
        signed, plain = _sign_factors(w, s)
        assert signed.index.equals(plain.index)
        assert np.array_equal(np.abs(signed["rate"].to_numpy()), np.abs(plain["rate"].to_numpy()))   # (1)
        assert np.array_equal(signed["interval_hours"].to_numpy(), plain["interval_hours"].to_numpy())
        nz = plain["rate"].to_numpy() != 0
        f = signed["rate"].to_numpy()[nz] / plain["rate"].to_numpy()[nz]
        assert set(np.unique(f)) <= {-1.0, 1.0}
        per[s] = dict(zip(signed.index.asi8[nz].tolist(), f.tolist()))
    if null == "B":                                                     # null B: the recorded rates up to the sign
        real = tables[panel[0]]["funding"]
        real = real[real.index <= pd.Timestamp(C.VAL_END, tz="UTC")]
        assert np.array_equal(np.abs(_sign_factors(w, panel[0])[0]["rate"].to_numpy()), np.abs(real["rate"].to_numpy()))
    a, b = panel[0], panel[1]
    common = sorted(set(per[a]) & set(per[b]))
    assert len(common) > 100 and all(per[a][t] == per[b][t] for t in common)                    # (2) same time
    vals = np.array([per[a][t] for t in sorted(per[a])])
    assert (vals > 0).any() and (vals < 0).any()
    assert abs(float(np.mean(vals[1:] * vals[:-1]))) < 0.05                                        # (4) no persistence
    w2, w3 = UC.UWorld(src, null, 13), UC.UWorld(src, null, 14)                                   # (3) per seed
    assert np.array_equal(_sign_factors(w2, a)[0]["rate"], _sign_factors(w, a)[0]["rate"])
    assert not np.array_equal(_sign_factors(w3, a)[0]["rate"], _sign_factors(w, a)[0]["rate"])


def test_d6_source_day_stats_are_a_deterministic_number_per_world(world_src):
    _, panel, _, src = world_src
    w = UC.UWorld(src, "A", 21)
    st = w.source_day_stats()
    for s in panel:                                                     # building tables (and evicting them)
        w.tables(s)
    assert w.source_day_stats() == st == UC.UWorld(src, "A", 21).source_day_stats()
    assert st["shared"] > 0 and st["fallback"] > 0


def test_d1_partial_header_binds_the_run(tmp_path):
    p = tmp_path / "x.partial.jsonl"
    part = UC.Partial(p, {"a": 1}, log=lambda s: None)
    part.record(UC.task_key("null", ["A", 1]), [{"x": float("inf"), "y": 0.5}])
    with p.open("a", encoding="ascii") as f:
        f.write('{"key": "torn')                                       # a line torn by a crash is ignored
    again = UC.Partial(p, {"a": 1}, log=lambda s: None)
    assert again.done == {UC.task_key("null", ["A", 1]): [{"x": "inf", "y": 0.5}]}
    with pytest.raises(UC.PartialMismatch):
        UC.Partial(p, {"a": 2}, log=lambda s: None)
    fresh = UC.Partial(p, {"a": 2}, restart=True, log=lambda s: None)
    assert fresh.done == {}


@pytest.fixture
def tiny_run(world_src, monkeypatch):
    """A tiny synthetic dry run: one family, one world per null, one oracle world, a short rho grid."""
    _, _, _, src = world_src
    monkeypatch.setattr(UC, "synthetic_source", lambda *a, **k: src)
    monkeypatch.setattr(UC, "FAMILIES", ("ucal_xs_momentum",))
    monkeypatch.setattr(CB, "N_DRAWS", 2)
    monkeypatch.setattr(UC, "OPTS", PL.Opts(include_g8=False, keep_detail=False, u_lags=5, jitter_n=1,
                                            truncation_cuts=1, start_cuts=1, start_cuts_val=1))
    monkeypatch.setattr(UC, "RHO_GRID", np.array([0.0, 0.3, 0.6, 0.9]))
    monkeypatch.setattr(UC, "FINE_POINTS", 3)
    return ["--unlocked-dry-run", "--workers", "0", "--worlds", "1", "--oracle-worlds", "1"]


def _artifact(path):
    art = json.loads(path.read_bytes())
    art.pop("created_at")
    art.pop("wall_seconds")
    return art


def test_d1_an_interrupted_run_resumes_to_the_same_artifact(tiny_run, tmp_path, monkeypatch, capsys):
    whole = tmp_path / "whole.json"
    UC.main(tiny_run + ["--out", str(whole)])
    assert not whole.with_suffix(".partial.jsonl").exists()            # removed after the artifact is written
    cut = tmp_path / "cut.json"
    real = UC.Partial.record
    calls = []

    def dying(self, key, result):
        real(self, key, result)
        calls.append(key)
        if len(calls) == 3:
            raise KeyboardInterrupt("killed after three tasks")
    monkeypatch.setattr(UC.Partial, "record", dying)
    with pytest.raises(KeyboardInterrupt):
        UC.main(tiny_run + ["--out", str(cut)])
    assert not cut.exists() and cut.with_suffix(".partial.jsonl").exists()
    monkeypatch.setattr(UC.Partial, "record", real)
    capsys.readouterr()
    UC.main(tiny_run + ["--out", str(cut)])
    out = capsys.readouterr().out
    assert "resuming: 3 finished tasks" in out
    assert "source liquidation ratios (R-O): " in out                    # printed once per run (R-O)
    a, b = _artifact(whole), _artifact(cut)
    assert set(a["source_liq"]) == {"active_rows", "active_rows_without_mark", "min_low_over_open",
                                    "max_high_over_open"} and a["source_liq"]["active_rows"] > 0
    tun = a["oracle"]["A"]["tuning"]["fast"]["1.5"]
    assert tun["liquidated_books"] >= 0 and tun["books"] == 1
    assert a == b
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)
    assert a["protocol"]["levels"] == [1.5] and a["protocol_version"] == UC.PROTOCOL_VERSION
    assert {r["level"] for n in ("A", "B") for r in a["oracle"][n]["rows"]} == {1.5}
    assert set(a["oracle"]["A"]["summary"]) == {"fast|1.5", "slow|1.5"}


def test_d2_the_memory_preflight_refuses_unless_forced(tiny_run, tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(UP, "available_memory_bytes", lambda: 2 * 2 ** 30)
    args = ["--unlocked-dry-run", "--workers", "4", "--out", str(tmp_path / "m.json")]
    with pytest.raises(SystemExit) as e:
        UC.main(args)
    assert e.value.code == UC.EXIT_MEMORY
    out = capsys.readouterr().out
    assert "MEMORY" in out and "1 workers fit" in out
    mp_ = UC.memory_preflight(1, 10 ** 8)
    assert mp_["ok"] and mp_["workers_that_fit"] == 1


def test_d4_defaults():
    import argparse
    seen = {}

    def grab(self, args=None, namespace=None):
        ns = argparse.ArgumentParser.parse_known_args(self, [])[0]
        seen.update(vars(ns))
        raise SystemExit(0)
    import unittest.mock as um
    with um.patch.object(argparse.ArgumentParser, "parse_args", grab):
        with pytest.raises(SystemExit):
            UC.main([])
    assert seen["worlds"] == 200 and seen["oracle_worlds"] == 100 and seen["workers"] == 4


# ---------------------------------------------------------------- R-F: null A source days per month


def test_r_f_pooled_months_put_every_member_on_the_shared_day(world_src):
    _, panel, _, src = world_src
    pools = src.meta["pools"]
    assert pools["min_pool_days"] == UC.POOL_MIN_DAYS == 90 and pools["pooled_months"] > 0
    assert pools["smallest_pool_days"] >= 90 and pools["months_whole_period_pool"] >= 1
    acts = src.acts(pd.Timestamp(C.VAL_END, tz="UTC").value)
    mem = U.membership(acts, list(acts), pd.Timestamp(C.UNIVERSE_START, tz="UTC").value,
                       pd.Timestamp(C.VAL_END, tz="UTC").value)
    w = UC.UWorld(src, "A", 31)
    dp = np.asarray(src.arr["day_pool"])
    checked = 0
    for i, m in enumerate(mem.months):
        if not mem.unit_exists("top30", i):
            continue
        g = (int(m) // U.DAY_NS) - src.D0                                    # the month's first global day
        if g >= len(dp) or dp[g] < 0:
            continue
        nd = pd.Timestamp(int(m), tz="UTC").days_in_month
        for s in mem.members("top30", i):
            ms = src.sym(s)
            sd, ok = w._source_days(s)
            local = np.arange(g, min(g + nd, len(dp))) - (ms["sd0"] - src.D0)
            local = local[(local >= 0) & (local < ms["nd"])]
            assert ok is not None and ok[local].all()                        # no member on a fallback day
            assert np.array_equal(sd[local], w.pick[local + ms["sd0"] - src.D0])     # the shared day
            checked += 1
    assert checked > 100


def test_r_f_deterministic_per_seed_and_drawn_from_the_pools(world_src):
    _, _, _, src = world_src
    a, b, c = UC.UWorld(src, "A", 5), UC.UWorld(src, "A", 5), UC.UWorld(src, "A", 6)
    assert np.array_equal(a.pick, b.pick) and not np.array_equal(a.pick, c.pick)
    dp, off, days = (np.asarray(src.arr[k]) for k in ("day_pool", "pool_off", "pool_days"))
    for d in np.nonzero(dp >= 0)[0][::37]:
        assert a.pick[d] in set(days[off[dp[d]]:off[dp[d] + 1]].tolist())
    lo = src.meta["pool_lo"]
    assert ((a.pick[dp < 0] >= lo) & (a.pick[dp < 0] < src.ND)).all()


# ---------------------------------------------------------------- fix pass 6: F3 partial file integrity


def _quiet(*a, **k):
    return None


def test_f3_a_torn_tail_does_not_swallow_the_next_record(tmp_path):
    p = tmp_path / "t.partial.jsonl"
    part = UC.Partial(p, {"h": 1}, log=_quiet)
    for i in range(3):
        part.record(UC.task_key("null", ["A", i]), [{"v": i}])
    with p.open("ab") as f:
        f.write(b'{"key": "[\\"null\\",[\\"A\\",3]]", "result": [{"v"')            # torn, no newline
    logs = []
    again = UC.Partial(p, {"h": 1}, log=logs.append)
    assert again.discarded == 1 and len(again.done) == 3 and "1 damaged lines discarded" in logs[0]
    again.record(UC.task_key("null", ["A", 3]), [{"v": 3}])                     # the next append after a torn tail
    third = UC.Partial(p, {"h": 1}, log=_quiet)
    assert third.done == {UC.task_key("null", ["A", i]): [{"v": i}] for i in range(4)}   # nothing lost


def test_f3_a_flipped_character_in_a_stored_result_is_discarded_and_recomputed(tmp_path):
    p = tmp_path / "t.partial.jsonl"
    part = UC.Partial(p, {"h": 1}, log=_quiet)
    part.record(UC.task_key("null", ["A", 0]), [{"val_sharpe": 0.123456}])
    part.record(UC.task_key("null", ["A", 1]), [{"val_sharpe": 0.5}])
    lines = p.read_bytes().split(b"\n")
    assert b"0.123456" in lines[1]
    lines[1] = lines[1].replace(b"0.123456", b"0.123457")                     # one flipped digit
    p.write_bytes(b"\n".join(lines))
    again = UC.Partial(p, {"h": 1}, log=_quiet)
    assert again.discarded == 1 and list(again.done) == [UC.task_key("null", ["A", 1])]


def test_f3_a_key_twice_with_different_results_stops_and_the_same_result_twice_is_accepted(tmp_path):
    p = tmp_path / "t.partial.jsonl"
    part = UC.Partial(p, {"h": 1}, log=_quiet)
    k = UC.task_key("curve", ["A", 1, "fast", [0.1]])
    part.record(k, [1.0])
    part.record(k, [1.0])
    assert UC.Partial(p, {"h": 1}, log=_quiet).done == {k: [1.0]}
    part.record(k, [2.0])
    with pytest.raises(UC.PartialMismatch):
        UC.Partial(p, {"h": 1}, log=_quiet)
    assert UC.Partial(p, {"h": 1}, restart=True, log=_quiet).done == {}


# ---------------------------------------------------------------- fix pass 6: F6 oracle phases first


def _power_rows(null, perm_p, seeds=(0, 1, 2, 3)):
    return [[{"null": null, "speed": s, "level": 1.5, "rho": 0.1, "world_seed": w, "status": "evaluated",
              "val_sharpe": 1.5, "perm_p": perm_p,
              "gates": {g: True for g in ("G1", "G2", "G3", "G4", "G5", "G7", "G10")} | {"G6": None, "G8": None}}
             for s in CB.SPEEDS] for w in seeds]


@pytest.mark.parametrize("perm_p,advisory", [(0.5, True), (0.001, False)])
def test_f6_oracle_phases_run_first_and_a_hopeless_power_is_announced(monkeypatch, perm_p, advisory):
    """Light: fabricated task results (no universe is built). The oracle phases of both nulls come before the
    null worlds; with power 0 at the largest threshold one prominent ADVISORY line is logged before the null
    phases, with full power none."""
    calls = []

    def fake_run_tasks(pool, partial, kind, arglist, log, label, on_progress=None):
        calls.append(kind)
        if kind == "power":
            return _power_rows(arglist[0][0], perm_p, seeds=range(len(arglist)))
        return [[] for _ in arglist]
    monkeypatch.setattr(UC, "run_tasks", fake_run_tasks)
    monkeypatch.setattr(UC, "tune_rho", lambda pool, partial, null, speed, seeds, log: (
        calls.append("curve"), {"1.5": {"rho": 0.1}})[1])
    logs = []
    nulls, oracle = UC.calibrate_run(None, None, list(UC.FAMILIES), 3, 4, logs.append)
    assert calls == ["curve", "curve", "power", "curve", "curve", "power", "null", "null"]
    adv = [ln for ln in logs if ln.startswith("ADVISORY")]
    assert bool(adv) == advisory
    if advisory:
        assert "seal rule will STOP" in adv[0] and "interrupted" in adv[0] and "null A fast" in adv[0]
    assert any("Tier-1 power" in ln for ln in logs)
    assert set(oracle) == {"A", "B"} and set(nulls) == {"A", "B"}


def test_f6_the_artifact_does_not_depend_on_the_phase_order(tiny_run, tmp_path, monkeypatch):
    """HEAVY (builds the synthetic universe): the artifact of the oracle-first run equals the one of a run that
    takes the null worlds first, apart from created_at and wall_seconds."""
    first = tmp_path / "oracle_first.json"
    UC.main(tiny_run + ["--out", str(first)])
    real = UC.calibrate_run

    def nulls_first(pool, partial, fams, worlds, oracle_worlds, log):
        nulls = {}
        for null in ("A", "B"):
            res = UC.run_tasks(pool, partial, "null", [[null, UC.SEEDS[null] + i] for i in range(worlds)], log, null)
            rows = sorted((r for rr in res for r in rr), key=lambda r: (r["world_seed"], r["family"]))
            nulls[null] = {"rows": rows, "summary": CB.null_summary(rows, fams, worlds)}   # R-R: designed pairs
        _, oracle = real(pool, partial, fams, worlds, oracle_worlds, log)     # null tasks are reused from partial
        return nulls, oracle
    monkeypatch.setattr(UC, "calibrate_run", nulls_first)
    second = tmp_path / "nulls_first.json"
    UC.main(tiny_run + ["--out", str(second)])
    assert _artifact(first) == _artifact(second)


# ---------------------------------------------------------------- fix pass 6: F8 (R-I) universe oracle speeds


def test_f8_the_universe_oracle_speeds_are_a_unit_constant(monkeypatch):
    """Light: the run header carries the unit speeds; the oracle tasks build each speed's UOracle with
    USPEEDS days; omr.calibrate's speeds are unchanged."""
    assert UC.USPEEDS == {"fast": UC.UNIVERSE_FAST_DAYS, "slow": 20} and set(UC.USPEEDS) == set(CB.SPEEDS)
    assert CB.SPEEDS == {"fast": 1, "slow": 20}                                      # the core is untouched
    h = UC.run_header({"semantic": "s" * 64}, "r" * 64, list(UC.FAMILIES), 2, 2, True)
    assert h["speeds_days"] == UC.USPEEDS
    built = []

    class FakeOracle:
        def __init__(self, ud, k_days, eps_seed):
            built.append(k_days)
            self.bu = None

        def val_sharpe(self, rho):
            return 0.0

        def weights(self, rho):
            return None
    monkeypatch.setattr(UC, "UOracle", FakeOracle)
    monkeypatch.setattr(UC, "build_uworld", lambda *a, **k: None)
    monkeypatch.setattr(UP, "evaluate_weights_u", lambda *a, **k: {"status": "liquidated", "reason": "x"})
    UC._W.clear()
    UC._W.update({"src": None, "handle": None})
    UC.task_oracle_curve(["A", 1, "fast", [0.1]])
    UC.task_oracle_curve(["A", 1, "slow", [0.1]])
    assert built == [UC.USPEEDS["fast"], 20]
    built.clear()
    UC.task_oracle_power(["A", 1, {"fast|1.5": 0.1, "slow|1.5": 0.1}])
    assert built == [UC.USPEEDS["fast"], UC.USPEEDS["slow"]]
    UC._W.clear()


# ---------------------------------------------------------------- fix pass 6: F9 (R-J) the reversal family


def test_f9_the_reversal_family_is_the_momentums_mirror_on_daily_bars():
    """Light (the 12-symbol probe panel): the family parses in unit top30 within the lookback limit, its draws stay
    within 3..20 days by the momentum's mechanism, and for the same n its signal and weights are exactly minus the
    momentum family's."""
    from omr import interp as X
    from omr import probe
    rev = L.parse_file(UC.family_path("ucal_xs_reversal"))
    mom = L.parse_file(UC.family_path("ucal_xs_momentum"))
    assert rev.unit == "top30" and rev.kind == "portfolio" and list(rev.params) == ["n"]
    p = rev.params["n"]
    assert p.is_int and (p.low, p.high) == (3, 20) and rev.lookback_hours <= C.LOOKBACK_MAX_HOURS
    rng = np.random.default_rng(4)
    draws = [CB.draw_params(rev, rng)["n"] for _ in range(2000)]
    assert min(draws) == 3 and max(draws) == 20 and all(isinstance(d, int) for d in draws)
    panel, btc = probe.universe_panel()
    for n in (3, 7, 20):
        r_raw, r_kn = X.evaluate_full(rev, {"n": n}, panel, btc)
        m_raw, m_kn = X.evaluate_full(mom, {"n": n}, panel, btc)
        assert np.array_equal(r_kn, m_kn) and r_kn.any()
        assert np.array_equal(r_raw, -m_raw, equal_nan=True)
        assert np.array_equal(UP.uweights(r_raw), -UP.uweights(m_raw))


# ---------------------------------------------------------------- fix pass 8: R-M one expected day gross (both nulls)

# The draws BEFORE the R-M edit (code at 58ba59e; the test source; null A seed 17, null B seed 4): R-M changes no draw
DRAWS_58BA59E = {"pick_A17": "413a4e1ba9aac100e26c4bbd937e50c7d85d6b1f08357d0340a18a17f14255e4",
                 "source_days_A17": "53dd79441e6188c110c3a367a961ad229dbaa1d46d479398ccdc91c8535d6c82",
                 "flip_B4": "c4d6431be672a4a85a5304b38c991981b71fb3b474b5f845276afaf71714e0e9"}


def _sha(a, dt) -> str:
    import hashlib
    return hashlib.sha256(np.ascontiguousarray(np.asarray(a, dtype=dt)).tobytes()).hexdigest()


def _raw(src, s):
    """From the raw rows only (no kernel helper): per row the local day, the active flag and lrt = log(g * cr);
    per local day full (24 active rows, finite sum) and the day's log gross (NaN unless full)."""
    m = src.sym(s)
    g, cr = np.asarray(src.rows(s, "g"), dtype=np.float64), np.asarray(src.rows(s, "cr"), dtype=np.float64)
    act = np.asarray(src.rows(s, "act"), dtype=bool)
    lrt = np.log(g * cr)
    ld = (m["start"] + H * np.arange(m["n"])) // U.DAY_NS - m["sd0"]
    cnt = np.bincount(ld[act], minlength=m["nd"])[:m["nd"]]
    sm = np.bincount(ld[act], weights=lrt[act], minlength=m["nd"])[:m["nd"]]
    full = (cnt == 24) & np.isfinite(sm)
    return ld, act, lrt, full, np.where(full, sm, np.nan)


def _global(src, s, local):
    m = src.sym(s)
    shift = m["sd0"] - src.D0
    out = np.full(src.ND, np.nan)
    n = min(m["nd"], src.ND - shift)
    out[shift:shift + n] = local[:n]
    return out


def _pool_sets(src):
    off, days = np.asarray(src.arr["pool_off"]), np.asarray(src.arr["pool_days"])
    sets = [days[off[j]:off[j + 1]] for j in range(len(off) - 1)]
    return sets + [np.arange(src.meta["pool_lo"], src.ND)]


def _common_gross(src) -> float:
    tot, cnt = 0.0, 0
    for s in src.symbols:
        d = _raw(src, s)[4]
        v = np.exp(d[np.isfinite(d)])
        tot, cnt = tot + float(v.sum()), cnt + len(v)
    return tot / cnt


def _null_a_expected(src, k, s, j, Q) -> float:
    """P(shared) * mean over Q's full days of Qd * exp(pool_adj) + P(fallback) * mean over all full days of Qd * exp(fb_adj);
    the pick is uniform over Q, the fallback uniform over the symbol's full days."""
    pa, fb = np.asarray(src.arr["pool_adj"]), np.asarray(src.arr["fb_adj"])
    loc = _raw(src, s)[4]
    qd_all = np.exp(loc[np.isfinite(loc)])
    gq = _global(src, s, loc)[Q]
    v = np.exp(gq[np.isfinite(gq)])
    p_sh = len(v) / len(Q)
    sh = float(np.mean(v * np.exp(pa[j, k]))) if len(v) else 0.0
    return p_sh * sh + (1.0 - p_sh) * float(np.mean(qd_all * np.exp(fb[k])))


def test_r_m_t1_null_a_every_set_and_symbol_expects_the_common_day_gross(world_src):
    _, _, _, src = world_src
    Gc = _common_gross(src)
    assert src.meta["pools"]["common_day_gross"] == pytest.approx(Gc, rel=1e-12)
    assert src.meta["pools"]["full_days_nonfinite"] == 0
    assert "sym_c" not in src.arr and "dret" not in src.arr                     # no dead array in the shared spec
    pa, fb = np.asarray(src.arr["pool_adj"]), np.asarray(src.arr["fb_adj"])
    sets = _pool_sets(src)
    assert pa.shape == (len(sets), len(src.symbols)) and fb.shape == (len(src.symbols),)
    checked = 0
    for k, s in enumerate(src.symbols):
        loc = _raw(src, s)[4]
        qd_all = np.exp(loc[np.isfinite(loc)])
        if not len(qd_all):
            assert fb[k] == 0.0 and not pa[:, k].any()
            continue
        assert np.exp(fb[k]) == pytest.approx(Gc / qd_all.mean(), rel=1e-12)    # G / M(s)
        gq = _global(src, s, loc)
        for j, Q in enumerate(sets):
            v = np.exp(gq[Q][np.isfinite(gq[Q])])
            if len(v):
                assert np.exp(pa[j, k]) == pytest.approx(Gc / v.mean(), rel=1e-12)   # G / M(Q, s)
            else:
                assert pa[j, k] == 0.0
            assert abs(_null_a_expected(src, k, s, j, Q) / Gc - 1.0) <= 1e-12, (s, j)
            checked += 1
    assert checked > 100


def test_r_m_t2_world_rows_carry_the_day_factor_and_the_draws_did_not_change(world_src):
    _, panel, _, src = world_src
    wa, wb = UC.UWorld(src, "A", 17), UC.UWorld(src, "B", 4)
    assert _sha(wa.pick, np.int64) == DRAWS_58BA59E["pick_A17"]
    assert _sha(np.concatenate([wa.source_days(s) for s in src.symbols]), np.int64) == DRAWS_58BA59E["source_days_A17"]
    assert _sha(wb.flip, np.uint8) == DRAWS_58BA59E["flip_B4"]
    pa, fb, dp = np.asarray(src.arr["pool_adj"]), np.asarray(src.arr["fb_adj"]), np.asarray(src.arr["day_pool"])
    seen = {"shared": 0, "fallback": 0}
    for s in panel[:10]:
        m, k = src.sym(s), src.k[s]
        shift = m["sd0"] - src.D0
        kl = wa.tables(s, trim=False)["klines"]
        ld, act, lrt, full, loc = _raw(src, s)
        gq = _global(src, s, loc)
        sd, ok = wa._source_days(s)
        tns = m["start"] + H * np.arange(m["n"])
        hour = (tns // H) % 24
        o, c = kl["open"].to_numpy(), kl["close"].to_numpy()
        prev = np.r_[m["first_open"], c[:-1]]
        ai = np.nonzero(act)[0]
        ai = ai[ai > 0]                                                          # row 0 keeps G = 1 (the real first open)
        sr = ((sd[ld[ai]] + src.D0) * U.DAY_NS + hour[ai] * H - m["start"]) // H
        gd = ld[ai] + shift
        adj = np.where(ok[ld[ai]], pa[np.where(dp[gd] >= 0, dp[gd], pa.shape[0] - 1), k], fb[k])
        np.testing.assert_allclose((o[ai] / prev[ai]) / np.asarray(src.rows(s, "g"))[sr], np.exp(adj / 24.0), rtol=1e-12)
        for col, name in (("high", "hr"), ("low", "lr"), ("close", "cr")):
            np.testing.assert_allclose(kl[col].to_numpy()[ai] / o[ai], np.asarray(src.rows(s, name))[sr], rtol=1e-12)
        for d in np.unique(ld[ai])[1::5]:
            rows = np.nonzero(ld == d)[0]
            if len(rows) != 24 or not act[rows].all() or rows[0] == 0:
                continue
            a = (pa[dp[d + shift] if dp[d + shift] >= 0 else -1, k]) if ok[d] else fb[k]
            got = float(np.prod(c[rows] / prev[rows]))                          # the world day's gross
            assert abs(got / (float(np.exp(gq[sd[d]])) * float(np.exp(a))) - 1.0) <= 1e-12   # Qd * factor ** 24
            seen["shared" if ok[d] else "fallback"] += 1
    assert seen["shared"] > 20 and seen["fallback"] > 5


def test_r_m_t3_the_finding_in_miniature_every_symbol_expects_the_same_day_gross_under_both_nulls(world_src):
    """The test source's symbols have clearly different sample means (a drift per symbol). Under the 58ba59e
    construction (null A: R-K's c_s; null B: the mirror's centre m) the expected day gross differed across the 44
    symbols: SD of (expected day gross - 1) x 365 = 0.685 under null A (the whole-period set; 0.709 median over the
    pooled months' members) and 0.684 under null B (computed once before the edit; scratch fp8_pre_records.py).
    Under R-M it is G for every symbol: null A by enumeration, null B by the two faces of every day."""
    _, _, _, src = world_src
    Gc = src.meta["pools"]["common_day_gross"]
    sets = _pool_sets(src)
    own, devA = [], 0.0
    for k, s in enumerate(src.symbols):
        loc = _raw(src, s)[4]
        own.append(float(np.mean(np.exp(loc[np.isfinite(loc)]))))
        for j, Q in enumerate(sets):
            devA = max(devA, abs(_null_a_expected(src, k, s, j, Q) / Gc - 1.0))
    assert float(np.std((np.array(own) - 1.0) * 365, ddof=1)) > 0.3            # the sample means do differ
    assert devA <= 1e-12
    w = UC.UWorld(src, "B", 4)
    w2 = UC.UWorld(src, "B", 4)
    w2.flip = ~w.flip                                                            # the other face of every day
    devB, n_days = 0.0, 0
    for s in src.symbols:
        m = src.sym(s)
        ld, act, lrt, full, loc = _raw(src, s)
        faces = []
        for ww in (w, w2):
            c = ww.tables(s, trim=False)["klines"]["close"].to_numpy()
            lg = np.log(c / np.r_[m["first_open"], c[:-1]])
            faces.append(np.exp(np.bincount(ld[act], weights=lg[act], minlength=m["nd"])[:m["nd"]]))
        days = np.nonzero(full)[0]
        days = days[days > ld[0]]                                                # not the first day (G[0] = 1)
        e = float(np.mean((faces[0][days] + faces[1][days]) / 2.0))
        devB = max(devB, abs(e / Gc - 1.0))
        n_days += len(days)
    assert devB <= 1e-12 and n_days > 1000


NULL_B_PIN = "50fe43f66e8c08bfd0b0b03ce5f8c13d309c2a2a4b148ef62530d620ced3e6a7"      # R-M (fix pass 8)
# The pin of fix passes 6 to 7b no longer matches: R-M multiplies every active null B row by its day factor
NULL_B_PIN_58BA59E = "e7ec7d09d5f3dc0176c2f766a1fcc2daf7e28037b1d5686bbc17829e4c96892e"


def _frames_sha(frames) -> str:
    import hashlib
    h = hashlib.sha256()
    for df in frames:
        h.update(np.asarray(df.index.asi8, dtype=np.int64).tobytes())
        for col in df.columns:
            h.update(str(col).encode("ascii"))
            v = df[col].to_numpy()
            v = v.astype(np.uint8) if v.dtype == bool else v.astype(np.float64)
            h.update(np.ascontiguousarray(v).tobytes())
    return h.hexdigest()


def test_r_m_t4_null_b_day_products_flipped_and_unflipped_full_and_partial(world_src):
    _, panel, _, src = world_src
    Gc = src.meta["pools"]["common_day_gross"]
    w = UC.UWorld(src, "B", 4)
    kinds = {"flipped": 0, "unflipped": 0, "partial": 0}
    for s in src.symbols:
        m = src.sym(s)
        ld, act, lrt, full, loc = _raw(src, s)
        kl = w.tables(s, trim=False)["klines"]
        o, c = kl["open"].to_numpy(), kl["close"].to_numpy()
        lg = np.log(c / np.r_[m["first_open"], c[:-1]])                         # log(G_row * CR_row) of the world
        cnt = np.bincount(ld[act], minlength=m["nd"])[:m["nd"]]
        x = np.bincount(ld[act], weights=lrt[act] - m["m"], minlength=m["nd"])[:m["nd"]]
        got = np.exp(np.bincount(ld[act], weights=lg[act], minlength=m["nd"])[:m["nd"]])
        for d in np.nonzero(cnt)[0]:
            if d == ld[0]:
                continue                                                         # the first day: G[0] = 1
            fl = bool(w.flip[d + m["sd0"] - src.D0])
            want = Gc ** (cnt[d] / 24.0) * ((1.0 - np.tanh(x[d])) if fl else (1.0 + np.tanh(x[d])))
            assert abs(got[d] / want - 1.0) <= 1e-12, (s, d, fl)
            kinds["flipped" if fl else "unflipped"] += 1
            kinds["partial"] += int(cnt[d] < 24)
        F = w.flip[ld + m["sd0"] - src.D0] & act                                 # shapes as before R-M
        hr, lr, cr = (np.asarray(src.rows(s, nm)) for nm in ("hr", "lr", "cr"))
        np.testing.assert_allclose(kl["high"].to_numpy()[act] / o[act], np.where(F, 1.0 / lr, hr)[act], rtol=1e-12)
        np.testing.assert_allclose(kl["low"].to_numpy()[act] / o[act], np.where(F, 1.0 / hr, lr)[act], rtol=1e-12)
        np.testing.assert_allclose(c[act] / o[act], np.where(F, 1.0 / cr, cr)[act], rtol=1e-12)
    assert kinds["flipped"] > 100 and kinds["unflipped"] > 100 and kinds["partial"] > 5
    frames = []
    for s in (panel[1], panel[4]):
        t = w.tables(s, trim=False)
        frames += [t["klines"], t["funding"]]
    sha = _frames_sha(frames)
    assert sha == NULL_B_PIN and sha != NULL_B_PIN_58BA59E


def test_r_r_a_version_8_partial_file_is_refused(tmp_path):
    """Was the fix pass 10 protocol test (versions 5 to 7 refused, protocol 8); fix pass 11 raises the protocol to 9
    (R-R). The header names the universe lag count and the speed limit instead of perm_n and carries the options."""
    h8 = UC.run_header({"semantic": "s" * 64}, "r" * 64, list(UC.FAMILIES), 2, 2, True)
    assert h8["protocol_version"] == UC.PROTOCOL_VERSION == 9
    assert h8["g6_lags"] == C.UNIVERSE_G6_LAGS and h8["g6_memory_max"] == C.UNIVERSE_G6_MEMORY_MAX and "perm_n" not in h8
    assert h8["opts"]["u_lags"] == UC.OPTS.u_lags
    for old in (5, 6, 7, 8):
        p = tmp_path / f"v{old}.partial.jsonl"
        UC.Partial(p, dict(h8, protocol_version=old), log=lambda *a: None)
        with pytest.raises(UC.PartialMismatch):
            UC.Partial(p, h8, log=lambda *a: None)


def test_7b_3_the_advisory_names_a_power_or_level_that_is_not_a_number(monkeypatch):
    gates = {g: True for g in ("G1", "G2", "G3", "G4", "G5", "G7", "G10")} | {"G6": None, "G8": None}
    rows = [{"speed": s, "level": 1.5, "world_seed": i, "status": "evaluated", "val_sharpe": 1.5, "perm_p": 0.001,
             "rho": 0.1, "gates": dict(gates)} for s in UC.USPEEDS for i in range(10)]

    def adv(edit):
        oracle = {n: {"summary": UC.oracle_summary(rows)} for n in ("A", "B")}
        edit(oracle)
        return UC.oracle_advisory(oracle)

    lines, stop = adv(lambda o: None)
    assert stop == [] and len(lines) == 4

    def both(o):
        o["A"]["summary"]["fast|1.5"]["by_threshold"]["0.1"]["power"] = float("nan")
        o["B"]["summary"]["slow|1.5"]["mean_val_sharpe"] = float("nan")
    lines, stop = adv(both)
    assert stop == ["null A fast: power at 0.1 below 0.5", "null B slow: level 1.5 achieved outside its bound"]
    assert any("nan" in ln for ln in lines)

    def exact(o):
        o["A"]["summary"]["fast|1.5"]["by_threshold"]["0.1"]["power"] = C.POWER_MIN
        o["B"]["summary"]["slow|1.5"]["mean_val_sharpe"] = 1.625
    monkeypatch.setattr(UC.CB, "RHO_BOUND", 0.125)
    assert adv(exact)[1] == []                                                   # exactly at both bounds: no STOP


# ---------------------------------------------------------------- fix pass 8: FP8-4 the null advisory (log only)

_GATES8 = {g: True for g in ("G1", "G2", "G3", "G4", "G5", "G7", "G10")} | {"G6": None, "G8": None}


def _nrows(null, worlds, passes=None, start=0):
    """worlds x families null rows; passes {family: [perm_p of its first worlds]} (the others 0.5)."""
    rows = []
    for i in range(start, start + worlds):
        for f in UC.FAMILIES:
            ps = (passes or {}).get(f, [])
            rows.append({"null": null, "family": f, "world_seed": i, "submitted": True, "status": "evaluated",
                         "params": {}, "val_sharpe": 0.1, "perm_p": ps[i - start] if i - start < len(ps) else 0.5,
                         "gates": dict(_GATES8)})
    return rows


def _oracle8(slow_a_perm_p=0.001):
    out = {}
    for n in ("A", "B"):
        rows = [{"speed": s, "level": 1.5, "world_seed": i, "status": "evaluated", "val_sharpe": 1.5, "rho": 0.1,
                 "perm_p": slow_a_perm_p if (n == "A" and s == "slow") else 0.001, "gates": dict(_GATES8)}
                for s in UC.USPEEDS for i in range(10)]
        out[n] = {"summary": UC.oracle_summary(rows)}
    return out


def test_fp8_4_the_null_advisory_reads_the_counts_so_far():
    fams, W = list(UC.FAMILIES), 100                     # caps: pooled 0.03 x 300 = 9 passes, a family 0.06 x 100 = 6
    mom = "ucal_xs_momentum"
    lines, stop = UC.null_advisory({"A": _nrows("A", 50, {mom: [0.01] * 6}), "B": []}, W, fams, _oracle8())
    assert stop == [] and len(lines) == 2 and "50 of 100 worlds" in lines[0]                 # nothing dead: silent
    lines, stop = UC.null_advisory({"A": _nrows("A", 50, {mom: [0.01] * 7}), "B": []}, W, fams, _oracle8())
    assert len(stop) == 1 and stop[0].startswith("every G6 threshold is already dead") and "DEAD" in lines[0]
    lines, stop = UC.null_advisory({"A": [], "B": _nrows("B", 40, {f: [0.01] * 4 for f in fams[:2]} |
                                                         {fams[2]: [0.01, 0.01]})}, W, fams, _oracle8())
    assert stop and stop[0].startswith("every G6 threshold is already dead")                # pooled 10 > 9
    slow_low = _oracle8(slow_a_perm_p=0.04)              # null A slow: power 0 at 0.025, 1 at 0.05 and 0.10
    lines, stop = UC.null_advisory({"A": _nrows("A", 30, {mom: [0.04] * 7}), "B": []}, W, fams, slow_low)
    assert stop == ["largest threshold not dead 0.025: null A slow: power at 0.025 below 0.5"]
    lines, stop = UC.null_advisory({"A": _nrows("A", 30, {mom: [0.08] * 7}), "B": []}, W, fams, slow_low)
    assert stop == []                                    # only 0.10 dead; power at 0.05 is fine: silent
    bad = _nrows("A", 2)
    bad[1]["gates"] = {}
    with pytest.raises(ValueError):
        UC.null_advisory({"A": bad, "B": []}, W, fams, _oracle8())


def _fake_null_run(monkeypatch, rows_for, malformed_first=False):
    """calibrate_run with fabricated tasks: power rows at full power; every null task fills the partial's
    done mapping and calls on_progress (once with a malformed row in it when malformed_first)."""
    class Part:
        done = {}

    def fake_run_tasks(pool, partial, kind, arglist, log, label, on_progress=None):
        if kind == "power":
            return _power_rows(arglist[0][0], 0.001, seeds=range(len(arglist)))
        out = []
        for null, seed in arglist:
            rows = rows_for(null, seed)
            key = UC.task_key("null", [null, seed])
            if malformed_first:
                broken = [dict(r) for r in rows]
                broken[0]["gates"] = {}
                partial.done[key] = broken
                on_progress()
            partial.done[key] = rows
            out.append(rows)
            if on_progress is not None:
                on_progress()
        return out
    monkeypatch.setattr(UC, "run_tasks", fake_run_tasks)
    monkeypatch.setattr(UC, "tune_rho", lambda pool, partial, null, speed, seeds, log: {"1.5": {"rho": 0.1}})
    logs = []
    nulls, oracle = UC.calibrate_run(None, Part(), list(UC.FAMILIES), 20, 4, logs.append)
    return logs, nulls


def test_fp8_4_calibrate_run_logs_the_null_advisory_once_with_the_counts(monkeypatch):
    mom = "ucal_xs_momentum"
    logs, nulls = _fake_null_run(monkeypatch, lambda null, seed: _nrows(null, 1, {mom: [0.01]}, start=seed))
    adv = [ln for ln in logs if ln.startswith("ADVISORY: the seal rule will STOP whatever the rest of the null")]
    assert len(adv) == 1 and "every G6 threshold is already dead" in adv[0]
    i = logs.index(adv[0])
    assert logs[i - 3].startswith("  null advisory, null A") and logs[i - 2].startswith("  null advisory, null B")
    assert len(nulls["A"]["rows"]) == 60 and not any("unavailable" in ln for ln in logs)
    quiet, _ = _fake_null_run(monkeypatch, lambda null, seed: _nrows(null, 1, start=seed))
    assert not any("null advisory" in ln or "rest of the null" in ln for ln in quiet)       # nothing dead: silent


def test_fp8_4_a_malformed_row_makes_the_advisory_unavailable_once_and_the_run_goes_on(monkeypatch):
    logs, nulls = _fake_null_run(monkeypatch, lambda null, seed: _nrows(null, 1, start=seed), malformed_first=True)
    un = [ln for ln in logs if ln.startswith("null advisory unavailable: ")]
    assert len(un) == 1 and un[0].startswith("null advisory unavailable: ValueError: ") and "gate G1 is missing" in un[0]
    assert len(nulls["A"]["rows"]) == 60 and len(nulls["B"]["rows"]) == 60
    _, clean = _fake_null_run(monkeypatch, lambda null, seed: _nrows(null, 1, start=seed))
    assert nulls == clean                                                        # the run's results are unchanged


def test_fp8_4_the_pooled_bound_alone_makes_a_threshold_dead():
    """Case f: no single family over its count (4, 4 and 2 passes, a family's cap 6), the three together over
    NULL_PASS_MAX x worlds x families (10 > 9)."""
    fams, W = list(UC.FAMILIES), 100
    split = {fams[0]: [0.08] * 4, fams[1]: [0.08] * 4, fams[2]: [0.08] * 2}       # pass at 0.10 only
    lines, stop = UC.null_advisory({"A": _nrows("A", 40, split), "B": []}, W, fams, _oracle8())
    assert "at 0.1: 10 (cap 9), per family " in lines[0] and lines[0].count("DEAD (pooled)") == 1
    assert "at 0.05: 0 (cap 9)" in lines[0] and stop == []                       # 0.05 still open, power fine
    split = {f: [0.01] * len(v) for f, v in split.items()}                         # pass at every threshold
    lines, stop = UC.null_advisory({"A": _nrows("A", 40, split), "B": []}, W, fams, _oracle8())
    assert lines[0].count("DEAD (pooled)") == 3 and stop and stop[0].startswith("every G6 threshold is already dead")


# ---------------------------------------------------------------- fix pass 10: R-O mark wicks in the null worlds

CAP = pd.Timestamp(C.VAL_END, tz="UTC")


def _active_ts(kl, after, n=1):
    sel = (kl.index >= pd.Timestamp(after, tz="UTC")) & ~kl["is_gap"].to_numpy() & (kl["trades"].to_numpy() > 0)
    return list(kl.index[sel][:n])


def _ohlc(kl):
    mk = kl[["open", "high", "low", "close"]].copy()
    mk["samples"] = 3600.0
    return mk


def _mark_tables():
    """The test source's tables with mark bars that differ from the last-price bars. Roles: wide (mark wicks 1%
    outside the last-price wicks, no mark row at 05:00 of any day), bad (invalid mark rows: low 0, high NaN, high
    below low, open <= 0, and one missing row), empty (no mark bar at all), flip_mark / flip_nomark (one active VAL
    bar whose last-price low is open / 500; its mark bar ordinary, low / open 0.9 and high / open 1.02; for
    flip_nomark the mark row is removed)."""
    tables, panel, special = _real_tables()
    tables = {s: dict(t) for s, t in tables.items()}
    live = [s for s in panel if s != special and len(_active_ts(tables[s]["klines"], "2022-08-01", 5)) == 5]
    roles = dict(zip(("wide", "bad", "empty", "flip_mark", "flip_nomark"), live[:5]))
    kl = tables[roles["wide"]]["klines"]
    mk = _ohlc(kl)
    mk["high"], mk["low"] = mk["high"] * 1.01, mk["low"] * 0.99
    tables[roles["wide"]]["mark_klines"] = mk[mk.index.hour != 5]
    kl = tables[roles["bad"]]["klines"]
    mk = _ohlc(kl)
    ts = _active_ts(kl, "2022-08-01", 5)
    mk.loc[ts[0], "low"] = 0.0
    mk.loc[ts[1], "high"] = np.nan
    mk.loc[ts[2], ["high", "low"]] = [mk.loc[ts[2], "low"] * 0.99, mk.loc[ts[2], "high"] * 1.01]
    mk.loc[ts[3], "open"] = -1.0
    tables[roles["bad"]]["mark_klines"] = mk.drop(index=ts[4])
    roles["bad_ts"] = ts
    tables[roles["empty"]]["mark_klines"] = _ohlc(tables[roles["empty"]]["klines"]).iloc[:0]
    for role in ("flip_mark", "flip_nomark"):
        kl = tables[roles[role]]["klines"].copy()
        t0 = _active_ts(kl, "2023-03-01 10:00")[0]
        o = kl.loc[t0, "open"]
        kl.loc[t0, "low"] = o / 500.0                                       # a last-price bad print
        mk = _ohlc(kl)
        mk.loc[t0, ["open", "high", "low"]] = [o, 1.02 * o, 0.9 * o]        # an ordinary mark bar
        tables[roles[role]] = dict(tables[roles[role]], klines=kl,
                                   mark_klines=mk if role == "flip_mark" else mk.drop(index=t0))
        roles[role + "_ts"] = t0
    return tables, panel, roles


@pytest.fixture(scope="module")
def mark_src():
    tables, panel, roles = _mark_tables()
    return tables, panel, roles, UC.USource.build(panel, lambda x: tables[x])


def test_r_o_t1_source_mark_ratios_are_the_liquidation_ratios_where_the_mark_bar_is_valid(mark_src):
    tables, panel, roles, src = mark_src
    for role in ("wide", "bad", "empty", "flip_mark", "flip_nomark"):
        s = roles[role]
        kl = tables[s]["klines"]
        kl = kl[kl.index <= CAP]
        mk = tables[s]["mark_klines"]
        lq = D.liquidation_ratios(kl, mk if len(mk) else None)
        has = lq["has_mark"].to_numpy()
        hm, lm = np.asarray(src.rows(s, "hm")), np.asarray(src.rows(s, "lm"))
        assert len(hm) == len(kl) and np.array_equal(np.isfinite(hm), has) and np.array_equal(np.isfinite(lm), has)
        assert np.array_equal(hm[has], lq["up"].to_numpy()[has]) and np.array_equal(lm[has], lq["dn"].to_numpy()[has])
    s = roles["bad"]
    pos = src.sym(s)["start"]
    for t in roles["bad_ts"]:                                              # low 0, high NaN, high < low, open <= 0,
        i = (t.value - pos) // H                                           # missing row: no mark ratios
        assert np.isnan(src.rows(s, "hm")[i]) and np.isnan(src.rows(s, "lm")[i])
    assert not np.isfinite(src.rows(roles["empty"], "hm")).any()          # an empty mark table: NaN everywhere
    s = roles["wide"]
    m = src.sym(s)
    hour = ((m["start"] + H * np.arange(m["n"])) // H) % 24
    act = np.asarray(src.rows(s, "act"), dtype=bool)
    hm, hr = np.asarray(src.rows(s, "hm")), np.asarray(src.rows(s, "hr"))
    assert np.isnan(hm[hour == 5]).all() and np.isfinite(hm[hour != 5]).all()
    assert np.all(hm[act & (hour != 5)] > hr[act & (hour != 5)])            # the mark wick, not the last-price one
    liq = src.meta["liq"]
    assert liq["active_rows"] == int(sum(np.asarray(src.rows(x, "act"), dtype=bool).sum() for x in src.symbols))
    assert liq["active_rows_without_mark"] > 0 and liq["min_low_over_open"] <= 0.9 and liq["max_high_over_open"] >= 1.02
    spec, blocks = src.to_shared()                                         # the two row fields go through
    try:
        twin, mine = UC.USource.from_shared(spec)
        for k in ("hm", "lm"):
            assert np.array_equal(src.arr[k], twin.arr[k], equal_nan=True)
        for x in mine:
            x.close()
    finally:
        for x in blocks:
            x.close()
            x.unlink()
    s0 = roles["wide"]
    with pytest.raises(KeyError, match="mark_klines"):
        UC.USource.build([s0], lambda x: {"klines": tables[x]["klines"], "funding": tables[x]["funding"]})


def _liq_and_short(src, s, w, t0):
    """(liq_up, liq_dn) of FullPanel at bar t0 of a world, and whether a book 50% short s from 200 bars before t0
    is liquidated by the universe engine."""
    from omr import engine as E
    fp = UP.FullPanel(UC.world_udata(src, "B", 4, world=w), "top30", symbols=[s])
    i = int(np.searchsorted(fp.ns, t0.value))
    assert fp.ns[i] == t0.value and fp.active[i, 0]
    up, dn = fp.col("liq_up"), fp.col("liq_dn")
    lo, hi = i - 200, i + 3
    av = fp.active[lo:hi]
    out = E.run_arrays_u(fp.col("open")[lo:hi], fp.col("close")[lo:hi], av, dn[lo:hi], up[lo:hi],
                         np.zeros(av.shape), np.where(av, -0.5, 0.0))
    return float(up[i, 0]), float(dn[i, 0]), bool(out[7] >= 0)


def test_r_o_t2_null_b_a_last_price_bad_print_with_an_ordinary_mark_bar_no_longer_liquidates(mark_src):
    tables, panel, roles, src = mark_src
    for role in ("flip_mark", "flip_nomark"):
        s, t0 = roles[role], roles[role + "_ts"]
        day = t0.value // U.DAY_NS - src.D0
        for flipped in (True, False):
            w = UC.UWorld(src, "B", 4)
            w.flip = w.flip.copy()
            w.flip[day] = flipped
            up, dn, liquidated = _liq_and_short(src, s, w, t0)
            if role == "flip_mark":
                want = (1 / 0.9, 1 / 1.02) if flipped else (1.02, 0.9)
                assert up == pytest.approx(want[0], rel=1e-12) and dn == pytest.approx(want[1], rel=1e-12)
                assert not liquidated                                      # the mark bar decides, as in the real run
            elif flipped:
                assert up == pytest.approx(500.0, rel=1e-9) and liquidated    # no mark row: the documented fallback


def _src_rows(src, s, w):
    m = src.sym(s)
    sd, ok = w._source_days(s)
    tns = m["start"] + H * np.arange(m["n"])
    ld, hour = tns // U.DAY_NS - m["sd0"], (tns // H) % 24
    ai = np.nonzero(np.asarray(src.rows(s, "act"), dtype=bool))[0]
    sr = ((sd[ld[ai]] + src.D0) * U.DAY_NS + hour[ai] * H - m["start"]) // H
    return ai, sr, ok[ld[ai]]


def test_r_o_t3_null_a_wicks_are_the_drawn_source_rows_mark_ratios(mark_src):
    tables, panel, roles, src = mark_src
    w = UC.UWorld(src, "A", 17)
    seen = {"shared_mark": 0, "fallback_mark": 0, "last_price": 0}
    for s in (roles["wide"], roles["bad"]):
        t = w.tables(s, trim=False)
        lq = D.liquidation_ratios(t["klines"], t["mark_klines"])
        ai, sr, shared = _src_rows(src, s, w)
        hm, lm, hr, lr = (np.asarray(src.rows(s, x)) for x in ("hm", "lm", "hr", "lr"))
        mark = np.isfinite(hm[sr])
        np.testing.assert_allclose(lq["up"].to_numpy()[ai], np.where(mark, hm[sr], hr[sr]), rtol=1e-15)
        np.testing.assert_allclose(lq["dn"].to_numpy()[ai], np.where(mark, lm[sr], lr[sr]), rtol=1e-15)
        seen["shared_mark"] += int((mark & shared).sum())
        seen["fallback_mark"] += int((mark & ~shared).sum())
        seen["last_price"] += int((~mark).sum())
    assert all(v > 50 for v in seen.values()), seen


def test_r_o_t4_a_null_b_world_without_a_flip_reads_the_source_liquidation_ratios(mark_src):
    """Tolerance: the world's mark high is open * hm and the check divides by the world open again (the world open
    is not the source open: R-M and the cumulated path), so two roundings separate the two ratios: rtol 1e-15."""
    tables, panel, roles, src = mark_src
    w = UC.UWorld(src, "B", 4)
    w.flip = np.zeros_like(w.flip)
    for role in ("wide", "bad", "empty", "flip_mark", "flip_nomark"):
        s = roles[role]
        t = w.tables(s, trim=False)
        lqw = D.liquidation_ratios(t["klines"], t["mark_klines"])
        kl = tables[s]["klines"]
        mk = tables[s]["mark_klines"]
        lqs = D.liquidation_ratios(kl[kl.index <= CAP], mk if len(mk) else None)
        act = np.asarray(src.rows(s, "act"), dtype=bool)
        for c in ("up", "dn"):
            np.testing.assert_allclose(lqw[c].to_numpy()[act], lqs[c].to_numpy()[act], rtol=1e-15)


WORLD_PINS_8BFABC4 = {                                  # the test source, every panel symbol, untrimmed, before R-O
    "A17_klines": "b067dcd6e52fd7804558cd46240a086aa1cc2008f21500be831b3b2f3a1bfe64",
    "A17_mark": "04d24a862e1ffa5f9088bc5aac185a09311acb63d1ef6ee4c1f5b90936b7c623",
    "B4_klines": "cf215d0cd2bcc5831e16393b11f7cc3baa0e54385b1baf73c15df93879277e1c",
    "B4_mark": "279efe42c51a64d1d84b1f2136ad8ac4c1547e2ef040519be38668b201b80d74"}


def test_r_o_t5_world_klines_are_unchanged(world_src):
    """The klines of every world are what they were at 8bfabc4 (and NULL_B_PIN, klines and funding, still holds).
    On this source the mark bars ARE its last-price bars, so the world mark tables did not change either."""
    _, _, _, src = world_src
    for null, seed in (("A", 17), ("B", 4)):
        w = UC.UWorld(src, null, seed)
        tabs = [w.tables(s, trim=False) for s in src.symbols]
        assert _frames_sha([t["klines"] for t in tabs]) == WORLD_PINS_8BFABC4[f"{null}{seed}_klines"]
        assert _frames_sha([t["mark_klines"] for t in tabs]) == WORLD_PINS_8BFABC4[f"{null}{seed}_mark"]


def test_r_o_t6_a_row_without_trades_keeps_a_flat_mark_bar_and_index_is_mark(world_src):
    tables, panel, special, src = world_src
    lo, hi = pd.Timestamp("2021-03-03 05:00", tz="UTC"), pd.Timestamp("2021-03-03 09:00", tz="UTC")
    real = tables[special]["mark_klines"]
    assert (real.loc[lo:hi, "high"] > real.loc[lo:hi, "low"]).all()       # the source has mark wicks there
    for null, seed in (("A", 17), ("B", 4)):
        t = UC.UWorld(src, null, seed).tables(special, trim=False)
        assert t["index_klines"] is t["mark_klines"]
        mk = t["mark_klines"].loc[lo:hi]
        assert len(mk) == 5
        for c in ("high", "low", "close"):
            assert np.array_equal(mk[c].to_numpy(), mk["open"].to_numpy())  # flat (left as it is, R-O)


def test_r_o_t8_tune_rho_records_the_liquidated_tuning_books(monkeypatch):
    def fake(pool, partial, kind, arglist, log, label, on_progress=None):
        out = []
        for i, (null, seed, speed, rhos) in enumerate(arglist):
            vals = [5.0 * r for r in rhos]                                  # Sharpe = 5 rho
            if len(rhos) == 1 and i < 2:
                vals = [float("-inf") if i == 0 else float("nan")]           # two books not finite at the chosen rho
            out.append(vals)
        return out
    monkeypatch.setattr(UC, "run_tasks", fake)
    logs = []
    out = UC.tune_rho(None, None, "B", "slow", [1, 2, 3, 4], logs.append)
    assert out["1.5"]["liquidated_books"] == 2 and out["1.5"]["books"] == 4
    assert out["1.5"]["achieved_mean_val_sharpe"] == pytest.approx(5.0 * out["1.5"]["rho"])
    assert any("2 of 4 tuning books liquidated" in ln for ln in logs)


def test_r_o_t9_the_real_source_loader_reads_mark_klines_through_the_logged_handle(monkeypatch):
    """The real-source loader on in-memory tables (no disk fixture exists for it): datasets.load_raw and the symbol
    table are replaced by fakes that record every call; a symbol without a mark file gets an empty table."""
    tables, panel, special = _real_tables()
    handle = object()
    nomark = panel[4]
    calls = []

    def fake_load_raw(ds, s, upto=None, handle=None, cache=True):
        calls.append((ds, s, upto, handle, cache))
        if ds == "mark_klines" and s == nomark:
            raise FileNotFoundError(s)
        return tables[s][ds]
    monkeypatch.setattr(UC.D, "load_raw", fake_load_raw)
    monkeypatch.setattr(UC.U, "load_symbols", lambda: {"symbols": {s: {"until": None} for s in tables}})
    monkeypatch.setattr(UC.U, "crypto_symbols", lambda table: sorted(table["symbols"]))
    src = UC.load_source(handle, log=lambda *a: None)
    assert nomark in src.symbols
    marks = [c for c in calls if c[0] == "mark_klines"]
    assert sorted(c[1] for c in marks) == sorted(src.symbols)               # every panel symbol's mark bars
    assert all(c[2] == "val_end" and c[3] is handle and c[4] is False for c in calls)   # the logged handle
    assert not np.isfinite(src.rows(nomark, "hm")).any()
    assert np.isfinite(src.rows(src.symbols[0] if src.symbols[0] != nomark else src.symbols[1], "hm")).any()


def _ended(rows, status):
    for r in rows:
        r["status"] = status
        r.pop("gates", None)
        r.pop("perm_p", None)
        if status == "not_submitted":
            r["submitted"] = False
    return rows


def test_r_r_t8_the_null_advisory_boundaries():
    """R-R (g): designed 3 x 100 = 300 pairs under null A; every boundary of the advisory, one pair inside and one
    beyond."""
    fams, W = list(UC.FAMILIES), 100
    by = lambda rows, f: [r for r in rows if r["family"] == f]                      # noqa: E731

    def dead(rows):
        return UC._null_dead({"A": rows, "B": []}, W, fams)[1]
    rows = _nrows("A", 100)
    _ended(by(rows, fams[0])[:50], "liquidated")                            # a family at 50 of 100 still reachable
    assert dead(rows) == set()
    _ended(by(rows, fams[0])[50:51], "not_submitted")
    assert dead(rows) == set(C.G6_GRID)                                     # 49 of 100 at most: below its floor
    rows = _nrows("A", 100)
    for f in fams:
        _ended(by(rows, f)[:25], "liquidated")                              # 225 of 300 at most: the null floor
    assert dead(rows) == set()
    _ended(by(rows, fams[1])[25:26], "liquidated")
    assert dead(rows) == set(C.G6_GRID)
    rows = _nrows("A", 100)
    _ended(by(rows, fams[2])[:9], "kernel_fault")                           # 9 faults of 300 designed: at the bound
    assert dead(rows) == set()
    _ended(by(rows, fams[2])[9:10], "weird")
    assert dead(rows) == set(C.G6_GRID)
    rows = _nrows("A", 100)
    for f in fams:
        _ended(by(rows, f)[:25], "liquidated")                              # 225 evaluated at most: pooled cap 6.75
    passers = [by(rows, f)[25 + i] for f in fams for i in range(2)]          # 6 passes (2 per family) at 0.10 only
    for r in passers:
        r["perm_p"] = 0.08
    assert dead(rows) == set()
    by(rows, fams[0])[27]["perm_p"] = 0.08                                   # 7 of 225: the pooled rate is lost
    assert dead(rows) == {0.1}
    rows = _nrows("A", 100)
    for f in fams:
        _ended(by(rows, f)[:25], "liquidated")
    for r in by(rows, fams[0])[25:29]:
        r["perm_p"] = 0.04                                                  # family 4 of 75 at most: cap 4.5
    assert dead(rows) == set()
    by(rows, fams[0])[29]["perm_p"] = 0.04                                   # 5 of 75 (pooled 5 of 225 still fine)
    assert dead(rows) == {0.05, 0.1}


def test_r_r_t8_the_null_advisory_never_calls_a_threshold_dead_that_the_completed_rows_could_still_qualify(monkeypatch):
    """Enumeration: one family, 3 worlds; every outcome of each pair (a pass at 0.025, an evaluated pair without a pass,
    liquidated, not submitted, a fault), every prefix of rows finished so far, every completion of the rest. Wherever
    the advisory calls a threshold dead, no completion qualifies it under the rule (decide, null B perfect)."""
    import itertools
    monkeypatch.setattr(C, "NULL_PASS_MAX", 0.34)                           # bounds a 3-world null can meet
    monkeypatch.setattr(C, "FAMILY_PASS_MAX", 0.5)
    monkeypatch.setattr(C, "NULL_FAULT_MAX", 0.34)
    fam, W = "f", 3
    outcomes = ("pass", "fail", "liquidated", "not_submitted", "fault")

    def row(i, o, null="A"):
        r = {"null": null, "family": fam, "world_seed": UC.SEEDS[null] + i, "submitted": True, "status": "evaluated",
             "params": {}, "val_sharpe": 0.1, "perm_p": 0.01 if o == "pass" else 0.5, "gates": dict(_GATES8)}
        if o in ("liquidated", "not_submitted", "fault"):
            _ended([r], {"fault": "kernel_fault"}.get(o, o))
        return r
    good_b = [row(i, "fail", "B") for i in range(W)]
    oracle = _oracle8()

    def qualifies(final):
        nulls = {"A": {"summary": CB.null_summary(final, [fam], W)}, "B": {"summary": CB.null_summary(good_b, [fam], W)}}
        return set(CB.decide(nulls, oracle)["qualifying"])
    seen_dead = 0
    for full in itertools.product(outcomes, repeat=W):
        for j in range(W + 1):
            prefix = [row(i, full[i]) for i in range(j)]
            dead = UC._null_dead({"A": prefix, "B": []}, W, [fam])[1]
            if not dead:
                continue
            seen_dead += 1
            for rest in itertools.product(outcomes, repeat=W - j):
                final = prefix + [row(j + i, o) for i, o in enumerate(rest)]
                assert not (dead & qualifies(final)), (full[:j], rest, dead)
    assert seen_dead > 50


def test_r_r_t7_a_real_universe_run_with_reduced_sizes_is_refused_before_any_data_access(monkeypatch):
    from omr import access, data, kernel_lock

    def boom(*a, **k):
        raise AssertionError("data, the kernel lock or a source was read")
    for mod, name in ((kernel_lock, "verify"), (data, "load_manifest"), (data, "validation_ok"),
                      (access, "for_calibration"), (UC, "load_source"), (UC, "synthetic_source")):
        monkeypatch.setattr(mod, name, boom)
    for argv in (["--worlds", "10"], ["--oracle-worlds", "5"], ["--worlds", "10", "--workers", "0"]):
        with pytest.raises(SystemExit) as e:
            UC.main(argv)
        assert "protocol's sizes" in str(e.value)


# ---------------------------------------------------------------- fix pass 10: R-Q in the universe unit


def _rq_universe(monkeypatch, sharpes):
    draws, calls, it = [], [], iter(sharpes)
    fam = "ucal_xs_momentum"

    class FakeBlocked:
        def __init__(self, *a, **k):
            pass
    monkeypatch.setattr(UC, "build_uworld", lambda src, null, seed: None)
    monkeypatch.setattr(UC, "dev_view", lambda src, null, seed: None)
    monkeypatch.setattr(UP, "Blocked", FakeBlocked)
    monkeypatch.setattr(UP, "screen_dev_u", lambda prog, q, fp: (draws.append(dict(q)), {"ok": True, "W": None})[1])
    monkeypatch.setattr(UC, "dev_sharpe_u", lambda fp, W: next(it))
    monkeypatch.setattr(UP, "stage1_u", lambda *a, **k: (calls.append("stage1"), {"ok": True})[1])
    monkeypatch.setattr(UP, "stage2_u", lambda *a, **k: (calls.append("stage2"),
                                                         {"status": "liquidated", "reason": "fake"})[1])
    monkeypatch.setattr(UC, "_W", {"src": None, "handle": None, "progs": {fam: L.parse_file(UC.family_path(fam))}})
    rows = UC.task_null(("A", 11000))
    assert len(rows) == 1 and len(draws) == CB.N_DRAWS
    return rows[0], draws, calls


def test_r_q_universe_tq1_to_tq4(monkeypatch):
    n = CB.N_DRAWS
    row, draws, calls = _rq_universe(monkeypatch, [float("-inf")] * n)                   # TQ1
    assert row["submitted"] is False and row["status"] == "not_submitted" and calls == []
    assert row["stage1"] == {"passed": n, "dev_liquidated": n}
    s = CB.null_summary([row], ["ucal_xs_momentum"])                                      # TQ4
    assert s["n_not_submitted"] == 1 and s["n_submitted"] == 0 and s["n_submitted_fault"] == 0
    row, draws, calls = _rq_universe(monkeypatch, [float("-inf"), 0.5] + [0.1] * (n - 2))   # TQ2
    assert row["submitted"] and row["params"] == draws[1] and calls == ["stage1", "stage2"]
    assert row["stage1"] == {"passed": n, "dev_liquidated": 1}
    row, draws, _ = _rq_universe(monkeypatch, [float("nan"), 0.2, 0.4] + [0.1] * (n - 3))  # TQ3
    assert row["params"] == draws[2] and row["stage1"] == {"passed": n, "dev_sharpe_not_finite": 1}
