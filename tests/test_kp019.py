"""KP-019: tf_last(x, tf) and tf_mean(x, tf) - parse and type rules, canonical form, lookback, values against a
pure-Python reference, visibility, locality (random programs: end cuts, start cuts, rescale, week shift,
determinism, the lookback bound), unit top30 (blocks, self-checks, block_overlap, entrants against a cs_* inside
or outside), the constant probe cases of the design, G5, and an end-to-end evaluation. Synthetic data only."""
import numpy as np
import pandas as pd
import pytest

from conftest import SynthProvider, prog_text, synth_raw, synth_universe, synth_world
from omr import constants as C
from omr import datasets as D
from omr import interp as X
from omr import lang as L
from omr import pipeline as PL
from omr import probe
from omr import upipeline as UP
from omr import windows as WN

TFS = ("h2", "h3", "h4", "h6", "h8", "h12", "daily", "weekly")


def parse(body, kind="portfolio", probe_=True, unit=None):
    text = prog_text(body, kind=kind)
    if unit:
        text = text.replace("hypothesis", f'unit = "{unit}"\nhypothesis', 1)
    return L.parse(text, "x_test", probe=probe_)


def frames(start="2021-01-04 00:00", end="2021-04-30 23:00", seeds=(1, 2, 3)):
    out = [D.assemble_frame(synth_raw(start=start, end=end, seed=s), D.PROGRAM_EXTRA) for s in seeds]
    return out[:-1], out[-1]


FR, BTC = frames()


# ---------------------------------------------------------------- T1 parse and type rules

@pytest.mark.parametrize("body,rule", [
    ("signal = tf_mean(ret(close, 1), 24)\n", "timeframe_name"),
    ("signal = tf_mean(ret(close, 1), h1)\n", "timeframe_name"),
    ("n = param(24, 12, 36)\nsignal = tf_mean(ret(close, 1), n)\n", "timeframe_name"),
    ("signal = tf_mean(ret(close, 1), close)\n", "timeframe_name"),
    ("signal = tf_last(ret(close, 1), btc)\n", "timeframe_name"),
    ("x = ret(close, 1)\nsignal = tf_mean(x, x)\n", "timeframe_name"),
    ("signal = tf_last(ret(close, 1), daily(close))\n", "timeframe_name"),
    ("signal = tf_last(close, daily) / close\n", "unit"),
    ("signal = tf_mean(quote_volume, daily) / quote_volume\n", "unit"),
    ("signal = where(tf_last(close > open, daily), 1, -1)\n", "type"),
    ("n = param(2, 1, 3)\nsignal = tf_last(n, daily) * ret(close, 1)\n", "type"),
    ("signal = tf_mean(ret(daily(close), 1), weekly)\n", "timeframe_input"),
    ("signal = tf_mean(ret(h4(close), 1), daily)\n", "timeframe_input"),
    ("signal = tf_mean(ret(close, 1))\n", "arity"),
    ("signal = tf_mean(ret(close, 1), daily, daily)\n", "arity"),
    ("tf_mean = ret(close, 1)\nsignal = tf_mean\n", "shadowing"),
    ("signal = tf_last\n", "bare_function"),
])
def test_t1_rejected_forms(body, rule):
    with pytest.raises(L.LangError) as e:
        parse(body)
    assert e.value.rule == rule, (body, e.value.rule, e.value.msg)


@pytest.mark.parametrize("body,tf,lookback", [
    ("signal = tf_mean(ret(close, 1), daily)\n", "daily", 46 + 2),
    ("signal = tf_last(ret(close, 1), weekly)\n", "weekly", 334 + 2),
    ("signal = tf_mean(funding8h, daily)\n", "daily", 46 + 17),
    ("signal = tf_mean((close - index_close) / index_close, daily)\n", "daily", 46 + 7),
    ("signal = tf_mean(ret(btc(close), 1), h4)\n", "h4", 6 + 2),
    ("signal = tf_last(tf_mean(ret(close, 1), h4), daily)\n", "daily", 46 + 6 + 2),
    ("n = param(5, 3, 8)\nsignal = tf_last(sma(ret(daily(close), 1), n), weekly)\n", "weekly", 334 + 47 + 24 + 7 * 24),
    ("n = param(5, 3, 8)\nsignal = sma(tf_mean(ret(close, 1), daily), n)\n", "daily", 48 + 7 * 24),
    ("signal = tf_last(ret(close, 1), h2) - ret(close, 1)\n", "h1", 2 + 2),
])
def test_t1_t3_accepted_forms_type_and_lookback(body, tf, lookback):
    p = parse(body)
    assert p.types["signal"].unit == () and p.types["signal"].tf == tf
    assert p.lookback_hours == lookback, (body, p.lookback_hours)


