"""Calibration constructions: null-B mirror (OHLC consistency, r' = 2m - r), oracle alignment and
injection after the interpreter, the stage-1 filter of the DEV-overfit protocol, summaries per
SUBMITTED pair, and the family restriction."""
import numpy as np
import pandas as pd
import pytest

from omr import calibrate as K
from omr import constants as C
from omr import lang as L
from omr import pipeline
from conftest import synth_world


def _fake_source(nd=3, seed=0):
    rng = np.random.default_rng(seed)
    o_rel = np.exp(0.001 * rng.standard_normal((nd, 24)))
    c_rel = np.exp(0.01 * rng.standard_normal((nd, 24)))
    hr = np.maximum(1.0, c_rel) * np.exp(np.abs(0.005 * rng.standard_normal((nd, 24))))
    lr = np.minimum(1.0, c_rel) * np.exp(-np.abs(0.005 * rng.standard_normal((nd, 24))))
    has = np.ones((nd, 24), dtype=bool)
    has[1, 5] = False
    return {"days": pd.date_range("2021-01-01", periods=nd, freq="D", tz="UTC").as_unit("ns"), "nd": nd,
            "g": o_rel, "hr": hr, "lr": lr, "cr": c_rel,
            "gm": o_rel.copy(), "hm": hr * 0.999 + 0.001, "lm": lr, "cm": c_rel, "has": has,
            "other": np.ones((nd, 24, len(K.OTHER))), "gap": np.zeros((nd, 24), dtype=bool),
            "fhour": np.zeros(0, dtype=np.int64), "frate": np.zeros(0), "fint": np.zeros(0),
            "offs": np.zeros(nd + 1, dtype=np.int64), "p0": 100.0, "mp0": 100.0, "m": 0.0002, "m_mark": 0.0002}


def test_null_b_mirror_is_consistent_and_negates_the_demeaned_path():
    v = _fake_source()
    days = np.arange(3)
    f0, _ = K._synth_symbol(v, days, np.zeros(3, dtype=bool))
    f1, liq1 = K._synth_symbol(v, days, np.array([False, True, False]))
    o, h, l_, c = (f1[k].to_numpy() for k in ("open", "high", "low", "close"))
    assert np.all(h >= np.maximum(o, c) - 1e-12) and np.all(l_ <= np.minimum(o, c) + 1e-12)
    assert np.allclose(f1.iloc[:24][["open", "high", "low", "close"]].to_numpy(),
                       f0.iloc[:24][["open", "high", "low", "close"]].to_numpy(), rtol=0, atol=1e-12)
    r = np.diff(np.log(f0["close"].to_numpy()))[23:47]
    r1 = np.diff(np.log(c))[23:47]
    assert np.allclose(r1, 2 * v["m"] - r, atol=1e-12)
    b = 24 + 7
    assert abs(h[b] / o[b] - 1.0 / v["lr"][1, 7]) < 1e-12 and abs(l_[b] / o[b] - 1.0 / v["hr"][1, 7]) < 1e-12
    assert not liq1["has_mark"].iloc[24 + 5] and liq1["has_mark"].iloc[24 + 6]
    assert "mark_klines.close" in f1.columns and "funding.rate" in f1.columns       # program frames


