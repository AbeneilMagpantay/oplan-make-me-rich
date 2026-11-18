"""The strategy language (.omr): parse, check, type and canonicalise. Kernel module.

A program is never compiled, executed, evaluated or imported. Its text is parsed with ast.parse
and the resulting tree is walked by this module only; omr.interp evaluates the checked tree with
numpy. See LANGUAGE.md for the grammar, fields, functions, units and limits.
"""
from __future__ import annotations

import ast
import hashlib
import math
import re
from dataclasses import dataclass, field

from omr import constants as C

MAX_BYTES = 16 * 1024
NAME_PATTERN = r"[a-z_][a-z0-9_]*"
PROGRAM_NAME_PATTERN = r"[a-z0-9_]{3,64}"


def _name_ok(s: str) -> bool:
    return isinstance(s, str) and s.isascii() and re.fullmatch(NAME_PATTERN, s) is not None


def _program_name_ok(s: str) -> bool:
    return isinstance(s, str) and s.isascii() and re.fullmatch(PROGRAM_NAME_PATTERN, s) is not None

HEADER = ("name", "family", "kind", "hypothesis")
FAMILIES = ("trend", "meanrev", "carry", "volatility", "relative", "flow", "other")
MAX_PARAMS = C.MAX_PARAMS
MAX_BODY = 30
MAX_NODES = 120
MAX_DEPTH = 12
MAX_WINDOW_BARS = 5000
MAX_WINDOW_DAYS = 400
MAX_LITERALS = 8              # jitterable literal tokens (every body literal except 0; windows excluded)

_P, _V, _N = (("P", 1),), (("V", 1),), (("N", 1),)
_PV = (("P", 1), ("V", 1))     # quote volume = price x base volume
# field -> (unit: sorted ((base, exponent), ...), () = dimensionless; aggregation for timeframes or None)
FIELDS = {
    "open": (_P, "first"), "high": (_P, "max"), "low": (_P, "min"), "close": (_P, "last"),
    "mark_close": (_P, "last"), "volume": (_V, "sum"), "taker_buy_volume": (_V, "sum"),
    "quote_volume": (_PV, "sum"), "taker_buy_quote_volume": (_PV, "sum"), "trades": (_N, "sum"),
    "funding8h": ((), None), "hour": ((), None), "weekday": ((), None),
}


def _btc_unit(unit: tuple) -> tuple:
    return tuple(sorted((b + "_btc", e) for b, e in unit))
BTC_FIELDS = tuple(f for f in FIELDS if f not in ("hour", "weekday"))
TIMEFRAMES = {"h2": 2, "h3": 3, "h4": 4, "h6": 6, "h8": 8, "h12": 12, "daily": 24, "weekly": 168}
ROLLING = ("sma", "ema", "std", "rmin", "rmax", "rsum", "median", "zscore", "rank")
LAGS = ("lag", "delta", "ret", "logret")
ELEMENTWISE = ("abs", "sign", "sqrt", "log", "exp", "tanh")
CROSS = ("cs_mean", "cs_demean", "cs_rank", "cs_scale")
FUNCTIONS = (set(ROLLING) | set(LAGS) | set(ELEMENTWISE) | set(CROSS) | set(TIMEFRAMES)
             | {"corr", "rsi", "atr", "realised_vol", "funding_mean", "clip", "min2", "max2", "where", "hold", "btc"})
WINDOW_FUNCS = {**{f: 1 for f in ROLLING}, **{f: 1 for f in LAGS}, "rsi": 1, "realised_vol": 1, "corr": 2,
                "atr": 3, "funding_mean": 0, "hold": 4}          # function -> index of its window argument
# rows of memory per unit of the window argument (the window limits apply to n x this)
WINDOW_MEMORY = {"ema": C.EMA_MEMORY, "rsi": C.RSI_MEMORY, "atr": C.ATR_MEMORY}
ARITY = {**{f: 2 for f in ROLLING}, **{f: 2 for f in LAGS}, **{f: 1 for f in ELEMENTWISE},
         **{f: 1 for f in CROSS}, **{f: 1 for f in TIMEFRAMES},
         "corr": 3, "rsi": 2, "atr": 4, "realised_vol": 2, "funding_mean": 1, "clip": 3, "min2": 2, "max2": 2,
         "where": 3, "hold": 5, "btc": 1}