def test_t1_node_count_counts_the_call_and_the_timeframe_name():
    assert parse("signal = tf_mean(ret(close, 1), daily)\n").node_count == \
        parse("signal = ret(close, 1)\n").node_count + 2


def test_t3_the_top30_lookback_limit_applies():
    ok = "n = param(9, 7, 11)\nsignal = cs_rank(sma(tf_last(ret(close, 1), weekly), n))\n"
    assert parse(ok, unit="top30").lookback_hours == 334 + 2 + 10 * 168 <= C.LOOKBACK_MAX_HOURS
    with pytest.raises(L.LangError) as e:
        parse("n = param(10, 8, 12)\nsignal = cs_rank(sma(tf_last(ret(close, 1), weekly), n))\n", unit="top30")
    assert e.value.rule == "lookback_exceeds_seasoning"


def test_t3_window_limit_counts_the_timeframe_hours():
    with pytest.raises(L.LangError) as e:                                    # 60 weekly rows > 400 days
        parse("n = param(50, 40, 60)\nsignal = sma(tf_last(ret(close, 1), weekly), n)\n")
    assert e.value.rule == "window_limit"


# ---------------------------------------------------------------- T2 canonical form

def test_t2_canonical_form():
    a = parse("x = ret(close, 1)\nsignal = cs_rank(tf_mean(x, weekly))\n")
    b = L.parse(prog_text("# a comment\nmy_r = ret(close, 1)\nsignal = cs_rank(tf_mean(my_r,   weekly))\n",
                          kind="portfolio"), "x_test")
    assert a.canonical == b.canonical == "kind=portfolio;signal=cs_rank(tf_mean(ret(close,1),weekly));params=[]"
    assert parse("signal = cs_rank(tf_last(ret(close, 1), weekly))\n").canonical != a.canonical


# ---------------------------------------------------------------- T4 values against a pure-Python reference

def _bins(idx, tf):
    t = idx.asi8
    h = L.TIMEFRAMES[tf] * X.HOUR_NS
    key = t - ((t - X.MONDAY_NS) % X.WEEK_NS) if tf == "weekly" else t - (t % h)
    return key


def reference(x, xk, idx, tf, how):
    """Hourly view of tf_last / tf_mean by plain loops: complete bins, every hour known, visible from the last."""
    hrs = L.TIMEFRAMES[tf]
    key = _bins(idx, tf)
    n, k = x.shape
    val, kn = np.full((n, k), np.nan), np.zeros((n, k), dtype=bool)
    cur_v, cur_k = None, None
    i = 0
    while i < n:
        j = i
        while j < n and key[j] == key[i]:
            j += 1
        if j - i == hrs:
            v = np.empty(k)
            kk = np.empty(k, dtype=bool)
            for c in range(k):
                kk[c] = all(xk[r, c] for r in range(i, j))
                if how == "last":
                    v[c] = x[j - 1, c]
                else:
                    s = 0.0
                    for r in range(i, j):
                        s += x[r, c]
                    v[c] = s / hrs
            cur_v, cur_k = np.where(kk, v, np.nan), kk
        if cur_v is not None and j - i == hrs:
            val[j - 1:], kn[j - 1:] = cur_v, cur_k
        i = j
    return np.where(np.isfinite(val), val, np.nan), kn