def test_oracle_uses_the_future_block_return_and_is_injected_after_the_interpreter(val_handle):
    w = synth_world(seed=9)
    ob = K.OracleBase(w, 20, eps_seed=1)
    W1, W0 = ob.weights(1.0), ob.weights(0.0)
    starts = np.arange(ob.dev_s, ob.val_e, 480)
    ends = np.minimum(starts + 480, ob.val_e)
    R = np.log(ob.mk.op[ends, 0] / ob.mk.op[starts, 0])
    sgn = np.where(R - R.mean() >= 0, 0.5, -0.5)
    assert np.allclose(W1[starts - 1, 0], sgn)
    assert np.allclose(W1[ends - 2, 0], sgn)
    assert np.all(W1[: ob.dev_s - 1] == 0.0)
    assert ob.val_sharpe(1.0) > 3.0 and abs(ob.val_sharpe(0.0)) < ob.val_sharpe(1.0) / 2
    res = pipeline.evaluate_weights(W1, ob.grid, w, 3, pipeline.Opts(perm_n=60, keep_detail=False), val_handle, 0.05)
    assert res["status"] == "evaluated" and res["gates"]["G6"]["pass"] and res["gates"]["G5"]["g5_vacuous"]
    noise = pipeline.evaluate_weights(W0, ob.grid, w, 3, pipeline.Opts(perm_n=60, keep_detail=False), val_handle, 0.05)
    assert not noise["gates"]["G6"]["pass"]


def test_families_are_only_the_kernel_baselines():
    assert K.FAMILIES == ("gen000_sma_cross_ls", "gen000_donchian_ls", "gen000_rsi_meanrev_ls",
                          "gen000_voltarget_trend_ls", "gen000_funding_carry")
    for f in K.FAMILIES:
        assert L.parse_file(K.family_path(f)).name == f
    with pytest.raises(ValueError):
        K.family_path("my_own_strategy")
    with pytest.raises(ValueError):
        K.family_path("../strategies/gen000_sma_cross_ls")


def test_draws_respect_declared_ranges_and_types():
    prog = L.parse_file(K.family_path("gen000_funding_carry"))
    rng = np.random.default_rng(0)
    for _ in range(50):
        q = K.draw_params(prog, rng)
        assert isinstance(q["lookback"], int) and 6 <= q["lookback"] <= 90
        assert 0.00015 <= q["hi"] <= 0.001 and -0.0005 <= q["lo"] <= 0.0


def test_null_summary_counts_submitted_pairs_only():
    sub = {"submitted": True, "status": "evaluated", "params": {}, "val_sharpe": 1.0,
           "gates": {g: True for g in ("G1", "G2", "G3", "G4", "G5", "G7", "G10")} | {"G6": None, "G8": None}}
    rows = [dict(sub, family="a", world_seed=1, perm_p=0.01, stage1={"passed": 3, "activity_dev": 17}),
            dict(sub, family="a", world_seed=2, perm_p=0.5, stage1={"passed": 20}),
            dict(sub, family="a", world_seed=3, status="liquidated", stage1={"passed": 20}),
            {"family": "a", "world_seed": 4, "submitted": False, "status": "not_submitted", "stage1": {"activity_dev": 20}}]
    s = K.null_summary(rows, ["a"])
    assert s["n_pairs"] == 4 and s["n_submitted"] == 3 and s["n_not_submitted"] == 1
    b = s["by_threshold"]["0.025"]
    assert b["tier1"] == 1 and b["pass_rate"] == 1 / 3 and b["pass_rate_all_pairs"] == 1 / 4
    assert b["gate_pass_rate_submitted"]["G1"] == 2 / 3                       # the liquidated pair fails every gate
    assert s["stage1_draws"] == {"passed": 43, "activity_dev": 37}
    assert s["submitted_status"] == {"evaluated": 2, "liquidated": 1}


def test_stage1_filter_and_dev_sharpe_selection_on_a_synthetic_world():
    w = synth_world(seed=4)
    frames_dev, btc_dev = K.dev_view(w)
    prog = L.parse_file(K.family_path("gen000_sma_cross_ls"))
    q = L.default_params(prog)
    s1 = pipeline.stage1(prog, q, frames_dev, btc_dev, np.random.default_rng(1), pipeline.Opts(truncation_cuts=3))
    assert s1["ok"] and np.isfinite(K.dev_sharpe(frames_dev, w.liq, s1))
    assert frames_dev[C.BTC].index[-1] == pd.Timestamp(C.DEV_END, tz="UTC")
