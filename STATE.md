# STATE (2026-11-19: generations 0 and 1 complete)

## Where things stand

- Kernel (sealed): semantic `7446278556aadd8f4f10e30b75ddebbc2ab272a255f2b8fc0472ed57a18ecad1`
  (32 files), text `d51a84cd8c13dc1b545b5f29a06c97a2d381c3bf972853c20381d28cd1b97ef1` (22 files),
  G6 threshold 0.10 from `ledger/calibration_7446278556aadd8f.json`. Seal recounted by the fifth
  audit; artifact, calibration-log row and seal are in commit d2c2d4f.
- Generation 0 (`generations/gen000/REPORT.md`): five textbook baselines; SMA cross rejected in
  stage 1 (uncounted); four evaluated, none Tier 1; best VAL Sharpe 0.384.
- Generation 1 (`generations/gen001/REPORT.md`): five pre-registered hypotheses, 18 DEV sandbox runs,
  one counted submission. gen001_tsmom_long_flat (24778ca0881b6c26): VAL Sharpe 0.830, PSR(0) 0.926,
  passes eight gates and fails G6 (p 0.279). Not Tier 1.
- Ledger: M = 5 counted trials (generation 0: 4, generation 1: 1), N = 4.86, Tier 1: 0, pool 0 of 5,
  one uncounted stage-1 rejection; all chains verify.
- Benchmark over VAL, for reference: long BTC and ETH half each, Sharpe 0.921.
- Data: the counted trials above were scored on research_hash
  `cf26f534cf1c9f4a0bff334c77a041ed66862484a7dc167581cd50562783b4d8`. The data store has since been
  extended and hole-filled for the KP-015 build (research hash `28d9084a8c5c7659...`), which is not
  locked yet.
- Repository: git, private GitHub remote. `main` holds approved, verifying states only (HEAD 521687f).
  The unapproved KP-015 build is on branch `kp015-build` (snapshots bd6920b, 973e413, e4e44e2, 32e32e0,
  then fix pass 6)
  and is merged into `main` only after approval, re-key and seal. The coordinator commits and pushes at
  gates (`tools/git_gate.ps1`, which pushes the current branch). Research sessions make no git writes.

## How a generation runs (as done in generation 1)

1. A fresh researcher session reads LANGUAGE.md, RESEARCH_PLAYBOOK.md, LESSONS.md, the last two
   REPORTs, trial rows and `python -m omr.status` (never ledger/returns, ledger/trials/ or data/).
2. It writes generations/genNNN/PLAN.md with 3 to 5 hypotheses BEFORE its first sandbox run, then
   explores on DEV only with `python -m omr.sandbox` (at most 60 runs, every run logged in the plan).
3. The coordinator commits and pushes the plan and programs BEFORE scoring, reads each candidate's
   source (RESEARCH_PLAYBOOK section 5), and runs every counted `python -m omr.evaluate` itself.
4. REPORT.md, LESSONS.md and this file are updated; the coordinator commits and pushes.

## Next

Generation 2 can open (generations/gen001/REPORT.md exists). The evidence so far (LESSONS 8 to 10)
says single-coin timing rules on two instruments mostly collect the market's drift. The coordinator's
recommendation is KP-015 (a point-in-time universe for market-neutral rules, and open interest,
long/short ratios and basis as new data) before spending many more counted trials on the current
two-coin instrument. KP-015 changes the kernel and needs the human's approval.

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
Still to do before the re-key: a small end-to-end pilot of the universe calibration (dry run, outputs in
scratch). It needs about 2.6 GiB of free memory and was refused at 1.6; a waiting script starts it.
Next: the pilot, the human's approval, re-key, both calibrations (core about 40 minutes; top30 about 88
worker-hours: about 22 hours with 4 workers, which need about 7 GiB free, or about 4 days with 1 worker;
resumable; the oracle phases come first and show after about a third of the run whether the seal can
succeed), seal of both units, selftest, independent recount, merge into `main`.

## Open decisions for the human

1. The rule set (CONSTITUTION, LANGUAGE.md) and the lock's approval label still say "human
   confirmation pending".
2. KP-015 (built, unlocked; audit clean as of fix pass 6): approve the semantic re-key. The re-key
   itself waits for the pilot above. Run time on this PC: see Next.
3. KP-014: text-only LANGUAGE.md additions from the fifth audit (keeps the seal and trial ids).
4. KP-002, KP-004, KP-005, KP-010 remain open; KP-009 kernel-side check optional.
5. KP-016 (open, not blocking): count the null pass rate over DEV-positive submissions only.
