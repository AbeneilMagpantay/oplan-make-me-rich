"""Point-in-time universe of USDT perpetuals (KP-015): symbol table and monthly membership. Kernel module.

    python -m omr.universe symbols   build data/symbols.json from the public exchangeInfo and the archive listing
    python -m omr.universe members   membership per month from the stored klines (COUNTS only)

SYMBOL TABLE (A1). Every folder name under the archive's USD-M monthly or daily 1h klines that matches
^[0-9A-Z]+USDT$ gets one row and one class; only `crypto_perpetual` can ever be a member. Rules, in order:
  R1 present in the public exchangeInfo (fapi/v1/exchangeInfo, fetched at build time):
     contractType TRADIFI_PERPETUAL -> `tradfi_perpetual`; BUT if the archive holds monthly klines files for
       that name from a month before the TradFi contract's onboard month, the name was reused: the earlier
       series is a `crypto_perpetual` whose rows end before the TradFi onboard hour (`until`); TradFi
       perpetuals first appeared in 2025-12, and no rows at or after `until` are ever used;
     contractType PERPETUAL, quoteAsset USDT, underlyingType COIN -> `crypto_perpetual`;
     underlyingType INDEX -> `index_contract`; anything else (pre-market, quarterly, ...) -> `other`.
  R2 absent from exchangeInfo (ended contracts): the index contracts named in INDEX_ABSENT ->
     `index_contract`; every other absent name -> `crypto_perpetual`.
  Folders not matching the pattern (dated delivery contracts, *USDTSETTLED copies, other quote assets)
  are counted, not listed. Renamed contracts are NOT merged: each name is its own series.
  The table is written to data/symbols.json and its sha256 is pinned in the manifest by the universe
  download (python -m omr.data universe).

ACTIVITY (A2, S3). A 1h bar is ACTIVE iff it exists in the archive and has trades > 0 (membership counts
active bars only). A symbol's history starts at its first active bar. A bar is USABLE (its fields known as
recorded, the symbol tradable, the engine able to hold it) when it is active, or when it is present with
zero trades and the run of consecutive non-active bars ending at it is at most 24 long (counted backwards
only, so it is causal): a short exchange halt does not flatten programs, while delisting padding and long
stretches drop out after a day (a held position is then closed at the frozen last price). A bar absent from
the archive is never usable.

MEMBERSHIP (B). Reconstituted at the first hour m of each calendar month (UTC) from bars with open time
strictly before m; a pure function of the klines that reads only [m - 97 days, m) (READ_DAYS):
  SEASONED  (R1a) its first active bar is at least 90 days before m (an active bar in [m - 97 days,
            m - 90 days]) AND no run of 7 or more consecutive 24-hour blocks without an active bar reaches
            into the 90 days before m (a run that started earlier counts with its full visible length).
            A relisted name or a delisting gap of 7+ days restarts the seasoning (B4); a shorter archive
            hole does not (the ACTIVE rule may still exclude the symbol for the next month);
  ACTIVE    active on at least 95% of the 720 hours before m;
  SCORE     the median, over the 90 days before m, of the day's quote volume (inactive bars count 0).
  Eligible = crypto_perpetual, seasoned and active. Ranked by score (ties by name): `top30` = ranks 1-30,
  `next30` = ranks 31-60. A month with fewer than 10 eligible symbols has no top30 unit; a month with fewer
  than 10 symbols ranked 31-60 has no next30 unit. A month whose 97-day read window starts before the
  data supplied is UNKNOWN (start cuts: the unit is unknown there, never different).
A row's decision is taken at its close, so the membership in force at row t is that of the month
containing t + 1 hour (the last row of a month already trades the next month's members).

TRADABLE (R2). A member is tradable at row t when its bar at t is active AND its latest funding settlement
visible at t is no older than twice that settlement's own interval (a symbol the engine cannot charge
funding on is not held). Only tradable members are IN PLAY. No *_SETTLED folder is read: a symbol whose
funding is missing from its own folder is simply out of play while it is missing (recorded, not repaired).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

from omr import constants as C
from omr import paths as P

HOUR_NS = 3_600_000_000_000
DAY_NS = 24 * HOUR_NS
LISTING = "https://s3-ap-northeast-1.amazonaws.com/data.binance.vision"   # the public bucket behind data.binance.vision
S3_NS = "{http://s3.amazonaws.com/doc/2006-03-01/}"
NAME_PATTERN = r"[0-9A-Z]+USDT"
MONTH_PATTERN = r"-1h-(\d{4}-\d{2})\.zip$"


def _name_ok(n: str) -> bool:
    return re.fullmatch(NAME_PATTERN, n) is not None
INDEX_ABSENT = ("BLUEBIRDUSDT", "DOTECOUSDT", "FOOTBALLUSDT")
CLASSES = ("crypto_perpetual", "tradfi_perpetual", "index_contract", "other")
BANDS = {"top30": (0, C.UNIVERSE_TOP), "next30": (C.UNIVERSE_TOP, 2 * C.UNIVERSE_TOP)}
READ_DAYS = C.UNIVERSE_SEASONING_DAYS + C.UNIVERSE_RELIST_GAP_DAYS     # membership reads [m - 97 days, m)
SEASON_BLOCKS = READ_DAYS                                                # (name kept for callers)
ACTIVE_HOURS_MIN = int(np.ceil(C.UNIVERSE_ACTIVE_FRAC * C.UNIVERSE_ACTIVE_DAYS * 24 - 1e-9))
SYMBOLS_FILE = P.DATA_DIR / "symbols.json"
LISTING_DIR = P.RAW_DIR / "listings"


# ---------------------------------------------------------------- symbol table (A1)

def _ms_iso(ms) -> str | None:
    if ms is None:
        return None
    return str(pd.Timestamp(int(ms), unit="ms", tz="UTC").floor("h"))


def classify(name: str, info: dict | None, months: list) -> dict:
    """One symbol-table row. info: the exchangeInfo entry or None (absent); months: sorted 'YYYY-MM' labels
    of the name's monthly 1h klines files."""
    row = {"class": None, "rule": None, "until": None, "exchange_info": None,
           "first_month": months[0] if months else None, "last_month": months[-1] if months else None,
           "n_months": len(months)}
    if info is not None:
        row["exchange_info"] = {k: info.get(k) for k in ("contractType", "underlyingType", "quoteAsset", "status")}
        row["exchange_info"]["onboard"] = _ms_iso(info.get("onboardDate"))
        ct, ut, q = info.get("contractType"), info.get("underlyingType"), info.get("quoteAsset")
        if ct == "TRADIFI_PERPETUAL":
            onboard = pd.Timestamp(int(info["onboardDate"]), unit="ms", tz="UTC").floor("h")
            if months and months[0] < onboard.strftime("%Y-%m"):
                row.update({"class": "crypto_perpetual", "rule": "R1 name reused by a TradFi perpetual: the earlier "
                            "series is a crypto perpetual whose rows end before the TradFi onboard hour",
                            "until": str(onboard)})
            else:
                row.update({"class": "tradfi_perpetual", "rule": "R1 contractType TRADIFI_PERPETUAL"})
        elif ct == "PERPETUAL" and q == "USDT" and ut == "COIN":
            row.update({"class": "crypto_perpetual", "rule": "R1 PERPETUAL, USDT, underlying COIN"})
        elif ut == "INDEX":
            row.update({"class": "index_contract", "rule": "R1 underlyingType INDEX"})
        else:
            row.update({"class": "other", "rule": f"R1 contractType {ct}, underlyingType {ut}"})
    elif name in INDEX_ABSENT:
        row.update({"class": "index_contract", "rule": "R2 absent from exchangeInfo; a named index contract"})
    else:
        row.update({"class": "crypto_perpetual", "rule": "R2 absent from exchangeInfo: an ended coin contract"})
    return row


