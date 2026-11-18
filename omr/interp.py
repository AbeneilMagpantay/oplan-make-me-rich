"""Interpreter for checked .omr programs. Kernel module.

evaluate(prog, params, frames, btc) walks the checked tree (omr.lang) and computes every name once
on a panel: frames is a list of symbol frames on ONE hourly index (columns = the unit's symbols),
btc the BTCUSDT frame (any index; it is aligned to the panel index). Nothing is compiled or executed.

Semantics (LANGUAGE.md): comparisons with NaN are False; division by zero and any non-finite result
give NaN; timeframes use complete bins only (anchored 00:00 UTC, weekly on Monday 00:00 UTC), a
coarse bar is visible from the hourly bar in which it closed; mixing timeframes aligns to hourly by
the last completed value; rolling functions need a full window and act at the series' timeframe.
"""
from __future__ import annotations

import ast
import math
from dataclasses import dataclass

import numpy as np
import pandas as pd

from omr import indicators as ind
from omr import lang as L

HOUR_NS = 3_600_000_000_000
DAY_NS = 24 * HOUR_NS
WEEK_NS = 7 * DAY_NS
MONDAY_NS = 4 * DAY_NS                       # 1970-01-05 00:00 UTC was a Monday
PERIODS_PER_YEAR = {"h1": 8760.0, "h2": 4380.0, "h3": 2920.0, "h4": 2190.0, "h6": 1460.0, "h8": 1095.0,
                    "h12": 730.0, "daily": 365.0, "weekly": 365.0 / 7.0}
TF_HOURS = {"h1": 1, **L.TIMEFRAMES}


@dataclass
class S:
    """A series value: arr (n x k) float64 or bool, at timeframe tf with bar open times idx."""
    arr: np.ndarray
    tf: str
    idx: pd.DatetimeIndex


def _clean(a: np.ndarray) -> np.ndarray:
    if a.dtype == bool:
        return a
    a = np.asarray(a, dtype=np.float64)
    return np.where(np.isfinite(a), a, np.nan)


