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
        for k in src.arr:
            assert np.array_equal(src.arr[k], twin.arr[k]) and src.arr[k].dtype == twin.arr[k].dtype
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
    monkeypatch.setattr(UC, "OPTS", PL.Opts(include_g8=False, keep_detail=False, perm_n=10, jitter_n=2,
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
    res = UP.evaluate_weights_u(W, ob.bu, 1, PL.Opts(perm_n=20, include_g8=False), val_handle, 0.1)
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
    monkeypatch.setattr(UC, "OPTS", PL.Opts(include_g8=False, keep_detail=False, perm_n=5, jitter_n=1,
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
    assert "resuming: 3 finished tasks" in capsys.readouterr().out
    a, b = _artifact(whole), _artifact(cut)
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
