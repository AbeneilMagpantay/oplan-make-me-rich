"""Universe calibration (unit top30, KP-015):

    python -m omr.ucalibrate [--worlds 100] [--oracle-worlds 100] [--workers 4]
    python -m omr.ucalibrate --unlocked-dry-run --out FILE      (fully synthetic panel; never sealable)

The core calibration (omr.calibrate) is unchanged. The seal (omr.kernel_lock seal) applies decide_both:
the LARGEST G6 threshold whose null pass rate is <= NULL_PASS_MAX under BOTH nulls IN BOTH UNITS, with
oracle power at true Sharpe 1.5 >= POWER_MIN for both speeds, both nulls, both units.

PANEL: the 30 crypto perpetuals with the most active hours between DEV start and VAL end (ties by name),
read with a logged calibration handle. POOL: the UTC days from the first day on which all 30 have complete
history to VAL end. Membership in the null worlds is CONSTANT: all 30 symbols are top30 members in every
month whose 97-day read window lies inside the world (so the unit is unknown for the first months, as in
real data, and start cuts behave as in real data).
NULL A (bootstrap): every world day draws one pool day iid, the SAME source day for all 30 symbols, so the
  cross-sectional correlation of that day survives; each day keeps its intraday bars and funding.
NULL B (sign-flip): the pool in real order, aligned so the world's last day is the pool's last day (days
  before the pool start are drawn iid from the pool); per day ONE fair coin shared by all 30 symbols
  mirrors every symbol's demeaned hourly log-return path; funding unchanged.
Mark and index bars of the null worlds are the synthetic last-price bars (no universe family reads them;
the liquidation check then uses last-price wicks, which are wider than mark wicks: conservative).
Inactive hours of a source day stay inactive (trades 0) in the world.

Families: three hash-locked cross-sectional programs (omr/programs/ucal_*.omr): momentum, short-term
reversal, funding carry. Protocol per (world, family): 20 parameter draws, SCREENED by the DEV signals and
the activity rule; the activity passer with the best DEV Sharpe gets the full stage 1 and is SUBMITTED to
stage 2 (G8 not run: it can only veto, so null pass rates are upper bounds).
NOISY ORACLE (cross-sectional): per symbol x = rho * z + sqrt(1 - rho^2) * eps, z = the symbol's future
k-day log return minus the panel mean, standardised per symbol; weights = (x - mean x) / sum |x - mean x|
over the in-play symbols, re-decided every k days (decided at the 23:00 bar, executed at the next 00:00
open). Speeds k = 1 and 20 days; rho tuned on the power worlds until the achieved mean VAL Sharpe is
within RHO_TOL of the level (1.0 and 1.5).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import multiprocessing as mp
import time
from pathlib import Path

import numpy as np
import pandas as pd

from omr import access
from omr import calibrate as CB
from omr import constants as C
from omr import data
from omr import datasets as D
from omr import kernel_lock
from omr import lang as L
from omr import ledger
from omr import paths as P
from omr import pipeline as PL
from omr import stats as S
from omr import universe as U
from omr import upipeline as UP

PROTOCOL_VERSION = 1
FAMILIES = ("ucal_xs_momentum", "ucal_xs_reversal", "ucal_xs_carry")
N_PANEL = C.UNIVERSE_TOP
SEEDS = {"A": 11000, "B": 14000, "oracle_A": 17000, "oracle_B": 18000}
OPTS = PL.Opts(include_g8=False, keep_detail=False)
HOUR_NS = U.HOUR_NS
DAY_NS = U.DAY_NS
OTHER = ["volume", "quote_volume", "trades", "taker_buy_volume", "taker_buy_quote_volume"]


def T(s) -> pd.Timestamp:
    return pd.Timestamp(s, tz="UTC").as_unit("ns")


def family_path(name: str) -> Path:
    if name not in FAMILIES:
        raise ValueError(f"unknown universe calibration family {name!r}: only {FAMILIES}")
    return P.PROGRAMS_DIR / f"{name}.omr"


# ---------------------------------------------------------------- source

def choose_panel(acts: dict) -> list:
    """The N_PANEL symbols with the most active hours in DEV+VAL (ties by name)."""
    lo, hi = T(C.DEV_START).value, T(C.VAL_END).value
    n = {}
    for s, a in acts.items():
        i0, i1 = U.rows_in(a, lo, hi)
        n[s] = int(a.active[i0:i1].sum())
    return sorted(sorted(n), key=lambda s: -n[s])[:N_PANEL]


class USource:
    """Whole UTC pool days of the panel symbols as open-relative ratios (as omr.calibrate.Source)."""

    def __init__(self, tables: dict):
        self.symbols = sorted(tables)
        end_day = T(C.VAL_END).normalize()
        first = max((tables[s]["klines"].index[0] + pd.Timedelta(hours=23)).normalize() + pd.Timedelta(days=1)
                    for s in self.symbols)
        self.pool_start = first
        days = pd.date_range(first, end_day, freq="D").as_unit("ns")
        self.nd = len(days)
        if self.nd < 60:
            raise RuntimeError("the calibration pool is shorter than 60 days")
        self.days = days
        self.sym = {}
        a, b = first, T(C.VAL_END)
        for s in self.symbols:
            kl = tables[s]["klines"]
            seg = kl.loc[a:b]
            if len(seg) != self.nd * 24:
                raise RuntimeError(f"{s}: the pool is not covered by whole days")
            o, h, lo, c = (seg[k].to_numpy(dtype=np.float64) for k in ("open", "high", "low", "close"))
            pc = np.r_[kl.loc[:a - pd.Timedelta(hours=1), "close"].iloc[-1], c[:-1]]
            gap = seg["is_gap"].to_numpy(dtype=bool) | ~(seg["trades"].to_numpy(dtype=np.float64) > 0)
            with np.errstate(divide="ignore", invalid="ignore"):
                lr = np.log(c / pc)
            fu = tables[s]["funding"].loc[a:b]
            ft = data.ns_int(fu.index)
            fday = ((ft - a.value) // DAY_NS).astype(np.int64)
            order = np.argsort(fday, kind="mergesort")
            fday = fday[order]
            self.sym[s] = {"g": (o / pc).reshape(-1, 24), "hr": (h / o).reshape(-1, 24), "lr": (lo / o).reshape(-1, 24),
                           "cr": (c / o).reshape(-1, 24), "other": seg[OTHER].to_numpy(dtype=np.float64).reshape(-1, 24, 5),
                           "gap": gap.reshape(-1, 24), "m": float(np.mean(lr[np.isfinite(lr) & ~gap])) if (~gap).any() else 0.0,
                           "p0": float(pc[0]), "fhour": ((ft[order] % DAY_NS) // HOUR_NS).astype(np.int64),
                           "frate": fu["rate"].to_numpy()[order], "fint": fu["interval_hours"].to_numpy()[order],
                           "offs": np.searchsorted(fday, np.arange(self.nd + 1))}


def _synth_tables(v: dict, src: np.ndarray, flip: np.ndarray, start: pd.Timestamp) -> dict:
    nd = len(src)
    g, hr, lr, cr = (v[k][src].copy() for k in ("g", "hr", "lr", "cr"))
    F = flip[:, None]
    g = np.where(F, np.exp(2 * v["m"]) / g, g)
    hr, lr = np.where(F, 1.0 / lr, hr), np.where(F, 1.0 / hr, lr)
    cr = np.where(F, 1.0 / cr, cr)
    g, hr, lr, cr = (x.reshape(-1) for x in (g, hr, lr, cr))
    step = g * cr
    prev_c = v["p0"] * np.r_[1.0, np.cumprod(step)[:-1]]
    o = prev_c * g
    idx = pd.date_range(start, periods=nd * 24, freq="h").as_unit("ns")
    idx.name = "open_time"
    kl = pd.DataFrame({"open": o, "high": o * hr, "low": o * lr, "close": o * cr}, index=idx)
    oth = v["other"][src].reshape(nd * 24, 5)
    gap = v["gap"][src].reshape(-1)
    for j, c in enumerate(OTHER):
        kl[c] = np.where(gap, 0.0, oth[:, j])
    kl["is_gap"] = gap
    mark = kl[["open", "high", "low", "close"]].copy()
    mark["samples"] = 3600.0
    mark = mark[~gap]
    sel = np.concatenate([np.arange(v["offs"][p], v["offs"][p + 1]) for p in src])
    day_of = np.concatenate([np.full(v["offs"][p + 1] - v["offs"][p], i) for i, p in enumerate(src)])
    ft = start.value + day_of * DAY_NS + v["fhour"][sel] * HOUR_NS
    fu = pd.DataFrame({"rate": v["frate"][sel], "interval_hours": v["fint"][sel], "offset_ms": 0.0},
                      index=pd.DatetimeIndex(pd.to_datetime(ft, unit="ns", utc=True)).as_unit("ns"))
    fu.index.name = "settle_time"
    return {"klines": kl, "funding": fu, "mark_klines": mark, "index_klines": mark}


class ConstUData(UP.UData):
    """Null-world universe data: every panel symbol is a top30 member in every month whose 97-day read
    window lies inside the supplied rows (constant membership)."""

    def membership(self, lo_ns: int, hi_ns: int) -> U.Membership:
        months = U.month_starts(lo_ns, hi_ns)
        known = np.array([m - U.SEASON_BLOCKS * DAY_NS >= lo_ns for m in months], dtype=bool)
        syms = sorted(self.raw)
        return U.Membership(months=months, known=known, ranked=[syms if k else [] for k in known],
                            scores=[{} for _ in known])


def build_uworld(src: USource, null: str, seed: int, end: str = C.VAL_END) -> ConstUData:
    rng = np.random.default_rng([seed, 21 if null == "A" else 22])
    start = T(C.UNIVERSE_START)
    cal = pd.date_range(start, T(C.VAL_END).normalize(), freq="D")
    n = len(cal)
    if null == "A":
        pick = rng.integers(0, src.nd, n)
        flips = np.zeros(n, dtype=bool)
    elif null == "B":
        k = min(n, src.nd)
        pick = np.r_[rng.integers(0, src.nd, n - k), np.arange(src.nd - k, src.nd)]
        flips = rng.uniform(size=n) < 0.5
    else:
        raise ValueError(null)
    tables = {s: _synth_tables(src.sym[s], pick, flips, start) for s in src.symbols}
    b = src.symbols[0]
    btc = D.assemble_frame(tables[b], D.PROGRAM_EXTRA)
    ud = UP.udata_from_tables(tables, btc, end)
    return ConstUData(acts=ud.acts, raw=ud.raw, btc=ud.btc, end=ud.end, until={})


def dev_view(ud: ConstUData) -> ConstUData:
    cap = T(C.DEV_END)
    raw = {s: {d: (t[t.index <= cap] if d != "funding" else t[t.index.floor("h") <= cap]) for d, t in r.items()}
           for s, r in ud.raw.items()}
    acts = {s: U.activity_of(raw[s]["klines"]) for s in raw}
    return ConstUData(acts=acts, raw=raw, btc=ud.btc[ud.btc.index <= cap], end=cap, until={})


# ---------------------------------------------------------------- oracle

class UOracle:
    def __init__(self, ud: ConstUData, k_days: int, eps_seed):
        self.bu = UP.Blocked(ud, "top30", months=None)              # one block (30 symbols)
        self.inplay = self.bu.inplay()
        self.dev_s, self.val_e = self.bu.pos(C.DEV_START), self.bu.pos(C.VAL_END)
        step = 24 * k_days
        self.starts = np.arange(self.dev_s, self.val_e, step)
        self.ends = np.minimum(self.starts + step, self.val_e)
        op = self.bu.eng_rows("open", 0, len(self.bu.ns) - 1)
        self.shape = op.shape
        with np.errstate(divide="ignore", invalid="ignore"):
            R = np.log(op[self.ends] / op[self.starts])
        R = np.where(np.isfinite(R), R, 0.0)
        R = R - R.mean(axis=1, keepdims=True)
        sd = R.std(axis=0, ddof=1)
        self.z = np.where(sd > 0, (R - R.mean(axis=0)) / np.where(sd > 0, sd, 1.0), 0.0)
        self.eps = np.random.default_rng(eps_seed).standard_normal(self.z.shape)
        self.rows = np.arange(self.starts[0] - 1, self.ends[-1] - 1)
        self.block = np.repeat(np.arange(len(self.starts)), self.ends - self.starts)

    def weights(self, rho: float) -> np.ndarray:
        x = rho * self.z + math.sqrt(max(0.0, 1.0 - rho * rho)) * self.eps
        W = np.zeros(self.shape)
        xb = x[self.block]
        P_ = self.inplay[self.rows]
        k = P_.sum(axis=1, keepdims=True)
        m = np.where(P_, xb, 0.0).sum(axis=1, keepdims=True) / np.where(k > 0, k, 1)
        d = np.where(P_, xb - m, 0.0)
        s = np.abs(d).sum(axis=1, keepdims=True)
        W[self.rows] = np.where(s > 0, d / np.where(s > 0, s, 1.0), 0.0)
        return W

    def val_sharpe(self, rho: float) -> float:
        return PL.val_sharpe_of(self.bu.run(self.weights(rho), self.dev_s, self.val_e))


# ---------------------------------------------------------------- workers

_W = {}


def synthetic_panel_tables(seed: int = 9, n: int = N_PANEL) -> dict:
    """Fully synthetic panel tables for the dry run (no real bar is read)."""
    from omr import probe
    rng = np.random.default_rng(seed)
    hours = int((T(C.VAL_END) - T("2019-11-01 00:00")) / pd.Timedelta(hours=1)) + 1
    return {f"S{i:02d}USDT": probe.synthetic_symbol(rng, float(np.exp(rng.normal(2.0, 1.5))), start="2019-11-01 00:00",
                                                    hours=hours) for i in range(n)}


def _init(families, handle, synthetic=False, tables=None):
    _W["handle"] = handle
    if tables is None:
        tables = synthetic_panel_tables() if synthetic else load_panel_tables(handle)[0]
    _W["src"] = USource(tables)
    _W["progs"] = {f: L.parse_file(family_path(f)) for f in families}


def load_panel_tables(handle) -> tuple:
    table = U.load_symbols()
    acts = {}
    for s in U.crypto_symbols(table):
        try:
            kl = D.load_raw("klines", s, upto="val_end", handle=handle)
        except FileNotFoundError:
            continue
        acts[s] = U.activity_of(kl, table["symbols"][s].get("until"))
    panel = choose_panel(acts)
    tables = {s: {d: D.load_raw(d, s, upto="val_end", handle=handle) for d in ("klines", "funding")} for s in panel}
    return tables, panel


def dev_sharpe_u(fp_dev, W) -> float:
    run = fp_dev.run(W, fp_dev.pos(C.DEV_START), fp_dev.pos(C.DEV_END))
    return float("-inf") if run.liquidated else S.sharpe(run.daily_returns())


def task_null(args) -> list:
    null, world_seed = args
    ud = build_uworld(_W["src"], null, world_seed)
    udd = dev_view(ud)
    fp_dev = UP.Blocked(udd, "top30", months=None)
    out = []
    for fam, prog in _W["progs"].items():
        rng = np.random.default_rng(CB._seed("udraws", null, fam, world_seed))
        best, best_sh, codes = None, float("-inf"), {}
        for _ in range(CB.N_DRAWS):
            q = CB.draw_params(prog, rng)
            sc = UP.screen_dev_u(prog, q, fp_dev)
            if not sc["ok"]:
                codes[sc["code"]] = codes.get(sc["code"], 0) + 1
                continue
            codes["passed"] = codes.get("passed", 0) + 1
            sh = dev_sharpe_u(fp_dev, sc["W"])
            if best is None or sh > best_sh:
                best, best_sh = q, sh
        base = {"null": null, "family": fam, "world_seed": world_seed, "stage1": codes}
        if best is None:
            out.append(dict(base, submitted=False, status="not_submitted"))
            continue
        s1 = UP.stage1_u(prog, best, udd, np.random.default_rng(CB._seed("us1", null, fam, world_seed)), OPTS,
                         months=None)
        if not s1["ok"]:
            out.append(dict(base, submitted=False, status=f"stage1_{s1['code']}", params=best, fault=s1.get("fault")))
            continue
        res = UP.stage2_u(prog, best, ud, s1, OPTS, _W["handle"], CB._seed("unull", null, fam, world_seed), None,
                          months=None)
        out.append(CB.summarise(res, dict(base, submitted=True, params=best, best_dev_sharpe_of_passers=best_sh)))
    return out


def task_oracle_curve(args) -> list:
    null, world_seed, speed, rhos = args
    ob = UOracle(build_uworld(_W["src"], null, world_seed), CB.SPEEDS[speed], CB._seed("ueps", null, world_seed, speed))
    return [ob.val_sharpe(float(r)) for r in rhos]


def task_oracle_power(args) -> list:
    null, world_seed, rhos = args
    ud = build_uworld(_W["src"], null, world_seed)
    out = []
    for speed in CB.SPEEDS:
        ob = UOracle(ud, CB.SPEEDS[speed], CB._seed("ueps", null, world_seed, speed))
        for lvl in CB.LEVELS:
            rho = rhos[f"{speed}|{lvl}"]
            res = UP.evaluate_weights_u(ob.weights(rho), ob.bu, CB._seed("uoracle", null, world_seed, speed, lvl), OPTS,
                                        _W["handle"], None)
            out.append(CB.summarise(res, {"null": null, "speed": speed, "level": lvl, "rho": rho,
                                          "world_seed": world_seed}))
    return out


def tune_rho(pool, null: str, speed: str, seeds: list, log) -> dict:
    """As omr.calibrate.tune_rho, with the universe oracle."""
    def means(rhos):
        res = pool.map(task_oracle_curve, [(null, s, speed, [float(r) for r in rhos]) for s in seeds])
        mat = np.array(res, dtype=np.float64)
        return np.nanmean(np.where(np.isfinite(mat), mat, np.nan), axis=0)

    mean = means(CB.RHO_GRID)
    out = {"mean_curve": {f"{r:.4f}": float(m) for r, m in zip(CB.RHO_GRID, mean)}}
    fine = {}
    for lvl in CB.LEVELS:
        idx = np.nonzero(mean >= lvl)[0]
        if len(idx) == 0:
            lo, hi = float(CB.RHO_GRID[-2]), float(CB.RHO_GRID[-1])
        elif idx[0] == 0:
            lo, hi = float(CB.RHO_GRID[0]), float(CB.RHO_GRID[1])
        else:
            lo, hi = float(CB.RHO_GRID[idx[0] - 1]), float(CB.RHO_GRID[idx[0]])
        fine[lvl] = np.linspace(lo, hi, 41)
    fm = means(np.concatenate([fine[lv] for lv in CB.LEVELS]))
    picks = {lvl: float(fine[lvl][int(np.nanargmin(np.abs(fm[i * 41:(i + 1) * 41] - lvl)))])
             for i, lvl in enumerate(CB.LEVELS)}
    ach = means([picks[lv] for lv in CB.LEVELS])
    for i, lvl in enumerate(CB.LEVELS):
        out[str(lvl)] = {"rho": picks[lvl], "achieved_mean_val_sharpe": float(ach[i]),
                         "within_bound": bool(abs(float(ach[i]) - lvl) <= CB.RHO_BOUND)}
        log(f"    null {null} {speed:4s} level {lvl}: rho {picks[lvl]:.5f} -> achieved {float(ach[i]):.3f}")
    return out


# ---------------------------------------------------------------- the rule over both units

def verdict_from_rows(art: dict) -> dict:
    return CB.verdict_from_rows(art)


def decide_both(core_art: dict, uni_art: dict) -> dict:
    """The seal rule over both units (applied by omr.kernel_lock seal to the stored rows)."""
    vc, vu = CB.verdict_from_rows(core_art), CB.verdict_from_rows(uni_art)
    rates = {"core": vc["null_pass_rate"], "top30": vu["null_pass_rate"]}
    qualifying = [t for t in C.G6_GRID
                  if all(rates[u][n][str(t)] is not None and rates[u][n][str(t)] <= C.NULL_PASS_MAX + 1e-12
                         for u in rates for n in ("A", "B"))]
    chosen = max(qualifying) if qualifying else None
    out = {"rule": "G6 threshold = the LARGEST of G6_GRID whose null pass rate (Tier-1 passes / SUBMITTED pairs) "
                   "is <= NULL_PASS_MAX under BOTH nulls IN BOTH UNITS (core, top30); then oracle power at true "
                   "Sharpe 1.5 >= POWER_MIN for BOTH speeds under BOTH nulls in BOTH units, every oracle level "
                   "achieved within RHO_BOUND; otherwise STOP",
           "null_pass_rate": rates, "qualifying": qualifying, "chosen_threshold": chosen}
    if chosen is None:
        out.update(STOP=True, reason="no G6 threshold keeps the null pass rate <= NULL_PASS_MAX in both units")
        return out
    power, below, off = {}, [], []
    for unit, art in (("core", core_art), ("top30", uni_art)):
        orc = {n: {"summary": CB.oracle_summary(art["oracle"][n]["rows"])} for n in ("A", "B")}
        power[unit] = {n: {s: orc[n]["summary"][f"{s}|1.5"]["by_threshold"][str(chosen)]["power"] for s in CB.SPEEDS}
                       for n in ("A", "B")}
        below += [f"{unit}/{n}/{s}" for n in power[unit] for s in power[unit][n]
                  if power[unit][n][s] is None or power[unit][n][s] < C.POWER_MIN]
        for n in ("A", "B"):
            for k, v in orc[n]["summary"].items():
                if v["mean_val_sharpe"] is None or abs(v["mean_val_sharpe"] - float(k.split("|")[1])) > CB.RHO_BOUND:
                    off.append(f"{unit}/{n}/{k}")
    out.update(power_at_1_5_chosen=power, below_power_min=below, oracle_level_outside_bound=off,
               STOP=bool(below) or bool(off))
    if off:
        out["reason"] = "oracle achieved mean VAL Sharpe outside the bound: " + ", ".join(off)
    elif below:
        out["reason"] = "oracle power at true Sharpe 1.5 below POWER_MIN: " + ", ".join(below)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m omr.ucalibrate")
    ap.add_argument("--worlds", type=int, default=100)
    ap.add_argument("--oracle-worlds", type=int, default=100)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--unlocked-dry-run", action="store_true")
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    t0 = time.time()

    def log(s):
        print(s, flush=True)

    problems = kernel_lock.verify()
    lock_ok = not problems
    if not lock_ok and not a.unlocked_dry_run:
        log("KERNEL LOCK DOES NOT VERIFY - the calibration runs only on the locked kernel")
        raise SystemExit(3)
    if a.unlocked_dry_run and not a.out:
        raise SystemExit("--unlocked-dry-run needs --out <path>")
    k = kernel_lock.read_lock() if lock_ok else kernel_lock.compute()
    synthetic = bool(a.unlocked_dry_run)
    if synthetic:
        rh, panel = "synthetic-dry-run", sorted(synthetic_panel_tables())
        handle = access.for_calibration(f"universe calibration DRY RUN, semantic {k['semantic'][:16]}: synthetic panel")
    else:
        if not data.validation_ok():
            raise SystemExit("data not validated: run python -m omr.data validate")
        rh = data.load_manifest()["research_hash"]
        handle = access.for_calibration(f"universe calibration v{PROTOCOL_VERSION}, semantic {k['semantic'][:16]}: "
                                        "null worlds built from DEV+VAL bars of a 30-symbol panel")
        panel = load_panel_tables(handle)[1]
    fams = list(FAMILIES)
    nulls, oracle = {}, {}
    with mp.get_context("spawn").Pool(a.workers, initializer=_init, initargs=(fams, handle, synthetic)) as pool:
        for null in ("A", "B"):
            rows = []
            for i, rr in enumerate(pool.imap_unordered(task_null, [(null, SEEDS[null] + i) for i in range(a.worlds)])):
                rows.extend(rr)
                if (i + 1) % 10 == 0:
                    log(f"  null {null}: {i + 1}/{a.worlds} worlds ({time.time() - t0:.0f} s)")
            rows.sort(key=lambda r: (r["world_seed"], r["family"]))
            nulls[null] = {"rows": rows, "summary": CB.null_summary(rows, fams)}
        for null in ("A", "B"):
            seeds = [SEEDS[f"oracle_{null}"] + i for i in range(a.oracle_worlds)]
            rhos, tuning = {}, {}
            for speed in CB.SPEEDS:
                tuning[speed] = tune_rho(pool, null, speed, seeds, log)
                for lvl in CB.LEVELS:
                    rhos[f"{speed}|{lvl}"] = tuning[speed][str(lvl)]["rho"]
            rows = []
            for rr in pool.imap_unordered(task_oracle_power, [(null, s, rhos) for s in seeds]):
                rows.extend(rr)
            rows.sort(key=lambda r: (r["world_seed"], r["speed"], r["level"]))
            oracle[null] = {"rhos": rhos, "tuning": tuning, "rows": rows, "summary": CB.oracle_summary(rows)}
    verdict = CB.decide(nulls, oracle)
    out = {"protocol_version": PROTOCOL_VERSION, "unit": "top30", "kernel_hash": k["combined"],
           "semantic_hash": k["semantic"], "text_hash": k["text"], "kernel_lock_verified": lock_ok and not synthetic,
           "synthetic_dry_run": synthetic, "research_hash": rh, "panel": panel,
           "created_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "families": {f: ledger.sha256_file(family_path(f)) for f in fams},
           "protocol": {"worlds_per_null": a.worlds, "draws_per_pair": CB.N_DRAWS, "oracle_worlds": a.oracle_worlds,
                        "speeds_days": CB.SPEEDS, "levels": list(CB.LEVELS), "seeds": SEEDS,
                        "membership": "constant (all 30 panel symbols)", "reduced_pipeline": "G8 not run"},
           "nulls": nulls, "oracle": oracle, "verdict_unit_only": verdict, "wall_seconds": round(time.time() - t0, 1)}
    path = Path(a.out) if a.out else P.LEDGER_DIR / f"ucalibration_{k['semantic'][:16]}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(ledger.clean(out), indent=1, sort_keys=True), encoding="ascii")
    log(f"saved {path}")
    if not a.out:
        kernel_lock.log_calibration(path, k["semantic"], rh)
    log(f"wall time {out['wall_seconds']} s")


if __name__ == "__main__":
    main()
