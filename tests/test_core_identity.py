"""KP-015 hard requirement: the core unit is BIT-IDENTICAL to the kernel of commit b12df97.

The reference is tests/ref_kernel_b12df97.zip (`git archive b12df97 omr`), extracted to a temp folder and
run in its own process by tests/ref_core_runner.py; the working kernel runs the same script. Compared
exactly: every existing core program's weights and raw signal (stage 1 and the full DEV+VAL grid), and
its stage-2 metrics, gate values, info and daily returns on a synthetic world; and, on the REAL DEV
frames, the stage-1 weights and raw signal of the strategies of generations 0 and 1 and the kernel's core
programs. Strategies written since the universe unit (generation 2 on) carry a `unit` header line that the
reference kernel cannot read, so they are not part of this comparison (batch re-key of 2026-11-25: before
it, core_programs() copied every file in strategies/ and the reference run stopped at the first of them).
"""
import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import numpy as np
import pytest

from conftest import synth_raw

ROOT = Path(__file__).resolve().parent.parent
REF_ZIP = ROOT / "tests" / "ref_kernel_b12df97.zip"
RUNNER = ROOT / "tests" / "ref_core_runner.py"
LATE = ["2020-09-14 00:00", "2020-02-10 00:00", "2020-01-06 00:00", "2020-01-31 00:00", "2020-07-10 00:00",
        "2020-01-09 00:00", "2020-01-17 00:00", "2020-09-23 00:00"]
EXT = ("SOLUSDT", "BNBUSDT", "XRPUSDT", "ADAUSDT", "DOGEUSDT", "LTCUSDT", "LINKUSDT", "AVAXUSDT")
REF_GENERATIONS = ("gen000_", "gen001_")     # the strategies written in the reference kernel's language
REF_STRATEGIES = 11                          # their number; they are closed generations and never change


def core_programs(dest: Path) -> list:
    dest.mkdir(parents=True, exist_ok=True)
    strategies = [f for f in sorted((ROOT / "strategies").glob("*.omr")) if f.name.startswith(REF_GENERATIONS)]
    assert len(strategies) == REF_STRATEGIES, [f.name for f in strategies]
    files = strategies + [ROOT / "omr" / "programs" / f"{s}.omr" for s in
                          ("kernel_kitchen_sink", "kernel_noise_single", "kernel_noise_portfolio")]
    for f in files:
        shutil.copyfile(f, dest / f.name)
    return [f.stem for f in files]


@pytest.fixture(scope="module")
def ref_root(tmp_path_factory):
    d = tmp_path_factory.mktemp("ref_b12df97")
    with zipfile.ZipFile(REF_ZIP) as z:
        z.extractall(d)
    assert (d / "omr" / "pipeline.py").exists() and not (d / "omr" / "upipeline.py").exists()
    return d


def run(kernel_root: Path, args: list, out: Path):
    r = subprocess.run([sys.executable, "-I", str(RUNNER), str(kernel_root), *[str(a) for a in args], str(out)],
                       capture_output=True, text=True, timeout=3000)
    assert r.returncode == 0, r.stderr[-3000:]


def identical(out_a: Path, out_b: Path) -> list:
    """Every difference between two runner outputs (empty = bit-identical)."""
    diffs = []
    a, b = np.load(out_a / "arrays.npz"), np.load(out_b / "arrays.npz")
    if sorted(a.files) != sorted(b.files):
        diffs.append("array names differ")
    for k in sorted(set(a.files) & set(b.files)):
        x, y = a[k], b[k]
        if x.shape != y.shape or x.dtype != y.dtype or not np.array_equal(x, y, equal_nan=True) \
                or x.tobytes() != y.tobytes():
            diffs.append(f"array {k}")
    ra = (out_a / "results.json").read_text(encoding="ascii")
    rb = (out_b / "results.json").read_text(encoding="ascii")
    if ra != rb:
        ja, jb = json.loads(ra), json.loads(rb)
        diffs += [f"results {k}" for k in sorted(set(ja) | set(jb)) if ja.get(k) != jb.get(k)]
    return diffs


def test_the_comparison_can_fail(tmp_path):
    """An assertion that cannot fail certifies nothing: one ulp in one weight is reported."""
    for d in ("a", "b"):
        (tmp_path / d).mkdir()
        (tmp_path / d / "results.json").write_text('{"p": {"x": 1}}', encoding="ascii")
    w = np.linspace(-1, 1, 50).reshape(25, 2)
    np.savez(tmp_path / "a" / "arrays.npz", p__W=w)
    w2 = w.copy()
    w2[7, 1] = np.nextafter(w2[7, 1], 2.0)
    np.savez(tmp_path / "b" / "arrays.npz", p__W=w2)
    assert identical(tmp_path / "a", tmp_path / "b") == ["array p__W"]
    (tmp_path / "b" / "results.json").write_text('{"p": {"x": 2}}', encoding="ascii")
    np.savez(tmp_path / "b" / "arrays.npz", p__W=w)
    assert identical(tmp_path / "a", tmp_path / "b") == ["results p"]


def test_core_unit_is_bit_identical_on_a_synthetic_world(tmp_path, ref_root):
    data = tmp_path / "data"
    data.mkdir()
    starts = {"BTCUSDT": "2019-09-09 00:00", "ETHUSDT": "2019-11-28 00:00", **dict(zip(EXT, LATE))}
    for i, (s, st) in enumerate(starts.items()):
        raw = synth_raw(start=st, end="2025-06-30 23:00", seed=300 + i)
        for ds, df in raw.items():
            df.to_parquet(data / f"{s}__{ds}.parquet")
    progs = tmp_path / "programs"
    names = core_programs(progs)
    run(ref_root, ["synthetic", data, progs], tmp_path / "ref")
    run(ROOT, ["synthetic", data, progs], tmp_path / "cur")
    assert identical(tmp_path / "ref", tmp_path / "cur") == []
    res = json.loads((tmp_path / "cur" / "results.json").read_text(encoding="ascii"))
    assert sorted(res) == sorted(names)
    assert sum(1 for r in res.values() if r.get("status") == "evaluated") >= 8      # stage 2 was really compared


@pytest.mark.skipif(not (ROOT / "data" / "index_klines" / "BTCUSDT.parquet").exists(),
                    reason="needs the stored real data with index_klines (python -m omr.data universe)")
def test_core_stage1_is_bit_identical_on_the_real_dev_frames(tmp_path, ref_root):
    progs = tmp_path / "programs"
    names = core_programs(progs)
    run(ref_root, ["realdev", ROOT / "data", progs], tmp_path / "ref")
    run(ROOT, ["realdev", ROOT / "data", progs], tmp_path / "cur")
    assert identical(tmp_path / "ref", tmp_path / "cur") == []
    res = json.loads((tmp_path / "cur" / "results.json").read_text(encoding="ascii"))
    assert sorted(res) == sorted(names) and all(r["fault"] is None for r in res.values())
