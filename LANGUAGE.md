# The .omr strategy language (SEMANTICS_VERSION 1)

This file is part of the KERNEL (hashed in `kernel.lock`). A strategy is a small text program,
`strategies/<name>.omr`, that the kernel PARSES and INTERPRETS itself. No strategy code is ever
compiled, executed, evaluated or imported: `omr/lang.py` reads the text with `ast.parse` and walks
the tree with its own checker; `omr/interp.py` evaluates the checked tree with numpy. If this file
and the code disagree, the code is what ran and the disagreement is a kernel bug.

## 1. File

- `strategies/<name>.omr`, UTF-8, at most 16 KB. The file stem must equal the `name` header.
- Python syntax is used only as a notation; almost all of Python is rejected (section 4).
- Comments (`# ...`) and blank lines are free.
- Every rejection names a rule, a line and a column (`parse:<rule>` in `ledger/stage1_log.jsonl`).
  Unparseable text (SyntaxError, RecursionError, MemoryError, ValueError such as a null byte) is
  `parse_error`.

## 2. Statements

Only `name = expression`, with exactly one plain-name target matching `^[a-z_][a-z0-9_]*$`. Each
name is assigned once (`reassigned`), defined before use (`undefined`), and may not shadow a field,
a function, a header key or `param` (`shadowing`).

1. Header, first, each key exactly once, string literals (`header_missing`, `header_value`,
   `header_order`):
   - `name`: `^[a-z0-9_]{3,64}$`, equal to the file stem (`header_name`);
   - `family`: one of trend, meanrev, carry, volatility, relative, flow, other;
   - `kind`: `single` or `portfolio`;
   - `hypothesis`: 10 to 500 printable ASCII characters.
2. Params: `x = param(default, low, high)` with three numeric literals (an optional leading minus);
   an integer param when all three are integer literals. At most 6 params. `low <= default <= high`,
   `low < high`, `default != 0`, and the range contains the whole jitter range 0.8 x default to
   1.2 x default (mirrored for negative defaults); an integer param also needs default - 1 and
   default + 1 inside the range. (`param_form`, `param_literal`, `param_range`,
   `param_zero_default`, `param_jitter_range`, `too_many_params`.)
3. Body: at most 30 assignments (`too_many_statements`), at most 120 expression nodes in total
   (`too_many_nodes`), nesting depth at most 12 (`too_deep`). The LAST statement assigns `signal`
   (`signal_last`), which must be a dimensionless numeric series (`signal_type`). Every body name
   and every param must be used by `signal` (`name_unused`, `param_unused`).

## 3. Expressions

Allowed nodes: names (fields, params, earlier body names), numeric literals, calls to the functions
of section 6 by plain name with positional arguments, binary `+ - * /`, unary minus, `not`,
`and`/`or`, and single comparisons `< > <= >=`. Everything else is rejected: attributes, subscripts,
strings, booleans, None, lambdas, comprehensions, conditional expressions, walrus, starred or keyword
arguments, `** % //` and bit operators, `==` and `!=`, chained comparisons
(`node`, `call`, `operator`, `comparison`, `keywords`, `unknown_function`, `bare_function`).

Literals in the body (`literal_value`, `literal_expression`, `comparison_literal`,
`scalar_comparison`, `window_arg`):
- numbers are integers -10..10 or +-0.5; any other number must be a param;
- the window / lag / count argument of a function is an INTEGER param (with low >= 1) or the
  literal 1; a window param's high is at most 5,000 bars and at most 400 days at the timeframe it is
  used on (funding_mean counts 8 hours per settlement) (`window_param_low`, `window_limit`);
- a literal compared with something must be 0, 0.5 or 1 (or negative);
- an expression made only of literals is rejected; a comparison between two scalars is rejected.

## 4. Types and units

Every value is a BOOL series, a NUMERIC series (with a unit and a timeframe) or a SCALAR (params,
literals; dimensionless). Base units: P (price of the symbol), V (base volume), Q (quote volume),
N (trade count); BTC's own price and volumes are distinct bases (P_btc, V_btc, Q_btc, N_btc).
- `*` and `/` add and subtract unit exponents; `+`, `-`, comparisons, `min2`, `max2` and the two
  branches of `where` need identical units (`unit`).
