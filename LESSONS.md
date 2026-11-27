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

## From generation 2, round 4 (same kernel and unit; generations/gen002/REPORT.md, round 4)

30. In unit top30 on DEV, averaging the cross-sectional rank of round 3's funding-shock signal over 16
    days roughly halved its costs (0.218 against 0.445 of equity over DEV; 0.285 against 0.521 per unit
    of gross; windows of 10 and 28 days of funding8h), inside the estimate fixed beforehand from the
    engine's rule. The book then passed every item of a screen fixed in advance: a cost ceiling with a
    per-gross clause, the costs paid twice with the funding removed, both G5 corners, a price-neutral
    twin (1.466 against 1.492) and the speed-limit diagnostic (R -0.356). PLAN.md version 4, runs 1, 3,
    4 and 7 to 9; no trial id. WEAK: DEV only, one researcher session. The rule was written after round
    3's DEV result, so its DEV Sharpe (1.492) is not evidence, and its stale-copy pass is weak for a
    book anti-correlated with itself one lag step back. Eligible only subject to the KP-017 measurement.
31. Measuring the perp premium against the coin's own 28-day norm, net of a cross-sectional fit on the
    10-day return, with the residual's rank averaged over 16 days, cost about as little (0.216 of equity
    over DEV) but left too little edge: DEV Sharpe 0.731 at the default and 0.249 at the 0.8 corner,
    which did not cover its costs twice. PLAN.md version 4, runs 2 and 5; no trial id. WEAK: DEV only,
    one default and one corner.
