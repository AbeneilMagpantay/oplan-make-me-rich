"""Interpreter semantics (LANGUAGE.md sections 5-7) against naive hand computations: timeframes,
fixed-order windows, the finite ema / rsi / atr, the windowed hold, the knownness channel, cross
sections, weights."""
import math

import numpy as np
import pandas as pd
import pytest

from omr import constants as C
from omr import datasets as D
from omr import interp as X
from omr import lang as L
from omr import windows as WN
from conftest import prog_text, synth_raw


def frame(start="2022-03-01 00:00", end="2022-03-20 23:00", seed=1, **kw):
    return D.assemble_frame(synth_raw(start=start, end=end, seed=seed, **kw), D.PROGRAM_EXTRA)


def ev(body, frames, kind="single", params=None, btc=None, probe=True):
    prog = L.parse(prog_text(body, kind=kind), "x_test", probe=probe)
    p = L.default_params(prog)
    p.update(params or {})
    raw, kn = X.evaluate_full(prog, p, frames, btc if btc is not None else frames[0])
    return raw, kn


def naive_mean(w):
    s = 0.0
    for v in w:
        s += v
    return s / len(w)


def naive_std(w):
    m = naive_mean(w)
    ss = 0.0
    for v in w:
        ss += (v - m) * (v - m)
    return math.sqrt(ss / (len(w) - 1))


def test_daily_bins_are_complete_and_visible_from_the_closing_bar():
    f = frame(start="2022-03-01 05:00", end="2022-03-04 12:00")          # first and last days incomplete
    raw, kn = ev("signal = daily(close) / daily(open) - 1", [f])
    day2 = f.loc["2022-03-02"]
    want = day2["close"].iloc[-1] / day2["open"].iloc[0] - 1
    t23 = f.index.get_loc(pd.Timestamp("2022-03-02 23:00", tz="UTC"))
    assert not kn[:t23, 0].any() and np.isnan(raw[:t23, 0]).all()       # 03-01 incomplete: never known
    assert kn[t23, 0] and raw[t23, 0] == want                           # known in the bar that closes the day
    assert raw[t23 + 23, 0] == want and raw[t23 + 24, 0] != want


def test_weekly_bins_anchor_on_monday_and_aggregations():
    f = frame(start="2022-03-01 00:00", end="2022-03-22 23:00")           # 2022-03-07 and 03-14 are Mondays
    raw, kn = ev("signal = weekly(close) / weekly(open) - 1", [f])
    wk = f.loc["2022-03-07":"2022-03-13"]
    t = f.index.get_loc(pd.Timestamp("2022-03-13 23:00", tz="UTC"))
    assert not kn[:t, 0].any() and raw[t, 0] == wk["close"].iloc[-1] / wk["open"].iloc[0] - 1
    raw2, _ = ev("signal = daily(high) / daily(low) - 1", [f])
    d = f.loc["2022-03-05"]
    t5 = f.index.get_loc(pd.Timestamp("2022-03-05 23:00", tz="UTC"))
    assert raw2[t5, 0] == d["high"].max() / d["low"].min() - 1


@pytest.mark.parametrize("fn,ref", [("sma", naive_mean), ("std", naive_std), ("rmin", min), ("rmax", max),
                                    ("rsum", lambda w: naive_mean(w) * 0 + sum_seq(w)),
                                    ("median", lambda w: float(np.median(w)))])
def test_windows_are_computed_from_their_own_rows_in_fixed_order(fn, ref):
    f = frame()
    n = 5
    raw, kn = ev(f"n = param(5, 2, 8)\nsignal = {fn}(volume, n) / volume", [f], probe=False)
    v = f["volume"].to_numpy()
    assert not kn[:n - 1, 0].any() and kn[n - 1:, 0].all()
    for t in (n - 1, 40, 200, len(v) - 1):
        assert raw[t, 0] == ref(list(v[t - n + 1:t + 1])) / v[t]


def sum_seq(w):
    s = 0.0
    for v in w:
        s += v
    return s


