# STATE (2026-11-19, end of the build session: FIX PASS 4 + 5 locked, calibrated and sealed)

## Where things stand

- Kernel v1 (formula language, locality by construction) LOCKED AND SEALED:
  - semantic `4598ef4299ceb43c2bde1b3bf0928fd194054ffc5019322c195e5c330e3f2e8b` (32 files: omr/**,
    requirements.txt) - trial identities and the seal bind to it;
  - text `63c0f6ad94998acf270af9c6fc60f3699e60cbc27fde33fdfce1b530ca242ed7` (22 files:
    CONSTITUTION.md, LANGUAGE.md, tests/**).
  - Approved-by label: "coordinator (Claude), pre-genesis construction, zero trials evaluated; human
    confirmation pending". History: `ledger/kernel_history.jsonl` rows 5 (re-key) and 6 (seal).
  - Seal: G6 threshold 0.05 from `ledger/calibration_4598ef4299ceb43c.json` (sha256
    394e46fed235bcb6f66386b4e87c898b26723fca14d6e1edd1f65db703e30a7a, logged in
    `ledger/calibration_log.jsonl`).
- Calibration v3 on the locked kernel (14.5 min): null pass rate per submitted pair at 0.025 / 0.05 /
  0.10: null A 0.80% / 2.81% / 3.21% (499 submitted), null B 0.00% / 0.80% / 2.20% (500) -> largest
  qualifying 0.05. Oracle power at true Sharpe 1.5 at 0.05: A fast 0.83, slow 0.81; B fast 0.91, slow
  0.81 (achieved mean VAL Sharpe within 0.002 of nominal) -> stop rule passed.
- `python -m omr.selftest`: OK. Tests: 662 pass in about 75 s.
- Data: research_hash `cf26f534cf1c9f4a0bff334c77a041ed66862484a7dc167581cd50562783b4d8`; validate
  PASSED (0 failing counts) after the re-key.
- Ledger: 0 trials, 0 stage-1 rejections. Generation 0 has NOT been run; nothing has been scored on
  VAL. VAL access log: 11 rows (5 retired-kernel calibrations incl. one dry run, 1 synthetic dry run,
  1 calibration of 4598ef42, 2 selftests, 2 temp_ledger_trial rows of the last selftest).
- DEV-only facts: direction changes in DEV at the defaults - SMA cross 16, Donchian 65, RSI 311,
  vol-target trend 92, funding carry 60. The SMA cross is expected to be an uncounted
  `activity_dev` rejection at generation 0.
- Repository: git, branch main, private GitHub remote; the coordinator commits and pushes at gates
  (KP-009). Coordinator files outside the lock: `.gitattributes`, `tools/git_push.ps1`, `.gitignore`.
  Research sessions make no git writes.

## Open decisions for the human / coordinator

1. Confirm the kernel (the lock's approval is pending human confirmation).
2. Generation 0: the SMA-cross baseline fails the DEV activity floor at its pre-registered defaults
   (16 < 20); keep it as a recorded stage-1 rejection or replace it.
3. KP-002, KP-004, KP-005, KP-010 open; KP-009 kernel-side check optional.

## Next session

Generation 0 is ordered by the coordinator after the independent re-audit of this build. Then:
`python -m omr.evaluate strategies/<name>.omr --generation 0` for each gen-0 program (at most 5
counted), then generations/gen000/REPORT.md (required before generation 1). Any kernel change ->
tests, re-key (a semantic change removes the seal), calibrate on the locked kernel, seal.
