"""KP-029 premise study, STAGE 2 entry point (NOT run in stage 1). One evaluation per call, logged before printed.

    .venv\\Scripts\\python.exe -I studies\\kp029\\run_study.py --coverage    (first: spot data counts, tripwires)
    .venv\\Scripts\\python.exe -I studies\\kp029\\run_study.py <program stem> [--label default|corner08|corner12]
                                                            [--reserve]
    .venv\\Scripts\\python.exe -I studies\\kp029\\run_study.py --summary

--coverage (once, after the download, before the first evaluation; counts of the spot data only, no book, no return;
written to studies/kp029/spot_coverage.json):
  - the spot OUTAGE hours (ruling 5: hours at or after the first stored spot BTCUSDT row, to DEV end, for which that
    table has no row), their blocks and the longest block, and over all outage hours the share of the other stored
    pairs with a real row in the 24 hours before that have no row either;
  - per perpetual of spot_symbols.json, on its IN-PLAY hours (the kernel's mask, top30 and next30): real spot rows,
    synthetic outage rows, slots known, and the hours the 50% price guard rejects on real rows (ruling 6, revised).
  TRIPWIRES (fixed in the coordinator's rulings 5 and 6): outage share under 95%, or an outage block longer than 24
  hours, or more than 200 outage hours on DEV, or more than 5 pairs with more than 24 guard-rejected in-play hours.
  Any of them sets "stop": true in the file, and run_study.py then refuses every evaluation (report to the
  coordinator; for the guard tripwire an amendment of the symbol map only). No evaluation runs before the file exists.

Each evaluation: the memory floor (1,000,000 KB physical, 4,000,000 KB commit); the sha256 of every study file; the
kernel's perpetual rows under the dev_end ceiling (omr.upipeline.load_udata); the spot rows from
_build/kp029_study/spot (kp029_spot.SpotStore: checksum at read, no month after 2022-06, no row after 2022-06-30
23:00); then, in this order:
  1. the kernel's stage 1 on the study program (omr.upipeline.stage1_u: 24 random truncation cuts + DEV end, start
     cuts, block_overlap, activity);
  2. the study's truncation test (guard D2: 6 fixed + 2 random cuts, the input rebuilt from rows up to each cut
     only); a failure makes the run VOID: no reading is computed or printed;
  3. every reading (kp029_eval.measure) and the screen W1..W8 at the study's thresholds; for a corner the corner
     rule, for a control the margin against its hypothesis's default;
  4. one row appended to studies/kp029/run_log.jsonl (flushed and fsynced) BEFORE anything is printed; a run that
     faults or raises writes its row too (status kernel_fault / void / error).
Budget and order (ruling 8): three hypotheses, H-S1, H-S2, H-S4, one default each; for a hypothesis that passed the
screen at its default: its control, then the 0.8 corner, then the 1.2 corner, stopping at the first failure (at most
9); a re-run only after a void or error row, with --reserve (2 at most); CAP 14 evaluations in all.
"""
from __future__ import annotations

import argparse
import json
import os
import secrets
import sys
import time
import traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
for p in (str(ROOT), str(HERE)):
    if p not in sys.path:
        sys.path.insert(0, p)

import hashlib  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from omr import constants as C  # noqa: E402
from omr import kernel_lock  # noqa: E402
from omr import lang as L  # noqa: E402
from omr import upipeline as UP  # noqa: E402

import kp029_eval as EV  # noqa: E402
import kp029_features as F  # noqa: E402
import kp029_spot as SP  # noqa: E402

