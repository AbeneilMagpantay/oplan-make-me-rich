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


def test_the_dry_run_reads_no_real_bar(monkeypatch):
    """M3: --unlocked-dry-run builds its worlds from fully synthetic core tables."""
    from omr import datasets as D

    def refuse(*a, **k):
        raise AssertionError("the dry run read stored data")
    monkeypatch.setattr(D, "load_raw", refuse)
    src = K.Source(tables=K.synthetic_tables())
    w = K.build_world(src, "B", 3)
    grid = pipeline.core_grid(w.core, C.CORE)
    assert grid[-1] == pd.Timestamp(C.VAL_END, tz="UTC") and grid[0] < pd.Timestamp(C.DEV_START, tz="UTC")


def test_draws_are_screened_and_only_the_submitted_one_gets_the_full_stage1(monkeypatch, val_handle):
    """M5: 20 draws screened with the activity rule only; the full stage 1 (self-checks) and stage 2 run
    once, for the submitted draw."""
    calls = {"screen": 0, "stage1": 0, "stage2": 0}
    for name in ("screen_dev", "stage1", "stage2"):
        orig = getattr(pipeline, name)

        def wrap(*a, _o=orig, _n=name, **k):
            calls[{"screen_dev": "screen"}.get(_n, _n)] += 1
            return _o(*a, **k)
        monkeypatch.setattr(pipeline, name, wrap)
    monkeypatch.setitem(K._W, "src", K.Source(tables=K.synthetic_tables()))
    monkeypatch.setitem(K._W, "progs", {"gen000_voltarget_trend_ls": L.parse_file(K.family_path("gen000_voltarget_trend_ls"))})
    monkeypatch.setitem(K._W, "handle", val_handle)
    monkeypatch.setattr(K, "OPTS", pipeline.Opts(include_g8=False, keep_detail=False, perm_n=20, jitter_n=2))
    rows = K.task_null(("A", 1000))
    assert calls["screen"] == K.N_DRAWS and calls["stage1"] == 1 and calls["stage2"] == 1
    assert rows[0]["submitted"] and rows[0]["status"] == "evaluated"


# ---------------------------------------------------------------- fix pass 7: R-L family bound (FAMILY_PASS_MAX)

_GATES = ("G1", "G2", "G3", "G4", "G5", "G7", "G10")


def _row(fam, seed, p, g3=True, status="evaluated"):
    gates = {g: True for g in _GATES} | {"G6": None, "G8": None}
    gates["G3"] = g3
    return {"family": fam, "world_seed": seed, "submitted": True, "status": status, "params": {}, "val_sharpe": 0.1,
            "perm_p": p, "stage1": {"passed": 20}, "gates": gates}


def _null_rows(n_sub, passes=None):
    """n_sub: {family: submitted pairs}; passes: {family: [perm_p of its first rows]}; the rest have perm_p 0.5."""
    rows, seed = [], 0
    for f, n in n_sub.items():
        ps = list((passes or {}).get(f, []))
        for i in range(n):
            rows.append(_row(f, seed, ps[i] if i < len(ps) else 0.5))
            seed += 1
    return rows


def _oracle_rows():
    return [{"speed": s, "level": lvl, "world_seed": i, "status": "evaluated", "val_sharpe": lvl, "perm_p": 0.001,
             "rho": 0.1, "gates": {g: True for g in _GATES} | {"G6": None, "G8": None}}
            for s in K.SPEEDS for lvl in K.LEVELS for i in range(10)]


def _decide(rows_a, rows_b, fams):
    nulls = {"A": {"summary": K.null_summary(rows_a, fams)}, "B": {"summary": K.null_summary(rows_b, fams)}}
    oracle = {n: {"summary": K.oracle_summary(_oracle_rows())} for n in ("A", "B")}
    return K.decide(nulls, oracle), nulls


FIVE = ("a", "b", "c", "d", "e")


