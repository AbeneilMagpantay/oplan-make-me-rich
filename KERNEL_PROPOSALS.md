# KERNEL PROPOSALS

Requests for kernel changes, for the human to decide. The research loop appends here; it never
edits the kernel. Format per entry: date, problem, evidence, proposed change, expected effect on pass
rates, status.

## 2026-11-18 (build session) KP-001 Liquidation check on mark price, not last-trade wicks

- Problem: the genesis liquidation check used last-trade bar high/low; the ETHUSDT perp printed a
  high of 323.00 against an open of 95.73 on 2020-03-13 02:00 UTC (mark high 119.47).
- Change made: `mark_klines` admitted; the liquidation check uses mark high/low relative to the mark
  open of the same bar, last-price fallback where a bar has no mark data; 2.5% rule kept.
- Status: CLOSED 2026-11-18 (approved by the coordinator; pre-genesis, zero trials evaluated).

## 2026-11-18 (build session) KP-002 Model the exchange-side protective stop

- Problem: CONSTITUTION section 11 requires a reduce-only protective stop on every live position;
  the v1 engine does not model it.
- Proposed change: kernel v2 engine option for a stop at a fixed distance, with fills at the stop
  level or the bar open if gapped through.
- Status: open (required before any live use).

## 2026-11-18 (build session) KP-003 Confirm the denominator of the null pass rate

- Problem: the threshold rule's denominator was ambiguous (counted pairs vs all pairs) while
  ~25-29% of null pairs failed activity in stage 2.
- Status: CLOSED 2026-11-19 by the FINAL PRE-GENESIS ORDER: the denominator is SUBMITTED pairs.
  Activity is now a free stage-1 filter (`activity_dev`), a pair is submitted only if one of its 20
  draws passes stage 1, and the rule is applied in code by the seal (CONSTITUTION section 8).

## 2026-11-18 (build session) KP-004 Mark-bar quality and maintenance tiers

- Problem: about 3,000 mark bars per symbol have fewer than 3,600 sampled seconds (partial
  sampling), and Binance applies tiered maintenance margins by position size; v1 uses a flat 2.5%
  and treats partial mark bars as complete.
- Proposed change: report partial bars as a separate class, and model the maintenance tier for the
  deploy-scale position size before any live use.
- Status: open (low priority at gross <= 1).

## 2026-11-18 (build session) KP-005 Calibrate G8

- Problem: synthetic worlds carry only the core symbols, so G8 is never exercised in calibration;
  null pass rates are upper bounds and G8's false-veto rate on real edges is unknown.
- Proposed change: extend null A/B worlds to the extended perps (same day blocks and coins) and
  report the G8 pass rate of the oracles.
- Status: open.

## 2026-11-18 (build session) KP-006 Position-encoded calendars

- Problem: a Python strategy could encode remembered history through bar positions (`len(bars)`,
  cumulative counters).
- Status: CLOSED 2026-11-19: no strategy code exists. The language has no index, position, bar
  count, date or cumulative quantity; every window is bounded (<= 5,000 bars, <= 400 days); a
  program's only time inputs are hour and weekday of the decision time. Property tests check
  identical signals under whole-week time shifts on 220 random programs. (Remembered history
  through the CHOICE of structure and parameters remains: KP-010.)

## 2026-11-18 (build session) KP-007 Attribute allowlist is name-based

- Status: CLOSED 2026-11-19: the attribute allowlist and the Python parser it guarded are deleted.
  `.omr` programs have no attributes at all (an attribute is rejected as `node` or `call`); every
  audit payload is a rejected-text regression test (tests/test_exploits.py).

## 2026-11-18 (build session) KP-008 Outdated docstring in omr/strategy_api.py

- Status: CLOSED 2026-11-19: `omr/strategy_api.py` is deleted (with the child runner, the allowlist
  and the Python strategies; archived in `archive/kernel_2317921c_python_sandbox.zip`).

## 2026-11-19 (build session) KP-009 The ledger head needs an external anchor

