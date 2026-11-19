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
- Data: research_hash `cf26f534cf1c9f4a0bff334c77a041ed66862484a7dc167581cd50562783b4d8`, validated.
- Repository: git, branch main, private GitHub remote; the coordinator commits and pushes at gates
  (`tools/git_gate.ps1`). Research sessions make no git writes.

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
Open: the R-B basket counterexample (a delisting row makes A_k and S_k differ) awaits a ruling.
Next: audit, approval, re-key, both calibrations (core and top30), seal, selftest.

## Open decisions for the human

1. The rule set (CONSTITUTION, LANGUAGE.md) and the lock's approval label still say "human
   confirmation pending".
2. KP-015: widen the universe and add futures-native data (semantic re-key, calibration, audit).
3. KP-014: text-only LANGUAGE.md additions from the fifth audit (keeps the seal and trial ids).
4. KP-002, KP-004, KP-005, KP-010 remain open; KP-009 kernel-side check optional.