@pytest.mark.parametrize("tf", TFS)
@pytest.mark.parametrize("how", ("last", "mean"))
def test_t4_values_and_knownness_equal_the_reference(tf, how):
    fr = [f.copy() for f in FR]
    for f in fr:                                       # an unknown stretch (mark bars more than 6 hours stale)
        m = (f.index >= pd.Timestamp("2021-02-10 03:00", tz="UTC")) & (f.index < pd.Timestamp("2021-02-10 15:00", tz="UTC"))
        f.loc[m, "mark_klines.new"] = False
    body = f"signal = tf_{how}((close - mark_close) / close, {tf})\n"
    p = parse(body, probe_=False)
    raw, kn = X.evaluate_full(p, {}, fr, BTC)
    ctx = X.Context(p, {}, fr, BTC)
    c, m = ctx.field("close"), ctx.field("mark_close")
    x = (c.arr - m.arr) / c.arr
    ref, rk = reference(x, c.kn & m.kn, ctx.idx, tf, how)
    assert np.array_equal(kn, rk) and kn.any() and (~kn[200:]).any()
    assert np.array_equal(raw, ref, equal_nan=True)


@pytest.mark.parametrize("tf", ("h4", "daily", "weekly"))
def test_t4_tf_mean_is_sma_at_the_bins_last_hour_bit_for_bit(tf):
    hrs = L.TIMEFRAMES[tf]
    a = parse(f"signal = tf_mean(ret(close, 1), {tf})\n", probe_=False)
    lo, hi = int(np.floor(0.8 * hrs)), int(np.ceil(1.2 * hrs)) + 1
    b = parse(f"n = param({hrs}, {lo}, {hi})\nsignal = tf_last(sma(ret(close, 1), n), {tf})\n", probe_=False)
    ra, ka = X.evaluate_full(a, {}, FR, BTC)
    rb, kb = X.evaluate_full(b, L.default_params(b), FR, BTC)
    both = ka & kb
    assert both.sum() > 100 and np.array_equal(ra[both].view(np.int64), rb[both].view(np.int64))
    assert (kb <= ka).all()                                         # tf_last(sma) needs one more bin of history


def test_t4_anchoring_known_nan_and_a_coarser_input():
    p = parse("signal = tf_last(weekday, weekly) + tf_last(hour, daily)\n", probe_=False)
    raw, kn = X.evaluate_full(p, {}, FR, BTC)
    assert np.all(raw[kn] == 0.0)                                   # the decision time of a bin's last bar
    first = np.nonzero(kn[:, 0])[0][0]
    t = FR[0].index[first]
    assert t.day_of_week == 6 and t.hour == 23                        # first complete week (from a Monday) closes
    q = parse("signal = tf_mean(log(ret(close, 1)), daily)\n", probe_=False)   # log of a negative return: a known NaN
    rq, kq = X.evaluate_full(q, {}, FR, BTC)
    assert kq.any() and np.isnan(rq[kq]).all()
    r = parse("n = param(3, 2, 4)\nsignal = tf_last(sma(ret(daily(close), 1), n), weekly)\n", probe_=False)
    s = parse("n = param(3, 2, 4)\nsignal = sma(ret(daily(close), 1), n)\n", probe_=False)
    rr, kr = X.evaluate_full(r, {"n": 3}, FR, BTC)
    rs, ks = X.evaluate_full(s, {"n": 3}, FR, BTC)
    sun = (FR[0].index.day_of_week == 6) & (FR[0].index.hour == 23)
    assert kr[sun].any() and np.array_equal(rr[sun & kr[:, 0]], rs[sun & kr[:, 0]], equal_nan=True)


# ---------------------------------------------------------------- T5 visibility and the future

