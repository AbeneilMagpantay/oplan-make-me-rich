# AUDIT LOG

One entry per audit round. Auditor: an independent Opus auditor working on a copy of the tree; from
round 3 also the coordinator's own read of the core modules.

## Round 1 - 2026-11-18 - Python-sandbox kernel, before hardening
- Verdict: NOT READY. 6 critical: the kernel was reachable through an import; file access through
  whitelisted modules; memoised outputs beat the lookahead test; a NaN column skipped every
  lookahead cut; VAL numbers were readable without a counted trial; hard-coded dates passed.
- Fixed by: the hardening build (child runner, allowlist, two-stage count-before-exposure, VAL handles).

## Round 2 - 2026-11-18 to 19 - hardened kernel 2317921c
- Verdict: NOT READY. 4 critical: pandas string dispatch escaping the child; a file-backed memo;
  stored data rewritten between stages; epoch arithmetic undoing the fixed time shifts. Also G8
  failing every strategy on real data, and the G6 denominator.
- Answered by: replacing Python strategies with the interpreted formula language (no strategy code is
  executed), hash-at-read data, the G8 fix and the submitted-pair denominator.

## Round 3 - 2026-11-19 - commit c891061 (kernel 2c20fe77)
- Verdict: NOT READY. 1 critical: a bar-position clock through an infinite-memory filter seeded at
  the frame start (a remembered-calendar program reached Tier 1 on a synthetic world). 1 high:
  constants built without literals. 3 medium: seal accepted a hand-edited artifact; the dry run read
  real VAL bars; one-line PLAN.md opened a generation.
- Coordinator's read: literals escaping the jitter; a redirectable VAL access log; VAL returns by
  period in stored detail; quote-volume units; a parser crash on huge literals.
- Answered by: FIX PASS 4 and 5 - locality by construction (known channel, finite memory, windowed
  hold, fixed-order windows, start-cut self-checks), jittered literals, the constant probe, the
  two-part lock, the calibration log, the synthetic dry run, the REPORT rule.

## Round 4 - 2026-11-19 - commit adf910b (semantic 4598ef42)
- Verdict: READY, no critical or high. Residuals documented: near-constants, the seal forgeable
  locally, report content not checked, a custom data provider.
- Coordinator's read: the probe's NaN gap (`hour / hour`), its false rejections of rare-event rules,
  mark_close windows blanked by single missing bars.
- Fixed in: FIX PASS 6 (refined probe, stale-limited mark_close, probe_fault, 300/200-world
  calibration, documents).

## Round 5 - 2026-11-19 - commit d2c2d4f (semantic 74462785)
- Verdict: READY, no critical, high or medium.
- Independent recount of `ledger/calibration_7446278556aadd8f.json`: null A 10, 26, 44 of 1,498 and
  null B 6, 18, 35 of 1,500 at 0.025 / 0.05 / 0.10; the rule gives 0.10; null A at 0.10 is one pair
  from the 3.0% limit (95% interval about 2.2% to 3.9%). Artifact, calibration-log row and seal are
  in d2c2d4f.
- Two low, text-only items: KERNEL_PROPOSALS KP-014 (open; needs the human's approval).

## Round 6 - 2026-11-19 to 20 - KP-015 build, commit bd6920b (unlocked, branch kp015-build)
- Verdict: NOT READY for the re-key. Auditor's suite on its copy: 723 passed, 13 skipped (real data
  absent from the copy). Nothing in the project was written by the auditor.
- CRITICAL (found by the coordinator's read, confirmed independently by the auditor; FIXED in
  973e413): the block-by-block evaluation recomputed membership inside every block, so any window,
  lag or hold applied to a cs_* result was unknown for (window - 2) hours after every block start.
  `sma(cs_rank(x), 1500)` lost 410,900 of 1,232,287 known cells; a stage-2 VAL Sharpe changed from
  -1.4086 to -1.4556 with no fault. Every self-check compared blocked runs with blocked runs. Fix:
  one membership per run, block panels from every month the evaluated rows touch, the block_overlap
  self-check. The auditor's probes on 973e413: 0 differences; block_overlap can fail.
- HIGH (open): the masked G6 is not exchangeable under membership churn. On synthetic worlds where no
  timing skill can exist (41 worlds, 60 shifts): reversal p = 1.000 in 41 of 41; slow momentum
  p <= 0.10 in 17.1% +- 5.9% (23.8% in falling markets); a constant equal-weight basket p <= 0.10 in
  15% of rising worlds, against p = 1 always without churn. The universe calibration's constant
  membership cannot see it. Ruling (fix pass 4, U1 and U2): G6 in universe units becomes a paired test
  on the names common to both dates, re-centred to each row's own net; the universe nulls are built
  on the real panel with the real membership calendar and run through the production block path.
- MEDIUM (open): data/symbols.json is outside the research hash (U5).
- LOW to MEDIUM (open): one known non-finite input makes cs_* NaN for the whole row; 0 affected
  unit-hours for six natural expressions on real DEV; the VAL hour 2024-10-28 20:00 (every symbol
  zero trades) would poison volume-ratio inputs (U3).
- LOW (open): the two-symbol constant probe rejects honest top30 programs such as
  `abs(cs_rank(x))` (U6); funding8h has unbounded as-of memory while the documents say every
  function is bounded (U7); sandbox prints before it logs; rekey would raise on an old-format seal;
  document wording (U8).
- Data artefact (open, U4): the monthly archive files lack 2022-02-26..28 and 2022-04-01..02 for about
  49 symbols; under the 95% activity rule LUNAUSDT is outside the unit in May 2022, its collapse
  month. The daily archive files for those dates exist; ruling: fill from them.
- Sound: membership recomputed independently on the real archive for every month 2020-05..2026-11
  (79 months, 17,705 eligible symbol-months, 0 differences in eligible set, top30, next30 or order;
  data at or after a month start changes nothing; the comparison can fail); usable and funding-fresh
  flags causal and bounded; the universe engine against two references on 40 adversarial worlds
  (1.7e-14, events identical) and across blocks bit for bit; lookback_hours an upper bound on every
  construct tested; identity; count before exposure (reading); symbol classification.
- Not probed: anything on real VAL rows; the real calibrations and selftest; revision detection on a
  second download; the real-data core-identity test (run by the builder, not the auditor).
- Detail: `audits/round6_findings.md` (the auditor's full findings file, copied unchanged; the probe
  scripts it names were session scratch and are not kept).

## Coordinator's review of fix pass 4 - 2026-11-20 - commit e4e44e2 (unlocked, branch kp015-build)
- Not an audit round: the coordinator's own read of the changed critical parts before round 7.
- G6 in universe units, two defects in the coordinator's own U1 ruling (none in the builder's code):
  (1) the two books' reference nets were measured differently (the actual book after dropping names
  without a bar, the shifted book before), so an equal-weight basket got p = 0.524 on a churn panel
  instead of 1 (reported by the builder as a stop case);
  (2) a circular shift takes the source of every row i < k from L - k rows in the FUTURE, so the
  common-names mask restricts both books at that row to names that are still members at a later
  date: future information at the evaluated row, on about half of all rows. The calibration worlds
  (real membership calendar, resampled prices) cannot show it, nor can churn worlds whose volume is
  independent of price.
  Ruling R-C (fix pass 5): a paired LAG test. The shifted book is the program's own weights k hours
  earlier (k from 30 days to half the VAL length; rows before VAL start are used as sources), both
  books on the names in play at both rows, each row re-centred to the net of the weight row it came
  from. No row after the decision row enters either book.
