"""Interpreter for checked .omr programs. Kernel module.

evaluate(prog, params, frames, btc) walks the checked tree (omr.lang) and computes every name once
on a panel: frames is a list of symbol frames on ONE hourly index (columns = the unit's symbols),
btc the BTCUSDT frame (aligned to the panel index). Nothing is compiled or executed.

LOCALITY BY CONSTRUCTION (LANGUAGE.md section 7). Every series carries a VALUE array and a KNOWN
array. A definite value at row t is a function of a bounded trailing window of data; whether that
window's history exists is the known channel, which a program cannot observe:
- fields are known where their row exists (mark_close / index_close only while their last mark / index
  bar is recent, funding8h once a settlement exists; hour and weekday always);
- an elementwise result is known only where every input is known; a windowed result only where its
  input is known on every row of the window; a timeframe bar only if its bin is complete and every
  hour in it is known; where() only where the condition and BOTH branches are known; hold() only
  where its four inputs are known on all h rows; cs_* only where every symbol is known in that row;
- the final weight is 0 where the signal is not known (or its value is NaN).
UNIVERSE PANELS (unit top30 / next30, omr.upipeline): the input is a Panel of per-field arrays with an
IN-PLAY mask (omr.universe.inplay_matrix). cs_* (KP-015 S2) compute across the symbols that are in play
AND whose input is known at that row (sums are sequential in panel column order, so a column outside that
set changes nothing); the result is known for those symbols when the unit's membership is known and at
least UNIVERSE_MIN_CS of them exist, otherwise unknown for everyone; the final signal of a symbol that is
not in play is unknown (weight 0). A cs_* over a timeframe series uses the in-play mask of the hour at
which each of its bars becomes visible. funding_mean is known only when its last n settlements all fall
inside the last 8n hours (S1), so every function is bounded in time.
So a program is flat until every subexpression has its history (one uniform warm-up), and nothing
can switch on later than anything else. Values keep the arithmetic rules (division by zero and
non-finite results give NaN; a comparison with a NaN value is False). Every recursive function has
finite memory (ema 5n, rsi and atr 10n rows) and every window is computed from its own rows in a
fixed order (omr.windows), so results are bit-identical under end truncation and start cuts.
"""
from __future__ import annotations

import ast
import math
from dataclasses import dataclass

import numpy as np
import pandas as pd

from omr import constants as C
from omr import lang as L
from omr import windows as WN

HOUR_NS = 3_600_000_000_000
DAY_NS = 24 * HOUR_NS
WEEK_NS = 7 * DAY_NS
MONDAY_NS = 4 * DAY_NS                       # 1970-01-05 00:00 UTC was a Monday
PERIODS_PER_YEAR = {"h1": 8760.0, "h2": 4380.0, "h3": 2920.0, "h4": 2190.0, "h6": 1460.0, "h8": 1095.0,
                    "h12": 730.0, "daily": 365.0, "weekly": 365.0 / 7.0}
TF_HOURS = {"h1": 1, **L.TIMEFRAMES}
ROLL_OP = {"sma": WN.MEAN, "std": WN.STD, "rmin": WN.MIN, "rmax": WN.MAX, "rsum": WN.SUM, "median": WN.MEDIAN,
           "zscore": WN.ZSCORE, "rank": WN.RANK}


class Panel:
    """Universe panel: lazy per-field (T x K) float arrays on one hourly index (col(name) -> array, the
    same column names as a program frame), the in-play mask (T x K) and unit_known (T)."""

    def __init__(self, index, symbols, getter, inplay, unit_known):
        self.index = pd.DatetimeIndex(index).as_unit("ns")
        self.symbols = list(symbols)
        self._get = getter
        self._cache = {}
        self.inplay = np.asarray(inplay, dtype=bool)
        self.unit_known = np.asarray(unit_known, dtype=bool)

    def __len__(self):
        return len(self.symbols)

    def col(self, name: str) -> np.ndarray:
        if name not in self._cache:
            self._cache[name] = self._get(name)
        return self._cache[name]


