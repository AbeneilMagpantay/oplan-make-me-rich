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

# Round 2 (PLAN version 2)

## Sources
- generations/gen003/PLAN.md: version 2 as committed in afce52a together with the coordinator's round-2 rulings
  (127,710 bytes, sha256 af92ebcc682af2da...; the researcher's version 2 ended at 124,880 bytes, sha256
  827ee8a7c01abbf0...), with the stage-2 run log, amendments (none), screen outcome, DEV observations and recommendation
  appended (139,818 bytes, sha256 5efd3dfa569d66c5...).
- The three sandbox outputs of the researcher session (DEV only; scratch gen003_r2/run_01 to run_03), rows 46 to 48
  (0-indexed) of ledger/sandbox_log.jsonl, `python -m omr.status`, `python -m omr.ledger summary` (trial rows),
  `omr.ledger verify`, `omr.kernel_lock verify`.
- No returns file, no trial detail file, no calibration file and no data file was read. No VAL number exists for any
  generation-3 program: none was submitted.

## What was run
- Unit top30 on the sealed kernel of the batch re-key (semantic 7d923e7e2375986d..., G6 0.05 in core and 0.10 in
  top30). The coordinator's frame for this round: the one pattern DEV kept showing (continuation of a recent move;
  LESSONS 16, 17, 21, 23, 26, 39, 43) had never had a counted trial, because every continuation rule had been written
  after a DEV result; this round could pre-register such rules openly, with the DEV numbers that shaped them, a reason
  beyond them, weekly construction, a screen fixed in advance on the kernel's readings, and at most two candidates.
- A fresh researcher session wrote PLAN version 2 with three hypotheses, three candidate programs and three DEV-only
  controls BEFORE any round-2 sandbox run; each file passed a parse-only check. The coordinator committed and pushed
  them unchanged as afce52a.
- Coordinator's rulings, recorded in PLAN.md before run 1: H4 accepted under this round's frame, with its tension with
  LESSONS 23 recorded (it is the idea of generation 2's H6 in a new construction); H5 and H6 accepted on the same terms;
  the screen as written; the controls allowed as DEV-only measurements; one set of diagnostics for H4 and H6, H4 first;
  --g6-lags on runs 1 to 3; KP-017's restriction does not apply, KP-020 does; cap 11 runs (9 planned, 2 in reserve);
  at most ONE program of the round to get a counted trial without a further decision; a survivor is not thereby
  submitted.
- The three hypotheses, all continuation rules written after DEV results, dollar neutral (gross 1), re-decided once a
  week through tf_mean or tf_last, none reading funding, mark or index prices:
  - H4 gen003_multiweek_momentum: the coin's residual move of the last 3 weeks (hourly residual to the unit's mean,
    rolling 14-day beta; G5 at 2 or 4 weeks), in units of its residual volatility, continues (LESSONS 16 and 23).
  - H5 gen003_jump_continuation: the sign mirror of generation 2's H5, sampled weekly: coins whose last 21 daily
    residual returns were right-skewed keep outperforming (LESSONS 21; MAX momentum in crypto as outside support).
  - H6 gen003_week_continuation: round 1's x with the continuation sign: last week's residual move continues
    (LESSONS 16).
- The screen, fixed in advance: round 1's items at round 1's thresholds (S1 activity, gross, liquidation, names held;
  S2 DEV Sharpe >= 0.6; S3 two of three years; S4 G4's DEV reading > 0; S5 G2's DEV reading > 0; S7 speed limit <= 0.40;
  S8 paired reading A <= 4 and B > 0; S10 both G5 corners positive and positive at doubled costs), S6 tightened (next30
  DEV Sharpe >= 0.3) and S9 a control comparison (plain continuation for H4 and H6, the drift of the same days for H5).
  The plan listed which readings were predictable from the parents (S2, S3, partly S6 and S10) and did not count them
  as support; no item of its own was given to the known 2022H1 weakness of multi-week residual momentum.
- 3 sandbox runs of the 9 planned (cap 11): the three defaults, each with --g6-lags. Every default failed at least one
  of S1 to S8, so no control (runs 4 and 7) and no corner (runs 5, 6, 8 and 9) was due. No stage-1 rejection, no kernel
  fault, no refusal; each run 84.0 to 140.3 s, one at a time, under the coordinator's memory rule.

