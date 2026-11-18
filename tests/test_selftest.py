"""D: the selftest returns ONLY "OK" or the failed assertion and file:line; no metric leaves it and its
temporary directory is removed (synthetic data; the CLI runs the same function on real data)."""
import re

from omr import paths as P
from omr import selftest
from conftest import SynthProvider, synth_world

LATE = ["2020-09-14 00:00", "2020-02-10 00:00", "2020-01-06 00:00", "2020-01-31 00:00", "2020-07-10 00:00",
        "2020-01-09 00:00", "2020-01-17 00:00", "2020-09-23 00:00"]


def test_selftest_ok_and_cleans_up(tmp_path):
    w = synth_world(seed=41, extended=8, ext_start=LATE)
    with P.temporary_ledger(tmp_path / "outer"):
        out = selftest.run(provider=SynthProvider(w), require_lock=False, p_max=0.05, tmp_parent=tmp_path)
        from omr import ledger
        log = ledger.read_rows(P.VAL_ACCESS_LOG)
    assert out == "OK"
    assert [r["kind"] for r in log] == ["selftest"]
    assert [p.name for p in tmp_path.iterdir()] == ["outer"]                 # the selftest's temp dir is gone
    assert not (tmp_path / "outer" / "trials.jsonl").exists()               # nothing reached the outer ledger


def test_selftest_failure_names_the_assertion_and_location_only(tmp_path):
    w = synth_world(seed=42, extended=0)                                     # no extended symbols: G8 cannot run
    with P.temporary_ledger(tmp_path / "outer"):
        out = selftest.run(provider=SynthProvider(w), require_lock=False, p_max=0.05, tmp_parent=tmp_path)
    assert re.fullmatch(r"[a-z0-9_]+ at omr/selftest\.py:\d+", out), out
    assert out.startswith("no_kernel_fault_kernel_noise_single")
    assert [p.name for p in tmp_path.iterdir()] == ["outer"]


def test_selftest_requires_a_sealed_lock(monkeypatch, tmp_path):
    from omr import kernel_lock
    monkeypatch.setattr(kernel_lock, "verify", lambda *a, **k: [])
    monkeypatch.setattr(kernel_lock, "read_lock", lambda *a, **k: {"combined": "c" * 64})
    out = selftest.run(provider=None, require_lock=True, tmp_parent=tmp_path)
    assert out.startswith("kernel_sealed at omr/selftest.py:")
