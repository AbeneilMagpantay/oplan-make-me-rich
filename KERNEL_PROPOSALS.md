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
- Fix pass 3 (2026-11-20): the coordinator's review found blocks NOT equal to the whole panel for programs
  with a window over a cs_* result (each block recomputed the membership from its own rows, so its warm-up
  was unknown). Now a run has one membership and every block uses it; block panels hold the members of
  every month their evaluated rows touch; the self-check `block_overlap`; lookback_hours counts a leaf's
  staleness under a timeframe and under btc(). Permanent tests in tests/test_blocks.py.
- Fix pass 4 (2026-11-20, audit round 6): G6 in top30 is a paired test on the common names (A_k: the actual
  book on the names tradable now and in play at the source row; S_k: the source row's book on the same
  names; re-centred to the unmasked row's net, flat under 10 names; the plain shift test bit for bit when
  there is no churn); universe calibration worlds keep the REAL rows of every symbol ever in top30 (the
  kernel's own rule reproduces the real membership calendar; only prices are resampled) and run on the
  production block path; cs_* count known AND finite inputs; `data universe` fills archive holes from the
  daily files (checksum required, pinned, revision check); the symbol table is in the research hash and the
  validation fingerprint; top30 programs are probed on 12 in-play symbols; funding8h is known only while
  its settlement is at most 2 x min(interval, 8) hours old in every unit (lookback leaf 17; the in-play
  freshness caps the interval too); sandbox log row before any metric; rekey tolerates an old seal;
  block_overlap_cells recorded. Follow-up rulings: R-A the ten core / extended symbols are hole-filled by
  the same rule (core identity still proved on the same stored data); R-B G6 ties (books within 1e-12 =
  tie, else a 1e-9 Sharpe margin). Open: an equal-weight basket still gets p = 0.52 on a churn panel with
  delistings (A_k's own set drops a delisting name's weight, S_k's does not); A_k's own set = in play at
  the decision row would make every shift a tie. Evidence: notes/kp015_build_evidence.md.
- Fix pass 5 (2026-11-20): G6 in top30 becomes a causal PAIRED LAG test (R-C): the program's own weights k
  hours earlier (k from 30 days to half the VAL length; rows before VAL start for the first k rows) against
  its actual weights, on the names tradable now and in play at the earlier row, each book re-centred to the
  net of the row it came from. It replaces the circular shift of pass 4, whose source rows for the first k
  rows lay in the future (a survivor filter through future membership); with the symmetric own sets an
  equal-weight basket gets p = 1. Universe calibration (R-D): resumable through a partial file bound to the
  kernel, data and protocol; a memory preflight; level 1.5 only; defaults 200 / 100 / 4. R-E: universe null
  funding rates carry a fair sign coin per settlement hour, so no carry can be earned in a null world (the
  core calibration unchanged). R-F: null A draws a month's source days from the days on which every top30
  member of that month is fully active, so the members share one source day. R-G: the hole fill remembers a
  404 only for a day at least a week old, checks every reused daily file against its manifest pin, and
  commits tables and manifest through a journal that the next `python -m omr.data` command completes or
  rolls back. Evidence: notes/kp015_build_evidence.md.
- Fix pass 6 (2026-11-20; audit round 7 first judged 32e32e0 READY, then restated NOT READY after measuring
  Tier-1 power on the real membership structure, where the 1-day oracle fails G4 in 24 of 24 worlds; fix pass 6
  was reviewed READY on the working tree; the coordinator's rulings on the round's items): R-H
  the G6 threshold is decided PER UNIT, each unit by the section-8 rule on its own rows (the core artifact's
  null A pass rate at 0.10 is 2.94%, so under the shared rule one more core pass would have moved both units,
  and top30's rows could tighten the core threshold; the units use different G6 constructions and null
  distributions); both units seal or neither; kernel.lock holds {"core": x, "top30": y}; the evaluator applies
  the program's own unit's threshold. An incomplete unit artifact stops the seal with a reason. The universe
  calibration's partial file carries a sha per line (damaged lines discarded, a torn tail repaired, a task
  stored twice with different results stops), and the oracle phases run first with a power advisory.
  Documented limits of the universe lag test: recent entrants are in neither book, and each book pays its own
  costs. PROTOCOL_VERSION 4. R-I (F8): the universe oracle's speeds are a unit constant, fast = 5 days and
  slow = 20 (the core keeps 1 and 20): at 12.5 bps per side a 1-day oracle with net Sharpe 1.5 cannot pass G4
  at doubled costs (cost drag 3.86 Sharpe units, Tier-1 0 of 24), so the seal would stop with certainty; at 5
  days the drag is 0.93 and Tier-1 18 of 24 (the coordinator's rule: the fastest of 5, 7, 10 days with Tier-1
  at least 0.65 at all thresholds). R-J (F9): the reversal family is now the momentum's mirror on daily bars
  (n from 3 to 20 days), inside the unit's certified holding periods; the former 4-96 hour reversal was
  cost-dominated (VAL Sharpe about -9.7 in a measured null world), could never reach Tier 1 and diluted the null
  pass rate. A malformed unit artifact stops the seal; a sealed threshold must be a grid value. Evidence: notes/kp015_build_evidence.md.
- Fix pass 7 (2026-11-21; audit round 7, addendum X10 judged 4286abf NOT READY, with no false-pass risk: the
  universe calibration would have stopped after its full run; the coordinator's rulings): R-K under null A
  every symbol has ONE expected daily log return in every month, c = its mean over all its fully active source
  days (the set its fallback draws from). X10 found that the monthly pools of R-F are windows of history that
  change with the membership, so every pooled month carried its own cross-section of expected returns (pool
  mean minus whole-period mean: cross-sectional SD about 0.6 a year, correlation between month m and month m-k
  0.77 / 0.48 / 0.24 / 0.13 by lag band); a slow momentum book held the current pool's drift and the paired lag
  test read it as timing. Momentum under null A reached Tier 1 in 5 / 6 / 8 of 12 worlds at 0.025 / 0.05 /
  0.10 (null B 0 / 1 / 1), the pooled null A pass rate was 13.9% / 16.7% / 22.2% of submitted pairs, and no
  threshold could qualify. Now a world day that uses the shared source day drawn from a set Q (the month's pool,
  or the whole period) has every active row's open / previous close ratio multiplied by exp((c - the symbol's
  mean over Q's fully active days) / 24); a fallback day gets nothing; high, low and close relative to the open,
  the source days drawn, funding and null B are unchanged (null B worlds byte-identical to fix pass 6);
  hour-of-day means are deliberately not equalised. R-L: in addition to the pooled 3%, no single family's null
  pass rate (its Tier-1 passes / its own submitted pairs) may exceed FAMILY_PASS_MAX = 0.06 under either null
  at the chosen threshold, in both units. In the top30 null worlds 13 of the 36 submitted pairs per null had a
  positive DEV Sharpe (12 momentum, 1 carry); reversal and carry cannot pass there, so the pooled bound alone
  allowed momentum 9%. 0.06 is the conventional 5% level plus a sampling allowance (200 worlds per null: a
  true 4.5% is accepted in about 88% of runs per null, 9% refused in about 91%). It can only lower a threshold;
  on the stored core rows (7446278556aadd8f) it changes nothing (worst family 14 of 300 = 4.67% at 0.10, under
  null A). The artifacts store per threshold the family rates and the rate over DEV-positive pairs (KP-016,
  information only); a STOP names, for each threshold, the bound and the null that failed; the seal's refusal
  shows the family rates. omr/ucalibrate.py PROTOCOL_VERSION 5, omr/calibrate.py PROTOCOL_VERSION 4.
  Evidence: notes/kp015_build_evidence.md.
- Fix pass 8 (2026-11-21; audit round 7, addendum X11 judged 58ba59e NOT READY, with no code defect and no
  false-pass risk; the coordinator's rulings): R-M replaces R-K. In both top30 nulls every symbol has ONE
  expected day gross G on every world day (day gross = the product of the day's 24 hourly close / previous
  close ratios; G = its mean over all fully active symbol-days of the source). X11: the momentum family still
  reached Tier 1 in 4 / 6 / 9 of 48 null A worlds at 0.025 / 0.05 / 0.10 (8.3 / 12.5 / 18.8%); in the null
  worlds of both nulls its VAL Sharpe was about 2 and it passed every gate but G6 in 47 of 48 worlds. Both
  nulls kept each symbol's own sample mean as its expected return (null A: R-K's c; null B: the mirror's centre
  plus the log mirror's own drift). The auditor's synthetic source has a true per-symbol drift (SD 0.70 a
  year, by its generator), so most of that premium was real on that source (momentum on the source histories:
  mean VAL Sharpe 1.23 over nine draws; in the null worlds built from one of them about 2; on a drift-free source
  about 0 in the history and 0.0 to 0.2 in its null worlds); R-M stands because a kept sample mean is a
  permanent difference between symbols, luck or not (corrected in fix pass 9). Null A: shared-branch
  rows are multiplied by (G / M(Q, s))^(1/24), fallback rows by (G / M(s))^(1/24) (R-K left fallback days
  alone); null B: every active row by G^(1/24) exp(-m) cosh(x)^(-1/n), so a day's gross is G^(n/24) (1 +- tanh
  x), G^(n/24) in expectation whatever the path. Simple day returns are equalised because positions are held
  between rebalances. The draws, the bar shapes, the funding and the core unit are unchanged; the null B worlds
  change. On the test suite's synthetic source the spread of the expected day gross across symbols (SD of
  (E - 1) x 365) went from 0.685 (null A) and 0.684 (null B) to zero within rounding. FP8-2: tier_at (one
  implementation in omr/pipeline.py, which omr/calibrate.py refers to) raises on a malformed evaluated row (a
  required gate missing or not a boolean, perm_p not a finite number in [0, 1]) and the unit verdict is the
  "malformed" STOP; reading such a row as "not passing" would be the loose direction for a null row. FP8-3:
  unit_verdict catches every Exception. FP8-4: an advisory during the null phases (log only) when the passes so
  far already exceed the pooled or a family bound at every threshold, or the largest threshold still open lacks
  oracle power. omr/ucalibrate.py PROTOCOL_VERSION 6. Evidence: notes/kp015_build_evidence.md.
- Fix pass 9 (2026-11-21; audit round 7, addendum X12-prep: the auditor's attack on R-M and its measurement of
  the lag axis; the coordinator's ruling R-N, top30 only, the core unit's G6 unchanged). D2: for a book with a 37
  to 60 day window the correlation of two lagged Sharpe ratios is +0.87 at 0 to 10 days apart, +0.50 at 10 to 25,
  +0.07 at 25 to 50 and about zero beyond, so G6's 200 uniform lags held only about 11 to 14 independent values;
  a slow book earning a premium without timing was first among its copies about 1 time in 13 at any threshold
  under 0.08 and first or second about 1 time in 6 at 0.10. R-N (a): UNIVERSE_G6_LAGS = 20 lags, equally spaced
  by step = (half of VAL - 30 days) // 20 (621 hours, about 26 days) from 30 days plus one random phase (the
  only draw of the lag generator); p = (1 + lagged books at least as good) / 21, so 0.05 means no stale copy as
  good, 0.10 at most one, and 0.025 cannot be reached in top30. R-N (b): the speed limit UNIVERSE_G6_MEMORY_MAX =
  0.5: the correlation of the weights with their own copy j steps earlier (j = 1 .. 19, the common names,
  each name's mean over the rows compared removed) must not exceed it, otherwise p = 1 and no lag book is run (an
  undefined correlation counts as above). Both constants are provisional until the auditor's K = 20 / K = 40
  measurement. The G6 gate record, the trial detail and every calibration row show the memory, the step and
  whether the limit was exceeded; pipeline.Opts.u_lags carries the lag count (the core keeps perm_n = 200).
  omr/ucalibrate.py PROTOCOL_VERSION 7. Texts: the R-M reason corrected (a kept sample mean is a permanent
  difference between symbols, luck or not: a premium world, not a no-skill one); CONSTITUTION sections 12 and
  13, LANGUAGE section 10. Evidence: notes/kp015_build_evidence.md.