RUN_LOG = HERE / "run_log.jsonl"
COVERAGE = HERE / "spot_coverage.json"
PROGS = HERE / "programs"
RESERVE_MAX = 2
CAP = 14                                  # ruling 8: 3 defaults + at most 9 control and corner runs + 2 in reserve
OUTAGE_SHARE_MIN = 0.95                   # ruling 5 tripwires
OUTAGE_BLOCK_MAX = 24
OUTAGE_HOURS_MAX = 200
GUARD_PAIR_HOURS = 24                     # ruling 6 (revised) tripwire: more than 5 pairs with more than 24 rejected
GUARD_PAIRS_MAX = 5
_C3 = {"corner08": {"k": 6, "n": 22, "nb": 34}, "corner12": {"k": 8, "n": 34, "nb": 50}}
_C2 = {"corner08": {"k": 6, "nb": 34}, "corner12": {"k": 8, "nb": 50}}
_C4 = {"corner08": {"k": 22, "nb": 34}, "corner12": {"k": 34, "nb": 50}}
REGISTERED = {   # PLAN version 2 after rulings 3 and 4: the hypotheses in run order, their controls and corners
    "kp029_hs1_share_shift": {"id": "H-S1", "role": "hypothesis", "control": "kp029_cs1_perp_volume_shift",
                              "corners": _C3},
    "kp029_hs2_spot_flow": {"id": "H-S2", "role": "hypothesis", "control": "kp029_cs2_perp_flow", "corners": _C2},
    "kp029_hs4_rally_carrier": {"id": "H-S4", "role": "hypothesis", "control": "kp029_cs4_volume_return",
                                "corners": _C4},
    "kp029_cs1_perp_volume_shift": {"id": "C-S1", "role": "control", "of": "kp029_hs1_share_shift"},
    "kp029_cs2_perp_flow": {"id": "C-S2", "role": "control", "of": "kp029_hs2_spot_flow"},
    "kp029_cs4_volume_return": {"id": "C-S4", "role": "control", "of": "kp029_hs4_rally_carrier"},
}


def read_log(path: Path) -> list:
    if not path.exists():
        return []
    return [json.loads(x) for x in path.read_text(encoding="ascii").splitlines() if x.strip()]


def append(path: Path, row: dict) -> None:
    line = json.dumps(row, sort_keys=True, allow_nan=False)
    line.encode("ascii")
    with open(path, "a", encoding="ascii", newline="\n") as f:
        f.write(line + "\n")
        f.flush()
        os.fsync(f.fileno())


def params_of(prog, stem: str, label: str) -> dict:
    p = L.default_params(prog)
    if label == "default":
        return p
    spec = REGISTERED[stem]
    if spec["role"] != "hypothesis" or label not in spec["corners"]:
        raise SystemExit(f"{stem}: no registered configuration {label!r}")
    for k, v in spec["corners"][label].items():
        q = prog.params[k]
        if not (q.low <= v <= q.high):
            raise SystemExit(f"{stem} {label}: {k}={v} outside the declared range")
        p[k] = int(v) if q.is_int else float(v)
    return p


def _last(rows, stem, label, statuses=("ok",)):
    hit = [r for r in rows if r.get("program") == stem and r.get("label") == label and r.get("status") in statuses
           and not r.get("synthetic")]
    return hit[-1] if hit else None


def budget_check(rows: list, stem: str, label: str, reserve: bool) -> None:
    """Ruling 8's budget and order (raises SystemExit when the call is not allowed now)."""
    spec = REGISTERED[stem]
    real = [r for r in rows if not r.get("synthetic")]
    if len(real) >= CAP:
        raise SystemExit(f"the cap of {CAP} evaluations is reached")
    if _last(rows, stem, label) is not None:
        raise SystemExit(f"{stem} {label} has already been evaluated (one evaluation per registered configuration)")
    if _last(rows, stem, label, ("void", "error", "kernel_fault")) is not None and not reserve:
        raise SystemExit(f"{stem} {label}: an earlier run is void/error; a re-run needs --reserve (an amendment first)")
    if reserve and sum(1 for r in real if r.get("reserve")) >= RESERVE_MAX:
        raise SystemExit("the reserve of 2 runs is spent")
    if spec["role"] == "control":
        h = _last(rows, spec["of"], "default")
        if h is None or not h.get("screen", {}).get("pass"):
            raise SystemExit(f"{stem}: its hypothesis has not passed the screen at its default")
    elif label == "corner08":
        h = _last(rows, stem, "default")
        c = _last(rows, spec["control"], "default")
        if h is None or not h.get("screen", {}).get("pass"):
            raise SystemExit(f"{stem}: corners only after the default passed the screen")
        if c is None or not (c.get("control_vs_hypothesis") or {}).get("pass"):
            raise SystemExit(f"{stem}: corners only after the control condition passed")
    elif label == "corner12":
        c8 = _last(rows, stem, "corner08")
        if c8 is None or not c8.get("corner_ok"):
            raise SystemExit(f"{stem}: the 1.2 corner only after the 0.8 corner passed")