class Context:
    def __init__(self, prog: L.Program, params: dict, frames: list, btc: pd.DataFrame | None):
        self.prog = prog
        self.params = params
        self.frames = frames
        idx = pd.DatetimeIndex(frames[0].index).as_unit("ns")
        for f in frames[1:]:
            if not pd.DatetimeIndex(f.index).as_unit("ns").equals(idx):
                raise ValueError("panel frames must share one hourly index")
        self.idx = idx
        self.ns = idx.asi8
        self.k = len(frames)
        self.btc = btc
        self.values = {}
        self._tf_cache = {}

    # ------------------------------------------------------------ fields
    def col(self, name: str) -> np.ndarray:
        return np.column_stack([f[name].to_numpy(dtype=np.float64) for f in self.frames])

    def field(self, name: str, btc: bool = False) -> S:
        if btc:
            if self.btc is None:
                raise ValueError("btc() needs the BTCUSDT frame")
            b = self.btc.reindex(self.idx)
            v = self._field_from([b], name)[:, :1]
            return S(np.repeat(v, self.k, axis=1), "h1", self.idx)
        return S(self._field_from(self.frames, name), "h1", self.idx)

    def _field_from(self, frames, name):
        if name == "mark_close":
            return np.column_stack([f["mark_klines.close"].to_numpy(dtype=np.float64) for f in frames])
        if name == "funding8h":
            return np.column_stack([(f["funding.rate"] * 8.0 / f["funding.interval_hours"]).to_numpy(dtype=np.float64)
                                    for f in frames])
        if name in ("hour", "weekday"):
            dec = self.idx + pd.Timedelta(hours=1)                 # decision time = bar close
            v = np.asarray(dec.hour if name == "hour" else dec.day_of_week, dtype=np.float64)
            return np.repeat(v[:, None], len(frames), axis=1)
        return np.column_stack([f[name].to_numpy(dtype=np.float64) for f in frames])

    # ------------------------------------------------------------ timeframes
    def to_tf(self, s: S, how: str, tf: str) -> S:
        hrs = L.TIMEFRAMES[tf]
        size = hrs * HOUR_NS
        t = self.ns
        if tf == "weekly":
            key = t - ((t - MONDAY_NS) % WEEK_NS)
        else:
            key = t - (t % size)
        starts = np.r_[0, np.nonzero(key[1:] != key[:-1])[0] + 1]
        ends = np.r_[starts[1:], len(t)]
        complete = ((ends - starts) == hrs) & (t[ends - 1] == key[starts] + size - HOUR_NS)
        a = s.arr
        if len(starts) == 0 or not complete.any():
            return S(np.zeros((0, a.shape[1])), tf, pd.DatetimeIndex([], tz="UTC").as_unit("ns"))
        if how == "first":
            out = a[starts]
        elif how == "last":
            out = a[ends - 1]
        elif how == "max":
            out = np.maximum.reduceat(a, starts, axis=0)
        elif how == "min":
            out = np.minimum.reduceat(a, starts, axis=0)
        else:
            out = np.add.reduceat(a, starts, axis=0)
        out = out[complete]
        cidx = pd.DatetimeIndex(pd.to_datetime(key[starts][complete], unit="ns", utc=True)).as_unit("ns")
        return S(_clean(out), tf, cidx)

    def to_h1(self, s: S) -> S:
        if s.tf == "h1":
            return s
        vis = s.idx.asi8 + TF_HOURS[s.tf] * HOUR_NS - HOUR_NS
        pos = np.searchsorted(vis, self.ns, side="right") - 1
        ok = pos >= 0
        if s.arr.dtype == bool:
            out = np.zeros((len(self.ns), s.arr.shape[1]), dtype=bool)
        else:
            out = np.full((len(self.ns), s.arr.shape[1]), np.nan)
        if len(s.arr):
            out[ok] = s.arr[pos[ok]]
        return S(out, "h1", self.idx)

    def align(self, *vals):
        """Bring series operands to a common timeframe (hourly if they differ); scalars pass through."""
        ser = [v for v in vals if isinstance(v, S)]
        tfs = {v.tf for v in ser}
        if len(tfs) <= 1:
            return list(vals)
        return [self.to_h1(v) if isinstance(v, S) else v for v in vals]

    # ------------------------------------------------------------ evaluation
    def ev(self, node):
        lit = L._literal_value(node)
        if lit is not None:
            return lit[0]
        if isinstance(node, ast.Name):
            n = node.id
            if n in self.prog.params:
                return float(self.params[n])
            if n in L.FIELDS:
                return self.field(n)
            return self.values[n]
        if isinstance(node, ast.BinOp):
            a, b = self.align(self.ev(node.left), self.ev(node.right))
            return self.binop(type(node.op), a, b)
        if isinstance(node, ast.UnaryOp):
            v = self.ev(node.operand)
            if isinstance(node.op, ast.Not):
                return S(~v.arr, v.tf, v.idx)
            return -v if not isinstance(v, S) else S(-v.arr, v.tf, v.idx)
        if isinstance(node, ast.BoolOp):
            vs = self.align(*[self.ev(v) for v in node.values])
            out = vs[0].arr.copy()
            for v in vs[1:]:
                out = (out & v.arr) if isinstance(node.op, ast.And) else (out | v.arr)
            return S(out, vs[0].tf, vs[0].idx)
        if isinstance(node, ast.Compare):
            a, b = self.align(self.ev(node.left), self.ev(node.comparators[0]))
            ref = a if isinstance(a, S) else b
            x = a.arr if isinstance(a, S) else a
            y = b.arr if isinstance(b, S) else b
            op = type(node.ops[0])
            with np.errstate(invalid="ignore"):
                r = {ast.Lt: np.less, ast.Gt: np.greater, ast.LtE: np.less_equal, ast.GtE: np.greater_equal}[op](x, y)
            return S(np.asarray(r, dtype=bool), ref.tf, ref.idx)
        if isinstance(node, ast.Call):
            return self.call(node)
        raise ValueError("unchecked node")

    def binop(self, op, a, b):
        ref = a if isinstance(a, S) else (b if isinstance(b, S) else None)
        x = a.arr if isinstance(a, S) else a
        y = b.arr if isinstance(b, S) else b
        with np.errstate(all="ignore"):
            if op is ast.Add:
                r = x + y
            elif op is ast.Sub:
                r = x - y
            elif op is ast.Mult:
                r = x * y
            else:
                r = np.divide(x, y) if ref is not None else (x / y if y != 0 else float("nan"))
        if ref is None:
            return float(r) if math.isfinite(r) else float("nan")
        return S(_clean(r), ref.tf, ref.idx)

    def window(self, node) -> int:
        lit = L._literal_value(node)
        if lit is not None:
            return int(lit[0])
        return int(self.params[node.id])

    def call(self, node):
        fn = node.func.id
        a = node.args
        if fn == "btc":
            return self.field(a[0].id, btc=True)
        if fn in L.TIMEFRAMES:
            arg = a[0]
            if isinstance(arg, ast.Call):
                fld, base = arg.args[0].id, self.field(arg.args[0].id, btc=True)
            else:
                fld, base = arg.id, self.field(arg.id)
            return self.to_tf(base, L.FIELDS[fld][1], fn)
        if fn == "funding_mean":
            return self.funding_mean(self.window(a[0]))
        if fn in L.ROLLING:
            return self.rolling(fn, self.ev(a[0]), self.window(a[1]))
        if fn in L.LAGS:
            return self.lags(fn, self.ev(a[0]), self.window(a[1]))
        if fn == "corr":
            # rolling covariance / (rolling std x * rolling std y), each with ddof 1. (pandas' own
            # rolling corr takes (var_x * var_y) ** 0.5 through pow(), which is not exactly
            # scale-equivariant; this form is, bit for bit, under power-of-two rescales.)
            x, y = self.align(self.ev(a[0]), self.ev(a[1]))
            n = self.window(a[2])
            dx, dy = pd.DataFrame(x.arr), pd.DataFrame(y.arr)
            cov = dx.rolling(n, min_periods=n).cov(dy).to_numpy()
            sx = dx.rolling(n, min_periods=n).std(ddof=1).to_numpy()
            sy = dy.rolling(n, min_periods=n).std(ddof=1).to_numpy()
            with np.errstate(all="ignore"):
                r = cov / (sx * sy)
            return S(_clean(r), x.tf, x.idx)
        if fn == "rsi":
            x, n = self.ev(a[0]), self.window(a[1])
            if len(x.arr) == 0:                       # a coarse timeframe with no complete bar yet
                return S(np.zeros((0, x.arr.shape[1])), x.tf, x.idx)
            out = np.column_stack([ind.rsi_wilder(pd.Series(x.arr[:, j]), n).to_numpy() for j in range(x.arr.shape[1])])
            return S(_clean((out - 50.0) / 50.0), x.tf, x.idx)
        if fn == "atr":
            h, l, c = self.ev(a[0]), self.ev(a[1]), self.ev(a[2])
            n = self.window(a[3])
            if len(h.arr) == 0:
                return S(np.zeros((0, h.arr.shape[1])), h.tf, h.idx)
            cols = []
            for j in range(h.arr.shape[1]):
                bars = pd.DataFrame({"high": h.arr[:, j], "low": l.arr[:, j], "close": c.arr[:, j]})
                cols.append(ind.atr(bars, n).to_numpy())
            return S(_clean(np.column_stack(cols)), h.tf, h.idx)
        if fn == "realised_vol":
            x, n = self.ev(a[0]), self.window(a[1])
            if len(x.arr) == 0:
                return S(np.zeros((0, x.arr.shape[1])), x.tf, x.idx)
            with np.errstate(all="ignore"):
                lr = np.log(x.arr[1:] / x.arr[:-1])
            lr = np.vstack([np.full((1, x.arr.shape[1]), np.nan), _clean(lr)])
            sd = pd.DataFrame(lr).rolling(n, min_periods=n).std(ddof=1).to_numpy()
            return S(_clean(sd * math.sqrt(PERIODS_PER_YEAR[x.tf])), x.tf, x.idx)
        if fn in L.ELEMENTWISE:
            v = self.ev(a[0])
            x = v.arr if isinstance(v, S) else np.asarray(v, dtype=np.float64)
            with np.errstate(all="ignore"):
                r = {"abs": np.abs, "sign": np.sign, "sqrt": np.sqrt, "log": np.log, "exp": np.exp,
                     "tanh": np.tanh}[fn](x)
            if not isinstance(v, S):
                r = float(r)
                return r if math.isfinite(r) else float("nan")
            return S(_clean(r), v.tf, v.idx)
        if fn == "clip":
            v, lo, hi = self.ev(a[0]), self.ev(a[1]), self.ev(a[2])
            lo, hi = min(lo, hi), max(lo, hi)
            return S(_clean(np.clip(v.arr, lo, hi)), v.tf, v.idx)
        if fn in ("min2", "max2"):
            x, y = self.align(self.ev(a[0]), self.ev(a[1]))
            ref = x if isinstance(x, S) else y
            xa = x.arr if isinstance(x, S) else x
            ya = y.arr if isinstance(y, S) else y
            r = (np.minimum if fn == "min2" else np.maximum)(xa, ya)
            if not isinstance(ref, S):
                return float(r)
            return S(_clean(r), ref.tf, ref.idx)
        if fn == "where":
            c, x, y = self.align(self.ev(a[0]), self.ev(a[1]), self.ev(a[2]))
            xa = x.arr if isinstance(x, S) else x
            ya = y.arr if isinstance(y, S) else y
            r = np.where(c.arr, xa, ya)
            return S(_clean(np.broadcast_to(r, c.arr.shape).astype(np.float64)), c.tf, c.idx)
        if fn == "hold":
            el, xl, es, xs = self.align(*[self.ev(x) for x in a])
            return S(_hold(el.arr, xl.arr, es.arr, xs.arr), el.tf, el.idx)
        if fn in L.CROSS:
            v = self.ev(a[0])
            return S(_clean(_cross(fn, v.arr)), v.tf, v.idx)
        raise ValueError(f"unknown function {fn}")

    def rolling(self, fn, x: S, n: int) -> S:
        d = pd.DataFrame(x.arr)
        if fn == "ema":
            return S(_clean(np.column_stack([_ema(x.arr[:, j], n) for j in range(x.arr.shape[1])])), x.tf, x.idx)
        r = d.rolling(n, min_periods=n)
        if fn == "sma":
            out = r.mean()
        elif fn == "std":
            out = r.std(ddof=1)
        elif fn == "rmin":
            out = r.min()
        elif fn == "rmax":
            out = r.max()
        elif fn == "rsum":
            out = r.sum()
        elif fn == "median":
            out = r.median()
        elif fn == "zscore":
            m, s = r.mean().to_numpy(), r.std(ddof=1).to_numpy()
            with np.errstate(all="ignore"):
                z = np.where(s > 0, (x.arr - m) / s, np.nan)
            return S(_clean(z), x.tf, x.idx)
        else:   # rank: share of the last n values (current included) that are <= the current value
            out = r.rank(method="max", ascending=True, pct=True)
        return S(_clean(out.to_numpy()), x.tf, x.idx)

    def lags(self, fn, x: S, n: int) -> S:
        a = x.arr
        if a.dtype == bool:
            out = np.zeros_like(a)
            if n < len(a):
                out[n:] = a[:-n] if n > 0 else a
            return S(out, x.tf, x.idx)
        prev = np.full_like(a, np.nan)
        if n < len(a):
            prev[n:] = a[:len(a) - n]
        with np.errstate(all="ignore"):
            if fn == "lag":
                r = prev
            elif fn == "delta":
                r = a - prev
            elif fn == "ret":
                r = a / prev - 1.0
            else:
                q = a / prev
                r = np.where(q > 0, np.log(np.where(q > 0, q, 1.0)), np.nan)
        return S(_clean(r), x.tf, x.idx)

    def funding_mean(self, n: int) -> S:
        cols = []
        for f in self.frames:
            new = f["funding.new"].to_numpy(dtype=bool)
            r8 = (f["funding.rate"] * 8.0 / f["funding.interval_hours"]).to_numpy(dtype=np.float64)
            ev = pd.Series(r8[new])
            m = ev.rolling(n, min_periods=n).mean().to_numpy()
            col = np.full(len(f), np.nan)
            col[np.nonzero(new)[0]] = m
            cols.append(pd.Series(col).ffill().to_numpy())
        return S(_clean(np.column_stack(cols)), "h1", self.idx)


