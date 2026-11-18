"""Ledger hash chains; kernel lock (any file under omr/ and tests/, LANGUAGE.md, environment pins);
the calibration seal (C4): applied by rule, refused for unverified or mismatched artifacts or a STOP
verdict, recorded in kernel.lock and kernel_history, removed by a re-key."""
import json
import shutil
from pathlib import Path

import pytest

from omr import calibrate as K
from omr import constants as C
from omr import kernel_lock as KL
from omr import ledger as LG

ROOT = Path(__file__).resolve().parent.parent


def test_chain_detects_tampered_deleted_and_truncated_rows(tmp_path):
    p = tmp_path / "t.jsonl"
    for i in range(4):
        LG.append(p, {"i": i, "val_sharpe": 0.1 * i})
    assert LG.verify_chain(p) == []
    lines = p.read_text().splitlines()
    row = json.loads(lines[2])
    row["val_sharpe"] = 9.9
    tampered = lines[:2] + [LG.canonical(row)] + lines[3:]
    p.write_text("\n".join(tampered) + "\n")
    assert any("row 2" in x for x in LG.verify_chain(p))
    p.write_text("\n".join(lines[:1] + lines[2:]) + "\n")
    assert LG.verify_chain(p)
    p.write_text("\n".join(lines[:-1]) + "\n")                       # last row removed: HEAD catches it
    assert any("HEAD" in x for x in LG.verify_chain(p))


def make_kernel(root):
    (root / "omr" / "programs").mkdir(parents=True)
    (root / "tests").mkdir()
    (root / "omr" / "a.py").write_text("X = 1\n")
    (root / "tests" / "test_a.py").write_text("def test(): pass\n")
    for f in K.FAMILIES:
        shutil.copyfile(ROOT / "omr" / "programs" / f"{f}.omr", root / "omr" / "programs" / f"{f}.omr")
    (root / "CONSTITUTION.md").write_text("rules\n")
    (root / "LANGUAGE.md").write_text("grammar\n")
    (root / "requirements.txt").write_text("# python==0.0.0\nnumpy==1\n")
    return root / "kernel.lock", root / "hist.jsonl"


def verify(root, lock, hist):
    return KL.verify(root, lock, hist, check_env=False)


def test_kernel_lock_detects_edits_new_files_anywhere_and_language_md(tmp_path):
    lock, hist = make_kernel(tmp_path)
    KL.rekey("initial", "tester", root=tmp_path, lock_path=lock, history_path=hist)
    assert verify(tmp_path, lock, hist) == []
    assert "LANGUAGE.md" in KL.read_lock(lock)["files"] and "omr/programs/gen000_funding_carry.omr" in KL.read_lock(lock)["files"]
    (tmp_path / "omr" / "a.py").write_text("X = 2\n")
    assert any("changed: omr/a.py" in x for x in verify(tmp_path, lock, hist))
    (tmp_path / "omr" / "a.py").write_text("X = 1\n")
    assert verify(tmp_path, lock, hist) == []
    for stray in ("omr/__pycache__/a.cpython-312.pyc", "tests/__pycache__/x.pyc", "omr/notes.txt", "tests/.cache/z"):
        p = tmp_path / stray
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(b"x")
        assert any("not in the lock" in x and stray in x for x in verify(tmp_path, lock, hist)), stray
        p.unlink()
    (tmp_path / "LANGUAGE.md").write_text("looser grammar\n")
    assert any("LANGUAGE.md" in x for x in verify(tmp_path, lock, hist))


def test_kernel_lock_detects_lock_rewrite_without_history(tmp_path):
    lock, hist = make_kernel(tmp_path)
    KL.rekey("initial", "tester", root=tmp_path, lock_path=lock, history_path=hist)
    (tmp_path / "omr" / "a.py").write_text("X = 3\n")
    cur = KL.compute(tmp_path)
    lock.write_text(json.dumps({"files": cur["files"], "combined": cur["combined"]}))
    assert any("kernel_history" in x for x in verify(tmp_path, lock, hist))


