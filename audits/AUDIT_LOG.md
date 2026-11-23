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
- Refinement of R-P, made the same day before anything was built on it (this entry was committed
  as 8bfabc4 with the narrower wording above): the bound counts every submitted pair whose status
  is not "evaluated" (liquidated, a kernel fault or anything else), since none of them can pass;
  the constant is NULL_NOT_EVALUATED_MAX = 0.03. The builder and the auditor both work from this
  form.
- Early warning from the size arm, same day, and ruling R-Q. In the auditor's null A size run (20
  worlds so far, on the copy before R-O) the carry family is liquidated in 5 worlds; in each of
  them EVERY screened draw was liquidated on DEV (best DEV Sharpe -inf) and the pair was still
  submitted, because task_null keeps the first screen passer whatever its DEV Sharpe (a first NaN
  could never be replaced either). A pair that nobody would submit then counts as a submitted
  pair that cannot pass: it pads the denominator of the null pass rate, the loose side again.
  Ruling R-Q (fix pass 10, both units): a screened draw that is liquidated on DEV, or whose DEV
  Sharpe is not a finite number, is not a candidate; the best finite DEV Sharpe among the rest is
  submitted; a pair without a candidate is not submitted. The draws are unchanged, so a pair with
  a finite best submits the same draw as before. R-P then reads only the pairs that end without a
  result after DEV. Open, with the auditor: why the carry book is liquidated on DEV at all under
  null A (its guess: one name with extreme funding holds about half the gross, the R-E sign coin
  puts the book short that name half the time, and a real up-wick does the rest), whether R-O
  changes it, and whether what remains is a realistic property of a concentrated book or a
  property of the null world.

## Round 7, addendum X12 (size arm) - 2026-11-22 - fix pass 10 built (306eb8c, 76765ce); the pilot reads NOT READY; one reused DEV bar; a gap in the rule after R-Q

- State. Fix pass 10 was built from the ruling texts: stage A `306eb8c` (R-O in
  `omr/ucalibrate.py`: the source keeps hm and lm per row, the world's mark bars carry them, the
  loader reads mark_klines with the logged handle, universe protocol 8; R-P in `calibrate.decide`
  and R-Q in both task_null, core protocol 5; NULL_NOT_EVALUATED_MAX = 0.03), stage B `76765ce`
  (full suite 910 passed, 0 failed, 0 skipped in 2139 s on 306eb8c; 15 tests new). Coordinator's
  review of the kernel diff, line by line: built as ruled, no defect found. The auditor measured
  on its own copy (1442b42 with R-N, R-O and R-Q patched in from the ruling texts alone); its
  bit-for-bit runs on 306eb8c are still to come.
- W, the power arm after R-O (24 oracle books per cell at Sharpe 1.5, K = 20, counts at 0.05 and
  at 0.10). Null A (copy before R-O; no book liquidated): fast 15 and 16, slow 11 and 16. Null B
  on the R-O copy: fast 12 and 15 (rho 0.046750), slow 14 and 16 (rho 0.081875); 0 of 48 books
  liquidated (34 of 48 before R-O); largest memory 0.37. The rule fixed in the X12-prep entry for
  the number of lags (every power cell at 14 or more of 24 at 0.10) is met: 16, 16, 15, 16. K =
  20 stands. With K = 40 the same books give 15, 15, 15, 16 at 0.10.
- The carry liquidations under null A, the question left open in the last entry. Every one that
  remains comes from one source bar, 2022-05-11 13:00 (effective up 4.895 by mark, 5.52 by last
  price). The carry book is short that name at w = -0.33 to -0.42 because the R-E sign coin flips
  a real funding of -0.41% per 8 hours; a real carry book would be long there. Coordinator's
  judgment, with the auditor: a property of the null world, not of the book or the engine; R-Q is
  the treatment (the pair drops out of numerator and denominator alike; about a quarter of the
  null A carry pairs, 12 of 48); the family cannot pass anyway (mean VAL Sharpe -1.44 under null
  A). No kernel change for it; one limitation sentence goes into CONSTITUTION section 12 in the
  next pass. DEV panel rows with effective up of 3 or more: three (4.895 and 4.873 on that name;
  6.987 on 2022-06-07 20:00 on another). After DEV end, counts only: 1 row at 3 or more, none at
  4 or more, none with dn at 1/3 or less.
- N, the size arm (48 worlds per null, three families, K = 20 with the speed limit). Per family:
  not submitted under R-Q / evaluated / not evaluated after DEV; Tier-1 at 0.05 and at 0.10; mean
  VAL Sharpe.
  Null A (copy before R-O, read under R-Q): momentum 0 / 48 / 0; 1 and 1; -0.26. Reversal 0 / 48
  / 0; 0 and 0; -0.66. Carry 12 / 36 / 0; 0 and 0; -1.44. R-P: 0 of 132.
  Null B (copy with R-O and R-Q): momentum 0 / 45 / 3; 0 and 0; -0.51. Reversal 5 / 38 / 5; 0 and
  0; -0.24. Carry 7 / 41 / 0; 0 and 0; -1.49. R-P: 8 of 132 = 6.1%, above 0.03: on source D null B
  fails every threshold.
  Triggers of the reading rule: no family has a mean VAL Sharpe above +0.5 and none is at 4 or
  more of 48 at 0.10 under either null; null B has more than 1 liquidated row among its submitted
  pairs, to be explained before any re-key.
- The explanation (auditor's diagnostic p53). All 8 rows (reversal in five worlds, momentum in
  three) are liquidated at the same world bar, in the part after DEV end, on a day that is not
  flipped. That bar is source D's copy of the real DEV bar 2022-06-07 20:00, the only DEV panel
  bar above 5 times the open (effective up 6.987 by mark, 7.56 by last price; mark and last price
  agree, so R-O rightly leaves it). Every one of the 8 books is short that one name as its largest
  position, w = -0.16 to -0.34 (contribution -0.98 to -2.00 of equity; the next largest -0.005 or
  less); a lone short is liquidated at that bar from w = 0.975 / 5.99 = 0.16. Source D's block
  sequence places that DEV day exactly once after DEV end. In the real run the bar exists once,
  at its own date, in DEV; a draw it liquidates is not a candidate (R-Q) and R-P never sees it.
  After DEV end the real panel has 1 row at an effective up of 3 or more and none at 4 or more, so
  a lone short would need w of 0.33 or more; one of the 8 books (w = -0.335) reaches that.
  Accepted: the 8 are a property of the pilot's source (its days after DEV end are DEV days, and
  DEV holds the wilder bars), not of the kernel.
