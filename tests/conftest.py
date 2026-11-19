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
    from omr import probe
    return {"klines": kl, "funding": fu, "mark_klines": mk, "index_klines": probe.index_bars(kl)}


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


def _pad(raw: dict, start: str, end: str | None = None, gap: bool = False) -> dict:
    """Make the klines rows in [start, end] inactive: padding (frozen last close, zero volume and trades)
    or, with gap=True, missing rows (is_gap). Mark, index and funding rows there are dropped."""
    kl = raw["klines"].copy()
    a = pd.Timestamp(start, tz="UTC")
    b = pd.Timestamp(end, tz="UTC") if end else kl.index[-1]
    m = (kl.index >= a) & (kl.index <= b)
    last = kl.loc[kl.index < a, "close"].iloc[-1]
    for c in ("open", "high", "low", "close"):
        kl.loc[m, c] = last
    for c in ("volume", "quote_volume", "trades", "taker_buy_volume", "taker_buy_quote_volume"):
        kl.loc[m, c] = 0.0
    kl.loc[m, "is_gap"] = gap
    out = dict(raw, klines=kl)
    for d in ("mark_klines", "index_klines", "funding"):
        t = raw[d]
        out[d] = t[(t.index < a) | (t.index > b)]
    return out


# the traps of the real archive (KP-015 B4), in a synthetic universe
TRAP_DEAD, TRAP_RELIST, TRAP_HOLE, TRAP_TRADFI, TRAP_INDEX = ("DEADUSDT", "RELISTUSDT", "HOLEUSDT", "TRADFIUSDT",
                                                              "INDEXUSDT")
TRAP_LONGHOLE, TRAP_NOFUND = "LONGHOLEUSDT", "NOFUNDUSDT"
DEAD_AT, RELIST_FROM, RELIST_TO, HOLE_DAY = ("2021-06-15 00:00", "2021-03-01 00:00", "2021-04-30 23:00",
                                             "2021-09-10 00:00")
NOFUND_FROM, NOFUND_TO = "2021-06-01 00:00", "2021-08-31 23:00"


def synth_universe(seed=5, n=36, end="2025-06-30 23:00", traps=True):
    """(tables, symbols table, BTCUSDT frame): n listed coins U00.. (listings every 12 days from 2019-09-09,
    quote volume scaled so liquidity ranks differ) plus, with traps, a delisted coin padded to the end, a
    relisted coin (two months of padding), a coin with a three-day archive hole (does not restart the
    seasoning), one with an eight-day hole (restarts it), one whose funding is missing for three months
    (R2: out of play), and a TradFi and an index name with the largest volume (never members)."""
    rng = np.random.default_rng(seed)
    t0 = pd.Timestamp("2019-09-09 00:00", tz="UTC")
    tables, table = {}, {"symbols": {}}
    names = [f"U{i:02d}USDT" for i in range(n)]
    if traps:
        names += [TRAP_DEAD, TRAP_RELIST, TRAP_HOLE, TRAP_TRADFI, TRAP_INDEX, TRAP_LONGHOLE, TRAP_NOFUND]
    for i, s in enumerate(names):
        start = t0 + pd.Timedelta(days=12 * (i % n)) if s.startswith("U") else t0 + pd.Timedelta(days=5)
        raw = synth_raw(start=str(start)[:16], end=end, seed=seed * 1000 + i, price0=float(np.exp(rng.normal(3, 1))))
        scale = float(np.exp(rng.normal(0.0, 1.0)))
        if s in (TRAP_DEAD, TRAP_TRADFI, TRAP_INDEX, TRAP_RELIST, TRAP_HOLE, TRAP_LONGHOLE, TRAP_NOFUND):
            scale = 50.0                                           # always the most liquid
        raw["klines"]["quote_volume"] = raw["klines"]["quote_volume"] * scale
        if s == TRAP_DEAD:
            raw = _pad(raw, DEAD_AT)
        elif s == TRAP_RELIST:
            raw = _pad(raw, RELIST_FROM, RELIST_TO)
        elif s in (TRAP_HOLE, TRAP_LONGHOLE):
            days = 3 if s == TRAP_HOLE else 8
            raw = _pad(raw, HOLE_DAY, str(pd.Timestamp(HOLE_DAY) + pd.Timedelta(hours=24 * days - 1))[:16], gap=True)
        elif s == TRAP_NOFUND:
            fu = raw["funding"]
            raw["funding"] = fu[(fu.index < pd.Timestamp(NOFUND_FROM, tz="UTC")) | (fu.index > pd.Timestamp(NOFUND_TO, tz="UTC"))]
        tables[s] = raw
        cls = {TRAP_TRADFI: "tradfi_perpetual", TRAP_INDEX: "index_contract"}.get(s, "crypto_perpetual")
        table["symbols"][s] = {"class": cls, "until": None, "n_months": 1}
    btc = D.assemble_frame(synth_raw(start="2019-09-09 00:00", end=end, seed=seed + 7), D.PROGRAM_EXTRA)
    return tables, table, btc


