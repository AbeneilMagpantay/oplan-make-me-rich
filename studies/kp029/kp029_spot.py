"""KP-029 premise study (generation 4, round 2): spot-file rules shared by the downloader and the feature builder.

NOT kernel code. Nothing here is imported by omr/; nothing here writes under data/ or ledger/.

What this module fixes (generations/gen004/PLAN.md, PLAN version 2):
- The CEILING. No spot file of a month after 2022-06 can be named, requested or read (month_allowed, url, the
  loader); rows whose open time is after 2022-06-30 23:00 UTC (= the kernel's DEV end) are dropped on load. The
  first month is 2019-12 (the kernel's universe grid starts 2019-12-31 00:00; nothing earlier is ever read).
- The SYMBOL MAP. A perpetual XXXUSDT maps to the spot pair XXXUSDT; 1000XXXUSDT (and 1000000XXXUSDT) map to the
  spot pair XXXUSDT with a price multiplier of 1000 (1,000,000) for the price-agreement guard. Quote volumes in
  USDT are compared as they are (no multiplier).
- The FILE FORMAT. data.binance.vision spot monthly klines, 1h: one CSV per zip, 12 columns (open time, open,
  high, low, close, base volume, close time, quote volume, trades, taker-buy base volume, taker-buy quote volume,
  ignore), no header expected (a header line is skipped if present); open time in milliseconds, or in
  microseconds when the value is >= 1e14 (the archive's format from 2025-01; never reached under the ceiling).
- HASH AT READ. Every zip is read only after its sha256 equals the one in its own .CHECKSUM file (downloaded next
  to it and verified at download too).
"""
from __future__ import annotations

import hashlib
import io
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SPOT_ROOT = ROOT / "_build" / "kp029_study" / "spot"      # git-ignored (_build/)
FIRST_MONTH = (2019, 12)
LAST_MONTH = (2022, 6)                                      # HARD CEILING: no later month, ever
ROW_CEILING = pd.Timestamp("2022-06-30 23:00", tz="UTC")    # = omr.constants.DEV_END; later rows dropped on load
ROW_FLOOR = pd.Timestamp("2019-12-01 00:00", tz="UTC")
BASE_URL = "https://data.binance.vision/data/spot/monthly/klines"
HOUR_NS = 3_600_000_000_000
PREFIXES = (("1000000", 1_000_000.0), ("1000", 1000.0))     # longest first
COLS = ("open_time", "open", "high", "low", "close", "volume", "close_time", "quote_volume", "trades",
        "taker_buy_volume", "taker_buy_quote_volume", "ignore")
KEEP = ("close", "quote_volume", "trades", "taker_buy_quote_volume")


class CeilingError(RuntimeError):
    """A month or row beyond the study's DEV ceiling was named or found."""


def spot_symbol(perp: str) -> tuple:
    """(spot pair, price multiplier) for a USDT perpetual name."""
    for pre, mult in PREFIXES:
        if perp.startswith(pre) and len(perp) > len(pre) + 4:
            return perp[len(pre):], mult
    return perp, 1.0


def month_allowed(y: int, m: int) -> bool:
    return FIRST_MONTH <= (int(y), int(m)) <= LAST_MONTH and 1 <= int(m) <= 12


def months_between(a: tuple, b: tuple) -> list:
    """Calendar months a..b inclusive, clipped to FIRST_MONTH..LAST_MONTH."""
    a = max(tuple(a), FIRST_MONTH)
    b = min(tuple(b), LAST_MONTH)
    out = []
    y, m = a
    while (y, m) <= b:
        out.append((y, m))
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


def zip_name(sym: str, y: int, m: int) -> str:
    return f"{sym}-1h-{int(y):04d}-{int(m):02d}.zip"


def url(sym: str, y: int, m: int, checksum: bool = False) -> str:
    """The archive address of one monthly file; refuses any month outside 2019-12 .. 2022-06."""
    if not month_allowed(y, m):
        raise CeilingError(f"month {y:04d}-{m:02d} is outside the study's window {FIRST_MONTH} .. {LAST_MONTH}")
    if not sym.isascii() or not sym.isalnum() or not sym.endswith("USDT"):
        raise ValueError(f"not a USDT spot pair name: {sym!r}")
    u = f"{BASE_URL}/{sym}/1h/{zip_name(sym, y, m)}"
    return u + ".CHECKSUM" if checksum else u


def month_of_name(sym: str, fname: str):
    """(y, m) of a stored file name SYM-1h-YYYY-MM.zip, else None."""
    pre = f"{sym}-1h-"
    if not (fname.startswith(pre) and fname.endswith(".zip")):
        return None
    ym = fname[len(pre):-4]
    if len(ym) != 7 or ym[4] != "-" or not (ym[:4].isdigit() and ym[5:].isdigit()):
        return None
    return int(ym[:4]), int(ym[5:])


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def checksum_of(text: str, fname: str) -> str:
    """The sha256 in a .CHECKSUM file ('<hex>  <file name>')."""
    parts = text.strip().split()
    if len(parts) != 2 or parts[1] != fname or len(parts[0]) != 64:
        raise ValueError(f"malformed CHECKSUM for {fname}")
    return parts[0].lower()


