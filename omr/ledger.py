"""Append-only, hash-chained JSONL logs and the trial ledger. Kernel module.

Every chained file holds one JSON object per line with prev_hash and row_hash:
    row_hash = sha256(prev_hash + canonical_json(row without prev_hash/row_hash))
The first row's prev_hash is 64 zeros. HEAD.json next to the chains anchors each chain's
row count and head hash; it is rewritten on every append and checked by verify and evaluate.

Trial lifecycle:
- a stage-1 rejection (parse/static, activity_dev, or a kernel fault found by the truncation
  self-check) is NOT a trial: one row in ledger/stage1_log.jsonl, nothing in trials.jsonl;
- otherwise a COUNTED row status "pending" is appended to ledger/trials.jsonl and flushed BEFORE
  any VAL bar is read (it issues the trial's ValHandle); result files are written after it; the
  final row ("evaluated", "liquidated" or "kernel_fault") is appended last. A pending row without
  a final row is "incomplete" and still counted.

CLI:
    python -m omr.ledger verify      chains, HEAD anchors, trial file hashes, incomplete/orphans
    python -m omr.ledger summary     one line per trial
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from omr import paths as P

GENESIS = "0" * 64
HEAD_NAME = "HEAD.json"
COUNTED_FINAL = ("evaluated", "liquidated", "kernel_fault")


def clean(o):
    """Make an object JSON-safe and deterministic (NaN -> None, inf -> 'inf'/'-inf', numpy -> python)."""
    if isinstance(o, dict):
        return {str(k): clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean(v) for v in o]
    if isinstance(o, (np.bool_, bool)):
        return bool(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating, float)):
        f = float(o)
        if math.isnan(f):
            return None
        if math.isinf(f):
            return "inf" if f > 0 else "-inf"
        return f
    if isinstance(o, (pd.Timestamp,)):
        return str(o)
    return o


def canonical(o) -> str:
    return json.dumps(clean(o), sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)


def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_rows(path: Path) -> list:
    path = Path(path)
    if not path.exists():
        return []
    out = []
    for line in path.read_text(encoding="ascii").splitlines():
        if line.strip():
            out.append(json.loads(line))
    return out


def row_hash(prev: str, row: dict) -> str:
    body = {k: v for k, v in row.items() if k not in ("prev_hash", "row_hash")}
    return sha256_text(prev + canonical(body))


def _head_path(path: Path) -> Path:
    return Path(path).parent / HEAD_NAME


def read_head(path: Path) -> dict:
    hp = _head_path(path)
    if not hp.exists():
        return {}
    return json.loads(hp.read_text(encoding="ascii"))


def _write_head(path: Path, rows: int, head: str):
    hp = _head_path(path)
    cur = read_head(path)
    cur[Path(path).name] = {"rows": rows, "head": head}
    tmp = hp.with_suffix(".tmp")
    tmp.write_text(json.dumps(cur, indent=1, sort_keys=True), encoding="ascii")
    os.replace(tmp, hp)


def append(path: Path, row: dict) -> dict:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = read_rows(path)
    prev = rows[-1]["row_hash"] if rows else GENESIS
    body = clean({k: v for k, v in row.items() if k not in ("prev_hash", "row_hash")})
    body["prev_hash"] = prev
    body["row_hash"] = row_hash(prev, body)
    with open(path, "a", encoding="ascii", newline="\n") as f:
        f.write(canonical(body) + "\n")
        f.flush()
        os.fsync(f.fileno())
    _write_head(path, len(rows) + 1, body["row_hash"])
    return body


def verify_chain(path: Path) -> list:
    """Problems with the chain itself and with its HEAD anchor (empty = intact)."""
    problems = []
    prev = GENESIS
    rows = read_rows(path)
    for i, row in enumerate(rows):
        if row.get("prev_hash") != prev:
            problems.append(f"{Path(path).name} row {i}: prev_hash does not match the previous row")
        if row_hash(row.get("prev_hash", ""), row) != row.get("row_hash"):
            problems.append(f"{Path(path).name} row {i}: row_hash does not match its content")
        prev = row.get("row_hash", "")
    head = read_head(path).get(Path(path).name)
    if rows and head is None:
        problems.append(f"{Path(path).name}: no HEAD anchor")
    elif head is not None:
        if head.get("rows") != len(rows) or head.get("head") != (rows[-1]["row_hash"] if rows else GENESIS):
            problems.append(f"{Path(path).name}: HEAD anchor says {head.get('rows')} rows, chain has {len(rows)} "
                            "(rows removed or appended outside the ledger)")
    return problems


# ---------------------------------------------------------------- trials

def trials(path: Path | None = None) -> list:
    path = P.TRIALS_JSONL if path is None else path
    return read_rows(path)


def trial_states(path: Path | None = None) -> dict:
    path = P.TRIALS_JSONL if path is None else path
    """{trial_id: {"rows": [...], "counted": bool, "final": row|None, "pending": row|None, "status": str}}"""
    out = {}
    for r in trials(path):
        t = out.setdefault(r["trial_id"], {"rows": [], "counted": False, "final": None, "pending": None})
        t["rows"].append(r)
        if r["status"] == "pending":
            t["counted"] = True
            t["pending"] = r
        elif r["status"] in COUNTED_FINAL:
            t["final"] = r
    for t in out.values():
        if t["final"] is not None:
            t["status"] = t["final"]["status"]
        elif t["counted"]:
            t["status"] = "incomplete"
        else:
            t["status"] = t["rows"][-1]["status"]
    return out


def find_trial(trial_id: str, path: Path | None = None):
    path = P.TRIALS_JSONL if path is None else path
    """The trial's most informative row: final, else pending, else its only row."""
    st = trial_states(path).get(trial_id)
    if st is None:
        return None
    return st["final"] or st["pending"] or st["rows"][-1]


