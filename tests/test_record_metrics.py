"""KP-015 H: the forward metrics recorder (tools/record_metrics.py, outside the kernel) logs each file's
first-seen sha256 once and reports a file whose bytes later differ (offline: a fake archive)."""
import datetime as dt
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import record_metrics as RM  # noqa: E402


class FakeArchive:
    def __init__(self):
        self.files = {}
        self.headers = {}
        self.calls = 0

    def put(self, name, body: bytes):
        self.files[name] = body
        self.files[name + ".CHECKSUM"] = f"{hashlib.sha256(body).hexdigest()}  {name}\n".encode("ascii")

    def get(self, url, timeout=None):
        self.calls += 1
        body = self.files.get(url.rsplit("/", 1)[1])

        class R:
            status_code = 200 if body is not None else 404
            content = body
        return R()


def test_first_seen_is_logged_once_and_a_revision_is_reported(tmp_path, monkeypatch):
    monkeypatch.setattr(RM, "PAUSE_S", 0.0)
    today = dt.date(2026, 11, 19)
    arc = FakeArchive()
    for d in ("2026-11-17", "2026-11-18"):
        arc.put(f"BTCUSDT-metrics-{d}.zip", f"rows {d}".encode())
    folder, log = tmp_path / "raw", tmp_path / "log.jsonl"
    lines = []
    assert RM.run(["BTCUSDT"], 3, folder, log, False, session=arc, today=today, out=lines.append) == 0
    rows = [json.loads(x) for x in log.read_text().splitlines()]
    assert [r["event"] for r in rows] == ["first_seen", "first_seen"] and all(r["checksum_ok"] for r in rows)
    assert "missing=1" in lines[-1]                                   # 2026-11-16 is not in the archive
    assert RM.run(["BTCUSDT"], 3, folder, log, False, session=arc, today=today, out=lines.append) == 0
    assert len(log.read_text().splitlines()) == 2                     # nothing logged twice
    arc.put("BTCUSDT-metrics-2026-11-17.zip", b"rows rewritten")      # the archive rewrites a day
    out = []
    assert RM.run(["BTCUSDT"], 3, folder, log, True, session=arc, today=today, out=out.append) == 2
    assert any("REVISED" in x and "2026-11-17" in x for x in out)
    last = json.loads(log.read_text().splitlines()[-1])
    assert last["event"] == "revised" and last["where"] == "archive"
    assert (folder / "BTCUSDT" / "BTCUSDT-metrics-2026-11-17.zip").read_bytes() == b"rows 2026-11-17"   # first copy kept
    (folder / "BTCUSDT" / "BTCUSDT-metrics-2026-11-18.zip").write_bytes(b"edited")                     # a local edit
    out = []
    assert RM.run(["BTCUSDT"], 3, folder, log, False, session=arc, today=today, out=out.append) == 2
    assert any("stored copy" in x for x in out)
