"""DEV sandbox: python -m omr.sandbox <program.omr> [--set name=value ...] [--quick]

Free, uncounted exploration on the DEV region only. Data is loaded with the dev_end ceiling, so
nothing after 2022-06-30 23:00 is visible. The program is parsed and interpreted by the kernel
(nothing is executed). By default stage 1 runs exactly as in the evaluator (truncation self-check
and activity_dev); --quick checks only the DEV end. Not a trial. Each run appends one line to
ledger/sandbox_log.jsonl BEFORE it prints any metric (a kernel-fault exit writes its line too, status
kernel_fault). A program of unit top30 (KP-015) runs on the DEV universe panel
(omr.upipeline; membership from DEV bars only) with the universe engine; its benchmark is the
equal-weight long of the in-play members. KP-018: a top30 program also gets readings on DEV rows only, each by
the gate's own code (logged with the row, printed after it): G6's speed-limit statistic at one to three lag steps
(upipeline.dev_speed_limit), the DEV Sharpe on unit next30 (upipeline.next30_score, G8's function, run after the
top30 panel is released), the gross funding paid and received (the universe engine's running totals), the DEV
Sharpe under G2's funding stress and under G4's doubled costs (the gates' engine calls on DEV rows), and the
average number of names held next to the number in play; --g6-lags adds the DEV reading of G6's paired lag
comparison (upipeline.dev_paired_lags: a DEV reading, not the gate).
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
    ap.add_argument("--g6-lags", action="store_true", help="unit top30: also the DEV reading of G6's paired lag "
                    "comparison (10 stale copies over the last 365 days of DEV; a DEV reading, not the gate)")
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
    try:
        rel = path.resolve().relative_to(P.ROOT).as_posix()
    except ValueError:
        rel = path.name
    row = {"at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "file": rel,
           "source_sha256": ledger.sha256_file(path), "program": prog.name, "canonical": prog.canonical,
           "params": params, "kernel_hash": kh, "stage1": "quick" if a.quick else "full"}
    header = [f"SANDBOX (DEV only, {C.DEV_START} .. {C.DEV_END}) - not a trial",
              f"program {prog.name}  kind {prog.kind}  params {params}  nodes {prog.node_count}",
              f"canonical form (identity, with the semantic kernel hash and research_hash): {prog.canonical}"]
    if s1.get("code") == "kernel_fault":
        # U8: a kernel-fault exit writes its row too (before anything is printed)
        ledger.append(P.SANDBOX_LOG, dict(row, status="kernel_fault", fault=s1.get("fault")))
        for line in header:
            print(line)
        print(f"KERNEL FAULT in the {s1.get('fault')} self-check: report it; this program cannot be evaluated")
        sys.exit(2)
    W, grid = s1["W"], s1["grid"]
    if prog.unit != "core":
        fp = upipeline.Blocked(ud, "top30", fields=upipeline.program_fields(prog))
        mk = fp
        inplay = fp.inplay()
        k = inplay.sum(axis=1, keepdims=True)
        Wb = np.where(inplay, 1.0 / np.where(k > 0, k, 1), 0.0)
    else:
        mk = pipeline.Market(core, liq, grid, C.CORE)
        Wb = np.full_like(W, 1.0 / len(C.CORE))
    s, e = mk.pos(C.DEV_START), mk.pos(C.DEV_END)
    run = mk.run(W, s, e)
    daily = run.daily_returns()
    bench = mk.run(Wb, s, e).daily_returns()
    sm = S.summary(daily)
    rd, extra = None, {}
    if prog.unit != "core":
        n_unit = len(fp.symbols)
        rd = top30_readings(fp, s1, inplay, run, s, e, a.g6_lags)
        del fp, mk                                     # KP-018 (b): next30 only after the top30 panel is released
        rd["next30"] = upipeline.next30_score(prog, params, ud, end=C.DEV_END, keep=True)
        extra = readings_log(rd)
    # U8: the log row is appended BEFORE any metric is printed
    ledger.append(P.SANDBOX_LOG, dict(row, status="ok", dev_sharpe=sm["sharpe"], rebalances=run.n_rebalances,
                                      direction_changes_dev=s1["direction_changes_dev"], **extra))
    for line in header:
        print(line)
    print(f"stage 1: truncation self-check OK ({s1['cuts']} cuts)  direction changes (DEV) {s1['direction_changes_dev']} "
          f"(need >= {C.MIN_DIRECTION_CHANGES_DEV})  -> {'PASS' if s1['ok'] else 'activity_dev'}")
    if prog.unit != "core":
        print(f"unit {prog.unit}: {n_unit} symbols ever in the unit on DEV; lookback {prog.lookback_hours} h")
    print(f"DEV Sharpe {sm['sharpe']:.3f}  PSR(0) {sm['psr0']:.3f}  total {sm['total_return']:.3f}  CAGR {sm['cagr']:.3f}  "
          f"maxDD {sm['max_drawdown']:.3f}  Calmar {sm['calmar']:.3f}")
    print(f"rebalances {run.n_rebalances}  avg gross {run.gross.mean():.3f}  avg net {run.net.mean():.3f}  "
          f"funding paid {run.funding_paid:.4f}  costs {run.ev_cost.sum():.4f}  liquidated {run.liquidated}")
    print(f"benchmark (long 1/K each; top30: in-play members) DEV Sharpe {S.sharpe(bench):.3f}  maxDD {S.max_drawdown(bench):.3f}")
    print("year   days   return   sharpe   maxDD")
    for r in S.per_year(daily):
        print(f"{r['year']}  {r['n_days']:5d}  {r['return']:7.3f}  {r['sharpe']:7.3f}  {r['max_drawdown']:6.3f}")
    if rd is not None:
        for line in readings_lines(rd):
            print(line)


def top30_readings(fp, s1: dict, inplay, run, s: int, e: int, g6_lags: bool) -> dict:
    """KP-018, unit top30, DEV rows only (fp: the DEV Blocked panel; s1: stage 1 on the same grid; run: the base DEV
    run s..e). Every reading uses the gate's own code; next30 is added by the caller after fp is released."""
    W, kn = s1["W"], s1["known"]
    out = {"speed_limit": upipeline.dev_speed_limit(fp, W, kn, inplay),
           "names": upipeline.dev_names_held(W, inplay, s, e),
           "funding_paid_gross": float(run.funding_paid_gross), "funding_received_gross": float(run.funding_received_gross),
           "funding_net": float(run.funding_paid),
           "g2_dev_sharpe": pipeline.dev_sharpe_of(fp.run(W, s, e, pay=C.FUNDING_STRESS_PAY, recv=C.FUNDING_STRESS_RECV)),
           "g4_dev_sharpe": pipeline.dev_sharpe_of(fp.run(W, s, e, cost_mult=C.COST_STRESS_MULT))}
    if g6_lags:
        out["paired"] = upipeline.dev_paired_lags(fp, W, kn, inplay)
    return out


