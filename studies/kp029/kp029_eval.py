"""KP-029 premise study (generation 4, round 2): the EVALUATOR. NOT kernel code; nothing in omr/ imports it.

It scores a program exactly as the kernel's DEV sandbox does for a top30 program (omr/sandbox.py, main and
top30_readings), by CALLING the kernel's own functions in the same order and with the same arguments; no kernel
code is copied, edited or patched, and omr.sandbox / omr.evaluate are never imported:

  stage 1   omr.upipeline.stage1_u (the kernel's truncation self-check over 24 random cuts + DEV end, its start
            cuts, its block_overlap check, the activity count)
  base      omr.upipeline.Blocked(ud, "top30").run(W, DEV start, DEV end) -> daily returns -> omr.stats.summary,
            omr.stats.per_year; the equal-weight benchmark of the in-play members
  G2, G4    the same engine with funding paid x1.5 / received x0.5, and with costs x2 (omr.pipeline.dev_sharpe_of)
  speed     omr.upipeline.dev_speed_limit (G6's speed-limit statistic at 1..3 lag steps of 621 h)
  names     omr.upipeline.dev_names_held
  paired    omr.upipeline.dev_paired_lags (10 stale copies over the last 365 days of DEV)
  next30    omr.upipeline.next30_score(..., end=DEV end, keep=True), after the top30 panel is released

The data are the kernel's (omr.upipeline.load_udata("dev_end", ...)): perpetual rows only through the kernel's
loaders under the DEV ceiling; no ValHandle exists in this study. For a study program the UData is the one of
kp029_features.study_udata (the same tables with the two spot slots filled).

Also here: the screen W1..W8 with the floor before costs at 1.85 (PLAN version 2), the corner and control rules,
the study's own truncation test (guard D2), the memory check, and the sha256 of the study's files.
"""
from __future__ import annotations

import ctypes
import datetime as dt
import hashlib
import math
import platform
import secrets
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from omr import constants as C  # noqa: E402
from omr import pipeline as PL  # noqa: E402
from omr import stats as S  # noqa: E402
from omr import upipeline as UP  # noqa: E402

import kp029_features as F  # noqa: E402

# ---------------------------------------------------------------- the pass rule (PLAN version 2, fixed in advance)
W1_DIRECTION_CHANGES = 30
W1_AVG_GROSS = 0.5
W1_NAMES = 15
W2_PRE_COST = 1.85                           # KP-029: the floor before costs raised from 1.5 to 1.85
W5_NEXT30 = 0.3
W6_SPEED = 0.40
W7_STALE_MAX = 4
W8_YEARS = 2
CONTROL_MARGIN = 0.5                          # pre-cost(hypothesis) - pre-cost(control) >= 0.5 (generation 3 rulings)

# ---------------------------------------------------------------- the study's truncation test (guard D2)
FIXED_CUTS = ("2020-08-16 23:00", "2020-12-13 22:00", "2021-04-11 23:00", "2021-08-18 13:00", "2021-12-19 23:00",
              "2022-05-10 07:00")             # Sunday 23:00 decision bars, one an hour before one, two mid-week
RANDOM_CUTS = 2

STUDY_FILES = ("kp029_spot.py", "kp029_features.py", "kp029_eval.py", "run_study.py", "download_spot.py",
               "spot_plan.py", "validate_evaluator.py", "synthetic_tests.py", "guard_table.py", "spot_symbols.json")


def T(s) -> pd.Timestamp:
    return UP.T(s)


def _f(x):
    """JSON-safe number."""
    if x is None:
        return None
    x = float(x)
    return x if math.isfinite(x) else (None if math.isnan(x) else ("inf" if x > 0 else "-inf"))


