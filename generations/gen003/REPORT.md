# Generation 3 - REPORT (one part per round; round 1: PLAN version 1)

Generation 3 is the first under the kernel sealed on 2026-11-26 (semantic 7d923e7e2375986d; G6 0.05 in unit
core, 0.10 in unit top30). Each part is the researcher's text for its round, saved by the coordinator after
its gate (the plan appended only; the programs unchanged; the sandbox rows counted; the ledger verified).

# Round 1 (PLAN version 1)

## Sources
- generations/gen003/PLAN.md: version 1 as committed in 48e12d0 together with the coordinator's rulings (52,751 bytes,
  sha256 3b0fe817b7cacacc...; the researcher's first 50,786 bytes sha256 12af6378563a6b0c...), with the stage-2 run
  log, amendments (none), screen outcome, DEV observations and recommendation appended (62,735 bytes, sha256
  55701bdfea0e84fd...).
- The three sandbox outputs of the researcher session (DEV only; scratch gen003_r1/run_01 to run_03), rows 43 to 45
  (0-indexed) of ledger/sandbox_log.jsonl, `python -m omr.status`, `python -m omr.ledger summary` (trial rows),
  `omr.ledger verify`, `omr.kernel_lock verify`.
- No returns file, no trial detail file, no calibration file and no data file was read. No VAL number exists for any
  generation-3 program: none was submitted.

## What was run
- Unit top30 on the sealed kernel of the batch re-key (semantic 7d923e7e2375986d..., G6 0.05 in core and 0.10 in
  top30). A fresh researcher session wrote PLAN version 1 with three hypotheses, three candidate programs and three
  DEV-only placebos BEFORE any generation-3 sandbox run; each file passed a parse-only check (grammar, units, the
  constant probe on the synthetic panel). The coordinator committed and pushed them unchanged as 48e12d0.
