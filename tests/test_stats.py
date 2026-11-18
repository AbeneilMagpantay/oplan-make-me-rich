"""Statistics tests against hand-computed values."""
import math

import numpy as np
import pandas as pd

from omr import stats as S


def alternating(n=100, m=0.001, d=0.01):
    return np.array([m + d if i % 2 == 0 else m - d for i in range(n)])


def test_sharpe_annualisation():
    r = alternating()
    # sample std = d * sqrt(n/(n-1)); per-day SR = 0.1 * sqrt(99/100)
    assert abs(S.sharpe_daily(r) - 0.1 * math.sqrt(0.99)) < 1e-12
    assert abs(S.sharpe(r) - 0.1 * math.sqrt(0.99) * math.sqrt(365)) < 1e-12


def test_psr_closed_form_two_point_series():
    # alternating m+d / m-d: g3 = 0, g4 = 1, so the denominator is 1 and z = SR*sqrt(n-1) = 0.99
    r = alternating()
    g3, g4 = S.moments(r)
    assert abs(g3) < 1e-9 and abs(g4 - 1.0) < 1e-9
    assert abs(S.psr(r) - 0.8389129404891691) < 1e-9


def test_psr_from_moments_hand_value():
    # den = 1 - (-1)(0.05) + (6-1)/4 * 0.05^2 = 1.053125 ; z = 0.05*sqrt(999)/sqrt(den) = 1.53997187
    assert abs(S.psr_from(0.05, 1000, -1.0, 6.0) - 0.9382163945108943) < 1e-12
    # a positive benchmark SR* lowers PSR
    assert S.psr_from(0.05, 1000, -1.0, 6.0, sr_star=0.03) < 0.9382163945108943


def test_sr0_and_effective_n_hand_values():
    # sqrt(V)=0.02; (1-g)*PhiInv(0.9) + g*PhiInv(1-1/(10e)) = 0.42278*1.28155 + 0.57722*1.78924
    assert abs(S.sr0(0.0004, 10.0) - 0.03149196602689944) < 1e-12
    assert abs(S.effective_n(10, 0.3) - 7.3) < 1e-12
    assert S.effective_n(10, 1.7) == 1.0      # rho clipped to 1
    assert S.effective_n(10, -0.5) == 10.0    # rho clipped to 0
    assert S.sr0(0.0004, 1.0) == 0.0
    assert S.sr0(0.0004, 0.5) == 0.0


def test_dsr_non_increasing_in_M():
    rng = np.random.default_rng(0)
    r = 0.002 + 0.02 * rng.standard_normal(1000)
    sh = [0.01, 0.03, 0.05, 0.02]
    vals = [S.dsr(r, sh, 0.2, M)["dsr"] for M in range(1, 60)]
    assert all(b <= a + 1e-15 for a, b in zip(vals, vals[1:]))
    assert vals[-1] < vals[0] - 0.05


def test_n_le_1_gives_psr0():
    rng = np.random.default_rng(1)
    r = 0.001 + 0.02 * rng.standard_normal(800)
    p0 = S.psr(r)
    assert abs(S.dsr(r, [0.05], 0.0, 1)["dsr"] - p0) < 1e-15        # M = 1 -> N = 1
    assert abs(S.dsr(r, [0.01, 0.09, 0.05], 1.0, 3)["dsr"] - p0) < 1e-15  # rho = 1 -> N = 1
    assert S.dsr(r, [0.01, 0.09, 0.05], 0.0, 3)["dsr"] < p0


def test_dsr_variance_floor():
    rng = np.random.default_rng(2)
    r = 0.001 + 0.02 * rng.standard_normal(500)
    d = S.dsr(r, [0.03, 0.03], 0.0, 2)        # zero cross-trial variance -> floor 1/(n-1)
    assert abs(d["V"] - 1.0 / 499) < 1e-15


def test_max_drawdown_and_constant_series():
    r = np.array([0.1, -0.5, 0.2])
    # path 1, 1.1, 0.55, 0.66 -> peak 1.1, trough 0.55 -> 50%
    assert abs(S.max_drawdown(r) - 0.5) < 1e-12
    assert S.sharpe(np.zeros(10)) == 0.0
    assert S.psr(np.zeros(10)) == 0.0


def test_mean_pairwise_corr_clipped():
    rng = np.random.default_rng(3)
    a = rng.standard_normal(300)
    df = pd.DataFrame({"a": a, "b": -a, "c": -a})
    # pairs: (a,b)=-1, (a,c)=-1, (b,c)=+1 -> mean -1/3 -> clipped to 0
    assert S.mean_pairwise_corr(df) == 0.0
    df2 = pd.DataFrame({"a": a, "b": a + 0.0 * rng.standard_normal(300)})
    assert abs(S.mean_pairwise_corr(df2) - 1.0) < 1e-12