def parse_csv_bytes(data: bytes) -> pd.DataFrame:
    """One monthly CSV -> DataFrame indexed by bar open time (UTC, ns) with KEEP columns, float64. Rows outside
    ROW_FLOOR .. ROW_CEILING are dropped. Raises on an open time off the hour or a duplicate open time."""
    text = data.decode("ascii")
    lines = [ln for ln in text.splitlines() if ln.strip()]
    if lines and not lines[0].split(",")[0].strip().lstrip("-").isdigit():
        lines = lines[1:]                                   # a header line, if the archive ever adds one
    if not lines:
        return pd.DataFrame({c: np.zeros(0) for c in KEEP}, index=pd.DatetimeIndex([], tz="UTC").as_unit("ns"))
    rows = [ln.split(",") for ln in lines]
    if any(len(r) < 11 for r in rows):
        raise ValueError("a spot kline row has fewer than 11 columns")
    ot = np.array([int(r[0]) for r in rows], dtype=np.int64)
    ns = np.where(ot >= 10 ** 14, ot * 1000, ot * 1_000_000)          # microseconds from 2025-01, else ms
    if np.any(ns % HOUR_NS != 0):
        raise ValueError("a spot kline open time is not on the hour")
    vals = {c: np.array([float(r[COLS.index(c)]) for r in rows], dtype=np.float64) for c in KEEP}
    idx = pd.DatetimeIndex(pd.to_datetime(ns, unit="ns", utc=True)).as_unit("ns")
    df = pd.DataFrame(vals, index=idx)
    if df.index.has_duplicates:
        raise ValueError("duplicate spot kline open times")
    df = df.sort_index()
    return df[(df.index >= ROW_FLOOR) & (df.index <= ROW_CEILING)]


def read_zip(path: Path, sym: str, y: int, m: int) -> pd.DataFrame:
    """One verified monthly zip -> rows (hash at read against its .CHECKSUM file)."""
    if not month_allowed(y, m):
        raise CeilingError(f"stored spot file of a month outside the window: {path.name}")
    b = path.read_bytes()
    ck = Path(str(path) + ".CHECKSUM")
    if not ck.exists():
        raise ValueError(f"{path.name}: no .CHECKSUM next to it")
    if sha256_bytes(b) != checksum_of(ck.read_text(encoding="ascii"), path.name):
        raise ValueError(f"{path.name}: sha256 differs from its .CHECKSUM")
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        names = z.namelist()
        want = path.name[:-4] + ".csv"
        if names != [want]:
            raise ValueError(f"{path.name}: unexpected members {names[:3]}")
        return parse_csv_bytes(z.read(want))


def clean(df: pd.DataFrame) -> tuple:
    """(rows, n_dropped): rows with a non-finite or non-positive close, a non-finite or negative volume, or a
    taker-buy quote volume above the quote volume (beyond 1e-9 relative) are dropped (so they are unknown)."""
    c, q, t, b = (df[k].to_numpy() for k in ("close", "quote_volume", "trades", "taker_buy_quote_volume"))
    with np.errstate(invalid="ignore"):
        ok = (np.isfinite(c) & (c > 0) & np.isfinite(q) & (q >= 0) & np.isfinite(t) & (t >= 0) & np.isfinite(b)
              & (b >= 0) & (b <= q * (1 + 1e-9) + 1e-12))
    return df[ok], int((~ok).sum())


class SpotStore:
    """Spot rows per spot pair from SPOT_ROOT/<SYM>/<SYM>-1h-YYYY-MM.zip (lazy, cached). get(sym) -> the CLEANED rows
    (DataFrame) or None when the pair has no stored file; raw_index(sym) -> the open times of every stored row before
    cleaning (the outage rule asks whether a pair HAS a row, ruling 5). A stored file of a month after 2022-06 stops
    the run (CeilingError)."""

    def __init__(self, root: Path = SPOT_ROOT):
        self.root = Path(root)
        self._c = {}
        self._raw = {}
        self.dropped = {}

    def raw_index(self, sym: str):
        self.get(sym)
        return self._raw.get(sym)

    def files(self, sym: str) -> list:
        d = self.root / sym
        if not d.is_dir():
            return []
        out = []
        for p in sorted(d.iterdir()):
            if p.name.endswith(".zip"):
                ym = month_of_name(sym, p.name)
                if ym is None:
                    raise ValueError(f"unexpected file in the spot folder: {p.name}")
                if not month_allowed(*ym):
                    raise CeilingError(f"stored spot file of a month outside the window: {p.name}")
                out.append((ym, p))
        return out

    def get(self, sym: str):
        if sym in self._c:
            return self._c[sym]
        parts = [read_zip(p, sym, y, m) for (y, m), p in self.files(sym)]
        if not parts:
            self._c[sym] = None
            return None
        df = pd.concat(parts).sort_index()
        if df.index.has_duplicates:
            raise ValueError(f"{sym}: duplicate open times across monthly files")
        self._raw[sym] = df.index.copy()
        df, n = clean(df)
        self.dropped[sym] = n
        self._c[sym] = df
        return df


class DictSpot:
    """In-memory spot rows {spot pair: DataFrame} (tests), with the same ceiling on rows."""

    def __init__(self, tables: dict):
        self.t, self._raw = {}, {}
        for k, v in tables.items():
            v = v[(v.index >= ROW_FLOOR) & (v.index <= ROW_CEILING)].sort_index()
            self._raw[k] = v.index.copy()
            self.t[k], _ = clean(v)

    def get(self, sym: str):
        return self.t.get(sym)

    def raw_index(self, sym: str):
        return self._raw.get(sym)
