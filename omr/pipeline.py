"""Evaluation pipeline for .omr programs. Kernel module.

No strategy code exists or runs: signals come from the kernel's interpreter (omr.interp) over a
checked program (omr.lang). All comparisons, metrics and gates are computed here.

stage1(...)  DEV-only frames, uncounted: signals; the truncation self-check (end cuts) and the
             start-cut self-check (rows removed from the start of every frame): a mismatch is a
             kernel fault (every function is causal and local by construction); activity_dev.
stage2(...)  DEV+VAL frames, counted, needs a ValHandle: recompute; DEV rows (values and known) must
             equal stage 1 and start cuts must agree (else kernel_fault); engine; liquidation;
             metrics; gates G1-G8 and G10.
evaluate_weights(...)  calibration only: gates for injected weights (noisy oracles).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from omr import access
from omr import constants as C
from omr import engine as E
from omr import interp as X
from omr import lang as L
from omr import stats as S


def T(s: str) -> pd.Timestamp:
    return pd.Timestamp(s, tz="UTC").as_unit("ns")


class KernelFault(Exception):
    """An internal invariant of the kernel failed (never a property of the program)."""


@dataclass
class World:
    """core / extended: {symbol: frame}; btc: the BTCUSDT frame used by btc(field);
    liq: {symbol: DataFrame(dn, up, has_mark)} (mark-price liquidation ratios)."""
    core: dict
    extended: dict = field(default_factory=dict)
    btc: pd.DataFrame | None = None
    liq: dict = field(default_factory=dict)
    symbols: tuple = C.CORE


@dataclass
class Opts:
    perm_n: int = C.PERM_N                          # the core unit's G6 (circular shifts)
    u_lags: int = C.UNIVERSE_G6_LAGS                # the top30 unit's G6 (R-N, fix pass 9): equally spaced lags
    jitter_n: int = C.JITTER_N
    include_g8: bool = True
    keep_detail: bool = True
    truncation_cuts: int = C.TRUNCATION_CUTS
    start_cuts: int = C.START_CUTS_DEV
    start_cuts_val: int = C.START_CUTS_VAL


# ---------------------------------------------------------------- market

def liq_ratios(frame: pd.DataFrame, liq, grid: pd.DatetimeIndex):
    f = frame.reindex(grid)
    o = f["open"].to_numpy(dtype=np.float64)
    dn = f["low"].to_numpy(dtype=np.float64) / o
    up = f["high"].to_numpy(dtype=np.float64) / o
    if liq is not None:
        lq = liq.reindex(grid)
        has = lq["dn"].notna().to_numpy() & lq["up"].notna().to_numpy()
        dn = np.where(has, lq["dn"].to_numpy(dtype=np.float64), dn)
        up = np.where(has, lq["up"].to_numpy(dtype=np.float64), up)
    return dn, up


class Market:
    """Aligned price arrays for `symbols` on `grid` (no region requirement)."""

    def __init__(self, frames: dict, liq: dict, grid: pd.DatetimeIndex, symbols):
        syms = list(symbols)
        self.grid = grid
        self.op = np.column_stack([frames[s]["open"].reindex(grid).to_numpy(dtype=np.float64) for s in syms])
        r = [liq_ratios(frames[s], liq.get(s), grid) for s in syms]
        self.dn = np.column_stack([x[0] for x in r])
        self.up = np.column_stack([x[1] for x in r])
        self.fr = np.column_stack([frames[s]["funding_rate"].reindex(grid).to_numpy(dtype=np.float64) for s in syms])

    def pos(self, s: str):
        t = T(s)
        return int(self.grid.get_loc(t)) if t in self.grid else None

    def run(self, Wn: np.ndarray, s: int, e: int, cost_mult=1.0, pay=1.0, recv=1.0) -> E.Run:
        """Run over grid positions s..e (s >= 1). Target at position j = decision at j-1."""
        return E.run(self.grid[s:e + 1], self.op[s:e + 1], self.dn[s:e + 1], self.up[s:e + 1], self.fr[s:e + 1],
                     Wn[s - 1:e], cost_rate=C.COST_RATE * cost_mult, pay_mult=pay, recv_mult=recv)


def core_grid(frames: dict, symbols) -> pd.DatetimeIndex:
    idx = None
    for s in symbols:
        i = pd.DatetimeIndex(frames[s].index).as_unit("ns")
        idx = i if idx is None else idx.intersection(i)
    return idx


# ---------------------------------------------------------------- signals

def _cut(df, upto, start):
    if df is None:
        return None
    if upto is not None:
        df = df.loc[:upto]
    if start is not None:
        df = df.loc[start:]
    return df


def unit_full(prog: L.Program, params: dict, frames: dict, symbols, btc, grid: pd.DatetimeIndex,
              upto: pd.Timestamp | None = None, literals=None, start: pd.Timestamp | None = None):
    """(weights, raw, known) on grid[start:upto]. single: each symbol evaluated alone on its own
    history; portfolio: one panel on the grid. Every frame (BTC included) is cut to [start, upto].
    raw is NaN wherever not known; weights are 0 there and valid by construction.
    literals: jittered literal values (G5 variants); None = as written."""
    symbols = list(symbols)
    g = grid
    if upto is not None:
        g = g[g <= upto]
    if start is not None:
        g = g[g >= start]
    b = _cut(btc, upto, start)
    if prog.kind == "single":
        raws, kns = [], []
        for s in symbols:
            f = _cut(frames[s], upto, start)
            r, k = X.evaluate_full(prog, params, [f], b, literals)
            ix = pd.DatetimeIndex(f.index).as_unit("ns")
            raws.append(pd.Series(r[:, 0], index=ix).reindex(g).to_numpy())
            kns.append(pd.Series(k[:, 0], index=ix).reindex(g, fill_value=False).to_numpy(dtype=bool))
        raw, kn = np.column_stack(raws), np.column_stack(kns)
    else:
        panel = [frames[s].reindex(g) for s in symbols]
        raw, kn = X.evaluate_full(prog, params, panel, b, literals)
    return X.weights(prog, raw, len(symbols)), raw, kn


def unit_signals(prog: L.Program, params: dict, frames: dict, symbols, btc, grid: pd.DatetimeIndex,
                 upto: pd.Timestamp | None = None, literals=None):
    """(weights, raw) on grid[:upto]; see unit_full."""
    W, raw, _ = unit_full(prog, params, frames, symbols, btc, grid, upto=upto, literals=literals)
    return W, raw


def start_cut_agrees(raw_cut, kn_cut, raw_base, kn_base) -> bool:
    """Wherever the cut run is known, the base run must be known and bit-identical."""
    if raw_cut.shape != raw_base.shape:
        return False
    if not bool(np.all(kn_base[kn_cut])):
        return False
    return bool(np.array_equal(raw_cut[kn_cut], raw_base[kn_cut], equal_nan=True))


def start_cut_check(prog, params, frames, symbols, btc, grid, raw, kn, rng, n_cuts: int, span: float):
    """None if every start cut agrees, else the failing cut position."""
    hi = int(span * len(grid))
    if hi < 2 or n_cuts <= 0:
        return None
    for c in sorted(rng.choice(np.arange(1, hi), size=min(n_cuts, hi - 1), replace=False).tolist()):
        _, rc, kc = unit_full(prog, params, frames, symbols, btc, grid, start=grid[c])
        if not start_cut_agrees(rc, kc, raw[c:], kn[c:]):
            return c
    return None


def direction_changes(W: np.ndarray, lo: int, hi: int) -> int:
    """Per symbol: state = sign(w) where |w| > DIRECTION_TOL else 0; count decision rows lo..hi whose
    state differs from the previous row; sum over symbols."""
    st = np.where(np.abs(W) > C.DIRECTION_TOL, np.sign(W), 0.0)
    if lo < 1:
        raise KernelFault("direction_changes needs a row before lo")
    return int(np.sum(st[lo:hi + 1] != st[lo - 1:hi]))


def same_rows(a: np.ndarray, b: np.ndarray) -> bool:
    return a.shape == b.shape and bool(np.array_equal(a, b, equal_nan=True))


# ---------------------------------------------------------------- stage 1

def stage1(prog: L.Program, params: dict, frames_dev: dict, btc_dev, rng, opts: Opts = Opts(),
           symbols=C.CORE) -> dict:
    grid = core_grid(frames_dev, symbols)
    if grid[-1] != T(C.DEV_END):
        raise KernelFault("stage 1 frames must end at DEV end")
    W, raw, kn = unit_full(prog, params, frames_dev, symbols, btc_dev, grid)
    dev_s = int(grid.get_loc(T(C.DEV_START)))
    dev_e = len(grid) - 1
    pool = np.arange(dev_s - 1, dev_e)
    cuts = sorted(set(rng.choice(pool, size=min(opts.truncation_cuts, len(pool)), replace=False).tolist()) | {dev_e})
    for c in cuts:
        _, rt, kt = unit_full(prog, params, frames_dev, symbols, btc_dev, grid, upto=grid[c])
        if not (same_rows(rt, raw[:c + 1]) and np.array_equal(kt, kn[:c + 1])):
            return {"ok": False, "code": "kernel_fault", "fault": "truncation", "cuts": len(cuts)}
    bad = start_cut_check(prog, params, frames_dev, symbols, btc_dev, grid, raw, kn, rng, opts.start_cuts,
                          C.START_CUT_SPAN)
    if bad is not None:
        return {"ok": False, "code": "kernel_fault", "fault": "start_cut", "cuts": len(cuts)}
    n_dev = direction_changes(W, dev_s - 1, dev_e - 1)
    out = {"ok": n_dev >= C.MIN_DIRECTION_CHANGES_DEV, "code": None if n_dev >= C.MIN_DIRECTION_CHANGES_DEV else "activity_dev",
           "cuts": len(cuts), "start_cuts": opts.start_cuts, "direction_changes_dev": n_dev, "grid": grid, "W": W,
           "raw": raw, "known": kn}
    return out


def screen_dev(prog: L.Program, params: dict, frames_dev: dict, btc_dev, symbols=C.CORE) -> dict:
    """Calibration screening only: DEV signals and the activity rule, no self-checks."""
    grid = core_grid(frames_dev, symbols)
    W, raw, kn = unit_full(prog, params, frames_dev, symbols, btc_dev, grid)
    dev_s = int(grid.get_loc(T(C.DEV_START)))
    n_dev = direction_changes(W, dev_s - 1, len(grid) - 2)
    return {"ok": n_dev >= C.MIN_DIRECTION_CHANGES_DEV, "code": None if n_dev >= C.MIN_DIRECTION_CHANGES_DEV
            else "activity_dev", "direction_changes_dev": n_dev, "grid": grid, "W": W}


# ---------------------------------------------------------------- stage 2

def split_daily(daily: pd.Series):
    dev = daily[(daily.index >= T(C.DEV_START)) & (daily.index <= T(C.DEV_END))]
    val = daily[(daily.index >= T(C.VAL_START)) & (daily.index <= T(C.VAL_END))]
    return dev, val


def val_sharpe_of(run: E.Run) -> float:
    if run.liquidated:
        return float("-inf")
    return S.sharpe(split_daily(run.daily_returns())[1])


def jitter_params(prog: L.Program, base: dict, rng, n: int) -> list:
    """n G5 variants, each (params, literal values). Every param x U(0.8, 1.2) (ints rounded and,
    if rounding leaves the value unchanged, moved by 1 with a random sign; clipped to the declared
    bounds); then every jitterable literal token (all body literals except 0; window arguments are
    not literals here) x its own U(0.8, 1.2). Draw order from the one generator: params in
    declaration order, then literals in source order."""
    out = []
    for _ in range(n):
        q = {}
        for k, p in prog.params.items():
            d = base[k]
            v = d * rng.uniform(C.JITTER_LO, C.JITTER_HI)
            if p.is_int:
                v = int(math.floor(v + 0.5))
                if v == d:
                    v = d + (1 if rng.uniform() < 0.5 else -1)
            v = min(max(v, p.low), p.high)
            q[k] = int(v) if p.is_int else float(v)
        lits = tuple(float(v * rng.uniform(C.JITTER_LO, C.JITTER_HI)) for _, v in prog.literals)
        out.append((q, lits))
    return out


def g5_vacuous(prog: L.Program) -> bool:
    return not prog.params and not prog.literals


def perm_offsets(L_: int, rng, n: int) -> np.ndarray:
    lo = C.PERM_MIN_OFFSET_DAYS * 24
    hi = L_ - C.PERM_MIN_OFFSET_DAYS * 24
    if hi < lo:
        raise KernelFault("VAL too short for the permutation test")
    return rng.integers(lo, hi + 1, size=n)


def g5_rule(base_val: float, variant_sharpes) -> dict:
    shs = np.asarray(variant_sharpes, dtype=np.float64)
    med = float(np.median(shs))
    frac = float(np.mean(shs > 0))
    return {"pass": bool(med >= C.JITTER_MEDIAN_FRAC * base_val and frac >= C.JITTER_POSITIVE_FRAC),
            "median": med, "frac_positive": frac}


def g6_p(actual: float, shifted) -> float:
    shifted = np.asarray(shifted, dtype=np.float64)
    return (1 + int(np.sum(shifted >= actual))) / (len(shifted) + 1)


def g7_rule(bucket_returns) -> dict:
    lr = [math.log1p(R) if R > -1 else float("-inf") for R in bucket_returns]
    n_pos = sum(1 for R in bucket_returns if R > 0)
    pos_sum = sum(x for x in lr if x > 0)
    largest = max(lr) if lr else float("-inf")
    share = largest / pos_sum if pos_sum > 0 else None          # undefined without a positive bucket (G7 fails)
    return {"pass": bool(n_pos >= C.G7_MIN_POSITIVE and pos_sum > 0 and largest <= C.G7_MAX_SHARE * pos_sum),
            "n_positive": n_pos, "largest_share": share}


def g8_rule(unit_rows: list) -> dict:
    """Units that could not be scored count as NOT positive."""
    shs = np.array([r["sharpe"] if r.get("code") is None else -np.inf for r in unit_rows], dtype=np.float64)
    if len(shs) == 0:
        return {"pass": False, "median": None, "frac_positive": None, "n": 0}
    med = float(np.median(shs))
    frac = float(np.mean(shs > 0))
    return {"pass": bool(med > 0 and frac >= 0.5), "median": med, "frac_positive": frac, "n": int(len(shs))}


def g10_rule(n_val: int) -> dict:
    return {"pass": bool(n_val >= C.G10_MIN_DIRECTION_CHANGES_VAL), "value": int(n_val)}


def g8_units(prog: L.Program, world: World) -> list:
    ext = list(world.extended)
    if prog.kind == "single":
        return [(s,) for s in ext]
    k = len(world.symbols)
    return [tuple(ext[i:i + k]) for i in range(0, len(ext) - k + 1, k)]


def g8_scores(prog: L.Program, params: dict, world: World, end: str = C.VAL_END,
              min_years: float = C.G8_MIN_YEARS) -> list:
    """G8 units: each scored from its own first bar (signals from its own history, so its own
    warm-up is flat), DEV start at the earliest, to `end`. btc(...) stays the real BTC frame.
    A unit with less than min_years of scored history or liquidated gets a named code (counts as
    not positive in g8_rule). No exception is caught here."""
    rows = []
    for unit in g8_units(prog, world):
        grid = core_grid(world.extended, unit)
        grid = grid[grid <= T(end)]
        start = max(T(C.DEV_START), grid[1])
        si = int(np.searchsorted(grid.asi8, start.value))
        ei = int(grid.get_loc(T(end)))
        name = "+".join(unit)
        years = (T(end) - grid[si]) / pd.Timedelta(days=365)
        if years < min_years:
            rows.append({"unit": name, "code": "short_history", "years": round(float(years), 2)})
            continue
        W, _ = unit_signals(prog, params, world.extended, unit, world.btc, grid)
        mk = Market(world.extended, world.liq, grid, unit)
        run = mk.run(W, si, ei)
        if run.liquidated:
            rows.append({"unit": name, "code": "liquidated"})
            continue
        rows.append({"unit": name, "code": None, "sharpe": S.sharpe(run.daily_returns()),
                     "years": round(float(years), 2)})
    return rows


def stage2(prog: L.Program, params: dict, world: World, s1: dict | None, opts: Opts, handle, seed: int,
           p_max: float | None) -> dict:
    """COUNTED. Raises on unexpected errors (the evaluator turns that into a kernel_fault row)."""
    access.require(handle, "pipeline.stage2")
    syms = list(world.symbols)
    grid = core_grid(world.core, syms)
    grid = grid[grid <= T(C.VAL_END)]
    W, raw, kn = unit_full(prog, params, world.core, syms, world.btc, grid)
    if s1 is not None:
        n = len(s1["grid"])
        if not s1["grid"].equals(grid[:n]) or not same_rows(raw[:n], s1["raw"]) or \
                not np.array_equal(kn[:n], s1["known"]):
            return {"status": "kernel_fault", "reason": "dev_rows_changed"}
    if opts.start_cuts_val > 0:
        bad = start_cut_check(prog, params, world.core, syms, world.btc, grid, raw, kn,
                              np.random.default_rng([seed, 4]), opts.start_cuts_val, C.START_CUT_SPAN_VAL)
        if bad is not None:
            return {"status": "kernel_fault", "reason": "start_cut"}
    mk = Market(world.core, world.liq, grid, syms)
    rng = np.random.default_rng([seed, 2])
    variants = [] if g5_vacuous(prog) else jitter_params(prog, params, rng, opts.jitter_n)
    jit_W = [unit_signals(prog, q, world.core, syms, world.btc, grid, literals=lv)[0] for q, lv in variants]
    if opts.include_g8 and not world.extended:
        raise KernelFault("G8 requested but the world has no extended universe")
    g8 = g8_scores(prog, params, world) if opts.include_g8 else None
    return gates(W, world, mk, np.random.default_rng([seed, 3]), opts, p_max, variants=variants, jit_W=jit_W,
                 g8=g8, n_params=len(prog.params))


def evaluate_weights(W: np.ndarray, grid: pd.DatetimeIndex, world: World, seed: int, opts: Opts, handle,
                     p_max: float | None) -> dict:
    """CALIBRATION ONLY: gates for injected weights (noisy oracles). G5 passes by definition (no
    params); G8 is not run."""
    access.require(handle, "pipeline.evaluate_weights")
    mk = Market(world.core, world.liq, grid, list(world.symbols))
    return gates(W, world, mk, np.random.default_rng([seed, 3]), opts, p_max, variants=[], jit_W=[], g8=None,
                 n_params=0)


def gates(W, world, mk: Market, rng_perm, opts: Opts, p_max, variants, jit_W, g8, n_params) -> dict:
    K = W.shape[1]
    dev_s, val_s, val_e = mk.pos(C.DEV_START), mk.pos(C.VAL_START), mk.pos(C.VAL_END)
    base = mk.run(W, dev_s, val_e)
    if base.liquidated:
        return {"status": "liquidated", "reason": "liquidation"}
    daily = base.daily_returns()
    dev, val = split_daily(daily)
    m = {"dev": S.summary(dev), "val": S.summary(val)}
    m["dev_val_max_drawdown"] = S.max_drawdown(daily)
    m["deploy_scale"] = min(1.0, C.DEPLOY_RISK_BUDGET / m["dev_val_max_drawdown"]) if m["dev_val_max_drawdown"] > 0 else 1.0
    n_years = len(daily) / C.PERIODS_PER_YEAR
    m["turnover_per_year"] = float(base.ev_turn.sum() / n_years) if n_years > 0 else 0.0
    m["avg_gross_exposure"] = float(base.gross.mean())
    m["avg_net_exposure"] = float(base.net.mean())
    m["rebalances"] = int(len(base.ev_idx))
    m["direction_changes_dev"] = direction_changes(W, dev_s - 1, mk.pos(C.DEV_END) - 1)
    m["direction_changes_val"] = direction_changes(W, val_s - 1, val_e - 1)
    m["funding_paid_total"] = float(base.funding_paid)
    m["costs_total"] = float(base.ev_cost.sum())
    m["val_sharpe_daily"] = S.sharpe_daily(val)
    m["n_daily"] = int(len(daily))
    g = {}
    g["G1"] = {"pass": bool(m["val"]["psr0"] >= C.G1_PSR_MIN), "value": m["val"]["psr0"]}
    fs_sh = val_sharpe_of(mk.run(W, dev_s, val_e, pay=C.FUNDING_STRESS_PAY, recv=C.FUNDING_STRESS_RECV))
    g["G2"] = {"pass": bool(fs_sh > 0), "value": fs_sh}
    g["G3"] = {"pass": bool(m["dev"]["sharpe"] > 0), "value": m["dev"]["sharpe"]}
    cs_sh = val_sharpe_of(mk.run(W, dev_s, val_e, cost_mult=C.COST_STRESS_MULT))
    g["G4"] = {"pass": bool(cs_sh > 0), "value": cs_sh}
    if variants:
        shs = [val_sharpe_of(mk.run(Wv, dev_s, val_e)) for Wv in jit_W]
        r5 = g5_rule(m["val"]["sharpe"], shs)
        g["G5"] = {"pass": r5["pass"], "value": {"n": len(shs), "median": r5["median"], "frac_positive": r5["frac_positive"]},
                   "g5_vacuous": False}
    else:
        g["G5"] = {"pass": True, "value": None, "g5_vacuous": True}
    L_ = val_e - val_s + 1
    Wv0 = W[val_s - 1: val_e].copy()
    vgrid = mk.grid[val_s: val_e + 1]
    sl = slice(val_s, val_e + 1)
    args = (mk.op[sl], mk.dn[sl], mk.up[sl], mk.fr[sl])

    def vrun(tgt):
        out = E.run_arrays(*args, tgt)
        if out[7] >= 0:
            return float("-inf")
        return S.sharpe(E.daily_returns(out[8], out[0], vgrid).to_numpy())

    actual = vrun(Wv0)
    offs = perm_offsets(L_, rng_perm, opts.perm_n)
    shifted = np.array([vrun(np.roll(Wv0, int(k), axis=0)) for k in offs])
    p = g6_p(actual, shifted)
    g["G6"] = {"pass": (bool(p <= p_max + 1e-12) if p_max is not None else None), "value": p, "threshold": p_max}
    buckets = []
    for name, a, b in C.G7_BUCKETS:
        r = daily[(daily.index >= T(a).normalize()) & (daily.index <= T(b))]
        buckets.append({"bucket": name, "n_days": int(len(r)), "return": S.total_return(r)})
    r7 = g7_rule([x["return"] for x in buckets])
    g["G7"] = {"pass": r7["pass"], "value": {"n_positive": r7["n_positive"], "largest_share": r7["largest_share"]}}
    if g8 is None:
        g["G8"] = {"pass": None, "value": "not run", "not_run": True}
    else:
        r8 = g8_rule(g8)
        g["G8"] = {"pass": r8["pass"], "value": {"median": r8["median"], "frac_positive": r8["frac_positive"], "n": r8["n"]}}
    r10 = g10_rule(m["direction_changes_val"])
    g["G10"] = {"pass": r10["pass"], "value": r10["value"]}
    decided = [v["pass"] for v in g.values() if v["pass"] is not None]
    tier1 = all(decided) and g["G6"]["pass"] is not None and g["G8"]["pass"] is not None
    Wb = np.full_like(W, 1.0 / K)
    bdaily = mk.run(Wb, dev_s, val_e).daily_returns()
    bdev, bval = split_daily(bdaily)
    info = {"benchmark_val_sharpe": S.sharpe(bval), "benchmark_val_max_drawdown": S.max_drawdown(bval),
            "benchmark_dev_sharpe": S.sharpe(bdev)}
    info.update({f"vs_benchmark_{k}": v for k, v in S.beta_alpha(val.to_numpy(), bval.reindex(val.index).to_numpy()).items()})
    res = {"status": "evaluated", "metrics": m, "gates": g, "tier": "tier1" if tier1 else "none", "info": info,
           "daily_returns": daily, "n_params": n_params}
    if opts.keep_detail:
        fin = shifted[np.isfinite(shifted)]
        res["detail"] = {"permutation": {"actual_val_sharpe_restarted": actual, "n": int(len(offs)), "p": p,
                                         "shifted_mean": float(np.mean(fin)) if len(fin) else None,
                                         "shifted_p95": float(np.percentile(fin, 95)) if len(fin) else None},
                         "per_year": dev_only_years(S.per_year(daily)), "buckets": dev_only_buckets(buckets),
                         "extended": g8, "stress": {"funding_stress_val_sharpe": fs_sh, "cost2x_val_sharpe": cs_sh}}
    return res


def dev_only_years(rows: list) -> list:
    """No time-resolved VAL performance is stored: only calendar years ending by DEV end."""
    end = T(C.DEV_END)
    return [r for r in rows if T(f"{r['year']}-12-31 23:00") <= end]


def dev_only_buckets(buckets: list) -> list:
    """G7 buckets: the return only for buckets ending by DEV end; name and n_days for later ones."""
    end = T(C.DEV_END)
    ends = {name: T(b) for name, _, b in C.G7_BUCKETS}
    return [x if ends[x["bucket"]] <= end else {"bucket": x["bucket"], "n_days": x["n_days"]} for x in buckets]


# The calibration's gates (omr.calibrate.GATES refers to this tuple); every one but G6 must be stored for an
# evaluated calibration row
TIER_GATES = ("G1", "G2", "G3", "G4", "G5", "G6", "G7", "G10")


def _is_bool(v) -> bool:
    return isinstance(v, (bool, np.bool_))


def tier_at(row: dict, p_max: float) -> bool:
    """Tier 1 re-read at G6 threshold p_max from a stored calibration row (the one implementation; omr.calibrate
    refers to it). A row whose status is not "evaluated" is not Tier 1. An evaluated row must be well formed,
    otherwise ValueError (fix pass 8, FP8-2): "gates" a mapping holding every gate of TIER_GATES but G6 with a
    boolean (Python or numpy); G6 and G8 may be None or absent (G6 is re-read from perm_p and its stored value is
    ignored; G8 is not run in calibration); a G8 or any other gate that is present and not None must be a boolean
    and counts; perm_p a finite number in [0, 1] (not a bool). Why it raises instead of reading the row as "not
    passing": that reading is the LOOSE direction for a null row (it lowers the null pass rate) and the strict one
    for an oracle row (it lowers the power), so no silent reading is safe in both; the unit verdict turns the
    ValueError into the "malformed" STOP."""
    if row.get("status") != "evaluated":
        return False
    who = f"world_seed {row.get('world_seed')!r}, " + (f"family {row.get('family')!r}" if "family" in row
                                                         else f"speed {row.get('speed')!r}")
    gates = row.get("gates")
    if not isinstance(gates, dict):
        raise ValueError(f"evaluated calibration row ({who}): gates is not a mapping ({type(gates).__name__})")
    ok = True
    for g in TIER_GATES:
        if g == "G6":
            continue
        if g not in gates:
            raise ValueError(f"evaluated calibration row ({who}): gate {g} is missing")
        if not _is_bool(gates[g]):
            raise ValueError(f"evaluated calibration row ({who}): gate {g} is not a boolean ({gates[g]!r})")
        ok = ok and bool(gates[g])
    for g, v in gates.items():
        if g in TIER_GATES and g != "G6" or v is None:
            continue
        if not _is_bool(v):
            raise ValueError(f"evaluated calibration row ({who}): gate {g} is not a boolean ({v!r})")
        if g != "G6":
            ok = ok and bool(v)
    p = row.get("perm_p")
    if isinstance(p, (bool, np.bool_)) or not isinstance(p, (int, float, np.integer, np.floating)) or \
            not math.isfinite(float(p)) or not (0.0 <= float(p) <= 1.0):
        raise ValueError(f"evaluated calibration row ({who}): perm_p is not a finite number in [0, 1] ({p!r})")
    return ok and float(p) <= p_max + 1e-12