def readings_log(rd: dict) -> dict:
    """The KP-018 fields of the logged sandbox row (no row after DEV end is behind any of them)."""
    sl, n30, nm = rd["speed_limit"], rd["next30"], rd["names"]
    out = {"g6_memory_dev": sl.get("r"), "g6_memory_dev_max": sl.get("max"),
           "g6_memory_dev_from": str(sl["start"]) if sl.get("ok") else None,
           "next30_dev_sharpe": n30.get("sharpe"), "next30_code": n30.get("code"), "next30_symbols": n30.get("symbols"),
           "funding_paid_gross": rd["funding_paid_gross"], "funding_received_gross": rd["funding_received_gross"],
           "g2_dev_sharpe": rd["g2_dev_sharpe"], "g4_dev_sharpe": rd["g4_dev_sharpe"],
           "names_held_avg": nm["held"], "names_inplay_avg": nm["inplay"]}
    if "paired" in rd:
        pr = rd["paired"]
        out["g6_paired_dev"] = ({k: pr[k] for k in ("lags", "at_least_as_good", "p", "book_median", "stale_median")}
                                if pr.get("ok") else {"lags": pr["lags"], "reason": pr.get("reason")})
    return out


def readings_lines(rd: dict) -> list:
    sl, n30, nm = rd["speed_limit"], rd["next30"], rd["names"]
    out = ["top30 readings on DEV rows only (uncounted; KP-018):"]
    if sl.get("ok"):
        rs = "  ".join(f"r({j} step{'s' if j > 1 else ''}) {r:.3f}" for j, r in enumerate(sl["r"], start=1))
        out.append(f"  G6 speed limit as G6 computes it (lag step {sl['step']} h; decision rows {sl['start']} .. "
                   f"{sl['end']}):")
        out.append(f"    {rs}  max {sl['max']:.3f}  limit {sl['limit']:.2f} -> "
                   f"{'OVER the limit' if sl['over'] else 'under the limit'}")
        out.append(f"    (G6 on VAL takes the max over 1 to {C.UNIVERSE_G6_LAGS - 1} steps; an undefined correlation "
                   "counts as over)")
    else:
        out.append(f"  G6 speed limit: {sl.get('reason')}")
    if n30.get("code") is None:
        out.append(f"  next30 (G8's unit, ranks 31-60): DEV Sharpe {n30['sharpe']:.3f}  ({n30['symbols']} symbols ever in "
                   "next30 on DEV)")
    else:
        out.append(f"  next30 (G8's unit, ranks 31-60): no DEV Sharpe ({n30['code']})")
    out.append(f"  funding paid {rd['funding_paid_gross']:.4f}  received {rd['funding_received_gross']:.4f}  net "
               f"{rd['funding_net']:.4f}  (G2 counts paid x{C.FUNDING_STRESS_PAY:g} and received x{C.FUNDING_STRESS_RECV:g})")
    out.append(f"  G2 on DEV (funding paid x{C.FUNDING_STRESS_PAY:g}, received x{C.FUNDING_STRESS_RECV:g}): DEV Sharpe "
               f"{rd['g2_dev_sharpe']:.3f}   G4 on DEV (costs x{C.COST_STRESS_MULT:g}): DEV Sharpe {rd['g4_dev_sharpe']:.3f}")
    if nm["held"] is None:
        out.append("  names held: no DEV decision row with a unit")
    else:
        out.append(f"  names held: average {nm['held']:.1f} of {nm['inplay']:.1f} in play (DEV decision rows with a unit)")
    if "paired" in rd:
        pr = rd["paired"]
        if pr.get("ok"):
            out.append(f"  G6 paired lag reading - a DEV reading, NOT the gate ({pr['lags']} stale copies at "
                       f"{pr['lag_min'] // 24} to {pr['lag_max'] // 24} days; decisions {pr['start']} .. {pr['end']}):")
            out.append(f"    stale copies at least as good as the book: {pr['at_least_as_good']} of {pr['lags']} (p "
                       f"{pr['p']:.3f}; on VAL, G6 compares the book with {C.UNIVERSE_G6_LAGS} stale copies)")
            out.append(f"    book Sharpe on the common names, median over lags {pr['book_median']:.3f}; stale copies median "
                       f"{pr['stale_median']:.3f}")
        else:
            out.append(f"  G6 paired lag reading (a DEV reading, not the gate): {pr.get('reason')}")
    return out


if __name__ == "__main__":
    main()
