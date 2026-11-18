"""Kernel lock and seal, in two parts. Kernel module.

Kernel files: EVERY file under omr/ and tests/ (no exclusions: a stray __pycache__ or any other
file there fails verify), plus CONSTITUTION.md, LANGUAGE.md and requirements.txt. They form two
parts, each with its own hash:
- SEMANTIC: everything under omr/ (code, constants, the kernel programs) and requirements.txt -
  what runs. The trial identity and the seal bind to this hash.
- TEXT: CONSTITUTION.md, LANGUAGE.md and everything under tests/ - what describes or checks it.
kernel.lock stores every file hash, both part hashes and their combination.

CLI:
    python -m omr.kernel_lock verify
    python -m omr.kernel_lock hash
    python -m omr.kernel_lock rekey --reason "..." --approved-by "<name>"
    python -m omr.kernel_lock seal --calibration ledger/calibration_<hash16>.json

rekey rewrites kernel.lock and appends a hash-chained row to ledger/kernel_history.jsonl; it KEEPS
the seal when the semantic hash is unchanged (a text-only re-key) and drops it otherwise. seal
reads a calibration artifact that omr.calibrate wrote AND logged (ledger/calibration_log.jsonl,
hash-chained; the bytes must match), produced on the locked semantic kernel, re-applies the
calibration rule in code (omr.calibrate.decide on the stored per-pair rows) and, if a G6 threshold
qualifies and the stop rule passes, writes the threshold, the artifact's sha256 and the semantic
hash into kernel.lock and kernel_history.jsonl. omr.evaluate refuses an unsealed lock.

verify also checks: kernel.lock matches the latest kernel_history row (both hashes and the seal);
the seal belongs to the current semantic hash; the sealed artifact still has its sha256 and its
calibration_log row; the installed package versions equal the exact pins in requirements.txt (read
from the *.dist-info folders of the running environment) and the running Python the pinned one.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import platform
import sys
import sysconfig
from pathlib import Path

from omr import ledger
from omr import paths as P

KERNEL_DIRS = ("omr", "tests")
KERNEL_FILES = ("CONSTITUTION.md", "LANGUAGE.md", "requirements.txt")
SEAL_KEYS = ("g6_threshold", "calibration_file", "calibration_sha256", "semantic_hash")


def is_semantic(rel: str) -> bool:
    return rel.startswith("omr/") or rel == "requirements.txt"


def kernel_files(root: Path) -> list:
    root = Path(root)
    out = []
    for d in KERNEL_DIRS:
        base = root / d
        if base.exists():
            for p in base.rglob("*"):
                if p.is_file():
                    out.append(p.relative_to(root).as_posix())
    for f in KERNEL_FILES:
        if (root / f).exists():
            out.append(f)
    return sorted(out)


def _part_hash(files: dict) -> str:
    return hashlib.sha256("".join(f"{k}:{v}\n" for k, v in sorted(files.items())).encode("ascii")).hexdigest()


def compute(root: Path = None) -> dict:
    root = P.ROOT if root is None else root
    files = {}
    for rel in kernel_files(root):
        files[rel] = hashlib.sha256((Path(root) / rel).read_bytes()).hexdigest()
    semantic = _part_hash({k: v for k, v in files.items() if is_semantic(k)})
    text = _part_hash({k: v for k, v in files.items() if not is_semantic(k)})
    combined = hashlib.sha256(f"semantic:{semantic}\ntext:{text}\n".encode("ascii")).hexdigest()
    return {"files": files, "semantic": semantic, "text": text, "combined": combined}


def kernel_hash(root: Path = None) -> str:
    return compute(root)["combined"]


def semantic_hash(root: Path = None) -> str:
    return compute(root)["semantic"]


def read_lock(lock_path: Path = None):
    lock_path = P.KERNEL_LOCK if lock_path is None else lock_path
    if not Path(lock_path).exists():
        return None
    return json.loads(Path(lock_path).read_text(encoding="ascii"))


# ---------------------------------------------------------------- environment pins

def _norm(name: str) -> str:
    return name.lower().replace("_", "-").replace(".", "-")


def pins(req_path: Path = None) -> tuple:
    """({package: version}, python version or None) from requirements.txt (exact == pins only)."""
    req_path = (P.ROOT / "requirements.txt") if req_path is None else req_path
    out, py = {}, None
    for line in Path(req_path).read_text(encoding="ascii").splitlines():
        s = line.strip()
        if s.startswith("# python=="):
            py = s.split("==", 1)[1].strip()
            continue
        if not s or s.startswith("#"):
            continue
        if "==" not in s:
            raise ValueError(f"requirements.txt: not an exact pin: {s}")
        n, v = s.split("==", 1)
        out[_norm(n)] = v.strip()
    return out, py


def installed(site: Path = None) -> dict:
    """{package: version} from the METADATA of every *.dist-info folder in site-packages."""
    site = Path(sysconfig.get_paths()["purelib"]) if site is None else Path(site)
    out = {}
    for d in sorted(site.glob("*.dist-info")):
        meta = d / "METADATA"
        if not meta.exists():
            continue
        name = ver = None
        for line in meta.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.startswith("Name:") and name is None:
                name = line.split(":", 1)[1].strip()
            elif line.startswith("Version:") and ver is None:
                ver = line.split(":", 1)[1].strip()
            if not line.strip():
                break
        if name and ver:
            out[_norm(name)] = ver
    return out


IGNORED_DISTS = {"pip", "setuptools", "wheel"}


def env_problems(req_path: Path = None, site: Path = None) -> list:
    want, py = pins(req_path)
    have = installed(site)
    probs = []
    for n, v in sorted(want.items()):
        if n not in have:
            probs.append(f"pinned package not installed: {n}=={v}")
        elif have[n] != v:
            probs.append(f"installed {n} {have[n]} != pinned {v}")
    for n in sorted(set(have) - set(want) - IGNORED_DISTS):
        probs.append(f"installed package not pinned in requirements.txt: {n} {have[n]}")
    if py is None:
        probs.append("requirements.txt has no '# python==X.Y.Z' pin")
    elif platform.python_version() != py:
        probs.append(f"python {platform.python_version()} != pinned {py}")
    return probs


# ---------------------------------------------------------------- verify / rekey / seal

def _hist_semantic(row: dict):
    return row.get("new_semantic")


def verify(root: Path = None, lock_path: Path = None, history_path: Path = None, check_env: bool = True,
           calibration_log: Path = None) -> list:
    """Return problems (empty = kernel matches its lock, history, seal and environment pins)."""
    root = P.ROOT if root is None else root
    history_path = P.KERNEL_HISTORY if history_path is None else history_path
    calibration_log = P.CALIBRATION_LOG if calibration_log is None else calibration_log
    lock = read_lock(lock_path)
    if lock is None:
        return ["kernel.lock missing (run rekey once, with approval)"]
    cur = compute(root)
    problems = []
    for f in sorted(set(lock["files"]) | set(cur["files"])):
        if f not in cur["files"]:
            problems.append(f"kernel file removed: {f}")
        elif f not in lock["files"]:
            problems.append(f"file in kernel area not in the lock: {f}")
        elif lock["files"][f] != cur["files"][f]:
            problems.append(f"kernel file changed: {f}")
    for k in ("semantic", "text", "combined"):
        if lock.get(k) != cur[k] and not problems:
            problems.append(f"{k} hash mismatch")
    hist = ledger.read_rows(history_path)
    if not hist:
        problems.append("kernel_history.jsonl missing or empty")
    else:
        last = hist[-1]
        if last.get("new_semantic") != lock.get("semantic") or last.get("new_text") != lock.get("text") \
                or last.get("new_combined") != lock.get("combined"):
            problems.append("kernel.lock does not match the latest kernel_history row")
        seal = lock.get("seal")
        if seal is not None:
            if seal.get("semantic_hash") != lock.get("semantic"):
                problems.append("the seal belongs to another semantic kernel")
            if any(last.get(k) != seal.get(k) for k in SEAL_KEYS):
                problems.append("kernel.lock seal does not match the latest kernel_history row")
            art = Path(root) / seal["calibration_file"]
            if not art.exists() or ledger.sha256_file(art) != seal["calibration_sha256"]:
                problems.append("sealed calibration artifact missing or changed")
            if not _logged_artifact(calibration_log, seal["calibration_file"], seal["calibration_sha256"]):
                problems.append("sealed calibration artifact has no row in ledger/calibration_log.jsonl")
        elif last.get("calibration_sha256"):
            problems.append("kernel_history says sealed but kernel.lock has no seal")
        problems.extend(ledger.verify_chain(history_path))
        if Path(calibration_log).exists():
            problems.extend(ledger.verify_chain(calibration_log))
    if check_env:
        problems.extend(env_problems(Path(root) / "requirements.txt"))
    return problems


def _logged_artifact(calibration_log: Path, rel: str, sha: str) -> bool:
    return any(r.get("file") == rel and r.get("sha256") == sha for r in ledger.read_rows(calibration_log))


def log_calibration(path: Path, semantic_hash: str, research_hash: str, calibration_log: Path = None,
                    root: Path = None) -> dict:
    """Called by omr.calibrate right after it writes an artifact into ledger/ (M2)."""
    root = P.ROOT if root is None else root
    calibration_log = P.CALIBRATION_LOG if calibration_log is None else calibration_log
    rel = Path(path).resolve().relative_to(Path(root).resolve()).as_posix()
    return ledger.append(calibration_log, {"at": _now(), "file": rel, "sha256": ledger.sha256_file(path),
                                           "semantic_hash": semantic_hash, "research_hash": research_hash})


def _now():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _write_lock(lock: dict, lock_path: Path = None):
    lock_path = P.KERNEL_LOCK if lock_path is None else lock_path
    Path(lock_path).write_text(json.dumps(lock, indent=1, sort_keys=True), encoding="ascii")


def rekey(reason: str, approved_by: str, root: Path = None, lock_path: Path = None,
          history_path: Path = None) -> dict:
    """Rewrite kernel.lock. The seal is KEPT when the semantic hash is unchanged (a text-only re-key:
    documents or tests), and dropped otherwise (calibrate again, then seal)."""
    root = P.ROOT if root is None else root
    history_path = P.KERNEL_HISTORY if history_path is None else history_path
    if not reason or not reason.strip():
        raise ValueError("--reason is required")
    if not approved_by or not approved_by.strip():
        raise ValueError("--approved-by is required")
    old = read_lock(lock_path)
    cur = compute(root)
    changed = []
    if old:
        for f in sorted(set(old["files"]) | set(cur["files"])):
            if old["files"].get(f) != cur["files"].get(f):
                changed.append(f)
    now = _now()
    lock = {"created_at": now, "reason": reason, "approved_by": approved_by, **cur}
    kept = None
    if old and old.get("seal") and old.get("semantic") == cur["semantic"]:
        kept = old["seal"]
        lock["seal"] = kept
    _write_lock(lock, lock_path)
    row = {"at": now, "event": "rekey", "reason": reason, "approved_by": approved_by,
           "old_combined": old.get("combined") if old else None, "old_semantic": old.get("semantic") if old else None,
           "old_text": old.get("text") if old else None, "new_combined": cur["combined"],
           "new_semantic": cur["semantic"], "new_text": cur["text"], "changed_files": changed,
           "seal_kept": kept is not None}
    if kept is not None:
        row.update({k: kept[k] for k in SEAL_KEYS})
    ledger.append(history_path, row)
    return lock


class SealRefused(Exception):
    pass


def check_artifact(art: dict, lock: dict, research_hash: str) -> list:
    """Reasons the artifact cannot be sealed (empty = acceptable input to the rule)."""
    bad = []
    if art.get("kernel_lock_verified") is not True:
        bad.append("artifact was not produced on a verified kernel lock (kernel_lock_verified is not true)")
    if art.get("semantic_hash") != lock.get("semantic"):
        bad.append("artifact semantic_hash does not equal the locked semantic kernel")
    if art.get("research_hash") != research_hash:
        bad.append("artifact research_hash does not equal the stored data")
    fams = art.get("families") or {}
    from omr import calibrate
    if sorted(fams) != sorted(calibrate.FAMILIES):
        bad.append("artifact families are not the kernel's five baseline programs")
    for f, h in fams.items():
        if lock["files"].get(f"omr/programs/{f}.omr") != h:
            bad.append(f"artifact family {f} hash does not equal the locked kernel program")
    for k in ("nulls", "oracle"):
        if k not in art:
            bad.append(f"artifact has no {k}")
    return bad


def seal(artifact_path, root: Path = None, lock_path: Path = None, history_path: Path = None,
         research_hash: str | None = None, log=print, check_env: bool = True, calibration_log: Path = None) -> dict:
    """Apply the calibration rule in code to a LOGGED calibration artifact and write the G6 threshold."""
    from omr import calibrate
    from omr import data
    root = P.ROOT if root is None else root
    history_path = P.KERNEL_HISTORY if history_path is None else history_path
    calibration_log = P.CALIBRATION_LOG if calibration_log is None else calibration_log
    problems = verify(root, lock_path, history_path, check_env=check_env, calibration_log=calibration_log)
    if problems:
        raise SealRefused("kernel lock does not verify: " + "; ".join(problems[:5]))
    lock = read_lock(lock_path)
    if lock.get("seal") is not None:
        raise SealRefused("kernel.lock is already sealed (a semantic re-key removes the seal)")
    ap = Path(artifact_path)
    if not ap.is_absolute():
        ap = Path(root) / ap
    try:
        rel = ap.resolve().relative_to(Path(root).resolve()).as_posix()
    except ValueError:
        raise SealRefused("the calibration artifact must live inside the project folder")
    raw = ap.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    if not _logged_artifact(calibration_log, rel, sha):
        raise SealRefused("the artifact's bytes have no row in ledger/calibration_log.jsonl (only an artifact "
                          "exactly as omr.calibrate wrote it can be sealed)")
    art = json.loads(raw.decode("ascii"))
    rh = research_hash if research_hash is not None else data.load_manifest()["research_hash"]
    bad = check_artifact(art, lock, rh)
    if bad:
        raise SealRefused("; ".join(bad))
    verdict = calibrate.verdict_from_rows(art)
    if verdict.get("chosen_threshold") is None or verdict.get("STOP"):
        raise SealRefused("calibration rule: " + json.dumps(ledger.clean({k: verdict.get(k) for k in
                                                                          ("chosen_threshold", "reason",
                                                                           "below_power_min", "null_pass_rate")})))
    s = {"g6_threshold": verdict["chosen_threshold"], "calibration_file": rel, "calibration_sha256": sha,
         "semantic_hash": lock["semantic"], "sealed_at": _now(), "rule": verdict["rule"],
         "null_pass_rate": verdict["null_pass_rate"], "power_at_1_5": verdict["power_at_1_5_chosen"]}
    lock["seal"] = s
    _write_lock(lock, lock_path)
    ledger.append(history_path, {"at": s["sealed_at"], "event": "seal", "reason": "calibration seal (rule in code)",
                                 "approved_by": "omr.kernel_lock seal", "old_combined": lock["combined"],
                                 "new_combined": lock["combined"], "new_semantic": lock["semantic"],
                                 "new_text": lock["text"], "changed_files": [], **{k: s[k] for k in SEAL_KEYS}})
    log(f"sealed: G6 threshold {s['g6_threshold']}  calibration {rel}  sha256 {sha[:16]}")
    return lock


def require_kernel(log=print) -> dict:
    """Exit with an error if the kernel does not match its lock; returns the lock."""
    problems = verify()
    if problems:
        log("KERNEL LOCK MISMATCH - refusing to run:")
        for p in problems[:20]:
            log("  " + p)
        sys.exit(3)
    return read_lock()


def require_sealed(log=print) -> dict:
    """{semantic, text, combined, g6_threshold}; exits if the lock does not verify or is not sealed."""
    lock = require_kernel(log)
    seal_ = lock.get("seal")
    if not seal_:
        log("KERNEL NOT SEALED - refusing to evaluate: run the calibration on the locked kernel, then "
            "python -m omr.kernel_lock seal --calibration <artifact>")
        sys.exit(4)
    return {"semantic": lock["semantic"], "text": lock["text"], "combined": lock["combined"],
            "g6_threshold": float(seal_["g6_threshold"])}


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m omr.kernel_lock")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("verify")
    sub.add_parser("hash")
    rk = sub.add_parser("rekey")
    rk.add_argument("--reason", required=True)
    rk.add_argument("--approved-by", required=True)
    se = sub.add_parser("seal")
    se.add_argument("--calibration", required=True)
    a = ap.parse_args(argv)
    if a.cmd == "verify":
        pr = verify()
        if pr:
            print("KERNEL LOCK: FAIL")
            for p in pr:
                print("  " + p)
            sys.exit(1)
        lock = read_lock()
        s = lock.get("seal")
        n_sem = sum(1 for f in lock["files"] if is_semantic(f))
        print(f"KERNEL LOCK: OK  semantic {lock['semantic']} ({n_sem} files)  text {lock['text']} "
              f"({len(lock['files']) - n_sem} files)  " + (f"sealed G6 {s['g6_threshold']}" if s else "NOT SEALED"))
    elif a.cmd == "hash":
        cur = compute()
        print(f"semantic {cur['semantic']}\ntext {cur['text']}\ncombined {cur['combined']}")
    elif a.cmd == "rekey":
        lock = rekey(a.reason, a.approved_by)
        print(f"re-keyed: semantic {lock['semantic']}  text {lock['text']}  ({len(lock['files'])} files)  "
              + ("seal KEPT (semantic unchanged)" if lock.get("seal") else "(not sealed)"))
    else:
        try:
            seal(a.calibration)
        except SealRefused as e:
            print(f"SEAL REFUSED: {e}")
            sys.exit(2)


if __name__ == "__main__":
    main()
