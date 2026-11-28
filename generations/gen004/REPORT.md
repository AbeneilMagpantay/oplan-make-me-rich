# Generation 4 - REPORT (one part per round; round 1: PLAN version 1, a tier premise test)

Generation 4 runs on the kernel sealed on 2026-11-26 (semantic 7d923e7e2375986d; G6 0.05 in unit core, 0.10 in
unit top30). It opened by a decision taken by delegation after generation 3 closed (KERNEL_PROPOSALS.md, entry
of 2026-11-27): before any build for the less liquid coins, test the premise with the tools as they are. Each
part is the researcher's text for its round, saved by the coordinator after its gate (the plan appended only;
the programs unchanged; the sandbox rows counted; the ledger verified), followed by the coordinator's own part.

# Round 1 (PLAN version 1, a tier premise test)

## Sources
- generations/gen004/PLAN.md: version 1 and the coordinator's rulings as committed in e116ad8 (36,075 bytes, sha256
  b0e9de81773184ac...), with the stage-2 run log, amendments (none), the round's reading, the top30 screen outcome and
  DEV observations appended (46,323 bytes, sha256 a507a4d9aaeb5291...).
- The twelve sandbox outputs of the researcher session (DEV only; scratch gen004_r1/run_01 to run_12), rows 83 to 94
  (0-indexed) of ledger/sandbox_log.jsonl, `omr.status`, `omr.ledger summary`, `omr.ledger verify`,
  `omr.kernel_lock verify`.
- No returns file, no trial detail file, no calibration file and no data file was read. No VAL number exists for any
  program of this round: none was submitted.

## The premise and the rule, as fixed in advance
- The premise (KERNEL_PROPOSALS.md, decision of 2026-11-27): there is more to find in the coins ranked below the top 30,
  where a small account is not at a disadvantage. Tested with the tools as they are: the sandbox already reads every
  top30 program on unit next30 (ranks 31 to 60) and prints its DEV Sharpe there.
- The rule, fixed before any idea was written: k = the number of the round's ideas whose next30 DEV Sharpe is 1.0 or
  more with the registered sign. k of 3 or more: the coordinator proposes a unit for the less liquid tier to the human.
  k of 2 or fewer: the place gap is closed as a front for these data, and the coordinator goes on to the information gap
  (a desk study of other free, long and clean data).