def test_rank_and_zscore():
    f = frame()
    v = f["volume"].to_numpy()
    raw, _ = ev("n = param(5, 2, 8)\nsignal = rank(volume, n)", [f])
    for t in (4, 40, 200):
        assert raw[t, 0] == np.sum(v[t - 4:t + 1] <= v[t]) / 5
    raw, _ = ev("n = param(5, 2, 8)\nsignal = zscore(volume, n)", [f])
    w = list(v[36:41])
    assert raw[40, 0] == (v[40] - naive_mean(w)) / naive_std(w)


def test_ema_is_a_finite_weighted_mean_of_5n_rows():
    f = frame()
    n = 4
    m = C.EMA_MEMORY * n
    raw, kn = ev("n = param(4, 2, 8)\nsignal = ema(volume, n) / volume", [f])
    x = f["volume"].to_numpy()
    w = list(WN.decay_weights(n, m, 1.0 - 2.0 / (n + 1.0)))           # w[i] = r ** (m - 1 - i), oldest first
    assert w[-1] == 1.0 and abs(w[0] / 0.6 ** (m - 1) - 1) < 1e-12
    W = sum_seq(w)
    assert not kn[:m - 1, 0].any() and kn[m - 1, 0]
    for t in (m - 1, 100, 300):
        s = 0.0
        for i in range(m):
            s += w[i] * x[t - m + 1 + i]
        assert raw[t, 0] == (s / W) / x[t]


def test_rsi_is_finite_and_centred():
    f = frame()
    n = 3
    m = C.RSI_MEMORY * n
    raw, kn = ev("n = param(3, 2, 5)\nsignal = rsi(close, n)", [f])
    c = f["close"].to_numpy()
    w = list(WN.decay_weights(n, m, 1.0 - 1.0 / n))
    assert not kn[:m, 0].any() and kn[m, 0]
    for t in (m, 200):
        G = Ls = 0.0
        for i in range(m):
            k = t - m + 1 + i
            d = c[k] - c[k - 1]
            if d > 0:
                G += w[i] * d
            elif d < 0:
                Ls += w[i] * (-d)
        assert raw[t, 0] == (G - Ls) / (G + Ls)
    assert np.nanmax(np.abs(raw)) <= 1.0


def test_atr_and_realised_vol():
    f = frame()
    n = 3
    m = C.ATR_MEMORY * n
    raw, kn = ev("n = param(3, 2, 5)\nsignal = atr(high, low, close, n) / close", [f])
    h, lo, c = (f[k].to_numpy() for k in ("high", "low", "close"))
    w = list(WN.decay_weights(n, m, 1.0 - 1.0 / n))
    t = 200
    s = 0.0
    for i in range(m):
        k = t - m + 1 + i
        s += w[i] * max(h[k] - lo[k], abs(h[k] - c[k - 1]), abs(lo[k] - c[k - 1]))
    assert raw[t, 0] == (s / sum_seq(w)) / c[t] and not kn[m - 1, 0] and kn[m, 0]
    raw, kn = ev("n = param(10, 5, 20)\nsignal = realised_vol(close, n)", [f])
    lr = [math.log(c[k] / c[k - 1]) for k in range(t - 9, t + 1)]
    assert raw[t, 0] == naive_std(lr) * math.sqrt(8760.0) and not kn[9, 0] and kn[10, 0]


def test_lags_and_returns_need_every_row_of_their_window():
    f = frame()
    c = f["close"].to_numpy()
    raw, kn = ev("n = param(3, 2, 5)\nsignal = ret(close, n)", [f])
    assert not kn[:3, 0].any() and kn[3, 0] and raw[10, 0] == c[10] / c[7] - 1.0
    raw, _ = ev("signal = logret(close, 1)", [f])
    assert raw[10, 0] == np.log(c[10] / c[9])


