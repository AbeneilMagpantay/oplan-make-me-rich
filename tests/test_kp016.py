"""KP-016 and the code items 3 and 4 of KP-017 in the seal's rule (omr.calibrate.decide, both units): the pooled
3% bound over the DEV-POSITIVE evaluated pairs, the floor DEV_POSITIVE_MIN, the family bound still over evaluated
pairs, the verdict's fields; a chosen draw that fails stage 1 counts as a fault; tier_at checks that p lies on its
lattice (edges, a JSON round trip, the unit verdict's STOP); the null advisory stays certain. Hand-built rows only
(p values on a lattice of 1000 unless a test says otherwise)."""
import json

import numpy as np
import pytest

from omr import calibrate as K
from omr import constants as C
from omr import pipeline as PL
from omr import ucalibrate as UC

GATES = ("G1", "G2", "G3", "G4", "G5", "G7", "G10")
FIVE = ("a", "b", "c", "d", "e")
NP = 999                                           # hand-built rows: p on the lattice k / 1000


def row(fam, seed, p=0.5, g3=True, status="evaluated"):
    gates = {g: True for g in GATES} | {"G6": None, "G8": None}
    gates["G3"] = g3
    return {"family": fam, "world_seed": seed, "submitted": True, "status": status, "params": {}, "val_sharpe": 0.1,
            "perm_p": p, "stage1": {"passed": 20}, "gates": gates}


def null_rows(per=40, fams=FIVE):
    return [row(f, i * 10 + j) for j, f in enumerate(fams) for i in range(per)]


def oracle_rows():
    return [{"speed": s, "level": lvl, "world_seed": i, "status": "evaluated", "val_sharpe": lvl, "perm_p": 0.001,
             "rho": 0.1, "gates": {g: True for g in GATES} | {"G6": None, "G8": None}}
            for s in K.SPEEDS for lvl in K.LEVELS for i in range(10)]


def decide(rows_a, rows_b, fams=FIVE, designed=40):
    nulls = {n: {"summary": K.null_summary(r, fams, designed, n_perm=NP)} for n, r in (("A", rows_a), ("B", rows_b))}
    oracle = {n: {"summary": K.oracle_summary(oracle_rows(), n_perm=NP)} for n in ("A", "B")}
    return K.decide(nulls, oracle), nulls


def redecide(nulls):
    return K.decide(nulls, {n: {"summary": K.oracle_summary(oracle_rows(), n_perm=NP)} for n in ("A", "B")})


def stage1_failed(r):
    for k in ("gates", "perm_p", "val_sharpe"):
        r.pop(k, None)
    r.update(submitted=False, status="stage1_kernel_fault", fault="truncation")
    return r


# ---------------------------------------------------------------- KP-016: the denominator and the floor

def test_the_pooled_bound_is_over_dev_positive_evaluated_pairs():
    assert C.NULL_PASS_MAX == 0.03 and C.DEV_POSITIVE_MIN == 100 and C.FAMILY_PASS_MAX == 0.06
    rows = null_rows()
    for r in rows[::2]:
        r["gates"]["G3"] = False                                             # 100 DEV-negative pairs
    for f in FIVE[:4]:                                                      # 4 passes at 0.10, one per family
        [r for r in rows if r["gates"]["G3"] and r["family"] == f][0]["perm_p"] = 0.08
    v, nulls = decide(rows, null_rows())
    s = nulls["A"]["summary"]
    assert s["n_evaluated"] == 200 and s["n_dev_positive"] == 100
    b = s["by_threshold"]["0.1"]
    assert b["pass_rate"] == 4 / 200 <= C.NULL_PASS_MAX                     # inside over every evaluated pair
    assert b["pass_rate_dev_positive"] == 4 / 100 > C.NULL_PASS_MAX          # outside over the DEV-positive ones
    assert v["threshold_failures"]["0.1"] == ["null A: pooled 0.0400 > NULL_PASS_MAX"]
    assert v["chosen_threshold"] == 0.05 and v["qualifying"] == [0.025, 0.05] and not v["STOP"]
    assert v["null_pass_rate"]["A"]["0.1"] == 0.04 and v["null_pass_rate_evaluated"]["A"]["0.1"] == 0.02
    assert v["null_pass_rate_dev_positive"] == v["null_pass_rate"]
    assert v["n_dev_positive"] == {"A": 100, "B": 200} and v["dev_positive_min"] == 100
    assert v["denominator"].startswith("DEV-positive evaluated pairs (pooled")
    assert K.PROTOCOL_VERSION == 7 and UC.PROTOCOL_VERSION == 10