- Fix pass 10 (2026-11-21; audit round 7, addendum X12: the power arm on real DEV-period prices stopped because
  under null B 16 of 24 fast and 18 of 24 slow oracle books, and 34 of 48 submitted null pairs, were liquidated;
  the coordinator's rulings). Cause: the real evaluation and the core calibration's worlds take the liquidation
  wicks from the mark bar, but the top30 worlds used their own last-price bars, so two real last-price bad prints
  (low / open 0.00206 and 0.00136, ordinary mark bars) became highs of 485 and 736 times the open on a flipped
  null B day. R-O (top30 calibration worlds only): the source keeps per row hm and lm, the up and dn of
  datasets.liquidation_ratios where the row has a valid mark bar (NaN elsewhere); on an active world row whose
  source row has them the world's mark bar has high = open * HM and low = open * LM ((hm, lm), mirrored as (1 / lm,
  1 / hm) on a flipped null B row); every other mark row is the world's last-price bar; mark open and close are the
  world's; the index table stays the mark table. Left as it is: a world row without trades stays flat. The source
  records the active rows, those without a valid mark bar and the two extreme effective ratios (meta "liq"); the run
  prints them, the artifact carries them (source_liq), and tune_rho records per cell the liquidated (non-finite)
  tuning books at the chosen rho. The real-source loader reads mark_klines with the same logged handle. Klines,
  funding, draws and the R-M factors are unchanged. Universe PROTOCOL_VERSION 8. R-P (calibrate.decide, both units):
  under each null at most NULL_NOT_EVALUATED_MAX = 0.03 of the submitted pairs may end without an evaluation
  (liquidated, a kernel fault or anything else); otherwise that null fails every threshold (fail-closed: both counts
  proper, n_submitted > 0, the share at most the bound); the verdict records the bound and each null's share; the
  null advisory marks every threshold dead once the not-evaluated pairs so far exceed the bound over the largest
  final denominator. R-Q (calibrate.task_null and ucalibrate.task_null, both units): a screened draw liquidated on
  DEV (counted dev_liquidated) or whose DEV Sharpe is otherwise not finite (dev_sharpe_not_finite) is not a
  candidate, so a draw liquidated on DEV is never submitted, and a pair without a candidate is not submitted (the
  auditor's null A size run had the carry family submitted in 5 of 20 worlds although every screened draw was
  liquidated on DEV; and a NaN first value could never be replaced). Draws and ties are unchanged, so a pair with a
  finite best submits the same draw as before. omr/calibrate.py PROTOCOL_VERSION 5 (the core calibration keeps no
  partial file). Correction: the X12-prep reason for the speed limit gave a lagged-Sharpe correlation of "about
  a quarter" at a weight correlation of 0.5; the auditor measured 0.35 to 0.46 at a memory of 0.49 to 0.53 (the
  phrase stood only in audits/AUDIT_LOG.md, not in the kernel texts; the design and the constants do not change).
  Evidence: notes/kp015_build_evidence.md.