- Problem: `ledger/HEAD.json` anchors each hash chain's row count and head hash, but it lives in the
  same folder. Anyone with write access can rewrite a chain from any row and regenerate HEAD.json
  consistently; truncating trials.jsonl and HEAD.json together would silently lower M.
- Addressed operationally (2026-11-19): the project is its own git repository (branch main, private
  remote on GitHub). `ledger/` (all chains and HEAD.json), `kernel.lock`, `data/manifest.json` and
  `data/validation.json` are tracked; the coordinator commits and pushes at every gate, so each
  pushed commit is an anchor of the chain heads outside the folder. A rewrite of a chain after a push
  shows up as a diff against the remote. Research sessions make no git writes.
- Remaining (optional kernel change): `ledger verify` could compare HEAD.json with the latest pushed
  commit itself instead of relying on the coordinator's review of the diff.
- Status: addressed operationally by the coordinator's commits; kernel-side check open.

## 2026-11-19 (build session) KP-011 FIX PASS 4 (coordinator review, pre-genesis, zero trials)

- C1 literals are jittered in G5 like params (at most 8, `too_many_literals`, `n_literals` recorded;
  `comparison_literal` removed). C2 quote volumes have the unit price x base volume. C3 the VAL
  access log is never redirected; temporary-ledger trials that read real VAL bars are logged in it
  (`temp_ledger_trial`). C4 no time-resolved VAL performance is stored (per-year and G7 bucket
  returns only for periods ending by DEV end). C5 any non-LangError inside the parser is
  `parse_error`. C6 documents.
- Status: implemented and tested; takes effect at the next re-key (with the independent audit's
  findings), followed by calibration on the locked kernel and the seal.

## 2026-11-19 (after generation 0) KP-014 LANGUAGE.md: more of what the constant probe does not catch, and honest restatements

- Source: the fifth audit (commit d2c2d4f), two low findings, TEXT ONLY.
- Problem: LANGUAGE.md lists near-constants and hidden thresholds as left to the source read but
  omits forms the audit found: small-offset calendar averages such as `sma(hour + 0.5, n)` at
  n = 24 (exactly 12 on every row, but the literal moves it, so the probe accepts it);
  rounding-noise constants such as `sma(hour + e, n) - e` (not bit-exact, so not "constant"); a sign
  cliff tuned to the probe panel's fixed seed; and `1 / (1 + k)` with a tiny param (a near-constant
  scale). It also does not say which HONEST forms the probe rejects and how to restate them:
  `open / lag(close, 1) - 1` is exactly 0 wherever the synthetic open equals the previous close and
  can be restated as `(open - lag(close, 1)) / close`; `exp(where(rare, 1, 0))` and
  `rank(where(rare, 1, 0), n)` are non-zero constants on the panel when the event never fires and can
  be restated with the event series itself (`where(rare, 1, 0)`, a zero series, is accepted) or a
  jittered scale.
- Proposed change: add both lists to LANGUAGE.md section 3 (no code change).
- Expected effect: none on any result; a text-only re-key keeps the seal and every trial id.
- Status: open - needs the human's approval now that trials exist (text-only re-key).

## 2026-11-19 (build session) KP-013 FIX PASS 6 (fourth audit READY; coordinator's read)

- P1 constant probe refined: constancy on finite values only; an all-zero series accepted; a
  non-zero constant rejected unless jittering the literals and non-window params moves it (3
  fixed-seed draws, window params at their defaults). Closes `hour / hour` (NaN once a day) and stops
  rejecting honest rare-event rules (`where(z > 4, ...)`, `sma(where(rare, 1, 0), n)`).
- P2 mark_close = the close of the last mark bar at or before the row, known while at most 6 hours old
  (MARK_MAX_STALE_HOURS); computed in the interpreter from the frame's own mark rows.
- P3 an exception while probing is `probe_fault` with the exception type (uncounted), not
  `parse_error`.
- P4 calibration: 300 worlds per null, 200 per oracle configuration (the rule is unchanged).
- P5 documents: what the probe catches and what it leaves to the source read; when a seal counts;
  PLAN/REPORT existence only; a custom provider reading the stored files is a route the kernel cannot
  prevent.
- Status: implemented and tested; one semantic re-key, calibration, seal.

