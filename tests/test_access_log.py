"""C3: the VAL access log cannot be redirected. A temporary ledger leaves VAL_ACCESS_LOG alone; a disk
load of VAL bars by a trial whose pending row is not in the REAL trial ledger is logged there
(kind temp_ledger_trial) before any frame is returned; logged-purpose handles issued inside a
temporary ledger are logged in the real log; synthetic providers log nothing.

The tests point the "real" log and the "real" trial ledger at a temp folder (conftest autouse
fixture), and the disk loaders at a synthetic data folder."""
import pytest

from omr import access
from omr import constants as C
from omr import data
from omr import datasets as D
from omr import evaluate
from omr import ledger
from omr import paths as P
from omr import pipeline
from omr import selftest
from conftest import SynthProvider, make_disk_data, prog_text, synth_world

FAST = pipeline.Opts(jitter_n=2, perm_n=10, truncation_cuts=2)
NOISE = prog_text("n = param(20, 10, 40)\nv = daily(volume)\nsignal = 2 * rank(v / lag(v, 1), n) - 1", name="t_noise")


@pytest.fixture(scope="module")
def disk_root(tmp_path_factory):
    root = tmp_path_factory.mktemp("disk_data")
    rh = make_disk_data(root, universe=True)
    return root, rh


@pytest.fixture
def disk(disk_root, monkeypatch):
    root, rh = disk_root
    monkeypatch.setattr(data, "DATA_DIR", root)
    monkeypatch.setattr(data, "MANIFEST", root / "manifest.json")
    from omr import universe as U
    monkeypatch.setattr(U, "SYMBOLS_FILE", root / "symbols.json")
    monkeypatch.setattr(data, "VALIDATION", root / "validation.json")
    data._CACHE.clear()

    class DiskLike(evaluate.DiskProvider):
        """The real disk loaders on synthetic files (research-hash and validation checks skipped)."""

        def check(self):
            return rh
    yield DiskLike()
    data._CACHE.clear()


def kinds():
    return [r["kind"] for r in ledger.read_rows(P.VAL_ACCESS_LOG)]


def test_temporary_ledger_does_not_redirect_the_access_log(tmp_path):
    real = P.VAL_ACCESS_LOG
    with P.temporary_ledger(tmp_path / "led"):
        assert P.VAL_ACCESS_LOG == real and P.TRIALS_JSONL != P.REAL_TRIALS_JSONL
        access.for_calibration("inside a temporary ledger")
    assert kinds() == ["calibration"] and not (tmp_path / "led" / "val_access_log.jsonl").exists()


def test_a_temporary_ledger_trial_on_disk_data_is_logged_in_the_real_log(tmp_path, disk):
    f = tmp_path / "t_noise.omr"
    f.write_text(NOISE, encoding="ascii")
    gens = tmp_path / "gens"
    (gens / "gen000").mkdir(parents=True)
    (gens / "gen000" / "PLAN.md").write_text("p\n", encoding="ascii")
    with P.temporary_ledger(tmp_path / "led", generations=gens):
        row = evaluate.evaluate_file(str(f), 0, provider=disk, opts=FAST, quiet=True, require_lock=False, p_max=0.05)
    assert row["status"] == "evaluated"
    rows = ledger.read_rows(P.VAL_ACCESS_LOG)
    assert [r["kind"] for r in rows] == ["temp_ledger_trial"]
    assert rows[0]["trial_id"] == row["trial_id"] and len(rows[0]["source_sha256"]) == 64
    assert ledger.verify_chain(P.VAL_ACCESS_LOG) == []


def test_a_trial_in_the_real_ledger_adds_no_log_row(tmp_path, disk, monkeypatch, tmp_ledger):
    monkeypatch.setattr(P, "REAL_TRIALS_JSONL", P.TRIALS_JSONL)          # the trial ledger in use IS the real one
    f = tmp_path / "t_noise.omr"
    f.write_text(NOISE, encoding="ascii")
    row = evaluate.evaluate_file(str(f), 0, provider=disk, opts=FAST, quiet=True, require_lock=False, p_max=0.05)
    assert row["status"] == "evaluated" and kinds() == []


def test_the_log_row_is_written_before_any_frame_is_returned(tmp_path, disk, tmp_ledger):
    _, h = ledger.append_pending({"trial_id": "e" * 16, "generation": 0, "source_sha256": "s" * 64})
    assert kinds() == []
    D.load_raw("klines", "BTCUSDT", upto="val_end", handle=h)
    assert kinds() == ["temp_ledger_trial"]
    D.load_frames(C.CORE, D.PROGRAM_EXTRA, upto="val_end", handle=h)     # once per handle
    assert kinds() == ["temp_ledger_trial"]


def test_a_synthetic_provider_logs_nothing(tmp_path, tmp_ledger):
    w = synth_world(seed=3, extended=8)
    f = tmp_path / "t_noise.omr"
    f.write_text(NOISE, encoding="ascii")
    row = evaluate.evaluate_file(str(f), 0, provider=SynthProvider(w), opts=FAST, quiet=True, require_lock=False,
                                 p_max=0.05)
    assert row["status"] == "evaluated" and kinds() == []


def test_one_selftest_on_disk_data_leaves_exactly_three_rows(tmp_path, disk):
    out = selftest.run(provider=disk, require_lock=False, p_max=0.05, tmp_parent=tmp_path)
    assert out == "OK"
    assert kinds() == ["selftest", "temp_ledger_trial", "temp_ledger_trial", "temp_ledger_trial"]
    assert list(tmp_path.iterdir()) == []