@pytest.mark.parametrize("tf", ("h4", "daily", "weekly"))
def test_t5_a_bin_is_visible_from_its_last_bar_and_never_earlier(tf):
    p = parse(f"signal = tf_mean(ret(close, 1), {tf})\n", probe_=False)
    raw, kn = X.evaluate_full(p, {}, FR, BTC)
    key = _bins(FR[0].index, tf)
    hrs = L.TIMEFRAMES[tf]
    ends = np.nonzero((key[1:] != key[:-1]))[0]                    # last rows of bins
    j = int(ends[len(ends) // 2])
    fr = [f.copy() for f in FR]
    fr[0].iloc[j, fr[0].columns.get_loc("close")] *= 1.05           # perturb the bin's last bar
    r2, k2 = X.evaluate_full(p, {}, fr, BTC)
    assert np.array_equal(raw[:j], r2[:j], equal_nan=True) and np.array_equal(kn, k2)
    assert not np.array_equal(raw[j:j + hrs, 0], r2[j:j + hrs, 0], equal_nan=True)


def test_t5_rows_after_t_never_reach_rows_up_to_t():
    p = parse("n = param(3, 2, 4)\nsignal = cs_rank(sma(tf_mean(ret(close, 1), daily), n) - tf_last(ret(close, 1), "
              "weekly))\n", probe_=False)
    raw, kn = X.evaluate_full(p, {"n": 3}, FR, BTC)
    rng = np.random.default_rng(3)
    for c in sorted(rng.choice(np.arange(500, len(FR[0]) - 1), size=4, replace=False)):
        fr = [f.copy() for f in FR]
        for f in fr:
            for col in ("open", "high", "low", "close"):
                f.iloc[c + 1:, f.columns.get_loc(col)] *= 1.5
        r2, k2 = X.evaluate_full(p, {"n": 3}, fr, BTC)
        assert np.array_equal(raw[:c + 1], r2[:c + 1], equal_nan=True) and np.array_equal(kn[:c + 1], k2[:c + 1])


# ---------------------------------------------------------------- T6 / T7 random programs

class Gen:
    def __init__(self, rng, kind):
        self.r, self.kind, self.used = rng, kind, set()

    def pick(self, xs):
        return xs[int(self.r.integers(len(xs)))]

    def w(self):
        if self.r.random() < 0.3:
            return "1"
        n = self.pick(["w1", "w2", "w3"])
        self.used.add(n)
        return n

    def hourly(self):
        opts = [lambda: "ret(close, 1)", lambda: f"logret(close, {self.w()})", lambda: "(close - open) / close",
                lambda: "funding8h", lambda: "(close - mark_close) / close", lambda: "taker_buy_volume / volume",
                lambda: "ret(btc(close), 1)", lambda: "where(close > open, 1, -1)", lambda: f"zscore(close, {self.w()})",
                lambda: "(close - index_close) / index_close"]
        if self.kind == "portfolio":
            opts += [lambda: f"cs_rank(ret(close, {self.w()}))", lambda: "cs_demean(ret(close, 1))"]
        return self.pick(opts)()

    def coarse(self):
        tf = self.pick(["h4", "daily"])
        return self.pick([lambda: f"ret({tf}(close), {self.w()})", lambda: f"zscore({tf}(volume), {self.w()})"])()

    def tfnode(self, d=0):
        tf = self.pick(list(TFS))
        r = self.r.random()
        if r < 0.45:
            return f"tf_mean({self.hourly()}, {tf})"
        if r < 0.75:
            return f"tf_last({self.hourly()}, {tf})"
        if r < 0.9:
            return f"tf_last({self.coarse()}, {self.pick(['daily', 'weekly'])})"
        inner = self.pick(["h2", "h4", "h6"])
        return f"tf_last(tf_mean({self.hourly()}, {inner}), {self.pick(['daily', 'weekly'])})"

    def outer(self):
        t = self.tfnode()
        opts = [lambda: t, lambda: f"sma({t}, {self.w()})", lambda: f"lag({t}, {self.w()})",
                lambda: f"({t} - {self.hourly()})", lambda: f"where({t} > 0, {self.hourly()}, {t})",
                lambda: f"tanh({t} * {self.par('k1')})",
                lambda: f"hold({t} > 0, {t} < 0, {t} < 0, {t} > 0, {self.par('hz')})",
                lambda: f"rank({t}, {self.w()})"]
        if self.kind == "portfolio":
            opts += [lambda: f"cs_rank({t})", lambda: f"cs_scale(cs_demean({t}))"]
        return self.pick(opts)()

    def par(self, n):
        self.used.add(n)
        return n

    def program(self):
        sig = self.outer() if self.r.random() < 0.6 else f"clip({self.outer()} + {self.outer()}, -1, 1)"
        params = {"w1": "param(2, 1, 3)", "w2": "param(3, 2, 4)", "w3": "param(4, 3, 5)", "k1": "param(0.5, 0.25, 1.0)",
                  "hz": "param(6, 4, 9)"}
        decl = "".join(f"{n} = {params[n]}\n" for n in sorted(self.used))
        return (f'name = "x_kp19"\nfamily = "other"\nkind = "{self.kind}"\n'
                f'hypothesis = "random tf program for the KP-019 property tests"\n{decl}signal = {sig}\n')


def generate(n_target=60, seed=20261125):
    rng = np.random.default_rng(seed)
    out, tried, reasons = [], 0, {}
    while len(out) < n_target and tried < 30 * n_target:
        tried += 1
        text = Gen(rng, "portfolio" if rng.random() < 0.5 else "single").program()
        try:
            out.append(L.parse(text, "x_kp19"))
        except L.LangError as e:
            reasons[e.rule] = reasons.get(e.rule, 0) + 1
    return out, reasons


PROGS, REASONS = generate()


def run(prog, fr, btc):
    if prog.kind == "single":
        fr = fr[:1]
    return X.evaluate_full(prog, L.default_params(prog), fr, btc)


def test_t6_the_generator_covers_both_functions_every_timeframe_and_nesting():
    assert len(PROGS) >= 55, REASONS
    can = " ".join(p.canonical for p in PROGS)
    for tf in TFS:
        assert f",{tf})" in can, tf
    assert "tf_last(tf_mean(" in can and "cs_rank(tf_" in can and "hold(" in can
    assert sum(int(run(p, FR, BTC)[1].sum() > 0) for p in PROGS) >= 0.8 * len(PROGS)


@pytest.mark.parametrize("i", range(60))
def test_t6_t7_program_properties(i):
    if i >= len(PROGS):
        pytest.skip("generator produced fewer programs")
    prog = PROGS[i]
    rng = np.random.default_rng(100 + i)
    raw, kn = run(prog, FR, BTC)
    n = len(FR[0])
    assert np.isnan(raw[~kn]).all()
    r2, k2 = run(prog, FR, BTC)
    assert np.array_equal(raw, r2, equal_nan=True) and np.array_equal(kn, k2)                   # determinism
    for c in sorted(rng.choice(np.arange(24, n - 1), size=3, replace=False)):                  # end cuts
        cut = FR[0].index[c]
        rc, kc = run(prog, [f.loc[:cut] for f in FR], BTC.loc[:cut])
        assert np.array_equal(rc, raw[:c + 1], equal_nan=True) and np.array_equal(kc, kn[:c + 1]), prog.canonical
    Lh = prog.lookback_hours
    for c in sorted(rng.choice(np.arange(1, int(0.5 * n)), size=3, replace=False)):           # start cuts
        cut = FR[0].index[c]
        rc, kc = run(prog, [f.loc[cut:] for f in FR], BTC.loc[cut:])
        assert kn[c:][kc].all(), prog.canonical
        assert np.array_equal(rc[kc], raw[c:][kc], equal_nan=True), prog.canonical
        a = Lh - 1                                                                              # T7: the lookback bound
        assert np.array_equal(kc[a:], kn[c + a:]) and np.array_equal(rc[a:], raw[c + a:], equal_nan=True), \
            (prog.canonical, Lh)
    sc = []                                                                                     # power-of-two rescale
    for f in FR + [BTC]:
        g = f.copy()
        p, v, q = (float(2.0 ** int(rng.integers(-5, 6))) for _ in range(3))
        cols = ["open", "high", "low", "close", "mark_klines.open", "mark_klines.high", "mark_klines.low",
                "mark_klines.close", "index_klines.open", "index_klines.high", "index_klines.low", "index_klines.close"]
        g[cols] = g[cols] * p
        g[["volume", "taker_buy_volume"]] = g[["volume", "taker_buy_volume"]] * v
        g[["quote_volume", "taker_buy_quote_volume"]] = g[["quote_volume", "taker_buy_quote_volume"]] * (p * v)
        g[["trades"]] = g[["trades"]] * q
        sc.append(g)
    rs, ks = run(prog, sc[:-1], sc[-1])
    assert np.array_equal(rs, raw, equal_nan=True) and np.array_equal(ks, kn), prog.canonical
    k = int(rng.integers(1, 30)) * (1 if rng.random() < 0.5 else -1)                           # whole-week shift
    sh = [f.copy() for f in FR + [BTC]]
    for f in sh:
        f.index = f.index + pd.Timedelta(weeks=k)
    rw, kw = run(prog, sh[:-1], sh[-1])
    assert np.array_equal(rw, raw, equal_nan=True) and np.array_equal(kw, kn), prog.canonical


# ---------------------------------------------------------------- T8 unit top30

@pytest.fixture(scope="module")
def uni():
    return synth_universe(seed=5, n=40)


@pytest.fixture(scope="module")
def ud_dev(uni):
    tables, table, btc = uni
    return UP.udata_from_tables(tables, btc, C.DEV_END, symbols_table=table)


TOP30 = {
    "weekly_inside": "signal = cs_scale(cs_demean(tf_last(cs_rank(ret(close, 1)), weekly)))\n",
    "weekly_outside": "n = param(3, 2, 4)\nsignal = cs_scale(cs_demean(cs_rank(sma(tf_mean(ret(close, 1), weekly), n))))\n",
    "daily_nested": "signal = cs_scale(cs_demean(tf_last(tf_mean(cs_demean(ret(close, 1)), h6), daily) + "
                    "tf_mean(funding8h, daily)))\n",
}


@pytest.mark.parametrize("name", sorted(TOP30))
def test_t8_blocks_equal_the_whole_panel_and_stage1_passes(ud_dev, name):
    prog = parse(TOP30[name], unit="top30", probe_=False)
    q = L.default_params(prog)
    f = UP.program_fields(prog)
    whole = UP.Blocked(ud_dev, "top30", months=None, fields=f).unit(prog, q)
    half = UP.Blocked(ud_dev, "top30", fields=f).unit(prog, q)                  # raises on a block_overlap
    assert whole[2].any()
    for a, b in zip(whole, half):
        assert np.array_equal(a, b, equal_nan=True)
    assert all(np.array_equal(a, b, equal_nan=True) for a, b in zip(UP.unit_full_u(prog, q, UP.FullPanel(ud_dev, "top30")),
                                                                     whole))
    s1 = UP.stage1_u(prog, q, ud_dev, np.random.default_rng(4), PL.Opts(truncation_cuts=4, start_cuts=2))
    assert s1.get("fault") is None and s1["block_overlap_cells"] > 0


def test_t8_block_overlap_fires_when_a_tf_lookback_is_understated(ud_dev, monkeypatch):
    real = L.lookback_hours
    monkeypatch.setattr(L, "lookback_hours", lambda prog: max(1, real(prog) - 400))
    prog = parse(TOP30["weekly_outside"], unit="top30", probe_=False)
    with pytest.raises(PL.KernelFault) as e:
        UP.Blocked(ud_dev, "top30", fields=UP.program_fields(prog)).unit(prog, L.default_params(prog))
    assert str(e.value) == "block_overlap"


def test_t8_an_entrant_inside_or_outside_a_cross_section():
    """LANGUAGE.md section 10: with the cs_* inside, a symbol entering mid-week is unknown until it has one complete
    bin in play; with the cs_* outside, its first bin is ranked as soon as one becomes visible while it is in play."""
    pan, btc = probe.universe_panel()
    T = len(pan.index)
    inplay = np.ones((T, len(pan.symbols)), dtype=bool)
    idx = pan.index
    entry = int(np.nonzero((idx.day_of_week == 2) & (idx.hour == 12))[0][20])    # a Wednesday noon, week 21
    inplay[:entry, 0] = False
    p2 = X.Panel(idx, pan.symbols, pan.col, inplay, pan.unit_known)
    inside = parse("signal = tf_last(cs_rank(ret(close, 1)), weekly)\n", unit="top30", probe_=False)
    outside = parse("signal = cs_rank(tf_last(ret(close, 1), weekly))\n", unit="top30", probe_=False)
    _, ki = X.evaluate_full(inside, {}, p2, btc)
    _, ko = X.evaluate_full(outside, {}, p2, btc)
    sun = np.nonzero((idx.day_of_week == 6) & (idx.hour == 23))[0]
    first_sun = int(sun[sun >= entry][0])                                        # the bin of the entry closes
    second_sun = int(sun[sun >= entry][1])                                       # the first bin fully in play closes
    assert not ki[entry:second_sun, 0].any() and ki[second_sun, 0]
    assert not ko[entry:first_sun, 0].any() and ko[first_sun, 0]
    assert ki[entry:, 1].all() and ko[entry:, 1].all()                           # an incumbent is known throughout


# ---------------------------------------------------------------- T9 the constant probe through the real parser

PROBE_CASES = [("tf_mean(hour, daily) * ret(close, 1)", "constant_subexpression"),
               ("tf_mean(hour, weekly) * ret(close, 1)", "constant_subexpression"),
               ("tf_mean(weekday, weekly) * ret(close, 1)", "constant_subexpression"),
               ("tf_mean(hour / hour, daily) * ret(close, 1)", "constant_subexpression"),
               ("ret(close, 1) / tf_last(hour, daily)", "constant_subexpression"),
               ("tf_last(hour, daily) + ret(close, 1)", None), ("tf_last(hour, weekly) + ret(close, 1)", None),
               ("tf_last(weekday, weekly) + ret(close, 1)", None), ("tf_last(weekday, daily) * ret(close, 1)", None),
               ("tf_mean(weekday, daily) * ret(close, 1)", None),
               ("tf_mean(0.5 * hour, daily) * ret(close, 1)", None),
               ("tf_mean(hour + funding8h, daily) * ret(close, 1)", None),
               ("tf_mean(mark_close / close, daily) * ret(close, 1)", None)]
PROBE_CASES += [(f"tf_{h}({c}, {tf}) * ret(close, 1)", None) for tf in TFS[:6] for h in ("last", "mean")
                for c in ("hour", "weekday")]


@pytest.mark.parametrize("body,rule", PROBE_CASES)
def test_t9_probe_cases_of_the_design(body, rule):
    if rule is None:
        parse(f"signal = {body}\n")
    else:
        with pytest.raises(L.LangError) as e:
            parse(f"signal = {body}\n")
        assert e.value.rule == rule


def test_t9_the_probe_records_the_tf_node_and_its_input():
    p = parse("signal = tf_mean(ret(close, 1), daily) * 1\n", probe_=False)
    frames_, btc = probe._probe_frames(p)
    rec = []
    X.evaluate_full(p, {}, frames_, btc, record=rec)
    tfs = [s.tf for node, s in rec]
    assert "daily" in tfs and "h1" in tfs


# ---------------------------------------------------------------- T10 G5

def test_t10_nothing_of_the_function_is_jittered():
    p = parse("k = param(2, 1, 3)\nsignal = tf_mean(ret(close, k) * 2, daily) - tf_last(ret(close, 1), weekly)\n")
    assert p.n_literals == 1 and [v for _, v in p.literals] == [2.0]
    v = PL.jitter_params(p, L.default_params(p), np.random.default_rng(1), 3)
    assert all(len(lits) == 1 for _, lits in v)


# ---------------------------------------------------------------- T11 end to end

def test_t11_an_evaluation_of_a_core_tf_program(tmp_path, tmp_ledger):
    from omr import evaluate
    src = tmp_path / "x_tf.omr"
    src.write_text(prog_text("n = param(3, 2, 4)\nsignal = sign(sma(tf_mean(ret(close, 1), daily), n))\n",
                             kind="single", name="x_tf"), encoding="ascii")
    row = evaluate.evaluate_file(str(src), 0, provider=SynthProvider(synth_world(seed=5, extended=8)), quiet=True,
                                 require_lock=False, p_max=0.1, opts=PL.Opts(perm_n=40, jitter_n=2, truncation_cuts=2,
                                                                             start_cuts=1, start_cuts_val=1))
    assert row["status"] == "evaluated" and row["lookback_hours"] == 48 + 3 * 24