def build_table(exchange_info: dict, monthly_names, daily_names, months_by_name: dict, meta: dict) -> dict:
    """The symbol table from an exchangeInfo body and the archive's klines folder names (pure)."""
    info = {s["symbol"]: s for s in exchange_info.get("symbols", [])}
    names = sorted(set(monthly_names) | set(daily_names))
    rows, excluded = {}, {}
    for n in names:
        if not _name_ok(n):
            key = ("dated_delivery" if re.match(r"^[0-9A-Z]+_\d{6}$", n) else
                   "settled_copy" if "SETTLED" in n else "other_quote_or_name")
            excluded[key] = excluded.get(key, 0) + 1
            continue
        rows[n] = classify(n, info.get(n), sorted(months_by_name.get(n, [])))
        if rows[n]["class"] == "crypto_perpetual":
            rows[n]["months"] = sorted(months_by_name.get(n, []))
    counts = {c: sum(1 for r in rows.values() if r["class"] == c) for c in CLASSES}
    counts["crypto_perpetual_with_monthly_files"] = sum(1 for r in rows.values()
                                                       if r["class"] == "crypto_perpetual" and r["n_months"])
    return {"version": 1, **meta, "rules": __doc__.split("ACTIVITY (A2)")[0].split("SYMBOL TABLE (A1).")[1].strip(),
            "counts": counts, "excluded_folder_names": excluded, "symbols": rows}


