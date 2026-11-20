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
