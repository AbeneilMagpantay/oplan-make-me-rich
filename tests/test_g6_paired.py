"""R-C (fix pass 5): G6 in universe units is a causal PAIRED LAG test. For lag k the program's own weights k
hours earlier (rows before VAL start included) are compared with its actual weights on the names tradable now
and in play at the source row; both books are re-centred symmetrically to the nets of the rows they came from
(upipeline.g6_lags / g6_books / ugates). Synthetic data only."""
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


def _calendar(seed=0, T=3000, K=40, missing=0.03):
    """A whole-grid churn calendar: in-play sets change every 90 rows (some with fewer than 10 names), a few
    bars missing at execution rows, weights demeaned with a small net."""
    rng = np.random.default_rng(seed)
    P_ = np.zeros((T, K), dtype=bool)
    for b in range(0, T, 90):
        n = int(rng.integers(5, 31)) if b // 90 % 4 == 3 else 30
        P_[b:b + 90, rng.choice(K, n, replace=False)] = True
    av = rng.uniform(size=P_.shape) > missing
    x = np.where(P_, rng.standard_normal(P_.shape), 0.0)
    k_ = P_.sum(axis=1, keepdims=True)
    W = np.where(P_, x - x.sum(axis=1, keepdims=True) / np.where(k_ > 0, k_, 1), 0.0) + 0.01 * P_
    return W, P_, av


def check_books(W, P_, ok, g0, k):
    """Every property R-C asks of the paired books of lag k (T1); returns (rows re-centred, flat rows)."""
    A, S_ = UP.g6_books(W, P_, ok, g0, k)
    L_ = len(ok)
    Wa, Da = W[g0:g0 + L_], P_[g0:g0 + L_]
    Ws, Ds = W[g0 - k:g0 - k + L_], P_[g0 - k:g0 - k + L_]
    mask = ok & Ds
    flat = mask.sum(axis=1) < C.UNIVERSE_MIN_CS
    live = ~flat
    assert not A[flat].any() and not S_[flat].any()                       # flat in BOTH books
    assert not np.any(A[~mask]) and not np.any(S_[~mask])                 # only common names are held
    assert np.array_equal(A[live] != 0, mask[live]) and np.array_equal(S_[live] != 0, mask[live])
    own_a, own_s = np.where(Da, Wa, 0.0), np.where(Ds, Ws, 0.0)
    assert np.allclose(_seq(A)[live], _seq(own_a)[live], rtol=0, atol=1e-12)    # nets = the own rows' nets
    assert np.allclose(_seq(S_)[live], _seq(own_s)[live], rtol=0, atol=1e-12)
    assert np.all(np.abs(A).sum(axis=1) <= np.abs(own_a).sum(axis=1) + 1e-12)   # gross never above the own row
    assert np.all(np.abs(S_).sum(axis=1) <= np.abs(own_s).sum(axis=1) + 1e-12)
    recentred = int((((Da & ~mask).any(axis=1) | (Ds & ~mask).any(axis=1)) & live).sum())
    return recentred, int(flat.sum())


def test_r_c_t1_paired_books_on_a_random_churn_calendar():
    W, P_, av = _calendar()
    g0, L_ = 1500, 1200
    ok = P_[g0:g0 + L_] & av[g0 + 1:g0 + 1 + L_]
    tot_rc, tot_flat = 0, 0
    for k in (24, 91, 300, 451, 777, 1500):
        rc, fl = check_books(W, P_, ok, g0, k)
        tot_rc += rc
        tot_flat += fl
    assert tot_rc > 0 and tot_flat > 0                                    # both rules were exercised


def _circular_books(W, P_, ok, g0, k):
    """The pass-4 circular form (U1), kept here only as the negative control of T2."""
    L_ = len(ok)
    Wv0, D_ = W[g0:g0 + L_], P_[g0:g0 + L_]
    src = (np.arange(L_) - k) % L_
    Ws, Ds = Wv0[src], D_[src]
    mask = ok & Ds
    nm = mask.sum(axis=1)
    out = []
    for w, own in ((Wv0, ok), (Ws, Ds)):
        b = np.where(mask, w, 0.0)
        rc = np.nonzero((own & ~mask).any(axis=1) & (nm > 0))[0]
        if len(rc):
            b[rc] = np.where(mask[rc], b[rc] + ((_seq(np.where(own[rc], w[rc], 0.0)) - _seq(b[rc])) / nm[rc])[:, None],
                             0.0)
        b[nm < C.UNIVERSE_MIN_CS] = 0.0
        out.append(b)
    return out