32. Averaging the rank cut costs per unit of gross by about half but not further in the settings read: a
    longer average (H11's 1.2 corner) cost more per unit of gross (0.310 against 0.285), and a stale
    copy of the same weight path, which holds only names known on every hour of the last 30 days, cost
    0.172. Part of an averaged rank book's costs probably comes from names entering, leaving or dropping
    out of play, which no averaging removes. Suggestive only, not measured. PLAN.md version 4, runs 1, 4
    and 7. WEAK as a number; a design yardstick next to 19, 24 and 28.
33. Process: a round whose candidates were engineered against a known cost failure, and screened only on
    readings nobody had taken, spent 8 sandbox runs of 12 planned and no counted trial, and produced the
    first candidate of generation 2 that is eligible by its DEV screen. Certain as an account of this
    round; not evidence about markets.

## From generation 2, the counted trial (generations/gen002/REPORT.md, last part)

34. A contrarian funding-shock rule in unit top30 (the rank of a 10-day against a 28-day funding mean,
    averaged over 16 days) that had passed a DEV screen of ten items fixed in advance (DEV Sharpe 1.499)
    had a VAL Sharpe of -0.249 and failed G1, G2, G4, G5, G6 and G7; before costs it earned about
    nothing in VAL. Trial 7eadbeeaf2adc98d. WEAK about markets: one trial, one period, and a rule
    shaped on DEV after two rounds of DEV results. It is the first counted trial in unit top30.
35. A DEV screen, however many items it has (costs, corners, a stale copy, a price-neutral twin, the
    speed limit), reads DEV only: it measured how well the rule of lesson 34 fitted DEV and nothing
    about VAL. Each round that reshapes a rule after a DEV result makes its DEV numbers worth less;
    after rounds 3 and 4 they were worth nothing as evidence, as the plans said, and the counted trial
    confirmed it. Trial 7eadbeeaf2adc98d and the four PLAN versions. Certain as an account of
    generation 2; a caution, not a rule about markets.

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

## About the kernel's own tests (batch re-key of 2026-11-25; audits/AUDIT_LOG.md, round 8, the build)

36. The kernel's core-identity test handed every file in strategies/ to a frozen reference kernel, so it
    failed from the day generation 2's first programs (a unit the reference cannot read) were committed, and
    nobody saw it for the life of that kernel: the full suite ran at the kernel's build and not again before
    the next kernel change. A kernel test that reads the genome folder by a pattern must hold for every program
    the language accepts, and the full suite runs when a generation closes as well as at every build. PROCESS.

## About the instrument after the batch re-key (ledger/calibration_7d923e7e2375986d.json, ledger/ucalibration_7d923e7e2375986d.json)

37. Counted over the pairs a researcher would submit (a positive DEV Sharpe), the no-skill worlds of unit
    core passed Tier 1 in 3.8% (null A, 44 of 1,144) and 3.1% (null B, 35 of 1,130) of cases at a G6
    threshold of 0.10, above the 3% bound; at 0.05 in 2.3% and 1.6%. Unit core is sealed at 0.05 since
    2026-11-26. At 0.05 a program with a true VAL Sharpe of 1.5 passes 81% to 91% of the time, one with 1.0
    only 50% to 63%. INSTRUMENT.
38. In unit top30 the same count gives 0 of 165 and 1 of 225 at 0.10, but on families that lose to their
    costs (lesson 13). For a book that is cheap to trade the 3% bound is not measured (KERNEL_PROPOSALS
    KP-020): in the null worlds of the KP-017 measurement two cheap books, with costs switched off, passed
    every gate but G6 in 4 of 128 cases and G6 as well in 1; with costs on, in none. A top30 Tier-1 result is
    therefore measured per program in null worlds before it enters the pool. INSTRUMENT, open.

## From generation 3, round 1 (kernel 7d923e7e2375986d, unit top30; generations/gen003/REPORT.md)

39. In unit top30 on DEV, a weekly book contrarian on the weekend part of a coin's residual move, held
    orthogonal to the whole move of the week, lost (DEV Sharpe -1.348, negative in 2020, 2021 and 2022H1): the
    weekend part tended to persist relative to the weekday part. Generation 3 PLAN run log, run 1; no trial id.
    WEAK: DEV only, one default. DEV is spent as a screen for the mirror.
40. The heavy-hour part (contrarian, coin-specific volume) and the storm-hour part (contrarian, BTC's share of
    variance) of the same construction showed no usable DEV edge after costs and stresses (DEV Sharpe -0.256
    and 0.349; under doubled costs -0.705 and -0.071). Runs 2 and 3; no trial id. WEAK.
41. Weekly targets built from hourly inputs through tf_mean(., weekly) traded like weekly rank books (0.172 to
    0.229 of equity over DEV at 12.5 bps per side, 0.21 to 0.27 per unit of gross), although their beta is
    re-estimated every hour: the weekly bar bounds the turnover, unlike the daily-updated beta of lesson 24.
    Runs 1 to 3. WEAK as a number; a design yardstick next to lesson 19.
42. For a dollar-neutral top30 book that holds a full book through DEV, the funding stress of G2 cost more
    Sharpe than the doubled costs of G4 (0.66 to 0.77 against 0.41 to 0.45 in these three books; 0.61 against
    0.46 and 0.76 against 0.33 in two books of generation 2, sandbox rows 40 and 41), whether or not the book
    reads funding: such a book pays and receives 0.3 to 0.5 of equity in gross funding over DEV, and G2 charges
    half of each. A top30 idea needs a DEV Sharpe of about 0.7 before either stress to survive both. WEAK as a
    number; a design yardstick. INSTRUMENT.
43. Process: a screen fixed in advance on the kernel's own DEV readings stopped three defaults in 3 sandbox runs
    of 12 planned, before any placebo or corner run, with no counted trial. Across generations 2 and 3, fifteen
    pre-registered market-neutral top30 ideas have now been screened on DEV: every bet against a recent move
    lost or earned too little, and the only DEV-positive price books continue a recent move. PROCESS.

## From generation 3, round 2 (same kernel and unit; generations/gen003/REPORT.md, round 2)

44. In unit top30 on DEV, three weekly continuation books written after DEV results (3-week residual momentum;
    jump continuation, the mirror of the skewness rule of lesson 21; one-week residual continuation) had the
    registered sign but a DEV Sharpe of only 0.541, 0.705 and 0.836 after costs. Each was strongly positive in
    2020 (Sharpe 2.0 to 2.9) and negative in 2022H1 (-0.7 to -2.7), lost on the common names over the last 365
    days of DEV (paired reading, book median -0.76 to -1.79), and read negative on next30 (-0.10, -0.82, -0.31).
    The DEV continuation of lessons 16, 21, 23 and 43 was concentrated early in DEV and did not show in ranks 31
    to 60 after costs. Generation 3 PLAN run log, round 2, runs 1 to 3; no trial id. WEAK: DEV only, one default
    each, rules written after DEV results.
45. Weekly continuation books cost 0.239 to 0.375 of equity over DEV at 12.5 bps per side (0.29 to 0.45 per unit
    of gross), above round 1's weekly books on the same bins (0.172 to 0.229) and above the plan's estimates; a
    weekly sample of the 21-day skewness book cost more than its daily-updated form in generation 2 (0.239
    against 0.140); and these books paid and received 0.51 to 0.60 of equity in gross funding each way.
    Suggestive only: a target held for a week is traded back against the drift of the movers a continuation
    book holds. Round 2, runs 1 to 3. WEAK as a number; a design yardstick next to lessons 19, 24 and 41.
46. Process: a screen fixed in advance, whose unseen readings (next30 and the paired comparison) were allowed to
    drop rules written after DEV results, stopped all three defaults in 3 sandbox runs of 9 planned, with no
    counted trial. Two outcomes the plan had called predictable from the parents did not come out as expected
    (a DEV Sharpe under the liveness bar; a next30 sign that a mirror's reading had seemed to fix, but a mirror
    pays its costs again). The one pattern DEV had kept showing was put to its own unseen DEV readings before
    any VAL bar was spent on it, and it did not survive them. PROCESS.

## From generation 3, round 3, the first wide screen (same kernel and unit; generations/gen003/REPORT.md, round 3)

47. In unit top30 on DEV, eleven pre-registered ideas from eight mechanism classes (a price against a recent
    reference, volatility and illiquidity shocks, the calendar clientele of volume, intrabar wicks, comovement
    with BTC, a volume trend, the noise of the premium, and an equal-weight combination) met one screen fixed
    in advance, and none passed; eight had the wrong sign. Only the anchoring book (distance below the 6-week
    high in volatility units) cleared the floor before costs (1.820), both stresses and next30 (0.601), and it
    failed the paired reading over the last 365 days of DEV (6 of 10 stale copies at least as good; book
    median -0.549). Generation 3 PLAN run log, round 3, runs 1 to 11; no trial id. WEAK: DEV only, one default
    each.
48. In that round no single-idea top30 book earned in both halves of DEV. Books that lean toward recent winners
    (a price against its recent high or average cost, volume growth) earned in 2020 and lost in 2022H1 and over
    the last 365 days, as round 2's continuation books did; books on unsigned or move-neutral measures lost in
    2020 and earned in 2022H1; an equal-weight combination of both kinds was flat (DEV Sharpe 0.372). WEAK as
    evidence about markets; a rule built on the split would descend from it. What it does say about the
    instrument: DEV holds two unlike regimes, and a book that reads well over the whole of it may be reading
    one of them.
49. A weekly book short the coins whose weekend share of volume rose lost in every DEV year (Sharpe -2.343):
    coins whose trading tilted toward the weekend did better the next week, the direction of lesson 39. Two
    constructions now agree on DEV in every year, but neither showed it on next30. Round 3, run 6; no trial
    id. WEAK; DEV is spent as a screen for the mirror, whose next30 reading would fail the screen as fixed.
50. Yardstick: weekly books that rank a price against a recent reference cost 0.30 to 0.31 of equity over DEV
    (0.35 to 0.37 per unit of gross) and paid and received 0.68 to 0.79 in gross funding each way, like
    continuation books; weekly books on unsigned volume and volatility measures cost 0.11 to 0.20 (0.13 to 0.23
    per unit of gross). Round 3, runs 1 to 10. WEAK as a number; a design yardstick next to lessons 19, 41, 45.
51. Process: the wide screen settled eleven ideas in eleven short runs, with no corner, no control and no
    counted trial. Thirty-nine ideas have now been screened or scored in all (ten in unit core, twenty-nine in
    unit top30), six of them in counted trials; none Tier 1. PROCESS.

## From generation 3, round 4, the second wide screen (same kernel and unit; generations/gen003/REPORT.md, round 4)

52. In unit top30 on DEV, ten pre-registered ideas (eight from six new mechanism classes, most built from the
    taker fields; two state-conditional forms) met one screen fixed in advance, and none passed; eight had the
    wrong sign. The market-state continuation book (three-week continuation after BTC's 8-week rise, reversal
    after its fall) read well on every item its design could shape (1.879 before costs, both stresses
    positive, all three DEV years positive, 2 of 10 stale copies with a book median of 0.579) and failed the
    one it could not shape: next30 read 0.106 against 0.3 required. Generation 3 PLAN run log, round 4, runs 1
    to 10; no trial id. WEAK: DEV only, one default each; the state rule was DEV-informed by design.
53. A weekly book short the coins whose takers bought at higher prices than they sold within the week, net of
    the week's move, lost in every DEV year (Sharpe -2.514): such coins did better the next week; next30 read
    +0.059. Round 4, run 1; no trial id. WEAK; DEV is spent as a screen for the mirror.
54. Yardstick: weekly top30 books on taker-imbalance and co-movement measures cost 0.09 to 0.17 of equity over
    DEV (0.11 to 0.20 per unit of gross) and lost 0.24 to 0.45 Sharpe under G4's reading and 0.57 to 0.82 under
    G2's; a state-switched continuation book cost 0.31 (0.37 per unit of gross) and paid and received 0.62 and
    0.69 in gross funding, like continuation books. Round 4, runs 1 to 10. WEAK as a number; a design yardstick
    next to lessons 41, 45 and 50.
55. Process: the second wide screen settled ten ideas in ten short runs, with no corner, no control and no
    counted trial. Forty-nine ideas have now been screened or scored (ten in unit core, thirty-nine in unit
    top30), six in counted trials; none Tier 1. PROCESS.
56. Across generation 3 the bets AGAINST pressure in the thirty most liquid perpetuals lost in every DEV year,
    whichever way the pressure was measured (the weekend part of a move, lesson 39; the weekend share of volume,
    lesson 49; the prices takers paid against the prices they sold at, lesson 53; flow in quiet hours), while
    the same books read about zero or the other way on next30. So DEV shows something in top30 that it does
    not show in ranks 31 to 60: a rule built on it would be a mirror of failed books, and it would meet G8,
    which asks for a positive Sharpe on next30, with DEV's own next30 readings against it. Rounds 1, 3 and 4;
    no trial id. WEAK: DEV only, read from failures, never registered. INSTRUMENT and PROCESS.