# ---------------------------------------------------------------- memory (the coordinator's rule)
def memory_kb() -> dict:
    """{"phys_kb", "commit_kb"}: available physical memory and available commit (GlobalMemoryStatusEx), or None."""
    class MS(ctypes.Structure):
        _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
    try:
        m = MS()
        m.dwLength = ctypes.sizeof(MS)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m)):
            return {"phys_kb": int(m.ullAvailPhys // 1024), "commit_kb": int(m.ullAvailPageFile // 1024)}
    except Exception:
        pass
    return {"phys_kb": None, "commit_kb": None}


def memory_ok(m: dict) -> bool:
    return (m.get("phys_kb") or 0) >= 1_000_000 and (m.get("commit_kb") or 0) >= 4_000_000


# ---------------------------------------------------------------- hashes
def study_hashes() -> dict:
    out = {}
    for name in STUDY_FILES:
        p = HERE / name
        out[name] = hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None
    for p in sorted((HERE / "programs").glob("*.omr")):
        out["programs/" + p.name] = hashlib.sha256(p.read_bytes()).hexdigest()
    return out


def versions() -> dict:
    import numba
    import scipy
    return {"python": platform.python_version(), "numpy": np.__version__, "pandas": pd.__version__,
            "numba": numba.__version__, "scipy": scipy.__version__}


# ---------------------------------------------------------------- evaluation
def stage1(prog, params: dict, ud, seed=None, cuts: int = C.TRUNCATION_CUTS) -> tuple:
    """The kernel's stage 1 on DEV (as the sandbox runs it). Returns (s1, summary)."""
    seed = secrets.randbits(63) if seed is None else int(seed)
    s1 = UP.stage1_u(prog, params, ud, np.random.default_rng(seed), PL.Opts(truncation_cuts=cuts))
    summ = {k: s1.get(k) for k in ("ok", "code", "fault", "cuts", "start_cuts", "direction_changes_dev",
                                   "block_overlap_cells")}
    return s1, summ


def _spot_coverage(fp, inplay: np.ndarray, s: int, e: int):
    """Share of in-play (symbol, DEV decision row) cells whose spot slot `volume` is known (finite)."""
    num = den = 0
    for bp in fp.blocks:
        if "volume" not in bp.fields:
            return None
        lo, hi = max(bp.b, s - 1), min(bp.e - 1, e - 1)
        if lo > hi:
            continue
        cols = np.array([fp.col[x] for x in bp.symbols], dtype=np.int64)
        v = bp.fields["volume"][lo - bp.s:hi - bp.s + 1]
        ip = inplay[lo:hi + 1][:, cols]
        num += int((np.isfinite(v) & ip).sum())
        den += int(ip.sum())
    return _f(num / den) if den else None


def measure(prog, params: dict, ud, s1: dict, g6_lags: bool = True, coverage: bool = False) -> dict:
    """Every DEV reading of the sandbox for a top30 program, by the kernel's own functions, from stage 1's W."""
    W, kn = s1["W"], s1["known"]
    fp = UP.Blocked(ud, "top30", fields=UP.program_fields(prog))
    inplay = fp.inplay()
    s, e = fp.pos(C.DEV_START), fp.pos(C.DEV_END)
    run = fp.run(W, s, e)
    daily = run.daily_returns()
    sm = S.summary(daily)
    k = inplay.sum(axis=1, keepdims=True)
    Wb = np.where(inplay, 1.0 / np.where(k > 0, k, 1), 0.0)
    bench = fp.run(Wb, s, e).daily_returns()
    sl = UP.dev_speed_limit(fp, W, kn, inplay)
    nm = UP.dev_names_held(W, inplay, s, e)
    g2 = PL.dev_sharpe_of(fp.run(W, s, e, pay=C.FUNDING_STRESS_PAY, recv=C.FUNDING_STRESS_RECV))
    g4 = PL.dev_sharpe_of(fp.run(W, s, e, cost_mult=C.COST_STRESS_MULT))
    pr = UP.dev_paired_lags(fp, W, kn, inplay) if g6_lags else None
    cov =_spot_coverage(fp, inplay, s, e) if coverage else None
    n_unit = len(fp.symbols)
    del fp
    n30 = UP.next30_score(prog, params, ud, end=C.DEV_END, keep=True)
    years = [{"year": r["year"], "n_days": r["n_days"], "return": _f(r["return"]), "sharpe": _f(r["sharpe"]),
              "max_drawdown": _f(r["max_drawdown"])} for r in S.per_year(daily)]
    out = {
        "dev_sharpe": _f(sm["sharpe"]), "psr0": _f(sm["psr0"]), "total_return": _f(sm["total_return"]),
        "cagr": _f(sm["cagr"]), "max_drawdown": _f(sm["max_drawdown"]), "n_days": sm["n_days"],
        "rebalances": run.n_rebalances, "avg_gross": _f(run.gross.mean()), "avg_net": _f(run.net.mean()),
        "costs": _f(run.ev_cost.sum()), "liquidated": bool(run.liquidated),
        "funding_net": _f(run.funding_paid), "funding_paid_gross": _f(run.funding_paid_gross),
        "funding_received_gross": _f(run.funding_received_gross),
        "g2_dev_sharpe": _f(g2), "g4_dev_sharpe": _f(g4),
        "names_held_avg": _f(nm["held"]), "names_inplay_avg": _f(nm["inplay"]),
        "g6_memory_dev": [_f(x) for x in sl["r"]] if sl.get("ok") else None,
        "g6_memory_dev_max": _f(sl.get("max")) if sl.get("ok") else None,
        "g6_memory_dev_from": str(sl["start"]) if sl.get("ok") else None,
        "g6_memory_reason": None if sl.get("ok") else sl.get("reason"),
        "next30_dev_sharpe": _f(n30.get("sharpe")), "next30_code": n30.get("code"),
        "next30_symbols": n30.get("symbols"),
        "per_year": years, "bench_dev_sharpe": _f(S.sharpe(bench)), "bench_max_drawdown": _f(S.max_drawdown(bench)),
        "unit_symbols": n_unit, "direction_changes_dev": s1.get("direction_changes_dev"),
        "spot_known_share_inplay": cov,
    }
    if pr is not None:
        out["g6_paired_dev"] = ({"lags": pr["lags"], "at_least_as_good": pr["at_least_as_good"], "p": _f(pr["p"]),
                                 "book_median": _f(pr["book_median"]), "stale_median": _f(pr["stale_median"]),
                                 "start": str(pr["start"]), "end": str(pr["end"])}
                                if pr.get("ok") else {"lags": pr["lags"], "reason": pr.get("reason")})
    return out


# ---------------------------------------------------------------- the screen (PLAN version 2)
def pre_cost(r: dict):
    d, g4 = r.get("dev_sharpe"), r.get("g4_dev_sharpe")
    if not isinstance(d, float) or not isinstance(g4, float):
        return None
    return d + (d - g4)


def screen(r: dict, stage1_summary: dict) -> dict:
    """W1..W8 at the study's thresholds (one screen for all; H-S3 and its own W1 are struck, rulings 3 and 4); every
    item with its value and pass; `pass` = all eight."""
    it = {}
    st_ok = bool(stage1_summary.get("ok")) and stage1_summary.get("code") is None
    dc = stage1_summary.get("direction_changes_dev") or 0
    w1 = (st_ok and dc >= W1_DIRECTION_CHANGES and (r.get("avg_gross") or 0) >= W1_AVG_GROSS
          and (r.get("names_held_avg") or 0) >= W1_NAMES and not r.get("liquidated"))
    it["W1"] = {"pass": bool(w1), "stage1_ok": st_ok, "direction_changes": dc, "avg_gross": r.get("avg_gross"),
                "names_held": r.get("names_held_avg"), "liquidated": r.get("liquidated")}
    pc = pre_cost(r)
    it["W2"] = {"pass": pc is not None and pc >= W2_PRE_COST, "pre_cost": pc, "floor": W2_PRE_COST}
    g4, g2 = r.get("g4_dev_sharpe"), r.get("g2_dev_sharpe")
    it["W3"] = {"pass": isinstance(g4, float) and g4 > 0, "g4_dev_sharpe": g4}
    it["W4"] = {"pass": isinstance(g2, float) and g2 > 0, "g2_dev_sharpe": g2}
    n30 = r.get("next30_dev_sharpe")
    it["W5"] = {"pass": r.get("next30_code") is None and isinstance(n30, float) and n30 >= W5_NEXT30,
                "next30_dev_sharpe": n30, "code": r.get("next30_code")}
    m = r.get("g6_memory_dev")
    it["W6"] = {"pass": m is not None and all(isinstance(x, float) and x <= W6_SPEED for x in m), "r": m}
    pr = r.get("g6_paired_dev") or {}
    ok7 = "at_least_as_good" in pr and pr["at_least_as_good"] <= W7_STALE_MAX and isinstance(pr.get("book_median"), float) \
        and pr["book_median"] > 0
    it["W7"] = {"pass": bool(ok7), "at_least_as_good": pr.get("at_least_as_good"), "book_median": pr.get("book_median"),
                "reason": pr.get("reason")}
    ys = {y["year"]: y for y in r.get("per_year") or []}
    npos = sum(1 for y in (2020, 2021, 2022) if y in ys and isinstance(ys[y]["return"], float) and ys[y]["return"] > 0)
    it["W8"] = {"pass": npos >= W8_YEARS, "years_positive": npos}
    first = next((k for k in ("W1", "W2", "W3", "W4", "W5", "W6", "W7", "W8") if not it[k]["pass"]), None)
    return {"items": it, "pass": first is None, "first_failed": first}


def corner_ok(r: dict) -> bool:
    d, g4 = r.get("dev_sharpe"), r.get("g4_dev_sharpe")
    return isinstance(d, float) and d > 0 and isinstance(g4, float) and g4 > 0


def control_ok(r_hyp: dict, r_ctl: dict) -> dict:
    a, b = pre_cost(r_hyp), pre_cost(r_ctl)
    ok = a is not None and b is not None and a - b >= CONTROL_MARGIN
    return {"pass": bool(ok), "pre_cost_hypothesis": a, "pre_cost_control": b,
            "margin": (a - b) if (a is not None and b is not None) else None, "required": CONTROL_MARGIN}


# ---------------------------------------------------------------- the study's truncation test (guard D2)
def truncation_cuts(grid: pd.DatetimeIndex, rng) -> list:
    """Row positions of the fixed cuts and RANDOM_CUTS random hours between DEV start and DEV end - 1."""
    pos = []
    for c in FIXED_CUTS:
        t = T(c)
        if t in grid:
            pos.append(int(grid.get_loc(t)))
    a, b = int(grid.get_loc(T(C.DEV_START))), int(grid.get_loc(T(C.DEV_END))) - 1
    pos += [int(x) for x in rng.choice(np.arange(a, b), size=RANDOM_CUTS, replace=False)]
    return sorted(set(pos))


def truncation_test(prog, params: dict, ud_kernel, spot, s1: dict, cut_rows: list, shift_hours: int = 0) -> dict:
    """For each cut T: rebuild the study's input with EVERY perpetual and spot row after T dropped (the slots are
    re-derived from the truncated rows), evaluate the program by the kernel's block path up to T, and require the
    weights, raw signal and known channel of every row up to T to equal the full run's bit for bit. shift_hours:
    only the synthetic negative test uses it (a deliberate look-ahead that this test must catch)."""
    grid = s1["grid"]
    W, raw, kn = s1["W"], s1["raw"], s1["known"]
    res = []
    for c in cut_rows:
        cut = grid[c]
        udt = F.study_udata(ud_kernel, spot, cut=cut, shift_hours=shift_hours)
        fpt = UP.Blocked(udt, "top30", fields=UP.program_fields(prog))
        if list(fpt.symbols) != list(s1["symbols"]):
            res.append({"cut": str(cut), "equal": False, "why": "panel symbols differ"})
            continue
        wt, rt, kt = fpt.unit(prog, params, upto=cut)
        eq = (wt.shape == W[:c + 1].shape and bool(np.array_equal(wt, W[:c + 1]))
              and PL.same_rows(rt, raw[:c + 1]) and bool(np.array_equal(kt, kn[:c + 1])))
        res.append({"cut": str(cut), "equal": bool(eq), "known_rows_compared": int(kn[:c + 1].any(axis=1).sum())})
        del fpt, udt
    return {"pass": bool(res) and all(x["equal"] for x in res), "cuts": res}


def now_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
