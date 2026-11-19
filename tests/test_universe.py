"""KP-015: symbol table, activity, membership (B4 traps and start independence), the universe engine,
the top30 language rules (unit header, D3 lookback, index_close, in-play cross sections) and the top30
pipeline (locality self-checks, G6 masking, G8 on next30). Synthetic data only."""
import numpy as np
import pandas as pd
import pytest

from conftest import (DEAD_AT, HOLE_DAY, NOFUND_FROM, NOFUND_TO, RELIST_TO, TRAP_DEAD, TRAP_HOLE, TRAP_INDEX,
                      TRAP_LONGHOLE, TRAP_NOFUND, TRAP_RELIST, TRAP_TRADFI,
                      prog_text, synth_raw, synth_udata, synth_universe)
from omr import constants as C
from omr import engine as E
from omr import interp as X
from omr import lang as L
from omr import pipeline as PL
from omr import universe as U
from omr import upipeline as UP

H = U.HOUR_NS


def ts(s):
    return pd.Timestamp(s, tz="UTC").value


@pytest.fixture(scope="module")
def uni():
    return synth_universe(seed=5, n=52)


@pytest.fixture(scope="module")
def ud_full(uni):
    tables, table, btc = uni
    return UP.udata_from_tables(tables, btc, C.VAL_END, symbols_table=table)


@pytest.fixture(scope="module")
def ud_dev(uni):
    tables, table, btc = uni
    return UP.udata_from_tables(tables, btc, C.DEV_END, symbols_table=table)


def months_of(mem):
    return [pd.Timestamp(int(m), tz="UTC").strftime("%Y-%m") for m in mem.months]


# ---------------------------------------------------------------- A1 symbol table