def coverage_gate(path: Path = COVERAGE) -> None:
    """Refuses every evaluation before the coverage count, or when one of its tripwires is set."""
    if not path.exists():
        raise SystemExit("run --coverage first (the spot data counts come before the first evaluation)")
    cov = json.loads(path.read_text(encoding="ascii"))
    if cov.get("stop") is not False:
        raise SystemExit(f"STOP: a coverage tripwire is set ({cov.get('reasons')}); report to the coordinator")


def evaluate_and_log(stem: str, label: str, ud_kernel, spot, log_path: Path = RUN_LOG,
                     stage1_cuts: int = C.TRUNCATION_CUTS, check_memory: bool = True, synthetic: bool = False,
                     reserve: bool = False) -> dict:
    """One evaluation of a registered study program; returns the logged row."""
    t0 = time.time()
    spec = REGISTERED[stem]
    path = PROGS / f"{stem}.omr"
    prog = L.parse_file(path)
    params = params_of(prog, stem, label)
    mem = EV.memory_kb()
    row = {"at": EV.now_utc(), "study": "KP-029", "generation": 4, "round": 2, "hypothesis": spec["id"],
           "program": stem, "role": spec["role"], "label": label, "params": params, "synthetic": bool(synthetic),
           "reserve": bool(reserve), "memory_kb": mem, "study_hashes": EV.study_hashes(),
           "program_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
           "canonical_sha256": hashlib.sha256(prog.canonical.encode("ascii")).hexdigest(),
           "lookback_hours": int(prog.lookback_hours), "kernel_hash": kernel_lock.kernel_hash(),
           "versions": EV.versions(), "guard_tol": F.GUARD_TOL}
    if check_memory and not EV.memory_ok(mem):
        raise SystemExit(f"memory below the floor (physical {mem['phys_kb']} KB, commit {mem['commit_kb']} KB): not run")
    try:
        sud = F.study_udata(ud_kernel, spot)
        s1, st1 = EV.stage1(prog, params, sud, cuts=stage1_cuts)
        row["stage1"] = st1
        if st1.get("code") == "kernel_fault":
            row["status"] = "kernel_fault"
        else:
            seed = secrets.randbits(63)
            cuts = EV.truncation_cuts(s1["grid"], np.random.default_rng(seed))
            tt = EV.truncation_test(prog, params, ud_kernel, spot, s1, cuts)
            row["truncation_test"] = dict(tt, seed=str(seed))
            if not tt["pass"]:
                row["status"] = "void"
            else:
                r = EV.measure(prog, params, sud, s1, g6_lags=True, coverage=True)
                row["readings"] = r
                row["pre_cost"] = EV.pre_cost(r)
                row["screen"] = EV.screen(r, st1)
                if label != "default":
                    row["corner_ok"] = EV.corner_ok(r)
                if spec["role"] == "control":
                    h = _last(read_log(log_path), spec["of"], "default")
                    row["control_vs_hypothesis"] = (EV.control_ok(h["readings"], r) if h is not None
                                                    else {"pass": False, "why": "no hypothesis default row"})
                row["status"] = "ok"
        if hasattr(spot, "dropped"):
            row["spot_rows_dropped_by_clean"] = int(sum(spot.dropped.values()))
            row["spot_pairs_loaded"] = int(sum(1 for v in getattr(spot, "_c", {}).values() if v is not None))
    except Exception as e:
        row["status"] = "error"
        row["error"] = f"{type(e).__name__}: {str(e)[:300]}"
        row["seconds"] = round(time.time() - t0, 1)
        append(log_path, row)
        traceback.print_exc()
        raise
    row["seconds"] = round(time.time() - t0, 1)
    append(log_path, row)
    return row