## What was run
- Kernel 7d923e7e2375986d (sealed: G6 core 0.05, top30 0.10). Ten ideas written for the less liquid tier, each a weekly,
  dollar-neutral top30 program (nine also beta neutral), none from a closed class, none a relative of a logged next30
  reading: T-01 BTC catch-up of delayed coins and T-02 reversal where price impact rose (both "family seen", the flavour
  of the three positive limits-to-arbitrage readings logged before); T-03, T-04, T-05 perp leverage dynamics (premium
  against price, a loading on the unit's funding changes, premium against volume); T-06, T-07, T-10 trade-size
  composition (against returns, against absolute returns, against the premium); T-08, T-09 the timing of volume
  (leading or trailing big moves; chasing gains). T-03, T-05 and T-10 read index_close, T-04 funding8h.
- Coordinator's rulings before run 1: ten accepted; T-01 and T-02 family seen, T-08 not; two closed top30 forms whose
  next30 reading was never logged ADDED before any run and counted: T-11 gen002_prior_month_reversal and T-12
  gen002_activity_fade, unchanged at their defaults (twelve ideas); cap 18 runs.
- 12 sandbox runs of the cap of 18: the twelve defaults with --g6-lags, in the registered order. No stage-1 rejection,
  no kernel fault, no refusal; 79 to 211 s per run. No idea passed the top30 screen W1 to W8, so no corner was run.

## Result
| idea | next30 DEV | top30 DEV | G4 DEV | G2 DEV | pre-cost | A of 10; B | years + | first failed (top30 screen) |
|---|---|---|---|---|---|---|---|---|
| T-01 btc_catchup (family seen) | -0.568 | -0.544 | -0.950 | -1.223 | -0.138 | 6; -0.952 | 0 | W2 |
| T-02 impact_reversal (family seen) | 1.259 | -0.984 | -1.340 | -1.519 | -0.628 | 4; -0.563 | 0 | W2 |
| T-03 premium_feedback (basis) | -1.402 | 0.565 | 0.300 | -0.141 | 0.830 | 6; -0.268 | 2 | W2 |
| T-04 leverage_loading (funding) | 0.394 | -0.407 | -0.676 | -1.077 | -0.138 | 0; 0.778 | 1 | W2 |
| T-05 premium_volume (basis) | -1.078 | -0.063 | -0.335 | -0.773 | 0.209 | 6; -0.105 | 1 | W2 |
| T-06 rally_tickets | 0.020 | 0.094 | -0.174 | -0.638 | 0.362 | 9; -1.499 | 2 | W2 |
| T-07 move_tickets | 0.095 | -0.582 | -0.866 | -1.386 | -0.298 | 9; -1.768 | 1 | W2 |
| T-08 volume_lead | -0.981 | 0.220 | -0.067 | -0.642 | 0.507 | 1; 1.779 | 2 | W2 |
| T-09 gain_chasing | 0.554 | 1.102 | 0.862 | 0.344 | 1.342 | 5; -0.187 | 2 | W2 |
| T-10 premium_tickets (basis) | 1.559 | -1.431 | -1.727 | -2.200 | -1.135 | 6; -1.254 | 0 | W2 |
| T-11 prior_month_reversal | -0.790 | 0.381 | 0.057 | -0.297 | 0.705 | 8; -0.658 | 2 | W2 |
| T-12 activity_fade | -0.332 | 0.172 | -0.140 | -0.457 | 0.484 | 1; 0.899 | 2 | W2 |

Costs 0.100 to 0.192 of equity over DEV (C/G 0.117 to 0.225); names held 27.7 to 27.9 of 28.0 (T-04 22.7); speed limit
-0.165 to 0.274; none liquidated; next30 over 100 symbols in every run.

## k and what the rule says
k = 2: T-02 (1.259, family seen) and T-10 (1.559, reads the basis). Every idea printed a next30 Sharpe. By the rule fixed
in advance, k of 2 or fewer: the place gap is closed as a front for these data; no unit for the less liquid tier is
proposed. With no edge, two or more of twelve reach 1.0 in about 14 rounds of 100: the count is in the range chance gives.
Top30 screen, for information: all twelve failed W2 first (six with the wrong sign in top30, six under the pre-cost
floor); T-09 came closest (failed W2 at 1.342 and W7). No counted submission; M is unchanged at 6.

## What must NOT be concluded
- A next30 reading is one DEV number over about 2.5 years (standard error about 0.6), after the top30 cost rate, with
  no stress reading, of a program written for another unit. Two readings above 1.0 are not two edges, and ten below it
  are not ten absences.
- T-02 and T-10 are not candidates for anything: each lost in every DEV year in top30, and a unit for ranks 31 to 60
  would have to be built, audited and calibrated before either could be tested there. DEV is now spent for them on
  next30.
- "Less liquid coins hold nothing" is not established: the tier tested is ranks 31 to 60 of one exchange's perpetuals,
  at the top30 cost rate, with the fields and the 90-day lookback of the language; mechanisms that need both tiers (a
  lead from the top 30) or a level (illiquidity, size) could not be tested.
- The mirrors of the strongly negative next30 readings (T-03 -1.402, T-05 -1.078, T-08 -0.981) are flipped readings,
  not discoveries.
- Choosing ideas is still open to hindsight (KP-010); the plan named what could bias each one.

## After the round
M = 6 (generation 0: 4, 1: 1, 2: 1, 3: 0, 4: 0 of 5), Tier 1: 0, pool 0 of 5, one uncounted stage-1 rejection. Sandbox
runs used in generation 4: 12 of 60 (ledger/sandbox_log.jsonl now 95 rows, the twelve new rows status ok, stage1 full,
their logged readings equal to the printed ones). PLAN.md's committed prefix of 36,075 bytes unchanged (checked before
and after the append).

