# Generation 2 - REPORT (round 1: PLAN version 1)

Written by the researcher session of round 1; saved to this file by the coordinator (the session could not
create it), with nothing changed but the file's line endings.

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
