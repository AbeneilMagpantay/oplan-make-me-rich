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

    def fake_run_tasks(pool, partial, kind, arglist, log, label):
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
            nulls[null] = {"rows": rows, "summary": CB.null_summary(rows, fams)}
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


# ---------------------------------------------------------------- fix pass 7: R-K one expected daily return (null A)


def _sym_days(src, s):
    """(global full mask, global day returns with NaN where not full or not finite) of symbol s."""
    m = src.sym(s)
    shift = m["sd0"] - src.D0
    fl = np.asarray(src.arr["full"][m["full_off"]:m["full_off"] + m["nd"]], dtype=bool)
    dr = np.asarray(src.arr["dret"][m["full_off"]:m["full_off"] + m["nd"]], dtype=np.float64)
    full = np.zeros(src.ND, dtype=bool)
    ret = np.full(src.ND, np.nan)
    n = min(len(fl), src.ND - shift)
    full[shift:shift + n] = fl[:n]
    ret[shift:shift + n] = np.where(fl[:n] & np.isfinite(dr[:n]), dr[:n], np.nan)
    return full, ret


def _pool_sets(src):
    off, days = np.asarray(src.arr["pool_off"]), np.asarray(src.arr["pool_days"])
    sets = [days[off[j]:off[j + 1]] for j in range(len(off) - 1)]
    return sets + [np.arange(src.meta["pool_lo"], src.ND)]


def test_r_k_t1_every_set_and_symbol_has_the_symbols_one_mean_after_the_adjustment(world_src):
    _, _, _, src = world_src
    adj, c = np.asarray(src.arr["pool_adj"]), np.asarray(src.arr["sym_c"])
    sets = _pool_sets(src)
    assert adj.shape == (len(sets), len(src.symbols)) and src.meta["pools"]["full_days_nonfinite"] == 0
    checked = 0
    for k, s in enumerate(src.symbols):
        full, ret = _sym_days(src, s)
        assert c[k] == pytest.approx(float(np.nanmean(ret)), abs=1e-12)          # c_s over ALL its full days
        for j, Q in enumerate(sets):
            v = ret[Q][np.isfinite(ret[Q])]
            if len(v):
                assert abs(float(np.mean(v)) + adj[j, k] - c[k]) <= 1e-12
                checked += 1
            else:
                assert adj[j, k] == 0.0
    assert checked > 100


def test_r_k_t2_world_days_carry_the_adjustment_on_the_shared_branch_only(world_src):
    _, panel, _, src = world_src
    w = UC.UWorld(src, "A", 17)
    adj = np.asarray(src.arr["pool_adj"])
    dp = np.asarray(src.arr["day_pool"])
    seen = {"shared": 0, "fallback": 0}
    for s in panel[:10]:
        m, k = src.sym(s), src.k[s]
        shift = m["sd0"] - src.D0
        kl = w.tables(s, trim=False)["klines"]
        act = np.asarray(src.rows(s, "act"), dtype=bool)
        sd, ok = w._source_days(s)
        _, ret = _sym_days(src, s)
        tns = m["start"] + U.HOUR_NS * np.arange(m["n"])
        ld = tns // U.DAY_NS - m["sd0"]
        close = kl["close"].to_numpy()
        for d in np.unique(ld)[1:][::9]:                                       # never the first row's day
            rows = np.nonzero(ld == d)[0]
            if len(rows) != 24 or not act[rows].all() or rows[0] == 0:
                continue
            got = float(np.log(close[rows[-1]]) - np.log(close[rows[0] - 1]))
            gsrc = int(sd[d])
            if ok[d]:
                q = dp[d + shift] if dp[d + shift] >= 0 else adj.shape[0] - 1
                want = ret[gsrc] + adj[q, k]
                seen["shared"] += 1
            else:
                want = ret[gsrc]
                seen["fallback"] += 1
            assert abs(got - want) <= 1e-9, (s, d, ok[d])
        ai = np.nonzero(act)[0][1:]                                              # (c) every active row's shape
        hour = (tns // U.HOUR_NS) % 24
        sr = ((sd[ld[ai]] + src.D0) * U.DAY_NS + hour[ai] * U.HOUR_NS - m["start"]) // U.HOUR_NS
        o = kl["open"].to_numpy()[ai]
        for col, name in (("high", "hr"), ("low", "lr"), ("close", "cr")):
            np.testing.assert_allclose(kl[col].to_numpy()[ai] / o, np.asarray(src.rows(s, name))[sr], rtol=1e-12)
    assert seen["shared"] > 20 and seen["fallback"] > 5


def test_r_k_t3_the_finding_in_miniature(world_src):
    """For every pooled month and member, the expected day return under the builder's rule (the pool enumerated,
    the adjustment applied) equals c_s; without the adjustment it would vary across members."""
    _, _, _, src = world_src
    adj, c = np.asarray(src.arr["pool_adj"]), np.asarray(src.arr["sym_c"])
    sets = _pool_sets(src)
    acts = src.acts(pd.Timestamp(C.VAL_END, tz="UTC").value)
    mem = U.membership(acts, list(acts), pd.Timestamp(C.UNIVERSE_START, tz="UTC").value,
                       pd.Timestamp(C.VAL_END, tz="UTC").value)
    dp = np.asarray(src.arr["day_pool"])
    with_adj, without = [], []
    for i, mo in enumerate(mem.months):
        if not mem.unit_exists("top30", i):
            continue
        g = int(mo) // U.DAY_NS - src.D0
        if g >= len(dp) or dp[g] < 0:
            continue
        Q = sets[dp[g]]
        diffs = []
        for s in mem.members("top30", i):
            k = src.k[s]
            _, ret = _sym_days(src, s)
            e = float(np.mean(ret[Q]))                                           # every member is full on every pool day
            with_adj.append(e + adj[dp[g], k] - c[k])
            diffs.append(e - c[k])
        without.append(float(np.std(diffs)))
    assert with_adj and max(abs(x) for x in with_adj) <= 1e-12
    assert max(without) > 0.0                                                    # so the test can fail


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


NULL_B_PIN = "e7ec7d09d5f3dc0176c2f766a1fcc2daf7e28037b1d5686bbc17829e4c96892e"     # at 6d9fb34, before R-K


def test_r_k_t4_null_b_worlds_are_byte_identical_to_fix_pass_6(world_src):
    _, panel, _, src = world_src
    w = UC.UWorld(src, "B", 4)
    frames = []
    for s in (panel[1], panel[4]):
        t = w.tables(s, trim=False)
        frames += [t["klines"], t["funding"]]
    assert _frames_sha(frames) == NULL_B_PIN


def test_r_k_t5_a_version_4_partial_file_is_refused(tmp_path):
    h5 = UC.run_header({"semantic": "s" * 64}, "r" * 64, list(UC.FAMILIES), 2, 2, True)
    assert h5["protocol_version"] == UC.PROTOCOL_VERSION == 5
    p = tmp_path / "v4.partial.jsonl"
    UC.Partial(p, dict(h5, protocol_version=4), log=lambda *a: None)
    with pytest.raises(UC.PartialMismatch):
        UC.Partial(p, h5, log=lambda *a: None)
