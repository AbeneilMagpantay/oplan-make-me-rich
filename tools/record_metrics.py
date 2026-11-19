"""Forward recorder of Binance USD-M daily `metrics` files (open interest, long/short ratios). NOT kernel code.

    python tools/record_metrics.py [--symbols BTCUSDT,ETHUSDT] [--days 7] [--recheck]
                                   [--dir data/metrics_raw] [--log records/metrics_first_seen.jsonl]

Why: the feasibility study (notes/kp015_feasibility.md) found the archive's metrics files backfilled and
rewritten after the fact, so they are inadmissible as history. They can only be used FORWARD, from copies
this project stores itself with the hash it saw first.

What it does, per symbol and UTC day (the last --days complete days; the archive publishes about a day late):
- downloads data/futures/um/daily/metrics/<SYM>/<SYM>-metrics-<YYYY-MM-DD>.zip from data.binance.vision
  (generic User-Agent, a short pause between requests) and verifies the published .CHECKSUM;
- stores the bytes under --dir (data/ is untracked) the first time a file is seen, and appends one row
  {"event": "first_seen", file, symbol, day, sha256, bytes, checksum_ok, at} to the tracked --log;
- a file already in the log is compared with its first-seen sha256 (the stored copy always; with
  --recheck the archive copy is downloaded again): any difference is REPORTED and logged as
  {"event": "revised", file, first_sha256, sha256, where, at}; the first-seen copy is never overwritten
  (a revised archive copy is kept beside it as <name>.rev-<sha12>).
The kernel never reads the folder or the log. Exit code 0 = no revision seen, 2 = a revision was reported.
"""
import argparse
import datetime as dt
import hashlib
import json
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
BULK = "https://data.binance.vision/data/futures/um/daily/metrics"
USER_AGENT = "research-data-client/1.0"
DEFAULT_SYMBOLS = ("BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT", "ADAUSDT", "DOGEUSDT", "LTCUSDT",
                   "LINKUSDT", "AVAXUSDT")
PAUSE_S = 0.2


def get(session, url):
    """bytes, or None on 404; raises after retries."""
    last = None
    for attempt in range(5):
        try:
            r = session.get(url, timeout=60)
            if r.status_code == 404:
                return None
            if r.status_code == 200:
                return r.content
            last = f"HTTP {r.status_code}"
        except requests.RequestException as e:
            last = type(e).__name__
        time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"GET failed ({last}): {url}")


def read_log(path: Path) -> dict:
    first = {}
    if path.exists():
        for line in path.read_text(encoding="ascii").splitlines():
            if line.strip():
                r = json.loads(line)
                if r.get("event") == "first_seen" and r["file"] not in first:
                    first[r["file"]] = r
    return first


def append(path: Path, row: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="ascii", newline="\n") as f:
        f.write(json.dumps(row, sort_keys=True) + "\n")


def now():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run(symbols, days: int, folder: Path, log: Path, recheck: bool, session=None, today=None, out=print) -> int:
    session = session or requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    today = today or dt.datetime.now(dt.timezone.utc).date()
    first = read_log(log)
    revised = 0
    counts = {"first_seen": 0, "unchanged": 0, "missing": 0, "revised": 0}
    for sym in symbols:
        for k in range(days, 0, -1):
            day = (today - dt.timedelta(days=k)).isoformat()
            name = f"{sym}-metrics-{day}.zip"
            dest = folder / sym / name
            seen = first.get(name)
            if seen is not None:
                if dest.exists() and hashlib.sha256(dest.read_bytes()).hexdigest() != seen["sha256"]:
                    append(log, {"event": "revised", "file": name, "first_sha256": seen["sha256"],
                                 "sha256": hashlib.sha256(dest.read_bytes()).hexdigest(), "where": "stored copy",
                                 "at": now()})
                    out(f"REVISED (stored copy differs from first seen): {name}")
                    revised += 1
                if not recheck:
                    counts["unchanged"] += 1
                    continue
            url = f"{BULK}/{sym}/{name}"
            body = get(session, url)
            time.sleep(PAUSE_S)
            if body is None:
                counts["missing"] += 1
                continue
            chk = get(session, url + ".CHECKSUM")
            time.sleep(PAUSE_S)
            sha = hashlib.sha256(body).hexdigest()
            ok = chk is not None and chk.decode("ascii", "replace").split()[0].strip().lower() == sha
            if seen is None:
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(body)
                row = {"event": "first_seen", "file": name, "symbol": sym, "day": day, "sha256": sha,
                       "bytes": len(body), "checksum_ok": bool(ok), "at": now()}
                append(log, row)
                first[name] = row
                counts["first_seen"] += 1
            elif sha != seen["sha256"]:
                rev = dest.with_name(f"{name}.rev-{sha[:12]}")
                rev.write_bytes(body)
                append(log, {"event": "revised", "file": name, "first_sha256": seen["sha256"], "sha256": sha,
                             "where": "archive", "at": now()})
                out(f"REVISED (archive bytes differ from first seen): {name}")
                revised += 1
                counts["revised"] += 1
            else:
                counts["unchanged"] += 1
    out("metrics recorder: " + " ".join(f"{k}={v}" for k, v in counts.items()))
    return 2 if revised else 0


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python tools/record_metrics.py")
    ap.add_argument("--symbols", default=",".join(DEFAULT_SYMBOLS))
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--recheck", action="store_true", help="download already-seen files again and compare")
    ap.add_argument("--dir", default=str(ROOT / "data" / "metrics_raw"))
    ap.add_argument("--log", default=str(ROOT / "records" / "metrics_first_seen.jsonl"))
    a = ap.parse_args(argv)
    syms = [s.strip().upper() for s in a.symbols.split(",") if s.strip()]
    return run(syms, a.days, Path(a.dir), Path(a.log), a.recheck)


if __name__ == "__main__":
    sys.exit(main())
