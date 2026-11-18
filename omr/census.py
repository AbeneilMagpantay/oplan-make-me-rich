"""Forward census of the paper pool: python -m omr.census [--no-update]

1. Updates the data (append only; the research_hash must not change).
2. For each pool member, parses the program from the ledger's frozen source copy (hash-checked;
   the member's SEMANTICS_VERSION must equal the kernel's), interprets it on all data (the
   "latest" ceiling), and runs the engine flat from birth on post-birth bars only. Birth = the
   later of the trial's born_at and its pool admission, rounded up to the next bar open, and never
   before the bar after VAULT_END (vault performance is never computed).
3. Stores forward daily returns (complete UTC days only) raw and at deploy_scale in
   ledger/forward/<trial_id>.parquet, prints days forward / forward return / current target
   weights, and appends a census row only when something changed (idempotent).

This module and omr/data.py are the only kernel modules allowed to use the "latest" ceiling.
"""
from __future__ import annotations

import argparse
import datetime as dt

import numpy as np
import pandas as pd

from omr import access
from omr import constants as C
from omr import data
from omr import datasets as D
from omr import engine as E
from omr import kernel_lock
from omr import lang as L
from omr import ledger
from omr import paths as P
from omr import pipeline
from omr import pool
from omr import stats as S


def T(s) -> pd.Timestamp:
    t = pd.Timestamp(s)
    t = t.tz_localize("UTC") if t.tzinfo is None else t.tz_convert("UTC")
    return t.as_unit("ns")


def forward_start(trial_row: dict, pool_row: dict) -> pd.Timestamp:
    birth = max(T(trial_row["born_at"]), T(pool_row["at"]))
    start = birth.ceil("h")
    return max(start, T(C.VAULT_END) + pd.Timedelta(hours=1))


def member_program(trial_row: dict) -> L.Program:
    tid = trial_row["trial_id"]
    src = P.TRIAL_SOURCE_DIR / f"{tid}.omr"
    if ledger.sha256_file(src) != trial_row["source_sha256"]:
        raise RuntimeError(f"frozen source of {tid} does not match its ledger hash")
    if trial_row.get("semantics_version") != C.SEMANTICS_VERSION:
        raise RuntimeError(f"{tid} was evaluated under SEMANTICS_VERSION {trial_row.get('semantics_version')}, "
                           f"the kernel's is {C.SEMANTICS_VERSION}")
    text = src.read_bytes().decode("utf-8")
    prog = L.parse(text, trial_row["program"])
    if prog.canonical != trial_row["canonical"]:
        raise RuntimeError(f"frozen source of {tid} no longer parses to its recorded canonical form")
    return prog


def run_member(trial_row: dict, pool_row: dict, frames: dict, liqs: dict) -> dict:
    tid = trial_row["trial_id"]
    prog = member_program(trial_row)
    params = trial_row["params"]
    grid = pipeline.core_grid(frames, C.CORE)
    W, _ = pipeline.unit_signals(prog, params, frames, C.CORE, frames[C.BTC], grid)
    start = forward_start(trial_row, pool_row)
    scale = float(trial_row.get("deploy_scale") or 1.0)
    out = {"trial_id": tid, "program": prog.name, "forward_start": str(start),
           "deploy_scale": scale, "current_target_weights": {s: float(w) for s, w in zip(C.CORE, W[-1])},
           "data_end": str(grid[-1])}
    if start not in grid or start > grid[-1]:
        out.update({"days_forward": 0, "forward_return_raw": 0.0, "forward_return_scaled": 0.0,
                    "forward_sharpe_raw": None})
        return out
    mk = pipeline.Market(frames, liqs, grid, C.CORE)
    s = int(grid.get_loc(start))
    e = len(grid) - 1
    raw = mk.run(W, s, e)
    scaled = mk.run(W * scale, s, e)
    keep = E.daily_complete_mask(grid[s:e + 1])            # daily intervals that end at a 00:00 bar
    dr = raw.daily_returns()[keep]
    ds = scaled.daily_returns()[keep]
    P.FORWARD_DIR.mkdir(parents=True, exist_ok=True)
    pd.DataFrame({"ret_raw": dr, "ret_scaled": ds}).to_parquet(P.FORWARD_DIR / f"{tid}.parquet")
    out.update({"days_forward": int(len(dr)), "forward_return_raw": S.total_return(dr),
                "forward_return_scaled": S.total_return(ds),
                "forward_sharpe_raw": S.sharpe(dr) if len(dr) > 1 else None,
                "liquidated_raw": bool(raw.liquidated)})
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m omr.census")
    ap.add_argument("--no-update", action="store_true", help="skip the data update (offline)")
    a = ap.parse_args(argv)
    kernel_lock.require_kernel()
    if not a.no_update:
        try:
            data.snapshot("update", log=lambda s: print("  data: " + s, flush=True))
        except Exception as e:
            print(f"  data update FAILED, using stored data: {type(e).__name__}: {str(e)[:300]}")
    manifest = data.load_manifest()
    mem = pool.members()
    results = []
    if mem:
        handle = access.for_census(f"census of {len(mem)} pool member(s)")
        frames = D.load_frames(C.CORE, D.PROGRAM_EXTRA, upto="latest", handle=handle)
        liqs = D.load_liqs(C.CORE, upto="latest", handle=handle)
        st = ledger.trial_states()
        for tid, prow in mem.items():
            trow = {**st[tid]["pending"], **st[tid]["final"]}       # pending row: source hash, canonical
            results.append(run_member(trow, prow, frames, liqs))
    print(f"census at data end {manifest['snapshot_end']} - pool {len(mem)} member(s)")
    for r in results:
        w = ", ".join(f"{k} {v:+.3f}" for k, v in r["current_target_weights"].items())
        print(f"  {r['trial_id']}  {r['program']}  forward from {r['forward_start']}  days {r['days_forward']}  "
              f"return raw {r['forward_return_raw']:+.4f}  at deploy_scale {r['deploy_scale']:.3f}: "
              f"{r['forward_return_scaled']:+.4f}  target weights now: {w}")
    body = {"snapshot_end": manifest["snapshot_end"], "members": results}
    prev = ledger.read_rows(P.CENSUS_LOG)
    last = prev[-1] if prev else None
    if last is None or ledger.canonical({k: last[k] for k in ("snapshot_end", "members")}) != ledger.canonical(body):
        ledger.append(P.CENSUS_LOG, {"at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), **body})
        print("  census row appended")
    else:
        print("  nothing changed since the last census (no row appended)")


if __name__ == "__main__":
    main()
