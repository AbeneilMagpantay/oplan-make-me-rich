"""KP-018 (the sandbox's DEV readings for unit top30) and the KP-017 rider (g6_lag_detail): the universe engine's
gross funding totals, the refactored G6 code (g6_memory, the paired lag loop, next30_score) equal to the code it
replaced, the DEV readings, the per-lag detail (it reproduces p; never in a trial), and the sandbox end to end on
synthetic disk data (DEV rows only, the log row before any print). Synthetic data only."""
import numpy as np
import pandas as pd
import pytest

from conftest import SynthProvider, make_disk_data, prog_text, synth_universe, synth_world
from omr import constants as C
from omr import data
from omr import datasets as D
from omr import engine as E
from omr import kernel_lock
from omr import lang as L
from omr import ledger
from omr import paths as P
from omr import pipeline as PL
from omr import sandbox
from omr import stats as S
from omr import universe as U
from omr import upipeline as UP


def top30(body, name="x_test"):
    return L.parse(prog_text(body, kind="portfolio", name=name).replace("hypothesis", 'unit = "top30"\nhypothesis', 1),
                   name, probe=False)


PROG = "n = param(7, 5, 9)\nsignal = cs_scale(cs_demean(sma(tf_mean(cs_rank(ret(close, 1)), daily), n)))\n"


@pytest.fixture(scope="module")
def uni():
    return synth_universe(seed=5, n=40)


@pytest.fixture(scope="module")
def ud_dev(uni):
    tables, table, btc = uni
    return UP.udata_from_tables(tables, btc, C.DEV_END, symbols_table=table)


@pytest.fixture(scope="module")
def ud_full(uni):
    tables, table, btc = uni
    return UP.udata_from_tables(tables, btc, C.VAL_END, symbols_table=table)


@pytest.fixture(scope="module")
def dev_book(ud_dev):
    prog = top30(PROG)
    q = L.default_params(prog)
    fp = UP.Blocked(ud_dev, "top30", fields=UP.program_fields(prog))
    W, raw, kn = fp.unit(prog, q)
    return prog, q, fp, W, kn, fp.inplay()


# ---------------------------------------------------------------- the universe engine's gross funding totals