- Universe calibration nulls: the funding table kept its real persistence under null B, and its
  within-day persistence under null A, so the carry family could earn real carry in a "null" world.
  The sealed core artifact shows the effect at small size (carry family mean VAL Sharpe -0.30 under
  null A against +0.07 under null B; Tier-1 passes under null B 0, 1, 3 of 300 at 0.025, 0.05, 0.10).
  Ruling R-E (fix pass 5): in the universe null worlds every settlement's rate is multiplied by a
  fair coin shared by all symbols at that settlement time. The core calibration is unchanged.
- Ruling R-D (fix pass 5): the universe calibration resumes after an interruption, checks memory
  before it starts, evaluates the oracle at level 1.5 only, and defaults to 200 null worlds and 100
  oracle worlds per null.
- Read and found consistent with the rulings: cs_* over known finite inputs (U3), funding freshness
  (U7), the hole fill's revision check and staged writes (U4), the top30 probe panel (U6), the
  sandbox log order (U8). All of these still need the independent verification of round 7.

## Round 7 - 2026-11-20 to 21 - KP-015 fix passes 4 to 6: commits e4e44e2 and 32e32e0, then the fix pass 6 working tree (unlocked, branch kp015-build)
- Verdict: 32e32e0 NOT READY for the re-key; fix pass 6 READY for the re-key (reviewed on the working
  tree, on condition that the full suite passes; it did: 849 passed, 0 skipped, on the final files).
  The auditor first judged 32e32e0 READY (16:27) and withdrew that at 22:45 after the measurement
  below. It worked on verified copies (142 blobs each) under a memory cap, wrote nothing in the
  project, and by its instructions evaluated no program on real rows after 2022-06-30 (its real-data
  probes report counts and correlations only).
