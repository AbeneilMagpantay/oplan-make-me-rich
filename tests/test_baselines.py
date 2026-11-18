"""B12 + FIX PASS 5: the five .omr baselines reproduce independent naive references of the CURRENT
definitions (tests/ref_gen0.py) weight for weight, on synthetic data and the real DEV frames, at the
defaults and at random parameter draws. Against the pre-language Python strategies ("before"): SMA
cross and funding carry are bit-identical; the vol-target trend differs only by rounding (fixed-order
window sums); Donchian and RSI changed by rule (the windowed hold, the finite RSI) and agree on every
row where the new program is known, up to the finite-RSI rows reported."""
import numpy as np
import pytest

from omr import constants as C
from omr import datasets as D
from omr import lang as L
from omr import paths as P
from omr import pipeline
from conftest import BASELINES, kernel_program, synth_raw
from ref_gen0 import PY_BOUNDS, PY_DEFAULTS, PY_MAP, old_weights, reference_weights


def carry_world(seed=5):
    """Synthetic core frames whose funding drifts through the carry thresholds."""
    frames = {}
    for i, (s, start) in enumerate((("BTCUSDT", "2019-09-09 00:00"), ("ETHUSDT", "2019-11-28 00:00"))):
        raw = synth_raw(start=start, end="2022-06-30 23:00", seed=seed + i)
        fu = raw["funding"]
        t = np.arange(len(fu))
        rng = np.random.default_rng(seed + 10 + i)
        fu["rate"] = 0.0002 + 0.0005 * np.sin(t / (40.0 + 7 * i)) + 0.0001 * rng.standard_normal(len(fu))
        frames[s] = D.assemble_frame(raw, D.PROGRAM_EXTRA)
    return frames


def kernel_weights(stem, q, frames):
    prog = kernel_program(stem)
    grid = pipeline.core_grid(frames, C.CORE)
    W, raw, kn = pipeline.unit_full(prog, q, frames, C.CORE, frames[C.BTC], grid)
    return W, kn, grid


def diff_rows(stem, q, frames):
    W, kn, grid = kernel_weights(stem, q, frames)
    R = reference_weights(stem, q, frames, C.CORE, grid)
    return np.nonzero(~np.all(W == R, axis=1))[0], W, R, grid


def draws(stem, n, seed):
    prog = kernel_program(stem)
    rng = np.random.default_rng(seed)
    out = [L.default_params(prog)]
    for _ in range(n):
        out.append({k: (int(rng.integers(int(p.low), int(p.high) + 1)) if p.is_int else float(rng.uniform(p.low, p.high)))
                    for k, p in prog.params.items()})
    return out


@pytest.mark.parametrize("stem", BASELINES)
def test_defaults_and_bounds_are_the_python_ones(stem):
    prog = kernel_program(stem)
    mp = PY_MAP[stem]
    assert mp(L.default_params(prog)) == pytest.approx(PY_DEFAULTS[stem], rel=0, abs=1e-12)
    lows = mp({k: p.low for k, p in prog.params.items()})
    highs = mp({k: p.high for k, p in prog.params.items()})
    assert set(lows) == set(PY_BOUNDS[stem])
    for k, (lo, hi) in PY_BOUNDS[stem].items():
        assert (lows[k], highs[k]) == pytest.approx((lo, hi), rel=0, abs=1e-12), k


@pytest.mark.parametrize("stem", BASELINES)
def test_identical_weights_to_the_naive_reference_on_synthetic_data(stem):
    frames = carry_world()
    for i, q in enumerate(draws(stem, 4, seed=BASELINES.index(stem) + 1)):
        bad, W, R, grid = diff_rows(stem, q, frames)
        assert len(bad) == 0, f"{stem} {q}: {len(bad)} differing rows, first at {grid[bad[0]]}: {W[bad[0]]} vs {R[bad[0]]}"
        if i == 0:
            assert np.abs(W).sum() > 0, f"{stem} defaults: never in the market on this world"


REAL = all((P.DATA_DIR / d / f"{s}.parquet").exists() for d in ("klines", "funding", "mark_klines") for s in C.CORE)


@pytest.mark.skipif(not REAL, reason="real data not downloaded")
@pytest.mark.parametrize("stem", BASELINES)
def test_identical_weights_to_the_naive_reference_on_real_dev_frames(stem):
    frames = D.load_frames(C.CORE, D.PROGRAM_EXTRA, upto="dev_end")
    for q in draws(stem, 2, seed=7):
        bad, W, R, grid = diff_rows(stem, q, frames)
        assert len(bad) == 0, f"{stem} {q}: {len(bad)} differing rows, first at {grid[bad[0]]}: {W[bad[0]]} vs {R[bad[0]]}"


@pytest.mark.skipif(not REAL, reason="real data not downloaded")
@pytest.mark.parametrize("stem", BASELINES)
def test_against_the_pre_language_python_on_real_dev(stem):
    """The "before": exact for SMA cross and carry; rounding-level for the vol target; for Donchian and
    RSI (changed rules) equal wherever the new program is known, except a few finite-RSI rows."""
    frames = D.load_frames(C.CORE, D.PROGRAM_EXTRA, upto="dev_end")
    q = L.default_params(kernel_program(stem))
    W, kn, grid = kernel_weights(stem, q, frames)
    O = old_weights(stem, q, frames, C.CORE, grid)
    if stem in ("gen000_sma_cross_ls", "gen000_funding_carry"):
        assert np.array_equal(W, O)
    elif stem == "gen000_voltarget_trend_ls":
        assert np.max(np.abs(W - O)) <= 1e-12 and np.array_equal(np.sign(W), np.sign(O))
    else:
        rows = kn.all(axis=1)
        differ = int(np.sum(~np.all(W[rows] == O[rows], axis=1)))
        limit = 0 if stem == "gen000_donchian_ls" else int(0.005 * rows.sum())
        assert differ <= limit, (stem, differ, int(rows.sum()))
