# Generation 2 - REPORT (rounds 1, 2 and 3: PLAN versions 1, 2 and 3, one part each)

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

# Round 3 (PLAN version 3)

## What was run
- Same kernel (semantic 5ea66b0fb79ca267..., G6 0.10 in both units), unit top30. A fresh researcher session wrote
  PLAN version 3, appended to generations/gen002/PLAN.md with versions 1 and 2 unchanged. It held three
  hypotheses on the inputs opened in this round (funding and the perp-index basis), three candidate programs and
  eight DEV-only diagnostics (three stale copies, two price-neutral twins, three D-ACF), all written BEFORE any
  round-3 sandbox run. The coordinator committed and pushed them unchanged as afb835b.
- Coordinator's rulings, recorded in PLAN.md before run 1: the stale copies (S7) and the price-neutral twins (S10)
  are allowed as DEV-only measurements; the source read of H8 to H10 found nothing to change, and H9's `size` is
  accepted as a declared per-name size; the researcher's reading of funding code is accepted; a recommendation
  reads "eligible, subject to the KP-017 measurement"; the notes on a funding window in hours, gross funding in
  the sandbox and the names held are filed with KP-018 and KP-019.
- The three hypotheses. All are dollar neutral and all bet against crowded leverage. All read funding_mean or
  index_close, so a counted run would also need the KP-017 measurement.
  - H8 gen002_premium_shock: short the coins whose perp premium over the spot index rose above their own norm,
    long those whose premium fell below it. The premium is a daily-close snapshot; the signal is the 14-day median
    minus the 42-day median.
  - H9 gen002_funding_shock: the same idea on settled funding: the 14-day mean minus the 42-day mean. Rank weights
    are capped at 0.1 per name because clamped funding ties at the default rate.
  - H10 gen002_unrewarded_premium: short the premium that a cross-sectional fit on the coin's 14-day return does
    not explain. It is orthogonal to that return by construction.
- The screen kept S1 to S6 (S1 and S3 tightened) and added four items: S7, a stale copy at 30 days; S8, a
  funding-stress proxy (the DEV return must stay positive with all net funding removed); S9, a cost ceiling (DEV
  costs at most 0.25); S10, a price-neutral twin, for H8 and H9 only.
- 3 sandbox runs of the 14 planned (cap 17). No stage-1 rejection, kernel fault or refusal. Each run took 70 to
  101 s; the kernel's memory estimate fitted before each.

## Result
| program | DEV Sharpe | total | costs | funding paid | dir. changes | avg gross | positive years (2020, 2021, 2022H1) |
|---|---|---|---|---|---|---|---|
| H8 premium_shock (a=14, b=42) | 0.823 | 0.475 | 0.5081 | -0.1434 (received) | 4723 | 0.867 | 3 of 3 |
| H9 funding_shock (a=42, b=126, size=0.1) | 1.197 | 0.734 | 0.4447 | -0.2821 (received) | 3803 | 0.853 | 2 of 3 (2022H1 -0.123) |
| H10 unrewarded_premium (n=14) | 0.980 | 0.564 | 0.4497 | -0.2975 (received) | 4068 | 0.867 | 3 of 3 |

Every run printed the benchmark at DEV Sharpe 0.619, maxDD 0.847. No counted submission. M is unchanged at 5.

## Against each pre-registered DEV falsifier
- H8: the sign was the registered one (0.823). It failed S4 (0.475 - 0.508 = -0.033) and S9 (costs 0.508 > 0.25).
  Falsified on DEV.
- H9: it met S1, S2, S4 (0.289), S5 and S8 (0.452). It failed S9 (0.445). Falsified on DEV.
- H10: it met S1, S2, S4 (0.114), S5 and S8 (0.267). It failed S9 (0.450). Falsified on DEV.
- By the run order a default that fails S9 ends the hypothesis, so the G5 corners (S3), the stale copies (S7), the
  twins (S10) and the speed-limit diagnostics (S6) were not run for any of them.

## Reading
- For the first time in generation 2 every hypothesis of a round had the registered sign on DEV. All three
  contrarian books earned a positive DEV Sharpe (0.82 to 1.20) and received funding: 0.14 to 0.30 of equity, 30 to
  53% of their total return. Each stayed positive with that funding removed.
- Their costs stopped them: 0.45 to 0.51 of equity over DEV, about 0.18 to 0.20 a year. That is two to five times
  the plan's estimates and above every book of rounds 1 and 2. H8 and H10 change targets once a day but rebalanced
  about 1,090 times in 912 days; H9's 8-hourly funding means rebalanced 1,975 times. The cause is not measured.
  One candidate is that rank weights swap whenever closely bunched values cross, so a slowly moving input still
  re-ranks often; another is that H10's residual moves with a 14-day return that changes daily.

## What must NOT be concluded
- These DEV numbers are not evidence of a timing edge or of leverage information. S7 and S10 were never taken, and
  the plan had named the confound: on DEV recent losers carried higher funding (H6 received funding; H1 and H7
  paid it), so books short high funding can ride DEV's continuation of recent moves.
- DEV is now partly spent for contrarian funding and premium rules. A slower or cheaper version registered later
  would be written after this result. Its DEV numbers would not be evidence; only its counted VAL run, after the
  KP-017 measurement, could test it.
- Lowering the cost ceiling after the fact would be tuning the screen to a known result. It was fixed in advance
  for KP-017's reason: the G6 finding concerns books dominated by their costs.
- No VAL bar was read. One default per hypothesis was run, and no parameter value is implied. Choosing ideas is
  still open to hindsight (KP-010).

## After the round
- Ledger: M = 5 (generation 2: 0 of 5 counted), N 4.86, rho 0.035, Tier 1: 0, pool 0 of 5.
- Sandbox runs used in generation 2: 14 of 60 (rounds 1 to 3: 4, 7 and 3); ledger/sandbox_log.jsonl now has 32
  rows.
- `omr.kernel_lock`: OK, sealed (core 0.10, top30 0.10). `omr.ledger verify`: OK, all six chains.
- LESSONS.md entries 27 to 29, as proposed by the researcher and reviewed by the coordinator.
