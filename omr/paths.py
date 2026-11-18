"""Filesystem locations. Kernel module."""
from contextlib import contextmanager
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
MANIFEST = DATA_DIR / "manifest.json"

LEDGER_DIR = ROOT / "ledger"
TRIALS_JSONL = LEDGER_DIR / "trials.jsonl"
STAGE1_LOG = LEDGER_DIR / "stage1_log.jsonl"
TRIAL_DETAIL_DIR = LEDGER_DIR / "trials"
TRIAL_SOURCE_DIR = LEDGER_DIR / "sources"
RETURNS_DIR = LEDGER_DIR / "returns"
FORWARD_DIR = LEDGER_DIR / "forward"
KERNEL_HISTORY = LEDGER_DIR / "kernel_history.jsonl"
SANDBOX_LOG = LEDGER_DIR / "sandbox_log.jsonl"
POOL_LOG = LEDGER_DIR / "pool_log.jsonl"
CENSUS_LOG = LEDGER_DIR / "census_log.jsonl"
VAL_ACCESS_LOG = LEDGER_DIR / "val_access_log.jsonl"

# The REAL trial ledger and the REAL VAL access log. temporary_ledger never redirects these two:
# VAL_ACCESS_LOG is the audit trail of every VAL read, and REAL_TRIALS_JSONL is where a trial
# handle's pending row must exist for its VAL reads to need no extra log row (omr.access).
REAL_TRIALS_JSONL = LEDGER_DIR / "trials.jsonl"
# Every artifact omr.calibrate writes into ledger/ gets a hash-chained row here; seal needs it.
CALIBRATION_LOG = LEDGER_DIR / "calibration_log.jsonl"

KERNEL_LOCK = ROOT / "kernel.lock"
STRATEGIES_DIR = ROOT / "strategies"
GENERATIONS_DIR = ROOT / "generations"
PROGRAMS_DIR = ROOT / "omr" / "programs"          # kernel programs (baselines, selftest), hash-locked

# Trial-ledger locations that a temporary ledger replaces. NOT replaced: KERNEL_HISTORY,
# VAL_ACCESS_LOG and REAL_TRIALS_JSONL (the VAL access log is always the real file).
_LEDGER_NAMES = {"LEDGER_DIR": "", "TRIALS_JSONL": "trials.jsonl", "STAGE1_LOG": "stage1_log.jsonl",
                 "TRIAL_DETAIL_DIR": "trials", "TRIAL_SOURCE_DIR": "sources", "RETURNS_DIR": "returns",
                 "FORWARD_DIR": "forward", "SANDBOX_LOG": "sandbox_log.jsonl", "POOL_LOG": "pool_log.jsonl",
                 "CENSUS_LOG": "census_log.jsonl"}


@contextmanager
def temporary_ledger(root: Path, generations: Path | None = None):
    """Point every trial-ledger path (and optionally the generations folder) at `root` for the
    duration of the block; restore afterwards. Used by the selftest. The VAL access log is never
    redirected: a VAL read by a trial whose pending row is not in the real trial ledger is logged
    there (kind temp_ledger_trial)."""
    g = globals()
    saved = {k: g[k] for k in list(_LEDGER_NAMES) + ["GENERATIONS_DIR"]}
    try:
        root = Path(root)
        for k, rel in _LEDGER_NAMES.items():
            g[k] = root / rel if rel else root
        if generations is not None:
            g["GENERATIONS_DIR"] = Path(generations)
        root.mkdir(parents=True, exist_ok=True)
        yield root
    finally:
        g.update(saved)