def test_the_family_bound_stays_over_evaluated_pairs_and_dev_positive_family_rates_are_information():
    rows = null_rows()
    for r in [r for r in rows if r["family"] == "a"][1:]:
        r["gates"]["G3"] = False                                             # family a: 1 DEV-positive pair of 40
    rows[0]["perm_p"] = 0.08                                                # ... and it passes at 0.10
    v, nulls = decide(rows, null_rows())
    b = nulls["A"]["summary"]["by_threshold"]["0.1"]
    assert b["family_pass_rate"]["a"] == 1 / 40 and b["family_pass_rate_dev_positive"]["a"] == 1.0
    assert nulls["A"]["summary"]["dev_positive_per_family"]["a"] == 1
    assert v["chosen_threshold"] == 0.1 and v["family_pass_rate_dev_positive"]["A"]["0.1"]["a"] == 1.0


@pytest.mark.parametrize("negatives,stop", [(100, False), (101, True), (200, True)])
def test_dev_positive_min_is_a_floor_on_each_null(negatives, stop):
    rows = null_rows()
    for r in rows[:negatives]:
        r["gates"]["G3"] = False
    v, _ = decide(null_rows(), rows)
    n = 200 - negatives
    assert v["n_dev_positive"]["B"] == n and v["STOP"] == stop
    why = f"null B: {n} DEV-positive evaluated pairs < DEV_POSITIVE_MIN (100)"
    assert all((why in v["threshold_failures"][str(t)]) == stop for t in C.G6_GRID)
    if stop:
        assert v["chosen_threshold"] is None and why in v["reason"]


def test_the_dev_positive_count_is_fail_closed():
    _, nulls = decide(null_rows(), null_rows())
    s = nulls["A"]["summary"]
    for bad in (None, True, -1, 201, 150.0, "150"):
        keep = s["n_dev_positive"]
        s["n_dev_positive"] = bad
        w = redecide(nulls)
        assert w["STOP"] and w["n_dev_positive"]["A"] is None, bad
        assert "the count of DEV-positive evaluated pairs is missing or malformed" in w["reason"], bad
        s["n_dev_positive"] = keep
    assert not redecide(nulls)["STOP"]


def test_a_missing_dev_positive_rate_fails():
    _, nulls = decide(null_rows(), null_rows())
    nulls["B"]["summary"]["by_threshold"]["0.1"]["pass_rate_dev_positive"] = None
    w = redecide(nulls)
    assert w["chosen_threshold"] == 0.05 and "null B: pooled rate missing" in w["threshold_failures"]["0.1"][0]
    nulls["B"]["summary"]["by_threshold"]["0.1"]["pass_rate_dev_positive"] = float("nan")
    assert redecide(nulls)["chosen_threshold"] == 0.05


# ---------------------------------------------------------------- KP-017 item 3: a chosen draw that fails stage 1

def test_a_chosen_draw_that_fails_stage_1_counts_as_a_fault():
    rows = null_rows()
    for r in rows[:6]:
        stage1_failed(r)
    v, nulls = decide(rows, null_rows())
    s = nulls["A"]["summary"]
    assert s["n_stage1_fault"] == 6 and s["n_submitted"] == 194 and s["n_submitted_fault"] == 0
    assert v["null_fault_share"]["A"] == 6 / 200 and not v["STOP"]               # exactly at the 3% bound
    stage1_failed(rows[6])
    v, _ = decide(rows, null_rows())
    why = "null A: 7 of 200 candidate pairs (7 chosen draws failed stage 1) ended in a fault (0.0350) > NULL_FAULT_MAX"
    assert v["STOP"] and all(why in v["threshold_failures"][str(t)] for t in C.G6_GRID)
    rows = null_rows()                                                          # submitted faults and stage-1 together
    for r in rows[:4]:
        stage1_failed(r)
    for r in rows[4:7]:
        r.update(status="kernel_fault")
        r.pop("gates")
        r.pop("perm_p")
    v, _ = decide(rows, null_rows())
    assert v["STOP"] and v["null_fault_share"]["A"] == 7 / 200


