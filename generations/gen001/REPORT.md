# Generation 1 - REPORT

Sources: ledger/trials.jsonl, `python -m omr.status`, the coordinator's evaluate output,
generations/gen001/PLAN.md. No returns file and no trial detail file was read.

## What was run
- An independent researcher session wrote PLAN.md version 1 with five hypotheses before its first
  sandbox run, then used 18 DEV sandbox runs (cap 60). Plan, programs and sandbox log were committed
  and pushed as ace76ee BEFORE anything was scored.
- The coordinator read the source of gen001_tsmom_long_flat (every number is a declared param or the
  literals 1 and 0; no field ratio, calendar average or algebra across a comparison) and scored it
  once, 2026-11-19, on the sealed kernel (semantic 7446278556aadd8f..., G6 0.10).
- Not submitted, on DEV evidence only (PLAN.md amendment A2):
  - gen001_relmom_pair: turns negative at a neighbouring lookback; heavy rebalancing costs.
  - gen001_capitulation_long: 12 to 16 DEV direction changes on its whole pre-registered grid, below
    the floor of 20; its trigger was not loosened to get it through.
  - gen001_calm_long: its switch adds little over an always-long control except at the default.
  - gen001_taker_flow_long: never beats holding in DEV and has the highest costs.
- strategies/gen001_diag_volsized_long.omr is a DEV-only control (always long, volatility-sized,
  zero direction changes). It is never to be submitted.

## Result
| program | trial | status | DEV SR | VAL SR | PSR(0) | DSR (M then) |
|---|---|---|---|---|---|---|
| tsmom_long_flat | 24778ca0881b6c26 | evaluated, tier none | 1.740 | 0.830 | 0.926 | 0.532 (5) |

| gate | value | result |
|---|---|---|
| G1 VAL PSR(0) >= 0.90 | 0.926 | pass |
| G2 funding stress > 0 | 0.746 | pass |
| G3 DEV SR > 0 | 1.740 | pass |
| G4 2x costs > 0 | 0.760 | pass |
| G5 jitter median; share > 0 | 0.842; 1.00 | pass |
| G6 p <= 0.10 | 0.279 | FAIL |
| G7 positive of 6; largest share | 5; 0.471 | pass |
| G8 median; share > 0 of 8 | 0.912; 0.875 | pass |
| G10 VAL direction changes >= 12 | 193 | pass |

Direction changes DEV 116, VAL 193. deploy_scale 0.524. VAL max drawdown 0.382.
Benchmark (information, not a gate): long BTC and ETH half each, VAL Sharpe 0.921, max drawdown 0.488.
Tier 1: none. Pool 0 of 5. No liquidation, no kernel fault.

## Against the pre-registered falsifier
"Falsified if VAL PSR(0) < 0.90, the timing permutation shows no timing skill, or funding stress
turns it negative." PSR(0) is 0.926 and the funding stress is positive; the timing permutation gives
p = 0.279. Falsified by the timing test.

## Reading
- It passed eight of nine gates and failed only the timing permutation: with the same positions
  shifted in time, about 28% of shifts did at least as well. Its VAL Sharpe (0.830) is below simply
  holding (0.921). That is what a long-biased exposure to a rising market looks like when its on/off
  timing adds nothing measurable, and G6 is the gate built for that case.
- Against generation 0's long/short version of a similar rule (992b1aacbef67bb1, VAL 0.384),
  dropping the short side raised the VAL Sharpe to 0.830. Two trials, one period.

## What must NOT be concluded
- One counted trial in this generation and five in total, on one VAL period of hindsight-prone data.
- A G6 failure at p 0.279 does not show the rule has no timing value: the instrument passes a true
  Sharpe-1.0 timing edge only about 55 to 63% of the time.
- The drift this rule rode was known to the researcher from the generation-0 report (the benchmark's
  VAL Sharpe) and from the author model's memory of the period.

## After the generation
M = 5 (generation 1: 1 of 5), N = 4.86, rho 0.035, Tier 1: 0, pool 0 of 5; all chains verified.
