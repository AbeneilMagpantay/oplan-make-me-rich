"""E5: property tests over >= 200 random VALID programs (a generator of typed expressions; every
program is accepted by the real parser before use):
- truncation invariance at random cuts (rows up to the cut identical with and without later bars);
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
          "hh": "param(12, 9, 15)", "wd": "param(3, 2, 4)"}


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
            lambda: f"hold({self.B(d - 1)}, {self.B(d - 1)}, {self.B(d - 1)}, {self.B(d - 1)})",
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


def panel(start="2022-01-03 00:00", end="2022-03-13 23:00", shift_weeks=0):
    frames = []
    for seed in (1, 2, 3):                                     # two symbols and the BTC frame
        f = D.assemble_frame(synth_raw(start=start, end=end, seed=seed), D.PROGRAM_EXTRA)
        if shift_weeks:
            f = f.copy()
            f.index = f.index + pd.Timedelta(weeks=shift_weeks)
        frames.append(f)
    return frames[:2], frames[2]


FR, BTC = panel()


def run(prog, frames, btc):
    return X.evaluate(prog, L.default_params(prog), frames, btc)


def test_generator_yields_at_least_200_valid_programs_of_both_kinds():
    assert len(PROGS) >= 200, (len(PROGS), TRIED, REASONS)
    assert sum(p.kind == "portfolio" for p in PROGS) >= 40 and sum(p.kind == "single" for p in PROGS) >= 100
    funcs = set()
    for p in PROGS:
        for tok in L.FUNCTIONS:
            if tok + "(" in p.canonical:
                funcs.add(tok)
    assert len(funcs) >= 35, sorted(set(L.FUNCTIONS) - funcs)       # the generator covers the language


@pytest.mark.parametrize("i", range(0, 220, 1))
def test_program_properties(i):
    if i >= len(PROGS):
        pytest.skip("generator produced fewer programs")
    prog = PROGS[i]
    rng = np.random.default_rng(i)
    full = run(prog, FR, BTC)
    assert full.shape == (len(FR[0]), 2)
    # determinism
    assert np.array_equal(full, run(prog, FR, BTC), equal_nan=True)
    # truncation invariance at random cuts
    for c in sorted(rng.choice(np.arange(24, len(FR[0]) - 1), size=3, replace=False)):
        cut = FR[0].index[c]
        part = run(prog, [f.loc[:cut] for f in FR], BTC.loc[:cut])
        assert np.array_equal(part, full[:c + 1], equal_nan=True), f"cut {c}: {prog.canonical}"
    # per-symbol power-of-two rescale of price / base volume / quote volume / trade count
    scaled = []
    for f in FR + [BTC]:
        g = f.copy()
        for cols in (PRICE_COLS, VOL_COLS, QUOTE_COLS, COUNT_COLS):
            g[cols] = g[cols] * float(2.0 ** int(rng.integers(-6, 7)))
        scaled.append(g)
    assert np.array_equal(run(prog, scaled[:2], scaled[2]), full, equal_nan=True), prog.canonical
    # whole-week time shift
    k = int(rng.integers(1, 60)) * (1 if rng.random() < 0.5 else -1)
    sh = [f.copy() for f in FR + [BTC]]
    for f in sh:
        f.index = f.index + pd.Timedelta(weeks=k)
    assert np.array_equal(run(prog, sh[:2], sh[2]), full, equal_nan=True), prog.canonical
