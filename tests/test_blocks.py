"""KP-015 fix pass 3: blocked evaluation equals the whole panel for programs with a window over a cs_* result
(one membership per run), the block_overlap self-check fires when a program's true memory exceeds its recorded
lookback and stays silent otherwise, and lookback_hours is a true upper bound for leaves under a timeframe
and under btc(). Synthetic data only."""
import shutil

import numpy as np
import pandas as pd
import pytest

from conftest import (PROGRAMS, SynthProvider, kernel_program, prog_text, synth_raw, synth_universe, synth_world)
from omr import constants as C
from omr import datasets as D
from omr import interp as X
from omr import lang as L
from omr import pipeline as PL
from omr import upipeline as UP

H = 3_600_000_000_000


def ts(s):
    return pd.Timestamp(s, tz="UTC").value


def top30(body: str):
    text = prog_text(body, kind="portfolio").replace("hypothesis", 'unit = "top30"\nhypothesis', 1)
    return L.parse(text, "x_test", probe=False)


WINDOWS_OVER_CS = {
    "sma_over_cs_demean": "k = param(24, 12, 48)\nn = param(48, 24, 96)\n"
                          "signal = cs_scale(sma(cs_demean(ret(close, k)), n))\n",
    "ema_over_cs_rank": "k = param(24, 12, 48)\nn = param(24, 12, 48)\n"
                        "signal = cs_scale(cs_demean(ema(cs_rank(ret(close, k)), n)))\n",
    "hold_on_cs_rank": "k = param(24, 12, 48)\nh = param(72, 24, 168)\nr = cs_rank(ret(close, k))\n"
                       "signal = cs_scale(hold(r > 0.5, r < 0, r < -0.5, r > 0, h))\n",
    "window_over_cs_mean": "k = param(24, 12, 48)\nn = param(168, 72, 336)\nm = sma(cs_mean(ret(close, 1)), n)\n"
                           "signal = cs_scale(cs_demean(ret(close, k)) * sign(m))\n",
    "zscore_over_cs_demean_daily": "n = param(20, 10, 40)\n"
                                   "signal = cs_scale(zscore(cs_demean(ret(daily(close), 1)), n))\n",
    "lookback_at_the_limit": "k = param(24, 12, 48)\nn = param(1799, 1439, 2159)\n"
                             "signal = cs_scale(cs_demean(ret(close, k)) * sign(sma(cs_mean(ret(close, 1)), n)))\n",
}


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


