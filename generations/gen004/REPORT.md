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
