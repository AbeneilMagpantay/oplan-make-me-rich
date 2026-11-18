"""TRUSTED reference implementations of the five generation-0 baselines (tests only; never loaded by
the kernel).

OLD_*: the pre-language Python strategies (kernel 2317921c, strategies/gen000_*.py), kept in logic as
plain functions (pandas arithmetic, unbounded state machines). They are the "before".
NAIVE_*: independent naive implementations of the CURRENT definitions (LANGUAGE.md): window sums in
plain Python loops, oldest value first; two-pass standard deviations; the finite RSI; the windowed
hold re-run from flat for every row; and the knownness rule (a value only where every input window
exists). Each returns the per-symbol signal on bars.index (NaN = unknown or NaN); the kernel's
single-kind weight is signal / number of symbols.
"""
import math

import numpy as np
import pandas as pd

from omr.indicators import align_to_base, resample_ohlcv, rsi_wilder, realised_vol, sma


# ---------------------------------------------------------------- the "before" (pre-language Python)

def old_sma_cross_ls(bars, p):
    d = resample_ohlcv(bars, "1D")
    fast = sma(d["close"], p["fast"])
    slow = sma(d["close"], p["slow"])
    s = pd.Series(np.where(fast > slow, 1.0, -1.0), index=d.index)
    s[fast.isna() | slow.isna()] = np.nan
    return align_to_base(s, bars.index, "1D")


def old_voltarget_trend_ls(bars, p):
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


def old_funding_carry(bars, p):
    new = bars["funding.new"].to_numpy(dtype=bool)
    rate8 = (bars["funding.rate"] * 8.0 / bars["funding.interval_hours"])[new]
    f = rate8.rolling(p["lookback"], min_periods=p["lookback"]).mean()
    fv = f.to_numpy()
    sig = np.where(fv > p["hi"], -1.0, np.where(fv < p["lo"], 1.0, 0.0))
    sig = np.where(np.isnan(fv), np.nan, sig)
    ev = pd.Series(sig, index=rate8.index)
    return ev.reindex(bars.index).ffill()


def old_donchian_ls(bars, p):
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


def old_rsi_meanrev_ls(bars, p):
    b4 = resample_ohlcv(bars, "4h")
    rsi = rsi_wilder(b4["close"], p["period"]).to_numpy()
    lo, hi = 50.0 - p["band"], 50.0 + p["band"]
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


# ---------------------------------------------------------------- naive references of the current definitions

def _seq_sum(xs):
    s = 0.0
    for v in xs:
        s += v
    return s


def _naive_hold(el, xl, es, xs, kn, h):
    """State at t: the machine from flat over rows t-h+1..t; NaN unless all four inputs are known on
    all h rows."""
    n = len(el)
    out = np.full(n, np.nan)
    for t in range(h - 1, n):
        if not kn[t - h + 1:t + 1].all():
            continue
        st = 0.0
        for k in range(t - h + 1, t + 1):
            a, b, c, d = el[k], xl[k], es[k], xs[k]
            if st == 0.0:
                st = 1.0 if (a and not c) else (-1.0 if (c and not a) else 0.0)
            elif st == 1.0:
                st = -1.0 if c else (0.0 if b else 1.0)
            else:
                st = 1.0 if a else (0.0 if d else -1.0)
        out[t] = st
    return out


def naive_donchian_ls(bars, p):
    d = resample_ohlcv(bars, "1D")
    hi_, lo_, c = d["high"].to_numpy(), d["low"].to_numpy(), d["close"].to_numpy()
    n = len(c)

    def prior(arr, w, f):
        out = np.full(n, np.nan)
        for t in range(w, n):
            out[t] = f(arr[t - w:t])                                       # the w completed days before t
        return out
    ue, le = prior(hi_, p["entry"], max), prior(lo_, p["entry"], min)
    ux, lx = prior(hi_, p["exit"], max), prior(lo_, p["exit"], min)
    kn = ~(np.isnan(ue) | np.isnan(le) | np.isnan(ux) | np.isnan(lx))
    with np.errstate(invalid="ignore"):
        out = _naive_hold(c > ue, c < lx, c < le, c > ux, kn, p["horizon"])
    return align_to_base(pd.Series(out, index=d.index), bars.index, "1D")


