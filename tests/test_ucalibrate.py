"""KP-015 F: the universe calibration on synthetic panels (never run for real here): null worlds built
jointly across symbols, constant membership, the three hash-locked families, the screen-and-submit
protocol, the cross-sectional oracle, and the seal rule over both units."""
import numpy as np
import pandas as pd
import pytest

from conftest import synth_raw
from omr import calibrate as CB
from omr import constants as C
from omr import lang as L
from omr import pipeline as PL
from omr import ucalibrate as UC
from omr import universe as U
from omr import upipeline as UP


@pytest.fixture(scope="module")
def src():
    tables = {f"S{i:02d}USDT": synth_raw(start="2019-11-01 00:00", end=C.VAL_END, seed=700 + i,
                                         price0=float(10 + 7 * i)) for i in range(12)}
    return UC.USource(tables)


def test_families_are_top30_kernel_programs_within_the_lookback_limit():
    for f in UC.FAMILIES:
        p = L.parse_file(UC.family_path(f))
        assert p.unit == "top30" and p.kind == "portfolio" and p.lookback_hours <= C.LOOKBACK_MAX_HOURS
    with pytest.raises(ValueError):
        UC.family_path("gen000_donchian_ls")


def test_null_a_draws_one_source_day_for_every_symbol(src):
    ud = UC.build_uworld(src, "A", 3)
    a, b = src.symbols[0], src.symbols[3]
    ka, kb = ud.raw[a]["klines"], ud.raw[b]["klines"]
    assert ka.index.equals(kb.index) and ka.index[0] == pd.Timestamp(C.UNIVERSE_START, tz="UTC")
    # the hourly open-relative ratios of a world day are those of ONE source day, for both symbols
    ra = (ka["close"] / ka["open"]).to_numpy().reshape(-1, 24)
    rb = (kb["close"] / kb["open"]).to_numpy().reshape(-1, 24)
    for d in (10, 400, 1500):
        ia = int(np.argmin(np.abs(src.sym[a]["cr"] - ra[d]).sum(axis=1)))
        ib = int(np.argmin(np.abs(src.sym[b]["cr"] - rb[d]).sum(axis=1)))
        assert ia == ib and np.allclose(src.sym[a]["cr"][ia], ra[d])


def test_null_b_flips_every_symbol_with_one_coin_per_day(src):
    ud = UC.build_uworld(src, "B", 4)
    a, b = src.symbols[1], src.symbols[4]
    ra = (ud.raw[a]["klines"]["close"] / ud.raw[a]["klines"]["open"]).to_numpy().reshape(-1, 24)
    rb = (ud.raw[b]["klines"]["close"] / ud.raw[b]["klines"]["open"]).to_numpy().reshape(-1, 24)
    n = ra.shape[0]
    tail_a, tail_b = src.sym[a]["cr"][-200:], src.sym[b]["cr"][-200:]    # the world's last days = the pool's last days
    fa = [np.allclose(ra[n - 200 + i], 1.0 / tail_a[i]) and not np.allclose(ra[n - 200 + i], tail_a[i]) for i in range(200)]
    fb = [np.allclose(rb[n - 200 + i], 1.0 / tail_b[i]) and not np.allclose(rb[n - 200 + i], tail_b[i]) for i in range(200)]
    assert fa == fb and 60 < sum(fa) < 140


def test_constant_membership_and_its_known_window(src):
    ud = UC.build_uworld(src, "A", 5)
    g = ud.grid()
    mem = ud.membership(g[0].value, g[-1].value)
    for i, m in enumerate(mem.months):
        assert mem.known[i] == (m - U.SEASON_BLOCKS * U.DAY_NS >= g[0].value)
        assert mem.ranked[i] == (sorted(src.symbols) if mem.known[i] else [])
    cut = g[3000].value
    mc = ud.membership(cut, g[-1].value)
    assert mc.known.sum() < mem.known.sum()


def test_one_null_world_runs_the_protocol(src, val_handle, monkeypatch):
    monkeypatch.setattr(CB, "N_DRAWS", 2)
    monkeypatch.setattr(UC, "OPTS", PL.Opts(include_g8=False, keep_detail=False, perm_n=10, jitter_n=2,
                                            truncation_cuts=2, start_cuts=1, start_cuts_val=1))
    UC._W.clear()
    UC._W.update({"handle": val_handle, "src": src, "progs": {f: L.parse_file(UC.family_path(f)) for f in UC.FAMILIES}})
    rows = UC.task_null(("A", 11000))
    assert [r["family"] for r in rows] == list(UC.FAMILIES)
    sub = [r for r in rows if r["submitted"]]
    assert sub and all(r["status"] in ("evaluated", "liquidated") for r in sub)
    assert all("perm_p" in r and 0 < r["perm_p"] <= 1 for r in sub if r["status"] == "evaluated")
    summ = CB.null_summary(rows, list(UC.FAMILIES))
    assert summ["n_pairs"] == 3 and summ["n_submitted"] == len(sub)


def test_the_cross_sectional_oracle_is_market_neutral_and_has_power(src, val_handle):
    ud = UC.build_uworld(src, "A", 6)
    ob = UC.UOracle(ud, 1, 99)
    W = ob.weights(0.6)
    rows = W[ob.rows]
    live = np.abs(rows).sum(axis=1) > 0
    assert live.mean() > 0.8
    assert np.allclose(rows[live].sum(axis=1), 0.0, atol=1e-12) and np.allclose(np.abs(rows[live]).sum(axis=1), 1.0)
    assert ob.val_sharpe(0.6) > ob.val_sharpe(0.0) + 1.0                   # foresight pays
    res = UP.evaluate_weights_u(W, ob.bu, 1, PL.Opts(perm_n=20, include_g8=False), val_handle, 0.1)
    assert res["status"] == "evaluated" and res["gates"]["G8"]["pass"] is None and res["gates"]["G5"]["pass"]