## Requests to the coordinator
- LESSONS.md entries proposed for review (numbering from 62):
  - 62. A tier premise test registered twelve weekly top30 programs whose mechanisms belong to the less liquid coins
    (ten new; two closed top30 forms never read on next30) and counted those with a next30 DEV Sharpe of 1.0 or more with
    the registered sign, by a rule fixed before any idea was written. k = 2 (an impact-conditioned reversal 1.259; a
    trade-size-against-premium book 1.559), under the 3 the rule required; the twelve read a mean of -0.106. Generation 4
    PLAN run log, round 1, runs 1 to 12; no trial id. WEAK: DEV only, one default each; under the rule, the place gap is
    closed as a front for these data.
  - 63. Across that round the top30 and next30 DEV Sharpes of the same program were negatively related (correlation
    -0.589, same sign in 4 of 12; +0.244 over the 42 runs logged before): both readings that reached 1.0 on next30 came
    from books that lost in every DEV year in top30, as X-08, Y-05 and Y-13 had, and the best top30 books read 0.554,
    -1.402 and -0.790 on next30. No rule has yet earned in both tiers. Round 1, runs 1 to 12. WEAK; suggestive only.
  - 64. The two textbook liquidity-provision and attention forms closed in top30 also read negative on next30 (the
    reversal of the month before last -0.790, the fade of a trade-count burst -0.332). Round 1, runs 11 and 12; no
    trial id. WEAK: one default each.
- No kernel defect was seen. The sandbox's readings were printed and logged as documented; every run took under 4
  minutes.

# Round 1 closed: the coordinator's gate and the rule applied (written by the coordinator, 2026-11-27)

The gate. The plan's committed prefix (36,075 bytes, commit e116ad8) is unchanged and the stage-2 parts stand
below the rulings (46,323 bytes in all). The ten programs are byte for byte the pre-registered ones (git shows
no change under strategies/), and the two forms of generation 2 were run from their committed files. The
sandbox log has 95 rows (83 + 12) and all six chains verify; the lock verifies, sealed. The coordinator counted
k itself from rows 83 to 94 (0-indexed) of ledger/sandbox_log.jsonl: a next30 DEV Sharpe of 1.0 or more in two
rows, gen004_t02_impact_reversal (1.259) and gen004_t10_premium_tickets (1.559); six of the twelve above 0;
mean -0.106. That agrees with the researcher's table. (The column "pre-cost" differs from the log's unrounded
values in the third decimal for five ideas; no screen item is near enough to depend on it.)

The rule, as decided before any idea was written (KERNEL_PROPOSALS.md, entry of 2026-11-27): k = 2, so the
place gap is closed as a front for these data. No unit for the less liquid tier is proposed to the human. The
next step under the same decision is a desk study of which other data are free, long enough and clean enough to
be admitted (the information gap). It was ordered on 2026-11-27, reads documentation and file listings only,
and changes no project file.

What the coordinator adds to the researcher's reading.
- One short of the bar is not "nearly". The rule was fixed so that a count like this could not be argued up
  afterwards: with no edge at all, two or more of twelve happen in about 14 rounds of 100. Both hits came from
  programs that lost in every DEV year in the unit they were written for, and two other programs read -1.0 or
  worse on next30. Four of twelve readings beyond 1.0 in size, two each way, is what a tier with noisier books
  looks like; it is not what a tier with more to find looks like.
- The wider spread on next30 (0.93, against about 0.63 from chance alone) is the one thing in the round that
  could be read as "these coins react more to such signals". It is recorded as an observation, not as a
  finding. Three of the programs read the same series (the basis), so the twelve are not twelve independent
  draws, and a signal whose sign cannot be said in advance is not a rule. The mirrors of T-03, T-05 and T-08
  are barred like every mirror of a logged reading.
- The next30 reading charges the top30 cost rate. Coins ranked 31 to 60 cost more to trade than that, so the
  readings flatter the tier; a unit built for it would have started from lower numbers than these.
- What the round cost: twelve runs of two to four minutes and no counted trial. What it saved: a design, a
  build, audits and both calibrations (about 13 machine hours and days of work) for a unit whose premise now
  has no support.