## 2026-11-19 (build session) KP-012 FIX PASS 5 (independent audit of c891061, pre-genesis, zero trials)

- CRITICAL (a program could read its own bar position: a first-bar impulse fed into the unbounded
  ema gave the bar index to 1e-9; a remembered-calendar program reached Tier 1 on a synthetic
  world): fixed by LOCALITY BY CONSTRUCTION - a known channel next to every value with strict
  propagation (K1), values kept apart (K2), finite memory for ema / rsi / atr (K3), a windowed
  five-argument hold (K4), fixed-order window arithmetic (K5, omr/windows.py), a start-cut
  self-check in stage 1 and stage 2 (K6), and regression tests for the clock, a hold latch and two
  warm-ups (K7).
- HIGH (constants and hidden windows without literals): the constant probe at parse time
  (`constant_subexpression`, `probe_undefined`) and `nested_unit_window`.
- MEDIUM: two-part lock with the seal and the trial identity bound to the SEMANTIC hash (M1);
  ledger/calibration_log.jsonl and seal refusing unlogged or hand-edited artifacts (M2); a fully
  synthetic calibration dry run (M3); generation N >= 1 needs REPORT.md of N - 1, and the
  CONSTITUTION says the cap paces work while M protects against many attempts (M4); calibration
  screens draws with the activity rule and runs the self-checks only on the submitted draw (M5).
- LOW: wording on scale invariance and on clipping / scaling by rule.
- Baselines: Donchian and RSI got a hold horizon (90 days, 84 4h bars; on real DEV a horizon of 60
  or more never binds) and the RSI uses the finite definition.
- Status: implemented and tested; one re-key, then calibration and seal.

## 2026-11-19 (build session) KP-010 Remembered history through choice of structure and params

- Problem: the language removes dates, positions and price levels, but the researcher (an LLM
  trained on market history to about mid-2026) can still choose a structure and default params that
  fit remembered VAL-period behaviour (e.g. a lookback that happens to time 2022-2024 regimes). No
  static or dynamic check can see this; G5 (jitter) and G6 (timing permutation) only weaken it.
- Related: since FIX PASS 4 every body literal other than 0 is jittered in G5 like a param, and
  since FIX PASS 5 the constant probe rejects numeric nodes that are constant on a synthetic probe
  panel (`one = close / close`, `rank(x, 1)`). A constant that the probe panel does not expose (for
  example one that varies only on synthetic data) still escapes the jitter, and the probe does not
  catch NEAR-constants (`mark_close / close`, `sma(hour, 25)`, sums of such ratios used as a scale)
  or thresholds hidden by multiplying both sides of a comparison by the same series (FIX PASS 6). That is deliberate
  evasion, not an honest mistake: the source audit of each generation's programs catches it, and a
  program found doing it is reported in the generation REPORT. Since FIX PASS 5 a program also cannot
  read its position in history from the frame (locality, KP-012); it can still react to market
  events its author remembers.
- Proposed change: none in the kernel. Keep forward results as the judge (CONSTITUTION sections 11
  and 12); consider requiring forward days before pool-to-live promotion to scale with the number of
  counted trials of the family.
- Status: open (documentation of a residual risk).

## 2026-11-19 (coordinator, after generation 1) KP-015 Widen the tradable universe and add futures-native data

- Problem: after five counted trials on two coins, every rule with a positive VAL Sharpe was
  long-biased and failed on timing (LESSONS 8 and 9), and the one market-neutral idea had only two
  instruments to choose between (LESSONS 10). Rules that do not depend on the market's direction need
  a cross-section, and questions about crowding and positioning need data the kernel does not have.
- Proposed change (a semantic re-key, a new calibration and seal, and an independent audit before
  any trial):
  1. a point-in-time universe of USDT perpetuals as a second tradable unit for kind portfolio:
     membership decided only from data available at the time, delisted contracts included, with
     listing-age and liquidity filters;
  2. futures-native datasets under the admission rules (history covering DEV and VAL, a
     knowable-as-of timestamp, the same source available live): open interest, long/short account
     ratios, and basis against the index.
