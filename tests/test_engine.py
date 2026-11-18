"""Engine tests (synthetic arrays)."""
import numpy as np
import pandas as pd
import pytest

from omr import engine as E

C_ = 0.00075  # 7.5 bps per side
EQ, GROSS, NET, EV, TURN, COST, FUND, LIQ, PRE = range(9)


def flat(T, K, v=0.0):
    return np.full((T, K), v)


def run(op, tgt, fr=None, lo=None, hi=None, cost=C_, band=0.01, **kw):
    op = np.asarray(op, float)
    if op.ndim == 1:
        op = op.reshape(-1, 1)
    T, K = op.shape
    tgt = np.asarray(tgt, float).reshape(T, K)
    fr = flat(T, K) if fr is None else np.asarray(fr, float).reshape(T, K)
    lo = op if lo is None else np.asarray(lo, float).reshape(T, K)
    hi = op if hi is None else np.asarray(hi, float).reshape(T, K)
    # the engine takes intrabar ratios relative to the open (dn = low/open, up = high/open)
    return E.run_arrays(op, lo / op, hi / op, fr, tgt, cost_rate=cost, band=band, **kw)


def test_all_cash_stays_one():
    rng = np.random.default_rng(1)
    op = 100 * np.exp(np.cumsum(0.02 * rng.standard_normal((500, 2)), axis=0))
    fr = np.where(np.arange(500)[:, None] % 8 == 0, 0.001, 0.0) * np.ones((1, 2))
    out = run(op, flat(500, 2), fr=fr)
    assert np.all(out[EQ] == 1.0) and len(out[EV]) == 0


def test_full_long_equals_open_to_open_product_minus_entry_cost():
    rng = np.random.default_rng(2)
    op = 100 * np.exp(np.cumsum(0.01 * rng.standard_normal(300)))
    out = run(op, np.ones(300))
    assert np.max(np.abs(out[EQ] - (1 - C_) * op / op[0])) < 1e-12
    assert list(out[EV]) == [0]


def test_two_asset_band_hand_computed():
    op = np.array([[100, 100], [110, 100], [111, 100], [111, 90]], float)
    out = run(op, flat(4, 2, 0.5), cost=0.001)
    e0 = 0.999
    h0 = 0.4995 * 1.1
    e1p = e0 + (h0 - 0.4995)
    e1 = e1p - 0.001 * (abs(0.5 * e1p - h0) + abs(0.5 * e1p - 0.4995))
    h0b = 0.5 * e1 * 111 / 110
    e2 = e1 + (h0b - 0.5 * e1)
    h1c = 0.5 * e1 * 0.9
    e3p = e2 + (h1c - 0.5 * e1)
    e3 = e3p - 0.001 * (abs(0.5 * e3p - h0b) + abs(0.5 * e3p - h1c))
    assert list(out[EV]) == [0, 1, 3]
    assert abs(e1 - 1.04890005) < 1e-12
    np.testing.assert_allclose(out[EQ], [e0, e1, e2, e3], rtol=0, atol=1e-13)
    # pre-trade equity: before the trade at t (equals post-trade where no trade happened)
    np.testing.assert_allclose(out[PRE], [1.0, e1p, e2, e3p], rtol=0, atol=1e-13)


def test_zero_cost_zero_band_equals_vectorised_sum():
    rng = np.random.default_rng(3)
    T, K = 600, 3
    op = 100 * np.exp(np.cumsum(0.01 * rng.standard_normal((T, K)), axis=0))
    W = rng.uniform(-1, 1, (T, K))
    W = W / np.maximum(1.0, np.abs(W).sum(axis=1, keepdims=True))
    tgt = np.vstack([np.zeros((1, K)), W[:-1]])
    eq = run(op, tgt, cost=0.0, band=0.0)[EQ]
    r = op[1:] / op[:-1] - 1.0
    expected = np.r_[1.0, np.cumprod(1.0 + np.sum(tgt[:-1] * r, axis=1))]
    assert np.max(np.abs(eq - expected)) < 1e-10


def _random_book(seed, T=3000, K=3, vol=0.01, wick=0.01):
    rng = np.random.default_rng(seed)
    op = 100 * np.exp(np.cumsum(vol * rng.standard_normal((T, K)), axis=0))
    dn = 1 - np.abs(wick * rng.standard_normal((T, K)))
    up = 1 + np.abs(wick * rng.standard_normal((T, K)))
    fr = np.where((np.arange(T) % 8 == 0)[:, None], 0.0003 * rng.standard_normal((T, K)), 0.0)
    W = np.where(rng.uniform(size=(T, 1)) < 0.02, rng.uniform(-1, 1, (T, K)), np.nan)
    W[0] = 0.0
    W = pd.DataFrame(W).ffill().to_numpy()
    W = W / np.maximum(1.0, np.abs(W).sum(axis=1, keepdims=True))
    return op, dn, up, fr, W


def test_numba_and_reference_agree():
    op, dn, up, fr, W = _random_book(4)
    for pay, recv in ((1.0, 1.0), (1.5, 0.5)):
        fast = E.run_arrays(op, dn, up, fr, W, pay_mult=pay, recv_mult=recv, fast=True)
        ref_eq, ref_ev, ref_liq = E.run_reference(op, dn, up, fr, W, pay_mult=pay, recv_mult=recv)
        assert E.HAVE_NUMBA
        assert np.max(np.abs(fast[EQ] - np.array(ref_eq))) < 1e-10
        assert list(fast[EV]) == ref_ev and fast[LIQ] == ref_liq == -1
        assert len(ref_ev) > 20