def _list(prefix: str, cache: Path, log) -> dict:
    """One S3 listing (all pages) of `prefix` with delimiter '/', cached as JSON under data/raw/listings."""
    from omr import data
    cache.mkdir(parents=True, exist_ok=True)
    path = cache / (prefix.replace("/", "__") + ".json")
    if path.exists():
        return json.loads(path.read_text(encoding="ascii"))
    keys, prefixes, marker = [], [], None
    while True:
        params = {"prefix": prefix, "delimiter": "/"}
        if marker:
            params["marker"] = marker
        body = data.http_get(LISTING, params=params)
        if body is None:
            raise RuntimeError(f"listing returned 404: {prefix}")
        root = ET.fromstring(body)
        for c in root.findall(S3_NS + "Contents"):
            keys.append([c.find(S3_NS + "Key").text, int(c.find(S3_NS + "Size").text)])
        for p in root.findall(S3_NS + "CommonPrefixes"):
            prefixes.append(p.find(S3_NS + "Prefix").text)
        time.sleep(C.DOWNLOAD_PAUSE_S)
        if (root.find(S3_NS + "IsTruncated").text or "").strip().lower() != "true":
            break
        nm = root.find(S3_NS + "NextMarker")
        marker = nm.text if (nm is not None and nm.text) else max([k[0] for k in keys[-1:]] + prefixes[-1:])
    out = {"prefix": prefix, "keys": keys, "prefixes": prefixes}
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(out), encoding="ascii")
    tmp.replace(path)
    return out


def build_symbols(log=print, cache: Path | None = None) -> dict:
    """Network: exchangeInfo + archive listing -> data/symbols.json."""
    from omr import data
    import hashlib
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    cache = cache or (LISTING_DIR / stamp[:8])
    raw = data.http_get(f"{data.FAPI}/exchangeInfo")
    if raw is None:
        raise RuntimeError("exchangeInfo returned 404")
    P.RAW_DIR.mkdir(parents=True, exist_ok=True)
    ei_path = P.RAW_DIR / f"exchange_info_{stamp}.json"
    ei_path.write_bytes(raw)
    ei = json.loads(raw)
    mon = _list("data/futures/um/monthly/klines/", cache, log)
    day = _list("data/futures/um/daily/klines/", cache, log)
    mnames = [p.rstrip("/").split("/")[-1] for p in mon["prefixes"]]
    dnames = [p.rstrip("/").split("/")[-1] for p in day["prefixes"]]
    cand = sorted(n for n in set(mnames) if _name_ok(n))
    log(f"archive klines folders: monthly {len(mnames)}, daily {len(dnames)}; listing {len(cand)} *USDT names")
    months = {}
    for i, n in enumerate(cand):
        lst = _list(f"data/futures/um/monthly/klines/{n}/1h/", cache, log)
        months[n] = sorted({m.group(1) for k, _ in lst["keys"] for m in [re.search(MONTH_PATTERN, k)] if m})
        if (i + 1) % 100 == 0:
            log(f"  listed {i + 1}/{len(cand)}")
    meta = {"built_at": stamp, "exchange_info_file": ei_path.name,
            "exchange_info_sha256": hashlib.sha256(raw).hexdigest(),
            "exchange_info_server_time": _ms_iso(ei.get("serverTime")), "listing": LISTING,
            "listing_prefix": "data/futures/um/{monthly,daily}/klines/"}
    table = build_table(ei, mnames, dnames, months, meta)
    SYMBOLS_FILE.parent.mkdir(parents=True, exist_ok=True)
    SYMBOLS_FILE.write_text(json.dumps(table, indent=1, sort_keys=True), encoding="ascii")
    log(f"wrote {SYMBOLS_FILE.name}: " + ", ".join(f"{k} {v}" for k, v in table["counts"].items()))
    return table


def load_symbols(path: Path | None = None, check: bool = True) -> dict:
    """data/symbols.json, hash-checked against the manifest pin when check is True."""
    from omr import data
    path = path or SYMBOLS_FILE
    raw = Path(path).read_bytes()
    if check:
        import hashlib
        pin = data.load_manifest().get("universe", {}).get("symbols_sha256")
        if pin is None or hashlib.sha256(raw).hexdigest() != pin:
            raise data.DataIntegrityError("data/symbols.json does not match the manifest pin")
    return json.loads(raw.decode("ascii"))


def crypto_symbols(table: dict) -> list:
    return sorted(n for n, r in table["symbols"].items() if r["class"] == "crypto_perpetual" and r["n_months"])


# ---------------------------------------------------------------- activity (A2)