- HIGH X8-F1 (process, no false-pass risk; FIXED in fix pass 6, ruling R-I). Three rounds had measured
  the pass rate of G6 alone. The coordinator ordered Tier-1 power measured the way the calibration
  measures it (one rho per speed at mean VAL Sharpe 1.5, every gate except G8, 40 lags) on 24 worlds
  with the real structure of the 134-symbol panel and synthetic prices (the kernel's rule gives the
  real top30 calendar on them in 67 of 67 months). The 1-day oracle failed G4 (VAL Sharpe at doubled
  costs) in 24 of 24 worlds, so Tier-1 was 0 at every threshold and the seal rule would have stopped
  with certainty after a universe calibration of about 88 worker-hours. Cost drag of the oracle at
  12.5 bps per side, in Sharpe units: 3.86 at 1 day, 1.50 at 3, 0.93 at 5, 0.64 at 7, 0.39 at 10,
  0.29 at 20 days. Tier-1 of 24 at 0.025 / 0.05 / 0.10: 5 days 18 / 18 / 19 (G4 20 of 24), 7 days
  15 / 15 / 19, 10 days 15 / 18 / 20, 20 days 17 / 18 / 20 (0.71 / 0.75 / 0.83; translated to the
  production's 200 lags about 0.59 / 0.72 / 0.81).
  Ruling R-I: the universe oracle's speeds are 5 and 20 days (the core keeps 1 and 20). The choice
  rule was fixed before the sweep: the fastest of 5, 7 and 10 days with Tier-1 at least 0.65 at all
  three thresholds. G4 and the cost rate are not weakened; the unit is certified for holding periods
  of about 5 days and longer, and the rules say so.
- The shared threshold (the coordinator's read of the sealed core artifact, taken up by the auditor):
  the core qualifies 0.10 by one pass (44 of 1,498 submitted pairs under null A, 2.94% against 3%),
  and under the rule of 32e32e0 the top30 rows could have moved the core's threshold and the reverse.
  Ruling R-H: the threshold is decided per unit on its own rows; both units seal or neither; the seal
  holds {"core": x, "top30": y}; the evaluator applies the threshold of the program's own unit.
- MEDIUM, closed. (1) Part 1, H1: null A's personal fallback days destroyed the shared-day
  cross-section (mean pairwise correlation 0.137 against 0.360 in the source). Fixed in 32e32e0 by
  monthly pools: 0.311 on the synthetic source; on the real panel 1.8% fallback symbol-days and a
  member correlation in DEV of 0.67-0.68 against 0.64 real in 2020 and 0.60-0.63 against 0.60 in
  2021; the stress months of 2022 H1 are not reproduced (0.59-0.64 against 0.75 real; note X5-N1,
  direction of the effect on the null pass rate not established). (2) Part 2, X3-F1: the 20-day power
  of G6 at 0.025 was 35% on synthetic churn worlds (about 45% translated to 200 lags), under the 50%
  the seal rule needs; on the real calendar it is 0.71 (above), so the finding is closed and the
  auditor withdrew its suggestion to cap the lag range. Reference arms for the 20-day oracle on the
  same worlds, G6 passes of 24: lags uniform over 30-365 days 15 / 18 / 21, log-uniform 15 / 18 / 20,
  production (uniform from 30 days to half the VAL length) 17 / 18 / 20. The coordinator had refused
  the cap because lagged copies of a slow book stay correlated within the signal's memory of up to 90
  days, which leaves few independent comparisons in a short range.
- LOW, fixed. Part 1 (fixed in 32e32e0, re-probed in part 2): A1 a permanent .missing marker, A2
  daily-file pins never compared, A3 a crash window between table replace and manifest write (a crash
  simulated after every step of the commit now recovers to all-old or all-new). Part 2 (fixed in fix
  pass 6): a torn last line of the calibration's partial file swallowed the next record, a duplicated
  key kept the last value silently, and an artifact without level-1.5 rows raised instead of stopping
  (every line now carries its sha256, a torn tail is repaired, a task stored twice with different
  results stops the run, an incomplete artifact stops the seal with a reason). The sha detects damage,
  not a deliberate edit: the partial file has the same procedural trust as the seal (one pushed
  commit and an independent recount).
- LOW, open, documented in CONSTITUTION section 13 and LANGUAGE section 10. (1) Entrant blind spot:
  both books hold only names in play at both rows, so positions in names that entered the unit less
  than k hours before are in neither book (an entrant-tilt book kept 1-2% of its gross). The real
  top30 gains 3.59 new members per VAL month; the mask keeps 0.81 / 0.69 / 0.63 / 0.57 of the in-play
  names for lags of 30-89 / 90-179 / 180-364 / 365-547 days; for the 20-day oracle the masked actual
  book has Sharpe 1.24 / 1.25 / 1.27 / 1.12 in those bands against 1.5 unmasked, its lagged copies
  -0.15 to -0.29. (2) Each book pays its own costs, so the comparison is distorted for cost-dominated
  fast books (24-hour reversal p about 1; 24-hour momentum p = 0.024 in 1 of 3 worlds; both have a
  VAL Sharpe between -17 and -20 and fail G1 to G4).
- Size of the paired lag G6 where no timing skill can exist (28 synthetic worlds with 2.0 new members
  a month, seven fixed programs, 40 lags): over the 162 non-tie p values 0.6% / 2.5% / 4.3% at 0.025 /
  0.05 / 0.10 (nominal 2.5 / 5 / 10): conservative. The constant basket has p = 1 in every world.
  Volume that follows price against independent volume on the same price paths: no difference. One
  program with a 60-day memory rejected in 3 of 28 worlds at 0.05 and its p values are U-shaped
  (note). The look-ahead of the circular form of e4e44e2 was demonstrated in part 1: the basket
  masked by a future row earned 2.55e-5 per hour more than the same basket masked by a past row
  (se 0.34e-5, 240 seed-lag pairs).
- Sound: the lag code (source row g0 + i - k; mask = tradable now and in play at the source row;
  re-centring; ties and the margin only raise p; the only post-decision input is the execution-bar
  flag shared by both books); the calibration's resume (the header binds protocol, hashes, seeds and
  counts; results in argument order); the funding coin (6,471 settlement hours, 0 with two coins);
  membership on the FILLED real data recomputed independently (79 months, 17,795 eligible
  symbol-months, 0 differences; the control can fail); the hole fill on a sample (31 cached daily
  files: checksum 31 of 31, pin 31 of 31, 733 hourly rows equal); a calibration dry run killed and
  resumed (the rows of the finished tasks equal field for field; the verdict recomputed from the
  stored rows equals the stored one). Fix pass 6, on the working tree: the per-unit decision and seal
  (one unit's rows never move the other's threshold; a float seal, a one-unit mapping, a bool or text
  are refused; the evaluator takes the program's own unit's value right after the parse); the partial
  file's round trip exact for NaN, infinities, -0.0, extreme and numpy values; the oracle-first order
  (by reading); every universe use of the speeds reads the unit constant; the texts match the code.
- Fix pass 6 review items, all answered before this entry: FP6-1 LOW a malformed row raised inside the
  unit verdict (now a STOP with a reason); FP6-2 LOW a stale "round 7 READY" in KERNEL_PROPOSALS
  (corrected); FP6-3 note, a sealed threshold must be a G6_GRID value (done); FP6-4 note, the sealed
  units are C.UNITS (done); FP6-6 note, two wordings (done); FP6-5 note, a torn HEADER is refused as
  "another run" (safe, the message misleads; left). The auditor's residual opinion: the 4-96 hour
  reversal family was cost-dominated (VAL Sharpe about -9.7 in a measured null world), could never
  pass, and so diluted the top30 null pass rate by about a third. Ruling R-J: the family is now the
  momentum's mirror on daily bars, n from 3 to 20 days.
- Coordinator's review of what changed AFTER the auditor's review (the auditor did not see it): the
  FP6 fixes, R-J and the texts that confirm 5 days. Read: the family file (its test compares signal
  and weights with minus the momentum's for the same n, exactly); unit_verdict (the exception path
  can only stop, never pass); thresholds_of (grid values only; NaN, infinity, bool and text refused);
  CONSTITUTION sections 8 and 13, LANGUAGE section 10 and KERNEL_PROPOSALS against the numbers above.
  One change by the coordinator after the suite: the turnover bullet of LANGUAGE section 10 said a
  book replaced daily "cannot pass G4"; it now states the cost (about 0.9 of the gross per year,
  about 1.8 at doubled costs) and that no realistic edge covers it. Runs on the final files (by the
  builder; logs read by the coordinator): tests/test_ucalibrate.py 28 passed; full suite 849 passed
  in 1744.60 s, 0 skipped; ledger verify OK; ledger/ and data/ unchanged. After the wording change:
  tests/test_structure.py 9 passed.
- Residual risks (auditor): the real panel's idiosyncratic volatility is lower than the test worlds'
  (0.62 against 0.75), so the real cost drag in Sharpe units is about 20% higher (5 days: about 1.1
  instead of 0.93). Expect the top30 5-day power a few points under the 0.75 measured here, still
  above 0.50 on these numbers; the oracle-first order shows it after about a third of the run. The
  calibration is tens of CPU-hours with an advisory and no automatic exit.
- Not probed: anything on real VAL rows; the real calibrations, the seal and the selftest; the
  multiprocessing path of the universe calibration. The heavy oracle-order test and the full suite
  were run by the builder, not by the auditor.
- NOT YET RUN at this entry: the end-to-end pilot of the universe calibration on the fix pass 6 code
  (dry run, 1 null world per null, 4 oracle worlds, 1 worker, outputs in scratch). The memory
  preflight refused its single worker (1.6 GiB available, about 1.9 GiB needed). It is required
  before the re-key; pass condition: it finishes, and oracle Tier-1 power is above zero at both
  speeds under both nulls.
- Parked, not part of KP-015 (KERNEL_PROPOSALS KP-016): the null pass rate is counted over SUBMITTED
  pairs, of which about 76% had a positive DEV Sharpe in the sealed core artifact; counted over those
  only, the core's rate at 0.10 would be about 3.9% instead of 2.94%. G8, which the calibration does
  not run, pulls the other way.
- Detail: `audits/round7_findings.md` (the auditor's full findings file, copied unchanged; the probe
  scripts it names were session scratch and are not kept).

## Round 7, addendum X10 - 2026-11-21 - the calibration pilot, then the seal-rule cells through the kernel's null builders: commit 4286abf (unlocked, branch kp015-build)
- Verdict: 4286abf NOT READY for the re-key. This supersedes the READY of fix pass 6 above. No
  false-pass risk was found: the universe calibration would have stopped after its full run (about 88
  worker-hours) because no G6 threshold could qualify under null A. The auditor worked on a verified
  copy of 4286abf (143 blobs) under the same rules as before (synthetic prices on the real structure;
  nothing written in the project).
- The pilot (the kernel's own dry run on its synthetic universe; 4 oracle worlds per cell, 1 null
  world per null, 1 worker, 200 lags): it ran end to end in 62 minutes, the first run of the
  multiprocessing path and of the oracle-first order. Tier-1 power at 0.025 / 0.05 / 0.10: null A fast
  1 / 2 / 3 of 4, null A slow 1 / 1 / 1, null B fast 2 / 3 / 4, null B slow 3 / 3 / 3; its advisory
  fired and its unit verdict is STOP. The pass condition written in the entry above (it finishes;
  power above zero in every cell) was met and was too weak: the coordinator did not ask for the re-key
  on 1 of 4 in a cell and ordered X10 with a reading rule fixed in advance (proceed at 15 of 24 or
  more in every cell at all three thresholds; no re-key at 10 of 24 or fewer at 0.10; in between the
  odds go to the owner).
- X10 Q1, the pilot's low cell: reproduced exactly (all 16 p values and VAL Sharpe ratios). The dry-run
  source is harsher than the real calendar: 5.89 new top30 members per VAL month against 3.59, so the
  common-names mask keeps 0.67 / 0.48 / 0.39 / 0.30 of the in-play cells at lags of 30-89 / 90-179 /
  180-364 / 365-547 days against 0.81 / 0.69 / 0.63 / 0.57. In the three failing null A slow worlds
  the MASKED ACTUAL book collapses at long lags (pooled Sharpe 1.11 / 1.24 / 0.77 / 0.49 by band; 91
  of the 95 beating lags are at 180-547 days); the lagged copies do not earn (-0.17 to -0.72). Null B
  has the same mask and the same lagged copies; its better long-lag Sharpe is within chance at 4
  worlds. So the pilot's weak cell is the dry-run structure plus chance, not a property of null A.
- X10 Q2, the four cells the seal rule reads (the kernel's calibrate_run in one process on the
  real-structure source through its null builders; 24 worlds per null, 200 lags, level 1.5; 282
  minutes). Tier-1 of 24 at 0.025 / 0.05 / 0.10: A fast 17 / 19 / 19, A slow 14 / 17 / 19, B fast
  17 / 20 / 20, B slow 14 / 15 / 17 (G6 alone: 19 / 23 / 24, 14 / 17 / 20, 19 / 23 / 23, 16 / 19 / 21;
  the other gates pass 19 to 24 of 24). Tuned rho 0.048 / 0.089 / 0.049 / 0.073, achieved mean VAL
  Sharpe 1.50. The mask keeps 0.81 / 0.69 / 0.63 / 0.57 and the masked actual book stays at 1.05 to
  1.38 in every band, so the pilot's collapse does not recur. By the rule fixed in advance: MARGINAL
  (both slow cells are 14 at 0.025; no cell is at or under 10 at 0.10).
- HIGH X10-F1 (design, no false-pass risk; ruling R-K, fix pass 7 ordered). Q3: the three calibration
  families in null worlds on the same source (12 worlds per null, every pair submitted). Momentum
  under null A: VAL Sharpe 2.07 to 4.16, every other gate passed in 12 of 12, p = 0.005 (the minimum)
  in 5 of 12, Tier-1 5 / 6 / 8 of 12; under null B 0 / 1 / 1 of 12 with p values skewed high (median
  0.66). Reversal and carry: 0 everywhere (VAL Sharpe -1.5 to -4.7). Pooled null A pass rate 13.9% /
  16.7% / 22.2% of submitted pairs against the 3% bound: no threshold qualifies. Mechanism (P21):
  under null A a month's days are drawn from POOL(m), the source days on which every member of month
  m is fully active, so a symbol's expected return in month m is its mean over that pool. The
  pool-specific part (pool mean minus whole-period mean) has a cross-sectional SD of about 0.6 a year
  and a correlation between month m and month m-k of 0.77 / 0.48 / 0.24 / 0.13 by lag band: a slow
  momentum book holds the current pool's drift, its lagged copies hold less of it the longer the lag,
  and the paired lag test reads that as timing. Null B keeps one constant drift per symbol, which
  every lag shares. The pilot's single null A momentum pair had shown the same (p 0.0945, Tier 1 at
  0.10). Reference arm P22 (the auditor's copy only: pool-specific mean removed, same 12 seeds):
  momentum Tier-1 0 / 0 / 2 of 12, p values 0.075 to 0.940, median VAL Sharpe 1.9 instead of 2.8.
- Coordinator's review of X10-F1 (read: USource._build_pools, UWorld.__init__, _source_days, _build;
  the auditor's P22 patch). The finding stands. POOL(m) is in practice the period since the youngest
  member of month m was listed, so the pools are windows of history that change with the membership;
  the null worlds therefore contained a slowly changing cross-section of expected returns, which is
  predictability a no-skill world must not have. It entered in fix pass 5 with R-F (monthly pools,
  the answer to H1); neither the coordinator's review nor X5 (correlations of the pooled worlds)
  looked at the pools' means. The reference arm also shifts the days that use a personal fallback
  day, whose expected return is not the pool's, and takes its constant from UNIVERSE_START onward
  while the fallback draws from all of a symbol's full days; the ruling is exact per branch.
  Ruling R-K: under null A every symbol has ONE expected daily log return c in every month, c = its
  mean over all its fully active source days (the set its fallback draws from). A world day that uses
  the world's shared source day drawn from a set Q (POOL(m), or the whole period for an unpooled
  month) gets c minus the symbol's mean over the fully active days of Q, spread evenly over the day's
  24 hours and applied to the open-relative gap ratio, so every bar keeps its source shape; a
  fallback day gets nothing (its expectation is already c). Shared source days, intraday paths,
  funding and null B are unchanged.
