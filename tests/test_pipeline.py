"""Pipeline: activity (direction changes), gates G5-G8 and G10, G8 on late listings (synthetic and real
DEV-only frames), stage-1 truncation self-check, stage-2 DEV-row check, liquidation, VAL handles,
and the mark-price liquidation path (KP-001)."""
import json

import numpy as np
import pandas as pd
import pytest

from omr import access
from omr import constants as C
from omr import datasets as D
from omr import engine as E
from omr import interp as X
from omr import lang as L
from omr import ledger
from omr import paths as P
from omr import pipeline
from conftest import dev_only, kernel_program, prog_text, synth_raw, synth_world

FAST = pipeline.Opts(jitter_n=3, perm_n=30, truncation_cuts=4, include_g8=False)
LATE = ["2020-09-14 00:00", "2020-02-10 00:00", "2020-01-06 00:00", "2020-01-31 00:00", "2020-07-10 00:00",
        "2020-01-09 00:00", "2020-01-17 00:00", "2020-09-23 00:00"]          # real listing dates (SOL ... AVAX)
LONG = prog_text("x = param(0.8, 0.5, 1.0)\nsignal = x * sign(close / open)")


def test_direction_changes_count_state_changes_per_symbol():
    W = np.array([[0.0, 0.5], [0.3, 0.5], [0.3, -0.5], [0.005, -0.5], [-0.2, 0.0], [-0.2, 0.008], [0.4, 0.5]])
    # symbol 0 states: 0, 1, 1, 0, -1, -1, 1 -> changes at rows 1, 3, 4, 6 = 4
    # symbol 1 states: 1, 1, -1, -1, 0, 0, 1 -> changes at rows 2, 4, 6 = 3
    assert pipeline.direction_changes(W, 1, 6) == 7
    assert pipeline.direction_changes(W, 4, 6) == 4
    assert pipeline.direction_changes(np.full((5, 2), 0.25), 1, 4) == 0          # constant position: no change
    with pytest.raises(pipeline.KernelFault):
        pipeline.direction_changes(W, 0, 3)


def test_g10_and_activity_thresholds():
    assert pipeline.g10_rule(12)["pass"] and not pipeline.g10_rule(11)["pass"]
    assert C.G10_MIN_DIRECTION_CHANGES_VAL == 12 and C.MIN_DIRECTION_CHANGES_DEV == 20


def test_g5_g6_g7_g8_rules():
    assert pipeline.g5_rule(1.0, [0.8, 0.9, 0.7, 0.6, 1.1, 0.95, 0.85, 0.75])["pass"]
    assert not pipeline.g5_rule(1.0, [0.8, -0.1, -0.2, 0.3, 0.2, -0.3, 0.1, 0.2])["pass"]
    assert not pipeline.g5_rule(2.0, [0.5, 0.6, 0.7, 0.8, 0.9, 0.5, 0.6, 0.7])["pass"]
    assert pipeline.g6_p(2.0, np.linspace(-1, 1, 199)) == 1 / 200
    assert pipeline.g6_p(0.0, np.linspace(-1, 1, 199)) > 0.4
    assert pipeline.g7_rule([0.1, 0.12, 0.08, -0.05, 0.09, 0.07])["pass"]
    assert not pipeline.g7_rule([0.1, -0.1, -0.1, -0.1, 0.1, 0.2])["pass"]
    assert not pipeline.g7_rule([2.0, 0.01, 0.01, 0.01, 0.01, -0.1])["pass"]
    ok = [{"unit": str(i), "code": None, "sharpe": s} for i, s in enumerate([0.3, 0.1, -0.2, 0.4, 0.2, -0.1, 0.5, 0.05])]
    assert pipeline.g8_rule(ok)["pass"]
    # an unscorable unit counts as NOT positive
    one_short = ok[:4] + [{"unit": "x", "code": "short_history"}] * 4
    assert not pipeline.g8_rule(one_short)["pass"]


