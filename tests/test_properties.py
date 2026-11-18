"""E5 / K6: property tests over >= 200 random VALID programs (a generator of typed expressions that
includes hold, ema, rsi, atr and every timeframe; every program is accepted by the real parser,
constant probe included, before use):
- truncation invariance at random END cuts (rows up to the cut identical, values and known);
- START-cut invariance (rows removed from the start of every frame, BTC included): wherever the cut
  run is known, the base run is known and bit-identical;
- identical signals under random per-symbol rescales of price, base volume, quote volume and trade
  count (powers of two, so floating point is exact; dimensionless signals must not move);
- identical signals under whole-week time shifts;
- determinism.
"""
import numpy as np
import pandas as pd
import pytest

from omr import datasets as D
from omr import interp as X
from omr import lang as L
from conftest import synth_raw

TF = ["h2", "h3", "h4", "h6", "h8", "h12", "daily", "weekly"]
PRICE = ["open", "high", "low", "close", "mark_close"]
VOL = ["volume", "taker_buy_volume"]
PRICE_COLS = ["open", "high", "low", "close", "mark_klines.open", "mark_klines.high", "mark_klines.low",
              "mark_klines.close"]
VOL_COLS = ["volume", "taker_buy_volume"]
QUOTE_COLS = ["quote_volume", "taker_buy_quote_volume"]
COUNT_COLS = ["trades"]
PARAMS = {"w1": "param(2, 1, 3)", "w2": "param(3, 2, 4)", "w3": "param(4, 3, 5)", "k1": "param(0.5, 0.25, 1.0)",
          "hh": "param(12, 9, 15)", "wd": "param(3, 2, 4)", "hz": "param(6, 4, 9)"}