@dataclass
class Activity:
    """One symbol's history: contiguous hourly rows from `start` (its first active bar, open time ns) to its
    last stored row, the active flag (trades > 0), the quote volume (0 where inactive) and the usable flag."""
    start: int
    active: np.ndarray
    qv: np.ndarray
    usable: np.ndarray = None

    def __post_init__(self):
        if self.usable is None:
            self.usable = self.active.copy()

    @property
    def ns(self) -> np.ndarray:
        return self.start + HOUR_NS * np.arange(len(self.active), dtype=np.int64)

    @property
    def end(self) -> int:
        return self.start + HOUR_NS * (len(self.active) - 1)


def usable_of(active: np.ndarray, present: np.ndarray) -> np.ndarray:
    """S3: active, or present with zero trades while the run of consecutive non-active bars ending there is
    at most UNIVERSE_ZERO_TRADE_MAX (absent bars count in the run and are never usable)."""
    idx = np.arange(len(active))
    last_act = np.maximum.accumulate(np.where(active, idx, -1))
    run = idx - last_act                                      # non-active bars ending at t (0 when active)
    return active | (present & (last_act >= 0) & (run <= C.UNIVERSE_ZERO_TRADE_MAX))


def activity_of(klines: pd.DataFrame, until: str | None = None) -> Activity:
    """From a stored (gridded) klines table: active = row present (not a gap row) and trades > 0; usable per
    S3. Rows at or after `until` are dropped; the history starts at the first active bar."""
    from omr import data
    ns = data.ns_int(klines.index)
    if len(ns) > 1 and not bool(np.all(np.diff(ns) == HOUR_NS)):
        raise ValueError("klines rows must be a contiguous hourly grid")
    tr = klines["trades"].to_numpy(dtype=np.float64)
    gap = klines["is_gap"].to_numpy(dtype=bool) if "is_gap" in klines else np.zeros(len(ns), dtype=bool)
    act = (~gap) & np.isfinite(tr) & (tr > 0)
    if until is not None:
        keep = ns < data.ts(until).value
        ns, act, tr = ns[keep], act[keep], tr[keep]
    qv = klines["quote_volume"].to_numpy(dtype=np.float64)[: len(ns)]
    if not act.any():
        return Activity(0, np.zeros(0, dtype=bool), np.zeros(0))
    i0 = int(np.argmax(act))
    sl = slice(i0, len(act))
    a = act[sl]
    pres = (~gap)[: len(act)][sl]
    return Activity(int(ns[i0]), a.copy(), np.where(a, np.nan_to_num(qv[sl], nan=0.0), 0.0), usable_of(a, pres))


