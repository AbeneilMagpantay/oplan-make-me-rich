# STATE (2026-11-25: generations 0 to 2 have counted trials, six in all, none Tier 1; the KP-015 kernel is sealed)

## Where things stand

- Kernel (KP-015; sealed 2026-11-23 and on `main` since the merge of the same day): semantic
  `5ea66b0fb79ca267d3c8de22d203976aab3bca5634b22e026b13687c69eb2687` (39 files), text
  `1366fb8fd0b6976839a3e6b16e40c402291c0154bb8ccfeae24bcd6848c72924` (35 files), G6 threshold 0.10
  for unit core and 0.10 for unit top30, from `ledger/calibration_5ea66b0fb79ca267.json` and
  `ledger/ucalibration_5ea66b0fb79ca267.json`. Selftest OK. The seal was recounted by the coordinator
  and by an independent auditor (audits/seal_recount_findings.md: AGREE, no blocker).
- The earlier kernel (the one that scored the five counted trials; on `main` until 521687f): semantic
  `7446278556aadd8f4f10e30b75ddebbc2ab272a255f2b8fc0472ed57a18ecad1` (32 files), text
  `d51a84cd8c13dc1b545b5f29a06c97a2d381c3bf972853c20381d28cd1b97ef1` (22 files), G6 threshold 0.10
  from `ledger/calibration_7446278556aadd8f.json`. Seal recounted by the fifth audit; artifact,
  calibration-log row and seal are in commit d2c2d4f.
- Generation 0 (`generations/gen000/REPORT.md`): five textbook baselines; SMA cross rejected in
  stage 1 (uncounted); four evaluated, none Tier 1; best VAL Sharpe 0.384.
- Generation 1 (`generations/gen001/REPORT.md`): five pre-registered hypotheses, 18 DEV sandbox runs,
  one counted submission. gen001_tsmom_long_flat (24778ca0881b6c26): VAL Sharpe 0.830, PSR(0) 0.926,
  passes eight gates and fails G6 (p 0.279). Not Tier 1.
- Generation 2, round 1 (`generations/gen002/REPORT.md`; unit top30, KP-015 kernel): four pre-registered
  weekly market-neutral hypotheses (residual reversal, activity fade, small tickets, absorbed flow),
  committed as fd19943 BEFORE any sandbox run. All four failed the DEV screen fixed in advance at their
  defaults (DEV Sharpe -1.57, 0.17, -0.21 and -1.25), so no neighbour, control or diagnostic run was due:
  4 sandbox runs of 60, no counted submission, M unchanged. In the ledger generation 2 is still open
  (0 of 5 counted), so a further round is a further PLAN version in the same file.
- Generation 2, round 2 (same report, second part; PLAN version 2 committed as b64b229 BEFORE any round-2
  sandbox run, by a fresh researcher session): three hypotheses. Residual skewness lost on DEV (Sharpe
  -1.91); reversal of the month before last was too weak (0.38); 4-week residual momentum, a continuation
  rule written after round 1's DEV result and screened more strictly for that reason, reached 0.92 to 1.07
  at five settings but lost in 2022H1 in all of them and so failed the per-year item registered for it.
  7 sandbox runs (11 of 60 used), no counted submission, M unchanged.
- Generation 2, round 3 (same report, third part; PLAN version 3 committed as afb835b BEFORE any round-3
  sandbox run, by a fresh researcher session): three contrarian hypotheses on the inputs opened for it,
  funding and the perp premium over the index. All three had the registered sign on DEV (Sharpe 0.82, 1.20
  and 0.98 after costs), received funding and stayed positive with it removed, but traded far more than
  estimated (costs 0.45 to 0.51 of equity over DEV) and failed the cost ceiling fixed in advance (0.25),
  so their timing, price-neutral and speed-limit readings were not taken. 3 sandbox runs (14 of 60 used),
  no counted submission, M unchanged.