MAX_INLINED_NODES = 4000      # the canonical (fully inlined) tree; guards against exponential reuse
RESERVED = set(FIELDS) | FUNCTIONS | set(HEADER) | {"param"}


def literal_key(node) -> tuple:
    """Source position of a literal token (the minus sign of a negative literal included)."""
    return (node.lineno, node.col_offset)


class LangError(Exception):
    def __init__(self, rule: str, node=None, msg: str = ""):
        line = getattr(node, "lineno", 0) if node is not None else 0
        col = getattr(node, "col_offset", 0) if node is not None else 0
        super().__init__(f"{rule} at line {line} col {col}: {msg}")
        self.rule, self.line, self.col, self.msg = rule, line, col, msg


@dataclass(frozen=True)
class Ty:
    kind: str                     # "bool", "num" (series) or "scalar"
    unit: tuple = ()              # sorted ((base, exponent), ...); () = dimensionless
    tf: str | None = None         # "h1", "h2", ..., "weekly" for series


SCALAR = Ty("scalar")


@dataclass
class Param:
    name: str
    default: float
    low: float
    high: float
    is_int: bool


@dataclass
class Program:
    header: dict
    params: dict                                    # name -> Param (declaration order)
    defs: list                                      # [(name, ast expr)] in order; last is ("signal", expr)
    types: dict = field(default_factory=dict)       # name -> Ty
    node_count: int = 0
    canonical: str = ""
    param_order: list = field(default_factory=list)  # params in order of first use in the inlined tree
    literals: list = field(default_factory=list)     # [(source key, base value)] jitterable literals, source order

    @property
    def n_literals(self):
        return len(self.literals)

    @property
    def kind(self):
        return self.header["kind"]

    @property
    def name(self):
        return self.header["name"]


def _unit_mul(a: tuple, b: tuple, sign: int = 1) -> tuple:
    d = dict(a)
    for base, e in b:
        d[base] = d.get(base, 0) + sign * e
    return tuple(sorted((k, v) for k, v in d.items() if v != 0))


def _tf_join(*tys) -> str:
    tfs = {t.tf for t in tys if t.kind in ("num", "bool")}
    return tfs.pop() if len(tfs) == 1 else "h1"


def _literal_value(node):
    """Numeric literal (optionally negated) -> (value, is_int) else None."""
    neg = False
    n = node
    if isinstance(n, ast.UnaryOp) and isinstance(n.op, ast.USub):
        neg, n = True, n.operand
    if isinstance(n, ast.Constant) and type(n.value) in (int, float):
        v = -n.value if neg else n.value
        return float(v), type(n.value) is int
    return None


def _str_literal(node):
    return node.value if isinstance(node, ast.Constant) and isinstance(node.value, str) else None


def parse(text: str, stem: str, probe: bool = True) -> Program:
    """Parse and fully check a program. Raises LangError (rule, line, column); any other exception
    raised while checking (e.g. OverflowError from a 400-digit literal) becomes `parse_error`.
    probe=True (always, outside the probe's own unit tests) runs the constant probe (omr.probe)."""
    try:
        return _parse(text, stem, probe)
    except LangError:
        raise
    except Exception as e:
        raise LangError("parse_error", None, type(e).__name__)