def test_numba_and_reference_agree_on_a_liquidating_path():
    op, dn, up, fr, W = _random_book(5, wick=0.01)
    up[1700, :] = 4.0                       # a 300% intrabar spike: shorts liquidate
    W[:] = np.array([-0.4, -0.3, -0.3])
    fast = E.run_arrays(op, dn, up, fr, W)
    ref_eq, ref_ev, ref_liq = E.run_reference(op, dn, up, fr, W)
    assert fast[LIQ] == ref_liq == 1700
    assert np.max(np.abs(fast[EQ] - np.array(ref_eq))) < 1e-10


def test_numba_and_reference_agree_when_equity_dies():
    op = np.array([[100.0], [100.0], [250.0], [260.0]])      # 1x short through a +150% open gap
    one = np.ones_like(op)
    fast = E.run_arrays(op, one, one, np.zeros_like(op), -np.ones_like(op))
    ref_eq, ref_ev, ref_liq = E.run_reference(op, one, one, np.zeros_like(op), -np.ones_like(op))
    assert fast[LIQ] == ref_liq == 2
    assert list(fast[EQ][2:]) == [0.0, 0.0] and ref_eq[2:] == [0.0, 0.0]
    np.testing.assert_allclose(fast[EQ], ref_eq, atol=1e-12)


def test_short_profits_when_price_falls():
    out = run([100.0, 99.0], [-1.0, -1.0], band=0.05)
    assert abs(out[EQ][1] - (1 - C_) * 1.01) < 1e-12
    path = np.linspace(100, 80, 50)
    assert run(path, -np.ones(50))[EQ][-1] > 1.15
    assert run(path, np.ones(50))[EQ][-1] < 0.85


@pytest.mark.parametrize("w,rate,expected_factor", [(1.0, 0.001, 0.999), (-1.0, 0.001, 1.001),
                                                    (1.0, -0.002, 1.002), (-1.0, -0.002, 0.998)])
def test_funding_sign_hand_computed(w, rate, expected_factor):
    out = run([100.0] * 4, [w] * 4, fr=[0.0, 0.0, rate, 0.0])
    assert abs(out[EQ][1] - (1 - C_)) < 1e-15
    assert abs(out[EQ][2] - (1 - C_) * expected_factor) < 1e-15
    assert abs(out[FUND] - (1 - C_) * (1 - expected_factor)) < 1e-15


def test_funding_stress_multipliers():
    eq_pay = run([100.0] * 3, [1.0] * 3, fr=[0, 0.001, 0], pay_mult=1.5, recv_mult=0.5)[EQ]
    eq_recv = run([100.0] * 3, [-1.0] * 3, fr=[0, 0.001, 0], pay_mult=1.5, recv_mult=0.5)[EQ]
    assert abs(eq_pay[1] - (1 - C_) * (1 - 0.0015)) < 1e-15
    assert abs(eq_recv[1] - (1 - C_) * (1 + 0.0005)) < 1e-15


def test_funding_applied_to_pre_rebalance_position():
    out = run([100.0] * 3, [1.0, 1.0, -1.0], fr=[0.0, 0.0, 0.001])
    h = 1 - C_
    e_f = h - 0.001 * h
    expected = e_f - C_ * abs(-1.0 * e_f - h)
    assert list(out[EV]) == [0, 2] and abs(out[EQ][2] - expected) < 1e-15
    e_wrong = h - C_ * abs(-h - h)
    assert abs(out[EQ][2] - (e_wrong + 0.001 * e_wrong)) > 1e-4


def test_non_finite_funding_is_rejected():
    with pytest.raises(ValueError):
        run([100.0] * 3, [1.0] * 3, fr=[0.0, np.nan, 0.0])


def test_synthetic_crash_trips_liquidation_including_exactly_two_and_a_half_percent():
    op = np.array([100.0, 100.0, 100.0])
    assert run(op, [1.0] * 3, lo=np.array([100.0, 2.0, 100.0]))[LIQ] == 1
    assert run(op, [-1.0] * 3, hi=np.array([100.0, 199.0, 100.0]))[LIQ] == 1
    assert run(op, [1.0] * 3, lo=np.array([100.0, 50.0, 100.0]))[LIQ] == -1
    # 1x long, low/open = 0.025 -> worst equity = 2.5% of gross exactly: flagged
    o = np.full((3, 1), 100.0)
    for ratio, expect in ((0.0251, -1), (0.025, 1), (0.0249, 1)):
        d = np.array([[1.0], [ratio], [1.0]])
        assert E.run_arrays(o, d, np.ones_like(o), np.zeros_like(o), np.ones_like(o), cost_rate=0.0)[LIQ] == expect


def test_daily_returns_sampled_at_midnight_pre_trade():
    idx = pd.date_range("2022-01-01 00:00", periods=48, freq="h", tz="UTC")
    pre = np.linspace(1.0, 1.47, 48)
    post = pre.copy()
    post[24] = pre[24] - 0.01                # a trade cost at the 00:00 open of day 2
    d = E.daily_returns(pre, post, idx)
    assert len(d) == 2
    assert abs(d.iloc[0] - (pre[24] / 1.0 - 1)) < 1e-15          # day 1: start capital -> 00:00 pre-trade
    assert abs(d.iloc[1] - (post[47] / pre[24] - 1)) < 1e-15     # last day: 23 hours, to the last post value
    assert list(E.daily_complete_mask(idx)) == [True, False]