- Dilution of the null pass bound (coordinator, from the Q3 rows and the sealed core artifact; ruling
  R-L, fix pass 7 ordered). In the top30 null worlds 13 of the 36 submitted pairs per null have a
  positive DEV Sharpe (12 momentum, 1 carry): reversal and carry can never pass there, so a bound of
  3% over SUBMITTED pairs allows the one family that can pass a rate of 9%, and that family passes
  every other gate, so its rate is the level of G6 itself. In the core artifact the five families
  have a positive DEV Sharpe in 48% to 89% of their pairs and the worst family's rate at the sealed
  0.10 is 4.67% (14 of 300). Ruling R-L: in addition to the pooled bound, no single family's null
  pass rate (per its own submitted pairs) may exceed FAMILY_PASS_MAX = 0.06 under either null at the
  chosen threshold. 0.06 is the conventional 5% level plus a sampling allowance: with 200 worlds a
  family with a true rate of 4.5% is accepted in about 88% of runs per null, one with 9% is refused
  in about 91%. The rule can only lower a threshold. On the stored core rows it changes nothing.
  KP-016 (count over DEV-positive pairs) stays open as the stricter alternative: on the stored core
  rows it gives 0.05 instead of 0.10 (rates 3.85% and 3.10% at 0.10, 2.27% and 1.59% at 0.05; power
  at 0.05 is 81% to 90.5%), and in top30 it would put the bound of 3% on a family whose rate is the
  test's level, which leaves only 0.025 and, at 200 worlds per null, fails a valid test at that level
  by chance in about four runs in ten. The artifact will store the per-family rates and the rate over
  DEV-positive pairs next to the rule's.
- Reading of the next measurement (X11, on the fix pass 7 commit), fixed here before it runs. Size,
  24 null worlds per null with all three families: no re-key if under either null the momentum
  family's Tier-1 count is 3 or more of 24 at 0.025 or 4 or more of 24 at 0.05 (either has a chance
  of about 2% to 3% for a test whose pass rate equals its level); a Tier-1 pass of reversal or carry
  is reported as a finding. Power, the two null A cells again (24 worlds; the null B cells of X10
  stand once one of their worlds is shown to reproduce): the rule of X10 unchanged. The null B slow
  cell is 14 of 24 at 0.025, so the best possible reading is MARGINAL and the owner gets the odds of
  a successful seal with the request for approval.
- Not probed in X10: anything on real price rows; the fixed null A for the oracle cells and for
  reversal and carry; the spawn-worker path (the in-process path reproduced the pilot exactly); the
  core unit; G8.
- Detail: `audits/round7_findings.md`, replaced by the auditor's file with the X10 sections appended
  (sha256 52b232782cc934770407db4faba0762ac270e2d759ea2fba547a3bfac7fec45c).

