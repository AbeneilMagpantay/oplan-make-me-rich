"""Market data storage: download, validate, store, manifest, research hash. Kernel module.

Source: Binance USD-M futures public bulk files (data.binance.vision), with the
public REST API (fapi.binance.com) used only for (a) the warm-up months before
the first bulk month and (b) the hours/settlements after the last bulk file.
No key, account or login is used. Generic User-Agent, no personal details.

CLI:
    python -m omr.data download     first snapshot (sets vault_end)
    python -m omr.data update       append new data (vault_end and research_hash must not change)
    python -m omr.data verify       recompute file hashes and research_hash against the manifest
    python -m omr.data validate     finiteness, positive prices, OHLC consistency, non-negative volumes,
                                    hourly unique sorted timestamps, funding, mark coverage, gap bars:
                                    COUNTS only, per dataset/symbol/region; writes data/validation.json
                                    bound to the data fingerprint (omr.evaluate refuses without it)
    python -m omr.data summary      print the manifest summary

Every stored file is hashed at the moment it is read (_read_stored) and must equal its manifest
sha256; the readers are private to the data layer (omr.datasets is the only other caller).

This module and omr/census.py are the only kernel modules allowed to use the
"latest" ceiling (enforced by tests/test_structure.py).
"""
from __future__ import annotations

import datetime as dt
import hashlib
import io
import json
import sys
import time
import zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd
import requests

from omr import constants as C
from omr.paths import DATA_DIR, MANIFEST, RAW_DIR

USER_AGENT = "omr-research-client/1.0"
BULK = "https://data.binance.vision/data/futures/um"
FAPI = "https://fapi.binance.com/fapi/v1"
REST_HISTORY_START_MS = 1567296000000  # 2019-09-01 00:00 UTC, before the first USD-M listing
HOUR_MS = 3_600_000
FIRST_BULK_MONTH = (2020, 1)

KLINE_FLOAT_COLS = ["open", "high", "low", "close", "volume", "quote_volume",
                    "trades", "taker_buy_volume", "taker_buy_quote_volume"]
KLINE_COLS = KLINE_FLOAT_COLS + ["is_gap"]
FUNDING_COLS = ["rate", "interval_hours", "offset_ms"]
MARK_COLS = ["open", "high", "low", "close", "samples"]   # samples = seconds sampled in the hour (3600 = full)
FUNDING_DEFAULT_INTERVAL_H = 8.0   # declared default settlement interval of the funding dataset
DATASET_COLS = {"klines": KLINE_COLS, "funding": FUNDING_COLS, "mark_klines": MARK_COLS}

# Ceilings for every loader. "latest" = no ceiling (census and this data layer only).
CEILINGS = {
    "dev_end": C.DEV_END,
    "val_end": C.VAL_END,
    "latest": None,
}


def ceiling_ts(upto: str):
    """Return the inclusive bar-open-time ceiling for `upto`, or None for no ceiling."""
    if upto not in CEILINGS:
        raise ValueError(f"unknown ceiling {upto!r}; use one of {sorted(CEILINGS)}")
    v = CEILINGS[upto]
    return None if v is None else ts(v)


def ts(s: str) -> pd.Timestamp:
    """UTC timestamp at nanosecond resolution (pandas 3 defaults to us; we pin ns)."""
    return pd.Timestamp(s, tz="UTC").as_unit("ns")


def ns_index(idx) -> pd.DatetimeIndex:
    """Return idx as a UTC DatetimeIndex at nanosecond resolution."""
    idx = pd.DatetimeIndex(idx)
    if idx.tz is None:
        idx = idx.tz_localize("UTC")
    return idx.as_unit("ns")


def ns_int(idx) -> np.ndarray:
    """Epoch nanoseconds of a DatetimeIndex, independent of its stored unit."""
    return ns_index(idx).asi8


def stored_path(dataset: str, symbol: str) -> Path:
    return DATA_DIR / dataset / f"{symbol}.parquet"


_CACHE: dict = {}


class DataIntegrityError(RuntimeError):
    pass


def _read_stored(dataset: str, symbol: str, manifest: dict | None = None) -> pd.DataFrame:
    """Read the full stored table for (dataset, symbol). PRIVATE to the data layer.

    The file's bytes are hashed at the moment they are read and must equal the manifest's sha256
    (the same bytes are then parsed, so nothing can change in between). Callers slice by ceiling.
    """
    p = stored_path(dataset, symbol)
    if not p.exists():
        raise FileNotFoundError(f"no stored data for {dataset}/{symbol}: run python -m omr.data download")
    raw = p.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    manifest = manifest if manifest is not None else load_manifest()
    want = manifest.get("datasets", {}).get(dataset, {}).get(symbol, {}).get("sha256")
    if want is None:
        raise DataIntegrityError(f"stored {dataset}/{symbol} has no sha256 in data/manifest.json")
    if want != digest:
        raise DataIntegrityError(f"stored {dataset}/{symbol} does not match data/manifest.json")
    if digest not in _CACHE:
        _CACHE.clear() if len(_CACHE) > 64 else None
        _CACHE[digest] = pd.read_parquet(io.BytesIO(raw))
    return _CACHE[digest].copy()


def load_manifest() -> dict:
    if not MANIFEST.exists():
        raise FileNotFoundError("data/manifest.json missing: run python -m omr.data download")
    return json.loads(MANIFEST.read_text(encoding="ascii"))


# ---------------------------------------------------------------- hashing

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _frame_bytes(df: pd.DataFrame, cols) -> list:
    out = [np.asarray(ns_int(df.index), dtype=np.int64).tobytes()]
    for c in cols:
        v = df[c].to_numpy()
        if v.dtype == bool:
            out.append(v.astype(np.uint8).tobytes())
        else:
            out.append(np.asarray(v, dtype=np.float64).tobytes())
    return out


