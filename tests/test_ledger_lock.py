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


def test_the_seal_needs_both_units_and_decides_each_unit_alone(tmp_path):
    """KP-015 + R-H: both calibrations are needed; each unit's threshold is the largest that keeps ITS null pass
    rate <= 3% under both of its nulls (e: the seal writes the mapping)."""
    k = Kern(tmp_path)
    lock = k.rekey()
    art = k.write_art(artifact(lock, tmp_path, passes_010=2, passes_005=1))     # core: 0.10 qualifies
    with pytest.raises(KL.SealRefused):
        k.seal(art, uart=None)
    ua = uartifact(lock, tmp_path, passes_010=6, passes_005=2)                 # top30: 6.7% at 0.10, 2.2% at 0.05
    v = UC.decide_both(json.loads(art.read_text()), ua)
    assert v["chosen_threshold"] == {"core": 0.10, "top30": 0.05} and not v["STOP"]
    assert v["per_unit"]["top30"]["qualifying"] == [0.025, 0.05] and v["per_unit"]["core"]["qualifying"] == [0.025, 0.05, 0.1]
    k.seal(art, uart=k.write_art(ua, name="ucalibration_y.json"))
    sealed = KL.read_lock(k.lock)["seal"]
    assert sealed["g6_threshold"] == {"core": 0.10, "top30": 0.05}
    assert sealed["universe_calibration_file"] == "ledger/ucalibration_y.json"
    assert set(sealed["null_pass_rate"]) == {"core", "top30"} and set(sealed["power_at_1_5"]) == {"core", "top30"}
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
    both = {"core": 0.05, "top30": 0.10}                              # the default top30 artifact qualifies at 0.10
    assert sealed["seal"]["g6_threshold"] == both and sealed["seal"]["calibration_file"] == "ledger/calibration_x.json"
    assert sealed["seal"]["semantic_hash"] == lock["semantic"] and sealed["combined"] == lock["combined"]
    last = LG.read_rows(k.hist)[-1]
    assert last["event"] == "seal" and last["g6_threshold"] == both and last["new_semantic"] == lock["semantic"]
    assert k.verify() == []
    with pytest.raises(KL.SealRefused):                               # sealed once per semantic key
        k.seal(art)
    art.write_text(art.read_text() + " ")                            # the sealed artifact changed
    assert any("artifact" in x for x in k.verify())
    art.write_text(art.read_text()[:-1])
    forged = dict(sealed)
    forged["seal"] = dict(sealed["seal"], g6_threshold={"core": 0.1, "top30": 0.1})    # hand-edited threshold
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
    assert l2["seal"]["g6_threshold"] == {"core": 0.05, "top30": 0.10}
    assert l2["semantic"] == lock["semantic"] and l2["text"] != lock["text"]
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


def test_u8_a_text_only_rekey_keeps_a_seal_made_before_the_universe_keys(tmp_path):
    """A seal kept from before KP-015 has no universe_calibration_* keys: the re-key must not raise and the
    kernel must still verify."""
    k = Kern(tmp_path)
    lock = k.rekey()
    k.seal(k.write_art(artifact(lock, tmp_path)))
    old = KL.read_lock(k.lock)
    seal = {kk: v for kk, v in old["seal"].items() if not kk.startswith("universe_")}
    k.lock.write_text(json.dumps(dict(old, seal=seal)))
    rows = LG.read_rows(k.hist)
    last = {kk: v for kk, v in rows[-1].items() if not kk.startswith("universe_") and kk not in ("prev_hash", "row_hash")}
    k.hist.write_text("")
    for r in rows[:-1]:
        LG.append(k.hist, {kk: v for kk, v in r.items() if kk not in ("prev_hash", "row_hash")})
    LG.append(k.hist, last)
    assert k.verify() == []
    (tmp_path / "LANGUAGE.md").write_text("grammar, reworded\n")
    l2 = k.rekey("text only, old seal")
    assert l2["seal"] == seal and LG.read_rows(k.hist)[-1]["seal_kept"] is True
    assert LG.read_rows(k.hist)[-1]["universe_calibration_file"] is None and k.verify() == []