- The odds, from the auditor's model written before the run (K = 20, W and N as measured, 200
  null worlds and 100 oracle worlds per null, core 0.98): 0.02 as measured (R-P fails null B in
  95% of the simulated runs); 0.31 with the 8 counted as none (0.10 chosen in 38% of runs, 0.05
  in 33%, neither in 28%). Named limits: the pooled 3% and momentum's 6% under null A (1 of 48,
  and a prior that leaves a family without a pass at about 2%), and the power at 0.05 (null A
  slow 11 of 24).
- Reading, by the rule fixed in advance: under 0.40 either way. NOT READY. The owner is not
  asked for the re-key.
- A gap in the rule after R-Q (coordinator, reading `calibrate.decide` against the diagnostic).
  R-Q turns a liquidation on DEV into "not submitted". A breakage like W-F1 whose bad rows lie in
  DEV (both of W-F1's did) would then show as pairs never submitted; R-P counts submitted pairs
  only; decide skips a family without a submitted pair; a null with a handful of submitted pairs
  and no pass qualifies every threshold. Thin evidence would read as safety: the loose side once
  more. And R-P's 3% is a hard stop on a count that one real bar moves by several points (8 of
  132 here): under null B the day order is real, so one bar after DEV end meets every world in
  which its day is not flipped; after R-O such liquidations are real wicks, not artefacts, and a
  liquidated no-skill book is a non-pass in the real evaluation as well.
- Ruling R-R (fix pass 11, both units; replaces the cap of R-P).
  (a) The pooled and the per-family null pass rates are Tier-1 passes over EVALUATED pairs (a
  submitted pair that ends liquidated or faulted leaves the denominator, as a pair never
  submitted already does). Never looser on the rate than before: the passes are the same and
  evaluated <= submitted. A rate without an evaluated pair fails; no family is skipped.
  (b) Evidence floors, under each null: every family must end with at least
  FAMILY_EVALUATED_MIN = 0.50 of its designed pairs evaluated, and the null as a whole with at
  least NULL_EVALUATED_MIN = 0.75 of its designed pairs; below either floor that null fails every
  threshold.
  (c) Faults: the share of submitted pairs whose status is neither "evaluated" nor "liquidated"
  stays bounded at 0.03 (NULL_FAULT_MAX, which replaces NULL_NOT_EVALUATED_MAX), fail-closed on
  the counts as before.
  (d) Designed pairs are the worlds ordered for the null times the families, never the rows that
  happen to be present; the stored null rows must be exactly one per protocol seed and family,
  the oracle rows exactly one per protocol seed, speed and level; a missing, double or foreign
  row stops the unit.
  (e) The seal refuses a calibration whose sizes are not the protocol's (core 300 null worlds per
  null and 200 oracle worlds; top30 200 and 100; kernel constants from now on). Found on the way:
  `check_artifact` and `check_universe_artifact` test neither the sizes nor the row counts, so a
  logged real run made with a reduced --worlds could have been sealed.
- The auditor's attack on R-R, asked for before the build. No unintended loosening on the rate.
  One loss named: R-P's 3% also worked as a sentinel for a milder breakage (5% to 40% of the
  pairs lost with the survivors hurt); its remedy, the floor for the null as a whole at 0.75, is
  adopted in (b). Two traps named and closed in (a) and (d): the designed count must come from
  the protocol, and 0 of 0 must never read as a rate of 0. Its own choice for the family floor
  was 0.60; ruled 0.50, because the pilot fixes carry's share under null A only to 36 of 48 (95%
  interval about 0.61 to 0.85), so 0.60 is a floor the known, harmless loss can touch, and a stop
  for that reason would cost a real run and say nothing about breakage. Shares evaluated of
  designed in the pilot: null A momentum 48, reversal 48, carry 36 of 48, together 132 of 144;
  null B on source D 45, 38 and 41 of 48, together 124 of 144. W-F1 would have been stopped (null
  B before R-O, 16 worlds: 5, 3 and 6 of 16; together 14 of 48). Core, read from the sealed
  artifact `ledger/calibration_7446278556aadd8f.json` (300 worlds per null, five families): every
  family has at least 299 of 300 pairs evaluated under both nulls and evaluated = submitted
  everywhere, so R-R leaves every core rate as it is.
- Reading before the seal, fixed here: after the real calibration and before `kernel_lock seal`
  the coordinator sets every family's evaluated share under each null against the pilot's (null
  A 48, 48 and 36 of 48; null B, with the 8 rows of the replayed bar counted as evaluated, 48, 43
  and 41 of 48) and explains any cell that differs by more than 0.15 before sealing. This is a
  reading, not a bound of the rule: it asks for a cause, it does not stop the seal by itself.
- Open, with the auditor (its reading of the sealed core artifact): core's null A pooled rate at
  0.10 is 44 of 1498 = 2.94% against 3%, one pass to spare (largest family: donchian 14 of 300 =
  4.67% against 6%). After the re-key the core calibration runs again; whether the new kernel
  reproduces the sealed rows bit for bit is being read (the delta from `main` over everything the
  core calibration imports; a fully synthetic dry run under both kernels), with core's power at
  0.05 as the fallback. The answer enters the odds.
- The pilot's size (coordinator's suspicion, the auditor to confirm by the ceiling of its model):
  with 48 worlds per null and 24 books per power cell the model written before the run may not be
  able to read 0.70 for any outcome, the priors of the cells without a pass doing most of the
  work. If so, the rule fixed in the X12-prep entry could only ever say "not ready" or "advice
  not to run": the coordinator's planning error, no property of the kernel. Remedy: ONE extension
  of the pilot on the committed code, sized by a pre-posterior calculation of the same model, its
  size and its reading rule recorded before its first world is built.