## Round 7, addendum X11 - 2026-11-21 - fix pass 7 and 7b re-measured: commits ead27c6 and 58ba59e (unlocked, branch kp015-build)
- Verdict: 58ba59e NOT READY for the re-key (the auditor's judgment and the coordinator's). No code
  defect and no false-pass risk were found. By the rule fixed in the X10 entry the measurement reads
  MARGINAL (size not triggered; two power cells under 15 of 24 at 0.025, none at or under 10 at 0.10),
  which sends the odds to the owner. The auditor's odds of a successful seal are about 1 in 10 (range
  0.05 to 0.25), most likely a STOP on the momentum family's bound under null A after the full run,
  so the coordinator does not ask for the re-key. The size trigger of that rule was too loose: 3 of
  24 is 12.5%, while the seal's own family bound is 6% of about 200 pairs. The auditor worked on a
  verified copy of ead27c6 (143 blobs), read the 7b delta, and wrote nothing in the project.
- Coordinator's review of fix pass 7 before the measurement (read: the whole diff of 6d9fb34 to
  ead27c6 in omr/, the new tests' intent). R-K and R-L were built as ruled. Two defects found and
  fixed in 7b: the rule's two new bounds were written as "missing or above", under which a NaN rate
  qualified (now every bound holds only when the value IS inside it); the DEV-positive count read
  the gate with `is True` (now by truthiness, as tier_at reads it). The builder's re-read found the
  same weakness in the power and level bounds and in the oracle advisory (fixed in 7b). Full suite at
  58ba59e: 864 passed, 0 skipped; ledger verify OK.
- X11 Part A (the auditor, by reading and probes). R-K is exact: its own enumeration from the source
  rows equals sym_c and pool_adj; the expected day log return minus c is at most 3.5e-18 over 7,295
  (set, symbol) pairs, members or not (without R-K: SD 0.98 a year over all symbols, 0.63 over
  members); the draws are unchanged (0 of 134 symbols differ), null B tables are byte-identical, the
  null A tables differ only by the intended factor, and a one-worker spawn pool gives the in-process
  result bit for bit. R-L binds as designed (12 of 200 accepted, 13 refused; an unknown family or a
  text p value gives the "malformed" STOP). 7b is sound. The world builders are byte-identical in
  ead27c6 and 58ba59e, so the measurements stand for 58ba59e. Notes without action: a symbol's first
  world row loses 1/24 of its adjustment; 0.16% of symbol-days are partial and get a proportional
  share; 9 (set, symbol) pairs have 1 to 5 full days (adjustments up to 6.1% a day, exact in
  expectation); pool-specific volatility remains (SD 0.028 on synthetic prices, larger on real ones).
- X11 Part B, size (the X10 source: real structure, synthetic iid prices; every pair submitted).
  Tier-1 at 0.025 / 0.05 / 0.10. Null A, worlds 11000-11023: momentum 2 / 3 / 5 of 24, reversal 0,
  carry 0 (pooled 2.8 / 4.2 / 6.9% of 72). Null A, 24 further worlds, momentum only (the auditor's
  extension): 2 / 3 / 4. Null A momentum over all 48: 4 / 6 / 9 = 8.3 / 12.5 / 18.8%, and the p values
  are U-shaped (9 of 48 at 0.10 or under, 7 of 48 at 0.90 or over). Null B, worlds 14000-14023 (the
  first 12 are X10's rows; world 14000 reproduced exactly): momentum 0 / 1 / 2 of 24, reversal 0,
  carry 0; p values concentrated around one half. Positive DEV Sharpe: 23 momentum and 1 carry of 72
  pairs under null A, 24 and 1 under null B, reversal never. In the 24 listed null A worlds the
  momentum family's chosen window is 30 to 59 days in every world and its VAL Sharpe is 1.15 to 3.63.
  On seeds 11000-11011 R-K moved the Tier-1 count at 0.10 from 8 (X10) to 2. On the kernel's dry-run
  universe: momentum 0 / 0 / 0 of 12 under null A.
- X11 Part B, power (Tier-1 of 24 at 0.025 / 0.05 / 0.10; level 1.5; 200 lags). Null A re-measured
  under the fixed null A: fast 17 / 19 / 19 (rho 0.049125), slow 12 / 15 / 18 (rho 0.089125). Null B
  stands from X10 (world 18000 reproduced exactly): fast 17 / 20 / 20, slow 14 / 15 / 17. G6 alone:
  19 / 23 / 24, 12 / 16 / 20, 19 / 23 / 23, 16 / 19 / 21.
- The auditor's odds (its model: only momentum can pass in null worlds, so the binding bound is
  momentum at 12 or fewer of about 200 pairs per null; rates from its 48 and 24 rows; each power cell
  from its 24 worlds, measured on 100; the core unit seals with probability 0.95). Threshold chosen:
  none 0.72, 0.025 0.25, 0.05 0.03, 0.10 0.00; power in all four cells given 0.025: 0.28, given 0.05:
  0.74; P(seal) 0.09. With a momentum rate exactly at the test's level the same model gives 0.56.
- X11-F1 (the auditor, HIGH, process, no false-pass risk): the momentum excess under null A is
  reduced, not gone. Its suggested mechanism (6 worlds per null, "suggestive only"): null A draws
  days WITH replacement from a pool, so a source day inside a 50-day window can recur in the holding
  period, and lagged signals from other pools share fewer such days; the 50-day signal's correlation
  with the next day's return is 0.025 at lags 0 and 60 days and 0.020 at 180 and 365 days under null
  A, flat (0.019 to 0.022) under null B. Its suggested fix: draw without replacement inside a pool.