def test_r_l_a_one_family_above_the_bound_under_one_null_moves_the_threshold_down():
    assert C.FAMILY_PASS_MAX == 0.06 and C.NULL_PASS_MAX == 0.03
    n_sub = {f: 40 for f in FIVE}                                          # 200 submitted pairs per null
    rows_a = _null_rows(n_sub, {"a": [0.08, 0.08, 0.08]})                  # family a: 3 / 40 = 7.5% at 0.10 only
    rows_b = _null_rows(n_sub, {"a": [0.08]})
    v, _ = _decide(rows_a, rows_b, FIVE)
    assert v["null_pass_rate"]["A"]["0.1"] == 3 / 200 <= C.NULL_PASS_MAX      # the pooled bound alone keeps 0.10
    assert v["qualifying"] == [0.025, 0.05] and v["chosen_threshold"] == 0.05 and not v["STOP"]
    assert v["threshold_failures"] == {"0.025": [], "0.05": [], "0.1": ["null A: family a 0.0750 > FAMILY_PASS_MAX"]}
    assert v["family_pass_max"] == 0.06
    assert v["family_pass_rate"]["A"]["0.1"]["a"] == 3 / 40 and v["family_pass_rate"]["B"]["0.1"]["a"] == 1 / 40
    assert v["family_pass_rate"]["A"]["0.05"]["a"] == 0.0
    rows_b2 = _null_rows(n_sub, {"a": [0.08], "b": [0.01, 0.01, 0.01]})     # null B family b 7.5% at every threshold
    v2, _ = _decide(rows_a, rows_b2, FIVE)
    assert v2["STOP"] and v2["chosen_threshold"] is None and v2["qualifying"] == []
    for t in ("0.025", "0.05"):
        assert f"{t}: null B: family b 0.0750 > FAMILY_PASS_MAX" in v2["reason"]
    assert "0.1: null A: family a 0.0750 > FAMILY_PASS_MAX, null B: family b 0.0750 > FAMILY_PASS_MAX" in v2["reason"]
    rows_a3 = _null_rows(n_sub, {f: [0.04, 0.08] for f in FIVE[:4]})         # pooled 2% at 0.05, 4% at 0.10
    v3, _ = _decide(rows_a3, rows_b, FIVE)
    assert v3["threshold_failures"]["0.05"] == [] and v3["chosen_threshold"] == 0.05
    assert v3["threshold_failures"]["0.1"] == ["null A: pooled 0.0400 > NULL_PASS_MAX"]       # families at 5%: pooled


def test_r_l_b_a_family_at_exactly_the_bound_qualifies():
    n_sub = {f: 50 for f in FIVE}
    v, _ = _decide(_null_rows(n_sub, {"c": [0.08, 0.08, 0.08]}), _null_rows(n_sub, {"c": [0.08, 0.08, 0.08]}), FIVE)
    assert v["family_pass_rate"]["A"]["0.1"]["c"] == 3 / 50 == 0.06
    assert v["chosen_threshold"] == 0.1 and v["threshold_failures"]["0.1"] == [] and not v["STOP"]
    v4, _ = _decide(_null_rows(n_sub, {"c": [0.08] * 4}), _null_rows(n_sub), FIVE)       # 4 / 50 = 8%: refused
    assert v4["chosen_threshold"] == 0.05 and v4["threshold_failures"]["0.1"] == ["null A: family c 0.0800 > FAMILY_PASS_MAX"]


def test_r_l_c_a_family_without_a_submitted_pair_is_skipped():
    fams = ("a", "b", "c", "d", "e", "f")
    rows = _null_rows({f: 40 for f in ("a", "b", "c", "d")}, {"a": [0.08, 0.08]})
    rows += [{"family": "e", "world_seed": 900 + i, "submitted": False, "status": "not_submitted",
              "stage1": {"activity_dev": 20}} for i in range(10)]                     # e: pairs, none submitted
    v, nulls = _decide(rows, rows, fams)                                               # f: no pair at all
    for n in ("A", "B"):
        fr = nulls[n]["summary"]["by_threshold"]["0.1"]["family_pass_rate"]
        assert fr["e"] is None and fr["f"] is None and fr["a"] == 2 / 40
    assert v["chosen_threshold"] == 0.1 and not v["STOP"] and v["threshold_failures"]["0.1"] == []


def test_r_l_d_the_dev_positive_rate_is_information_only():
    rows = _null_rows({f: 40 for f in FIVE}, {"a": [0.08, 0.04]})
    for r in rows[100:150]:
        r["gates"]["G3"] = False                                                       # DEV-negative: 50 pairs
    rows[160]["status"] = "liquidated"                                                 # G3 True but not evaluated
    s = K.null_summary(rows, FIVE)
    assert s["n_dev_positive"] == 200 - 50 - 1
    assert s["by_threshold"]["0.1"]["pass_rate_dev_positive"] == 2 / 149
    assert s["by_threshold"]["0.05"]["pass_rate_dev_positive"] == 1 / 149
    v, nulls = _decide(rows, rows, FIVE)
    assert v["null_pass_rate_dev_positive"]["A"]["0.1"] == 2 / 149 and v["chosen_threshold"] == 0.1
    for fake in (0.99, None, 0.0):                                                     # whatever it says, same choice
        for n in ("A", "B"):
            for t in C.G6_GRID:
                nulls[n]["summary"]["by_threshold"][str(t)]["pass_rate_dev_positive"] = fake
        oracle = {n: {"summary": K.oracle_summary(_oracle_rows())} for n in ("A", "B")}
        w = K.decide(nulls, oracle)
        assert (w["chosen_threshold"], w["qualifying"], w["STOP"]) == (v["chosen_threshold"], v["qualifying"], v["STOP"])
    assert K.null_summary([], FIVE)["by_threshold"]["0.1"]["pass_rate_dev_positive"] is None
    assert K.PROTOCOL_VERSION == 4