- Fix pass 11 (2026-11-22; audit round 7, addendum X12 (size arm): the pilot read NOT READY and the coordinator found
  a gap in the rule after R-Q; ruling R-R, both units, replacing the cap of R-P; the human may decline it). Why: after
  R-Q a liquidation on DEV turns a pair into "not submitted", R-P counted submitted pairs only and decide skipped a
  family without a submitted pair, so a breakage whose bad rows lie in DEV would read as safety; and R-P's 3% is a
  hard stop on a count that one real bar moves by several points (8 of 132 null B pairs on the pilot's source, one
  replayed DEV bar). R-R: (a) the pooled and the family rates are Tier-1 passes over EVALUATED pairs (the rate over
  submitted pairs is kept as information) and a missing rate fails; (b) FAMILY_EVALUATED_MIN = 0.50 per family and
  NULL_EVALUATED_MIN = 0.75 per null of the DESIGNED pairs (the worlds ordered); (c) NULL_FAULT_MAX = 0.03 of the
  submitted pairs neither evaluated nor liquidated (NULL_NOT_EVALUATED_MAX removed); (d) the stored rows exactly the
  protocol design (one null row per seed and family, one oracle row per seed, speed and level, the module's seeds),
  else STOP; (e) CALIBRATION_WORLDS = 300, CALIBRATION_ORACLE_WORLDS = 200, UNIVERSE_CALIBRATION_WORLDS = 200,
  UNIVERSE_CALIBRATION_ORACLE_WORLDS = 100: the argparse defaults read them, and the seal refuses an artifact whose
  protocol header is not the one the checking kernel writes for a real run of the protocol's size, key by key after a
  JSON round trip (core: calibrate.protocol_header, written by main as "protocol"; universe: run_header, now stored in
  the artifact; both carry the options object); (f) a real run with other sizes (and a core real run with a subset of the families) is refused
  before any data access; (g) the universe null advisory follows the rule and stays certain. On the sealed core rows
  R-R changes nothing (evaluated = submitted, every family at least 299 of 300 evaluated; chosen 0.10).
  omr/calibrate.py PROTOCOL_VERSION 6, omr/ucalibrate.py PROTOCOL_VERSION 9. Texts: CONSTITUTION sections 8, 12 and
  13. Evidence: notes/kp015_build_evidence.md.
- Decision (2026-11-23). The pilot's extension read odds of 0.843 for a successful seal against the 0.75 fixed in
  advance (audits/AUDIT_LOG.md, round 7, X12 extension, interim reading). The coordinator stated the exact change to
  the human again (the unit top30 with the index price, a G6 threshold per unit, the rulings R-L, R-M, R-N, R-O, R-Q
  and R-R, each of which he may decline), with the odds, what the pilot cannot cover, the known limits and the run
  time, recommended approval and asked for it. The human replied, in full: "decide whats the best". Acting for the
  human on that delegation (CONSTITUTION section 10, step 2; recorded as such, it is not a yes in his own words), the
  coordinator approved KP-015 as built at 305e2c6 with all six rulings. KP-016, KP-014 and the confirmation of the
  rule set as a whole are NOT covered and stay open. Re-keyed on 2026-11-23 on branch kp015-build: semantic
  5ea66b0fb79ca267..., text 1366fb8fd0b69768..., not sealed (ledger/kernel_history.jsonl, row 9). Both calibrations,
  the seal, the selftest, an independent recount and the merge into `main` follow (audits/AUDIT_LOG.md, round 7, X12
  decision).
- Sealed (2026-11-23). Both real calibrations ran to the end on the re-keyed kernel (top30 01:05 to 13:22 with three
  workers, core 13:23 to 14:08) and neither stopped: G6 threshold 0.10 for core and 0.10 for top30
  (ledger/kernel_history.jsonl, row 10; artifacts ledger/calibration_5ea66b0fb79ca267.json and
  ledger/ucalibration_5ea66b0fb79ca267.json). Top30: no Tier-1 pass among 547 evaluated null pairs under null A and
  1 among 542 under null B at 0.10; power at true Sharpe 1.5: 0.82, 0.74, 0.70 and 0.68. Core: every row equals the
  earlier sealed kernel's. The reading before the seal, the coordinator's recount and the selftest are in
  audits/AUDIT_LOG.md (round 7, X12 seal); an independent recount and the merge into `main` follow.

## 2026-11-21 (coordinator, audit round 7) KP-016 Count the null pass rate over DEV-positive submissions

- Problem: the threshold rule's denominator is SUBMITTED pairs (KP-003): per world and family the
  activity passer with the best DEV Sharpe among 20 draws, whatever the sign of that Sharpe. A
  researcher does not spend a counted trial on a program with a negative DEV Sharpe, and such a pair
  fails G3 with certainty, so these pairs only enlarge the denominator. In the sealed core artifact
  (7446278556aadd8f) about 76% of the submitted pairs pass G3; counted over those, the pass rate at
  0.10 under null A would be about 3.9% instead of 2.94%, and 0.05 would be the largest qualifying
  threshold (about 2.3%). In the other direction the calibration does not run G8, which can only
  veto, so its rates are upper bounds per submitted pair. The same reasoning led to R-J in KP-015 (a
  family that could never pass diluted the top30 rate by about a third).
- Proposed change: count the null pass rate over the submitted pairs with a positive DEV Sharpe, per
  unit, and store both rates in the artifact.
- Cost: a semantic change of the rule (omr/calibrate.py, CONSTITUTION section 8), so a re-key and both
  calibrations again (top30 about 88 worker-hours). Not bundled into KP-015: it changes the core
  unit's outcome (0.05 instead of 0.10 on the stored rows), and the size of the effect next to G8 is
  not measured. (Fix pass 7 does add the family bound R-L to the rule of both units; on the stored
  core rows that changes nothing.)
- Interim: after each calibration the coordinator reports the rate over DEV-positive submissions next
  to the sealed thresholds, computed from the stored rows.
- Evidence added 2026-11-21 (audit round 7, X10; audits/AUDIT_LOG.md). (1) Top30: in the null worlds
  13 of the 36 submitted pairs per null have a positive DEV Sharpe (12 momentum, 1 carry); reversal
  and carry never pass, so the bound over SUBMITTED pairs allows the momentum family 9%. That family
  passes every other gate in those worlds, so its rate is the level of G6 itself, and under this
  proposal only 0.025 lies under the 3% bound; at 200 worlds per null a valid test at that level
  misses the bound by chance in about four runs in ten. Adopting this proposal for top30 therefore
  needs a decision on the grid or the bound as well. (2) Core, on the stored rows of 7446278556aadd8f:
  this proposal gives 0.05 (2.27% and 1.59% under nulls A and B) instead of 0.10 (3.85% and 3.10%);
  oracle power at true Sharpe 1.5 at 0.05 is 81% to 90.5%.
- Built into KP-015 instead (fix pass 7, ruling R-L): FAMILY_PASS_MAX = 0.06. No single family's null
  pass rate (per its own submitted pairs) may exceed 6% under either null at the chosen threshold, in
  addition to the pooled 3%. It can only lower a threshold; on the stored core rows it changes nothing
  (worst family 4.67% at 0.10). The artifact stores the per-family rates and the rate over
  DEV-positive pairs. This proposal stays open as the stricter rule.
- Evidence added 2026-11-23 (the sealed rows of KP-015; audits/AUDIT_LOG.md, round 7, X12 seal). Over the
  evaluated pairs with a positive DEV Sharpe, Tier-1 at 0.025 / 0.05 / 0.10: top30 null A 0 / 0 / 0 of 165,
  null B 0 / 0 / 1 of 225 (0.44%); core null A 10 / 26 / 44 of 1144 (0.87%, 2.27%, 3.85%), null B 6 / 18 /
  35 of 1130 (0.53%, 1.59%, 3.10%). After R-M and R-N the concern of 2026-11-21 about top30 is gone (top30
  would keep 0.10); core would get 0.05, with power at true Sharpe 1.5 of 0.84, 0.83, 0.905 and 0.81. The
  cost as measured: both calibrations again take about 13 machine hours with three workers (top30 11.8
  hours, core 0.7), after a build, an audit and a re-key.
- Status: APPROVED BY DELEGATION 2026-11-25 (see the entry of that date at the end of this file); in the
  batch re-key with KP-018 and KP-019. The one counted trial of generation 2 (7eadbeeaf2adc98d) keeps the id
  of the earlier kernel.

## 2026-11-23 (coordinator, seal recount) KP-017 Findings of the independent recount of the KP-015 seal

- Source: audits/seal_recount_findings.md (verdict AGREE with the seal; no blocker) and audits/AUDIT_LOG.md,
  round 7, X12 seal recount.
- S1, G6 in top30 on books dominated by costs. Under null B the carry calibration family passes G6 alone in
  53 of 166 evaluated pairs at 0.10 and in 31 at 0.05 (nominal 2/21 and 1/21). No such pair passes the other
  gates, so the seal does not depend on it. Conjectured cause: each book pays its own costs and the test
  compares Sharpe ratios, so of two losing books the more volatile one wins; under null B the actual carry
  book is the more volatile one. Possible change, only if a measurement on DEV-period worlds shows an effect
  on books that can pass the other gates: compare the two books on the difference of their return series (or
  another statistic that a difference in volatility cannot move). Cost: a semantic change of omr/upipeline.py,
  a pilot, a re-key and both calibrations. Until measured: no funding-driven program is submitted for a
  counted trial in unit top30 (RESEARCH_PLAYBOOK section 4b).
- Text, at the next text pass (a text-only re-key keeps the seal and the trial ids): CONSTITUTION section 13,
  limit (2) of G6 in top30, to state the size and the direction that were measured; section 8 to state the
  1e-12 tolerance of the rule's comparisons, that the seal compares the research hash with the manifest, and
  that of the top30 artifact the run header is the part compared key by key. From generation 2's researcher:
  LANGUAGE.md section 3 to say that an integer window param cannot default to 1 (default - 1 lies below the
  minimum of 1), so a one-bar horizon is always the literal 1 and is never jittered; CONSTITUTION section 13 to
  say that in unit top30 the 2020 bucket of G7 is short (the unit needs seasoned members), so G7 is in effect
  four of the five later buckets.
- Code, at the next semantic re-key (each needs both calibrations again, so none is worth a re-key alone): the
  level check of an oracle cell averages the evaluated books while the power counts every book of the cell
  (omr/calibrate.py oracle_summary and its top30 counterpart); the docstring of omr/calibrate.py that still
  says "submitted pairs" for the family rate; a chosen draw that fails stage 1 is stored as not submitted and
  can never count against the 3% fault bound; tier_at does not check that p lies on its lattice.
- Measured 2026-11-25 (audits/AUDIT_LOG.md, "KP-017 measurement"; audits/kp017/). In the kernel's null worlds
  built from DEV-period rows only, 32 worlds per null: G6 alone passed the generation-2 candidate
  (gen002_averaged_funding_shock) in 5 of 64 worlds with costs on (bound 11) and, with costs off, in 3 of the 32
  worlds in which it did well by luck, against 4 of 33 for a price-only book. The restriction was lifted for that
  one program (its counted trial then failed on its merits: 7eadbeeaf2adc98d). The carry family at its default
  did NOT show S1 in those worlds (0 of 16 evaluated worlds with costs on, 0 of 16 with costs off), although its
  actual book was 1.16 times as volatile as its stale copies. So S1 belongs to the calibration's own worlds
  (rows of the validation period, the best of 20 draws) and can only be examined inside a calibration: a later
  calibration could store the per-lag details of the carry family. No change of the G6 statistic is proposed.
  For every other program reading funding or the basis the restriction of RESEARCH_PLAYBOOK section 4b stays.
- Status: open (S1 not explained; no change of the G6 statistic proposed; every change needs the human's
  approval). Riding on the batch re-key of 2026-11-25 (see the entry of that date at the end of this file): the
  storage of per-lag details in the top30 calibration and the code items above; the text items wait.

## 2026-11-23 (researcher, generation 2 round 1) KP-018 Sandbox readings of G6's speed limit and of next30 for unit top30

- Problem: two top30 gates can fail a counted trial on grounds a researcher cannot see on DEV. G6's speed limit
  fails any book whose weights correlate above 0.5 with its own weights one lag step (about 26 days) earlier, a
  hard p = 1 with no lag run. G8 needs a positive Sharpe on next30 (ranks 31 to 60). The sandbox prints neither,
  so a slow or universe-specific book can only be found out by spending a counted trial (M + 1 forever).
- Evidence: in generation 2 the researcher had to write DEV-only diagnostic programs (signal = c * w(t) *
  w(t - k), read as avg net / avg gross) to bound the speed-limit statistic; their lookback had to fit inside
  the 2,160-hour limit together with the program's own, which kept the baselines of three hypotheses to 4
  weeks; the coordinator had to rule on whether such diagnostics are allowed. No next30 reading is possible
  from inside the language (unit next30 cannot be declared).
- Proposed change: `omr.sandbox`, for a unit top30 program, also prints (a) the speed-limit statistic computed
  as G6 computes it, on DEV rows, for one to three lag steps, with the 0.5 limit shown, and (b) the DEV Sharpe
  of the same program on unit next30. Both use DEV data only, are uncounted and are logged like every other
  sandbox metric. No threshold, gate or trial rule changes. Added by round 3's researcher (2026-11-24): (c)
  the gross funding paid and the gross funding received, separately (G2 stresses the two differently and the
  sandbox prints only their net, so a DEV reading of G2 is a proxy), and (d) the average number of names the
  book holds (names lost to data holes are invisible while ten or more remain).
- Cost: omr/sandbox.py is a semantic file, so a re-key and both calibrations again (about 13 machine hours),
  although no gate changes: worth it only together with another semantic change.
- Expected effect: no change in any pass rate; fewer counted trials wasted on books that fail the speed limit
  by construction or that work only in the top 30; diagnostic programs are no longer needed.
- Status: APPROVED BY DELEGATION 2026-11-25 (see the entry of that date at the end of this file); in the batch
  re-key; design, build and audit pending.

## 2026-11-23 (researcher, generation 2 round 1) KP-019 Aggregate or sample a dimensionless expression over a timeframe

- Problem: the timeframe functions take only a FIELD or btc(field). A signal built from an expression of hourly
  data (realised skewness or signed jumps from hourly returns, returns by trading session, the shape of the
  week's range) can only be a rolling window on hourly rows. It then re-ranks every hour, and the engine trades
  whenever a name moves 0.01 off target: at 12.5 bps per side such a book pays about a full replacement a day
  (about 0.9 of gross a year, 1.8 doubled), far beyond what G4 allows.
- Evidence: generation 2's plan gave up two ideas for this reason alone (a lottery-demand skewness ranking and
  an Asia against US session split) and kept only signals whose inputs are fields aggregated to weekly bars.
  The plan's cost estimate for weekly rank books (about 0.09 of gross a year) was confirmed on DEV (0.055 to
  0.092 a year in four runs).
