"""Dataset registry and the single point-in-time alignment function. Kernel module.

Each dataset adapter declares: name, frequency, history start, source, the
fields it exposes, and the rule for WHEN a row becomes knowable, expressed as
`visible_from(rows)` = the open time of the 1h bar from whose CLOSE the row may
be used. `align_to_grid` is the only function that puts dataset rows on the 1h
grid; it never lets a row appear before its visible_from bar.

v1 datasets: klines (the 1h base grid), funding, and mark_klines (admitted
2026-11-18; used by the engine's liquidation check). New datasets are added only
by a human-approved kernel re-key after the data-admission checks in
CONSTITUTION.md. Nothing in the engine or evaluator names a dataset except
through this registry.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from omr import access
from omr import data

HOUR = pd.Timedelta(hours=1)


@dataclass(frozen=True)
class Dataset:
    name: str
    freq: str            # "1h" (one row per bar) or "event" (irregular rows)
    history_start: str
    source: str
    knowable_rule: str
    fields: tuple = field(default_factory=tuple)

    def visible_from(self, rows: pd.DataFrame) -> pd.DatetimeIndex:
        raise NotImplementedError


class _Klines(Dataset):
    def visible_from(self, rows):
        # A bar's OHLCV is final at its close, so it is usable from the decision
        # taken at the close of that same bar: visible_from = its open time.
        return data.ns_index(rows.index)


class _Funding(Dataset):
    def visible_from(self, rows):
        # Settlement times are rounded to the hour at storage. A rate settled at
        # time t is final at t, i.e. inside the bar that opens at t; it is usable
        # from that bar's close. visible_from = floor(t to the hour).
        return data.ns_index(rows.index).floor("h")


KLINES = _Klines(
    name="klines", freq="1h", history_start="2019-09-08",
    source="Binance USD-M bulk klines 1h (data.binance.vision); REST fapi.binance.com for warm-up backfill and top-up",
    knowable_rule="bar row known at its close; visible from its own bar",
    fields=tuple(data.KLINE_COLS),
)
FUNDING = _Funding(
    name="funding", freq="event", history_start="2019-09-10",
    source="Binance USD-M bulk fundingRate (data.binance.vision); REST fapi.binance.com for backfill and top-up",
    knowable_rule="rate known at settlement time t (rounded to the hour); visible from the bar that opens at t",
    fields=("rate", "interval_hours"),
)

MARK_KLINES = _Klines(
    name="mark_klines", freq="1h", history_start="2019-12-23",
    source="Binance USD-M bulk markPriceKlines 1h (data.binance.vision); REST fapi.binance.com for backfill and top-up",
    knowable_rule="mark-price bar known at its close; visible from its own bar; missing bars stay missing",
    fields=("open", "high", "low", "close"),
)

REGISTRY = {d.name: d for d in (KLINES, FUNDING, MARK_KLINES)}
LIQ = "mark_klines"   # dataset used by the engine's liquidation check
BASE = "klines"
# Every frame carries funding_rate (rate settled at that bar's open, else 0; used by the engine).
ALWAYS = ("funding",)
# Datasets exposed to the interpreter as '<name>.<field>' columns (fields funding8h, mark_close,
# funding_mean). Every program frame is assembled with these.
PROGRAM_EXTRA = ("funding", "mark_klines")


def get(name: str) -> Dataset:
    if name not in REGISTRY:
        raise KeyError(f"unknown dataset {name!r}; registered: {sorted(REGISTRY)}")
    return REGISTRY[name]


def _check_access(upto: str, handle, what: str) -> None:
    """Any ceiling beyond DEV end (val_end, latest) needs a ledger-issued ValHandle; a trial handle
    whose pending row is not in the real trial ledger is logged in the real VAL access log before
    any frame is returned (access.note_val_read)."""
    if upto != "dev_end":
        access.require(handle, f"{what}(upto={upto!r})")
        access.note_val_read(handle)


def load_raw(name: str, symbol: str, upto: str, handle=None) -> pd.DataFrame:
    """Stored rows of one dataset for one symbol whose visible_from bar <= the ceiling."""
    _check_access(upto, handle, "load_raw")
    ds = get(name)
    rows = data._read_stored(name, symbol)
    cap = data.ceiling_ts(upto)
    if cap is not None:
        rows = rows[ds.visible_from(rows) <= cap]
    return rows


def align_to_grid(rows: pd.DataFrame, visible_from: pd.DatetimeIndex, grid: pd.DatetimeIndex):
    """Point-in-time alignment of irregular rows onto the 1h grid.

    Returns (asof, new):
      asof: DataFrame on `grid`, the latest row visible at each bar (forward filled), NaN before the first.
      new:  bool array, True at the bar where a row became visible (rows visible before the grid
            starts only seed the as-of state and are not marked new).
    A row is placed at the first grid bar >= its visible_from, never earlier. Rows visible after
    the grid end are dropped. If several rows map to one bar, the last one wins.
    """
    grid = data.ns_index(grid)
    vf = data.ns_index(visible_from)
    g = data.ns_int(grid)
    v = data.ns_int(vf)
    order = np.argsort(v, kind="mergesort")
    v = v[order]
    vals = rows.iloc[order]
    keep = v <= g[-1]
    v, vals = v[keep], vals[keep]
    pos = np.searchsorted(g, v, side="left")
    pre = v < g[0]
    out = pd.DataFrame(np.nan, index=grid, columns=list(rows.columns), dtype=np.float64)
    new = np.zeros(len(grid), dtype=bool)
    if len(v):
        # last row per target position wins
        last = np.r_[pos[1:] != pos[:-1], True]
        p_last = pos[last]
        arr = vals.to_numpy(dtype=np.float64)[last]
        out.iloc[p_last, :] = arr
        new_rows = last & ~pre
        new[pos[new_rows]] = True
        out = out.ffill()
    return out, new


def assemble_frame(raw: dict, extra: tuple = ()) -> pd.DataFrame:
    """Build the frame the interpreter reads for one symbol from in-memory raw dataset tables.

    raw: {"klines": DataFrame on the 1h grid, "funding": settlements, ...}
    extra: names of declared datasets to expose as '<name>.<field>' plus '<name>.new'.
    The frame always carries the klines columns and `funding_rate`.
    """
    kl = raw[BASE]
    grid = data.ns_index(kl.index)
    frame = pd.DataFrame({c: kl[c].to_numpy() for c in data.KLINE_COLS}, index=grid)
    frame.index.name = "open_time"
    names = list(dict.fromkeys(list(ALWAYS) + [n for n in extra if n != BASE]))
    for name in names:
        ds = get(name)
        rows = raw[name]
        asof, new = align_to_grid(rows[list(ds.fields)], ds.visible_from(rows), grid)
        if name == "funding":
            frame["funding_rate"] = np.where(new, asof["rate"].to_numpy(), 0.0)
        if name in extra:
            for f in ds.fields:
                frame[f"{name}.{f}"] = asof[f].to_numpy()
            frame[f"{name}.new"] = new
    return frame


def liquidation_ratios(klines: pd.DataFrame, mark) -> pd.DataFrame:
    """Intrabar adverse-move ratios for the engine's liquidation check, on the klines grid.

    dn = mark low / mark open, up = mark high / mark open of the SAME bar. Where a bar has no
    valid mark row (missing, non-positive or non-finite), fall back to the last-price
    low / open and high / open of that bar. Column has_mark says which source was used.
    """
    grid = data.ns_index(klines.index)
    o = klines["open"].to_numpy(dtype=np.float64)
    dn_last = klines["low"].to_numpy(dtype=np.float64) / o
    up_last = klines["high"].to_numpy(dtype=np.float64) / o
    if mark is None or len(mark) == 0:
        has = np.zeros(len(grid), dtype=bool)
        dn, up = dn_last, up_last
    else:
        m = mark.reindex(grid)
        mo = m["open"].to_numpy(dtype=np.float64)
        mh = m["high"].to_numpy(dtype=np.float64)
        ml = m["low"].to_numpy(dtype=np.float64)
        has = np.isfinite(mo) & np.isfinite(mh) & np.isfinite(ml) & (mo > 0) & (ml > 0) & (mh >= ml)
        with np.errstate(divide="ignore", invalid="ignore"):
            dn = np.where(has, ml / np.where(has, mo, 1.0), dn_last)
            up = np.where(has, mh / np.where(has, mo, 1.0), up_last)
    return pd.DataFrame({"dn": dn, "up": up, "has_mark": has}, index=grid)


def load_liq(symbol: str, upto: str, handle=None) -> pd.DataFrame:
    _check_access(upto, handle, "load_liq")
    kl = load_raw(BASE, symbol, upto=upto, handle=handle)
    try:
        mark = load_raw(LIQ, symbol, upto=upto, handle=handle)
    except FileNotFoundError:
        mark = None
    return liquidation_ratios(kl, mark)


def load_liqs(symbols, upto: str, handle=None) -> dict:
    _check_access(upto, handle, "load_liqs")
    return {s: load_liq(s, upto=upto, handle=handle) for s in symbols}


def load_frame(symbol: str, extra: tuple, upto: str, handle=None) -> pd.DataFrame:
    _check_access(upto, handle, "load_frame")
    names = list(dict.fromkeys([BASE] + list(ALWAYS) + list(extra)))
    raw = {n: load_raw(n, symbol, upto=upto, handle=handle) for n in names}
    return assemble_frame(raw, tuple(extra))


def load_frames(symbols, extra: tuple, upto: str, handle=None) -> dict:
    _check_access(upto, handle, "load_frames")
    return {s: load_frame(s, tuple(extra), upto=upto, handle=handle) for s in symbols}