def _arrays(seed, T=2000, K=5):
    rng = np.random.default_rng(seed)
    op = 50 * np.exp(np.cumsum(0.01 * rng.standard_normal((T, K)), axis=0))
    cl = op * np.exp(0.002 * rng.standard_normal((T, K)))
    av = rng.uniform(size=(T, K)) > 0.02
    dn, up = np.full((T, K), 0.99), np.full((T, K), 1.01)
    fr = np.where((np.arange(T) % 8 == 0)[:, None], 3e-4 * rng.standard_normal((T, K)), 0.0)
    tgt = np.repeat(rng.uniform(-0.2, 0.2, (T // 24 + 1, K)), 24, axis=0)[:T]
    return op, cl, av, dn, up, fr, tgt


@pytest.mark.parametrize("pay,recv", [(1.0, 1.0), (1.5, 0.5), (1.0, 0.0)])
def test_gross_funding_totals_add_up_to_the_net_and_carry_across_blocks(pay, recv):
    op, cl, av, dn, up, fr, tgt = _arrays(1)
    out = E.run_block_u(op, cl, av, dn, up, fr, tgt, pay_mult=pay, recv_mult=recv)
    assert len(out) == 14 and out[12] > 0 and (out[13] > 0 or recv == 0.0)
    assert abs((out[12] - out[13]) - out[6]) <= 1e-12 * max(1.0, abs(out[12]) + abs(out[13]))
    if recv == 0.0:
        assert out[13] == 0.0
    a = E.run_block_u(op[:901], cl[:901], av[:901], dn[:901], up[:901], fr[:901], tgt[:901], pay_mult=pay, recv_mult=recv)
    b = E.run_block_u(op[900:], cl[900:], av[900:], dn[900:], up[900:], fr[900:], tgt[900:], pay_mult=pay, recv_mult=recv,
                      h0=a[9], eq0=a[10], dead0=a[11], t0=1, fp0=a[6], pg0=a[12], rg0=a[13])
    assert (b[12], b[13], b[6]) == (out[12], out[13], out[6])                 # carried bit for bit
    slow = E.run_block_u(op, cl, av, dn, up, fr, tgt, pay_mult=pay, recv_mult=recv, fast=False)
    assert slow[12] == pytest.approx(out[12], rel=1e-12) and slow[13] == pytest.approx(out[13], rel=1e-12, abs=1e-15)
    for i in range(12):                                                        # the existing outputs (numba = Python)
        x, y = out[i], slow[i]
        assert np.allclose(x, y, rtol=0, atol=1e-10) if isinstance(x, np.ndarray) else abs(float(x) - float(y)) < 1e-10


def test_run_arrays_u_and_run_u_keep_their_shape():
    op, cl, av, dn, up, fr, tgt = _arrays(2)
    assert len(E.run_arrays_u(op, cl, av, dn, up, fr, tgt)) == 9
    r = E.run_u(pd.date_range("2021-01-01", periods=len(op), freq="h", tz="UTC"), op, cl, av, dn, up, fr, tgt)
    assert np.isnan(r.funding_paid_gross) and np.isnan(r.funding_received_gross)  # only block runs carry them


def test_blocked_runs_carry_the_totals(dev_book):
    prog, q, fp, W, kn, inplay = dev_book
    s, e = fp.pos(C.DEV_START), fp.pos(C.DEV_END)
    run = fp.run(W, s, e)
    one = UP.Blocked(fp.ud, "top30", months=None, fields=UP.program_fields(prog)).run(W, s, e)
    assert run.funding_paid_gross == one.funding_paid_gross and run.funding_received_gross == one.funding_received_gross
    assert abs(run.funding_paid_gross - run.funding_received_gross - run.funding_paid) < 1e-12


# ---------------------------------------------------------------- refactors equal the code they replaced

def old_g6_memory(W, P_, ok, g0, step, n):
    """omr.upipeline.g6_memory as it was at 469c1cd (copied for the comparison)."""
    L_ = len(ok)
    Wa = W[g0:g0 + L_]
    best = None
    for j in range(1, n):
        k = j * step
        if g0 - k < 0:
            raise PL.KernelFault("lag reaches before the grid")
        Ws = W[g0 - k:g0 - k + L_]
        mask = ok & P_[g0 - k:g0 - k + L_]
        cnt = mask.sum(axis=0)
        cols = cnt >= 2
        den = np.where(cnt > 0, cnt, 1)
        ma = UP._seq_colsum(np.where(mask, Wa, 0.0)) / den
        ms = UP._seq_colsum(np.where(mask, Ws, 0.0)) / den
        a = np.where(mask, Wa - ma, 0.0)
        s = np.where(mask, Ws - ms, 0.0)
        num = UP._seq_sum(UP._seq_colsum(a * s)[cols])
        saa = UP._seq_sum(UP._seq_colsum(a * a)[cols])
        sss = UP._seq_sum(UP._seq_colsum(s * s)[cols])
        with np.errstate(divide="ignore", invalid="ignore"):
            r = num / float(np.sqrt(saa * sss)) if saa > 0.0 and sss > 0.0 else float("nan")
        if not np.isfinite(r):
            r = 1.0
        best = r if best is None else max(best, r)
    return 0.0 if best is None else float(best)


def test_g6_memory_equals_the_old_code_bit_for_bit():
    rng = np.random.default_rng(5)
    for trial in range(6):
        T, K = 3000, 12
        W = np.repeat(rng.standard_normal((T // 24 + 1, K)), 24, axis=0)[:T] * (rng.uniform(size=(1, K)) > 0.2)
        if trial == 0:
            W[:] = 0.3                                                         # a book that never changes: 1.0
        P_ = rng.uniform(size=(T, K)) > 0.1
        ok = P_[1500:2600] & (rng.uniform(size=(1100, K)) > 0.05)
        for n in (1, 2, 4, 20):
            step = 70 if n == 20 else 300
            new, old = UP.g6_memory(W, P_, ok, 1500, step, n), old_g6_memory(W, P_, ok, 1500, step, n)
            assert np.float64(new).view(np.int64) == np.float64(old).view(np.int64)
            if n > 1:
                assert UP.g6_memory_by_lag(W, P_, ok, 1500, step, n)[n - 2] <= new
    with pytest.raises(PL.KernelFault):
        UP.g6_memory(W, P_, ok, 1500, 600, 4)
    assert UP.g6_step(UP.val_rows(), C.UNIVERSE_G6_LAGS) == 621 and UP.val_rows() == 26304


def test_the_paired_lag_loop_equals_the_old_inline_loop(ud_full, val_handle):
    prog = top30(PROG)
    q = L.default_params(prog)
    fp = UP.Blocked(ud_full, "top30", fields=UP.program_fields(prog))
    W, _, _ = fp.unit(prog, q, raw_rows=0)
    val_s, val_e = fp.pos(C.VAL_START), fp.pos(C.VAL_END)
    g0 = val_s - 1
    inplay = fp.inplay()
    ok = inplay[g0:val_e] & fp.eng_rows("av", val_s, val_e)

    def vrun(tgt):                                                             # the old ugates.vrun
        run = fp.run_targets(np.where(ok, tgt, 0.0), val_s, val_e)
        if run.liquidated:
            return float("-inf")
        return S.sharpe(run.daily_returns().to_numpy())

    plain = np.where(ok, W[g0:val_e], 0.0)
    actual = vrun(plain)
    offs, step = UP.g6_lags(val_e - val_s + 1, g0, np.random.default_rng(3), 6)
    a_old, s_old = np.zeros(len(offs)), np.zeros(len(offs))
    t_old = np.zeros(len(offs), dtype=bool)
    for j, k in enumerate(offs):
        A_k, S_k = UP.g6_books(W, inplay, ok, g0, int(k))
        a_old[j] = actual if np.array_equal(A_k, plain) else vrun(A_k)
        t_old[j] = UP.g6_books_tie(A_k, S_k)
        s_old[j] = a_old[j] if t_old[j] else vrun(S_k)
    run_book = UP.g6_book_runner(fp, ok, val_s, val_e)
    act = run_book(plain)
    assert np.float64(act[0]).view(np.int64) == np.float64(actual).view(np.int64)
    a_new, s_new, t_new, a_st, s_st = UP.g6_paired_runs(W, inplay, ok, g0, offs, plain, act, run_book)
    assert a_new.tobytes() == a_old.tobytes() and s_new.tobytes() == s_old.tobytes() and np.array_equal(t_new, t_old)
    assert [x["sharpe"] for x in a_st] == list(a_new) and [x["sharpe"] for x in s_st] == list(s_new)


def test_next30_score_end_and_keep(ud_full, ud_dev):
    prog = top30(PROG)
    q = L.default_params(prog)
    a = UP.next30_score(prog, q, ud_full)
    assert a == UP.next30_score(prog, q, ud_full, end=C.VAL_END, keep=True)
    b = UP.next30_score(prog, q, ud_dev, end=C.DEV_END)
    assert b == UP.next30_score(prog, q, ud_dev, end=C.DEV_END, keep=True)
    assert (a["code"] is None) == (b["code"] is None)


# ---------------------------------------------------------------- the DEV readings

def test_dev_speed_limit_is_g6s_own_statistic_on_dev_rows(dev_book):
    prog, q, fp, W, kn, inplay = dev_book
    r = UP.dev_speed_limit(fp, W, kn, inplay)
    assert r["ok"] and r["step"] == 621 and len(r["r"]) == 3 and r["limit"] == C.UNIVERSE_G6_MEMORY_MAX
    g0 = int(fp.grid.get_loc(r["start"]))
    first = int(np.nonzero(kn.any(axis=1))[0][0])
    dev_e = len(fp.ns) - 1
    assert g0 == max(fp.pos(C.DEV_START) - 1, first + 3 * 621) and fp.grid[dev_e - 1] == r["end"]
    ok = inplay[g0:dev_e] & fp.eng_rows("av", g0 + 1, dev_e)
    assert r["r"] == UP.g6_memory_by_lag(W, inplay, ok, g0, 621, 4) and r["max"] == UP.g6_memory(W, inplay, ok, g0, 621, 4)
    assert r["over"] == (not r["max"] <= 0.5)
    never = UP.dev_speed_limit(fp, W, np.zeros_like(kn), inplay)
    assert not never["ok"] and "never known" in never["reason"]


def test_dev_paired_lags_runs_g6s_comparison_on_the_last_year(dev_book):
    prog, q, fp, W, kn, inplay = dev_book
    r = UP.dev_paired_lags(fp, W, kn, inplay)
    assert r["ok"] and r["lags"] == 10 and r["lag_min"] == 720 and r["lag_max"] == 720 + 9 * 621
    k = r["p"] * 11
    assert abs(k - round(k)) < 1e-9 and r["at_least_as_good"] == round(k) - 1
    assert str(r["end"]) == "2022-06-30 22:00:00+00:00"
    short = UP.dev_paired_lags(fp, W, kn, inplay, hours=24 * 700)              # the lagged rows before the first known
    assert not short["ok"] and "not enough DEV history" in short["reason"]


def test_dev_names_held_counts_names_with_a_weight():
    W = np.array([[0.0, 0.0, 0.0], [0.5, -0.5, 0.0], [0.2, 0.0, 0.0], [0.1, 0.1, 0.1]])
    P_ = np.array([[False] * 3, [True, True, True], [True, True, False], [True] * 3])
    out = UP.dev_names_held(W, P_, 1, 4)                                       # decision rows 0 .. 3
    assert out == {"held": (2 + 1 + 3) / 3, "inplay": (3 + 2 + 3) / 3, "rows": 3}
    assert UP.dev_names_held(W, np.zeros_like(P_), 1, 4)["held"] is None


# ---------------------------------------------------------------- g6_lag_detail (KP-017 rider)

def test_the_per_lag_detail_reproduces_p_and_never_enters_a_trial(tmp_path, tmp_ledger, ud_dev, ud_full):
    from omr import evaluate
    src = tmp_path / "x_lagd.omr"
    src.write_text(prog_text(PROG, kind="portfolio", name="x_lagd").replace("hypothesis", 'unit = "top30"\nhypothesis', 1),
                   encoding="ascii")
    prov = SynthProvider(synth_world(seed=3), universe=(ud_dev, ud_full))
    seen = {}
    real = UP.ugates

    def spy(*a, **k):
        res = real(*a, **k)
        seen["res"] = res
        return res
    UP.ugates, keep = spy, UP.ugates
    try:
        row = evaluate.evaluate_file(str(src), 0, provider=prov, quiet=True, require_lock=False, p_max=0.1,
                                     opts=PL.Opts(jitter_n=2, truncation_cuts=2, start_cuts=1, start_cuts_val=1))
    finally:
        UP.ugates = keep
    assert row["status"] == "evaluated"
    det = seen["res"]["g6_lag_detail"]
    assert "g6_lag_detail" not in row and "g6_lag_detail" not in (P.TRIAL_DETAIL_DIR / f"{row['trial_id']}.json").read_text()
    lags = det["lags"]
    assert len(lags) == C.UNIVERSE_G6_LAGS and 720 <= lags[0] < 720 + 621
    assert all(lags[i + 1] - lags[i] == 621 for i in range(len(lags) - 1))
    a, s, t = det["a"]["sharpe"], det["s"]["sharpe"], det["tie"]
    ge = sum(1 for x, y, z in zip(a, s, t) if z or y >= x - C.G6_PAIRED_SHARPE_MARGIN)
    assert (1 + ge) / (len(lags) + 1) == row["gate_values"]["G6"]
    assert set(det["a"]) == set(det["s"]) == set(UP.BOOK_STATS) and set(det["actual"]) == set(UP.BOOK_STATS)
    for book in (det["a"], det["s"]):
        for j in range(len(lags)):
            if book["sd"][j] is not None:
                assert book["mean_gross"][j] >= book["mean"][j] and book["costs"][j] >= 0 and book["rebalances"][j] >= 0
    assert det["actual"]["sharpe"] == seen["res"]["detail"]["permutation"]["actual_val_sharpe_restarted"]


def test_book_stats_and_daily_cost_shares():
    op, cl, av, dn, up, fr, tgt = _arrays(3)
    idx = pd.date_range("2021-01-01", periods=len(op), freq="h", tz="UTC")
    run = E.run_u(idx, op, cl, av, dn, up, fr, tgt)
    d = run.daily_returns().to_numpy()
    st = UP.book_stats(run, d, S.sharpe(d))
    share = E.daily_cost_shares(run.pre, run.ev_idx, run.ev_cost, run.index)
    assert len(share) == len(d) and st["sharpe"] == S.sharpe(d) and st["rebalances"] == run.n_rebalances
    starts = np.r_[1.0, run.pre[E.day_points(idx)][1:]]
    assert abs(float(np.sum(share * starts)) - float(run.ev_cost.sum())) < 1e-12
    assert st["mean_gross"] == pytest.approx(float(np.mean(d + share)))
    free = E.run_u(idx, op, cl, av, dn, up, fr, tgt, cost_rate=0.0)
    df = free.daily_returns().to_numpy()
    assert UP.book_stats(free, df, S.sharpe(df))["mean_gross"] == float(np.mean(df))
    assert UP.book_stats(run, None, float("-inf")) == {"sharpe": float("-inf"), "sd": None, "mean": None,
                                                       "mean_gross": None, "costs": None, "funding": None,
                                                       "rebalances": None}


# ---------------------------------------------------------------- the sandbox end to end

@pytest.fixture(scope="module")
def disk_root(tmp_path_factory):
    root = tmp_path_factory.mktemp("kp018_disk")
    make_disk_data(root, universe=True)
    return root


@pytest.fixture
def env(disk_root, tmp_path, monkeypatch):
    monkeypatch.setattr(data, "DATA_DIR", disk_root)
    monkeypatch.setattr(data, "MANIFEST", disk_root / "manifest.json")
    monkeypatch.setattr(U, "SYMBOLS_FILE", disk_root / "symbols.json")
    monkeypatch.setattr(data, "VALIDATION", disk_root / "validation.json")
    data._CACHE.clear()
    monkeypatch.setattr(P, "SANDBOX_LOG", tmp_path / "sandbox_log.jsonl")
    monkeypatch.setattr(kernel_lock, "require_kernel", lambda: {"combined": "k" * 64})
    printed, appended_at, ceilings = [], [], set()
    monkeypatch.setattr(sandbox, "print", lambda *a, **k: printed.append(" ".join(str(x) for x in a)), raising=False)
    real_append, real_load = ledger.append, D.load_raw

    def spy(path, row):
        appended_at.append(len(printed))
        return real_append(path, row)

    def load(ds, s, upto=None, handle=None, cache=True):
        ceilings.add(upto)
        return real_load(ds, s, upto=upto, handle=handle, cache=cache)
    monkeypatch.setattr(ledger, "append", spy)
    monkeypatch.setattr(D, "load_raw", load)
    f = tmp_path / "x_sbx.omr"
    f.write_text(prog_text(PROG, kind="portfolio", name="x_sbx").replace("hypothesis", 'unit = "top30"\nhypothesis', 1),
                 encoding="ascii")
    yield f, printed, appended_at, ceilings
    data._CACHE.clear()


def test_the_sandbox_prints_and_logs_the_dev_readings(env):
    f, printed, appended_at, ceilings = env
    sandbox.main([str(f), "--quick", "--g6-lags"])
    assert ceilings == {"dev_end"}                                             # no row after DEV end is read
    rows = ledger.read_rows(P.SANDBOX_LOG)
    assert len(rows) == 1 and appended_at == [0] and ledger.verify_chain(P.SANDBOX_LOG) == []
    r = rows[0]
    for k in ("g6_memory_dev", "g6_memory_dev_max", "g6_memory_dev_from", "next30_dev_sharpe", "next30_code",
              "next30_symbols", "funding_paid_gross", "funding_received_gross", "g2_dev_sharpe", "g4_dev_sharpe",
              "names_held_avg", "names_inplay_avg", "g6_paired_dev", "dev_sharpe"):
        assert k in r, k
    assert len(r["g6_memory_dev"]) == 3 and r["g6_memory_dev_from"] < "2022-07-01"
    assert r["g6_paired_dev"]["lags"] == 10 and 0 <= r["names_held_avg"] <= r["names_inplay_avg"] <= 30
    text = "\n".join(printed)
    assert "top30 readings on DEV rows only (uncounted; KP-018):" in text
    assert "G6 speed limit as G6 computes it (lag step 621 h" in text and "limit 0.50" in text
    assert "next30 (G8's unit, ranks 31-60)" in text and "funding paid" in text and "names held: average" in text
    assert "G2 on DEV (funding paid x1.5, received x0.5)" in text and "G4 on DEV (costs x2)" in text
    assert "G6 paired lag reading - a DEV reading, NOT the gate" in text
    ud = UP.load_udata("dev_end", fields=UP.program_fields(L.parse_file(f)))   # the same readings, recomputed
    prog = L.parse_file(f)
    n30 = UP.next30_score(prog, L.default_params(prog), ud, end=C.DEV_END)
    assert r["next30_dev_sharpe"] == n30.get("sharpe") and r["next30_code"] == n30.get("code")


def test_a_default_run_has_no_paired_reading(env):
    f, printed, _, _ = env
    sandbox.main([str(f), "--quick"])
    assert "g6_paired_dev" not in ledger.read_rows(P.SANDBOX_LOG)[0]
    assert not any("paired lag reading" in line for line in printed)
