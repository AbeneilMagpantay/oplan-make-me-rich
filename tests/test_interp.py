"""Interpreter semantics (A9-A13) against hand computations on small synthetic panels."""
import math

import numpy as np
import pandas as pd
import pytest

from omr import datasets as D
from omr import interp as X
from omr import lang as L
from conftest import prog_text, synth_raw


def frame(start="2022-03-01 00:00", end="2022-03-20 23:00", seed=1, **kw):
    return D.assemble_frame(synth_raw(start=start, end=end, seed=seed, **kw), D.PROGRAM_EXTRA)


def ev(body, frames, kind="single", params=None, btc=None):
    prog = L.parse(prog_text(body, kind=kind), "x_test")
    p = L.default_params(prog)
    p.update(params or {})
    return X.evaluate(prog, p, frames, btc if btc is not None else frames[0]), prog


def test_daily_bins_are_complete_and_visible_from_the_closing_bar():
    f = frame(start="2022-03-01 05:00", end="2022-03-04 12:00")          # first and last days incomplete
    raw, _ = ev("signal = daily(close) / daily(open) - 1", [f])
    idx = f.index
    day2 = f.loc["2022-03-02"]
    want = day2["close"].iloc[-1] / day2["open"].iloc[0] - 1
    t23 = idx.get_loc(pd.Timestamp("2022-03-02 23:00", tz="UTC"))
    assert np.isnan(raw[:t23, 0]).all()                                    # 03-01 incomplete: never a value
    assert raw[t23, 0] == want                                             # visible in the bar that closes the day
    assert raw[t23 + 23, 0] == want and raw[t23 + 24, 0] != want           # held until the next day closes
    assert not np.isnan(raw[-1, 0])                                        # 03-03 complete; 03-04 partial never shows


def test_weekly_bins_anchor_on_monday_and_daily_high_low_aggregate():
    f = frame(start="2022-03-01 00:00", end="2022-03-22 23:00")           # 2022-03-07 and 03-14 are Mondays
    raw, _ = ev("signal = weekly(close) / weekly(open) - 1", [f])
    wk = f.loc["2022-03-07":"2022-03-13"]
    t = f.index.get_loc(pd.Timestamp("2022-03-13 23:00", tz="UTC"))
    assert np.isnan(raw[:t, 0]).all()
    assert raw[t, 0] == wk["close"].iloc[-1] / wk["open"].iloc[0] - 1
    raw2, _ = ev("signal = daily(high) / daily(low) - 1", [f])
    d = f.loc["2022-03-05"]
    t5 = f.index.get_loc(pd.Timestamp("2022-03-05 23:00", tz="UTC"))
    assert raw2[t5, 0] == d["high"].max() / d["low"].min() - 1
    raw3, _ = ev("signal = h4(volume) / h4(volume) - 1 + h4(trades) / lag(h4(trades), 1)", [f])
    t4 = f.index.get_loc(pd.Timestamp("2022-03-05 07:00", tz="UTC"))
    b = f.loc[pd.Timestamp("2022-03-05 04:00", tz="UTC"):pd.Timestamp("2022-03-05 07:00", tz="UTC")]
    a = f.loc[pd.Timestamp("2022-03-05 00:00", tz="UTC"):pd.Timestamp("2022-03-05 03:00", tz="UTC")]
    assert raw3[t4, 0] == b["trades"].sum() / a["trades"].sum()


def test_rolling_windows_need_a_full_window_and_match_pandas():
    f = frame()
    n = 5
    raw, _ = ev("n = param(5, 2, 8)\nsignal = sma(volume, n) / volume", [f])
    v = f["volume"]
    want = (v.rolling(n, min_periods=n).mean() / v).to_numpy()
    assert np.isnan(raw[:n - 1, 0]).all()
    assert np.array_equal(raw[:, 0], want, equal_nan=True)
    raw, _ = ev("n = param(5, 2, 8)\nsignal = std(volume, n) / volume", [f])
    assert np.array_equal(raw[:, 0], (v.rolling(n, min_periods=n).std(ddof=1) / v).to_numpy(), equal_nan=True)
    raw, _ = ev("n = param(5, 2, 8)\nsignal = rank(volume, n)", [f])
    x = v.to_numpy()
    for t in (n - 1, 40, 200):
        win = x[t - n + 1:t + 1]
        assert raw[t, 0] == np.sum(win <= x[t]) / n                        # share of the window <= current, in (0, 1]
    raw, _ = ev("n = param(5, 2, 8)\nsignal = rsum(volume, n) / rmax(volume, n) - rmin(volume, n) / median(volume, n)", [f])
    r = v.rolling(n, min_periods=n)
    assert np.allclose(raw[:, 0], (r.sum() / r.max() - r.min() / r.median()).to_numpy(), equal_nan=True, rtol=0, atol=0)