- Counts allowed for the exposure after DEV end, in addition to those of the last entry: panel
  rows with an effective up of 2.0, 2.5, 3.0 or 3.5 and more, and with an effective dn of 0.5,
  0.4 or 1/3 and less (counts only; no price, name or date after 2022-06-30).
- Detail: the auditor's findings file is copied into `audits/round7_findings.md` at its final
  report.

## Round 7, addendum X12 (extension) - 2026-11-22 - the odds model opened, the core unit, and ONE extension of the pilot fixed before its first world

- The auditor's odds model, as written before the run and used for the reading of the last entry.
  Per null and family four categories (Tier-1 with p <= 0.05; Tier-1 with 0.05 < p <= 0.10;
  evaluated without Tier-1; not evaluated), posterior Dirichlet(counts + 0.5). A real run draws
  200 pairs per family. Rates over evaluated pairs, pooled 3% and family 6%, floors as in R-R.
  The larger qualifying of 0.05 and 0.10 is chosen (0.025 cannot be reached with 20 lags). Power:
  per cell Dirichlet(counts + 0.5) over the bands, 100 books, at least 50 in all four cells at
  the chosen threshold. Families, nulls and cells independent; core as a factor.
- Its decomposition at the data of the last entry (P(seal) 0.305, the 8 rows out of the
  denominator). At 0.10: pooled bound met with probability 0.58 under null A and 0.72 under null
  B; family caps 0.78 (A momentum), 0.94 (A reversal), 0.88 (A carry), 0.93, 0.89 and 0.91 (B);
  power cells 0.94 (A fast), 0.95 (A slow), 0.89 (B fast), 0.95 (B slow). At 0.05: pooled 0.84
  and 0.94; family caps 0.87 to 0.98; power 0.85, 0.34, 0.49 and 0.75. Threshold chosen: 0.10 in
  37% of the simulated runs, 0.05 in 34%, neither in 29%. The floors never bind. Pairs passing
  every gate but G6: 1 of 264 (null A momentum, p <= 0.05).
- Correction of the coordinator's suspicion in the last entry. The ceiling of the model at this
  pilot size is 0.856 (no pass anywhere, 24 of 24 at 0.05 in every power cell): 0.70 could be
  read, by a nearly perfect outcome, so the pilot's size was not a bar in principle. What holds
  the reading down is the prior mass on the cells without a pass: two Tier-1 bands at +0.5 each
  give a family without a pass 2% at 0.10 on 48 pairs, and three families at that level fill the
  pooled 3%. The auditor's pre-posterior calculation (the truth drawn from that same posterior)
  gives no extension size more than 1 chance in 10 of a reading of 0.70 and a median reading of
  0.25 to 0.29 at every size: the model expects a bad truth two times in three. Coordinator:
  whether the truth is bad is what is not known. The evidence outside the counts (mean VAL
  Sharpe of -0.66, -1.44, -0.51, -0.24 and -1.49 in the five cells without a pass; one pair in
  264 passing every gate but G6) says those cells lie well under 2%. The model is not changed
  after the data; more data decides.
- Core (auditor; reading and fully synthetic runs only). "Core 0.98" in the earlier odds was a
  judgment. The delta from the sealed kernel (`main` 521687f, semantic 7446278556aadd8f) to
  306eb8c over what the core calibration imports: not reachable from it (the universe additions
  in engine, interp, lang, data, the pipeline options, probe); rule-level only, no stored row
  (tier_at moved; null_summary, decide, R-L, R-P); output-changing but without effect on core
  (R-Q: the sealed core artifact has no submitted row with a DEV liquidation; the freshness rule
  of funding_mean: the real BTC and ETH settlements are all 8 hours apart; funding8h freshness
  and index_klines: no core family reads them). Data: the BTC and ETH mark tables grew by about
  288 bars since genesis, klines and funding are identical by sha256, and a core book would need
  a move of about -97.5% inside one bar to be liquidated. Expected: the rows reproduce, hence
  0.10 again. If they did not, core would seal at 0.05: the sealed artifact's power at 0.05 is
  0.84, 0.83, 0.905 and 0.81 (A fast, A slow, B fast, B slow), its null rates at 0.05 are 1.74%
  and 1.20% pooled and 3.0% for the largest family; for a fresh run of the protocol's size the
  model gives 0.10 in 13%, 0.05 in 76%, 0.025 in 11% and P(core seals) 0.997. A comparison of
  both kernels on a synthetic dry run is under way. Core is not the weak point.
- Exposure after DEV end (counts only). Panel rows with an effective up of 2.0 / 2.5 / 3.0 / 3.5
  and more: DEV 5 / 4 / 3 / 3, after DEV end 4 / 1 / 1 / 0. With an effective dn of 0.5 / 0.4 /
  1/3 and less: DEV 10 / 3 / 2, after DEV end 2 / 0 / 0. Largest short weight held at any hour
  by the submitted books (12 worlds per null so far): momentum median 0.27 and maximum 0.41 under
  null A, 0.33 and 0.48 under null B; reversal 0.42 and 0.50 (the whole short side in one name)
  under null A, 0.40 and 0.46 under null B; hours with a short of 0.33 or more are 0.0% to 0.7%
  of a book's hours. After DEV end the one bar at 3.0 or more needs a lone short of 0.39 to 0.49.
- R-R (e) widened on the auditor's advice: the seal compares the whole protocol header of an
  artifact (seeds, sizes, draws per pair, speeds, levels, rho grid, fine points, G6 lags and
  memory bound, pool minimum) with the one the locked kernel writes for a real run of the
  protocol's size; the semantic hash pins the constants, not what a run can change at run time.
