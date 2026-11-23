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
