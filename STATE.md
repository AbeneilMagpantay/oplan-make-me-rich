# STATE (2026-11-19: generation 0 complete)

## Where things stand

- Kernel (sealed): semantic `7446278556aadd8f4f10e30b75ddebbc2ab272a255f2b8fc0472ed57a18ecad1`
  (32 files), text `d51a84cd8c13dc1b545b5f29a06c97a2d381c3bf972853c20381d28cd1b97ef1` (22 files),
  G6 threshold 0.10 from `ledger/calibration_7446278556aadd8f.json`. Seal recounted by the fifth
  audit; artifact, calibration-log row and seal are in commit d2c2d4f.
- Generation 0 ran on that kernel (commit d2c2d4f, 2026-11-19). Results in
  `generations/gen000/REPORT.md`: SMA cross rejected in stage 1 (`activity_dev`, uncounted);
  Donchian, RSI mean reversion, vol-target trend and funding carry evaluated, none Tier 1; the
  vol-target trend was the only positive VAL Sharpe (0.384; benchmark 0.921).
- Ledger: M = 4 counted trials (generation 0: 4 of 5), N = 4.00, Tier 1: 0, pool 0 of 5, one
  uncounted stage-1 rejection; all chains verify.
- Data: research_hash `cf26f534cf1c9f4a0bff334c77a041ed66862484a7dc167581cd50562783b4d8`, validated.
- Repository: git, branch main, private GitHub remote; the coordinator commits and pushes at gates.
  Research sessions make no git writes.

## Next session does first

Generation 1:
1. Read LESSONS.md, generations/gen000/REPORT.md, `python -m omr.ledger summary`, `python -m
   omr.status` (trial rows and status only; never ledger/returns or ledger/trials/).
2. Write generations/gen001/PLAN.md with 3 to 5 pre-registered hypotheses (rule as program text,
   mechanism, falsifier, relation to earlier trials) BEFORE any evaluation.
3. Explore on DEV only with `python -m omr.sandbox`.
4. The coordinator reads each program's source for near-constants and hidden thresholds
   (RESEARCH_PLAYBOOK section 5) before any counted submission.
5. At most 5 counted submissions: `python -m omr.evaluate strategies/gen001_<idea>.omr --generation 1`;
   then generations/gen001/REPORT.md.

## Open decisions for the human

1. The rule set (CONSTITUTION, LANGUAGE.md) and the lock's approval label still say "human
   confirmation pending": the human has not yet confirmed the kernel.
2. KP-014 (text-only LANGUAGE.md additions from the fifth audit) is open: a text-only re-key keeps the
   seal and trial ids, but needs the human's approval now that trials exist.
3. KP-002, KP-004, KP-005, KP-010 remain open; KP-009 kernel-side check optional.