def custom_boundaries(bu):
    """Mid-month and short blocks: inside HOLEUSDT's 3-day hole, inside RELISTUSDT's first month back, a 10-day
    block, and half-year starts."""
    row = lambda t: int((ts(t) - bu.ns[0]) // H)                     # noqa: E731
    return [row("2020-07-01 00:00"), row("2021-01-01 00:00"), row("2021-08-14 13:00"), row("2021-09-11 05:00"),
            row("2021-09-21 05:00"), row("2022-01-01 00:00"), row("2022-07-01 00:00"), row("2023-03-17 09:00"),
            row("2024-01-01 00:00")]


def same3(a, b) -> bool:
    return (np.array_equal(a[0], b[0]) and np.array_equal(a[1], b[1], equal_nan=True) and np.array_equal(a[2], b[2]))


def test_the_lookback_limit_program_is_at_the_limit():
    assert top30(WINDOWS_OVER_CS["lookback_at_the_limit"]).lookback_hours == C.LOOKBACK_MAX_HOURS


@pytest.mark.parametrize("name", sorted(WINDOWS_OVER_CS))
def test_whole_panel_equals_blocks_for_windows_over_cross_sections(ud_full, name):
    prog = top30(WINDOWS_OVER_CS[name])
    q = L.default_params(prog)
    f = UP.program_fields(prog)
    whole = UP.Blocked(ud_full, "top30", months=None, fields=f)
    ref = whole.unit(prog, q)
    assert ref[2].any()
    half = UP.Blocked(ud_full, "top30", fields=f)                                     # production half-years
    custom = UP.Blocked(ud_full, "top30", fields=f, boundaries=custom_boundaries(whole), keep=False)
    assert len(half.blocks) >= 10 and len(custom.plan) == 10
    assert same3(half.unit(prog, q), ref) and same3(custom.unit(prog, q), ref)
    fp = UP.FullPanel(ud_full, "top30")                                                # the original whole path
    assert same3(UP.unit_full_u(prog, q, fp), ref)
    if name in ("sma_over_cs_demean", "lookback_at_the_limit"):
        a = UP.next30_score(prog, q, ud_full, months=None)
        b = UP.next30_score(prog, q, ud_full, months=3)
        assert a == b and a["code"] is None


def test_stage1_and_stage2_with_blocks_equal_one_block(ud_dev, ud_full, val_handle):
    prog = top30(WINDOWS_OVER_CS["sma_over_cs_demean"])
    q = L.default_params(prog)
    opts = PL.Opts(perm_n=20, jitter_n=2, truncation_cuts=3, start_cuts=2, start_cuts_val=1)
    s1a = UP.stage1_u(prog, q, ud_dev, np.random.default_rng(9), opts, months=None)
    s1b = UP.stage1_u(prog, q, ud_dev, np.random.default_rng(9), opts)
    assert s1a["ok"] and s1b["ok"]
    for k in ("W", "raw", "known"):
        assert np.array_equal(s1a[k], s1b[k], equal_nan=True), k
    ra = UP.stage2_u(prog, q, ud_full, s1a, opts, val_handle, 3, 0.1, months=None)
    rb = UP.stage2_u(prog, q, ud_full, s1b, opts, val_handle, 3, 0.1)
    assert ra["status"] == rb["status"] == "evaluated"
    assert ra["gates"] == rb["gates"] and ra["metrics"] == rb["metrics"] and ra["info"] == rb["info"]
    assert ra["daily_returns"].equals(rb["daily_returns"])


def test_the_old_per_block_membership_is_caught(ud_full, monkeypatch):
    """The defect this pass fixes, kept able to fail: with the membership recomputed from each block's own rows
    the blocked run is no longer the whole panel (a difference, or the block_overlap self-check fires)."""
    prog = top30(WINDOWS_OVER_CS["sma_over_cs_demean"])
    q = L.default_params(prog)
    f = UP.program_fields(prog)
    ref = UP.Blocked(ud_full, "top30", months=None, fields=f).unit(prog, q)
    real = UP.Blocked._eval

    def per_block(self, bp, prog_, params, r0, r1, literals, mem):
        return real(self, bp, prog_, params, r0, r1, literals, self.ud.membership(int(self.ns[r0]), int(self.ns[r1])))
    monkeypatch.setattr(UP.Blocked, "_eval", per_block)
    half = UP.Blocked(ud_full, "top30", fields=f)
    try:
        out = half.unit(prog, q)
        caught = not same3(out, ref)
    except PL.KernelFault as e:
        caught = str(e) == "block_overlap"
    assert caught


# ---------------------------------------------------------------- block_overlap fires / stays silent

def _evaluate(tmp_path, tmp_ledger, ud_dev, ud_full, body):
    from omr import evaluate, ledger
    src = tmp_path / "x_overlap.omr"
    src.write_text(prog_text(body, kind="portfolio", name="x_overlap").replace(
        "hypothesis", 'unit = "top30"\nhypothesis', 1), encoding="ascii")
    prov = SynthProvider(synth_world(seed=3), universe=(ud_dev, ud_full))
    row = evaluate.evaluate_file(str(src), 0, provider=prov, quiet=True, require_lock=False, p_max=0.1,
                                 opts=PL.Opts(perm_n=10, jitter_n=2, truncation_cuts=2, start_cuts=1, start_cuts_val=1))
    return row, ledger


def test_block_overlap_fires_when_the_recorded_lookback_is_too_short(tmp_path, tmp_ledger, ud_dev, ud_full,
                                                                     monkeypatch):
    monkeypatch.setattr(L, "lookback_hours", lambda prog: 3)                    # recorded far below the true 144
    row, ledger = _evaluate(tmp_path, tmp_ledger, ud_dev, ud_full, WINDOWS_OVER_CS["sma_over_cs_demean"])
    assert row["code"] == "kernel_fault" and row["fault"] == "block_overlap"
    assert ledger.counted_ids() == []                                            # stage 1: uncounted


def test_block_overlap_fires_when_a_window_under_reports(tmp_path, tmp_ledger, ud_dev, ud_full, monkeypatch):
    real = L._extra_rows
    monkeypatch.setattr(L, "_extra_rows", lambda fn, n: 0 if fn == "sma" else real(fn, n))
    prog = top30(WINDOWS_OVER_CS["sma_over_cs_demean"])
    assert prog.lookback_hours == 49                                              # the sma's 95 hours are missing
    row, ledger = _evaluate(tmp_path, tmp_ledger, ud_dev, ud_full, WINDOWS_OVER_CS["sma_over_cs_demean"])
    assert row["code"] == "kernel_fault" and row["fault"] == "block_overlap"
    assert ledger.counted_ids() == []


def _kernel_and_strategy_programs():
    out = []
    for f in sorted(PROGRAMS.glob("*.omr")) + sorted((PROGRAMS.parent.parent / "strategies").glob("*.omr")):
        text = f.read_bytes().decode("ascii")
        if 'unit = "top30"' not in text:
            text = text.replace("hypothesis", 'unit = "top30"\nhypothesis', 1)
        try:
            out.append((f.stem, L.parse(text, f.stem, probe=False)))
        except L.LangError:
            continue                                              # single programs, or lookback over 90 days
    return out


def test_block_overlap_is_silent_on_kernel_and_strategy_programs(ud_dev):
    progs = _kernel_and_strategy_programs()
    names = [n for n, _ in progs]
    assert {"ucal_xs_momentum", "ucal_xs_reversal", "ucal_xs_carry", "kernel_noise_top30"} <= set(names)
    assert "gen001_relmom_pair" in names and "kernel_noise_portfolio" in names
    for name, prog in progs:
        q = L.default_params(prog)
        f = UP.program_fields(prog)
        out = UP.Blocked(ud_dev, "top30", fields=f).unit(prog, q)                # raises on a block_overlap
        assert same3(out, UP.Blocked(ud_dev, "top30", months=None, fields=f).unit(prog, q)), name


# ---------------------------------------------------------------- T3: lookback is a true upper bound

def _gapped_raw(seed, gaps):
    raw = synth_raw(start="2021-01-01 00:00", end="2021-03-31 23:00", seed=seed)
    mk = raw["mark_klines"]
    ik = raw["index_klines"]
    drop = np.zeros(len(mk), dtype=bool)
    for a, n in gaps:
        drop |= (mk.index >= pd.Timestamp(a, tz="UTC")) & (mk.index < pd.Timestamp(a, tz="UTC") + pd.Timedelta(hours=n))
    raw["mark_klines"] = mk[~drop]
    raw["index_klines"] = ik[~drop]
    return raw


GAPS = [("2021-02-01 00:00", 3), ("2021-02-10 04:00", 5), ("2021-02-20 00:00", 2), ("2021-03-01 00:00", 4)]
CUTS = ["2021-02-01 00:00", "2021-02-10 04:00", "2021-02-20 00:00", "2021-03-01 00:00", "2021-02-14 13:00"]


@pytest.mark.parametrize("body", [
    "signal = sign(daily(mark_close) - close)\n",
    "signal = sign(h4(index_close) - close)\n",
    "signal = sign(daily(btc(mark_close)) - btc(close))\n",
    "signal = sign(btc(mark_close) - btc(close))\n",
    "n = param(3, 2, 5)\nsignal = sign(sma(daily(mark_close), n) - close)\n",
    "n = param(10, 6, 14)\nsignal = rsi(close, n)\n",
    "n = param(10, 6, 14)\nsignal = sign(ema(mark_close, n) - close)\n",
    "n = param(4, 3, 6)\nsignal = tanh(atr(high, low, close, n) / close)\n",
    "n = param(4, 3, 6)\nsignal = hold(close > lag(close, n), close < lag(close, n), mark_close < close, "
    "mark_close > close, n)\n",
    "n = param(5, 4, 6)\nsignal = tanh(funding_mean(n) + realised_vol(close, n))\n",
])
def test_lookback_is_a_true_upper_bound(body):
    """Cut the frame at c: from row c + lookback - 1 on, the cut run must be known exactly where the whole run
    is, with the same value (every leaf under a timeframe and under btc() included)."""
    prog = L.parse(prog_text(body), "x_test", probe=False)
    q = L.default_params(prog)
    f = D.assemble_frame(_gapped_raw(1, GAPS), D.PROGRAM_EXTRA)
    btc = D.assemble_frame(_gapped_raw(2, GAPS), D.PROGRAM_EXTRA)
    raw, kn = X.evaluate_full(prog, q, [f], btc)
    Lh = prog.lookback_hours
    for c_t in CUTS:
        c = int(f.index.get_loc(pd.Timestamp(c_t, tz="UTC")))
        rc, kc = X.evaluate_full(prog, q, [f.iloc[c:]], btc.iloc[c:])
        a = Lh - 1
        assert np.array_equal(kc[a:], kn[c + a:]), (body, c_t)
        assert np.array_equal(rc[a:], raw[c + a:], equal_nan=True), (body, c_t)


def test_the_old_timeframe_rule_under_reports():
    """Able to fail: with the old 2h - 1 for a timeframe over mark_close, a cut just before a mark gap is
    unknown in the cut run at a row the old lookback calls complete."""
    prog = L.parse(prog_text("signal = sign(daily(mark_close) - close)\n"), "x_test", probe=False)
    assert prog.lookback_hours == 2 * 24 - 2 + C.MARK_MAX_STALE_HOURS + 1
    f = D.assemble_frame(_gapped_raw(1, GAPS), D.PROGRAM_EXTRA)
    raw, kn = X.evaluate_full(prog, {}, [f])
    old = 2 * 24 - 1
    bad = False
    for c_t in CUTS[:4]:
        c = int(f.index.get_loc(pd.Timestamp(c_t, tz="UTC")))
        rc, kc = X.evaluate_full(prog, {}, [f.iloc[c:]])
        bad |= not np.array_equal(kc[old - 1:], kn[c + old - 1:])
    assert bad


# ---------------------------------------------------------------- U8: the check's coverage is recorded

def test_u8_block_overlap_cells_are_counted_and_recorded(tmp_path, tmp_ledger, ud_dev, ud_full):
    prog = top30(WINDOWS_OVER_CS["sma_over_cs_demean"])
    q = L.default_params(prog)
    opts = PL.Opts(truncation_cuts=1, start_cuts=1)
    s1 = UP.stage1_u(prog, q, ud_dev, np.random.default_rng(9), opts)
    one = UP.stage1_u(prog, q, ud_dev, np.random.default_rng(9), opts, months=None)
    assert s1["block_overlap_cells"] > 0 and one["block_overlap_cells"] == 0      # one block: nothing compared
    row, ledger = _evaluate(tmp_path, tmp_ledger, ud_dev, ud_full, WINDOWS_OVER_CS["sma_over_cs_demean"])
    assert row["status"] == "evaluated" and row["block_overlap_cells"] == s1["block_overlap_cells"]
    from omr import paths as P
    pend = [r for r in ledger.read_rows(P.TRIALS_JSONL) if r["status"] == "pending"][0]
    assert pend["stage1"]["block_overlap_cells"] == pend["block_overlap_cells"] == s1["block_overlap_cells"]
