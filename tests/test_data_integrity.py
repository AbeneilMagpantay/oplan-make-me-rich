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
                         ("mark_klines", "BTCUSDT"): raw["mark_klines"], ("index_klines", "BTCUSDT"): raw["index_klines"]})
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
                        ("mark_klines", "BTCUSDT"): raw["mark_klines"], ("index_klines", "BTCUSDT"): raw["index_klines"]})
    data._CACHE.clear()
    assert not data.validation_ok()
    bad = data.validate(log=lambda s: None)
    assert not bad["passed"] and bad["counts"]["klines/BTCUSDT/dev"]["nonpositive_price"] == 1
    assert bad["counts"]["klines/BTCUSDT/dev"]["ohlc_inconsistent"] >= 0 and not data.validation_ok()
    assert "nonpositive_price" in text


def _pin_symbols(root, table):
    """Write symbols.json, pin it in the manifest and rewrite the manifest's research hash with the fold."""
    import hashlib
    b = json.dumps(table, sort_keys=True).encode("ascii")
    (root / "symbols.json").write_bytes(b)
    man = json.loads((root / "manifest.json").read_text(encoding="ascii"))
    man["universe"] = {"symbols_sha256": hashlib.sha256(b).hexdigest()}
    man["research_hash"] = data.research_hash_from_disk(man)
    (root / "manifest.json").write_text(json.dumps(man), encoding="ascii")
    return man


def test_u5_the_symbol_table_is_in_the_research_hash_and_the_fingerprint(datadir, monkeypatch):
    from omr import lang as L
    from omr import universe as U
    monkeypatch.setattr(U, "SYMBOLS_FILE", datadir / "symbols.json")
    plain = data.research_hash_from_disk()                     # no universe stored: no fold, as before
    table = {"symbols": {"AAAUSDT": {"class": "crypto_perpetual", "until": None, "n_months": 3},
                         "BBBUSDT": {"class": "crypto_perpetual", "until": "2023-03-01 00:00", "n_months": 3}}}
    man = _pin_symbols(datadir, table)
    rh0, fp0 = data.research_hash_from_disk(), data.data_fingerprint()
    assert rh0 == man["research_hash"] and rh0 != plain
    assert data.validate(log=lambda s: None)["passed"] and data.validation_ok()
    from conftest import prog_text
    prog = L.parse(prog_text("signal = sign(ret(close, 1))\n"), "x_test", probe=False)
    tid0 = L.trial_id(prog, "s" * 64, rh0)
    seen = {rh0}
    for edit in (("AAAUSDT", "class", "tradfi_perpetual"), ("BBBUSDT", "until", "2023-04-01 00:00")):
        t = json.loads(json.dumps(table))
        t["symbols"][edit[0]][edit[1]] = edit[2]
        (datadir / "symbols.json").write_bytes(json.dumps(t, sort_keys=True).encode("ascii"))
        rh = data.research_hash_from_disk()
        assert rh not in seen                                   # one class or one `until` changes the hash
        seen.add(rh)
        assert data.data_fingerprint() != fp0 and not data.validation_ok()   # validation (and the seal) unbound
        assert L.trial_id(prog, "s" * 64, rh) != tid0           # and every trial id
    (datadir / "symbols.json").write_bytes(json.dumps(table, sort_keys=True).encode("ascii"))
    assert data.research_hash_from_disk() == rh0 and data.data_fingerprint() == fp0 and data.validation_ok()