# ---------------------------------------------------------------- fix pass 7b: fail-closed bounds, numpy gate values


def _redecide(nulls):
    return K.decide(nulls, {n: {"summary": K.oracle_summary(_oracle_rows())} for n in ("A", "B")})


def test_7b_1_a_rate_that_is_not_a_number_never_qualifies():
    n_sub = {f: 40 for f in FIVE}
    base, nulls = _decide(_null_rows(n_sub, {"a": [0.08]}), _null_rows(n_sub), FIVE)
    assert base["chosen_threshold"] == 0.1 and base["qualifying"] == [0.025, 0.05, 0.1]
    bt = {n: nulls[n]["summary"]["by_threshold"] for n in ("A", "B")}
    keep = bt["A"]["0.1"]["pass_rate"]
    bt["A"]["0.1"]["pass_rate"] = float("nan")                                  # pooled NaN, one threshold, null A
    v = _redecide(nulls)
    assert v["qualifying"] == [0.025, 0.05] and v["chosen_threshold"] == 0.05 and not v["STOP"]
    assert v["threshold_failures"]["0.1"] == ["null A: pooled nan is not a finite rate"]
    bt["A"]["0.1"]["pass_rate"] = float("inf")                                  # +inf: like any rate above the bound
    v = _redecide(nulls)
    assert v["chosen_threshold"] == 0.05 and v["threshold_failures"]["0.1"] == ["null A: pooled inf is not a finite rate"]
    bt["A"]["0.1"]["pass_rate"] = keep
    bt["B"]["0.1"]["family_pass_rate"]["c"] = float("nan")                      # family NaN, one threshold, null B
    v = _redecide(nulls)
    assert v["chosen_threshold"] == 0.05 and v["threshold_failures"]["0.1"] == ["null B: family c nan is not a finite rate"]
    bt["B"]["0.1"]["family_pass_rate"]["c"] = float("inf")
    v = _redecide(nulls)
    assert v["chosen_threshold"] == 0.05 and v["threshold_failures"]["0.1"] == ["null B: family c inf is not a finite rate"]
    bt["B"]["0.1"]["family_pass_rate"]["c"] = 0.0
    for t in C.G6_GRID:                                                          # NaN at every threshold: STOP
        bt["A"][str(t)]["pass_rate"] = float("nan")
    v = _redecide(nulls)
    assert v["STOP"] and v["chosen_threshold"] is None and v["qualifying"] == []
    for t in C.G6_GRID:
        assert f"{t}: null A: pooled nan is not a finite rate" in v["reason"]
    for t in C.G6_GRID:                                                          # family NaN at every threshold: STOP
        bt["A"][str(t)]["pass_rate"] = 0.0
        bt["A"][str(t)]["family_pass_rate"]["e"] = float("nan")
    v = _redecide(nulls)
    assert v["STOP"] and v["chosen_threshold"] is None
    assert K._bound_failure("A", "pooled", None, "NULL_PASS_MAX") == "null A: pooled rate missing (no submitted pair)"
    assert K._bound_failure("A", "pooled", "x", "NULL_PASS_MAX") == "null A: pooled 'x' is not a finite rate"


