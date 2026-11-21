# The .omr strategy language

This file is part of the KERNEL (its TEXT part, hashed in `kernel.lock`). A strategy is a small text
program, `strategies/<name>.omr`, that the kernel PARSES and INTERPRETS itself. No strategy code is
ever compiled, executed, evaluated or imported: `omr/lang.py` reads the text with `ast.parse` and
walks the tree with its own checker; `omr/interp.py` evaluates the checked tree with numpy and the
fixed-order window kernels of `omr/windows.py`. If this file and the code disagree, the code is what
ran and the disagreement is a kernel bug.

## 1. File

- `strategies/<name>.omr`, UTF-8, at most 16 KB. The file stem must equal the `name` header.
- Python syntax is used only as a notation; almost all of Python is rejected (section 3).
- Comments (`# ...`) and blank lines are free.
- Every rejection names a rule, a line and a column (`parse:<rule>` in `ledger/stage1_log.jsonl`).
  Unparseable text (SyntaxError, RecursionError, MemoryError, ValueError such as a null byte), and
  any other error raised while checking (for example a 400-digit literal), is `parse_error`.

## 2. Statements

Only `name = expression`, with exactly one plain-name target matching `^[a-z_][a-z0-9_]*$`. Each
name is assigned once (`reassigned`), defined before use (`undefined`), and may not shadow a field,
a function, a header key or `param` (`shadowing`).

1. Header, first, each key exactly once, string literals (`header_missing`, `header_value`,
   `header_order`): `name` (`^[a-z0-9_]{3,64}$`, equal to the file stem, `header_name`); `family`
   (trend, meanrev, carry, volatility, relative, flow, other); `kind` (`single` or `portfolio`);
   `hypothesis` (10 to 500 printable ASCII characters). One OPTIONAL key (KP-015): `unit`, `core`
   (the default: the two-coin unit, exactly as before) or `top30` (needs kind `portfolio`;
   `header_unit`); see section 10.
2. Params: `x = param(default, low, high)` with three numeric literals (an optional leading minus);
   an integer param when all three are integer literals. At most 6 params. `low <= default <= high`,
   `low < high`, `default != 0`, and the range contains the whole jitter range 0.8 x default to
   1.2 x default (mirrored for negative defaults); an integer param also needs default - 1 and
   default + 1 inside the range (`param_form`, `param_literal`, `param_range`,
   `param_zero_default`, `param_jitter_range`, `too_many_params`).
3. Body: at most 30 assignments (`too_many_statements`), at most 120 expression nodes in total
   (`too_many_nodes`), nesting depth at most 12 (`too_deep`), at most 4,000 nodes once every body
   name is inlined (`inlined_too_large`). The LAST statement assigns `signal` (`signal_last`), a
   dimensionless numeric series (`signal_type`). Every body name and every param must be used by
   `signal` (`name_unused`, `param_unused`).

## 3. Expressions, literals and the constant probe

Allowed nodes: names (fields, params, earlier body names), numeric literals, calls to the functions
of section 6 by plain name with positional arguments, binary `+ - * /`, unary minus, `not`,
`and`/`or`, and single comparisons `< > <= >=`. Everything else is rejected: attributes, subscripts,
strings, booleans, None, lambdas, comprehensions, conditional expressions, walrus, starred or keyword
arguments, `** % //` and bit operators, `==` and `!=`, chained comparisons (`node`, `call`,
`operator`, `comparison`, `keywords`, `unknown_function`, `bare_function`).

Literals (`literal_value`, `literal_expression`, `scalar_comparison`, `window_arg`,
`too_many_literals`, `nested_unit_window`):
- numbers are integers -10..10 or +-0.5; any other number must be a param;
- the window / lag / count / horizon argument of a function is an INTEGER param (low >= 1) or the
  literal 1. The memory of a window (n rows; 5n for ema; 10n for rsi and atr; one settlement = 8
  hours for funding_mean) is at most 5,000 bars and 400 days at the timeframe it is used on,
  checked at the param's HIGH (`window_param_low`, `window_limit`);