## Result
| program | DEV Sharpe | total | costs | C/G | funding paid / received (gross) | G2 DEV | G4 DEV | next30 DEV | speed limit r(1..3) | paired (A of 10; book median B) | names held | years + (2020, 2021, 2022H1) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| H4 multiweek_momentum (n=336, m=3) | 0.541 | 0.305 | 0.2399 | 0.293 | 0.5096 / 0.5701 | -0.015 | 0.314 | -0.100 | -0.054, -0.061, -0.024 | 9; -1.431 | 23.5 of 28.0 | 2 of 3 (SR 2.015, 1.176, -2.716) |
| H5 jump_continuation (n=21) | 0.705 | 0.406 | 0.2386 | 0.298 | 0.5443 / 0.5347 | 0.105 | 0.447 | -0.820 | -0.107, -0.062, 0.018 | 10; -1.785 | 22.2 of 28.0 | 2 of 3 (SR 2.384, 0.891, -2.289) |
| H6 week_continuation (n=336) | 0.836 | 0.604 | 0.3754 | 0.451 | 0.5741 / 0.5988 | 0.305 | 0.501 | -0.314 | -0.006, -0.010, 0.022 | 5; -0.757 | 25.1 of 28.0 | 2 of 3 (SR 2.933, 0.401, -0.674) |

Direction changes 1074, 1047 and 1780; avg gross 0.818, 0.801 and 0.833; rebalances 652, 609 and 647; maxDD 0.400, 0.341
and 0.284; PSR(0) 0.801, 0.869 and 0.911; net funding -0.0604 (received), 0.0096 (paid) and -0.0247 (received); none
liquidated; 75 symbols ever in the unit; lookback 1243, 1605 and 739 h. Every run printed the benchmark (equal-weight
long of the in-play members) at DEV Sharpe 0.619, maxDD 0.847.

| hypothesis | S1 | S2 | S3 | S4 | S5 | S6 | S7 | S8 | S9, S10 | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| H4 | pass | FAIL (0.541) | pass (predictable) | pass (0.314) | FAIL (-0.015) | FAIL (-0.100) | pass (max -0.024) | FAIL (9; -1.431) | not due | dropped |
| H5 | pass | pass (0.705, predictable) | pass (predictable) | pass (0.447) | pass (0.105) | FAIL (-0.820) | pass (max 0.018) | FAIL (10; -1.785) | not due | dropped |
| H6 | pass | pass (0.836, predictable) | pass (partly predictable) | pass (0.501) | pass (0.305) | FAIL (-0.314) | pass (max 0.022) | FAIL (5; -0.757) | not due | dropped |

No counted submission in generation 3. M is unchanged at 6. Tier 1: none. Pool 0 of 5.