def compute_research_hash(tables: dict, only: str | None = None) -> str:
    """sha256 over every stored row visible at or before VAL_END.

    tables: {(dataset, symbol): DataFrame}. Rows are cut at VAL_END by index
    (for every v1 dataset the index is the bar from which the row is visible).
    only: restrict to one dataset (per-dataset revision hash).
    """
    cut = ts(C.VAL_END)
    h = hashlib.sha256()
    for (dataset, symbol) in sorted(tables):
        if only is not None and dataset != only:
            continue
        df = tables[(dataset, symbol)]
        df = df[df.index <= cut]
        cols = DATASET_COLS[dataset]
        h.update(f"{dataset}/{symbol}/{len(df)}\n".encode("ascii"))
        for b in _frame_bytes(df, cols):
            h.update(b)
    return h.hexdigest()


def dataset_hashes(tables: dict) -> dict:
    return {d: compute_research_hash(tables, only=d) for d in sorted({k[0] for k in tables})}


def _tables_from_disk(manifest: dict) -> dict:
    """PRIVATE: every stored table, hash-verified against `manifest`."""
    tables = {}
    for dataset, per_sym in manifest["datasets"].items():
        for symbol in per_sym:
            tables[(dataset, symbol)] = _read_stored(dataset, symbol, manifest)
    return tables


def research_hash_from_disk(manifest: dict | None = None) -> str:
    manifest = manifest or load_manifest()
    return compute_research_hash(_tables_from_disk(manifest))


def data_fingerprint(manifest: dict | None = None) -> str:
    """sha256 over the research_hash and every stored file's manifest sha256 (binds validation)."""
    manifest = manifest or load_manifest()
    parts = [manifest["research_hash"]]
    for dataset in sorted(manifest["datasets"]):
        for s in sorted(manifest["datasets"][dataset]):
            parts.append(f"{dataset}/{s}:{manifest['datasets'][dataset][s]['sha256']}")
    return hashlib.sha256("\n".join(parts).encode("ascii")).hexdigest()


VALIDATION = DATA_DIR / "validation.json"
_REGIONS = (("warmup", None, C.DEV_START), ("dev", C.DEV_START, C.DEV_END), ("val", C.VAL_START, C.VAL_END),
            ("vault", C.VAULT_START, C.VAULT_END), ("after_vault", C.VAULT_END, None))


def _region_mask(idx: pd.DatetimeIndex, lo, hi, name) -> np.ndarray:
    m = np.ones(len(idx), dtype=bool)
    if lo is not None:
        m &= idx >= ts(lo) if name != "after_vault" else idx > ts(lo)
    if hi is not None:
        m &= (idx < ts(hi)) if name == "warmup" else (idx <= ts(hi))
    return m


def validate(log=print) -> dict:
    """Check every region of every stored table; print COUNTS only; write data/validation.json."""
    manifest = load_manifest()
    tables = _tables_from_disk(manifest)
    counts, fails = {}, 0
    for (dataset, s), df in sorted(tables.items()):
        idx = ns_index(df.index)
        steps = np.diff(ns_int(idx))
        ts_bad = int((steps <= 0).sum()) + int((ns_int(idx) % (3_600_000_000_000) != 0).sum())
        if dataset == "klines":
            ts_bad += int((steps != 3_600_000_000_000).sum())
        for region, lo, hi in _REGIONS:
            m = _region_mask(idx, lo, hi, region)
            d = df[m]
            c = {"rows": int(len(d))}
            if dataset in ("klines", "mark_klines"):
                px = d[["open", "high", "low", "close"]].to_numpy(dtype=np.float64)
                c["nonfinite_price"] = int((~np.isfinite(px)).sum())
                c["nonpositive_price"] = int((px <= 0).sum())
                o, h, l_, cl = px.T if len(px) else (np.zeros(0),) * 4
                c["ohlc_inconsistent"] = int(((h < np.maximum(o, cl)) | (l_ > np.minimum(o, cl)) | (h < l_)).sum())
            if dataset == "klines":
                vol = d[["volume", "quote_volume", "trades", "taker_buy_volume", "taker_buy_quote_volume"]].to_numpy(dtype=np.float64)
                c["nonfinite_volume"] = int((~np.isfinite(vol)).sum())
                c["negative_volume"] = int((vol < 0).sum())
                c["gap_bars"] = int(d["is_gap"].sum())
            if dataset == "funding":
                fv = d[["rate", "interval_hours"]].to_numpy(dtype=np.float64)
                c["nonfinite_funding"] = int((~np.isfinite(fv)).sum())
                c["nonpositive_interval"] = int((d["interval_hours"] <= 0).sum())
            if dataset == "mark_klines":
                kl = tables[("klines", s)]
                g = ns_index(kl.index)
                gm = g[_region_mask(g, lo, hi, region)]
                c["grid_bars"] = int(len(gm))
                c["mark_bars_on_grid"] = int(gm.isin(idx[m]).sum())
            bad = sum(v for k, v in c.items() if k in ("nonfinite_price", "nonpositive_price", "ohlc_inconsistent",
                                                       "nonfinite_volume", "negative_volume", "nonfinite_funding",
                                                       "nonpositive_interval"))
            fails += bad
            counts[f"{dataset}/{s}/{region}"] = c
        counts[f"{dataset}/{s}/timestamps_bad"] = {"count": ts_bad}
        fails += ts_bad
    out = {"data_fingerprint": data_fingerprint(manifest), "research_hash": manifest["research_hash"],
           "passed": fails == 0, "failures": int(fails), "counts": counts,
           "validated_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
    VALIDATION.write_text(json.dumps(out, indent=1, sort_keys=True), encoding="ascii")
    for k, c in counts.items():
        log(f"{k}: " + " ".join(f"{a}={b}" for a, b in c.items()))
    log(("PASSED" if out["passed"] else "FAILED") + f" data validation ({fails} failing counts)")
    return out


def validation_ok() -> bool:
    """True when data/validation.json passed for the CURRENT data (fingerprint match)."""
    if not VALIDATION.exists():
        return False
    v = json.loads(VALIDATION.read_text(encoding="ascii"))
    return bool(v.get("passed")) and v.get("data_fingerprint") == data_fingerprint()


# ---------------------------------------------------------------- http

_SESSION = None


def _session():
    global _SESSION
    if _SESSION is None:
        s = requests.Session()
        s.headers.update({"User-Agent": USER_AGENT})
        _SESSION = s
    return _SESSION


def http_get(url: str, params: dict | None = None, retries: int = 5, timeout: int = 60):
    """GET url. Returns bytes, or None on 404. Raises after retries on other failures."""
    last = None
    for attempt in range(retries):
        try:
            r = _session().get(url, params=params, timeout=timeout)
            if r.status_code == 404:
                return None
            if r.status_code == 200:
                return r.content
            last = f"HTTP {r.status_code}"
            if r.status_code in (418, 429):
                time.sleep(10 * (attempt + 1))
                continue
        except requests.RequestException as e:
            last = type(e).__name__
        time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"GET failed after {retries} tries ({last}): {url}")