def test_jitter_moves_every_param_and_stays_in_bounds():
    prog = L.parse(prog_text("n = param(2, 1, 5)\nk = param(0.5, 0.25, 1.0)\nsignal = sma(ret(close, 1), n) * k"),
                   "x_test")
    vs = pipeline.jitter_params(prog, {"n": 2, "k": 0.5}, np.random.default_rng(0), 50)
    assert all(v["n"] in (1, 3) for v in vs)                                      # rounding never leaves it unchanged
    assert all(0.4 <= v["k"] <= 0.6 and v["k"] != 0.5 for v in vs)


def test_g8_scores_late_listings_on_synthetic_frames(val_handle):
    w = synth_world(seed=12, extended=8, ext_start=LATE)
    for stem, n in (("gen000_sma_cross_ls", 8), ("kernel_noise_portfolio", 4)):
        prog = kernel_program(stem)
        rows = pipeline.g8_scores(prog, L.default_params(prog), w)
        assert len(rows) == n and all(r["code"] is None and np.isfinite(r["sharpe"]) for r in rows), rows
        assert min(r["years"] for r in rows) < 5.0                                 # a late listing was scored from its own start


REAL = all((P.DATA_DIR / d / f"{s}.parquet").exists() for d in ("klines", "funding", "mark_klines") for s in C.ALL_SYMBOLS)


@pytest.mark.skipif(not REAL, reason="real data not downloaded")
def test_g8_scores_late_listings_on_real_dev_only_frames():
    ext = D.load_frames(C.EXTENDED, D.PROGRAM_EXTRA, upto="dev_end")
    core = D.load_frames(C.CORE, D.PROGRAM_EXTRA, upto="dev_end")
    liq = D.load_liqs(C.ALL_SYMBOLS, upto="dev_end")
    w = pipeline.World(core=core, extended=ext, btc=core[C.BTC], liq=liq)
    starts = {s: f.index[0] for s, f in ext.items()}
    assert max(starts.values()) > pd.Timestamp("2020-01-01", tz="UTC")             # really late listings
    for stem in ("gen000_sma_cross_ls", "gen000_rsi_meanrev_ls", "kernel_noise_portfolio"):
        prog = kernel_program(stem)
        rows = pipeline.g8_scores(prog, L.default_params(prog), w, end=C.DEV_END, min_years=1.0)
        assert len(rows) == (8 if prog.kind == "single" else 4)
        assert all(r["code"] is None and np.isfinite(r["sharpe"]) for r in rows), rows


def test_stage1_passes_a_causal_program_and_flags_a_non_causal_kernel(monkeypatch):
    w = synth_world(seed=13)
    fd, bd = dev_only(w)
    prog = kernel_program("gen000_sma_cross_ls")
    s1 = pipeline.stage1(prog, L.default_params(prog), fd, bd, np.random.default_rng(1), FAST)
    assert s1["ok"] and s1["cuts"] == 5 and s1["direction_changes_dev"] >= 20
    orig = X.Context.rolling

    def centred(self, fn, x, n):                     # a kernel bug: a centred (future-reading) window
        out = orig(self, fn, x, n)
        return X.S(np.roll(out.arr, -1, axis=0), out.tf, out.idx)
    monkeypatch.setattr(X.Context, "rolling", centred)
    s1 = pipeline.stage1(prog, L.default_params(prog), fd, bd, np.random.default_rng(1), FAST)
    assert not s1["ok"] and s1["code"] == "kernel_fault"


def test_stage2_without_an_extended_universe_is_a_kernel_fault(val_handle):
    w = synth_world(seed=18)
    prog = kernel_program("kernel_noise_single")
    with pytest.raises(pipeline.KernelFault):
        pipeline.stage2(prog, L.default_params(prog), w, None, pipeline.Opts(jitter_n=2, perm_n=10), val_handle, 1, 0.05)


def test_stage1_activity_dev():
    w = synth_world(seed=14)
    fd, bd = dev_only(w)
    prog = L.parse(LONG, "x_test")
    s1 = pipeline.stage1(prog, L.default_params(prog), fd, bd, np.random.default_rng(1), FAST)
    assert not s1["ok"] and s1["code"] == "activity_dev" and s1["direction_changes_dev"] == 0