def show(row: dict) -> None:
    print(f"{row['hypothesis']} {row['program']} {row['label']} {row['params']}: status {row['status']} "
          f"({row.get('seconds')} s)")
    print(f"  kernel stage 1: {row.get('stage1')}")
    tt = row.get("truncation_test")
    if tt:
        print(f"  truncation test: {'PASS' if tt['pass'] else 'FAIL -> VOID'} over {len(tt['cuts'])} cuts")
    r = row.get("readings")
    if not r:
        return
    print(f"  DEV Sharpe {r['dev_sharpe']}  G4 {r['g4_dev_sharpe']}  G2 {r['g2_dev_sharpe']}  pre-cost {row['pre_cost']}")
    print(f"  next30 {r['next30_dev_sharpe']} ({r['next30_code']})  speed {r['g6_memory_dev']}  paired "
          f"{r.get('g6_paired_dev')}")
    print(f"  years {[(y['year'], y['return'], y['sharpe']) for y in r['per_year']]}")
    print(f"  names held {r['names_held_avg']} of {r['names_inplay_avg']}  avg gross {r['avg_gross']}  "
          f"costs {r['costs']}  spot known {r['spot_known_share_inplay']}")
    sc = row["screen"]
    print(f"  screen: {'PASS' if sc['pass'] else 'fail at ' + str(sc['first_failed'])}  "
          + "  ".join(f"{k} {'P' if v['pass'] else 'F'}" for k, v in sc["items"].items()))
    if "corner_ok" in row:
        print(f"  corner rule (DEV Sharpe > 0 and G4 > 0): {'PASS' if row['corner_ok'] else 'FAIL'}")
    if "control_vs_hypothesis" in row:
        print(f"  control condition: {row['control_vs_hypothesis']}")


# ---------------------------------------------------------------- the coverage count (rulings 5 and 6)
def outage_stats(spot, pairs: list, dev_end: pd.Timestamp) -> dict:
    """Outage hours from the stored spot BTCUSDT table (ruling 5), their blocks, and the share of the other pairs
    with a real row in the 24 hours before an outage hour that have no row at it, over all outage hours."""
    ref = spot.raw_index(F.OUTAGE_REF)
    if ref is None or len(ref) == 0:
        return {"ref_rows": 0, "hours": [], "n_hours": 0, "blocks": 0, "longest_block": 0, "share": None,
                "eligible": 0, "no_row": 0, "missing_ref": True}
    ref = pd.DatetimeIndex(ref)
    grid = pd.date_range(ref.min(), dev_end, freq="h").as_unit("ns")
    out_h = grid[~grid.isin(ref)]
    blocks, longest, run, prev = 0, 0, 0, None
    for t in out_h:
        if prev is not None and t - prev == F.HOUR:
            run += 1
        else:
            blocks += 1
            run = 1
        longest = max(longest, run)
        prev = t
    elig = norow = 0
    others = [p for p in pairs if p != F.OUTAGE_REF]
    tabs = {}
    for p in others:
        sp, raw = spot.get(p), spot.raw_index(p)
        if sp is not None and len(sp):
            tabs[p] = (sp.index.asi8, pd.DatetimeIndex(raw).asi8)
    H = F.HOUR.value
    for t in out_h.asi8:
        for real, raw in tabs.values():
            a = np.searchsorted(real, t - 24 * H, side="left")
            b = np.searchsorted(real, t - H, side="right")
            if b > a:                                   # a real row in the 24 hours before
                elig += 1
                j = np.searchsorted(raw, t)
                if not (j < len(raw) and raw[j] == t):
                    norow += 1
    return {"ref_rows": int(len(ref)), "hours": [str(t) for t in out_h], "n_hours": int(len(out_h)),
            "blocks": blocks, "longest_block": longest, "share": (norow / elig) if elig else None,
            "eligible": int(elig), "no_row": int(norow), "missing_ref": False}