def test_d3_decide_both_reads_the_levels_present_in_each_unit(tmp_path):
    """Fix pass 5 (D3): the universe artifact holds oracle level 1.5 only; the core artifact keeps 1.0 and 1.5.
    The rule reads power at 1.5, and a level a unit did not run is not an 'oracle level outside the bound'."""
    k = Kern(tmp_path)
    lock = k.rekey()
    core = artifact(lock, tmp_path, passes_010=2, passes_005=1)
    ua = uartifact(lock, tmp_path, passes_010=2, passes_005=1)
    for n in ("A", "B"):
        ua["oracle"][n]["rows"] = [r for r in ua["oracle"][n]["rows"] if r["level"] == 1.5]
    v = UC.decide_both(core, ua)
    assert v["chosen_threshold"] == {"core": 0.10, "top30": 0.10} and not v["STOP"]
    assert v["per_unit"]["top30"]["oracle_level_outside_bound"] == []
    assert set(UC.oracle_summary(ua["oracle"]["A"]["rows"])) == {"fast|1.5", "slow|1.5"}
    assert UC.oracle_summary(core["oracle"]["A"]["rows"]) == K.oracle_summary(core["oracle"]["A"]["rows"])


# ---------------------------------------------------------------- fix pass 6: R-H per-unit thresholds, F2


def oracle_rows_at(p_values):
    """Oracle rows (both speeds, levels 1.0 and 1.5, 10 worlds) whose i-th world has perm_p p_values[i]."""
    rows = []
    for s in K.SPEEDS:
        for lvl in K.LEVELS:
            for i, p in enumerate(p_values):
                rows.append({"speed": s, "level": lvl, "world_seed": i, "status": "evaluated", "val_sharpe": lvl,
                             "perm_p": p, "rho": 0.1,
                             "gates": {g: True for g in ("G1", "G2", "G3", "G4", "G5", "G7", "G10")} | {"G6": None,
                                                                                                         "G8": None}})
    return rows


def _two_units(core_p=None, top_p=None, core_pass=(2, 1), top_pass=(6, 2)):
    lock = {"semantic": "s"}
    core = artifact(lock, ROOT, passes_010=core_pass[0], passes_005=core_pass[1])
    top = uartifact(lock, ROOT, passes_010=top_pass[0], passes_005=top_pass[1])
    for art, ps in ((core, core_p), (top, top_p)):
        if ps is not None:
            for n in ("A", "B"):
                art["oracle"][n]["rows"] = oracle_rows_at(ps)
    return core, top


def test_r_h_a_each_unit_at_its_own_threshold_and_its_power_there():
    # core: 7 worlds pass at every threshold, 2 only at 0.10 -> power 0.9 at 0.10, 0.7 at 0.05
    # top30: 8 worlds pass at every threshold, 1 only at 0.10 -> power 0.8 at 0.05
    core, top = _two_units(core_p=[0.001] * 7 + [0.07] * 2 + [0.5], top_p=[0.001] * 8 + [0.07] + [0.5])
    v = UC.decide_both(core, top)
    assert v["chosen_threshold"] == {"core": 0.10, "top30": 0.05} and not v["STOP"]
    assert v["power_at_1_5_chosen"]["core"] == {n: {"fast": 0.9, "slow": 0.9} for n in ("A", "B")}
    assert v["power_at_1_5_chosen"]["top30"] == {n: {"fast": 0.8, "slow": 0.8} for n in ("A", "B")}
    assert v["null_pass_rate"]["core"]["A"]["0.1"] == 0.02 and v["null_pass_rate"]["top30"]["A"]["0.05"] == 2 / 90


