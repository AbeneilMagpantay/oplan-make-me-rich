"""K7: regressions for the audit's bar-position clock and its variants. Every definite value is a
function of a bounded trailing window; history sufficiency is the unobservable known channel. So the
clock evaluates to unknown or to start-independent values, the start-cut check sees no dependence,
and nothing built on it reaches Tier 1."""
import numpy as np
import pytest

from omr import constants as C
from omr import evaluate
from omr import lang as L
from omr import pipeline
from conftest import SynthProvider, dev_only, kernel_program, synth_world

HDR = 'name = "{n}"\nfamily = "other"\nkind = "{k}"\nhypothesis = "probe: bar-position clock from an ema of a first-bar impulse"\n'
# the audit used w = 1000 (800..1200); ema memory is now 5w rows, so the largest allowed is 1000
CLOCK = ("w = param(800, 600, 1000)\n"
         "imp = where(lag(close, 1) / close > 0, 0, 1)\n"
         "e = ema(imp, w)\n"
         "clk = (log(e) + log(w)) / log((w - 1) / (w + 1)) + w - 1\n")
CLOCK_SIGNAL = "signal = clk / w\n"
# (the audit scaled clk by literals; the literal cap of C1 now limits that, so it is scaled by w)
CALENDAR = "signal = where(clk / w > 0.5, -1, 1)\n"
FAST = pipeline.Opts(jitter_n=2, perm_n=20, truncation_cuts=4, include_g8=False)


@pytest.fixture(scope="module")
def world():
    return synth_world(seed=31)


def test_the_clock_is_rejected_by_the_constant_probe():
    with pytest.raises(L.LangError) as e:
        L.parse(HDR.format(n="r05_clock", k="portfolio") + CLOCK + CLOCK_SIGNAL, "r05_clock")
    # imp is 0 on every known row (accepted: a zero series is harmless); e = ema(imp, w) is 0 too, and
    # clk has no finite value on any known row
    assert e.value.rule == "constant_subexpression" and e.value.line == 8


def test_the_clock_has_no_definite_value_and_no_start_dependence(world):
    prog = L.parse(HDR.format(n="r05_clock", k="portfolio") + CLOCK + CLOCK_SIGNAL, "r05_clock", probe=False)
    grid = pipeline.core_grid(world.core, C.CORE)
    W, raw, kn = pipeline.unit_full(prog, {"w": 800}, world.core, C.CORE, world.btc, grid)
    assert not np.isfinite(raw).any() and not W.any()          # imp is unknown at the first bar, 0 after: e == 0
    assert pipeline.start_cut_check(prog, {"w": 800}, world.core, C.CORE, world.btc, grid, raw, kn,
                                    np.random.default_rng(1), 6, 0.6) is None


def test_the_remembered_calendar_never_reaches_tier1(world, tmp_path, tmp_ledger):
    src = HDR.format(n="r05_calendar", k="portfolio") + CLOCK + CALENDAR
    f = tmp_path / "r05_calendar.omr"
    f.write_text(src, encoding="ascii")
    row = evaluate.evaluate_file(str(f), 0, provider=SynthProvider(world), opts=FAST, quiet=True, require_lock=False,
                                 p_max=0.025)
    assert row["code"] == "parse:constant_subexpression"                          # uncounted stage-1 rejection
    prog = L.parse(src, "r05_calendar", probe=False)                               # even without the probe:
    fd, bd = dev_only(world)
    s1 = pipeline.stage1(prog, {"w": 800}, fd, bd, np.random.default_rng(2), FAST)
    # clk is NaN wherever known (e == 0), so the condition is False and the signal is a constant +1 once
    # known: one switch-on per symbol, no calendar
    assert not s1["ok"] and s1["code"] == "activity_dev" and s1["direction_changes_dev"] <= 2


def test_a_hold_latch_carries_no_memory_of_the_frame_start(world):
    """`hold(hour < 1, ...)` as a one-shot impulse: unbounded it would be 0 until the first midnight and
    1 forever after (a 'frame has started' flag); windowed it is 1 on every known row."""
    body = ("hz = param(48, 24, 96)\n"
            "st = hold(hour < 1, hour < 0, hour < 0, hour < 0, hz)\nsignal = st * sign(ret(close, 1))\n")
    with pytest.raises(L.LangError) as e:
        L.parse(HDR.format(n="x_latch", k="single") + body, "x_latch")
    assert e.value.rule == "constant_subexpression"
    prog = L.parse(HDR.format(n="x_latch", k="single") + body.replace("signal = st * sign(ret(close, 1))", "signal = st"),
                   "x_latch", probe=False)
    grid = pipeline.core_grid(world.core, C.CORE)
    W, raw, kn = pipeline.unit_full(prog, L.default_params(prog), world.core, C.CORE, world.btc, grid)
    assert (raw[kn] == 1.0).all()
    assert pipeline.start_cut_check(prog, L.default_params(prog), world.core, C.CORE, world.btc, grid, raw, kn,
                                    np.random.default_rng(3), 6, 0.6) is None


def test_two_components_with_different_warm_ups_switch_on_together(world):
    body = ("a = param(5, 2, 8)\nb = param(300, 200, 400)\n"
            "signal = sign(sma(ret(close, 1), a)) + sign(sma(ret(close, 1), b))\n")
    prog = L.parse(HDR.format(n="x_warm", k="single") + body, "x_warm")
    grid = pipeline.core_grid(world.core, C.CORE)
    W, raw, kn = pipeline.unit_full(prog, L.default_params(prog), world.core, C.CORE, world.btc, grid)
    for c in (500, 2000, 9000):
        _, rc, kc = pipeline.unit_full(prog, L.default_params(prog), world.core, C.CORE, world.btc, grid,
                                       start=grid[c])
        assert int(np.argmax(kc[:, 0])) == 300 and not kc[:300].any()           # known 300 rows after any start
        assert pipeline.start_cut_agrees(rc, kc, raw[c:], kn[c:])


@pytest.mark.parametrize("stem", ["gen000_sma_cross_ls", "gen000_donchian_ls", "gen000_rsi_meanrev_ls",
                                  "gen000_voltarget_trend_ls", "gen000_funding_carry", "kernel_kitchen_sink",
                                  "kernel_noise_single", "kernel_noise_portfolio"])
def test_every_kernel_program_is_start_cut_invariant(world, stem):
    prog = kernel_program(stem)
    q = L.default_params(prog)
    grid = pipeline.core_grid(world.core, C.CORE)
    W, raw, kn = pipeline.unit_full(prog, q, world.core, C.CORE, world.btc, grid)
    assert kn.any()
    assert pipeline.start_cut_check(prog, q, world.core, C.CORE, world.btc, grid, raw, kn,
                                    np.random.default_rng(5), 6, 0.9) is None
