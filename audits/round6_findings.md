# Audit round 6 - KP-015 universe unit (commit bd6920b) - findings

Copy: scratchpad\review6\kern = the 134 blobs of bd6920b (git-blob hashes verified, setup6.py); data/ tracked
files in tracked_data\. All scripts and outputs in scratchpad\review6\. A second copy kern973 (135 blobs of the
builder's fix commit 973e413, verified) was used only to re-run the block probes against the fix.

VERDICT: NOT READY for the re-key of bd6920b. F1 (blocks) is fixed in 973e413 for every probe I have
(p01_973_out.txt, p01b_973_out.txt, p10_out.txt); F2 (G6 under churn) and the MEDIUM items stand.

State: start - git status --short empty, HEAD bd6920b; end - git status --short empty, HEAD 973e413 (the
builder's commit, pushed). listing6.py start vs end: 2,747 lines, only STATE.md and data/validation.json differ,
and both equal their blobs in 973e413 (git hash-object == ls-tree); ledger/, kernel.lock, every parquet of the
four datasets and the data/raw summary are unchanged. Nothing was written inside the project by me.
Test suite (copy of bd6920b, no real data in the copy, one process): 723 passed, 13 skipped (all skips: real data
absent), 498 s (pytest_copy_out.txt).

## F1 is fixed in 973e413 (re-run of my probes against kern973)
- p01_blocks_973.py: every program of p01 (lag(cs,3), sma(cs_rank,48), cs(sma(cs)), hold over cs, sma(cs,1500)):
  0 known cells differ, 0 values differ, 0 weights differ between production blocks and one block.
- p01b_blocks_g8_973.py: next30 3-month blocks 0 lost; G8 Sharpe identical (-1.5764 / -1.0844); daily cs window
  0 lost; stage1_u W identical with blocks and with one block (15,673 direction changes both); stage2_u VAL Sharpe
  -1.40863 both.
- p10_overlap_can_fail_973.py: the new block_overlap check CAN fail: with the recorded lookback forced from 144 to
  1 hour, stage1_u returns kernel_fault / block_overlap; with the true lookback, ok.
- On paper (diff_fix3.txt): every run (base, truncation cut, start cut, jitter variant) computes its own
  membership once (run_membership(r0, r1)), so the cut checks keep their power; block symbols now come from every
  month touched by s0..e-1 (no "previous block" rule); OVERLAP_HOURS >= LOOKBACK_MAX_HOURS + 168 is asserted;
  block_overlap ends stage 1 uncounted and stage 2 as a counted kernel_fault. Remaining weakness: block_overlap is
  vacuous when the compared rows are unknown in both blocks (no minimum of known cells), and funding8h's unbounded
  as-of memory stays invisible to it (tables() never cuts funding, so no difference arises today).

## F1 CRITICAL - six-month (and G8 three-month) blocks are NOT bit-identical to the whole panel when a window,
## lag, hold or timeframe is applied to a cs_* result; the result is silently changed

Script: p01_blocks.py (synthetic universe = the builder's own conftest.synth_universe(seed=5, n=52), VAL end).
Observed (p01_out.txt), whole panel (one block) vs production half-year blocks:
- cs_* outermost (control) and lag(cs_demean(x), 1): identical.
- lag(cs_demean(ret(close,n)), m=3): 564 known cells lost, rows 0-1 after each block start.
- sma(cs_rank(ret(close,n)), m=48): 12,972 known cells lost (rows 0..45 after each block start); cs(sma(cs)) same.
- hold over a cs_rank (h=72): 19,740 known cells lost (rows 0..69 after each block start).
- sma(cs_rank(ret(close,n)), m=1500): 410,900 of 1,232,287 known cells lost (33%): the program is flat for the
  first 1,497 hours (62 days) of every half-year block.
- values equal wherever both runs are known (only the known channel differs; weights become 0).
Cause: Blocked._eval recomputes membership from the block's own rows (from s0 = 97 days before the block's first
month), so every month that starts before the block's first month has an UNKNOWN membership in the block run;
in-play is False there, every cs_* value of the warm-up rows is unknown, and any window that reads them is unknown.
Kernel self-checks cannot see it: stage-1 truncation and start cuts, stage-2 DEV-rows-equal and stage-2 start cuts
all compare the blocked evaluator with itself (stage1_u and stage2_u both use Blocked with the same boundaries).
LANGUAGE.md section 10 ("the stitched result is bit-identical to the whole panel") and CONSTITUTION section 13
are false for this program class. None of the builder's block tests uses a window over a cs_* result.
Fix: semantic re-key (code). See the attack on the builder's intended fix below (to be completed).

### F1 continued: G8 next30 3-month blocks, daily cs_* series, and the self-checks (p01b_blocks_g8.py, p01b_out.txt)
- next30, 3-month blocks vs one block: sma(cs_rank(ret(close,n)),48) loses 19,136 known cells and G8's next30
  Sharpe changes from -1.5764 (one block) to -1.5976 (blocks); sma over a DAILY cs_rank (5 days) loses 39,520
  known cells on next30 (G8 Sharpe -1.0844 vs -1.0864) and 26,790 on top30 (6-month blocks). Control (cs_*
  outermost): 0 lost, G8 identical.
- stage1_u with production blocks on sma(cs_rank,48): ok, no fault (25 truncation cuts, 7 start cuts incl. the
  symbol cut), 15,715 DEV direction changes; with one block: 15,673; the stage-1 weight matrices differ.
- stage2_u (synthetic handle, perm_n 20, jitter 2, 3 VAL start cuts): status evaluated, no fault; VAL Sharpe
  -1.4556 with production blocks vs -1.4086 with one block. The counted result changes and nothing notices.

### F1 continued: can any self-check notice? (reading; p01b_blocks_g8.py runs it)
No. stage1_u builds Blocked(months=6) and its truncation cuts (Blocked.unit(upto=..)) and start cuts
(Blocked.unit(start=..)) re-run the same blocks; stage2_u's dev_rows_equal compares the blocked stage-2 run with
the blocked stage-1 run; stage2_u's start cuts are block by block (Blocked.start_cut_agrees). Every comparison is
blocked-vs-blocked, so the block artifact appears on both sides.

### F1 continued: attack on the builder's intended fix (one membership per run used by every block; block panel
### = members of every month the block's evaluated rows touch, warm-up included; new check that each block's
### warm-up rows beyond the static lookback equal the previous block's values)
1. "One membership per run" must mean per EVALUATION CALL, not per stage. If one membership object computed to the
   run's ceiling is reused by the truncation cuts (upto c) and the start cuts, both self-checks lose their power
   against a non-local or look-ahead membership (the cut and the base would share it), and the builder's own
   test_a_non_local_membership_is_caught_by_the_start_cut_check would pass for the wrong reason or fail. Blocks of
   the production run may share the run's membership; every cut must recompute it from the cut's rows.
2. G8 next30 blocks are 3 months (89-92 days), shorter than the 97-day warm-up: the warm-up of block k reaches into
   block k-2. The symbol set must be built from the months the warm-up touches (as proposed), not from "this block
   and the previous one" (the current rule, upipeline.block_plan / universe.block_plan: cur | prev).
3. The proposed block check compares only rows [s0 + L, b) where L = the STATIC lookback (window params at high).
   With L close to 90 days that is about 7 days of rows; if those rows are unknown in both runs (warm-ups, a month
   without a unit, < 10 known members) the check is vacuous. It also checks only knownness/values of the program
   output, not the in-play mask or the engine inputs. It should assert that a minimum number of compared cells are
   known, or compare against a one-block reference on a sample of blocks.
4. True memory beyond lookback_hours that the fix does not address: funding8h is an as-of value known while any
   earlier settlement exists (unbounded memory through a funding gap; with the 2x-interval fresh rule an in-play
   symbol's funding8h can be up to 16 h old, lookback counts 8). Blocks stay equal only because funding tables are
   never cut (tables(): funding rows up to hi, no lower bound) - keep that invariant explicitly or bound funding8h.
5. The fix leaves P2 (non-finite poisoning), the G6 masking question (P3) and the false rejections of the 2-symbol
   probe untouched.
6. The memory estimate (R3) must be re-derived: block panels grow (members of up to 5 months for top30, up to 3-4
   blocks of months for next30) and stage2_sizes in validation.json would be stale.

## F2 HIGH (P3) - the masked G6 is NOT exchangeable under membership churn; the universe calibration (constant
## membership) cannot see it
Script: p03_g6_churn.py (synthetic only; settings `75 0.15 0.07 run 100`): 100 symbols with staggered listings
(30 early, the rest 2020-01..2024-10) and lifetimes of 700-2,200 days; hourly log return = market factor
(drift +5e-5 or -5e-5 per hour by world, sd 0.006) + constant per-symbol drift (sd 8e-5/h) + idiosyncratic noise
(sd 0.008); no autocorrelation, so no TIMING skill exists; quote volume = scale x price x a slow random-walk regime
(volume follows price); funding iid. Membership by the kernel's rule (udata_from_tables). Churn achieved: about
2 new top30 members per VAL month (I could not reach the requested 4-6 with this generator; ever-members ~90).
Programs FIXED at defaults: ucal_xs_momentum, ucal_xs_reversal, ucal_xs_carry, slow momentum smoothed INSIDE the
cross-section (cs_scale(cs_demean(sma(ret(close,24),720)))) and a long-only equal-weight basket of the in-play
members (injected). G6 p from the kernel's own ugates, perm_n = 60 (fewer shifts than production's 200).
Run: 41 worlds (20 rising, 21 falling; I stopped it after 55 minutes at 80 s per world to leave time for the
other probes). Output p03_results.jsonl, p03_summary_out.txt. Rejection rates (binomial SE), nominal = threshold:
| program | market | p<=0.025 | p<=0.05 | p<=0.10 | mean p | actual gross/net | shifted gross/net |
|---|---|---|---|---|---|---|---|
| long basket | rising | 0.000 | 0.050+-0.049 | 0.150+-0.080 | 0.446 | 0.998/+0.998 | 0.626/+0.626 |
| long basket | falling | 0.000 | 0.000 | 0.000 | 0.565 | 0.998/+0.998 | 0.610/+0.610 |
| momentum (n=14d) | rising | 0.000 | 0.000 | 0.100+-0.067 | 0.573 | 1.000/0.000 | 0.626/+0.003 |
| momentum | falling | 0.048+-0.046 | 0.048+-0.046 | 0.143+-0.076 | 0.436 | 0.999/0.000 | 0.610/+0.004 |
| slow momentum | rising | 0.000 | 0.050+-0.049 | 0.100+-0.067 | 0.412 | 1.000/0.000 | 0.627/+0.005 |
| slow momentum | falling | 0.048+-0.046 | 0.143+-0.076 | 0.238+-0.093 | 0.361 | 0.999/0.000 | 0.610/+0.006 |
| reversal (h=24) | both | 0 | 0 | 0 | 1.000 (41/41 worlds p = 1) | 1.000/0.000 | 0.619/-0.001 |
| carry (n=9) | both | 0 | 0 | 0 | 0.918 | 1.000/0.000 | 0.618/-0.001 |
All programs: slow momentum overall p<=0.05 in 9.8%+-4.6%, p<=0.10 in 17.1%+-5.9%, mean p 0.386 (uniform: 0.5,
SE 0.045). Control without churn (p03c_control.py, p03c_out.txt: same return model, 30 symbols, no listings or
delistings, the calibration's constant membership ucalibrate.ConstUData, 12 worlds): slow momentum p never <= 0.10
(min 0.148, mean 0.477), momentum 1/12 <= 0.10, long basket p = 1.000 in 12/12 (ties: every shift equals the
actual). So the departures come from churn + masking.
Reading of the mechanism: masking keeps only symbols in play at both the source and the target time, so every
shifted book holds about 62% of the actual gross and fewer names. (1) Cost-dominated books (reversal, carry):
the actual is worse than every masked shift in 41/41 worlds - impossible under exchangeability (p would be
uniform); the gate is then deaf to such programs whatever their skill (false negatives). (2) Slow cross-sectional
books: a static, timing-free per-symbol effect (constant drift; names that fade fall in volume rank and leave)
is earned by the actual book but cannot be reproduced by shifts that lose the names which joined or left in
between; p shifts down, most in falling markets (2.4x nominal at 0.10, 2.9x at 0.05). (3) A constant
equal-weight long basket: p = 1 without churn, but under churn its p becomes roughly uniform with 15% <= 0.10 in
rising markets, so a timing-free basket can pass G6 at about the nominal rate or above. Net exposure of the
shifted books stayed near zero here (my faders are symmetric); the coordinator's net-tilt mechanism did not
show at this churn level (about 2 new members per month; real data churn is higher).
Remedy check (p03b_remedy.py, p03b_out.txt: the same G6 shifts with each masked shifted row rescaled to the
SOURCE row's gross): p barely moves (pairs kernel/rescaled per world, e.g. reversal 1.0/1.0 in every world, carry
0.854/0.927, slow momentum 0.049/0.049, long basket 0.634/0.561). Restoring gross (and, by symmetry, net) is NOT
enough. The better explanation is diversification: a masked shifted book holds about 60% of the names, so its
volatility per unit of gross is higher; for a book whose VAL mean is negative (costs) that pulls the shifted
Sharpes towards 0 (actual worst: p -> 1); for a book whose VAL mean is positive for a static, timing-free reason
it pulls the shifted Sharpes down (p too small: false timing credit). A remedy has to keep the number of names
and the gross of every shifted row equal to the actual book's (for example re-map each shifted row onto the
target row's in-play names, or rotate each symbol's weights within its own in-play time), and must be verified
on null worlds with churn.
Fix direction (semantic + recalibration): the null must be exchangeable with the actual under the real
membership calendar: e.g. shift each symbol's weights in its own in-play time, or renormalise each shifted row
to the source row's gross and net over the surviving names, and in all cases calibrate the universe G6 on null
worlds WITH churn (listings, delistings, volume following price) instead of constant membership.

## P2 (coordinator) - a KNOWN non-finite input of ONE in-play symbol makes cs_* NaN for EVERY symbol of the row
Script: p02_nonfinite.py (synthetic part), output p02_synth_out.txt: one symbol with a frozen bar
((close-open)/(high-low) = 0/0, known) in a 12-symbol all-in-play row -> cs_mean, cs_demean, cs_scale, cs_rank:
row known 12/12, finite 0/12 (all other rows 60/60 finite). Cause: interp._cross_inplay sums with cumsum over
S_ = in-play & known (a NaN term makes the total NaN) and cs_rank marks the row bad if any S_ value is
non-finite. The row's weights become 0 (whole unit flat) and any window over the cs_* output carries the NaN
for its whole window.
Real-DEV size (p02_nonfinite.py real, output p02_real_out.txt; DEV-bounded pyarrow reader -> udata_from_tables,
no handle; 78-symbol DEV top30 panel, 18,985 DEV unit-hours): for ret(close,24)/std(ret(close,1),24),
zscore(close,24), volume/sma(volume,24), log(volume/lag(volume,1)), taker_buy_volume/volume and
log(quote_volume/sma(quote_volume,24)): 0 unit-hours with a known non-finite in-play value, 0 unit-hours flattened
for their cs_demean; no symbol. On DEV the in-play rule (usable bar, fresh funding) keeps frozen bars out.
Remaining exposure (not measured: VAL rows may not be evaluated): the market-wide zero-trade hour 2024-10-28 20:00
(320 symbols present with zero trades, usable under S3) makes every volume-ratio or log-volume input NaN for every
member at that hour (unit flat, and any window over the cs_* output NaN for its length); a near-constant contract
(USDCUSDT is classed crypto but is never a top30 member 2020-05..2026-11, p04) would do the same for
volatility-normalised inputs. Severity LOW-MEDIUM: rare on this data, but the failure is silent and unit-wide.
Fix: compute cs_* over the in-play symbols whose input is known AND finite (treat a non-finite input like an
unknown one for the cross-section), or make non-finite results unknown at the source.

## A: membership recomputed independently on the REAL archive, every month (market structure only) - SOUND
Script p04_membership_real.py, output p04_out.txt. Project klines read read-only with pyarrow (open_time, trades,
quote_volume, is_gap) for all 678 crypto names of data/symbols.json (until applied). My implementation from the
documented rules (seasoning = first active bar after the last run of >= 7 whole UTC days without an active bar is
>= 90 days before the month; >= 684 active hours in the previous 720; score = median of 90 daily quote-volume sums
over active bars; ties by name) vs the kernel's activity_of + membership on the same rows:
79 known months (2020-05 .. 2026-11), 17,705 eligible symbol-months: 0 months with any difference in the eligible
set, the top30 names, the next30 names, or the top30 order.
Point in time: for every month, the kernel's membership computed from rows strictly before the month start equals
the one from all rows (0 months differ). Control (the check can fail): multiplying one eligible name's quote
volume by 1e6 over the 46 days BEFORE the month changed the ranking in 12/12 sampled months; over the 46 days FROM
the month start, 0/12. Distinct names ever (2020-05..2026-11): top30 155, next30 269. Reused names NU, ANT, MDT
are never top30 members. LUNAUSDT is a top30 member in 11 months, the last 2022-04 (not 2022-03 and not 2022-05:
the archive holes of 2022-02-26..28 and 2022-04-01..02 fail the 95% activity rule, as the build notes disclose; the
LUNA collapse month is therefore outside the unit because of an archive artefact, not a market rule).

## Sound so far
- Engine (p07_engine.py, p07_out.txt): 40 adversarial worlds (gross targets up to 14, sign flips, NaN prices on
  unavailable bars, a hole at row 0, 10 consecutive missing bars then relist, a never-available symbol, a
  delisting, crash paths): run_arrays_u vs the kernel's run_reference_u AND my own units/cash reference: max
  relative equity difference 1.7e-14, event lists and liquidation indexes identical; two blocks with carried
  state == one run bit for bit.
- Identity (p05_light_checks.py): unit "core" explicit == omitted (same canonical); unit top30 adds "unit=top30;"
  to the canonical form (distinct trial id); "Top30", "top30 ", "TOP30" rejected (header_unit).
- Core identity, funding spacing (p05): the ten core-data symbols have NO funding settlement gap on DEV rows;
  S1 drops 0 DEV hours for n = 3, 9, 21. (VAL rows not inspected.)
- Flags (p06_flags.py, p06_out.txt): usable_of on 200 random active/present patterns equals a naive per-row
  reference, has the prefix property (0 violations) and is bounded (a 30-row window with an active bar gives
  the same value); funding_fresh on 200 settlement patterns (mixed 4h/8h, 30 h and 200 h gaps) equals a naive
  reference and is unchanged by later settlements. Both causal and row-local.
- lookback_hours (p09_lookback.py, synthetic core frame, every window param at its high bound): declared >= the
  empirically needed rows for daily(btc(close)) 191 vs 168, sma(daily(close),n) 215 vs 192, hold over ret 120 vs
  120, funding_mean 96 vs 96, corr 97 vs 97; btc() and timeframe functions accept only fields (btc_arg,
  timeframe_arg), so no window can hide inside them. Exceptions found by reading: membership inside cs_* (F1)
  and funding8h's as-of value (unbounded through a funding gap; up to 16 h while 'fresh').
- Sequential sums: every cross-column sum on the evaluation path is sequential in column order (uweights,
  _cross_inplay, the engine's loops skip or add exact zeros); the only pairwise numpy row sums found are in
  ucalibrate.UOracle.weights (calibration, always one block) - no other block-dependent rounding found.
- Symbol table (p08_symbols.py): classify() re-applied to the pinned exchangeInfo reproduces all classes; the 26
  R2 names are coin contracts; status (TRADING 517 / SETTLING 135) is not used.

## Constant probe: honest top30 programs falsely rejected (LOW)
p05_light_checks.py: `cs_scale(cs_demean(abs(cs_rank(ret(close,n)))))` and the same with `r * r` are rejected
(constant_subexpression): the probe panel has TWO symbols, where cs_rank is always +-1, so abs/square of it is
constant; on a 30-symbol unit it varies. Fix: probe top30 programs on a panel with >= 10 symbols (semantic).

## J: the symbol table is NOT inside the research hash (MEDIUM)
Reading: data.compute_research_hash / hashes_streaming (data.py:157-208) hash the stored TABLES of the manifest
only; research_hash_from_disk (data.py:215) and DiskProvider.check (evaluate.py:66-73) recompute exactly that;
data_fingerprint (data.py:222) adds per-file table sha256s only. data/symbols.json is pinned only by
manifest["universe"]["symbols_sha256"] (universe.load_symbols, universe.py:217-227), which `data universe`
rewrites. The symbol table decides which names can be members (class) and where a reused name's rows end
(`until`, applied by activity_of and FullPanel), so a rebuilt symbols.json changes top30 membership and results
while the research hash - and therefore every trial id (lang.trial_id), the dedupe, and the seal's research_hash
binding (kernel_lock.check_artifact / check_universe_artifact) - stays the same. CONSTITUTION section 13 and the
build notes say "one research hash"; the brief asks for one hash "over every stored table and the symbol table".
Fix (semantic): fold the symbols.json sha256 (or the per-name class/until rows) into the research hash.

## Sandbox (NOTE, unchanged pattern)
omr/sandbox.py prints DEV metrics (lines 98-106) before appending the sandbox_log row (111-116); a kernel_fault
exits (line 80) without a row, and an interruption after the printout leaves no row. DEV only, so no VAL exposure.
The top30 sandbox uses the production blocks, so F1 applies to its printout too.

## Calibration design notes (item I, reading)
- ucalibrate defaults: 100 worlds per null x 3 families = 300 pairs per null (core: 300 worlds x 5 = 1,500). At a
  3% pass rate the binomial SE is about 1.0% per null (core about 0.44%): the threshold choice in the top30 unit
  is decided with roughly 2.2x the noise of the core's.
- The 30-symbol null panel = the names with the most active hours over DEV+VAL (choose_panel): long-lived
  survivors; constant membership; no churn. The real unit has 138 distinct members (validation.json) and churn,
  which matters for G6 (see P3).
- decide_both applies the rule to both units, both nulls, power in both units; artifact hashes go through
  _logged_bytes (calibration_log rows) and the universe artifact must carry kernel_lock_verified and the
  research hash (a dry run cannot be sealed). Core calibrate.py changed only in the (unused) index field.

## Not probed / could not check
- Anything evaluated on real VAL or VAULT rows (forbidden): the P2 size on VAL (the 2024-10-28 20:00 hour), G6 on
  real churn, real calibration, real selftest, the real core-identity runner (test_core_identity real-data case
  skipped: the copy holds no data store), the stored-row revision check on a second download (needs network).
- Core identity on real data for G8 extended units: only the funding SPACING of the ten core-data symbols on DEV
  rows (no gaps, S1 drops nothing); VAL rows not inspected.
- The real panel's churn (coordinator: 4-6 changes a month); my generator reached about 2, so the P3 effect on
  real data is likely larger, not smaller. P3 used 60 shifts (production 200) and 41 worlds (stopped early).
- A text-only re-key keeping a seal: reading only (a seal needs both calibrations, which were not run).
- 973e413 beyond the block code: its lang.py and test_blocks.py changes were not reviewed.

## K: documents against code (reading)
1. LANGUAGE.md s10 "Blocks (S4): ... the stitched result is bit-identical to the whole panel" and CONSTITUTION s13
   "bit-identical to the whole panel": false for any window/lag/hold over a cs_* result (F1).
2. LANGUAGE.md s10 "Every function is bounded in time (funding_mean included)": funding8h is the as-of rate of the
   latest settlement and stays KNOWN through a funding gap of any length (interp funding8h: kn = isfinite);
   lookback counts it as 8 h. No bit difference today only because funding tables are never cut.
3. LANGUAGE.md s10 cs_* paragraph: silent on the non-finite case (P2: one known NaN flattens the whole unit).
4. LANGUAGE.md s10 Costs "closed at its last ACTIVE close": the engine uses cl[t-1] of the previous USABLE bar,
   which can be a zero-trade bar (frozen price) - same price in practice, wording differs.
5. universe.inplay_matrix docstring says in play = member and ACTIVE bar (D2); callers pass usable & fresh
   (R2/S3) - stale docstring, behaviour as documented in LANGUAGE.md.
6. CONSTITUTION s13 / build notes "one research hash": the symbol table is outside it (J above).
7. kernel_lock.rekey copies every SEAL_KEYS field from the kept seal: a text-only re-key on a seal written by the
   b12df97 kernel (no universe keys) would raise KeyError. Not reachable now (KP-015 is a semantic re-key).

## Notes
- validation.json (tracked, readable without a counted trial) carries VAL-period membership COUNTS per month,
  distinct-symbol counts per region and per block, unit availability per region, and names three symbols in
  r2_funding_removed (ICP, TLM, SOL). Structure only, no prices; the R3 memory estimate is derived from it.
- USDCUSDT is classed crypto (could enter the unit; near-constant price: see P2). 1000000BOBUSDT/BOBUSDT and
  1000CATUSDT/CATUSDT coexist as separate names (not merged, as documented).