def inplay_rows(ud) -> dict:
    """{perpetual: in-play grid rows on DEV} over top30 and next30, by the kernel's own mask (Blocked.inplay)."""
    out = {}
    for band, months in (("top30", C.UNIVERSE_BLOCK_MONTHS), ("next30", C.UNIVERSE_BLOCK_MONTHS_G8)):
        fp = UP.Blocked(ud, band, months=months, fields={"close"})
        ip = fp.inplay()
        s0 = fp.pos(C.DEV_START)
        for k, s in enumerate(fp.symbols):
            rows = np.nonzero(ip[:, k])[0]
            rows = rows[rows >= s0]
            out[s] = np.union1d(out.get(s, np.zeros(0, dtype=np.int64)), rows)
        del fp, ip
    return out


def coverage(ud, spot, plan: dict, out_path=COVERAGE, inplay: dict | None = None) -> dict:
    """The coverage count and its tripwires (see the module docstring). inplay: {perpetual: in-play grid rows} (tests
    pass their own; by default the kernel's mask)."""
    inplay = inplay_rows(ud) if inplay is None else inplay
    grid = ud.grid()
    pairs = sorted({r["spot"] for r in plan["symbols"]})
    ost = outage_stats(spot, pairs, pd.Timestamp(C.DEV_END, tz="UTC"))
    per = {}
    for r in plan["symbols"]:
        s = r["perp"]
        rows = inplay.get(s, np.zeros(0, dtype=np.int64))
        kl = ud.tables(s)["klines"]
        sp, raw, ref, mult = F.spot_inputs(s, spot)
        d = F.slot_detail(kl, sp, mult, raw, ref)
        pos = kl.index.get_indexer(grid[rows]) if len(rows) else np.zeros(0, dtype=np.int64)
        pos = pos[pos >= 0]
        pick = lambda a: int(np.asarray(a)[pos].sum())  # noqa: E731
        per[s] = {"spot": r["spot"], "inplay_hours": int(len(pos)), "real": pick(d["real"]),
                  "synthetic": pick(d["synthetic"]), "slot_known": pick(np.isfinite(d["volume"])),
                  "guard_rejected": pick(d["guard_reject"])}
    rej = {s: v["guard_rejected"] for s, v in per.items() if v["guard_rejected"] > GUARD_PAIR_HOURS}
    reasons = []
    if ost["missing_ref"]:
        reasons.append("no stored spot BTCUSDT table")
    if ost["share"] is not None and ost["share"] < OUTAGE_SHARE_MIN:
        reasons.append(f"outage share {ost['share']:.4f} < {OUTAGE_SHARE_MIN}")
    if ost["longest_block"] > OUTAGE_BLOCK_MAX:
        reasons.append(f"outage block of {ost['longest_block']} h > {OUTAGE_BLOCK_MAX}")
    if ost["n_hours"] > OUTAGE_HOURS_MAX:
        reasons.append(f"{ost['n_hours']} outage hours > {OUTAGE_HOURS_MAX}")
    if len(rej) > GUARD_PAIRS_MAX:
        reasons.append(f"{len(rej)} pairs with more than {GUARD_PAIR_HOURS} guard-rejected in-play hours > "
                       f"{GUARD_PAIRS_MAX} (symbol map)")
    out = {"at": EV.now_utc(), "guard_tol": F.GUARD_TOL, "outage": ost, "pairs": len(per),
           "inplay_hours": sum(v["inplay_hours"] for v in per.values()),
           "real": sum(v["real"] for v in per.values()), "synthetic": sum(v["synthetic"] for v in per.values()),
           "slot_known": sum(v["slot_known"] for v in per.values()),
           "guard_rejected": sum(v["guard_rejected"] for v in per.values()), "pairs_over_24_rejected": rej,
           "stop": bool(reasons), "reasons": reasons, "per_perp": per}
    if out_path is not None:
        Path(out_path).write_text(json.dumps(out, indent=1, sort_keys=True) + "\n", encoding="ascii", newline="\n")
    print(f"outage hours {ost['n_hours']} in {ost['blocks']} blocks, longest {ost['longest_block']} h; share of the other "
          f"pairs without a row at outage hours {ost['share']} ({ost['no_row']} of {ost['eligible']})")
    print(f"in-play coin-hours {out['inplay_hours']}: real spot rows {out['real']}, synthetic {out['synthetic']}, slots "
          f"known {out['slot_known']}, guard-rejected {out['guard_rejected']}; pairs with > 24 rejected: {rej}")
    print(f"STOP: {reasons} -> report to the coordinator; no evaluation will run" if reasons else
          "no tripwire set: the runs may go on")
    return out