def _parse(text: str, stem: str, probe: bool = True) -> Program:
    if not isinstance(text, str):
        raise LangError("parse_error", None, "source must be text")
    if len(text.encode("utf-8")) > MAX_BYTES:
        raise LangError("too_large", None, f"source exceeds {MAX_BYTES} bytes")
    try:
        tree = ast.parse(text, mode="exec")
    except (SyntaxError, RecursionError, MemoryError, ValueError) as e:
        raise LangError("parse_error", None, type(e).__name__)
    stmts = tree.body
    header, params, defs = {}, {}, []
    seen = set()
    for i, st in enumerate(stmts):
        if not isinstance(st, ast.Assign):
            raise LangError("statement", st, f"{type(st).__name__} is not allowed; only `name = expression`")
        if len(st.targets) != 1 or not isinstance(st.targets[0], ast.Name):
            raise LangError("target", st, "exactly one plain-name target")
        name = st.targets[0].id
        if not _name_ok(name):
            raise LangError("target_name", st, f"name {name!r} must match ^[a-z_][a-z0-9_]*$")
        if name in seen:
            raise LangError("reassigned", st, f"{name} assigned twice")
        seen.add(name)
        if name in HEADER:
            if params or defs:
                raise LangError("header_order", st, "header keys come before any other statement")
            v = _str_literal(st.value)
            if v is None:
                raise LangError("header_value", st, f"{name} must be a string literal")
            header[name] = v
            continue
        if len(header) != len(HEADER):
            raise LangError("header_missing", st, f"header needs {', '.join(HEADER)} before other statements")
        if name in RESERVED and name != "signal":
            raise LangError("shadowing", st, f"{name} is a field, function or header key")
        if isinstance(st.value, ast.Call) and isinstance(st.value.func, ast.Name) and st.value.func.id == "param":
            params[name] = _parse_param(name, st.value)
            continue
        defs.append((name, st.value))
    for k in HEADER:
        if k not in header:
            raise LangError("header_missing", None, f"header key {k} missing")
    if header["name"] != stem or not _program_name_ok(header["name"]):
        raise LangError("header_name", None, "name must match ^[a-z0-9_]{3,64}$ and equal the file stem")
    if header["family"] not in FAMILIES:
        raise LangError("header_family", None, f"family must be one of {', '.join(FAMILIES)}")
    if header["kind"] not in ("single", "portfolio"):
        raise LangError("header_kind", None, "kind must be single or portfolio")
    h = header["hypothesis"]
    if len(h) > 500 or not all(32 <= ord(ch) <= 126 for ch in h) or len(h.strip()) < 10:
        raise LangError("header_hypothesis", None, "hypothesis: 10 to 500 printable ASCII characters")
    if len(params) > MAX_PARAMS:
        raise LangError("too_many_params", None, f"{len(params)} params (max {MAX_PARAMS})")
    if not defs or defs[-1][0] != "signal":
        raise LangError("signal_last", None, "the last statement must assign `signal`")
    if any(n == "signal" for n, _ in defs[:-1]):
        raise LangError("reassigned", None, "signal assigned twice")
    if len(defs) > MAX_BODY:
        raise LangError("too_many_statements", None, f"{len(defs)} body assignments (max {MAX_BODY})")
    prog = Program(header=header, params=params, defs=defs)
    _check_body(prog)
    _canonicalise(prog)
    _check_unit_windows(prog)
    if probe:
        from omr import probe as _probe                     # late import: the probe uses the interpreter
        _probe.check(prog)
    return prog


def _is_one(node) -> bool:
    return isinstance(node, ast.Constant) and type(node.value) is int and node.value == 1


def _check_unit_windows(prog: Program):
    """H1b: a call with the literal window 1 may not sit inside another such call on any path of the
    inlined tree (`lag(lag(close, 1), 1)` is a hidden window of 2; a longer fixed lag needs a param)."""
    defs = dict(prog.defs)
    seen = set()

    def walk(node, inside):
        if isinstance(node, ast.Name) and node.id in defs:
            key = (node.id, inside)
            if key not in seen:
                seen.add(key)
                walk(defs[node.id], inside)
            return
        unit = (isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in WINDOW_FUNCS
                and _is_one(node.args[WINDOW_FUNCS[node.func.id]]))
        if unit and inside:
            raise LangError("nested_unit_window", node, f"{node.func.id}(..., 1) inside another call with window 1; "
                            "use an integer param for a longer window")
        for child in ast.iter_child_nodes(node):
            walk(child, inside or unit)
    walk(defs["signal"], False)