def test_the_stage_1_fault_count_is_fail_closed():
    _, nulls = decide(null_rows(), null_rows())
    s = nulls["B"]["summary"]
    for bad in (None, True, -1, 1.0):
        keep = s["n_stage1_fault"]
        s["n_stage1_fault"] = bad
        w = redecide(nulls)
        assert w["STOP"] and w["null_fault_share"]["B"] is None, bad
        assert "the count of submitted pairs in a fault is missing or malformed" in w["reason"]
        s["n_stage1_fault"] = keep
    assert not redecide(nulls)["STOP"]


def test_a_stage_1_failure_of_another_kind_counts_too_and_a_not_submitted_pair_does_not():
    rows = null_rows()
    stage1_failed(rows[0])["status"] = "stage1_activity_dev"
    rows[1].update(submitted=False, status="not_submitted")
    for k in ("gates", "perm_p"):
        rows[1].pop(k)
    s = K.null_summary(rows, FIVE, 40, n_perm=NP)
    assert s["n_stage1_fault"] == 1 and s["n_not_submitted"] == 2


# ---------------------------------------------------------------- KP-017 item 4: tier_at and the p lattice

def lattice_row(p):
    return row("a", 0, p=p)


@pytest.mark.parametrize("n_perm", [C.UNIVERSE_G6_LAGS, C.PERM_N])
def test_every_point_of_the_lattice_is_accepted_also_after_a_json_round_trip(n_perm):
    assert (C.UNIVERSE_G6_LAGS, C.PERM_N) == (20, 200)
    for k in range(1, n_perm + 2):
        p = k / (n_perm + 1)
        for q in (p, json.loads(json.dumps(p)), np.float64(p)):
            assert PL.tier_at(lattice_row(q), 0.1, n_perm) == (q <= 0.1 + 1e-12)


@pytest.mark.parametrize("n_perm,p", [(20, 0.0), (20, 1.5 / 21), (20, 0.05), (20, 0.1), (20, 1 / 21 + 1e-8),
                                      (200, 0.05), (200, 0.0), (200, 10 / 201 + 1e-8), (20, 1 / 201)])
def test_a_p_off_its_lattice_raises(n_perm, p):
    with pytest.raises(ValueError) as e:
        PL.tier_at(lattice_row(p), 0.1, n_perm)
    assert "not on its lattice" in str(e.value)


def test_the_lattice_tolerance_and_bad_counts():
    assert PL.PERM_LATTICE_TOL == 1e-9
    PL.tier_at(lattice_row(1 / 21 + 1e-13), 0.1, 20)                          # within the tolerance
    for bad in (0, -1, True, 2.0, None):
        with pytest.raises(ValueError):
            PL.tier_at(lattice_row(1 / 21), 0.1, bad)
    assert PL.tier_at({"status": "liquidated"}, 0.1, 20) is False             # not evaluated: never Tier 1