def test_r_h_b_one_unit_rows_never_move_the_other_units_choice():
    base = UC.decide_both(*_two_units())
    for tp in ((0, 0), (2, 1), (9, 9)):                               # top30 null rows vary: core stays 0.10
        v = UC.decide_both(*_two_units(top_pass=tp))
        assert v["chosen_threshold"]["core"] == base["chosen_threshold"]["core"] == 0.10
        assert v["per_unit"]["core"] == base["per_unit"]["core"]
    for cp in ((0, 0), (4, 2), (9, 9)):                               # core null rows vary: top30 stays 0.05
        v = UC.decide_both(*_two_units(core_pass=cp))
        assert v["chosen_threshold"]["top30"] == base["chosen_threshold"]["top30"] == 0.05
        assert v["per_unit"]["top30"] == base["per_unit"]["top30"]


def test_r_h_c_top30_power_below_the_minimum_at_its_threshold_stops_naming_top30():
    # top30 chosen 0.05; its oracle worlds pass only at 0.10 (perm_p 0.07): power 0 at 0.05
    v = UC.decide_both(*_two_units(top_p=[0.07] * 9 + [0.5]))
    assert v["STOP"] and v["chosen_threshold"] == {"core": 0.10, "top30": 0.05}
    assert v["reason"].startswith("top30:") and "core:" not in v["reason"]


def test_r_h_d_a_unit_without_a_qualifying_threshold_stops():
    core, top = _two_units(core_pass=(9, 9))
    for n in ("A", "B"):                                               # 5% pass even at 0.025: no grid value fits
        for r in core["nulls"][n]["rows"][:5]:
            r["perm_p"] = 0.01
    v = UC.decide_both(core, top)
    assert v["STOP"] and v["chosen_threshold"]["core"] is None and v["reason"].startswith("core:")
    assert v["chosen_threshold"]["top30"] == 0.05


def test_r_h_e_the_seal_refuses_on_a_per_unit_stop(tmp_path):
    k = Kern(tmp_path)
    lock = k.rekey()
    art = k.write_art(artifact(lock, tmp_path, passes_010=2, passes_005=1))
    ua = uartifact(lock, tmp_path, passes_010=6, passes_005=2)
    for n in ("A", "B"):
        ua["oracle"][n]["rows"] = oracle_rows_at([0.07] * 9 + [0.5])
    with pytest.raises(KL.SealRefused) as e:
        k.seal(art, uart=k.write_art(ua, name="ucalibration_w.json"))
    assert "top30" in str(e.value) and "per_unit" in str(e.value)
    assert "seal" not in KL.read_lock(k.lock)


def test_r_h_g_require_sealed_refuses_a_seal_without_both_units(monkeypatch):
    base = {"semantic": "s" * 64, "text": "t" * 64, "combined": "c" * 64, "files": {}}
    monkeypatch.setattr(KL, "verify", lambda *a, **k: [])
    msgs = []
    for bad in (0.05, {"core": 0.05}, {"core": 0.05, "top30": "x"}):
        monkeypatch.setattr(KL, "read_lock", lambda *a, _b=bad, **k: dict(base, seal={"g6_threshold": _b}))
        with pytest.raises(SystemExit) as e:
            KL.require_sealed(log=msgs.append)
        assert e.value.code == 4
    assert all("PER-UNIT" in m for m in msgs)
    monkeypatch.setattr(KL, "read_lock", lambda *a, **k: dict(base, seal={"g6_threshold": {"core": 0.1, "top30": 0.05}}))
    assert KL.require_sealed()["g6_threshold"] == {"core": 0.1, "top30": 0.05}
    assert KL.format_threshold({"core": 0.1, "top30": 0.05}) == "core 0.1 top30 0.05"


@pytest.mark.parametrize("gap", ["no_level_15", "no_speed", "no_null", "no_oracle"])
def test_f2_an_incomplete_unit_artifact_stops_with_a_reason(gap):
    core, top = _two_units()
    if gap == "no_level_15":
        for n in ("A", "B"):
            top["oracle"][n]["rows"] = [r for r in top["oracle"][n]["rows"] if r["level"] != 1.5]
    elif gap == "no_speed":
        top["oracle"]["B"]["rows"] = [r for r in top["oracle"]["B"]["rows"] if r["speed"] != "slow"]
    elif gap == "no_null":
        del top["nulls"]["B"]
    else:
        del top["oracle"]
    v = UC.decide_both(core, top)                                      # no KeyError
    assert v["STOP"] and v["reason"].startswith("top30: top30 artifact incomplete")
    assert v["chosen_threshold"]["core"] == 0.10