- ONE extension of the pilot, fixed here before its first world.
  Condition: the auditor's model must read 0.70 or more for a proportional repeat of round 1 at
  the full size (192 worlds per null with 4 Tier-1 passes for momentum under null A and none
  elsewhere; 64, 64, 60 and 64 of 96 in the power cells at 0.10). If it does not, the extension
  cannot do its job with this instrument and is not run.
  Size and order: on the committed code and the auditor's source D unchanged, seeds continued.
  Null worlds 48 to 143 under each null and oracle worlds 24 to 71 in each cell; interim reading;
  then null worlds 144 to 191 and oracle worlds 72 to 95; final reading. About 15 hours to the
  interim reading and 22 in all, one process at a time.
  Data: both rounds pooled. A row of round 1 counts only as reproduced bit for bit on the
  committed code; the null A rows measured before R-O are replaced by their reruns where they
  differ.
  Model: the auditor's as above, unchanged, with core at 0.997 and R-R.
  Reading: an interim P(seal) of 0.75 or more stops the extension and reads "ask the owner with
  the odds". Otherwise the full size, and then: 0.70 or more, ask; 0.40 to 0.70, the owner gets
  the odds with the advice not to run yet; under 0.40, not ready, and then no further extension
  but design.
  To be explained before any re-key whatever the odds: a family with a mean VAL Sharpe above
  +0.5 under either null; a family whose Tier-1 share at 0.10 among its evaluated pairs is above
  6% in the pooled pilot; a family under 0.60 or a null under 0.80 evaluated of designed in the
  pooled pilot; a power cell with more than 5% of its books liquidated; the premium rule (P) as
  fixed in the X12-prep entry.
  Known and no trigger: source D replays DEV days after DEV end, so the bar of 2022-06-07 20:00
  again liquidates short books in the worlds where its day is not flipped; under R-R those pairs
  leave the denominator. And a limit of the pilot that no size removes: its days after DEV end
  are DEV days, so its no-skill rates are those of the DEV period's kind of market, not of the
  real VAL period's.
- Condition met, before any extension world (auditor, same model unchanged): for a proportional
  repeat of round 1 the model reads P(seal) 0.911 at the full size (0.10 qualifies in 0.959 of
  the simulated runs; pooled bound at 0.10 met with 0.980 under null A and 0.999 under null B;
  momentum's cap under null A 0.969; every power cell at 0.10 at 0.970 or more) and 0.853 at the
  interim size (3 of 144 for momentum under null A; 48, 48, 45 and 48 of 72). The extension can
  therefore read "ask" on good data and is ordered; it starts when this entry is committed.
- Core comparison done (auditor): on a fully synthetic dry run with the same seeds (30 null and
  10 oracle worlds per null) the sealed kernel and 306eb8c give identical null rows (150 and
  150), oracle rows (40 and 40) and tuning picks. The two verdicts differ through the rule
  alone: R-L's family bound, added after genesis, fails on that 30-world sample (null B
  funding_carry 2 of 30); the sealed core artifact meets R-L with room (largest family 4.67% at
  0.10). On real data the open channels stay R-Q, where a draw is liquidated on DEV (the sealed
  artifact has none), and the added mark rows through the liquidation check.
- Fix pass 11 stage A is commit 305e2c6 (R-R as ruled, with this entry). Coordinator's review of
  the kernel diff, line by line: built as ruled, no defect found; on the sealed core rows the
  design holds and the verdict stays 0.10. The auditor's reading of the delta 306eb8c..305e2c6:
  no world builder, draw or per-pair row can differ (upipeline, engine, universe, interp,
  datasets, data, pipeline, lang, stats and the three programs are identical files; in
  ucalibrate and calibrate only the decision side, the seal checks, the advisory and main
  changed), so the extension runs on 305e2c6 and the bit-for-bit stage on 306eb8c stands. Its
  attack on the pass found no defect: no path by which a thin or foreign artifact still seals;
  the advisory cannot call a threshold dead that a completion could still qualify (its fault
  test can only miss a death); no header field differs between a real run and the seal. Two
  notes: the sealed genesis core artifact does not carry the new header, so the re-key
  includes the core calibration again, as planned; in the universe artifact the run header is
  compared key by key and the older "protocol" entry is read for sizes and seeds only.
- Bit-for-bit on 306eb8c so far (auditor). Null A worlds 0 to 11: 29 of 36 rows identical in
  every field, the kernel's G6 p included; the 7 that differ are all carry (3 liquidated rows
  now not submitted under R-Q, 4 with the new stage-1 counts only); momentum and reversal 24 of
  24. Carry in all 48 null A worlds: 27 identical, 12 the pairs liquidated on DEV and now not
  submitted, 9 with the new stage-1 counts only; no pair picks another draw. Still to run: null
  B and both power arms.
- Fix pass 11 stage B (builder): the full suite on 305e2c6 gave 962 passed, 0 failed, 0 skipped
  in 1757 s (910 at 306eb8c; 52 new: test_ledger_lock 45, test_calibrate 5, test_ucalibrate 2);
  ledger verify OK; ledger/, data/ and kernel.lock untouched.

## Round 7, addendum X12 (round 1 closed) - 2026-11-22 - bit-for-bit on the committed code, controls, the premium arm, cost; the extension is running

- Bit-for-bit on 306eb8c (the committed code, no patch). Null A worlds 0 to 11: 29 of 36 rows
  identical in every field, the kernel's G6 p included; the 7 that differ are carry rows changed
  by R-Q alone (3 not submitted, 4 with the new stage-1 counts). Carry in all 48 null A worlds:
  27 identical, 12 not submitted, 9 with the new counts only; no pair picks another draw. Null
  B, 25 worlds (0 to 11 and every world with a liquidated or R-Q row): 75 of 75 identical. Power
  arms: 48 of 48 rows identical under each null, tuning picks and achieved means equal; under
  null A the coarse tuning curve of the fast speed differs at 31 of 81 points, all at rho of 0.40
  and above, where the copy before R-O had liquidations that R-O removes (the bracket, the picks
  and the power rows are not touched). The kernel's memory statistic differs from the auditor's
  own by at most 5e-15 and every p is equal. So the rows of round 1 stand as measured, with the
  carry rows of the commit.