- `log sqrt exp tanh clip`, the `cs_*` functions and `signal` need a dimensionless input.
- Arithmetic on BOOL, or BOOL where a number is needed (and the reverse) is `type`.
So a signal can never depend on the price LEVEL, the volume level, or the size of BTC relative to
the symbol: rescaling any of them leaves every signal unchanged (tested bit for bit with
power-of-two rescales).

## 5. Fields

Per symbol, on the hourly grid (bar open time, UTC); a value at bar t is known at the close of
bar t, the decision time:

| field | unit | timeframe aggregation |
|---|---|---|
| open, high, low, close | P | first, max, min, last |
| mark_close | P (Binance mark price, as of the last mark bar) | last |
| volume, taker_buy_volume | V | sum |
| quote_volume, taker_buy_quote_volume | Q | sum |
| trades | N | sum |
| funding8h | dimensionless: the latest settled funding rate x 8 / its interval in hours | not aggregatable |
| hour, weekday | dimensionless: hour 0-23 and weekday 0 (Monday) - 6 of the DECISION time (the bar close) | not aggregatable |

There is no bar index, position, bar count, date, year or cumulative quantity: a program cannot
know where it is in history.

## 6. Functions

`n` below is a window/lag/count argument (an integer param or the literal 1). "Needs a full
window": the first n - 1 rows are NaN. Rolling functions act at the timeframe of their input.

Timeframes. `h2 h3 h4 h6 h8 h12 daily weekly` take a FIELD or `btc(field)` and aggregate it
(column above) into complete bins only, anchored at 00:00 UTC (weekly at Monday 00:00 UTC); a bin
missing any hour is dropped. A coarse value is visible from the hourly bar in which its bin
closed (daily: the 23:00 bar). When series of different timeframes meet, each is aligned to the
hourly grid by its last completed value.