- Coordinator's review of X11-F1 (read: UWorld.__init__, _source_days and _build; upipeline g6_lags,
  g6_books, g6_paired_p and ugates; the family program; the engine's accounting; the auditor's rows).
  (1) The suggested fix is not adopted. A world day's source day is one independent uniform draw, so
  after R-K the expected product of a window return and a later day's return is the same at every
  lag: a repeated source day is part of independent sampling, not a separate effect. Drawing without
  replacement inside a pool would ADD a dependence (a day drawn early is missing later: a covariance
  of minus the variance over N - 1 for every pair of days of one pass through a pool of N days),
  about as large as the effect it is meant to remove, in favour of the reversal family, and it would
  leave the pool boundaries as they are.
  (2) A hypothesis for the excess, ordered to be tested (D2 below): G6 draws its 200 lags uniformly
  between 30 days and half of VAL (547 days). Lagged copies of a 50-day momentum book at lags closer
  than 50 days share most of their windows, so the 200 lagged Sharpe ratios hold only about ten
  independent values; the actual book is then first or second among them about 1 time in 11 and 2 in
  11, not 2.5% and 10%. That is what the 48 worlds show (8.3% at 0.025, 18.8% at 0.10, and the same
  excess at the other end). Under null B the lagged copies differ from each other for reasons fixed
  by the real calendar, which would hide it. If confirmed it is a property of G6 for slow books, not
  of null A, and becomes a recorded limitation and a proposal of its own.
  (3) The root of the certain STOP is neither of these: BOTH nulls hand the momentum family a
  premium. In the null worlds its VAL Sharpe is about 2, it passes every gate but G6 in 47 of 48
  worlds, its best DEV draw is always a long window, and its mirror, the reversal family, never has
  a positive DEV Sharpe. Cause: both nulls keep each symbol's own sample mean as its expected return
  (null A: R-K's c; null B: the mirror's centre plus the mirror's own drift). A sample mean over two
  to five years is mostly luck: on the auditor's source, whose prices are iid with no true difference
  between symbols, the means still differ by 0.6 to 0.7 a year, and every world resampled from that
  source turns the luck into a permanent difference that a slow momentum book learns and collects.
  (The known bias of a bootstrap that keeps sample means: Conrad and Kaul 1998, Jegadeesh and Titman
  2002; cited from memory, not re-read.) A no-skill world must not contain it. With it the momentum
  family's Tier-1 rate is G6's own false-pass rate, the family bound can admit only the smallest
  thresholds, and there the slow oracle cells sit at 12 and 14 of 24.
- Ruling R-M (replaces R-K; fix pass 8 ordered): in both top30 nulls the expected gross return of a
  day is ONE number G for every symbol on every world day. Day gross = the product of the day's 24
  hourly close over previous close ratios; G = its mean over all fully active symbol-days of the
  source. Null A: with M(Q, s) = the mean day gross of s over the fully active days of the set Q it
  draws from (POOL(m), or the whole period) and M(s) = its mean over all its fully active days (the
  set its fallback draws from), every active row of a shared-branch day has its open / previous
  close ratio multiplied by (G / M(Q, s))^(1/24) and every active row of a fallback day by
  (G / M(s))^(1/24). Null B: for symbol s and day d with n active rows, x = the day's sum of (hourly
  log return - m), m the symbol's mean hourly log return as before; every active row of the day, on
  either face of the coin, has its open / previous close ratio multiplied by
  G^(1/24) * exp(-m) * cosh(x)^(-1/n), so the day's gross is G^(n/24) * (1 + tanh(x)) or
  G^(n/24) * (1 - tanh(x)) and its expectation over the coin is G^(n/24) whatever the path (the log
  mirror's own drift, half the squared day move, goes with the mean). High / open, low / open, close
  / open, the shared source days, the funding and its sign coin are unchanged; so is the core unit.
  Simple returns are equalised, not log returns, because the engine holds positions between
  rebalances and the family's signal is an n-day simple return: with one expected day gross and
  independent days, the signal's expectation and a held position's expected profit are the same for
  every symbol, so a market-neutral book fixed before the day has no expected profit. Not equalised:
  hour-of-day means and the path inside a source day (both nulls keep them by design). Said plainly:
  R-M makes the null worlds more correct AND makes the seal easier to reach; the alternative is to
  keep the worlds as they are and accept that top30 cannot be sealed with the present grid and
  power. The owner is told both with the request for approval.
- Also ordered in fix pass 8. tier_at STOPS on a malformed row instead of reading it: a missing gate
  key, a gate that is not a boolean, or a p that is not a finite number raises, and the unit verdict
  becomes the "malformed" STOP. Counting such a row as "not passing" (the auditor's suggestion) is
  not adopted: for a null row that is the loose direction. unit_verdict catches every Exception. An
  advisory during the null phases when the pooled or a family bound can no longer be met at any
  threshold, so that a run that must STOP can be interrupted early.
- Ordered from the auditor before the next measurement: an attack on R-M and on points (1) to (3);
  D1, the momentum family on the iid source HISTORY itself against its null worlds (expected: about
  zero against about 2); D2, the lagged Sharpe ratios of a null A momentum book along the lag axis
  (how many independent values they hold).
- Reading of the next measurement (X12, on the fix pass 8 commit), fixed here before it runs. Source:
  the real structure with the real prices of the DEV period, and every price ratio and funding rate
  after DEV end replaced by real DEV-period days of the same panel drawn in blocks, so that the
  source has real volatility clustering and tails and no real VAL price; plus a control of 12 worlds
  per null on the X10 source. Size: 48 worlds per null, all three families. Power: the four cells,
  24 worlds each. The auditor's odds model of X11, written down before the run, gives P(seal). At
  0.70 or more the coordinator asks the owner for the re-key with the odds; between 0.40 and 0.70
  the owner gets the odds with the coordinator's advice not to run yet; under 0.40 not ready. To be
  explained before any re-key whatever the odds: a family whose mean VAL Sharpe over its null worlds
  is above +0.5 under either null (a premium remains), or a family at 4 or more of 48 at 0.05 under
  either null.
- Not probed in X11: anything on real price rows; the core unit's re-run; G8; a full multi-worker
  calibration (one spawn worker only); the without-replacement variant; the mechanism of X11-F1
  beyond the 6-world check.
- Detail: `audits/round7_findings.md`, replaced by the auditor's file with the X11 section appended
  (sha256 b8c0c3f86513ab0f282887c981d608c65cbfbc1ceb3df1acfda09f31ca1fdfca).

## Round 7, addendum X12-prep - 2026-11-21 - fix pass 8 built (258c1a5, 1442b42); the auditor's attack on R-M, D1 and D2; ruling R-N
- State: fix pass 8 is built and committed (stage A 258c1a5, stage B 1442b42: R-M in both nulls,
  tier_at stops on a malformed row, unit_verdict catches every Exception, the null advisory; full
  suite 891 passed, 0 skipped; against 258c1a5 the kernel changed by five docstring lines).
  Coordinator's review of the kernel diff 2dd58a2 to 258c1a5: built as ruled, no defect found. The
  builder reported, and the coordinator accepted, one inexactness: the day's factor sits on the gap
  ratios of the day's own rows, so a position opened at a day's first open holds 23/24 of that
  day's factor and 1/24 of the next day's (largest measured per hold: about 0.43% on a 60-symbol
  dry-run source, 0.08% on the test source). The measurement X12 has NOT run: the auditor stopped
  after its attack, as the coordinator's condition asked. Still NOT READY for the re-key.
- The auditor on the coordinator's three points of the X11 entry. (1) Without replacement: agreed;
  it withdraws its X11 mechanism and its fix (independent draws have zero covariance between
  different days; its 6-world difference was within noise). (2) G6's independent lags: confirmed
  by D2. (3) The premise was WRONG and is corrected here: the X10 / X11 source is not "iid with no
  true difference between symbols". Its generator (the kernel's own dry-run universe) gives every
  symbol a constant true drift with an SD of 0.70 a year; the spread of the sample means (0.78) is
  mostly that true drift, and sampling noise over about four years adds about 0.37.
- D1 (the momentum family on source HISTORIES, not null worlds; the calibration's protocol). Nine
  draws of the X10 generator: VAL Sharpe 0.38 to 2.18, mean 1.23 (n fixed at 50: mean 1.35); every
  other gate passes in 7 of 9. The X11 null worlds built from one of them: median 1.9 (null A) and
  2.2 (null B). A drift-free source: history -0.08 (n = 50: 0.17); six null A worlds under R-K mean
  0.02, six null B worlds mean 0.22. Reading: the coordinator's prediction (about zero on the
  history against about 2 in the worlds) does not hold on that source; most of the X11 premium was
  the source's true drift, which both nulls kept, and the part that is luck made permanent is small
  there (about 0.1 to 0.2, more under null B). R-M stands for another reason than the one written
  in the X11 entry: a world that keeps each symbol's sample mean as its expected return holds a
  permanent difference between symbols, luck or not, and in it ranking on past returns is a real
  forecast; that is a premium world, not a no-skill world. How much of the real symbols' mean
  spread is luck is not known (real DEV rows: 1.18 a year over at most two and a half years of
  history, which sampling noise alone can produce at real volatility).
- D2 (the lag axis; 8 null A and 4 null B momentum worlds of X11, 200 lags each, p values
  reproduced). Correlation of two lagged Sharpe ratios by the distance between their lags: +0.87
  (0 to 10 days), +0.50 (10 to 25), +0.07 (25 to 50), about zero beyond (null B: +0.81, +0.50,
  +0.09). So the 200 lags of a book with a window of 37 to 60 days hold about 11 to 14 independent
  values: point (2) is confirmed as a property of G6 for slow books, not of null A. The actual
  book is first among them about 1 time in 13 at any threshold under about 0.08 and first or
  second about 1 time in 6 at 0.10. (The auditor also reports a mean gap of +0.25 between the
  actual book and its copies and a wider spread across worlds than across lags; the 12 worlds
  were picked by the coordinator from both tails of the p values, so neither number is an
  estimate. The premium arm below measures it on unselected worlds.)
- The auditor's verdict on R-M: a correct no-skill world (one expected simple day gross is the
  right quantity for this engine and these signals; the null B algebra is right), but NOT
  sufficient for the seal. Under R-M the null worlds no longer measure what G6 does with a slow
  book that collects a real premium without timing; for such a book Tier 1 rests on G6 alone, and
  D2 says G6 passes it about 1 time in 12 below 0.08 and 1 in 6 at 0.10 whatever the threshold.
  Its proposals: a G6-only bound on a premium arm, or a recorded limit and a bound on lookbacks.
  New or remaining artifacts it lists under R-M, none checked yet on R-M worlds: pool-specific
  volatility; in null A a pool with one extreme up day gives the symbol a steady negative drift on
  its other days (a negatively skewed payoff for a short, which may raise G1 pass rates); in null B
  the day's own move enters every hour of that day (below one trade's cost) and up days are
  compressed (the day gross is at most twice G).