- What stays true: the test covered ranks 31 to 60 of one exchange with the fields the data holds. Ranks below
  60, and mechanisms that need a level or both tiers at once, were not measured. Nothing in the project argues
  for measuring them next.

State after the round: M = 6, Tier 1: 0, pool 0 of 5. Generation 4 has used 12 of 60 sandbox runs and 0 of 5
counted submissions. Seventy-two ideas have now been screened or scored (ten in unit core, sixty-two in unit
top30; the two forms of generation 2 read again in this round are not counted twice), six of them in counted
trials; none Tier 1. Generation 4 stays open: a later round, if there is one, is a new PLAN version in the same
file.

# Round 2 (PLAN version 2, the spot premise study, KP-029)

## Sources
- generations/gen004/PLAN.md: PLAN version 2, the coordinator's rulings, the ruling on the guard table and the stage-1b
  amendment, as pre-registered in 64ba281 (86,523 bytes, sha256 a484673824121f8a...), with the stage-2 run log, the
  amendments (none), the round's reading and the DEV observations appended (93,648 bytes, sha256 39e3330cb46ab022...).
- studies/kp029/ as committed in 64ba281 (unchanged since), and its stage-2 outputs: run_log.jsonl (3 rows),
  spot_coverage.json; the downloader's log in _build/kp029_study/spot/download_log.jsonl (git-ignored); the session's
  scratch outputs gen004_r2/download_1.txt, coverage.txt, run_01_hs1.txt to run_03_hs4.txt.
- No returns file, no trial detail file, no calibration file was read; perpetual rows only through the kernel's loaders
  under the DEV ceiling; spot files of 2019-12 .. 2022-06 only. No VAL number exists for anything of this round; no
  sandbox or evaluator run, no ledger row (the sandbox log stays at 95 rows).