- Controls (the X10 source with independent days, through R-M, R-O and R-Q; 12 worlds per null):
  no family reaches Tier 1, no pair passes every other gate, every pair is evaluated. Mean VAL
  Sharpe under null A and null B: momentum -0.72 and -0.70, reversal -0.88 and -1.28, carry
  -3.11 and -3.21. In X11 the same worlds gave momentum a VAL Sharpe of 1.15 to 3.63 with every
  other gate passed in 11 and 10 of 12 worlds: R-M removed that source's premium.
- Premium arm (worlds that keep each symbol's mean, with R-O and R-Q; the momentum family; 20
  lags with the speed limit). Admitted books and their G6 passes at 0.05 and at 0.10: X source
  null A 37 with 3 and 5, null B 16 with 0 and 0; source D null A 16 with 1 and 2, null B 9 with
  0 and 0; together 78 with 4 and 7 (5.1% and 9.0%). Rule (P) is not triggered (5 of 37 at 0.10
  has a probability of 0.31 under a true 10%). The spread across worlds of the gap between the
  actual and the stale Sharpe against the spread of the stale Sharpes inside a world: 0.61 to
  0.51, 0.45 to 0.49, 0.59 to 0.51, 0.46 to 0.51 (X11: 0.87 to 0.53); adjacent lagged Sharpe
  ratios correlate +0.25 to +0.44. With 20 lags G6 holds its nominal level among books that earn
  a premium without timing.
- G1 in the R-M worlds of the size arm passes less often than its nominal 10% in every family
  and null (null A 1 of 48, 1 of 48, 0 of 36; null B 0 of 45, 1 of 38, 0 of 41).
- Odds of round 1 on the commit's rows: 0.305 under R-R (0.02 under the former cap of R-P). NOT
  READY stands; the extension decides.
- The auditor's reading of the delta 1442b42..306eb8c: R-N, R-O, R-P and R-Q are as ruled and
  identical in expression to its own patches; the reproductions above confirm it.
- Cost of the real top30 calibration (auditor, measured): about 34 worker-hours (26 to 29
  without contention). Wall time about 34 hours with one worker (oracle phases done after about
  14.5), 17 with two (7.3), 9 to 10 with four (about 4). About 1.6 GiB per worker and 0.44 GB for
  the shared source; three workers fit on this machine with the editor open. Core: about 5 hours
  with one worker.
- Limitation sentences the auditor proposes for CONSTITUTION section 12, and the coordinator's
  reading. (1) Carry pairs liquidated on DEV are not submitted: stated since fix pass 11. (2)
  Null A can draw a real extreme bar more than once in a world (2022-05-11, 2022-06-07), and a
  no-skill book is short where the real book was not, so concentrated short books are liquidated
  there more often than history did: the text states the mechanism and the denominator; this
  nuance is recorded here and enters the text with the next text pass, if there is one. (3) A
  world row without trades stays flat although the real evaluation would read its mark wick:
  stated in section 13 (R-O). (4) 0.025 cannot be reached with 20 lags and slow books fail the
  speed limit: stated in sections 12 and 13. No text pass for these now.
- The extension started at 12:19 on 305e2c6 and runs detached: null worlds 48 to 143 under each
  null, then the oracle worlds to 71 in each cell, then the interim reading, expected about 16
  hours after the start; the full size follows only if that reading is under 0.75.
- Detail: `audits/round7_findings.md`, replaced by the auditor's file with section X12-R (sha256
  7524ed5b364f91bee57fb93fd970423a161a48adc8f4a0c48c1530c5dc0913bc).

## Round 7, addendum X12 (extension, interim reading) - 2026-11-23 - the pooled pilot reads 0.843; the rule says: ask the owner with the odds

- Run (auditor): on 305e2c6 without a patch, source D unchanged, seeds continued, one process at
  a time, 2026-11-22 12:19 to 2026-11-23 00:05. Null worlds 48 to 143 under each null (288 pairs
  per null), then the oracle worlds 0 to 71 in each cell, tuned on all 72 (the tasks of worlds 0
  to 23 reused from the runs on 306eb8c, keyed by world, seed and rho). The reading script and
  the model carry file times of 2026-11-22 09:04 and 03:00, before the first extension world.
  The full-size steps found the stop flag and ran nothing.
