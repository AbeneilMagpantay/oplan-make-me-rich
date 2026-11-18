"""Evaluator: python -m omr.evaluate <program.omr> --generation N

No strategy code exists: a program is parsed and checked by omr.lang and interpreted by omr.interp.

Order (count before exposure):
1. Kernel lock verified AND sealed (the seal carries the G6 threshold); ledger chains intact; stored
   data equal to the manifest (every file hashed at the moment it is read) and validated
   (python -m omr.data validate). Generation rules: N equals the highest generation in the trial
   ledger or that plus one (0 for an empty ledger); generations/genNNN/PLAN.md exists, and for N >= 1
   generations/gen(N-1)/REPORT.md exists; at most MAX_COUNTED_PER_GENERATION counted trials per
   generation (the next one is refused before any row). The cap paces the work; the protection
   against many attempts is the count M in the DSR.
2. Stage 1 (UNCOUNTED, DEV-only frames, no handle): parse/static checks (incl. the constant probe),
   identity and dedupe, signals on DEV, the truncation and start-cut self-checks, activity_dev. A
   rejection is one row in ledger/stage1_log.jsonl; nothing enters the trial ledger.
3. A COUNTED `pending` row is appended, flushed and fsynced; it issues the trial's ValHandle.
4. Stage 2 on DEV+VAL frames. Result files are written, then the final row: `evaluated` (with
   tier), `liquidated`, or `kernel_fault` (any unexpected exception, or stage-2 DEV rows differing
   from stage 1; no metrics). A pending row is never left behind by an exception.
Trial identity = sha256(canonical program + SEMANTIC kernel hash + research_hash)[:16].
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import platform
import secrets
import shutil
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from omr import constants as C
from omr import data
from omr import datasets as D
from omr import kernel_lock
from omr import lang as L
from omr import ledger
from omr import paths as P
from omr import pipeline
from omr import stats as S


def versions() -> dict:
    import numba
    import pyarrow
    import scipy
    return {"python": platform.python_version(), "numpy": np.__version__, "pandas": pd.__version__,
            "numba": numba.__version__, "pyarrow": pyarrow.__version__, "scipy": scipy.__version__}


class Refused(SystemExit):
    pass


class DiskProvider:
    """Real data from data/. DEV frames need no handle; VAL frames need the trial's handle."""

    def check(self) -> str:
        manifest = data.load_manifest()
        rh = data.research_hash_from_disk(manifest)
        if rh != manifest["research_hash"]:
            raise Refused("DATA MISMATCH: stored data does not match data/manifest.json research_hash. Refusing.")
        if not data.validation_ok():
            raise Refused("DATA NOT VALIDATED for the current files: run python -m omr.data validate. Refusing.")
        return rh

    def dev_frames(self):
        frames = D.load_frames(C.CORE, D.PROGRAM_EXTRA, upto="dev_end")
        return frames, frames[C.BTC]

    def val_world(self, handle) -> pipeline.World:
        core = D.load_frames(C.CORE, D.PROGRAM_EXTRA, upto="val_end", handle=handle)
        ext = D.load_frames(C.EXTENDED, D.PROGRAM_EXTRA, upto="val_end", handle=handle)
        liq = D.load_liqs(C.ALL_SYMBOLS, upto="val_end", handle=handle)
        return pipeline.World(core=core, extended=ext, btc=core[C.BTC], liq=liq, symbols=C.CORE)


def dsr_for(trial_id: str, daily: pd.Series) -> dict:
    """DSR of this trial's VAL returns. M = every counted trial (this one included, with or without
    stored returns); V and rho only from counted trials with stored returns."""
    mat = ledger.counted_val_matrix(extra={trial_id: daily})
    val = ledger.val_slice(daily)
    sh = [S.sharpe_daily(mat[c]) for c in mat.columns]
    rho = S.mean_pairwise_corr(mat)
    M = max(len(ledger.counted_ids()), mat.shape[1])
    return S.dsr(val.to_numpy(), sh, rho, M)