| function | definition | result unit |
|---|---|---|
| btc(field) | that field of BTCUSDT on the same hourly index (any field but hour/weekday) | BTC base |
| sma(x, n) | mean of the last n values | of x |
| ema(x, n) | alpha = 2 / (n + 1), seeded with the SMA of the first n consecutive valid values; a NaN input gives NaN and restarts the seeding | of x |
| std(x, n) | standard deviation of the last n values, ddof 1 | of x |
| rmin, rmax, rsum, median (x, n) | rolling min, max, sum, median of the last n values | of x |
| zscore(x, n) | (x - sma(x, n)) / std(x, n); NaN where the std is 0 | dimensionless |
| rank(x, n) | share of the last n values (current included) that are <= the current value, in (0, 1] | dimensionless |
| corr(x, y, n) | rolling covariance / (std x * std y), ddof 1 | dimensionless |
| lag(x, n) | x n rows earlier (BOOL allowed: False before the first) | of x |
| delta(x, n) | x - lag(x, n) | of x |
| ret(x, n) | x / lag(x, n) - 1 | dimensionless |
| logret(x, n) | log(x / lag(x, n)); NaN where the ratio is not positive | dimensionless |
| rsi(x, n) | Wilder RSI (first average = mean of the first n gains/losses, then y += (v - y) / n), CENTRED: (RSI - 50) / 50, in [-1, 1] | dimensionless |
| atr(h, l, c, n) | Wilder average of the true range max(h - l, abs(h - prev c), abs(l - prev c)); three inputs of identical unit and timeframe | of h |
| realised_vol(x, n) | std (ddof 1) of the last n log ratios log(x_t / x_t-1), x sqrt(periods per year of x's timeframe: 8760 hourly ... 365 daily, 365/7 weekly) | dimensionless |
| funding_mean(n) | mean of the last n funding settlements (each as an 8h rate), held until the next settlement | dimensionless |
| abs, sign | elementwise; sign is dimensionless | of x / none |
| sqrt, log, exp, tanh | elementwise on a dimensionless input; invalid -> NaN | dimensionless |
| clip(x, lo, hi) | x clipped to [min(lo, hi), max(lo, hi)]; lo, hi scalars | dimensionless |
| min2(x, y), max2(x, y) | elementwise min / max (NaN propagates) | of x |
| where(c, x, y) | x where the BOOL c is True, else y | of x |
| hold(enter_long, exit_long, enter_short, exit_short) | a state in {-1, 0, +1}, starting flat. Flat: enter_long and not enter_short -> +1; enter_short and not enter_long -> -1. Long: enter_short -> -1, else exit_long -> 0. Short: enter_long -> +1, else exit_short -> 0. | dimensionless |
| cs_mean, cs_demean, cs_rank, cs_scale (x) | portfolio kind only (`cross_section_single`): across the unit's symbols at each row: mean; x - mean; average rank mapped to [-1, 1] (NaN in a row if any value is NaN); x / sum(abs(x)) | dimensionless |

## 7. Semantics

- Each name is computed once, on the whole panel, in statement order.
- Comparisons with NaN are False. Division by zero and any non-finite result give NaN.
- signal -> weights: NaN -> 0, clip to [-1, 1]. Kind single: the program runs on each symbol of the
  unit ALONE, on that symbol's own history (its own warm-up), and weight = signal / number of
  symbols in the unit. Kind portfolio: one panel of the unit's symbols on their common index;
  weights are scaled down by 1 / gross when the gross exceeds 1.
- Execution: the weight at bar t is decided at the close of t and executed at the open of t + 1
  (CONSTITUTION section 4).
- The truncation self-check (stage 1) re-evaluates the program on data cut at 24 random DEV bars
  plus DEV end and requires every row up to each cut to be identical. Every function above is
  causal by construction, so a mismatch is a KERNEL fault, never a property of the program.

## 8. Identity

Canonical form: `kind=<kind>;signal=<signal tree with every body name inlined>;params=[...]`,
params renamed `$0, $1, ...` in order of first use in the inlined tree, each with its type and
(default, low, high). Comments, layout, body names and param names do not change it.
Trial id = sha256(canonical + "\n" + SEMANTICS_VERSION + "\n" + research_hash)[:16]. The kernel
hash is recorded with every trial but is not part of its identity; SEMANTICS_VERSION changes
whenever the meaning of a field, a function, the engine, the costs, the regions, a gate or a
statistic changes (`omr/constants.py`).

## 9. Examples: the five generation-0 baselines

These are `strategies/gen000_*.omr` and the hash-locked kernel copies in `omr/programs/` used by the
calibration. Each reproduces the pre-language Python strategy weight for weight (tested on synthetic
data and on the real DEV frames, at the defaults and at random parameter draws).

```
# trend: SMA cross (single)
fast = param(20, 5, 60)
slow = param(100, 50, 250)
d = daily(close)
signal = sign(sma(d, fast) - sma(d, slow))
```

```
# trend: Donchian breakout with exits (single)
entry = param(20, 10, 60)
exit = param(10, 5, 30)
d = daily(close)
upper_entry = lag(rmax(daily(high), entry), 1)
lower_entry = lag(rmin(daily(low), entry), 1)
upper_exit = lag(rmax(daily(high), exit), 1)
lower_exit = lag(rmin(daily(low), exit), 1)
signal = hold(d > upper_entry, d < lower_exit, d < lower_entry, d > upper_exit)
```

```
# meanrev: 4h RSI bands (single); the Python band 20 (RSI 30/70) is 0.4 on the centred scale
period = param(14, 7, 28)
band = param(0.4, 0.2, 0.6)
r = rsi(h4(close), period)
signal = hold(r < -band, r > 0, r > band, r < 0)
```

```
# trend: volatility-targeted SMA trend (single)
ma_n = param(50, 20, 150)
vol_lookback = param(30, 10, 90)
target_vol = param(0.4, 0.2, 0.8)
d = daily(close)
direction = sign(d - sma(d, ma_n))
size = min2(1, target_vol / realised_vol(d, vol_lookback))
signal = direction * size
```

```
# carry: funding carry (single)
lookback = param(21, 6, 90)
hi = param(0.0003, 0.00015, 0.001)
lo = param(-0.0001, -0.0005, 0.0)
f = funding_mean(lookback)
signal = where(f > hi, -1, where(f < lo, 1, 0))
```

(Each file also carries the four header lines.) Known tie behaviour versus the Python versions:
the Python SMA cross and trend direction mapped an exact tie to -1, `sign` maps it to 0; the vol
target Python version sized a zero volatility as 1, the language gives NaN (flat). Neither case
occurred on the synthetic or real DEV data tested.
