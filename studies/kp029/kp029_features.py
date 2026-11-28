"""KP-029 premise study (generation 4, round 2): the FEATURE BUILDER. NOT kernel code; nothing in omr/ imports it.

The study's hypotheses are written in the kernel's own language (studies/kp029/programs/*.omr) and computed by the
kernel's own interpreter, block machinery and self-checks (omr.upipeline.Blocked, omr.interp). The language has no
spot field, so the study serves the spot market through two SLOTS of the perpetual klines table that no study
program reads in their usual sense (SPOT SLOT MAP, PLAN version 2, ruling 1):

    volume            := the SPOT quote volume (USDT) of the same coin and hour
    taker_buy_volume  := the SPOT taker-buy quote volume (USDT) of the same coin and hour

Every other column (open, high, low, close, quote_volume, trades, taker_buy_quote_volume, is_gap), the funding,
mark and index tables, the activity, membership, in-play mask and every engine column are the kernel's own, read
by the kernel's own loaders under the dev_end ceiling. The perpetual's own base volume is not available to a
study program.

How a spot value enters at hour h (open time on the exchange clock), from rows at or before h only:
1. A REAL row: the pair's own row of hour h (after kp029_spot.clean), from the spot pair of the symbol map.
2. An OUTAGE HOUR (ruling 5): an hour at or after the first row of the stored spot BTCUSDT table for which that
   table has no row. At an outage hour a pair with no row of its own gets a SYNTHETIC row (zero trades, zero quote
   volume, zero taker-buy quote volume), provided it has a real row at some earlier hour. Every other absent hour
   (not listed yet, halted, ended, a row dropped by the cleaning) is unknown, never zero.
3. Usable bars follow the kernel's rule S3 (omr.universe.usable_of) on the pair's own hourly grid: a bar with
   trades is usable; a present bar with zero trades (synthetic rows included) while the run of non-trading hours
   ending there is at most 24; outage and absent hours count in the run.
4. The price guard (ruling 6, revised): a real row is used when spot close x multiplier lies within 50% of the
   perpetual's close of the same hour (a ratio from 0.5 to 1.5); a synthetic row takes the verdict of the pair's
   last real row. Otherwise both slots are unknown for that hour.
5. The slot values are placed in the klines table that the kernel's panel builder reads; the kernel masks every
   klines field outside the perpetual's usable bars and the interpreter treats NaN as unknown (LANGUAGE.md 5, 7).
   A window or timeframe bin containing an unknown hour is unknown, so the coin drops out of those decisions.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from omr import constants as C  # noqa: E402
from omr import datasets as D  # noqa: E402
from omr import universe as U  # noqa: E402
from omr import upipeline as UP  # noqa: E402

import kp029_spot as SP  # noqa: E402

SLOTS = {"volume": "quote_volume", "taker_buy_volume": "taker_buy_quote_volume"}   # program slot -> spot column
GUARD_TOL = 0.50                 # ruling 6 (revised): spot close x multiplier / perpetual close within 0.5 .. 1.5
OUTAGE_REF = "BTCUSDT"           # ruling 5: the spot pair whose missing rows define the exchange's outage hours
HOUR = pd.Timedelta(hours=1)


def _empty(n: int) -> dict:
    return {k: np.full(n, np.nan) for k in SLOTS}


def slot_detail(kl: pd.DataFrame, sp, mult: float, sp_raw=None, ref_raw=None, tol: float = GUARD_TOL) -> dict:
    """Per hour of kl.index: the slot values and the reasons behind them. kl: perpetual klines (index = open time,
    contiguous hourly); sp: the pair's cleaned spot rows or None; sp_raw: the pair's stored open times before cleaning
    (default: sp.index); ref_raw: the stored open times of the spot BTCUSDT table (None: no outage hour exists).
    Every quantity at hour h reads rows at or before h only."""
    n = len(kl)
    out = _empty(n)
    out.update(real=np.zeros(n, bool), synthetic=np.zeros(n, bool), outage=np.zeros(n, bool),
               guard_reject=np.zeros(n, bool))
    if sp is None or len(sp) == 0 or n == 0:
        return out
    raw_idx = sp.index if sp_raw is None or len(sp_raw) == 0 else pd.DatetimeIndex(sp_raw).union(sp.index)
    start = min(raw_idx[0], kl.index[0])
    end = kl.index[-1]
    if end < start:
        return out
    G = pd.date_range(start, end, freq="h").as_unit("ns")
    real = sp.reindex(G)
    is_real = np.isfinite(real["close"].to_numpy(dtype=np.float64))
    raw_present = G.isin(raw_idx)
    if ref_raw is not None and len(ref_raw):
        ref = pd.DatetimeIndex(ref_raw)
        outage = (G >= ref.min()) & ~G.isin(ref)
    else:
        outage = np.zeros(len(G), dtype=bool)
    seen_before = np.r_[False, np.cumsum(is_real)[:-1] > 0]          # a real row at some EARLIER hour
    synth = outage & ~raw_present & seen_before
    present = is_real | synth
    trades = np.where(is_real, real["trades"].to_numpy(dtype=np.float64), 0.0)
    active = present & (trades > 0)
    usable = U.usable_of(active, present)
    pc = kl["close"].reindex(G).to_numpy(dtype=np.float64)
    sc = real["close"].to_numpy(dtype=np.float64)
    with np.errstate(invalid="ignore", divide="ignore"):
        guard_real = is_real & np.isfinite(pc) & (pc > 0) & (np.abs(sc * mult / pc - 1.0) <= tol)
    pos = np.arange(len(G))
    last_real = np.maximum.accumulate(np.where(is_real, pos, -1))
    verdict = np.where(last_real >= 0, guard_real[np.maximum(last_real, 0)], False)
    ok = present & usable & verdict
    for slot, col in SLOTS.items():
        v = np.where(is_real, real[col].to_numpy(dtype=np.float64), 0.0)
        out[slot] = pd.Series(np.where(ok & np.isfinite(v), v, np.nan), index=G).reindex(kl.index).to_numpy()
    rx = lambda a: pd.Series(a, index=G).reindex(kl.index, fill_value=False).to_numpy(dtype=bool)  # noqa: E731
    out["real"], out["synthetic"], out["outage"] = rx(is_real), rx(synth), rx(outage)
    out["guard_reject"] = rx(is_real & ~guard_real)
    return out


def slot_columns(kl, sp, mult, sp_raw=None, ref_raw=None, tol: float = GUARD_TOL) -> dict:
    """{slot: float array aligned to kl.index} (see slot_detail)."""
    d = slot_detail(kl, sp, mult, sp_raw, ref_raw, tol)
    return {k: d[k] for k in SLOTS}


def cut_tables(t: dict, cut: pd.Timestamp) -> dict:
    """The perpetual tables with every row visible after `cut` dropped (the study's truncation test)."""
    out = {}
    for d, df in t.items():
        if len(df) == 0:
            out[d] = df
            continue
        out[d] = df[D.get(d).visible_from(df) <= cut]
    return out


def _upto(ix, cut):
    if ix is None or cut is None:
        return ix
    ix = pd.DatetimeIndex(ix)
    return ix[ix <= cut]


def spot_inputs(perp: str, spot, cut=None, shift_hours: int = 0) -> tuple:
    """(cleaned rows, stored open times, BTCUSDT stored open times, multiplier) of a perpetual's spot pair, every
    table cut at `cut` (the BTCUSDT table too). shift_hours: ONLY the synthetic negative test uses it (a deliberate
    look-ahead: the pair's row of t + shift_hours is served at t); always 0 in the study."""
    sname, mult = SP.spot_symbol(perp)
    sp = spot.get(sname) if spot is not None else None
    raw = spot.raw_index(sname) if spot is not None else None
    ref = spot.raw_index(OUTAGE_REF) if spot is not None else None
    if sp is not None and cut is not None:
        sp = sp[sp.index <= cut]
    raw, ref = _upto(raw, cut), _upto(ref, cut)
    if shift_hours and sp is not None:
        sp = sp.copy()
        sp.index = sp.index - shift_hours * HOUR
        raw = None if raw is None else pd.DatetimeIndex(raw) - shift_hours * HOUR
    return sp, raw, ref, mult


def inject(tables: dict, perp: str, spot, cut=None, tol: float = GUARD_TOL, shift_hours: int = 0) -> dict:
    """The kernel's tables of one perpetual with the two spot slots filled in the klines table. cut: drop every
    perpetual and spot row after it first (truncation test)."""
    t = dict(tables) if cut is None else cut_tables(tables, cut)
    kl = t["klines"]
    sp, raw, ref, mult = spot_inputs(perp, spot, cut, shift_hours)
    cols = slot_columns(kl, sp, mult, raw, ref, tol)
    kl2 = kl.copy()
    for slot, v in cols.items():
        kl2[slot] = v
    t["klines"] = kl2
    return t


def study_udata(ud: UP.UData, spot, cut=None, tol: float = GUARD_TOL, shift_hours: int = 0) -> UP.UData:
    """A UData with the kernel's activity, membership inputs, ceiling and BTC frame, whose per-symbol tables are
    the kernel's own tables with the spot slots injected (the UData `loader` hook; nothing of the kernel is
    replaced or patched). cut: the truncation test's input with every row after the cut dropped."""
    def loader(s):
        return inject(ud.tables(s), s, spot, cut=cut, tol=tol, shift_hours=shift_hours)
    btc = ud.btc if cut is None or ud.btc is None else ud.btc[ud.btc.index <= cut]
    return UP.UData(acts=ud.acts, raw={}, btc=btc, end=ud.end, until=dict(ud.until), loader=loader,
                    loadable=frozenset(set(ud.raw) | set(ud.loadable)))


def needed_fields(prog_fields: set) -> set:
    """Fields to load from the kernel for a study program: its own fields plus close (the guard reads it); the
    slots are filled by inject whether or not the kernel loaded the perpetual's base volume."""
    return set(prog_fields) | {"close"}


def slot_fields_read(prog) -> set:
    return UP.program_fields(prog) & set(SLOTS)


def dev_end_ok(ud: UP.UData) -> bool:
    return ud.end == UP.T(C.DEV_END)
