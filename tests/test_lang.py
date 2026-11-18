"""E6: every grammar, header, param, limit, literal, type/unit, field, timeframe and function rule of
the .omr language, each with an accepted and a rejected case; canonical form and trial identity."""
import pytest

from omr import constants as C
from omr import lang as L
from conftest import prog_text

H = 'name = "x_test"\nfamily = "other"\nkind = "single"\nhypothesis = "test program for the kernel test suite"\n'
HP = H.replace('kind = "single"', 'kind = "portfolio"')


def rule_of(text, stem="x_test"):
    try:
        L.parse(text, stem)
        return None
    except L.LangError as e:
        return e.rule


OK_BODIES = [
    # (body, kind)
    ("signal = sign(close - open)", "single"),
    ("n = param(20, 5, 60)\nsignal = sign(sma(daily(close), n) - daily(close))", "single"),
    ("n = param(3, 2, 5)\nsignal = zscore(volume, n)", "single"),
    ("signal = tanh(ret(close, 1))", "single"),
    ("signal = clip(logret(h4(close), 1), -1, 1)", "single"),
    ("signal = where(close > open, 1, -1)", "single"),
    ("signal = where(close > open, 0.5, -0.5)", "single"),
    ("n = param(4, 2, 8)\nsignal = rank(volume, n) - 0.5", "single"),
    ("signal = sign(close / btc(close) - lag(close / btc(close), 1))", "single"),
    ("n = param(5, 2, 10)\nsignal = corr(close, btc(close), n)", "single"),
    ("n = param(5, 2, 10)\nsignal = atr(high, low, close, n) / close", "single"),
    ("n = param(5, 2, 10)\nsignal = realised_vol(close, n) - 1", "single"),
    ("n = param(5, 2, 10)\nsignal = funding_mean(n) / funding8h", "single"),
    ("k = param(12, 9, 15)\nsignal = where(hour > k, 1, 0)", "single"),
    ("k = param(3, 2, 4)\nsignal = where(weekday < k, 1, 0)", "single"),
    ("h = param(10, 5, 20)\nsignal = hold(close > open, close < open, close < low, close > high, h)", "single"),
    ("signal = sign(mark_close - close)", "single"),
    ("signal = sign(taker_buy_volume / volume - 0.5)", "single"),
    ("signal = sign(taker_buy_quote_volume / quote_volume - 0.5)", "single"),
    ("signal = sign(trades / lag(trades, 1) - 1)", "single"),
    ("signal = cs_rank(ret(close, 1))", "portfolio"),
    ("signal = cs_scale(cs_demean(ret(close, 1)))", "portfolio"),
    ("signal = cs_mean(ret(close, 1))", "portfolio"),
    ("x = weekly(close)\nsignal = sign(x - lag(x, 1))", "single"),
    ("a = h2(high)\nb = h3(low)\nc = h6(open)\nd = h8(close)\ne = h12(close)\n"
     "signal = sign(a - d) + sign(c - e) + sign(b - d)", "single"),
    ("k = param(2.0, 1.5, 3.0)\nsignal = min2(1, max2(-1, k * ret(close, 1)))", "single"),
    ("k = param(0.5, 0.25, 1.0)\nsignal = sqrt(abs(ret(close, 1))) * k", "single"),
    ("signal = log(close / open) + exp(ret(close, 1)) - 1", "single"),
    ("signal = where(not (close > open) and close > low or close > high, 1, 0)", "single"),
    ("k = param(-0.005, -0.01, -0.0025)\nsignal = where(ret(close, 1) < k, 1, 0)", "single"),
    ("n = param(2, 1, 4)\nsignal = delta(ret(close, 1), n)", "single"),
    ("n = param(3, 2, 5)\nsignal = sign(rsum(volume, n) - rmax(volume, n) - rmin(volume, n) - ema(volume, n))", "single"),
    ("n = param(3, 2, 5)\nsignal = rsi(daily(close), n)", "single"),
    ("n = param(20, 5, 60)\nsignal = where(zscore(close, n) > 2, 1, 0)", "single"),
    ("signal = where(hour > 3, 1, 0)", "single"),
    ("n = param(20, 5, 60)\nv = rsum(quote_volume, n) / rsum(volume, n)\nsignal = sign(close - v)", "single"),
    ("signal = sign(quote_volume / volume - close) + sign(btc(quote_volume) / btc(volume) - btc(close))", "single"),
]

