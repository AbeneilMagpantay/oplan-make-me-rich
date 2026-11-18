# Generation 0 - REPORT

Sources: ledger/trials.jsonl, ledger/stage1_log.jsonl, `python -m omr.status`, the coordinator's run
log. No returns file and no trial detail file was read.

## What was run
- Run by the coordinator 2026-11-19 (07:08-07:09 +08:00), commit d2c2d4f, after the fifth audit said
  READY and recounted the seal.
- Kernel: semantic 7446278556aadd8f4f10e30b75ddebbc2ab272a255f2b8fc0472ed57a18ecad1, text
  d51a84cd8c13dc1b545b5f29a06c97a2d381c3bf972853c20381d28cd1b97ef1, combined fa6b7a1e2639fbb5...
- Seal: G6 0.10 from ledger/calibration_7446278556aadd8f.json (sha256 67a71662ee0f...).
- Data research_hash cf26f534cf1c9f4a..., validated. PLAN.md sha256 in every pending row 740b2ed3a2dcb8b8...
- The five pre-registered baselines (strategies/gen000_*.omr) at their declared defaults, once each.

## Results
| program | trial | status | DEV SR | VAL SR | PSR(0) | DSR (M then) |
|---|---|---|---|---|---|---|
| sma_cross_ls | fcdaf8a31244afb1 | stage 1 rejected activity_dev (16 < 20), NOT counted | - | - | - | - |
| donchian_ls | 0f725c07dd8ae8fb | evaluated, tier none | 1.168 | -0.531 | 0.178 | 0.178 (1) |
| rsi_meanrev_ls | c6ea0c6759f7482e | evaluated, tier none | -1.238 | -0.770 | 0.088 | 0.030 (2) |
| voltarget_trend_ls | 992b1aacbef67bb1 | evaluated, tier none | 1.453 | 0.384 | 0.747 | 0.408 (3) |
| funding_carry | c30a93ef73a529bd | evaluated, tier none | -0.388 | -0.323 | 0.289 | 0.055 (4) |

| gate | donchian | rsi_meanrev | voltarget | carry |
|---|---|---|---|---|
| G1 VAL PSR(0) >= 0.90 | F 0.178 | F 0.088 | F 0.747 | F 0.289 |
| G2 funding stress > 0 | F -0.616 | F -0.826 | P 0.288 | F -0.376 |
| G3 DEV SR > 0 | P 1.168 | F -1.238 | P 1.453 | F -0.388 |
| G4 2x costs > 0 | F -0.587 | F -0.931 | P 0.297 | F -0.350 |
| G5 jitter median; share > 0 | F -0.378; 0.00 | F -0.625; 0.00 | P 0.327; 1.00 | F -0.334; 0.08 |
| G6 p <= 0.10 | F 0.866 | F 0.806 | F 0.239 | F 0.667 |
| G7 positive of 6; largest share | F 2; 0.667 | F 1; 1.000 | P 5; 0.465 | F 2; 0.797 |
| G8 median; share > 0 of 8 | P 0.408; 0.75 | F -0.563; 0.13 | P 0.650; 0.63 | F -0.034; 0.50 |
| G10 VAL direction changes >= 12 | P 113 | P 407 | P 121 | P 18 |

| program | dir. changes DEV/VAL | deploy_scale | VAL maxDD | DEV+VAL maxDD | n_literals | g5_vacuous |
|---|---|---|---|---|---|---|
| donchian | 65/113 | 0.277 | 0.701 | 0.721 | 0 | no |
| rsi_meanrev | 311/407 | 0.207 | 0.717 | 0.967 | 0 | no |
| voltarget | 92/121 | 0.487 | 0.394 | 0.411 | 1 | no |
| carry | 60/18 | 0.304 | 0.304 | 0.658 | 2 | no |

Benchmark (information, not a gate): long BTC and ETH half each, VAL Sharpe 0.921, VAL max drawdown 0.488.
Tier 1: none. Pool 0 of 5. No liquidation, no kernel fault.

## Against each pre-registered falsifier
- sma_cross: not evaluated; its 16 DEV direction changes were known before any VAL bar was read.
- donchian ("G1, G6, or G7"): all three failed. Falsified.
- rsi_meanrev ("G1, G4, or G6"): all three failed; it also lost in DEV (G3). Falsified.
- voltarget ("G1 or G6; or G5 if it hinges on the vol target"): G1 and G6 failed; G5 passed (12/12
  variants positive). Falsified by G1 and G6.
- carry ("G1, G2, or the activity rules"): G1 and G2 failed; G10 passed (18). Falsified by G1, G2.

## What must NOT be concluded
- Four counted trials, each one 3-year VAL period.
- Hindsight-prone data: the author model has read this market history; no forward result exists.
- A strict instrument: about 2.3-2.9% of no-edge programs pass at G6 0.10, and a true VAL Sharpe 1.0
  edge passes only about 55-63% (1.5: 84-91%). Failure does not show "no edge"; a single pass would
  not have shown an edge.
- Fixed, untuned defaults: nothing is implied about other parameter values; none is recommended.
- The benchmark is information, not a gate.

## After the generation
M = 4 (generation 0: 4 of 5), N = 4.00, Tier 1: 0, pool 0 of 5, one uncounted stage-1 rejection;
all chains verified.
