"""Census forward run on synthetic frames that extend past VAULT_END (no real data); frozen-source
and SEMANTICS_VERSION checks; pool admission by SEMANTICS_VERSION."""
import numpy as np
import pandas as pd
import pytest

from omr import census
from omr import constants as C
from omr import engine as E
from omr import lang as L
from omr import ledger
from omr import paths as P
from omr import pipeline
from omr import pool
from conftest import liq_of, prog_text, synth_raw

SRC = prog_text("x = param(0.8, 0.5, 1.0)\nsignal = x * sign(close / open)", name="t_always_long")


def setup_member(tmp_path, tid="t0t0t0t0t0t0t0t0", text=SRC, **over):
    (tmp_path / "sources").mkdir(exist_ok=True)
    src = tmp_path / "sources" / f"{tid}.omr"
    src.write_text(text, encoding="ascii")
    prog = L.parse(text, "t_always_long")
    row = {"trial_id": tid, "program": "t_always_long", "source_sha256": ledger.sha256_file(src), "params": {"x": 1.0},
           "canonical": prog.canonical, "semantics_version": C.SEMANTICS_VERSION,
           "born_at": "2026-11-20T05:20:00Z", "deploy_scale": 0.25}
    row.update(over)
    return row


def test_census_runs_flat_from_birth_on_post_birth_bars_only(tmp_path, monkeypatch):
    raws = {s: synth_raw(start="2026-10-01 00:00", end="2026-11-25 23:00", seed=5 + i) for i, s in enumerate(C.CORE)}
    from omr import datasets as D
    frames = {s: D.assemble_frame(r, D.PROGRAM_EXTRA) for s, r in raws.items()}
    liqs = {s: liq_of(r) for s, r in raws.items()}
    monkeypatch.setattr(P, "TRIAL_SOURCE_DIR", tmp_path / "sources")
    monkeypatch.setattr(P, "FORWARD_DIR", tmp_path / "forward")
    trow = setup_member(tmp_path)
    out = census.run_member(trow, {"at": "2026-11-20T06:40:00Z"}, frames, liqs)
    assert out["forward_start"] == "2026-11-20 07:00:00+00:00"
    assert out["days_forward"] == 5
    assert out["current_target_weights"] == {"BTCUSDT": 0.5, "ETHUSDT": 0.5}
    fwd = pd.read_parquet(tmp_path / "forward" / "t0t0t0t0t0t0t0t0.parquet")
    assert str(fwd.index[0].date()) == "2026-11-20"
    g = frames["BTCUSDT"].index
    s = g.get_loc(pd.Timestamp("2026-11-20 07:00", tz="UTC"))
    e = g.get_loc(pd.Timestamp("2026-11-21 00:00", tz="UTC"))
    mk = pipeline.Market(frames, liqs, g, C.CORE)
    out_e = E.run_arrays(mk.op[s:e + 1], mk.dn[s:e + 1], mk.up[s:e + 1], mk.fr[s:e + 1], np.full((e - s + 1, 2), 0.5))
    assert abs(fwd["ret_raw"].iloc[0] - (out_e[8][-1] - 1.0)) < 1e-12
    assert np.all(np.abs(fwd["ret_scaled"]) < np.abs(fwd["ret_raw"]) + 1e-15)
    early = census.forward_start({"born_at": "2024-01-01T00:00:00Z"}, {"at": "2024-01-02T00:00:00Z"})
    assert early == pd.Timestamp(C.VAULT_END, tz="UTC") + pd.Timedelta(hours=1)


@pytest.mark.parametrize("over,msg", [({"source_sha256": "0" * 64}, "ledger hash"),
                                      ({"semantics_version": C.SEMANTICS_VERSION + 1}, "SEMANTICS_VERSION"),
                                      ({"canonical": "kind=single;signal=x;params=[]"}, "canonical")])
def test_census_refuses_tampered_or_incompatible_members(tmp_path, monkeypatch, over, msg):
    monkeypatch.setattr(P, "TRIAL_SOURCE_DIR", tmp_path / "sources")
    trow = setup_member(tmp_path, **over)
    with pytest.raises(RuntimeError) as e:
        census.member_program(trow)
    assert msg in str(e.value)


def test_pool_admission_needs_tier1_and_the_same_semantics_version(tmp_ledger, monkeypatch):
    from omr import kernel_lock
    monkeypatch.setattr(kernel_lock, "read_lock", lambda *a, **k: {"combined": "k" * 64})
    base = {"status": "evaluated", "tier": "tier1", "program": "p", "kernel_hash": "old" * 21 + "x",
            "deploy_scale": 0.5, "born_at": "2026-11-20T00:00:00Z"}
    ledger.append_pending({"trial_id": "a" * 16, "generation": 0})
    ledger.append(P.TRIALS_JSONL, dict(base, trial_id="a" * 16, semantics_version=C.SEMANTICS_VERSION))
    ledger.append_pending({"trial_id": "b" * 16, "generation": 0})
    ledger.append(P.TRIALS_JSONL, dict(base, trial_id="b" * 16, semantics_version=C.SEMANTICS_VERSION + 1))
    pool.admit("a" * 16, "test")                                         # other kernel hash, same semantics: admitted
    assert pool.members()["a" * 16]["kernel_hash"] == base["kernel_hash"]
    with pytest.raises(SystemExit):
        pool.admit("b" * 16, "test")