PROBE = 'name = "{stem}"\nfamily = "other"\nkind = "single"\nhypothesis = "coordinator probe of the parser rules"\n'
# the coordinator's probe (C1): (stem, body, number of jitterable literals)
PROBES = [
    ("p01_shifted_threshold", "n = param(20, 5, 60)\nz = zscore(close, n)\nsignal = where(z - 2 > 0, -1, where(z + 2 < 0, 1, 0))\n", 4),
    ("p02_named_literal", "n = param(20, 5, 60)\nthr = 7\nz = zscore(close, n)\nsignal = where(z * 4 > thr, -1, 0)\n", 3),
    ("p03_inert_param", "n = param(20, 5, 60)\nk = param(100, 50, 200)\nz = zscore(close, n)\nsignal = where(z > k * 0 + 3, -1, 0)\n", 2),
    ("p04_min2_constant", "n = param(20, 5, 60)\nk = param(100, 50, 200)\nz = zscore(close, n)\nsignal = where(z > min2(k, 3), -1, 0)\n", 2),
    ("p06_scaled_tanh", "n = param(20, 5, 60)\nsignal = tanh(zscore(close, n) * 3)\n", 1),
    ("p08_plain_threshold", "n = param(20, 5, 60)\nz = zscore(close, n)\nsignal = where(z > 2, -1, 0)\n", 2),
]


@pytest.mark.parametrize("stem,body,n_lit", PROBES)
def test_probe_programs_are_accepted_and_their_literals_are_jitterable(stem, body, n_lit):
    p = L.parse(PROBE.format(stem=stem) + body, stem)
    assert p.n_literals == n_lit, p.literals
    assert all(v != 0 for _, v in p.literals)


def test_zero_and_window_arguments_are_not_literals_and_order_is_source_order():
    p = L.parse(prog_text("n = param(3, 2, 5)\nsignal = where(ret(close, 1) > 0, 2 * sign(lag(ret(close, n), 1)), -0.5)"),
                "x_test")
    assert [v for _, v in p.literals] == [2.0, -0.5]                      # 0 and the windows 1 excluded
    assert p.literals == sorted(p.literals)
    q = L.parse(prog_text("n = param(3, 2, 5)\nsignal = sign(ret(close, 1)) + sign(lag(ret(close, n), 1))"), "x_test")
    assert q.n_literals == 0


def test_the_ones_series_constant_is_rejected_by_the_probe():
    body = "n = param(20, 5, 60)\none = close / close\nz = zscore(close, n)\nsignal = where(z > one + one + one, -1, 0)\n"
    with pytest.raises(L.LangError) as e:
        L.parse(PROBE.format(stem="p05_ones_series") + body, "p05_ones_series")
    assert e.value.rule == "constant_subexpression" and e.value.line == 6


@pytest.mark.parametrize("body,rule", [
    ("signal = sign(close / close - ret(close, 1))", "constant_subexpression"),
    ("n = param(5, 2, 8)\nsignal = sign(rank(close, 1) - ret(close, n))", "constant_subexpression"),
    ("signal = sign(ret(close, 1) - ret(close, 1) + ret(open, 1))", "constant_subexpression"),
    ("signal = sign(close / open) * ret(close, 1)", "constant_subexpression"),
    ("signal = sign(median(close, 1) - close) + sign(ret(close, 1))", "constant_subexpression"),
    ("signal = sign(std(close, 1) / close) + sign(ret(close, 1))", "constant_subexpression"),
    ("n = param(47, 37, 57)\nsignal = rank(zscore(sma(ret(weekly(close), 1), n), n), n) - 0.5", "probe_undefined"),
    ("n = param(20, 5, 60)\nz = zscore(close, n)\nsignal = where(z * 0.5 * 0.5 > 1, -1, 0)", "constant_subexpression"),
    ("signal = where(ret(close, 1) > 10, 1, 0)", "constant_subexpression"),
])
def test_constant_probe(body, rule):
    with pytest.raises(L.LangError) as e:
        L.parse(prog_text(body), "x_test")
    assert e.value.rule == rule, body