- Proposed change: one of (a) `tf_sum(x, tf)`, `tf_mean(x, tf)`, `tf_last(x, tf)` for a DIMENSIONLESS series x
  and a timeframe tf: complete bins only, anchored as the existing timeframe functions, known only if x is
  known on every hour of the bin, visible from the hour the bin closes; or (b) `sample(x, tf)`: x's value at
  the last hour of each completed bin, held until the next. The input must be dimensionless (no price or volume
  level can leak); lookback by the leaf rule of a timeframe plus the input's own; the probe, the truncation and
  the start-cut self-checks apply unchanged.
- Cost: a new function is a semantic change: a build, an audit of the new function against the constant probe
  and the locality checks, a re-key and both calibrations.
- Expected effect: no direct change in pass rates; it widens the ideas whose holding period fits the unit's
  certified speed (5 to 20 days). Risk: more ways to write a near-constant (a weekly mean of hour, say); the
  probe and the coordinator's source read already cover calendar averages.
- Related requests of round 3's researcher (2026-11-24): the perp premium over the index can be read only as
  bin-close snapshots or as an hourly rolling mean, so a daily mean premium is out of reach without (a); and
  `funding_mean(n)` counts settlements, so the same n spans half the hours on a coin with 4-hour funding: a
  funding window measured in hours would need a time-based function.