def _parse_param(name, call) -> Param:
    if call.keywords or len(call.args) != 3:
        raise LangError("param_form", call, "param(default, low, high) with three positional numeric literals")
    vals = [_literal_value(a) for a in call.args]
    if any(v is None for v in vals):
        raise LangError("param_literal", call, "param bounds must be numeric literals (optional leading minus)")
    (d, di), (lo, li), (hi, hii) = vals
    is_int = di and li and hii
    if not all(math.isfinite(x) for x in (d, lo, hi)) or not (lo <= d <= hi) or lo == hi:
        raise LangError("param_range", call, "need finite low <= default <= high and low < high")
    if d == 0:
        raise LangError("param_zero_default", call, "a zero default cannot be jittered")
    jl, jh = sorted((C.JITTER_LO * d, C.JITTER_HI * d))
    if lo > jl + 1e-12 * abs(d) or hi < jh - 1e-12 * abs(d):
        raise LangError("param_jitter_range", call, f"range must contain [{jl:.6g}, {jh:.6g}]")
    if is_int and (lo > d - 1 or hi < d + 1):
        raise LangError("param_jitter_range", call, "integer range must contain default-1 and default+1")
    return Param(name, d, lo, hi, is_int)


class _Checker:
    def __init__(self, prog: Program):
        self.p = prog
        self.types = {}
        self.nodes = 0
        self.used_params = set()
        self.used_names = set()
        self.literals = {}             # source key -> base value (jitterable literal tokens)

    def has_param(self, node) -> bool:
        return any(isinstance(n, ast.Name) and n.id in self.p.params for n in ast.walk(node))

    def window(self, node, tf: str, fn: str):
        if isinstance(node, ast.Constant) and type(node.value) is int and node.value == 1:
            return
        if isinstance(node, ast.Name) and node.id in self.p.params:
            par = self.p.params[node.id]
            if not par.is_int:
                raise LangError("window_arg", node, f"{fn}: window param {node.id} must be an integer param")
            if par.low < 1:
                raise LangError("window_param_low", node, f"{fn}: window param {node.id} needs low >= 1")
            hours = 8 if fn == "funding_mean" else (1 if tf == "h1" else TIMEFRAMES[tf])
            rows = par.high * WINDOW_MEMORY.get(fn, 1)
            if rows > MAX_WINDOW_BARS or rows * hours > MAX_WINDOW_DAYS * 24:
                raise LangError("window_limit", node, f"{fn}: {node.id} high {par.high:g} gives {rows:g} rows of "
                                f"memory, above {MAX_WINDOW_BARS} bars or {MAX_WINDOW_DAYS} days at this timeframe")
            self.used_params.add(node.id)
            return
        raise LangError("window_arg", node, f"{fn}: a window, lag or count must be an integer param or the literal 1")

    def expr(self, node, depth: int) -> Ty:
        if depth > MAX_DEPTH:
            raise LangError("too_deep", node, f"nesting depth above {MAX_DEPTH}")
        self.nodes += 1
        if self.nodes > MAX_NODES:
            raise LangError("too_many_nodes", node, f"more than {MAX_NODES} expression nodes")
        lit = _literal_value(node)
        if lit is not None:
            v, is_int = lit
            if not ((is_int and -10 <= v <= 10) or v in (0.5, -0.5)):
                raise LangError("literal_value", node, "body literals: integers -10..10 or +-0.5; other numbers must be params")
            if v != 0:                                   # every literal but 0 is jittered like a param (G5)
                self.literals[literal_key(node)] = v
                if len(self.literals) > MAX_LITERALS:
                    raise LangError("too_many_literals", node, f"more than {MAX_LITERALS} literals other than 0 "
                                    "(each is jittered like a param)")
            return SCALAR
        if isinstance(node, ast.Name):
            n = node.id
            if n in self.p.params:
                self.used_params.add(n)
                return SCALAR
            if n in FIELDS:
                return Ty("num", FIELDS[n][0], "h1")
            if n in self.types:
                self.used_names.add(n)
                return self.types[n]
            if n in FUNCTIONS:
                raise LangError("bare_function", node, f"{n} is a function")
            raise LangError("undefined", node, f"{n} is not defined before use")
        if isinstance(node, ast.BinOp):
            if not isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div)):
                raise LangError("operator", node, f"{type(node.op).__name__} is not allowed")
            a, b = self.expr(node.left, depth + 1), self.expr(node.right, depth + 1)
            for t, side in ((a, node.left), (b, node.right)):
                if t.kind == "bool":
                    raise LangError("type", side, "arithmetic on a boolean series")
            if isinstance(node.op, (ast.Add, ast.Sub)):
                if a.unit != b.unit:
                    raise LangError("unit", node, "+ and - need identical units")
                unit = a.unit
            else:
                unit = _unit_mul(a.unit, b.unit, 1 if isinstance(node.op, ast.Mult) else -1)
            if a.kind == "scalar" and b.kind == "scalar":
                self._scalar_ok(node)
                return SCALAR
            return Ty("num", unit, _tf_join(a, b))
        if isinstance(node, ast.UnaryOp):
            if isinstance(node.op, ast.USub):
                t = self.expr(node.operand, depth + 1)
                if t.kind == "bool":
                    raise LangError("type", node, "unary minus on a boolean series")
                if t.kind == "scalar":
                    self._scalar_ok(node)
                return t
            if isinstance(node.op, ast.Not):
                t = self.expr(node.operand, depth + 1)
                if t.kind != "bool":
                    raise LangError("type", node, "`not` needs a boolean series")
                return t
            raise LangError("operator", node, f"{type(node.op).__name__} is not allowed")
        if isinstance(node, ast.BoolOp):
            ts = [self.expr(v, depth + 1) for v in node.values]
            if any(t.kind != "bool" for t in ts):
                raise LangError("type", node, "and/or need boolean series")
            return Ty("bool", (), _tf_join(*ts))
        if isinstance(node, ast.Compare):
            if len(node.ops) != 1 or not isinstance(node.ops[0], (ast.Lt, ast.Gt, ast.LtE, ast.GtE)):
                raise LangError("comparison", node, "single comparison with < > <= >=")
            left, right = node.left, node.comparators[0]
            a, b = self.expr(left, depth + 1), self.expr(right, depth + 1)
            if a.kind == "bool" or b.kind == "bool":
                raise LangError("type", node, "comparison of boolean series")
            if a.kind == "scalar" and b.kind == "scalar":
                raise LangError("scalar_comparison", node, "a comparison between two scalars")
            if a.unit != b.unit:
                raise LangError("unit", node, "comparison needs identical units")
            return Ty("bool", (), _tf_join(a, b))
        if isinstance(node, ast.Call):
            return self.call(node, depth)
        raise LangError("node", node, f"{type(node).__name__} is not allowed")

    def _scalar_ok(self, node):
        if not self.has_param(node):
            raise LangError("literal_expression", node, "an expression made only of literals")

    def series(self, t: Ty, node, what="numeric series"):
        if t.kind != "num":
            raise LangError("type", node, f"expected a {what}")

    def dimless(self, t: Ty, node):
        if t.unit != ():
            raise LangError("unit", node, "needs a dimensionless input")

    def call(self, node, depth) -> Ty:
        if not isinstance(node.func, ast.Name):
            raise LangError("call", node, "functions are called by plain name")
        fn = node.func.id
        if fn not in FUNCTIONS:
            raise LangError("unknown_function", node, f"{fn} is not a function of the language")
        if node.keywords:
            raise LangError("keywords", node, "keyword arguments are not allowed")
        if any(isinstance(a, ast.Starred) for a in node.args):
            raise LangError("node", node, "starred arguments are not allowed")
        if len(node.args) != ARITY[fn]:
            raise LangError("arity", node, f"{fn} takes {ARITY[fn]} arguments")
        args = node.args
        if fn == "btc":
            a = args[0]
            if not (isinstance(a, ast.Name) and a.id in BTC_FIELDS):
                raise LangError("btc_arg", a, "btc() takes a field name")
            self.nodes += 1
            return Ty("num", _btc_unit(FIELDS[a.id][0]), "h1")
        if fn in TIMEFRAMES:
            a = args[0]
            fld = a.id if isinstance(a, ast.Name) else None
            is_btc = isinstance(a, ast.Call) and isinstance(a.func, ast.Name) and a.func.id == "btc"
            if is_btc:
                t = self.expr(a, depth + 1)
                fld = a.args[0].id
            elif fld in FIELDS:
                self.nodes += 1
                t = Ty("num", FIELDS[fld][0], "h1")
            else:
                raise LangError("timeframe_arg", a, f"{fn}() takes a field or btc(field)")
            if FIELDS[fld][1] is None:
                raise LangError("timeframe_arg", a, f"{fld} cannot be aggregated to a timeframe")
            return Ty("num", t.unit, fn)
        if fn == "funding_mean":
            self.window(args[0], "h1", fn)
            return Ty("num", (), "h1")
        if fn in WINDOW_FUNCS:
            wi = WINDOW_FUNCS[fn]
            data_args = [a for i, a in enumerate(args) if i != wi]
            ts = [self.expr(a, depth + 1) for a in data_args]
            if fn == "lag":
                if ts[0].kind not in ("num", "bool"):
                    raise LangError("type", args[0], "lag needs a series")
                self.window(args[wi], ts[0].tf, fn)
                return ts[0]
            if fn == "hold":
                if any(t.kind != "bool" for t in ts):
                    raise LangError("type", node, "hold takes four boolean series and a horizon")
                tf = _tf_join(*ts)
                self.window(args[wi], tf, fn)
                return Ty("num", (), tf)
            for t, a in zip(ts, data_args):
                self.series(t, a)
            if fn == "corr":
                tf = _tf_join(*ts)
                self.window(args[wi], tf, fn)
                return Ty("num", (), tf)
            if fn == "atr":
                if not (ts[0].unit == ts[1].unit == ts[2].unit and ts[0].tf == ts[1].tf == ts[2].tf):
                    raise LangError("unit", node, "atr needs three series with identical units and timeframe")
                self.window(args[wi], ts[0].tf, fn)
                return Ty("num", ts[0].unit, ts[0].tf)
            t = ts[0]
            self.window(args[wi], t.tf, fn)
            if fn in ("zscore", "rank", "ret", "logret", "rsi", "realised_vol"):
                return Ty("num", (), t.tf)
            return Ty("num", t.unit, t.tf)
        ts = [self.expr(a, depth + 1) for a in args]
        if fn in ("abs", "sign"):
            if ts[0].kind == "bool":
                raise LangError("type", args[0], f"{fn} needs a numeric input")
            if ts[0].kind == "scalar":
                self._scalar_ok(node)
                return SCALAR
            return Ty("num", ts[0].unit if fn == "abs" else (), ts[0].tf)
        if fn in ("sqrt", "log", "exp", "tanh"):
            if ts[0].kind == "bool":
                raise LangError("type", args[0], f"{fn} needs a numeric input")
            self.dimless(ts[0], args[0])
            if ts[0].kind == "scalar":
                self._scalar_ok(node)
                return SCALAR
            return ts[0]
        if fn == "clip":
            self.series(ts[0], args[0])
            self.dimless(ts[0], args[0])
            for t, a in zip(ts[1:], args[1:]):
                if t.kind != "scalar":
                    raise LangError("type", a, "clip bounds must be scalars")
            return ts[0]
        if fn in ("min2", "max2"):
            if any(t.kind == "bool" for t in ts):
                raise LangError("type", node, f"{fn} needs numeric inputs")
            if ts[0].unit != ts[1].unit:
                raise LangError("unit", node, f"{fn} needs identical units")
            if ts[0].kind == "scalar" and ts[1].kind == "scalar":
                self._scalar_ok(node)
                return SCALAR
            return Ty("num", ts[0].unit, _tf_join(*ts))
        if fn == "where":
            if ts[0].kind != "bool":
                raise LangError("type", args[0], "where needs a boolean condition")
            if ts[1].kind == "bool" or ts[2].kind == "bool":
                raise LangError("type", node, "where branches must be numeric")
            if ts[1].unit != ts[2].unit:
                raise LangError("unit", node, "where branches need identical units")
            return Ty("num", ts[1].unit, _tf_join(*ts))
        if fn in CROSS:
            if self.p.kind != "portfolio":
                raise LangError("cross_section_single", node, f"{fn} is only allowed in kind portfolio")
            self.series(ts[0], args[0])
            self.dimless(ts[0], args[0])
            return Ty("num", (), ts[0].tf)
        raise LangError("unknown_function", node, fn)