def test_boolean_nodes_are_not_probed():
    # the rare condition never fires on the probe panel, but only its numeric where() is probed: varies
    L.parse(prog_text("signal = where(ret(close, 1) > 10, ret(close, 1), 0 - ret(close, 1))"), "x_test")


def test_exponential_reuse_is_bounded():
    body = "x0 = ret(close, 1)\n" + "".join(f"x{i} = x{i - 1} + x{i - 1}\n" for i in range(1, 20)) + "signal = tanh(x19)"
    with pytest.raises(L.LangError) as e:
        L.parse(prog_text(body), "x_test")
    assert e.value.rule == "inlined_too_large"


def test_literal_cap():
    ok = "signal = clip(" + " + ".join(f"{i} * ret(close, 1)" for i in range(1, 9)) + ", -1, 1)"
    with pytest.raises(L.LangError) as e:                                 # 8 terms + the two clip bounds = 10
        L.parse(prog_text(ok), "x_test")
    assert e.value.rule == "too_many_literals"
    eight = "signal = " + " + ".join(f"{i} * ret(close, 1)" for i in range(1, 9))
    assert L.parse(prog_text(eight), "x_test").n_literals == 8
    nine = "signal = " + " + ".join(f"{i} * ret(close, 1)" for i in range(1, 10))
    with pytest.raises(L.LangError) as e:
        L.parse(prog_text(nine), "x_test")
    assert e.value.rule == "too_many_literals"


def test_huge_integer_literals_are_parse_errors_not_crashes():
    for body in ("n = param(" + "9" * 400 + ", 1, 2)\nsignal = sign(ret(close, n))",
                 "signal = sign(ret(close, 1)) * " + "9" * 400):
        with pytest.raises(L.LangError) as e:
            L.parse(prog_text(body), "x_test")
        assert e.value.rule == "parse_error"


def test_quote_volume_is_price_times_volume():
    p = L.parse(prog_text("signal = sign(quote_volume / volume - close)"), "x_test")
    assert L.FIELDS["quote_volume"][0] == (("P", 1), ("V", 1))
    assert L.FIELDS["taker_buy_quote_volume"][0] == (("P", 1), ("V", 1))
    assert p.types["signal"].unit == ()


@pytest.mark.parametrize("body,kind", OK_BODIES)
def test_accepts(body, kind):
    assert rule_of(prog_text(body, kind=kind)) is None, body


