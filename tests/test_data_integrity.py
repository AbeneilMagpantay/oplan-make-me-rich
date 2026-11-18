"""B4 / B9 / B10: every stored file is hashed at the moment it is read (a modified file is caught in both
stages), and `data validate` writes counts bound to the data fingerprint (synthetic temp data dir)."""
import json

import numpy as np
import pytest

from omr import data
from omr import datasets as D
from conftest import synth_raw


@pytest.fixture
def datadir(tmp_path, monkeypatch):
    monkeypatch.setattr(data, "DATA_DIR", tmp_path)
    monkeypatch.setattr(data, "MANIFEST", tmp_path / "manifest.json")
    monkeypatch.setattr(data, "VALIDATION", tmp_path / "validation.json")
    data._CACHE.clear()
    raw = synth_raw(start="2019-12-20 00:00", end="2022-07-10 23:00", seed=3)
    write_all(tmp_path, {("klines", "BTCUSDT"): raw["klines"], ("funding", "BTCUSDT"): raw["funding"],
                         ("mark_klines", "BTCUSDT"): raw["mark_klines"]})
    yield tmp_path
    data._CACHE.clear()


def write_all(root, tables):
    man = {"datasets": {}}
    for (ds, s), df in tables.items():
        p = root / ds / f"{s}.parquet"
        p.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(p)
        man["datasets"].setdefault(ds, {})[s] = {"sha256": data.sha256_file(p)}
    man["research_hash"] = data.compute_research_hash(tables)
    (root / "manifest.json").write_text(json.dumps(man), encoding="ascii")


def test_reads_verify_the_hash_at_read_and_catch_a_modified_file(datadir):
    df = data._read_stored("klines", "BTCUSDT")
    assert len(df) > 1000
    assert data.research_hash_from_disk() == data.load_manifest()["research_hash"]
    frame = D.load_frame("BTCUSDT", D.PROGRAM_EXTRA, upto="dev_end")             # the stage-1 path
    assert frame.index[-1] == data.ts("2022-06-30 23:00")
    mod = df.copy()
    mod.iloc[500, mod.columns.get_loc("close")] *= 1.0001                        # an edit inside DEV
    mod.to_parquet(datadir / "klines" / "BTCUSDT.parquet")
    with pytest.raises(data.DataIntegrityError):
        data._read_stored("klines", "BTCUSDT")
    with pytest.raises(data.DataIntegrityError):
        D.load_frame("BTCUSDT", D.PROGRAM_EXTRA, upto="dev_end")
    with pytest.raises(data.DataIntegrityError):
        data.research_hash_from_disk()


def test_a_file_missing_from_the_manifest_is_refused(datadir):
    (datadir / "klines" / "ETHUSDT.parquet").write_bytes((datadir / "klines" / "BTCUSDT.parquet").read_bytes())
    with pytest.raises(data.DataIntegrityError):
        data._read_stored("klines", "ETHUSDT")


def test_validate_counts_and_binding(datadir):
    out = data.validate(log=lambda s: None)
    assert out["passed"] and out["failures"] == 0 and data.validation_ok()
    c = out["counts"]
    assert c["klines/BTCUSDT/dev"]["rows"] > 0 and c["klines/BTCUSDT/dev"]["nonpositive_price"] == 0
    assert c["mark_klines/BTCUSDT/dev"]["mark_bars_on_grid"] == c["mark_klines/BTCUSDT/dev"]["grid_bars"]
    assert set(k.split("/")[2] for k in c) >= {"warmup", "dev", "val", "timestamps_bad"}
    text = (datadir / "validation.json").read_text()
    assert all(isinstance(v, int) for k, d in c.items() for v in d.values())     # counts only, no prices
    # new data (fingerprint change) invalidates the stored validation
    raw = synth_raw(start="2019-12-20 00:00", end="2022-07-10 23:00", seed=4)
    kl = raw["klines"].copy()
    kl.iloc[700, kl.columns.get_loc("low")] = -1.0                               # a non-positive price
    write_all(datadir, {("klines", "BTCUSDT"): kl, ("funding", "BTCUSDT"): raw["funding"],
                        ("mark_klines", "BTCUSDT"): raw["mark_klines"]})
    data._CACHE.clear()
    assert not data.validation_ok()
    bad = data.validate(log=lambda s: None)
    assert not bad["passed"] and bad["counts"]["klines/BTCUSDT/dev"]["nonpositive_price"] == 1
    assert bad["counts"]["klines/BTCUSDT/dev"]["ohlc_inconsistent"] >= 0 and not data.validation_ok()
    assert "nonpositive_price" in text