- Effect: every earlier trial identity is orphaned (the five trials stay counted in M under the old
  semantic hash); the role of G8 changes once the extended coins are tradable; the calibration needs
  null worlds for the wider unit.
- Feasibility study, 2026-11-19 (`notes/kp015_feasibility.md`, tables in `notes/kp015_tables_v2.txt`):
  - Open interest and long/short ratios are NOT admissible as research data: history starts
    2021-12 for nine of the ten symbols (23% of DEV), and the archive was backfilled and rewritten, so
    "not revised after the fact" cannot be shown. They can only be used forward, from copies the
    project stores itself with first-seen hashes.
  - Index price (basis) is admissible: complete from each listing month, and served live.
  - A point-in-time universe is feasible, but membership must come from trading activity in the
    klines: delisted contracts are padded with frozen, zero-volume files, 237 TradFi perpetuals share
    the naming, and names are reused and relisted. Only three contracts existed before September 2020.
- Revised proposal: (1) a point-in-time top-K unit for kind portfolio, built from kline activity with a
  seasoning period and an explicit contract classification; (2) admit the index price as a field;
  (3) do not admit open interest or the ratios, and start storing them now for forward-only use.
- Status: open. On 2026-11-19 the human replied "continue" to the coordinator's recommendation and
  its question whether to go ahead; the coordinator reads that as approval of the direction and will
  state the exact change again before any re-key.
- Build (2026-11-19, working tree only; NOT re-keyed, calibrated or sealed): data/symbols.json and the
  universe download (678 crypto perpetuals, index_klines admitted for all, research hash d1b6ce5b...);
  omr/universe.py (symbol table, activity, membership), omr/upipeline.py (unit top30 pipeline, G8 on
  next30), the universe engine in omr/engine.py, `unit` header, `index_close` and the 90-day lookback
  rule in omr/lang.py, in-play cross-sections in omr/interp.py, omr/ucalibrate.py (written, tested on
  synthetic panels only), a seal over both units, kernel_noise_top30 in the selftest,
  tools/record_metrics.py (forward-only metrics, outside the kernel). The core unit is bit-identical to
  commit b12df97 (tests/test_core_identity.py). Two refinements of the order's text, to be confirmed by
  the audit: a member is IN PLAY only on rows where its bar is active (not merely a member), and
  seasoning is read as "at least one active bar in each of the 91 days before the month" (so a
  relisting, a delisting gap or a missing day restarts it). Next: independent audit of the working
  tree, the human's approval, re-key, both calibrations, seal.
- Fix pass (2026-11-19): R1a seasoning (first active bar >= 90 days before the month, no 7-day run without
  an active bar inside those 90 days); R2 tradable = member + active bar + latest funding settlement no
  older than twice its interval (ICP 9 and TLM 1 member-months out of play in DEV; SOL 3 hours in VAL);
  R3 memory estimate and uncounted `memory_insufficient` refusal, needed columns only, G8 panel first;
  R4 the sandbox relies on per-file hashes at read. R1b (cross-sections over the in-play symbols whose
  input is known, known when >= 10) NOT adopted: a start cut can change that set through funding_mean,
  whose "last n settlements" memory is unbounded (a 150-day funding gap followed by resumption; synthetic
  counterexample). Proposed fix for a ruling: in universe panels funding_mean is known only when its last
  n settlements lie inside its own 8n-hour window (the window D3 already counts); with it, 0 of 40 start
  cuts disagree on every tested case, because the membership's 97-day read window already makes every
  cut run unknown longer than the 90-day lookback limit.
- Fix pass 2 (2026-11-19): S1 adopted in EVERY unit (the core comparison with b12df97 stayed bit-identical
  on the synthetic world and on real DEV); S2 (R1b) adopted, with the counterexample and the hole cases as
  permanent tests; S3: the market-wide hour 2024-10-28 20:00 UTC is 320 rows present with zero trades, so
  zero-trade bars are usable while their zero-trade run is <= 24 (membership still counts trades only); S4:
  six-month blocks, bit-identical to the whole panel for signals, weights, engine output and every gate
  (boundaries inside a hole and inside a member's first month tested).