- Coordinator's rulings, recorded in PLAN.md before run 1: weekday as a selector of hours in H1 accepted; d as a float
  param accepted as declared; the placebos and S9 allowed as DEV-only measurements; --g6-lags on runs 1 to 3 and S8
  accepted; KP-017's restriction does not apply (no funding or basis input); the cap of 14 runs stands; two stale
  texts mended or filed (STATE.md "Next"; CONSTITUTION section 13's heading as KP-024).
- The three hypotheses, all dollar neutral (gross 1), all re-decided once a week at the Monday 00:00 open through
  `tf_mean(., weekly)` (the first use of KP-019 in research), none reading funding, mark or index prices. Each takes
  the coin's hourly return net of its rolling 14-day hourly beta to the unit's mean, and ranks one part of the week's
  residual move net of a cross-sectional fit on the whole move (orthogonal to the week's move on every bin), with the
  contrarian sign:
  - H1 gen003_weekend_share: the part made on Saturday and Sunday (thin weekend liquidity) reverses.
  - H2 gen003_heavy_hours: the part made in the coin's own abnormally heavy hours (hourly quote volume over its
    trailing week, ranked across coins each hour) reverses (forced and attention flow).
  - H3 gen003_storm_share: the part made in BTC storm hours (each hour weighted by its share of BTC's recent
    variance) reverses (forced deleveraging in market stress).
- The screen, fixed in advance, read the kernel's new DEV readings (KP-018) as drop conditions: S1 activity, gross,
  liquidation and names held; S2 DEV Sharpe >= 0.6 with the registered sign; S3 two of three years positive; S4 G4's
  DEV reading > 0; S5 G2's DEV reading > 0; S6 next30 DEV Sharpe > 0; S7 the speed-limit statistic <= 0.40 at one to
  three lag steps; S8 the paired lag reading (at most 4 of 10 stale copies at least as good, and the book's median
  Sharpe positive); S9 a placebo below half the book's Sharpe; S10 both G5 corners positive and positive at doubled
  costs.
- 3 sandbox runs of the 12 planned (cap 14): the three defaults, each with --g6-lags. Every default failed at least
  one of S1 to S8, so no placebo (runs 4, 7, 10) and no corner (runs 5, 6, 8, 9, 11, 12) was due. No stage-1 rejection,
  no kernel fault, no refusal; each run 152.9 to 177.0 s (run 1: 2 min 48 s wall time), one at a time, under the
  coordinator's memory rule of stage 2.

## Result
| program | DEV Sharpe | total | costs | C/G | funding paid / received (gross) | G2 DEV | G4 DEV | next30 DEV | speed limit r(1..3) | paired (A of 10; book median B) | names held | years + (2020, 2021, 2022H1) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| H1 weekend_share (n=336, d=5.0) | -1.348 | -0.549 | 0.1720 | 0.206 | 0.2911 / 0.2916 | -2.004 | -1.756 | 0.217 | -0.033, -0.049, 0.009 | 8; -1.740 | 25.0 of 28.0 | 0 of 3 |
| H2 heavy_hours (n=336, k=168) | -0.256 | -0.152 | 0.2286 | 0.274 | 0.3908 / 0.3992 | -1.030 | -0.705 | 0.007 | -0.020, -0.003, -0.059 | 9; -1.200 | 25.1 of 28.0 | 1 of 3 |
| H3 storm_share (n=336, k=168) | 0.349 | 0.132 | 0.2217 | 0.267 | 0.3807 / 0.3729 | -0.379 | -0.071 | -0.740 | 0.032, -0.017, -0.033 | 6; -0.813 | 25.1 of 28.0 | 2 of 3 |

Direction changes 1791, 1675 and 1695; avg gross 0.833, 0.833 and 0.829; rebalances 668, 600 and 573; maxDD 0.580,
0.345 and 0.210; PSR(0) 0.011, 0.343 and 0.711; none liquidated; 75 symbols ever in the unit; lookback 739 h. Every
run printed the benchmark (equal-weight long of the in-play members) at DEV Sharpe 0.619, maxDD 0.847.

| hypothesis | S1 | S2 | S3 | S4 | S5 | S6 | S7 | S8 | S9, S10 | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| H1 | pass | FAIL (-1.348, wrong sign) | FAIL (0 of 3) | FAIL (-1.756) | FAIL (-2.004) | pass (0.217) | pass (max 0.009) | FAIL (8; -1.740) | not due | dropped |
| H2 | pass | FAIL (-0.256, wrong sign) | FAIL (1 of 3) | FAIL (-0.705) | FAIL (-1.030) | pass (0.007) | pass (max -0.003) | FAIL (9; -1.200) | not due | dropped |
| H3 | pass | FAIL (0.349) | pass (2 of 3) | FAIL (-0.071) | FAIL (-0.379) | FAIL (-0.740) | pass (max 0.032) | FAIL (6; -0.813) | not due | dropped |

No counted submission in generation 3. M is unchanged at 6. Tier 1: none. Pool 0 of 5.

## Against each pre-registered DEV falsifier
- H1 ("a wrong DEV sign drops it, never flipped"; the screen S1 to S10): DEV Sharpe -1.348, negative in all three DEV
  years, and negative under both stresses. Falsified on DEV.
- H2 (same screen): DEV Sharpe -0.256, the wrong sign, small; positive only in 2020. Falsified on DEV.
- H3 (same screen): the registered sign (0.349) but below the liveness bar of 0.6, negative under doubled costs and
  under the funding stress, negative on next30, and a failed paired reading. Falsified on DEV.

## Reading
- Holding the week's residual move fixed, the weekend part did not reverse relative to the weekday part on DEV; the
  registered book lost by more than one Sharpe unit in every year. Coins whose move was made more on the weekend did
  better the following week. On next30 the registered book read +0.217. WEAK: one DEV period, one default.
- The heavy-hour part showed nothing usable either way (-0.256), with a sign in the direction of LESSONS 17 and 21
  (heavy, one-sided activity went with continuation on DEV). The storm-hour part reversed a little, as registered,
  but its price P&L before costs and funding (roughly 0.36 of equity over DEV) did not cover its costs twice, and
  next30 disagreed.
- The construction did what it was built to do on the engineering side: weekly targets from hourly inputs paid
  weekly-book costs (0.172 to 0.229 of equity over DEV, inside the estimate of 0.15 to 0.25, though the beta is
  re-estimated every hour); speed-limit readings near zero (-0.059 to 0.032); about 25 of 28 names held despite a
  21-day knownness span.
- G2 was the binding stress for all three: the Sharpe fell by 0.66 to 0.77 under the funding stress against 0.41 to
  0.45 under doubled costs. None of the books reads funding; each paid and received 0.29 to 0.40 of equity in gross
  funding over DEV, and G2 charges half of each.

## What must NOT be concluded
- DEV is now spent as a screen for the mirror of H1 (continuation of the weekend part of a week's residual move, or
  equivalently reversal of its weekday part): the author has seen this result. A later plan that registers it must
  say it was written after this result, and only its counted VAL run could test it. The same holds, with less force,
  for continuation of the heavy-hour part (H2's mirror), which would also lean on LESSONS 17 and 21.
- Three DEV failures say nothing about VAL. No VAL bar was read for any of these programs.
- One default per hypothesis was run; nothing is implied about other values of n, d or k, and none is recommended.
- The placebos were never run, so nothing is known about whether the construction itself (the orthogonal fit, the
  volatility scaling) carries a return of its own on DEV.
- The G2 observation is a yardstick, not a measured cause: why these books' gross funding flows were larger than
  generation 2's H1 was not measured.
- Choosing ideas is still open to hindsight (KP-010); the plan named what could bias each one.

## After the round
M = 6 (generation 0: 4, generation 1: 1, generation 2: 1, generation 3: 0 of 5), N = 5.90, rho 0.021, Tier 1: 0,
pool 0 of 5, one uncounted stage-1 rejection (generation 0). Sandbox runs used in generation 3: 3 of 60
(ledger/sandbox_log.jsonl now 46 rows, the three new rows status ok, source_sha256 equal to the committed files).
`omr.kernel_lock`: OK, sealed (core 0.05, top30 0.1). `omr.ledger verify`: OK, all six chains.

## Requests to the coordinator
- LESSONS.md entries proposed for review (numbering after 38):
  - In unit top30 on DEV, a weekly book contrarian on the weekend part of a coin's residual move, held orthogonal to
    the whole move, lost (DEV Sharpe -1.348, negative in 2020, 2021 and 2022H1): the weekend part tended to persist
    relative to the weekday part. PLAN.md (generation 3) run log, run 1; no trial id. WEAK: DEV only, one default. DEV
    is spent as a screen for the mirror.
  - The heavy-hour part (contrarian, coin-specific volume) and the storm-hour part (contrarian, BTC's variance share)
    of the same construction showed no usable DEV edge after costs and stresses (DEV Sharpe -0.256 and 0.349; G4
    readings -0.705 and -0.071). Runs 2 and 3; no trial id. WEAK.
  - Weekly targets built from hourly inputs through tf_mean(., weekly) traded like weekly rank books (0.172 to 0.229
    of equity over DEV at 12.5 bps per side, 0.21 to 0.27 per unit of gross), although their beta is re-estimated
    every hour: the weekly bar bounds the turnover, unlike the daily-updated beta of LESSONS 24. Runs 1 to 3. WEAK as
    a number; a design yardstick next to LESSONS 19.
  - For a dollar-neutral top30 book that holds a full book through DEV, G2's DEV reading cost more Sharpe than G4's
    (0.66 to 0.77 against 0.41 to 0.45 here; 0.61 against 0.46 for generation 2's H1, 0.76 against 0.33 for H11,
    sandbox rows 40 and 41), whether or not the book reads funding: G2 charges half of the gross funding paid and
    received. Runs 1 to 3 and rows 40 and 41. WEAK as a number; a design yardstick.
  - Process: a screen fixed in advance on the kernel's own DEV readings (KP-018) stopped three defaults in 3 sandbox
    runs of 12 planned, before any placebo or corner run, with no counted trial. Certain as an account of this round;
    not evidence about markets.
- No kernel defect was seen. The sandbox's new readings were printed and logged as documented (the logged values equal
  the printed ones), and every run took under 3 minutes.