BAD = [
    # (full text or body, expected rule, kind)
    ("import os\nsignal = sign(close - open)", "statement"),
    ("def f():\n    pass\nsignal = sign(close - open)", "statement"),
    ("x += 1\nsignal = sign(close - open)", "statement"),
    ("x: int = 1\nsignal = sign(close - open)", "statement"),
    ("a = b = close\nsignal = sign(a - b)", "target"),
    ("a, b = close, open\nsignal = sign(a - b)", "target"),
    ("A = close\nsignal = sign(A - open)", "target_name"),
    ("x = close\nx = open\nsignal = sign(x - close)", "reassigned"),
    ("close = open\nsignal = sign(close - open)", "shadowing"),
    ("sma = open\nsignal = sign(sma - close)", "shadowing"),
    ("param = open\nsignal = sign(param - close)", "shadowing"),
    ("signal = sign(close - open)\nx = close", "signal_last"),
    ("x = y\ny = close\nsignal = sign(x - y)", "undefined"),
    ("x = close\nsignal = sign(close - open)", "name_unused"),
    ("n = param(5, 2, 10)\nsignal = sign(close - open)", "param_unused"),
    ("signal = close - open", "signal_type"),
    ("signal = close > open", "signal_type"),
    ("n = param(5, 2, 10)\nsignal = n", "signal_type"),
    # params (A4)
    ("n = param(5, 2)\nsignal = sma(ret(close, 1), n)", "param_form"),
    ("n = param(5, 2, high=10)\nsignal = sma(ret(close, 1), n)", "param_form"),
    ("n = param(x, 2, 10)\nsignal = sma(ret(close, 1), n)", "param_literal"),
    ("n = param(5, 6, 10)\nsignal = sma(ret(close, 1), n)", "param_range"),
    ("n = param(0.0, -0.01, 0.01)\nsignal = ret(close, 1) * n", "param_zero_default"),
    ("n = param(20.0, 19.999, 20.001)\nsignal = ret(close, 1) * n", "param_jitter_range"),
    ("n = param(5, 5, 10)\nsignal = sma(ret(close, 1), n)", "param_jitter_range"),
    ("n = param(5, 1, 5)\nsignal = sma(ret(close, 1), n)", "param_jitter_range"),
    ("".join(f"p{i} = param(1.0, 0.5, 2.0)\n" for i in range(7)) + "signal = ret(close, 1) * "
     + " * ".join(f"p{i}" for i in range(7)), "too_many_params"),
    # limits (A5)
    ("".join(f"x{i} = ret(close, 1)\n" for i in range(30)) + "signal = " + " + ".join(f"x{i}" for i in range(30)),
     "too_many_statements"),
    ("signal = " + "abs(" * 13 + "ret(close, 1)" + ")" * 13, "too_deep"),
    ("".join(f"x{i} = " + " + ".join(["ret(close, 1)"] * 6) + "\n" for i in range(10))
     + "signal = " + " + ".join(f"x{i}" for i in range(10)), "too_many_nodes"),
    # operators and nodes (A6)
    ("signal = ret(close, 1) ** 2", "operator"),
    ("signal = ret(close, 1) % 2", "operator"),
    ("signal = ret(close, 1) // 2", "operator"),
    ("signal = where(close == open, 1, 0)", "comparison"),
    ("signal = where(close != open, 1, 0)", "comparison"),
    ("signal = where(low < close < high, 1, 0)", "comparison"),
    ("signal = close.shift(-1) / close", "call"),
    ("signal = close.shift / close", "node"),
    ("signal = close[0] / close", "node"),
    ("signal = (lambda: 1)()", "call"),
    ("signal = [x for x in close]", "node"),
    ("signal = ret(close, 1) if hour else ret(open, 1)", "node"),
    ('signal = where(close > open, "1", 0)', "node"),
    ("signal = where(close > open, True, 0)", "node"),
    ("signal = sign(close - open) + {}", "node"),
    ("signal = (y := ret(close, 1))", "node"),
    ("signal = ~ret(close, 1)", "operator"),
    ("signal = +ret(close, 1)", "operator"),
    ("signal = foo(close)", "unknown_function"),
    ("signal = sma", "bare_function"),
    ("signal = sma(close, n=5)", "keywords"),
    ("signal = sign(*close)", "node"),
    ("signal = abs(close)", "signal_type"),
    ("signal = sign(close, open)", "arity"),
    # literals (A7)
    ("signal = ret(close, 1) * 11", "literal_value"),
    ("signal = ret(close, 1) * 0.25", "literal_value"),
    ("signal = ret(close, 1) * 1e9", "literal_value"),
    ("signal = sma(ret(close, 1), 5)", "window_arg"),
    ("signal = lag(ret(close, 1), -1)", "window_arg"),
    ("signal = lag(ret(close, 1), 0)", "window_arg"),
    ("k = param(2.0, 1.0, 3.0)\nsignal = lag(ret(close, 1), k)", "window_arg"),
    ("n = param(2, 0, 3)\nsignal = lag(ret(close, 1), n)", "window_param_low"),
    ("n = param(4000, 3000, 6000)\nsignal = sma(ret(close, 1), n)", "window_limit"),
    ("n = param(300, 200, 500)\nsignal = sma(ret(daily(close), 1), n)", "window_limit"),
    ("n = param(60, 40, 80)\nsignal = sma(ret(weekly(close), 1), n)", "window_limit"),
    ("signal = where(ret(close, 1) > 0.0001, 1, 0)", "literal_value"),
    ("signal = where(ret(close, 1) > 2.5, 1, 0)", "literal_value"),
    ("signal = where(hour > 11, 1, 0)", "literal_value"),
    ("signal = where(close > " + "9" * 400 + ", 1, 0)", "parse_error"),
    ("signal = sign(quote_volume - close)", "unit"),
    ("signal = sign(quote_volume / close - close)", "unit"),
    ("signal = ret(close, 1) * (2 * 3)", "literal_expression"),
    ("x = 2 * 3\nsignal = ret(close, 1) * x", "literal_expression"),
    ("k = param(2.0, 1.0, 3.0)\nsignal = where(k > 1, ret(close, 1), 0)", "scalar_comparison"),
    # types and units (A8)
    ("signal = sign(close - volume)", "unit"),
    ("signal = where(close > volume, 1, 0)", "unit"),
    ("signal = where(close > 0, 1, 0)", "unit"),
    ("signal = tanh(close)", "unit"),
    ("signal = sign(close / btc(close) - 1) + sign(close - btc(close))", "unit"),
    ("signal = where(close > open, close, 0)", "unit"),
    ("signal = clip(close, -1, 1)", "unit"),
    ("signal = min2(close, 1)", "unit"),
    ("signal = sign((close > open) - 1)", "type"),
    ("signal = where(close, 1, 0)", "type"),
    ("h = param(10, 5, 20)\nsignal = hold(close, close > open, close < open, close < low, h)", "type"),
    ("signal = hold(close > open, close < open, close < low, close > high)", "arity"),
    ("signal = hold(close > open, close < open, close < low, close > high, 5)", "window_arg"),
    ("n = param(900, 700, 1100)\nsignal = ema(ret(close, n), n)", "window_limit"),
    ("n = param(501, 400, 650)\nsignal = rsi(close, n)", "window_limit"),
    ("signal = sign(lag(lag(close, 1), 1) - close)", "nested_unit_window"),
    ("signal = sign(ret(lag(close, 1), 1))", "nested_unit_window"),
    ("a = lag(close, 1)\nsignal = sign(ret(a, 1))", "nested_unit_window"),
    ("signal = sign(ema(ret(close, 1), 1))", "nested_unit_window"),
    ("signal = where(not close, 1, 0)", "type"),
    ("signal = where((close > open) and close, 1, 0)", "type"),
    ("signal = cs_rank(ret(close, 1))", "cross_section_single"),
    # fields and timeframes (A9, A10)
    ("signal = sign(index - 1)", "undefined"),
    ("signal = sign(bar_count - 1)", "undefined"),
    ("signal = btc(hour)", "btc_arg"),
    ("signal = btc(ret(close, 1))", "btc_arg"),
    ("signal = daily(ret(close, 1))", "timeframe_arg"),
    ("signal = daily(hour)", "timeframe_arg"),
    ("signal = daily(funding8h)", "timeframe_arg"),
    ("signal = monthly(close) / close", "unknown_function"),
]


