"""omr.evaluate end to end on synthetic data and a temporary ledger: write order, dedupe, counting,
stage-1 rejections in stage1_log only, generation rules (allowed numbers, PLAN.md, the cap of 5
refused before any row), pending-row contents, stage-2 exceptions as kernel_fault (never a pending row
left behind), the sealed-lock requirement, and the data-validation requirement."""
import json

import numpy as np
import pandas as pd
import pytest

from omr import constants as C
from omr import evaluate
from omr import kernel_lock
from omr import ledger
from omr import paths as P
from omr import pipeline
from omr import stats as S
from conftest import SynthProvider, prog_text, synth_world

FAST = pipeline.Opts(jitter_n=3, perm_n=30, truncation_cuts=4)
NOISE = (prog_text("n = param(20, 10, 40)\nv = daily(volume)\nsignal = 2 * rank(v / lag(v, 1), n) - 1",
                   name="t_noise"))


class Prov(SynthProvider):
    def __init__(self, world, on_val=None, raise_val=None):
        super().__init__(world)
        self.on_val, self.raise_val, self.val_calls = on_val, raise_val, 0

    def val_world(self, handle):
        w = super().val_world(handle)
        self.val_calls += 1
        if self.on_val:
            self.on_val()
        if self.raise_val is not None:
            raise self.raise_val
        return w


def write(tmp_path, text, stem):
    f = tmp_path / f"{stem}.omr"
    f.write_text(text, encoding="ascii")
    return f


def run(f, prov, gen=0):
    return evaluate.evaluate_file(str(f), gen, provider=prov, opts=FAST, quiet=True, require_lock=False, p_max=0.05)


@pytest.fixture(scope="module")
def world():
    return synth_world(seed=31, extended=8)


def test_write_order_dedupe_counting_and_pending_contents(tmp_path, tmp_ledger, world):
    seen = {}

    def at_val():
        st = ledger.trial_states()
        seen["rows"] = [r["status"] for t in st.values() for r in t["rows"]]
        seen["returns"] = list(P.RETURNS_DIR.glob("*")) if P.RETURNS_DIR.exists() else []
        seen["detail"] = list(P.TRIAL_DETAIL_DIR.glob("*")) if P.TRIAL_DETAIL_DIR.exists() else []

    f = write(tmp_path, NOISE, "t_noise")
    row = run(f, Prov(world, at_val))
    assert seen == {"rows": ["pending"], "returns": [], "detail": []}
    rows = ledger.trials()
    assert [r["status"] for r in rows] == ["pending", "evaluated"]
    pend = rows[0]
    assert rows[1]["pending_hash"] == pend["row_hash"] and row["status"] == "evaluated"
    assert ledger.counted_ids() == [row["trial_id"]] and row["M"] == 1
    assert pend["plan_sha256"] == ledger.sha256_file(P.GENERATIONS_DIR / "gen000" / "PLAN.md")
    assert set(pend["versions"]) == {"python", "numpy", "pandas", "numba", "pyarrow", "scipy"}
    from omr import kernel_lock
    k = kernel_lock.compute()
    assert pend["semantic_hash"] == k["semantic"] and pend["text_hash"] == k["text"] and pend["node_count"] > 0
    assert pend["stage1"]["start_cuts"] == FAST.start_cuts and "semantics_version" not in pend
    assert pend["canonical"].startswith("kind=single;signal=") and pend["params"] == {"n": 20}
    assert (P.TRIAL_SOURCE_DIR / f"{row['trial_id']}.omr").read_bytes() == f.read_bytes()
    assert "eval_seconds" not in row and "eval_seconds" not in pend
    assert set(row["gates"]) == {"G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8", "G10"}
    assert row["g6_threshold"] == 0.05 and row["direction_changes_val"] >= 12
    detail = json.loads((P.TRIAL_DETAIL_DIR / f"{row['trial_id']}.json").read_text())
    assert len(detail["extended"]) == 8
    # C4: no time-resolved VAL performance is stored
    assert [r["year"] for r in detail["per_year"]] == [2020, 2021]
    assert [set(b) for b in detail["buckets"]] == [{"bucket", "n_days", "return"}] * 2 + [{"bucket", "n_days"}] * 4
    assert set(row["gate_values"]["G7"]) == {"n_positive", "largest_share"}
    assert pend["n_literals"] == 2 and row["n_literals"] == 2 and row["node_count"] == pend["node_count"]
    for b in detail["buckets"]:                                       # no VAL period appears with a value
        assert ("return" in b) == (b["bucket"] in ("2020", "2021"))
    # dedupe: identical program (even renamed names and comments) returns the existing row, appends nothing
    g = write(tmp_path, NOISE.replace("v = daily(volume)\nsignal = 2 * rank(v / lag(v, 1), n) - 1",
                                      "# same idea\nq = daily(volume)\nsignal = 2 * rank(q / lag(q, 1), n) - 1"), "t_noise")
    again = run(g, Prov(world))
    assert again["trial_id"] == row["trial_id"] and len(ledger.trials()) == 2
    assert ledger.verify_all(log=lambda s: None)