@pytest.mark.parametrize("books", ["lag", "circular"])
def test_r_c_t2_causality(books):
    """Two inputs identical up to grid row r and different after it (membership, in-play flags, weights, bars):
    for every lag the books are identical on every VAL row executed at or before r. The pass-4 circular form
    fails the same check (negative control)."""
    W1, P1, av1 = _calendar(seed=1)
    W2, P2, av2 = W1.copy(), P1.copy(), av1.copy()
    r = 2100
    rng = np.random.default_rng(9)
    P2[r + 1:] = rng.uniform(size=P2[r + 1:].shape) < 0.6                 # another membership after r
    W2[r + 1:] = np.where(P2[r + 1:], rng.standard_normal(P2[r + 1:].shape) * 0.05, 0.0)
    av2[r + 1:] = rng.uniform(size=av2[r + 1:].shape) > 0.2
    g0, L_ = 1500, 1200
    fn = UP.g6_books if books == "lag" else _circular_books
    upto = r - (g0 + 1)                                                   # VAL rows executed at or before r
    leaks = 0
    for k in (24, 300, 600, 777, 1100):
        ok1 = P1[g0:g0 + L_] & av1[g0 + 1:g0 + 1 + L_]
        ok2 = P2[g0:g0 + L_] & av2[g0 + 1:g0 + 1 + L_]
        A1, S1 = fn(W1, P1, ok1, g0, k)
        A2, S2 = fn(W2, P2, ok2, g0, k)
        same = np.array_equal(A1[:upto + 1], A2[:upto + 1]) and np.array_equal(S1[:upto + 1], S2[:upto + 1])
        leaks += not same
    if books == "lag":
        assert leaks == 0
    else:
        assert leaks > 0                                                  # the circular form uses later rows


def _momentum():
    return L.parse_file(PROGRAMS / "ucal_xs_momentum.omr")