def _ema(x: np.ndarray, n: int) -> np.ndarray:
    """EMA with alpha 2/(n+1), seeded with the SMA of the first n consecutive valid values; a NaN
    input gives NaN and restarts the seeding."""
    out = np.full(len(x), np.nan)
    alpha = 2.0 / (n + 1.0)
    run = 0
    acc = 0.0
    y = np.nan
    for t in range(len(x)):
        v = x[t]
        if not math.isfinite(v):
            run, acc, y = 0, 0.0, np.nan
            continue
        if run < n:
            acc += v
            run += 1
            if run == n:
                y = acc / n
                out[t] = y
            continue
        y = y + alpha * (v - y)
        out[t] = y
    return out


def _hold(el, xl, es, xs) -> np.ndarray:
    T, K = el.shape
    out = np.zeros((T, K))
    for j in range(K):
        st = 0.0
        for t in range(T):
            a, b, c, d = el[t, j], xl[t, j], es[t, j], xs[t, j]
            if st == 0.0:
                if a and not c:
                    st = 1.0
                elif c and not a:
                    st = -1.0
            elif st == 1.0:
                if c:
                    st = -1.0
                elif b:
                    st = 0.0
            else:
                if a:
                    st = 1.0
                elif d:
                    st = 0.0
            out[t, j] = st
    return out


