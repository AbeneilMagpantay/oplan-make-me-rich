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

KERNEL_LOCK = ROOT / "kernel.lock"
STRATEGIES_DIR = ROOT / "strategies"
GENERATIONS_DIR = ROOT / "generations"
PROGRAMS_DIR = ROOT / "omr" / "programs"          # kernel programs (baselines, selftest), hash-locked

# Trial-ledger locations that a temporary ledger replaces (kernel_history stays where it is).
_LEDGER_NAMES = {"LEDGER_DIR": "", "TRIALS_JSONL": "trials.jsonl", "STAGE1_LOG": "stage1_log.jsonl",
                 "TRIAL_DETAIL_DIR": "trials", "TRIAL_SOURCE_DIR": "sources", "RETURNS_DIR": "returns",
                 "FORWARD_DIR": "forward", "SANDBOX_LOG": "sandbox_log.jsonl", "POOL_LOG": "pool_log.jsonl",
                 "CENSUS_LOG": "census_log.jsonl", "VAL_ACCESS_LOG": "val_access_log.jsonl"}


@contextmanager
def temporary_ledger(root: Path, generations: Path | None = None):
    """Point every trial-ledger path (and optionally the generations folder) at `root` for the
    duration of the block; restore afterwards. Used by the selftest and calibration only."""
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
