"""Kernel selftest: python -m omr.selftest   (prints ONLY `OK` or the failed assertion and file:line)

The single exception to "any scored run on VAL bars is a counted trial" (CONSTITUTION.md): it reads
real DEV+VAL bars under a logged `selftest` handle and scores ONLY the kernel's two noise programs,
into a temporary ledger that is deleted afterwards. No metric leaves this module: run() returns
"OK" or the name and location of the first failed assertion, nothing else.

1. Interpreter smoke: the five baseline programs and the kitchen-sink program (every field,
   timeframe and function) on real DEV+VAL frames. Shape, alignment, finiteness and bounds only;
   nothing is scored.
2. Pipeline smoke: kernel_noise_single and kernel_noise_portfolio through the complete evaluate
   path (generation rules, stage 1, pending row, stage 2, result files, final row) on a temporary
   ledger. Asserts: status evaluated; every metric and gate input finite; every G8 unit scored, with
   the expected unit count; G6 p in (0, 1]; activity above both thresholds; the daily-return length;
   stage-2 DEV rows equal to stage 1 (no kernel_fault); `ledger verify` clean on the temporary ledger.
"""
from __future__ import annotations

import json
import math
import shutil
import sys
import tempfile
import traceback
from pathlib import Path

import numpy as np
import pandas as pd

from omr import access
from omr import constants as C
from omr import evaluate
from omr import kernel_lock
from omr import lang as L
from omr import ledger
from omr import paths as P
from omr import pipeline

SMOKE_PROGRAMS = ("gen000_sma_cross_ls", "gen000_donchian_ls", "gen000_rsi_meanrev_ls", "gen000_voltarget_trend_ls",
                  "gen000_funding_carry", "kernel_kitchen_sink")
NOISE_PROGRAMS = ("kernel_noise_single", "kernel_noise_portfolio")
HOUR_NS = 3_600_000_000_000


class SelftestFailure(Exception):
    def __init__(self, where: str):
        super().__init__(where)
        self.where = where


def _here(depth: int = 2) -> str:
    f = sys._getframe(depth)
    try:
        rel = Path(f.f_code.co_filename).resolve().relative_to(P.ROOT).as_posix()
    except ValueError:
        rel = Path(f.f_code.co_filename).name
    return f"{rel}:{f.f_lineno}"


def check(cond, name: str):
    if not bool(cond):
        raise SelftestFailure(f"{name} at {_here()}")


def _finite_numbers(o) -> bool:
    if isinstance(o, dict):
        return all(_finite_numbers(v) for v in o.values())
    if isinstance(o, (list, tuple)):
        return all(_finite_numbers(v) for v in o)
    if isinstance(o, bool) or o is None:
        return True
    if isinstance(o, (int, float, np.integer, np.floating)):
        return math.isfinite(float(o))
    if isinstance(o, str):
        return o not in ("inf", "-inf")
    return True


class _Cached:
    """Wraps a provider so the research-hash check runs once."""

    def __init__(self, base, rh):
        self.base, self.rh = base, rh

    def check(self):
        return self.rh

    def dev_frames(self):
        return self.base.dev_frames()

    def val_world(self, handle):
        return self.base.val_world(handle)


def interpreter_smoke(world: pipeline.World):
    syms = list(world.symbols)
    grid = pipeline.core_grid(world.core, syms)
    grid = grid[grid <= pd.Timestamp(C.VAL_END, tz="UTC")]
    check(len(grid) > 0 and grid[-1] == pd.Timestamp(C.VAL_END, tz="UTC"), "grid_ends_at_val_end")
    check(bool(np.all(np.diff(grid.asi8) == HOUR_NS)), "grid_hourly_without_gaps")
    for stem in SMOKE_PROGRAMS:
        prog = L.parse_file(P.PROGRAMS_DIR / f"{stem}.omr")
        params = L.default_params(prog)
        W, raw = pipeline.unit_signals(prog, params, world.core, syms, world.btc, grid)
        W2, raw2 = pipeline.unit_signals(prog, params, world.core, syms, world.btc, grid)
        check(W.shape == (len(grid), len(syms)) and raw.shape == W.shape, f"shape_{stem}")
        check(pipeline.same_rows(raw, raw2) and np.array_equal(W, W2), f"deterministic_{stem}")
        check(not np.isinf(raw).any(), f"raw_no_inf_{stem}")
        check(np.isfinite(W).all(), f"weights_finite_{stem}")
        if prog.kind == "single":
            check(np.abs(W).max() <= 1.0 / len(syms) + 1e-12, f"single_bounds_{stem}")
        else:
            check(np.abs(W).sum(axis=1).max() <= 1.0 + 1e-9, f"portfolio_gross_{stem}")
        val = grid >= pd.Timestamp(C.VAL_START, tz="UTC")
        check(np.isfinite(raw[val]).any(), f"defined_in_val_{stem}")


