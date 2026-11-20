"""Universe calibration (unit top30, KP-015):

    python -m omr.ucalibrate [--worlds 200] [--oracle-worlds 100] [--workers 4] [--restart] [--force]
    python -m omr.ucalibrate --unlocked-dry-run --out FILE      (fully synthetic universe; never sealable)

The core calibration (omr.calibrate) is unchanged. The seal (omr.kernel_lock seal) applies decide_both,
PER UNIT (fix pass 6, R-H): each unit's G6 threshold is the LARGEST of G6_GRID whose null pass rate is <=
NULL_PASS_MAX under both of THAT unit's nulls, with oracle power at true Sharpe 1.5 >= POWER_MIN for both
speeds under both of its nulls at THAT threshold (each unit's oracle levels as present in its artifact: the
core 1.0 and 1.5, top30 1.5 only). Both units seal or neither; kernel.lock holds {"core": x, "top30": y}.

WORLDS ON THE REAL MEMBERSHIP CALENDAR (fix pass 4, U2). PANEL: every symbol ever a top30 member from
UNIVERSE_START to VAL end (the kernel's own rule on the real bars, read with the logged calibration
handle). Every symbol keeps its REAL rows: which hours are present or absent, trades, volume, quote volume
and taker volumes exactly as recorded, so the kernel's own membership rule reproduces the real monthly
schedule, usable flags and unit sizes in every world (removing symbols never ranked 1 to 30 cannot change
ranks 1 to 30). Only PRICES are resampled: open-relative ratios (open / previous close, high / open,
low / open, close / open) cumulated from the symbol's real first open over its own present rows; a present
zero-trade bar is flat; an absent bar stays absent. These worlds keep the real calendar while prices are
resampled, so they cannot show an effect that needs membership to follow price; the causal (lag) form of
G6 is what excludes such an effect.
NULL A (bootstrap): every world day draws one source day iid, shared by all symbols. R-F: a day of calendar
  month m draws from POOL(m), the source days (UNIVERSE_START to VAL end) on which EVERY top30 member of m
  (the kernel's own rule on the source) has 24 active hours, so on every world day of a pooled month all
  members share one source day; a month with no unit or a pool under POOL_MIN_DAYS (90) draws from the whole
  period. A symbol uses its own bars of the source day when all 24 of its hours are active there, otherwise
  a personal fallback day drawn iid from its own fully active days by a per-(world, symbol) generator
  (mostly non-members). Funding keeps the settlement times and intervals of the real day and takes the rates of the
  source day used for that symbol, in order (cycled if the counts differ; a source day without a
  settlement is replaced by a day with one, drawn by the same generator).
NULL B (sign-flip): the real order; per day ONE fair coin shared by all symbols mirrors each symbol's
  demeaned hourly log-return path; funding rates as recorded.
FUNDING SIGN (R-E, both nulls): every settlement's rate is then multiplied by a fair coin drawn per
  settlement HOUR of the world (its own generator of the world seed), the same coin for every symbol that
  settles in that hour, so no funding payment can be predicted from earlier funding and a carry strategy
  earns nothing; sizes, intervals, times and the cross-section up to the shared sign are kept. The core
  calibration is unchanged; its carry effect was small (core carry family mean VAL Sharpe -0.30 under null
  A, +0.07 under null B; Tier-1 passes under null B 0, 1 and 3 of 300 at the three thresholds), while a
  cross-sectional carry over thirty coins could earn far more.
Mark and index bars of the null worlds are the synthetic last-price bars of the present rows (no universe
family reads them; the liquidation check then uses last-price wicks, wider than mark wicks: conservative).

Families: three hash-locked cross-sectional programs (omr/programs/ucal_*.omr): momentum and reversal on
daily returns (n from 3 to 60 and from 3 to 20 days; the reversal is the momentum's mirror since fix pass 6, R-J),
and funding carry. Protocol per (world, family): 20 parameter draws, SCREENED by the DEV signals and
the activity rule; the activity passer with the best DEV Sharpe gets the full stage 1 and is SUBMITTED to
stage 2 (G8 not run: it can only veto, so null pass rates are upper bounds). Everything runs on the
PRODUCTION block path (six-month blocks); G6 is the paired lag test of omr.upipeline.ugates.
NOISY ORACLE (cross-sectional, on the same worlds): per symbol x = rho * z + sqrt(1 - rho^2) * eps, z = the
symbol's future k-day log return minus the cross-sectional mean of the symbols with a return, standardised
per symbol; weights = (x - mean x) / sum |x - mean x| over the in-play symbols, re-decided every k days
(decided at the 23:00 bar, executed at the next 00:00 open). Speeds USPEEDS (fix pass 6, R-I): fast = 5 days
(UNIVERSE_FAST_DAYS, confirmed), slow = 20 days; the core's 1-day speed is not attainable in this unit (at 12.5
bps per side its cost drag of 3.86 Sharpe units makes G4 at doubled costs fail for every book with net Sharpe
1.5; at 5 days the drag is 0.93). rho tuned on the power worlds for the level the rule reads (true Sharpe 1.5,
ULEVELS).
RUN: the source arrays are built once and shared with the workers (multiprocessing shared memory); each
world builds a symbol's tables only when a block needs them. Every finished task is appended and fsynced
to a partial file whose header binds the kernel, the data and the protocol, each line with the sha256 of its
content (a damaged or torn line is discarded and its task runs again; a task stored twice with different
results stops the run); a restart with the same header skips the finished tasks (the artifact is the same,
apart from created_at and wall_seconds), another header is refused unless --restart. A memory preflight
refuses to start when the workers do not fit (--force). The oracle phases run first (fix pass 6); their power
is logged, and if the power at the largest threshold is below POWER_MIN (or a level misses its bound) a
prominent line says the seal rule will STOP whatever the null worlds give.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import multiprocessing as mp
import os
import time
from multiprocessing import shared_memory
from pathlib import Path

import numpy as np
import pandas as pd

from omr import access
from omr import calibrate as CB
from omr import constants as C
from omr import data
from omr import datasets as D
from omr import kernel_lock
from omr import lang as L
from omr import ledger
from omr import paths as P
from omr import pipeline as PL
from omr import stats as S
from omr import universe as U
from omr import upipeline as UP

PROTOCOL_VERSION = 4                        # fix pass 6: per-unit seal rule (R-H), partial lines with a sha (F3),
                                            # oracle phases before the null worlds (F6); 3 = pass 5
FAMILIES = ("ucal_xs_momentum", "ucal_xs_reversal", "ucal_xs_carry")
SEEDS = {"A": 11000, "B": 14000, "oracle_A": 17000, "oracle_B": 18000}
OPTS = PL.Opts(include_g8=False, keep_detail=False)
ULEVELS = (1.5,)                            # D3: the rule reads power at true Sharpe 1.5 only
# F8 (R-I): the universe oracle's speeds in DAYS (the names are the core's, so calibrate.decide reads them). The fast
# speed is CONFIRMED at 5 days (the coordinator's rule, fixed before the audit sweep: the fastest of 5 / 7 / 10 days
# with Tier-1 >= 0.65 at all three thresholds): at 12.5 bps per side the cost drag is 3.86 Sharpe units at 1 day
# (Tier-1 0 of 24, G4 fails) and 0.93 at 5 days (Tier-1 18 of 24). Change it here only.
UNIVERSE_FAST_DAYS = 5
USPEEDS = {"fast": UNIVERSE_FAST_DAYS, "slow": 20}
RHO_GRID = CB.RHO_GRID                      # coarse oracle curve (as the core calibration)
FINE_POINTS = 41                            # fine curve points inside the bracket
WORKER_PEAK_BYTES = int(1.6 * 2 ** 30)      # D2: measured peak private bytes of one worker (fix pass 5, M1)
EXIT_MEMORY, EXIT_PARTIAL = 4, 5
HOUR_NS = U.HOUR_NS
DAY_NS = U.DAY_NS
OTHER = ["volume", "quote_volume", "trades", "taker_buy_volume", "taker_buy_quote_volume"]
POOL_MIN_DAYS = 90                          # R-F: a smaller monthly pool uses the whole-period pool
KEEP_BEFORE_DAYS = 30                       # world rows kept before UNIVERSE_START (as-of seeds, as load_udata)


def T(s) -> pd.Timestamp:
    return pd.Timestamp(s, tz="UTC").as_unit("ns")


def family_path(name: str) -> Path:
    if name not in FAMILIES:
        raise ValueError(f"unknown universe calibration family {name!r}: only {FAMILIES}")
    return P.PROGRAMS_DIR / f"{name}.omr"


# ---------------------------------------------------------------- source (the real panel)

def panel_symbols(acts: dict) -> list:
    """Every symbol ever a top30 member between UNIVERSE_START and VAL end (the kernel's own rule)."""
    mem = U.membership(acts, list(acts), T(C.UNIVERSE_START).value, T(C.VAL_END).value)
    return mem.ever("top30")


_ROW_F = ("g", "hr", "lr", "cr") + tuple(OTHER)
_ROW_B = ("gap", "act")
_ACT = ("a_active", "a_qv", "a_usable")
_FUND = ("f_ns", "f_iv", "f_rate", "f_offms")
_DAY = ("full", "fd_off")


class USource:
    """The panel's real rows as concatenated arrays (shareable): per row the price ratios, the volume
    columns, gap and active flags; per symbol its Activity (as omr.universe.activity_of on the real table),
    its funding settlements and, per local day, whether all 24 hours are active and the day's settlements."""

    def __init__(self, meta: dict, arr: dict):
        self.meta, self.arr = meta, arr
        self.symbols = [m["name"] for m in meta["symbols"]]
        self.k = {s: i for i, s in enumerate(self.symbols)}
        self.D0, self.ND = int(meta["D0"]), int(meta["ND"])
        self.until = {m["name"]: m["until"] for m in meta["symbols"]}

    @classmethod
    def build(cls, symbols, get_tables, until: dict | None = None, btc_symbol: str | None = None) -> "USource":
        """get_tables(symbol) -> {"klines", "funding"} (one symbol in memory at a time)."""
        until = dict(until or {})
        cap = T(C.VAL_END)
        parts = {n: [] for n in _ROW_F + _ROW_B + _ACT + _FUND + _DAY}
        metas, off, aoff, foff, doff, full_off = [], 0, 0, 0, 0, 0
        for s in sorted(symbols):
            t = get_tables(s)
            kl = t["klines"][t["klines"].index <= cap]
            fu = t["funding"]
            fu = fu[D.get("funding").visible_from(fu) <= cap]
            ns = data.ns_int(kl.index)
            n = len(ns)
            gap = kl["is_gap"].to_numpy(dtype=bool)
            tr = kl["trades"].to_numpy(dtype=np.float64)
            act = (~gap) & np.isfinite(tr) & (tr > 0)
            o, h, lo, c = (kl[x].to_numpy(dtype=np.float64) for x in ("open", "high", "low", "close"))
            pc = np.r_[np.nan, c[:-1]]
            with np.errstate(divide="ignore", invalid="ignore"):
                g = np.where(act, o / pc, 1.0)
                g[0] = 1.0
                hr, lr, cr = np.where(act, h / o, 1.0), np.where(act, lo / o, 1.0), np.where(act, c / o, 1.0)
                lrt = np.log(g * cr)
            ok = act & np.isfinite(lrt)
            ok[0] = False
            fv = data.ns_int(D.get("funding").visible_from(fu))
            order = np.argsort(fv, kind="mergesort")
            fv = fv[order]
            day_r = ns // DAY_NS
            sd0 = int(min(day_r[0], fv[0] // DAY_NS if len(fv) else day_r[0]))
            sd1 = int(max(day_r[-1], fv[-1] // DAY_NS if len(fv) else day_r[-1]))
            nd = sd1 - sd0 + 1
            full = np.bincount(day_r[act] - sd0, minlength=nd)[:nd] == 24
            fd_off = np.searchsorted(fv // DAY_NS - sd0, np.arange(nd + 1), side="left").astype(np.int64)
            a = U.activity_of(kl, until.get(s))
            for name, v in zip(_ROW_F, (g, hr, lr, cr) + tuple(kl[x].to_numpy(dtype=np.float64) for x in OTHER)):
                parts[name].append(v)
            parts["gap"].append(gap)
            parts["act"].append(act)
            parts["a_active"].append(a.active)
            parts["a_qv"].append(a.qv)
            parts["a_usable"].append(a.usable)
            parts["f_ns"].append(fv)
            for name, col in (("f_iv", "interval_hours"), ("f_rate", "rate"), ("f_offms", "offset_ms")):
                parts[name].append(fu[col].to_numpy(dtype=np.float64)[order])
            parts["full"].append(full)
            parts["fd_off"].append(fd_off)
            metas.append({"name": s, "start": int(ns[0]), "n": n, "off": off, "first_open": float(o[0]),
                          "m": float(np.mean(lrt[ok])) if ok.any() else 0.0, "sd0": sd0, "nd": nd, "doff": doff,
                          "full_off": full_off, "f_off": foff, "f_n": int(len(fv)), "a_start": int(a.start),
                          "a_n": int(len(a.active)), "a_off": aoff, "until": until.get(s)})
            off, aoff, foff = off + n, aoff + len(a.active), foff + len(fv)
            doff, full_off = doff + nd + 1, full_off + nd
            del t, kl, fu
        D0 = min(m["sd0"] for m in metas)
        ND = int(T(C.VAL_END).value // DAY_NS) - D0 + 1
        arr = {k: np.concatenate(v) if v else np.zeros(0) for k, v in parts.items()}
        names = [m["name"] for m in metas]
        btc = btc_symbol if btc_symbol in names else (C.BTC if C.BTC in names else names[0])
        meta = {"symbols": metas, "D0": D0, "ND": ND, "pool_lo": int(T(C.UNIVERSE_START).value // DAY_NS) - D0,
                "btc": btc}
        src = cls(meta, arr)
        src._build_pools()
        return src

    def _build_pools(self) -> None:
        """R-F: per calendar month m of the world, POOL(m) = the source days (UNIVERSE_START .. VAL end) on which
        EVERY top30 member of month m (the kernel's own rule on the source, the schedule every world
        reproduces) has 24 active hours. A month with no unit or a pool under POOL_MIN_DAYS uses the
        whole-period pool. Arrays: day_pool (per global day: pool id or -1), pool_days, pool_off."""
        ND, D0, lo = self.ND, self.D0, self.meta["pool_lo"]
        full_g = {}
        for s in self.symbols:
            m = self.sym(s)
            g = np.zeros(ND, dtype=bool)
            shift = m["sd0"] - D0
            fl = np.asarray(self.arr["full"][m["full_off"]:m["full_off"] + m["nd"]], dtype=bool)
            n = min(len(fl), ND - shift)
            g[shift:shift + n] = fl[:n]
            full_g[s] = g
        acts = self.acts(T(C.VAL_END).value)
        mem = U.membership(acts, list(acts), T(C.UNIVERSE_START).value, T(C.VAL_END).value)
        pools, sizes, pool_of = [], [], np.full(len(mem.months), -1, dtype=np.int64)
        for i in range(len(mem.months)):
            if not mem.unit_exists("top30", i):
                continue
            ok = np.ones(ND, dtype=bool)
            ok[:lo] = False
            for s in mem.members("top30", i):
                ok &= full_g[s]
            days = np.nonzero(ok)[0]
            if len(days) >= POOL_MIN_DAYS:
                pool_of[i] = len(pools)
                pools.append(days)
                sizes.append(len(days))
        day_ns = (D0 + np.arange(ND, dtype=np.int64)) * DAY_NS
        mi = np.searchsorted(mem.months, day_ns, side="right") - 1
        day_pool = np.where(mi >= 0, pool_of[np.clip(mi, 0, max(len(mem.months) - 1, 0))], -1) if len(mem.months) \
            else np.full(ND, -1, dtype=np.int64)
        self.arr["day_pool"] = np.asarray(day_pool, dtype=np.int64)
        self.arr["pool_days"] = np.concatenate(pools).astype(np.int64) if pools else np.zeros(0, dtype=np.int64)
        self.arr["pool_off"] = np.r_[0, np.cumsum(sizes)].astype(np.int64)
        months = pd.DatetimeIndex(pd.to_datetime(day_ns, unit="ns", utc=True)).strftime("%Y-%m")
        whole = sorted(set(months[day_pool < 0]))
        self.meta["pools"] = {"min_pool_days": POOL_MIN_DAYS, "pooled_months": int(len(set(months[day_pool >= 0]))),
                              "months_whole_period_pool": int(len(whole)),
                              "smallest_pool_days": int(min(sizes)) if sizes else None,
                              "median_pool_days": float(np.median(sizes)) if sizes else None}

    # ---- sharing with the workers
    def to_shared(self) -> tuple:
        """(spec, blocks): the arrays copied into shared-memory blocks; the caller keeps `blocks` open while
        workers run and closes / unlinks them afterwards."""
        spec, blocks = {"meta": self.meta, "arrays": {}}, []
        for k, v in self.arr.items():
            v = np.ascontiguousarray(v)
            shm = shared_memory.SharedMemory(create=True, size=max(1, v.nbytes))
            np.ndarray(v.shape, dtype=v.dtype, buffer=shm.buf)[...] = v
            spec["arrays"][k] = (shm.name, v.shape, v.dtype.str)
            blocks.append(shm)
        return spec, blocks

    @classmethod
    def from_shared(cls, spec) -> tuple:
        arr, blocks = {}, []
        for k, (name, shape, dtype) in spec["arrays"].items():
            shm = shared_memory.SharedMemory(name=name)
            a = np.ndarray(tuple(shape), dtype=np.dtype(dtype), buffer=shm.buf)
            a.flags.writeable = False
            arr[k], blocks = a, blocks + [shm]
        return cls(spec["meta"], arr), blocks

    # ---- per symbol
    def sym(self, s: str) -> dict:
        return self.meta["symbols"][self.k[s]]

    def rows(self, s: str, name: str) -> np.ndarray:
        m = self.sym(s)
        return self.arr[name][m["off"]:m["off"] + m["n"]]

    def activity(self, s: str, cap_ns: int) -> U.Activity:
        """The symbol's real Activity cut at cap (a prefix: usable_of looks backwards only)."""
        m = self.sym(s)
        n = m["a_n"] if m["a_n"] == 0 else max(0, min(m["a_n"], (cap_ns - m["a_start"]) // HOUR_NS + 1))
        sl = slice(m["a_off"], m["a_off"] + n)
        return U.Activity(m["a_start"] if n else 0, self.arr["a_active"][sl], self.arr["a_qv"][sl],
                          self.arr["a_usable"][sl])

    def acts(self, cap_ns: int) -> dict:
        out = {}
        for s in self.symbols:
            a = self.activity(s, cap_ns)
            if len(a.active):
                out[s] = a
        return out


# ---------------------------------------------------------------- null worlds

class UWorld:
    """The draws of one null world (shared by all symbols); a symbol's tables are built on demand."""

    def __init__(self, src: USource, null: str, seed: int):
        if null not in ("A", "B"):
            raise ValueError(null)
        self.src, self.null, self.seed = src, null, int(seed)
        rng = np.random.default_rng([seed, 21 if null == "A" else 22])
        ND = src.ND
        if null == "A":
            # R-F: a pooled month's days draw from POOL(m) (every member fully active), others from the whole period
            u = rng.random(ND)
            lo = src.meta["pool_lo"]
            self.pick = lo + np.minimum((u * (ND - lo)).astype(np.int64), ND - lo - 1)
            dp = np.asarray(src.arr["day_pool"], dtype=np.int64)
            pooled = dp >= 0
            if pooled.any():
                off = np.asarray(src.arr["pool_off"], dtype=np.int64)
                size = off[dp[pooled] + 1] - off[dp[pooled]]
                at = off[dp[pooled]] + np.minimum((u[pooled] * size).astype(np.int64), size - 1)
                self.pick[pooled] = np.asarray(src.arr["pool_days"], dtype=np.int64)[at]
            self.flip = np.zeros(ND, dtype=bool)
        else:
            self.pick = np.arange(ND)
            self.flip = rng.uniform(size=ND) < 0.5
        # R-E: one fair funding sign per hour of the world (its own generator), shared by every symbol that
        # settles in that hour, independent between hours
        self.fsign = np.where(np.random.default_rng([seed, 31]).integers(0, 2, ND * 24) == 1, 1.0, -1.0)
        self._cache = {}

    def _source_days(self, s: str) -> tuple:
        src, m = self.src, self.src.sym(s)
        shift = m["sd0"] - src.D0
        gd = np.arange(m["nd"]) + shift
        if self.null == "B":
            return gd, None
        full = src.arr["full"][m["full_off"]:m["full_off"] + m["nd"]]
        p = self.pick[gd]
        lp = p - shift
        inside = (lp >= 0) & (lp < m["nd"])
        ok = inside & full[np.clip(lp, 0, m["nd"] - 1)]
        fulld = np.nonzero(full)[0] + shift
        if len(fulld) == 0:                                        # no fully active day: its own days
            return gd, None
        rs = np.random.default_rng([self.seed, 21, self.src.k[s]])
        fb = fulld[rs.integers(0, len(fulld), m["nd"])]
        return np.where(ok, p, fb), ok

    def source_days(self, s: str) -> np.ndarray:
        """Per local day of the symbol: the GLOBAL source day it uses (null A: the world's draw if all 24 of
        the symbol's hours are active there, else its personal fallback; null B: the day itself)."""
        return self._source_days(s)[0]

    def source_day_stats(self) -> dict:
        """D6: over the days on which each panel symbol has an active bar, how many use the world's shared
        source day, a personal fallback day, or the symbol's own day (no fully active day at all); a
        deterministic number per world (null A)."""
        out = {"shared": 0, "fallback": 0, "own": 0}
        for s in self.src.symbols:
            m = self.src.sym(s)
            act = self.src.rows(s, "act")
            tns = m["start"] + HOUR_NS * np.nonzero(act)[0]
            days = np.unique(tns // DAY_NS - m["sd0"])
            sd, ok = self._source_days(s)
            if ok is None:
                out["own"] += len(days)
                continue
            out["shared"] += int(ok[days].sum())
            out["fallback"] += int((~ok[days]).sum())
        return out

    def tables(self, s: str, cap_ns: int | None = None, trim: bool = True) -> dict:
        key = (s, cap_ns, trim)
        if key in self._cache:
            return self._cache[key]
        out = self._build(s, cap_ns, trim)
        if len(self._cache) >= 6:
            self._cache.pop(next(iter(self._cache)))
        self._cache[key] = out
        return out

    def _build(self, s: str, cap_ns, trim: bool) -> dict:
        src, m = self.src, self.src.sym(s)
        n, start = m["n"], m["start"]
        g, hr, lr, cr = (src.rows(s, x) for x in ("g", "hr", "lr", "cr"))
        gap, act = src.rows(s, "gap"), src.rows(s, "act")
        r = np.arange(n, dtype=np.int64)
        tns = start + HOUR_NS * r
        ld = tns // DAY_NS - m["sd0"]
        hour = (tns // HOUR_NS) % 24
        sd = self.source_days(s)
        shift = m["sd0"] - src.D0
        if self.null == "A":
            ai = np.nonzero(act)[0]
            sr = ((sd[ld[ai]] + src.D0) * DAY_NS + hour[ai] * HOUR_NS - start) // HOUR_NS
            G, HR, LR, CR = (np.ones(n) for _ in range(4))
            G[ai], HR[ai], LR[ai], CR[ai] = g[sr], hr[sr], lr[sr], cr[sr]
        else:
            F = self.flip[ld + shift] & act
            G = np.where(F, np.exp(2.0 * m["m"]) / g, g)
            HR, LR = np.where(F, 1.0 / lr, hr), np.where(F, 1.0 / hr, lr)
            CR = np.where(F, 1.0 / cr, cr)
        G = np.where(act, G, 1.0)
        G[0] = 1.0                                                  # cumulated from the real first open
        HR, LR, CR = np.where(act, HR, 1.0), np.where(act, LR, 1.0), np.where(act, CR, 1.0)
        c = m["first_open"] * np.cumprod(G * CR)
        o = np.r_[m["first_open"], c[:-1]] * G
        idx = pd.DatetimeIndex(pd.to_datetime(tns, unit="ns", utc=True)).as_unit("ns")
        idx.name = "open_time"
        kl = pd.DataFrame({"open": o, "high": o * HR, "low": o * LR, "close": c}, index=idx)
        for x in OTHER:
            kl[x] = src.rows(s, x)
        kl["is_gap"] = np.asarray(gap, dtype=bool)
        mark = kl.loc[~kl["is_gap"].to_numpy(), ["open", "high", "low", "close"]].copy()
        mark["samples"] = 3600.0
        fu = self._funding(s, sd)
        keep_lo = T(C.UNIVERSE_START).value - KEEP_BEFORE_DAYS * DAY_NS if trim else None
        if keep_lo is not None or cap_ns is not None:
            lo = keep_lo if keep_lo is not None else -(2 ** 62)
            hi = cap_ns if cap_ns is not None else 2 ** 62
            kl = kl[(kl.index.asi8 >= lo) & (kl.index.asi8 <= hi)]
            mark = mark[(mark.index.asi8 >= lo) & (mark.index.asi8 <= hi)]
            fu = fu[fu.index.asi8 <= hi]
        return {"klines": kl, "funding": fu, "mark_klines": mark, "index_klines": mark}

    def _funding(self, s: str, sd: np.ndarray, signs: bool = True) -> pd.DataFrame:
        """The symbol's funding table: the real settlement times and intervals; null A: the rates of the source
        day used for the symbol, in order (cycled); null B: the real rates. R-E: every rate times the world's
        sign coin of its settlement hour (signs=False: without the coin, for the tests)."""
        src, m = self.src, self.src.sym(s)
        fsl = slice(m["f_off"], m["f_off"] + m["f_n"])
        fns, iv, rate, offms = (src.arr[x][fsl] for x in _FUND)
        if self.null == "A" and len(fns):
            doff = m["doff"]
            fd = np.asarray(src.arr["fd_off"][doff:doff + m["nd"] + 1], dtype=np.int64)
            cnt = fd[1:] - fd[:-1]
            ld = fns // DAY_NS - m["sd0"]
            kk = np.arange(len(fns)) - fd[ld]                        # its place in its real day
            shift = m["sd0"] - src.D0
            sl = sd[ld] - shift                                     # the source day (local)
            sl_ok = (sl >= 0) & (sl < m["nd"])
            sl = np.clip(sl, 0, m["nd"] - 1)
            bad = ~sl_ok | (cnt[sl] == 0)
            if bad.any():
                have = np.nonzero(cnt > 0)[0]
                rs = np.random.default_rng([self.seed, 23, src.k[s]])
                alt = have[rs.integers(0, len(have), m["nd"])]
                sl = np.where(bad, alt[ld], sl)
            rate = rate[fd[sl] + kk % cnt[sl]]
        rate = np.asarray(rate, dtype=np.float64)
        if signs and len(fns):
            rate = rate * self.fsign[(np.asarray(fns) - src.D0 * DAY_NS) // HOUR_NS]
        idx = pd.DatetimeIndex(pd.to_datetime(np.asarray(fns), unit="ns", utc=True)).as_unit("ns")
        idx.name = "settle_time"
        return pd.DataFrame({"rate": np.asarray(rate, dtype=np.float64), "interval_hours": np.asarray(iv),
                             "offset_ms": np.asarray(offms)}, index=idx)


def world_udata(src: USource, null: str, seed: int, end: str = C.VAL_END, world: UWorld | None = None) -> UP.UData:
    """A null world as universe data: the real Activity of every panel symbol (so the kernel's own rule gives
    the real membership), price tables built per symbol when a block needs them."""
    w = world if world is not None else UWorld(src, null, seed)
    cap = T(end)
    ud = UP.UData(acts=src.acts(cap.value), raw={}, btc=None, end=cap, until=dict(src.until),
                  loader=lambda s: w.tables(s, cap.value))
    ud.loadable = frozenset(src.symbols)
    ud.btc = D.assemble_frame(w.tables(src.meta["btc"], cap.value, trim=False), D.PROGRAM_EXTRA)
    ud.world = w
    return ud


def build_uworld(src: USource, null: str, seed: int, end: str = C.VAL_END) -> UP.UData:
    return world_udata(src, null, seed, end)


def dev_view(src: USource, null: str, seed: int) -> UP.UData:
    """The same world under the DEV ceiling (identical rows up to DEV end; membership from DEV bars)."""
    return world_udata(src, null, seed, C.DEV_END)


# ---------------------------------------------------------------- oracle

class UOracle:
    def __init__(self, ud: UP.UData, k_days: int, eps_seed):
        self.bu = UP.Blocked(ud, "top30", fields=set())             # production blocks; engine columns only
        self.inplay = self.bu.inplay()
        self.dev_s, self.val_e = self.bu.pos(C.DEV_START), self.bu.pos(C.VAL_END)
        step = 24 * k_days
        self.starts = np.arange(self.dev_s, self.val_e, step)
        self.ends = np.minimum(self.starts + step, self.val_e)
        op = self.bu.eng_rows("open", 0, len(self.bu.ns) - 1)
        self.shape = op.shape
        with np.errstate(divide="ignore", invalid="ignore"):
            R = np.log(op[self.ends] / op[self.starts])
        fin = np.isfinite(R)
        cnt = fin.sum(axis=1, keepdims=True)
        R = np.where(fin, R, 0.0)
        R = np.where(fin, R - R.sum(axis=1, keepdims=True) / np.where(cnt > 0, cnt, 1), 0.0)
        n = fin.sum(axis=0)
        mu = R.sum(axis=0) / np.where(n > 0, n, 1)
        var = np.where(fin, (R - mu) ** 2, 0.0).sum(axis=0) / np.where(n > 1, n - 1, 1)
        sd = np.sqrt(var)
        self.z = np.where(fin & (sd > 0) & (n > 1), (R - mu) / np.where(sd > 0, sd, 1.0), 0.0)
        self.eps = np.random.default_rng(eps_seed).standard_normal(self.z.shape)
        self.rows = np.arange(self.starts[0] - 1, self.ends[-1] - 1)
        self.block = np.repeat(np.arange(len(self.starts)), self.ends - self.starts)

    def weights(self, rho: float) -> np.ndarray:
        x = rho * self.z + math.sqrt(max(0.0, 1.0 - rho * rho)) * self.eps
        W = np.zeros(self.shape)
        xb = x[self.block]
        P_ = self.inplay[self.rows]
        k = P_.sum(axis=1, keepdims=True)
        m = np.where(P_, xb, 0.0).sum(axis=1, keepdims=True) / np.where(k > 0, k, 1)
        d = np.where(P_, xb - m, 0.0)
        s = np.abs(d).sum(axis=1, keepdims=True)
        W[self.rows] = np.where(s > 0, d / np.where(s > 0, s, 1.0), 0.0)
        return W

    def val_sharpe(self, rho: float) -> float:
        return PL.val_sharpe_of(self.bu.run(self.weights(rho), self.dev_s, self.val_e))


# ---------------------------------------------------------------- the dry run's synthetic universe

def synthetic_churn_universe(seed: int = 9, n_sym: int = 100, early: int = 30, start: str = "2019-08-01 00:00",
                             end: str = C.VAL_END, scale_sd: float = 0.35, regime_half_life_days: float = 60.0,
                             regime_sd: float = 0.6) -> tuple:
    """(tables, symbols table): a FULLY synthetic universe with membership churn (no real bar is read):
    `early` symbols listed in the first 120 days, the rest staggered over 2020-2024; every symbol lives 700
    to 2200 days (then delisted: no further rows); hourly log return = market factor + per-symbol drift +
    noise; quote volume follows price (its close over its own 90-day mean close: a fading symbol falls in
    rank) times a mean-reverting per-symbol volume regime; funding every 8 hours. Membership comes from the
    kernel's own rule."""
    from scipy.signal import lfilter
    phi = math.exp(-math.log(2.0) / (24.0 * regime_half_life_days))
    rng = np.random.default_rng(seed)
    t0, tend = T(start), T(end)
    grid = pd.date_range(t0, tend, freq="h").as_unit("ns")
    H = pd.Timedelta(hours=1)
    mkt = 0.006 * rng.standard_normal(len(grid))
    tables, table = {}, {"symbols": {}}
    for i in range(n_sym):
        if i < early:
            lst = t0 + pd.Timedelta(days=int(rng.integers(0, 120)))
        else:
            lst = T("2020-01-01 00:00") + pd.Timedelta(days=int(rng.integers(0, 365 * 4 + 300)))
        last = min(lst + pd.Timedelta(days=int(rng.integers(700, 2200))), tend)
        i0, i1 = int((lst - t0) / H), int((last - t0) / H) + 1
        if i1 - i0 < 48:
            i0 = max(0, i1 - 48)
        n = i1 - i0
        lr = mkt[i0:i1] + 0.00008 * rng.standard_normal() + 0.008 * rng.standard_normal(n)
        p0 = float(np.exp(rng.normal(2.0, 1.5)))
        close = p0 * np.exp(np.cumsum(lr))
        opn = np.r_[p0, close[:-1]]
        spr = np.abs(0.004 * rng.standard_normal(n)) * close
        idx = grid[i0:i1]
        regime = lfilter([1.0], [1.0, -phi], regime_sd * math.sqrt(1.0 - phi * phi) * rng.standard_normal(n))
        rel = close / pd.Series(close).rolling(24 * 90, min_periods=1).mean().to_numpy()
        qv = float(np.exp(rng.normal(0.0, scale_sd))) * 1e4 * rel * np.exp(regime + 0.3 * rng.standard_normal(n))
        kl = pd.DataFrame({"open": opn, "high": np.maximum(opn, close) + spr, "low": np.minimum(opn, close) - spr,
                           "close": close, "volume": qv / close, "quote_volume": qv,
                           "trades": rng.integers(10, 100, n).astype(float), "taker_buy_volume": 0.5 * qv / close,
                           "taker_buy_quote_volume": 0.5 * qv, "is_gap": np.zeros(n, dtype=bool)}, index=idx)
        kl.index.name = "open_time"
        mk = kl[["open", "high", "low", "close"]].copy()
        mk["samples"] = 3600.0
        mk.index.name = "open_time"
        ft = idx[idx.hour % 8 == 0]
        fu = pd.DataFrame({"rate": 0.0001 + 0.0001 * rng.standard_normal(len(ft)), "interval_hours": 8.0,
                           "offset_ms": 0.0}, index=ft)
        fu.index.name = "settle_time"
        s = f"W{i:03d}USDT"
        tables[s] = {"klines": kl, "funding": fu, "mark_klines": mk, "index_klines": mk.copy()}
        table["symbols"][s] = {"class": "crypto_perpetual", "until": None, "n_months": 1}
    return tables, table


DRY_RUN_SYMBOLS = 170                        # about 140 ever in top30 (UNIVERSE_START to VAL end)


def synthetic_source(seed: int = 9, n_sym: int = DRY_RUN_SYMBOLS) -> USource:
    tables, _ = synthetic_churn_universe(seed=seed, n_sym=n_sym)
    acts = {s: U.activity_of(t["klines"]) for s, t in tables.items()}
    panel = panel_symbols({s: a for s, a in acts.items() if len(a.active)})
    return USource.build(panel, lambda s: tables[s])


def load_source(handle, log=print) -> USource:
    """The real panel, read with the logged calibration handle (one table in memory at a time)."""
    table = U.load_symbols()
    acts, until = {}, {}
    for s in U.crypto_symbols(table):
        try:
            kl = D.load_raw("klines", s, upto="val_end", handle=handle, cache=False)
        except FileNotFoundError:
            continue
        until[s] = table["symbols"][s].get("until")
        a = U.activity_of(kl, until[s])
        if len(a.active):
            acts[s] = a
        del kl
    panel = panel_symbols(acts)
    log(f"panel: {len(panel)} symbols ever in top30 ({C.UNIVERSE_START} .. {C.VAL_END})")

    def get(s):
        return {d: D.load_raw(d, s, upto="val_end", handle=handle, cache=False) for d in ("klines", "funding")}
    return USource.build(panel, get, until={s: until.get(s) for s in panel})


# ---------------------------------------------------------------- workers

_W = {}


def _init(families, handle, spec):
    _W["handle"] = handle
    _W["src"], _W["blocks"] = USource.from_shared(spec)
    _W["progs"] = {f: L.parse_file(family_path(f)) for f in families}


def dev_sharpe_u(fp_dev, W) -> float:
    run = fp_dev.run(W, fp_dev.pos(C.DEV_START), fp_dev.pos(C.DEV_END))
    return float("-inf") if run.liquidated else S.sharpe(run.daily_returns())


def task_null(args) -> list:
    null, world_seed = args
    src = _W["src"]
    ud = build_uworld(src, null, world_seed)
    udd = dev_view(src, null, world_seed)
    out = []
    for fam, prog in _W["progs"].items():
        fp_dev = UP.Blocked(udd, "top30", fields=UP.program_fields(prog))   # production blocks
        rng = np.random.default_rng(CB._seed("udraws", null, fam, world_seed))
        best, best_sh, codes = None, float("-inf"), {}
        for _ in range(CB.N_DRAWS):
            q = CB.draw_params(prog, rng)
            sc = UP.screen_dev_u(prog, q, fp_dev)
            if not sc["ok"]:
                codes[sc["code"]] = codes.get(sc["code"], 0) + 1
                continue
            codes["passed"] = codes.get("passed", 0) + 1
            sh = dev_sharpe_u(fp_dev, sc["W"])
            if best is None or sh > best_sh:
                best, best_sh = q, sh
        del fp_dev
        base = {"null": null, "family": fam, "world_seed": world_seed, "stage1": codes}
        if best is None:
            out.append(dict(base, submitted=False, status="not_submitted"))
            continue
        s1 = UP.stage1_u(prog, best, udd, np.random.default_rng(CB._seed("us1", null, fam, world_seed)), OPTS)
        if not s1["ok"]:
            out.append(dict(base, submitted=False, status=f"stage1_{s1['code']}", params=best, fault=s1.get("fault")))
            continue
        res = UP.stage2_u(prog, best, ud, s1, OPTS, _W["handle"], CB._seed("unull", null, fam, world_seed), None)
        out.append(CB.summarise(res, dict(base, submitted=True, params=best, best_dev_sharpe_of_passers=best_sh)))
    return out


def task_oracle_curve(args) -> list:
    null, world_seed, speed, rhos = args
    ob = UOracle(build_uworld(_W["src"], null, world_seed), USPEEDS[speed], CB._seed("ueps", null, world_seed, speed))
    return [ob.val_sharpe(float(r)) for r in rhos]


def task_oracle_power(args) -> list:
    null, world_seed, rhos = args
    ud = build_uworld(_W["src"], null, world_seed)
    out = []
    for speed in USPEEDS:
        ob = UOracle(ud, USPEEDS[speed], CB._seed("ueps", null, world_seed, speed))
        for lvl in ULEVELS:
            rho = rhos[f"{speed}|{lvl}"]
            res = UP.evaluate_weights_u(ob.weights(rho), ob.bu, CB._seed("uoracle", null, world_seed, speed, lvl), OPTS,
                                        _W["handle"], None)
            out.append(CB.summarise(res, {"null": null, "speed": speed, "level": lvl, "rho": rho,
                                          "world_seed": world_seed}))
        del ob
    return out


_TASKS = {"null": task_null, "curve": task_oracle_curve, "power": task_oracle_power}


def task_any(item) -> tuple:
    """(kind, args) -> (kind, args, result): one entry point, so finished tasks can be keyed and recorded."""
    kind, args = item
    return kind, args, _TASKS[kind](args)


def _plain(x):
    """A result as it is stored (JSON, cleaned), so a resumed run and an uninterrupted one see the same objects."""
    return json.loads(ledger.canonical(x))


def task_key(kind: str, args) -> str:
    return ledger.canonical([kind, args])


# ---------------------------------------------------------------- resume (D1)

class Partial:
    """Finished tasks of a calibration run, appended and fsynced one line each to a partial file whose first
    line is the header binding the run (kernel, data, protocol). A run with the same header skips the tasks
    already there and reuses their rows. F3: every record line carries "sha", the sha256 of the canonical JSON
    of {"key", "result"}; a line that does not parse or whose sha does not match is discarded (its task runs
    again) and counted; a file whose last line was torn gets a newline before the next append; a key stored
    twice with DIFFERENT results raises PartialMismatch (the same result twice is accepted)."""

    def __init__(self, path: Path, header: dict, restart: bool = False, log=print):
        self.path, self.header, self.done = Path(path), _plain(header), {}
        self.discarded = 0
        if self.path.exists() and restart:
            self.path.unlink()
        if self.path.exists():
            raw = self.path.read_bytes()
            lines = raw.decode("ascii", "replace").splitlines()
            try:
                old = json.loads(lines[0])["header"] if lines else None
            except (ValueError, KeyError, TypeError):
                old = None
            if old != self.header:
                raise PartialMismatch(f"{self.path} belongs to another run (its header differs: kernel, data or "
                                      "protocol). Remove it or pass --restart.")
            seen = {}
            for ln in lines[1:]:
                rec = self._parse(ln)
                if rec is None:                                   # torn or damaged: that task runs again
                    self.discarded += 1
                    continue
                k, body = rec
                if k in seen and seen[k] != body:
                    raise PartialMismatch(f"{self.path} holds task {k[:60]} twice with different results. Remove "
                                          "it or pass --restart.")
                seen[k] = body
                self.done[k] = json.loads(body)["result"]
            if raw and not raw.endswith(b"\n"):                  # a torn tail must not swallow the next record
                with open(self.path, "ab") as f:
                    f.write(b"\n")
                    f.flush()
                    os.fsync(f.fileno())
            log(f"resuming: {len(self.done)} finished tasks in {self.path.name}; {self.discarded} damaged lines "
                "discarded (their tasks run again)")
        else:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self._write({"header": self.header})

    @staticmethod
    def _body(key: str, result) -> str:
        return ledger.canonical({"key": key, "result": result})

    @classmethod
    def _parse(cls, ln: str):
        """(key, canonical body) of a sound record line, else None."""
        try:
            rec = json.loads(ln)
            key, result, sha = rec["key"], rec["result"], rec["sha"]
        except (ValueError, KeyError, TypeError):
            return None
        if not isinstance(key, str):
            return None
        body = cls._body(key, result)
        return (key, body) if ledger.sha256_text(body) == sha else None

    def _write(self, obj) -> None:
        with open(self.path, "a", encoding="ascii", newline="\n") as f:
            f.write(ledger.canonical(obj) + "\n")
            f.flush()
            os.fsync(f.fileno())

    def record(self, key: str, result) -> None:
        self.done[key] = _plain(result)
        self._write({"key": key, "result": result, "sha": ledger.sha256_text(self._body(key, result))})

    def remove(self) -> None:
        if self.path.exists():
            self.path.unlink()


class PartialMismatch(RuntimeError):
    pass


class _SerialPool:
    """workers = 0: the tasks run in this process (tests and small dry runs)."""

    def __init__(self, initializer, initargs):
        initializer(*initargs)

    def imap_unordered(self, fn, items):
        return (fn(x) for x in items)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def _hms(s: float) -> str:
    s = int(max(0, s))
    return f"{s // 3600}h{(s % 3600) // 60:02d}m"


def run_tasks(pool, partial: Partial, kind: str, arglist: list, log, label: str) -> list:
    """Results in the order of arglist; finished tasks are reused, new ones recorded as they finish, with
    progress lines (elapsed time and an estimate of the time left in this phase)."""
    keys = [task_key(kind, a) for a in arglist]
    todo = [(kind, a) for a, k in zip(arglist, keys) if k not in partial.done]
    t0, n_all, n_new = time.time(), len(arglist), 0
    step = max(1, len(todo) // 20)
    for _, args, res in pool.imap_unordered(task_any, todo):
        partial.record(task_key(kind, args), res)
        n_new += 1
        if n_new % step == 0 or n_new == len(todo):
            el = time.time() - t0
            left = el / n_new * (len(todo) - n_new)
            log(f"  {label}: {n_all - len(todo) + n_new}/{n_all} done ({n_all - len(todo)} resumed); "
                f"{_hms(el)} elapsed, about {_hms(left)} left in this phase")
    return [partial.done[k] for k in keys]


def tune_rho(pool, partial: Partial, null: str, speed: str, seeds: list, log) -> dict:
    """As omr.calibrate.tune_rho, with the universe oracle, for the levels the rule reads (ULEVELS)."""
    def means(rhos):
        res = run_tasks(pool, partial, "curve", [[null, s, speed, [float(r) for r in rhos]] for s in seeds], log,
                        f"oracle {null} {speed} curve ({len(rhos)} rhos)")
        mat = np.array(res, dtype=np.float64)
        return np.nanmean(np.where(np.isfinite(mat), mat, np.nan), axis=0)

    mean = means(RHO_GRID)
    out = {"mean_curve": {f"{r:.4f}": float(m) for r, m in zip(RHO_GRID, mean)}}
    fine = {}
    for lvl in ULEVELS:
        idx = np.nonzero(mean >= lvl)[0]
        if len(idx) == 0:
            lo, hi = float(RHO_GRID[-2]), float(RHO_GRID[-1])
        elif idx[0] == 0:
            lo, hi = float(RHO_GRID[0]), float(RHO_GRID[1])
        else:
            lo, hi = float(RHO_GRID[idx[0] - 1]), float(RHO_GRID[idx[0]])
        fine[lvl] = np.linspace(lo, hi, FINE_POINTS)
    fm = means(np.concatenate([fine[lv] for lv in ULEVELS]))
    F = FINE_POINTS
    picks = {lvl: float(fine[lvl][int(np.nanargmin(np.abs(fm[i * F:(i + 1) * F] - lvl)))])
             for i, lvl in enumerate(ULEVELS)}
    ach = means([picks[lv] for lv in ULEVELS])
    for i, lvl in enumerate(ULEVELS):
        out[str(lvl)] = {"rho": picks[lvl], "achieved_mean_val_sharpe": float(ach[i]),
                         "within_bound": bool(abs(float(ach[i]) - lvl) <= CB.RHO_BOUND)}
        log(f"    null {null} {speed:4s} level {lvl}: rho {picks[lvl]:.5f} -> achieved {float(ach[i]):.3f}")
    return out


# ---------------------------------------------------------------- the rule over both units

def _finite(x) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def oracle_summary(rows: list) -> dict:
    """As omr.calibrate.oracle_summary, for the levels PRESENT in the rows (D3: the universe artifact holds
    level 1.5 only; on the core artifact's rows it gives the core summary)."""
    levels = sorted({float(r["level"]) for r in rows})
    out = {}
    for speed in USPEEDS:
        for lvl in levels:
            rr = [r for r in rows if r["speed"] == speed and float(r["level"]) == lvl]
            fin = [r["val_sharpe"] for r in rr if r.get("status") == "evaluated" and _finite(r.get("val_sharpe"))]
            out[f"{speed}|{lvl}"] = {
                "n": len(rr), "mean_val_sharpe": float(np.mean(fin)) if fin else None,
                "not_evaluated": int(sum(1 for r in rr if r.get("status") != "evaluated")),
                "by_threshold": {str(t): {"power": (sum(CB.tier_at(r, t) for r in rr) / len(rr)) if rr else None,
                                          "tier1": int(sum(CB.tier_at(r, t) for r in rr)),
                                          "gate_pass_rate": CB.gate_rates(rr, t)} for t in C.G6_GRID}}
    return out


def verdict_from_rows(art: dict) -> dict:
    """The unit's own verdict recomputed from its stored rows (oracle levels as present)."""
    fams = list(art["families"])
    nulls = {n: {"summary": CB.null_summary(art["nulls"][n]["rows"], fams)} for n in ("A", "B")}
    oracle = {n: {"summary": oracle_summary(art["oracle"][n]["rows"])} for n in ("A", "B")}
    return CB.decide(nulls, oracle)


RULE_PER_UNIT = ("G6 threshold PER UNIT (core, top30), each from its own stored rows: the LARGEST of G6_GRID whose "
                 "null pass rate (Tier-1 passes / SUBMITTED pairs) is <= NULL_PASS_MAX under BOTH nulls of that unit; "
                 "then oracle power at true Sharpe 1.5 >= POWER_MIN for BOTH speeds under BOTH nulls of that unit at "
                 "that unit's threshold, every oracle level present in that unit's artifact achieved within "
                 "RHO_BOUND. Both units seal or neither: STOP if either unit has no qualifying threshold, power below "
                 "POWER_MIN or a level outside its bound")


def artifact_gaps(art: dict) -> list:
    """F2: what a unit artifact lacks for the rule (empty = complete): families, the null and oracle rows of
    both nulls, and oracle rows at true Sharpe 1.5 for every speed."""
    gaps = []
    if not isinstance(art.get("families"), dict) or not art["families"]:
        gaps.append("no families")
    for k in ("nulls", "oracle"):
        for n in ("A", "B"):
            rows = ((art.get(k) or {}).get(n) or {}).get("rows")
            if not isinstance(rows, list) or not rows:
                gaps.append(f"no {k} rows for null {n}")
    for n in ("A", "B"):
        rows = ((art.get("oracle") or {}).get(n) or {}).get("rows") or []
        for s in USPEEDS:
            if not any(isinstance(r, dict) and r.get("speed") == s and _finite(r.get("level")) and
                       float(r["level"]) == 1.5 for r in rows):
                gaps.append(f"no oracle rows at level 1.5 for null {n} speed {s}")
    return gaps


def unit_verdict(art: dict, unit: str) -> dict:
    """One unit's decision from its own stored rows (the unit rule: verdict_from_rows -> calibrate.decide), or
    STOP naming what the artifact lacks."""
    gaps = artifact_gaps(art)
    if gaps:
        return {"STOP": True, "chosen_threshold": None, "reason": f"{unit} artifact incomplete: " + "; ".join(gaps)}
    try:
        return verdict_from_rows(art)
    except (KeyError, TypeError, ValueError) as e:             # FP6-1: a malformed row stops, it does not raise
        return {"STOP": True, "chosen_threshold": None,
                "reason": f"{unit} artifact malformed: {type(e).__name__}: {e}"}


def decide_both(core_art: dict, uni_art: dict) -> dict:
    """The seal rule (applied by omr.kernel_lock seal to the stored rows), R-H: the G6 threshold is decided PER
    UNIT, each unit by its own rows (its oracle summary with the levels present in its artifact: core 1.0 and
    1.5, top30 1.5). Both units seal or neither."""
    v = {"core": unit_verdict(core_art, "core"), "top30": unit_verdict(uni_art, "top30")}
    out = {"rule": RULE_PER_UNIT, "per_unit": v,
           "chosen_threshold": {u: v[u].get("chosen_threshold") for u in v},
           "null_pass_rate": {u: v[u].get("null_pass_rate") for u in v},
           "power_at_1_5_chosen": {u: v[u].get("power_at_1_5_chosen") for u in v}}
    stops = [u for u in v if v[u].get("STOP") or v[u].get("chosen_threshold") is None]
    out["STOP"] = bool(stops)
    if stops:
        out["reason"] = "; ".join(f"{u}: {v[u].get('reason') or 'no qualifying threshold'}" for u in stops)
    return out


# ---------------------------------------------------------------- the run

def memory_preflight(workers: int, source_bytes: int) -> dict:
    """D2: available memory (the probe of upipeline.memory_check) against workers x WORKER_PEAK_BYTES plus the
    shared source."""
    avail = UP.available_memory_bytes()
    need = workers * WORKER_PEAK_BYTES + int(source_bytes)
    fit = None if avail is None else max(0, int((avail - source_bytes) // WORKER_PEAK_BYTES))
    return {"ok": avail is not None and avail >= need, "available_bytes": avail, "needed_bytes": need,
            "workers_that_fit": fit}


def run_header(k: dict, rh: str, fams: list, worlds: int, oracle_worlds: int, synthetic: bool) -> dict:
    return {"protocol_version": PROTOCOL_VERSION, "semantic_hash": k["semantic"], "research_hash": rh,
            "synthetic_dry_run": synthetic, "families": {f: ledger.sha256_file(family_path(f)) for f in fams},
            "seeds": SEEDS, "worlds_per_null": worlds, "oracle_worlds": oracle_worlds, "levels": list(ULEVELS),
            "speeds_days": USPEEDS, "perm_n": OPTS.perm_n, "draws_per_pair": CB.N_DRAWS,
            "rho_grid": [float(r) for r in RHO_GRID], "fine_points": FINE_POINTS,
            "pool_min_days": POOL_MIN_DAYS}


def oracle_advisory(oracle: dict) -> tuple:
    """F6: (log lines of the Tier-1 power per null, speed, level and grid threshold, reasons the seal rule must
    STOP whatever the null worlds give: power at the LARGEST grid threshold below POWER_MIN, or an achieved
    oracle level outside RHO_BOUND)."""
    lines, stop, top = [], [], max(C.G6_GRID)
    for n in ("A", "B"):
        summ = (oracle.get(n) or {}).get("summary") or {}
        for s in USPEEDS:
            for lvl in ULEVELS:
                v = summ.get(f"{s}|{lvl}") or {}
                pw = {t: ((v.get("by_threshold") or {}).get(str(t)) or {}).get("power") for t in C.G6_GRID}
                mv = v.get("mean_val_sharpe")
                lines.append(f"  oracle null {n} {s:4s} level {lvl}: Tier-1 power " +
                             "  ".join(f"at {t:g}: {'n/a' if pw[t] is None else f'{pw[t]:.3f}'}" for t in C.G6_GRID) +
                             f"; achieved mean VAL Sharpe {'n/a' if mv is None else f'{mv:.3f}'}")
                if pw[top] is None or pw[top] < C.POWER_MIN:
                    stop.append(f"null {n} {s}: power at {top:g} below {C.POWER_MIN:g}")
                if mv is None or abs(mv - lvl) > CB.RHO_BOUND:
                    stop.append(f"null {n} {s}: level {lvl} achieved outside its bound")
    return lines, stop


def calibrate_run(pool, partial: Partial, fams: list, worlds: int, oracle_worlds: int, log) -> tuple:
    """(nulls, oracle) of one run; every finished task is in `partial`. F6: the oracle phases of both nulls run
    FIRST, then the oracle power is logged, with one prominent line when the seal rule must STOP whatever the
    null worlds give; the results are assembled in argument order, so the artifact does not depend on the
    order of the phases."""
    nulls, oracle = {}, {}
    for null in ("A", "B"):
        seeds = [SEEDS[f"oracle_{null}"] + i for i in range(oracle_worlds)]
        rhos, tuning = {}, {}
        for speed in USPEEDS:
            tuning[speed] = tune_rho(pool, partial, null, speed, seeds, log)
            for lvl in ULEVELS:
                rhos[f"{speed}|{lvl}"] = tuning[speed][str(lvl)]["rho"]
        res = run_tasks(pool, partial, "power", [[null, s, rhos] for s in seeds], log, f"oracle {null} power")
        rows = sorted((r for rr in res for r in rr), key=lambda r: (r["world_seed"], r["speed"], r["level"]))
        oracle[null] = {"rhos": rhos, "tuning": tuning, "rows": rows, "summary": oracle_summary(rows)}
    lines, stop = oracle_advisory(oracle)
    for ln in lines:
        log(ln)
    if stop:
        log("!" * 100)
        log("ADVISORY: the seal rule will STOP whatever the null worlds give (" + "; ".join(stop) + "). The run can "
            "be interrupted now: the partial file keeps the finished work.")
        log("!" * 100)
    for null in ("A", "B"):
        res = run_tasks(pool, partial, "null", [[null, SEEDS[null] + i] for i in range(worlds)], log, f"null {null}")
        rows = sorted((r for rr in res for r in rr), key=lambda r: (r["world_seed"], r["family"]))
        nulls[null] = {"rows": rows, "summary": CB.null_summary(rows, fams)}
    return nulls, oracle


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m omr.ucalibrate")
    ap.add_argument("--worlds", type=int, default=200)
    ap.add_argument("--oracle-worlds", type=int, default=100)
    ap.add_argument("--workers", type=int, default=4, help="0: run every task in this process")
    ap.add_argument("--unlocked-dry-run", action="store_true")
    ap.add_argument("--out", default=None)
    ap.add_argument("--partial", default=None, help="partial file (default ledger/ucalibration_<semantic16>.partial.jsonl)")
    ap.add_argument("--restart", action="store_true", help="discard a partial file of another run and start again")
    ap.add_argument("--force", action="store_true", help="start although the memory preflight says it does not fit")
    a = ap.parse_args(argv)
    t0 = time.time()

    def log(s):
        print(s, flush=True)

    problems = kernel_lock.verify()
    lock_ok = not problems
    if not lock_ok and not a.unlocked_dry_run:
        log("KERNEL LOCK DOES NOT VERIFY - the calibration runs only on the locked kernel")
        raise SystemExit(3)
    if a.unlocked_dry_run and not a.out:
        raise SystemExit("--unlocked-dry-run needs --out <path>")
    k = kernel_lock.read_lock() if lock_ok else kernel_lock.compute()
    synthetic = bool(a.unlocked_dry_run)
    fams = list(FAMILIES)
    if synthetic:
        rh = "synthetic-dry-run"
    else:
        if not data.validation_ok():
            raise SystemExit("data not validated: run python -m omr.data validate")
        rh = data.load_manifest()["research_hash"]
    header = run_header(k, rh, fams, a.worlds, a.oracle_worlds, synthetic)
    ppath = Path(a.partial) if a.partial else (Path(a.out).with_suffix(".partial.jsonl") if a.out else
                                               P.LEDGER_DIR / f"ucalibration_{k['semantic'][:16]}.partial.jsonl")
    try:
        partial = Partial(ppath, header, restart=a.restart, log=log)
    except PartialMismatch as e:
        log(str(e))
        raise SystemExit(EXIT_PARTIAL)
    if synthetic:
        handle = access.for_calibration(f"universe calibration DRY RUN, semantic {k['semantic'][:16]}: synthetic universe")
        src = synthetic_source()
    else:
        handle = access.for_calibration(f"universe calibration v{PROTOCOL_VERSION}, semantic {k['semantic'][:16]}: "
                                        "null worlds on the real membership calendar of the top30 panel")
        src = load_source(handle, log)
    src_bytes = int(sum(v.nbytes for v in src.arr.values()))
    if a.workers > 0:
        mem = memory_preflight(a.workers, src_bytes)
        if not mem["ok"]:
            log(f"MEMORY: {a.workers} workers need about {mem['needed_bytes'] / 2 ** 30:.1f} GiB, "
                f"{(mem['available_bytes'] or 0) / 2 ** 30:.1f} GiB available; {mem['workers_that_fit']} workers fit")
            if not a.force:
                raise SystemExit(EXIT_MEMORY)
    spec, blocks = src.to_shared()
    try:
        if a.workers > 0:
            ctx = mp.get_context("spawn").Pool(a.workers, initializer=_init, initargs=(fams, handle, spec))
        else:
            ctx = _SerialPool(_init, (fams, handle, spec))
        with ctx as pool:
            nulls, oracle = calibrate_run(pool, partial, fams, a.worlds, a.oracle_worlds, log)
    finally:
        _W.pop("blocks", None)
        for b in blocks:
            b.close()
            b.unlink()
    verdict = CB.decide(nulls, oracle)
    out = {"protocol_version": PROTOCOL_VERSION, "unit": "top30", "kernel_hash": k["combined"],
           "semantic_hash": k["semantic"], "text_hash": k["text"], "kernel_lock_verified": lock_ok and not synthetic,
           "synthetic_dry_run": synthetic, "research_hash": rh, "panel": src.symbols,
           "created_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "families": header["families"],
           "protocol": {"worlds_per_null": a.worlds, "draws_per_pair": CB.N_DRAWS, "oracle_worlds": a.oracle_worlds,
                        "speeds_days": USPEEDS, "levels": list(ULEVELS), "seeds": SEEDS, "perm_n": OPTS.perm_n,
                        "membership": "the real monthly schedule (the kernel's rule on the real activity)",
                        "funding": "rates times a fair sign coin per settlement hour (R-E)",
                        "null_a_source_days": src.meta["pools"],
                        "g6": "paired lag test (R-C)", "blocks": "production (six-month blocks)",
                        "reduced_pipeline": "G8 not run"},
           "nulls": nulls, "oracle": oracle, "verdict_unit_only": verdict, "wall_seconds": round(time.time() - t0, 1)}
    path = Path(a.out) if a.out else P.LEDGER_DIR / f"ucalibration_{k['semantic'][:16]}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(ledger.clean(out), indent=1, sort_keys=True), encoding="ascii")
    log(f"saved {path}")
    if not a.out:
        kernel_lock.log_calibration(path, k["semantic"], rh)
    partial.remove()                                       # D1: only after the artifact is written (and logged)
    log(f"wall time {out['wall_seconds']} s")


if __name__ == "__main__":
    main()
