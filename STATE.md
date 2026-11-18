# STATE (2026-11-19, build session, FINAL PRE-GENESIS ORDER - in progress)

## Where things stand

- The Python-sandbox kernel (2317921c...) is retired and archived
  (`archive/kernel_2317921c_python_sandbox.zip`). Strategies are now `.omr` programs in a formula
  language that the kernel parses and interprets (LANGUAGE.md); no strategy code is executed.
- Build and tests: done, 582 tests pass in about 30 s.
- Re-keyed ONCE: `2c20fe7752b64de21e11b5885137ae7a4e7021bde9a18157261a519e95642cba` (50 files),
  approved-by label "coordinator (Claude), pre-genesis construction, zero trials evaluated; human
  confirmation pending". NOT sealed yet. `data validate` re-run after the re-key: PASSED.
- Calibration v3 on the locked kernel: running. Seal and selftest: pending.
- Data: Binance USD-M perps, 10 symbols, klines + funding + mark_klines; research_hash
  `cf26f534cf1c9f4a0bff334c77a041ed66862484a7dc167581cd50562783b4d8`. `python -m omr.data validate`
  PASSED with 0 failing counts (pre-re-key run).
- Ledger: 0 trials. Generation 0 has NOT been run.
- DEV-only facts (no VAL result involved): direction changes in DEV at the defaults - SMA cross 16,
  Donchian 67, RSI mean-reversion 311, vol-target trend 92, funding carry 60. The SMA cross is
  therefore expected to be an uncounted `activity_dev` rejection at generation 0.

## Next

Re-key once -> data validate -> calibrate on the locked kernel -> seal -> selftest OK -> STOP.
Generation 0 is ordered by the coordinator after the independent re-audit of this build.