def test_symbol_table_rules():
    ei = {"symbols": [
        {"symbol": "AAAUSDT", "contractType": "PERPETUAL", "quoteAsset": "USDT", "underlyingType": "COIN",
         "status": "TRADING", "onboardDate": 1600000000000},
        {"symbol": "BBBUSDT", "contractType": "TRADIFI_PERPETUAL", "quoteAsset": "USDT", "underlyingType": "EQUITY",
         "status": "TRADING", "onboardDate": ts("2026-01-05 13:30") // 10 ** 6},
        {"symbol": "NUUSDT", "contractType": "TRADIFI_PERPETUAL", "quoteAsset": "USDT", "underlyingType": "EQUITY",
         "status": "TRADING", "onboardDate": ts("2026-11-12 09:00") // 10 ** 6},
        {"symbol": "DEFIUSDT", "contractType": "PERPETUAL", "quoteAsset": "USDT", "underlyingType": "INDEX",
         "status": "SETTLING", "onboardDate": 1598598000000},
        {"symbol": "PREUSDT", "contractType": "PERPETUAL", "quoteAsset": "USDT", "underlyingType": "PREMARKET",
         "status": "TRADING", "onboardDate": 1792916100000}]}
    months = {"AAAUSDT": ["2020-09"], "BBBUSDT": ["2026-01"], "NUUSDT": ["2021-10", "2022-02", "2026-11"],
              "DEFIUSDT": ["2020-08"], "PREUSDT": ["2026-10"], "LUNAUSDT": ["2021-01", "2022-05"],
              "FOOTBALLUSDT": ["2021-10"]}
    t = U.build_table(ei, list(months) + ["BTCUSDT_250328", "AERGOUSDTSETTLED", "ETHBTC"], [], months, {})
    cls = {n: r["class"] for n, r in t["symbols"].items()}
    assert cls == {"AAAUSDT": "crypto_perpetual", "BBBUSDT": "tradfi_perpetual", "NUUSDT": "crypto_perpetual",
                   "DEFIUSDT": "index_contract", "PREUSDT": "other", "LUNAUSDT": "crypto_perpetual",
                   "FOOTBALLUSDT": "index_contract"}
    assert t["symbols"]["NUUSDT"]["until"] == "2026-11-12 09:00:00+00:00"           # name reused by TradFi
    assert t["symbols"]["AAAUSDT"]["until"] is None
    assert t["excluded_folder_names"] == {"dated_delivery": 1, "settled_copy": 1, "other_quote_or_name": 1}
    assert U.crypto_symbols(t) == ["AAAUSDT", "LUNAUSDT", "NUUSDT"]


# ---------------------------------------------------------------- A2 activity

def test_activity_usable_bars_and_until():
    """A2 + S3: the history starts at the first active bar and keeps every later stored row; a zero-trade bar
    is usable while its run of non-active bars is <= 24 (absent rows count and are never usable)."""
    raw = synth_raw(start="2021-01-01 00:00", end="2021-03-31 23:00", seed=1)
    kl = raw["klines"].copy()
    kl.loc[kl.index >= pd.Timestamp("2021-03-01", tz="UTC"), "trades"] = 0.0          # trailing padding
    kl.loc[kl.index < pd.Timestamp("2021-01-02", tz="UTC"), "trades"] = 0.0           # leading inactive day
    kl.loc[pd.Timestamp("2021-02-01 05:00", tz="UTC"), "is_gap"] = True                # a missing row inside
    halt = (kl.index >= pd.Timestamp("2021-02-10 00:00", tz="UTC")) & (kl.index < pd.Timestamp("2021-02-11 06:00", tz="UTC"))
    kl.loc[halt, "trades"] = 0.0                                                      # a 30-hour halt
    a = U.activity_of(kl)
    r = lambda t: (ts(t) - a.start) // H                                             # noqa: E731
    assert a.start == ts("2021-01-02 00:00") and a.end == ts("2021-03-31 23:00")
    assert not a.active[r("2021-02-01 05:00")] and not a.usable[r("2021-02-01 05:00")]   # absent: never usable
    assert a.usable[r("2021-02-10 00:00")] and a.usable[r("2021-02-10 23:00")]           # zero-trade runs 1..24
    assert not a.usable[r("2021-02-11 00:00")] and not a.usable[r("2021-02-11 05:00")]   # 25th on: unusable
    assert not a.active[r("2021-02-10 03:00")]                                          # membership: real trades
    assert a.usable[r("2021-03-01 23:00")] and not a.usable[r("2021-03-02 00:00")]       # padding: one day only
    b = U.activity_of(kl, until="2021-02-10 00:00")
    assert b.end == ts("2021-02-09 23:00")


def test_s3_absent_rows_count_in_the_zero_trade_run():
    act = np.array([1, 0, 0, 1] + [0] * 30, dtype=bool)
    pres = np.ones(len(act), dtype=bool)
    pres[5:15] = False                                                               # ten absent rows inside
    u = U.usable_of(act, pres)
    assert u[:5].all() and not u[5:15].any() and u[15:28].all() and not u[28:].any()


# ---------------------------------------------------------------- B membership

def test_membership_traps(ud_full):
    g = ud_full.grid()
    mem = ud_full.membership(g[0].value, g[-1].value)
    labs = months_of(mem)
    ever = set(mem.ever("top30")) | set(mem.ever("next30"))
    assert TRAP_TRADFI not in ud_full.acts and TRAP_INDEX not in ud_full.acts       # never candidates
    assert TRAP_TRADFI not in ever and TRAP_INDEX not in ever
    in30 = {lab: set(mem.members("top30", i)) for i, lab in enumerate(labs)}
    # the delisted coin is a member before its delisting and never after its last active bar
    assert TRAP_DEAD in in30["2021-06"]
    assert all(TRAP_DEAD not in in30[lab] and TRAP_DEAD not in mem.members("next30", i)
               for i, lab in enumerate(labs) if lab >= "2021-07")
    # the relisted coin: padding 2021-03-01 .. 2021-04-30, active again from 2021-05-01. Still a member for
    # March (decided from February's bars) but never in play while padded; then it seasons again
    assert TRAP_RELIST in in30["2021-03"] and TRAP_RELIST not in in30["2021-04"]
    first_back = min(lab for lab in labs if lab > "2021-04" and TRAP_RELIST in in30[lab])
    assert first_back == "2021-08"                                   # first m with m - 90 days > the 61-day gap
    # R1a: a three-day hole does NOT restart the seasoning; only the 95% activity rule drops it for one month
    assert TRAP_HOLE in in30["2021-09"] and TRAP_HOLE not in in30["2021-10"] and TRAP_HOLE in in30["2021-11"]
    # an eight-day hole is a relisting: 90 days of seasoning again (last empty day 2021-09-17 -> 2022-01)
    assert TRAP_LONGHOLE in in30["2021-09"]
    assert all(TRAP_LONGHOLE not in in30[lab] for lab in ("2021-10", "2021-11", "2021-12"))
    assert TRAP_LONGHOLE in in30["2022-01"]
    # ranks: top30 are the 30 highest scores, next30 the following ones
    i = labs.index("2023-01")
    sc = mem.scores[i]
    top, nxt = mem.members("top30", i), mem.members("next30", i)
    assert len(top) == 30 and min(sc[s] for s in top) >= max(sc[s] for s in nxt) and len(nxt) >= 10


def test_months_without_ten_eligible_have_no_unit(ud_full):
    g = ud_full.grid()
    mem = ud_full.membership(g[0].value, g[-1].value)
    labs = months_of(mem)
    for i, lab in enumerate(labs):
        n = len(mem.ranked[i])
        assert (len(mem.members("top30", i)) > 0) == (mem.known[i] and n >= 10)
        assert (len(mem.members("next30", i)) > 0) == (mem.known[i] and n - 30 >= 10)
    assert not mem.known[labs.index("2020-01")] and not mem.known[labs.index("2020-03")]


def test_membership_is_unchanged_by_appended_data_and_by_cuts_beyond_what_it_reads(uni):
    tables, table, btc = uni
    full = UP.udata_from_tables(tables, btc, C.VAL_END, symbols_table=table)
    dev = UP.udata_from_tables(tables, btc, C.DEV_END, symbols_table=table)
    lo = ts(C.UNIVERSE_START)
    mf = full.membership(lo, ts(C.VAL_END))
    md = dev.membership(lo, ts(C.DEV_END))
    for i, m in enumerate(md.months):                                # appending later data changes nothing
        j = int(np.searchsorted(mf.months, m))
        assert md.known[i] == mf.known[j] and md.ranked[i] == mf.ranked[j] and md.scores[i] == mf.scores[j]
    cut = ts("2021-02-14 07:00")                                      # a cut inside a month
    mc = full.membership(cut, ts(C.VAL_END))
    for i, m in enumerate(mc.months):
        j = int(np.searchsorted(mf.months, m))
        if m - U.SEASON_BLOCKS * U.DAY_NS >= cut:
            assert mc.known[i] and mc.ranked[i] == mf.ranked[j] and mc.scores[i] == mf.scores[j]
        else:
            assert not mc.known[i] and mc.ranked[i] == []             # unknown, never different
    assert mc.known.any() and not mc.known.all()


def test_inplay_uses_the_month_of_the_decision_time(ud_full):
    fp = UP.FullPanel(ud_full, "top30")
    _, panel = UP.view(fp)
    mem = ud_full.membership(fp.ns[0], fp.ns[-1])
    r = int(np.searchsorted(fp.ns, ts("2021-06-30 23:00")))          # decision at 2021-07-01 00:00
    k = fp.symbols.index(TRAP_DEAD)
    assert not panel.inplay[r, k] and panel.inplay[r - 1, k] is not None
    i7 = int(np.searchsorted(mem.months, ts("2021-07-01 00:00")))
    members = set(mem.members("top30", i7))
    assert {fp.symbols[j] for j in np.nonzero(panel.inplay[r])[0]} <= members
    # a member is not in play on a row whose bar is inactive (the dead coin after its delisting, mid-month)
    r2 = int(np.searchsorted(fp.ns, ts(DEAD_AT))) + 30          # S3: padding is usable for 24 bars only
    assert not panel.inplay[r2, k] and panel.inplay[r2].sum() >= 25


# ---------------------------------------------------------------- C engine

def _rand_market(seed, T=400, K=5):
    rng = np.random.default_rng(seed)
    op = 100 * np.exp(np.cumsum(0.01 * rng.standard_normal((T, K)), axis=0))
    cl = op * np.exp(0.005 * rng.standard_normal((T, K)))
    av = rng.uniform(size=(T, K)) > 0.08
    av[:, 0] = True
    dn = 1 - np.abs(0.01 * rng.standard_normal((T, K)))
    up = 1 + np.abs(0.01 * rng.standard_normal((T, K)))
    fr = np.where(rng.uniform(size=(T, K)) < 0.1, 0.0003 * rng.standard_normal((T, K)), 0.0)
    w = rng.standard_normal((T, K))
    w = w / np.maximum(1.0, np.abs(w).sum(axis=1, keepdims=True))
    return op, cl, av, dn, up, fr, w


@pytest.mark.parametrize("seed", [1, 2, 3])
def test_universe_engine_matches_the_independent_reference(seed):
    op, cl, av, dn, up, fr, w = _rand_market(seed)
    out = E.run_arrays_u(op, np.where(av, cl, np.nan), av, dn, up, fr, w)
    ref_eq, ref_ev, ref_liq = E.run_reference_u(op, cl, av, dn, up, fr, w)
    assert np.allclose(out[0], ref_eq, rtol=1e-11, atol=1e-12)
    assert list(out[3]) == ref_ev and out[7] == ref_liq
    slow = E.run_arrays_u(op, cl, av, dn, up, fr, w, fast=False)
    assert np.array_equal(slow[0], out[0])


def test_a_position_without_a_next_bar_is_closed_at_its_last_close_with_cost():
    T = 6
    op = np.array([[100.0], [100.0], [110.0], [120.0], [130.0], [140.0]])
    cl = np.array([[100.0], [110.0], [115.0], [np.nan], [np.nan], [140.0]])
    av = np.array([[True], [True], [True], [False], [False], [True]])
    one = np.ones((T, 1))
    tgt = np.array([[0.0], [1.0], [1.0], [1.0], [1.0], [0.0]])
    eq = E.run_arrays_u(op, cl, av, one * 0.99, one * 1.01, one * 0.0, tgt, cost_rate=0.001)[0]
    c = 0.001
    e1 = 1.0 - c                         # buy at the open of bar 1
    e2 = e1 * 110 / 100                  # mark to bar 2's open
    e3 = e2 * 115 / 110                  # bar 3 missing: marked to bar 2's CLOSE, then sold there with cost
    e3 -= e2 * 115 / 110 * c
    assert np.isclose(eq[1], e1) and np.isclose(eq[2], e2) and np.isclose(eq[3], e3) and np.isclose(eq[4], e3)
    assert np.isclose(eq[5], e3)         # target 0 at bar 5: nothing to trade


# ---------------------------------------------------------------- D language

def test_unit_header_rules_and_canonical_form():
    body = 'n = param(10, 5, 20)\nsignal = cs_demean(ret(close, n))\n'
    core = L.parse(prog_text(body, kind="portfolio"), "x_test", probe=False)
    t = prog_text(body, kind="portfolio").replace('hypothesis', 'unit = "top30"\nhypothesis', 1)
    top = L.parse(t, "x_test", probe=False)
    assert core.unit == "core" and top.unit == "top30"
    assert core.canonical.startswith("kind=portfolio;") and top.canonical == "unit=top30;" + core.canonical
    with pytest.raises(L.LangError) as e:
        L.parse(t.replace('kind = "portfolio"', 'kind = "single"').replace("cs_demean(ret(close, n))", "ret(close, n)"),
                "x_test", probe=False)
    assert e.value.rule == "header_unit"
    with pytest.raises(L.LangError) as e:
        L.parse(t.replace('"top30"', '"top99"'), "x_test", probe=False)
    assert e.value.rule == "header_unit"
    with pytest.raises(L.LangError) as e:
        L.parse(prog_text('unit = sma(close, 2)\nsignal = sign(ret(close, 1))\n'), "x_test", probe=False)
    assert e.value.rule in ("header_order", "shadowing", "header_value")


@pytest.mark.parametrize("body,hours", [
    ("n = param(10, 5, 20)\nsignal = sign(ret(close, n))\n", 21),
    ("n = param(10, 5, 20)\nsignal = sign(sma(close, n) - close)\n", 20),
    ("n = param(10, 5, 20)\nsignal = tanh(ema(ret(close, 1), n))\n", 101),
    ("n = param(10, 5, 20)\nsignal = rsi(close, n)\n", 201),
    ("n = param(10, 5, 20)\nsignal = sign(ret(daily(close), n))\n", 47 + 20 * 24),
    ("signal = sign(mark_close - close)\n", C.MARK_MAX_STALE_HOURS + 1),
    ("n = param(10, 5, 20)\nsignal = funding_mean(n)\n", 160),
    ("n = param(10, 5, 20)\nsignal = sign(sma(close - lag(close, 1), n))\n", 21),
])
def test_lookback_hours(body, hours):
    assert L.parse(prog_text(body), "x_test", probe=False).lookback_hours == hours


def test_d3_rejects_a_top30_program_longer_than_the_seasoning_period():
    ok = prog_text('n = param(60, 30, 88)\nsignal = cs_demean(ret(daily(close), n))\n', kind="portfolio")
    ok = ok.replace('hypothesis', 'unit = "top30"\nhypothesis', 1)
    assert L.parse(ok, "x_test", probe=False).lookback_hours <= C.LOOKBACK_MAX_HOURS
    bad = ok.replace("param(60, 30, 88)", "param(60, 30, 89)")         # 47 + 89 x 24 = 2183 hours
    with pytest.raises(L.LangError) as e:
        L.parse(bad, "x_test", probe=False)
    assert e.value.rule == "lookback_exceeds_seasoning"
    core = bad.replace('unit = "top30"\n', "")                         # the core unit has no such rule
    assert L.parse(core, "x_test", probe=False).lookback_hours > C.LOOKBACK_MAX_HOURS


def test_index_close_basis_and_its_staleness():
    p = L.parse(prog_text("k = param(100, 50, 200)\nsignal = tanh(k * (close - index_close) / index_close)\n"),
                "x_test", probe=False)
    raw = synth_raw(start="2021-01-01 00:00", end="2021-02-28 23:00", seed=3)
    idx = raw["index_klines"]
    cut = (idx.index >= pd.Timestamp("2021-02-01 00:00", tz="UTC")) & (idx.index < pd.Timestamp("2021-02-01 10:00", tz="UTC"))
    raw["index_klines"] = idx[~cut]                                  # 10 index bars missing
    from omr import datasets as D
    f = D.assemble_frame(raw, D.PROGRAM_EXTRA)
    r, kn = X.evaluate_full(p, {"k": 100}, [f])
    pos = {h: f.index.get_loc(pd.Timestamp(f"2021-02-01 {h:02d}:00", tz="UTC")) for h in range(12)}
    assert kn[pos[0] - 1, 0] and kn[pos[5], 0] and kn[pos[6] - 1, 0]       # last index bar 6 h old: known
    assert not kn[pos[7], 0] and not kn[pos[9], 0] and kn[pos[10], 0]      # older than 6 h: unknown
    c, i = f["close"].iloc[pos[3]], f["index_klines.close"].iloc[pos[0] - 1]
    assert np.isclose(r[pos[3], 0], np.tanh(100 * (c - i) / i))


def test_cross_sections_use_the_in_play_symbols_with_a_known_input():
    """S2 (R1b): across the in-play symbols whose input is known; known for them when at least 10 exist."""
    p = L.parse(prog_text("signal = cs_demean(ret(close, 1))\n", kind="portfolio"), "x_test", probe=False)
    T, K = 30, 12
    rng = np.random.default_rng(0)
    close = 100 * np.exp(np.cumsum(0.01 * rng.standard_normal((T, K)), axis=0))
    close[12, 3] = np.nan                                            # symbol 3: a hole at row 12
    close[20, :3] = np.nan                                           # row 20: three holes -> only 9 known at row 21
    P_ = np.ones((T, K), dtype=bool)
    P_[:, 2] = False                                                 # symbol 2 never in play
    idx = pd.date_range("2021-01-01", periods=T, freq="h", tz="UTC")
    panel = X.Panel(idx, [f"S{i:02d}" for i in range(K)], lambda n: close if n == "close" else None,
                    P_ & np.isfinite(close), np.ones(T, dtype=bool))
    raw, kn = X.evaluate_full(p, {}, panel)
    r = close[1:] / close[:-1] - 1
    live = [k for k in range(K) if k != 2]
    assert not kn[:, 2].any()                                        # not in play: unknown
    m = np.mean(r[4, live])
    assert kn[5, live].all() and np.allclose(raw[5, live], r[4, live] - m)
    # row 13: symbol 3's input (ret over rows 12..13) is unknown -> it drops out, the other 10 stay known
    ok13 = [k for k in live if k != 3]
    assert not kn[13, 3] and kn[13, ok13].all()
    assert np.allclose(raw[13, ok13], r[12, ok13] - np.mean(r[12, ok13]))
    assert not kn[21].any()                                          # 9 known in-play symbols: unknown for everyone


# ---------------------------------------------------------------- E pipeline (locality, gates)

def _prog(stem):
    from conftest import kernel_program
    return kernel_program(stem)


def test_stage1_self_checks_pass_on_the_universe_and_include_a_symbol_cut(ud_dev):
    prog = _prog("kernel_noise_top30")
    s1 = UP.stage1_u(prog, L.default_params(prog), ud_dev, np.random.default_rng(3))
    assert s1["ok"] and s1["code"] is None and s1["start_cuts"] == C.START_CUTS_DEV + 1
    fp = UP.FullPanel(ud_dev, "top30")
    cuts = UP.start_cut_positions(fp, np.random.default_rng(3), 0, C.START_CUT_SPAN, symbol_cut=True)
    assert len(cuts) == 1
    c = cuts[0]
    starts = [ud_dev.acts[s].start for s in fp.symbols]
    assert any(st < fp.ns[c] <= st + 31 * H for st in starts)          # removes a symbol's first bars
    assert fp.ns[c] % (24 * H) != 0                                    # inside a day (so inside a month)


def test_a_non_local_membership_is_caught_by_the_start_cut_check(ud_dev, monkeypatch):
    """The self-check can fail: a start-cut run whose membership is KNOWN where its 91-day window was cut
    (here: the full-data ranking without its first symbol, as a rule reading partial data would give)
    disagrees with the base run."""
    prog = _prog("ucal_xs_reversal")
    q = L.default_params(prog)
    fp = UP.FullPanel(ud_dev, "top30")
    _, raw, kn = UP.unit_full_u(prog, q, fp)
    full = ud_dev.membership(fp.ns[0], fp.ns[-1])
    real = UP.UData.membership

    def leaky(self, lo, hi):
        m = real(self, lo, hi)
        if lo == fp.ns[0]:
            return m
        months = U.month_starts(lo, hi)                              # every month known
        j = np.searchsorted(full.months, months)
        ranked = [m.ranked[i] if m.known[i] else full.ranked[k][1:] for i, k in enumerate(j)]
        return U.Membership(months=months, known=full.known[j], ranked=ranked, scores=[{} for _ in j])
    monkeypatch.setattr(UP.UData, "membership", leaky)
    ud_dev._mem.clear()
    c = int(np.searchsorted(fp.ns, ts("2021-03-10 13:00")))
    _, rc, kc = UP.unit_full_u(prog, q, fp, start=fp.grid[c])
    assert not PL.start_cut_agrees(rc, kc, raw[c:], kn[c:])
    ud_dev._mem.clear()


def test_stage2_top30_gates_and_g8_on_next30(ud_dev, ud_full, val_handle):
    prog = _prog("ucal_xs_carry")
    q = L.default_params(prog)
    s1 = UP.stage1_u(prog, q, ud_dev, np.random.default_rng(4), PL.Opts(truncation_cuts=3, start_cuts=1))
    opts = PL.Opts(perm_n=20, jitter_n=2, start_cuts_val=1)
    res = UP.stage2_u(prog, q, ud_full, s1, opts, val_handle, 9, 0.1)
    assert res["status"] == "evaluated"
    g = res["gates"]
    assert set(g) == {"G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8", "G10"}
    assert g["G8"]["pass"] is not None and np.isfinite(g["G8"]["value"]["next30_sharpe"])
    assert 0 < g["G6"]["value"] <= 1
    bad = dict(s1, raw=s1["raw"].copy())
    bad["raw"][len(bad["raw"]) // 2, 0] += 1e-9 if np.isfinite(bad["raw"][len(bad["raw"]) // 2, 0]) else 0
    k = np.argwhere(np.isfinite(s1["raw"]))[len(np.argwhere(np.isfinite(s1["raw"]))) // 2]
    bad["raw"][k[0], k[1]] += 1e-9
    assert UP.stage2_u(prog, q, ud_full, bad, opts, val_handle, 9, 0.1)["status"] == "kernel_fault"


def test_g6_shifted_weights_never_land_on_symbols_out_of_play(ud_full, val_handle, monkeypatch):
    prog = _prog("ucal_xs_reversal")
    seen = []
    real = UP.Blocked.run_targets

    def spy(self, tgt, s, e, **kw):
        seen.append((s, e, np.asarray(tgt)))
        return real(self, tgt, s, e, **kw)
    monkeypatch.setattr(UP.Blocked, "run_targets", spy)
    bu = UP.Blocked(ud_full, "top30", fields=UP.program_fields(prog))
    W, _, _ = bu.unit(prog, L.default_params(prog))
    UP.ugates(W, bu, np.random.default_rng(1), PL.Opts(perm_n=5), 0.1, prog, {}, [], None, 0)
    vs, ve = bu.pos(C.VAL_START), bu.pos(C.VAL_END)
    ok = bu.inplay()[vs - 1:ve] & bu.eng_rows("av", vs, ve)
    g6 = [t for s, e, t in seen if (s, e) == (vs, ve)]
    assert len(g6) >= 6
    assert all(not np.any(t[~ok]) for t in g6)                        # actual and shifted runs alike


def test_evaluate_file_runs_a_top30_program_and_records_unit_and_lookback(tmp_path, tmp_ledger, ud_dev, ud_full):
    from conftest import SynthProvider, synth_world
    from omr import evaluate, ledger
    import shutil
    src = tmp_path / "kernel_noise_top30.omr"
    shutil.copyfile(_prog_path("kernel_noise_top30"), src)
    prov = SynthProvider(synth_world(seed=3), universe=(ud_dev, ud_full))
    row = evaluate.evaluate_file(str(src), 0, provider=prov, quiet=True, require_lock=False, p_max=0.1,
                                 opts=PL.Opts(perm_n=10, jitter_n=2, truncation_cuts=2, start_cuts=1, start_cuts_val=1))
    assert row["status"] == "evaluated" and row["unit"] == "top30" and row["lookback_hours"] == 1007
    pend = [r for r in ledger.read_rows(evaluate.P.TRIALS_JSONL) if r["status"] == "pending"]
    assert pend[0]["unit"] == "top30" and pend[0]["lookback_hours"] == 1007
    assert row["gates"]["G8"] is not None


def _prog_path(stem):
    from conftest import PROGRAMS
    return PROGRAMS / f"{stem}.omr"


# ---------------------------------------------------------------- R1a seasoning at the edges

@pytest.mark.parametrize("first_bar,gap_days,gap_end,ok", [
    ("2021-04-02 00:00", 0, None, True),            # listed exactly 90 days before 2021-07-01
    ("2021-04-02 01:00", 0, None, False),           # one hour short
    ("2021-01-01 00:00", 6, "2021-05-20", True),    # a 6-day hole inside the 90 days: still seasoned
    ("2021-01-01 00:00", 7, "2021-05-20", False),   # a 7-day hole inside: a relisting
    ("2021-01-01 00:00", 7, "2021-04-01", True),    # a 7-day hole ending the day before the 90 days start
    ("2021-01-01 00:00", 7, "2021-04-03", False),   # ... ending inside them (it started before them)
])
def test_r1a_seasoning_rule(first_bar, gap_days, gap_end, ok):
    start = ts(first_bar)
    n = (ts("2021-07-01 00:00") - start) // H
    act = np.ones(n, dtype=bool)
    if gap_days:
        e = (ts(gap_end + " 00:00") - start) // H + 24          # the gap's last day is gap_end
        act[e - 24 * gap_days:e] = False
    a = U.Activity(int(start), act, np.where(act, 1.0, 0.0))
    other = {f"X{i}": U.Activity(int(ts("2020-01-01 00:00")), np.ones(13000, dtype=bool), np.ones(13000)) for i in range(10)}
    mem = U.membership({"A": a, **other}, ["A"] + list(other), ts("2020-01-01 00:00"), ts("2021-06-30 23:00"))
    i = int(np.searchsorted(mem.months, ts("2021-07-01 00:00")))
    assert mem.known[i] and (("A" in mem.ranked[i]) == ok)


# ---------------------------------------------------------------- R2 funding

def test_r2_a_member_without_fresh_funding_is_not_in_play(ud_full):
    fp = UP.FullPanel(ud_full, "top30")
    _, panel = UP.view(fp)
    mem = ud_full.membership(fp.ns[0], fp.ns[-1])
    labs = months_of(mem)
    assert TRAP_NOFUND in mem.members("top30", labs.index("2021-07"))      # still a member (klines decide)
    k = fp.symbols.index(TRAP_NOFUND)
    gap = (fp.ns >= ts(NOFUND_FROM) + 16 * H) & (fp.ns <= ts(NOFUND_TO))
    assert fp.active[gap, k].all() and not panel.inplay[gap, k].any()       # active but out of play
    back = (fp.ns >= ts(NOFUND_TO) + 2 * H) & (fp.ns < ts("2021-09-30 00:00"))
    assert panel.inplay[back, k].mean() > 0.95
    prog = _prog("ucal_xs_momentum")
    W, _, kn = UP.unit_full_u(prog, L.default_params(prog), fp)
    assert not np.any(W[gap, k]) and not kn[gap, k].any()


def test_r2_funding_fresh_is_twice_the_own_interval():
    grid = np.arange(0, 40) * H
    st = np.array([0, 4, 8, 24]) * H                                 # 4-hour interval, then a gap
    ok = U.funding_fresh(grid, st, np.array([4.0, 4.0, 4.0, 4.0]))
    assert ok[:17].all() and not ok[17:24].any() and ok[24:33].all() and not ok[33:].any()
    assert not U.funding_fresh(grid, np.zeros(0, dtype=np.int64), np.zeros(0)).any()


# ---------------------------------------------------------------- R3 memory

from omr.upipeline import available_memory_bytes as REAL_AVAILABLE   # noqa: E402  (before the autouse patch)


def test_r3_the_os_reports_available_memory():
    v = REAL_AVAILABLE()
    assert isinstance(v, int) and v > 10 ** 8


def test_r3_columns_and_estimate():
    prog = _prog("ucal_xs_momentum")
    f = UP.program_fields(prog)
    assert f == {"close"}
    cols = UP.needed_columns(f)
    assert cols["index_klines"] == [] and "volume" not in cols["klines"] and "close" in cols["klines"]
    assert UP.needed_columns(UP.program_fields(_prog("kernel_noise_top30")))["index_klines"]
    blocks = {"top30": [[6700, 4400, 50]] * 11, "next30": [[6700, 4400, 70]] * 11}
    sizes = {"rows": 48192, "top30": 138, "next30": 217, "symbol_rows": 300 * 30000, "symbol_rows_max": 48000,
             "crypto_rows": 15_000_000, "blocks": blocks}
    e1 = UP.stage2_memory_estimate(prog, sizes)
    e2 = UP.stage2_memory_estimate(prog, dict(sizes, blocks={"top30": [[6700, 4400, 20]] * 11, "next30": blocks["next30"]},
                                              top30=60))
    assert e1["bytes"] == e1["activity_bytes"] + max(e1["top30"], e1["next30"])
    assert e1["top30"] > e2["top30"] > 0 and e1["next30"] == e2["next30"] and e1["bytes"] >= e2["bytes"]
    assert e1["bytes"] < 10 ** 9                                       # blocks: well under 1 GiB at these sizes


def test_r3_refusal_is_uncounted_and_named(tmp_path, tmp_ledger, ud_dev, ud_full, monkeypatch):
    from conftest import SynthProvider, synth_world
    from omr import evaluate, ledger
    import shutil
    monkeypatch.setattr(UP, "available_memory_bytes", lambda: 10 ** 6)
    src = tmp_path / "ucal_xs_carry.omr"
    shutil.copyfile(_prog_path("ucal_xs_carry"), src)
    prov = SynthProvider(synth_world(seed=3), universe=(ud_dev, ud_full))
    row = evaluate.evaluate_file(str(src), 0, provider=prov, quiet=True, require_lock=False, p_max=0.1,
                                 opts=PL.Opts(truncation_cuts=2, start_cuts=1))
    assert row["code"] == "memory_insufficient" and row["available_bytes"] == 10 ** 6 and row["estimate_bytes"] > 10 ** 7
    assert not evaluate.P.TRIALS_JSONL.exists() or ledger.counted_ids() == []
    assert ledger.read_rows(evaluate.P.STAGE1_LOG)[-1]["code"] == "memory_insufficient"


# ---------------------------------------------------------------- locality with holes (fix pass)

def _holed_universe(seed=3, n=14):
    from conftest import _pad
    from omr import datasets as D
    from omr import ucalibrate as UC
    rng = np.random.default_rng(seed)
    tables = {}
    for i in range(n):
        raw = synth_raw(start="2020-06-01 07:00" if i == 3 else "2019-11-01 00:00", end="2022-06-30 23:00",
                        seed=950 + i, funding_every=4 if i % 2 else 8)
        for st in rng.integers(2000, 14000, 3):                     # holes at different places per symbol
            d = raw["klines"].index[0] + pd.Timedelta(hours=int(st))
            raw = _pad(raw, str(d)[:16], str(d + pd.Timedelta(hours=int(rng.integers(3, 60))))[:16], gap=True)
        if i % 5 == 0:                                               # a 150-day funding gap, then resumption
            fu = raw["funding"]
            a = pd.Timestamp("2021-02-01", tz="UTC") + pd.Timedelta(days=i)
            raw["funding"] = fu[(fu.index < a) | (fu.index > a + pd.Timedelta(days=150))]
        tables[f"H{i:02d}USDT"] = raw
    btc = D.assemble_frame(tables["H00USDT"], D.PROGRAM_EXTRA)
    ud = UP.udata_from_tables(tables, btc, "2022-06-30 23:00")
    return UC.ConstUData(acts=ud.acts, raw=ud.raw, btc=ud.btc, end=ud.end, until={})


@pytest.mark.parametrize("body", ["n = param(24, 12, 48)\nsignal = cs_rank(ret(close, n))\n",
                                  "n = param(9, 5, 20)\nsignal = cs_rank(funding_mean(n))\n",
                                  "signal = cs_demean(log(mark_close / close))\n"])
def test_cross_sections_stay_local_with_holes_and_funding_gaps(body):
    """S2 (permanent): start cuts (random, one inside a hole, one removing a symbol's early bars) and
    truncation cuts agree exactly wherever the cut run is known, on a panel with per-symbol bar holes, mixed
    funding intervals and a 150-day funding gap followed by resumption (the R1b counterexample, which S1
    closes)."""
    text = prog_text(body, kind="portfolio").replace("hypothesis", 'unit = "top30"\nhypothesis', 1)
    prog = L.parse(text, "x_test", probe=False)
    ud = _holed_universe()
    fp = UP.FullPanel(ud, "top30")
    q = L.default_params(prog)
    _, raw, kn = UP.unit_full_u(prog, q, fp)
    assert kn.any()
    holes = np.argwhere(~fp.active[2500:] & (np.arange(len(fp.ns))[2500:, None] < np.array(
        [(ud.acts[s].end - fp.ns[0]) // H for s in fp.symbols])))
    straddle = int(holes[len(holes) // 2][0]) + 2500
    early = int((ud.acts[fp.symbols[3]].start - fp.ns[0]) // H) + 30
    rng = np.random.default_rng(1)
    cuts = sorted(set(rng.integers(200, len(fp.ns) - 4000, 6).tolist()) | {straddle, max(early, 1)})
    for c in cuts:
        _, rc, kc = UP.unit_full_u(prog, q, fp, start=fp.grid[c])
        assert PL.start_cut_agrees(rc, kc, raw[c:], kn[c:]), c
    for c in sorted(rng.integers(3000, len(fp.ns) - 1, 3).tolist()):
        _, rt, kt = UP.unit_full_u(prog, q, fp, upto=fp.grid[c])
        assert PL.same_rows(rt, raw[:c + 1]) and np.array_equal(kt, kn[:c + 1])


# ---------------------------------------------------------------- S4 blocks: bit-identical to the whole panel

def _same(a, b) -> bool:
    if isinstance(a, dict):
        return isinstance(b, dict) and set(a) == set(b) and all(_same(a[k], b[k]) for k in a)
    if isinstance(a, (list, tuple)):
        return len(a) == len(b) and all(_same(x, y) for x, y in zip(a, b))
    if isinstance(a, (pd.Series, pd.DataFrame)):
        return a.index.equals(b.index) and np.array_equal(a.to_numpy(), b.to_numpy(), equal_nan=True)
    if isinstance(a, np.ndarray):
        return a.shape == b.shape and np.array_equal(a, b, equal_nan=True)
    if isinstance(a, float) and isinstance(b, float) and np.isnan(a) and np.isnan(b):
        return True
    return a == b


def _boundaries(bu_whole):
    """Block starts: calendar half-years, one inside the 3-day hole of HOLEUSDT and one inside the first month
    RELISTUSDT is a member again (2021-08)."""
    ns = bu_whole.ns
    row = lambda t: int((ts(t) - ns[0]) // H)                          # noqa: E731
    return [row("2020-07-01 00:00"), row("2021-01-01 00:00"), row("2021-08-14 13:00"), row("2021-09-11 05:00"),
            row("2022-01-01 00:00"), row("2022-07-01 00:00"), row("2023-03-17 09:00"), row("2024-01-01 00:00")]


@pytest.mark.parametrize("stem", ["ucal_xs_momentum", "kernel_noise_top30", "ucal_xs_carry"])
def test_s4_blocks_equal_the_whole_panel_for_signals_weights_and_engine(ud_full, stem):
    prog = _prog(stem)
    q = L.default_params(prog)
    whole = UP.Blocked(ud_full, "top30", months=None)
    blocked = UP.Blocked(ud_full, "top30", fields=UP.program_fields(prog), boundaries=_boundaries(whole))
    half = UP.Blocked(ud_full, "top30", fields=UP.program_fields(prog))                 # production: half-years
    assert len(blocked.blocks) == 9 and len(half.blocks) >= 10 and whole.symbols == blocked.symbols
    fp = UP.FullPanel(ud_full, "top30")                                                   # the old whole-panel path
    ref = UP.unit_full_u(prog, q, fp)
    for bu in (whole, blocked, half):
        out = bu.unit(prog, q)
        assert all(_same(x, y) for x, y in zip(out, ref)), bu.bounds
    assert _same(whole.inplay(), blocked.inplay())
    W = ref[0]
    mk = UP.UMarket(fp)
    s, e = mk.pos(C.DEV_START), mk.pos(C.VAL_END)
    r0 = mk.run(W, s, e)
    for bu in (blocked, half):
        r1 = bu.run(W, s, e)
        for f in ("equity", "pre", "gross", "net", "ev_idx", "ev_turn", "ev_cost"):
            assert _same(getattr(r0, f), getattr(r1, f)), f
        assert r0.funding_paid == r1.funding_paid and r0.liq_idx == r1.liq_idx
        assert _same(r0.daily_returns(), r1.daily_returns())
    # cuts inside blocks: a start cut inside the hole block and a truncation inside RELIST's first month
    b = _boundaries(whole)
    for kw in ({"start": whole.grid[b[3] + 100]}, {"upto": whole.grid[b[2] + 50]}):
        assert all(_same(x, y) for x, y in zip(blocked.unit(prog, q, **kw), UP.unit_full_u(prog, q, fp, **kw)))


def test_s4_every_gate_is_identical_with_blocks(ud_full, val_handle):
    prog = _prog("ucal_xs_momentum")
    q = L.default_params(prog)
    opts = PL.Opts(perm_n=30, jitter_n=3)
    whole = UP.Blocked(ud_full, "top30", months=None)
    blocked = UP.Blocked(ud_full, "top30", fields=UP.program_fields(prog), boundaries=_boundaries(whole))
    W = whole.unit(prog, q)[0]
    rng = np.random.default_rng([5, 2])
    variants = PL.jitter_params(prog, q, rng, opts.jitter_n)
    g8w = UP.next30_score(prog, q, ud_full, months=None)
    g8b = UP.next30_score(prog, q, ud_full)
    assert _same(g8w, g8b)
    a = UP.ugates(W, whole, np.random.default_rng(7), opts, 0.1, prog, q, variants, g8w, 1)
    b = UP.ugates(W, blocked, np.random.default_rng(7), opts, 0.1, prog, q, variants, g8b, 1)
    assert a["status"] == b["status"] == "evaluated"
    for k in ("metrics", "gates", "info", "daily_returns", "tier", "detail"):
        assert _same(a[k], b[k]), k


def test_s4_stage2_with_blocks_equals_one_block(ud_dev, ud_full, val_handle):
    prog = _prog("ucal_xs_reversal")
    q = L.default_params(prog)
    opts = PL.Opts(perm_n=20, jitter_n=2, truncation_cuts=3, start_cuts=2, start_cuts_val=1)
    s1a = UP.stage1_u(prog, q, ud_dev, np.random.default_rng(9), opts, months=None)
    s1b = UP.stage1_u(prog, q, ud_dev, np.random.default_rng(9), opts)
    assert s1a["ok"] and s1b["ok"] and all(_same(s1a[k], s1b[k]) for k in ("W", "raw", "known", "symbols"))
    ra = UP.stage2_u(prog, q, ud_full, s1a, opts, val_handle, 3, 0.1, months=None)
    rb = UP.stage2_u(prog, q, ud_full, s1b, opts, val_handle, 3, 0.1)
    assert ra["status"] == rb["status"] == "evaluated"
    for k in ("metrics", "gates", "info", "daily_returns", "detail"):
        assert _same(ra[k], rb[k]), k


def test_without_s1_the_funding_gap_breaks_cross_section_locality(monkeypatch):
    """The counterexample, permanent and able to fail: with funding_mean known once n settlements exist since
    the frame start (no 8n-hour bound), a start cut inside a 150-day funding gap changes the set a cs_ sees."""
    from omr import windows as WN

    def unbounded(self, n):
        new = X._stack_true(self.frames, "funding.new")
        with np.errstate(all="ignore"):
            r8 = X._stack(self.frames, "funding.rate") * 8.0 / X._stack(self.frames, "funding.interval_hours")
        new = new & np.isfinite(r8)
        vals, kn = WN.event_mean(X._f64(r8), new, n)
        return X.S(X._clean(vals), kn, "h1", self.idx)
    monkeypatch.setattr(X.Context, "funding_mean", unbounded)
    text = prog_text("n = param(9, 5, 20)\nsignal = cs_rank(funding_mean(n))\n", kind="portfolio")
    prog = L.parse(text.replace("hypothesis", 'unit = "top30"\nhypothesis', 1), "x_test", probe=False)
    ud = _holed_universe()
    fp = UP.FullPanel(ud, "top30")
    q = L.default_params(prog)
    _, raw, kn = UP.unit_full_u(prog, q, fp)
    bad = []
    for t in ("2021-02-20 05:00", "2021-03-15 05:00", "2021-04-10 05:00", "2021-05-05 05:00"):
        c = int((ts(t) - fp.ns[0]) // H)
        _, rc, kc = UP.unit_full_u(prog, q, fp, start=fp.grid[c])
        bad.append(not PL.start_cut_agrees(rc, kc, raw[c:], kn[c:]))
    assert any(bad)
