"""U8: the sandbox appends its log row BEFORE it prints any metric, and a kernel-fault exit writes a row too
(synthetic disk data, a temp sandbox log)."""
import pytest

from conftest import make_disk_data, prog_text
from omr import constants as C
from omr import data
from omr import kernel_lock
from omr import ledger
from omr import paths as P
from omr import pipeline
from omr import sandbox


@pytest.fixture(scope="module")
def disk_root(tmp_path_factory):
    root = tmp_path_factory.mktemp("sandbox_data")
    make_disk_data(root, symbols=C.CORE, end="2022-08-31 23:00")
    return root


@pytest.fixture
def env(disk_root, tmp_path, monkeypatch):
    monkeypatch.setattr(data, "DATA_DIR", disk_root)
    monkeypatch.setattr(data, "MANIFEST", disk_root / "manifest.json")
    data._CACHE.clear()
    monkeypatch.setattr(P, "SANDBOX_LOG", tmp_path / "sandbox_log.jsonl")
    monkeypatch.setattr(kernel_lock, "require_kernel", lambda: {"combined": "k" * 64})
    printed, appended_at = [], []
    monkeypatch.setattr(sandbox, "print", lambda *a, **k: printed.append(" ".join(str(x) for x in a)), raising=False)
    real = ledger.append

    def spy(path, row):
        appended_at.append(len(printed))
        return real(path, row)
    monkeypatch.setattr(ledger, "append", spy)
    f = tmp_path / "x_test.omr"
    f.write_text(prog_text("n = param(24, 12, 48)\nsignal = sign(ret(close, n))\n"), encoding="ascii")
    yield f, printed, appended_at
    data._CACHE.clear()


def test_u8_the_row_is_appended_before_any_metric_is_printed(env):
    f, printed, appended_at = env
    sandbox.main([str(f), "--quick"])
    rows = ledger.read_rows(P.SANDBOX_LOG)
    assert len(rows) == 1 and rows[0]["status"] == "ok" and "dev_sharpe" in rows[0]
    assert appended_at == [0]                                       # nothing printed before the row
    assert any("DEV Sharpe" in line for line in printed)


def test_u8_a_kernel_fault_exit_writes_a_row(env, monkeypatch):
    f, printed, appended_at = env
    monkeypatch.setattr(pipeline, "stage1", lambda *a, **k: {"ok": False, "code": "kernel_fault",
                                                             "fault": "truncation", "cuts": 2})
    with pytest.raises(SystemExit) as e:
        sandbox.main([str(f), "--quick"])
    assert e.value.code == 2
    rows = ledger.read_rows(P.SANDBOX_LOG)
    assert len(rows) == 1 and rows[0]["status"] == "kernel_fault" and rows[0]["fault"] == "truncation"
    assert appended_at == [0] and any("KERNEL FAULT" in line for line in printed)