class Gen:
    def __init__(self, rng, kind):
        self.r, self.kind, self.used = rng, kind, set()

    def pick(self, xs):
        return xs[int(self.r.integers(len(xs)))]

    def w(self):
        if self.r.random() < 0.25:
            return "1"
        n = self.pick(["w1", "w2", "w3"])
        self.used.add(n)
        return n

    def par(self, n):
        self.used.add(n)
        return n

    def field(self, names):
        f = self.pick(names)
        return f if self.r.random() < 0.5 else f"{self.pick(TF)}({f})"

    def P(self, d):
        if d <= 0 or self.r.random() < 0.35:
            return self.field(PRICE)
        fn = self.pick(["sma", "ema", "rmax", "rmin", "median", "lag"])
        return f"{fn}({self.P(d - 1)}, {self.w()})"

    def V(self, d):
        if d <= 0 or self.r.random() < 0.4:
            return self.field(VOL)
        fn = self.pick(["sma", "rsum", "rmax", "ema", "lag"])
        return f"{fn}({self.V(d - 1)}, {self.w()})"

    def base(self):
        return self.pick([
            lambda: "ret(close, 1)",
            lambda: f"{self.P(0)} / {self.P(0)}",
            lambda: f"{self.V(0)} / {self.V(0)}",
            lambda: "funding8h",
            lambda: f"funding_mean({self.w()})",
            lambda: f"btc(close) / lag(btc(close), {self.w()})",
            lambda: f"trades / lag(trades, {self.w()})",
            lambda: "taker_buy_quote_volume / quote_volume",
            lambda: f"rsum(quote_volume, {self.w()}) / rsum(volume, {self.w()}) / close",
        ])()

    def D(self, d):
        if d <= 0 or self.r.random() < 0.2:
            return self.base()
        opts = [
            lambda: f"ret({self.P(d - 1)}, {self.w()})",
            lambda: f"logret({self.P(d - 1)}, {self.w()})",
            lambda: f"zscore({self.pick([self.P, self.V, self.D])(d - 1)}, {self.w()})",
            lambda: f"rank({self.pick([self.P, self.V, self.D])(d - 1)}, {self.w()})",
            lambda: f"rsi({self.P(d - 1)}, {self.w()})",
            lambda: f"realised_vol({self.P(d - 1)}, {self.w()})",
            lambda: f"corr({self.P(d - 1)}, {self.V(d - 1)}, {self.w()})",
            lambda: f"{self.pick(['tanh', 'sign', 'abs'])}({self.D(d - 1)})",
            lambda: f"sqrt(abs({self.D(d - 1)}))",
            lambda: f"exp(clip({self.D(d - 1)}, -1, 1))",
            lambda: f"log({self.P(d - 1)} / {self.P(d - 1)})",
            lambda: f"({self.D(d - 1)} {self.pick(['+', '-', '*', '/'])} {self.D(d - 1)})",
            lambda: f"(-{self.D(d - 1)})",
            lambda: f"min2({self.D(d - 1)}, {self.D(d - 1)})",
            lambda: f"max2({self.D(d - 1)}, 0.5)",
            lambda: f"where({self.B(d - 1)}, {self.D(d - 1)}, {self.D(d - 1)})",
            lambda: f"where({self.B(d - 1)}, 1, -1)",
            lambda: f"hold({self.B(d - 1)}, {self.B(d - 1)}, {self.B(d - 1)}, {self.B(d - 1)}, {self.par('hz')})",
            lambda: f"ema({self.D(d - 1)}, {self.w()})",
            lambda: f"rsi({self.field(PRICE)}, {self.w()})",
            lambda: f"atr(h4(high), h4(low), h4(close), {self.w()}) / h4(close)",
            lambda: f"atr(high, low, close, {self.w()}) / close",
            lambda: f"atr(daily(high), daily(low), daily(close), {self.w()}) / daily(close)",
            lambda: f"delta({self.P(d - 1)}, {self.w()}) / {self.P(d - 1)}",
            lambda: f"std({self.P(d - 1)}, {self.w()}) / {self.P(d - 1)}",
            lambda: f"({self.D(d - 1)} * {self.par('k1')})",
        ]
        if self.kind == "portfolio":
            opts += [lambda: f"{self.pick(['cs_rank', 'cs_demean', 'cs_scale', 'cs_mean'])}({self.D(d - 1)})"] * 3
        return self.pick(opts)()

    def B(self, d):
        opts = [
            lambda: f"{self.D(d - 1)} > 0",
            lambda: f"{self.D(d - 1)} < 0.5",
            lambda: f"{self.D(d - 1)} >= -0.5",
            lambda: f"{self.P(d - 1)} > {self.P(d - 1)}",
            lambda: f"{self.D(d - 1)} <= {self.par('k1')}",
            lambda: f"hour > {self.par('hh')}",
            lambda: f"weekday < {self.par('wd')}",
        ]
        if d > 0:
            opts += [lambda: f"({self.B(d - 1)} and {self.B(d - 1)})", lambda: f"({self.B(d - 1)} or {self.B(d - 1)})",
                     lambda: f"not ({self.B(d - 1)})"]
        return self.pick(opts)()

    def program(self):
        lines, names = [], []
        for i in range(int(self.r.integers(0, 3))):
            names.append(f"x{i}")
            lines.append(f"x{i} = {self.D(int(self.r.integers(1, 3)))}")
        sig = self.D(int(self.r.integers(1, 4)))
        if names:
            sig = "clip(" + " + ".join(names + [sig]) + ", -1, 1)"
        head = (f'name = "x_prop"\nfamily = "other"\nkind = "{self.kind}"\n'
                'hypothesis = "random valid program for property tests"\n')
        decl = "".join(f"{n} = {PARAMS[n]}\n" for n in sorted(self.used))
        return head + decl + "\n".join(lines) + ("\n" if lines else "") + f"signal = {sig}\n"


def generate(n_target=220, seed=20261119):
    rng = np.random.default_rng(seed)
    out, tried, reasons = [], 0, {}
    while len(out) < n_target and tried < 20 * n_target:
        tried += 1
        g = Gen(rng, "portfolio" if rng.random() < 0.35 else "single")
        text = g.program()
        try:
            out.append(L.parse(text, "x_prop"))
        except L.LangError as e:
            reasons[e.rule] = reasons.get(e.rule, 0) + 1
    return out, tried, reasons


PROGS, TRIED, REASONS = generate()


def panel(start="2022-01-03 00:00", end="2022-07-24 23:00", shift_weeks=0):
    frames = []
    for seed in (1, 2, 3):                                     # two symbols and the BTC frame
        raw = synth_raw(start=start, end=end, seed=seed)
        mk = raw["mark_klines"]                                # mark gaps: single bars and a 10-hour block
        keep = np.random.default_rng(seed).uniform(size=len(mk)) > 0.02
        keep[1000 + 100 * seed:1010 + 100 * seed] = False
        raw["mark_klines"] = mk[keep]
        f = D.assemble_frame(raw, D.PROGRAM_EXTRA)
        if shift_weeks:
            f = f.copy()
            f.index = f.index + pd.Timedelta(weeks=shift_weeks)
        frames.append(f)
    return frames[:2], frames[2]