def _check_body(prog: Program):
    ch = _Checker(prog)
    for name, node in prog.defs:
        t = ch.expr(node, 1)
        ch.types[name] = t
        lit = _literal_value(node)
        if t.kind == "scalar" and lit is None and not ch.has_param(node):
            raise LangError("literal_expression", node, "an expression made only of literals")
    sig = ch.types["signal"]
    if sig.kind != "num" or sig.unit != ():
        raise LangError("signal_type", prog.defs[-1][1], "signal must be a dimensionless numeric series")
    # reachability from signal: unused params and names are rejected
    reach = set()

    def visit(node):
        for n in ast.walk(node):
            if isinstance(n, ast.Name) and n.id in ch.types and n.id not in reach:
                reach.add(n.id)
                visit(dict(prog.defs)[n.id])
    visit(prog.defs[-1][1])
    for name, _ in prog.defs[:-1]:
        if name not in reach:
            raise LangError("name_unused", None, f"{name} is not used by signal")
    used_p = {n.id for name, node in prog.defs if name in reach or name == "signal"
              for n in ast.walk(node) if isinstance(n, ast.Name) and n.id in prog.params}
    for p in prog.params:
        if p not in used_p:
            raise LangError("param_unused", None, f"param {p} is not used by signal")
    prog.types = ch.types
    prog.node_count = ch.nodes
    prog.literals = sorted(ch.literals.items())             # source order


