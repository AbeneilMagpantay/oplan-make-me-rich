"""U1: G6 in universe units is a PAIRED test on the names common to the actual row and the shifted row's
source (upipeline.g6_books / ugates). Synthetic data only."""
import numpy as np
import pytest

from conftest import PROGRAMS, synth_raw, synth_udata
from omr import constants as C
from omr import datasets as D
from omr import lang as L
from omr import pipeline as PL
from omr import stats as S
from omr import ucalibrate as UC
from omr import upipeline as UP


def _seq(x):
    return UP._seq_rowsum(x)


def check_books(Wv0, D_, ok, k):
    """Every property U1 asks of the paired books of shift k; returns (rows re-centred, flat rows)."""
    A, S_ = UP.g6_books(Wv0, D_, ok, k)
    L_ = len(Wv0)
    src = (np.arange(L_) - k) % L_
    Ws, Ds = Wv0[src], D_[src]
    mask = ok & Ds
    nm = mask.sum(axis=1)
    flat = nm < C.UNIVERSE_MIN_CS
    assert not A[flat].any() and not S_[flat].any()                       # flat in BOTH books
    live = ~flat
    assert not np.any(A[~mask]) and not np.any(S_[~mask])                 # only common names are held
    assert np.array_equal(A[live] != 0, mask[live]) and np.array_equal(S_[live] != 0, mask[live])
    un_a = _seq(np.where(ok, Wv0, 0.0))
    un_s = _seq(np.where(Ds, Ws, 0.0))
    assert np.allclose(_seq(A)[live], un_a[live], rtol=0, atol=1e-12)    # row nets = the unmasked rows' nets
    assert np.allclose(_seq(S_)[live], un_s[live], rtol=0, atol=1e-12)
    assert np.all(np.abs(A).sum(axis=1) <= np.abs(np.where(ok, Wv0, 0.0)).sum(axis=1) + 1e-12)
    assert np.all(np.abs(S_).sum(axis=1) <= np.abs(np.where(Ds, Ws, 0.0)).sum(axis=1) + 1e-12)
    recentred = int((((ok & ~mask).any(axis=1) | (Ds & ~mask).any(axis=1)) & live).sum())
    return recentred, int(flat.sum())


def test_u1_paired_books_on_a_random_churn_calendar():
    rng = np.random.default_rng(0)
    L_, K = 900, 40
    D_ = np.zeros((L_, K), dtype=bool)
    for b in range(0, L_, 90):                                    # membership changes every 90 rows
        n = int(rng.integers(5, 31)) if b // 90 % 4 == 3 else 30   # some months with fewer than 10 members
        D_[b:b + 90, rng.choice(K, n, replace=False)] = True
    ok = D_ & (rng.uniform(size=D_.shape) < 0.97)                 # a few bars missing at the execution row
    x = np.where(D_, rng.standard_normal(D_.shape), 0.0)
    k_ = D_.sum(axis=1, keepdims=True)
    W = np.where(D_, x - x.sum(axis=1, keepdims=True) / np.where(k_ > 0, k_, 1), 0.0) + 0.01 * D_
    tot_rc, tot_flat = 0, 0
    for k in (24, 91, 300, 451, 777):
        rc, fl = check_books(W, D_, ok, k)
        tot_rc += rc
        tot_flat += fl
    assert tot_rc > 0 and tot_flat > 0                            # both rules were exercised


def _momentum():
    return L.parse_file(PROGRAMS / "ucal_xs_momentum.omr")


def _old_rule(W, fp, rng, perm_n):
    """The rule before U1 (pass 3): shifted books = np.roll of the VAL weights under the actual mask."""
    vs, ve = fp.pos(C.VAL_START), fp.pos(C.VAL_END)
    Wv0 = W[vs - 1:ve]
    ok = fp.inplay()[vs - 1:ve] & fp.eng_rows("av", vs, ve)

    def vrun(t):
        run = fp.run_targets(np.where(ok, t, 0.0), vs, ve)
        return float("-inf") if run.liquidated else S.sharpe(run.daily_returns().to_numpy())

    actual = vrun(Wv0)
    offs = PL.perm_offsets(ve - vs + 1, rng, perm_n)
    shifted = np.array([vrun(np.roll(Wv0, int(k), axis=0)) for k in offs])
    return actual, shifted, PL.g6_p(actual, shifted)


def test_u1_bit_identical_to_the_present_rule_without_churn():
    ud = synth_udata(n=14, traps=False)
    prog = _momentum()
    fp = UP.Blocked(ud, "top30", fields=UP.program_fields(prog))
    vs, ve = fp.pos(C.VAL_START), fp.pos(C.VAL_END)
    Dv = fp.inplay()[vs - 1:ve]
    assert Dv.all() and (fp.inplay()[vs - 1:ve] & fp.eng_rows("av", vs, ve)).all()    # constant membership
    W, _, _ = fp.unit(prog, L.default_params(prog))
    opts = PL.Opts(perm_n=25, include_g8=False, keep_detail=True)
    res = UP.ugates(W, fp, np.random.default_rng(7), opts, 0.1, prog, {}, [], None, 0)
    actual, shifted, p_old = _old_rule(W, fp, np.random.default_rng(7), 25)
    per = res["detail"]["permutation"]
    assert res["gates"]["G6"]["value"] == p_old
    assert per["actual_val_sharpe_restarted"] == actual and per["actual_common_mean"] == actual
    assert per["shifted_mean"] == float(np.mean(shifted[np.isfinite(shifted)]))
    assert per["ties"] == 0                                                 # R-B: no tie, and no shifted
    assert not np.any((shifted < actual) & (shifted >= actual - C.G6_PAIRED_SHARPE_MARGIN))   # Sharpe in the band