- Generation 2, round 4 (same report, fourth part; PLAN version 4 committed as 350a246 BEFORE any round-4
  sandbox run, by a fresh researcher session): cheaper-to-trade forms of round 3's two mechanisms, said to
  be written after round 3's DEV result, so that their DEV Sharpe is not evidence. Averaging the
  cross-sectional rank over 16 days halved the costs. gen002_averaged_funding_shock (H11) passed every item
  of the screen fixed in advance (costs 0.218 of equity over DEV under the ceiling of 0.25 and its
  per-gross clause; positive with the funding removed and the costs paid twice; both corners; a stale copy
  at 0.03 against the book's 1.49; a price-neutral twin at 1.47; speed-limit diagnostic -0.36):
  ELIGIBLE, SUBJECT TO THE KP-017 MEASUREMENT. gen002_averaged_unrewarded_shift (H12) failed at its first
  corner. 8 sandbox runs (22 of 60 used).
- Generation 2, the counted trial (same report, last part; 2026-11-25). The KP-017 measurement met both
  conditions fixed in advance (audits/AUDIT_LOG.md), the restriction was lifted for this one program, and
  the decision was committed as 6c20689 before scoring. gen002_averaged_funding_shock (7eadbeeaf2adc98d):
  DEV Sharpe 1.499, VAL Sharpe -0.249, PSR(0) 0.333; fails G1, G2, G4, G5, G6 (p 0.571) and G7; passes G3,
  G8 and G10. Not Tier 1. Before costs it earned about nothing in VAL.
- Ledger: M = 6 counted trials (generation 0: 4, generation 1: 1, generation 2: 1 of 5), N = 5.90,
  Tier 1: 0, pool 0 of 5, one uncounted stage-1 rejection; all chains verify.
- Benchmark over VAL, for reference: long BTC and ETH half each, Sharpe 0.921.
- Data: the counted trials above were scored on research_hash
  `cf26f534cf1c9f4a0bff334c77a041ed66862484a7dc167581cd50562783b4d8`. The data store has since been
  extended and hole-filled for the KP-015 build (research hash `28d9084a8c5c7659...`); the
  calibrations of the re-keyed kernel bind to it.
- Repository: git, private GitHub remote. `main` holds approved, verifying states only; since
  2026-11-23 that is the sealed KP-015 kernel (approved by delegation; before the merge `main` stood at
  521687f). The branch `kp015-build` is kept as the record of the build. The coordinator commits and
  pushes at gates (`tools/git_gate.ps1`, which pushes the current branch). Research sessions make no
  git writes.

## How a generation runs (as done in generation 1)

1. A fresh researcher session reads LANGUAGE.md, RESEARCH_PLAYBOOK.md, LESSONS.md, the last two
   REPORTs, trial rows and `python -m omr.status` (never ledger/returns, ledger/trials/ or data/).
2. It writes generations/genNNN/PLAN.md with 3 to 5 hypotheses BEFORE its first sandbox run, then
   explores on DEV only with `python -m omr.sandbox` (at most 60 runs, every run logged in the plan).
3. The coordinator commits and pushes the plan and programs BEFORE scoring, reads each candidate's
   source (RESEARCH_PLAYBOOK section 5), and runs every counted `python -m omr.evaluate` itself. Since
   generation 2 the plan is committed and pushed before the FIRST sandbox run as well, and it fixes the
   DEV screen and the order of the runs in advance.
4. REPORT.md, LESSONS.md and this file are updated; the coordinator commits and pushes.

## Next

Generation 2 is the next research step (generations/gen001/REPORT.md exists). It runs on the KP-015
kernel in unit top30 (RESEARCH_PLAYBOOK section 4b). The human has the KP-016 counts (open decision 5);
in unit top30 that proposal changes no threshold, so trials scored there keep their verdicts if it is
adopted later (their ids would then belong to this kernel). Until the finding of the seal recount is
measured (open decision 6), no funding-driven program is submitted for a counted trial in unit top30.
The evidence so far (LESSONS 8 to 10) says single-coin timing rules on two instruments mostly collect
the market's drift; that is why KP-015 (a point-in-time universe for market-neutral rules, with the
index price as new data) was built first. What follows is the history of that build.