def test_stage1_rejections_go_to_stage1_log_only(tmp_path, tmp_ledger, world):
    prov = Prov(world)
    bad = write(tmp_path, prog_text("signal = close.shift(-1) / close", name="t_bad"), "t_bad")
    r = run(bad, prov)
    assert r["code"] == "parse:call" and r["line"] == 5
    flat = write(tmp_path, prog_text("signal = sign(ret(close, 1)) + 2", name="t_flat"), "t_flat")
    r2 = run(flat, prov)
    assert r2["code"] == "activity_dev" and r2["direction_changes_dev"] == 0
    assert prov.val_calls == 0 and ledger.trials() == [] and ledger.counted_ids() == []
    assert [x["code"] for x in ledger.read_rows(P.STAGE1_LOG)] == ["parse:call", "activity_dev"]
    assert ledger.verify_chain(P.STAGE1_LOG) == []


def test_stage1_interpreter_exception_is_an_uncounted_kernel_fault(tmp_path, tmp_ledger, world, monkeypatch):
    def boom(*a, **k):
        raise ZeroDivisionError("x")
    monkeypatch.setattr(pipeline, "stage1", boom)
    r = run(write(tmp_path, NOISE, "t_noise"), Prov(world))
    assert r["code"] == "kernel_fault" and r["error_type"] == "ZeroDivisionError" and ledger.trials() == []


def test_stage2_exception_is_a_counted_kernel_fault_without_metrics(tmp_path, tmp_ledger, world):
    r = run(write(tmp_path, NOISE, "t_noise"), Prov(world, raise_val=RuntimeError("disk")))
    assert r["status"] == "kernel_fault" and r["reason"] == "exception" and r["error_type"] == "RuntimeError"
    assert not {"val_sharpe", "dev_sharpe", "gates", "tier", "returns_sha256"} & set(r)
    st = ledger.trial_states()
    assert [t["status"] for t in st.values()] == ["kernel_fault"]           # counted, not incomplete
    msgs = []
    assert ledger.verify_all(log=msgs.append) and not any(m.startswith("INCOMPLETE") for m in msgs)


def test_interrupt_after_pending_writes_kernel_fault_then_reraises(tmp_path, tmp_ledger, world):
    with pytest.raises(KeyboardInterrupt):
        run(write(tmp_path, NOISE, "t_noise"), Prov(world, raise_val=KeyboardInterrupt()))
    st = ledger.trial_states()
    assert [t["status"] for t in st.values()] == ["kernel_fault"] and len(ledger.counted_ids()) == 1


def test_stage2_dev_row_mismatch_is_a_kernel_fault(tmp_path, tmp_ledger, world, monkeypatch):
    orig = pipeline.stage1

    def tampered(*a, **k):
        s1 = orig(*a, **k)
        s1["raw"] = s1["raw"].copy()
        s1["raw"][-1, 0] = 7.0
        return s1
    monkeypatch.setattr(pipeline, "stage1", tampered)
    r = run(write(tmp_path, NOISE, "t_noise"), Prov(world))
    assert r["status"] == "kernel_fault" and r["reason"] == "dev_rows_changed"


