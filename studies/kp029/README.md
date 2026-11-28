# KP-029 premise study: the spot market of the same coins (generation 4, round 2)

A study OUTSIDE the kernel and outside the sandbox, on DEV only (2020-01-01 to 2022-06-30), decided by the human on
2026-11-28 (KERNEL_PROPOSALS.md, KP-029 and "The human's decision on KP-029"). It asks one question cheaply, before
any build: do the spot market's volume and order flow of the same coins add information that a weekly top30 book
could use? The plan, the hypotheses, the exact pass rule and the guards are in `generations/gen004/PLAN.md`:
"PLAN version 2 (round 2: the spot premise study, KP-029)", the coordinator's rulings after it, and the stage-1b
amendment. Those texts rule; this file only says how to run. Three hypotheses remain: H-S1, H-S2, H-S4 (H-S3 and its
control were struck before any run, rulings 3 and 4).

## Rules (from KP-029 and the plan)

- No kernel file is changed. Nothing here is imported by `omr/`. The kernel is CALLED, never copied or patched:
  `omr.upipeline` (load_udata, Blocked, stage1_u, dev_speed_limit, dev_names_held, dev_paired_lags, next30_score),
  `omr.pipeline.dev_sharpe_of`, `omr.stats`, `omr.lang`, `omr.universe.usable_of`. `omr.sandbox` and
  `omr.evaluate` are never imported or run; nothing is written under `ledger/` or `data/`.
- Perpetual rows only through the kernel's loaders with the `dev_end` ceiling. No ValHandle, no `val_end`, no
  `latest`, no VAL row of any kind.
- Spot files only of months 2019-12 to 2022-06 (hard-coded; `kp029_spot.url` refuses any other month), stored in
  `_build/kp029_study/spot/<SYMBOL>/` (git-ignored), sha256-checked against their `.CHECKSUM` at download AND at
  every read; rows after 2022-06-30 23:00 UTC are dropped on load.
- The spot market enters the kernel's language through two SLOTS of the perpetual klines table, for study programs
  only: `volume` = SPOT quote volume (USDT), `taker_buy_volume` = SPOT taker-buy quote volume (USDT), of the same
  coin and hour. A missing spot hour, a spot bar unusable by the kernel's S3 rule, or a spot close more than 50% from
  the perpetual's close of the same hour (ratio outside 0.5 .. 1.5; ruling 6) is UNKNOWN in both slots, never zero,
  with one exception (ruling 5): at a spot OUTAGE hour (at or after the first stored spot BTCUSDT row, an hour with no
  BTCUSDT row) a pair without a row of its own gets a zero row if it had a real row earlier; S3 then decides (at most
  24 non-trading hours in a row) and the guard verdict is that of its last real row. `1000XXXUSDT` maps to spot
  `XXXUSDT` (price x1000 in the guard). Every other column, the membership, the in-play mask and the engine are the
  kernel's.
- Before the first evaluation, `run_study.py --coverage` counts the spot data and checks the tripwires of rulings 5
  and 6 (outage share under 95%, an outage block over 24 h, over 200 outage hours, more than 5 pairs with more than
  24 guard-rejected in-play hours); any of them stops every evaluation for a report to the coordinator.
- Every evaluation runs the kernel's stage 1 and the study's truncation test (6 fixed + 2 random cuts, the input
  rebuilt from the rows up to each cut) BEFORE any reading is computed; a run that fails the truncation test is
  VOID. Every evaluation, failed ones included, is appended to `run_log.jsonl` (with the sha256 of every study file)
  before anything is printed.
- The budget and order (ruling 8: 3 defaults, at most 9 control and corner runs, 2 in reserve, cap 14) are enforced
  by `run_study.py`.

## Files

| file | what | stage |
|---|---|---|
| `kp029_spot.py` | ceilings, symbol map, CSV parsing, hash-at-read spot store | both |
| `kp029_features.py` | the feature builder: spot rows -> the two slots (outage rule, guard, S3 rule), the study UData | both |
| `kp029_eval.py` | the evaluator (kernel calls in the sandbox's order), screen W1..W8, corner and control rules, the truncation test | both |
| `programs/kp029_hs*.omr` | the three hypotheses H-S1, H-S2, H-S4 | 2 |
| `programs/kp029_cs*.omr` | their controls C-S1, C-S2, C-S4 (coverage matched) | 2 |
| `guard_table.py` | stage 1b: perpetual close against index close on the kernel's DEV rows (ruling 6) | 1b (run) |
| `guard_table.json` | its output (counts and the hours beyond 10%) | 1b |
| `validate_evaluator.py` | stage 1: reproduces the logged sandbox readings of three registered programs | 1 (run) |
| `validation_stage1.json` | its output (DEV readings of registered programs, already logged) | 1 |
| `synthetic_tests.py` | stage 1: look-ahead, missing-hour, guard, ceiling and pipeline tests on synthetic data | 1 (run) |
| `spot_plan.py` | stage 1: the download plan from the kernel's DEV membership (no network) | 1 (run) |
| `spot_symbols.json` | its output: perpetuals, spot pairs, months, counts | 1 |
| `download_spot.py` | stage 2: the downloader (`--go`) | 2 only |
| `run_study.py` | stage 2: one evaluation per call, logged; `--summary` gives the verdict | 2 only |
| `spot_coverage.json` | stage 2: spot data counts and tripwires (`run_study.py --coverage`), before any evaluation | 2 |
| `run_log.jsonl` | stage 2: every evaluation (created by the first run) | 2 |

## How to run (from the project root; Windows PowerShell)

Stage 1 (done in the stage-1 session):

    .venv\Scripts\python.exe -I studies\kp029\validate_evaluator.py
    .venv\Scripts\python.exe -I studies\kp029\synthetic_tests.py
    .venv\Scripts\python.exe -I studies\kp029\spot_plan.py <desk-study listing of spot folder names>
    .venv\Scripts\python.exe -I studies\kp029\guard_table.py                (stage 1b)

Stage 2 (only when the coordinator orders it, after stage 1 is committed and on the remote):

    .venv\Scripts\python.exe -I studies\kp029\download_spot.py --go
    .venv\Scripts\python.exe -I studies\kp029\run_study.py --coverage      (counts and tripwires; no book is read)
    (if it prints STOP: report to the coordinator; every evaluation is refused)
    .venv\Scripts\python.exe -I studies\kp029\run_study.py kp029_hs1_share_shift
    .venv\Scripts\python.exe -I studies\kp029\run_study.py kp029_hs2_spot_flow
    .venv\Scripts\python.exe -I studies\kp029\run_study.py kp029_hs4_rally_carrier
    then, only for a hypothesis that passed the screen at its default, in this order:
    .venv\Scripts\python.exe -I studies\kp029\run_study.py <its control>
    .venv\Scripts\python.exe -I studies\kp029\run_study.py <hypothesis> --label corner08
    .venv\Scripts\python.exe -I studies\kp029\run_study.py <hypothesis> --label corner12
    .venv\Scripts\python.exe -I studies\kp029\run_study.py --summary

`-I` keeps the interpreter from loading code from the current or the script's folder; every script puts the
project root and its own folder on the path itself. One heavy run at a time, each started with at least
1,000,000 KB of free physical memory and 4,000,000 KB of free commit (checked by the scripts).
