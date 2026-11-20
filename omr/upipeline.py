"""Evaluation pipeline for programs of unit top30 (KP-015). Kernel module.

The core unit's pipeline (omr.pipeline) is untouched; this module evaluates a portfolio program on a
point-in-time universe panel (omr.universe) with the universe engine (omr.engine.run_arrays_u).

Data (UData): the activity of every crypto perpetual under one ceiling (membership needs all of them),
the stored tables of the symbols that are ever members of top30 or next30, and the core BTCUSDT frame
(btc(...)). A band's PANEL is the hourly grid UNIVERSE_START .. ceiling with one column per symbol that is
ever a member of that band (sorted by name). Every RUN (the base evaluation and each truncation cut, start
cut and jitter variant) computes the membership ONCE from the bars inside its own row range, so a cut can
only make the unit unknown, never different; the blocks of a run all use that one membership (see BLOCKS).
Klines fields are NaN (unknown) where the bar is not usable (omr.universe, S3); mark / index / funding
columns are aligned as of each bar exactly as in program frames (omr.datasets.align_to_grid).

BLOCKS (S4, fix pass 3): a band is evaluated in blocks of UNIVERSE_BLOCK_MONTHS calendar months (top30;
boundaries at the first hour of January and July) or UNIVERSE_BLOCK_MONTHS_G8 (next30, G8). A RUN (the base
evaluation, a truncation cut, a start cut, a jitter variant) computes its membership ONCE from the bars of
its own rows r0..r1, exactly as the whole-panel path does; every block of the run takes its in-play mask
from that one membership. A block is only a computation chunk: its panel holds the band's members of every
month touched by the decision rows of its evaluated range (warm-up included), and it is evaluated from
OVERLAP_HOURS (97 days, at least the 90-day lookback limit plus 7 days) before the first hour of the month
of its first row. Self-check `block_overlap`: on the rows from (a block's first evaluated row + the
program's lookback_hours) to the row before the block, its own warm-up result must equal the previous
block's result bit for bit (a fault means the program's true memory exceeds its recorded lookback).
The engine runs block after block carrying positions, equity and the funding total.

stage1_u   DEV-only, uncounted: signals, truncation cuts (24 random + DEV end), start cuts (6 random over
           the first 60% of the grid, plus one that removes the first 31 hours of a panel symbol's history),
           activity_dev.
stage2_u   DEV+VAL, counted, needs a ValHandle: DEV rows equal to stage 1 (by symbol), 3 start cuts,
           engine, gates. G1-G7 and G10 as for the core; G6 shifts the whole weight matrix in time and sets
           to 0 every weight that lands on a symbol that is not in play or has no bar (actual and shifted
           runs alike); G8 = the same program on unit next30 has a positive Sharpe over its DEV+VAL span.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from omr import access
from omr import constants as C
from omr import data as DT
from omr import datasets as D
from omr import engine as E
from omr import interp as X
from omr import lang as L
from omr import pipeline as PL
from omr import stats as S
from omr import universe as U

HOUR_NS = U.HOUR_NS
KLINE_FIELDS = ("open", "high", "low", "close", "volume", "quote_volume", "trades", "taker_buy_volume",
                "taker_buy_quote_volume")
ENGINE_KLINE_COLS = ("open", "high", "low", "close", "trades", "is_gap")   # engine, activity, liquidation fallback
MEM_SAFETY = 1.5                                                            # R3: available >= 1.5 x the estimate


def program_fields(prog: L.Program) -> set:
    """Field names the program reads (btc(...) reads the core BTCUSDT frame, loaded in full)."""
    import ast as _ast
    out = set()
    for _, node in prog.defs:
        for n in _ast.walk(node):
            if isinstance(n, _ast.Call) and isinstance(n.func, _ast.Name) and n.func.id == "funding_mean":
                out.add("funding_mean")
            if isinstance(n, _ast.Name) and n.id in L.FIELDS:
                out.add(n.id)
    return out


def needed_columns(fields: set) -> dict:
    """{dataset: columns} a universe panel loads for a program reading `fields` (R3)."""
    kl = set(ENGINE_KLINE_COLS) | (fields & set(KLINE_FIELDS))
    return {"klines": sorted(kl), "funding": ["rate", "interval_hours"], "mark_klines": ["open", "high", "low", "close"],
            "index_klines": ["open", "high", "low", "close"] if "index_close" in fields else []}


def program_arrays(prog: L.Program) -> float:
    """Number of (T x K) float64 arrays a universe evaluation of `prog` holds at once (R3 estimate): the
    program's field arrays, the engine's five price / ratio / funding arrays and three boolean masks, the
    interpreter's named values and in-flight nodes (value + known), the base run's weights, raw signal and
    known channel, one cut run's, and one jitter variant's weights."""
    f = program_fields(prog)
    n_f = len(f & set(KLINE_FIELDS)) + (2.125 if "mark_close" in f else 0) + (2.125 if "index_close" in f else 0) \
        + (2.0 if ("funding8h" in f or "funding_mean" in f) else 0) + (0.125 if "funding_mean" in f else 0)
    return n_f + 5 + 3 * 0.125 + 1.125 * (len(prog.defs) + 6) + 2.125 * 2 + 1


def stage2_memory_estimate(prog: L.Program, sizes: dict) -> dict:
    """Bytes stage 2 needs for a top30 program (R3, with S4 blocks). sizes (omr.universe.stage2_sizes, from
    data/validation.json): grid rows, distinct top30 / next30 symbols, stored rows (sum and largest symbol),
    activity rows, and per band and block [rows evaluated, engine rows, symbols]. Per band: the block caches
    (program columns over each block's rows with overlap, engine columns over its own rows), the stored
    tables of one block's symbols while it is built, the interpreter's values on the largest block, and the
    whole-grid weights, raw signal, known channel and masks (G6's paired lag books for top30). The next30 band
    (G8) is evaluated and released first, so the peak is the larger band plus the activity of every symbol."""
    T = int(sizes["rows"])
    f = program_fields(prog)
    n_field = len(field_columns(f))
    cols = needed_columns(f)
    n_tab = len(cols["klines"]) + 2 + 4 + len(cols["index_klines"]) + 1
    interp = 1.125 * (len(prog.defs) + 6) + 2.125 + 1
    acts = int(sizes["crypto_rows"]) * 10
    out = {"activity_bytes": acts, "rows": T}
    for band, k_all in (("top30", int(sizes["top30"])), ("next30", int(sizes["next30"]))):
        blocks = sizes["blocks"][band]
        per = [k * (re * (8 * n_field + 2) + rg * 41) for re, rg, k in blocks]
        cache = sum(per) if band == "top30" else max(per)          # next30 blocks are streamed (one at a time)
        build = max(k for _, _, k in blocks) * int(sizes["symbol_rows_max"]) * 8 * n_tab
        work = max(k * re for re, _, k in blocks) * 8 * interp
        # G6 on the VAL half (R-C, paired lag; the actual and source rows are views of W): the plain actual
        # targets, A_k, S_k, one re-centring temporary and one engine target copy (5 float64) and the ok and
        # mask booleans per cell
        glob = T * k_all * (18 if band == "top30" else 17) + (T // 2) * k_all * 42 * (band == "top30")
        out[band] = int(cache + build + work + glob)
    out["bytes"] = int(acts + max(out["top30"], out["next30"]))
    return out


def available_memory_bytes():
    """Physical memory the operating system reports as available, or None when it cannot be read."""
    try:
        import ctypes

        class MS(ctypes.Structure):
            _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                        ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                        ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                        ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                        ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
        m = MS()
        m.dwLength = ctypes.sizeof(MS)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m)):
            return int(m.ullAvailPhys)
    except Exception:
        pass
    try:
        with open("/proc/meminfo", encoding="ascii") as f:
            for line in f:
                if line.startswith("MemAvailable:"):
                    return int(line.split()[1]) * 1024
    except Exception:
        pass
    return None


def memory_check(prog: L.Program, sizes: dict) -> dict:
    """{"ok", "estimate_bytes", "available_bytes"}: ok when the OS reports at least MEM_SAFETY x the estimate."""
    est = stage2_memory_estimate(prog, sizes)
    avail = available_memory_bytes()
    ok = avail is not None and avail >= MEM_SAFETY * est["bytes"]
    return {"ok": bool(ok), "estimate_bytes": est["bytes"], "available_bytes": avail, "estimate": est}


def T(s) -> pd.Timestamp:
    t = pd.Timestamp(s)
    t = t.tz_localize("UTC") if t.tzinfo is None else t.tz_convert("UTC")
    return t.as_unit("ns")


@dataclass
class UData:
    """Universe data under one ceiling. acts: {symbol: universe.Activity} of every crypto perpetual;
    raw: {symbol: {"klines", "funding", "mark_klines", "index_klines"}} of the panel symbols; until:
    {symbol: until or None}; btc: the core BTCUSDT frame; end: the ceiling (last grid row)."""
    acts: dict
    raw: dict
    btc: pd.DataFrame
    end: pd.Timestamp
    until: dict = field(default_factory=dict)
    _mem: dict = field(default_factory=dict)
    loader: object = None                       # symbol -> tables, for symbols not held in `raw` (disk data)
    loadable: frozenset = frozenset()
    start: object = None                        # first grid row (default UNIVERSE_START; a block's own start)

    def grid(self) -> pd.DatetimeIndex:
        a = T(C.UNIVERSE_START) if self.start is None else T(self.start)
        return pd.date_range(a, self.end, freq="h").as_unit("ns")

    def has(self, s: str) -> bool:
        return s in self.raw or s in self.loadable

    def tables(self, s: str, lo_ns: int | None = None, hi_ns: int | None = None) -> dict:
        """The symbol's tables; with a window, klines / mark / index rows from lo - 48 h to hi only (every
        panel column of the window is unchanged: as-of seeds before it are never read) and funding rows up
        to hi (all earlier settlements: as-of fields and freshness read them)."""
        t = self.raw[s] if s in self.raw else self.loader(s)
        if lo_ns is None:
            return t
        a, b = pd.Timestamp(int(lo_ns) - 48 * HOUR_NS, tz="UTC"), pd.Timestamp(int(hi_ns), tz="UTC")
        out = {}
        for d, df in t.items():
            ix = df.index
            out[d] = df[ix <= b] if d == "funding" else df[(ix >= a) & (ix <= b)]
        return out

    def membership(self, lo_ns: int, hi_ns: int) -> U.Membership:
        key = (int(lo_ns), int(hi_ns))
        if key not in self._mem:
            if len(self._mem) > 8:
                self._mem.clear()
            self._mem[key] = U.membership(self.acts, list(self.acts), lo_ns, hi_ns)
        return self._mem[key]


def uweights(raw: np.ndarray) -> np.ndarray:
    """The portfolio weight rule for universe units: not known -> 0, clip to [-1, 1], scale down by 1 / gross
    when gross > 1, with gross summed SEQUENTIALLY in column (name) order, so a column that holds 0 changes
    nothing and a block panel gives the same bits as the whole panel (S4)."""
    w = np.clip(np.where(np.isfinite(raw), raw, 0.0), -1.0, 1.0)
    if w.shape[1] == 0:
        return w
    g = np.cumsum(np.abs(w), axis=1)[:, -1:]
    return np.where(g > 1.0, w / np.where(g > 0, g, 1.0), w)


def _scatter(grid_ns: np.ndarray, idx_ns: np.ndarray, vals: np.ndarray, fill):
    out = np.full(len(grid_ns), fill, dtype=np.float64)
    pos = np.searchsorted(grid_ns, idx_ns)
    ok = (pos < len(grid_ns)) & (grid_ns[np.minimum(pos, len(grid_ns) - 1)] == idx_ns)
    out[pos[ok]] = np.asarray(vals)[ok]
    return out


class FullPanel:
    """Full-grid arrays of one band's panel (lazy per column), shared by every cut of one evaluation."""

    def __init__(self, ud: UData, band: str, symbols=None):
        self.ud, self.band = ud, band
        self.grid = ud.grid()
        self.ns = self.grid.asi8
        if symbols is None:
            mem = ud.membership(int(self.ns[0]), int(self.ns[-1]))
            missing = [s for s in mem.ever(band) if not ud.has(s)]
            if missing:
                raise PL.KernelFault(f"panel symbols without stored tables: {missing[:5]}")
            symbols = mem.ever(band)
        self.symbols = sorted(symbols)
        self._c = {}
        self.active = self._active()
        self.fresh = self._fresh()                     # R2: funding fresh enough to be held

    def _active(self) -> np.ndarray:
        out = np.zeros((len(self.ns), len(self.symbols)), dtype=bool)
        for k, s in enumerate(self.symbols):
            a = self.ud.acts[s]
            i0, i1 = U.rows_in(a, int(self.ns[0]), int(self.ns[-1]))
            if i1 > i0:
                p0 = (a.start + i0 * HOUR_NS - self.ns[0]) // HOUR_NS
                out[p0:p0 + (i1 - i0), k] = a.usable[i0:i1]          # S3: usable bars
        return out

    def _fresh(self) -> np.ndarray:
        out = np.zeros((len(self.ns), len(self.symbols)), dtype=bool)
        for k, s in enumerate(self.symbols):
            fu = self.ud.tables(s)["funding"]
            u = self.ud.until.get(s)
            if u:
                fu = fu[fu.index < T(u)]
            out[:, k] = U.funding_fresh(self.ns, DT.ns_int(D.get("funding").visible_from(fu)),
                                        fu["interval_hours"].to_numpy(dtype=np.float64))
        return out

    def _kl(self, s):
        kl = self.ud.tables(s)["klines"]
        u = self.ud.until.get(s)
        return kl[kl.index < T(u)] if u else kl

    def col(self, name: str) -> np.ndarray:
        if name in self._c:
            return self._c[name]
        Tn, K = len(self.ns), len(self.symbols)
        if name in KLINE_FIELDS:
            out = np.full((Tn, K), np.nan)
            for k, s in enumerate(self.symbols):
                kl = self._kl(s)
                out[:, k] = _scatter(self.ns, DT.ns_int(kl.index), kl[name].to_numpy(dtype=np.float64), np.nan)
            out[~self.active] = np.nan
            self._c[name] = out
            return out
        if name == "funding.fresh":                    # U7: funding8h known only while funding is fresh (as R2)
            return self.fresh
        ds = name.split(".")[0]
        if ds in ("funding", "mark_klines", "index_klines"):
            dset = D.get(ds)
            cols = list(dset.fields)
            arrs = {f: np.full((Tn, K), np.nan) for f in cols}
            new = np.zeros((Tn, K), dtype=bool)
            for k, s in enumerate(self.symbols):
                rows = self.ud.tables(s)[ds]
                u = self.ud.until.get(s)
                if u:
                    rows = rows[rows.index < T(u)]
                if len(rows) == 0:
                    continue
                asof, nw = D.align_to_grid(rows[cols], dset.visible_from(rows), self.grid)
                for f in cols:
                    arrs[f][:, k] = asof[f].to_numpy()
                new[:, k] = nw
            for f in cols:
                self._c[f"{ds}.{f}"] = arrs[f]
            self._c[f"{ds}.new"] = new
            return self._c[name]
        if name == "funding_rate":                     # engine: rate settled at that bar's open, else 0
            out = np.where(self.col("funding.new"), self.col("funding.rate"), 0.0)
            out[~self.active] = 0.0
            self._c[name] = out
            return out
        if name in ("liq_dn", "liq_up"):
            dn = np.full((Tn, K), np.nan)
            up = np.full((Tn, K), np.nan)
            for k, s in enumerate(self.symbols):
                kl = self._kl(s)
                mk = self.ud.tables(s)["mark_klines"]
                lq = D.liquidation_ratios(kl, mk if len(mk) else None)
                dn[:, k] = _scatter(self.ns, DT.ns_int(kl.index), lq["dn"].to_numpy(), np.nan)
                up[:, k] = _scatter(self.ns, DT.ns_int(kl.index), lq["up"].to_numpy(), np.nan)
            self._c["liq_dn"], self._c["liq_up"] = dn, up
            return self._c[name]
        raise KeyError(name)


def view(fp: FullPanel, start: pd.Timestamp | None = None, upto: pd.Timestamp | None = None):
    """(row slice, Panel) for the rows grid[start:upto] with the membership recomputed from those rows."""
    i0 = 0 if start is None else int(np.searchsorted(fp.ns, T(start).value))
    i1 = len(fp.ns) if upto is None else int(np.searchsorted(fp.ns, T(upto).value, side="right"))
    sl = slice(i0, i1)
    ns = fp.ns[sl]
    mem = fp.ud.membership(int(ns[0]), int(ns[-1]))
    act = fp.active[sl] & fp.fresh[sl]                # R2: in play = member, active bar, fresh funding
    P_, uk = U.inplay_matrix(mem, fp.band, ns, fp.symbols, act)
    panel = X.Panel(fp.grid[sl], fp.symbols, lambda name: fp.col(name)[sl], P_, uk)
    return sl, panel


def unit_full_u(prog: L.Program, params: dict, fp: FullPanel, start=None, upto=None, literals=None):
    """(weights, raw, known) on grid[start:upto]; not-in-play symbols are unknown (weight 0)."""
    sl, panel = view(fp, start, upto)
    btc = fp.ud.btc.reindex(panel.index)
    raw, kn = X.evaluate_full(prog, params, panel, btc, literals)
    return uweights(raw), raw, kn


def start_cut_positions(fp: FullPanel, rng, n_cuts: int, span: float, symbol_cut: bool) -> list:
    hi = int(span * len(fp.ns))
    cuts = sorted(rng.choice(np.arange(1, hi), size=min(n_cuts, hi - 1), replace=False).tolist()) if hi >= 2 else []
    if symbol_cut and fp.symbols:
        mid = fp.ns[len(fp.ns) // 2]
        firsts = [(abs(fp.ud.acts[s].start - mid), fp.ud.acts[s].start) for s in fp.symbols
                  if fp.ud.acts[s].start > fp.ns[0]]
        if firsts:
            c = int((min(firsts)[1] + 31 * HOUR_NS - fp.ns[0]) // HOUR_NS)   # removes its first 31 hours
            if 0 < c < len(fp.ns) - 1:
                cuts.append(c)
    return cuts


def _unit(obj, prog, params, start=None, upto=None, literals=None):
    if isinstance(obj, Blocked):
        return obj.unit(prog, params, start=start, upto=upto, literals=literals)
    return unit_full_u(prog, params, obj, start=start, upto=upto, literals=literals)


def start_cut_check_u(prog, params, fp, raw, kn, cuts) -> int | None:
    for c in cuts:
        _, rc, kc = _unit(fp, prog, params, start=fp.grid[c])
        if not PL.start_cut_agrees(rc, kc, raw[c:], kn[c:]):
            return c
    return None


# ---------------------------------------------------------------- blocks (S4)

OVERLAP_HOURS = U.OVERLAP_HOURS               # 97 days: the membership read window
if OVERLAP_HOURS < C.LOOKBACK_MAX_HOURS + 168:   # fix pass 3 (d): a week beyond the 90-day lookback limit
    raise RuntimeError("OVERLAP_HOURS must be at least LOOKBACK_MAX_HOURS + 168")
ENGINE_COLS = ("open", "close", "liq_dn", "liq_up", "funding_rate")


def field_columns(fields: set) -> list:
    """Panel column names the interpreter may request for a program reading `fields`."""
    out = [f for f in KLINE_FIELDS if f in fields]
    if "mark_close" in fields:
        out += ["mark_klines.close", "mark_klines.new"]
    if "index_close" in fields:
        out += ["index_klines.close", "index_klines.new"]
    if "funding8h" in fields or "funding_mean" in fields:
        out += ["funding.rate", "funding.interval_hours", "funding.new"]
    if "funding8h" in fields:
        out += ["funding.fresh"]
    return out


class BlockPanel:
    """One block: global rows [b, e), program columns over [s, e) (s = b - overlap), engine columns over
    [eng0, e) (eng0 = b - 1: the previous row of positions carried in)."""

    def __init__(self, k, b, e, s, eng0, symbols, usable, fresh, fields, eng):
        self.k, self.b, self.e, self.s, self.eng0 = k, b, e, s, eng0
        self.symbols = list(symbols)
        self.colset = set(symbols)
        self.usable, self.fresh, self.fields, self.eng = usable, fresh, fields, eng


class Blocked:
    """A band's panel in time blocks (S4). months=None: one block (the whole panel)."""

    def __init__(self, ud: UData, band: str, months=C.UNIVERSE_BLOCK_MONTHS, fields=None, boundaries=None,
                 keep=True):
        self.ud, self.band = ud, band
        self.grid = ud.grid()
        self.ns = self.grid.asi8
        self.mem = ud.membership(int(self.ns[0]), int(self.ns[-1]))
        ever = self.mem.ever(band)
        missing = [x for x in ever if not ud.has(x)]
        if missing:
            raise PL.KernelFault(f"panel symbols without stored tables: {missing[:5]}")
        self.symbols = sorted(ever)
        self.col = {x: k for k, x in enumerate(self.symbols)}
        self.fields = (set(L.FIELDS) | {"funding_mean"}) if fields is None else set(fields)
        self.months = months
        self.plan = U.block_plan(self.mem, self.ns, band, months=months, boundaries=boundaries)
        self.bounds = [(x["b"], x["e"]) for x in self.plan]
        self.keep = keep                              # False: each block is built when used and then dropped
        self.overlap_cells = 0
        self._blocks = [self._block(k) for k in range(len(self.plan))] if keep else None

    @property
    def blocks(self):
        if self._blocks is not None:
            return self._blocks
        return (self._block(k) for k in range(len(self.plan)))

    def _block(self, k: int) -> BlockPanel:
        """Block k from the stored tables of its symbols, sliced to the block's window."""
        names = field_columns(self.fields)
        blk = self.plan[k]
        b, e, s0 = blk["b"], blk["e"], blk["s0"]
        syms = sorted(blk["symbols"] & set(self.symbols))
        raw = {sym: self.ud.tables(sym, int(self.ns[s0]), int(self.ns[e - 1])) for sym in syms}
        eng0 = max(b - 1, 0)
        bud = UData(acts=self.ud.acts, raw=raw, btc=None, end=self.grid[e - 1], until=self.ud.until,
                    start=self.grid[s0])
        fp = FullPanel(bud, self.band, symbols=syms)
        fields = {n: np.ascontiguousarray(fp.col(n)) for n in names}
        i = eng0 - s0
        eng = {n: np.ascontiguousarray(fp.col(n)[i:]) for n in ENGINE_COLS}
        eng["av"] = np.ascontiguousarray(fp.active[i:])
        bp = BlockPanel(k, b, e, s0, eng0, syms, fp.active, fp.fresh, fields, eng)
        del fp, bud, raw
        return bp

    # ------------------------------------------------------------ evaluation
    def rows(self, start=None, upto=None) -> tuple:
        r0 = 0 if start is None else int(np.searchsorted(self.ns, T(start).value))
        r1 = len(self.ns) - 1 if upto is None else int(np.searchsorted(self.ns, T(upto).value, side="right")) - 1
        return r0, r1

    def run_membership(self, r0: int, r1: int) -> U.Membership:
        """T1 (a): the ONE membership of a run on rows r0..r1, from the bars of those rows."""
        return self.ud.membership(int(self.ns[r0]), int(self.ns[r1]))

    def _eval(self, bp: BlockPanel, prog, params, r0: int, r1: int, literals, mem):
        """Block bp on global rows r0..r1 with the run's membership `mem`."""
        i0, i1 = r0 - bp.s, r1 - bp.s + 1
        ns = self.ns[r0:r1 + 1]
        P_, uk = U.inplay_matrix(mem, self.band, ns, bp.symbols, bp.usable[i0:i1] & bp.fresh[i0:i1])

        def get(name):
            if name not in bp.fields:
                raise KeyError(f"column {name} was not loaded for this program")
            return bp.fields[name][i0:i1]
        panel = X.Panel(self.grid[r0:r1 + 1], bp.symbols, get, P_, uk)
        btc = self.ud.btc.reindex(panel.index)
        raw, kn = X.evaluate_full(prog, params, panel, btc, literals)
        return uweights(raw), raw, kn, P_

    def _overlap_tail(self, k: int, r0: int, hi: int, ev0: int, rb, kb, syms, lookback: int):
        """The rows of block k's result the next block will compare (from the next block's first evaluated
        row + lookback to hi), or None."""
        if k + 1 >= len(self.plan):
            return None
        a = max(max(r0, self.plan[k + 1]["s0"]) + lookback, ev0)
        if a > hi:
            return None
        return {"a": a, "z": hi, "syms": list(syms), "raw": rb[a - ev0:].copy(), "kn": kb[a - ev0:].copy()}

    def _check_overlap(self, tail, ev0: int, lo: int, rb, kb, syms, lookback: int) -> int:
        """T1 (e) block_overlap: on the rows from this block's first evaluated row + lookback to the row before
        the block that the previous block also evaluated, results equal bit for bit, by symbol. Returns the
        number of KNOWN cells compared (U8: a check over no known cell is vacuous, and visible as 0)."""
        if tail is None:
            return 0
        a, z = max(tail["a"], ev0 + lookback), min(tail["z"], lo - 1)
        if a > z:
            return 0
        prev = {x: j for j, x in enumerate(tail["syms"])}
        cur = {x: j for j, x in enumerate(syms)}
        pr, pk = tail["raw"][a - tail["a"]:z - tail["a"] + 1], tail["kn"][a - tail["a"]:z - tail["a"] + 1]
        cr, ck = rb[a - ev0:z - ev0 + 1], kb[a - ev0:z - ev0 + 1]
        cells = 0
        for x in set(prev) | set(cur):
            if x in prev and x in cur:
                i, j = prev[x], cur[x]
                if not (np.array_equal(pk[:, i], ck[:, j]) and np.array_equal(pr[:, i], cr[:, j], equal_nan=True)):
                    raise PL.KernelFault("block_overlap")
                cells += int(pk[:, i].sum())
            elif x in prev:
                if pk[:, prev[x]].any():
                    raise PL.KernelFault("block_overlap")
            elif ck[:, cur[x]].any():
                raise PL.KernelFault("block_overlap")
        return cells

    def _runs(self, prog, params, r0: int, r1: int, literals=None, mem=None, from_row: int | None = None):
        """One RUN on rows r0..r1: yields (bp, lo, hi, ev0, W, raw, known, inplay) block by block, every block
        with the run's one membership, checking block_overlap between consecutive evaluated blocks. from_row:
        skip the blocks that end before it (they are not evaluated)."""
        mem = self.run_membership(r0, r1) if mem is None else mem
        L_ = int(prog.lookback_hours)
        tail = None
        cells = 0
        for bp in self.blocks:
            lo, hi = max(bp.b, r0), min(bp.e - 1, r1)
            if lo > hi or (from_row is not None and hi < from_row):
                continue
            ev0 = max(r0, bp.s)
            Wb, rb, kb, Pb = self._eval(bp, prog, params, ev0, hi, literals, mem)
            cells += self._check_overlap(tail, ev0, lo, rb, kb, bp.symbols, L_)
            tail = self._overlap_tail(bp.k, r0, hi, ev0, rb, kb, bp.symbols, L_)
            yield bp, lo, hi, ev0, Wb, rb, kb, Pb
        self.overlap_cells = cells                    # U8: known cells the last completed run's check compared

    def unit(self, prog, params, start=None, upto=None, literals=None, inplay=False, raw_rows=None):
        """(W, raw, known[, inplay]) on rows start..upto over the global columns, stitched from the blocks of
        ONE run (one membership). raw_rows: None = raw and known on every row; an int n = on the first n rows
        only (memory)."""
        r0, r1 = self.rows(start, upto)
        n, K = r1 - r0 + 1, len(self.symbols)
        nr = n if raw_rows is None else min(int(raw_rows), n)
        W = np.zeros((n, K))
        raw = np.full((nr, K), np.nan)
        kn = np.zeros((nr, K), dtype=bool)
        P_ = np.zeros((n, K), dtype=bool) if inplay else None
        for bp, lo, hi, ev0, Wb, rb, kb, Pb in self._runs(prog, params, r0, r1, literals):
            t = slice(lo - ev0, hi - ev0 + 1)
            rows = np.arange(lo - r0, hi - r0 + 1)[:, None]
            cols = np.array([self.col[x] for x in bp.symbols], dtype=np.int64)[None, :]
            W[rows, cols] = Wb[t]
            keep = rows[:, 0] < nr
            if keep.any():
                raw[rows[keep], cols] = rb[t][keep]
                kn[rows[keep], cols] = kb[t][keep]
            if inplay:
                P_[rows, cols] = Pb[t]
        return (W, raw, kn, P_) if inplay else (W, raw, kn)

    def start_cut_agrees(self, prog, params, c: int) -> bool:
        """The start-cut self-check block by block: wherever the run cut at row c is known, the base run is
        known and bit-identical. The cut run uses the cut run's membership (rows c..end), the base run the
        base run's (every row); the base blocks are recomputed, so no whole-grid raw is kept."""
        T1 = len(self.ns) - 1
        cut = self._runs(prog, params, c, T1)
        base = self._runs(prog, params, 0, T1, mem=self.mem, from_row=c)
        for (bp, lo, hi, ev_c, _, rc, kc, _), (bq, lo_b, hi_b, ev_b, _, rb, kb, _) in zip(cut, base):
            if bp.k != bq.k or hi != hi_b:
                raise PL.KernelFault("start-cut blocks out of step")
            rc, kc = rc[lo - ev_c:], kc[lo - ev_c:]
            rb, kb = rb[lo - ev_b:], kb[lo - ev_b:]
            if not PL.start_cut_agrees(rc, kc, rb, kb):
                return False
        return True

    # ------------------------------------------------------------ engine
    def pos(self, s: str):
        t = T(s)
        return int(self.grid.get_loc(t)) if t in self.grid else None

    def eng_rows(self, name: str, r0: int, r1: int) -> np.ndarray:
        """An engine column over rows r0..r1 for the global columns (NaN / False / 0 outside the blocks)."""
        n, K = r1 - r0 + 1, len(self.symbols)
        out = np.zeros((n, K), dtype=bool) if name == "av" else (np.zeros((n, K)) if name == "funding_rate"
                                                                  else np.full((n, K), np.nan))
        for bp in self.blocks:
            lo, hi = max(bp.b, r0), min(bp.e - 1, r1)
            if lo > hi:
                continue
            cols = np.array([self.col[x] for x in bp.symbols], dtype=np.int64)[None, :]
            out[np.arange(lo - r0, hi - r0 + 1)[:, None], cols] = bp.eng[name][lo - bp.eng0:hi - bp.eng0 + 1]
        return out

    def _extra(self, syms: list, r0: int, r1: int) -> dict:
        """Engine columns for symbols carried into a block whose panel does not hold them (a residual
        position below the rebalance band from an earlier block)."""
        bud = UData(acts=self.ud.acts, raw={x: self.ud.tables(x) for x in syms}, btc=None, end=self.grid[r1],
                    until=self.ud.until, start=self.grid[r0])
        fp = FullPanel(bud, self.band, symbols=syms)
        out = {n: fp.col(n) for n in ENGINE_COLS}
        out["av"] = fp.active
        return out

    def run_targets(self, tgt: np.ndarray, s: int, e: int, cost_rate=C.UNIVERSE_COST_RATE, pay=1.0, recv=1.0) -> E.Run:
        """The universe engine over rows s..e with targets tgt (row j of tgt executed at row s + j), block by
        block, carrying positions, equity, the dead flag and the funding total."""
        n = e - s + 1
        equity, pre, gross, net = np.zeros(n), np.zeros(n), np.zeros(n), np.zeros(n)
        ev_i, ev_t, ev_c = [], [], []
        h, eq, dead, fpaid, liq, first = {}, 1.0, False, 0.0, -1, True
        for bp in self.blocks:
            lo, hi = max(bp.b, s), min(bp.e - 1, e)
            if lo > hi:
                continue
            warm = not first
            a0 = (lo - 1 if warm else lo) - bp.eng0
            a1 = hi - bp.eng0 + 1
            syms = list(bp.symbols)
            arrs = {nm: bp.eng[nm][a0:a1] for nm in ENGINE_COLS + ("av",)}
            extra = sorted(x for x, v in h.items() if v != 0.0 and x not in bp.colset)
            if extra:
                ex = self._extra(extra, lo - 1, hi)
                arrs = {nm: np.concatenate([arrs[nm], ex[nm]], axis=1) for nm in arrs}
                syms = syms + extra
                order = np.argsort(np.array(syms, dtype=object), kind="stable")    # keep the name order
                syms = [syms[i] for i in order]
                arrs = {nm: np.ascontiguousarray(v[:, order]) for nm, v in arrs.items()}
            cols = np.array([self.col.get(x, -1) for x in syms], dtype=np.int64)
            tg = np.zeros((a1 - a0, len(syms)))
            have = cols >= 0
            tg[(1 if warm else 0):, have] = tgt[lo - s:hi - s + 1][:, cols[have]]
            h0 = np.array([h.get(x, 0.0) for x in syms])
            out = E.run_block_u(arrs["open"], arrs["close"], arrs["av"], arrs["liq_dn"], arrs["liq_up"],
                                arrs["funding_rate"], tg, cost_rate=cost_rate, pay_mult=pay, recv_mult=recv,
                                h0=h0, eq0=eq, dead0=dead, t0=1 if warm else 0, fp0=fpaid)
            t0 = 1 if warm else 0
            seg = slice(lo - s, hi - s + 1)
            equity[seg], gross[seg], net[seg], pre[seg] = out[0][t0:], out[1][t0:], out[2][t0:], out[8][t0:]
            ev_i.append(out[3] - t0 + (lo - s))
            ev_t.append(out[4])
            ev_c.append(out[5])
            fpaid = out[6]
            if out[7] >= 0 and liq < 0:
                liq = int(out[7]) - t0 + (lo - s)
            h = {x: v for x, v in zip(syms, out[9]) if v != 0.0}
            eq, dead = out[10], bool(out[11])
            first = False
        cat = (lambda xs, dt: np.concatenate(xs).astype(dt) if xs else np.zeros(0, dtype=dt))
        return E.Run(self.grid[s:e + 1], equity, gross, net, cat(ev_i, np.int64), cat(ev_t, np.float64),
                     cat(ev_c, np.float64), float(fpaid), int(liq), pre)

    def inplay(self, start=None, upto=None) -> np.ndarray:
        """The in-play mask (membership, usable bar, fresh funding) on rows start..upto, global columns."""
        r0, r1 = self.rows(start, upto)
        mem = self.run_membership(r0, r1)                 # one membership for the run
        out = np.zeros((r1 - r0 + 1, len(self.symbols)), dtype=bool)
        for bp in self.blocks:
            lo, hi = max(bp.b, r0), min(bp.e - 1, r1)
            if lo > hi:
                continue
            ns = self.ns[lo:hi + 1]
            i0, i1 = lo - bp.s, hi - bp.s + 1
            P_, _ = U.inplay_matrix(mem, self.band, ns, bp.symbols, bp.usable[i0:i1] & bp.fresh[i0:i1])
            cols = np.array([self.col[x] for x in bp.symbols], dtype=np.int64)[None, :]
            out[np.arange(lo - r0, hi - r0 + 1)[:, None], cols] = P_
        return out

    def run(self, W: np.ndarray, s: int, e: int, cost_mult=1.0, pay=1.0, recv=1.0) -> E.Run:
        """As UMarket.run: rows s..e, the target at row j is the decision of row j-1 (W on the full grid)."""
        return self.run_targets(W[s - 1:e], s, e, cost_rate=C.UNIVERSE_COST_RATE * cost_mult, pay=pay, recv=recv)


# ---------------------------------------------------------------- market

class UMarket:
    """Engine arrays of a band's panel; run(W, s, e) trades grid positions s..e (target at j = decision j-1)."""

    def __init__(self, fp: FullPanel):
        self.fp = fp
        self.grid = fp.grid
        self.av = fp.active
        self.op = fp.col("open")
        self.cl = fp.col("close")
        self.dn, self.up = fp.col("liq_dn"), fp.col("liq_up")
        self.fr = fp.col("funding_rate")

    def pos(self, s: str):
        t = T(s)
        return int(self.grid.get_loc(t)) if t in self.grid else None

    def args(self, s: int, e: int):
        sl = slice(s, e + 1)
        return self.op[sl], self.cl[sl], self.av[sl], self.dn[sl], self.up[sl], self.fr[sl]

    def run(self, W: np.ndarray, s: int, e: int, cost_mult=1.0, pay=1.0, recv=1.0) -> E.Run:
        return E.run_u(self.grid[s:e + 1], *self.args(s, e), W[s - 1:e],
                       cost_rate=C.UNIVERSE_COST_RATE * cost_mult, pay_mult=pay, recv_mult=recv)


# ---------------------------------------------------------------- stage 1

def stage1_u(prog: L.Program, params: dict, ud_dev: UData, rng, opts: PL.Opts = PL.Opts(),
             months=C.UNIVERSE_BLOCK_MONTHS) -> dict:
    """Stage 1 of a top30 program; the block_overlap self-check fails it as an (uncounted) kernel fault."""
    try:
        return _stage1_u(prog, params, ud_dev, rng, opts, months)
    except PL.KernelFault as e:
        if str(e) != "block_overlap":
            raise
        return {"ok": False, "code": "kernel_fault", "fault": "block_overlap", "cuts": 0}


def _stage1_u(prog, params, ud_dev, rng, opts, months) -> dict:
    fp = Blocked(ud_dev, "top30", months=months, fields=program_fields(prog))
    grid = fp.grid
    if grid[-1] != T(C.DEV_END):
        raise PL.KernelFault("stage 1 universe data must end at DEV end")
    W, raw, kn = fp.unit(prog, params)
    cells = int(fp.overlap_cells)                   # U8: known cells the base run's block_overlap check compared
    dev_s = int(grid.get_loc(T(C.DEV_START)))
    dev_e = len(grid) - 1
    pool = np.arange(dev_s - 1, dev_e)
    cuts = sorted(set(rng.choice(pool, size=min(opts.truncation_cuts, len(pool)), replace=False).tolist()) | {dev_e})
    for c in cuts:
        _, rt, kt = fp.unit(prog, params, upto=grid[c])
        if not (PL.same_rows(rt, raw[:c + 1]) and np.array_equal(kt, kn[:c + 1])):
            return {"ok": False, "code": "kernel_fault", "fault": "truncation", "cuts": len(cuts),
                    "block_overlap_cells": cells}
    sc = start_cut_positions(fp, rng, opts.start_cuts, C.START_CUT_SPAN, symbol_cut=True)
    if start_cut_check_u(prog, params, fp, raw, kn, sc) is not None:
        return {"ok": False, "code": "kernel_fault", "fault": "start_cut", "cuts": len(cuts),
                "block_overlap_cells": cells}
    n_dev = PL.direction_changes(W, dev_s - 1, dev_e - 1)
    ok = n_dev >= C.MIN_DIRECTION_CHANGES_DEV
    return {"ok": ok, "code": None if ok else "activity_dev", "cuts": len(cuts), "start_cuts": len(sc),
            "direction_changes_dev": n_dev, "grid": grid, "W": W, "raw": raw, "known": kn,
            "symbols": list(fp.symbols), "block_overlap_cells": cells}


def screen_dev_u(prog: L.Program, params: dict, fp_dev) -> dict:
    """Calibration screening only: DEV signals and the activity rule, no self-checks (fp_dev: a Blocked)."""
    W, raw, kn = _unit(fp_dev, prog, params)
    dev_s = int(fp_dev.grid.get_loc(T(C.DEV_START)))
    n_dev = PL.direction_changes(W, dev_s - 1, len(fp_dev.grid) - 2)
    ok = n_dev >= C.MIN_DIRECTION_CHANGES_DEV
    return {"ok": ok, "code": None if ok else "activity_dev", "direction_changes_dev": n_dev, "grid": fp_dev.grid,
            "W": W}


# ---------------------------------------------------------------- stage 2

def dev_rows_equal(s1: dict, fp, raw, kn) -> bool:
    """Stage-2 DEV rows equal stage 1, compared by symbol; a symbol not in the stage-1 panel is unknown on
    every DEV row."""
    n = len(s1["grid"])
    if not s1["grid"].equals(fp.grid[:n]):
        return False
    col1 = {s: k for k, s in enumerate(s1["symbols"])}
    for k, s in enumerate(fp.symbols):
        if s in col1:
            j = col1[s]
            if not (PL.same_rows(raw[:n, k], s1["raw"][:, j]) and np.array_equal(kn[:n, k], s1["known"][:, j])):
                return False
        elif kn[:n, k].any():
            return False
    return all(s in fp.symbols or not s1["known"][:, col1[s]].any() for s in s1["symbols"])


def next30_score(prog: L.Program, params: dict, ud: UData, months=C.UNIVERSE_BLOCK_MONTHS_G8) -> dict:
    """G8: the program on unit next30, DEV start to VAL end; positive Sharpe passes."""
    bu = Blocked(ud, "next30", months=months, fields=program_fields(prog), keep=False)    # blocks not kept
    if not bu.symbols:
        return {"code": "no_unit", "sharpe": None}
    W, _, _ = bu.unit(prog, params, raw_rows=0)
    run = bu.run(W, bu.pos(C.DEV_START), bu.pos(C.VAL_END))
    fp = bu
    if run.liquidated:
        return {"code": "liquidated", "sharpe": None}
    return {"code": None, "sharpe": S.sharpe(run.daily_returns()), "symbols": len(fp.symbols)}


def stage2_u(prog: L.Program, params: dict, ud: UData, s1: dict | None, opts: PL.Opts, handle, seed: int,
             p_max: float | None, months=C.UNIVERSE_BLOCK_MONTHS) -> dict:
    """COUNTED. Raises on unexpected errors (the evaluator turns that into a kernel_fault row); the
    block_overlap self-check (any blocked run: base, start cuts, jitter variants, G8) ends it as the counted
    kernel fault `block_overlap`."""
    access.require(handle, "upipeline.stage2_u")
    try:
        return _stage2_u(prog, params, ud, s1, opts, handle, seed, p_max, months)
    except PL.KernelFault as e:
        if str(e) != "block_overlap":
            raise
        return {"status": "kernel_fault", "reason": "block_overlap"}


def _stage2_u(prog, params, ud, s1, opts, handle, seed, p_max, months) -> dict:
    if ud.end != T(C.VAL_END):
        raise PL.KernelFault("stage 2 universe data must end at VAL end")
    g8m = C.UNIVERSE_BLOCK_MONTHS_G8 if months == C.UNIVERSE_BLOCK_MONTHS else months
    g8 = next30_score(prog, params, ud, months=g8m) if opts.include_g8 else None   # streamed, released first
    fp = Blocked(ud, "top30", months=months, fields=program_fields(prog))
    n_dev = len(s1["grid"]) if s1 is not None else 0
    W, raw, kn = fp.unit(prog, params, raw_rows=n_dev)             # raw / known kept for the DEV rows only
    if s1 is not None and not dev_rows_equal(s1, fp, raw, kn):
        return {"status": "kernel_fault", "reason": "dev_rows_changed"}
    if opts.start_cuts_val > 0:
        sc = start_cut_positions(fp, np.random.default_rng([seed, 4]), opts.start_cuts_val, C.START_CUT_SPAN_VAL,
                                 symbol_cut=False)
        if not all(fp.start_cut_agrees(prog, params, c) for c in sc):
            return {"status": "kernel_fault", "reason": "start_cut"}
    rng = np.random.default_rng([seed, 2])
    variants = [] if PL.g5_vacuous(prog) else PL.jitter_params(prog, params, rng, opts.jitter_n)
    del raw, kn
    return ugates(W, fp, np.random.default_rng([seed, 3]), opts, p_max, prog=prog, params=params,
                  variants=variants, g8=g8, n_params=len(prog.params))


def evaluate_weights_u(W: np.ndarray, fp, seed: int, opts: PL.Opts, handle, p_max) -> dict:
    """CALIBRATION ONLY: gates for injected universe weights (noisy oracles); G5 passes, G8 not run.
    fp: a Blocked panel."""
    access.require(handle, "upipeline.evaluate_weights_u")
    return ugates(W, fp, np.random.default_rng([seed, 3]), opts, p_max, prog=None, params=None,
                  variants=[], g8=None, n_params=0)


def _seq_rowsum(x: np.ndarray) -> np.ndarray:
    """Row sums, sequential in column order (not pairwise)."""
    return np.cumsum(x, axis=1)[:, -1] if x.shape[1] else np.zeros(x.shape[0])


def g6_lags(L_: int, g0: int, rng, n: int) -> np.ndarray:
    """R-C: n lags in hours, uniform on [PERM_MIN_OFFSET_DAYS * 24, L // 2] (L = VAL rows, g0 = the grid row of
    the first VAL decision). KernelFault when VAL is too short or the grid holds fewer than L // 2 rows
    before g0 (every source row must exist)."""
    lo, hi = C.PERM_MIN_OFFSET_DAYS * 24, L_ // 2
    if hi < lo:
        raise PL.KernelFault("VAL too short for the lag test")
    if g0 - hi < 0:
        raise PL.KernelFault("not enough history before VAL for the lag test")
    return rng.integers(lo, hi + 1, size=n)


def g6_books(W: np.ndarray, P_: np.ndarray, ok: np.ndarray, g0: int, k: int) -> tuple:
    """R-C: the paired books of lag k on the VAL window. W, P_: weights and in-play mask over the WHOLE grid;
    VAL row i (i = 0 .. L-1, L = len(ok)) is decided at grid row g0 + i and executed at g0 + 1 + i; ok[i] =
    in play at the decision row and a usable bar at the execution row. The source of row i is grid row
    g0 + i - k: always k hours BEFORE the decision row (before VAL start for i < k), never a later row.
    mask[i] = ok[i] and in play at the source row. A_k = W[g0 + i] on mask, S_k = W[g0 + i - k] on mask (0
    elsewhere). SYMMETRIC re-centring: a row whose own in-play set (A: P_[g0 + i]; S: P_[g0 + i - k]) has a
    name outside mask gets, on every mask name, (net of the row over its own set - net of the masked row) /
    (number of mask names); sums sequential in column order; no gross rescaling. A row with fewer than
    UNIVERSE_MIN_CS mask names is flat in both."""
    L_ = len(ok)
    if g0 - k < 0:
        raise PL.KernelFault("lag reaches before the grid")
    Wa, Da = W[g0:g0 + L_], P_[g0:g0 + L_]
    Ws, Ds = W[g0 - k:g0 - k + L_], P_[g0 - k:g0 - k + L_]       # views: the program's own earlier rows
    mask = ok & Ds
    nm = mask.sum(axis=1)
    books = []
    for w, own in ((Wa, Da), (Ws, Ds)):
        b = np.where(mask, w, 0.0)
        rc = np.nonzero((own & ~mask).any(axis=1) & (nm > 0))[0]
        if len(rc):
            un = _seq_rowsum(np.where(own[rc], w[rc], 0.0))
            ms = _seq_rowsum(b[rc])
            c = (un - ms) / nm[rc]
            b[rc] = np.where(mask[rc], b[rc] + c[:, None], 0.0)
        b[nm < C.UNIVERSE_MIN_CS] = 0.0
        books.append(b)
    return books[0], books[1]


def g6_books_tie(A_k: np.ndarray, S_k: np.ndarray) -> bool:
    """R-B (1): the shifted book equals the actual book of its pair within G6_PAIRED_BOOK_TIE on every cell."""
    return bool(np.all(np.abs(S_k - A_k) <= C.G6_PAIRED_BOOK_TIE))


def g6_paired_p(actual_sharpes, shifted_sharpes, ties=None) -> float:
    """p = (1 + number of k with S_k >= A_k) / (N + 1): a tie (R-B (1)) counts; otherwise S_k >= A_k when
    Sharpe(S_k) >= Sharpe(A_k) - G6_PAIRED_SHARPE_MARGIN (R-B (2)). Both can only raise p."""
    a = np.asarray(actual_sharpes, dtype=np.float64)
    s = np.asarray(shifted_sharpes, dtype=np.float64)
    t = np.zeros(len(s), dtype=bool) if ties is None else np.asarray(ties, dtype=bool)
    with np.errstate(invalid="ignore"):
        ge = t | (s >= a - C.G6_PAIRED_SHARPE_MARGIN)       # -inf (liquidated) on both sides counts as >=
    return (1 + int(np.sum(ge))) / (len(s) + 1)


def ugates(W, fp, rng_perm, opts: PL.Opts, p_max, prog, params, variants, g8, n_params) -> dict:
    mk = fp
    dev_s, val_s, val_e = mk.pos(C.DEV_START), mk.pos(C.VAL_START), mk.pos(C.VAL_END)
    base = mk.run(W, dev_s, val_e)
    if base.liquidated:
        return {"status": "liquidated", "reason": "liquidation"}
    daily = base.daily_returns()
    dev, val = PL.split_daily(daily)
    m = {"dev": S.summary(dev), "val": S.summary(val)}
    m["dev_val_max_drawdown"] = S.max_drawdown(daily)
    m["deploy_scale"] = min(1.0, C.DEPLOY_RISK_BUDGET / m["dev_val_max_drawdown"]) if m["dev_val_max_drawdown"] > 0 else 1.0
    n_years = len(daily) / C.PERIODS_PER_YEAR
    m["turnover_per_year"] = float(base.ev_turn.sum() / n_years) if n_years > 0 else 0.0
    m["avg_gross_exposure"] = float(base.gross.mean())
    m["avg_net_exposure"] = float(base.net.mean())
    m["rebalances"] = int(len(base.ev_idx))
    m["direction_changes_dev"] = PL.direction_changes(W, dev_s - 1, mk.pos(C.DEV_END) - 1)
    m["direction_changes_val"] = PL.direction_changes(W, val_s - 1, val_e - 1)
    m["funding_paid_total"] = float(base.funding_paid)
    m["costs_total"] = float(base.ev_cost.sum())
    m["val_sharpe_daily"] = S.sharpe_daily(val)
    m["n_daily"] = int(len(daily))
    m["unit_symbols"] = len(fp.symbols)
    m["unit_known_frac_dev_val"] = float(np.mean(W[dev_s - 1:val_e].any(axis=1)))
    g = {}
    g["G1"] = {"pass": bool(m["val"]["psr0"] >= C.G1_PSR_MIN), "value": m["val"]["psr0"]}
    fs_sh = PL.val_sharpe_of(mk.run(W, dev_s, val_e, pay=C.FUNDING_STRESS_PAY, recv=C.FUNDING_STRESS_RECV))
    g["G2"] = {"pass": bool(fs_sh > 0), "value": fs_sh}
    g["G3"] = {"pass": bool(m["dev"]["sharpe"] > 0), "value": m["dev"]["sharpe"]}
    cs_sh = PL.val_sharpe_of(mk.run(W, dev_s, val_e, cost_mult=C.COST_STRESS_MULT))
    g["G4"] = {"pass": bool(cs_sh > 0), "value": cs_sh}
    if variants:
        shs = []
        for q, lv in variants:                         # one variant in memory at a time
            Wv, _, _ = fp.unit(prog, q, literals=lv)
            shs.append(PL.val_sharpe_of(mk.run(Wv, dev_s, val_e)))
            del Wv
        r5 = PL.g5_rule(m["val"]["sharpe"], shs)
        g["G5"] = {"pass": r5["pass"], "value": {"n": len(shs), "median": r5["median"], "frac_positive": r5["frac_positive"]},
                   "g5_vacuous": False}
    else:
        g["G5"] = {"pass": True, "value": None, "g5_vacuous": True}
    L_ = val_e - val_s + 1
    g0 = val_s - 1
    # G6 (R-C): a causal PAIRED LAG test. VAL row i is decided at grid row g0 + i and executed at val_s + i;
    # D = in play at the decision row, ok = D and a usable bar at the execution row. For each lag k the program's
    # own weights k hours earlier (g6_books) are compared with its actual weights on the common names; the
    # plain actual run is reused when no row of A_k differs from it.
    inplay = fp.inplay()
    D_ = inplay[g0:val_e]
    ok = D_ & fp.eng_rows("av", val_s, val_e)

    def vrun(tgt):
        run = fp.run_targets(np.where(ok, tgt, 0.0), val_s, val_e)
        if run.liquidated:
            return float("-inf")
        return S.sharpe(run.daily_returns().to_numpy())

    plain = np.where(ok, W[g0:val_e], 0.0)
    actual = vrun(plain)                                  # the unmasked actual (kept in the detail)
    offs = g6_lags(L_, g0, rng_perm, opts.perm_n)
    a_sh, s_sh = np.zeros(len(offs)), np.zeros(len(offs))
    ties = np.zeros(len(offs), dtype=bool)
    for j, k in enumerate(offs):
        A_k, S_k = g6_books(W, inplay, ok, g0, int(k))
        a_sh[j] = actual if np.array_equal(A_k, plain) else vrun(A_k)
        ties[j] = g6_books_tie(A_k, S_k)                   # R-B (1): no second engine run for a tie
        s_sh[j] = a_sh[j] if ties[j] else vrun(S_k)
        del A_k, S_k
    p = g6_paired_p(a_sh, s_sh, ties)
    shifted = s_sh
    g["G6"] = {"pass": (bool(p <= p_max + 1e-12) if p_max is not None else None), "value": p, "threshold": p_max}
    buckets = []
    for name, a, b in C.G7_BUCKETS:
        r = daily[(daily.index >= T(a).normalize()) & (daily.index <= T(b))]
        buckets.append({"bucket": name, "n_days": int(len(r)), "return": S.total_return(r)})
    r7 = PL.g7_rule([x["return"] for x in buckets])
    g["G7"] = {"pass": r7["pass"], "value": {"n_positive": r7["n_positive"], "largest_share": r7["largest_share"]}}
    if g8 is None:
        g["G8"] = {"pass": None, "value": "not run", "not_run": True}
    else:
        g["G8"] = {"pass": bool(g8.get("code") is None and g8["sharpe"] > 0),
                   "value": {"next30_sharpe": g8.get("sharpe"), "code": g8.get("code")}}
    r10 = PL.g10_rule(m["direction_changes_val"])
    g["G10"] = {"pass": r10["pass"], "value": r10["value"]}
    decided = [v["pass"] for v in g.values() if v["pass"] is not None]
    tier1 = all(decided) and g["G6"]["pass"] is not None and g["G8"]["pass"] is not None
    k = inplay.sum(axis=1, keepdims=True)
    Wb = np.where(inplay, 1.0 / np.where(k > 0, k, 1), 0.0)             # benchmark: equal-weight long in play
    bdaily = mk.run(Wb, dev_s, val_e).daily_returns()
    bdev, bval = PL.split_daily(bdaily)
    info = {"benchmark": "equal-weight long of the in-play top30 members", "benchmark_val_sharpe": S.sharpe(bval),
            "benchmark_val_max_drawdown": S.max_drawdown(bval), "benchmark_dev_sharpe": S.sharpe(bdev)}
    info.update({f"vs_benchmark_{kk}": v for kk, v in S.beta_alpha(val.to_numpy(), bval.reindex(val.index).to_numpy()).items()})
    res = {"status": "evaluated", "metrics": m, "gates": g, "tier": "tier1" if tier1 else "none", "info": info,
           "daily_returns": daily, "n_params": n_params}
    if opts.keep_detail:
        fin = shifted[np.isfinite(shifted)]
        afin = a_sh[np.isfinite(a_sh)]
        res["detail"] = {"permutation": {"actual_val_sharpe_restarted": actual, "n": int(len(offs)), "p": p,
                                         "paired": True, "ties": int(ties.sum()), "lagged": True,
                                         "lag_min": int(offs.min()), "lag_max": int(offs.max()),
                                         "actual_common_mean": float(np.mean(afin)) if len(afin) else None,
                                         "shifted_mean": float(np.mean(fin)) if len(fin) else None,
                                         "shifted_p95": float(np.percentile(fin, 95)) if len(fin) else None},
                         "per_year": PL.dev_only_years(S.per_year(daily)), "buckets": PL.dev_only_buckets(buckets),
                         "next30": g8, "stress": {"funding_stress_val_sharpe": fs_sh, "cost2x_val_sharpe": cs_sh}}
    return res


# ---------------------------------------------------------------- loading (disk)

def load_udata(upto: str, handle=None, symbols_table: dict | None = None, log=None, fields=None) -> UData:
    """Every crypto perpetual's klines (activity, under the ceiling), then the tables of the symbols that
    are ever members of top30 or next30 between UNIVERSE_START and the ceiling, restricted to the columns
    the program (`fields`, from program_fields; None = every field) and the engine read (R3)."""
    if upto not in ("dev_end", "val_end"):
        raise ValueError("load_udata: upto must be dev_end or val_end")

    def get(ds, s):                                    # every loader call names its ceiling literally
        if upto == "dev_end":
            return D.load_raw(ds, s, upto="dev_end", cache=False)
        return D.load_raw(ds, s, upto="val_end", handle=handle, cache=False)

    table = symbols_table or U.load_symbols()
    acts, until = {}, {}
    cols = needed_columns(set(L.FIELDS) | {"funding_mean"} if fields is None else set(fields))
    g0 = T(C.UNIVERSE_START) - pd.Timedelta(days=30)                    # as-of seeds before the grid are kept

    def tables(s):                                     # S4: loaded per symbol when a block needs it
        out = {}
        for d in ("klines", "funding", "mark_klines", "index_klines"):
            if not cols[d]:
                out[d] = pd.DataFrame({c: np.zeros(0) for c in ("open", "high", "low", "close")},
                                      index=pd.DatetimeIndex([], tz="UTC").as_unit("ns"))
                continue
            t = get(d, s)
            out[d] = t.loc[t.index >= g0, cols[d]] if d != "funding" else t[cols[d]]
        return out
    for s in U.crypto_symbols(table):                  # pass 1: activity only (one table in memory at a time)
        try:
            kl = get("klines", s)
        except FileNotFoundError:
            continue
        until[s] = table["symbols"][s].get("until")
        a = U.activity_of(kl, until[s])
        if len(a.active):
            acts[s] = a
        del kl
    end = T(C.DEV_END if upto == "dev_end" else C.VAL_END)
    ud = UData(acts=acts, raw={}, btc=None, end=end, until=until, loader=tables)
    g = ud.grid()
    mem = ud.membership(int(g[0].value), int(g[-1].value))
    ud.loadable = frozenset(set(mem.ever("top30")) | set(mem.ever("next30")))
    if upto == "dev_end":
        ud.btc = D.load_frame(C.BTC, D.PROGRAM_EXTRA, upto="dev_end")
    else:
        ud.btc = D.load_frame(C.BTC, D.PROGRAM_EXTRA, upto="val_end", handle=handle)
    if log:
        log(f"universe data ({upto}): {len(acts)} crypto perpetuals with bars, {len(ud.loadable)} ever in top30/next30")
    return ud


def udata_from_tables(tables: dict, btc_frame: pd.DataFrame, end: str, until: dict | None = None,
                      symbols_table: dict | None = None) -> UData:
    """Tests and calibration: UData from in-memory tables {symbol: {klines, funding, mark_klines,
    index_klines}} cut at `end`; every symbol's full tables are kept. With a symbol table, only its
    crypto perpetuals are candidates (as load_udata)."""
    cap = T(end)
    acts, raw = {}, {}
    until = dict(until or {})
    if symbols_table is not None:
        crypto = set(U.crypto_symbols(symbols_table))
        tables = {s: t for s, t in tables.items() if s in crypto}
        until.update({s: symbols_table["symbols"][s].get("until") for s in tables})
    for s, t in tables.items():
        kl = t["klines"][t["klines"].index <= cap]
        a = U.activity_of(kl, until.get(s))
        if len(a.active):
            acts[s] = a
            raw[s] = {"klines": kl, **{d: t[d][D.get(d).visible_from(t[d]) <= cap] for d in ("funding", "mark_klines",
                                                                                         "index_klines")}}
    return UData(acts=acts, raw=raw, btc=btc_frame[btc_frame.index <= cap], end=cap, until=dict(until))
