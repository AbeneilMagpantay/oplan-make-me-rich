"""Instrument calibration (protocol v6, formula language):

    python -m omr.calibrate [--worlds 300] [--oracle-worlds 200] [--workers 6]

Runs ONLY on a verified kernel lock (the artifact records kernel_lock_verified true and the locked
kernel hash); `--unlocked-dry-run --out <file>` is for construction checks and can never be sealed.
The G6 threshold is not a constant: `python -m omr.kernel_lock seal --calibration <artifact>`
re-applies `decide` (below) to the stored per-pair rows and writes the result into kernel.lock.

Families: the five generation-0 baseline programs shipped inside the kernel (omr/programs/*.omr,
hash-locked); --families accepts a subset of these names and nothing else. Every program run here
goes through the real pipeline functions in-process (pipeline.stage1, pipeline.stage2); nothing is
written to the trial ledger.

Synthetic worlds are built from the real core data (BTCUSDT, ETHUSDT) over the real 1h calendar,
carrying klines, mark-price klines and funding together (read with a logged calibration handle).
NULL A (bootstrap): whole UTC days drawn iid with replacement from DEV+VAL, the same source day for
  both core symbols; each day keeps its intraday bars, mark bars and funding settlements. Keeps
  drift, intraday shape and within-day volatility; destroys multi-day predictability.
NULL B (sign-flip): the real day order; per UTC day one fair coin (shared by both core symbols)
  mirrors that day's DEMEANED hourly log-return path (r' = -(r - m) + m); high/low excursions swap;
  mark bars likewise with their own m; funding unchanged. Keeps the real volatility dynamics;
  destroys directional predictability across days.

DEV-overfit protocol (false-positive rate): for each (world, family) draw 20 parameter sets
  uniformly from the declared ranges; SCREEN them with the DEV signals and the activity rule only
  (activity_dev on the world's DEV-only frames); the activity passer with the best DEV Sharpe gets the
  full stage 1 (truncation and start-cut self-checks) and is SUBMITTED to stage 2; if no draw passes
  the screen, nothing is submitted for that pair. Fix pass 10 (R-Q): a draw liquidated on DEV (stage1
  count dev_liquidated) or with a DEV Sharpe that is otherwise not finite (dev_sharpe_not_finite) is never a
  candidate, so it is never submitted; a pair without a candidate is not submitted. Null pass rate =
  Tier-1 passes / EVALUATED pairs (fix pass 11, R-R; the rate over submitted pairs is kept as information).
  Every gate value and the G6 p-value of every submitted pair are stored.
Dry run (--unlocked-dry-run --out FILE): the same protocol on FULLY SYNTHETIC core prices (omr.probe
  generator); no real bar after DEV end is read; the artifact can never be sealed.
Every artifact written into ledger/ gets a hash-chained row in ledger/calibration_log.jsonl (its
  sha256); `seal` refuses an artifact without that row or whose bytes differ.
NOISY-ORACLE power: per asset, signal = sign(rho * z_future + sqrt(1 - rho^2) * eps), z_future =
  standardised future k-day open-to-open log return, eps independent N(0,1), re-decided every k days
  (decided at the 23:00 bar, executed at the next 00:00 open), weight = signal / K; injected after
  the interpreter into pipeline.evaluate_weights (G5 passes by definition: no params; G8 not run).
  Speeds: fast k = 1 day, slow k = 20 days. For each (null, speed, level 1.0 / 1.5) rho is tuned on
  the power worlds themselves (fixed eps per world) until the ACHIEVED mean VAL Sharpe is within
  RHO_TOL of the nominal level; the achieved value is reported.
Reduced pipeline (stated in the artifact): G8 not run (no extended universe in synthetic worlds;
  G8 can only veto, so null pass rates are upper bounds). Everything else is the real stage 1 and
  stage 2 with 200 permutation shifts and 12 jitter perturbations.

Rule (decide): the LARGEST G6 threshold in G6_GRID whose null pass rate is <= NULL_PASS_MAX under
BOTH nulls and whose every family's null pass rate (per its own submitted pairs; fix pass 7, R-L) is <=
FAMILY_PASS_MAX under both nulls; then oracle power at true Sharpe 1.5 must be >= POWER_MIN for both
speeds under both nulls. None qualifies, or the power rule fails -> STOP (the seal refuses). The pass
rate over DEV-positive pairs (KP-016) is stored as information; the rule does not read it. Fix pass 11 (R-R,
which replaces fix pass 10's cap R-P): the pooled and the family rates are Tier-1 passes over EVALUATED pairs and a
missing rate fails (no family is skipped); under each null every family must have at least FAMILY_EVALUATED_MIN
and the null as a whole at least NULL_EVALUATED_MIN of its DESIGNED pairs (the worlds ordered for the null)
evaluated, and at most NULL_FAULT_MAX of the submitted pairs may end neither evaluated nor liquidated; otherwise
that null fails every threshold. The stored rows must be exactly the protocol's design (design_problems: one null
row per seed and family, one oracle row per seed, speed and level, the module's SEEDS), else the unit STOPs. A
real run takes the protocol's sizes (CALIBRATION_WORLDS, CALIBRATION_ORACLE_WORLDS; the seal refuses others).
"""
from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import json
import math
import multiprocessing as mp
import time
from pathlib import Path

import numpy as np
import pandas as pd

from omr import access
from omr import constants as C
from omr import data
from omr import datasets as D
from omr import kernel_lock
from omr import lang as L
from omr import ledger
from omr import paths as P
from omr import pipeline
from omr import stats as S

PROTOCOL_VERSION = 6                  # fix pass 11: R-R (rates over evaluated pairs, evidence floors, faults,
                                      # complete rows, protocol sizes); 5 = fix pass 10 (R-P, R-Q); 4 = pass 7 (R-L)
FAMILIES = ("gen000_sma_cross_ls", "gen000_donchian_ls", "gen000_rsi_meanrev_ls",
            "gen000_voltarget_trend_ls", "gen000_funding_carry")
N_DRAWS = 20
SPEEDS = {"fast": 1, "slow": 20}
LEVELS = (1.0, 1.5)
RHO_GRID = np.round(np.concatenate([np.linspace(0.0, 0.2, 41), np.linspace(0.22, 1.0, 40)]), 6)
RHO_TOL = 0.02                     # bisection target; the order's bound is 0.1
RHO_BOUND = 0.1
HOUR_NS = 3_600_000_000_000
DAY_NS = 24 * HOUR_NS
OTHER = ["volume", "quote_volume", "trades", "taker_buy_volume", "taker_buy_quote_volume"]
GATES = list(pipeline.TIER_GATES)              # ["G1", "G2", "G3", "G4", "G5", "G6", "G7", "G10"]
SEEDS = {"A": 1000, "B": 4000, "oracle_A": 7000, "oracle_B": 8000}
OPTS = pipeline.Opts(include_g8=False, keep_detail=False)


