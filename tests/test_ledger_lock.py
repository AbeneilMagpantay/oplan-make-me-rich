"""Ledger hash chains; the two-part kernel lock (SEMANTIC: omr/**, requirements.txt; TEXT:
CONSTITUTION.md, LANGUAGE.md, tests/**), any file under omr/ and tests/, environment pins; the
calibration seal (C4, M1, M2): applied by rule to an artifact that omr.calibrate wrote AND logged,
refused for unverified, unlogged, hand-edited or mismatched artifacts or a STOP verdict; kept by a
text-only re-key, dropped by a semantic re-key."""
import json
import shutil
from pathlib import Path

import pytest

from omr import calibrate as K
from omr import constants as C
from omr import kernel_lock as KL
from omr import ucalibrate as UC
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
    p.write_text("\n".join(lines[:2] + [LG.canonical(row)] + lines[3:]) + "\n")
    assert any("row 2" in x for x in LG.verify_chain(p))
    p.write_text("\n".join(lines[:1] + lines[2:]) + "\n")
    assert LG.verify_chain(p)
    p.write_text("\n".join(lines[:-1]) + "\n")
    assert any("HEAD" in x for x in LG.verify_chain(p))


class Kern:
    def __init__(self, root):
        self.root = root
        (root / "omr" / "programs").mkdir(parents=True)
        (root / "tests").mkdir()
        (root / "omr" / "a.py").write_text("X = 1\n")
        (root / "tests" / "test_a.py").write_text("def test(): pass\n")
        for f in K.FAMILIES + UC.FAMILIES:
            shutil.copyfile(ROOT / "omr" / "programs" / f"{f}.omr", root / "omr" / "programs" / f"{f}.omr")
        (root / "CONSTITUTION.md").write_text("rules\n")
        (root / "LANGUAGE.md").write_text("grammar\n")
        (root / "requirements.txt").write_text("# python==0.0.0\nnumpy==1\n")
        (root / "ledger").mkdir()
        self.lock, self.hist, self.clog = root / "kernel.lock", root / "ledger" / "hist.jsonl", root / "ledger" / "cal.jsonl"

    def rekey(self, why="initial"):
        return KL.rekey(why, "tester", root=self.root, lock_path=self.lock, history_path=self.hist)

    def verify(self):
        return KL.verify(self.root, self.lock, self.hist, check_env=False, calibration_log=self.clog)

    def seal(self, art, rh="r" * 64, uart="default"):
        if uart == "default":
            uart = self.write_art(uartifact(KL.read_lock(self.lock), self.root), name="ucalibration_x.json")
        return KL.seal(art, root=self.root, lock_path=self.lock, history_path=self.hist, research_hash=rh,
                       log=lambda s: None, check_env=False, calibration_log=self.clog, universe_artifact=uart)

    def write_art(self, art, name="calibration_x.json", logged=True):
        p = self.root / "ledger" / name
        p.write_text(json.dumps(art), encoding="ascii")
        if logged:
            KL.log_calibration(p, art.get("semantic_hash", ""), art.get("research_hash", ""),
                               calibration_log=self.clog, root=self.root)
        return p


def test_two_part_hashes(tmp_path):
    k = Kern(tmp_path)
    a = KL.compute(tmp_path)
    (tmp_path / "tests" / "test_a.py").write_text("def test(): assert True\n")
    b = KL.compute(tmp_path)
    assert a["semantic"] == b["semantic"] and a["text"] != b["text"] and a["combined"] != b["combined"]
    (tmp_path / "LANGUAGE.md").write_text("grammar v2\n")
    c = KL.compute(tmp_path)
    assert c["semantic"] == a["semantic"]
    (tmp_path / "omr" / "programs" / "gen000_funding_carry.omr").write_text("x\n")
    d = KL.compute(tmp_path)
    assert d["semantic"] != c["semantic"]
    (tmp_path / "requirements.txt").write_text("# python==0.0.0\nnumpy==2\n")
    assert KL.compute(tmp_path)["semantic"] != d["semantic"]
    assert KL.is_semantic("omr/x.py") and KL.is_semantic("requirements.txt") and not KL.is_semantic("tests/x.py")
    assert not KL.is_semantic("CONSTITUTION.md") and not KL.is_semantic("LANGUAGE.md")


def test_kernel_lock_detects_edits_and_any_new_file(tmp_path):
    k = Kern(tmp_path)
    k.rekey()
    assert k.verify() == []
    (tmp_path / "omr" / "a.py").write_text("X = 2\n")
    assert any("changed: omr/a.py" in x for x in k.verify())
    (tmp_path / "omr" / "a.py").write_text("X = 1\n")
    assert k.verify() == []
    for stray in ("omr/__pycache__/a.cpython-312.pyc", "tests/__pycache__/x.pyc", "omr/notes.txt", "tests/.cache/z"):
        p = tmp_path / stray
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(b"x")
        assert any("not in the lock" in x and stray in x for x in k.verify()), stray
        p.unlink()
    (tmp_path / "LANGUAGE.md").write_text("looser grammar\n")
    assert any("LANGUAGE.md" in x for x in k.verify())