def test_ema_is_sma_seeded_with_alpha_2_over_n_plus_1():
    f = frame()
    raw, _ = ev("n = param(4, 2, 8)\nsignal = ema(volume, n) / volume", [f])
    x = f["volume"].to_numpy()
    y = np.mean(x[:4])
    want = [np.nan] * 3 + [y]
    for t in range(4, 30):
        y = y + 0.4 * (x[t] - y)
        want.append(y)
    assert np.allclose(raw[:30, 0] * x[:30], np.array(want), equal_nan=True, rtol=1e-15)


def test_zscore_is_nan_where_std_is_zero_and_division_by_zero_is_nan():
    f = frame()
    f["volume"] = 3.0
    raw, _ = ev("n = param(3, 2, 5)\nsignal = zscore(volume, n)", [f])
    assert np.isnan(raw).all()
    f["taker_buy_volume"] = 0.0
    raw, _ = ev("signal = sign(volume / taker_buy_volume)", [f])
    assert np.isnan(raw).all()


def test_nan_comparisons_are_false_and_hold_transitions():
    f = frame()
    raw, _ = ev("n = param(30, 20, 40)\nsignal = where(sma(ret(close, 1), n) > 0, 1, -1)", [f])
    assert (raw[:30, 0] == -1).all()                                       # NaN > 0 is False
    el = np.array([0, 1, 0, 0, 0, 0, 1, 0, 0], dtype=bool)[:, None]
    xl = np.array([0, 0, 1, 0, 0, 0, 0, 0, 0], dtype=bool)[:, None]
    es = np.array([0, 0, 0, 1, 0, 1, 0, 1, 0], dtype=bool)[:, None]
    xs = np.array([0, 0, 0, 0, 1, 0, 0, 0, 1], dtype=bool)[:, None]
    out = X._hold(el, xl, es, xs)[:, 0]
    # flat, enter long, exit long, enter short, exit short, enter short, short->long, long->short, exit short
    assert out.tolist() == [0, 1, 0, -1, 0, -1, 1, -1, 0]
    both = X._hold(np.ones((2, 1), bool), np.zeros((2, 1), bool), np.ones((2, 1), bool), np.zeros((2, 1), bool))
    assert both[:, 0].tolist() == [0, 0]                                   # conflicting entries from flat: stay flat


def test_rsi_is_centred_and_atr_realised_vol_match_the_indicators():
    from omr import indicators as ind
    f = frame()
    raw, _ = ev("n = param(14, 7, 28)\nsignal = rsi(close, n)", [f])
    want = (ind.rsi_wilder(f["close"].reset_index(drop=True), 14).to_numpy() - 50.0) / 50.0
    assert np.array_equal(raw[:, 0], want, equal_nan=True)
    assert np.nanmax(np.abs(raw)) <= 1.0
    raw, _ = ev("n = param(10, 5, 20)\nsignal = atr(high, low, close, n) / close", [f])
    a = ind.atr(f[["high", "low", "close"]].reset_index(drop=True), 10).to_numpy()
    assert np.array_equal(raw[:, 0], a / f["close"].to_numpy(), equal_nan=True)
    raw, _ = ev("n = param(10, 5, 20)\nsignal = realised_vol(close, n)", [f])
    rv = ind.realised_vol(f["close"].reset_index(drop=True), 10, 8760.0).to_numpy()
    assert np.array_equal(raw[:, 0], rv, equal_nan=True)


def test_lags_and_returns():
    f = frame()
    c = f["close"].to_numpy()
    raw, _ = ev("n = param(3, 2, 5)\nsignal = ret(close, n)", [f])
    assert np.isnan(raw[:3, 0]).all() and raw[10, 0] == c[10] / c[7] - 1.0
    raw, _ = ev("signal = logret(close, 1)", [f])
    assert raw[10, 0] == np.log(c[10] / c[9])
    raw, _ = ev("signal = delta(close, 1) / lag(close, 1)", [f])
    assert raw[10, 0] == (c[10] - c[9]) / c[9]