def test_rekey_requires_reason_and_approver(tmp_path):
    make_kernel(tmp_path)
    with pytest.raises(ValueError):
        KL.rekey("", "tester", root=tmp_path, lock_path=tmp_path / "l", history_path=tmp_path / "h")
    with pytest.raises(ValueError):
        KL.rekey("why", "", root=tmp_path, lock_path=tmp_path / "l", history_path=tmp_path / "h")


def test_environment_pins(tmp_path):
    assert KL.env_problems() == []                                   # the running .venv matches requirements.txt
    req = tmp_path / "requirements.txt"
    pins, py = KL.pins()
    req.write_text(f"# python=={py}\n" + "".join(f"{k}=={v}\n" for k, v in pins.items() if k != "numpy")
                   + "numpy==0.0.1\n")
    probs = KL.env_problems(req)
    assert any("numpy" in x and "0.0.1" in x for x in probs)
    req.write_text("# python==2.7.0\n" + "".join(f"{k}=={v}\n" for k, v in pins.items() if k != "scipy"))
    probs = KL.env_problems(req)
    assert any("python" in x for x in probs) and any("not pinned" in x and "scipy" in x for x in probs)
    req.write_text("numpy>=1\n")
    with pytest.raises(ValueError):
        KL.pins(req)


# ---------------------------------------------------------------- seal

def null_rows(n, passes_010, passes_005):
    rows = []
    for i in range(n):
        p = 0.08 if i < passes_010 - passes_005 else (0.04 if i < passes_010 else 0.5)
        rows.append({"family": K.FAMILIES[i % 5], "world_seed": i, "submitted": True, "status": "evaluated",
                     "params": {}, "val_sharpe": 0.1, "perm_p": p, "stage1": {"passed": 20},
                     "gates": {g: True for g in ("G1", "G2", "G3", "G4", "G5", "G7", "G10")} | {"G6": None, "G8": None}})
    return rows


def oracle_rows(power):
    rows = []
    for s in K.SPEEDS:
        for lvl in K.LEVELS:
            for i in range(10):
                ok = i < power * 10
                rows.append({"speed": s, "level": lvl, "world_seed": i, "status": "evaluated", "val_sharpe": lvl,
                             "perm_p": 0.001 if ok else 0.5, "rho": 0.1,
                             "gates": {g: True for g in ("G1", "G2", "G3", "G4", "G5", "G7", "G10")} | {"G6": None,
                                                                                                         "G8": None}})
    return rows


def artifact(lock, root, passes_010=4, passes_005=2, power=0.8, verified=True):
    return {"kernel_lock_verified": verified, "kernel_hash": lock["combined"], "research_hash": "r" * 64,
            "families": {f: LG.sha256_file(root / "omr" / "programs" / f"{f}.omr") for f in K.FAMILIES},
            "nulls": {n: {"rows": null_rows(100, passes_010, passes_005)} for n in ("A", "B")},
            "oracle": {n: {"rows": oracle_rows(power)} for n in ("A", "B")}}


def write_art(root, art, name="calibration_x.json"):
    p = root / "ledger" / name
    p.parent.mkdir(exist_ok=True)
    p.write_text(json.dumps(art), encoding="ascii")
    return p