def test_7b_2_a_numpy_g3_counts_and_the_new_fields_survive_the_stored_form():
    import json
    from omr import ledger
    rows = _null_rows({f: 20 for f in FIVE}, {"a": [0.08, 0.04], "b": [0.5, 0.01]})     # passers rows 0, 1, 21
    for i, r in enumerate(rows):                                                 # numpy values as in memory
        r["gates"] = {k: (np.bool_(v) if isinstance(v, bool) else v) for k, v in r["gates"].items()}
        r["perm_p"] = np.float64(r["perm_p"])
        r["val_sharpe"] = np.float64(r["val_sharpe"])
        if i % 7 == 3:
            r["gates"]["G3"] = np.bool_(False)
        elif i % 7 == 5:                                                         # FP8-2: G3 None would be malformed
            r["status"] = "kernel_fault"
            del r["gates"], r["perm_p"]
        elif i % 7 == 6:
            r["gates"]["G3"] = False
    rows[1]["gates"]["G3"] = np.bool_(True)
    rows[8]["status"] = "liquidated"                                            # G3 True but not evaluated
    rows.append({"family": "c", "world_seed": 999, "submitted": False, "status": "not_submitted",
                 "stage1": {"activity_dev": 20}})
    want = sum(1 for i in range(100) if i % 7 not in (3, 5, 6) and i != 8)
    mem = K.null_summary(rows, FIVE)
    assert type(rows[0]["gates"]["G3"]) is np.bool_ and mem["n_dev_positive"] == want
    stored = K.null_summary(json.loads(json.dumps(ledger.clean(rows))), FIVE)
    assert stored["n_dev_positive"] == mem["n_dev_positive"]
    for t in C.G6_GRID:
        for k in ("family_pass_rate", "pass_rate_dev_positive", "pass_rate", "tier1"):
            assert stored["by_threshold"][str(t)][k] == mem["by_threshold"][str(t)][k], (t, k)
    assert mem["by_threshold"]["0.1"]["pass_rate_dev_positive"] == 3 / want
    one = {"family": "a", "world_seed": 0, "submitted": True, "status": "evaluated", "perm_p": 0.5, "params": {},
           "val_sharpe": 0.1, "stage1": {}}
    for g3, n in ((np.bool_(True), 1), (True, 1), (np.bool_(False), 0), (False, 0)):
        assert K.null_summary([dict(one, gates=dict(_row("a", 0, 0.5)["gates"], G3=g3))], ["a"])["n_dev_positive"] == n
    with pytest.raises(ValueError):                                              # FP8-2: an evaluated row needs G3
        K.null_summary([dict(one, gates=dict(_row("a", 0, 0.5)["gates"], G3=None))], ["a"])


def test_7b_3_a_power_or_achieved_mean_that_is_not_a_number_stops(monkeypatch):
    n_sub = {f: 40 for f in FIVE}
    _, nulls = _decide(_null_rows(n_sub), _null_rows(n_sub), FIVE)

    def run(edit):
        oracle = {n: {"summary": K.oracle_summary(_oracle_rows())} for n in ("A", "B")}
        edit(oracle)
        return K.decide(nulls, oracle)

    def setp(n, cell, x):
        return lambda o: o[n]["summary"][cell]["by_threshold"]["0.1"].__setitem__("power", x)

    def setm(n, cell, x):
        return lambda o: o[n]["summary"][cell].__setitem__("mean_val_sharpe", x)

    base = run(lambda o: None)
    assert base["chosen_threshold"] == 0.1 and not base["STOP"] and base["below_power_min"] == []
    v = run(setp("B", "slow|1.5", float("nan")))                                # NaN power at the chosen threshold
    assert v["STOP"] and v["below_power_min"] == ["B/slow"] and "B/slow" in v["reason"]
    v = run(setp("B", "slow|1.5", None))
    assert v["STOP"] and v["below_power_min"] == ["B/slow"]
    for x in (float("nan"), float("inf"), None):                                # achieved mean NaN / inf / None
        v = run(setm("A", "fast|1.0", x))
        assert v["STOP"] and v["oracle_level_outside_bound"] == ["A/fast|1.0"] and "A/fast|1.0" in v["reason"]
    v = run(setp("A", "fast|1.5", C.POWER_MIN))                                 # finite: exactly POWER_MIN is enough
    assert not v["STOP"] and v["below_power_min"] == []
    v = run(setp("A", "fast|1.5", np.nextafter(C.POWER_MIN, 0.0)))
    assert v["STOP"] and v["below_power_min"] == ["A/fast"]
    monkeypatch.setattr(K, "RHO_BOUND", 0.125)                                  # an exactly representable bound
    for x, inside in ((1.625, True), (1.375, True), (np.nextafter(1.625, 2.0), False), (np.nextafter(1.375, 0.0), False)):
        v = run(setm("B", "slow|1.5", x))
        assert (v["oracle_level_outside_bound"] == []) == inside, x
    monkeypatch.setattr(K, "RHO_BOUND", 0.1)
    x = 1.6
    for _ in range(4):
        x = np.nextafter(x, 0.0)
    for _ in range(9):                                                           # around 1.5 + 0.1: as the old rule
        v = run(setm("B", "slow|1.5", float(x)))
        assert ("B/slow|1.5" in v["oracle_level_outside_bound"]) == (abs(float(x) - 1.5) > 0.1), float(x)
        x = np.nextafter(x, 2.0)
