"""Perpetual-futures backtest engine (signed weights, gross <= 1). Kernel module.

Conventions
- Bars are indexed by OPEN time. A target decided at the close of bar t is
  executed at the open of bar t+1. The caller passes `tgt`, already aligned so
  that tgt[j] is the target executed at timestamp j of the run.
- Weights are signed notional / equity. Each in [-1, 1], gross sum(|w|) <= 1.
  Validity is checked before the engine; the engine never clips.
- Holdings (signed notional) drift with open-to-open price ratios. Cash earns 0.
- Order at every timestamp j:
    1. mark to the open: h_i *= O[j,i] / O[j-1,i]; equity += PnL
    2. funding: equity -= sum_i h_i * rate[j,i]   (drifted position coming into j;
       rate[j,i] is the rate settled at that open, 0 when no settlement).
       Under funding stress, payments (h*rate > 0) are scaled by pay_mult and
       receipts (h*rate < 0) by recv_mult.
       pre[j] = equity after steps 1-2 (before any trade at j).
    3. rebalance: if any |tgt_i - h_i/equity| > band, trade ALL to target.
       notional = sum_i |tgt_i*equity - h_i|; cost = notional * cost_rate;
       equity -= cost; h = tgt * equity (post-cost).
    4. liquidation check for the bar that opens at j: worst intrabar equity
       = equity + sum_{h>0} h*(dn-1) + sum_{h<0} h*(up-1), where dn/up are the bar's
       adverse ratios relative to its open (the caller passes MARK low/open and
       high/open, falling back to last-price ratios where a bar has no mark data).
       If gross > 0 and worst <= liq_frac * gross (+1e-12 relative, so a drop to
       exactly 2.5% is flagged), the run is flagged liquidated (first index kept).
- equity[j] is the equity at timestamp j after steps 1-3. The run starts flat
  with equity 1.0. If equity reaches <= 0 the run is dead: equity 0 afterwards.

Daily returns: the equity is sampled at the 00:00 UTC opens BEFORE any trade there
(pre[j]); a run's first day starts exactly at its first bar (starting capital 1.0) and
its last day ends at the post-trade equity of its last bar (a run ending at 23:00 has a
23-hour last day).

A numba-compiled core is used (no on-disk cache); `run_reference` is an independent
pure-Python implementation (units formulation) used by the tests.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from omr import constants as C

try:  # numba is optional; the pure-Python core is identical code
    import numba
    HAVE_NUMBA = True
except Exception:  # pragma: no cover
    HAVE_NUMBA = False

LIQ_EPS = 1e-12


def _core_impl(op, dn, up, fr, tgt, cost_rate, band, pay_mult, recv_mult, liq_frac):
    T, K = op.shape
    equity = np.empty(T)
    pre = np.empty(T)
    gross = np.empty(T)
    net = np.empty(T)
    ev_idx = np.empty(T, np.int64)
    ev_turn = np.empty(T)
    ev_cost = np.empty(T)
    n_ev = 0
    h = np.zeros(K)
    eq = 1.0
    funding_paid = 0.0
    liq_idx = -1
    dead = False
    for t in range(T):
        if dead:
            equity[t] = 0.0
            pre[t] = 0.0
            gross[t] = 0.0
            net[t] = 0.0
            continue
        if t > 0:
            pnl = 0.0
            for i in range(K):
                if h[i] != 0.0:
                    nv = h[i] * (op[t, i] / op[t - 1, i])
                    pnl += nv - h[i]
                    h[i] = nv
            eq += pnl
        pay = 0.0
        for i in range(K):
            p = h[i] * fr[t, i]
            if p > 0.0:
                pay += p * pay_mult
            elif p < 0.0:
                pay += p * recv_mult
        eq -= pay
        funding_paid += pay
        if eq <= 0.0:
            dead = True
            if liq_idx < 0:
                liq_idx = t
            equity[t] = 0.0
            pre[t] = 0.0
            gross[t] = 0.0
            net[t] = 0.0
            continue
        pre[t] = eq
        trade = False
        for i in range(K):
            if abs(tgt[t, i] - h[i] / eq) > band:
                trade = True
                break
        if trade:
            notional = 0.0
            for i in range(K):
                notional += abs(tgt[t, i] * eq - h[i])
            cost = notional * cost_rate
            eq2 = eq - cost
            for i in range(K):
                h[i] = tgt[t, i] * eq2
            ev_idx[n_ev] = t
            ev_turn[n_ev] = notional / eq
            ev_cost[n_ev] = cost
            n_ev += 1
            eq = eq2
        g = 0.0
        n = 0.0
        worst = eq
        for i in range(K):
            g += abs(h[i])
            n += h[i]
            if h[i] > 0.0:
                worst += h[i] * (dn[t, i] - 1.0)
            elif h[i] < 0.0:
                worst += h[i] * (up[t, i] - 1.0)
        if g > 0.0 and worst <= liq_frac * g + 1e-12 * g and liq_idx < 0:
            liq_idx = t
        equity[t] = eq
        gross[t] = g / eq
        net[t] = n / eq
    return equity, gross, net, ev_idx[:n_ev], ev_turn[:n_ev], ev_cost[:n_ev], funding_paid, liq_idx, pre


if HAVE_NUMBA:
    _core_fast = numba.njit(cache=False, nogil=True)(_core_impl)
else:  # pragma: no cover
    _core_fast = _core_impl


@dataclass
class Run:
    index: pd.DatetimeIndex
    equity: np.ndarray
    gross: np.ndarray
    net: np.ndarray
    ev_idx: np.ndarray
    ev_turn: np.ndarray
    ev_cost: np.ndarray
    funding_paid: float
    liq_idx: int
    pre: np.ndarray

    @property
    def liquidated(self) -> bool:
        return self.liq_idx >= 0

    @property
    def n_rebalances(self) -> int:
        return int(len(self.ev_idx))

    def equity_series(self) -> pd.Series:
        return pd.Series(self.equity, index=self.index, name="equity")

    def daily_returns(self) -> pd.Series:
        return daily_returns(self.pre, self.equity, self.index)

    def events(self) -> pd.DataFrame:
        return pd.DataFrame({"turnover": self.ev_turn, "cost": self.ev_cost},
                            index=self.index[self.ev_idx])


def _as2d(a) -> np.ndarray:
    a = np.asarray(a, dtype=np.float64)
    return a.reshape(-1, 1) if a.ndim == 1 else np.ascontiguousarray(a)


def run_arrays(op, dn, up, fr, tgt, cost_rate=C.COST_RATE, band=C.REBALANCE_BAND,
               pay_mult=1.0, recv_mult=1.0, liq_frac=C.LIQUIDATION_FRAC, fast=True):
    """Run the engine on aligned arrays (T x K). dn/up = intrabar low/open and high/open
    ratios used only by the liquidation check. Returns the raw tuple of the core:
    (equity, gross, net, ev_idx, ev_turn, ev_cost, funding_paid, liq_idx, pre)."""
    op, dn, up, fr, tgt = (_as2d(x) for x in (op, dn, up, fr, tgt))
    if not (op.shape == dn.shape == up.shape == fr.shape == tgt.shape):
        raise ValueError("engine inputs must share one shape")
    if not np.all(np.isfinite(tgt)):
        raise ValueError("targets must be finite (NaN warm-up must be zeroed before the engine)")
    if not (np.all(np.isfinite(op)) and np.all(op > 0)):
        raise ValueError("open prices must be finite and > 0")
    if not np.all(np.isfinite(fr)):
        raise ValueError("funding rates must be finite")
    if not (np.all(np.isfinite(dn)) and np.all(np.isfinite(up)) and np.all(dn > 0) and np.all(up > 0)):
        raise ValueError("liquidation ratios must be finite and > 0")
    fn = _core_fast if fast else _core_impl
    return fn(op, dn, up, fr, tgt, float(cost_rate), float(band), float(pay_mult),
              float(recv_mult), float(liq_frac))


def run(index, op, dn, up, fr, tgt, **kw) -> Run:
    out = run_arrays(op, dn, up, fr, tgt, **kw)
    return Run(pd.DatetimeIndex(index), *out)


def day_points(index: pd.DatetimeIndex) -> np.ndarray:
    """Positions where a daily interval starts: the first bar of the run and every later 00:00 bar."""
    idx = pd.DatetimeIndex(index)
    pos = np.nonzero(idx.hour == 0)[0]
    pos = pos[pos > 0]
    return np.r_[0, pos].astype(np.int64)


def daily_returns(pre: np.ndarray, post: np.ndarray, index: pd.DatetimeIndex) -> pd.Series:
    """Daily returns sampled at 00:00 UTC opens (pre-trade equity), labelled by each interval's
    start date. First interval starts at the run's first bar with capital 1.0; the last interval
    ends at the post-trade equity of the last bar."""
    idx = pd.DatetimeIndex(index)
    pts = day_points(idx)
    vals = np.asarray(pre, dtype=np.float64)[pts].copy()
    vals[0] = 1.0
    ends = np.r_[vals[1:], float(np.asarray(post)[-1])]
    if pts[-1] == len(idx) - 1 and len(pts) > 1:
        # the run ends exactly at a 00:00 bar: fold that bar into the previous day
        pts, vals = pts[:-1], vals[:-1]
        ends = np.r_[vals[1:], float(np.asarray(post)[-1])]
    with np.errstate(divide="ignore", invalid="ignore"):
        r = np.where(vals > 0, ends / vals - 1.0, np.where(ends > 0, np.inf, 0.0))
    r = np.where(np.isfinite(r), r, -1.0)
    days = idx[pts].normalize()
    return pd.Series(r, index=days, name="ret")


def daily_complete_mask(index: pd.DatetimeIndex) -> np.ndarray:
    """For each daily interval of daily_returns: True when it ends at a 00:00 bar (a complete
    interval); the last interval of a run is not complete."""
    pts = day_points(pd.DatetimeIndex(index))
    if pts[-1] == len(index) - 1 and len(pts) > 1:
        pts = pts[:-1]
    m = np.ones(len(pts), dtype=bool)
    m[-1] = False
    return m


def run_reference(op, dn, up, fr, tgt, cost_rate=C.COST_RATE, band=C.REBALANCE_BAND,
                  pay_mult=1.0, recv_mult=1.0, liq_frac=C.LIQUIDATION_FRAC):
    """Independent pure-Python engine (holds UNITS and cash, not drifted notional).
    Dead equity (<= 0) is clamped to 0 for the rest of the run, as in the core.

    Returns (equity list, rebalance index list, liquidation index).
    """
    op, dn, up, fr, tgt = (_as2d(x).tolist() for x in (op, dn, up, fr, tgt))
    T, K = len(op), len(op[0])
    units = [0.0] * K
    cash = 1.0
    equity, events = [], []
    liq = -1
    dead = False
    for t in range(T):
        if dead:
            equity.append(0.0)
            continue
        P = op[t]
        values = [units[i] * P[i] for i in range(K)]
        pay = 0.0
        for i in range(K):
            p = values[i] * fr[t][i]
            pay += p * (pay_mult if p > 0 else recv_mult)
        cash -= pay
        eq = cash + sum(values)
        if eq <= 0:
            dead = True
            liq = t if liq < 0 else liq
            equity.append(0.0)
            continue
        if any(abs(tgt[t][i] - values[i] / eq) > band for i in range(K)):
            notional = sum(abs(tgt[t][i] * eq - values[i]) for i in range(K))
            eq_after = eq - notional * cost_rate
            units = [tgt[t][i] * eq_after / P[i] for i in range(K)]
            cash = eq_after - sum(units[i] * P[i] for i in range(K))
            events.append(t)
            eq = eq_after
        gross_val = sum(abs(units[i] * P[i]) for i in range(K))
        worst = eq
        for i in range(K):
            if units[i] > 0:
                worst += units[i] * P[i] * (dn[t][i] - 1.0)
            elif units[i] < 0:
                worst += units[i] * P[i] * (up[t][i] - 1.0)
        if gross_val > 0 and worst <= liq_frac * gross_val + LIQ_EPS * gross_val and liq < 0:
            liq = t
        equity.append(eq)
    return equity, events, liq
