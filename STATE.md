# STATE (2026-11-19, end of the build session: FIX PASS 6 locked, calibrated (300 / 200 worlds) and sealed)

## Where things stand

- Kernel v1 (formula language, locality by construction, refined constant probe) LOCKED AND SEALED:
  - semantic `7446278556aadd8f4f10e30b75ddebbc2ab272a255f2b8fc0472ed57a18ecad1` (32 files: omr/**,
    requirements.txt) - trial identities and the seal bind to it;
  - text `d51a84cd8c13dc1b545b5f29a06c97a2d381c3bf972853c20381d28cd1b97ef1` (22 files:
    CONSTITUTION.md, LANGUAGE.md, tests/**).
  - Approved-by label: "coordinator (Claude), pre-genesis construction, zero trials evaluated; human
    confirmation pending". History: `ledger/kernel_history.jsonl` rows 7 (re-key) and 8 (seal).
  - Seal: G6 threshold 0.10 from `ledger/calibration_7446278556aadd8f.json` (sha256
    67a71662ee0fca2ee249cccb37520e583ea9286c2c81e2cceb777ea57c7e177e, logged in
    `ledger/calibration_log.jsonl`). Per CONSTITUTION section 8 the seal COUNTS only once the
    coordinator has pushed the artifact, its log row and kernel.lock in one commit and an independent
    auditor has recomputed the counts and the rule from the artifact.
- Calibration v3 on the locked kernel (38 min; 300 worlds per null, 200 per oracle configuration):
  null pass rate per submitted pair at 0.025 / 0.05 / 0.10: null A 10 / 26 / 44 of 1,498 (0.67% /
  1.74% / 2.94%), null B 6 / 18 / 35 of 1,500 (0.40% / 1.20% / 2.33%) -> largest qualifying 0.10
  (null A is one pass from the 3% limit: 45 would be 3.00%+). Oracle power at true Sharpe 1.5 at 0.10:
  A fast 0.84, slow 0.85; B fast 0.91, slow 0.85 -> stop rule passed.
- `python -m omr.selftest`: OK. Tests: 672 pass in about 76 s.
- Data: research_hash `cf26f534cf1c9f4a0bff334c77a041ed66862484a7dc167581cd50562783b4d8`; validate
  PASSED (0 failing counts) after the re-key.
- Ledger: 0 trials, 0 stage-1 rejections. Generation 0 has NOT been run; nothing has been scored on
  VAL. VAL access log: 15 rows (calibration, selftest and dry-run rows of this and earlier kernels,
  plus the temp_ledger_trial rows of the selftests).
- DEV-only facts: direction changes in DEV at the defaults - SMA cross 16, Donchian 65, RSI 311,
  vol-target trend 92, funding carry 60. The SMA cross is expected to be an uncounted
  `activity_dev` rejection at generation 0.
- Repository: git, branch main, private GitHub remote; the coordinator commits and pushes at gates
  (KP-009). Research sessions make no git writes.

## Open decisions for the human / coordinator

1. Confirm the kernel (the lock's approval is pending human confirmation) and make the seal count
   (one pushed commit + independent recomputation, CONSTITUTION section 8).
2. Generation 0: the SMA-cross baseline fails the DEV activity floor at its pre-registered defaults
   (16 < 20); keep it as a recorded stage-1 rejection or replace it.
3. Before every counted submission the coordinator reads the program for near-constants and hidden
   thresholds (RESEARCH_PLAYBOOK section 5).
4. KP-002, KP-004, KP-005, KP-010 open; KP-009 kernel-side check optional.

## Next session

Generation 0 is ordered by the coordinator after the independent re-audit of this build. Then:
`python -m omr.evaluate strategies/<name>.omr --generation 0` for each gen-0 program (at most 5
counted), then generations/gen000/REPORT.md (required before generation 1). Any kernel change ->
tests, re-key (a semantic change removes the seal), calibrate on the locked kernel, seal.