def test_u1_ties_and_the_margin_only_raise_p():
    a = np.array([1.0, 1.0, 1.0, float("-inf"), 0.5])
    s = np.array([1.0 - 5e-10, 1.0 - 2e-9, 0.2, float("-inf"), 0.1])
    assert UP.g6_paired_p(a, s) == (1 + 2) / 6                              # within the margin; both liquidated
    assert UP.g6_paired_p(a, s, ties=[False, False, False, False, True]) == (1 + 3) / 6
    A = np.array([[0.1, -0.1], [0.0, 0.0]])
    assert UP.g6_books_tie(A, A + 1e-13) and not UP.g6_books_tie(A, A + 1e-11)


@pytest.fixture(scope="module")
def churn():
    tables, table = UC.synthetic_churn_universe(seed=3, n_sym=56, early=30)
    btc = D.assemble_frame(synth_raw(start="2019-08-01 00:00", end=C.VAL_END, seed=99), D.PROGRAM_EXTRA)
    ud = UP.udata_from_tables(tables, btc, C.VAL_END, symbols_table=table)
    prog = _momentum()
    fp = UP.Blocked(ud, "top30", fields=UP.program_fields(prog))
    W, _, _ = fp.unit(prog, L.default_params(prog))
    return fp, W


def test_u1_churn_panel_books_hold_the_same_names_with_the_actual_nets(churn):
    fp, W = churn
    vs, ve = fp.pos(C.VAL_START), fp.pos(C.VAL_END)
    D_ = fp.inplay()[vs - 1:ve]
    ok = D_ & fp.eng_rows("av", vs, ve)
    assert (D_[1:] != D_[:-1]).any(axis=1).sum() >= 10                     # membership churns in VAL
    Wv0 = W[vs - 1:ve]
    offs = PL.perm_offsets(ve - vs + 1, np.random.default_rng(7), 6)
    rc = sum(check_books(Wv0, D_, ok, int(k))[0] for k in offs)
    assert rc > 0


def test_u1_masking_by_spying_no_weight_out_of_play_or_without_a_bar(churn, monkeypatch):
    fp, W = churn
    seen = []
    real = UP.Blocked.run_targets

    def spy(self, tgt, s, e, **kw):
        seen.append((s, e, np.asarray(tgt)))
        return real(self, tgt, s, e, **kw)
    monkeypatch.setattr(UP.Blocked, "run_targets", spy)
    res = UP.ugates(W, fp, np.random.default_rng(1), PL.Opts(perm_n=6, include_g8=False, keep_detail=True), 0.1,
                    None, {}, [], None, 0)
    vs, ve = fp.pos(C.VAL_START), fp.pos(C.VAL_END)
    ok = fp.inplay()[vs - 1:ve] & fp.eng_rows("av", vs, ve)
    g6 = [t for s, e, t in seen if (s, e) == (vs, ve)]
    assert len(g6) >= 1 + 6                                       # the actual, then A_k (unless reused) and S_k
    assert all(not np.any(t[~ok]) for t in g6)
    per = res["detail"]["permutation"]
    assert set(per) >= {"actual_val_sharpe_restarted", "actual_common_mean", "shifted_mean", "p", "n"}


def _basket(fp):
    inplay = fp.inplay()
    k = inplay.sum(axis=1, keepdims=True)
    Wb = np.where(inplay, 1.0 / np.where(k > 0, k, 1), 0.0)
    vs, ve = fp.pos(C.VAL_START), fp.pos(C.VAL_END)
    D_ = inplay[vs - 1:ve]
    ok = D_ & fp.eng_rows("av", vs, ve)
    return Wb, vs, ve, D_, ok


def test_u1_the_basket_counterexample_to_r_b(churn):
    """STOP case reported to the coordinator (not a rule): on rows where a member is in play at the decision row
    but has no bar at the execution row (a delisting; 27 rows of this VAL), A_k's own set (tradable now) loses
    that name's weight (net 29/30) while S_k's own set (in play at the source row) keeps the full net (1), so the
    paired books of an equal-weight basket differ by about 1/30 per row there: no tie, and Sharpe(S_k) - Sharpe(A_k)
    is about +-1e-3, so p is not 1. On the same calendar with every in-play name tradable at its execution row,
    every shift is a tie."""
    fp, _ = churn
    Wb, vs, ve, D_, ok = _basket(fp)
    assert (D_ & ~ok).any(axis=1).sum() > 0
    offs = PL.perm_offsets(ve - vs + 1, np.random.default_rng(5), 20)
    assert not any(UP.g6_books_tie(*UP.g6_books(Wb[vs - 1:ve], D_, ok, int(k))) for k in offs)
    full_bars = D_                                                     # every in-play name tradable at execution
    assert all(UP.g6_books_tie(*UP.g6_books(Wb[vs - 1:ve], D_, full_bars, int(k))) for k in offs)


@pytest.mark.xfail(strict=True, reason="R-B counterexample (test_u1_the_basket_counterexample_to_r_b): awaiting a "
                                       "ruling on A_k's own set; flips to a strict XPASS failure once p = 1")
def test_u1_an_injected_equal_weight_basket_gives_p_one(churn):
    fp, _ = churn
    Wb, vs, ve, D_, ok = _basket(fp)
    assert (D_.sum(axis=1)[1:] != D_.sum(axis=1)[:-1]).any()               # the in-play count varies
    res = UP.ugates(Wb, fp, np.random.default_rng(5), PL.Opts(perm_n=20, include_g8=False, keep_detail=True), 0.1,
                    None, {}, [], None, 0)
    assert res["gates"]["G6"]["value"] == 1.0                               # deterministic (R-B)
