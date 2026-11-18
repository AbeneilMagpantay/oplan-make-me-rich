"""Constant probe (H1a). Kernel module.

At parse time, with the default params, every NUMERIC series node of a program is evaluated on a
fixed synthetic probe panel: two years of hourly bars for two symbols and for BTC (fixed seed), with
trends and volatility regimes, a daily volume cycle, funding settlements that swing through
positive and negative regimes, and mark-price bars with a few missing hours.
- A numeric node that has the same value on every known row is rejected (`constant_subexpression`):
  a constant built without literals (`close / close`, `rank(x, 1)`, `x - x`) would escape the G5
  jitter, so it is not allowed.
- A numeric node with no known row on the panel is rejected (`probe_undefined`): its warm-up exceeds
  two years, so it could never be known for most of DEV.
Boolean nodes are not probed (a rare-event condition may legitimately never fire on the panel).
The panel is built once per process; nothing here reads real data.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from omr import datasets as D
from omr import lang as L

SEED = 20261119
START = "2020-01-06 00:00"           # a Monday
DAYS = 730
_PANEL = None


def synthetic_symbol(rng, price0: float, start: str = START, hours: int = DAYS * 24) -> dict:
    """Raw klines / funding / mark tables of a synthetic perp (also used by the calibration dry run)."""
    T = hours
    idx = pd.date_range(pd.Timestamp(start, tz="UTC"), periods=T, freq="h").as_unit("ns")
    reg_len = 24 * 30
    nreg = T // reg_len + 1
    reg = np.repeat(np.arange(nreg), reg_len)[:T]
    drift = rng.normal(0.0, 0.0004, nreg)
    vol = rng.uniform(0.003, 0.02, nreg)
    lr = drift[reg] + vol[reg] * rng.standard_normal(T)
    close = price0 * np.exp(np.cumsum(lr))
    opn = np.r_[price0, close[:-1]]
    spread = np.abs(vol[reg] * rng.standard_normal(T)) * close
    high = np.maximum(opn, close) + spread
    low = np.minimum(opn, close) - spread
    hour = np.asarray(idx.hour, dtype=np.float64)
    volume = np.exp(rng.normal(2.0, 0.5, T)) * (1.0 + 0.5 * np.sin(2 * np.pi * hour / 24.0)) * (1.0 + 20.0 * vol[reg])
    taker = volume * rng.uniform(0.3, 0.7, T)
    kl = pd.DataFrame({"open": opn, "high": high, "low": low, "close": close, "volume": volume,
                       "quote_volume": volume * close * (1.0 + 0.001 * rng.standard_normal(T)),
                       "trades": np.round(volume * rng.uniform(50, 150, T)),
                       "taker_buy_volume": taker, "taker_buy_quote_volume": taker * close,
                       "is_gap": np.zeros(T, dtype=bool)}, index=idx)
    kl.index.name = "open_time"
    m = 1.0 + 0.0005 * rng.standard_normal(T)
    mo, mc = opn * m, close * m
    mark = pd.DataFrame({"open": mo, "high": np.maximum(mo, mc) + 0.9 * spread, "low": np.minimum(mo, mc) - 0.9 * spread,
                         "close": mc, "samples": 3600.0}, index=idx)
    mark = mark[rng.uniform(size=T) > 0.01]                # about 1% of mark bars missing
    mark.index.name = "open_time"
    ft = idx[idx.hour % 8 == 0]
    day = np.arange(len(ft)) / 3.0
    rate = 0.0002 + 0.0007 * np.sin(2 * np.pi * day / 60.0) + 0.0001 * rng.standard_normal(len(ft))
    fu = pd.DataFrame({"rate": rate, "interval_hours": 8.0, "offset_ms": 0.0}, index=ft)
    fu.index.name = "settle_time"
    return {"klines": kl, "funding": fu, "mark_klines": mark}


def panel():
    """(symbol A frame, symbol B frame, BTC frame), built once per process."""
    global _PANEL
    if _PANEL is None:
        rng = np.random.default_rng(SEED)
        raws = [synthetic_symbol(rng, p0) for p0 in (100.0, 7.5, 30000.0)]
        _PANEL = tuple(D.assemble_frame(r, D.PROGRAM_EXTRA) for r in raws)
    return _PANEL


def check(prog: L.Program) -> None:
    from omr import interp as X
    a, b, btc = panel()
    frames = [a] if prog.kind == "single" else [a, b]
    rec = []
    X.evaluate_full(prog, L.default_params(prog), frames, btc, record=rec)
    for node, s in rec:
        kn = np.asarray(s.kn, dtype=bool)
        if not kn.any():
            raise L.LangError("probe_undefined", node, "this series is never known on the two-year probe panel "
                              "(its warm-up is too long)")
        v = np.asarray(s.arr, dtype=np.float64)[kn]
        fin = v[np.isfinite(v)]
        if len(fin) == 0 or (len(fin) == len(v) and bool(np.all(fin == fin[0]))):
            raise L.LangError("constant_subexpression", node, "this series has one value on every known row of the "
                              "probe panel: a constant built without literals escapes the G5 jitter")
