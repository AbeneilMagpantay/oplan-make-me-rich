"""KP-015 F + fix pass 4 (U2): the universe calibration on worlds with the REAL membership calendar (synthetic
source here, never run for real): every symbol keeps its real rows (present / absent hours, trades and volumes),
so the kernel's own membership rule reproduces the source's monthly schedule; only prices are resampled (null A:
one source day per world day shared by all symbols, personal fallback days; null B: one coin per day mirrors
every symbol); the protocol runs on the production block path; the oracle on the same worlds; the seal rule over
both units."""
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
    fw, fr = w.tables(s, trim=False)["funding"], tables[s]["funding"]
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
        assert np.array_equal(w.tables(s)["funding"]["rate"], tables[s]["funding"]["rate"][
            tables[s]["funding"].index <= pd.Timestamp(C.VAL_END, tz="UTC")])
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