@pytest.mark.parametrize("body,rule", BAD)
def test_rejects_with_rule(body, rule):
    kind = "single"
    assert rule_of(prog_text(body, kind=kind)) == rule, body


@pytest.mark.parametrize("text,rule", [
    ('family = "other"\nkind = "single"\nhypothesis = "test program for the kernel test suite"\nsignal = sign(close - open)',
     "header_missing"),
    ('signal_x = close\n' + H + "signal = sign(close - open)", "header_missing"),
    (H.replace('"x_test"', '"other_name"') + "signal = sign(close - open)", "header_name"),
    (H.replace('"x_test"', '"X_Test"') + "signal = sign(close - open)", "header_name"),
    (H.replace('family = "other"', 'family = "magic"') + "signal = sign(close - open)", "header_family"),
    (H.replace('kind = "single"', 'kind = "multi"') + "signal = sign(close - open)", "header_kind"),
    (H.replace("test program for the kernel test suite", "short") + "signal = sign(close - open)", "header_hypothesis"),
    (H.replace("test program for the kernel test suite", "x" * 501) + "signal = sign(close - open)", "header_hypothesis"),
    (H.replace("test program for the kernel test suite", "caf\u00e9 au lait rule set") + "signal = sign(close - open)",
     "header_hypothesis"),
    (H.replace('family = "other"', "family = 3") + "signal = sign(close - open)", "header_value"),
    (H + 'x = ret(close, 1)\nname = "x_test"\nsignal = sign(x)', "reassigned"),
    ('name = "x_test"\nfamily = "other"\nx = ret(close, 1)\nkind = "single"\n'
     'hypothesis = "test program for the kernel test suite"\nsignal = sign(x)', "header_missing"),
])
def test_header_rules(text, rule):
    assert rule_of(text) == rule


