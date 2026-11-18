"""Paper pool of forward-tested strategies.

    python -m omr.pool list
    python -m omr.pool admit <trial_id> --reason "..." [--replace <member_trial_id>]
    python -m omr.pool remove <trial_id> --reason "..."

Max 5 members, Tier-1 trials only, evaluated under the CURRENT semantic kernel hash (a text-only
re-key keeps members; a semantic re-key means members must be re-evaluated before the census can
run them). When full, admitting needs an explicit --replace. Every change is a
hash-chained row in ledger/pool_log.jsonl; the pool is the replay of that log.
"""
from __future__ import annotations

import argparse
import datetime as dt
import sys

from omr import constants as C
from omr import kernel_lock
from omr import ledger
from omr import paths as P


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def members() -> dict:
    """{trial_id: admission row} from replaying the pool log."""
    cur = {}
    for r in ledger.read_rows(P.POOL_LOG):
        if r["action"] == "admit":
            cur[r["trial_id"]] = r
        elif r["action"] == "remove":
            cur.pop(r["trial_id"], None)
    return cur


def admit(trial_id: str, reason: str, replace: str | None = None) -> None:
    row = ledger.find_trial(trial_id)
    if row is None:
        raise SystemExit(f"no trial {trial_id} in the ledger")
    if row.get("status") != "evaluated" or row.get("tier") != "tier1":
        raise SystemExit(f"trial {trial_id} is not Tier 1 (status {row.get('status')}, tier {row.get('tier')})")
    current = kernel_lock.read_lock()["semantic"]
    if row.get("semantic_hash") != current:
        raise SystemExit(f"trial {trial_id} was evaluated under semantic kernel {str(row.get('semantic_hash'))[:16]}, "
                         f"not the current {current[:16]}; it cannot be admitted")
    cur = members()
    if trial_id in cur:
        raise SystemExit(f"{trial_id} is already in the pool")
    if replace:
        if replace not in cur:
            raise SystemExit(f"--replace {replace} is not a pool member")
    elif len(cur) >= C.POOL_MAX:
        raise SystemExit(f"pool is full ({C.POOL_MAX}); name the member to replace with --replace")
    t = now()
    if replace:
        ledger.append(P.POOL_LOG, {"at": t, "action": "remove", "trial_id": replace,
                                   "reason": f"replaced by {trial_id}: {reason}"})
    ledger.append(P.POOL_LOG, {"at": t, "action": "admit", "trial_id": trial_id, "reason": reason,
                               "program": row.get("program"), "born_at": row.get("born_at"),
                               "deploy_scale": row.get("deploy_scale"), "kernel_hash": row.get("kernel_hash"),
                               "semantic_hash": row.get("semantic_hash"),
                               "admitted_under_kernel": kernel_lock.read_lock()["combined"]})
    print(f"admitted {trial_id} ({row.get('program')})" + (f", replacing {replace}" if replace else ""))


def remove(trial_id: str, reason: str) -> None:
    if trial_id not in members():
        raise SystemExit(f"{trial_id} is not a pool member")
    ledger.append(P.POOL_LOG, {"at": now(), "action": "remove", "trial_id": trial_id, "reason": reason})
    print(f"removed {trial_id}")


def show() -> None:
    cur = members()
    print(f"pool: {len(cur)} / {C.POOL_MAX}")
    for tid, r in cur.items():
        print(f"  {tid}  {r.get('program')}  born {r.get('born_at')}  admitted {r['at']}  deploy_scale {r.get('deploy_scale')}  "
              f"kernel {str(r.get('kernel_hash'))[:16]}")


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m omr.pool")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list")
    a1 = sub.add_parser("admit")
    a1.add_argument("trial_id")
    a1.add_argument("--reason", required=True)
    a1.add_argument("--replace")
    a2 = sub.add_parser("remove")
    a2.add_argument("trial_id")
    a2.add_argument("--reason", required=True)
    a = ap.parse_args(argv)
    kernel_lock.require_kernel()
    if a.cmd == "list":
        show()
    elif a.cmd == "admit":
        admit(a.trial_id, a.reason, a.replace)
    else:
        remove(a.trial_id, a.reason)


if __name__ == "__main__":
    main()