KP-015 feasibility (2026-11-19, `notes/kp015_feasibility.md`): open interest and long/short ratios are
not admissible for backtests (short history, archive rewritten); index price is admissible; a
point-in-time universe is feasible if membership comes from kline activity.

KP-015 build (2026-11-19): built and tested on the WORKING TREE only (KERNEL_PROPOSALS KP-015,
CONSTITUTION section 13, LANGUAGE.md section 10). The kernel lock therefore does NOT verify until the
human approves the re-key; nothing may be evaluated until then. The data store now holds the universe
(678 crypto perpetuals, index_klines for all; research hash d1b6ce5b8d0a0380...), data/validation.json
was rewritten by `data validate`. Ledger untouched. Fix pass done the same day (R1a seasoning, R2
fresh funding, R3 memory refusal, R4 sandbox data checks); R1b awaits a ruling (KERNEL_PROPOSALS KP-015).
Fix pass 2 done (S1 bounded funding_mean in every unit, S2 cross-sections over the in-play symbols with a
known input, S3 zero-trade bars usable up to 24 in a row, S4 six-month blocks). The R3 preflight stays.
Fix pass 3 (2026-11-20): one membership per run (blocks were not equal to the whole panel for a window over
a cs_* result), the block_overlap self-check, and the lookback of stale leaves under a timeframe or btc().
Fix pass 4 (2026-11-20): paired common-names G6 in top30, calibration worlds on the real membership
calendar, finite-only cross-sections, daily-file hole fill in `data universe` for every symbol including the
ten (data rewritten; research hash 28d9084a8c5c7659...), symbol table in the research hash, 12-symbol top30
probe, bounded funding8h, G6 ties (R-B), small items (KERNEL_PROPOSALS KP-015; notes/kp015_build_evidence.md).
Fix pass 5 (2026-11-20): G6 in top30 is a causal paired lag test (no future row; basket p = 1); the
universe calibration resumes after an interruption, checks memory first, tunes level 1.5 only (defaults
200 null worlds, 100 oracle worlds, 4 workers), its null funding carries a sign coin per settlement hour, and
null A shares one source day across a month's members; the data hole fill got three hardening items (marker
age, daily-file pins, a recoverable commit). Stored data and research hash unchanged by this pass.
Fix pass 6 (2026-11-20 to 21): the G6 threshold is decided and sealed PER UNIT ({"core": x, "top30": y};
both units seal or neither; the evaluator applies the program's own unit's threshold); the universe oracle's
speeds are 5 and 20 days, so top30 is certified for holding periods of about 5 days and longer (at 12.5 bps
per side a 1-day book with Sharpe 1.5 cannot pass the doubled-cost gate G4); the reversal calibration family
is the momentum's mirror on daily bars (3 to 20 days); the universe calibration stores a sha per finished
task, runs its oracle phases first and logs a power advisory. Stored data and research hash unchanged.
Audits of the build (audits/AUDIT_LOG.md): round 6 on bd6920b NOT READY, answered by fix passes 3 to 5;
round 7: 32e32e0 NOT READY (the seal rule would have stopped with certainty on top30 fast power; found by
measuring Tier-1 power on the real membership structure), fix pass 6 reviewed READY on the working tree;
full suite 849 passed on the final files.
Pilot of the universe calibration (2026-11-21, dry run on the synthetic universe, 4 oracle worlds per cell, 1
null world per null; notes/kp015_build_evidence.md): it ran end to end in 62 minutes with one worker. Tier-1
power at 0.025 / 0.05 / 0.10: null A fast 1 / 2 / 3 of 4, null A slow 1 / 1 / 1, null B fast 2 / 3 / 4, null B
slow 3 / 3 / 3. Its own advisory fired (null A slow under 50% at 0.10), and the unit verdict of the pilot
artifact is STOP. Four worlds cannot estimate a cell, but the slow rows are worse than the audit's
real-structure worlds, which did not go through the null builders. No re-key on that evidence.
Audit round 7, X10 (2026-11-21, audits/AUDIT_LOG.md): the pilot's weak cell was the dry-run structure plus
chance. On the real structure through the null builders the four cells read 17 / 19 / 19 (A fast), 14 / 17 / 19
(A slow), 17 / 20 / 20 (B fast) and 14 / 15 / 17 (B slow) of 24 at 0.025 / 0.05 / 0.10: marginal by the rule
fixed in advance. But 4286abf is NOT READY: under null A the momentum calibration family passes Tier 1 in
5 / 6 / 8 of 12 null worlds (the monthly pools give each symbol a slowly changing expected return, which the
lag test reads as timing; X10-F1, no false-pass risk), so no threshold could qualify and the calibration would
have stopped after its full run. Fix pass 7 (ordered 2026-11-21): R-K one constant expected return per symbol
in every month under null A; R-L no single family's null pass rate above 6% (FAMILY_PASS_MAX) next to the
pooled 3%, because in top30 only one of the three families can pass and the pooled bound alone would allow it
9%.
Fix pass 7 and 7b (ead27c6, 58ba59e; full suite 864 passed): R-K and R-L built; every bound of the rule holds
only when its value is a number inside it.
Audit round 7, X11 (2026-11-21): no code defect, but 58ba59e is NOT READY. Under the fixed null A the momentum
family still passes Tier 1 in 4 / 6 / 9 of 48 null worlds at 0.025 / 0.05 / 0.10 (null B 0 / 1 / 2 of 24); the
power cells read 17 / 19 / 19 (A fast), 12 / 15 / 18 (A slow), 17 / 20 / 20 (B fast), 14 / 15 / 17 (B slow) of
24; the auditor's odds of a successful seal are about 1 in 10. Coordinator's reading: both nulls keep each
symbol's own sample mean as its expected return, which hands the momentum family a premium in every null world
(VAL Sharpe about 2, every gate but G6 passed), so its Tier-1 rate is G6's own level; and for a 50-day book G6's
200 lags hold only about ten independent comparisons (hypothesis, being tested). The auditor's suggested fix
(draw without replacement) is not adopted. Fix pass 8 (258c1a5, 1442b42; full suite 891 passed): R-M every
symbol has the same expected simple return on every day in both top30 nulls (replaces R-K); tier_at stops on a
malformed row; an advisory during the null phases.
Audit round 7, X12-prep (2026-11-21): the auditor agrees that R-M is a correct no-skill world and confirms that
for a 50-day book G6's 200 lags hold only about 11 to 14 independent comparisons (a book that earns a premium
without timing passes G6 about 1 time in 12 below 0.08 and 1 in 6 at 0.10). It corrected the coordinator: the
premium in the X11 worlds was mostly a true drift built into the synthetic source, not luck. Its objection,
accepted: with R-M alone the seal would no longer measure that weakness of G6. Fix pass 9 (9ca8b62, db32ce2;
full suite 895 passed), R-N: G6 in top30 uses 20 equally spaced lags, and a book whose weights are still
correlated above 0.5 with its own weights one or more lag steps (about 26 days) earlier fails G6.
Audit round 7, X12 power arm (2026-11-21), the first measurement on real DEV-period prices: null A has
enough power (16 of 24 in both cells at 0.10), but under null B 34 of 48 oracle books were liquidated, so the
rule fixed in advance says NOT READY. Cause: the top30 null worlds checked liquidation against their own
last-price bars, while the real evaluation and the core null worlds use mark-price bars; two last-price bad
prints in the real DEV rows (lows at 1/485 and 1/736 of the open), mirrored into highs by null B, wipe out
any short. The same would have hit the real calibration, and it also emptied the null side (34 of 48
no-skill rows liquidated, which the rule would have read as safe). Fix pass 10 (ordered 2026-11-21): R-O
the top30 null worlds take their liquidation wicks from the mark-price bars, as the real evaluation does;
R-P a null with more than 3% of its submitted pairs left without a result (liquidated or faulted) cannot
seal; R-Q a calibration draw that is liquidated on DEV is never submitted (it used to pad the denominator of
the null pass rate). After R-O no row of the panel
comes near such a wick, in DEV or after it (counts only).
Fix pass 10 (306eb8c, 76765ce; full suite 910 passed): R-O, R-P and R-Q built; the coordinator's review of
the kernel diff found no defect.
Audit round 7, X12 size arm (2026-11-22, audits/AUDIT_LOG.md): after R-O no oracle book is liquidated and the
four power cells read 16, 16, 15 and 16 of 24 at 0.10 (the rule fixed in advance for the 20 lags asked for
14), and the no-skill side passes Tier 1 in 1 of 264 submitted pairs. But the reading is NOT READY: the
auditor's odds of a successful seal are 0.02 as the rule stands and 0.31 with one known artefact set aside,
against 0.70 to ask the human and 0.40 as the floor. The artefact: 8 of 132 submitted null B pairs were
liquidated after DEV by one real DEV bar (2022-06-07 20:00, mark high 7 times the open) that the pilot's source
replays after DEV end; in the real run that bar lies in DEV, where R-Q applies. The rest of the gap to 0.70
comes from the odds model itself: on 48 worlds per null it charges every family without a pass about 2% at
0.10, which fills the pooled 3%; only more worlds can settle that (the same model reads 0.91 if four times
the data look like the first round). Reading the
rule against this, the coordinator found that after R-Q a breakage inside DEV would show as pairs never
submitted, which R-P does not count, so a null with few submitted pairs could qualify every threshold. Fix
pass 11 (305e2c6; full suite 962 passed on it), R-R, replaces R-P's cap: null pass rates are taken over
EVALUATED pairs; under each null every family must end with at least half of its designed pairs evaluated and
the null as a whole with at least 75%; faults stay bounded at 3% of the submitted pairs; the stored rows must
be exactly the protocol's, and the seal refuses a calibration whose sizes (core 300 and 200 worlds, top30 200
and 100) or whose run header are not the kernel's own, which nothing checked before; a real run with other
sizes is refused at the start. The coordinator's review and the auditor's attack found no defect. Core: on a
synthetic dry run the new kernel reproduces the sealed kernel's rows exactly, so core should seal at 0.10
again (it met its 3% bound with 44 of 1498 and none to spare: a 45th pass would be 3.004%); if a row did
move, it would seal at 0.05 with power of 0.81 or more.
Round 1 of the pilot is closed (2026-11-22): every row checked on the committed code reproduces (carry
differing only through R-Q), the controls pass nothing, and the premium arm shows G6 at its nominal level with
20 lags (7 of 78 books that earn a premium without timing pass at 0.10, 4 at 0.05).
The ONE extension of the pilot (on 305e2c6, 2026-11-22 12:19 to 2026-11-23 00:05; size and reading rule
fixed in AUDIT_LOG before its first world) ended at its interim reading. Pooled with round 1 the pilot
holds 144 worlds per null and 72 books per power cell, and the auditor's odds of a successful seal read
0.84 against the 0.75 fixed for "ask the human with the odds". No-skill side: 3 Tier-1 passes among 396
evaluated pairs under null A at 0.10 (1 at 0.05) and none among 372 under null B; every family's mean VAL
Sharpe is negative; 0.76 to 1.00 of each family's pairs are evaluated. Power at 0.10: 52, 45, 47 and 44
of 72 (at 0.05: 48, 39, 42 and 38); no book liquidated. None of the checks that would have to be explained
before a re-key fires, and the coordinator's own recount from the result files agrees. What the odds cannot
cover: the pilot's days after DEV end are DEV days, so the real VAL period can differ in either direction.
Decision (2026-11-23): asked for the approval with these odds, the known limits and the run time, the human
replied "decide whats the best". Acting for the human on that delegation (recorded as such; CONSTITUTION
section 10, step 2), the coordinator approved KP-015 as built at 305e2c6 with all six rulings and re-keyed
the branch (not sealed). KP-016, KP-014 and the confirmation of the rule set are not covered by it.
The real calibrations (2026-11-23): the top30 calibration ran from 01:05 to 13:22 with three workers
(the human freed memory for it; from 01:34 under a detached supervisor in `_build/kp015_lock_run/`,
outside the kernel and git), the core calibration from 13:23 to 14:08. Neither stopped, restarted or
raised an advisory.
Result: SEALED on 2026-11-23 at G6 0.10 for core and 0.10 for top30. Top30, no-skill side: no Tier-1
pass among 547 evaluated pairs under null A and 1 among 542 under null B at 0.10 (none at 0.05); 0.745 to
1.00 of each family's pairs evaluated, within 0.012 of the reference fixed before the run; power at
Sharpe 1.5 at 0.10: 0.82, 0.74, 0.70 and 0.68 (at 0.05 one cell reads 0.48). Core: every row equals the
earlier sealed kernel's (44 of 1498 and 35 of 1500 at 0.10; power 0.84 to 0.905). The coordinator's
recount from the stored rows equals both artifacts and the seal, and the selftest prints OK
(audits/AUDIT_LOG.md, round 7, X12 seal). Top30 is certified for holding periods of about 5 days and
longer.
The independent recount agrees with the seal and finds no blocker (audits/seal_recount_findings.md;
audits/AUDIT_LOG.md, round 7, X12 seal recount), and `main` holds the sealed KP-015 kernel since
2026-11-23.
Open from the recount (KERNEL_PROPOSALS KP-017): in unit top30 the timing gate G6 passes the carry
calibration family far above its nominal level under null B (53 of 166 pairs at 0.10). No such pair
passes the other gates, so the seal does not depend on it, and the conjectured cause needs a book that
loses money. A measurement on DEV-period worlds is ordered; until it is read, no funding-driven program is
submitted for a counted trial in unit top30.
Generation 2, rounds 1 to 3 (2026-11-23 and 24, unit top30): all closed without a counted submission (see
"Where things stand"; lessons 16 to 29). Ten pre-registered ideas, no trial spent. Rounds 1 and 2 (prices,
trade counts, taker flow): nothing with the registered sign and enough size. Round 3 (funding and the perp
premium over the index, opened for DEV screening by the coordinator's ruling of 2026-11-24): the registered
sign in all three, stopped by their trading costs. The KP-016 counts of the real run were put to the human on
2026-11-23.
Round 4 (2026-11-24): the first candidate of generation 2, gen002_averaged_funding_shock, eligible by its DEV
screen and subject to the KP-017 measurement (lessons 30 to 33).
The KP-017 measurement (2026-11-25; audits/AUDIT_LOG.md, audits/kp017/): both conditions fixed in advance were
met in the kernel's null worlds built from DEV-period rows (G6 alone passed the candidate in 5 of 64 no-skill
worlds, bound 11; when it did well by luck, in 3 of 32 against 4 of 33 for a price-only book), and the
restriction was lifted for that one program. The carry calibration family did not show the finding of the seal
recount in those worlds, so KP-017 itself stays open (KERNEL_PROPOSALS).
The counted trial (2026-11-25): gen002_averaged_funding_shock failed in VAL (Sharpe -0.249 against 1.499 on
DEV; six gates failed; lessons 34 and 35). Generation 2 stands at 1 of 5 counted submissions and 22 of 60
sandbox runs; 12 pre-registered hypotheses in four rounds, one counted trial, no Tier 1.
Now: the kernel is being changed. Asked on 2026-11-25 to choose between one re-key for the researchers' two
requests (KP-018 and KP-019, with KP-016 riding on it) and more rounds on the kernel as it is, the human
replied "decide whats the best". The coordinator decided for the re-key and recorded it as an approval by
delegation for this batch only (KERNEL_PROPOSALS.md, entry of 2026-11-25). In the batch: KP-019, KP-018,
KP-016 and, of KP-017, the storage of per-lag details in the top30 calibration and the small code items; not
in it: the text items of KP-017 and KP-014. Order: design (no kernel file changed), the coordinator's gate,
build on branch kp019-build, tests, independent audit and the coordinator's own review, re-key, both
calibrations (about 13 machine hours, unattended), pre-seal reading, seal, selftest, recount, merge. Expected:
every stored row identical to the sealed artifacts; thresholds top30 0.10 and core 0.05. Until the seal no
research round runs and nothing is submitted; the human can strike any item until the re-key. Stage reached
(2026-11-25): the design passed the coordinator's gate (audits/AUDIT_LOG.md, round 8) and the build is ordered
on branch kp019-build; one limit of the unit top30 calibration was restated and filed as KP-020. The rule for the rounds after it stands: no rule that was shaped on a
DEV result is submitted for a counted trial without a reason beyond its DEV numbers.

