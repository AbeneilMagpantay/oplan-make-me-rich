"""Constant probe (H1a, refined in FIX PASS 6). Kernel module.

At parse time, with the default params, every NUMERIC series node of a program is evaluated on a
fixed synthetic probe panel: two years of hourly bars for two symbols and for BTC (fixed seed), with
trends and volatility regimes, a daily volume cycle, funding settlements that swing through
positive and negative regimes, and mark-price bars with a few missing hours. On each node's KNOWN
rows:
- no known row -> `probe_undefined` (its warm-up exceeds two years);
- known rows but no finite value -> `constant_subexpression`;
- constancy is judged on the FINITE values only (NaN rows are ignored, so `hour / hour`, NaN once a
  day, is still the constant 1);
- every finite value exactly 0 -> accepted (a zero series is harmless; a rare-event indicator is 0
  on the panel);
- every finite value the same NON-ZERO number -> rejected, UNLESS that number changes when the
  program's literals and non-window params are jittered (PROBE_JITTER_DRAWS fixed-seed draws, every
  window param kept at its default): then it is a jittered constant, which G5 tests. Keeping window
  params fixed matters: `sma(hour, n)` at n = 24 is exactly 11.5 and stays rejected.
What it does NOT catch: NEAR-constants (`mark_close / close`, `sma(hour, 25)`, sums of such ratios
used as a scale) and thresholds hidden by multiplying both sides of a comparison by the same series.
Those are deliberate and visible; the coordinator's source read catches them (KERNEL_PROPOSALS
KP-010). Boolean nodes are not probed. An exception raised while probing is `probe_fault` (a kernel
bug, not the researcher's syntax). The panel is built once per process; nothing here reads real data.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from omr import constants as C
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
    return {"klines": kl, "funding": fu, "mark_klines": mark, "index_klines": index_bars(kl)}


def index_bars(kl: pd.DataFrame) -> pd.DataFrame:
    """A deterministic index-price series near the last price (no random draw): a small daily basis cycle."""
    t = np.arange(len(kl), dtype=np.float64)
    f = 1.0 - 0.0004 * np.sin(2 * np.pi * t / 24.0) - 0.0002 * np.sin(2 * np.pi * t / 500.0)
    o, h, l_, c = (kl[k].to_numpy(dtype=np.float64) * f for k in ("open", "high", "low", "close"))
    out = pd.DataFrame({"open": o, "high": np.maximum(h, np.maximum(o, c)), "low": np.minimum(l_, np.minimum(o, c)),
                        "close": c, "samples": 3600.0}, index=kl.index)
    out.index.name = "open_time"
    return out


def panel():
    """(symbol A frame, symbol B frame, BTC frame), built once per process."""
    global _PANEL
    if _PANEL is None:
        rng = np.random.default_rng(SEED)
        raws = [synthetic_symbol(rng, p0) for p0 in (100.0, 7.5, 30000.0)]
        _PANEL = tuple(D.assemble_frame(r, D.PROGRAM_EXTRA) for r in raws)
    return _PANEL


def window_params(prog: L.Program) -> set:
    """Params used as a window / lag / count / horizon argument anywhere in the program."""
    import ast
    out = set()
    for _, node in prog.defs:
        for n in ast.walk(node):
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in L.WINDOW_FUNCS:
                a = n.args[L.WINDOW_FUNCS[n.func.id]]
                if isinstance(a, ast.Name) and a.id in prog.params:
                    out.add(a.id)
    return out


def jitter_draws(prog: L.Program, n: int = C.PROBE_JITTER_DRAWS):
    """(params, literal values) draws: literals and NON-window params x U(0.8, 1.2) (ints rounded, an
    unchanged int moved by 1, clipped to bounds); window params at their defaults. Fixed seed."""
    rng = np.random.default_rng(C.PROBE_JITTER_SEED)
    wp = window_params(prog)
    base = L.default_params(prog)
    out = []
    for _ in range(n):
        q = dict(base)
        for k, p in prog.params.items():
            if k in wp:
                continue
            v = base[k] * rng.uniform(C.JITTER_LO, C.JITTER_HI)
            if p.is_int:
                v = int(np.floor(v + 0.5))
                if v == base[k]:
                    v = base[k] + (1 if rng.uniform() < 0.5 else -1)
            v = min(max(v, p.low), p.high)
            q[k] = int(v) if p.is_int else float(v)
        lits = tuple(float(v * rng.uniform(C.JITTER_LO, C.JITTER_HI)) for _, v in prog.literals)
        out.append((q, lits))
    return out


def _constant_value(s):
    """None if the node passes; 'undefined', 'no_finite', or the constant non-zero value."""
    kn = np.asarray(s.kn, dtype=bool)
    if not kn.any():
        return "undefined"
    v = np.asarray(s.arr, dtype=np.float64)[kn]
    fin = v[np.isfinite(v)]
    if len(fin) == 0:
        return "no_finite"
    if not bool(np.all(fin == fin[0])):
        return None
    if fin[0] == 0.0:
        return None                                       # an all-zero series is harmless
    return float(fin[0])


def check(prog: L.Program) -> None:
    from omr import interp as X
    a, b, btc = panel()
    frames = [a] if prog.kind == "single" else [a, b]
    rec = []
    X.evaluate_full(prog, L.default_params(prog), frames, btc, record=rec)
    suspects = []
    for node, s in rec:
        c = _constant_value(s)
        if c == "undefined":
            raise L.LangError("probe_undefined", node, "this series is never known on the two-year probe panel "
                              "(its warm-up is too long)")
        if c == "no_finite":
            raise L.LangError("constant_subexpression", node, "this series has no finite value on any known row of "
                              "the probe panel")
        if c is not None:
            suspects.append((node, c))
    if not suspects:
        return
    moved = {id(node): False for node, _ in suspects}
    for q, lits in jitter_draws(prog):
        rj = []
        X.evaluate_full(prog, q, frames, btc, literals=lits, record=rj)
        by = {}
        for node, s in rj:
            by[id(node)] = s
        for node, c in suspects:
            s = by.get(id(node))
            if s is None:
                continue
            kn = np.asarray(s.kn, dtype=bool)
            v = np.asarray(s.arr, dtype=np.float64)[kn]
            fin = v[np.isfinite(v)]
            if len(fin) and not bool(np.all(fin == c)):
                moved[id(node)] = True
    for node, c in suspects:
        if not moved[id(node)]:
            raise L.LangError("constant_subexpression", node, f"this series is the constant {c:g} on every known row "
                              "of the probe panel and no jitter of the program's literals or non-window params "
                              "moves it: a constant built without literals escapes the G5 jitter")