def synth_udata(end="2025-06-30 23:00", seed=5, n=36, traps=True):
    from omr import upipeline as UP
    tables, table, btc = synth_universe(seed=seed, n=n, end="2025-06-30 23:00", traps=traps)
    return UP.udata_from_tables(tables, btc, end, symbols_table=table)


class SynthProvider:
    """evaluate.py data provider over a synthetic world (tests only); universe: (UData dev, UData full)."""

    def __init__(self, world, rh="synthetic-research-hash", universe=None):
        self.world = world
        self.rh = rh
        self.universe = universe

    def udev(self):
        return self.universe[0]

    def uval(self, handle, fields=None):
        from omr import access
        access.require(handle, "SynthProvider.uval")
        return self.universe[1]

    def universe_sizes(self):
        from omr import universe as U
        ud = self.universe[1]
        g = ud.grid()
        return U.stage2_sizes(ud.acts, ud.membership(g[0].value, g[-1].value), g[0].value, g[-1].value)

    def check(self):
        return self.rh

    def dev_frames(self):
        return dev_only(self.world)

    def val_world(self, handle):
        from omr import access
        access.require(handle, "SynthProvider.val_world")
        return self.world


@pytest.fixture(autouse=True)
def _never_touch_the_real_ledger_logs(tmp_path_factory, monkeypatch):
    """The kernel never redirects the VAL access log or the real trial ledger; the TESTS point them at
    a temp folder so no test writes to the project's ledger."""
    d = tmp_path_factory.mktemp("real_ledger")
    monkeypatch.setattr(P, "VAL_ACCESS_LOG", d / "val_access_log.jsonl")
    monkeypatch.setattr(P, "REAL_TRIALS_JSONL", d / "trials.jsonl")
    return d


def make_disk_data(root, symbols=C.ALL_SYMBOLS, end="2025-06-30 23:00", universe=False):
    """A disk-like data folder (parquet files + manifest) with synthetic data for `symbols`, so the
    real disk loaders (omr.datasets / omr.data) can be exercised without real data. universe=True adds
    the synthetic universe (synth_universe) and a symbols.json pinned in the manifest."""
    from omr import data
    import hashlib
    import json as _json
    starts = {"BTCUSDT": "2019-09-09 00:00", "ETHUSDT": "2019-11-28 00:00"}
    tables = {}
    for i, s in enumerate(symbols):
        raw = synth_raw(start=starts.get(s, "2020-01-06 00:00"), end=end, seed=200 + i)
        for ds in ("klines", "funding", "mark_klines", "index_klines"):
            tables[(ds, s)] = raw[ds]
    man = {"datasets": {}}
    if universe:
        ut, table, _ = synth_universe(seed=5, n=52)
        for s, raw in ut.items():
            for ds in ("klines", "funding", "mark_klines", "index_klines"):
                tables[(ds, s)] = raw[ds]
        for s in symbols:
            table["symbols"][s] = {"class": "crypto_perpetual", "until": None, "n_months": 1}
        b = _json.dumps(table).encode("ascii")
        (root / "symbols.json").write_bytes(b)
        man["universe"] = {"symbols_sha256": hashlib.sha256(b).hexdigest()}
        from omr import upipeline as UP
        ud = UP.udata_from_tables(ut, D.assemble_frame(ut["U00USDT"], D.PROGRAM_EXTRA), C.VAL_END, symbols_table=table)
        from omr import universe as U
        g = ud.grid()
        sizes = U.stage2_sizes(ud.acts, ud.membership(g[0].value, g[-1].value), g[0].value, g[-1].value)
        (root / "validation.json").write_text(_json.dumps({"universe_membership": {"stage2_sizes": sizes}}),
                                              encoding="ascii")
    for (ds, s), df in tables.items():
        p = root / ds / f"{s}.parquet"
        p.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(p)
        man["datasets"].setdefault(ds, {})[s] = {"sha256": data.sha256_file(p)}
    man["research_hash"] = data.compute_research_hash(tables)
    import json
    (root / "manifest.json").write_text(json.dumps(man), encoding="ascii")
    return man["research_hash"]


@pytest.fixture(autouse=True)
def _plenty_of_memory(monkeypatch):
    """R3's refusal depends on this machine's free memory; tests fix it (test_r3_* check the real reader and
    the refusal itself)."""
    from omr import upipeline as UP
    monkeypatch.setattr(UP, "available_memory_bytes", lambda: 10 ** 12)


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
