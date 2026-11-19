"""Ledger-issued handles for access to VAL bars (and anything later). Kernel module.

Every data loader and pipeline entry point that touches bars after DEV end requires a
ValHandle. Handles are issued only:
- by the ledger, when it appends a trial's COUNTED `pending` row (for_trial), or
- with an explicit, logged purpose (for_calibration, for_census, for_selftest), which appends a
  hash-chained row to ledger/val_access_log.jsonl.
(`python -m omr.data validate` reads every stored row inside the data layer itself and prints counts
only; it needs no handle.)
A script that calls a VAL loader or the VAL pipeline without a handle raises PermissionError.
This is a tripwire for honest mistakes, not a security boundary: the quarantine of VAL is
procedural (CONSTITUTION.md). No strategy code exists that could hold or forge a handle; the
only code that runs is the kernel's. The VAL access log is the audit trail: it is never redirected
(paths.temporary_ledger leaves it alone), and a disk load of real VAL bars with a trial handle whose
pending row is not in the REAL trial ledger is logged there before any frame is returned
(note_val_read, kind temp_ledger_trial).
"""
from __future__ import annotations

import datetime as dt
import secrets

from omr import paths as P

_ISSUER = object()


class ValHandle:
    __slots__ = ("purpose", "trial_id", "token", "source_sha256", "noted")

    def __init__(self, purpose: str, trial_id, token: str, _issuer=None, source_sha256=None):
        if _issuer is not _ISSUER:
            raise PermissionError("VAL handles are issued only by the ledger (access.for_trial / for_calibration / "
                                  "for_census / for_selftest)")
        self.purpose = purpose
        self.trial_id = trial_id
        self.token = token
        self.source_sha256 = source_sha256
        self.noted = False

    def __repr__(self):
        return f"ValHandle({self.purpose!r}, trial={self.trial_id})"


def require(handle, what: str) -> None:
    if not isinstance(handle, ValHandle):
        raise PermissionError(f"{what} touches bars after DEV end and needs a ledger-issued ValHandle")


def _now():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def for_trial(trial_id: str, pending_row_hash: str, source_sha256=None) -> ValHandle:
    """Called by omr.ledger.append_pending only, after the counted pending row is on disk."""
    return ValHandle("trial", trial_id, pending_row_hash, _issuer=_ISSUER, source_sha256=source_sha256)


def _in_real_trial_ledger(handle: ValHandle) -> bool:
    from omr import ledger
    for r in ledger.read_rows(P.REAL_TRIALS_JSONL):
        if r.get("status") == "pending" and r.get("trial_id") == handle.trial_id and r.get("row_hash") == handle.token:
            return True
    return False


def note_val_read(handle: ValHandle) -> None:
    """Called by the disk loaders before any REAL bar after DEV end is returned. A trial handle whose
    pending row is not in the REAL trial ledger (a temporary ledger) gets one row in the real VAL
    access log (kind temp_ledger_trial), once per handle. Logged-purpose handles were logged when
    issued."""
    require(handle, "note_val_read")
    if handle.purpose != "trial" or handle.noted:
        return
    if not _in_real_trial_ledger(handle):
        from omr import ledger
        ledger.append(P.VAL_ACCESS_LOG, {"at": _now(), "kind": "temp_ledger_trial", "trial_id": handle.trial_id,
                                         "source_sha256": handle.source_sha256, "token": handle.token})
    handle.noted = True


def _logged(purpose: str, kind: str) -> ValHandle:
    from omr import ledger
    if not purpose or not purpose.strip():
        raise ValueError("a VAL access purpose is required")
    token = secrets.token_hex(8)
    ledger.append(P.VAL_ACCESS_LOG, {"at": _now(), "kind": kind, "purpose": purpose, "token": token})
    return ValHandle(f"{kind}: {purpose}", None, token, _issuer=_ISSUER)


def for_calibration(purpose: str) -> ValHandle:
    return _logged(purpose, "calibration")


def for_census(purpose: str = "census of the paper pool") -> ValHandle:
    return _logged(purpose, "census")


def for_membership(purpose: str) -> ValHandle:
    """The universe membership builder and data validate-style counts (omr.universe): reads klines of every
    region as kernel code and prints COUNTS only; no program is evaluated."""
    return _logged(purpose, "membership")


def for_selftest(purpose: str = "selftest") -> ValHandle:
    """The kernel selftest (omr.selftest): reads real DEV+VAL bars, scores only kernel noise programs
    into a temporary ledger and returns no metric. The single exception to 'any scored run on VAL
    bars is a counted trial' (CONSTITUTION.md)."""
    return _logged(purpose, "selftest")