def _cross(fn, a: np.ndarray) -> np.ndarray:
    with np.errstate(all="ignore"):
        if fn == "cs_mean":
            m = np.mean(a, axis=1, keepdims=True)
            return np.broadcast_to(m, a.shape).copy()
        if fn == "cs_demean":
            return a - np.mean(a, axis=1, keepdims=True)
        if fn == "cs_scale":
            s = np.sum(np.abs(a), axis=1, keepdims=True)
            return np.where(s > 0, a / s, np.nan)
        k = a.shape[1]
        if k < 2:
            return np.full_like(a, np.nan)
        r = pd.DataFrame(a).rank(axis=1, method="average").to_numpy()
        bad = ~np.isfinite(a).all(axis=1)
        out = 2.0 * (r - 1.0) / (k - 1.0) - 1.0
        out[bad] = np.nan
        return out


def evaluate(prog: L.Program, params: dict, frames: list, btc: pd.DataFrame | None = None) -> np.ndarray:
    """Raw signal on the panel's hourly index, shape (T, k): NaN where undefined (not yet clipped)."""
    ctx = Context(prog, params, frames, btc)
    for name, node in prog.defs:
        v = ctx.ev(node)
        ctx.values[name] = v
    sig = ctx.to_h1(ctx.values["signal"])
    return sig.arr.astype(np.float64)


def weights(prog: L.Program, raw: np.ndarray, unit_size: int) -> np.ndarray:
    """Signal -> weights: NaN -> 0, clip to [-1, 1]; single: / unit size; portfolio: scale down when gross > 1."""
    s = np.clip(np.where(np.isfinite(raw), raw, 0.0), -1.0, 1.0)
    if prog.kind == "single":
        return s / float(unit_size)
    g = np.abs(s).sum(axis=1, keepdims=True)
    return np.where(g > 1.0, s / np.where(g > 0, g, 1.0), s)