def pipeline_smoke(provider, p_max: float, tmp: Path):
    gens = tmp / "generations"
    (gens / "gen000").mkdir(parents=True)
    (gens / "gen000" / "PLAN.md").write_text("selftest: kernel noise programs only (temporary ledger)\n", encoding="ascii")
    progdir = tmp / "programs"
    progdir.mkdir()
    expected_days = int((pd.Timestamp(C.VAL_END, tz="UTC").normalize() - pd.Timestamp(C.DEV_START, tz="UTC"))
                        / pd.Timedelta(days=1)) + 1
    with P.temporary_ledger(tmp / "ledger", generations=gens):
        for stem in NOISE_PROGRAMS:
            src = progdir / f"{stem}.omr"
            shutil.copyfile(P.PROGRAMS_DIR / f"{stem}.omr", src)
            prog = L.parse_file(src)
            row = evaluate.evaluate_file(str(src), 0, provider=provider, quiet=True, require_lock=False, p_max=p_max)
            check(row.get("status") != "kernel_fault", f"no_kernel_fault_{stem}")
            check(row.get("status") == "evaluated", f"evaluated_{stem}")
            for k in ("dev_sharpe", "val_sharpe", "psr0", "dsr", "val_max_drawdown", "dev_val_max_drawdown",
                      "deploy_scale", "turnover_per_year", "avg_gross_exposure", "benchmark_val_sharpe"):
                check(isinstance(row.get(k), (int, float)) and math.isfinite(row[k]), f"finite_{k}_{stem}")
            check(_finite_numbers(row["gate_values"]), f"finite_gate_values_{stem}")
            check(set(row["gates"]) == {"G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8", "G10"}, f"gate_set_{stem}")
            check(all(v is not None for v in row["gates"].values()), f"every_gate_decided_{stem}")
            p = row["gate_values"]["G6"]
            check(isinstance(p, float) and 0.0 < p <= 1.0, f"g6_p_in_unit_interval_{stem}")
            rows = ledger.read_rows(P.TRIALS_JSONL)
            check(sum(1 for r in rows if r["trial_id"] == row["trial_id"] and r["status"] == "pending") == 1,
                  f"one_pending_row_{stem}")
            detail = json.loads((P.TRIAL_DETAIL_DIR / f"{row['trial_id']}.json").read_text(encoding="ascii"))
            units = detail.get("extended") or []
            n_expected = len(C.EXTENDED) if prog.kind == "single" else len(C.EXTENDED) // len(C.CORE)
            check(len(units) == n_expected, f"g8_unit_count_{stem}")
            check(all(u.get("code") is None and math.isfinite(u["sharpe"]) for u in units), f"g8_every_unit_scored_{stem}")
            check(_finite_numbers(detail["metrics"]) and _finite_numbers(detail["info"]), f"finite_metrics_{stem}")
            check(row["direction_changes_dev"] >= C.MIN_DIRECTION_CHANGES_DEV, f"activity_dev_{stem}")
            check(row["direction_changes_val"] >= C.G10_MIN_DIRECTION_CHANGES_VAL, f"activity_val_{stem}")
            rets = ledger.load_returns(row["trial_id"])
            check(len(rets) == expected_days and np.isfinite(rets.to_numpy()).all(), f"daily_return_length_{stem}")
        lines = []
        ok = ledger.verify_all(log=lines.append)
        check(ok and not any(x.startswith(("FAIL", "BAD", "INCOMPLETE")) for x in lines), "temp_ledger_verify_clean")
        check(len(ledger.counted_ids()) == len(NOISE_PROGRAMS), "temp_ledger_counted_two")


def run(provider=None, require_lock: bool = True, p_max: float | None = None, tmp_parent=None) -> str:
    """Returns "OK" or "<assertion> at <file>:<line>". Nothing else leaves this function."""
    tmp = None
    try:
        if require_lock:
            problems = kernel_lock.verify()
            check(not problems, "kernel_lock_verified")
            seal = kernel_lock.read_lock().get("seal")
            check(seal is not None, "kernel_sealed")
            p_max = float(seal["g6_threshold"])
        check(p_max is not None, "g6_threshold_available")
        provider = provider or evaluate.DiskProvider()
        try:
            rh = provider.check()
        except SystemExit:
            rh = None
        check(rh is not None, "data_matches_manifest_and_validated")
        provider = _Cached(provider, rh)
        handle = access.for_selftest("selftest: interpreter smoke on DEV+VAL frames; noise programs scored into "
                                     "a temporary ledger; no metric is kept")
        interpreter_smoke(provider.val_world(handle))
        tmp = Path(tempfile.mkdtemp(prefix="omr_selftest_", dir=tmp_parent))
        pipeline_smoke(provider, p_max, tmp)
        return "OK"
    except SelftestFailure as e:
        return e.where
    except Exception as e:                                  # type and location only, never a message
        tb = traceback.extract_tb(e.__traceback__)
        last = tb[-1] if tb else None
        where = "?"
        if last is not None:
            try:
                where = f"{Path(last.filename).resolve().relative_to(P.ROOT).as_posix()}:{last.lineno}"
            except ValueError:
                where = f"{Path(last.filename).name}:{last.lineno}"
        return f"unexpected_{type(e).__name__} at {where}"
    finally:
        if tmp is not None:
            shutil.rmtree(tmp, ignore_errors=True)


def main(argv=None):
    print(run())


if __name__ == "__main__":
    main()