def fetch_bulk(url: str, dest: Path) -> str:
    """Download a bulk zip once, verify its published sha256 CHECKSUM, cache it.

    Returns "cached", "ok", "ok-nochecksum" or "missing".
    """
    if dest.exists():
        return "cached"
    data = http_get(url)
    if data is None:
        return "missing"
    chk = http_get(url + ".CHECKSUM")
    status = "ok"
    if chk is None:
        status = "ok-nochecksum"
    else:
        expected = chk.decode("ascii", "replace").split()[0].strip().lower()
        got = hashlib.sha256(data).hexdigest()
        if expected != got:
            raise RuntimeError(f"checksum mismatch for {url}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".tmp")
    tmp.write_bytes(data)
    tmp.replace(dest)
    return status


# ---------------------------------------------------------------- parsing

def _read_zip_csv(path: Path) -> bytes:
    with zipfile.ZipFile(path) as z:
        names = [n for n in z.namelist() if n.lower().endswith(".csv")]
        if len(names) != 1:
            raise RuntimeError(f"expected one csv in {path.name}, found {names}")
        return z.read(names[0])


def _has_header(raw: bytes) -> bool:
    first = raw.lstrip()[:1]
    return not (first.isdigit() or first == b"-")


def to_ms(values: np.ndarray):
    """Normalise epoch timestamps to milliseconds by magnitude (us -> ms). Returns (ms, n_us)."""
    v = np.asarray(values, dtype=np.int64)
    is_us = v > 10 ** 14
    out = np.where(is_us, v // 1000, v)
    return out, int(is_us.sum())


def parse_kline_bytes(raw: bytes) -> tuple[pd.DataFrame, int]:
    skip = 1 if _has_header(raw) else 0
    df = pd.read_csv(io.BytesIO(raw), header=None, skiprows=skip, usecols=list(range(11)))
    df.columns = ["open_time", "open", "high", "low", "close", "volume", "close_time",
                  "quote_volume", "trades", "taker_buy_volume", "taker_buy_quote_volume"]
    ms, n_us = to_ms(df["open_time"].to_numpy())
    out = pd.DataFrame({"open_time_ms": ms})
    for c in KLINE_FLOAT_COLS:
        out[c] = df[c].to_numpy(dtype=np.float64)
    return out, n_us


def parse_mark_bytes(raw: bytes) -> tuple[pd.DataFrame, int]:
    """markPriceKlines csv: open_time, open, high, low, close, (volume=0), close_time, (0), count, ..."""
    skip = 1 if _has_header(raw) else 0
    df = pd.read_csv(io.BytesIO(raw), header=None, skiprows=skip, usecols=[0, 1, 2, 3, 4, 8])
    df.columns = ["open_time", "open", "high", "low", "close", "samples"]
    ms, n_us = to_ms(df["open_time"].to_numpy())
    out = pd.DataFrame({"open_time_ms": ms})
    for c in MARK_COLS:
        out[c] = df[c].to_numpy(dtype=np.float64)
    return out, n_us


def parse_funding_bytes(raw: bytes) -> tuple[pd.DataFrame, int]:
    skip = 1 if _has_header(raw) else 0
    df = pd.read_csv(io.BytesIO(raw), header=None, skiprows=skip, usecols=[0, 1, 2])
    df.columns = ["calc_time", "interval_hours", "rate"]
    ms, n_us = to_ms(df["calc_time"].to_numpy())
    out = pd.DataFrame({"time_ms": ms,
                        "interval_hours": df["interval_hours"].to_numpy(dtype=np.float64),
                        "rate": df["rate"].to_numpy(dtype=np.float64)})
    return out, n_us


# ---------------------------------------------------------------- REST

def rest_klines(symbol: str, start_ms: int, end_ms: int) -> pd.DataFrame:
    """Closed 1h klines with open_time in [start_ms, end_ms] from the public REST API."""
    rows = []
    cur = start_ms
    while cur <= end_ms:
        data = http_get(f"{FAPI}/klines", params={"symbol": symbol, "interval": "1h",
                                                    "startTime": cur, "endTime": end_ms, "limit": 1500})
        if data is None:
            break
        batch = json.loads(data)
        if not batch:
            break
        rows.extend(batch)
        nxt = int(batch[-1][0]) + HOUR_MS
        if nxt <= cur:
            break
        cur = nxt
        time.sleep(0.2)
    if not rows:
        empty = {"open_time_ms": np.zeros(0, dtype=np.int64)}
        empty.update({c: np.zeros(0, dtype=np.float64) for c in KLINE_FLOAT_COLS})
        return pd.DataFrame(empty)
    a = pd.DataFrame(rows).iloc[:, :11]
    a.columns = ["open_time", "open", "high", "low", "close", "volume", "close_time",
                 "quote_volume", "trades", "taker_buy_volume", "taker_buy_quote_volume"]
    out = pd.DataFrame({"open_time_ms": a["open_time"].astype(np.int64).to_numpy()})
    for c in KLINE_FLOAT_COLS:
        out[c] = a[c].astype(np.float64).to_numpy()
    return out[(out.open_time_ms >= start_ms) & (out.open_time_ms <= end_ms)]


def rest_mark_klines(symbol: str, start_ms: int, end_ms: int) -> pd.DataFrame:
    """Closed 1h mark-price klines with open_time in [start_ms, end_ms] from the public REST API."""
    rows = []
    cur = start_ms
    while cur <= end_ms:
        data = http_get(f"{FAPI}/markPriceKlines", params={"symbol": symbol, "interval": "1h",
                                                            "startTime": cur, "endTime": end_ms, "limit": 1500})
        if data is None:
            break
        batch = json.loads(data)
        if not batch:
            break
        rows.extend(batch)
        nxt = int(batch[-1][0]) + HOUR_MS
        if nxt <= cur:
            break
        cur = nxt
        time.sleep(0.2)
    if not rows:
        empty = {"open_time_ms": np.zeros(0, dtype=np.int64)}
        empty.update({c: np.zeros(0, dtype=np.float64) for c in MARK_COLS})
        return pd.DataFrame(empty)
    a = pd.DataFrame(rows)
    out = pd.DataFrame({"open_time_ms": a[0].astype(np.int64).to_numpy()})
    for j, c in zip((1, 2, 3, 4, 8), MARK_COLS):
        out[c] = a[j].astype(np.float64).to_numpy()
    return out[(out.open_time_ms >= start_ms) & (out.open_time_ms <= end_ms)]


def rest_funding(symbol: str, start_ms: int, end_ms: int) -> pd.DataFrame:
    """Funding settlements with time in [start_ms, end_ms]. interval_hours is inferred
    from the gap to the previous settlement (the endpoint does not return it)."""
    rows = []
    cur = start_ms
    while cur <= end_ms:
        data = http_get(f"{FAPI}/fundingRate", params={"symbol": symbol, "startTime": cur,
                                                         "endTime": end_ms, "limit": 1000})
        if data is None:
            break
        batch = json.loads(data)
        if not batch:
            break
        rows.extend(batch)
        nxt = int(batch[-1]["fundingTime"]) + 1
        if nxt <= cur:
            break
        cur = nxt
        time.sleep(0.2)
    if not rows:
        return pd.DataFrame({"time_ms": np.zeros(0, dtype=np.int64),
                             "interval_hours": np.zeros(0, dtype=np.float64),
                             "rate": np.zeros(0, dtype=np.float64)})
    t = np.array([int(r["fundingTime"]) for r in rows], dtype=np.int64)
    rate = np.array([float(r["fundingRate"]) for r in rows], dtype=np.float64)
    out = pd.DataFrame({"time_ms": t, "rate": rate})
    out = out[(out.time_ms >= start_ms) & (out.time_ms <= end_ms)]
    out = out.drop_duplicates("time_ms").sort_values("time_ms").reset_index(drop=True)
    rounded = np.round(out.time_ms.to_numpy() / HOUR_MS)
    gaps = np.diff(rounded, prepend=np.nan)
    out["interval_hours"] = np.where(np.isnan(gaps), np.nan, gaps)
    return out


# ---------------------------------------------------------------- building

def _months(start: tuple, end: tuple):
    y, m = start
    while (y, m) <= end:
        yield y, m
        m += 1
        if m == 13:
            y, m = y + 1, 1


def last_complete_hour(now: dt.datetime | None = None) -> pd.Timestamp:
    now = now or dt.datetime.now(dt.timezone.utc)
    return (pd.Timestamp(now).tz_convert("UTC").floor("h") - pd.Timedelta(hours=1)).as_unit("ns")


def _bulk_plan(symbol: str, snapshot_end: pd.Timestamp):
    """List of (dataset, kind, url, dest, label) bulk files to fetch for a symbol."""
    cur = (snapshot_end.year, snapshot_end.month)
    prev_end = (cur[0], cur[1] - 1) if cur[1] > 1 else (cur[0] - 1, 12)
    plan = []
    for (y, m) in _months(FIRST_BULK_MONTH, prev_end):
        lab = f"{y:04d}-{m:02d}"
        plan.append(("klines", "monthly",
                     f"{BULK}/monthly/klines/{symbol}/1h/{symbol}-1h-{lab}.zip",
                     RAW_DIR / "klines" / symbol / f"{symbol}-1h-{lab}.zip", lab))
        plan.append(("funding", "monthly",
                     f"{BULK}/monthly/fundingRate/{symbol}/{symbol}-fundingRate-{lab}.zip",
                     RAW_DIR / "funding" / symbol / f"{symbol}-fundingRate-{lab}.zip", lab))
        plan.append(("mark_klines", "monthly",
                     f"{BULK}/monthly/markPriceKlines/{symbol}/1h/{symbol}-1h-{lab}.zip",
                     RAW_DIR / "mark_klines" / symbol / f"{symbol}-1h-{lab}.zip", lab))
    day = pd.Timestamp(year=cur[0], month=cur[1], day=1, tz="UTC")
    last_full_day = snapshot_end.normalize() - pd.Timedelta(days=1)
    if snapshot_end.hour == 23:
        last_full_day = snapshot_end.normalize()
    while day <= last_full_day:
        lab = day.strftime("%Y-%m-%d")
        plan.extend(_daily_items(symbol, lab))
        day += pd.Timedelta(days=1)
    return plan


_BULK_KIND = {"klines": "klines", "mark_klines": "markPriceKlines"}


def _daily_items(symbol: str, lab: str, datasets=("klines", "mark_klines")):
    return [(ds, "daily", f"{BULK}/daily/{_BULK_KIND[ds]}/{symbol}/1h/{symbol}-1h-{lab}.zip",
             RAW_DIR / ds / symbol / "daily" / f"{symbol}-1h-{lab}.zip", lab) for ds in datasets]


def _daily_fallback_plan(symbol: str, y: int, m: int, dataset: str = "klines"):
    start = pd.Timestamp(year=y, month=m, day=1, tz="UTC")
    end = (start + pd.offsets.MonthEnd(1)).normalize()
    out = []
    d = start
    while d <= end:
        out.extend(_daily_items(symbol, d.strftime("%Y-%m-%d"), (dataset,)))
        d += pd.Timedelta(days=1)
    return out


def _grid_klines(raw: pd.DataFrame, snapshot_end: pd.Timestamp) -> tuple[pd.DataFrame, dict]:
    raw = raw.sort_values("open_time_ms", kind="mergesort")
    n_before = len(raw)
    dup_mask = raw.duplicated("open_time_ms", keep="first")
    dups = raw[raw.open_time_ms.isin(raw.loc[dup_mask, "open_time_ms"])]
    conflicting = int(dups.drop_duplicates().duplicated("open_time_ms").sum())
    raw = raw[~dup_mask]
    misaligned = int((raw.open_time_ms % HOUR_MS != 0).sum())
    if misaligned:
        raise RuntimeError(f"{misaligned} kline open times not on the hour")
    idx = ns_index(pd.to_datetime(raw.open_time_ms.to_numpy().astype(np.int64), unit="ms", utc=True))
    df = pd.DataFrame({c: raw[c].to_numpy(dtype=np.float64) for c in KLINE_FLOAT_COLS}, index=idx)
    df.index.name = "open_time"
    df = df[df.index <= snapshot_end]
    grid = ns_index(pd.date_range(df.index[0], snapshot_end, freq="h", name="open_time"))
    grid.name = "open_time"
    df = df.reindex(grid)
    gap = df["close"].isna().to_numpy()
    df["close"] = df["close"].ffill()
    for c in ("open", "high", "low"):
        df[c] = df[c].where(~gap, df["close"])
    for c in ("volume", "quote_volume", "trades", "taker_buy_volume", "taker_buy_quote_volume"):
        df[c] = df[c].where(~gap, 0.0)
    df["is_gap"] = gap
    o, h, l, c_ = (df[k].to_numpy() for k in ("open", "high", "low", "close"))
    viol = int(((h < np.maximum(o, c_) - 1e-12) | (l > np.minimum(o, c_) + 1e-12) | (l <= 0)).sum())
    runs = int(((gap[1:] & ~gap[:-1]).sum()) + (1 if gap[0] else 0)) if len(gap) else 0
    info = {"raw_rows": n_before, "duplicates_dropped": int(dup_mask.sum()),
            "duplicates_conflicting": conflicting, "gap_count": int(gap.sum()),
            "gap_runs": runs, "ohlc_violations": viol}
    return df[KLINE_COLS], info


def _table_funding(raw: pd.DataFrame, snapshot_end: pd.Timestamp) -> tuple[pd.DataFrame, dict]:
    raw = raw.sort_values("time_ms", kind="mergesort").reset_index(drop=True)
    tm = raw.time_ms.to_numpy(dtype=np.int64)
    rounded = (np.round(tm / HOUR_MS) * HOUR_MS).astype(np.int64)
    offset = tm - rounded
    df = pd.DataFrame({"rate": raw.rate.to_numpy(dtype=np.float64),
                       "interval_hours": raw.interval_hours.to_numpy(dtype=np.float64),
                       "offset_ms": offset.astype(np.float64)},
                      index=ns_index(pd.to_datetime(rounded, unit="ms", utc=True)))
    df.index.name = "settle_time"
    dup = df.index.duplicated(keep="last")
    df = df[~dup]
    df = df[df.index <= snapshot_end]
    # interval_hours missing (REST rows): the gap to the PREVIOUS settlement; the very first row
    # uses the dataset's declared default (never a later row)
    ih = df["interval_hours"].to_numpy(dtype=np.float64).copy()
    gaps_h = np.diff(ns_int(df.index)) / 3.6e12
    for i in np.where(np.isnan(ih))[0]:
        ih[i] = gaps_h[i - 1] if i > 0 else FUNDING_DEFAULT_INTERVAL_H
    df["interval_hours"] = ih
    anomalies = int((np.abs(gaps_h - ih[1:]) > 0.5).sum()) if len(gaps_h) else 0
    info = {"raw_rows": int(len(raw)), "duplicates_after_rounding": int(dup.sum()),
            "max_abs_offset_ms": float(np.max(np.abs(offset))) if len(offset) else 0.0,
            "offsets_over_60s": int((np.abs(offset) > 60_000).sum()),
            "interval_anomalies": anomalies}
    return df[FUNDING_COLS], info


def build_symbol(symbol: str, snapshot_end: pd.Timestamp, results: dict, log) -> dict:
    """Assemble klines and funding tables for one symbol from cached bulk files + REST."""
    meta = {"klines": {}, "funding": {}}
    end_ms = int(snapshot_end.value // 10 ** 6)

    # ---- klines from bulk
    parts, n_us, files_used, missing, us_files = [], 0, {"monthly": 0, "daily": 0}, [], []
    for (dataset, kind, url, dest, lab) in results[symbol]:
        if dataset != "klines":
            continue
        if not dest.exists():
            missing.append(f"{kind}:{lab}")
            continue
        df, k = parse_kline_bytes(_read_zip_csv(dest))
        df["src"] = 0
        parts.append(df)
        files_used[kind] += 1
        if k:
            us_files.append(lab)
        n_us += k
    if not parts:
        raise RuntimeError(f"no bulk klines for {symbol}")
    bulk = pd.concat(parts, ignore_index=True).sort_values("open_time_ms")
    first_bulk = int(bulk.open_time_ms.iloc[0])
    last_bulk = int(bulk.open_time_ms.iloc[-1])

    # ---- REST backfill (warm-up before the first bulk month) and top-up
    back = rest_klines(symbol, REST_HISTORY_START_MS, first_bulk - HOUR_MS)
    back["src"] = 1
    top = rest_klines(symbol, last_bulk + HOUR_MS, end_ms) if last_bulk < end_ms else back.iloc[0:0]
    top["src"] = 2
    log(f"  {symbol} klines: bulk {len(bulk)} rows, rest backfill {len(back)}, rest top-up {len(top)}")

    crosscheck = None
    if symbol in C.CORE:
        first_month_end = first_bulk + 31 * 24 * HOUR_MS
        chk = rest_klines(symbol, first_bulk, first_month_end)
        m = bulk.merge(chk, on="open_time_ms", suffixes=("_b", "_r"))
        if len(m):
            diffs = {c: float(np.max(np.abs(m[c + "_b"] - m[c + "_r"]) / np.maximum(np.abs(m[c + "_b"]), 1e-12)))
                     for c in ("open", "high", "low", "close", "volume")}
            crosscheck = {"rows_compared": int(len(m)), "max_rel_diff": diffs}

    allk = pd.concat([back, bulk, top], ignore_index=True)
    kl, info = _grid_klines(allk.drop(columns=["src"]), snapshot_end)

    # unit-switch continuity check across 2024-12 -> 2025-01
    a, b = ts("2024-12-31 23:00"), ts("2025-01-01 00:00")
    cont = {"files_with_us_timestamps": us_files, "us_rows": n_us}
    if a in kl.index and b in kl.index:
        cont.update({
            "bar_2024_12_31_23_present_raw": bool(not kl.at[a, "is_gap"]),
            "bar_2025_01_01_00_present_raw": bool(not kl.at[b, "is_gap"]),
            "step_hours": float((b - a) / pd.Timedelta(hours=1)),
            "open_2025_over_close_2024_minus_1": float(kl.at[b, "open"] / kl.at[a, "close"] - 1.0),
        })
    years = kl.index.year
    if years.min() < 2019 or years.max() > snapshot_end.year:
        raise RuntimeError(f"{symbol}: timestamps outside plausible range (unit detection failed?)")
    meta["klines"] = {
        "source": "binance_usdm_bulk(data.binance.vision); rest(fapi.binance.com) for warm-up backfill and top-up",
        "bulk_files": files_used, "missing_bulk_files": missing,
        "rest_backfill_rows": int(len(back)), "rest_topup_rows": int(len(top)),
        "first_bar": str(kl.index[0]), "last_bar": str(kl.index[-1]), "rows": int(len(kl)),
        "unit_check": cont, "rest_vs_bulk_crosscheck": crosscheck, **info,
    }

    # ---- funding
    fparts, fus = [], 0
    for (dataset, kind, url, dest, lab) in results[symbol]:
        if dataset != "funding" or not dest.exists():
            continue
        df, k = parse_funding_bytes(_read_zip_csv(dest))
        fparts.append(df)
        fus += k
    fb = pd.concat(fparts, ignore_index=True).sort_values("time_ms") if fparts else \
        pd.DataFrame({"time_ms": np.zeros(0, dtype=np.int64),
                      "interval_hours": np.zeros(0, dtype=np.float64),
                      "rate": np.zeros(0, dtype=np.float64)})
    if len(fb):
        f_first, f_last = int(fb.time_ms.iloc[0]), int(fb.time_ms.iloc[-1])
        fback = rest_funding(symbol, REST_HISTORY_START_MS, f_first - 60_000)
        ftop = rest_funding(symbol, f_last + 60_000, end_ms + HOUR_MS)
    else:
        fback = rest_funding(symbol, REST_HISTORY_START_MS, end_ms + HOUR_MS)
        ftop = fback.iloc[0:0]
    # REST rows have interval inferred from the previous REST row; the first REST
    # top-up row's interval is taken from the gap to the last bulk settlement.
    allf = pd.concat([fback, fb, ftop], ignore_index=True)
    allf = allf.sort_values("time_ms").drop_duplicates("time_ms", keep="first").reset_index(drop=True)
    fd, finfo = _table_funding(allf, snapshot_end)
    log(f"  {symbol} funding: bulk {len(fb)} rows, rest backfill {len(fback)}, rest top-up {len(ftop)}")
    meta["funding"] = {
        "source": "binance_usdm_bulk fundingRate(data.binance.vision); rest(fapi.binance.com) for backfill and top-up",
        "bulk_rows": int(len(fb)), "rest_backfill_rows": int(len(fback)), "rest_topup_rows": int(len(ftop)),
        "us_rows": fus, "first_settlement": str(fd.index[0]) if len(fd) else None,
        "last_settlement": str(fd.index[-1]) if len(fd) else None, "rows": int(len(fd)), **finfo,
    }

    # ---- mark-price klines (stored as actual rows only; missing bars stay missing)
    md, minfo = build_mark(symbol, snapshot_end, results, kl, log)
    meta["mark_klines"] = minfo
    return {"klines": kl, "funding": fd, "mark_klines": md, "meta": meta}


def mark_coverage(mark: pd.DataFrame, grid: pd.DatetimeIndex) -> dict:
    """Fraction of 1h grid bars (DEV+VAL, and all) that have a valid mark bar."""
    valid = mark[(mark["open"] > 0) & np.isfinite(mark[["open", "high", "low"]]).all(axis=1)]
    a, b = ts(C.DEV_START), ts(C.VAL_END)
    g_dv = grid[(grid >= a) & (grid <= b)]
    have_dv = int(g_dv.isin(valid.index).sum())
    have_all = int(grid.isin(valid.index).sum())
    return {"grid_bars_dev_val": int(len(g_dv)), "mark_bars_dev_val": have_dv,
            "coverage_dev_val": (have_dv / len(g_dv)) if len(g_dv) else None,
            "missing_dev_val": int(len(g_dv) - have_dv),
            "grid_bars_all": int(len(grid)), "mark_bars_all": have_all,
            "coverage_all": have_all / len(grid) if len(grid) else None}


def build_mark(symbol: str, snapshot_end: pd.Timestamp, results: dict, kl: pd.DataFrame, log):
    end_ms = int(snapshot_end.value // 10 ** 6)
    parts, n_us, files_used, missing = [], 0, {"monthly": 0, "daily": 0}, []
    for (dataset, kind, url, dest, lab) in results[symbol]:
        if dataset != "mark_klines":
            continue
        if not dest.exists():
            missing.append(f"{kind}:{lab}")
            continue
        df, k = parse_mark_bytes(_read_zip_csv(dest))
        parts.append(df)
        files_used[kind] += 1
        n_us += k
    empty = pd.DataFrame({"open_time_ms": np.zeros(0, dtype=np.int64), **{c: np.zeros(0) for c in MARK_COLS}})
    bulk = pd.concat(parts, ignore_index=True).sort_values("open_time_ms") if parts else empty
    if len(bulk):
        first_b, last_b = int(bulk.open_time_ms.iloc[0]), int(bulk.open_time_ms.iloc[-1])
        back = rest_mark_klines(symbol, REST_HISTORY_START_MS, first_b - HOUR_MS)
        top = rest_mark_klines(symbol, last_b + HOUR_MS, end_ms) if last_b < end_ms else empty
    else:
        back = rest_mark_klines(symbol, REST_HISTORY_START_MS, end_ms)
        top = empty
    allm = pd.concat([back, bulk, top], ignore_index=True).sort_values("open_time_ms", kind="mergesort")
    dup = allm.duplicated("open_time_ms", keep="first")
    allm = allm[~dup]
    if int((allm.open_time_ms % HOUR_MS != 0).sum()):
        raise RuntimeError(f"{symbol}: mark open times not on the hour")
    idx = ns_index(pd.to_datetime(allm.open_time_ms.to_numpy().astype(np.int64), unit="ms", utc=True))
    md = pd.DataFrame({c: allm[c].to_numpy(dtype=np.float64) for c in MARK_COLS}, index=idx)
    md.index.name = "open_time"
    md = md[md.index <= snapshot_end]
    o, h, l, c_ = (md[k].to_numpy() for k in ("open", "high", "low", "close"))
    viol = int(((h < np.maximum(o, c_) - 1e-9) | (l > np.minimum(o, c_) + 1e-9) | (l <= 0)).sum())
    log(f"  {symbol} mark_klines: bulk {len(bulk)} rows, rest backfill {len(back)}, rest top-up {len(top)}")
    info = {"source": "binance_usdm_bulk markPriceKlines 1h (data.binance.vision); rest(fapi.binance.com) "
                      "for backfill and top-up",
            "bulk_files": files_used, "missing_bulk_files": missing, "rest_backfill_rows": int(len(back)),
            "rest_topup_rows": int(len(top)), "duplicates_dropped": int(dup.sum()), "us_rows": n_us,
            "first_bar": str(md.index[0]) if len(md) else None, "last_bar": str(md.index[-1]) if len(md) else None,
            "rows": int(len(md)), "ohlc_violations": viol,
            "partial_bars_samples_lt_3600": int((md["samples"] < 3600).sum()),
            **mark_coverage(md, kl.index)}
    return md[MARK_COLS], info


def snapshot(mode: str, log=print, admit=()) -> dict:
    """Download/refresh everything, write parquet + manifest. mode: 'download' or 'update'.

    Revision check: for every dataset already in the manifest, the per-dataset hash of rows
    visible at or before VAL end must be unchanged, and every previously stored row must be
    unchanged. A dataset not in the old manifest is written only if named in `admit`
    (data admission by kernel re-key, CONSTITUTION 3.2).
    """
    old = load_manifest() if MANIFEST.exists() else None
    if mode == "update" and old is None:
        raise RuntimeError("update needs an existing manifest; run download first")
    if old is not None:
        # the stored files must match the manifest before anything is appended
        for dataset, per in old["datasets"].items():
            for s, meta in per.items():
                p = stored_path(dataset, s)
                if not p.exists() or sha256_file(p) != meta.get("sha256"):
                    raise RuntimeError(f"stored {dataset}/{s} does not match data/manifest.json; refusing to update")
    old_hashes = None
    if old is not None:
        old_hashes = old.get("dataset_hashes") or dataset_hashes(_tables_from_disk(old))
    snapshot_end = last_complete_hour()
    log(f"snapshot_end (last complete hour) = {snapshot_end}")

    plan = {s: _bulk_plan(s, snapshot_end) for s in C.ALL_SYMBOLS}
    tasks = [(s, item) for s in C.ALL_SYMBOLS for item in plan[s]]

    def run(task):
        s, (dataset, kind, url, dest, lab) = task
        return s, (dataset, kind, url, dest, lab), fetch_bulk(url, dest)

    statuses = {}
    with ThreadPoolExecutor(max_workers=8) as ex:
        for s, item, st in ex.map(run, tasks):
            statuses[(s, item[3])] = st
    # monthly kline / mark files missing after the symbol's first available month -> daily fallback
    for s in C.ALL_SYMBOLS:
        for ds in ("klines", "mark_klines"):
            have = [it for it in plan[s] if it[0] == ds and it[1] == "monthly" and statuses[(s, it[3])] != "missing"]
            if not have:
                continue
            first_lab = have[0][4]
            extra = []
            for it in plan[s]:
                if it[0] == ds and it[1] == "monthly" and statuses[(s, it[3])] == "missing" and it[4] > first_lab:
                    y, m = int(it[4][:4]), int(it[4][5:7])
                    extra.extend(_daily_fallback_plan(s, y, m, ds))
            for it in extra:
                statuses[(s, it[3])] = fetch_bulk(it[2], it[3])
            plan[s].extend(extra)
    n_dl = sum(1 for v in statuses.values() if v.startswith("ok"))
    n_nochk = sum(1 for v in statuses.values() if v == "ok-nochecksum")
    log(f"bulk files: {len(statuses)} planned, {n_dl} downloaded now ({n_nochk} without checksum), "
        f"{sum(1 for v in statuses.values() if v == 'cached')} cached, "
        f"{sum(1 for v in statuses.values() if v == 'missing')} missing (mostly pre-listing months)")

    names = ("klines", "funding", "mark_klines")
    tables, metas = {}, {n: {} for n in names}
    for s in C.ALL_SYMBOLS:
        res = build_symbol(s, snapshot_end, plan, log)
        for n in names:
            tables[(n, s)] = res[n]
            metas[n][s] = res["meta"][n]

    for s in C.CORE:
        first = tables[("klines", s)].index[0]
        if first > ts(C.DEV_START):
            raise RuntimeError(f"core symbol {s} starts {first}, after DEV start: STOP")

    rh = compute_research_hash(tables)
    new_hashes = dataset_hashes(tables)
    if old is not None:
        for d, hsh in new_hashes.items():
            if d in old_hashes:
                if old_hashes[d] != hsh:
                    raise RuntimeError(f"dataset {d}: rows before VAL end were revised. Nothing written. "
                                       "Quarantine the source and report to the human.")
            elif d not in admit:
                raise RuntimeError(f"dataset {d} is not in the manifest; admit it explicitly (kernel re-key). "
                                   "Nothing written.")
        # previously stored rows must be unchanged (revision check), except trailing gap rows
        for (dataset, s), df in tables.items():
            p = stored_path(dataset, s)
            if p.exists() and dataset in old_hashes:
                prev = pd.read_parquet(p)
                common = prev.index.intersection(df.index)
                a_, b_ = prev.loc[common], df.loc[common]
                if dataset == "klines":
                    keep = ~prev.loc[common, "is_gap"].to_numpy()
                    a_, b_ = a_[keep], b_[keep]
                if not np.allclose(a_.to_numpy(dtype=float), b_.to_numpy(dtype=float), rtol=0, atol=0, equal_nan=True):
                    raise RuntimeError(f"revision detected in {dataset}/{s}: stored rows changed. Nothing written.")

    for (dataset, s), df in tables.items():
        p = stored_path(dataset, s)
        p.parent.mkdir(parents=True, exist_ok=True)
        tmp = p.with_suffix(".parquet.tmp")
        df.to_parquet(tmp)
        tmp.replace(p)
        metas[dataset][s]["sha256"] = sha256_file(p)

    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    manifest = {
        "kernel_data_version": 1,
        "created_at": old["created_at"] if old else now,
        "updated_at": now,
        "snapshot_end": str(snapshot_end),
        "vault_start": str(ts(C.VAULT_START)),
        "vault_end": str(ts(C.VAULT_END)),
        "dev": [C.DEV_START, C.DEV_END], "val": [C.VAL_START, C.VAL_END],
        "research_hash": rh,
        "dataset_hashes": new_hashes,
        "admitted_this_snapshot": sorted(d for d in new_hashes if old is not None and d not in old_hashes),
        "datasets": metas,
    }
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(manifest, indent=1, sort_keys=True), encoding="ascii")
    log(f"research_hash = {rh}")
    return manifest


def verify(log=print) -> bool:
    m = load_manifest()
    ok = True
    for dataset, per in m["datasets"].items():
        for s, meta in per.items():
            got = sha256_file(stored_path(dataset, s))
            if got != meta["sha256"]:
                log(f"FAIL sha256 {dataset}/{s}")
                ok = False
    rh = research_hash_from_disk(m)
    if rh != m["research_hash"]:
        log("FAIL research_hash")
        ok = False
    log(("OK" if ok else "FAIL") + f" data verify (research_hash {rh[:16]})")
    return ok


def summary(log=print):
    m = load_manifest()
    log(f"snapshot_end {m['snapshot_end']}  vault_end {m['vault_end']}  research_hash {m['research_hash'][:16]}")
    for s, k in m["datasets"]["klines"].items():
        f = m["datasets"]["funding"][s]
        log(f"{s:9s} klines {k['first_bar'][:16]} .. {k['last_bar'][:16]} rows {k['rows']:6d} gaps {k['gap_count']:4d} "
            f"(runs {k['gap_runs']}) | funding {str(f['first_settlement'])[:16]} .. {str(f['last_settlement'])[:16]} rows {f['rows']}")
    for s, mk in m["datasets"].get("mark_klines", {}).items():
        log(f"{s:9s} mark {str(mk['first_bar'])[:16]} .. {str(mk['last_bar'])[:16]} rows {mk['rows']:6d}  "
            f"coverage DEV+VAL {mk['mark_bars_dev_val']}/{mk['grid_bars_dev_val']} = {mk['coverage_dev_val']:.6f}  "
            f"all {mk['mark_bars_all']}/{mk['grid_bars_all']} = {mk['coverage_all']:.6f}  partial {mk['partial_bars_samples_lt_3600']}")


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else "summary"
    if cmd in ("download", "update"):
        admit = tuple(argv[argv.index("--admit") + 1].split(",")) if "--admit" in argv else ()
        snapshot(cmd, log=lambda s: print(s, flush=True), admit=admit)
        summary()
    elif cmd == "verify":
        sys.exit(0 if verify() else 1)
    elif cmd == "validate":
        sys.exit(0 if validate()["passed"] else 1)
    elif cmd == "summary":
        summary()
    else:
        print("usage: python -m omr.data download|update [--admit name[,name]]|verify|validate|summary")
        sys.exit(2)


if __name__ == "__main__":
    main()