def test_kernel_lock_detects_lock_rewrite_without_history(tmp_path):
    k = Kern(tmp_path)
    k.rekey()
    (tmp_path / "omr" / "a.py").write_text("X = 3\n")
    cur = KL.compute(tmp_path)
    k.lock.write_text(json.dumps(cur))
    assert any("kernel_history" in x for x in k.verify())


def test_rekey_requires_reason_and_approver(tmp_path):
    Kern(tmp_path)
    with pytest.raises(ValueError):
        KL.rekey("", "tester", root=tmp_path, lock_path=tmp_path / "l", history_path=tmp_path / "h")
    with pytest.raises(ValueError):
        KL.rekey("why", "", root=tmp_path, lock_path=tmp_path / "l", history_path=tmp_path / "h")


def test_environment_pins(tmp_path):
    assert KL.env_problems() == []
    req = tmp_path / "requirements.txt"
    pins, py = KL.pins()
    req.write_text(f"# python=={py}\n" + "".join(f"{k}=={v}\n" for k, v in pins.items() if k != "numpy")
                   + "numpy==0.0.1\n")
    assert any("numpy" in x and "0.0.1" in x for x in KL.env_problems(req))
    req.write_text("# python==2.7.0\n" + "".join(f"{k}=={v}\n" for k, v in pins.items() if k != "scipy"))
    probs = KL.env_problems(req)
    assert any("python" in x for x in probs) and any("not pinned" in x and "scipy" in x for x in probs)
    req.write_text("numpy>=1\n")
    with pytest.raises(ValueError):
        KL.pins(req)


# ---------------------------------------------------------------- seal

