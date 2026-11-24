# Generation 2 - REPORT (round 1: PLAN version 1; round 2: PLAN version 2, at the end)

Each round's part was written by that round's researcher session and saved to this file by the coordinator
(the sessions could not create it), with nothing changed but headings and line endings.

# Round 1 (PLAN version 1)

## Sources
- generations/gen002/PLAN.md (as committed fd19943, sha256 38d5d4a6...; with the stage-2 run log, screen
  outcomes and recommendation appended, sha256 abb4530b36d183dadfba4cff6ac951eb10d24e4e288e7faa3245d0fbd3d44c0f).
- The four sandbox outputs of the researcher session (DEV only), `python -m omr.status`, `python -m omr.ledger
  summary` (trial rows) and `python -m omr.ledger verify`.
- RESEARCH_PLAYBOOK.md, LANGUAGE.md, CONSTITUTION.md sections 3, 4, 6, 7 and 13, LESSONS.md, STATE.md,
  generations/gen000/REPORT.md, generations/gen001/PLAN.md and REPORT.md.
- No returns file, no trial detail file, no calibration file and no data file was read. No VAL number exists for
  any generation-2 program: none was submitted.

## What was run
- Unit top30 on the sealed KP-015 kernel (semantic 5ea66b0fb79ca267..., G6 0.10 for core and 0.10 for top30).
- A researcher session wrote PLAN.md version 1 with four hypotheses, four candidate programs and five DEV-only
  controls BEFORE its first sandbox run. Each program passed a grammar check. The coordinator committed and
  pushed the plan and programs unchanged as fd19943 before the first sandbox run.
- Coordinator's rulings, recorded in PLAN.md before run 1: the D-ACF speed-limit diagnostics are allowed as
  DEV-only measurements; the perp-index basis stays out with funding (KP-017); the source read of the four
  candidates found nothing to change; the requests about the sandbox and about timeframe aggregation go to the
  human as kernel proposals and are not to be worked around.
- The four hypotheses, all dollar neutral (gross 1), all ranked on WEEKLY bars, none reading funding, mark or
  index prices:
  - H1 gen002_resid_reversal: last week's return net of its BTC-beta part, in units of own volatility, reverses
    (long residual losers, short residual winners).
  - H2 gen002_activity_fade: a weekly trade-count burst against the coin's own 4-week mean predicts
    underperformance (attention).
  - H3 gen002_small_tickets: a falling weekly USD-per-trade against its own 4-week mean predicts
    underperformance (a retail crowd arriving).
  - H4 gen002_absorbed_flow: weekly taker buying that the week's return does not explain predicts
    underperformance (absorbed by patient, better-informed sellers).
- 4 sandbox runs of the 17 planned (plan cap 20, generation cap 60): the default of each hypothesis. The plan
  ran neighbours only after a default passed S1, S2 and S4, H1's control only after H1 passed S1 to S5, and a
  D-ACF diagnostic only for a hypothesis still standing. Every default failed S2 and S4, so runs 2, 3, 5, 6, 8, 9,
  11 and 12 (neighbours), 13 (control) and 14 to 17 (D-ACF) were not due. No stage-1 rejection, no kernel
  fault, no refusal; each run 67 to 86 s, full stage 1 (25 truncation cuts).
- DEV-only controls written with the plan and never run: strategies/gen002_diag_plain_reversal.omr and
  strategies/gen002_diag_acf_*.omr (four). They are never to be submitted.

## Result
| program | DEV Sharpe | PSR(0) | total return | costs | dir. changes | avg gross | positive years (of 2020, 2021, 2022H1) |
|---|---|---|---|---|---|---|---|
| H1 resid_reversal (n=30) | -1.566 | 0.006 | -0.644 | 0.1369 | 2849 | 0.866 | 0 of 3 (2020 SR -4.046) |
| H2 activity_fade (m=4) | 0.172 | 0.607 | 0.031 | 0.1669 | 1635 | 0.854 | 2 of 3 |
| H3 small_tickets (m=4) | -0.211 | 0.369 | -0.172 | 0.2309 | 1648 | 0.856 | 2 of 3 (2022H1 SR -3.453) |
| H4 absorbed_flow (m=4) | -1.251 | 0.023 | -0.466 | 0.1649 | 1850 | 0.854 | 0 of 3 |

Reference printed by every run: equal-weight long of the in-play members, DEV Sharpe 0.619, maxDD 0.847.
75 symbols were in the unit at some time in DEV.