- Status: APPROVED BY DELEGATION 2026-11-25 (see the entry of that date at the end of this file); in the batch
  re-key; design, build and audit pending.

## 2026-11-25 (coordinator) Decision by delegation: one semantic re-key for KP-016, KP-018 and KP-019

- The question, put to the human on 2026-11-25 after the counted trial 7eadbeeaf2adc98d: either one re-key
  that carries the two requests of generation 2's researchers (KP-018 and KP-019), on which KP-016 could ride
  at no extra machine time, or more rounds on the kernel as it is. The coordinator recommended the re-key.
  The human's answer, in his words: "decide whats the best". The coordinator decides for him and records it as
  that: an approval by delegation for this batch only, as with KP-015. It is not a standing delegation; every
  later kernel change needs the human's approval again, and he may strike any item below until the re-key.
- Decision: build the batch now, before any further round. Reasons: (1) all four rounds of generation 2 were
  shaped by the same two obstacles (LESSONS 16 to 33; generations/gen002/REPORT.md), the next round would be
  shaped by them again, a round costs about one usage window and a counted trial raises M for ever; (2) a
  semantic re-key costs about 13 machine hours whatever its size, so what needs one goes into this one;
  (3) KP-016 makes the bound stricter in the unit where the count has no pass to spare, costs little power
  there (0.81 to 0.905 at true Sharpe 1.5 on the stored rows) and changes no past result (no trial is Tier 1).