def null_rows(n, passes_010, passes_005, families=K.FAMILIES):
    rows = []
    for i in range(n):
        p = 0.08 if i < passes_010 - passes_005 else (0.04 if i < passes_010 else 0.5)
        rows.append({"family": families[i % len(families)], "world_seed": i, "submitted": True, "status": "evaluated",
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
    return {"kernel_lock_verified": verified, "semantic_hash": lock["semantic"], "research_hash": "r" * 64,
            "families": {f: LG.sha256_file(root / "omr" / "programs" / f"{f}.omr") for f in K.FAMILIES},
            "nulls": {n: {"rows": null_rows(100, passes_010, passes_005)} for n in ("A", "B")},
            "oracle": {n: {"rows": oracle_rows(power)} for n in ("A", "B")}}


def uartifact(lock, root, passes_010=2, passes_005=1, power=0.8, verified=True):
    return {"unit": "top30", "kernel_lock_verified": verified, "semantic_hash": lock["semantic"],
            "research_hash": "r" * 64,
            "families": {f: LG.sha256_file(root / "omr" / "programs" / f"{f}.omr") for f in UC.FAMILIES},
            "nulls": {n: {"rows": null_rows(90, passes_010, passes_005, UC.FAMILIES)} for n in ("A", "B")},
            "oracle": {n: {"rows": oracle_rows(power)} for n in ("A", "B")}}


def test_the_seal_needs_both_units_and_takes_the_stricter(tmp_path):
    """KP-015: the threshold is the largest one that keeps the null pass rate <= 3% in BOTH units."""
    k = Kern(tmp_path)
    lock = k.rekey()
    art = k.write_art(artifact(lock, tmp_path, passes_010=2, passes_005=1))     # core alone: 0.10 qualifies
    with pytest.raises(KL.SealRefused):
        k.seal(art, uart=None)
    ua = uartifact(lock, tmp_path, passes_010=6, passes_005=2)                 # top30: 6.7% at 0.10, 2.2% at 0.05
    v = UC.decide_both(json.loads(art.read_text()), ua)
    assert v["qualifying"] == [0.025, 0.05] and v["chosen_threshold"] == 0.05 and not v["STOP"]
    k.seal(art, uart=k.write_art(ua, name="ucalibration_y.json"))
    sealed = KL.read_lock(k.lock)["seal"]
    assert sealed["g6_threshold"] == 0.05 and sealed["universe_calibration_file"] == "ledger/ucalibration_y.json"
    assert k.verify() == []
    (tmp_path / "ledger" / "ucalibration_y.json").write_text("{}")                # the universe artifact changed
    assert any("universe calibration" in x for x in k.verify())


@pytest.mark.parametrize("case", ["low_power", "wrong_family", "unverified", "unlogged", "wrong_unit"])
def test_the_seal_refuses_a_bad_universe_artifact(tmp_path, case):
    k = Kern(tmp_path)
    lock = k.rekey()
    art = k.write_art(artifact(lock, tmp_path))
    ua = uartifact(lock, tmp_path, power=0.3 if case == "low_power" else 0.8, verified=case != "unverified")
    if case == "wrong_family":
        ua["families"]["ucal_xs_carry"] = "0" * 64
    if case == "wrong_unit":
        ua["unit"] = "core"
    p = k.write_art(ua, name="ucalibration_z.json", logged=case != "unlogged")
    with pytest.raises(KL.SealRefused):
        k.seal(art, uart=p)
    assert "seal" not in KL.read_lock(k.lock)


def test_seal_applies_the_rule_and_records_it(tmp_path):
    k = Kern(tmp_path)
    lock = k.rekey()
    art = k.write_art(artifact(lock, tmp_path))
    v = K.verdict_from_rows(json.loads(art.read_text()))
    assert v["chosen_threshold"] == 0.05 and v["qualifying"] == [0.025, 0.05] and not v["STOP"]
    k.seal(art)
    sealed = KL.read_lock(k.lock)
    assert sealed["seal"]["g6_threshold"] == 0.05 and sealed["seal"]["calibration_file"] == "ledger/calibration_x.json"
    assert sealed["seal"]["semantic_hash"] == lock["semantic"] and sealed["combined"] == lock["combined"]
    last = LG.read_rows(k.hist)[-1]
    assert last["event"] == "seal" and last["g6_threshold"] == 0.05 and last["new_semantic"] == lock["semantic"]
    assert k.verify() == []
    with pytest.raises(KL.SealRefused):                               # sealed once per semantic key
        k.seal(art)
    art.write_text(art.read_text() + " ")                            # the sealed artifact changed
    assert any("artifact" in x for x in k.verify())
    art.write_text(art.read_text()[:-1])
    forged = dict(sealed)
    forged["seal"] = dict(sealed["seal"], g6_threshold=0.1)            # hand-edited threshold
    k.lock.write_text(json.dumps(forged))
    assert any("seal" in x for x in k.verify())
    k.lock.write_text(json.dumps(sealed))
    assert k.verify() == []


def test_a_text_only_rekey_keeps_the_seal_a_semantic_rekey_drops_it(tmp_path):
    k = Kern(tmp_path)
    lock = k.rekey()
    k.seal(k.write_art(artifact(lock, tmp_path)))
    (tmp_path / "tests" / "test_a.py").write_text("def test(): assert 1\n")
    (tmp_path / "CONSTITUTION.md").write_text("rules, reworded\n")
    l2 = k.rekey("text only")
    assert l2["seal"]["g6_threshold"] == 0.05 and l2["semantic"] == lock["semantic"] and l2["text"] != lock["text"]
    assert LG.read_rows(k.hist)[-1]["seal_kept"] is True and k.verify() == []
    (tmp_path / "omr" / "a.py").write_text("X = 99\n")
    l3 = k.rekey("semantic change")
    assert "seal" not in l3 and LG.read_rows(k.hist)[-1]["seal_kept"] is False and k.verify() == []


@pytest.mark.parametrize("case", ["unverified", "wrong_kernel", "wrong_family", "wrong_research", "no_threshold",
                                  "low_power", "lock_broken", "unlogged", "hand_edited"])
def test_seal_refuses(tmp_path, case):
    k = Kern(tmp_path)
    lock = k.rekey()
    a = artifact(lock, tmp_path)
    rh = "r" * 64
    logged = True
    if case == "unverified":
        a["kernel_lock_verified"] = False
    elif case == "wrong_kernel":
        a["semantic_hash"] = "0" * 64
    elif case == "wrong_family":
        a["families"]["gen000_funding_carry"] = "0" * 64
    elif case == "wrong_research":
        rh = "s" * 64
    elif case == "no_threshold":
        a = artifact(lock, tmp_path, passes_010=6, passes_005=5)
        for n in ("A", "B"):
            for r in a["nulls"][n]["rows"][:5]:
                r["perm_p"] = 0.01
    elif case == "low_power":
        a = artifact(lock, tmp_path, power=0.3)
    elif case == "lock_broken":
        (tmp_path / "omr" / "a.py").write_text("X = 9\n")
    elif case == "unlogged":
        logged = False
    art = k.write_art(a, logged=logged)
    if case == "hand_edited":                                         # the audit's r08 forgery: edit after logging
        forged = json.loads(art.read_text())
        for n in ("A", "B"):
            for r in forged["nulls"][n]["rows"]:
                r["perm_p"] = 0.9
        art.write_text(json.dumps(forged), encoding="ascii")
    with pytest.raises(KL.SealRefused):
        k.seal(art, rh)
    assert "seal" not in KL.read_lock(k.lock)


def test_decide_rule_and_oracle_bound():
    a = artifact({"semantic": "s"}, ROOT)
    v = K.verdict_from_rows(a)
    assert v["chosen_threshold"] == 0.05 and v["power_at_1_5_chosen"]["A"]["fast"] == 0.8
    for r in a["oracle"]["A"]["rows"]:
        if r["level"] == 1.5 and r["speed"] == "slow":
            r["val_sharpe"] = 1.75
    v = K.verdict_from_rows(a)
    assert v["STOP"] and v["oracle_level_outside_bound"] == ["A/slow|1.5"]
    assert C.G6_GRID == (0.025, 0.05, 0.10) and C.NULL_PASS_MAX == 0.03 and C.POWER_MIN == 0.5