def test_r_c_t3_no_churn_every_bar_present_is_a_plain_lag_test(monkeypatch):
    ud = synth_udata(n=14, traps=False)
    prog = _momentum()
    fp = UP.Blocked(ud, "top30", fields=UP.program_fields(prog))
    vs, ve = fp.pos(C.VAL_START), fp.pos(C.VAL_END)
    g0, L_ = vs - 1, ve - vs + 1
    P_ = fp.inplay()
    assert P_[g0 - L_ // 2:ve].all() and fp.eng_rows("av", vs, ve).all()   # constant membership, every bar
    W, _, _ = fp.unit(prog, L.default_params(prog))
    N = 12
    seen = []
    real = UP.Blocked.run_targets

    def spy(self, tgt, s, e, **kw):
        seen.append((s, e))
        return real(self, tgt, s, e, **kw)
    monkeypatch.setattr(UP.Blocked, "run_targets", spy)
    res = UP.ugates(W, fp, np.random.default_rng(7), PL.Opts(perm_n=N, include_g8=False, keep_detail=True), 0.1,
                    prog, {}, [], None, 0)
    assert sum(1 for x in seen if x == (vs, ve)) == 1 + N                 # A_k = the plain actual for every lag
    monkeypatch.setattr(UP.Blocked, "run_targets", real)
    ok = P_[g0:ve] & fp.eng_rows("av", vs, ve)

    def vrun(t):
        run = fp.run_targets(np.where(ok, t, 0.0), vs, ve)
        return float("-inf") if run.liquidated else S.sharpe(run.daily_returns().to_numpy())
    actual = vrun(W[g0:ve])
    lags = UP.g6_lags(L_, g0, np.random.default_rng(7), N)
    for k in lags[:3]:
        A, S_ = UP.g6_books(W, P_, ok, g0, int(k))
        assert np.array_equal(A, np.where(ok, W[g0:ve], 0.0)) and np.array_equal(S_, np.where(ok, W[g0 - k:ve - k], 0.0))
    lagged = np.array([vrun(W[g0 - k:ve - k]) for k in lags])
    p = (1 + int(np.sum(lagged >= actual - C.G6_PAIRED_SHARPE_MARGIN))) / (N + 1)
    per = res["detail"]["permutation"]
    assert res["gates"]["G6"]["value"] == p and per["actual_val_sharpe_restarted"] == actual
    assert per["lagged"] is True and per["lag_min"] == int(lags.min()) and per["lag_max"] == int(lags.max())
    assert per["ties"] == 0 and not np.any((lagged < actual) & (lagged >= actual - C.G6_PAIRED_SHARPE_MARGIN))


@pytest.fixture(scope="module")
def churn():
    tables, table = UC.synthetic_churn_universe(seed=3, n_sym=56, early=30)
    btc = D.assemble_frame(synth_raw(start="2019-08-01 00:00", end=C.VAL_END, seed=99), D.PROGRAM_EXTRA)
    ud = UP.udata_from_tables(tables, btc, C.VAL_END, symbols_table=table)
    prog = _momentum()
    fp = UP.Blocked(ud, "top30", fields=UP.program_fields(prog))
    W, _, _ = fp.unit(prog, L.default_params(prog))
    return ud, fp, W


def test_r_c_churn_panel_books_hold_the_same_names_with_their_own_nets(churn):
    _, fp, W = churn
    vs, ve = fp.pos(C.VAL_START), fp.pos(C.VAL_END)
    P_ = fp.inplay()
    ok = P_[vs - 1:ve] & fp.eng_rows("av", vs, ve)
    assert (P_[vs:ve] != P_[vs - 1:ve - 1]).any(axis=1).sum() >= 10        # membership churns in VAL
    lags = UP.g6_lags(ve - vs + 1, vs - 1, np.random.default_rng(7), 6)
    assert sum(check_books(W, P_, ok, vs - 1, int(k))[0] for k in lags) > 0


def test_r_c_t4_the_equal_weight_basket_gets_p_one(churn):
    _, fp, _ = churn
    P_ = fp.inplay()
    k = P_.sum(axis=1, keepdims=True)
    Wb = np.where(P_, 1.0 / np.where(k > 0, k, 1), 0.0)
    vs, ve = fp.pos(C.VAL_START), fp.pos(C.VAL_END)
    assert (P_[vs - 1:ve] & ~fp.eng_rows("av", vs, ve)).any()              # rows where a member has no bar
    res = UP.ugates(Wb, fp, np.random.default_rng(5), PL.Opts(perm_n=20, include_g8=False, keep_detail=True), 0.1,
                    None, {}, [], None, 0)
    assert res["gates"]["G6"]["value"] == 1.0


def test_r_c_t5_masking_by_spying_no_weight_out_of_play_or_without_a_bar(churn, monkeypatch):
    _, fp, W = churn
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
    assert len(g6) >= 1 + 6
    assert all(not np.any(t[~ok]) for t in g6)
    per = res["detail"]["permutation"]
    assert set(per) >= {"actual_val_sharpe_restarted", "actual_common_mean", "shifted_mean", "p", "n", "lagged",
                        "lag_min", "lag_max", "ties"}


def test_r_c_t6_lags_inside_the_range_and_enough_history():
    L_ = 26304
    lags = UP.g6_lags(L_, 30000, np.random.default_rng(3), 500)
    assert lags.min() >= C.PERM_MIN_OFFSET_DAYS * 24 == 720 and lags.max() <= L_ // 2
    with pytest.raises(PL.KernelFault):
        UP.g6_lags(L_, L_ // 2 - 1, np.random.default_rng(3), 5)          # not enough history before VAL
    with pytest.raises(PL.KernelFault):
        UP.g6_lags(1000, 30000, np.random.default_rng(3), 5)              # VAL shorter than 2 x 30 days


def test_r_c_t7_planted_foresight_gets_the_smallest_p(churn):
    ud, _, _ = churn
    ob = UC.UOracle(ud, 1, 42)
    N = 10
    res = UP.ugates(ob.weights(0.9), ob.bu, np.random.default_rng(2), PL.Opts(perm_n=N, include_g8=False), 0.1,
                    None, {}, [], None, 0)
    assert res["gates"]["G6"]["value"] == 1.0 / (N + 1)


def test_ties_and_the_margin_only_raise_p():
    a = np.array([1.0, 1.0, 1.0, float("-inf"), 0.5])
    s = np.array([1.0 - 5e-10, 1.0 - 2e-9, 0.2, float("-inf"), 0.1])
    assert UP.g6_paired_p(a, s) == (1 + 2) / 6                              # within the margin; both liquidated
    assert UP.g6_paired_p(a, s, ties=[False, False, False, False, True]) == (1 + 3) / 6
    A = np.array([[0.1, -0.1], [0.0, 0.0]])
    assert UP.g6_books_tie(A, A + 1e-13) and not UP.g6_books_tie(A, A + 1e-11)