| hypothesis | S1 | S2 (>= 0.6, registered sign) | S4 (total - costs > 0) | S5 | S3, S6, S7 | verdict |
|---|---|---|---|---|---|---|
| H1 | pass (2849; 0.866) | FAIL (-1.566) | FAIL (-0.781) | FAIL (0 of 3) | not due | dropped |
| H2 | pass (1635; 0.854) | FAIL (0.172) | FAIL (-0.136) | pass (2 of 3) | not due | dropped |
| H3 | pass (1648; 0.856) | FAIL (-0.211) | FAIL (-0.403) | pass (2 of 3) | not due | dropped |
| H4 | pass (1850; 0.854) | FAIL (-1.251) | FAIL (-0.631) | FAIL (0 of 3) | not due | dropped |

No counted submission in generation 2. M is unchanged at 5. Tier 1: none. Pool 0 of 5.

## Against each pre-registered DEV falsifier
- H1 ("not recommended if the DEV screen fails"; S2 needs a DEV Sharpe >= 0.6 with the registered sign): DEV
  Sharpe -1.566, negative in all three DEV years. Falsified on DEV.
- H2 (same screen; "a wrong DEV sign drops it, never flipped"): the sign was the registered one, but 0.172 is
  below the liveness bar of 0.6 and the DEV return did not cover a second payment of costs (S4). Falsified on
  DEV.
- H3 (same screen): DEV Sharpe -0.211, the wrong sign; the loss sits in 2022H1. Falsified on DEV.
- H4 (same screen): DEV Sharpe -1.251, the wrong sign; negative in all three DEV years. Falsified on DEV.

## Reading
- The two hypotheses that bet against the week's move (H1 against the residual return, H4 against unexplained
  aggressive flow) lost by more than one Sharpe unit on DEV. In the top30 cross-section of 2020 to mid-2022, a
  week's beta-residual move tended to continue rather than reverse. Aggressive flow that the price did not
  follow also tended to go with continuation, not with the patient side. WEAK: one DEV period, one default each,
  one researcher session.
- The two retail-crowding ideas (H2, H3) showed nothing usable: H2 had the registered sign but a small Sharpe
  that its costs would not survive twice, and H3 had the wrong sign with its loss in one half-year.
- Costs were as the plan estimated: 0.137 to 0.231 of equity over about 2.5 years (about 0.055 to 0.092 a
  year) for weekly rebalancing at 12.5 bps per side. All four books held positions over most of DEV (avg gross
  0.85 to 0.87).

## What must NOT be concluded
- DEV is now spent as an out-of-sample screen for the mirrors of H1 and H4 (weekly residual momentum,
  continuation of unexplained aggressive flow): the author has seen these DEV results. If a later plan
  registers a mirror, only its counted VAL run could test it, and the plan would have to say it was written
  after this DEV result.
- Four DEV failures say nothing about VAL. No VAL bar was read for any of these programs, and DEV and VAL are
  different periods with different market states.
- The sign of a DEV result is not a tradable finding. A mirror pays the same costs as the original, so its DEV
  Sharpe would be well below the size of these losses. A weekly residual-momentum rule would also sit close to
  the calibration's momentum family (LESSONS 13).
- One default per hypothesis was run. Nothing is implied about other parameter values; none is recommended.
- The author model knows this market's history; the plan named what could bias each idea. Choosing ideas is
  still open to hindsight (KP-010).

## After the round
M = 5 (generation 0: 4, generation 1: 1, generation 2: 0 of 5), N = 4.86, rho 0.035, Tier 1: 0, pool 0 of 5,
one uncounted stage-1 rejection (generation 0). Sandbox runs used in generation 2: 4 of 60 (ledger/sandbox_log.jsonl
now 22 rows). `omr.kernel_lock`: OK, sealed (core 0.10, top30 0.10). `omr.ledger verify`: OK, all six chains.

## Requests to the coordinator
- Kernel proposal: the sandbox to print G6's speed-limit statistic on DEV and a next30 DEV reading for unit
  top30 programs (D-ACF was the stopgap; it was never needed in this round). Filed as KP-018.
- Kernel proposal: aggregate or sample a dimensionless expression over a timeframe, so that signals built
  from hourly returns can be re-ranked weekly instead of every hour. Filed as KP-019.
- Two text notes: a window param cannot default to 1 (so a one-bar horizon is always the literal 1, never
  jittered); in unit top30 the 2020 bucket of G7 is short (members need 90 days of seasoning), so G7 is in
  effect 4 of 5 buckets for a top30 program. Filed with KP-017's text items.
- LESSONS.md entries 16 to 20, as proposed by the researcher and reviewed by the coordinator.

# Round 2 (PLAN version 2)

## What was run
- Same kernel (semantic 5ea66b0fb79ca267..., G6 0.10 in both units), unit top30. A fresh researcher session wrote
  PLAN version 2, appended to generations/gen002/PLAN.md with version 1 unchanged. It held three new hypotheses,
  three candidate programs and three DEV-only controls, written BEFORE any round-2 sandbox run. The coordinator
  committed and pushed them unchanged as b64b229.