def T(s) -> pd.Timestamp:
    return pd.Timestamp(s, tz="UTC").as_unit("ns")


def family_path(name: str) -> Path:
    if name not in FAMILIES:
        raise ValueError(f"unknown calibration family {name!r}: only the kernel's baselines {FAMILIES}")
    return P.PROGRAMS_DIR / f"{name}.omr"


# ---------------------------------------------------------------- source days

class Source:
    """Real core data as whole UTC days, each bar stored as open-relative ratios.

    Per symbol, over its calendar from its first full day to VAL end:
      g  = open / previous close, hr = high / open, lr = low / open, cr = close / open
      mark: gm = mark open / previous mark close (NaN if unknown), hm, lm, cm (NaN if no mark bar)
    m (mean hourly close-to-close log return over DEV+VAL) for last price and for mark.
    """

    def __init__(self, handle=None, tables=None):
        """tables {symbol: {"klines", "funding", "mark_klines"}}; None = the real stored data, read
        with the logged calibration handle."""
        a, b = T(C.DEV_START), T(C.VAL_END)
        self.sym = {}
        for s in C.CORE:
            if tables is None:
                kl = D.load_raw("klines", s, upto="val_end", handle=handle)
                fu = D.load_raw("funding", s, upto="val_end", handle=handle)
                mk = D.load_raw("mark_klines", s, upto="val_end", handle=handle)
            else:
                kl, fu, mk = tables[s]["klines"], tables[s]["funding"], tables[s]["mark_klines"]
            first_full = (kl.index[0] + pd.Timedelta(hours=23)).normalize()
            seg = kl.loc[first_full:b]
            nd = len(seg) // 24
            if len(seg) != nd * 24:
                raise RuntimeError(f"{s}: not a whole number of days")
            o = seg["open"].to_numpy(dtype=np.float64)
            h = seg["high"].to_numpy(dtype=np.float64)
            lo = seg["low"].to_numpy(dtype=np.float64)
            c = seg["close"].to_numpy(dtype=np.float64)
            pc = np.r_[kl.loc[:first_full - pd.Timedelta(hours=1), "close"].iloc[-1], c[:-1]]
            m = mk.reindex(seg.index)
            mo, mh, ml, mc = (m[k].to_numpy(dtype=np.float64) for k in ("open", "high", "low", "close"))
            mpc = np.r_[np.nan, mc[:-1]]
            has = np.isfinite(mo) & np.isfinite(mh) & np.isfinite(ml) & np.isfinite(mc) & (mo > 0) & (ml > 0)
            with np.errstate(divide="ignore", invalid="ignore"):
                gm = np.where(has & np.isfinite(mpc) & (mpc > 0), mo / mpc, np.nan)
                hm, lm, cm = (np.where(has, x / mo, np.nan) for x in (mh, ml, mc))
            dv = (seg.index >= a) & (seg.index <= b)
            lr_close = np.log(c / pc)
            m_last = float(np.mean(lr_close[dv]))
            with np.errstate(divide="ignore", invalid="ignore"):
                mlr = np.log(mc / mpc)
            ok = dv & np.isfinite(mlr)
            m_mark = float(np.mean(mlr[ok])) if ok.any() else m_last
            f = fu.loc[first_full:b]
            ft = data.ns_int(f.index)
            fday = ((ft - data.ns_int(seg.index[:1])[0]) // DAY_NS).astype(np.int64)
            order = np.argsort(fday, kind="mergesort")
            fday = fday[order]
            pre_mark = mk["close"].loc[:first_full - pd.Timedelta(hours=1)]
            self.sym[s] = {
                "days": pd.DatetimeIndex(seg.index[::24]), "nd": nd,
                "g": (o / pc).reshape(nd, 24), "hr": (h / o).reshape(nd, 24), "lr": (lo / o).reshape(nd, 24),
                "cr": (c / o).reshape(nd, 24),
                "gm": gm.reshape(nd, 24), "hm": hm.reshape(nd, 24), "lm": lm.reshape(nd, 24), "cm": cm.reshape(nd, 24),
                "has": has.reshape(nd, 24),
                "other": seg[OTHER].to_numpy(dtype=np.float64).reshape(nd, 24, len(OTHER)),
                "gap": seg["is_gap"].to_numpy().reshape(nd, 24),
                "fhour": ((ft[order] % DAY_NS) // HOUR_NS).astype(np.int64),
                "frate": f["rate"].to_numpy()[order], "fint": f["interval_hours"].to_numpy()[order],
                "offs": np.searchsorted(fday, np.arange(nd + 1)),
                "p0": float(pc[0]), "mp0": float(pre_mark.iloc[-1]) if len(pre_mark) else float(pc[0]),
                "m": m_last, "m_mark": m_mark,
            }
        # DEV+VAL calendar dates shared by all core symbols: the null-A sampling pool
        self.pool = pd.date_range(a, b.normalize(), freq="D").as_unit("ns")


def synthetic_tables(seed: int = 7) -> dict:
    """Fully synthetic core tables (dry run, M3): no real bar is read."""
    from omr import probe
    rng = np.random.default_rng(seed)
    out = {}
    for s, start, p0 in (("BTCUSDT", "2019-09-08 17:00", 10000.0), ("ETHUSDT", "2019-11-27 07:00", 150.0)):
        hours = int((T(C.VAL_END) - T(start)) / pd.Timedelta(hours=1)) + 1
        out[s] = probe.synthetic_symbol(rng, p0, start=start, hours=hours)
    return out


def _synth_symbol(v: dict, src_days: np.ndarray, flip: np.ndarray):
    """klines / mark / funding tables for one symbol from source day indices and per-day mirror
    flags. Returns (frame, liq)."""
    nd = len(src_days)
    g, hr, lr, cr = (v[k][src_days].copy() for k in ("g", "hr", "lr", "cr"))
    gm, hm, lm, cm = (v[k][src_days].copy() for k in ("gm", "hm", "lm", "cm"))
    has = v["has"][src_days].copy()
    F = flip[:, None]
    # mirror the demeaned path: log g' = 2m - log g ; hr' = 1/lr ; lr' = 1/hr ; cr' = 1/cr
    g = np.where(F, np.exp(2 * v["m"]) / g, g)
    hr, lr = np.where(F, 1.0 / lr, hr), np.where(F, 1.0 / hr, lr)
    cr = np.where(F, 1.0 / cr, cr)
    gm = np.where(F, np.exp(2 * v["m_mark"]) / gm, gm)
    hm, lm = np.where(F, 1.0 / lm, hm), np.where(F, 1.0 / hm, lm)
    cm = np.where(F, 1.0 / cm, cm)
    g, hr, lr, cr = (x.reshape(-1) for x in (g, hr, lr, cr))
    gm, hm, lm, cm, has = (x.reshape(-1) for x in (gm, hm, lm, cm, has))
    step = g * cr
    prev_c = v["p0"] * np.r_[1.0, np.cumprod(step)[:-1]]
    o = prev_c * g
    idx = pd.date_range(v["days"][0], periods=nd * 24, freq="h").as_unit("ns")
    idx.name = "open_time"
    kl = pd.DataFrame({"open": o, "high": o * hr, "low": o * lr, "close": o * cr}, index=idx)
    oth = v["other"][src_days].reshape(nd * 24, len(OTHER))
    for j, c in enumerate(OTHER):
        kl[c] = oth[:, j]
    kl["is_gap"] = v["gap"][src_days].reshape(-1)
    gm_eff = np.where(np.isfinite(gm), gm, g)
    cm_eff = np.where(has, cm, cr)
    mstep = gm_eff * cm_eff
    mprev = v["mp0"] * np.r_[1.0, np.cumprod(mstep)[:-1]]
    mo = mprev * gm_eff
    mark = pd.DataFrame({"open": mo, "high": mo * hm, "low": mo * lm, "close": mo * cm,
                         "samples": 3600.0}, index=idx)[has]
    sel = np.concatenate([np.arange(v["offs"][p], v["offs"][p + 1]) for p in src_days])
    day_of = np.concatenate([np.full(v["offs"][p + 1] - v["offs"][p], i) for i, p in enumerate(src_days)])
    ft = data.ns_int(idx[:1])[0] + day_of * DAY_NS + v["fhour"][sel] * HOUR_NS
    fu = pd.DataFrame({"rate": v["frate"][sel], "interval_hours": v["fint"][sel], "offset_ms": 0.0},
                      index=pd.DatetimeIndex(pd.to_datetime(ft, unit="ns", utc=True)).as_unit("ns"))
    fu.index.name = "settle_time"
    raw = {"klines": kl, "funding": fu, "mark_klines": mark, "index_klines": mark}   # no core family reads index_close
    return D.assemble_frame(raw, D.PROGRAM_EXTRA), D.liquidation_ratios(kl, mark)


def build_world(src: Source, null: str, seed: int) -> pipeline.World:
    """null 'A': iid day bootstrap from DEV+VAL; null 'B': real day order with daily mirror coins."""
    rng = np.random.default_rng([seed, 11 if null == "A" else 12])
    syms = list(src.sym)
    start = min(src.sym[s]["days"][0] for s in syms)
    cal = pd.date_range(start, T(C.VAL_END).normalize(), freq="D").as_unit("ns")
    ncal = len(cal)
    if null == "A":
        pick_date = src.pool[rng.integers(0, len(src.pool), ncal)]
        flips = np.zeros(ncal, dtype=bool)
    elif null == "B":
        pick_date = cal
        flips = rng.uniform(size=ncal) < 0.5
    else:
        raise ValueError(null)
    frames, liqs = {}, {}
    for s in syms:
        v = src.sym[s]
        d0 = int((v["days"][0] - cal[0]) / pd.Timedelta(days=1))
        src_days = np.asarray(((pick_date[d0:] - v["days"][0]) // pd.Timedelta(days=1)).astype(np.int64))
        frames[s], liqs[s] = _synth_symbol(v, src_days, flips[d0:])
    return pipeline.World(core=frames, symbols=C.CORE, liq=liqs, btc=frames[C.BTC])


def dev_view(world: pipeline.World):
    cap = T(C.DEV_END)
    frames = {s: f.loc[:cap] for s, f in world.core.items()}
    return frames, frames[C.BTC]


# ---------------------------------------------------------------- noisy oracle

class OracleBase:
    """Per world and speed: standardised future block returns z and fixed eps draws."""

    def __init__(self, world: pipeline.World, k_days: int, eps_seed):
        self.grid = pipeline.core_grid(world.core, world.symbols)
        self.mk = pipeline.Market(world.core, world.liq, self.grid, world.symbols)
        self.dev_s, self.val_e = self.mk.pos(C.DEV_START), self.mk.pos(C.VAL_END)
        K = len(world.symbols)
        step = 24 * k_days
        self.starts = np.arange(self.dev_s, self.val_e, step)
        self.ends = np.minimum(self.starts + step, self.val_e)
        rng = np.random.default_rng(eps_seed)
        self.z, self.eps = [], []
        for j in range(K):
            o = self.mk.op[:, j]
            R = np.log(o[self.ends] / o[self.starts])
            sd = R.std(ddof=1)
            self.z.append((R - R.mean()) / sd if sd > 0 else np.zeros_like(R))
            self.eps.append(rng.standard_normal(len(R)))
        rows = np.arange(self.starts[0] - 1, self.ends[-1] - 1)
        self.rows = rows
        self.block = np.repeat(np.arange(len(self.starts)), self.ends - self.starts)
        self.K = K

    def weights(self, rho: float) -> np.ndarray:
        W = np.zeros((len(self.grid), self.K))
        for j in range(self.K):
            x = rho * self.z[j] + math.sqrt(max(0.0, 1.0 - rho * rho)) * self.eps[j]
            sgn = np.where(x >= 0, 1.0, -1.0) / self.K
            W[self.rows, j] = sgn[self.block]
            W[self.ends[-1] - 1:, j] = sgn[-1]
        return W

    def val_sharpe(self, rho: float) -> float:
        return pipeline.val_sharpe_of(self.mk.run(self.weights(rho), self.dev_s, self.val_e))


# ---------------------------------------------------------------- workers

_W = {}


def _init(families, handle, synthetic=False):
    _W["handle"] = handle
    _W["src"] = Source(tables=synthetic_tables()) if synthetic else Source(handle)
    _W["progs"] = {f: L.parse_file(family_path(f)) for f in families}


def _seed(*parts) -> int:
    return int(ledger.sha256_text("|".join(str(x) for x in parts))[:15], 16)


def draw_params(prog: L.Program, rng) -> dict:
    out = {}
    for k, p in prog.params.items():
        out[k] = int(rng.integers(int(p.low), int(p.high) + 1)) if p.is_int else float(rng.uniform(p.low, p.high))
    return out


def dev_candidate(codes: dict, sh: float) -> bool:
    """R-Q (fix pass 10, both units): whether a screened draw with DEV Sharpe sh is a candidate for submission. -inf is
    the DEV Sharpe of a liquidated DEV run (stats.sharpe is finite otherwise): counted as dev_liquidated; any other
    value that is not a finite number: dev_sharpe_not_finite. Neither is a candidate."""
    if sh == float("-inf"):
        codes["dev_liquidated"] = codes.get("dev_liquidated", 0) + 1
        return False
    if not np.isfinite(sh):
        codes["dev_sharpe_not_finite"] = codes.get("dev_sharpe_not_finite", 0) + 1
        return False
    return True


def dev_sharpe(world_dev_frames, liq, screened) -> float:
    mk = pipeline.Market(world_dev_frames, liq, screened["grid"], C.CORE)
    run = mk.run(screened["W"], mk.pos(C.DEV_START), mk.pos(C.DEV_END))
    return float("-inf") if run.liquidated else S.sharpe(run.daily_returns())


def summarise(res: dict, extra: dict) -> dict:
    out = dict(extra)
    out["status"] = res["status"]
    if res["status"] != "evaluated":
        out["reason"] = res.get("reason")
        return out
    g = res["gates"]
    out["gates"] = {k: v["pass"] for k, v in g.items()}
    out["gate_values"] = {k: v["value"] for k, v in g.items()}
    out["g5_vacuous"] = bool(g["G5"].get("g5_vacuous"))
    out["perm_p"] = g["G6"]["value"]
    m = res["metrics"]
    out.update(val_sharpe=m["val"]["sharpe"], dev_sharpe=m["dev"]["sharpe"], psr0=m["val"]["psr0"],
               direction_changes_dev=m["direction_changes_dev"], direction_changes_val=m["direction_changes_val"],
               rebalances=m["rebalances"])
    return out


def task_null(args) -> list:
    null, world_seed = args
    world = build_world(_W["src"], null, world_seed)
    frames_dev, btc_dev = dev_view(world)
    out = []
    for fam, prog in _W["progs"].items():
        rng = np.random.default_rng(_seed("draws", null, fam, world_seed))
        best, best_sh, codes = None, float("-inf"), {}
        for i in range(N_DRAWS):                       # screening: DEV signals and the activity rule only (M5)
            q = draw_params(prog, rng)
            sc = pipeline.screen_dev(prog, q, frames_dev, btc_dev)
            if not sc["ok"]:
                codes[sc["code"]] = codes.get(sc["code"], 0) + 1
                continue
            codes["passed"] = codes.get("passed", 0) + 1
            sh = dev_sharpe(frames_dev, world.liq, sc)
            if not dev_candidate(codes, sh):                   # R-Q: liquidated on DEV or not finite: never submitted
                continue
            if best is None or sh > best_sh:
                best, best_sh = q, sh
        base = {"null": null, "family": fam, "world_seed": world_seed, "stage1": codes}
        if best is None:
            out.append(dict(base, submitted=False, status="not_submitted"))
            continue
        # the submitted draw gets the full stage 1 (truncation and start-cut self-checks) and stage 2
        s1 = pipeline.stage1(prog, best, frames_dev, btc_dev, np.random.default_rng(_seed("s1", null, fam, world_seed)),
                             OPTS)
        if not s1["ok"]:
            out.append(dict(base, submitted=False, status=f"stage1_{s1['code']}", params=best,
                            fault=s1.get("fault")))
            continue
        res = pipeline.stage2(prog, best, world, s1, OPTS, _W["handle"], _seed("null", null, fam, world_seed), None)
        out.append(summarise(res, dict(base, submitted=True, params=best, best_dev_sharpe_of_passers=best_sh)))
    return out


def task_oracle_curve(args) -> list:
    null, world_seed, speed, rhos = args
    ob = OracleBase(build_world(_W["src"], null, world_seed), SPEEDS[speed], _seed("eps", null, world_seed, speed))
    return [ob.val_sharpe(float(r)) for r in rhos]


def task_oracle_power(args) -> list:
    null, world_seed, rhos = args      # rhos: {"speed|level": rho}
    world = build_world(_W["src"], null, world_seed)
    out = []
    for speed in SPEEDS:
        ob = OracleBase(world, SPEEDS[speed], _seed("eps", null, world_seed, speed))
        for lvl in LEVELS:
            rho = rhos[f"{speed}|{lvl}"]
            res = pipeline.evaluate_weights(ob.weights(rho), ob.grid, world, _seed("oracle", null, world_seed, speed, lvl),
                                            OPTS, _W["handle"], None)
            out.append(summarise(res, {"null": null, "speed": speed, "level": lvl, "rho": rho,
                                       "world_seed": world_seed}))
    return out


# ---------------------------------------------------------------- summaries and the rule

# Tier 1 re-read at G6 threshold p_max from a stored row: the one implementation is omr.pipeline.tier_at (fix pass
# 8, FP8-2: an evaluated row that is malformed raises ValueError, which the unit verdict turns into its STOP)
tier_at = pipeline.tier_at


def gate_rates(rows: list, p_max: float) -> dict:
    ev = [r for r in rows if r.get("status") == "evaluated"]
    out = {}
    for g in GATES:
        if not rows:
            out[g] = None
        elif g == "G6":
            out[g] = sum(r["perm_p"] <= p_max + 1e-12 for r in ev) / len(rows)
        else:
            out[g] = sum(bool(r["gates"].get(g)) for r in ev) / len(rows)
    return out


def null_summary(rows: list, families, designed=None) -> dict:
    """The null side of one null. R-R (fix pass 11): designed = the worlds ordered for this null (the run's --worlds;
    protocol.worlds_per_null of a stored artifact), never the rows present: every family's designed pairs. The rates
    of the rule are Tier-1 passes over EVALUATED pairs; a submitted pair that ends liquidated or in a fault leaves the
    denominator, as a pair never submitted does."""
    sub = [r for r in rows if r.get("submitted")]
    ev = [r for r in sub if r.get("status") == "evaluated"]
    out = {"n_pairs": len(rows), "n_submitted": len(sub),
           "n_not_submitted": len(rows) - len(sub), "n_evaluated": len(ev),
           "n_submitted_liquidated": sum(1 for r in sub if r.get("status") == "liquidated"),
           "n_submitted_fault": sum(1 for r in sub if r.get("status") not in ("evaluated", "liquidated")),
           "designed_per_family": designed,
           "submitted_status": {}, "stage1_draws": {}, "by_threshold": {},
           "per_family": {f: {"pairs": 0, "submitted": 0, "evaluated": 0} for f in families}}
    for r in rows:
        out["per_family"][r["family"]]["pairs"] += 1
        out["per_family"][r["family"]]["submitted"] += int(bool(r.get("submitted")))
        out["per_family"][r["family"]]["evaluated"] += int(bool(r.get("submitted")) and r.get("status") == "evaluated")
        for k, v in r.get("stage1", {}).items():
            out["stage1_draws"][k] = out["stage1_draws"].get(k, 0) + v
    for r in sub:
        out["submitted_status"][r["status"]] = out["submitted_status"].get(r["status"], 0) + 1
    # 7b-2: truthiness, as tier_at reads a gate (a numpy bool in memory counts as it does after JSON)
    dev_pos = [r for r in sub if r.get("status") == "evaluated" and bool((r.get("gates") or {}).get("G3"))]
    out["n_dev_positive"] = len(dev_pos)
    ev_f = {f: out["per_family"][f]["evaluated"] for f in families}
    for t in C.G6_GRID:
        passers = [r for r in sub if tier_at(r, t)]
        out["by_threshold"][str(t)] = {
            "tier1": len(passers),
            "pass_rate": len(passers) / len(ev) if ev else None,             # per EVALUATED pair (the rule, R-R)
            "pass_rate_submitted": len(passers) / len(sub) if sub else None,  # information (the rule before R-R)
            "family_pass_rate": {f: (sum(1 for r in passers if r["family"] == f) / ev_f[f]) if ev_f[f] else None
                                 for f in families},                            # per family (R-L, R-R: the rule)
            "pass_rate_dev_positive": len(passers) / len(dev_pos) if dev_pos else None,   # information (KP-016)
            "pass_rate_all_pairs": len(passers) / len(rows) if rows else None,
            "passer_families": {f: sum(1 for r in passers if r["family"] == f) for f in families},
            "passers": [{"family": r["family"], "world_seed": r["world_seed"], "params": r["params"],
                         "perm_p": r["perm_p"], "val_sharpe": r["val_sharpe"]} for r in passers],
            "gate_pass_rate_submitted": gate_rates(sub, t),
        }
    return out


def oracle_summary(rows: list) -> dict:
    out = {}
    for speed in SPEEDS:
        for lvl in LEVELS:
            rr = [r for r in rows if r["speed"] == speed and r["level"] == lvl]
            fin = [r["val_sharpe"] for r in rr if r.get("status") == "evaluated" and np.isfinite(r["val_sharpe"])]
            out[f"{speed}|{lvl}"] = {
                "n": len(rr), "mean_val_sharpe": float(np.mean(fin)) if fin else None,
                "not_evaluated": int(sum(1 for r in rr if r.get("status") != "evaluated")),
                "by_threshold": {str(t): {"power": (sum(tier_at(r, t) for r in rr) / len(rr)) if rr else None,
                                          "tier1": int(sum(tier_at(r, t) for r in rr)),
                                          "gate_pass_rate": gate_rates(rr, t)} for t in C.G6_GRID}}
    return out


RULE = ("G6 threshold = the LARGEST of G6_GRID whose null pass rate (Tier-1 passes / EVALUATED pairs) is "
        "<= NULL_PASS_MAX under BOTH nulls AND whose every family's null pass rate (its Tier-1 passes / its "
        "EVALUATED pairs; a missing rate fails) is <= FAMILY_PASS_MAX under BOTH nulls, where a null fails every "
        "threshold when a family has fewer than FAMILY_EVALUATED_MIN or the null fewer than NULL_EVALUATED_MIN of "
        "its DESIGNED pairs evaluated, or when more than NULL_FAULT_MAX of its SUBMITTED pairs ended neither "
        "evaluated nor liquidated, and the stored rows must be exactly the protocol's design; "
        "then oracle power at true Sharpe 1.5 >= POWER_MIN for BOTH speeds "
        "under BOTH nulls, with every oracle level's achieved mean VAL Sharpe within RHO_BOUND (0.1) of nominal; "
        "otherwise STOP")


def _bound_failure(null: str, what: str, r, bound: str) -> str:
    """The text of one failed bound; never raises (None, NaN, inf or a non-number)."""
    if r is None:
        return f"null {null}: {what} rate missing (no evaluated pair)"
    try:
        x = float(r)
    except (TypeError, ValueError):
        return f"null {null}: {what} {r!r} is not a finite rate"
    if not math.isfinite(x):
        return f"null {null}: {what} {x} is not a finite rate"
    return f"null {null}: {what} {x:.4f} > {bound}"


def _count(v) -> bool:
    return isinstance(v, (int, np.integer)) and not isinstance(v, (bool, np.bool_))


def fault_share(summary: dict, null: str) -> tuple:
    """R-R (c): (share or None, failure text or None) of the submitted pairs of one null that ended in a fault
    (status neither "evaluated" nor "liquidated"). Fail-closed: the bound holds only when both counts are proper
    (integers, 0 <= count <= n_submitted, n_submitted > 0) and the share IS <= NULL_FAULT_MAX (+1e-12)."""
    cnt, nsub = summary.get("n_submitted_fault"), summary.get("n_submitted")
    if not (_count(cnt) and _count(nsub) and nsub > 0 and 0 <= cnt <= nsub):
        return None, f"null {null}: the count of submitted pairs in a fault is missing or malformed ({cnt!r} of {nsub!r})"
    share = int(cnt) / int(nsub)
    if not (share <= C.NULL_FAULT_MAX + 1e-12):
        return share, f"null {null}: {int(cnt)} of {int(nsub)} submitted pairs ended in a fault ({share:.4f}) > NULL_FAULT_MAX"
    return share, None


def _floor(null: str, what: str, ev, designed, floor: float, name: str) -> tuple:
    """(share or None, failure text or None): evaluated / designed must be proper counts (designed > 0, 0 <= ev <=
    designed) and the share IS >= the floor (-1e-12)."""
    if not (_count(ev) and _count(designed) and designed > 0 and 0 <= ev <= designed):
        return None, f"null {null}: {what}: evaluated / designed counts missing or malformed ({ev!r} of {designed!r})"
    share = int(ev) / int(designed)
    if not (share >= floor - 1e-12):
        return share, f"null {null}: {what} evaluated {int(ev)} of {int(designed)} designed ({share:.4f}) < {name}"
    return share, None


def evidence_floors(summary: dict, null: str) -> tuple:
    """R-R (b): ({"pooled": share, "families": {f: share}}, failure texts) of one null against the floors: every
    family evaluated / designed >= FAMILY_EVALUATED_MIN, the null evaluated / (designed x families) >=
    NULL_EVALUATED_MIN; designed = the summary's designed_per_family (the worlds ordered)."""
    designed = summary.get("designed_per_family")
    per = summary.get("per_family")
    shares, fails = {"pooled": None, "families": {}}, []
    if not isinstance(per, dict) or not per:
        return shares, [f"null {null}: no families in the summary"]
    for f in sorted(per):
        ev = per[f].get("evaluated") if isinstance(per[f], dict) else None
        shares["families"][f], why = _floor(null, f"family {f}", ev, designed, C.FAMILY_EVALUATED_MIN,
                                            "FAMILY_EVALUATED_MIN")
        if why:
            fails.append(why)
    total = designed * len(per) if _count(designed) else None
    shares["pooled"], why = _floor(null, "pooled", summary.get("n_evaluated"), total, C.NULL_EVALUATED_MIN,
                                   "NULL_EVALUATED_MIN")
    if why:
        fails.append(why)
    return shares, fails


def _key_problems(label: str, rows, want: set, key, null: str, limit: int) -> list:
    if not isinstance(rows, list):
        return [f"{label}: no list of rows"]
    seen, bad = {}, []
    for i, r in enumerate(rows):
        if not isinstance(r, dict):
            bad.append(f"row {i} is not a mapping")
            continue
        k = key(r)
        if r.get("null") != null:
            bad.append(f"row {k} carries null {r.get('null')!r}")
        seen[k] = seen.get(k, 0) + 1
    missing = sorted((k for k in want if k not in seen), key=repr)
    double = sorted((k for k, c in seen.items() if c > 1 and k in want), key=repr)
    foreign = sorted((k for k in seen if k not in want), key=repr)
    out = []
    for what, ks in (("missing", missing), ("double", double), ("foreign", foreign)):
        if ks:
            out.append(f"{label}: {len(ks)} {what} row(s), first {', '.join(repr(k) for k in ks[:limit])}")
    if bad:
        out.append(f"{label}: {len(bad)} malformed row(s), first {', '.join(bad[:limit])}")
    return out


def _level(v):
    return float(v) if isinstance(v, (int, float, np.integer, np.floating)) and not isinstance(v, (bool, np.bool_)) else v


def design_problems(art: dict, seeds: dict, families, speeds, levels, limit: int = 3) -> list:
    """R-R (d), shared by both units: the stored rows against the protocol's design. protocol.worlds_per_null and
    protocol.oracle_worlds must be positive integers and protocol.seeds the module's SEEDS; then under each null
    exactly one null row per (world_seed, family) for world_seed in seeds[null] + 0 .. worlds - 1 and every family of
    the unit, and exactly one oracle row per (world_seed, speed, level) for world_seed in seeds["oracle_" + null] +
    0 .. oracle_worlds - 1, the unit's speeds and the levels it tunes; every row also carries its own null. Returns
    the problems (empty = the design), naming the first few missing, double, foreign or malformed rows."""
    prot = art.get("protocol") if isinstance(art.get("protocol"), dict) else {}
    W, OW = prot.get("worlds_per_null"), prot.get("oracle_worlds")
    out = []
    if not (_count(W) and W > 0):
        out.append(f"protocol worlds_per_null {W!r} is not a positive integer")
    if not (_count(OW) and OW > 0):
        out.append(f"protocol oracle_worlds {OW!r} is not a positive integer")
    if prot.get("seeds") != dict(seeds):
        out.append(f"protocol seeds {prot.get('seeds')!r} are not the module's {dict(seeds)!r}")
    if out:
        return out
    fams, spd, lvl = list(families), list(speeds), [float(x) for x in levels]
    for n in ("A", "B"):
        want = {(seeds[n] + i, f) for i in range(W) for f in fams}
        rows = ((art.get("nulls") or {}).get(n) or {}).get("rows")
        out += _key_problems(f"null {n}", rows, want, lambda r: (r.get("world_seed"), r.get("family")), n, limit)
        want = {(seeds["oracle_" + n] + i, s, x) for i in range(OW) for s in spd for x in lvl}
        rows = ((art.get("oracle") or {}).get(n) or {}).get("rows")
        out += _key_problems(f"oracle {n}", rows, want,
                             lambda r: (r.get("world_seed"), r.get("speed"), _level(r.get("level"))), n, limit)
    return out


def design_stop(unit: str, problems: list) -> dict:
    return {"STOP": True, "chosen_threshold": None,
            "reason": f"{unit} artifact malformed: rows do not match the protocol design: " + "; ".join(problems)}


def decide(nulls: dict, oracle: dict) -> dict:
    """The calibration rule (also applied by `omr.kernel_lock seal` to the stored rows)."""
    def rate(n, t, k="pass_rate"):
        return nulls[n]["summary"]["by_threshold"][str(t)][k]

    flt = {n: fault_share(nulls[n]["summary"], n) for n in ("A", "B")}                 # R-R (c)
    flo = {n: evidence_floors(nulls[n]["summary"], n) for n in ("A", "B")}             # R-R (b)

    def failures(t) -> list:
        """Which bound fails at threshold t under which null (pooled, or the family's NAME). Fail-closed (7b-1):
        a bound holds only when the rate IS <= it, so a NaN, an inf or a missing pooled rate fails."""
        out = []
        for n in ("A", "B"):
            out += flo[n][1]                              # R-R (b): a floor not met fails every threshold
            if flt[n][1] is not None:                     # R-R (c): too many faults
                out.append(flt[n][1])
            r = rate(n, t)
            if not (r is not None and r <= C.NULL_PASS_MAX + 1e-12):
                out.append(_bound_failure(n, "pooled", r, "NULL_PASS_MAX"))
            for f, fr in sorted(rate(n, t, "family_pass_rate").items()):
                if not (fr is not None and fr <= C.FAMILY_PASS_MAX + 1e-12):    # R-R (a): a missing rate fails
                    out.append(_bound_failure(n, f"family {f}", fr, "FAMILY_PASS_MAX"))
        return out
    fails = {str(t): failures(t) for t in C.G6_GRID}
    qualifying = [t for t in C.G6_GRID if not fails[str(t)]]
    chosen = max(qualifying) if qualifying else None
    verdict = {"rule": RULE, "grid": list(C.G6_GRID), "null_pass_max": C.NULL_PASS_MAX, "power_min": C.POWER_MIN,
               "family_pass_max": C.FAMILY_PASS_MAX, "denominator": "evaluated pairs",
               "family_evaluated_min": C.FAMILY_EVALUATED_MIN, "null_evaluated_min": C.NULL_EVALUATED_MIN,
               "evaluated_share": {n: flo[n][0] for n in ("A", "B")},
               "null_fault_max": C.NULL_FAULT_MAX, "null_fault_share": {n: flt[n][0] for n in ("A", "B")},
               "null_pass_rate": {n: {str(t): rate(n, t) for t in C.G6_GRID} for n in ("A", "B")},
               "null_pass_rate_submitted": {n: {str(t): rate(n, t, "pass_rate_submitted") for t in C.G6_GRID}
                                            for n in ("A", "B")},
               "family_pass_rate": {n: {str(t): rate(n, t, "family_pass_rate") for t in C.G6_GRID} for n in ("A", "B")},
               "null_pass_rate_dev_positive": {n: {str(t): rate(n, t, "pass_rate_dev_positive") for t in C.G6_GRID}
                                               for n in ("A", "B")},
               "null_pass_rate_all_pairs": {n: {str(t): rate(n, t, "pass_rate_all_pairs") for t in C.G6_GRID}
                                            for n in ("A", "B")},
               "threshold_failures": fails, "qualifying": qualifying, "chosen_threshold": chosen}
    if chosen is None:
        verdict["STOP"] = True
        verdict["reason"] = ("no G6 threshold in the grid qualifies under both nulls: " +
                             "; ".join(f"{t}: " + ", ".join(fails[str(t)]) for t in C.G6_GRID))
        return verdict
    achieved = {n: {k: v["mean_val_sharpe"] for k, v in oracle[n]["summary"].items()} for n in ("A", "B")}
    verdict["oracle_achieved_mean_val_sharpe"] = achieved
    # 7b-3: a level is inside its bound only when its achieved mean IS within RHO_BOUND (None, NaN, inf: outside)
    off = [f"{n}/{k}" for n in achieved for k, v in achieved[n].items()
           if not (v is not None and abs(v - float(k.split("|")[1])) <= RHO_BOUND)]
    verdict["oracle_level_outside_bound"] = off
    power15 = {n: {s: oracle[n]["summary"][f"{s}|1.5"]["by_threshold"][str(chosen)]["power"] for s in SPEEDS}
               for n in ("A", "B")}
    verdict["power_at_1_5_chosen"] = power15
    # 7b-3: a cell has enough power only when its power IS >= POWER_MIN (None, NaN: below)
    below = [f"{n}/{s}" for n in power15 for s in power15[n]
             if not (power15[n][s] is not None and power15[n][s] >= C.POWER_MIN)]
    verdict["below_power_min"] = below
    verdict["STOP"] = bool(below) or bool(off)
    if off:
        verdict["reason"] = f"oracle achieved mean VAL Sharpe more than {RHO_BOUND} from its level: " + ", ".join(off)
    elif below:
        verdict["reason"] = "oracle power at true Sharpe 1.5 below POWER_MIN at the chosen threshold: " + ", ".join(below)
    return verdict


def verdict_from_rows(art: dict) -> dict:
    """Recompute every summary from the stored per-pair rows and apply the rule (no re-run). R-R (d): rows that are
    not exactly the protocol's design stop the unit before the rule is read."""
    problems = design_problems(art, SEEDS, FAMILIES, SPEEDS, LEVELS)
    if problems:
        return design_stop("core", problems)
    fams = list(art["families"])
    W = art["protocol"]["worlds_per_null"]
    nulls = {n: {"summary": null_summary(art["nulls"][n]["rows"], fams, W)} for n in ("A", "B")}
    oracle = {n: {"summary": oracle_summary(art["oracle"][n]["rows"])} for n in ("A", "B")}
    return decide(nulls, oracle)


def tune_rho(pool, null: str, speed: str, seeds: list, log) -> dict:
    """rho per level so the mean VAL Sharpe over the power worlds (fixed eps per world) is as close
    as possible to the level: a coarse curve on RHO_GRID, a 41-point fine curve inside the bracket,
    the fine point closest to the level, then the achieved mean re-measured at that rho."""
    def means(rhos):
        res = pool.map(task_oracle_curve, [(null, s, speed, [float(r) for r in rhos]) for s in seeds])
        mat = np.array(res, dtype=np.float64)
        mat = np.where(np.isfinite(mat), mat, np.nan)
        return np.nanmean(mat, axis=0)

    mean = means(RHO_GRID)
    out = {"mean_curve": {f"{r:.4f}": float(m) for r, m in zip(RHO_GRID, mean)},
           "mean_val_sharpe_at_rho0": float(mean[0])}
    fine = {}
    for lvl in LEVELS:
        idx = np.nonzero(mean >= lvl)[0]
        if len(idx) == 0:
            lo, hi = float(RHO_GRID[-2]), float(RHO_GRID[-1])
        elif idx[0] == 0:
            lo, hi = float(RHO_GRID[0]), float(RHO_GRID[1])
        else:
            lo, hi = float(RHO_GRID[idx[0] - 1]), float(RHO_GRID[idx[0]])
        fine[lvl] = np.linspace(lo, hi, 41)
    fm = means(np.concatenate([fine[lv] for lv in LEVELS]))
    picks = {}
    for i, lvl in enumerate(LEVELS):
        seg = fm[i * 41:(i + 1) * 41]
        j = int(np.nanargmin(np.abs(seg - lvl)))
        picks[lvl] = float(fine[lvl][j])
    ach = means([picks[lv] for lv in LEVELS])
    for i, lvl in enumerate(LEVELS):
        a_ = float(ach[i])
        out[str(lvl)] = {"rho": picks[lvl], "achieved_mean_val_sharpe": a_,
                         "bracket": [float(fine[lvl][0]), float(fine[lvl][-1])],
                         "within_tol": bool(abs(a_ - lvl) <= RHO_TOL), "within_bound": bool(abs(a_ - lvl) <= RHO_BOUND)}
        log(f"    null {null} {speed:4s} level {lvl}: rho {picks[lvl]:.5f} -> achieved mean VAL Sharpe {a_:.3f} "
            f"on {len(seeds)} worlds")
    return out


def protocol_header(worlds: int, oracle_worlds: int) -> dict:
    """R-R (e), fix pass 11: the protocol header of a core calibration artifact ("protocol"): everything that fixes
    the run apart from the data and the families (their own checks), the options object included, because a run can
    change it at run time and the semantic hash does not pin that. main writes it; the seal compares the stored one
    with this function's value for the protocol's sizes, key by key."""
    return {"protocol_version": PROTOCOL_VERSION, "worlds_per_null": worlds, "oracle_worlds": oracle_worlds,
            "draws_per_pair": N_DRAWS, "speeds_days": dict(SPEEDS), "levels": list(LEVELS), "seeds": dict(SEEDS),
            "rho_tol": RHO_TOL, "rho_grid": [float(r) for r in RHO_GRID], "opts": dataclasses.asdict(OPTS),
            "reduced_pipeline": "G8 not run (no extended universe; G8 can only veto, so null pass rates are upper "
                                "bounds); oracles: G5 passes by definition (no params)"}


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m omr.calibrate")
    ap.add_argument("--worlds", type=int, default=C.CALIBRATION_WORLDS, help="null worlds per null (x 5 families)")
    ap.add_argument("--oracle-worlds", type=int, default=C.CALIBRATION_ORACLE_WORLDS)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--families", nargs="*", default=None, help="subset of the kernel's five baselines")
    ap.add_argument("--unlocked-dry-run", action="store_true",
                    help="construction check on FULLY SYNTHETIC prices (no real bar after DEV end is read); never sealable")
    ap.add_argument("--out", default=None, help="output path (required with --unlocked-dry-run)")
    a = ap.parse_args(argv)
    t0 = time.time()
    if not a.unlocked_dry_run and (a.worlds != C.CALIBRATION_WORLDS or a.oracle_worlds != C.CALIBRATION_ORACLE_WORLDS
                                   or (a.families is not None and sorted(a.families) != sorted(FAMILIES))):
        # R-R (f): no reduced real run (it would be a look at the null side before the run that counts)
        raise SystemExit(f"a real calibration takes the protocol's sizes and families: --worlds {C.CALIBRATION_WORLDS}, "
                         f"--oracle-worlds {C.CALIBRATION_ORACLE_WORLDS}, all of {list(FAMILIES)} (reduced sizes only "
                         "with --unlocked-dry-run)")

    def log(s):
        print(s, flush=True)

    fams = list(a.families) if a.families else list(FAMILIES)
    for f in fams:
        family_path(f)
    problems = kernel_lock.verify()
    lock_ok = not problems
    if not lock_ok and not a.unlocked_dry_run:
        log("KERNEL LOCK DOES NOT VERIFY - the calibration runs only on the locked kernel:")
        for p in problems[:10]:
            log("  " + p)
        raise SystemExit(3)
    if a.unlocked_dry_run and not a.out:
        raise SystemExit("--unlocked-dry-run needs --out <path> (never written into ledger/)")
    k = kernel_lock.read_lock() if lock_ok else kernel_lock.compute()
    kh, sem = k["combined"], k["semantic"]
    synthetic = bool(a.unlocked_dry_run)
    if synthetic:
        rh = "synthetic-dry-run"
        handle = access.for_calibration(f"calibration DRY RUN, semantic {sem[:16]}: fully synthetic prices, no real "
                                        "bar after DEV end is read")
    else:
        manifest = data.load_manifest()
        if not data.validation_ok():
            raise SystemExit("data not validated for the current files: run python -m omr.data validate")
        rh = manifest["research_hash"]
        handle = access.for_calibration(f"calibration protocol v{PROTOCOL_VERSION}, semantic {sem[:16]}: synthetic "
                                        "worlds built from DEV+VAL bars; no real-program VAL result is computed")
    log(f"calibration v{PROTOCOL_VERSION}: semantic kernel {sem[:16]} (lock {'VERIFIED' if lock_ok else 'NOT verified'}), "
        f"{'SYNTHETIC dry run' if synthetic else 'research_hash ' + rh[:16]}, families {fams}")
    ctx = mp.get_context("spawn")
    nulls, oracle = {}, {}
    with ctx.Pool(a.workers, initializer=_init, initargs=(fams, handle, synthetic)) as pool:
        for null in ("A", "B"):
            log(f"[null {null}] {a.worlds} worlds x {len(fams)} families, {N_DRAWS} draws screened by activity, "
                "best DEV Sharpe submitted")
            rows = []
            for i, rr in enumerate(pool.imap_unordered(task_null, [(null, SEEDS[null] + i) for i in range(a.worlds)])):
                rows.extend(rr)
                if (i + 1) % 20 == 0:
                    log(f"    {i + 1}/{a.worlds} worlds  ({time.time() - t0:.0f} s)")
            rows.sort(key=lambda r: (r["world_seed"], r["family"]))
            sm = null_summary(rows, fams, a.worlds)
            nulls[null] = {"rows": rows, "summary": sm}
            for t in C.G6_GRID:
                b = sm["by_threshold"][str(t)]
                rate = "n/a" if b["pass_rate"] is None else f"{b['pass_rate']:.4f}"
                log(f"    null {null} p<={t}: {b['tier1']}/{sm['n_evaluated']} evaluated = {rate} "
                    f"({sm['n_submitted']} submitted, {sm['n_pairs']} pairs)  passers {b['passer_families']}")
            log(f"    submitted status {sm['submitted_status']}  stage-1 draws {sm['stage1_draws']}")
        for null in ("A", "B"):
            seeds = [SEEDS[f"oracle_{null}"] + i for i in range(a.oracle_worlds)]
            log(f"[oracle {null}] tuning rho on the {len(seeds)} power worlds")
            rhos, tuning = {}, {}
            for speed in SPEEDS:
                tuning[speed] = tune_rho(pool, null, speed, seeds, log)
                for lvl in LEVELS:
                    rhos[f"{speed}|{lvl}"] = tuning[speed][str(lvl)]["rho"]
            log(f"[oracle {null}] power on the {len(seeds)} worlds")
            rows = []
            for rr in pool.imap_unordered(task_oracle_power, [(null, s, rhos) for s in seeds]):
                rows.extend(rr)
            rows.sort(key=lambda r: (r["world_seed"], r["speed"], r["level"]))
            oracle[null] = {"rhos": rhos, "tuning": tuning, "rows": rows, "summary": oracle_summary(rows)}
            for key, sm in oracle[null]["summary"].items():
                log(f"    null {null} {key}: mean VAL SR {sm['mean_val_sharpe']:.3f}  power " +
                    "  ".join(f"p<={t}: {sm['by_threshold'][str(t)]['tier1']}/{sm['n']}" for t in C.G6_GRID))

    problems = design_problems({"protocol": {"worlds_per_null": a.worlds, "oracle_worlds": a.oracle_worlds,
                                             "seeds": SEEDS}, "nulls": nulls, "oracle": oracle},
                               SEEDS, FAMILIES, SPEEDS, LEVELS)             # R-R (d), before the rule
    verdict = design_stop("core", problems) if problems else decide(nulls, oracle)
    out = {"protocol_version": PROTOCOL_VERSION, "kernel_hash": kh, "semantic_hash": sem, "text_hash": k["text"],
           "kernel_lock_verified": lock_ok and not synthetic, "synthetic_dry_run": synthetic,
           "research_hash": rh,
           "created_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "families": {f: ledger.sha256_file(family_path(f)) for f in fams},
           "protocol": protocol_header(a.worlds, a.oracle_worlds),       # R-R (e): compared by the seal
           "nulls": nulls, "oracle": oracle, "verdict": verdict, "wall_seconds": round(time.time() - t0, 1)}
    if a.out:
        path = Path(a.out)
    else:
        path = P.LEDGER_DIR / f"calibration_{sem[:16]}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(ledger.clean(out), indent=1, sort_keys=True), encoding="ascii")
    log(f"saved {path}")
    if not a.out:                                      # M2: the artifact's bytes are logged; seal needs the row
        row = kernel_lock.log_calibration(path, sem, rh)
        log(f"logged in ledger/calibration_log.jsonl: sha256 {row['sha256'][:16]}")
    log(json.dumps(ledger.clean(verdict), indent=1))
    log(f"wall time {out['wall_seconds']} s")


if __name__ == "__main__":
    main()