## The premise and the rule, as fixed in advance
- The premise (KERNEL_PROPOSALS.md, KP-029; the human's decision of 2026-11-28): the spot market of the same coins
  (hourly quote volume and taker-buy volume, which the kernel cannot see) adds information a weekly top30 book could
  use. Tested on DEV only, outside the sandbox, before any build.
- The rule, fixed in KP-029 before the human's decision and made exact in PLAN version 2 and the rulings, all before
  any spot file existed here: a hypothesis passes if it meets the wide screen of playbook 8b with the floor before
  costs at 1.85, then holds at both G5 corners (DEV Sharpe and G4 above 0), and beats its coverage-matched control by at
  least 0.5 of DEV Sharpe before costs, every run with the study's truncation test passed. At least one pass: an
  independent audit, then a proposal to admit the dataset. None: the spot front is closed, the dataset is not proposed,
  and the search is parked.

## What was run
- Three hypotheses (H-S3 and its control struck before any run, rulings 3 and 4), each a weekly, dollar- and
  beta-neutral top30 book in the kernel's language, the spot market served through two slots of the perpetual table
  (the loader hook; rulings 1 and 2): H-S1, short the coins whose trading moved most from spot to the perpetual (last
  week against the four before); H-S2, long the coins whose aggressive buying sits most on spot rather than on the
  perpetual (one week); H-S4, short the coins whose up days come with trading moving to the perpetual (four-week
  correlation). Controls: the same books with the spot input dropped, on the same coins and weeks.
- The download: 1,911 monthly spot files of 114 pairs, all kept, none missing, no checksum failure (68.2 MB, about 32
  minutes). The coverage count: 30 spot outage hours in 14 blocks (the longest 5 hours; every other pair without a row
  at them), 927,731 of 927,748 in-play slots known, 11 coin-hours rejected by the 50% guard; no tripwire.
- 3 evaluations of the cap of 14, through studies/kp029/run_study.py, in the registered order: the three defaults
  (kernel stage 1 with 25 truncation cuts and 7 start cuts, the study's truncation test over 8 cuts, every reading,
  the screen). About 212 s each. No default passed the screen, so no control and no corner was due. No void run, no
  fault, no amendment, the reserve unused.
- Before any of it (stage 1 and 1b): the evaluation path reproduced the sandbox's logged readings of three registered
  programs exactly (60 values, difference 0.0), and 31 synthetic checks of the look-ahead guards passed.

## Result
| hypothesis | DEV | G4 DEV | G2 DEV | pre-cost | next30 | speed max | A of 10; B | years + | names held | first failed |
|---|---|---|---|---|---|---|---|---|---|---|
| H-S1 share_shift | -0.210 | -0.612 | -1.029 | 0.193 | -0.875 | -0.013 | 0; 1.252 | 1 | 27.7 of 28.0 | W2 |
| H-S2 spot_flow | -1.218 | -1.545 | -1.945 | -0.891 | -1.103 | 0.102 | 6; -0.455 | 0 | 27.7 of 28.0 | W2 |
| H-S4 rally_carrier | -0.041 | -0.325 | -0.841 | 0.242 | 0.170 | 0.043 | 8; -0.960 | 1 | 27.7 of 28.0 | W2 |

Costs 0.111 to 0.160 of equity over DEV (C/G 0.130 to 0.187); none liquidated; benchmark 0.619; next30 over 100
symbols. Each also failed W3, W4, W5 and W8; H-S2 had the wrong sign in every DEV year.

## The verdict and what the rule says
No hypothesis passed: all three failed the screen at their defaults, at W2 first, far from the floor of 1.85 before
costs (best 0.242). By the rule fixed in advance, the spot front is closed: the dataset is not proposed to the human,
and the search is parked. No audit is due. Nothing was submitted; M is unchanged at 6.

## What must NOT be concluded
- "Spot data hold nothing" is not established: three weekly constructions on hourly volume and taker flow were tested,
  in the thirty most liquid perpetuals, on 2.5 years of DEV, with the kernel's fields, horizon and gates. Other uses
  (other horizons, other units, trade counts, the spot price itself) were not tested and are not proposed.
- The spot data did not fail on quality: coverage was 99.998%, the outage rule touched 1,052 in-play hours, the guard
  11. The study measured the premise, not the exchange's maintenance calendar.
- H-S2's negative reading in every year is not a finding of its mirror: flipped, it is a flipped reading; DEV is spent
  for it. The same for H-S1's good last year of DEV (0 of 10 stale copies, book median 1.252): one sub-period of one
  default, next30 -0.875, and a descendant would need a parent at 2.5 before costs.
- The evaluation path being exact (the sandbox's readings reproduced bit for bit) says the study measured what the
  kernel would have measured; it says nothing about VAL.

## After the round
M = 6, Tier 1: 0, pool 0 of 5. Generation 4: 12 of 60 sandbox runs (unchanged: this round used none) and 0 of 5 counted
submissions. Seventy-five ideas have now been screened or scored (ten in unit core, sixty-five in unit top30; the three
study hypotheses counted once each), six of them in counted trials; none Tier 1. The plan's pre-registered prefix of
86,523 bytes is unchanged (checked before and after the append). studies/kp029/run_log.jsonl and spot_coverage.json
are new and to be tracked (ruling 9); the spot files stay under _build/ and are never committed.

## Requests to the coordinator
- LESSONS.md entries proposed for review (numbering from 69):
  - 69. A premise study of the spot market of the same coins (hourly quote volume and taker-buy volume, unseen by the
    kernel) registered three weekly, dollar- and beta-neutral top30 books before any spot file existed, scored them with
    the kernel's own interpreter and engine outside the sandbox, and found none near the screen: before costs 0.193 (a
    shift of trading from spot to the perpetual, bet against), -0.891 (aggressive buying on spot against the perpetual,
    the wrong sign in every DEV year) and 0.242 (which market carries the rallies), against 1.85 required; next30 -0.875,
    -1.103, +0.170. Generation 4 PLAN run log, round 2, runs 1 to 3; no trial id. WEAK: DEV only, one default each; under
    the rule fixed in advance the spot front is closed and the search is parked.
  - 70. Binance's spot hourly archive for the coins of top30 and next30 was nearly complete on DEV: 1,911 monthly files
    of 114 pairs, all present and verified; 30 hours of exchange-wide outage in 14 blocks of at most 5 hours; 99.998% of
    in-play coin-hours with a usable spot row under a 50% price guard, which rejected 11 coin-hours (8 of LUNA's collapse).
    INSTRUMENT; counts, no result.
  - 71. Process: a study outside the kernel can be scored exactly as the kernel would score it by CALLING the kernel's
    functions (the weight matrix in, the readings out) and feeding new data through a constructor hook instead of
    copying the engine; the three registered programs it was checked on reproduced to the last bit. A tripwire table
    measured on the kernel's own rows before the data existed (the guard table) set a tolerance that did no harm, and a
    stop rule on it worked as intended. PROCESS.
- No kernel defect was seen. The study's runner refused nothing it should not have; every evaluation took about 212 s.

# Round 2 closed, generation 4 closed, the search parked (written by the coordinator, 2026-11-28)

The gate. The plan's pre-registered prefix (86,523 bytes, commit 64ba281) is unchanged and the stage-2 parts stand
below the amendment (93,648 bytes). The study's committed files are byte for byte the pre-registered ones (git
shows no difference under studies/ but the two new outputs). The lock verifies, sealed; all chains verify; the
sandbox log is at 95 rows, as before the round. The stored spot files number 1,911, of months 2020-01 to 2022-06
and none later. The coordinator recounted the verdict from studies/kp029/run_log.jsonl: three rows, every
truncation cut equal, Sharpe before costs 0.193, -0.891 and 0.242 against a floor of 1.85, and G4, G2 and next30
below their lines in all three. It agrees with the researcher's tables.

The rule, as fixed in KP-029 before the human's decision and before any spot file existed here: no hypothesis
passes, so the spot front is closed, the dataset is not proposed, and the search is parked. No audit is due.

What the coordinator adds.
- This was a fair test of the premise, and that was not a given. Two data rules were set by ruling before any
  spot file was opened. Left as first written, the thirty hours in which the spot exchange was down would have
  taken the books out of the market for about five weeks each time, fourteen times; and a price guard of 5%
  would have dropped up to 55 coins for weeks after the hours of greatest stress. With an outage counted as the
  zero volume it was, and the guard widened to its one job, 99.998% of the hours were usable. The books were
  fully invested (gross 0.85, 27.7 names of 28.0) and still read 0.19, -0.89 and 0.24 before costs.
- Nothing came near. The floor was 1.85, and the older floor of 1.5 would change nothing; no control and no
  corner was reached. The one flattering sub-reading (H-S1 over the last year of DEV) sits beside a next30 of
  -0.875 and a loss in 2020, and is recorded as an observation only.
- The scoring was the kernel's own: the study called the kernel's interpreter, stage 1 and engine, and
  reproduced sixty logged readings of three registered programs to the last bit before it scored anything new.
  A build would have measured the same numbers after days of work and thirteen machine hours.
- What it cost: an afternoon of one researcher, 68 MB of public files, three runs of three and a half minutes.

Generation 4 is closed with it: 0 of 5 counted submissions, 12 of 60 sandbox runs, and three study evaluations
outside the sandbox (of a cap of 14). Two premises were tested, each before the build it would have justified
and each under a rule written before its data were seen: the less liquid coins (k = 2 of 12, three needed) and
the spot market of the same coins (0 of 3). Both fronts are closed.

Where the project stands. Seventy-five ideas have been screened or scored (ten in unit core, sixty-five in unit
top30), six of them in counted trials; none passed, and none came close on held-back data. With free public
data, at the weekly horizon, in the thirty most liquid perpetuals, under gates that credit timing skill only,
the search has found nothing, and the two cheapest ways to widen it have been tested and closed. THE SEARCH IS
PARKED, as the human was told it would be if this check found nothing. The kernel stays sealed and ready: a
single idea he brings is tested in one short run against the same screen. Everything else (another horizon,
paid data, a change of what the scorer credits, live trading) is his decision, and none of it is recommended by
the evidence so far. None of his money belongs in any rule tested here.

The kernel's full test suite is run at this close, as the playbook asks; its result is recorded in STATE.md.