- a call with the literal window 1 may not sit inside another call with the literal window 1 on any
  path of the inlined program (`lag(lag(close, 1), 1)` is a hidden window of 2): a longer fixed lag
  needs an integer param (`nested_unit_window`);
- an expression made only of literals is rejected; a comparison between two scalars is rejected.

**A literal is not a free constant.** Every numeric literal token in the body except the literal 0
(and except window arguments) is an implicit parameter: in the G5 jitter each one is multiplied by
its own U(0.8, 1.2), exactly like a declared param (a name computed once, e.g. `thr = 7`, shares its
jittered value across its uses). At most 8 such literals per program; their number is recorded as
`n_literals` with every trial.

**The constant probe.** At parse time, with the default params, every NUMERIC series node of the
program is evaluated on a fixed synthetic probe panel (two years of hourly bars for two symbols and
for BTC, fixed seed, with trends, volatility regimes, swinging funding and missing mark bars;
`omr/probe.py`). On the node's known rows: no known row -> `probe_undefined` (a warm-up longer than
two years); no finite value -> `constant_subexpression`; constancy is judged on the FINITE values
only (`hour / hour`, NaN once a day, is still the constant 1); a series that is exactly 0 everywhere
is ACCEPTED (harmless, and a rare-event indicator is 0 on the panel); a series that is the same
NON-ZERO number everywhere is rejected (`constant_subexpression`) UNLESS that number moves when the
program's literals and non-window params are jittered (3 fixed-seed draws, window params kept at
their defaults: `sma(hour, n)` at n = 24 is exactly 11.5 and stays rejected). Boolean nodes are not
probed. An exception while probing is `probe_fault` (a kernel bug, not a syntax error).

What the probe catches: EXACT constants built without literals (`close / close`, `volume / volume`,
`hour / hour`, `rank(x, 1)`, `sign(close * 2)`, a hold whose entry is always true). What it does NOT
catch: NEAR-constants (`mark_close / close`, `sma(hour, 25)`, sums of such ratios used as a scale)
and thresholds hidden by multiplying both sides of a comparison by the same series. These are
deliberate and visible in the text; they are left to the coordinator's source read before any
counted submission (KERNEL_PROPOSALS KP-010).

## 4. Types and units

Every value is a BOOL series, a NUMERIC series (with a unit and a timeframe) or a SCALAR (params,
literals; dimensionless). Base units: P (price of the symbol), V (base volume), N (trade count); a
quote volume is price x base volume (P V), so `rsum(quote_volume, n) / rsum(volume, n)` (a VWAP) has
the unit of price and compares with `close`. BTC's own quantities have distinct bases (P_btc, V_btc,
N_btc).
- `*` and `/` add and subtract unit exponents; `+`, `-`, comparisons, `min2`, `max2` and the two
  branches of `where` need identical units (`unit`).
- `log sqrt exp tanh clip`, the `cs_*` functions and `signal` need a dimensionless input.
- Arithmetic on BOOL, or BOOL where a number is needed (and the reverse) is `type`.
So a signal cannot depend on the price LEVEL, the volume level, the trade-count level or the size of
BTC relative to the symbol: rescaling price by p, base volume by v (quote volumes by p x v) and trade
counts by n, per symbol, leaves every signal unchanged - bit-exact for power-of-two factors (tested
on 220 random programs) and otherwise exact up to floating-point ties.

## 5. Fields and the KNOWN channel

Per symbol, on the hourly grid (bar open time, UTC); a value at bar t is known at the close of bar t,
the decision time. Every series carries a VALUE and a KNOWN flag per row.