def test_generation_rules(tmp_path, tmp_ledger, world):
    f = write(tmp_path, NOISE, "t_noise")
    with pytest.raises(evaluate.Refused):
        run(f, Prov(world), gen=1)                                     # empty ledger: only generation 0
    for i in range(C.MAX_COUNTED_PER_GENERATION):
        ledger.append_pending({"trial_id": f"{i:016d}", "generation": 0})
    before = len(ledger.trials())
    with pytest.raises(evaluate.Refused) as e:
        run(f, Prov(world), gen=0)                                     # the 6th counted trial of gen 0
    assert "max" in str(e.value) and len(ledger.trials()) == before and ledger.read_rows(P.STAGE1_LOG) == []
    with pytest.raises(evaluate.Refused) as e:
        run(f, Prov(world), gen=1)                                     # gen 1 allowed by number but no PLAN.md
    assert "PLAN.md" in str(e.value)
    with pytest.raises(evaluate.Refused):
        run(f, Prov(world), gen=2)                                     # not highest or highest + 1
    (P.GENERATIONS_DIR / "gen001").mkdir()
    (P.GENERATIONS_DIR / "gen001" / "PLAN.md").write_text("plan 1\n", encoding="ascii")
    with pytest.raises(evaluate.Refused) as e:
        run(f, Prov(world), gen=1)                                     # M4: generation 0 has no REPORT.md yet
    assert "REPORT.md" in str(e.value)
    (P.GENERATIONS_DIR / "gen000" / "REPORT.md").write_text("report 0\n", encoding="ascii")
    r = run(f, Prov(world), gen=1)
    assert r["status"] == "evaluated" and r["generation"] == 1
    with pytest.raises(evaluate.Refused):
        run(f, Prov(world), gen=0)                                     # cannot go back below highest


def test_evaluate_refuses_an_unsealed_lock(monkeypatch):
    monkeypatch.setattr(kernel_lock, "verify", lambda *a, **k: [])
    monkeypatch.setattr(kernel_lock, "read_lock", lambda *a, **k: {"combined": "c" * 64, "files": {}})
    with pytest.raises(SystemExit) as e:
        evaluate.evaluate_file("x.omr", 0)
    assert e.value.code == 4


def test_disk_provider_refuses_unvalidated_or_mismatched_data(monkeypatch):
    from omr import data
    monkeypatch.setattr(data, "load_manifest", lambda: {"research_hash": "a"})
    monkeypatch.setattr(data, "research_hash_from_disk", lambda m=None: "a")
    monkeypatch.setattr(data, "validation_ok", lambda: False)
    with pytest.raises(evaluate.Refused) as e:
        evaluate.DiskProvider().check()
    assert "validate" in str(e.value)
    monkeypatch.setattr(data, "research_hash_from_disk", lambda m=None: "b")
    with pytest.raises(evaluate.Refused):
        evaluate.DiskProvider().check()


def test_dsr_for_counts_trials_without_returns_in_m_only(tmp_ledger):
    rng = np.random.default_rng(0)
    days = pd.date_range("2022-07-01", "2025-06-30", freq="D", tz="UTC")
    r1 = pd.Series(0.001 + 0.02 * rng.standard_normal(len(days)), index=days)
    sha = ledger.save_returns("aaaaaaaaaaaaaaaa", r1)
    ledger.append_pending({"trial_id": "aaaaaaaaaaaaaaaa", "generation": 0})
    ledger.append(P.TRIALS_JSONL, {"trial_id": "aaaaaaaaaaaaaaaa", "status": "evaluated", "returns_sha256": sha})
    ledger.append_pending({"trial_id": "bbbbbbbbbbbbbbbb", "generation": 0})
    ledger.append_pending({"trial_id": "cccccccccccccccc", "generation": 0})
    cur = pd.Series(0.002 + 0.02 * rng.standard_normal(len(days)), index=days)
    d = evaluate.dsr_for("cccccccccccccccc", cur)
    assert d["M"] == 3
    mat = ledger.counted_val_matrix(extra={"cccccccccccccccc": cur})
    assert mat.shape[1] == 2
    assert abs(d["rho"] - S.mean_pairwise_corr(mat)) < 1e-15
    assert abs(d["N"] - S.effective_n(3, d["rho"])) < 1e-12


def test_a_probe_exception_is_logged_as_probe_fault(tmp_path, tmp_ledger, world, monkeypatch):
    """P3: an exception while the constant probe evaluates a program is a kernel bug: stage-1 log code
    probe_fault with the exception type, uncounted, never shown as the researcher's parse error."""
    from omr import interp as X

    def boom(*a, **k):
        raise ZeroDivisionError("x")
    monkeypatch.setattr(X, "evaluate_full", boom)
    r = run(write(tmp_path, NOISE, "t_noise"), Prov(world))
    assert r["code"] == "probe_fault" and r["error_type"] == "ZeroDivisionError" and ledger.trials() == []