def test_stage2_requires_dev_rows_equal_to_stage1(val_handle):
    w = synth_world(seed=15)
    fd, bd = dev_only(w)
    prog = kernel_program("kernel_noise_single")
    q = L.default_params(prog)
    s1 = pipeline.stage1(prog, q, fd, bd, np.random.default_rng(1), FAST)
    ok = pipeline.stage2(prog, q, w, s1, FAST, val_handle, 3, 0.05)
    assert ok["status"] == "evaluated" and ok["gates"]["G5"]["g5_vacuous"] is False
    bad = dict(s1, raw=s1["raw"].copy())
    bad["raw"][100, 0] += 1e-9
    res = pipeline.stage2(prog, q, w, bad, FAST, val_handle, 3, 0.05)
    assert res == {"status": "kernel_fault", "reason": "dev_rows_changed"}


def test_g5_is_vacuous_without_params(val_handle):
    w = synth_world(seed=16)
    fd, bd = dev_only(w)
    prog = L.parse(prog_text("v = daily(volume)\nsignal = 2 * rank(v / lag(v, 1), 1) - 1 + sign(ret(daily(close), 1))"),
                   "x_test")
    s1 = pipeline.stage1(prog, {}, fd, bd, np.random.default_rng(1), FAST)
    res = pipeline.stage2(prog, {}, w, s1, FAST, val_handle, 3, 0.05)
    assert res["gates"]["G5"] == {"pass": True, "value": None, "g5_vacuous": True}


def test_liquidation_is_a_final_status_without_metrics_or_timestamps(val_handle):
    w = synth_world(seed=17)
    t = pd.Timestamp("2023-03-01 05:00", tz="UTC")
    for s in C.CORE:
        w.core[s] = w.core[s].copy()
        w.liq[s] = w.liq[s].copy()
        w.liq[s].loc[t, "dn"] = 0.01
    prog = L.parse(LONG, "x_test")
    res = pipeline.stage2(prog, {"x": 1.0}, w, None, FAST, val_handle, 3, 0.05)
    assert res == {"status": "liquidated", "reason": "liquidation"}
    assert "2023" not in json.dumps(ledger.clean(res))


def test_val_entry_points_and_loaders_need_a_handle():
    w = synth_world(seed=2)
    prog = kernel_program("gen000_sma_cross_ls")
    with pytest.raises(PermissionError):
        pipeline.stage2(prog, L.default_params(prog), w, None, FAST, None, 1, 0.05)
    grid = pipeline.core_grid(w.core, w.symbols)
    with pytest.raises(PermissionError):
        pipeline.evaluate_weights(np.zeros((len(grid), 2)), grid, w, 1, FAST, None, 0.05)
    for fn, args in ((D.load_raw, ("klines", "BTCUSDT")), (D.load_frame, ("BTCUSDT", ())),
                     (D.load_frames, (("BTCUSDT",), ())), (D.load_liq, ("BTCUSDT",)), (D.load_liqs, (("BTCUSDT",),))):
        for upto in ("val_end", "latest"):
            with pytest.raises(PermissionError):
                fn(*args, upto=upto)
    with pytest.raises(PermissionError):
        access.ValHandle("forged", None, "x")


def test_logged_handles(tmp_path, monkeypatch):
    monkeypatch.setattr(P, "VAL_ACCESS_LOG", tmp_path / "val_access_log.jsonl")
    h = access.for_calibration("unit test purpose")
    s = access.for_selftest()
    assert isinstance(h, access.ValHandle) and s.purpose.startswith("selftest")
    rows = ledger.read_rows(tmp_path / "val_access_log.jsonl")
    assert [r["kind"] for r in rows] == ["calibration", "selftest"]
    assert ledger.verify_chain(tmp_path / "val_access_log.jsonl") == []
    with pytest.raises(ValueError):
        access.for_calibration("   ")


# ---------------------------------------------------------------- mark-price liquidation (KP-001)