- Coordinator's ruling on the objection: accepted. The seal must not be made reachable by no longer
  looking at a known weakness of G6, and by the project's own rule a known fault of a gate is
  fixed before the first scored generation on the unit, not after. A bound on a premium arm cannot
  be met by choosing a threshold (the excess does not depend on it), so G6 itself is changed.
  Ruling R-N (fix pass 9 ordered; top30 only, the core unit's G6 unchanged):
  (a) K = 20 lags, EQUALLY spaced by step = (half of VAL - 30 days) / 20 (about 26 days), from 30
  days plus one random phase; p = (1 + number of lagged books at least as good) / 21 as before. So
  0.05 means no stale copy as good as the actual book, 0.10 at most one; 0.025 cannot be reached
  (power there is 0, so the seal cannot choose it for this unit).
  (b) A speed limit: with each name's own mean over VAL removed, the correlation between the
  program's weights and its own weights j steps earlier (the names in play at both rows) must be
  at most 0.5 for every j from 1 to 19; otherwise G6 fails (p = 1): its stale copies would not be
  independent comparisons, and three years of VAL cannot test a slower book for timing. An
  undefined correlation (a book that never changes) counts as above the limit.
  Why these numbers, to be checked by measurement before they are final: copies of a 50-day book
  26 days apart share about half their window, and D2 gives a correlation of their Sharpe ratios
  of about a quarter there; 20 is the largest spacing-first count at which 0.05 can still be
  reached. What it costs: books slower than about 50 days cannot be Tier 1 in top30; the timing
  gate's resolution is two steps. What it gives: a p value that means what it says for every book
  it admits, and a G6 with 20 engine pairs instead of 200 (the calibration gets several times
  shorter). What stays true and will be said to the owner: at the threshold that keeps power
  (0.10), a book that earns a steady premium with no timing passes G6 about 1 time in 10; with
  three years of VAL the gate cannot be both stricter than that and sensitive. G6 never protected
  against plain luck in VAL (stale copies do not share the actual book's luck); that rate is what
  the R-M null worlds measure and the seal bounds.
- Source D (for the measurement; the auditor's construction): the real structure; real prices and
  funding rates up to DEV end; after DEV end one shared sequence of 20-day blocks of real DEV
  days. 45% of the symbol-days after DEV end need a donor (47 symbols were listed after DEV end).
  The donor rule the coordinator specified (one donor per symbol, same day) makes clones (60% of
  those paths are copies); the auditor's third rule (donors at least 80% fully active and still
  listed at DEV end, the donor's day moved to a different DEV day) has none and is taken: absolute
  return autocorrelation 0.162 / 0.063 / 0.007 at lags 1 / 5 / 20 (real DEV rows 0.169 / 0.096 /
  -0.003), 0.1% and 99.9% day returns -0.43 and +0.37 (-0.49 and +0.42). No real price or rate
  after DEV end reaches it (the auditor's scramble check: all 27 source arrays identical).
- Reading of the next measurement (X12, replacing the rule of the X11 entry where they differ),
  fixed here before it runs. The auditor measures on a verified copy of 1442b42 with only the lag
  rule of R-N patched in, for K = 20 and K = 40, and applies the speed limit from the weights:
  (N) no-skill size: R-M worlds on source D, 48 worlds per null, the three families; control 12
  worlds per null on the X10 source. (W) power: the four cells, 24 worlds each, on source D.
  (P) premium arm: the momentum family in the 58ba59e worlds (kept means) on the X10 source (48
  null A, 24 null B) and on source D (24 per null): G6 passes among the rows that pass every other
  gate, by K and by window, on unselected worlds.
  Choice of K, fixed now: K = 20 if every power cell has at least 14 of 24 at 0.10; otherwise
  K = 40 if it has; otherwise not ready. To be explained before any re-key whatever the odds: in
  (P), among admitted books (speed limit met), a G6 pass rate at 0.10 that a true rate of 10%
  would produce in fewer than 1 run in 20; in (N), a family whose mean VAL Sharpe is above +0.5
  under either null, or a family at 4 or more of 48 at 0.10 under either null. Then the odds from
  the auditor's model, written down before the run: at 0.70 or more the coordinator asks the
  owner; 0.40 to 0.70 the owner gets the odds with the advice not to run yet; under 0.40 not ready.
- Texts to correct in fix pass 9: the "mostly luck" sentence in CONSTITUTION section 13 and the
  "no true difference between symbols" clause in the fix pass 8 entry of KERNEL_PROPOSALS.md rest
  on the premise corrected above.
- Detail: `audits/round7_findings.md`, replaced by the auditor's file with the X12-prep section
  appended (sha256 b63473f329c1202d1ec44ff69776287b494aca590a7f31cf6bd73eb7dd3a86e3).

## Round 7, addendum X12 (power arm) - 2026-11-21 - fix pass 9 built (9ca8b62, db32ce2); power on real DEV-period prices stops on null B liquidations; rulings R-O and R-P
- State: fix pass 9 is built and committed (stage A 9ca8b62, stage B db32ce2: R-N as ruled,
  universe protocol version 7, full suite 895 passed, 0 skipped). Coordinator's review of the
  kernel diff 1442b42 to 9ca8b62: built as ruled, no defect found (the lag set, the memory
  statistic against the ruling's formula, the positive form of the limit test so that a NaN
  counts as over the limit, the gate record). The measurement X12 ran its first arm and stopped,
  as its rule says: NOT READY.
- The auditor's attack on R-N, written before the runs: no flaw that changes the design. The
  memory statistic measures what is claimed (the weight correlation one step apart is about the
  window overlap). Correction of the stated reason: at a memory of 0.49 to 0.53 the correlation
  of adjacent lagged Sharpe ratios is 0.35 to 0.46, not "about a quarter". Simulated rank test
  with that dependence: K = 20, chance of p <= 0.05 is 0.055 to 0.061 (level 0.048) and of
  p <= 0.10 is 0.105 to 0.110; so books just under the limit carry a small excess. At K = 20 the
  limit admits every momentum window of the calibration family (60 days sits at the limit and is
  admitted in about half the worlds); at K = 40 only windows up to about 28 days. What R-N cannot
  remove, and the premium arm measures: the actual book's own luck may be wider than the spread
  of its copies.
- The auditor's reading of fix pass 8 (58ba59e to 1442b42): R-M exact (the common day gross
  reproduced; expected day gross off by at most 2.2e-16 over 7,295 set and symbol pairs in null
  A; null B day products to 7.8e-15); the draws unchanged; tier_at, unit_verdict and the null
  advisory sound.
- W, power (R-M worlds on source D, the calibration's own tuning, 24 worlds per cell, Tier-1
  counts). Null A: fast 15 / 16 at 0.05 / 0.10 with K = 20 and 12 / 14 / 15 at 0.025 / 0.05 / 0.10
  with K = 40; slow 11 / 16 and 10 / 13 / 15; no book liquidated. Null B: 16 of 24 fast books and
  18 of 24 slow books LIQUIDATED; of the rest fast 5 / 6 of 8 (K = 20), slow 3 / 3 of 6. No
  oracle book is over the speed limit (largest memory 0.36). By the rule fixed in advance no K
  qualifies: STOP.
- Finding W-F1 (HIGH). Cause, read in the code by the coordinator as well: the real evaluation
  takes the liquidation wicks from the MARK price bar (last price only where a bar has no valid
  mark row), and so do the core calibration's null worlds, which carry the mark wicks and mirror
  them; the top30 null worlds alone used their own last-price bars for it (UWorld._build), under
  a docstring that called this conservative. Null B mirrors a flipped bar's shape (high / open =
  1 / (low / open)). The real DEV rows hold two last-price bad prints: 2020-03-13 02:00 UTC with
  low / open 0.00206 and 2020-04-14 07:00 UTC with 0.00136, on symbols ranked 22 and 11 by volume
  that day (top30 members, not core or extended symbols). Flipped they become highs of 485 and
  736 times the open and liquidate any short above 0.2% of equity. Both bars have a valid mark
  row with ordinary wicks (mark low / open 0.848 and 0.987, high / open 1.262 and 1.005): the
  real evaluation never saw either print. Source D repeats both days after DEV end, which gives
  four exposure points; predicted share liquidated 68%, observed 71%. Earlier sources had
  synthetic prices and no such bar, so no earlier round could see it.
- Correction to "no false-pass risk": the shortcut is not conservative in either direction.
  Liquidated books cannot pass, so it lowers the power (tight) AND the null pass rate (loose: the
  rule divides the passes by the submitted pairs). In the auditor's null B size run so far, 34 of
  48 submitted pairs are liquidated and Tier 1 reads 0 at every threshold: a null side that says
  "every threshold qualifies" while 71% of its rows are gone. Here the power bound would have
  stopped the seal; a milder dose would have loosened it quietly.
- Facts the coordinator asked for before ruling (the auditor's read-only reader). DEV, active
  rows, the ratios the real pipeline uses (mark where valid, else last): no row with low / open
  at or under 1/5, one with high / open at or above 5 (6.99, a mark bar); smallest low / open
  0.271; 3,162 rows without a valid mark row, all of 2019. From 2022-07-01 to VAL end, COUNTS
  ONLY, by the coordinator's decision recorded here (no program, oracle or family is evaluated
  and nothing but counts leaves the reader; the count answers whether the real calibration would
  meet the same wall): panel 2,781,983 rows, none without a mark row, none at 1/5 or 5; all
  perpetuals 6,330,192 rows, 2 without a mark row, 1 at or under 1/5, 1 at or above 5, none in
  the panel.
- Ruling R-O (fix pass 10 ordered; top30 calibration worlds only): a null world's liquidation
  check reads what the real evaluation reads. The source carries per row hm and lm, the up and
  dn of datasets.liquidation_ratios on the rows where it has a mark bar, else NaN. On an active
  world row whose source row (null A: the drawn day's row; null B: its own) has them, the world's
  mark bar has high = open * HM and low = open * LM, with (HM, LM) = (hm, lm), and (1 / lm,
  1 / hm) on a flipped null B row; every other row of the mark table is the last-price bar as
  before; mark open and close stay the last-price open and close; the index table stays the same
  object. Left as it is and said in the docstring: a row without trades stays flat in the world
  although the real evaluation would read its mark wick (40 DEV rows on the panel). The source
  records the count of active rows without mark ratios and the two extreme effective ratios; the
  run prints them.
- Ruling R-P (same fix pass; calibrate.decide, both units): a null under which more than
  NULL_LIQUIDATED_MAX = 0.03 of the submitted pairs are liquidated fails every threshold (STOP).
  A liquidated pair cannot pass, so liquidations lower the null pass rate; the rule must not
  read that as safety. Fail-closed like the other bounds. Power needs no such rule. tune_rho
  keeps its rule (it averages the surviving books); the count of liquidated tuning books is
  recorded.
- Residual exposure after R-O, by the auditor's count: the largest mirrored high in DEV is about
  3.7 (a single short would have to be about 36% of equity), and no panel row after DEV end
  reaches 1/5 or 5. Under null A a row can change only through a liquidation flag (the equity
  path reads opens and closes only); mark wicks lie outside the last-price wicks by more than
  10% on 8 panel rows in DEV.
- The measurement goes on, on the auditor's copy patched from the ruling text alone (source D
  gets the mark bars of its donor days; the X10 source empty mark tables): W null B first, then
  the size arms, the premium arm and the odds. Added to the reading rule fixed in the X12-prep
  entry, before any result: after R-O on source D, a power cell with 2 or more of 24 books
  liquidated, or a null with more than 1 liquidated row among its 144 submitted pairs, is to be
  explained before any re-key. The null A rows measured before R-O stand only if they reproduce
  bit for bit on the final commit.
- Texts to correct in fix pass 10: "about a quarter" in the reason given for the speed limit
  (CONSTITUTION section 13 and wherever it was copied) becomes the measured 0.35 to 0.46; the
  "conservative" sentence of the ucalibrate docstring.
- Detail: `audits/round7_findings.md`, replaced by the auditor's file with the sections on the
  attack on R-N, Part A, W, W-F1 and X12-RO appended (sha256
  435241d581fe80594db20044cf7b91ab4b7e02dc26c5d303a653a572ed0320ad).