def summarize(path: Path = RUN_LOG) -> dict:
    """The verdict per hypothesis from the log: PASS = screen at the default, control margin, both corners, every one
    of those runs with its truncation test passed (status ok)."""
    rows = read_log(path)
    out = {}
    for stem, spec in REGISTERED.items():
        if spec["role"] != "hypothesis":
            continue
        d = _last(rows, stem, "default")
        c = _last(rows, spec["control"], "default")
        c8, c12 = _last(rows, stem, "corner08"), _last(rows, stem, "corner12")
        v = {"default_screen": None if d is None else d["screen"]["pass"],
             "first_failed": None if d is None else d["screen"]["first_failed"],
             "control": None if c is None else (c.get("control_vs_hypothesis") or {}).get("pass"),
             "corner08": None if c8 is None else c8.get("corner_ok"),
             "corner12": None if c12 is None else c12.get("corner_ok")}
        v["PASS"] = bool(v["default_screen"] and v["control"] and v["corner08"] and v["corner12"])
        out[spec["id"]] = v
    n_eval = sum(1 for r in rows if not r.get("synthetic"))
    print(f"{n_eval} evaluations logged (cap {CAP})")
    for k, v in out.items():
        print(f"  {k}: {v}")
    print(f"hypotheses passing: {sum(1 for v in out.values() if v['PASS'])} of {len(out)}")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(prog="run_study.py")
    ap.add_argument("program", nargs="?")
    ap.add_argument("--label", default="default", choices=("default", "corner08", "corner12"))
    ap.add_argument("--reserve", action="store_true")
    ap.add_argument("--summary", action="store_true")
    ap.add_argument("--coverage", action="store_true", help="stage 2, before the first evaluation: spot data counts")
    a = ap.parse_args(argv)
    if a.summary:
        summarize()
        return
    if not SP.SPOT_ROOT.is_dir():
        raise SystemExit(f"no spot folder {SP.SPOT_ROOT}: stage 2's download has not run")
    if a.coverage:
        if not EV.memory_ok(EV.memory_kb()):
            raise SystemExit("memory below the floor")
        ud = UP.load_udata("dev_end", fields={"close"})
        coverage(ud, SP.SpotStore(), json.loads((HERE / "spot_symbols.json").read_text(encoding="ascii")))
        return
    if a.program not in REGISTERED:
        raise SystemExit(f"not a registered study program: {a.program}")
    coverage_gate()
    budget_check(read_log(RUN_LOG), a.program, a.label, a.reserve)
    mem = EV.memory_kb()
    if not EV.memory_ok(mem):
        raise SystemExit(f"memory below the floor: {mem}")
    prog = L.parse_file(PROGS / f"{a.program}.omr")
    ud = UP.load_udata("dev_end", fields=F.needed_fields(UP.program_fields(prog)))
    if not F.dev_end_ok(ud):
        raise SystemExit("the kernel's data do not end at DEV end")
    row = evaluate_and_log(a.program, a.label, ud, SP.SpotStore(), RUN_LOG, reserve=a.reserve)
    show(row)


if __name__ == "__main__":
    main()
