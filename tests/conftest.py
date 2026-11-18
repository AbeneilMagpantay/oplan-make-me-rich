"""Shared synthetic-data helpers for the kernel tests (no network, no real data unless a test says so)."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from omr import constants as C  # noqa: E402
from omr import datasets as D  # noqa: E402
from omr import lang as L  # noqa: E402
from omr import paths as P  # noqa: E402

PROGRAMS = ROOT / "omr" / "programs"
BASELINES = ("gen000_sma_cross_ls", "gen000_donchian_ls", "gen000_rsi_meanrev_ls", "gen000_voltarget_trend_ls",
             "gen000_funding_carry")


def synth_raw(start="2021-01-01 00:00", end="2022-06-30 23:00", seed=0, drift=0.0, vol=0.01,
              funding_every=8, funding_rate=0.0001, price0=100.0):
    """Random-walk 1h klines on a complete grid, mark-price klines close to them, and funding
    settlements every `funding_every` hours."""
    rng = np.random.default_rng(seed)
    idx = pd.date_range(pd.Timestamp(start, tz="UTC"), pd.Timestamp(end, tz="UTC"), freq="h").as_unit("ns")
    n = len(idx)
    lr = drift + vol * rng.standard_normal(n)
    close = price0 * np.exp(np.cumsum(lr))
    opn = np.r_[price0, close[:-1]]
    spread = np.abs(vol * rng.standard_normal(n)) * close
    high = np.maximum(opn, close) + spread
    low = np.minimum(opn, close) - spread
    kl = pd.DataFrame({"open": opn, "high": high, "low": low, "close": close,
                       "volume": rng.uniform(1, 10, n), "quote_volume": rng.uniform(100, 1000, n),
                       "trades": rng.integers(10, 100, n).astype(float),
                       "taker_buy_volume": rng.uniform(0, 1, n), "taker_buy_quote_volume": rng.uniform(0, 100, n),
                       "is_gap": np.zeros(n, dtype=bool)}, index=idx)
    kl.index.name = "open_time"
    m = 1.0 + 0.0005 * rng.standard_normal(n)
    mo, mc = opn * m, close * m
    mk = pd.DataFrame({"open": mo, "high": np.maximum(mo, mc) + spread * 0.9, "low": np.minimum(mo, mc) - spread * 0.9,
                       "close": mc, "samples": 3600.0}, index=idx)
    mk.index.name = "open_time"
    ft = idx[idx.hour % funding_every == 0]
    fu = pd.DataFrame({"rate": funding_rate + 0.0001 * rng.standard_normal(len(ft)),
                       "interval_hours": float(funding_every), "offset_ms": 0.0}, index=ft)
    fu.index.name = "settle_time"
    return {"klines": kl, "funding": fu, "mark_klines": mk}


def synth_frame(**kw):
    return D.assemble_frame(synth_raw(**kw), D.PROGRAM_EXTRA)


def synth_frames(symbols=("BTCUSDT", "ETHUSDT"), **kw):
    seed = kw.pop("seed", 0)
    return {s: synth_frame(seed=seed + i, **kw) for i, s in enumerate(symbols)}


def liq_of(raw: dict):
    return D.liquidation_ratios(raw["klines"], raw["mark_klines"])


def synth_world(seed=11, extended=0, ext_start="2020-01-01 00:00", end="2025-06-30 23:00", **kw):
    """Core symbols start at different times, as in the real data (BTC 2019-09, ETH 2019-11)."""
    from omr import pipeline
    raws = {"BTCUSDT": synth_raw(start="2019-09-09 00:00", end=end, seed=seed, **kw),
            "ETHUSDT": synth_raw(start="2019-11-28 00:00", end=end, seed=seed + 1, **kw)}
    starts = ext_start if isinstance(ext_start, (list, tuple)) else [ext_start] * len(C.EXTENDED)
    for i, s in enumerate(C.EXTENDED[:extended]):
        raws[s] = synth_raw(start=starts[i], end=end, seed=seed + 100 + i, **kw)
    frames = {s: D.assemble_frame(r, D.PROGRAM_EXTRA) for s, r in raws.items()}
    liq = {s: liq_of(r) for s, r in raws.items()}
    core = {s: frames[s] for s in C.CORE}
    ext = {s: frames[s] for s in C.EXTENDED[:extended]}
    return pipeline.World(core=core, extended=ext, btc=core["BTCUSDT"], liq=liq, symbols=C.CORE)


def dev_only(world):
    """DEV-only copy of the core frames (what stage 1 receives)."""
    cap = pd.Timestamp(C.DEV_END, tz="UTC")
    frames = {s: f.loc[:cap] for s, f in world.core.items()}
    return frames, frames["BTCUSDT"]


def program(text: str, stem: str = "x_test"):
    return L.parse(text, stem)


def prog_text(body: str, kind="single", name="x_test", family="other",
              hypothesis="test program for the kernel test suite"):
    return f'name = "{name}"\nfamily = "{family}"\nkind = "{kind}"\nhypothesis = "{hypothesis}"\n' + body


def kernel_program(stem: str):
    return L.parse_file(PROGRAMS / f"{stem}.omr")


class SynthProvider:
    """evaluate.py data provider over a synthetic world (tests only)."""

    def __init__(self, world, rh="synthetic-research-hash"):
        self.world = world
        self.rh = rh

    def check(self):
        return self.rh

    def dev_frames(self):
        return dev_only(self.world)

    def val_world(self, handle):
        from omr import access
        access.require(handle, "SynthProvider.val_world")
        return self.world


@pytest.fixture
def val_handle(tmp_path, monkeypatch):
    """A calibration-purpose ValHandle whose access-log row goes to a temp file."""
    from omr import access
    monkeypatch.setattr(P, "VAL_ACCESS_LOG", tmp_path / "val_access_log.jsonl")
    return access.for_calibration("pytest")


@pytest.fixture
def tmp_ledger(tmp_path):
    """Point every trial-ledger path (and the generations folder) at a temp directory."""
    led = tmp_path / "ledger"
    gens = tmp_path / "generations"
    (gens / "gen000").mkdir(parents=True)
    (gens / "gen000" / "PLAN.md").write_text("test plan\n", encoding="ascii")
    with P.temporary_ledger(led, generations=gens):
        yield led