def test_funding_fields_and_funding_mean_over_settlements():
    f = frame()
    raw, _ = ev("n = param(3, 2, 5)\nsignal = funding_mean(n) / funding8h", [f])
    new = f["funding.new"].to_numpy()
    r8 = (f["funding.rate"] * 8.0 / f["funding.interval_hours"]).to_numpy()
    ev_pos = np.nonzero(new)[0]
    t = ev_pos[5] + 3                                                      # 3 bars after the 6th settlement
    want = np.mean(r8[ev_pos[3:6]]) / r8[t]
    assert raw[t, 0] == pytest.approx(want, rel=1e-15)
    assert np.isnan(raw[ev_pos[1], 0])                                     # fewer than 3 settlements yet


def test_hour_and_weekday_are_of_the_decision_time():
    f = frame(start="2022-03-06 00:00", end="2022-03-08 23:00")           # 03-06 is a Sunday
    k = {"k": 23}
    raw, _ = ev("k = param(12, 9, 15)\nsignal = where(hour > k, 1, 0) + where(hour < k, -1, 0)", [f], params=k)
    t = f.index.get_loc(pd.Timestamp("2022-03-06 22:00", tz="UTC"))        # decided at 23:00
    assert raw[t, 0] == 0 and raw[t + 1, 0] == -1                         # 23:00 bar decides at 00:00
    raw, _ = ev("k = param(3, 2, 4)\nsignal = where(weekday < k, 1, 0)", [f], params={"k": 1})
    assert raw[t + 1, 0] == 1 and raw[t, 0] == 0                           # Monday 00:00 (weekday 0) vs Sunday


def test_btc_is_broadcast_and_cross_sections():
    a, b = frame(seed=1), frame(seed=2)
    raw, _ = ev("signal = sign(close / btc(close) - lag(close / btc(close), 1))", [a], btc=b)
    q = a["close"].to_numpy() / b["close"].to_numpy()
    assert np.array_equal(raw[1:, 0], np.sign(q[1:] - q[:-1]))
    raw, _ = ev("signal = cs_rank(ret(close, 1))", [a, b], kind="portfolio")
    r = np.column_stack([a["close"].pct_change(), b["close"].pct_change()])
    assert set(np.unique(raw[1:])) <= {-1.0, 1.0}
    assert np.array_equal(raw[1:, 0] > 0, r[1:, 0] > r[1:, 1])
    raw, _ = ev("signal = cs_demean(ret(close, 1)) + cs_mean(ret(close, 1)) - ret(close, 1)", [a, b], kind="portfolio")
    assert np.allclose(raw[1:], 0.0, atol=1e-15)
    raw, _ = ev("signal = cs_scale(ret(close, 1))", [a, b], kind="portfolio")
    assert np.allclose(np.abs(raw[1:]).sum(axis=1), 1.0)


def test_weights_single_and_portfolio():
    prog = L.parse(prog_text("signal = sign(close - open)"), "x_test")
    raw = np.array([[2.0, np.nan], [-0.4, 0.7]])
    assert np.array_equal(X.weights(prog, raw, 2), np.array([[0.5, 0.0], [-0.2, 0.35]]))
    pp = L.parse(prog_text("signal = cs_rank(ret(close, 1))", kind="portfolio"), "x_test")
    w = X.weights(pp, np.array([[0.9, -0.9], [0.3, 0.2], [np.inf, 1.0]]), 2)
    assert np.allclose(w[0], [0.5, -0.5]) and np.allclose(w[1], [0.3, 0.2])
    assert np.array_equal(w[2], [0.0, 1.0])                                # non-finite -> 0, then clip


def test_each_name_is_evaluated_once(monkeypatch):
    f = frame()
    calls = []
    orig = X.Context.rolling

    def spy(self, fn, x, n):
        calls.append(fn)
        return orig(self, fn, x, n)
    monkeypatch.setattr(X.Context, "rolling", spy)
    ev("n = param(5, 2, 8)\nm = sma(volume, n)\nsignal = sign(m / volume - 1) + sign(m / lag(volume, 1) - 1)", [f])
    assert calls == ["sma"]


def test_panel_frames_must_share_one_index():
    a = frame(start="2022-03-01 00:00")
    b = frame(start="2022-03-01 01:00")
    prog = L.parse(prog_text("signal = cs_rank(ret(close, 1))", kind="portfolio"), "x_test")
    with pytest.raises(ValueError):
        X.evaluate(prog, {}, [a, b], a)
