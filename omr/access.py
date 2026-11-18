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
only code that runs is the kernel's.
"""
from __future__ import annotations

import datetime as dt
import secrets

from omr import paths as P

_ISSUER = object()


class ValHandle:
    __slots__ = ("purpose", "trial_id", "token")

    def __init__(self, purpose: str, trial_id, token: str, _issuer=None):
        if _issuer is not _ISSUER:
            raise PermissionError("VAL handles are issued only by the ledger (access.for_trial / for_calibration / "
                                  "for_census / for_selftest)")
        self.purpose = purpose
        self.trial_id = trial_id
        self.token = token

    def __repr__(self):
        return f"ValHandle({self.purpose!r}, trial={self.trial_id})"


def require(handle, what: str) -> None:
    if not isinstance(handle, ValHandle):
        raise PermissionError(f"{what} touches bars after DEV end and needs a ledger-issued ValHandle")


def _now():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def for_trial(trial_id: str, pending_row_hash: str) -> ValHandle:
    """Called by omr.ledger.append_pending only, after the counted pending row is on disk."""
    return ValHandle("trial", trial_id, pending_row_hash, _issuer=_ISSUER)


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


def for_selftest(purpose: str = "selftest") -> ValHandle:
    """The kernel selftest (omr.selftest): reads real DEV+VAL bars, scores only kernel noise programs
    into a temporary ledger and returns no metric. The single exception to 'any scored run on VAL
    bars is a counted trial' (CONSTITUTION.md)."""
    return _logged(purpose, "selftest")
