"""U7: funding8h is bounded in time in every unit: known only while the latest visible settlement is at
most 2 x min(its interval, 8) hours old, computed as of each row from the full funding table where frames
and panels are assembled (funding.fresh); R2's in-play freshness uses the same cap; the lookback leaf of
funding8h is 17. Synthetic data only (the core identity is proved by tests/test_core_identity.py)."""
import numpy as np
import pandas as pd
import pytest

from conftest import NOFUND_FROM, NOFUND_TO, TRAP_NOFUND, prog_text, synth_raw, synth_udata
from omr import constants as C
from omr import datasets as D
from omr import interp as X
from omr import lang as L
from omr import universe as U
from omr import upipeline as UP

H = pd.Timedelta(hours=1)


def _known(body, frame, kind="single"):
    prog = L.parse(prog_text(body, kind=kind), "x_test", probe=False)
    raw, kn = X.evaluate_full(prog, L.default_params(prog), [frame], frame)
    return kn[:, 0]


def test_u7_a_funding_gap_makes_funding8h_unknown_in_a_core_frame():
    raw = synth_raw(start="2021-01-01 00:00", end="2021-03-31 23:00", seed=4)
    a, b = pd.Timestamp("2021-02-10 00:00", tz="UTC"), pd.Timestamp("2021-02-13 00:00", tz="UTC")
    fu = raw["funding"]
    raw["funding"] = fu[(fu.index <= a) | (fu.index >= b)]               # settlements at a, then b: a 72 h gap
    f = D.assemble_frame(raw, D.PROGRAM_EXTRA)
    kn = _known("signal = sign(funding8h)\n", f)
    t = f.index
    assert kn[t == a + 16 * H].all() and not kn[t == a + 17 * H].any()   # 2 x 8 hours, then unknown
    gap = (t > a + 16 * H) & (t < b)
    assert not kn[gap].any() and kn[t == b].all()                        # known again at the next settlement
    assert kn[(t >= t[0] + 24 * H) & (t <= a + 16 * H)].all()
    fresh = f["funding.fresh"].to_numpy(dtype=bool)
    v = (f["funding.rate"] * 8.0 / f["funding.interval_hours"]).to_numpy(dtype=np.float64)
    assert np.array_equal(kn, fresh & np.isfinite(v))
    # a window over funding8h needs every row of its window fresh
    n_kn = _known("n = param(10, 5, 20)\nsignal = sign(sma(funding8h, n))\n", f)
    assert not n_kn[(t >= b) & (t < b + 9 * H)].any() and n_kn[t == b + 9 * H].all()


def test_u7_the_interval_is_capped_at_8_hours_for_funding8h_and_r2():
    raw = synth_raw(start="2021-01-01 00:00", end="2021-01-20 23:00", seed=5, funding_every=24)
    raw["funding"]["interval_hours"] = 24.0
    f = D.assemble_frame(raw, D.PROGRAM_EXTRA)
    kn = _known("signal = sign(funding8h)\n", f)
    h = f.index.hour
    assert kn[(h <= 16) & (f.index.day > 1)].all() and not kn[h > 16].any()
    grid = f.index.asi8
    st = raw["funding"].index.asi8
    fr = U.funding_fresh(grid, st, np.full(len(st), 24.0))
    assert np.array_equal(fr, f["funding.fresh"].to_numpy(dtype=bool))
    assert fr[h == 16].all() and not fr[h == 17].any()
    four = U.funding_fresh(grid, st, np.full(len(st), 4.0))              # below the cap: 2 x its own interval
    assert four[h == 8].all() and not four[h == 9].any()


def test_u7_universe_panels_carry_the_same_freshness_and_windows_over_funding8h_wait_for_it():
    ud = synth_udata(n=24)
    fp = UP.FullPanel(ud, "top30")
    k = fp.symbols.index(TRAP_NOFUND)
    assert fp.col("funding.fresh") is fp.fresh
    t = fp.grid
    gap = (t > pd.Timestamp(NOFUND_FROM, tz="UTC") + 16 * H) & (t < pd.Timestamp(NOFUND_TO, tz="UTC"))
    assert gap.any() and not fp.fresh[gap, k].any()
    prog = L.parse(prog_text('unit = "top30"\nn = param(10, 5, 20)\nsignal = cs_demean(sma(funding8h, n))\n',
                             kind="portfolio"), "x_test", probe=False)
    bu = UP.Blocked(ud, "top30", fields=UP.program_fields(prog))
    _, raw, kn = bu.unit(prog, L.default_params(prog))
    j = bu.symbols.index(TRAP_NOFUND)
    settle = ud.tables(TRAP_NOFUND)["funding"].index
    s0 = settle[settle > pd.Timestamp(NOFUND_TO, tz="UTC")][0]           # the first settlement after the gap
    g = bu.grid
    assert not kn[(g >= s0) & (g < s0 + 9 * H), j].any()                 # n = 10 fresh rows after the restart
    assert kn[g == s0 + 9 * H, j].all()


@pytest.mark.parametrize("body,hours", [
    ("signal = sign(funding8h)\n", 17),
    ("n = param(10, 5, 20)\nsignal = sign(sma(funding8h, n))\n", 19 + 17),
    ("signal = sign(btc(funding8h))\n", 17),
    ("n = param(10, 5, 20)\nsignal = sign(lag(funding8h, n) + ret(close, n))\n", 20 + 17),
])
def test_u7_lookback_leaf_of_funding8h_is_17(body, hours):
    assert L.parse(prog_text(body), "x_test", probe=False).lookback_hours == hours
