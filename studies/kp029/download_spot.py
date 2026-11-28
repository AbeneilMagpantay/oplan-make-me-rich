"""KP-029 premise study, STAGE 2 ONLY: the spot downloader. Written in stage 1, NOT run in stage 1.

    .venv\\Scripts\\python.exe -I studies\\kp029\\download_spot.py            (prints the plan; no network)
    .venv\\Scripts\\python.exe -I studies\\kp029\\download_spot.py --go       (stage 2: downloads; resumable)

What it fetches: for every spot pair and month in studies/kp029/spot_symbols.json (made by spot_plan.py from the
kernel's DEV membership: the pairs of every perpetual ever in top30 or next30 on DEV, months from 97 days before
its first member month to its last, clipped to 2019-12 .. 2022-06), the monthly 1h klines file
    https://data.binance.vision/data/spot/monthly/klines/<SYM>/1h/<SYM>-1h-<YYYY>-<MM>.zip
and its .CHECKSUM. The checksum file is fetched first: 404 means the month is not in the archive (recorded as
absent, no zip request). The zip's sha256 must equal the checksum, else it is not kept. Files go to
_build/kp029_study/spot/<SYM>/ (git-ignored), written as .part and renamed when verified; a verified file already
there is not fetched again.

The rules, hard-coded: no URL of a month after 2022-06 (or before 2019-12) can be built (kp029_spot.url raises);
one connection (one requests.Session, pool size 1, requests strictly one after another); a pause of at least
0.2 s between any two requests; a generic User-Agent "research-data-client/1.0" and no other identifying header;
no key, account or personal detail; only data.binance.vision. A log of every request's outcome (pair, month,
status, size, sha256; no data row) goes to _build/kp029_study/spot/download_log.jsonl. Prints counts only.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
for p in (str(ROOT), str(HERE)):
    if p not in sys.path:
        sys.path.insert(0, p)

import kp029_spot as SP  # noqa: E402

UA = "research-data-client/1.0"
PAUSE_S = 0.25                      # >= 0.2 s between requests
TIMEOUT_S = 60
RETRIES = 3
PLAN = HERE / "spot_symbols.json"


class Client:
    """One connection, one request at a time, a pause before every request."""

    def __init__(self):
        import requests
        from requests.adapters import HTTPAdapter
        self.requests = requests
        self.s = requests.Session()
        self.s.headers.clear()
        self.s.headers.update({"User-Agent": UA, "Accept-Encoding": "identity"})
        ad = HTTPAdapter(pool_connections=1, pool_maxsize=1, max_retries=0, pool_block=True)
        self.s.mount("https://", ad)
        self.s.mount("http://", ad)
        self.last = 0.0
        self.n = 0

    def get(self, url: str):
        if not url.startswith(SP.BASE_URL + "/"):
            raise ValueError(f"refused: not the archive's spot klines path: {url}")
        for attempt in range(RETRIES + 1):
            wait = PAUSE_S - (time.monotonic() - self.last)
            if wait > 0:
                time.sleep(wait)
            self.last = time.monotonic()
            self.n += 1
            try:
                r = self.s.get(url, timeout=TIMEOUT_S, allow_redirects=False)
            except (self.requests.ConnectionError, self.requests.Timeout):
                if attempt == RETRIES:
                    raise
                time.sleep(2 ** (attempt + 1))
                continue
            if r.status_code >= 500 and attempt < RETRIES:
                time.sleep(2 ** (attempt + 1))
                continue
            return r
        raise RuntimeError("unreachable")


def plan_items() -> list:
    plan = json.loads(PLAN.read_text(encoding="ascii"))
    items = []
    for sym, months in sorted(plan["pairs"].items()):
        for ymstr in months:
            y, m = int(ymstr[:4]), int(ymstr[5:])
            if not SP.month_allowed(y, m):
                raise SP.CeilingError(f"plan holds a month outside the window: {sym} {ymstr}")
            items.append((sym, y, m))
    return items


def verified(d: Path, sym: str, y: int, m: int) -> bool:
    name = SP.zip_name(sym, y, m)
    z, c = d / name, d / (name + ".CHECKSUM")
    if not (z.exists() and c.exists()):
        return False
    try:
        return SP.sha256_bytes(z.read_bytes()) == SP.checksum_of(c.read_text(encoding="ascii"), name)
    except ValueError:
        return False


def main(argv=None):
    ap = argparse.ArgumentParser(prog="download_spot.py")
    ap.add_argument("--go", action="store_true", help="stage 2 only: download")
    a = ap.parse_args(argv)
    items = plan_items()
    pairs = sorted({s for s, _, _ in items})
    print(f"plan: {len(pairs)} spot pairs, {len(items)} monthly files (+ {len(items)} checksum files), months "
          f"2019-12 .. 2022-06 only; about {2 * len(items) * (PAUSE_S + 0.25) / 60:.0f} minutes at one request per "
          f"{PAUSE_S + 0.25:.2f} s")
    if not a.go:
        print("no --go: nothing fetched")
        return
    SP.SPOT_ROOT.mkdir(parents=True, exist_ok=True)
    log = SP.SPOT_ROOT / "download_log.jsonl"
    cl = Client()
    counts = {"kept": 0, "already": 0, "absent": 0, "bad_checksum": 0, "http_error": 0}
    with open(log, "a", encoding="ascii", newline="\n") as lf:
        for sym, y, m in items:
            d = SP.SPOT_ROOT / sym
            d.mkdir(exist_ok=True)
            name = SP.zip_name(sym, y, m)
            if verified(d, sym, y, m):
                counts["already"] += 1
                continue
            rec = {"pair": sym, "month": f"{y:04d}-{m:02d}", "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
            rc = cl.get(SP.url(sym, y, m, checksum=True))
            if rc.status_code == 404:
                rec["status"] = "absent"
                counts["absent"] += 1
            elif rc.status_code != 200:
                rec["status"] = f"http {rc.status_code} (checksum)"
                counts["http_error"] += 1
            else:
                want = SP.checksum_of(rc.content.decode("ascii"), name)
                rz = cl.get(SP.url(sym, y, m))
                if rz.status_code != 200:
                    rec["status"] = f"http {rz.status_code} (zip)"
                    counts["http_error"] += 1
                elif SP.sha256_bytes(rz.content) != want:
                    rec["status"] = "bad_checksum"
                    counts["bad_checksum"] += 1
                else:
                    part = d / (name + ".part")
                    part.write_bytes(rz.content)
                    part.replace(d / name)
                    (d / (name + ".CHECKSUM")).write_bytes(rc.content)
                    rec.update(status="kept", size=len(rz.content), sha256=want)
                    counts["kept"] += 1
            lf.write(json.dumps(rec, sort_keys=True) + "\n")
            lf.flush()
    print(f"requests {cl.n}; {counts}")


if __name__ == "__main__":
    main()