def check_generation(generation: int) -> str:
    """Generation rules; returns the sha256 of generations/genNNN/PLAN.md. Raises Refused."""
    if not isinstance(generation, int) or generation < 0:
        raise Refused("--generation must be a non-negative integer")
    hi = ledger.highest_generation()
    allowed = (0,) if hi is None else (hi, hi + 1)
    if generation not in allowed:
        raise Refused(f"generation {generation} refused: the trial ledger's highest generation is {hi}; "
                      f"allowed: {' or '.join(str(x) for x in allowed)}")
    plan = P.GENERATIONS_DIR / f"gen{generation:03d}" / "PLAN.md"
    if not plan.exists():
        raise Refused(f"generation {generation} refused: {plan.relative_to(P.ROOT) if plan.is_relative_to(P.ROOT) else plan} "
                      "does not exist (write the plan first)")
    if generation >= 1:
        report = P.GENERATIONS_DIR / f"gen{generation - 1:03d}" / "REPORT.md"
        if not report.exists():
            raise Refused(f"generation {generation} refused: generation {generation - 1} has no REPORT.md "
                          "(report the previous generation first)")
    n = ledger.counted_in_generation(generation)
    if n >= C.MAX_COUNTED_PER_GENERATION:
        raise Refused(f"generation {generation} already has {n} counted trials (max {C.MAX_COUNTED_PER_GENERATION}); "
                      "refused before any row")
    return ledger.sha256_file(plan)


def _now():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _rel(p: Path) -> str:
    try:
        return p.relative_to(P.ROOT).as_posix()
    except ValueError:
        return p.name


def stage1_log(row: dict, quiet: bool) -> dict:
    written = ledger.append(P.STAGE1_LOG, dict(row, at=_now()))
    if not quiet:
        print(f"stage 1 REJECTED (not counted, logged to {P.STAGE1_LOG.name}): {row.get('code')}"
              + (f" at line {row['line']} col {row['col']}" if row.get("line") else ""))
    return written


def _fmt(x, nd=3):
    if isinstance(x, (int, np.integer)):
        return str(int(x))
    if isinstance(x, (float, np.floating)):
        return f"{x:.{nd}f}"
    return str(x)


def print_result(row: dict):
    print(f"trial {row['trial_id']}  {row.get('program')}  gen {row.get('generation')}  status {row['status']}")
    if row["status"] != "evaluated":
        print(f"  reason: {row.get('reason')}")
        print("  counted: YES (VAL was exposed)")
        return
    print(f"  tier: {row['tier']}   (G6 threshold {row['g6_threshold']})")
    print(f"  DEV Sharpe {_fmt(row['dev_sharpe'])}  VAL Sharpe {_fmt(row['val_sharpe'])}  PSR(0) {_fmt(row['psr0'])}  "
          f"DSR {_fmt(row['dsr'])} (M={row['M']} N={_fmt(row['N'], 2)} rho={_fmt(row['rho'], 2)})")
    print(f"  VAL maxDD {_fmt(row['val_max_drawdown'])}  DEV+VAL maxDD {_fmt(row['dev_val_max_drawdown'])}  "
          f"deploy_scale {_fmt(row['deploy_scale'])}  direction changes DEV {row['direction_changes_dev']} "
          f"VAL {row['direction_changes_val']}  rebalances {row['rebalances']}")
    print(f"  benchmark (info): VAL Sharpe {_fmt(row['benchmark_val_sharpe'])}  VAL maxDD {_fmt(row['benchmark_val_max_drawdown'])}")
    for g, ok in row["gates"].items():
        print(f"  {g} {'PASS' if ok else 'FAIL'}  {row['gate_values'].get(g)}")