- In the batch. KP-019: a way to sample or aggregate a DIMENSIONLESS expression over one of the existing
  timeframes (complete bins only, anchored and visible as the existing timeframe functions), in the smallest
  form that serves the requests on record. KP-018: the sandbox prints, for unit top30 and on DEV rows only,
  G6's speed-limit statistic, the DEV reading on next30, gross funding paid and received, and the average
  number of names held. KP-016: the pooled 3% bound is counted over the pairs with a positive DEV Sharpe. Of
  KP-017: the top30 calibration stores the per-lag details of G6 (the only way to examine S1), and the items
  listed there under "Code, at the next semantic re-key", each only where the design shows that it changes
  no outcome on the stored rows.
- Not in the batch: the text items of KP-017 and KP-014 (a text-only re-key keeps the seal and the trial ids
  and can be made at any time with the human's approval); KP-002, KP-004, KP-005, KP-010; any change of the
  G6 statistic, of costs, of a gate or of a threshold other than by KP-016's rule; any new calibration family.
- Expected, written before the build: every row of the existing calibration programs comes out identical to
  the sealed artifacts (ledger/calibration_5ea66b0fb79ca267.json, ledger/ucalibration_5ea66b0fb79ca267.json);
  thresholds top30 0.10 (0 of 165 and 1 of 225 at 0.10) and core 0.05 (26 of 1144 and 18 of 1130 at 0.05;
  44 of 1144 and 35 of 1130 at 0.10). A deviation is a finding to explain before the seal, not a number to
  accept.
- Known limit, stated now: the calibration families hold no sampled book. In unit top30 the null pass counts
  leave a wide margin under the bound (0 of 547 and 1 of 542 at 0.10), and G6 compares a book with lagged
  copies of its own weights, which a calendar-anchored refresh does not favour by construction; the design
  and the audit are to test both statements.
- Order: design (no kernel file changed) - the coordinator's gate - build on branch kp019-build - tests -
  independent audit, and the coordinator's own review of the parts in which a mistake corrupts every result
  (the new function's causality and locality, the seal's count) - re-key - both calibrations, unattended -
  pre-seal reading - seal - selftest - recount - merge. Until the seal: no research round, no counted trial.
