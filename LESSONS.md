# LESSONS

Only what the evidence supports. Each lesson: one sentence, the trials it rests on, how strong.
Strength scale: WEAK = one or two trials of one VAL period; INSTRUMENT = measured by the calibration
on synthetic worlds. No lesson recommends a parameter value.

## From generation 0 (sealed kernel 7446278556aadd8f, G6 0.10; generations/gen000/REPORT.md)

1. A DEV Sharpe above 1 did not carry into VAL for the breakout rule. Trial 0f725c07dd8ae8fb (DEV
   1.168, VAL -0.531, p 0.866). WEAK: one trial.
2. The only baseline with a positive VAL Sharpe was the volatility-sized trend rule, and it still
   trailed simply holding BTC and ETH half each in VAL (0.384 against 0.921) and failed G1 and G6.
   Trial 992b1aacbef67bb1. WEAK: one trial, one period.
3. Both non-trend baselines (4h RSI mean reversion and funding carry) lost in DEV as well as in VAL,
   so they failed before any question of VAL timing arose. Trials c6ea0c6759f7482e,
   c30a93ef73a529bd. WEAK: two trials at fixed defaults.
4. Both trend rules had a positive DEV Sharpe and passed the extended-universe check (G8) yet failed
   the VAL timing permutation (G6). Trials 0f725c07dd8ae8fb, 992b1aacbef67bb1. WEAK.
5. The activity floor removed the slow SMA cross in stage 1 before any VAL bar was read (16 direction
   changes in DEV, floor 20), at no cost to M. Stage-1 log row fcdaf8a31244afb1. Certain (a rule
   applied as designed).

## From generation 1 (same kernel; generations/gen001/REPORT.md)

8. Dropping the short side of a volatility-sized trend rule raised the VAL Sharpe from 0.384 to
   0.830, but the long-or-flat rule still trailed holding (0.921) and failed only the timing
   permutation (p 0.279). Trials 992b1aacbef67bb1, 24778ca0881b6c26. WEAK: two trials, one period.
9. A long-biased rule can pass every gate except G6 on the market's drift alone: eight of nine gates
   passed with no measurable timing. Trial 24778ca0881b6c26. WEAK as evidence about markets; it shows
   what G6 is for, and that more "long when X" variants mostly re-test the same question.
10. Of five pre-registered ideas only one survived the DEV screen: the rare-event rule could not reach
    the activity floor anywhere on its pre-registered grid, the market-neutral pair flipped sign at a
    neighbouring lookback, and two long-only switches added little over an always-long control.
    generations/gen001/PLAN.md run log. WEAK: DEV only, one researcher session.
11. An always-long, volatility-sized control is a cheap DEV check for any long-only switch: the
    switch has to beat the control, not zero. Process lesson from the same run log.

## From generation 2, round 1 (KP-015 kernel 5ea66b0fb79ca267, unit top30; generations/gen002/REPORT.md)

16. In unit top30 on DEV, a weekly cross-sectional reversal of beta-residual, volatility-scaled returns
    lost (DEV Sharpe -1.566, negative in 2020, 2021 and 2022H1): a week's residual move tended to
    continue, not reverse. generations/gen002/PLAN.md run log, run 1; no trial id. WEAK: DEV only, one
    default, one researcher session.
17. Ranking against weekly taker-buy flow that the week's return does not explain also lost on DEV (DEV
    Sharpe -1.251, negative in all three DEV years). PLAN.md run log, run 10; no trial id. WEAK: DEV
    only, one default, one researcher session. For 16 and 17 alike: DEV is spent as a screen for the
    mirror rule; a later plan that registers a mirror must say it was written after this result, and
    only its counted VAL run can test it.
18. Two retail-crowding proxies built from trade counts (a weekly activity burst; a falling USD ticket
    size) showed no usable DEV edge after weekly costs (DEV Sharpe 0.172 and -0.211). PLAN.md run log,
    runs 4 and 7; no trial id. WEAK: DEV only, one default each, one researcher session.
19. A dollar-neutral rank book over unit top30 rebalanced weekly paid about 0.055 to 0.092 of equity a
    year in costs at 12.5 bps per side, close to the estimate of 4/3 of gross traded per week. PLAN.md
    run log, runs 1, 4, 7 and 10. WEAK as a number (four programs, one DEV period); useful as a design
    yardstick.
20. Process: a DEV screen fixed in advance, which drops a hypothesis when its default fails and runs
    neighbours, controls and diagnostics only for hypotheses still standing, spent 4 sandbox runs of 17
    planned and no counted trial, with no room for tuning. PLAN.md exploration plan and run log. Certain
    as an account of this round; not evidence about markets.

## From generation 2, round 2 (same kernel and unit; generations/gen002/REPORT.md, round 2)

21. In unit top30 on DEV, a daily cross-sectional rank against the realised skewness of residual daily
    returns (short right-skewed, long left-skewed) lost (DEV Sharpe -1.906, negative in all three DEV
    years): recent residual up-jumps went with outperformance. PLAN.md version 2 run log, run 1; no
    trial id. WEAK: DEV only, one default, one researcher session. A mirror would be a continuation
    rule, with DEV already spent for it (as in 16 and 17).
22. Reversal of the beta-residual return of the month before last (weeks 8 to 4 back) had the
    registered sign on DEV but too little size (DEV Sharpe 0.381) to cover its costs twice. PLAN.md
    version 2, run 4; no trial id. WEAK: DEV only, one default.