def _fmt_num(v: float, is_int: bool) -> str:
    return str(int(v)) if is_int else repr(float(v))


def _canonicalise(prog: Program):
    defs = dict(prog.defs)
    order = []
    count = [0]

    def c(node) -> str:
        count[0] += 1
        if count[0] > MAX_INLINED_NODES:
            raise LangError("inlined_too_large", node, f"the inlined program exceeds {MAX_INLINED_NODES} nodes")
        lit = _literal_value(node)
        if lit is not None:
            return _fmt_num(*lit)
        if isinstance(node, ast.Name):
            n = node.id
            if n in prog.params:
                if n not in order:
                    order.append(n)
                return f"${order.index(n)}"
            if n in defs:
                return c(defs[n])
            return n
        if isinstance(node, ast.BinOp):
            op = {ast.Add: "+", ast.Sub: "-", ast.Mult: "*", ast.Div: "/"}[type(node.op)]
            return f"({c(node.left)}{op}{c(node.right)})"
        if isinstance(node, ast.UnaryOp):
            return f"(-{c(node.operand)})" if isinstance(node.op, ast.USub) else f"not({c(node.operand)})"
        if isinstance(node, ast.BoolOp):
            op = "and" if isinstance(node.op, ast.And) else "or"
            return f"{op}(" + ",".join(c(v) for v in node.values) + ")"
        if isinstance(node, ast.Compare):
            op = {ast.Lt: "<", ast.Gt: ">", ast.LtE: "<=", ast.GtE: ">="}[type(node.ops[0])]
            return f"({c(node.left)}{op}{c(node.comparators[0])})"
        if isinstance(node, ast.Call):
            return node.func.id + "(" + ",".join(c(a) for a in node.args) + ")"
        raise LangError("node", node, "uncanonicalisable node")

    tree = c(defs["signal"])
    ps = []
    for i, n in enumerate(order):
        p = prog.params[n]
        typ = "int" if p.is_int else "float"
        ps.append(f"${i}:{typ}({_fmt_num(p.default, p.is_int)},{_fmt_num(p.low, p.is_int)},{_fmt_num(p.high, p.is_int)})")
    prog.param_order = order
    prog.canonical = f"kind={prog.kind};signal={tree};params=[{','.join(ps)}]"


def trial_id(prog: Program, semantic_hash: str, research_hash: str) -> str:
    """sha256(canonical + semantic kernel hash + research_hash)[:16]: any change to the kernel's
    semantic files (omr/**, requirements.txt) changes every trial identity."""
    body = prog.canonical + "\n" + semantic_hash + "\n" + research_hash
    return hashlib.sha256(body.encode("ascii")).hexdigest()[:16]


def default_params(prog: Program) -> dict:
    return {n: (int(p.default) if p.is_int else float(p.default)) for n, p in prog.params.items()}


def parse_file(path) -> Program:
    from pathlib import Path
    p = Path(path)
    raw = p.read_bytes()
    if len(raw) > MAX_BYTES:
        raise LangError("too_large", None, f"file exceeds {MAX_BYTES} bytes")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        raise LangError("parse_error", None, "file is not UTF-8")
    if p.suffix != ".omr":
        raise LangError("file_type", None, "programs are .omr files")
    return parse(text, p.stem)
