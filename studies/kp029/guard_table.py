"""KP-029 premise study, stage 1b (ruling 6): the GUARD TABLE, from the kernel's own DEV rows only. No spot data.

    .venv\\Scripts\\python.exe -I studies\\kp029\\guard_table.py

For the perpetuals of unit top30 and of next30 on DEV (the 114 of spot_symbols.json), on the hours each is IN PLAY
in its band: how many coin-hours have the perpetual's close more than 2%, 5%, 10% and 20% away from its index close,
how many coins and how many distinct weeks (Monday 00:00 UTC) those hours touch. The index close is the kernel's own
field (LANGUAGE.md 5: the close of the last index bar at or before the row, known while at most 6 hours old) and the
in-play mask the kernel's own: the deviation is the signal of a one-line study program,
(close - index_close) / index_close, evaluated by the kernel's block path (omr.upipeline.Blocked.unit) on
load_udata("dev_end"); the raw signal is unknown wherever the coin is not in play or the index is stale. Counts only,
written to studies/kp029/guard_table.json. Ruling 6: more than 20 coin-hours beyond 20% stops the study for a report.
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

import numpy as np  # noqa: E402

from omr import constants as C  # noqa: E402
from omr import kernel_lock  # noqa: E402
from omr import lang as L  # noqa: E402
from omr import upipeline as UP  # noqa: E402

import kp029_eval as EV  # noqa: E402

LEVELS = (0.02, 0.05, 0.10, 0.20)
STOP_AT_20 = 20
TEXT = ('name = "kp029_guard_table"\nfamily = "other"\nkind = "portfolio"\nunit = "top30"\n'
        'hypothesis = "Not a strategy: the perpetual close against its index close, for the KP-029 guard table only."\n'
        'signal = (close - index_close) / index_close\n')
WEEK_NS = 7 * 24 * 3_600_000_000_000
MONDAY_NS = 4 * 24 * 3_600_000_000_000          # 1970-01-05 00:00 UTC was a Monday


def main():
    mem = EV.memory_kb()
    if not EV.memory_ok(mem):
        raise SystemExit(f"memory below the floor: {mem}")
    prog = L.parse(TEXT, "kp029_guard_table")
    plan = json.loads((HERE / "spot_symbols.json").read_text(encoding="ascii"))
    perps = {r["perp"] for r in plan["symbols"]}
    ud = UP.load_udata("dev_end", fields=UP.program_fields(prog))
    dev_s = None
    dev = {}                                     # symbol -> {grid row: |deviation|}
    for band, months in (("top30", C.UNIVERSE_BLOCK_MONTHS), ("next30", C.UNIVERSE_BLOCK_MONTHS_G8)):
        fp = UP.Blocked(ud, band, months=months, fields=UP.program_fields(prog))
        _, raw, kn = fp.unit(prog, {})
        ns = fp.ns
        dev_s = fp.pos(C.DEV_START)
        for k, s in enumerate(fp.symbols):
            rows = np.nonzero(kn[:, k] & np.isfinite(raw[:, k]))[0]
            rows = rows[rows >= dev_s]
            d = dev.setdefault(s, {})
            for i, v in zip(rows.tolist(), np.abs(raw[rows, k]).tolist()):
                d[i] = v
        del fp, raw, kn
    grid_ns = ud.grid().asi8
    out = {"at": EV.now_utc(), "kernel_hash": kernel_lock.kernel_hash(), "perpetuals_with_inplay_hours": len(dev),
           "perpetuals_in_plan": len(perps), "missing_from_plan": sorted(set(dev) - perps),
           "plan_without_inplay_hours": sorted(perps - set(dev)),
           "inplay_coin_hours": int(sum(len(v) for v in dev.values())), "levels": {}}
    for lv in LEVELS:
        hours, coins, weeks, per = 0, set(), set(), {}
        for s, d in dev.items():
            hit = [i for i, v in d.items() if v > lv]
            if hit:
                hours += len(hit)
                coins.add(s)
                per[s] = len(hit)
                weeks.update(int((grid_ns[i] - MONDAY_NS) // WEEK_NS) for i in hit)
        top = sorted(per.items(), key=lambda kv: -kv[1])[:8]
        out["levels"][f"{lv:.2f}"] = {"coin_hours": hours, "coins": len(coins), "weeks": len(weeks), "most": top}
    import pandas as pd
    out["beyond_10pct"] = sorted([s, str(pd.Timestamp(int(grid_ns[i]), tz="UTC"))[:16], round(v, 4)]
                                 for s, d in dev.items() for i, v in d.items() if v > 0.10)
    over20 = out["levels"]["0.20"]["coin_hours"]
    out["stop"] = bool(over20 > STOP_AT_20)
    (HERE / "guard_table.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n", encoding="ascii",
                                           newline="\n")
    print(f"in-play coin-hours on DEV {out['inplay_coin_hours']} over {len(dev)} perpetuals "
          f"(plan {len(perps)}; not in plan {out['missing_from_plan']}; plan without in-play hours "
          f"{out['plan_without_inplay_hours']})")
    for k, v in out["levels"].items():
        print(f"  |close / index close - 1| > {k}: {v['coin_hours']} coin-hours, {v['coins']} coins, {v['weeks']} weeks; "
              f"most {v['most']}")
    print("STOP (ruling 6): more than 20 coin-hours beyond 20%" if out["stop"] else "ruling 6 stop not triggered")


if __name__ == "__main__":
    main()
