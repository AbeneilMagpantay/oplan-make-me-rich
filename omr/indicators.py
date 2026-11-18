"""Indicator helpers for strategies. Kernel module.

Point-in-time rules
- resample_ohlcv returns COMPLETED coarse bars only: a coarse bar is kept only if every
  base bar inside it is present (the last, partial coarse bar is dropped).
- align_to_base makes a coarse-bar value visible only from the base bar in which that
  coarse bar CLOSED (for daily bars: the 23:00 bar of that day, whose close is midnight),
  then forward-fills. Values are indexed by coarse-bar OPEN time.
All rolling helpers use only past and current values.
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd

__all__ = ["resample_ohlcv", "align_to_base", "sma", "ema", "rsi_wilder", "atr", "realised_vol", "donchian"]

BASE = pd.Timedelta(hours=1)

_SUM_COLS = ("volume", "quote_volume", "trades", "taker_buy_volume", "taker_buy_quote_volume", "funding_rate")


def _ns(idx) -> np.ndarray:
    return pd.DatetimeIndex(idx).as_unit("ns").asi8


def resample_ohlcv(bars: pd.DataFrame, rule: str) -> pd.DataFrame:
    """Aggregate 1h bars to `rule` (e.g. "4h", "1D"), completed bars only.

    Bins are aligned to the UTC epoch (daily bins start at 00:00 UTC). Output index =
    coarse-bar open time. Columns: open, high, low, close, plus sums of volume-type
    columns and funding_rate when present, and gap_bars (count of gap-filled base bars).
    """
    F = pd.Timedelta(rule)
    if F < BASE or F % BASE != pd.Timedelta(0):
        raise ValueError("rule must be a whole multiple of 1h")
    n_per = int(F / BASE)
    t = _ns(bars.index)
    f_ns = int(F.value)
    key = t - (t % f_ns)
    # positions where a new bin starts
    starts = np.r_[0, np.nonzero(key[1:] != key[:-1])[0] + 1]
    ends = np.r_[starts[1:], len(t)]
    counts = ends - starts
    complete = (counts == n_per) & (t[ends - 1] == key[starts] + f_ns - int(BASE.value))
    s, e = starts[complete], ends[complete]
    o = bars["open"].to_numpy(dtype=np.float64)
    h = bars["high"].to_numpy(dtype=np.float64)
    lo = bars["low"].to_numpy(dtype=np.float64)
    c = bars["close"].to_numpy(dtype=np.float64)
    out = {"open": o[s], "close": c[e - 1]}
    if len(s):
        out["high"] = np.maximum.reduceat(h, starts)[complete]
        out["low"] = np.minimum.reduceat(lo, starts)[complete]
    else:
        out["high"] = np.zeros(0)
        out["low"] = np.zeros(0)
    for col in _SUM_COLS:
        if col in bars.columns:
            out[col] = np.add.reduceat(bars[col].to_numpy(dtype=np.float64), starts)[complete] if len(s) else np.zeros(0)
    if "is_gap" in bars.columns:
        g = bars["is_gap"].to_numpy(dtype=np.float64)
        out["gap_bars"] = np.add.reduceat(g, starts)[complete] if len(s) else np.zeros(0)
    idx = pd.DatetimeIndex(pd.to_datetime(key[s], unit="ns", utc=True)).as_unit("ns")
    idx.name = "open_time"
    cols = ["open", "high", "low", "close"] + [k for k in out if k not in ("open", "high", "low", "close")]
    return pd.DataFrame({k: out[k] for k in cols}, index=idx)


def align_to_base(values, base_index: pd.DatetimeIndex, rule: str):
    """Put coarse-bar values (indexed by coarse OPEN time) on the base 1h index.

    A value becomes visible at base bar (coarse_open + rule - 1h), the bar in which the
    coarse bar closed, and is forward-filled until the next one. NaN before the first.
    """
    F = pd.Timedelta(rule)
    shifted = values.copy()
    shifted.index = pd.DatetimeIndex(values.index).as_unit("ns") + (F - BASE)
    base = pd.DatetimeIndex(base_index).as_unit("ns")
    return shifted.reindex(base, method="ffill")


def sma(x: pd.Series, n: int) -> pd.Series:
    return x.rolling(int(n), min_periods=int(n)).mean()


def ema(x: pd.Series, n: int) -> pd.Series:
    return x.ewm(span=int(n), adjust=False, min_periods=int(n)).mean()


def _wilder(x: np.ndarray, n: int) -> np.ndarray:
    """Wilder smoothing: first value = mean of the first n valid inputs, then
    y[t] = y[t-1] + (x[t] - y[t-1]) / n. Leading NaNs are skipped."""
    out = np.full(len(x), np.nan)
    valid = np.nonzero(np.isfinite(x))[0]
    if len(valid) < n:
        return out
    start = valid[0]
    if not np.all(np.isfinite(x[start:start + n])):
        # require a contiguous warm-up window
        return out
    y = float(np.mean(x[start:start + n]))
    out[start + n - 1] = y
    for t in range(start + n, len(x)):
        v = x[t]
        if not math.isfinite(v):
            out[t] = y
            continue
        y = y + (v - y) / n
        out[t] = y
    return out


def rsi_wilder(close: pd.Series, n: int = 14) -> pd.Series:
    n = int(n)
    c = close.to_numpy(dtype=np.float64)
    d = np.r_[np.nan, np.diff(c)]
    gain = np.where(np.isfinite(d), np.maximum(d, 0.0), np.nan)
    loss = np.where(np.isfinite(d), np.maximum(-d, 0.0), np.nan)
    ag = _wilder(gain, n)
    al = _wilder(loss, n)
    with np.errstate(divide="ignore", invalid="ignore"):
        rs = ag / al
        rsi = 100.0 - 100.0 / (1.0 + rs)
    rsi = np.where((al == 0) & np.isfinite(ag), 100.0, rsi)
    rsi = np.where((al == 0) & (ag == 0), 50.0, rsi)
    return pd.Series(rsi, index=close.index, name="rsi")


def atr(bars: pd.DataFrame, n: int = 14) -> pd.Series:
    h = bars["high"].to_numpy(dtype=np.float64)
    lo = bars["low"].to_numpy(dtype=np.float64)
    c = bars["close"].to_numpy(dtype=np.float64)
    pc = np.r_[np.nan, c[:-1]]
    tr = np.nanmax(np.vstack([h - lo, np.abs(h - pc), np.abs(lo - pc)]), axis=0)
    return pd.Series(_wilder(tr, int(n)), index=bars.index, name="atr")


def realised_vol(close: pd.Series, n: int, periods_per_year: float) -> pd.Series:
    """Rolling std (ddof=1) of the last n log returns log(c_t / c_t-1), annualised by
    sqrt(periods_per_year). (The log of the ratio, not a difference of logs: a constant
    power-of-two price rescale then leaves the result bit-identical.)"""
    lr = np.log(close / close.shift(1))
    return lr.rolling(int(n), min_periods=int(n)).std(ddof=1) * math.sqrt(periods_per_year)


def donchian(high: pd.Series, low: pd.Series, n: int):
    """(upper, lower) = rolling max of high and min of low over the last n bars INCLUDING
    the current one. Use .shift(1) for 'prior n completed bars'."""
    n = int(n)
    return high.rolling(n, min_periods=n).max(), low.rolling(n, min_periods=n).min()