def test_windowed_hold_equals_the_machine_from_flat_over_h_rows():
    el = np.array([0, 1, 0, 0, 0, 0, 1, 0, 0], dtype=bool)[:, None]
    xl = np.array([0, 0, 1, 0, 0, 0, 0, 0, 0], dtype=bool)[:, None]
    es = np.array([0, 0, 0, 1, 0, 1, 0, 1, 0], dtype=bool)[:, None]
    xs = np.array([0, 0, 0, 0, 1, 0, 0, 0, 1], dtype=bool)[:, None]
    # with h = t + 1 the window starts at row 0: the unbounded machine
    full = [WN.hold_window(el, xl, es, xs, t + 1)[t, 0] for t in range(9)]
    assert full == [0, 1, 0, -1, 0, -1, 1, -1, 0]
    both = WN.hold_window(np.ones((2, 1), bool), np.zeros((2, 1), bool), np.ones((2, 1), bool), np.zeros((2, 1), bool), 2)
    assert both[1, 0] == 0                                                 # conflicting entries from flat: stay flat
    # sliding windows: a naive re-run from flat for every t
    rng = np.random.default_rng(3)
    A = rng.uniform(size=(300, 4, 2)) < np.array([0.05, 0.1, 0.05, 0.1])[None, :, None]
    for h in (1, 3, 17):
        got = WN.hold_window(A[:, 0].copy(), A[:, 1].copy(), A[:, 2].copy(), A[:, 3].copy(), h)
        for j in range(2):
            for t in range(h - 1, 300):
                st = 0.0
                for k in range(t - h + 1, t + 1):
                    a, b, c, d = A[k, :, j]
                    if st == 0.0:
                        st = 1.0 if (a and not c) else (-1.0 if (c and not a) else 0.0)
                    elif st == 1.0:
                        st = -1.0 if c else (0.0 if b else 1.0)
                    else:
                        st = 1.0 if a else (0.0 if d else -1.0)
                assert got[t, j] == st


def test_knownness_is_strict_and_unobservable():
    f = frame(end="2022-05-30 23:00")
    # a component known early plus one known late: the sum is known only after the longest warm-up
    raw, kn = ev("a = param(5, 2, 8)\nb = param(300, 200, 400)\n"
                 "signal = sign(sma(ret(close, 1), a)) + sign(sma(ret(close, 1), b))", [f])
    first = int(np.argmax(kn[:, 0]))
    assert first == 300 and not kn[:300, 0].any()
    # where() needs the condition and BOTH branches known
    raw, kn = ev("b = param(300, 200, 400)\nsignal = where(ret(close, 1) > 0, sign(sma(ret(close, 1), b)), 1)", [f])
    assert int(np.argmax(kn[:, 0])) == 300
    # a comparison on an unknown row has no definite value: the impulse at the first bar is unknown
    raw, kn = ev("signal = where(lag(close, 1) / close > 0, -1, 1)", [f], probe=False)
    assert not kn[0, 0] and np.isnan(raw[0, 0]) and (raw[1:, 0] == -1).all()


def test_nan_values_compare_false_and_division_by_zero_is_nan():
    f = frame()
    raw, kn = ev("signal = where(log(ret(close, 1)) > -10, 1, -1)", [f])
    r = f["close"].pct_change().to_numpy()
    assert kn[1:, 0].all() and (raw[1:, 0][r[1:] < 0] == -1).all()         # log of a negative: NaN, compares False
    f2 = f.copy()
    f2["taker_buy_volume"] = 0.0
    raw, kn = ev("signal = sign(volume / taker_buy_volume)", [f2], probe=False)
    assert kn[0, 0] and np.isnan(raw).all()                                # known, but the value is NaN
    f3 = f.copy()
    f3["volume"] = 3.0
    raw, kn = ev("n = param(3, 2, 5)\nsignal = zscore(volume, n)", [f3], probe=False)
    assert kn[5, 0] and np.isnan(raw).all()


def test_mark_close_is_the_last_mark_bar_known_while_at_most_6_hours_old():
    raw = synth_raw(start="2022-03-01 00:00", end="2022-03-10 23:00", seed=4)
    mk = raw["mark_klines"]
    raw["mark_klines"] = mk.drop(mk.index[[50]]).drop(mk.index[100:108])     # one missing bar; an 8-hour gap
    f = D.assemble_frame(raw, D.PROGRAM_EXTRA)
    prog = L.parse(prog_text("signal = sign(mark_close - close)"), "x_test")
    ctx = X.Context(prog, {}, [f], f)
    s = ctx.field("mark_close")
    mc = mk["close"].to_numpy()
    assert s.kn[50, 0] and s.arr[50, 0] == mc[49]                              # one missing bar: last bar's close
    assert s.kn[99 + 6, 0] and not s.kn[99 + 7, 0] and not s.kn[107, 0]          # 6 h old known, 7 h old not
    assert s.kn[108, 0] and s.arr[108, 0] == mc[108]
    r, kn = ev("n = param(3, 2, 5)\nsignal = sign(sma(mark_close, n) - close)", [f])
    assert kn[48:56, 0].all()                                                  # a window across the single gap
    assert not kn[106:110, 0].any() and kn[110, 0]                             # unknown after more than 6 h


