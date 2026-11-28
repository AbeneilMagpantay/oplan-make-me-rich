"""KP-029 premise study, stage 1: the DOWNLOAD PLAN (which spot pairs and months stage 2 may fetch). No network.

    .venv\\Scripts\\python.exe -I studies\\kp029\\spot_plan.py [<cached listing of spot folder names, JSON list>]

From the kernel's own DEV membership (omr.upipeline.load_udata("dev_end"): the activity of every crypto perpetual
under the DEV ceiling, membership over the universe grid 2019-12-31 .. 2022-06-30), it lists every perpetual that
was ever a member of unit top30 or next30 on DEV, its spot pair by the study's symbol map, and the months of spot
rows the study can need for it: from the month holding (its first member month - 97 days: the kernel's block
warm-up, which covers the 90-day lookback limit) to its last member month, clipped to 2019-12 .. 2022-06.
Writes studies/kp029/spot_symbols.json (names, months and counts only; no data row). The optional listing (file
names of the archive's spot folders, cached by the desk study of 2026-11-28) only marks which pairs had a folder.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
for p in (str(ROOT), str(HERE)):
    if p not in sys.path:
        sys.path.insert(0, p)

import pandas as pd  # noqa: E402

from omr import kernel_lock  # noqa: E402
from omr import upipeline as UP  # noqa: E402

import kp029_eval as EV  # noqa: E402
import kp029_spot as SP  # noqa: E402

WARMUP_DAYS = 97


def ym(ts: pd.Timestamp) -> tuple:
    return int(ts.year), int(ts.month)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    listed = None
    if argv:
        listed = set(json.loads(Path(argv[0]).read_text(encoding="utf-8")))
    mem_kb = EV.memory_kb()
    if not EV.memory_ok(mem_kb):
        raise SystemExit(f"memory below the floor: {mem_kb}")
    ud = UP.load_udata("dev_end", fields={"close"})
    g = ud.grid()
    mem = ud.membership(int(g[0].value), int(g[-1].value))
    months = {}
    for i, m in enumerate(mem.months):
        t = pd.Timestamp(int(m), tz="UTC")
        for band in ("top30", "next30"):
            for s in mem.members(band, i):
                d = months.setdefault(s, {"bands": set(), "months": []})
                d["bands"].add(band)
                d["months"].append(t)
    rows, pairs = [], {}
    for s in sorted(months):
        d = months[s]
        first, last = min(d["months"]), max(d["months"])
        w0 = ym(first - pd.Timedelta(days=WARMUP_DAYS))
        w1 = ym(last)
        mlist = SP.months_between(w0, w1)
        sp, mult = SP.spot_symbol(s)
        rows.append({"perp": s, "spot": sp, "mult": mult, "bands": sorted(d["bands"]),
                     "first_member_month": f"{first.year:04d}-{first.month:02d}",
                     "last_member_month": f"{last.year:04d}-{last.month:02d}",
                     "window_first": f"{mlist[0][0]:04d}-{mlist[0][1]:02d}" if mlist else None,
                     "window_last": f"{mlist[-1][0]:04d}-{mlist[-1][1]:02d}" if mlist else None,
                     "n_months": len(mlist), "spot_folder_listed": (sp in listed) if listed is not None else None})
        pairs.setdefault(sp, set()).update(mlist)
    out = {"made_at": EV.now_utc(), "kernel_hash": kernel_lock.kernel_hash(),
           "source": "omr.upipeline.load_udata('dev_end') membership, universe grid 2019-12-31 .. 2022-06-30",
           "warmup_days": WARMUP_DAYS, "first_month": "2019-12", "last_month": "2022-06",
           "n_top30": len(mem.ever("top30")), "n_next30": len(mem.ever("next30")), "n_perps": len(rows),
           "n_spot_pairs": len(pairs), "expected_monthly_files": int(sum(len(v) for v in pairs.values())),
           "listing": None if listed is None else "desk study cache spot_monthly_kline_symbols.json (folder names)",
           "pairs": {k: [f"{y:04d}-{m:02d}" for y, m in sorted(v)] for k, v in sorted(pairs.items())},
           "symbols": rows}
    (HERE / "spot_symbols.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n", encoding="ascii",
                                            newline="\n")
    nolist = [r["perp"] for r in rows if r["spot_folder_listed"] is False]
    print(f"perpetuals ever in top30 {out['n_top30']}, in next30 {out['n_next30']}, union {out['n_perps']}; spot pairs "
          f"{out['n_spot_pairs']}; monthly files planned {out['expected_monthly_files']}")
    print(f"1000-prefixed: {[r['perp'] for r in rows if r['mult'] != 1.0]}")
    print(f"pairs without a spot folder in the cached listing: {nolist}")


if __name__ == "__main__":
    main()