def _stack(frames, col: str) -> np.ndarray:
    if isinstance(frames, Panel):
        return np.asarray(frames.col(col), dtype=np.float64)
    return np.column_stack([f[col].to_numpy(dtype=np.float64) for f in frames])


def _stack_true(frames, col: str) -> np.ndarray:
    if isinstance(frames, Panel):
        v = frames.col(col)
        return np.asarray(v == True, dtype=bool)  # noqa: E712
    return np.column_stack([_is_true(f[col]) for f in frames])


@dataclass
class S:
    """A series: values arr (n x k, float64 or bool) and known kn (n x k bool), at timeframe tf with
    bar open times idx."""
    arr: np.ndarray
    kn: np.ndarray
    tf: str
    idx: pd.DatetimeIndex


def _clean(a: np.ndarray) -> np.ndarray:
    if a.dtype == bool:
        return a
    a = np.asarray(a, dtype=np.float64)
    return np.where(np.isfinite(a), a, np.nan)


def _f64(a) -> np.ndarray:
    return np.ascontiguousarray(np.asarray(a, dtype=np.float64))


def _is_true(col) -> np.ndarray:
    """A boolean column that may have become object dtype with NaN after a reindex."""
    v = np.asarray(col.to_numpy())
    return np.asarray(v == True, dtype=bool)  # noqa: E712