- Pooled pilot, 144 worlds per null (round 1 as reproduced on the commit: null A momentum and
  reversal from the size arm, carry from the commit's rerun; null B from the copy with R-O).
  Per family: Tier-1 with p <= 0.05; Tier-1 with 0.05 < p <= 0.10; evaluated without Tier-1; not
  evaluated (not submitted + liquidated after DEV end); evaluated share; mean VAL Sharpe.
  Null A momentum: 1; 1; 142; 0; 1.000; -0.26.
  Null A reversal: 0; 1; 142; 1 (0 + 1); 0.993; -0.59.
  Null A carry: 0; 0; 109; 35 (35 + 0); 0.757; -1.46.
  Null B momentum: 0; 0; 136; 8 (0 + 8); 0.944; -0.38.
  Null B reversal: 0; 0; 116; 28 (17 + 11); 0.806; -0.41.
  Null B carry: 0; 0; 120; 24 (24 + 0); 0.833; -1.51.
  Null A: 396 of 432 evaluated (0.917), Tier-1 over evaluated 1 of 396 at 0.05 and 3 of 396
  (0.76%) at 0.10. Null B: 372 of 432 evaluated (0.861), no Tier-1 pass. No faulted row.
- Power, 72 books per cell at the 72-world tuning, Tier-1 at 0.05 and at 0.10: A fast (rho
  0.047625) 48 and 52; A slow (0.07425) 39 and 45; B fast (0.047375) 42 and 47; B slow
  (0.086375) 38 and 44. Achieved mean VAL Sharpe 1.497 to 1.500. No book liquidated, none over
  the memory limit. Books passing every gate but G6: 54, 50, 48 and 55.
- Model (the auditor's, unchanged; R-R; core 0.997; 60000 simulated runs): P(seal) 0.843. The
  null side qualifies 0.10 in 0.932 of the runs, 0.05 only in 0.062, neither in 0.007; the
  pooled evaluated floor holds in every run under both nulls. Before the first extension world
  the same model read 0.853 for a proportional repeat of round 1 at this size.
- Checks to be explained before any re-key (the extension entry): none fires. Mean VAL Sharpe:
  negative for every family under both nulls. Largest Tier-1 share at 0.10 among evaluated
  pairs: null A momentum, 2 of 144 = 1.4% (trigger above 6%). Smallest evaluated share of a
  family: null A carry 0.757 (trigger under 0.60); nulls 0.917 and 0.861 (trigger under 0.80).
  No power book liquidated (trigger above 5%). Premium rule (P): not triggered (round 1, 7 of 78
  at 0.10).
- Coordinator's own recount from the result files (counts only): the six null cells and the
  four power cells as above. On every row that carries the kernel's own G6 fields (all rows run
  on 305e2c6, the carry rerun on 306eb8c, both power arms) the kernel's p and memory flag equal
  the auditor's side line in every evaluated row, and the Tier-1 counts from the kernel's
  fields alone are the same. Every evaluated row has a side-line p (a missing one would have
  read as "no Tier-1"). Statuses are evaluated, liquidated and not submitted only. Seeds are
  contiguous (11000 to 11143, 14000 to 14143, 17000 to 17071, 18000 to 18071), one row per
  pair. Reading of the two scripts: the model applies R-R (rates over evaluated pairs, family
  floor 0.50, pooled 3%, family 6%); the pooled floor is reported and not applied, and holds in
  every run; faults are not modelled, and none occurred.
- Observation (coordinator; information, no trigger). Pairs passing every gate but G6: null A 5
  of 396 (momentum 4, reversal 1), null B 0 of 372; G1 alone: 13 of 396 and 5 of 372. Of the 5,
  3 pass G6 at 0.10 and 1 at 0.05. Against luck G6 is not a 1-in-10 filter: a pair that passes
  G1 by luck has an actual Sharpe in the upper tail of its own lagged copies, so few of the 20
  lags beat it. The no-skill bound therefore rests on the joint rate of the other gates, which
  the calibration measures as part of Tier 1; G6's own level is what the premium arm measured
  (9% at 0.10).
- Reading, by the rule fixed before the extension's first world: interim P(seal) 0.843 is at
  least 0.75, so the extension stops and the reading is "ask the owner with the odds". What the
  odds do not cover, as stated before the run: the pilot's days after DEV end are DEV days. The
  no-skill rates and the power of the real VAL period can differ from the pilot's in either
  direction, and only the real calibration measures them. Known, counts only (the extension
  entry): after DEV end the real panel has fewer extreme rows than DEV, so the pairs lost after
  DEV end should be fewer than in the pilot.
- Reading before the seal (the size-arm entry), reference renewed on the pooled pilot with the
  same convention (pairs liquidated after DEV end by the source's replayed days counted as
  evaluated): null A momentum 144, reversal 144, carry 109 of 144; null B momentum 144, reversal
  127, carry 120 of 144. A cell of the real calibration that differs by more than 0.15 is
  explained before the seal. A reading, not a bound.
- Order of the real run, fixed before the owner is asked. Re-key on the branch; `data validate`;
  the top30 calibration first, at the protocol's size with three workers (its oracle phases
  come first, and its advisories say within about 5 hours whether a threshold can still
  qualify); then the core calibration at the protocol's size; the reading before the seal; the
  seal of both units; the selftest; the auditor's independent recount; the DEV-positive null
  pass rate reported for KP-016 (information); merge into `main`. If a unit stops, nothing is
  sealed, `main` stays on the sealed kernel (521687f) and the build returns to design; the seeds
  belong to the protocol, so no run is repeated with other seeds.
- Detail: `audits/round7_findings.md`, replaced by the auditor's file ending with "EXTENSION -
  INTERIM READING" (sha256 e31c899ad21a04ec0bd0f115ee1e1a99f0b22baee99239a650e24425d97725bc).
