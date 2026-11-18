"""Performance statistics on DAILY net returns. Kernel module.

Conventions: 365-day annualisation, risk-free 0.
- sharpe: mean / std(ddof=1) * sqrt(365); 0.0 when std == 0 or n < 2.
- skewness g3 = m3 / m2^1.5 and Pearson kurtosis g4 = m4 / m2^2 (normal = 3), with
  m_k the biased central moments (mean of (x - mean)^k).
- PSR(SR*) = Phi((SR - SR*) * sqrt(n-1) / sqrt(1 - g3*SR + (g4-1)/4 * SR^2)), SR per day.
  Returns 0.0 when std == 0 or the denominator is not positive (no evidence).
- DSR = PSR(SR0), SR0 = max(0, sqrt(V) * ((1-g)*PhiInv(1-1/N) + g*PhiInv(1-1/(N*e)))),
  SR0 = 0 when N <= 1.
- max drawdown: positive fraction, on the daily equity path cumprod(1+r) starting from 1.0.
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd
from scipy.stats import norm

from omr import constants as C

ANN = C.PERIODS_PER_YEAR


def _arr(r) -> np.ndarray:
    return np.asarray(r, dtype=np.float64)


SD_TOL = 1e-12   # a standard deviation below this is treated as zero (no evidence)


def sharpe_daily(r) -> float:
    x = _arr(r)
    if len(x) < 2 or not np.all(np.isfinite(x)):
        return 0.0
    sd = x.std(ddof=1)
    if not np.isfinite(sd) or sd < SD_TOL:
        return 0.0
    return float(x.mean() / sd)


def sharpe(r) -> float:
    return sharpe_daily(r) * math.sqrt(ANN)


def moments(r):
    x = _arr(r)
    d = x - x.mean()
    m2 = float(np.mean(d ** 2))
    if m2 == 0.0:
        return 0.0, 3.0
    g3 = float(np.mean(d ** 3) / m2 ** 1.5)
    g4 = float(np.mean(d ** 4) / m2 ** 2)
    return g3, g4


def psr_from(sr: float, n: int, g3: float, g4: float, sr_star: float = 0.0) -> float:
    if n < 2:
        return 0.0
    den = 1.0 - g3 * sr + ((g4 - 1.0) / 4.0) * sr * sr
    if not np.isfinite(den) or den <= 0.0:
        return 0.0
    z = (sr - sr_star) * math.sqrt(n - 1) / math.sqrt(den)
    return float(norm.cdf(z))


def psr(r, sr_star: float = 0.0) -> float:
    x = _arr(r)
    if len(x) < 2 or not np.all(np.isfinite(x)) or not x.std(ddof=1) >= SD_TOL:
        return 0.0
    g3, g4 = moments(x)
    return psr_from(sharpe_daily(x), len(x), g3, g4, sr_star)


def sr0(V: float, N: float) -> float:
    """Expected maximum per-day Sharpe under the null across N effective trials."""
    if N <= 1.0:
        return 0.0
    g = C.EULER_GAMMA
    val = math.sqrt(V) * ((1 - g) * norm.ppf(1 - 1.0 / N) + g * norm.ppf(1 - 1.0 / (N * math.e)))
    return max(0.0, float(val))


def effective_n(M: int, rho: float) -> float:
    rho = min(1.0, max(0.0, rho))
    return rho + (1.0 - rho) * M


def mean_pairwise_corr(frame: pd.DataFrame) -> float:
    """Mean of the off-diagonal pairwise correlations (NaN pairs dropped), clipped to [0, 1].
    0.0 when fewer than two series."""
    if frame.shape[1] < 2:
        return 0.0
    c = frame.corr().to_numpy()
    iu = np.triu_indices_from(c, k=1)
    v = c[iu]
    v = v[np.isfinite(v)]
    if len(v) == 0:
        return 0.0
    return float(min(1.0, max(0.0, v.mean())))


def dsr(r, val_sharpes_daily, rho: float, M: int) -> dict:
    """Deflated Sharpe of daily returns r given the per-day VAL Sharpes of all counted trials
    (including this one), their mean pairwise correlation rho and the count M."""
    x = _arr(r)
    n = len(x)
    s = _arr(val_sharpes_daily)
    V = float(np.var(s, ddof=1)) if len(s) >= 2 else 0.0
    floor = 1.0 / (n - 1) if n > 1 else 1.0
    V = max(V if np.isfinite(V) else 0.0, floor)
    N = effective_n(M, rho)
    s0 = sr0(V, N)
    return {"dsr": psr(x, s0), "sr0_daily": s0, "V": V, "N": N, "M": int(M), "rho": float(rho)}


def max_drawdown(r) -> float:
    x = _arr(r)
    if len(x) == 0:
        return 0.0
    eq = np.r_[1.0, np.cumprod(1.0 + x)]
    peak = np.maximum.accumulate(eq)
    with np.errstate(divide="ignore", invalid="ignore"):
        dd = np.where(peak > 0, eq / peak - 1.0, -1.0)
    return float(-dd.min())


def total_return(r) -> float:
    x = _arr(r)
    return float(np.prod(1.0 + x) - 1.0) if len(x) else 0.0


def cagr(r) -> float:
    x = _arr(r)
    if len(x) == 0:
        return 0.0
    g = np.prod(1.0 + x)
    if g <= 0:
        return -1.0
    return float(g ** (ANN / len(x)) - 1.0)


def calmar(r) -> float:
    mdd = max_drawdown(r)
    return float(cagr(r) / mdd) if mdd > 0 else float("nan")


def beta_alpha(rs, rb) -> dict:
    """OLS beta of strategy daily returns on benchmark daily returns, annualised alpha
    (mean residual * 365), and PSR(0) of the beta-hedged residual."""
    s, b = _arr(rs), _arr(rb)
    vb = np.var(b, ddof=1) if len(b) > 1 else 0.0
    beta = float(np.cov(s, b, ddof=1)[0, 1] / vb) if vb > 0 else 0.0
    resid = s - beta * b
    return {"beta": beta, "alpha_ann": float(resid.mean() * ANN), "resid_psr0": psr(resid),
            "resid_sharpe": sharpe(resid)}


def summary(r) -> dict:
    x = _arr(r)
    g3, g4 = moments(x) if len(x) > 1 else (0.0, 3.0)
    return {"n_days": int(len(x)), "sharpe": sharpe(x), "psr0": psr(x), "total_return": total_return(x),
            "cagr": cagr(x), "max_drawdown": max_drawdown(x), "calmar": calmar(x),
            "skew": g3, "kurtosis": g4}


def per_year(daily: pd.Series) -> list:
    out = []
    for y, grp in daily.groupby(daily.index.year):
        out.append({"year": int(y), "n_days": int(len(grp)), "return": total_return(grp),
                    "sharpe": sharpe(grp), "max_drawdown": max_drawdown(grp)})
    return out