class Context:
    def __init__(self, prog: L.Program, params: dict, frames: list, btc: pd.DataFrame | None, literals=None,
                 record=None):
        self.prog = prog
        self.params = params
        if literals is None:
            self.lits = {}
        else:
            if len(literals) != len(prog.literals):
                raise ValueError("one value per jitterable literal is required")
            self.lits = {k: float(v) for (k, _), v in zip(prog.literals, literals)}
        self.frames = frames
        self.inplay = None
        if isinstance(frames, Panel):
            idx = frames.index
            self.inplay, self.unit_known = frames.inplay, frames.unit_known
        else:
            idx = pd.DatetimeIndex(frames[0].index).as_unit("ns")
            for f in frames[1:]:
                if not pd.DatetimeIndex(f.index).as_unit("ns").equals(idx):
                    raise ValueError("panel frames must share one hourly index")
        self.idx = idx
        self.ns = idx.asi8
        self.k = len(frames)
        self.btc = btc
        self.values = {}
        self.record = record

    # ------------------------------------------------------------ fields
    def field(self, name: str, btc: bool = False) -> S:
        if btc:
            if self.btc is None:
                raise ValueError("btc() needs the BTCUSDT frame")
            b = self.btc.reindex(self.idx)
            v, kn = self._field_from([b], name)
            return S(np.repeat(v[:, :1], self.k, axis=1), np.repeat(kn[:, :1], self.k, axis=1), "h1", self.idx)
        v, kn = self._field_from(self.frames, name)
        return S(v, kn, "h1", self.idx)

    def _field_from(self, frames, name):
        n = len(self.idx)
        if name in ("hour", "weekday"):
            dec = self.idx + pd.Timedelta(hours=1)                 # decision time = bar close
            v = np.asarray(dec.hour if name == "hour" else dec.day_of_week, dtype=np.float64)
            return np.repeat(v[:, None], len(frames), axis=1), np.ones((n, len(frames)), dtype=bool)
        if name in ("mark_close", "index_close"):
            # the close of the LAST mark (index) bar at or before the row, taken from this frame's own rows
            # (<dataset>.new marks them); known while that bar is at most MARK (INDEX)_MAX_STALE_HOURS old
            ds, stale = (("mark_klines", C.MARK_MAX_STALE_HOURS) if name == "mark_close"
                         else ("index_klines", C.INDEX_MAX_STALE_HOURS))
            col = _stack(frames, f"{ds}.close")
            new = _stack_true(frames, f"{ds}.new") & np.isfinite(col)
            rows = np.arange(n)[:, None]
            last = np.maximum.accumulate(np.where(new, rows, -1), axis=0)
            has = last >= 0
            lp = np.where(has, last, 0)
            v = np.take_along_axis(col, lp, axis=0)
            age = self.ns[:, None] - self.ns[lp]
            kn = has & (age <= stale * HOUR_NS)
        elif name == "funding8h":
            if isinstance(frames, Panel):
                with np.errstate(all="ignore"):
                    v = _stack(frames, "funding.rate") * 8.0 / _stack(frames, "funding.interval_hours")
            else:
                v = np.column_stack([(f["funding.rate"] * 8.0 / f["funding.interval_hours"]).to_numpy(dtype=np.float64)
                                     for f in frames])
            kn = np.isfinite(v)
        else:
            v = _stack(frames, name)
            kn = np.isfinite(v)
        return np.where(kn, v, np.nan), kn

    # ------------------------------------------------------------ timeframes
    def to_tf(self, s: S, how: str, tf: str) -> S:
        hrs = L.TIMEFRAMES[tf]
        size = hrs * HOUR_NS
        t = self.ns
        k = s.arr.shape[1]
        empty = S(np.zeros((0, k)), np.zeros((0, k), dtype=bool), tf, pd.DatetimeIndex([], tz="UTC").as_unit("ns"))
        if len(t) == 0:
            return empty
        if tf == "weekly":
            key = t - ((t - MONDAY_NS) % WEEK_NS)
        else:
            key = t - (t % size)
        starts = np.r_[0, np.nonzero(key[1:] != key[:-1])[0] + 1]
        ends = np.r_[starts[1:], len(t)]
        complete = ((ends - starts) == hrs) & (t[ends - 1] == key[starts] + size - HOUR_NS)
        if not complete.any():
            return empty
        a = s.arr
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
        kn = np.minimum.reduceat(s.kn.astype(np.int8), starts, axis=0) == 1     # every hour of the bin known
        cidx = pd.DatetimeIndex(pd.to_datetime(key[starts][complete], unit="ns", utc=True)).as_unit("ns")
        kn = kn[complete]
        return S(np.where(kn, _clean(out[complete]), np.nan), kn, tf, cidx)

    def to_h1(self, s: S) -> S:
        if s.tf == "h1":
            return s
        vis = s.idx.asi8 + TF_HOURS[s.tf] * HOUR_NS - HOUR_NS
        pos = np.searchsorted(vis, self.ns, side="right") - 1
        ok = pos >= 0
        shape = (len(self.ns), s.arr.shape[1])
        out = np.zeros(shape, dtype=bool) if s.arr.dtype == bool else np.full(shape, np.nan)
        kn = np.zeros(shape, dtype=bool)
        if len(s.arr):
            out[ok] = s.arr[pos[ok]]
            kn[ok] = s.kn[pos[ok]]
        return S(out, kn, "h1", self.idx)

    def align(self, *vals):
        """Bring series operands to a common timeframe (hourly if they differ); scalars pass through."""
        tfs = {v.tf for v in vals if isinstance(v, S)}
        if len(tfs) <= 1:
            return list(vals)
        return [self.to_h1(v) if isinstance(v, S) else v for v in vals]

    @staticmethod
    def kn_of(*vals):
        out = None
        for v in vals:
            if isinstance(v, S):
                out = v.kn.copy() if out is None else (out & v.kn)
        return out

    # ------------------------------------------------------------ evaluation
    def ev(self, node):
        v = self._ev(node)
        if self.record is not None and isinstance(v, S) and v.arr.dtype != bool:
            self.record.append((node, v))
        return v

    def _ev(self, node):
        lit = L._literal_value(node)
        if lit is not None:
            return self.lits.get(L.literal_key(node), lit[0]) if lit[0] != 0 else lit[0]
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
                return S(~v.arr, v.kn, v.tf, v.idx)
            return -v if not isinstance(v, S) else S(-v.arr, v.kn, v.tf, v.idx)
        if isinstance(node, ast.BoolOp):
            vs = self.align(*[self.ev(v) for v in node.values])
            out = vs[0].arr.copy()
            for v in vs[1:]:
                out = (out & v.arr) if isinstance(node.op, ast.And) else (out | v.arr)
            return S(out, self.kn_of(*vs), vs[0].tf, vs[0].idx)
        if isinstance(node, ast.Compare):
            a, b = self.align(self.ev(node.left), self.ev(node.comparators[0]))
            ref = a if isinstance(a, S) else b
            x = a.arr if isinstance(a, S) else a
            y = b.arr if isinstance(b, S) else b
            op = type(node.ops[0])
            with np.errstate(invalid="ignore"):
                r = {ast.Lt: np.less, ast.Gt: np.greater, ast.LtE: np.less_equal, ast.GtE: np.greater_equal}[op](x, y)
            return S(np.asarray(r, dtype=bool), self.kn_of(a, b), ref.tf, ref.idx)
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
        return S(_clean(r), self.kn_of(a, b), ref.tf, ref.idx)

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
        if fn == "ema":
            x, n = self.ev(a[0]), self.window(a[1])
            m = C.EMA_MEMORY * n
            w = WN.decay_weights(n, m, 1.0 - 2.0 / (n + 1.0))
            return S(_clean(WN.wmean(_f64(x.arr), w)), WN.known_run(x.kn, m), x.tf, x.idx)
        if fn in ROLL_OP:
            x, n = self.ev(a[0]), self.window(a[1])
            return S(_clean(WN.roll(_f64(x.arr), n, ROLL_OP[fn])), WN.known_run(x.kn, n), x.tf, x.idx)
        if fn in L.LAGS:
            return self.lags(fn, self.ev(a[0]), self.window(a[1]))
        if fn == "corr":
            x, y = self.align(self.ev(a[0]), self.ev(a[1]))
            n = self.window(a[2])
            return S(_clean(WN.corr(_f64(x.arr), _f64(y.arr), n)), WN.known_run(x.kn & y.kn, n), x.tf, x.idx)
        if fn == "rsi":
            x, n = self.ev(a[0]), self.window(a[1])
            m = C.RSI_MEMORY * n
            w = WN.decay_weights(n, m, 1.0 - 1.0 / n)
            return S(_clean(WN.rsi_finite(_f64(x.arr), w)), WN.known_run(x.kn, m + 1), x.tf, x.idx)
        if fn == "atr":
            h, l_, c = self.ev(a[0]), self.ev(a[1]), self.ev(a[2])
            n = self.window(a[3])
            m = C.ATR_MEMORY * n
            w = WN.decay_weights(n, m, 1.0 - 1.0 / n)
            vals = WN.atr_finite(_f64(h.arr), _f64(l_.arr), _f64(c.arr), w)
            return S(_clean(vals), WN.known_run(h.kn & l_.kn & c.kn, m + 1), h.tf, h.idx)
        if fn == "realised_vol":
            x, n = self.ev(a[0]), self.window(a[1])
            sd = WN.log_ratio_std(_f64(x.arr), n)
            return S(_clean(sd * math.sqrt(PERIODS_PER_YEAR[x.tf])), WN.known_run(x.kn, n + 1), x.tf, x.idx)
        if fn in L.ELEMENTWISE:
            v = self.ev(a[0])
            x = v.arr if isinstance(v, S) else np.asarray(v, dtype=np.float64)
            with np.errstate(all="ignore"):
                r = {"abs": np.abs, "sign": np.sign, "sqrt": np.sqrt, "log": np.log, "exp": np.exp,
                     "tanh": np.tanh}[fn](x)
            if not isinstance(v, S):
                r = float(r)
                return r if math.isfinite(r) else float("nan")
            return S(_clean(r), v.kn, v.tf, v.idx)
        if fn == "clip":
            v, lo, hi = self.ev(a[0]), self.ev(a[1]), self.ev(a[2])
            lo, hi = min(lo, hi), max(lo, hi)
            return S(_clean(np.clip(v.arr, lo, hi)), v.kn, v.tf, v.idx)
        if fn in ("min2", "max2"):
            x, y = self.align(self.ev(a[0]), self.ev(a[1]))
            ref = x if isinstance(x, S) else y
            xa = x.arr if isinstance(x, S) else x
            ya = y.arr if isinstance(y, S) else y
            r = (np.minimum if fn == "min2" else np.maximum)(xa, ya)
            if not isinstance(ref, S):
                return float(r)
            return S(_clean(r), self.kn_of(x, y), ref.tf, ref.idx)
        if fn == "where":
            c, x, y = self.align(self.ev(a[0]), self.ev(a[1]), self.ev(a[2]))
            xa = x.arr if isinstance(x, S) else x
            ya = y.arr if isinstance(y, S) else y
            r = np.where(c.arr, xa, ya)
            return S(_clean(np.broadcast_to(r, c.arr.shape).astype(np.float64)), self.kn_of(c, x, y), c.tf, c.idx)
        if fn == "hold":
            el, xl, es, xs = self.align(*[self.ev(x) for x in a[:4]])
            h = self.window(a[4])
            st = WN.hold_window(np.ascontiguousarray(el.arr), np.ascontiguousarray(xl.arr),
                                np.ascontiguousarray(es.arr), np.ascontiguousarray(xs.arr), h)
            return S(st, WN.known_run(el.kn & xl.kn & es.kn & xs.kn, h), el.tf, el.idx)
        if fn in L.CROSS:
            v = self.ev(a[0])
            if self.inplay is not None:
                return self.cross_inplay(fn, v)
            kn = np.repeat(v.kn.all(axis=1, keepdims=True), v.kn.shape[1], axis=1)
            return S(_clean(_cross(fn, v.arr)), kn, v.tf, v.idx)
        raise ValueError(f"unknown function {fn}")

    def lags(self, fn, x: S, n: int) -> S:
        a = x.arr
        kn = WN.known_run(x.kn, n + 1)                 # rows t-n .. t
        if a.dtype == bool:
            out = np.zeros_like(a)
            if n < len(a):
                out[n:] = a[:len(a) - n]
            return S(out, kn, x.tf, x.idx)
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
        return S(_clean(r), kn, x.tf, x.idx)

    def cross_inplay(self, fn: str, v: S) -> S:
        """cs_* across the in-play symbols (universe panels); see the module docstring."""
        if v.tf == "h1":
            P_, uk = self.inplay, self.unit_known
        else:
            vis = v.idx.asi8 + TF_HOURS[v.tf] * HOUR_NS - HOUR_NS
            pos = np.searchsorted(self.ns, vis)
            ok = (pos < len(self.ns)) & (self.ns[np.minimum(pos, len(self.ns) - 1)] == vis)
            pos = np.minimum(pos, len(self.ns) - 1)
            P_ = self.inplay[pos] & ok[:, None]
            uk = self.unit_known[pos] & ok
        # S2 (R1b): across the in-play (tradable) symbols whose input is known at that row; known for those
        # symbols when at least UNIVERSE_MIN_CS of them exist, otherwise unknown for everyone
        S_ = P_ & v.kn
        row_kn = uk & (S_.sum(axis=1) >= C.UNIVERSE_MIN_CS)
        kn = S_ & row_kn[:, None]
        vals = _cross_inplay(fn, np.asarray(v.arr, dtype=np.float64), S_)
        return S(np.where(kn, _clean(vals), np.nan), kn, v.tf, v.idx)

    def funding_mean(self, n: int) -> S:
        new = _stack_true(self.frames, "funding.new")
        if isinstance(self.frames, Panel):
            with np.errstate(all="ignore"):
                r8 = _stack(self.frames, "funding.rate") * 8.0 / _stack(self.frames, "funding.interval_hours")
        else:
            r8 = np.column_stack([(f["funding.rate"] * 8.0 / f["funding.interval_hours"]).to_numpy(dtype=np.float64)
                                  for f in self.frames])
        new = new & np.isfinite(r8)
        vals, kn = WN.event_mean(_f64(r8), new, n)
        # S1 (KP-015): known only when its last n settlements all fall inside the last 8n hours (rows), so
        # funding_mean is bounded in time like every other function (a long funding gap makes it unknown)
        w = 8 * n
        cnt = np.cumsum(new, axis=0, dtype=np.int64)
        prev = np.zeros_like(cnt)
        if len(cnt) > w:
            prev[w:] = cnt[:-w]
        kn = kn & ((cnt - prev) >= n)
        return S(np.where(kn, _clean(vals), np.nan), kn, "h1", self.idx)


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