23. A residual 4-week momentum rule written after round 1's DEV result showed DEV Sharpe 0.92 to 1.07
    at its default and all four G5 neighbours, but lost in 2022H1 in all five settings, and so failed
    the stricter per-year item registered for a mirror. Its DEV numbers are not evidence for the rule,
    and a screen it failed is not reopened by registering it again. PLAN.md version 2, runs 9 to 13; no
    trial id. WEAK.
24. Residualising a multi-week return with a daily-updated beta made weekly-formation books cost about
    0.07 to 0.15 of equity a year at 12.5 bps per side, two to five times the estimate from consecutive
    weekly rankings: the turnover of an hourly-grid signal is set by its fastest-moving part. PLAN.md
    version 2, runs 4 and 9 to 13. WEAK as a number; useful as a design yardstick.
25. Process: a mirror screened only on readings nobody had seen, with stricter items fixed in advance,
    was stopped by one of those items rather than judged on its known DEV Sharpe; round 2 spent 7
    sandbox runs of 16 planned and no counted trial. PLAN.md version 2. Certain as an account of this
    round; not evidence about markets.
26. Across both rounds, seven pre-registered market-neutral top30 ideas built from prices, trade
    counts and taker flow failed their DEV screens; every bet against a recent move lost and the only
    DEV-positive book was continuation, which is the calibration's own momentum shape at a slower
    speed. The inputs not yet open in this unit are funding and the perp-index basis (KP-017).
    Coordinator's summary of the two run logs; WEAK as evidence about markets.

## From generation 2, round 3 (same kernel and unit; generations/gen002/REPORT.md, round 3)

27. In unit top30 on DEV, three contrarian books on funding and on the perp premium over the index had
    the registered sign (DEV Sharpe 0.823, 1.197 and 0.980): short the coins whose premium, or whose
    funding, rose above their own six-week norm, and short the premium that a coin's 14-day return
    does not explain. They received 0.14 to 0.30 of equity in funding and stayed positive with all of
    it removed. But each cost 0.45 to 0.51 of equity over DEV and failed the cost ceiling fixed in
    advance, so their timing, price-neutrality and speed-limit readings were never taken. PLAN.md
    version 3 run log, runs 1 to 3; no trial id. WEAK: DEV only, one default each, one researcher
    session; not evidence of a timing edge (on DEV recent losers carried higher funding, so DEV's
    continuation of recent moves is a named confound). DEV is now partly spent for these inputs: a
    later plan that registers a slower or cheaper version must say it was written after this result,
    and only its counted VAL run, after the KP-017 measurement, can test it.
28. Rank books whose targets change once a day (medians of daily premium snapshots) or at each funding
    settlement (14-day funding means) paid about 0.18 to 0.20 of equity a year at 12.5 bps per side,
    two to five times the plan's estimates and more than any weekly book: a slowly moving input did
    not make a slowly moving rank. Suggestive only; the cause (for example rank swaps among closely
    bunched values, with the engine trading every name once any one is 0.01 off) was not measured.
    PLAN.md version 3, runs 1 to 3. WEAK as a number; a design yardstick next to 19 and 24.
29. Process: a cost ceiling registered before any run stopped three DEV-positive books at their
    defaults, in 3 sandbox runs of 14 planned and with no counted trial, before any reading that could
    have flattered them was taken. PLAN.md version 3. Certain as an account of this round; not
    evidence about markets.

## About the instrument (calibration ledger/calibration_7446278556aadd8f.json)

6. A program with no edge, selected as the best of 20 DEV draws, passes Tier 1 in about 2.3% (null B)
   to 2.9% (null A) of cases at G6 0.10. INSTRUMENT: 1,498 and 1,500 submitted pairs.
7. A program with a true VAL Sharpe of 1.0 passes Tier 1 only 55% to 63% of the time (1.5: 84% to
   91%), so most failures say little about a modest real edge. INSTRUMENT: 200 oracle worlds per
   configuration.

Lessons 6 and 7 are about unit core. The KP-015 kernel (semantic 5ea66b0fb79ca267, sealed 2026-11-23
at G6 0.10 for core and 0.10 for top30) reproduces those rows exactly
(ledger/calibration_5ea66b0fb79ca267.json).

## About the instrument, unit top30 (ledger/ucalibration_5ea66b0fb79ca267.json; audits/AUDIT_LOG.md, round 7)

12. A market-neutral top30 book with a true VAL Sharpe of 1.5 passes Tier 1 in 68% to 82% of cases
    at G6 0.10 (holding periods of 5 and 20 days). No Sharpe 1.0 level was measured in this unit, so
    a failure says even less about a modest edge than in unit core. INSTRUMENT: 100 oracle books per
    configuration.
13. The no-skill calibration families of unit top30 (cross-sectional momentum and its mirror on
    daily bars, and funding carry) lose money after costs in the no-skill worlds (mean VAL Sharpe
    -0.5 to -1.9): 4 of 1,089 evaluated pairs pass G1 and 1 passes Tier 1. In this unit costs, not
    the timing gate, are what stops a no-skill book built on daily signals. INSTRUMENT.
14. G6 tests timing against the book's own stale copies; it does not test luck. A top30 book that
    earns a premium without timing passes it about 1 time in 10 at 0.10 (7 of 78 in the pilot), and
    in unit core 44 of the 112 (null A) and 35 of the 126 (null B) no-skill pairs that passed every
    other gate passed G6 as well. Against luck the protection is the other gates and the trial
    count M. INSTRUMENT.
15. In unit top30 the timing gate passed a losing funding-carry book far above its nominal level in
    the no-skill worlds that keep the real funding sizes (53 of 166 at 0.10, about 16 expected).
    Not yet measured for a book that passes the other gates; until it is, no funding-driven program
    is submitted in unit top30 (KERNEL_PROPOSALS KP-017). INSTRUMENT, open.
