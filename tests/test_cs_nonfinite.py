"""U3: in universe units a cs_* is computed across the in-play symbols whose input is known AND finite; the
at-least-UNIVERSE_MIN_CS rule counts those; an in-play symbol with a known but non-finite input stays known
with value NaN, so one symbol can no longer flatten the row. Synthetic panels only."""
import numpy as np
import pandas as pd
import pytest

from omr import constants as C
from omr import interp as X
from omr import lang as L

HDR = ('name = "x_test"\nfamily = "other"\nkind = "portfolio"\nunit = "top30"\n'
       'hypothesis = "non finite inputs inside a cross section"\n')
FNS = ("cs_mean", "cs_demean", "cs_scale", "cs_rank")


def _panel(K=12, T=6, seed=1):
    idx = pd.date_range("2021-01-01", periods=T, freq="h", tz="UTC")
    rng = np.random.default_rng(seed)
    opn = 10.0 + rng.uniform(0, 1, (T, K))
    cls = opn * np.exp(0.01 * rng.standard_normal((T, K)))
    cols = {"open": opn, "close": cls, "high": np.maximum(opn, cls) + 0.1, "low": np.minimum(opn, cls) - 0.1,
            "volume": rng.uniform(1, 10, (T, K))}
    cols["taker_buy_volume"] = cols["volume"] * rng.uniform(0.2, 0.8, (T, K))
    return idx, cols


def _eval(body, idx, cols):
    K = cols["close"].shape[1]
    T = len(idx)
    panel = X.Panel(idx, [f"S{i:02d}USDT" for i in range(K)], lambda n: cols[n], np.ones((T, K), bool),
                    np.ones(T, bool))
    prog = L.parse(HDR + body, "x_test", probe=False)
    return X.evaluate_full(prog, {}, panel, None)


def _expected(fn, x):
    """The cross section of the finite values x (1-d), as the kernel computes it."""
    if fn == "cs_mean":
        return np.full_like(x, np.cumsum(x)[-1] / len(x))
    if fn == "cs_demean":
        return x - np.cumsum(x)[-1] / len(x)
    if fn == "cs_scale":
        return x / np.cumsum(np.abs(x))[-1]
    r = pd.Series(x).rank(method="average").to_numpy()
    return 2.0 * (r - 1.0) / (len(x) - 1.0) - 1.0


@pytest.mark.parametrize("fn", FNS)
def test_u3_a_zero_over_zero_input_is_a_known_nan_and_the_row_survives(fn):
    idx, cols = _panel()
    for c in ("open", "close", "high", "low"):
        cols[c][2, 4] = 10.0                                         # a frozen bar: (close - open) / (high - low) = 0/0
    raw, kn = _eval(f"signal = {fn}((close - open) / (high - low))\n", idx, cols)
    assert kn[2].all()                                               # every in-play symbol stays known
    assert np.isnan(raw[2, 4]) and np.isfinite(np.delete(raw[2], 4)).all()
    with np.errstate(all="ignore"):
        x = (cols["close"][2] - cols["open"][2]) / (cols["high"][2] - cols["low"][2])
    np.testing.assert_array_equal(np.delete(raw[2], 4), _expected(fn, np.delete(x, 4)))
    assert np.isfinite(raw[[0, 1, 3, 4, 5]]).all()


@pytest.mark.parametrize("fn", FNS)
def test_u3_a_zero_volume_hour(fn):
    idx, cols = _panel(K=14)
    body = f"signal = {fn}(taker_buy_volume / volume)\n"
    for c in ("volume", "taker_buy_volume"):
        cols[c][3, :] = 0.0                                          # every symbol: 0/0 at row 3
        cols[c][1, :3] = 0.0                                         # three symbols: 0/0 at row 1
    raw, kn = _eval(body, idx, cols)
    assert not kn[3].any() and np.isnan(raw[3]).all()                # no finite input: under 10, unknown for everyone
    assert kn[1].all() and np.isnan(raw[1, :3]).all()                # 11 finite inputs: known; the three are NaN
    x = cols["taker_buy_volume"][1, 3:] / cols["volume"][1, 3:]
    np.testing.assert_array_equal(raw[1, 3:], _expected(fn, x))
    for c in ("volume", "taker_buy_volume"):
        cols[c][1, :5] = 0.0                                         # five symbols: 9 finite inputs < 10
    raw, kn = _eval(body, idx, cols)
    assert not kn[1].any()
    assert kn[[0, 2, 4, 5]].all()