def test_seal_applies_the_rule_and_records_it(tmp_path):
    lock_p, hist = make_kernel(tmp_path)
    lock = KL.rekey("initial", "tester", root=tmp_path, lock_path=lock_p, history_path=hist)
    art = write_art(tmp_path, artifact(lock, tmp_path))
    v = K.verdict_from_rows(json.loads(art.read_text()))
    assert v["chosen_threshold"] == 0.05 and v["qualifying"] == [0.025, 0.05] and not v["STOP"]
    KL.seal(art, root=tmp_path, lock_path=lock_p, history_path=hist, research_hash="r" * 64, log=lambda s: None,
            check_env=False)
    sealed = KL.read_lock(lock_p)
    assert sealed["seal"]["g6_threshold"] == 0.05 and sealed["seal"]["calibration_file"] == "ledger/calibration_x.json"
    assert sealed["combined"] == lock["combined"]
    last = LG.read_rows(hist)[-1]
    assert last["event"] == "seal" and last["g6_threshold"] == 0.05 and last["new_combined"] == lock["combined"]
    assert verify(tmp_path, lock_p, hist) == []
    with pytest.raises(KL.SealRefused):                               # sealed once per key
        KL.seal(art, root=tmp_path, lock_path=lock_p, history_path=hist, research_hash="r" * 64, log=lambda s: None,
                check_env=False)
    art.write_text(art.read_text() + " ")                            # the sealed artifact changed
    assert any("artifact" in x for x in verify(tmp_path, lock_p, hist))
    art.write_text(art.read_text()[:-1])
    forged = dict(sealed)
    forged["seal"] = dict(sealed["seal"], g6_threshold=0.1)            # hand-edited threshold
    lock_p.write_text(json.dumps(forged))
    assert any("seal" in x for x in verify(tmp_path, lock_p, hist))
    lock_p.write_text(json.dumps(sealed))
    KL.rekey("after seal", "tester", root=tmp_path, lock_path=lock_p, history_path=hist)
    assert "seal" not in KL.read_lock(lock_p) and verify(tmp_path, lock_p, hist) == []


@pytest.mark.parametrize("case", ["unverified", "wrong_kernel", "wrong_family", "wrong_research", "no_threshold",
                                  "low_power", "lock_broken"])
def test_seal_refuses(tmp_path, case):
    lock_p, hist = make_kernel(tmp_path)
    lock = KL.rekey("initial", "tester", root=tmp_path, lock_path=lock_p, history_path=hist)
    a = artifact(lock, tmp_path)
    rh = "r" * 64
    if case == "unverified":
        a["kernel_lock_verified"] = False
    elif case == "wrong_kernel":
        a["kernel_hash"] = "0" * 64
    elif case == "wrong_family":
        a["families"]["gen000_funding_carry"] = "0" * 64
    elif case == "wrong_research":
        rh = "s" * 64
    elif case == "no_threshold":
        a = artifact(lock, tmp_path, passes_010=6, passes_005=5)         # 5% null pass rate everywhere -> STOP
        for n in ("A", "B"):
            for r in a["nulls"][n]["rows"][:5]:
                r["perm_p"] = 0.01
    elif case == "low_power":
        a = artifact(lock, tmp_path, power=0.3)
    elif case == "lock_broken":
        (tmp_path / "omr" / "a.py").write_text("X = 9\n")
    art = write_art(tmp_path, a)
    with pytest.raises(KL.SealRefused):
        KL.seal(art, root=tmp_path, lock_path=lock_p, history_path=hist, research_hash=rh, log=lambda s: None,
                check_env=False)
    assert "seal" not in KL.read_lock(lock_p)


def test_decide_rule_and_oracle_bound():
    a = artifact({"combined": "c"}, ROOT)
    v = K.verdict_from_rows(a)
    assert v["chosen_threshold"] == 0.05 and v["power_at_1_5_chosen"]["A"]["fast"] == 0.8
    for r in a["oracle"]["A"]["rows"]:
        if r["level"] == 1.5 and r["speed"] == "slow":
            r["val_sharpe"] = 1.75                                     # achieved level off by 0.25 > 0.1
    v = K.verdict_from_rows(a)
    assert v["STOP"] and v["oracle_level_outside_bound"] == ["A/slow|1.5"]
    assert C.G6_GRID == (0.025, 0.05, 0.10) and C.NULL_PASS_MAX == 0.03 and C.POWER_MIN == 0.5