def test_parse_errors_and_size():
    assert rule_of(H + "signal = (") == "parse_error"
    assert rule_of(H + "signal = sign(close - open)\x00") == "parse_error"
    assert rule_of(H + "signal = " + "(" * 400 + "close" + ")" * 400) in ("parse_error", "too_deep")
    assert rule_of(H + "# " + "x" * L.MAX_BYTES + "\nsignal = sign(close - open)") == "too_large"


def test_parse_file_checks_suffix_utf8_and_stem(tmp_path):
    p = tmp_path / "x_test.omr"
    p.write_text(H + "signal = sign(close - open)", encoding="utf-8")
    assert L.parse_file(p).name == "x_test"
    q = tmp_path / "x_test.py"
    q.write_text(H + "signal = sign(close - open)", encoding="utf-8")
    with pytest.raises(L.LangError) as e:
        L.parse_file(q)
    assert e.value.rule == "file_type"
    r = tmp_path / "x_test2.omr"
    r.write_bytes(b"\xff\xfe" + (H + "signal = sign(close - open)").encode("ascii"))
    with pytest.raises(L.LangError) as e:
        L.parse_file(r)
    assert e.value.rule == "parse_error"


def test_errors_carry_line_and_column():
    with pytest.raises(L.LangError) as e:
        L.parse(H + "x = ret(close, 1)\nsignal = sign(x) ** 2", "x_test")
    assert e.value.rule == "operator" and e.value.line == 6 and e.value.col == 9


def test_integer_params_and_jitter_ranges():
    p = L.parse(prog_text("n = param(20, 5, 60)\nk = param(-0.0001, -0.0005, 0.0)\n"
                          "signal = where(funding_mean(n) < k, 1, 0)"), "x_test")
    assert p.params["n"].is_int and not p.params["k"].is_int
    assert L.default_params(p) == {"n": 20, "k": -0.0001}
    q = L.parse(prog_text("n = param(20.0, 5, 60)\nsignal = ret(close, 1) * n"), "x_test")
    assert not q.params["n"].is_int


def test_canonical_form_inlines_names_and_orders_params_by_first_use():
    a = L.parse(prog_text("fast = param(20, 5, 60)\nslow = param(100, 50, 250)\nd = daily(close)\n"
                          "signal = sign(sma(d, fast) - sma(d, slow))"), "x_test")
    b = L.parse(prog_text("slow = param(100, 50, 250)\nfast = param(20, 5, 60)\n# renamed and reordered\n"
                          "x = daily(close)\nq = sma(x, fast)\nsignal = sign(q - sma(x, slow))"), "x_test")
    assert a.canonical == b.canonical
    assert a.canonical == ("kind=single;signal=sign((sma(daily(close),$0)-sma(daily(close),$1)));"
                           "params=[$0:int(20,5,60),$1:int(100,50,250)]")
    rh = "r" * 64
    sem = "s" * 64
    assert L.trial_id(a, sem, rh) == L.trial_id(b, sem, rh) and len(L.trial_id(a, sem, rh)) == 16
    c = L.parse(prog_text("fast = param(21, 5, 60)\nslow = param(100, 50, 250)\nd = daily(close)\n"
                          "signal = sign(sma(d, fast) - sma(d, slow))"), "x_test")
    assert L.trial_id(c, sem, rh) != L.trial_id(a, sem, rh)                   # defaults are part of identity
    assert L.trial_id(a, sem, "q" * 64) != L.trial_id(a, sem, rh)             # research hash is part of identity


def test_the_semantic_kernel_hash_is_part_of_identity():
    a = L.parse(prog_text("signal = sign(close - open)"), "x_test")
    assert L.trial_id(a, "s" * 64, "r" * 64) != L.trial_id(a, "t" * 64, "r" * 64)