- Added after commit 2ede291 (coordinator's count on the same rows, for KP-016; information).
  Evaluated pairs with a positive DEV Sharpe (G3 true): null A 124 of 396 (momentum 67, reversal
  49, carry 8), null B 153 of 372 (74, 46 and 33). Tier-1 over those: null A 1 of 124 at 0.05
  and 3 of 124 (2.4%) at 0.10 (momentum 2 of 67, reversal 1 of 49); null B none of 153. This is
  the count the real run reports for KP-016. The owner is asked for the approval of KP-015 with
  the odds, the limit of the pilot stated above, and this count.

## Round 7, addendum X12 (decision) - 2026-11-23 - KP-015 approved by delegation and re-keyed; how the real calibrations start

- The owner was asked on 2026-11-23, after commit 36b8665, to approve KP-015 as built. The request
  stated: the odds of a successful seal (0.843) and what they cannot cover (the pilot's days after
  DEV end are DEV days); the change (the unit top30 with the index price, a G6 threshold per unit,
  and the six rulings R-L, R-M, R-N, R-O, R-Q and R-R, any of which he may decline at the cost of
  a rebuild and a new pilot); the known limits (a book that earns a premium without timing passes
  G6 about 1 time in 10 at 0.10; holding periods of roughly 5 to 50 days; the null pass rate is
  counted over all evaluated pairs, the DEV-positive count of the pilot being 3 of 124 and 0 of
  153; carry is not submitted in about a fifth of the null worlds; the five counted trials keep
  their place in M but their ids belong to the sealed kernel); the run time; and that a failed run
  seals nothing. The coordinator recommended approval.
- The owner's reply, in full: "decide whats the best". That is a delegation, not a yes in his own
  words, and it is recorded as that. CONSTITUTION section 10, step 2, provides for "the
  coordinator acting for the human, recorded as such". The delegation covers the question that
  was asked and nothing else.
- The coordinator's decision, acting for the owner: KP-015 is approved as built at 305e2c6 with
  all six rulings, and the real calibrations run. Reasons: the reading rule fixed before the
  extension's first world says "ask", and none of its checks fires; each ruling answers a defect
  that an audit measured, and the auditor attacked each one before it was built; what is still
  unknown (the real VAL period) can only be measured by the real run; a run that stops costs
  machine hours, seals nothing and leaves `main` on the sealed kernel. NOT decided here, and still
  the owner's: KP-016, KP-014, the confirmation of the rule set as a whole, and the other open
  items of STATE.md.
- KP-016 and the order of things. A semantic re-key after generation 2 has scored trials would
  orphan them. The count over DEV-positive pairs of the real run, for both units, therefore goes
  to the owner together with the result of the seal and BEFORE generation 2 opens.
- Pre-flight before the re-key (read only). The kernel files are those of 305e2c6 (no difference
  in omr/, tests/, CONSTITUTION.md, LANGUAGE.md and requirements.txt between 305e2c6 and
  36b8665); no environment problem; research hash 28d9084a8c5c7659..., validation passed for the
  data as stored; every ledger chain verifies.
- Re-key (2026-11-23, branch kp015-build): semantic
  5ea66b0fb79ca267d3c8de22d203976aab3bca5634b22e026b13687c69eb2687 (39 files), text
  1366fb8fd0b6976839a3e6b16e40c402291c0154bb8ccfeae24bcd6848c72924 (35 files), not sealed.
  `kernel_lock verify` and `ledger verify` are OK; ledger/kernel_history.jsonl has its ninth row,
  with the approval recorded in the words above. The seal of the earlier kernel (semantic
  7446278556aadd8f..., G6 0.10) stays on `main` (521687f) until both units seal here.
- Memory, and how the run starts. At 00:41 the machine had 1.4 GiB of physical memory available
  and under 4 GiB of commit headroom (the owner's other editor windows and sessions, opened at
  about 00:39). The kernel's own preflight needs 1.6 GiB per worker plus the shared source, so not
  even one worker fits, and the coordinator does not use --force. The real run therefore starts
  through a detached supervisor outside the kernel and outside git (`_build/kp015_lock_run/`): it
  waits for memory, starts `python -m omr.ucalibrate` with as many workers as fit (3 at most),
  ends the run when the kernel's own advisory says that the seal rule will stop whatever the rest
  gives (so that no null row is looked at without need), and starts `python -m omr.calibrate`
  after a top30 verdict that is not a stop. The commands, sizes and seeds are the protocol's own;
  the supervisor decides only when a process starts and with how many workers, and the artifact
  does not depend on either (the partial file binds the run header, which has no worker count).
  The seal, the reading before it, the selftest and the recount stay with the coordinator.
- The run (added after commit 42487f8). By 01:04 the owner had freed memory (8.0 GiB available).
  The coordinator started `python -m omr.ucalibrate --workers 3` directly at 01:05:30, detached
  and at below-normal priority: the lock verified, the source loaded (134 symbols ever in top30;
  4146843 active rows, 3162 without a valid mark bar; smallest effective low / open 0.298,
  largest effective high / open 6.987, the known DEV bar), the kernel's memory preflight passed,
  and the first oracle phase ran at about 100 tasks in 30 minutes. Meanwhile a helper built the
  supervisor and tested it with a stand-in command only: single instance, the wait for memory,
  exit codes 0, 4 and others, the stop on the advisory with the whole process tree, the stop on
  request, the low-memory pause, the worker upgrade, the guards against recomputing an artifact
  that exists, and a detached start that survives its launcher. The coordinator read the script.
  At 01:34:05 the coordinator stopped its own process tree and started the supervisor, whose
  first attempt began at 01:34:51 with 3 workers: "resuming: 91 finished tasks ...; 0 damaged
  lines discarded". The resume path is thereby proven on the real run, at the price of the tasks
  in flight. Every start of the calibration appends one row to ledger/val_access_log.jsonl.

## Round 7, addendum X12 (seal) - 2026-11-23 - both real calibrations finished; the reading before the seal; KP-015 sealed at core 0.10 and top30 0.10

- The run. The supervisor's first top30 attempt (started 01:34:51, three workers) ran to the end
  without a restart, a pause or an advisory: TOP30_DONE at 13:22:54, exit 0, wall time 42469.9 s
  after the resume (12 h 17 min after the first start at 01:05:30). The memory available stayed
  between 5.1 and 6.5 GiB at every heartbeat. The helper read the artifact ("VERDICT OK chosen
  0.1") and the supervisor started `python -m omr.calibrate --workers 3` at 13:23:40: CORE_DONE
  at 14:08:18, exit 0, wall time 2647.3 s, then SUPERVISOR END CORE_DONE. Both error logs are
  empty. ledger/val_access_log.jsonl has one row per start (rows 16 to 18).
- The artifacts, as the calibrations wrote them and as ledger/calibration_log.jsonl logs them
  (rows 3 and 4): ledger/ucalibration_5ea66b0fb79ca267.json, sha256
  24896cd3f99d84250668e93f5c043f3eb6153042c683b29bc415972c03cbcd61 (protocol version 9; 200
  worlds per null, 100 oracle worlds per null), and ledger/calibration_5ea66b0fb79ca267.json,
  sha256 a1ee5cfb86dda2b8b538cb7d685d0614ea3bfa516e84993620ccd7822b5ec0a5 (protocol version 6;
  300 and 200). Both carry the lock's semantic hash, research hash 28d9084a8c5c7659...,
  kernel_lock_verified true and synthetic_dry_run false.
- Top30, the no-skill side (Tier-1 passes over evaluated pairs at 0.025 / 0.05 / 0.10): null A
  0 / 0 / 0 of 547; null B 0 / 0 / 1 of 542 (0.18%). The one pass is a reversal pair with
  p = 2/21, the only one of the 1089 evaluated pairs that passes every gate but G6; 4 of them
  pass G1. No family is above 0.57% (the bound is 6%). Evaluated of 200 designed pairs per
  family: null A momentum 199, reversal 199, carry 149; null B momentum 200, reversal 176, carry
  166; pooled 0.912 and 0.903 against the floor of 0.75, every family above its floor of 0.50.
  Two submitted pairs were liquidated after DEV end (null A: one momentum, one reversal), no
  pair faulted, and 51 pairs (null A, all carry) and 58 pairs (null B: carry 34, reversal 24)
  were never submitted (R-Q). Mean VAL Sharpe of the evaluated pairs: null A momentum -0.53,
  reversal -0.70, carry -1.45; null B -0.68, -0.87 and -1.94.
- Top30, power at true Sharpe 1.5 (100 books per cell; Tier-1 at 0.025 / 0.05 / 0.10): null A
  fast 0 / 69 / 82, null A slow 0 / 62 / 74, null B fast 0 / 66 / 70, null B slow 0 / 48 / 68.
  At the chosen 0.10 every cell is at 0.68 or above (POWER_MIN 0.5). No book was liquidated; the
  achieved mean VAL Sharpe is 1.502, 1.500, 1.500 and 1.499 at rho 0.061, 0.098, 0.071 and
  0.107. At 0.05 the cell null B slow reads 0.48, so 0.05 could not have sealed top30; with 20
  lags 0.025 is out of reach, as known.
- Core. Every one of the 3000 null rows and 1600 oracle rows equals the row of the sealed
  kernel's artifact (calibration_7446278556aadd8f.json) in status, p value, VAL and DEV Sharpe,
  gates and parameters, although the research hash differs (the data store was extended for
  KP-015; the core world's rows did not change). Tier-1 over evaluated pairs: null A 10 / 26 /
  44 of 1498 (2.94% at 0.10), null B 6 / 18 / 35 of 1500 (2.33%); the worst family is at 4.67%
  (donchian, null A) against 6%; power at 1.5 at 0.10: 0.84, 0.855, 0.905 and 0.855.
- The reading before the seal, against the reference fixed on the pooled pilot (submitted pairs
  over designed pairs). Null A: momentum 1.000 against 1.000, reversal 1.000 against 1.000,
  carry 0.745 against 0.757. Null B: momentum 1.000 against 1.000, reversal 0.880 against 0.882,
  carry 0.830 against 0.833. The largest difference is 0.012 and nothing differs by more than
  0.15, so nothing had to be explained. The pilot's artefact (pairs liquidated after DEV end by
  the one replayed DEV bar) is absent from the real run, as predicted: null B has no liquidated
  pair.
- Against the pilot's forecast. The odds model read 0.843 for a seal (0.932 for 0.10 qualifying
  on the no-skill side); the run sealed at 0.10. The no-skill side came out quieter than in the
  pilot's DEV-day worlds (pilot at 0.10: 3 of 396 and 0 of 372; run: 0 of 547 and 1 of 542) and
  the power higher (pilot at 0.10: 0.72, 0.63, 0.65 and 0.61; run: 0.82, 0.74, 0.70 and 0.68),
  with a larger rho needed for the same Sharpe in every cell. One run cannot test an odds model;
  it does not contradict this one.
- The coordinator's recount, a script of its own that reads the stored rows without the kernel's
  summary code: the design, the statuses, the Tier-1 counts per threshold and family, the floors,
  the faults, the power and the level bounds, then the rule. It equals the stored summaries and
  verdicts of both artifacts in every count (top30 chosen 0.10, core chosen 0.10, no design
  problem), and both artifacts' sha256 are those of the calibration log.
- An observation handed to the independent recount (not a bound of the rule). Taken alone, G6
  passes the top30 carry family under null B far more often than its nominal level: p <= 0.10 in
  53 of 166 evaluated pairs and p <= 0.05 in 31 (null A: 6 and 3 of 149; momentum and reversal
  stay under 10% and 5% under both nulls). No carry pair passes every other gate (under null B
  none has a positive VAL Sharpe), so the reading of the rule does not depend on it. It does show
  what the null side of top30 can and cannot say: its families lose money in the no-skill
  worlds, so their Tier-1 rate measures the other gates much more than G6. The level of G6 for a
  book that does pass the other gates was measured in the pilot's premium arm (7 of 78 at 0.10,
  4 of 78 at 0.05). The auditor is asked what causes the carry reading and whether the same
  mechanism can reach a book that passes the other gates.