def test_an_off_lattice_row_stops_the_unit_verdict_and_a_summary_raises():
    rows = [row(f, 11000 + i, p=2 / 21) for i in range(4) for f in UC.FAMILIES]
    with pytest.raises(ValueError):
        K.null_summary(rows + [row("ucal_xs_carry", 99, p=0.07)], list(UC.FAMILIES), 4, n_perm=20)
    assert K.null_summary(rows, list(UC.FAMILIES), 4, n_perm=20)["by_threshold"]["0.1"]["tier1"] == len(rows)
    art = {"families": {f: "x" for f in UC.FAMILIES}, "protocol": {"worlds_per_null": 1, "oracle_worlds": 1,
                                                                   "seeds": dict(UC.SEEDS)},
           "nulls": {n: {"rows": [dict(row(f, UC.SEEDS[n], p=0.07), null=n) for f in UC.FAMILIES]} for n in "AB"},
           "oracle": {n: {"rows": [{"null": n, "speed": s, "level": 1.5, "world_seed": UC.SEEDS["oracle_" + n],
                                    "status": "evaluated", "val_sharpe": 1.5, "perm_p": 1 / 21,
                                    "gates": {g: True for g in GATES}} for s in UC.USPEEDS]} for n in "AB"}}
    v = UC.unit_verdict(art, "top30")
    assert v["STOP"] and "malformed" in v["reason"] and "not on its lattice k / 21" in v["reason"]
    for n in "AB":
        for r in art["nulls"][n]["rows"]:
            r["perm_p"] = 2 / 21
    v = UC.unit_verdict(art, "top30")
    assert "not on its lattice" not in str(v.get("reason"))                     # (it stops on the small design)


# ---------------------------------------------------------------- the null advisory under KP-016

def nrows(null, worlds, fams, g3_false=0):
    out = [dict(row(f, 100 + w), null=null) for w in range(worlds) for f in fams]
    for r in out[:g3_false]:
        r["gates"]["G3"] = False
    return out


def test_the_advisory_reads_the_dev_positive_maximum_and_stage_1_faults():
    fams, W = ["m", "r", "c"], 50                                              # 150 designed pairs
    _, dead = UC._null_dead({"A": nrows("A", 20, fams, g3_false=50), "B": []}, W, fams, NP)
    assert dead == set()                                                       # at most 100 DEV-positive: still alive
    lines, dead = UC._null_dead({"A": nrows("A", 20, fams, g3_false=51), "B": []}, W, fams, NP)
    assert dead == set(C.G6_GRID) and "floor DEV-positive" in lines[0]
    rows = nrows("A", 40, fams)                                                # 4 passes over at most 150 DEV-positive
    for r in rows[:4]:
        r["perm_p"] = 0.08
    assert UC._null_dead({"A": rows, "B": []}, W, fams, NP)[1] == set()
    for r in rows[4:30]:
        r["gates"]["G3"] = False                                               # at most 124 DEV-positive: 4 / 124 > 3%
    assert UC._null_dead({"A": rows, "B": []}, W, fams, NP)[1] == {0.1}
    rows = nrows("A", 10, fams)
    for r in rows[:5]:
        stage1_failed(r)                                                       # 5 faults of 150 designed: 3.3% > 3%
    lines, dead = UC._null_dead({"A": rows, "B": []}, W, fams, NP)
    assert dead == set(C.G6_GRID) and "faults" in lines[0]


def test_the_advisory_never_calls_dead_what_the_completed_rows_could_still_qualify():
    rng = np.random.default_rng(7)
    fams, W = ["m", "r", "c"], 60
    for trial in range(25):
        final = nrows("A", W, fams)
        for r in final:
            u = rng.random()
            if u < 0.2:
                r["gates"]["G3"] = False
            elif u < 0.24:
                r["perm_p"] = float(rng.choice([0.02, 0.04, 0.08]))
            elif u < 0.25:
                stage1_failed(r)
            elif u < 0.27:
                r.update(status="liquidated")
                r.pop("gates")
                r.pop("perm_p")
        rng.shuffle(final)
        nulls = {"A": {"summary": K.null_summary(final, fams, W, n_perm=NP)},
                 "B": {"summary": K.null_summary(nrows("B", W, fams), fams, W, n_perm=NP)}}
        v = K.decide(nulls, {n: {"summary": K.oracle_summary(oracle_rows(), n_perm=NP)} for n in ("A", "B")})
        failing = {t for t in C.G6_GRID if v["threshold_failures"][str(t)]}
        for cut in (10, 60, 120, 180):
            dead = UC._null_dead({"A": final[:cut], "B": []}, W, fams, NP)[1]
            assert dead <= failing, (trial, cut, dead, failing)