def counted_ids(path: Path | None = None) -> list:
    path = P.TRIALS_JSONL if path is None else path
    return [tid for tid, t in trial_states(path).items() if t["counted"]]


def counted_trials(path: Path | None = None) -> list:
    path = P.TRIALS_JSONL if path is None else path
    """Final rows of counted trials that were evaluated (have returns)."""
    return [t["final"] for t in trial_states(path).values() if t["final"] is not None and t["final"]["status"] == "evaluated"]


def append_pending(row: dict, path: Path | None = None):
    path = P.TRIALS_JSONL if path is None else path
    """Append the COUNTED pending row (flushed) and return (row, ValHandle) for stage 2."""
    from omr import access
    r = dict(row)
    r["status"] = "pending"
    written = append(path, r)
    return written, access.for_trial(written["trial_id"], written["row_hash"])


def returns_path(trial_id: str) -> Path:
    return P.RETURNS_DIR / f"{trial_id}.parquet"


def load_returns(trial_id: str) -> pd.Series:
    df = pd.read_parquet(returns_path(trial_id))
    return df["ret"]


def save_returns(trial_id: str, daily: pd.Series) -> str:
    p = returns_path(trial_id)
    p.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame({"ret": daily.astype(np.float64)}).to_parquet(p)
    return sha256_file(p)


def val_slice(daily: pd.Series) -> pd.Series:
    from omr import constants as C
    a = pd.Timestamp(C.VAL_START, tz="UTC")
    b = pd.Timestamp(C.VAL_END, tz="UTC")
    return daily[(daily.index >= a.normalize()) & (daily.index <= b)]


def counted_val_matrix(extra: dict | None = None) -> pd.DataFrame:
    """VAL daily returns of every counted trial THAT HAS stored returns (columns = trial ids),
    plus `extra` series."""
    cols = {}
    for r in counted_trials():
        if r.get("returns_sha256") and returns_path(r["trial_id"]).exists():
            cols[r["trial_id"]] = val_slice(load_returns(r["trial_id"]))
    for k, v in (extra or {}).items():
        cols[k] = val_slice(v)
    if not cols:
        return pd.DataFrame()
    return pd.DataFrame(cols).dropna(how="any")


def counted_in_generation(generation: int, path: Path | None = None) -> int:
    path = P.TRIALS_JSONL if path is None else path
    return sum(1 for t in trial_states(path).values() if t["counted"] and t["pending"].get("generation") == generation)


def highest_generation(path: Path | None = None):
    path = P.TRIALS_JSONL if path is None else path
    gens = [r.get("generation") for r in trials(path) if isinstance(r.get("generation"), int)]
    return max(gens) if gens else None


def verify_all(log=print) -> bool:
    ok = True
    for path in (P.TRIALS_JSONL, P.STAGE1_LOG, P.KERNEL_HISTORY, P.POOL_LOG, P.CENSUS_LOG, P.SANDBOX_LOG,
                 P.VAL_ACCESS_LOG):
        if Path(path).exists():
            pr = verify_chain(path)
            for x in pr:
                log("FAIL " + x)
            ok = ok and not pr
            log(("OK  " if not pr else "BAD ") + f"chain {Path(path).name} ({len(read_rows(path))} rows)")
    states = trial_states()
    referenced = {"returns": set(), "trials": set(), "sources": set()}
    for tid, t in states.items():
        for r in t["rows"]:
            for key, path, kind in (("detail_sha256", P.TRIAL_DETAIL_DIR / f"{tid}.json", "trials"),
                                    ("source_sha256", P.TRIAL_SOURCE_DIR / f"{tid}.omr", "sources"),
                                    ("returns_sha256", returns_path(tid), "returns")):
                want = r.get(key)
                if want is None:
                    continue
                referenced[kind].add(Path(path).name)
                if not Path(path).exists() or sha256_file(path) != want:
                    log(f"FAIL trial {tid}: {key} mismatch or file missing ({Path(path).name})")
                    ok = False
    incomplete = [tid for tid, t in states.items() if t["status"] == "incomplete"]
    for tid in incomplete:
        log(f"INCOMPLETE trial {tid}: pending row without a final row (counted)")
    for kind, d in (("returns", P.RETURNS_DIR), ("trials", P.TRIAL_DETAIL_DIR), ("sources", P.TRIAL_SOURCE_DIR)):
        if Path(d).exists():
            for f in Path(d).iterdir():
                if f.is_file() and f.name not in referenced[kind]:
                    log(f"INCOMPLETE orphan file {kind}/{f.name} (no ledger row references it)")
    log("ledger verify: " + ("OK" if ok else "FAILED") + (f" ({len(incomplete)} incomplete)" if incomplete else ""))
    return ok


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else "verify"
    if cmd == "verify":
        sys.exit(0 if verify_all() else 1)
    elif cmd == "summary":
        st = trial_states()
        print(f"{len(st)} trials, {sum(t['counted'] for t in st.values())} counted")
        for tid, t in st.items():
            r = t["final"] or t["pending"] or t["rows"][-1]
            g = r.get("gates") or {}
            gs = "".join("P" if g.get(k) else "F" for k in ("G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8", "G10")) \
                if g else "-"
            print(f"{tid}  gen {r.get('generation')}  {str(r.get('program', '?')):28s} {t['status']:18s} "
                  f"reason {r.get('reason', '-')}  tier {r.get('tier', '-')}  gates {gs}  VAL SR {r.get('val_sharpe')}  "
                  f"PSR0 {r.get('psr0')}  DSR {r.get('dsr')}")
    else:
        print("usage: python -m omr.ledger verify|summary")
        sys.exit(2)


if __name__ == "__main__":
    main()