- Coordinator's rulings, recorded in PLAN.md before run 1: H7's speed-limit reading by H6's diagnostic is
  accepted as a proxy; a book that pays or receives funding without reading it is not funding-driven; mark and
  index prices stay out of this generation in every form; the choice of neighbours for the two-param programs is
  accepted; the source read of H5 to H7 found nothing to change.
- The three hypotheses, all dollar neutral and residual to a market move, none reading funding, mark or index
  prices:
  - H5 gen002_resid_skew: short the coins whose daily returns, net of beta to the unit's mean, were most
    right-skewed over 21 days, long the most left-skewed (lottery demand).
  - H6 gen002_resid_momentum: the 4-week return net of the BTC-beta part, over own volatility, continues; ranked
    weekly. A continuation rule written after round 1's DEV result, so its DEV Sharpe was not evidence and its
    screen was stricter: each neighbour had to reach 0.6 and cover its costs twice, all three DEV years had to be
    positive, and it had to beat a plain-momentum control and pass the speed-limit diagnostic.
  - H7 gen002_prior_month_reversal: the same residual over the month before last (weeks 8 to 4 back) reverses.
- 7 sandbox runs of the 16 planned (cap 19). No stage-1 rejection, kernel fault or refusal; each run took 74 to
  104 s.

## Result
| program | DEV Sharpe | total | costs | dir. changes | avg gross | positive years (2020, 2021, 2022H1) |
|---|---|---|---|---|---|---|
| H5 resid_skew (n=21) | -1.906 | -0.730 | 0.1404 | 2645 | 0.823 | 0 of 3 |
| H7 prior_month_reversal (m=4, n=30) | 0.381 | 0.164 | 0.1772 | 1894 | 0.866 | 2 of 3 |
| H6 resid_momentum (m=4, n=30) | 0.945 | 0.643 | 0.3299 | 1871 | 0.865 | 2 of 3 (2022H1 SR -2.221) |
| H6 neighbours m=3 / m=5 / n=24 / n=36 | 0.955 / 0.923 / 1.039 / 1.069 | 0.697 / 0.627 / 0.728 / 0.775 | 0.380 / 0.313 / 0.368 / 0.332 | 1836 to 2082 | 0.865 to 0.866 | 2 of 3 each (2022H1 negative) |

Every run printed the benchmark (equal-weight long of the in-play members) at DEV Sharpe 0.619, maxDD 0.847.
No counted submission. M is unchanged at 5.

## Against each pre-registered DEV falsifier
- H5: the screen needed a DEV Sharpe of at least 0.6 with the registered sign. It got -1.906, negative in all
  three DEV years, and failed S4 as well. Falsified on DEV.
- H7: same screen. The sign was right, but 0.381 is below the liveness bar and the return did not cover a second
  payment of costs. Falsified on DEV.
- H6: stopped by its strict pre-registered S5. All five settings lost in 2022H1. Its default's DEV Sharpe was not
  evidence by rule. The control (S7) and the speed-limit diagnostic (S6) were not due, so neither was measured.

## Reading
- In the top30 cross-section of 2020 to mid-2022, recent residual up-jumps went with outperformance and recent
  crash days with underperformance: the lottery sign failed. This is the third bet against a recent move to lose
  on DEV, after round 1's H1 and H4. WEAK: one DEV period, one default.
- Reversal of the month-before-last residual had the registered sign but too little size to survive costs.
- The multi-week residual books cost far more than estimated: H6 about 0.125 to 0.15 a year, H7 about 0.07,
  against 0.03 to 0.06 estimated. The cause is not measured. The candidates are the daily-updated beta
  multiplying a large m-week BTC return, and the drift of a continuation book's holdings.

## What must NOT be concluded
- H6's DEV numbers are not evidence for residual momentum: it was written after round 1's DEV result. Its failure
  says only that it did not meet a strict screen fixed in advance.
- DEV is now spent as a screen for a mirror of H5 (continuation of jumps), as it already was for the mirrors of
  H1 and H4.
- No VAL bar was read. Three DEV results say nothing about VAL. One default per hypothesis was screened, plus H6's
  neighbours; no parameter value is implied or recommended.
- Choosing ideas is still open to hindsight (KP-010). The plan named what could bias each one.

## After the round
- Ledger: M = 5 (generation 2: 0 of 5 counted), N 4.86, rho 0.035, Tier 1: 0, pool 0 of 5.
- Sandbox runs used in generation 2: 11 of 60 (ledger/sandbox_log.jsonl now 29 rows).
- `omr.kernel_lock`: OK, sealed (core 0.10, top30 0.10). `omr.ledger verify`: OK, all six chains.
- LESSONS.md entries 21 to 25, as proposed by the researcher and reviewed by the coordinator.