# ---------------------------------------------------------------- fix pass 6: FP6-1 malformed rows, FP6-3 grid values


@pytest.mark.parametrize("case", ["unknown_family", "no_gates", "no_level"])
def test_fp6_1_a_malformed_unit_artifact_stops_instead_of_raising(case):
    core, top = _two_units()
    if case == "unknown_family":
        top["nulls"]["A"]["rows"][0]["family"] = "not_a_family"
    elif case == "no_gates":
        del top["nulls"]["A"]["rows"][0]["gates"]
    else:
        top["oracle"]["A"]["rows"].append({"speed": "fast", "status": "evaluated", "val_sharpe": 1.5, "perm_p": 0.001,
                                           "gates": {}})
    v = UC.decide_both(core, top)
    assert v["STOP"] and v["reason"].startswith("top30: top30 artifact malformed: ")
    assert v["chosen_threshold"]["core"] == 0.10


def test_fp6_3_a_sealed_threshold_must_be_a_grid_value():
    for bad in (float("nan"), float("inf"), 5, 0.07, -0.05):
        assert KL.thresholds_of({"core": 0.05, "top30": bad}) is None
        assert KL.thresholds_of({"core": bad, "top30": 0.05}) is None
    for g in C.G6_GRID:
        assert KL.thresholds_of({"core": g, "top30": g}) == {"core": g, "top30": g}
    assert KL.thresholds_of({"core": 0.1 + 1e-13, "top30": 0.025}) == {"core": 0.1, "top30": 0.025}
    assert KL.UNITS_SEALED == C.UNITS == ("core", "top30")


# ---------------------------------------------------------------- fix pass 7: R-L family bound in the per-unit seal


def test_r_l_e_a_summary_without_family_rates_stops_the_unit_as_malformed(monkeypatch):
    core, top = _two_units()
    orig = K.null_summary

    def no_family(rows, fams):
        s = orig(rows, fams)
        if "ucal_xs_momentum" in fams:                                  # the top30 unit only
            for b in s["by_threshold"].values():
                del b["family_pass_rate"]
        return s
    monkeypatch.setattr(K, "null_summary", no_family)
    v = UC.decide_both(core, top)
    assert v["STOP"] and v["reason"].startswith("top30: top30 artifact malformed: KeyError")
    assert v["chosen_threshold"] == {"core": 0.10, "top30": None}


def test_r_l_f_the_seal_refuses_a_unit_whose_family_passes_too_often_and_shows_the_family_rates(tmp_path):
    k = Kern(tmp_path)
    lock = k.rekey()
    art = k.write_art(artifact(lock, tmp_path, passes_010=2, passes_005=1))
    ua = uartifact(lock, tmp_path, passes_010=0, passes_005=0)
    for n in ("A", "B"):                                                # 2 / 30 of ucal_xs_momentum at every threshold
        for r in [r for r in ua["nulls"][n]["rows"] if r["family"] == "ucal_xs_momentum"][:2]:
            r["perm_p"] = 0.01
    v = UC.decide_both(json.loads(art.read_text()), ua)
    assert v["per_unit"]["top30"]["null_pass_rate"]["A"]["0.025"] == 2 / 90 <= C.NULL_PASS_MAX
    assert v["STOP"] and v["chosen_threshold"] == {"core": 0.10, "top30": None}
    assert "null A: family ucal_xs_momentum 0.0667 > FAMILY_PASS_MAX" in v["reason"]
    with pytest.raises(KL.SealRefused) as e:
        k.seal(art, uart=k.write_art(ua, name="ucalibration_f.json"))
    assert "family_pass_rate" in str(e.value) and "ucal_xs_momentum" in str(e.value)
    assert "seal" not in KL.read_lock(k.lock)