def _cross_inplay(fn: str, a: np.ndarray, P_: np.ndarray) -> np.ndarray:
    """cs_* values across the in-play columns P_ of each row (values of other columns are not used)."""
    k = P_.sum(axis=1, keepdims=True).astype(np.float64)
    with np.errstate(all="ignore"):
        if fn in ("cs_mean", "cs_demean"):
            tot = np.cumsum(np.where(P_, a, 0.0), axis=1)[:, -1:]          # sequential, in column order
            m = np.where(k > 0, tot / np.where(k > 0, k, 1.0), np.nan)
            return np.broadcast_to(m, a.shape).copy() if fn == "cs_mean" else a - m
        if fn == "cs_scale":
            tot = np.cumsum(np.where(P_, np.abs(a), 0.0), axis=1)[:, -1:]
            return np.where(tot > 0, a / np.where(tot > 0, tot, 1.0), np.nan)
        r = pd.DataFrame(np.where(P_, a, np.nan)).rank(axis=1, method="average").to_numpy()
        out = 2.0 * (r - 1.0) / np.where(k > 1, k - 1.0, 1.0) - 1.0
        bad = (k[:, 0] < 2) | ~np.all(np.isfinite(a) | ~P_, axis=1)
        out[bad] = np.nan
        return out


def evaluate_full(prog: L.Program, params: dict, frames, btc: pd.DataFrame | None = None,
                  literals=None, record=None):
    """(raw, known) on the panel's hourly index, shape (T, k). raw is NaN wherever not known. frames: a
    list of symbol frames (core unit) or a Panel (universe units: not-in-play symbols are unknown)."""
    ctx = Context(prog, params, frames, btc, literals, record)
    for name, node in prog.defs:
        ctx.values[name] = ctx.ev(node)
    sig = ctx.to_h1(ctx.values["signal"])
    kn = np.asarray(sig.kn, dtype=bool)
    if ctx.inplay is not None:
        kn = kn & ctx.inplay
    raw = np.where(kn, sig.arr.astype(np.float64), np.nan)
    return raw, kn


def evaluate(prog: L.Program, params: dict, frames: list, btc: pd.DataFrame | None = None,
             literals=None) -> np.ndarray:
    """Raw signal (NaN where not known or undefined), shape (T, k)."""
    return evaluate_full(prog, params, frames, btc, literals)[0]


def weights(prog: L.Program, raw: np.ndarray, unit_size: int) -> np.ndarray:
    """Signal -> weights: not known or NaN -> 0, clip to [-1, 1]; single: / unit size; portfolio: scale
    down by 1 / gross when gross > 1. (raw from evaluate is NaN wherever not known.)"""
    s = np.clip(np.where(np.isfinite(raw), raw, 0.0), -1.0, 1.0)
    if prog.kind == "single":
        return s / float(unit_size)
    g = np.abs(s).sum(axis=1, keepdims=True)
    return np.where(g > 1.0, s / np.where(g > 0, g, 1.0), s)