def naive_rsi_meanrev_ls(bars, p):
    b4 = resample_ohlcv(bars, "4h")
    x = b4["close"].to_numpy()
    n_, band = p["period"], p["band"]
    m = 10 * n_
    w = np.power(1.0 - 1.0 / n_, np.arange(m - 1, -1, -1, dtype=np.float64))
    r = np.full(len(x), np.nan)
    for t in range(m, len(x)):
        G = Ls = 0.0
        for i in range(m):
            k = t - m + 1 + i
            dlt = x[k] - x[k - 1]
            if dlt > 0:
                G += w[i] * dlt
            elif dlt < 0:
                Ls += w[i] * (-dlt)
        if G + Ls > 0:
            r[t] = (G - Ls) / (G + Ls)
    kn = np.zeros(len(x), dtype=bool)
    kn[m:] = True                                                          # the 4h closes are complete
    with np.errstate(invalid="ignore"):
        out = _naive_hold(r < -band, r > 0, r > band, r < 0, kn, p["horizon"])
    return align_to_base(pd.Series(out, index=b4.index), bars.index, "4h")


def naive_voltarget_trend_ls(bars, p):
    d = resample_ohlcv(bars, "1D")
    c = d["close"].to_numpy()
    n = len(c)
    ma_n, vl, tv = p["ma_n"], p["vol_lookback"], p["target_vol"]
    out = np.full(n, np.nan)
    for t in range(max(ma_n - 1, vl), n):
        ma = _seq_sum(c[t - ma_n + 1:t + 1]) / ma_n
        lr = [math.log(c[k] / c[k - 1]) for k in range(t - vl + 1, t + 1)]
        mu = _seq_sum(lr) / vl
        ss = _seq_sum([(v - mu) * (v - mu) for v in lr])
        vol = math.sqrt(ss / (vl - 1)) * math.sqrt(365.0)
        size = min(1.0, tv / vol) if vol > 0 else np.nan
        out[t] = np.sign(c[t] - ma) * size
    return align_to_base(pd.Series(out, index=d.index), bars.index, "1D")


# .omr program -> (reference of the CURRENT definition, map from .omr params to its params)
REFS = {
    "gen000_sma_cross_ls": (old_sma_cross_ls, lambda q: {"fast": q["fast"], "slow": q["slow"]}),
    "gen000_donchian_ls": (naive_donchian_ls, lambda q: dict(q)),
    "gen000_rsi_meanrev_ls": (naive_rsi_meanrev_ls, lambda q: dict(q)),
    "gen000_voltarget_trend_ls": (naive_voltarget_trend_ls, lambda q: dict(q)),
    "gen000_funding_carry": (old_funding_carry, lambda q: {"lookback": q["lookback"], "hi": q["hi"], "lo": q["lo"]}),
}
# .omr params -> the pre-language Python params (defaults and bounds must map onto these)
PY_MAP = {
    "gen000_sma_cross_ls": lambda q: {"fast": q["fast"], "slow": q["slow"]},
    "gen000_donchian_ls": lambda q: {"entry": q["entry"], "exit": q["exit"]},
    "gen000_rsi_meanrev_ls": lambda q: {"period": q["period"], "band": q["band"] * 50.0},
    "gen000_voltarget_trend_ls": lambda q: {"sma": q["ma_n"], "vol_lookback": q["vol_lookback"],
                                            "target_vol": q["target_vol"]},
    "gen000_funding_carry": lambda q: {"lookback": q["lookback"], "hi": q["hi"], "lo": q["lo"]},
}
OLD = {"gen000_sma_cross_ls": old_sma_cross_ls, "gen000_donchian_ls": old_donchian_ls,
       "gen000_rsi_meanrev_ls": old_rsi_meanrev_ls, "gen000_voltarget_trend_ls": old_voltarget_trend_ls,
       "gen000_funding_carry": old_funding_carry}
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


def _weights_from(fn, q, frames, symbols, grid):
    cols = []
    for s in symbols:
        sig = fn(frames[s], q).reindex(grid).to_numpy(dtype=np.float64)
        cols.append(np.where(np.isfinite(sig), np.clip(sig, -1.0, 1.0), 0.0) / len(symbols))
    return np.column_stack(cols)


def reference_weights(stem: str, q: dict, frames: dict, symbols, grid) -> np.ndarray:
    """Weights of the reference of the CURRENT definition on `grid` (each symbol on its own frame)."""
    fn, mp = REFS[stem]
    return _weights_from(fn, mp(q), frames, symbols, grid)


def old_weights(stem: str, q: dict, frames: dict, symbols, grid) -> np.ndarray:
    """Weights of the pre-language Python strategy at the corresponding params."""
    return _weights_from(OLD[stem], PY_MAP[stem](q), frames, symbols, grid)