| field | unit | timeframe aggregation | known where |
|---|---|---|---|
| open, high, low, close | P | first, max, min, last | the bar exists |
| mark_close | P (Binance mark price): the close of the LAST mark bar at or before the row, from the frame's own mark rows | last | that bar is at most 6 hours old (MARK_MAX_STALE_HOURS) |
| index_close | P (Binance index price, KP-015): the close of the LAST index-price bar at or before the row; basis = `(close - index_close) / index_close` | last | that bar is at most 6 hours old (INDEX_MAX_STALE_HOURS) |
| volume, taker_buy_volume | V | sum | the bar exists |
| quote_volume, taker_buy_quote_volume | P V | sum | the bar exists |
| trades | N | sum | the bar exists |
| funding8h | dimensionless: the latest settled funding rate x 8 / its interval in hours | not aggregatable | that settlement is at most 2 x min(its interval, 8) hours old (KP-015 U7, every unit; as of each row from the full funding table) |
| hour, weekday | dimensionless: hour 0-23 and weekday 0 (Monday) - 6 of the DECISION time | not aggregatable | always |

There is no bar index, position, bar count, date, year or cumulative quantity.

## 6. Functions

`n` is a window / lag / count argument (an integer param or the literal 1). Every windowed value at
row t is computed from ITS OWN rows only, in a fixed order (oldest first, plain sequential sums,
two-pass variances); a window containing a NaN VALUE gives NaN. Rolling functions act at the
timeframe of their input. KNOWN: a windowed result is known only where its input is known on EVERY
row of its window (the rows listed below).

Timeframes. `h2 h3 h4 h6 h8 h12 daily weekly` take a FIELD or `btc(field)` and aggregate it into
complete bins only, anchored at 00:00 UTC (weekly at Monday 00:00 UTC). A bin is known only if it is
complete and every hour in it is known. A coarse value is visible from the hourly bar in which its
bin closed (daily: the 23:00 bar). Series of different timeframes meet on the hourly grid, each by
its last completed bar (value and known).

