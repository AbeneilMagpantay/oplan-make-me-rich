# STATE (2026-11-19, end of the build session, FINAL PRE-GENESIS ORDER complete)

## Where things stand

- Kernel v1, formula language, LOCKED AND SEALED:
  `2c20fe7752b64de21e11b5885137ae7a4e7021bde9a18157261a519e95642cba` (50 files). Approved-by label
  "coordinator (Claude), pre-genesis construction, zero trials evaluated; human confirmation
  pending". Seal: G6 threshold 0.025 from `ledger/calibration_2c20fe7752b64de2.json` (sha256
  3019d5782bd01fe70c42dd7fba5697549f1a4c981d6308301c5b8d9e3411e7cc). History:
  `ledger/kernel_history.jsonl` rows 3 (re-key) and 4 (seal).
- Strategies are `.omr` programs (LANGUAGE.md) parsed and interpreted by the kernel; no strategy code
  is executed. The Python-sandbox kernel 2317921c is archived (`archive/`).
- Tests: 582 pass in about 30 s. `python -m omr.selftest`: OK (11 s).
- Data: Binance USD-M perps, 10 symbols, klines + funding + mark_klines; research_hash
  `cf26f534cf1c9f4a0bff334c77a041ed66862484a7dc167581cd50562783b4d8`; `python -m omr.data validate`
  PASSED (0 failing counts) before and after the re-key.
- Calibration v3 (on the locked kernel, 39 min): null pass rate per submitted pair at 0.025 / 0.05 /
  0.10: null A 1.20% / 3.21% / 3.81% (499 submitted), null B 0.20% / 1.20% / 2.80% (500 submitted) ->
  0.025 is the only qualifying value. Oracle power at true Sharpe 1.5 at 0.025: A fast 0.83, slow
  0.72; B fast 0.91, slow 0.79 (achieved mean VAL Sharpe within 0.002 of nominal) -> stop rule passed.
- Ledger: 0 trials, 0 stage-1 rejections. Generation 0 has NOT been run. VAL access log: 6 rows
  (3 retired-kernel calibrations, 1 calibration v3 dry run, 1 calibration v3, 1 selftest).
- DEV-only facts: direction changes in DEV at the defaults - SMA cross 16, Donchian 67, RSI
  mean-reversion 311, vol-target trend 92, funding carry 60. The SMA cross is therefore expected to
  be an uncounted `activity_dev` rejection at generation 0.
- Repository: the project is its own git repository (branch main, private GitHub remote); the
  coordinator commits and pushes at gates (KP-009 addressed operationally). Coordinator files outside
  the lock: `.gitattributes`, `tools/git_push.ps1`, `.gitignore` (tracks data/manifest.json and
  data/validation.json). Research sessions make no git writes.

## Open decisions for the human / coordinator

1. Confirm the kernel (the lock's approval is pending human confirmation).
2. Generation 0: the SMA-cross baseline fails the DEV activity floor at its pre-registered defaults
   (16 < 20); keep it as a recorded stage-1 rejection or replace it.
3. KP-002, KP-004, KP-005, KP-010 open; KP-009 kernel-side check optional.

## Next session

Generation 0 is ordered by the coordinator after the independent re-audit of this build. Then:
`python -m omr.evaluate strategies/<name>.omr --generation 0` for each gen-0 program, at most 5
counted. Any kernel change -> tests, re-key (removes the seal), calibrate on the locked kernel, seal.
