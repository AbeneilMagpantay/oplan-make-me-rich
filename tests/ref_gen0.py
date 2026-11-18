"""TRUSTED reference implementations of the five generation-0 baselines (tests only).

These are the pre-language Python strategies (kernel 2317921c, strategies/gen000_*.py), kept
verbatim in logic as plain functions so the tests can assert that the .omr ports produce identical
weights. They are never loaded by the kernel. Each returns the per-symbol signal on bars.index
(NaN = flat); the kernel's single-kind weight is signal / number of symbols.
"""
import numpy as np
import pandas as pd

from omr.indicators import align_to_base, resample_ohlcv, rsi_wilder, realised_vol, sma


def sma_cross_ls(bars, p):
    d = resample_ohlcv(bars, "1D")
    fast = sma(d["close"], p["fast"])
    slow = sma(d["close"], p["slow"])
    s = pd.Series(np.where(fast > slow, 1.0, -1.0), index=d.index)
    s[fast.isna() | slow.isna()] = np.nan
    return align_to_base(s, bars.index, "1D")


def donchian_ls(bars, p):
    d = resample_ohlcv(bars, "1D")
    hh_e = d["high"].rolling(p["entry"], min_periods=p["entry"]).max().shift(1).to_numpy()
    ll_e = d["low"].rolling(p["entry"], min_periods=p["entry"]).min().shift(1).to_numpy()
    hh_x = d["high"].rolling(p["exit"], min_periods=p["exit"]).max().shift(1).to_numpy()
    ll_x = d["low"].rolling(p["exit"], min_periods=p["exit"]).min().shift(1).to_numpy()
    c = d["close"].to_numpy()
    out = np.full(len(c), np.nan)
    pos = 0.0
    for i in range(len(c)):
        if np.isnan(hh_e[i]) or np.isnan(ll_e[i]):
            continue
        if c[i] > hh_e[i]:
            pos = 1.0
        elif c[i] < ll_e[i]:
            pos = -1.0
        elif pos == 1.0 and c[i] < ll_x[i]:
            pos = 0.0
        elif pos == -1.0 and c[i] > hh_x[i]:
            pos = 0.0
        out[i] = pos
    return align_to_base(pd.Series(out, index=d.index), bars.index, "1D")


def rsi_meanrev_ls(bars, p):
    """Python band in RSI points (20); the .omr band is centred (0.4 = 20 / 50)."""
    b4 = resample_ohlcv(bars, "4h")
    rsi = rsi_wilder(b4["close"], p["period"]).to_numpy()
    lo = 50.0 - p["band"]
    hi = 50.0 + p["band"]
    out = np.full(len(rsi), np.nan)
    pos = 0.0
    for i in range(len(rsi)):
        r = rsi[i]
        if np.isnan(r):
            continue
        if r < lo:
            pos = 1.0
        elif r > hi:
            pos = -1.0
        elif pos == 1.0 and r > 50.0:
            pos = 0.0
        elif pos == -1.0 and r < 50.0:
            pos = 0.0
        out[i] = pos
    return align_to_base(pd.Series(out, index=b4.index), bars.index, "4h")


def voltarget_trend_ls(bars, p):
    d = resample_ohlcv(bars, "1D")
    c = d["close"]
    ma = sma(c, p["sma"])
    vol = realised_vol(c, p["vol_lookback"], 365.0)
    direction = np.where(c > ma, 1.0, -1.0)
    v = vol.to_numpy()
    safe = np.where(v > 0.0, v, 1.0)
    size = np.where(v > 0.0, np.minimum(1.0, p["target_vol"] / safe), np.where(v == 0.0, 1.0, np.nan))
    s = pd.Series(direction * size, index=d.index)
    s[ma.isna() | vol.isna()] = np.nan
    return align_to_base(s, bars.index, "1D")


def funding_carry(bars, p):
    new = bars["funding.new"].to_numpy(dtype=bool)
    rate8 = (bars["funding.rate"] * 8.0 / bars["funding.interval_hours"])[new]
    f = rate8.rolling(p["lookback"], min_periods=p["lookback"]).mean()
    fv = f.to_numpy()
    sig = np.where(fv > p["hi"], -1.0, np.where(fv < p["lo"], 1.0, 0.0))
    sig = np.where(np.isnan(fv), np.nan, sig)
    ev = pd.Series(sig, index=rate8.index)
    return ev.reindex(bars.index).ffill()


# .omr program -> (reference function, param mapping from .omr names to reference names/values)
REFS = {
    "gen000_sma_cross_ls": (sma_cross_ls, lambda q: {"fast": q["fast"], "slow": q["slow"]}),
    "gen000_donchian_ls": (donchian_ls, lambda q: {"entry": q["entry"], "exit": q["exit"]}),
    "gen000_rsi_meanrev_ls": (rsi_meanrev_ls, lambda q: {"period": q["period"], "band": q["band"] * 50.0}),
    "gen000_voltarget_trend_ls": (voltarget_trend_ls, lambda q: {"sma": q["ma_n"], "vol_lookback": q["vol_lookback"],
                                                                 "target_vol": q["target_vol"]}),
    "gen000_funding_carry": (funding_carry, lambda q: {"lookback": q["lookback"], "hi": q["hi"], "lo": q["lo"]}),
}
# Python defaults (kernel 2317921c) for the record: the .omr defaults must map onto these.
PY_DEFAULTS = {
    "gen000_sma_cross_ls": {"fast": 20, "slow": 100},
    "gen000_donchian_ls": {"entry": 20, "exit": 10},
    "gen000_rsi_meanrev_ls": {"period": 14, "band": 20.0},
    "gen000_voltarget_trend_ls": {"sma": 50, "vol_lookback": 30, "target_vol": 0.40},
    "gen000_funding_carry": {"lookback": 21, "hi": 0.0003, "lo": -0.0001},
}
PY_BOUNDS = {
    "gen000_sma_cross_ls": {"fast": (5, 60), "slow": (50, 250)},
    "gen000_donchian_ls": {"entry": (10, 60), "exit": (5, 30)},
    "gen000_rsi_meanrev_ls": {"period": (7, 28), "band": (10.0, 30.0)},
    "gen000_voltarget_trend_ls": {"sma": (20, 150), "vol_lookback": (10, 90), "target_vol": (0.2, 0.8)},
    "gen000_funding_carry": {"lookback": (6, 90), "hi": (0.00015, 0.001), "lo": (-0.0005, 0.0)},
}


def reference_weights(stem: str, q: dict, frames: dict, symbols, grid) -> np.ndarray:
    """Reference single-kind weights on `grid`: each symbol on its own frame, signal / K, NaN -> 0."""
    fn, mp = REFS[stem]
    cols = []
    for s in symbols:
        sig = fn(frames[s], mp(q)).reindex(grid).to_numpy(dtype=np.float64)
        cols.append(np.where(np.isfinite(sig), np.clip(sig, -1.0, 1.0), 0.0) / len(symbols))
    return np.column_stack(cols)