- The seal (2026-11-23, 09:56:08Z). `python -m omr.kernel_lock verify`: OK, not sealed. Then
  `python -m omr.kernel_lock seal --calibration ledger/calibration_5ea66b0fb79ca267.json
  --universe-calibration ledger/ucalibration_5ea66b0fb79ca267.json` printed "sealed: G6
  threshold core 0.1 top30 0.1", and verify reads "sealed G6 core 0.1 top30 0.1". The seal
  applied the rule in code to the logged bytes of both artifacts and checked their headers and
  sizes against the kernel's own. ledger/kernel_history.jsonl has its tenth row (event seal).
- Selftest, after the seal: `python -m omr.selftest` printed OK in 6.7 minutes (the five baseline
  programs and the kitchen-sink program through the interpreter on the real frames; the three
  noise programs, one of them in unit top30, through the complete evaluate path into a temporary
  ledger that is deleted). It appended rows 19 to 22 to ledger/val_access_log.jsonl (its handle
  and one row per noise program scored into the temporary ledger). A first start of the selftest
  had been interrupted by the owner by mistake before it took its handle (no row, no file).
  `kernel_lock verify` and `ledger verify` are OK afterwards (six chains).
- For KP-016 (information): Tier-1 over the evaluated pairs with a positive DEV Sharpe, at
  0.025 / 0.05 / 0.10. Top30: null A 0 / 0 / 0 of 165; null B 0 / 0 / 1 of 225 (0.44%). Core:
  null A 10 / 26 / 44 of 1144 (0.87%, 2.27%, 3.85%); null B 6 / 18 / 35 of 1130 (0.53%, 1.59%,
  3.10%). With KP-016's denominator top30 would keep 0.10 and core would get 0.05 (power at 1.5
  at 0.05: 0.84, 0.83, 0.905 and 0.81), as the proposal said of the earlier core rows. The
  numbers go to the owner before generation 2 opens.
- Next: the independent recount of the seal by an auditor that has seen neither the build nor
  the coordinator's recount; then the merge of kp015-build into `main`. Generation 2 does not
  open before the owner has the KP-016 numbers.