def test_funding_fields_and_funding_mean_over_settlements():
    f = frame()
    raw, kn = ev("n = param(3, 2, 5)\nsignal = funding_mean(n) / funding8h", [f])
    new = f["funding.new"].to_numpy()
    r8 = (f["funding.rate"] * 8.0 / f["funding.interval_hours"]).to_numpy()
    ev_pos = np.nonzero(new)[0]
    t = ev_pos[5] + 3
    s = 0.0
    for v in r8[ev_pos[3:6]]:
        s += v
    assert raw[t, 0] == (s / 3) / r8[t]
    assert not kn[ev_pos[1], 0] and kn[ev_pos[2], 0]


def test_hour_and_weekday_are_of_the_decision_time():
    f = frame(start="2022-03-06 00:00", end="2022-03-08 23:00")
    raw, _ = ev("k = param(12, 9, 15)\nsignal = where(hour > k, 1, 0) + where(hour < k, -1, 0)", [f], params={"k": 23})
    t = f.index.get_loc(pd.Timestamp("2022-03-06 22:00", tz="UTC"))
    assert raw[t, 0] == 0 and raw[t + 1, 0] == -1
    raw, _ = ev("k = param(3, 2, 4)\nsignal = where(weekday < k, 1, 0)", [f], params={"k": 1})
    assert raw[t + 1, 0] == 1 and raw[t, 0] == 0


def test_btc_is_broadcast_and_cross_sections():
    a, b = frame(seed=1), frame(seed=2)
    n_ = "n = param(3, 2, 5)\n"
    raw, _ = ev(n_ + "signal = sign(close / btc(close) - lag(close / btc(close), n))", [a], btc=b)
    q = a["close"].to_numpy() / b["close"].to_numpy()
    assert np.array_equal(raw[3:, 0], np.sign(q[3:] - q[:-3]))
    raw, kn = ev("signal = cs_rank(ret(close, 1))", [a, b], kind="portfolio")
    r = np.column_stack([a["close"].pct_change(), b["close"].pct_change()])
    assert set(np.unique(raw[1:])) <= {-1.0, 1.0} and not kn[0].any()
    assert np.array_equal(raw[1:, 0] > 0, r[1:, 0] > r[1:, 1])
    raw, _ = ev("signal = cs_scale(ret(close, 1))", [a, b], kind="portfolio")
    assert np.allclose(np.abs(raw[1:]).sum(axis=1), 1.0)


def test_weights_single_and_portfolio():
    prog = L.parse(prog_text("signal = sign(close - open)"), "x_test")
    raw = np.array([[2.0, np.nan], [-0.4, 0.7]])
    assert np.array_equal(X.weights(prog, raw, 2), np.array([[0.5, 0.0], [-0.2, 0.35]]))
    pp = L.parse(prog_text("signal = cs_rank(ret(close, 1))", kind="portfolio"), "x_test")
    w = X.weights(pp, np.array([[0.9, -0.9], [0.3, 0.2], [np.inf, 1.0]]), 2)
    assert np.allclose(w[0], [0.5, -0.5]) and np.allclose(w[1], [0.3, 0.2])
    assert np.array_equal(w[2], [0.0, 1.0])


def test_each_name_is_evaluated_once(monkeypatch):
    f = frame()
    calls = []
    orig = WN.roll

    def spy(x, n, op):
        calls.append(op)
        return orig(x, n, op)
    monkeypatch.setattr(X.WN, "roll", spy)
    ev("n = param(5, 2, 8)\nm = sma(volume, n)\nsignal = sign(m / volume - 1) + sign(m / lag(volume, n) - 1)", [f])
    assert len(calls) == 2                                                # once for the probe, once here


def test_panel_frames_must_share_one_index():
    a = frame(start="2022-03-01 00:00")
    b = frame(start="2022-03-01 01:00")
    prog = L.parse(prog_text("signal = cs_rank(ret(close, 1))", kind="portfolio"), "x_test")
    with pytest.raises(ValueError):
        X.evaluate(prog, {}, [a, b], a)
