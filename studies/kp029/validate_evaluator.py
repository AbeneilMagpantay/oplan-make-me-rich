"""KP-029 premise study, stage 1: VALIDATION of the study's evaluation path on perpetual data only.

    .venv\\Scripts\\python.exe -I studies\\kp029\\validate_evaluator.py [program stems ...]

For three registered weekly top30 programs of different construction (default: gen003_w01_high_anchor,
gen003_x09_state_continuation, gen004_t09_gain_chasing) it obtains the weights from the kernel's own interpreter and
stage 1, scores them through the study's path (kp029_eval: the kernel's own functions, in the sandbox's order) and
compares every reading with the row the sandbox logged for the same program, parameters and kernel hash in
ledger/sandbox_log.jsonl (read only), and with the per-year Sharpe ratios, average gross and costs the round's plan
printed from the same sandbox run. It then checks that the study's spot wrapper (kp029_features.study_udata, here
with NO spot data) leaves a perpetual-only program's weights and engine run bit-identical.

Not a sandbox run: omr.sandbox and omr.evaluate are not imported; no ledger row is written; nothing is written
under ledger/ or data/. DEV rows only (load_udata("dev_end")). Output: studies/kp029/validation_stage1.json (DEV
numbers and counts only) and a printed table.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
for p in (str(ROOT), str(HERE)):
    if p not in sys.path:
        sys.path.insert(0, p)

import numpy as np  # noqa: E402

from omr import kernel_lock  # noqa: E402
from omr import lang as L  # noqa: E402
from omr import paths as P  # noqa: E402
from omr import upipeline as UP  # noqa: E402

import kp029_eval as EV  # noqa: E402
import kp029_features as F  # noqa: E402
import kp029_spot as SP  # noqa: E402

DEFAULT = ("gen003_w01_high_anchor", "gen003_x09_state_continuation", "gen004_t09_gain_chasing")
# Printed by the same sandbox runs and copied into the plans (per-year Sharpe 2020 / 2021 / 2022H1, average gross,
# costs over DEV): generations/gen003/PLAN.md round 3 run log (W-01) and round 4 run log (X-09), generations/gen004/
# PLAN.md round 1 run log (T-09). Three decimals as printed.
PRINTED = {
    "gen003_w01_high_anchor": {"years": (3.721, 1.831, -2.093), "avg_gross": 0.855, "costs": 0.3024, "rebalances": 571},
    "gen003_x09_state_continuation": {"years": (2.312, 1.532, 1.025), "avg_gross": 0.855, "costs": 0.3138,
                                      "rebalances": 636},
    "gen004_t09_gain_chasing": {"years": (0.743, 2.325, -0.926), "avg_gross": 0.853, "costs": 0.1669,
                                "rebalances": 578},
}
SCALARS = ("dev_sharpe", "g4_dev_sharpe", "g2_dev_sharpe", "next30_dev_sharpe", "g6_memory_dev_max", "names_held_avg",
           "names_inplay_avg", "funding_paid_gross", "funding_received_gross")
INTS = ("direction_changes_dev", "rebalances", "next30_symbols")


def logged_row(stem: str, params: dict, kh: str) -> dict:
    rows = [json.loads(x) for x in P.SANDBOX_LOG.read_text(encoding="ascii").splitlines() if x.strip()]
    hit = [r for r in rows if r.get("program") == stem and r.get("status") == "ok" and r.get("stage1") == "full"
           and r.get("params") == params and r.get("kernel_hash") == kh and "g6_paired_dev" in r]
    if not hit:
        raise SystemExit(f"no logged full sandbox row for {stem} {params} under kernel {kh[:16]}")
    return hit[-1]


def diff(a, b):
    if a is None or b is None or isinstance(a, str) or isinstance(b, str):
        return None
    return float(a) - float(b)


def compare(stem: str, rep: dict, log: dict) -> list:
    out = []
    for k in SCALARS:
        out.append((k, log.get(k), rep.get(k), diff(rep.get(k), log.get(k))))
    for k in INTS:
        out.append((k, log.get(k), rep.get(k), diff(rep.get(k), log.get(k))))
    for j, (a, b) in enumerate(zip(log.get("g6_memory_dev") or [], rep.get("g6_memory_dev") or []), start=1):
        out.append((f"g6_memory_dev r({j})", a, b, diff(b, a)))
    out.append(("g6_memory_dev_from", log.get("g6_memory_dev_from"), rep.get("g6_memory_dev_from"),
                0.0 if log.get("g6_memory_dev_from") == rep.get("g6_memory_dev_from") else None))
    lp, rp = log.get("g6_paired_dev") or {}, rep.get("g6_paired_dev") or {}
    for k in ("at_least_as_good", "p", "book_median", "stale_median"):
        out.append((f"g6_paired_dev {k}", lp.get(k), rp.get(k), diff(rp.get(k), lp.get(k))))
    pr = PRINTED.get(stem, {})
    ys = {y["year"]: y for y in rep.get("per_year") or []}
    for yr, v in zip((2020, 2021, 2022), pr.get("years", ())):
        got = ys.get(yr, {}).get("sharpe")
        out.append((f"year {yr} Sharpe (printed)", v, got, diff(got, v)))
    for k in ("avg_gross", "costs", "rebalances"):
        if k in pr:
            out.append((f"{k} (printed)", pr[k], rep.get(k), diff(rep.get(k), pr[k])))
    return out


def wrapper_identity(prog, params: dict, ud, s1: dict) -> dict:
    """The study wrapper with no spot data: the weights of a perpetual-only program and its engine run must be
    bit-identical to the kernel's (the slots are not read; every other column is the kernel's)."""
    sud = F.study_udata(ud, SP.DictSpot({}))
    fpw = UP.Blocked(sud, "top30", fields=UP.program_fields(prog))
    Ww, rw, kw = fpw.unit(prog, params)
    same_w = bool(np.array_equal(Ww, s1["W"])) and bool(np.array_equal(kw, s1["known"]))
    s, e = fpw.pos(EV.C.DEV_START), fpw.pos(EV.C.DEV_END)
    run_w = fpw.run(Ww, s, e)
    del fpw
    fpk = UP.Blocked(ud, "top30", fields=UP.program_fields(prog))
    run_k = fpk.run(s1["W"], s, e)
    del fpk
    same_run = bool(np.array_equal(run_w.equity, run_k.equity)) and bool(np.array_equal(run_w.gross, run_k.gross))
    return {"weights_identical": same_w, "engine_identical": same_run}


def main(argv=None):
    stems = (argv if argv is not None else sys.argv[1:]) or list(DEFAULT)
    kh = kernel_lock.require_kernel()["combined"]
    report = {"at": EV.now_utc(), "kernel_hash": kh, "study_hashes": EV.study_hashes(), "versions": EV.versions(),
              "programs": {}}
    out_path = HERE / "validation_stage1.json"
    for stem in stems:
        mem = EV.memory_kb()
        if not EV.memory_ok(mem):
            raise SystemExit(f"memory below the coordinator's floor: {mem}")
        prog = L.parse_file(ROOT / "strategies" / f"{stem}.omr")
        params = L.default_params(prog)
        log = logged_row(stem, params, kh)
        t0 = time.time()
        ud = UP.load_udata("dev_end", fields=UP.program_fields(prog))
        s1, st1 = EV.stage1(prog, params, ud)
        if st1.get("code") is not None:
            raise SystemExit(f"{stem}: stage 1 {st1}")
        rep = EV.measure(prog, params, ud, s1, g6_lags=True)
        wid = wrapper_identity(prog, params, ud, s1)
        rows = compare(stem, rep, log)
        report["programs"][stem] = {"params": params, "logged_row_at": log.get("at"), "memory_kb": mem,
                                    "stage1": st1, "readings": rep, "wrapper": wid, "seconds": round(time.time() - t0, 1),
                                    "compare": [{"reading": a, "logged": b, "reproduced": c, "diff": d}
                                                for a, b, c, d in rows]}
        out_path.write_text(json.dumps(report, indent=1, sort_keys=True) + "\n", encoding="ascii", newline="\n")
        print(f"== {stem} {params}  stage 1 {st1}  wrapper {wid}  {report['programs'][stem]['seconds']} s")
        for a, b, c, d in rows:
            dd = "n/a" if d is None else f"{d:+.2e}"
            print(f"   {a:36s} logged {b!s:>24s}  reproduced {c!s:>24s}  diff {dd}")
        del ud, s1
    worst = 0.0
    for v in report["programs"].values():
        for row in v["compare"]:
            if row["diff"] is not None and not row["reading"].endswith("(printed)"):
                worst = max(worst, abs(row["diff"]))
    report["max_abs_diff_vs_log"] = worst
    out_path.write_text(json.dumps(report, indent=1, sort_keys=True) + "\n", encoding="ascii", newline="\n")
    print(f"max |reproduced - logged| over the logged readings: {worst:.3e}")


if __name__ == "__main__":
    main()
