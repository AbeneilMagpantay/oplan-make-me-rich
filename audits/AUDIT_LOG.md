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