FR, BTC = panel()


def run(prog, frames, btc):
    return X.evaluate_full(prog, L.default_params(prog), frames, btc)


def rescaled(frames, rng):
    out = []
    for f in frames:
        g = f.copy()
        p = float(2.0 ** int(rng.integers(-6, 7)))
        v = float(2.0 ** int(rng.integers(-6, 7)))
        n = float(2.0 ** int(rng.integers(-6, 7)))
        g[PRICE_COLS] = g[PRICE_COLS] * p
        g[VOL_COLS] = g[VOL_COLS] * v
        g[QUOTE_COLS] = g[QUOTE_COLS] * (p * v)
        g[COUNT_COLS] = g[COUNT_COLS] * n
        out.append(g)
    return out[:-1], out[-1]


def same(a, b):
    return np.array_equal(a[0], b[0], equal_nan=True) and np.array_equal(a[1], b[1])


def test_vwap_feature_is_accepted_and_scale_invariant():
    """C2: close against the rolling VWAP (quote volume / volume has the unit of price)."""
    prog = L.parse('name = "x_vwap"\nfamily = "trend"\nkind = "single"\nhypothesis = "close above its rolling vwap"\n'
                   "n = param(20, 5, 60)\nv = rsum(quote_volume, n) / rsum(volume, n)\nsignal = sign(close - v)\n",
                   "x_vwap")
    full = run(prog, FR, BTC)
    assert full[1][30:].all() and np.isfinite(full[0][30:]).all()
    rng = np.random.default_rng(5)
    for _ in range(5):
        assert same(run(prog, *rescaled(FR + [BTC], rng)), full)


def test_generator_yields_at_least_200_valid_programs_of_both_kinds():
    assert len(PROGS) >= 200, (len(PROGS), TRIED, REASONS)
    assert sum(p.kind == "portfolio" for p in PROGS) >= 40 and sum(p.kind == "single" for p in PROGS) >= 100
    funcs = set()
    for p in PROGS:
        for tok in L.FUNCTIONS:
            if tok + "(" in p.canonical:
                funcs.add(tok)
    assert {"hold", "ema", "rsi", "atr"} | set(L.TIMEFRAMES) <= funcs, sorted(set(L.FUNCTIONS) - funcs)
    assert len(funcs) >= 38, sorted(set(L.FUNCTIONS) - funcs)
    known_rows = sum(int(run(p, FR, BTC)[1].sum() > 0) for p in PROGS)
    assert known_rows >= 0.8 * len(PROGS)                     # most programs are known somewhere on the panel


@pytest.mark.parametrize("i", range(0, 220, 1))
def test_program_properties(i):
    if i >= len(PROGS):
        pytest.skip("generator produced fewer programs")
    prog = PROGS[i]
    rng = np.random.default_rng(i)
    full = run(prog, FR, BTC)
    raw, kn = full
    n = len(FR[0])
    assert raw.shape == (n, 2) and np.isnan(raw[~kn]).all()
    assert same(full, run(prog, FR, BTC))                                              # determinism
    for c in sorted(rng.choice(np.arange(24, n - 1), size=3, replace=False)):         # end cuts
        cut = FR[0].index[c]
        part = run(prog, [f.loc[:cut] for f in FR], BTC.loc[:cut])
        assert np.array_equal(part[0], raw[:c + 1], equal_nan=True) and np.array_equal(part[1], kn[:c + 1]), \
            f"end cut {c}: {prog.canonical}"
    for c in sorted(rng.choice(np.arange(1, int(0.6 * n)), size=3, replace=False)):   # start cuts
        cut = FR[0].index[c]
        rc, kc = run(prog, [f.loc[cut:] for f in FR], BTC.loc[cut:])
        assert kn[c:][kc].all(), f"start cut {c}: known in the cut run but not in the base run: {prog.canonical}"
        assert np.array_equal(rc[kc], raw[c:][kc], equal_nan=True), f"start cut {c}: {prog.canonical}"
    assert same(run(prog, *rescaled(FR + [BTC], rng)), full), prog.canonical             # power-of-two rescale
    k = int(rng.integers(1, 60)) * (1 if rng.random() < 0.5 else -1)                   # whole-week shift
    sh = [f.copy() for f in FR + [BTC]]
    for f in sh:
        f.index = f.index + pd.Timedelta(weeks=k)
    assert same(run(prog, sh[:2], sh[2]), full), prog.canonical