## Against each pre-registered DEV falsifier
- H4 ("a negative DEV Sharpe drops it, never flipped"; the screen S1 to S10): the registered sign (0.541) but below the
  liveness bar of 0.6, negative under the funding stress and on next30, and a failed paired reading (9 of 10 stale
  copies at least as good; the book's median Sharpe on the common names -1.431 over the last 365 days of DEV).
  Falsified on DEV.
- H5 (same screen): the registered sign (0.705), positive under both stresses, but -0.820 on next30 and a failed paired
  reading (10 of 10; -1.785). Falsified on DEV. Its drift control was never due, so whether its DEV result came from
  jumps or from drift is not known.
- H6 (same screen): the registered sign (0.836), positive under both stresses, but -0.314 on next30 and a failed paired
  reading (5 of 10; -0.757). Falsified on DEV.

## Reading
- All three continuation books had the registered sign on DEV, and all three earned it early: Sharpe 2.0 to 2.9 in
  2020, 0.4 to 1.2 in 2021, -0.7 to -2.7 in 2022H1, and each lost on the common names over the last 365 days of DEV.
  On these weekly constructions, after costs, the DEV continuation of LESSONS 16, 21, 23 and 43 was concentrated in 2020
  and was gone by the last year of DEV. WEAK: one DEV period, one default each, rules written after DEV results.
- All three read negative on next30 (-0.100, -0.820, -0.314). The plan had called H6's next30 reading largely
  predictable as positive, because the one-week residual reversal had read -1.030 there (row 41); it was not: in ranks
  31 to 60 both signs of the one-week rule lost after costs on DEV.
- The items nobody had seen dropped all three (S6 and S8 for each; S5 for H4 as well). Two outcomes the plan had called
  predictable came out otherwise: H4's DEV Sharpe (the parents suggested about 1.0 to 1.4; it read 0.541) and H6's
  next30 sign.
- Costs were far above the plan's estimates: 0.240, 0.239 and 0.375 of equity over DEV (C/G 0.29, 0.30 and 0.45),
  against estimates of 0.09 to 0.23 and against 0.17 to 0.23 for round 1's books on the same weekly bins. The weekly
  skewness book cost more than generation 2's daily-updated form of the same statistic (0.239 against 0.140). Suggestive
  cause, not measured: a continuation book holds the movers, which keep moving, and a target held for a week is traded
  back against their drift, which a daily-updated target partly follows. The books also paid and received more gross
  funding (1.08 to 1.17 of equity, paid plus received) than any earlier top30 book read by the sandbox, and G2 again cost
  more Sharpe than G4 (0.53 to 0.60 against 0.23 to 0.34).

## What must NOT be concluded
- Three DEV failures say nothing about VAL. No VAL bar was read for any of these programs, and none was submitted: the
  one pattern DEV kept showing has still had no counted trial.
- These rules were written after DEV results, so their DEV numbers were never evidence for them; their failure says
  that the DEV pattern was weaker, later in DEV and in next30 than the parents' numbers suggested once it was built
  weekly and paid its costs, not that continuation is absent in crypto.
- One default per hypothesis was run; nothing is implied about other values of n, m or the formation window, and none
  is recommended. The controls and corners were never run, so whether the residual, the scaling or the jump part adds
  anything on DEV is not known.
- DEV is now spent for these three forms and their readings (next30, the paired comparison, the per-year rows). A later
  continuation variant built to get past S6 or S8 would be fitted to readings now seen.
- The cost observation is a yardstick, not a measured cause.
- Choosing ideas is still open to hindsight (KP-010); the plan named what could bias each one.

## After the round
M = 6 (generation 0: 4, generation 1: 1, generation 2: 1, generation 3: 0 of 5), N = 5.90, rho 0.021, Tier 1: 0, pool
0 of 5, one uncounted stage-1 rejection (generation 0). Sandbox runs used in generation 3: 6 of 60 (rounds 1 and 2: 3
and 3; ledger/sandbox_log.jsonl now 49 rows, the three new rows status ok, stage1 full, source_sha256 equal to the
committed files). `omr.kernel_lock`: OK, sealed (core 0.05, top30 0.1). `omr.ledger verify`: OK, all six chains.

## For the coordinator's decision
No hypothesis survived the screen, so there is no candidate to decide on; rulings (10) and (11) do not come into play.

## Requests to the coordinator
- LESSONS.md entries proposed for review (numbering after 43):
  - 44. In unit top30 on DEV, three weekly continuation books written after DEV results (3-week residual momentum, jump
    continuation as the mirror of the skewness rule of LESSONS 21, one-week residual continuation) had the registered
    sign but DEV Sharpe of only 0.541, 0.705 and 0.836 after costs; each was strongly positive in 2020 (Sharpe 2.0 to
    2.9) and negative in 2022H1 (-0.7 to -2.7), lost on the common names over the last 365 days of DEV (paired reading,
    book median -0.76 to -1.79), and read negative on next30 (-0.10, -0.82, -0.31). The DEV continuation of lessons 16,
    21, 23 and 43 was concentrated early in DEV and did not show in ranks 31 to 60 after costs. Generation 3 PLAN run
    log, round 2, runs 1 to 3; no trial id. WEAK: DEV only, one default each, rules written after DEV results.
  - 45. Weekly continuation books cost 0.239 to 0.375 of equity over DEV at 12.5 bps per side (0.29 to 0.45 per unit of
    gross), above round 1's weekly books on the same bins (0.172 to 0.229) and above the plan's estimates; a weekly
    sample of the 21-day skewness book cost more than its daily-updated form in generation 2 (0.239 against 0.140); and
    these books paid and received 0.51 to 0.60 of equity in gross funding each way. Suggestive only: a target held for a
    week is traded back against the drift of the movers a continuation book holds. Round 2, runs 1 to 3. WEAK as a
    number; a design yardstick next to lessons 19, 24 and 41.
  - 46. Process: a screen fixed in advance, whose unseen readings (next30 and the paired comparison) were allowed to drop
    rules written after DEV results, stopped all three defaults in 3 sandbox runs of 9 planned, with no counted trial;
    two outcomes the plan had called predictable from the parents did not come out as expected (a DEV Sharpe under the
    liveness bar; a next30 sign that a mirror's reading had seemed to fix, but a mirror pays its costs again). PROCESS.
- No kernel defect was seen. The sandbox's readings were printed and logged as documented (logged values equal the
  printed ones); every run took under 2.5 minutes.

# Round 3 (PLAN version 3, the wide screen)

## Sources
- generations/gen003/PLAN.md: version 3 as committed in 92d1a5a together with the coordinator's round-3 rulings
  (169,613 bytes, sha256 da83515e35b8c1d5...), with the stage-2 run log, amendments (none), screen outcome, DEV
  observations, recommendation and a one-paragraph correction appended (180,229 bytes, sha256 7b27f7c6ea7c621c...).
- The eleven sandbox outputs of the researcher session (DEV only; scratch gen003_r3/run_01 to run_11), rows 49 to 59
  (0-indexed) of ledger/sandbox_log.jsonl, `python -m omr.status`, `python -m omr.ledger summary` (trial rows),
  `omr.ledger verify`, `omr.kernel_lock verify`.
- No returns file, no trial detail file, no calibration file and no data file was read. No VAL number exists for any
  round-3 program: none was submitted.

## What was run
- Unit top30 on the sealed kernel of the batch re-key (semantic 7d923e7e2375986d..., G6 0.05 in core and 0.10 in
  top30). The first round in the form of a WIDE SCREEN (RESEARCH_PLAYBOOK 8b as amended on 2026-11-27, after the
  human's direction to go on in top30): eleven compactly registered ideas from eight mechanism classes, none from a
  closed class, one default run each against one screen fixed in advance (W1 to W8).
- A fresh researcher session wrote PLAN version 3 and eleven programs BEFORE any round-3 sandbox run; each parsed. The
  coordinator committed them as 92d1a5a after rulings: sparse books are outside this screen by intent; a calendar
  schedule fails the speed limit by construction, so calendar fields only select hours of a volume series; W-01 and
  W-02 open with a condition (a plain four-week continuation control and a pre-cost margin of 0.5 before any
  recommendation); W-09 and W-10 open (W-10 screen-only under KP-017); calendar thresholds as params accepted; W-11
  accepted; cap 19 runs.
- The eleven ideas, all dollar neutral (gross 1), decided once a week: W-01 distance below the 6-week high (anchoring),
  W-02 price over the 4-week VWAP (capital-gains overhang), W-03 short residual-variance shocks, W-04 long illiquidity
  shocks orthogonal to the week's move, W-05 long a rising US-hour share of volume, W-06 short a rising weekend share
  of volume, W-07 long net lower-wick absorption, W-08 short decoupling from BTC, W-09 long 2-week over 8-week volume
  growth, W-10 short a rise in basis churn per unit of price movement (reads index_close), W-11 the equal-weight sum of
  W-01, W-03 and W-07.
- 11 sandbox runs of the cap of 19: the eleven defaults with --g6-lags, in the registered order. No idea passed W1 to
  W8, so no corner and no control was due. No stage-1 rejection, no kernel fault, no refusal; 82 to 233 s per run, one
  at a time, under the coordinator's memory rule.

## Result
| idea | DEV SR | G4 DEV | G2 DEV | pre-cost | next30 | r max (1..3) | A of 10; B | years + (SR 2020 / 2021 / 2022H1) | costs (C/G) | first failed |
|---|---|---|---|---|---|---|---|---|---|---|
| W-01 high_anchor | 1.558 | 1.296 | 0.888 | 1.820 | 0.601 | 0.129 | 6; -0.549 | 2 (3.721 / 1.831 / -2.093) | 0.302 (0.354) | W7 |
| W-02 cost_basis | 1.049 | 0.794 | 0.438 | 1.304 | 0.755 | -0.013 | 9; -0.761 | 2 (3.469 / 0.787 / -2.290) | 0.314 (0.367) | W2 |
| W-03 vol_shock | -0.276 | -0.612 | -0.833 | 0.060 | 0.057 | 0.003 | 0; 1.331 | 1 (-1.491 / 0.046 / 0.500) | 0.154 (0.190) | W2 |
| W-04 illiquidity_shock | -0.156 | -0.530 | -0.875 | 0.218 | -0.407 | -0.015 | 1; 0.915 | 1 (-1.548 / -0.276 / 1.240) | 0.160 (0.187) | W2 |
| W-05 us_session_shift | -0.537 | -0.961 | -1.224 | -0.113 | -1.372 | -0.013 | 1; 0.574 | 1 (-0.568 / -1.771 / 1.491) | 0.177 (0.207) | W2 |
| W-06 weekend_tilt | -2.343 | -2.754 | -2.981 | -1.932 | -0.511 | 0.022 | 8; -0.816 | 0 (-2.837 / -3.281 / -0.658) | 0.127 (0.148) | W2 |
| W-07 wick_absorption | -0.932 | -1.225 | -1.660 | -0.639 | -0.902 | 0.083 | 7; -1.154 | 1 (-0.527 / -2.153 / 1.457) | 0.113 (0.132) | W2 |
| W-08 decoupling | -0.179 | -0.525 | -0.823 | 0.167 | -0.502 | 0.027 | 0; 0.980 | 1 (-0.938 / 0.011 / 0.378) | 0.166 (0.194) | W2 |
| W-09 volume_trend | -0.375 | -0.595 | -1.003 | -0.155 | 0.105 | -0.010 | 10; -2.147 | 1 (2.138 / -0.932 / -2.357) | 0.157 (0.184) | W2 |
| W-10 basis_instability | -0.188 | -0.568 | -0.861 | 0.192 | 0.670 | 0.006 | 9; -2.010 | 0 (-0.221 / -0.253 / 0.011) | 0.196 (0.230) | W2 |
| W-11 ensemble | 0.372 | 0.025 | -0.275 | 0.719 | 0.029 | 0.023 | 2; 0.248 | 2 (1.424 / -0.152 / 0.174) | 0.210 (0.259) | W2 |

Years + counts returns above 0 (W-03's and W-08's 2021 and W-10's 2022H1 returns were slightly negative with Sharpe
near 0). Names held 27.6 to 27.7 of 28.0, 22.8 for W-03 and 22.9 for W-11; avg gross 0.81 to 0.86; direction changes
1155 to 2187; none liquidated. Every run printed the benchmark at DEV Sharpe 0.619, maxDD 0.847.

No counted submission. M is unchanged at 6. Tier 1: none. Pool 0 of 5.

## Screen outcome
W-01 passed W1 to W6 and W8 and failed W7 only (6 of 10 stale copies at least as good; book median -0.549 over the last
365 days of DEV). The other ten failed W2 first: eight with the wrong sign over DEV (W-03 to W-10), W-02 and W-11 with
the registered sign but under the pre-cost floor (1.304, 0.719). All eleven are falsified on DEV; no sign is flipped.

## Reading
- No single-idea book earned in both halves of DEV. The books that lean toward recent winners (W-01, W-02, and W-09
  through volume growth) earned in 2020 and lost in 2022H1 and over the last 365 days, the profile of round 2's
  continuation books; the unsigned or move-orthogonal books (W-03, W-04, W-05, W-07, W-08) lost in 2020 and earned in
  2022H1, four of them with a positive book median and negative stale copies over the last 365 days. The combination
  W-11 was positive in both halves only because its parts' profiles cancelled (2020 SR 1.424, 2022H1 0.174; DEV 0.372).
  WEAK. (The plan's DEV observations first said "no registered book"; a correction is appended there.)
- W-01 came closest of any top30 book on its own readings: pre-cost 1.820, positive under both stresses and on next30
  (0.601), speed limit 0.129. It failed on the last year of DEV, where ruling 3's concern (it moves with continuation)
  pointed.
- W-06 lost in every year (-2.343): coins whose share of volume tilted toward the weekend did better the next week, in
  the direction of round 1's H1 (LESSONS 39).
- The anchoring books traded and paid funding like continuation books (costs 0.30 to 0.31; gross funding 0.68 to 0.79
  each way, the largest read); the unsigned volume and volatility books were the cheapest weekly top30 books so far
  (0.11 to 0.20, C/G 0.13 to 0.23).

## What must NOT be concluded
- Eleven DEV failures say nothing about VAL. No VAL bar was read for any program of this round.
- The time split above is a DEV observation, not a hypothesis: a rule built to earn in both halves, or one that keeps
  only the late-DEV sign, would descend from these results, and DEV is spent as a screen for it. The same holds for
  the mirror of W-06.
- One default per idea was run; nothing is implied about other values of any param, and none is recommended. No corner
  or control was run, so whether W-01's readings survive its corners or exceed plain continuation is not known.
- A wide screen tests many ideas at once: had one passed, it would have been a candidate for one counted trial only,
  with the number of ideas screened recorded (ruling 10). None did.
- Choosing ideas is still open to hindsight (KP-010); the plan named what could bias each one.

## After the round
M = 6 (generation 0: 4, generation 1: 1, generation 2: 1, generation 3: 0 of 5), N = 5.90, rho 0.021, Tier 1: 0, pool
0 of 5, one uncounted stage-1 rejection (generation 0). Sandbox runs used in generation 3: 17 of 60 (rounds 1 to 3: 3,
3 and 11; ledger/sandbox_log.jsonl now 60 rows, the eleven new rows status ok, stage1 full, source_sha256 equal to the
committed files). `omr.kernel_lock`: OK, sealed (core 0.05, top30 0.1). `omr.ledger verify`: OK, all six chains.

## Requests to the coordinator
- LESSONS.md entries proposed for review (numbering after 46):
  - 47. In unit top30 on DEV, eleven pre-registered ideas from eight mechanism classes (reference price, volatility and
    illiquidity shocks, calendar clientele of volume, intrabar wicks, comovement with BTC, volume trend, basis churn, and
    an equal-weight combination) met one screen fixed in advance and none passed; eight had the wrong sign. Only the
    anchoring book (distance below the 6-week high in volatility units) cleared the pre-cost floor (1.820), both
    stresses and next30 (0.601), and it failed the paired reading (6 of 10; book median -0.549). Generation 3 PLAN run
    log, round 3, runs 1 to 11; no trial id. WEAK: DEV only, one default each.
  - 48. In round 3 no single-idea top30 book earned in both halves of DEV: books that lean toward recent winners (a
    price against its recent high or VWAP, volume growth) earned in 2020 and lost in 2022H1 and over the last 365 days,
    as round 2's continuation books did, while unsigned or move-orthogonal books lost in 2020 and earned in 2022H1; an
    equal-weight combination of both kinds was flat (DEV Sharpe 0.372). Round 3, runs 1 to 11. WEAK as evidence about
    markets; a rule built on the split would descend from it.
  - 49. A weekly book short the coins whose weekend share of volume rose lost in every DEV year (Sharpe -2.343): coins
    whose trading tilted toward the weekend did better the next week, in the direction of lesson 39. Round 3, run 6;
    no trial id. WEAK; DEV is spent as a screen for the mirror.
  - 50. Yardstick: weekly books that rank a price against a recent reference cost 0.30 to 0.31 of equity over DEV (C/G
    0.35 to 0.37) and paid and received 0.68 to 0.79 in gross funding each way, like continuation books, while weekly
    books on unsigned volume and volatility measures cost 0.11 to 0.20 (C/G 0.13 to 0.23). Round 3, runs 1 to 10. WEAK
    as a number; a design yardstick next to lessons 19, 41 and 45.
- Process, for the record: the wide screen spent 11 runs of a cap of 19 and no counted trial; every verdict came from
  one default run.
- No kernel defect was seen. The sandbox's readings were printed and logged as documented (logged values equal the
  printed ones); every run took under 4 minutes.