## Open decisions for the human

1. The rule set (CONSTITUTION, LANGUAGE.md) and the lock's approval label still say "human
   confirmation pending".
2. KP-015: approved by delegation, re-keyed and sealed on 2026-11-23 (core 0.10, top30 0.10). Asked
   with odds of 0.84 for a successful seal (audit round 7, X12 extension, interim reading; build at
   305e2c6 with fix pass 11), the human replied "decide whats the best"; the coordinator decided for
   him and recorded it as that. The approval covers the rulings made during the build,
   among them R-L (no family above 6%), R-M
   (the same expected return for every symbol in the top30 null worlds), R-N (G6 in top30: 20 equally
   spaced lags and a speed limit), R-O (mark-price liquidation wicks in the top30 null worlds), R-Q (a draw
   liquidated on DEV is never submitted) and R-R (null pass rates over evaluated pairs; no seal when a
   family keeps under half or a null under 75% of its designed pairs, when more than 3% of the submitted
   pairs fault, or when a calibration is not of the protocol's size; it replaces R-P); the human may
   still decline any of them (that means a rebuild, a new pilot, another re-key and both calibrations
   again).
3. KP-014: text-only LANGUAGE.md additions from the fifth audit (keeps the seal and trial ids).
4. KP-002, KP-004, KP-005, KP-010 remain open; KP-009 kernel-side check optional.
5. KP-016 (approved by delegation on 2026-11-25 as part of the batch re-key, see "Now"; its counts were put
   to the human on 2026-11-23, then with the recommendation not to re-key for it alone): count the null pass
   rate over DEV-positive submissions only. Fix pass 7 built a weaker safeguard into KP-015 (R-L, no family above 6%). On the
   sealed rows of 2026-11-23, over the evaluated pairs with a positive DEV Sharpe: top30 has no Tier-1
   pass among 165 under null A and 1 among 225 (0.44%) under null B at 0.10, so top30 would keep 0.10;
   core has 44 of 1144 (3.85%) and 35 of 1130 (3.10%) at 0.10 and 26 of 1144 (2.27%) and 18 of 1130
   (1.59%) at 0.05, so core would get 0.05 instead of 0.10 (power at Sharpe 1.5 then 0.81 to 0.905).
   Adopting it is a semantic change: a build, an audit, a re-key and both calibrations again (about 13
   machine hours; the rows should come out the same). Left as it is, the count stays information that
   every calibration reports.
6. KP-017 (open): the findings of the independent recount of the seal. S1: G6 in unit top30 on books
   dominated by costs (see "Open from the recount" above); a measurement is ordered, and a change of the
   G6 statistic is proposed only if it shows an effect on books that can pass the other gates. Also small
   alignments of text and code, each waiting for the next re-key of its kind. Every change needs the
   human's approval. Riding on the batch re-key of 2026-11-25 (see "Now"): the storage of per-lag details in
   the top30 calibration and the code items; the text items wait.
7. KP-018 and KP-019 (approved by delegation on 2026-11-25, in the batch re-key, see "Now"; requests of
   generation 2's researcher): the sandbox to print the speed-limit
   statistic of G6 and a next30 reading on DEV; a way to aggregate or sample a dimensionless expression
   over a timeframe, so that signals built from hourly data can be re-ranked weekly. Both are semantic
   changes (a re-key and both calibrations), so they go into that one re-key.