def rows_in(a: Activity, lo_ns: int, hi_ns: int) -> tuple:
    """(i0, i1): the slice of a's rows with lo <= open time <= hi."""
    n = len(a.active)
    if n == 0:
        return 0, 0
    i0 = max(0, -(-(lo_ns - a.start) // HOUR_NS))
    i1 = min(n, (hi_ns - a.start) // HOUR_NS + 1)
    return int(i0), int(max(i0, i1))


# ---------------------------------------------------------------- membership (B)

def month_starts(lo_ns: int, hi_ns: int) -> np.ndarray:
    """First hours (ns) of every calendar month m with lo <= m <= hi + 1 hour (the month of the last row's
    decision time included)."""
    a = pd.Timestamp(int(lo_ns), tz="UTC")
    b = pd.Timestamp(int(hi_ns) + HOUR_NS, tz="UTC")
    first = pd.Timestamp(year=a.year, month=a.month, day=1, tz="UTC")
    if first.value < lo_ns:
        first = first + pd.offsets.MonthBegin(1)
    ms = pd.date_range(first, b, freq="MS")
    return np.asarray(ms.as_unit("ns").asi8, dtype=np.int64)


@dataclass
class Membership:
    months: np.ndarray                 # month starts (ns)
    known: np.ndarray                  # bool per month: the 97-day read window lies inside the data supplied
    ranked: list                       # per month: eligible symbols in rank order (empty when unknown)
    scores: list                       # per month: {symbol: score} of the eligible symbols
    n_crypto: list = field(default_factory=list)

    def members(self, band: str, i: int) -> tuple:
        a, b = BANDS[band]
        r = self.ranked[i]
        sel = tuple(r[a:b])
        return sel if len(sel) >= C.UNIVERSE_MIN_MEMBERS else ()

    def unit_exists(self, band: str, i: int) -> bool:
        return bool(self.known[i]) and len(self.members(band, i)) > 0

    def ever(self, band: str) -> list:
        out = set()
        for i in range(len(self.months)):
            out.update(self.members(band, i))
        return sorted(out)


def daily_matrix(acts: dict, names: list, lo_ns: int, hi_ns: int):
    """Per symbol and UTC day in [lo, hi]: active-hour count, quote-volume sum and whether the day's first
    hour is active, from the rows with lo <= open time <= hi only.
    Returns (day0 index, n_active (D x S) int16, qv (D x S) float64, first_hour_active (D x S) bool)."""
    d0 = lo_ns // DAY_NS
    d1 = hi_ns // DAY_NS
    D = int(d1 - d0 + 1)
    na = np.zeros((D, len(names)), dtype=np.int16)
    qv = np.zeros((D, len(names)), dtype=np.float64)
    fa = np.zeros((D, len(names)), dtype=bool)
    for j, n in enumerate(names):
        a = acts[n]
        i0, i1 = rows_in(a, lo_ns, hi_ns)
        if i1 <= i0:
            continue
        ns = a.start + HOUR_NS * np.arange(i0, i1, dtype=np.int64)
        day = (ns // DAY_NS - d0).astype(np.int64)
        na[:, j] += np.bincount(day, weights=a.active[i0:i1], minlength=D)[:D].astype(np.int16)
        qv[:, j] += np.bincount(day, weights=a.qv[i0:i1], minlength=D)[:D]
        first = (ns % DAY_NS) == 0
        fa[day[first], j] = a.active[i0:i1][first]
    return int(d0), na, qv, fa


def _seasoned(na_w: np.ndarray, fa_d90: np.ndarray) -> np.ndarray:
    """na_w: active-hour counts of the READ_DAYS day blocks before m (oldest first, D x S); fa_d90: first hour
    of the block starting exactly 90 days before m active. R1a (see the module docstring)."""
    g = C.UNIVERSE_RELIST_GAP_DAYS
    old = na_w[:g] >= 1                                          # blocks [m-97d, m-90d)
    first_ok = old.any(axis=0) | fa_d90
    z = na_w == 0
    run = np.zeros(z.shape[1], dtype=np.int32)
    bad = np.zeros(z.shape[1], dtype=bool)
    for p in range(z.shape[0]):
        run = np.where(z[p], run + 1, 0)
        if p >= g:                                               # a run reaching into the 90-day window
            bad |= run >= g
    return first_ok & ~bad


def membership(acts: dict, eligible_names, lo_ns: int, hi_ns: int, months: np.ndarray | None = None) -> Membership:
    """Membership for every month start in `months` (default: month_starts(lo, hi)) from the activity of
    `eligible_names` (crypto perpetuals) restricted to bars with lo <= open time <= hi."""
    names = sorted(eligible_names)
    if months is None:
        months = month_starts(lo_ns, hi_ns)
    d0, na, qv, fa = daily_matrix(acts, names, lo_ns, hi_ns)
    D = na.shape[0]
    known = np.zeros(len(months), dtype=bool)
    ranked, scores = [], []
    for i, m in enumerate(months):
        dm = int(m // DAY_NS) - d0
        ok = (m - SEASON_BLOCKS * DAY_NS >= lo_ns) and (m - HOUR_NS <= hi_ns) and dm - SEASON_BLOCKS >= 0 and dm <= D
        known[i] = ok
        if not ok:
            ranked.append([])
            scores.append({})
            continue
        seasoned = _seasoned(na[dm - READ_DAYS:dm], fa[dm - C.UNIVERSE_SEASONING_DAYS])
        act = na[dm - C.UNIVERSE_ACTIVE_DAYS:dm].sum(axis=0) >= ACTIVE_HOURS_MIN
        el = np.nonzero(seasoned & act)[0]
        sc = np.median(qv[dm - C.UNIVERSE_LIQ_DAYS:dm, el], axis=0) if len(el) else np.zeros(0)
        order = sorted(range(len(el)), key=lambda k: (-sc[k], names[el[k]]))
        ranked.append([names[el[k]] for k in order])
        scores.append({names[el[k]]: float(sc[k]) for k in order})
    return Membership(months=np.asarray(months, dtype=np.int64), known=known, ranked=ranked, scores=scores)


def funding_fresh(grid_ns: np.ndarray, settle_ns: np.ndarray, interval_h: np.ndarray) -> np.ndarray:
    """R2 per row: the latest settlement visible at the row (settle hour <= row) is at most 2 x its own
    interval old. settle_ns: settlement hours (ns, sorted); interval_h: their intervals in hours."""
    settle_ns = np.asarray(settle_ns, dtype=np.int64)
    if len(settle_ns) == 0:
        return np.zeros(len(grid_ns), dtype=bool)
    iv = np.asarray(interval_h, dtype=np.float64)
    idx = np.searchsorted(settle_ns, grid_ns, side="right") - 1
    ok = idx >= 0
    j = np.where(ok, idx, 0)
    lim = np.where(np.isfinite(iv[j]) & (iv[j] > 0), 2.0 * iv[j] * HOUR_NS, -1.0)
    return ok & ((grid_ns - settle_ns[j]).astype(np.float64) <= lim)


def inplay_matrix(mem: Membership, band: str, grid_ns: np.ndarray, panel: list, active: np.ndarray):
    """(inplay T x K, unit_known T): a symbol is IN PLAY at row t when it is a member of `band` for the
    month containing t + 1 hour and its bar at t is active (D2). unit_known: that month's membership is
    known and the unit exists."""
    T = len(grid_ns)
    mi = np.searchsorted(mem.months, grid_ns + HOUR_NS, side="right") - 1
    col = {s: k for k, s in enumerate(panel)}
    P_ = np.zeros((T, len(panel)), dtype=bool)
    uk = np.zeros(T, dtype=bool)
    for i in np.unique(mi):
        rows = mi == i
        if i < 0 or not mem.known[i]:
            continue
        mem_i = mem.members(band, int(i))
        if not mem_i:
            continue
        uk[rows] = True
        for s in mem_i:
            if s in col:
                P_[rows, col[s]] = True
    return P_ & active, uk


OVERLAP_HOURS = READ_DAYS * 24                  # S4 block warm-up (upipeline checks it)


def block_plan(mem: Membership, grid_ns: np.ndarray, band: str, months=C.UNIVERSE_BLOCK_MONTHS,
               boundaries=None) -> list:
    """S4 blocks of a band's panel on grid_ns: [{b, e, s0, symbols}] with rows [b, e) evaluated from row s0
    (97 days before the first hour of the month holding row b's decision time) and the symbols that are
    members (full-grid membership) in any month touched by the decision rows of the evaluated range
    s0 .. e-1, warm-up included (fix pass 3: no dependence on the previous block)."""
    Tn = len(grid_ns)
    cuts = [0]
    if boundaries is not None:
        cuts += sorted(int(b) for b in boundaries if 0 < int(b) < Tn)
    elif months is not None:
        for m in month_starts(int(grid_ns[0]), int(grid_ns[-1])):
            t = pd.Timestamp(int(m), tz="UTC")
            if grid_ns[0] < m <= grid_ns[-1] and (t.month - 1) % months == 0:
                cuts.append(int((m - grid_ns[0]) // HOUR_NS))
    cuts.append(Tn)
    out = []
    for k, (b, e) in enumerate((a, c) for a, c in zip(cuts[:-1], cuts[1:]) if c > a):
        if k == 0:
            s0 = 0
        else:
            t = pd.Timestamp(int(grid_ns[b]) + HOUR_NS, tz="UTC")
            m0 = pd.Timestamp(year=t.year, month=t.month, day=1, tz="UTC").value
            s0 = max(0, int((m0 - OVERLAP_HOURS * HOUR_NS - grid_ns[0]) // HOUR_NS))
        mi = np.searchsorted(mem.months, grid_ns[s0:e] + HOUR_NS, side="right") - 1
        syms = set()
        for i in np.unique(mi):
            if i >= 0:
                syms.update(mem.members(band, int(i)))
        out.append({"b": int(b), "e": int(e), "s0": s0, "symbols": syms})
    return out


def stage2_sizes(acts: dict, mem: Membership, lo_ns: int, hi_ns: int) -> dict:
    """Counts the evaluator's stage-2 memory estimate needs (omr.upipeline.stage2_memory_estimate)."""
    union = set(mem.ever("top30")) | set(mem.ever("next30"))
    grid = np.arange(lo_ns, hi_ns + 1, HOUR_NS, dtype=np.int64)
    months = {"top30": C.UNIVERSE_BLOCK_MONTHS, "next30": C.UNIVERSE_BLOCK_MONTHS_G8}
    blocks = {band: [[int(x["e"] - x["s0"]), int(x["e"] - max(x["b"] - 1, 0)), len(x["symbols"])]
                     for x in block_plan(mem, grid, band, months=months[band])] for band in BANDS}
    rows_of = {s: int(np.subtract(*rows_in(acts[s], lo_ns, hi_ns)[::-1])) for s in union}
    return {"rows": int((hi_ns - lo_ns) // HOUR_NS + 1), "top30": len(mem.ever("top30")),
            "next30": len(mem.ever("next30")), "symbol_rows": int(sum(rows_of.values())),
            "symbol_rows_max": int(max(rows_of.values())) if rows_of else 0,
            "crypto_rows": int(sum(len(a.active) for a in acts.values())), "blocks": blocks}


def market_wide_hours(presence: dict, lo_ns: int, hi_ns: int) -> list:
    """S3 fact: hours in [lo, hi] at which no symbol with a history has a trade. presence: {symbol: (start ns,
    present bool array, active bool array)} over each symbol's history. Returns [{hour, symbols_with_history,
    rows_present_zero_trades, rows_absent}]."""
    n = int((hi_ns - lo_ns) // HOUR_NS + 1)
    hist = np.zeros(n, dtype=np.int32)
    act = np.zeros(n, dtype=np.int32)
    zero = np.zeros(n, dtype=np.int32)
    for st, pres, a in presence.values():
        i0 = max(0, int((lo_ns - st) // HOUR_NS))
        i1 = min(len(a), int((hi_ns - st) // HOUR_NS) + 1)
        if i1 <= i0:
            continue
        p0 = int((st + i0 * HOUR_NS - lo_ns) // HOUR_NS)
        sl = slice(p0, p0 + i1 - i0)
        hist[sl] += 1
        act[sl] += a[i0:i1]
        zero[sl] += pres[i0:i1] & ~a[i0:i1]
    rows = np.nonzero((hist > 0) & (act == 0))[0]
    return [{"hour": str(pd.Timestamp(int(lo_ns + r * HOUR_NS), tz="UTC")), "symbols_with_history": int(hist[r]),
             "rows_present_zero_trades": int(zero[r]), "rows_absent": int(hist[r] - zero[r])} for r in rows]


def membership_counts(acts: dict, lo_ns: int, hi_ns: int, lookbacks_h=(1, 24, 168, 720, 2160),
                      funding: dict | None = None) -> dict:
    """COUNTS only (data validate): members per month, distinct symbols ever in each band within the
    DEV and VAL regions, the first month with a top30 unit, R2 (member-months and hours removed because
    funding is stale, by symbol), and UNIT AVAILABILITY on the hours of DEV and VAL at which the top30 unit
    exists: hours with every member in play; hours with every in-play member active on all of its last L
    hours (strict cross-sections: a klines-only program of lookback L is known); hours with at least 10
    in-play members whose last L hours are all active (the R1b proposal). funding: {symbol: (settle ns,
    interval hours)}; None = funding not checked."""
    mem = membership(acts, list(acts), lo_ns, hi_ns)
    months = [pd.Timestamp(int(m), tz="UTC").strftime("%Y-%m") for m in mem.months]
    out = {"months": {lab: {"known": int(mem.known[i]), "eligible": len(mem.ranked[i]),
                            "top30": len(mem.members("top30", i)), "next30": len(mem.members("next30", i))}
                      for i, lab in enumerate(months)}}
    first = [lab for i, lab in enumerate(months) if mem.unit_exists("top30", i)]
    out["first_top30_month"] = first[0] if first else None
    regions = {"dev": (C.DEV_START, C.DEV_END), "val": (C.VAL_START, C.VAL_END)}
    ever = {}
    for reg, (a, b) in regions.items():
        ia = int(np.searchsorted(mem.months, pd.Timestamp(a, tz="UTC").value))
        ib = int(np.searchsorted(mem.months, pd.Timestamp(b, tz="UTC").value + HOUR_NS, side="right"))
        for band in BANDS:
            ever[f"{band}_{reg}"] = len({s for i in range(ia, ib) for s in mem.members(band, i)})
    ever["top30_dev_val"] = len(set(mem.ever("top30")))
    ever["next30_dev_val"] = len(set(mem.ever("next30")))
    out["distinct_symbols"] = ever
    out["stage2_sizes"] = stage2_sizes(acts, mem, lo_ns, hi_ns)
    syms = mem.ever("top30")
    grid = np.arange(pd.Timestamp(C.DEV_START, tz="UTC").value, hi_ns + 1, HOUR_NS, dtype=np.int64)
    run = np.zeros((len(grid), len(syms)), dtype=np.int32)          # consecutive USABLE hours ending at t (S3)
    for k, s in enumerate(syms):
        a = acts[s]
        act = np.zeros(len(grid), dtype=bool)
        i0, i1 = rows_in(a, int(grid[0]), int(grid[-1]))
        if i1 > i0:
            p0 = (a.start + i0 * HOUR_NS - grid[0]) // HOUR_NS
            act[p0:p0 + (i1 - i0)] = a.usable[i0:i1]
        pre = a.usable[max(0, i0 - 3000):i0] if (i1 > i0 and p0 == 0) else np.zeros(0, dtype=bool)
        c0 = len(pre) - 1 - int(np.nonzero(~pre)[0][-1]) if (~pre).any() else len(pre)   # active run before DEV start
        idx = np.arange(len(grid))
        last_off = np.maximum.accumulate(np.where(~act, idx, -1))
        run[:, k] = np.where(last_off >= 0, idx - last_off, idx + 1 + c0)
    mi = np.searchsorted(mem.months, grid + HOUR_NS, side="right") - 1
    member = np.zeros((len(grid), len(syms)), dtype=bool)
    col = {s: k for k, s in enumerate(syms)}
    for i in np.unique(mi):
        if i >= 0 and mem.unit_exists("top30", int(i)):
            rows = mi == i
            for s in mem.members("top30", int(i)):
                member[rows, col[s]] = True
    fresh = np.ones((len(grid), len(syms)), dtype=bool)
    if funding is not None:
        for k, s in enumerate(syms):
            st, iv = funding.get(s, (np.zeros(0, dtype=np.int64), np.zeros(0)))
            fresh[:, k] = funding_fresh(grid, st, iv)
    has_unit = member.any(axis=1)
    avail, removed = {}, {}
    for reg, (a, b) in regions.items():
        m = has_unit & (grid >= pd.Timestamp(a, tz="UTC").value) & (grid <= pd.Timestamp(b, tz="UTC").value)
        active_member = member & (run >= 1)
        inplay = active_member & fresh
        n_clean = {L: (inplay & (run >= L)).sum(axis=1) for L in lookbacks_h}
        row = {"hours_with_unit": int(m.sum()),
               "all_members_in_play": int((m & ~np.any(member & ~((run >= 1) & fresh), axis=1)).sum()),
               "members_in_play_mean_x100": int(round(100 * float(inplay[m].sum(axis=1).mean()))) if m.any() else 0}
        for L in lookbacks_h:
            row[f"strict_all_in_play_clean_last_{L}h"] = int((m & ~np.any(inplay & (run < L), axis=1)).sum())
        for L in lookbacks_h:
            row[f"s2_at_least_10_clean_last_{L}h"] = int((m & (n_clean[L] >= C.UNIVERSE_MIN_CS)).sum())
        avail[reg] = row
        # R2: member-months (and member-hours) in which an ACTIVE member was out of play for stale funding
        stale = m[:, None] & active_member & ~fresh
        rr = {}
        for k, s in enumerate(syms):
            if not stale[:, k].any():
                continue
            months_k = mi[stale[:, k]]
            full = 0
            for i in np.unique(months_k):
                rows_i = m & (mi == i) & active_member[:, k]
                if rows_i.any() and not (rows_i & fresh[:, k]).any():
                    full += 1
            rr[s] = {"member_months_fully_removed": int(full), "member_months_touched": int(len(np.unique(months_k))),
                     "member_hours_removed": int(stale[:, k].sum())}
        removed[reg] = rr
    out["top30_unit_availability"] = avail
    out["r2_funding_removed"] = removed
    return out


# ---------------------------------------------------------------- CLI

def _load_acts(table: dict, handle, log=print) -> dict:
    from omr import datasets as D
    acts = {}
    for n in crypto_symbols(table):
        try:
            kl = D.load_raw("klines", n, upto="val_end", handle=handle)
        except FileNotFoundError:
            continue
        acts[n] = activity_of(kl, table["symbols"][n].get("until"))
    return acts


def members_report(log=print) -> dict:
    """Membership over every month from the universe start to the vault end; prints counts only."""
    from omr import access
    table = load_symbols()
    handle = access.for_membership("membership builder: counts of members per month over all regions; "
                                   "no program is evaluated")
    acts = _load_acts(table, handle)
    lo = pd.Timestamp(C.UNIVERSE_START, tz="UTC").value
    hi = pd.Timestamp(C.VAL_END, tz="UTC").value
    mem = membership(acts, list(acts), lo, hi)
    out = {"months": [], "ever": {b: len(mem.ever(b)) for b in BANDS}}
    for i, m in enumerate(mem.months):
        lab = pd.Timestamp(int(m), tz="UTC").strftime("%Y-%m")
        row = {"month": lab, "known": bool(mem.known[i]), "eligible": len(mem.ranked[i]),
               "top30": len(mem.members("top30", i)), "next30": len(mem.members("next30", i))}
        out["months"].append(row)
        log(f"{lab}  known {int(row['known'])}  eligible {row['eligible']:4d}  top30 {row['top30']:2d}  "
            f"next30 {row['next30']:2d}")
    log(f"distinct symbols ever in top30 {out['ever']['top30']}, in next30 {out['ever']['next30']} "
        f"(months {pd.Timestamp(int(mem.months[0]), tz='UTC'):%Y-%m} .. {pd.Timestamp(int(mem.months[-1]), tz='UTC'):%Y-%m})")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m omr.universe")
    ap.add_argument("cmd", choices=["symbols", "members"])
    a = ap.parse_args(argv)
    if a.cmd == "symbols":
        build_symbols(log=lambda s: print(s, flush=True))
    else:
        members_report(log=lambda s: print(s, flush=True))


if __name__ == "__main__":
    sys.exit(main())
