"""DEV sandbox: python -m omr.sandbox <program.omr> [--set name=value ...] [--quick]

Free, uncounted exploration on the DEV region only. Data is loaded with the dev_end ceiling, so
nothing after 2022-06-30 23:00 is visible. The program is parsed and interpreted by the kernel
(nothing is executed). By default stage 1 runs exactly as in the evaluator (truncation self-check
and activity_dev); --quick checks only the DEV end. Not a trial. Each run appends one line to
ledger/sandbox_log.jsonl. A program of unit top30 (KP-015) runs on the DEV universe panel
(omr.upipeline; membership from DEV bars only) with the universe engine; its benchmark is the
equal-weight long of the in-play members.
Data checks (R4): every stored file the sandbox reads is hashed at read and must equal its manifest
sha256; the full research-hash recomputation over every stored table (44 s with the universe) is done
only by omr.evaluate.
"""
from __future__ import annotations

import argparse
import datetime as dt
import secrets
import sys
from pathlib import Path

import numpy as np

from omr import constants as C
from omr import datasets as D
from omr import kernel_lock
from omr import lang as L
from omr import ledger
from omr import paths as P
from omr import pipeline
from omr import stats as S
from omr import upipeline


def parse_sets(items, prog: L.Program) -> dict:
    p = L.default_params(prog)
    for it in items or []:
        k, _, v = it.partition("=")
        if k not in prog.params:
            raise SystemExit(f"unknown param {k}")
        spec = prog.params[k]
        val = float(v)
        if spec.is_int:
            if not val.is_integer():
                raise SystemExit(f"param {k} is an integer param")
            val = int(val)
        if not (spec.low <= val <= spec.high):
            raise SystemExit(f"param {k}={val} outside declared [{spec.low:g}, {spec.high:g}]")
        p[k] = val
    return p


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m omr.sandbox")
    ap.add_argument("program_file")
    ap.add_argument("--set", action="append", default=[], help="param override name=value (within declared bounds)")
    ap.add_argument("--quick", action="store_true", help="truncation self-check at the DEV end only")
    a = ap.parse_args(argv)
    kh = kernel_lock.require_kernel()["combined"]
    path = Path(a.program_file)
    try:
        prog = L.parse_file(path)
    except L.LangError as e:
        print(f"REJECTED: {e.rule} at line {e.line} col {e.col}: {e.msg}")
        sys.exit(1)
    params = parse_sets(a.set, prog)
    opts = pipeline.Opts(truncation_cuts=0 if a.quick else C.TRUNCATION_CUTS)
    if prog.unit != "core":
        ud = upipeline.load_udata("dev_end", fields=upipeline.program_fields(prog))
        s1 = upipeline.stage1_u(prog, params, ud, np.random.default_rng(secrets.randbits(63)), opts)
    else:
        core = D.load_frames(C.CORE, D.PROGRAM_EXTRA, upto="dev_end")
        liq = D.load_liqs(C.CORE, upto="dev_end")
        s1 = pipeline.stage1(prog, params, core, core[C.BTC], np.random.default_rng(secrets.randbits(63)), opts)
    print(f"SANDBOX (DEV only, {C.DEV_START} .. {C.DEV_END}) - not a trial")
    print(f"program {prog.name}  kind {prog.kind}  params {params}  nodes {prog.node_count}")
    print(f"canonical form (identity, with the semantic kernel hash and research_hash): {prog.canonical}")
    if s1.get("code") == "kernel_fault":
        print("KERNEL FAULT in the truncation self-check: report it; this program cannot be evaluated")
        sys.exit(2)
    print(f"stage 1: truncation self-check OK ({s1['cuts']} cuts)  direction changes (DEV) {s1['direction_changes_dev']} "
          f"(need >= {C.MIN_DIRECTION_CHANGES_DEV})  -> {'PASS' if s1['ok'] else 'activity_dev'}")
    W, grid = s1["W"], s1["grid"]
    if prog.unit != "core":
        fp = upipeline.Blocked(ud, "top30", fields=upipeline.program_fields(prog))
        mk = fp
        inplay = fp.inplay()
        k = inplay.sum(axis=1, keepdims=True)
        Wb = np.where(inplay, 1.0 / np.where(k > 0, k, 1), 0.0)
        print(f"unit {prog.unit}: {len(fp.symbols)} symbols ever in the unit on DEV; lookback {prog.lookback_hours} h")
    else:
        mk = pipeline.Market(core, liq, grid, C.CORE)
        Wb = np.full_like(W, 1.0 / len(C.CORE))
    s, e = mk.pos(C.DEV_START), mk.pos(C.DEV_END)
    run = mk.run(W, s, e)
    daily = run.daily_returns()
    bench = mk.run(Wb, s, e).daily_returns()
    sm = S.summary(daily)
    print(f"DEV Sharpe {sm['sharpe']:.3f}  PSR(0) {sm['psr0']:.3f}  total {sm['total_return']:.3f}  CAGR {sm['cagr']:.3f}  "
          f"maxDD {sm['max_drawdown']:.3f}  Calmar {sm['calmar']:.3f}")
    print(f"rebalances {run.n_rebalances}  avg gross {run.gross.mean():.3f}  avg net {run.net.mean():.3f}  "
          f"funding paid {run.funding_paid:.4f}  costs {run.ev_cost.sum():.4f}  liquidated {run.liquidated}")
    print(f"benchmark (long 1/K each; top30: in-play members) DEV Sharpe {S.sharpe(bench):.3f}  maxDD {S.max_drawdown(bench):.3f}")
    print("year   days   return   sharpe   maxDD")
    for r in S.per_year(daily):
        print(f"{r['year']}  {r['n_days']:5d}  {r['return']:7.3f}  {r['sharpe']:7.3f}  {r['max_drawdown']:6.3f}")
    try:
        rel = path.resolve().relative_to(P.ROOT).as_posix()
    except ValueError:
        rel = path.name
    ledger.append(P.SANDBOX_LOG, {"at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                                  "file": rel, "source_sha256": ledger.sha256_file(path), "program": prog.name,
                                  "canonical": prog.canonical, "params": params, "kernel_hash": kh,
                                  "dev_sharpe": sm["sharpe"], "rebalances": run.n_rebalances,
                                  "direction_changes_dev": s1["direction_changes_dev"],
                                  "stage1": "quick" if a.quick else "full"})


if __name__ == "__main__":
    main()
