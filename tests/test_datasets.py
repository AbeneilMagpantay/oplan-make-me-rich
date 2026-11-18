"""Point-in-time alignment tests for the dataset registry and indicator helpers."""
import numpy as np
import pandas as pd

from omr import datasets as D
from omr import indicators as ind
from conftest import synth_raw


def grid(start="2022-03-01 00:00", hours=48):
    return pd.date_range(pd.Timestamp(start, tz="UTC"), periods=hours, freq="h").as_unit("ns")


def test_align_to_grid_never_earlier_than_visible_from():
    g = grid()
    rows = pd.DataFrame({"x": [1.0, 2.0, 3.0]},
                        index=pd.DatetimeIndex(["2022-02-28 20:00", "2022-03-01 05:00", "2022-03-01 05:30"], tz="UTC"))
    vf = pd.DatetimeIndex(["2022-02-28 20:00", "2022-03-01 05:00", "2022-03-01 05:30"], tz="UTC")
    asof, new = D.align_to_grid(rows, vf, g)
    assert asof["x"].iloc[0] == 1.0 and not new[0]         # pre-grid row seeds as-of, not new
    assert asof["x"].iloc[4] == 1.0                          # 04:00 still sees the old value
    assert asof["x"].iloc[5] == 2.0 and new[5]               # visible from 05:00
    assert asof["x"].iloc[6] == 3.0 and new[6]               # 05:30 -> first grid bar >= 05:30 is 06:00
    assert new.sum() == 2


def test_funding_settlement_visible_from_its_own_bar():
    raw = synth_raw(start="2022-03-01 00:00", end="2022-03-03 23:00", seed=1)
    fr = D.assemble_frame(raw, ("funding",))
    t08 = pd.Timestamp("2022-03-01 08:00", tz="UTC")
    t07 = pd.Timestamp("2022-03-01 07:00", tz="UTC")
    rate = raw["funding"].loc[t08, "rate"]
    assert fr.loc[t08, "funding_rate"] == rate                  # settled at 08:00 -> bar 08:00
    assert fr.loc[t07, "funding_rate"] == 0.0                   # not before
    assert fr.loc[t08, "funding.new"] and not fr.loc[t07, "funding.new"]
    assert fr.loc[t07, "funding.rate"] == raw["funding"].loc[pd.Timestamp("2022-03-01 00:00", tz="UTC"), "rate"]
    nonzero = fr.index[fr["funding_rate"] != 0]
    assert set(nonzero.hour) <= {0, 8, 16}


def test_frames_carry_funding_rate_without_declaring_funding():
    raw = synth_raw(start="2022-03-01 00:00", end="2022-03-02 23:00", seed=2)
    fr = D.assemble_frame(raw, ())
    assert "funding_rate" in fr.columns
    assert not any(c.startswith("funding.") for c in fr.columns)


def test_resample_drops_incomplete_bar_and_align_waits_for_close():
    raw = synth_raw(start="2022-03-01 00:00", end="2022-03-03 13:00", seed=3)
    bars = D.assemble_frame(raw)
    d = ind.resample_ohlcv(bars, "1D")
    assert len(d) == 2                                           # 03-03 is incomplete
    day1 = bars.loc["2022-03-01"]
    assert d["close"].iloc[0] == day1["close"].iloc[-1]
    assert d["high"].iloc[0] == day1["high"].max()
    a = ind.align_to_base(d["close"], bars.index, "1D")
    assert np.isnan(a.loc[pd.Timestamp("2022-03-01 22:00", tz="UTC")])
    assert a.loc[pd.Timestamp("2022-03-01 23:00", tz="UTC")] == d["close"].iloc[0]   # visible in the closing bar
    assert a.loc[pd.Timestamp("2022-03-02 22:00", tz="UTC")] == d["close"].iloc[0]
    assert a.loc[pd.Timestamp("2022-03-02 23:00", tz="UTC")] == d["close"].iloc[1]
    b4 = ind.resample_ohlcv(bars, "4h")
    assert b4.index[0] == pd.Timestamp("2022-03-01 00:00", tz="UTC")
    a4 = ind.align_to_base(b4["close"], bars.index, "4h")
    assert np.isnan(a4.iloc[2]) and a4.iloc[3] == b4["close"].iloc[0]


def test_rsi_wilder_hand_values():
    # constant gains -> RSI 100; alternating equal moves -> RSI near 50
    up = pd.Series(np.arange(1.0, 40.0))
    assert ind.rsi_wilder(up, 14).iloc[-1] == 100.0
    alt = pd.Series([10.0 + (i % 2) for i in range(60)])
    r = ind.rsi_wilder(alt, 14).iloc[-1]
    assert 40.0 < r < 60.0
    assert np.isnan(ind.rsi_wilder(up, 14).iloc[13]) and not np.isnan(ind.rsi_wilder(up, 14).iloc[14])