def evaluate_file(path: str, generation: int, provider=None, opts: pipeline.Opts | None = None,
                  quiet: bool = False, require_lock: bool = True, p_max: float | None = None) -> dict:
    if require_lock:
        k = kernel_lock.require_sealed()
        p_max = k["g6_threshold"]
    else:
        k = kernel_lock.compute()
        if p_max is None:
            raise ValueError("without the sealed lock a G6 threshold must be passed explicitly")
    for chain in (P.TRIALS_JSONL, P.STAGE1_LOG):
        probs = ledger.verify_chain(chain) if chain.exists() else []
        if probs:
            print("LEDGER CHAIN/HEAD PROBLEM - refusing to run:")
            for p in probs[:10]:
                print("  " + p)
            sys.exit(6)
    provider = provider or DiskProvider()
    opts = opts or pipeline.Opts()
    rh = provider.check()
    plan_sha = check_generation(int(generation))
    p = Path(path).resolve()
    base = {"generation": int(generation), "file": _rel(p), "kernel_hash": k["combined"],
            "semantic_hash": k["semantic"], "text_hash": k["text"], "research_hash": rh}
    try:
        prog = L.parse_file(p)
    except L.LangError as e:
        if e.rule == "probe_fault":                  # a kernel bug while probing: never shown as a syntax error
            return stage1_log(dict(base, code="probe_fault", error_type=e.msg), quiet)
        return stage1_log(dict(base, code=f"parse:{e.rule}", line=e.line, col=e.col), quiet)
    tid = L.trial_id(prog, k["semantic"], rh)
    existing = ledger.find_trial(tid)
    if existing:
        if not quiet:
            print(f"identical trial already in the ledger (not counted again): {tid}")
            print_result(existing)
        return existing
    P.LEDGER_DIR.mkdir(parents=True, exist_ok=True)
    lock = P.LEDGER_DIR / ".evaluate.lock"
    try:
        fd = os.open(str(lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.close(fd)
    except FileExistsError:
        print(f"another evaluation holds {lock}; if none is running, delete it and retry")
        sys.exit(5)
    try:
        return _evaluate_locked(p, prog, tid, base, plan_sha, provider, opts, quiet, p_max)
    finally:
        try:
            lock.unlink()
        except FileNotFoundError:
            pass


def _evaluate_locked(p, prog, tid, base, plan_sha, provider, opts, quiet, p_max):
    params = L.default_params(prog)
    seed = secrets.randbits(63)                       # fresh OS entropy; stored after the fact
    ident = dict(base, trial_id=tid, program=prog.name, family=prog.header["family"], kind=prog.kind)
    frames_dev, btc_dev = provider.dev_frames()
    try:
        s1 = pipeline.stage1(prog, params, frames_dev, btc_dev, np.random.default_rng([seed, 1]), opts)
    except Exception as e:                           # an interpreter error on a checked program is a kernel fault
        return stage1_log(dict(ident, code="kernel_fault", error_type=type(e).__name__), quiet)
    if not s1["ok"]:
        return stage1_log(dict(ident, code=s1["code"], fault=s1.get("fault"),
                               direction_changes_dev=s1.get("direction_changes_dev")), quiet)

    # ---- COUNTED from here on: the pending row is on disk before any VAL bar is read
    P.TRIAL_SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    src = P.TRIAL_SOURCE_DIR / f"{tid}.omr"
    shutil.copyfile(p, src)
    row = dict(ident, born_at=_now(), plan_sha256=plan_sha, hypothesis=prog.header["hypothesis"],
               canonical=prog.canonical, params=params, node_count=prog.node_count, n_literals=prog.n_literals,
               source_sha256=ledger.sha256_file(src), versions=versions(),
               stage1={"truncation_cuts": s1["cuts"], "start_cuts": s1["start_cuts"],
                       "direction_changes_dev": s1["direction_changes_dev"]})
    pending, handle = ledger.append_pending(row)
    keep = ("trial_id", "generation", "program", "family", "kind", "kernel_hash", "semantic_hash", "text_hash",
            "research_hash", "params", "node_count", "n_literals", "born_at")
    final = {k: row[k] for k in keep}
    final.update(pending_hash=pending["row_hash"], g6_threshold=p_max, seed=str(seed))
    try:
        world = provider.val_world(handle)
        res = pipeline.stage2(prog, params, world, s1, opts, handle, seed, p_max)
        if res["status"] == "kernel_fault":
            final.update(status="kernel_fault", reason=res["reason"])
        elif res["status"] == "liquidated":
            final.update(status="liquidated", reason="liquidation")
        else:
            final.update(_evaluated_fields(tid, res, seed, s1))
    except BaseException as e:                       # never leave a pending row behind
        final = {k: v for k, v in final.items() if k in keep + ("pending_hash", "g6_threshold", "seed")}
        final.update(status="kernel_fault", reason="exception", error_type=type(e).__name__)
        written = ledger.append(P.TRIALS_JSONL, final)
        if not quiet:
            print_result(written)
        if not isinstance(e, Exception):
            raise
        return written
    written = ledger.append(P.TRIALS_JSONL, final)
    if not quiet:
        print_result(written)
    return written


def _evaluated_fields(tid, res, seed, s1) -> dict:
    daily = res["daily_returns"]
    out = {"returns_sha256": ledger.save_returns(tid, daily)}
    d = dsr_for(tid, daily)
    m, g, info = res["metrics"], res["gates"], res["info"]
    out.update({
        "status": "evaluated", "tier": res["tier"],
        "gates": {k: v["pass"] for k, v in g.items()},
        "gate_values": {k: v["value"] for k, v in g.items()},
        "g5_vacuous": bool(g["G5"].get("g5_vacuous")),
        "dev_sharpe": m["dev"]["sharpe"], "val_sharpe": m["val"]["sharpe"], "psr0": m["val"]["psr0"],
        "dsr": d["dsr"], "M": d["M"], "N": d["N"], "rho": d["rho"], "dsr_V": d["V"], "dsr_sr0_daily": d["sr0_daily"],
        "val_sharpe_daily": m["val_sharpe_daily"], "val_max_drawdown": m["val"]["max_drawdown"],
        "dev_val_max_drawdown": m["dev_val_max_drawdown"], "deploy_scale": m["deploy_scale"],
        "rebalances": m["rebalances"], "direction_changes_dev": m["direction_changes_dev"],
        "direction_changes_val": m["direction_changes_val"],
        "turnover_per_year": m["turnover_per_year"], "avg_gross_exposure": m["avg_gross_exposure"],
        "benchmark_val_sharpe": info["benchmark_val_sharpe"],
        "benchmark_val_max_drawdown": info["benchmark_val_max_drawdown"],
        "vs_benchmark_beta": info["vs_benchmark_beta"], "vs_benchmark_alpha_ann": info["vs_benchmark_alpha_ann"],
        "vs_benchmark_resid_psr0": info["vs_benchmark_resid_psr0"],
    })
    detail = {"trial_id": tid, "metrics": m, "gates": g, "info": info, "dsr": d,
              "stage1": {"truncation_cuts": s1["cuts"], "direction_changes_dev": s1["direction_changes_dev"]},
              "seed": str(seed), **res.get("detail", {})}
    P.TRIAL_DETAIL_DIR.mkdir(parents=True, exist_ok=True)
    det_path = P.TRIAL_DETAIL_DIR / f"{tid}.json"
    det_path.write_text(json.dumps(ledger.clean(detail), indent=1, sort_keys=True), encoding="ascii")
    out["detail_sha256"] = ledger.sha256_file(det_path)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m omr.evaluate")
    ap.add_argument("program_file")
    ap.add_argument("--generation", type=int, required=True)
    a = ap.parse_args(argv)
    try:
        evaluate_file(a.program_file, a.generation)
    except Refused as e:
        print(str(e))
        sys.exit(7)


if __name__ == "__main__":
    main()