| function | definition (rows of the window) | result unit |
|---|---|---|
| btc(field) | that field of BTCUSDT on the same hourly index (not hour/weekday); known where the BTC row exists | BTC base |
| sma, std, rmin, rmax, rsum, median (x, n) | mean, std (ddof 1), min, max, sum, median of the last n values | of x |
| zscore(x, n) | (x - mean) / std over the last n values; NaN where the std is 0 | dimensionless |
| rank(x, n) | share of the last n values (current included) that are <= the current value, in (0, 1] | dimensionless |
| ema(x, n) | FINITE: the weighted mean of the last m = 5n values, weight (1 - 2/(n+1))^k for the value k rows back, weights normalised | of x |
| corr(x, y, n) | covariance / (std x * std y) over the last n rows, ddof 1, two-pass | dimensionless |
| lag(x, n) | x n rows earlier (BOOL allowed); window = rows t-n .. t | of x |
| delta, ret, logret (x, n) | x - lag(x, n); x / lag(x, n) - 1; log of that ratio (NaN if not positive) | of x / none / none |
| rsi(x, n) | FINITE, centred: (G - L) / (G + L) over the last m = 10n changes (rows t-m .. t), G and L the sums of gains and losses with weight (1 - 1/n)^k for the change k rows back; NaN when G + L = 0. Equal to (RSI - 50) / 50 for Wilder's smoothing truncated at m changes | dimensionless |
| atr(h, l, c, n) | FINITE: the same weights over the last m = 10n true ranges max(h - l, abs(h - prev c), abs(l - prev c)) (rows t-m .. t), normalised; three inputs of identical unit and timeframe | of h |
| realised_vol(x, n) | std (ddof 1, two-pass) of the last n log ratios log(x_t / x_t-1) (rows t-n .. t) x sqrt(periods per year of x's timeframe: 8760 hourly ... 365 daily, 365/7 weekly) | dimensionless |
| funding_mean(n) | mean of the last n funding settlements (each as an 8h rate), held until the next; known only when those n settlements all fall inside the last 8n hours (bounded in time like every other function; KP-015 S1) | dimensionless |
| hold(enter_long, exit_long, enter_short, exit_short, h) | WINDOWED: the state in {-1, 0, +1} reached by running the transition rules FROM FLAT over rows t-h+1 .. t, recomputed for every t (no phase anchored anywhere). From flat: enter_long and not enter_short -> +1; enter_short and not enter_long -> -1. Long: enter_short -> -1, else exit_long -> 0. Short: enter_long -> +1, else exit_short -> 0. Known only where all four inputs are known on all h rows. It equals the unbounded state machine whenever a position re-synchronises within h bars | dimensionless |
| abs, sign | elementwise; sign is dimensionless | of x / none |
| sqrt, log, exp, tanh | elementwise on a dimensionless input; invalid -> NaN | dimensionless |
| clip(x, lo, hi) | x clipped to [min(lo, hi), max(lo, hi)]; lo, hi scalars | dimensionless |
| min2(x, y), max2(x, y) | elementwise min / max (NaN propagates) | of x |
| where(c, x, y) | x where c is True, else y; known only where c AND BOTH branches are known | of x |
| cs_mean, cs_demean, cs_rank, cs_scale (x) | portfolio only (`cross_section_single`): across the unit's symbols at each row: mean; x - mean; average rank mapped to [-1, 1]; x / sum(abs(x)); core unit: known only where every symbol is known in that row (unit top30: section 10) | dimensionless |

## 7. Semantics: locality by construction

1. **Values.** Each name is computed once, on the whole panel, in statement order. Division by zero
   and any non-finite result give NaN; a comparison with a NaN VALUE is False; where() selects by its
   condition. NaN values are facts about known data.
2. **Knownness** is about history and is kept apart from values. An elementwise result is known only
   where every input is known; a windowed result only where its input is known on every row of its
   window; a timeframe bar only if complete with every hour known; where() only where its condition
   and both branches are known; hold() only where its four inputs are known on all h rows; cs_* only
   where every symbol is known. A row that is not known has NO definite value anywhere: comparisons,
   and/or/not, where and hold cannot turn it into True, False or a number. A program cannot observe
   the known channel.
3. **Weights.** signal -> weight: 0 where the signal is not known or its value is NaN; then the
   signal is CLIPPED to [-1, 1] (never failed). Kind single: the program runs on each symbol of the
   unit ALONE, on that symbol's own history, and weight = signal / number of symbols in the unit.
   Kind portfolio: one panel of the unit's symbols on their common index; weights are SCALED by
   1 / gross when the gross exceeds 1. The weight at bar t is executed at the open of t + 1.
4. **Uniform warm-up.** So a program is flat until every subexpression has its history, and nothing
   in it can switch on later than anything else.
5. **The guarantee.** Every definite value at row t is a function of a bounded trailing window of
   data, computed in a fixed order from that window alone. A program therefore cannot derive where
   it is in history from the frame: not from a first-bar impulse, an infinite-memory recursion, a
   state machine that starts flat, a warm-up that ends on a chosen date, or the date a dataset
   begins. The kernel checks this on every trial: the truncation self-check (rows up to 24 random
   cuts and DEV end identical) and the start-cut self-check (6 cuts over the first 60% of the DEV
   frame, 3 more over the full frame in stage 2: every frame, BTC included, loses its rows before
   the cut; wherever the cut run is known, the full run is known and bit-identical). A mismatch is a
   KERNEL fault. **The limit:** a program can still react to real market EVENTS it remembers (a
   pattern in the prices themselves), and its author can choose structure and parameters from
   remembered history (KERNEL_PROPOSALS KP-010). Only forward results judge that.

## 8. Identity

Canonical form: `kind=<kind>;signal=<signal tree with every body name inlined>;params=[...]`
(a unit other than core is prefixed: `unit=top30;kind=...`),
params renamed `$0, $1, ...` in order of first use in the inlined tree, each with its type and
(default, low, high). Comments, layout, body names and param names do not change it. Trial id =
sha256(canonical + "\n" + SEMANTIC kernel hash + "\n" + research_hash)[:16]: any change to the code,
constants or kernel programs that run (omr/**, requirements.txt) changes every trial id; a change to
documents or tests only (the TEXT part) does not.

## 9. Examples: the five generation-0 baselines

These are `strategies/gen000_*.omr` and the hash-locked kernel copies in `omr/programs/` used by the
calibration (each file also carries the four header lines). Each reproduces an independent naive
implementation of these definitions weight for weight (tests/ref_gen0.py). Against the
pre-language Python strategies: SMA cross and funding carry are bit-identical; the vol-target trend
differs only by floating-point rounding (fixed-order sums, at most 1e-12 in a weight); Donchian and
RSI changed by rule (the windowed hold, the finite RSI).

```
# trend: SMA cross (single)
fast = param(20, 5, 60)
slow = param(100, 50, 250)
d = daily(close)
signal = sign(sma(d, fast) - sma(d, slow))
```

```
# trend: Donchian breakout with exits (single); on real DEV data a horizon of 60 days or more never
# differs from an unbounded state machine
entry = param(20, 10, 60)
exit = param(10, 5, 30)
horizon = param(90, 60, 180)
d = daily(close)
upper_entry = lag(rmax(daily(high), entry), 1)
lower_entry = lag(rmin(daily(low), entry), 1)
upper_exit = lag(rmax(daily(high), exit), 1)
lower_exit = lag(rmin(daily(low), exit), 1)
signal = hold(d > upper_entry, d < lower_exit, d < lower_entry, d > upper_exit, horizon)
```

```
# meanrev: 4h RSI bands (single); band 0.4 = RSI 30 / 70; finite RSI over 10 x period changes
period = param(14, 7, 28)
band = param(0.4, 0.2, 0.6)
horizon = param(84, 60, 180)
r = rsi(h4(close), period)
signal = hold(r < -band, r > 0, r > band, r < 0, horizon)
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

Known tie behaviour versus the Python versions: the Python SMA cross and trend direction mapped an
exact tie to -1, `sign` maps it to 0; the Python vol target sized a zero volatility as 1, the
language gives NaN (flat). Neither occurred on the synthetic or real DEV data tested.

## 10. Units: core and top30 (KP-015)

`unit = "core"` (or no `unit` key) is the two-coin unit of every section above, unchanged. `unit =
"top30"` trades a point-in-time cross-section of USDT perpetuals:
- MEMBERSHIP (omr/universe.py): reconstituted at the first hour of each calendar month (UTC) from bars
  strictly before it (it reads the 97 days before the month). Eligible: a crypto perpetual
  (data/symbols.json; never a TradFi, index or other contract) whose first active bar (a bar with trades)
  is at least 90 days before the month with no run of 7 or more consecutive days without an active bar
  inside those 90 days (a relisting or a delisting gap restarts the seasoning; a shorter archive hole does
  not), and that was active on at least 95% of the previous 720 hours. Ranked by the median
  daily quote volume of the previous 90 days: `top30` = ranks 1 to 30 (G8 uses `next30` = ranks 31 to
  60). A month with fewer than 10 such members has no unit: every signal is unknown (flat).
- USABLE BARS (S3): a bar with trades is usable; a bar present with zero trades is usable (fields as
  recorded) while the run of consecutive bars without trades ending at it is at most 24 (counted
  backwards only); from the 25th on, and for a bar absent from the archive, the fields are unknown.
  Membership counts bars with trades only.
- IN PLAY (TRADABLE): a symbol is in play at a row when it is a member for the month containing the
  row's decision time (its close), its bar at that row is usable, and its latest funding settlement is no
  older than twice its own funding interval, capped at 8 hours (2 x min(interval, 8); a symbol the engine
  cannot charge funding on is not held). funding8h uses the same freshness in every unit.
- `cs_*` (S2, U3) compute across the symbols that are in play AND whose input is known AND finite at that
  row; when at least 10 such symbols exist the result is known for every in-play symbol with a known input
  (a known but non-finite input, such as a 0/0, gives a known NaN, so one symbol cannot flatten the row),
  otherwise it is unknown for everyone. A symbol whose
  window holds a hole simply drops out of the cross-section until its window is clean. The final signal of a
  symbol not in play is unknown (weight 0). A `cs_*` over a
  timeframe series uses the in-play symbols of the hour at which each of its bars becomes visible. The
  portfolio weight rule (clip to [-1, 1], scale down when gross exceeds 1) applies across the unit (gross
  summed sequentially in symbol-name order).
- LOOKBACK (D3, `lookback_exceeds_seasoning`): the program's total lookback, the longest chain of
  windows through the inlined tree with every window param at its `high` bound (ema 5n - 1, rsi / atr
  10n, lags and realised_vol n, other windows n - 1 extra rows; leaves: an hourly field, hour and
  weekday 1, mark_close and index_close 7 (their 6-hour staleness), funding8h 17 (its 16-hour
  freshness), btc(f) the same as f;
  a timeframe of h hours over a leaf of l hours 2h - 2 + l (its bin, the wait for the next bin's close and
  the leaf's own reach); rows of a timeframe series count as that many hours; funding_mean(n) 8n hours),
  must not exceed 90 days (2,160 hours). It is a true upper bound of a value's memory: from a frame's
  first row + lookback - 1 on, a value equals the whole run's (tests/test_blocks.py). Every program's
  lookback is recorded in its trial row (`lookback_hours`), in both units.
- Gates: CONSTITUTION section 13. G6 in top30 is a paired lag test: the program's weights are compared
  with its OWN weights from k hours earlier (k from 30 days to half the VAL length; for the first k rows of
  VAL the earlier weights come from before VAL start), traded at the same times; both books hold the same
  names on every row (tradable now and in play at the earlier row), each re-centred to the net of the
  row it came from, flat under 10 names. No row after the decision is used: a later row would choose the
  names by future membership. Limits (CONSTITUTION section 13; audits/AUDIT_LOG.md round 7): positions in
  names that entered the unit less than k hours before are in neither book, so an edge in recent entrants
  is not credited and a slow strategy has less power than in the core unit; and each book pays its own
  costs, which distorts the comparison for a book whose costs are large next to its volatility. In unit
  top30 G6 fails a program whose weights are still correlated above 0.5 with its own weights one or more
  lag steps (about 26 days) earlier, so a signal that is one slow average over most of the 90-day lookback
  will usually be too slow (CONSTITUTION section 13). The threshold applied is the program's own unit's
  (sealed per unit).
- Turnover: a book that replaces itself every day trades twice its gross a day and pays about 0.9 of its
  gross per year in costs (2 x 12.5 bps x 365), about 1.8 at the doubled costs of G4. To pass G4 it would
  have to earn more than that before costs, which no realistic edge does. Design top30 books for holding
  periods of days to weeks (the unit's timing test is calibrated for the oracle speeds of CONSTITUTION
  section 13, 5 and 20 days).
- Costs: 12.5 bps per side on every symbol. A position in a symbol whose next bar is missing is closed
  at its last usable close (the close of its previous usable bar, which can be a zero-trade bar with a
  frozen price) with that cost; a symbol leaving the unit gets weight 0.
- Locality: the truncation and start-cut self-checks run on the universe panel; every RUN (the base, a
  truncation cut, a start cut, a jitter variant) computes its membership once from its own rows (a cut can
  only make the unit unknown, never different); stage 1 adds one start cut that removes the first 31 hours
  of a panel symbol's history. Every function is
  bounded in time (funding_mean and funding8h included), and the membership's 97-day read window keeps a cut run
  unknown longer than the 90-day lookback limit, so a cut cannot change the set a `cs_*` sees.
- Blocks (S4, fix pass 3): the evaluator runs a top30 program in blocks of six calendar months (G8's
  next30 in three-month blocks). A block is only a computation chunk of a run: it takes its in-play mask
  from the run's one membership, holds the members of every month its evaluated rows touch, and is
  evaluated from 97 days (the 90-day limit plus a week) before the first hour of the month of its first
  row; the stitched result is bit-identical to the whole panel. Self-check `block_overlap` (a kernel
  fault): from a block's first evaluated row + lookback_hours to the row before the block, its result
  must equal the previous block's bit for bit; it fires when a program's true memory exceeds its
  recorded lookback.