def test_liquidation_ratios_use_mark_and_fall_back_to_last_price():
    raw = synth_raw(start="2022-03-01 00:00", end="2022-03-01 05:00", seed=1)
    kl = raw["klines"].copy()
    kl.iloc[2, kl.columns.get_loc("high")] = kl["open"].iloc[2] * 3.0
    idx = kl.index
    o = kl["open"]
    mark = pd.DataFrame({"open": o, "high": o * 1.01, "low": o * 0.99, "close": o, "samples": 3600.0},
                        index=idx).drop(idx[4])
    lq = D.liquidation_ratios(kl, mark)
    assert lq["has_mark"].tolist() == [True, True, True, True, False, True]
    assert abs(lq["up"].iloc[2] - 1.01) < 1e-12 and abs(lq["dn"].iloc[2] - 0.99) < 1e-12
    assert abs(lq["up"].iloc[4] - kl["high"].iloc[4] / kl["open"].iloc[4]) < 1e-12
    lq0 = D.liquidation_ratios(kl, None)
    assert abs(lq0["up"].iloc[2] - 3.0) < 1e-12 and not lq0["has_mark"].any()


def test_engine_liquidates_on_the_ratios_it_is_given():
    op = np.full(3, 100.0)
    dn = np.ones(3)
    zero = np.zeros(3)
    assert E.run_arrays(op, dn, np.array([1.0, 1.05, 1.0]), zero, np.full(3, -0.5))[7] == -1
    assert E.run_arrays(op, dn, np.array([1.0, 3.0, 1.0]), zero, np.full(3, -0.5))[7] == 1
    t1 = np.full(3, -1.0)
    assert E.run_arrays(op, dn, np.array([1.0, 1.97, 1.0]), zero, t1)[7] == -1
    assert E.run_arrays(op, dn, np.array([1.0, 1.98, 1.0]), zero, t1)[7] == 1


def test_market_takes_mark_ratios_from_liq_and_falls_back_without():
    raws = {s: synth_raw(start="2019-12-30 00:00", end="2020-01-03 23:00", seed=i) for i, s in enumerate(C.CORE)}
    frames = {s: D.assemble_frame(r, D.PROGRAM_EXTRA) for s, r in raws.items()}
    liq = {}
    for s, r in raws.items():
        o = r["klines"]["open"]
        mark = pd.DataFrame({"open": o, "high": o * 1.02, "low": o * 0.97, "close": o, "samples": 3600.0}, index=o.index)
        liq[s] = D.liquidation_ratios(r["klines"], mark)
    grid = frames["BTCUSDT"].index
    mk = pipeline.Market(frames, liq, grid, C.CORE)
    assert np.allclose(mk.up, 1.02) and np.allclose(mk.dn, 0.97)
    mk0 = pipeline.Market(frames, {}, grid, C.CORE)
    k = raws["BTCUSDT"]["klines"]
    assert np.allclose(mk0.up[:, 0], (k["high"] / k["open"]).to_numpy())


@pytest.mark.skipif(not REAL, reason="real data not downloaded")
def test_real_eth_wick_half_equity_short_is_not_liquidated():
    def ts(s):
        return pd.Timestamp(s, tz="UTC").as_unit("ns")
    kl = D.load_raw("klines", "ETHUSDT", upto="dev_end")
    lq = D.load_liq("ETHUSDT", upto="dev_end")
    a, b = ts("2020-03-12 20:00"), ts("2020-03-13 06:00")
    seg, l_ = kl.loc[a:b], lq.loc[a:b]
    t02 = ts("2020-03-13 02:00")
    assert kl.loc[t02, "high"] == 323.0 and kl.loc[t02, "open"] == 95.73
    assert bool(l_.loc[t02, "has_mark"]) and l_.loc[t02, "up"] < 1.3
    op = seg["open"].to_numpy()
    tgt = np.full(len(seg), -0.5)
    zero = np.zeros(len(seg))
    assert E.run_arrays(op, l_["dn"].to_numpy(), l_["up"].to_numpy(), zero, tgt)[7] == -1
    liq_last = E.run_arrays(op, (seg["low"] / seg["open"]).to_numpy(), (seg["high"] / seg["open"]).to_numpy(), zero, tgt)[7]
    assert seg.index[liq_last] == t02
    frame = D.load_frame("ETHUSDT", D.PROGRAM_EXTRA, upto="dev_end")
    mk = pipeline.Market({"ETHUSDT": frame}, {"ETHUSDT": lq}, frame.index, ("ETHUSDT",))
    s = int(frame.index.get_loc(a))
    e = int(frame.index.get_loc(b))
    assert not mk.run(np.full((len(frame), 1), -0.5), s, e).liquidated
