# Generation 3 - PLAN (version 1, round 1, pre-registered 2026-11-26 before any generation-3 sandbox run)

Researcher session for generation 3, round 1, stage 1 (read, think, pre-register). Unit: top30. A fresh session:
generations 0 to 2 are known to it only through the files listed below. The date in the heading is local time
(+08:00); the UTC time is in the last line of this version.

- Kernel: semantic 7d923e7e2375986dc12df4e54c20049bf214d90b49544be64d0665e24e6c3194 (40 files), text
  b74122f3f9821056bbb5217ece9526d7068207d61f5941f47f5118c16fcd5209 (39 files) (`python -m omr.status`: kernel OK
  d09812fdec752a17, sealed). Sealed G6 thresholds: core 0.05, top30 0.10. Data research_hash 28d9084a8c5c7659...,
  validated, snapshot_end 2026-11-18 10:00 UTC.
- Ledger when this was written: M = 6 counted trials (generation 0: 4, generation 1: 1, generation 2: 1), N 5.90, rho
  0.021, Tier 1: 0, pool 0 of 5, last census none, one uncounted stage-1 rejection (generation 0). `omr.ledger verify`
  OK, all six chains (trials 12 rows, stage1_log 1, kernel_history 12, calibration_log 6, sandbox_log 43,
  val_access_log 29); `omr.kernel_lock verify` OK (sealed, core 0.05, top30 0.1). Generation 3: 0 of 5 counted, 0 of
  60 sandbox runs.
- Read, in this order: RESEARCH_PLAYBOOK.md (all; sections 3, 4, 4b and 5 with care), LESSONS.md (all 38),
  STATE.md (all, with "Where things stand" and "Open decisions for the human"), generations/gen002/REPORT.md (all
  four rounds and the counted trial), generations/gen002/PLAN.md (all four versions with their rulings, run logs,
  screen outcomes, observations and recommendations, and the coordinator's decision before the counted run),
  LANGUAGE.md (all; sections 3, 6, 7 and 10 with care), CONSTITUTION.md sections 4 to 7 and 13, rows 40 and 41 of
  ledger/sandbox_log.jsonl (0-indexed; file lines 41 and 42; the first 300 characters of row 42 were also on screen:
  gen001_tsmom_long_flat, DEV Sharpe 1.740, 116 direction changes), `python -m omr.status`, `python -m omr.ledger
  summary` (trial rows only), `omr.ledger verify`, `omr.kernel_lock verify`.
- Kernel source read only to learn how the tool behaves: omr/sandbox.py (what a top30 run prints and logs, the KP-018
  readings), omr/upipeline.py (dev_speed_limit, dev_names_held and dev_paired_lags only: the decision rows and the
  lags each reading uses), omr/lang.py (the tf_last / tf_mean checks, the lookback rule, the Program fields,
  parse_file). Program shapes: omr/programs/ucal_xs_momentum.omr, ucal_xs_reversal.omr, ucal_xs_carry.omr,
  kernel_kitchen_sink_tf.omr, kernel_noise_top30.omr; strategies/gen002_absorbed_flow.omr,
  gen002_averaged_funding_shock.omr, gen002_diag_acf_averaged_funding_shock.omr. Code, not data or results.
- Not opened: anything under data/, ledger/returns/, ledger/trials/, _build/, audits/, every calibration file, and
  KERNEL_PROPOSALS.md. No VAL number exists for any program below. No generation-3 sandbox run has been made, and no
  project program was run on data: the only program run was a parse-only check (omr.lang.parse_file; the constant
  probe runs on the kernel's synthetic panel) from a script in the session scratch folder (gen003_r1/parse_check.py;
  the files were written by gen003_r1/write_programs.py, ASCII with LF).
- Files of this version: this PLAN.md and six new program files (three candidates, three DEV-only placebos). No
  earlier file was changed.

Three hypotheses. All are dollar neutral (cs_demean, gross 1 by cs_scale), all change their weights once a WEEK (every
input passes through `tf_mean(., weekly)`), and none reads funding8h, funding_mean, mark_close or index_close. Each
ranks HOW a coin's week was made, holding the week's residual move fixed: it is the first use in this project of the
kernel's new tf_mean (KP-019) to turn hourly information into a weekly bar.

| H | program | conditioning (which hours of the week) | prediction | family |
|---|---|---|---|---|
| H1 | gen003_weekend_share | the weekend: hours whose decision-time weekday is Saturday or Sunday | the weekend part of a coin's weekly residual move partly reverses, relative to the weekday part | meanrev |
| H2 | gen003_heavy_hours | the coin's own abnormally heavy hours: its hourly quote volume over its trailing week, ranked across coins every hour | the part made in the coin's heavy hours partly reverses, relative to the part made in its quiet hours | flow |
| H3 | gen003_storm_share | BTC storm hours: each hour weighted by its share of BTC's recent hourly variance (the same for every coin) | the part made in market storm hours partly reverses, relative to the calm-hour part | meanrev |

None of the three descends from a DEV result of generation 2: no earlier program conditions on hours, and each is
built orthogonal, coin against coin on every weekly bin, to the week's residual move, which is the quantity whose DEV
behaviour (continuation) earlier rounds measured. Their DEV numbers will still be DEV readings only (LESSONS 34, 35).

## What I had seen before writing (numbers known to this session)

- Every DEV number of generation 2 (generations/gen002/REPORT.md and PLAN.md run logs; KP-015 kernel, unit top30,
  defaults unless stated; costs = equity over DEV; years + of 2020, 2021, 2022H1):

  | round, program | DEV Sharpe | costs | funding paid (minus = received) | years + | other readings |
  |---|---|---|---|---|---|
  | 1 H1 resid_reversal | -1.566 | 0.1369 | 0.0212 | 0 of 3 | |
  | 1 H2 activity_fade | 0.172 | 0.1669 | 0.0141 | 2 of 3 | |
  | 1 H3 small_tickets | -0.211 | 0.2309 | -0.0486 | 2 of 3 | |
  | 1 H4 absorbed_flow | -1.251 | 0.1649 | 0.0145 | 0 of 3 | |
  | 2 H5 resid_skew | -1.906 | 0.1404 | 0.0057 | 0 of 3 | |
  | 2 H7 prior_month_reversal | 0.381 | 0.1772 | 0.0117 | 2 of 3 | |
  | 2 H6 resid_momentum | 0.945 | 0.3299 | -0.0764 | 2 of 3 | neighbours 0.923 to 1.069, all lost 2022H1 |
  | 3 H8 premium_shock | 0.823 | 0.5081 | -0.1434 | 3 of 3 | |
  | 3 H9 funding_shock | 1.197 | 0.4447 | -0.2821 | 2 of 3 | |
  | 3 H10 unrewarded_premium | 0.980 | 0.4497 | -0.2975 | 3 of 3 | |
  | 4 H11 averaged_funding_shock | 1.492 | 0.2182 | -0.1555 | 3 of 3 | corners 1.286 / 1.805; stale copy 0.032; twin 1.466; D-ACF R -0.356 |
  | 4 H12 averaged_unrewarded_shift | 0.731 | 0.2163 | -0.1025 | 2 of 3 | 0.8 corner 0.249 |

  Every run printed the benchmark (equal-weight long of the in-play members) at DEV Sharpe 0.619, maxDD 0.847.
- The aggregate VAL row of generation 2's counted trial, gen002_averaged_funding_shock (7eadbeeaf2adc98d): VAL Sharpe
  -0.249, PSR(0) 0.333, DSR 0.038 (M 6); G1 F, G2 F (-0.697), G3 P (DEV 1.499), G4 F (-0.659), G5 F (median -0.181,
  share 0.00), G6 F (p 0.571), G7 F (4 of 6; largest share 0.735), G8 P (0.478), G10 P (2792); deploy_scale 0.495;
  VAL max drawdown 0.383; benchmark VAL Sharpe 0.279. Also the rows of generations 0 and 1 in `omr.ledger summary`
  (VAL Sharpe -0.531, -0.770, 0.384, -0.323 and 0.830; none Tier 1) and STATE.md's BTC/ETH benchmark over VAL (0.921).
- The KP-018 readings in sandbox rows 40 and 41 (the coordinator's verification runs of 2026-11-25, re-keyed kernel):

  | row, program | DEV Sharpe | speed limit r(1), r(2), r(3) | next30 DEV | funding paid / received (gross) | G2 DEV | G4 DEV | names held / in play | paired reading |
  |---|---|---|---|---|---|---|---|---|
  | 40 gen002_averaged_funding_shock | 1.492 | -0.271, -0.088, 0.042 | 0.637 | 0.388 / 0.544 | 0.735 | 1.165 | 26.1 / 28.0 | not taken |
  | 41 gen002_resid_reversal | -1.566 | -0.001, -0.023, -0.001 | -1.030 | 0.198 / 0.177 | -2.179 | -2.022 | 27.9 / 28.0 | 1 of 10 at least as good (p 0.182); book median -0.066, stale median -0.544 |

  Two design yardsticks follow from them (not evidence about any market): (1) G2's stress charges half of the gross
  funding PAID plus half of the gross RECEIVED (paid x1.5, received x0.5), not the net: about 0.47 of equity over DEV
  for row 40 (net received 0.156), whose DEV Sharpe fell by 0.76 under G2 against 0.33 under G4; and about 0.19 for
  row 41, a book that reads no funding (Sharpe down 0.61 under G2, 0.46 under G4). For a top30 book that holds a full
  book through DEV, G2 binds as hard as G4 or harder, whatever its inputs. (2) A losing book read p 0.182 in the
  paired reading because its stale copies lost more: the reading alone says little, so the screen below also asks the
  book's own median Sharpe in that reading to be positive.

## What a top30 idea must clear (playbook 4b, LANGUAGE.md 10, CONSTITUTION 13), and how these programs meet it

- Costs: 12.5 bps per side. Weekly rank books paid 0.137 to 0.231 of equity over DEV (LESSONS 19); books with a
  daily-moving part paid more (LESSONS 24: a daily-updated beta made round 2's weekly-formation books cost 2 to 5
  times the estimate; LESSONS 28 and 32). Here the hourly beta, the hourly volume ranks and BTC's hourly variance
  shares enter ONLY through `tf_mean(., weekly)`, so the targets change once a week, at the bar that opens Sunday 23:00
  (traded at the Monday 00:00 open), whatever those hourly parts do. A name leaves or re-enters the book only through
  play and knownness (below). Estimate: the ranking is close to independent from week to week, so about 4/3 of gross
  is traded per week, plus drift and in-play churn: 0.15 to 0.25 of equity over DEV (0.19 to 0.29 per unit of avg
  gross), as round 1's weekly books. At a rank book's volatility (about 0.2 to 0.26 a year) that is 0.3 to 0.45 Sharpe
  units, as much again under G4.
- Funding stress (G2): none of the books reads funding, but each holds a full book and pays and receives funding on
  it. By the yardstick above, G2 should cost these books 0.4 to 0.6 Sharpe units on DEV. With G4's doubled costs, a
  DEV Sharpe of about 0.7 is needed to pass both DEV readings (S4, S5); the liveness bar S2 (0.6) is not the item that
  binds. G1 (VAL PSR(0) >= 0.90 over three years) needs a net VAL Sharpe of about 0.75.
- Timing (G6) and the speed limit. G6 compares the book with its own weights 30 days to about 18 months earlier. Each
  claim here is about the composition of the LAST week; a stale copy holds the compositions of weeks at least a month
  old, which on the hypotheses have long since played out, so it should earn nothing. What a stale copy shares with
  the book is any lasting per-coin tendency (a coin whose weekend share, heavy-hour share or storm sensitivity is
  always high): that earns no timing credit, as it should. The speed-limit statistic: one G6 lag step (621 hours) is
  about 3.7 weekly bins, and the book's weights at the two rows share no week of data; G6 removes each name's mean,
  so a lasting tendency does not count. Expected near 0; S7 reads it on DEV (row 41, a weekly book, read -0.02 to 0).
- Lookback (limit 2,160 hours; every window param at its high bound; parse check): 739 hours for all six files (405
  for the hourly return and the beta window at its high bound of 404 rows, plus the weekly bin's 2 x 168 - 2 = 334).
- Cross-sections (a cs_* needs at least 10 in-play names with a known input). The beta uses cs_mean of the hourly
  returns INSIDE a window, and a cs_* is known only for in-play names, so a coin gets a known weekly value only after
  being in play on every hour of the beta window and of the week: 21 days at the default (24 at the high bound).
  Month-start entrants therefore trade from about their fourth week (G6 does not credit recent entrants either). A
  name with one unusable hour or one stale funding settlement inside that span drops out for up to three weeks, and a
  market-wide unknown hour would flatten the whole book for as long. Named in advance; S1's names-held reading shows
  it on DEV (rows 40 and 41 held 26 and 28 of 28).
- G8 runs the rule on ranks 31 to 60: residuals, ratios to the coin's own trailing mean and ranks mean the same there.
- G7: with the unit's seasoning and three weeks of history, 2020 is a short bucket; in effect four of the five later
  buckets must be positive.
- Literals and G5: no candidate has a jitterable literal (n_literals 0). H1 has n (integer) and d (float); H2 and H3
  have n and k (integers). G5 multiplies every param by its own U(0.8, 1.2): n becomes 269 to 403 and k 134 to 202
  (never the defaults); d lands in (4, 5] (the weekend set Saturday and Sunday, unchanged) or in (5, 6] (Sunday only),
  each about half the time. d is a param and not the literal 5 so that the Sunday-only outcome can be read on DEV with
  `--set` (a literal cannot be set in the sandbox). The DEV corners (S10) are the two corners at which every param
  sits at the same G5 end; mixed corners are not read.
- Funding and basis: no program reads funding8h, funding_mean, mark_close or index_close, so the KP-017 restriction of
  playbook 4b does not apply to them (a book that pays or receives funding without reading it is not funding-driven:
  ruling of 2026-11-23, generation 2 round 2, (2)). KP-020 applies as to every top30 program: a Tier-1 result is
  measured per program in null worlds before it enters the pool. These books are built to be cheap to trade, which is
  exactly the case the unit's 3% bound has not measured (LESSONS 38).
- Calendar: H1 uses `weekday` to SELECT hours of a residual-return series; no calendar field is averaged over a bin,
  sampled at a bin's end, or used as a constant, threshold or scale. H2 and H3 use no calendar field.

## The construction shared by H1 to H3, and why

All three programs share their first five statements and their last three:

    r = ret(close, 1)                                    # the coin's hourly return
    m = cs_mean(r)                                       # the unit's equal-weighted hourly return
    e = r - corr(r, m, n) * std(r, n) / std(m, n) * m    # net of the coin's rolling hourly beta to m (n hours)
    vol = sqrt(tf_mean(e * e, weekly))                   # the week's residual hourly volatility
    x = cs_demean(tf_mean(e, weekly) / vol)              # the week's residual move, in units of vol
    y = cs_demean(tf_mean(<the conditioned part of e>, weekly) / vol)
    b = cs_mean(x * y) / cs_mean(x * x)                  # cross-sectional slope of y on x, every weekly bin
    z = y - b * x                                        # the conditioned part the week's move does not explain
    signal = cs_scale(cs_demean(-cs_rank(z)))

- Why a composition, orthogonal to the week's move. On DEV every bet against a recent residual move lost and the only
  DEV-positive price book was continuation (LESSONS 16, 17, 21, 23, 26), whose DEV is spent as a screen (LESSONS 16,
  17, 23) and which is the calibration's own momentum shape (LESSONS 13). Any book that is a function of the week's
  total move inherits that. Each book here holds the total fixed: across coins, z is uncorrelated with x on every bin
  by construction, so the book is neither a momentum nor a reversal book on the week, and its DEV result cannot be
  read off rounds 1 to 4. What it bets on is that one part of a week's move (weekend, heavy-hour, storm-hour) is more
  transient than the rest of the same move.
- Why hourly and then weekly. The conditioning needs the hour (was it a weekend hour, a heavy hour for this coin, a
  BTC storm hour?); tf_mean turns the hour-by-hour product into one weekly bar per coin, ranked once a week. In
  generation 2 this could only be written as an hourly rolling sum that re-ranked every hour (KP-019).
- Why a residual to the unit's mean with an hourly beta. A dollar-neutral rank book over coins with different betas
  is a market bet through beta whenever the conditioned hours carry a market move (a weekend crash, a storm hour, a
  heavy hour that is a market hour). With e net of each coin's own beta, a beta-1.5 coin's mechanical 1.5x move is
  not the signal. The market is the unit's mean and not BTC because BTC is a member: its residual against itself is
  zero up to rounding, and a ratio of two rounding noises would put BTC at a random extreme rank every week (the
  reason round 2's H5 gave). 14 days of hourly returns (336) estimate the beta far more precisely than 30 daily
  returns did (round 1's H1), and its hourly updates cannot reach the targets (above).
- Why in units of the week's residual volatility: the rank then reads how unusual the composition was for that coin;
  otherwise the extremes would be the most volatile coins every week.
- Why the contrarian sign: each mechanism says the conditioned part carries more transient price pressure than the
  rest of the move. Why weekly: the decision falls at the Monday 00:00 open, right after the weekend (natural for
  H1); for H2 and H3 a weekly decision bounds the turnover. The named risk common to all three: if the transient
  pressure decays within hours, nothing of it is left at the weekly decision, and the books earn nothing before
  costs (the falsifier then reads a DEV Sharpe near zero or below).
- The three conditioning variables are distinct (the calendar; the coin's own volume; the market's stress) but can
  overlap (a weekend storm; a coin's heavy hour inside a storm). That is why at most two are recommended, and why a
  placebo (S9) asks of each that its own conditioning, and not the construction, carries its DEV result.

## Disclosures that apply to every hypothesis

- The author model has read this market's history through DEV, VAL and the vault, and this session has read every
  DEV number of generation 2 and the counted trial's aggregate VAL row (listed above). No rule below names a date, a
  coin, a price level or a remembered event; every tunable number is a declared param. That does not remove hindsight
  from the CHOICE of ideas (KP-010); each hypothesis states what I remember that could bias it.
- What I remember about VAL (July 2022 to June 2025) that touches every market-neutral top30 book: BTC's share of
  crypto market value rose through most of VAL and most altcoins lagged it; memecoin waves in 2023 and 2024;
  single-coin collapses (FTT in November 2022, with SOL hit hard in the same days); the US spot ETFs (from January
  2024) concentrating institutional BTC and ETH flow in US weekday hours; several of the sharpest market moves falling
  on or around weekends (the USDC depeg weekend of March 2023; the night of Sunday 4 August into Monday 5 August 2024).
  I do not remember the result of any cross-sectional book conditioned on weekends, heavy hours or storm hours, in VAL
  or anywhere.
- What I remember about DEV (2020 to June 2022): the crash of 19 May 2021; the Saturday crash of 4 December 2021; the
  January 2022 sell-off; LUNA's collapse in May 2022 (with very heavy volume, in storm hours, and no recovery);
  Celsius and Three Arrows in June 2022; memecoin moves in 2021, several of them on weekends.
- At most TWO programs are recommended for a counted submission whatever DEV says (selection rule). LESSONS 12, 14,
  37 and 38: a true Sharpe-1.5 book passes Tier 1 only 68 to 82% of the time in this unit, G6 tests timing and not
  luck, and every counted trial raises M forever.
- Defaults are fixed now and are never changed after a run. The corners are a robustness check (the G5 ends), not a
  search; a better corner does not move the default. No sign is ever flipped: a wrong DEV sign drops a hypothesis, and
  its mirror would descend from that result.

## DEV screen (round 1), fixed now, before any number

A hypothesis is eligible only if it passes every item, in the sandbox (full stage 1, no --quick). Numbers are taken
as printed. The lines each item reads: "stage 1: ... direction changes (DEV) X ... -> PASS"; "DEV Sharpe S ...";
"rebalances ... avg gross G ... costs C  liquidated L"; the per-year rows; and the KP-018 block "top30 readings on DEV
rows only": "r(1 step) ... r(3 steps) ... max", "next30 ...: DEV Sharpe", "G2 on DEV ...: DEV Sharpe ...   G4 on DEV
...: DEV Sharpe", "names held: average H of ...", and with --g6-lags "stale copies at least as good as the book: A of
10" and "book Sharpe on the common names, median over lags B; stale copies median ...".

- S1 at the default: stage 1 PASS as written (parse, constant probe, truncation and start-cut self-checks), X >= 30,
  G >= 0.5, L False, and H >= 15 (the book holds at least about half the unit on average).
- S2 at the default: S >= 0.6 with the registered sign. A negative S drops the hypothesis; no sign is flipped.
  Liveness only, not evidence.
- S3 at the default: the year's return > 0 in at least two of the three DEV years printed (2020, 2021, 2022).
- S4 at the default (G4's reading): the DEV Sharpe under doubled costs > 0.
- S5 at the default (G2's reading): the DEV Sharpe under the funding stress > 0.
- S6 at the default (G8's reading): the next30 DEV Sharpe is printed (no code) and > 0.
- S7 at the default (G6's speed limit as G6 computes it): r(1), r(2) and r(3) are printed and each is <= 0.40. A
  margin under the gate's 0.5, because the DEV reading covers three lag steps and the gate takes the largest of 19;
  a reason line in place of the readings (no DEV history) fails S7.
- S8 at the default (--g6-lags, G6's paired comparison on DEV): A <= 4 (at most 4 of the 10 stale copies did at least
  as well as the book; p <= 5/11) AND B > 0 (the book's own median Sharpe on the common names over the ten lags is
  positive: the comparison means nothing for a book that lost over those 365 days, row 41). A refused reading fails
  S8. Under no timing, A is about uniform on 0 to 10, so S8 alone drops such a book a little more than half the time:
  a necessary reading, not a proof.
- S9 placebo: the DEV Sharpe of the hypothesis's placebo (gen003_diag_*, below) at its defaults is below 0.5 x S. The
  placebo is the same program with the conditioning moved off the hours the mechanism names, so if it earns half as
  well, the DEV result belongs to the construction, not to the mechanism.
- S10 at both G5 corners: DEV Sharpe > 0 AND the DEV Sharpe under doubled costs (G4's reading) > 0 at each. H1: (n, d)
  = (269, 4.5) and (403, 5.5). H2 and H3: (n, k) = (269, 134) and (403, 202). For d, 4.5 stands for G5's lower
  outcome (any d in (4, 5] gives the default set; 4.0 itself has probability 0) and 5.5 for its upper (Sunday only).

Order and economy: each default runs once, with --g6-lags, and that one run carries every reading of S1 to S8. If a
default fails any of S1 to S8, the hypothesis is dropped and nothing else is run for it. Otherwise its placebo runs
(S9); then, only if S9 passed, its corners in order, stopping at the first that fails S10. The defaults run first,
all three, so that no reading of one hypothesis is taken before every default has been read.

---

## H1. gen003_weekend_share

- Family meanrev. Kind portfolio. Unit top30. Dollar neutral, gross 1. A weekly series (bins from Monday 00:00 UTC,
  visible at the bar that opens Sunday 23:00, traded at the Monday 00:00 open).
- Rule: for each coin in play, e = its hourly return net of its rolling 14-day hourly beta to the unit's mean; over
  the week, x = the mean of e and y = the mean of e on the hours whose decision-time weekday is >= d (0 on the others),
  both over the week's residual hourly volatility. At d = 5 the selected hours are the 48 bars that open from Friday
  23:00 to Sunday 22:00 (decision times Saturday 00:00 to Sunday 23:00). z = y net of a cross-sectional fit on x.
  Weight: minus the cross-sectional rank of z, demeaned, scaled to gross 1. Short the coins whose weekend part was
  large for their week, long those whose weekend part was small.
- Program (default pre-registered; strategies/gen003_weekend_share.omr):

      n = param(336, 268, 404)       # hours in the rolling hourly beta to the unit's mean return (14 days)
      d = param(5.0, 4.0, 6.0)       # first decision-time weekday counted as weekend (5 = Saturday)
      r = ret(close, 1)
      m = cs_mean(r)
      e = r - corr(r, m, n) * std(r, n) / std(m, n) * m
      vol = sqrt(tf_mean(e * e, weekly))
      x = cs_demean(tf_mean(e, weekly) / vol)
      y = cs_demean(tf_mean(where(weekday >= d, e, 0), weekly) / vol)
      b = cs_mean(x * y) / cs_mean(x * x)
      z = y - b * x
      signal = cs_scale(cs_demean(-cs_rank(z)))

  2 params (n integer, G5 values 269 to 403; d float, G5 outcomes Saturday and Sunday, or Sunday only), 0 jitterable
  literals, 59 nodes, lookback 739 h. Parse check OK; canonical sha256 314bda30c2787ef3...; file sha256
  a88170965d1190d8....
- Hypothesis: the part of a coin's weekly residual move made on Saturday and Sunday partly reverses over the following
  week, relative to the part made on weekdays.
- Mechanism: time-varying liquidity supply. The weekend market is thin: bank and TradFi desks, CME and most
  arbitrage capital are off, market makers quote smaller with no hedging venue, and fiat rails are slow, while retail
  and leveraged speculative flow keeps trading. The same order flow then moves prices further, and the part of a move
  that was price pressure rather than information reverts when weekday liquidity returns. The equity analogues are
  the time-of-day clienteles: retail buying at the open lifts overnight returns that reverse during the day (Berkman,
  Koch, Tuttle and Zhang 2012), and returns accrue to different clienteles at different times of day (Lou, Polk and
  Skouras 2019). The book is the liquidity provider who leans against the weekend part and is paid on weekdays.
- Other side, and why it can persist: weekend momentum traders and retail flow in a thin book, and the positions
  squeezed or liquidated in it. Institutional calendars are structural, and providing liquidity on weekends is costly
  (staffing, risk limits, no hedging venue), so the weekend premium for liquidity need not be competed away.
- What its stale copies hold: the weekend compositions of weeks a month and more ago, which on the hypothesis have
  reverted long since; a coin whose weekend share is ALWAYS high is held by the copies too and earns no timing credit.
- Design choices, each made for a reason stated before any run: (1) the weekend is selected by the calendar, because
  the mechanism is about who is at work, not about volume (H2 is the volume test); (2) d = 5 takes both weekend days;
  G5's other outcome is Sunday only, a purer but smaller sample, read on DEV at the 1.2 corner; (3) the decision falls
  right after the weekend, so the book holds the weekend's information from the first weekday on; (4) the composition
  is orthogonal to the week's move (shared construction).
- Costs: weekly; estimate 0.15 to 0.25 of equity over DEV.
- Relation to earlier trials, lessons and rounds: new idea; no earlier program reads weekday or hour. Its x is close to
  the input of round 1's H1 (gen002_resid_reversal: the week's beta-residual return over volatility, which lost on DEV,
  LESSONS 16); H1 here is built orthogonal to x, so that result does not predict it. Not a calibration family. Answers
  LESSONS 13 and 14 (a timing claim about last week, not a characteristic), 19, 24 and 28 (weekly targets by
  construction).
- What I remember that could bias it: the "CME gap" folklore of crypto traders (BTC's weekend moves tend to be
  retraced after the CME futures reopen), which favours the registered sign but concerns BTC's level, not a
  cross-section; day-of-the-week studies on BTC (I recall Caporale and Plastun 2019, and Aharon and Qadan 2019, with
  Monday effects, not reliably); lower weekend volume in crypto, which I am sure of. From VAL: the ETF era sharpened
  the weekday clientele of BTC and ETH (favours the mechanism there); the weekend events listed above, whose
  cross-sectional outcome I do not remember. From DEV: the Saturday crash of December 2021 and weekend memecoin moves
  in 2021, outcomes not remembered. Nothing I remember tells the sign of a cross-sectional weekend-composition book.
- Falsifier. DEV (not submitted): S1 to S10 (a wrong DEV sign drops it, never flipped). Counted (VAL): falsified if
  G1 (PSR(0) < 0.90), G2 (funding-stress Sharpe <= 0), G4 (2x costs <= 0), G6 (p > 0.10, or the speed limit), G8
  (next30 Sharpe <= 0), or any other Tier-1 gate fails. Named risks: a weekend move that is information (news
  released on a weekend) is faded by the book; G7.
- DEV exploration (at most 4 runs): the default with --g6-lags; then the placebo gen003_diag_midweek_share (S9); then
  the corners (n, d) = (269, 4.5) and (403, 5.5) (S10).

## H2. gen003_heavy_hours

- Family flow. Kind portfolio. Unit top30. Dollar neutral, gross 1. A weekly series, as H1.
- Rule: e and x as in H1. q = the cross-sectional rank, at every hour across the in-play coins, of the coin's hourly
  quote volume over its own trailing k-hour mean (k = 168, one week); q is in [-1, 1]. y = the week's mean of e x q
  over the week's residual volatility: the residual move made in the coin's heavy hours minus that made in its light
  ones. z = y net of a cross-sectional fit on x. Weight: minus the rank of z, demeaned, scaled to gross 1. Short the
  coins whose heavy-hour part was large for their week, long those whose heavy-hour part was small.
- Program (default pre-registered; strategies/gen003_heavy_hours.omr): the shared statements with

      n = param(336, 268, 404)       # hours in the rolling hourly beta to the unit's mean return (14 days)
      k = param(168, 134, 202)       # hours in the coin's own trailing norm (7 days)
      q = cs_rank(quote_volume / sma(quote_volume, k))
      y = cs_demean(tf_mean(e * q, weekly) / vol)

  2 params (integers; G5 values n = 269 to 403, k = 134 to 202), 0 jitterable literals, 61 nodes, lookback 739 h.
  Parse check OK; canonical sha256 c807c41495defaf0...; file sha256 fc527938180a5ce7....
- Hypothesis: the part of a coin's weekly residual move made in its own abnormally heavy hours partly reverses over
  the following week, relative to the part made in its quiet hours.
- Mechanism: forced and attention flow is transient, gradual flow is information. In perps a coin-specific volume
  spike is mostly a liquidation cascade, a run of stops, a large holder leaving at any price, or a crowd arriving on a
  story; such flow moves the price beyond what patient holders think it is worth, and the excess reverts once the
  flow is done. Price changes that come with heavy volume from liquidity trading reverse (Campbell, Grossman and Wang
  1993; Avramov, Chordia and Goyal 2006), and information that arrives in many small steps is followed by stronger
  continuation than information that arrives in a few large ones (Da, Gurun and Warachka 2014, "frog in the pan").
  The book provides liquidity to the heavy-hour flow and holds the quietly made part of the move.
- Competing evidence, which is why the falsifier is directional: where trading is informed, heavy-volume moves
  continue (Llorente, Michaely, Saar and Wang 2002), and crypto altcoins may be such markets. The DEV results nearest
  to H2 side with the competitor: aggressive taker buying beyond the week's return went with continuation (LESSONS
  17), and right-skewed residual days went with outperformance (LESSONS 21). They argue against H2 on DEV; they did
  not shape it. A wrong DEV sign drops H2; its mirror would descend from those results and would not be registered.
- Other side, and why it can persist: liquidated and stopped-out traders, sellers who must sell now, and late arrivals
  in an attention burst. Leverage, liquidation engines and attention bursts are structural in perps, and the capital
  willing to absorb a coin-specific cascade is scarce exactly then.
- What its stale copies hold: heavy-hour compositions of weeks a month and more ago; a coin that always trades in
  bursts is held by the copies too and earns no timing credit.
- Design choices: (1) the RANK across coins at each hour, not the coin's own volume ratio: every coin's volume rises in
  the same hours of the day, on the same weekdays and in the same market storms, and the rank removes all of that, so q
  marks hours that were heavy for THIS coin; it also keeps q bounded, so one hour cannot carry the week; (2) quote
  volume (dollar activity), as a ratio to its own trailing week: it is the signal input, not a constant, threshold or
  scale; (3) no calendar field, so H2 does not overlap H1 by construction (a weekend hour is heavy for a coin only if
  it was heavy relative to other coins in that hour).
- Costs: weekly; estimate 0.15 to 0.25 of equity over DEV.
- Relation to earlier trials, lessons and rounds: new idea. Its fit is round 1's H4 device (gen002_absorbed_flow: a
  cross-sectional regression recomputed every bin, the residual ranked contrarian), applied to a different quantity
  (H4 ranked taker flow net of the week's return; H2 ranks the heavy-hour part of the move net of the whole move).
  Round 1's H2 (gen002_activity_fade) ranked a weekly trade-count shock (the level of activity) and had the registered
  sign but too little size (0.172; LESSONS 18); H2 here does not rank activity, it weights the week's returns by it.
  Not a calibration family.
- What I remember that could bias it: from DEV, LUNA's collapse (heavy volume, no recovery: against the long side) and
  the liquidation cascades of May 2021 (recoveries in the weeks after, by coin I do not remember); from VAL, FTT
  (heavy volume, no recovery) and memecoin listing bursts in 2023 and 2024, outcomes by coin not remembered. Nothing I
  remember tells the sign of the book.
- Falsifier. DEV: S1 to S10 (a wrong DEV sign drops it, never flipped). Counted (VAL): as H1. Named risks: single-coin
  collapses (the long side holds the coin that fell on heavy volume); G7.
- DEV exploration (at most 4 runs): the default with --g6-lags; then the placebo gen003_diag_lagged_heavy_hours (S9);
  then the corners (n, k) = (269, 134) and (403, 202).

## H3. gen003_storm_share

- Family meanrev. Kind portfolio. Unit top30. Dollar neutral, gross 1. A weekly series, as H1.
- Rule: e and x as in H1. s = BTC's squared hourly return over its own trailing k-hour mean square (k = 168): the
  hour's share of BTC's recent variance, the same for every coin in that hour (about 1 in an ordinary hour, tens in a
  storm hour). y = the week's mean of e x s over the week's residual volatility: the residual move made in BTC storm
  hours. z = y net of a cross-sectional fit on x. Weight: minus the rank of z, demeaned, scaled to gross 1. Short the
  coins whose storm-hour residual part was large for their week, long those whose storm-hour part was small (the coins
  that fell beyond their beta in the storm hours, given their week).
- Program (default pre-registered; strategies/gen003_storm_share.omr): the shared statements with

      n = param(336, 268, 404)       # hours in the rolling hourly beta to the unit's mean return (14 days)
      k = param(168, 134, 202)       # hours in BTC's own trailing norm (7 days)
      rb = ret(btc(close), 1)
      s = rb * rb / sma(rb * rb, k)
      y = cs_demean(tf_mean(e * s, weekly) / vol)

  2 params (integers; G5 values n = 269 to 403, k = 134 to 202), 0 jitterable literals, 67 nodes, lookback 739 h.
  Parse check OK; canonical sha256 92b7250ad822a7bb...; file sha256 31d7040382159fea....
- Hypothesis: the part of a coin's weekly residual move made in hours of market stress partly reverses over the
  following week, relative to the part made in calm hours.
- Mechanism: in a market-wide storm, how far an altcoin moves beyond its beta is set by leverage and liquidity, not
  by news about the coin: cross-margin liquidations and auto-deleveraging hit the most levered coins first, funds
  de-risk by selling what they can, and market makers withdraw from the thinnest books. Those residual moves are
  price pressure and revert as the stress passes. Liquidity provision earns most when liquidity evaporates (Nagel
  2012: short-term reversal returns rise with market volatility); cross-sectional reversal is stronger after market
  declines, when liquidity dries up (Hameed, Kang and Viswanathan 2010); margin spirals (Brunnermeier and Pedersen
  2009). The book buys the coins that were sold beyond their beta in the storm and sells those that held up.
- Other side, and why it can persist: liquidated and deleveraging traders, and holders de-risking in a hurry.
  Leverage is structural in perps, and the capital to absorb a market-wide cascade is scarcest exactly when it
  happens.
- What its stale copies hold: storm compositions of weeks a month and more ago; a coin that is ALWAYS sold hardest in
  storms (a lasting storm beta above its ordinary beta) is held by the copies too and earns no timing credit.
- Design choices: (1) BTC sets the storm clock (storms in this market are BTC-led, and btc(close) is known whatever
  the coin's play status), and the weight is the same for every coin in an hour, so the cross-section compares coins
  over the same hours; (2) squared moves, so that a storm hour outweighs a week of calm hours (an hour of five times
  the usual move weighs about 25), which is what the mechanism needs; (3) the beta residual matters most here:
  without it a coin with beta 1.5 falls 1.5 times the market in a storm hour by construction, and the book would be a
  bet that the market move reverses, through beta.
- Named limits, stated before any run: (a) in a calm week the weights spread over the hours in which BTC moved a
  little more than usual, and the ranking reads a weak form of the claim (noise, which costs a week of turnover); (b)
  a coin's beta in a storm is above its 14-day hourly beta (correlations rise in stress), so after a down storm the
  book is long the coins most sensitive to storms, and loses if the storm continues the next week; (c) a single-coin
  collapse inside a storm lands on the long side.
- Costs: weekly; estimate 0.15 to 0.25 of equity over DEV.
- Relation to earlier trials, lessons and rounds: new idea; no earlier program conditions on BTC's hourly moves. Round
  1's H1 removed a daily BTC beta from the week's return and ranked the whole residual; H3 is orthogonal to the whole
  residual. Not a calibration family. Answers LESSONS 13, 14, 19, 24 and 28 as H1.
- What I remember that could bias it: from DEV, the storms of May 2021, December 2021, January 2022 and May to June
  2022, with LUNA collapsing inside the May 2022 storms and not recovering (against the long side); from VAL, FTX in
  November 2022 (FTT and SOL fell far beyond beta and did not recover within weeks: against the long side), March 2023
  and August 2024 (outcomes by coin not remembered). I do not remember any cross-sectional result conditioned on
  storm hours. The memories I have argue against H3, through single-coin collapses.
- Falsifier. DEV: S1 to S10 (a wrong DEV sign drops it, never flipped). Counted (VAL): as H1. Named risks: limits (b)
  and (c) above; G7.
- DEV exploration (at most 4 runs): the default with --g6-lags; then the placebo gen003_diag_lagged_storm_share (S9);
  then the corners (n, k) = (269, 134) and (403, 202).

---

## DEV-only diagnostics (never to be submitted; each file's first line and hypothesis line say so)

Placebos for S9, a kind of DEV-only measurement new in this project (the coordinator's ruling is asked for below).
Each is its hypothesis's program with ONLY the conditioning moved off the hours the mechanism names; everything else
(the residual, the fit, the rank, the weekly decision) is unchanged, so it trades about as much and has the same
construction. Its Sharpe is read against the hypothesis's default; its other numbers mean nothing.

- strategies/gen003_diag_midweek_share.omr (H1's placebo): the weekend hours replaced by the 48 hours whose
  decision-time weekday is Wednesday or Thursday: `y = cs_demean(tf_mean(where((weekday >= 2) and (weekday < 4), e,
  0), weekly) / vol)`. 1 param (n), 2 literals (a diagnostic; never jittered in a gate), 63 nodes, lookback 739 h.
  canonical sha256 2f79889d4ce6ee6a...; file sha256 630561bcba922829....
- strategies/gen003_diag_lagged_heavy_hours.omr (H2's placebo): q taken j = 168 hours earlier (the same hour of the
  week, one week before), `q = lag(cs_rank(quote_volume / sma(quote_volume, k)), j)`, j = param(168, 134, 202): the
  weights keep their distribution and hour-of-week pattern but no longer mark the coin's heavy hours. 3 params, 0
  literals, 62 nodes, lookback 739 h. canonical sha256 278a3076305fba76...; file sha256 1186d86dfba2ca37....
- strategies/gen003_diag_lagged_storm_share.omr (H3's placebo): s taken j = 168 hours earlier, `s = lag(rb * rb /
  sma(rb * rb, k), j)`: BTC's variance shares of the same hour of the week, one week before, so the weights keep BTC's
  hour-of-week volatility pattern but no longer mark this week's storms. 3 params, 0 literals, 68 nodes, lookback
  739 h. canonical sha256 13024102e2865ebe...; file sha256 0235b6190a51180c....

Readings that generation 2 took with hand-made diagnostics (the speed limit by D-ACF, timing by a stale copy) are now
printed by the sandbox for every top30 run (KP-018), so no such diagnostic is written. No price-neutral twin is
needed: each candidate is orthogonal to the week's residual move by construction.

## Run order and budget (round 1, decided before any run)

| order | run | runs only if |
|---|---|---|
| 1 | H1 default (n = 336, d = 5.0), with --g6-lags | - |
| 2 | H2 default (n = 336, k = 168), with --g6-lags | - |
| 3 | H3 default (n = 336, k = 168), with --g6-lags | - |
| 4 | H1 placebo gen003_diag_midweek_share (n = 336) | run 1 passed S1 to S8 |
| 5, 6 | H1 corners (n, d) = (269, 4.5), then (403, 5.5) | run 4 passed S9; run 6 only if run 5 passed S10 |
| 7 | H2 placebo gen003_diag_lagged_heavy_hours (n = 336, k = 168, j = 168) | run 2 passed S1 to S8 |
| 8, 9 | H2 corners (n, k) = (269, 134), then (403, 202) | run 7 passed S9; run 9 only if run 8 passed S10 |
| 10 | H3 placebo gen003_diag_lagged_storm_share (n = 336, k = 168, j = 168) | run 3 passed S1 to S8 |
| 11, 12 | H3 corners (n, k) = (269, 134), then (403, 202) | run 10 passed S9; run 12 only if run 11 passed S10 |

`--g6-lags` is used on runs 1 to 3 only (the defaults), where S8 reads it. Command form (from the project root, venv
Python): `.venv\Scripts\python.exe -m omr.sandbox strategies\gen003_weekend_share.omr --g6-lags`, and for a corner
`.venv\Scripts\python.exe -m omr.sandbox strategies\gen003_weekend_share.omr --set n=269 --set d=4.5`; full stage 1
on every run, one run at a time.

Planned: at most 12 sandbox runs. Reserve: 2 runs for an honest restatement after a stage-1 rejection the parse check
cannot see (the activity floor or a self-check; the constant probe already ran with the parse check), each a recorded
amendment of one of the forms playbook section 4 lists, never a change of logic or of a default. Cap for this round:
14 (the instruction allows 16); generation 3 would then have used at most 14 of 60. A kernel_fault, or a refusal the
plan does not cover, stops the round. Every run goes into the log, including runs that fail.

Logged per run: DEV Sharpe, PSR(0), total return, maxDD, direction changes, rebalances, avg gross, avg net, costs,
C / G, funding paid (net), liquidated, the per-year rows, the number of symbols ever in the unit, the lookback; the
KP-018 readings: r(1) to r(3) and their max, next30 DEV Sharpe (and symbols, or its code), funding paid and received
(gross), G2 and G4 DEV Sharpes, names held and in play; on runs 1 to 3 the paired reading (A of 10, p, B, the stale
median, the lag range and decision span); for a placebo or a corner its DEV Sharpe against the default's.

## Selection rule (round 1)

- A hypothesis is eligible only if it passes every screen item: S1 to S10.
- At most TWO programs are recommended for a counted run. One or two eligible: they are recommended. All three
  eligible: H1 and the one of H2 and H3 with the higher MINIMUM DEV Sharpe over its default and its two corners (a tie
  goes to H3); H1 is kept because its mechanism (the calendar's clientele) is the one the other two do not share, and
  H2 and H3 are both forced-flow claims. If H2 and H3 are the two recommended, the coordinator should know that both
  are forced-flow claims and that their conditioning overlaps in storms.
- None eligible means none recommended; that is a result and is recorded as one.
- No recommendation needs the KP-017 measurement (no funding or basis input). KP-020 applies after a counted trial: a
  Tier-1 result is measured per program in null worlds before it enters the pool. A recommended program is submitted
  only at its declared defaults, unchanged, after the coordinator's source read (playbook section 5).
- DEV Sharpe is a liveness check, not a ranking beyond these rules. The placebos (gen003_diag_*) are never submitted.

## Notes and open questions for the coordinator (written with the plan)

Rulings asked for before run 1:
1. H1's use of `weekday` (playbook section 5, the source read): weekday SELECTS the weekend hours of a residual-return
   series inside tf_mean (`tf_mean(where(weekday >= d, e, 0), weekly)`). No calendar field is averaged over a bin,
   sampled at a bin's end, or used as a constant, threshold or scale, and the result is a return, ranked. Is it
   acceptable? If not, H1 and its placebo are withdrawn by an amendment written before run 1, and the planned runs
   fall by 4 (runs 1, 4, 5 and 6).
2. H1's d as a FLOAT param in a comparison with the integer-valued weekday: it is a step function (the selected set
   changes only at whole weekdays), as G5's jitter of a literal 5 would be; it is a param only so that G5's upper
   outcome (Sunday only) can be read on DEV with --set. Acceptable as declared?
3. The placebos (S9) as DEV-only measurements of a new kind (in the line of generation 2's stale copies and twins):
   allowed? Their runs count toward the cap and they are never submitted. If not allowed, S9 is removed by an
   amendment before run 1, and the planned runs fall by 3.
4. --g6-lags on the three default runs, and S8 as written (A <= 4 of 10 and B > 0; a refused reading fails S8).
5. Confirmation that the KP-017 restriction does not apply: no file reads funding8h, funding_mean, mark_close or
   index_close (H2 reads quote_volume; H3 reads btc(close)).

Notes:
- For the source read (playbook section 5): H2's `quote_volume / sma(quote_volume, k)` is the SIGNAL input (a ratio to
  the coin's own trailing week, then ranked across coins at each hour), not a constant, threshold or scale; H3's
  `rb * rb / sma(rb * rb, k)` likewise (BTC's variance share of an hour, a weight on returns); b is a cross-sectional
  regression slope recomputed at every weekly bin (round 1's H4 device); vol divides two series of the same coin and
  week. No program uses hour, a near-constant, a tiny-param scale or algebra across a comparison.
- The parse check's OK lines include the constant probe (omr.lang.parse_file runs it on the 12-symbol top30 probe
  panel). The activity floor and the self-checks remain for the sandbox.
- What I could not do in stage 1: no sandbox run and no synthetic turnover model; the cost estimate rests on round 1's
  measured weekly books (LESSONS 19), not on a computation. How much coverage the 21-day knownness span costs is
  unknown until S1's names-held reading.
- Ideas considered and not registered, with the reason: (a) continuation rules with other mechanisms (frog in the pan
  on its own, a capital-gains overhang from hourly VWAP, nearness to a recent high): DEV is spent for continuation
  (LESSONS 16, 17, 23), and a per-year item chosen now would be chosen knowing round 2's 2022H1 rows; (b) a session
  composition (Asian against US hours): a second calendar clientele, with boundaries that shift with daylight saving,
  left out to keep the calendar source read to one hypothesis; (c) volatility or illiquidity shocks: no clear sign,
  and close to round 1's H2 (activity bursts move with them); (d) betting against beta or low volatility: lasting
  characteristics whose premium G6's stale copies share; (e) any funding or premium form: DEV is partly spent
  (LESSONS 27), and the mechanism of the crowded-leverage forms failed its counted trial (LESSONS 34), so a new form of
  it would come close to tuning on a VAL result; (f) the part of a move made in hours where taker flow agreed with the
  price: it continues round 1's H4 result (LESSONS 17), whose mirror is DEV-spent.
- What I saw that disagrees with another part of the materials (no kernel defect found):
  (a) STATE.md as I first read it said generation 2 "is open at 1 of 5 counted submissions and 22 of 60 sandbox
      runs". While this plan was being written, uncommitted working-tree edits (STATE.md and
      generations/gen002/REPORT.md, both saved 2026-11-26 about 12:01 UTC, not by this session) closed generation 2
      in STATE.md's "Now" paragraph and added "Generation 2 closed" to the report; I saw them afterwards with a
      read-only `git diff`, and nothing in this plan depends on them. Still stale: STATE.md's section "Next" (line
      91) begins "Generation 2 is the next research step". The evaluator accepts generation 3
      (generations/gen002/REPORT.md exists and 3 is the ledger's highest generation plus one).
  (b) CONSTITUTION.md section 13's heading still reads "NOT in force until the human approves the re-key", while the
      unit has been sealed and in force since 2026-11-23 (STATE.md).
  (c) RESEARCH_PLAYBOOK section 3 asks for 3 to 5 hypotheses, the brief for 2 to 4; this plan has 3, inside both.
  (d) STATE.md calls rows 40 to 42 of ledger/sandbox_log.jsonl the coordinator's verification runs (three); the brief
      cites rows 40 and 41, the two top30 programs (0-indexed; file lines 41 and 42). Consistent once counted that way.
  (e) git status at the end of stage 1: the six new program files and generations/gen003/ untracked, and the two
      coordinator edits of (a) modified; this session made no git write.

Pre-registration (version 1): 2026-11-26T12:22:43Z; no generation-3 sandbox run has been made.

---

## Sandbox run log (round 1)

(filled in during stage 2; every run, chosen or not)

| # | program | params (non-default only) | DEV Sharpe | dir. changes | avg gross | names held | costs | C/G | funding paid / received (gross) | G2 DEV | G4 DEV | next30 DEV | r(1), r(2), r(3) | paired (A of 10; B) | years + (of printed) | note |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

## Amendments (round 1)

(to be filled in stage 2, if any)

## Screen outcome per hypothesis (round 1)

(to be filled in stage 2)

## DEV observations (round 1; NOT hypotheses, never to be submitted from this plan)

(to be filled in stage 2)

## Recommendation (round 1)

(to be filled in stage 2)

## Coordinator's rulings before run 1 (2026-11-26; appended by the coordinator, nothing above is changed)

The coordinator read the plan in full before any generation-3 sandbox run. The six program files parse (lookback
739 hours each); the sandbox log stands at 43 rows, none of generation 3.

1. H1's use of weekday: accepted. The language shows a program the hour and the weekday of the decision time so
   that it can condition on them. The source read of playbook section 5 is about constants, thresholds and scales
   built from calendar fields; here weekday selects which hours of a return series enter a weekly mean, and what
   is ranked is a return.
2. d as a float param: accepted as declared. A literal 5 would be jittered over the same interval by G5; as a
   param, the Sunday-only outcome can be read on DEV. A counted run of H1 would draw the Sunday-only set in about
   half of G5's variants, and the program must stand that.
3. The placebos and S9: allowed as DEV-only measurements. They count toward the cap and are never submitted. S9
   only drops: a placebo that earns nothing adds no evidence for its hypothesis.
4. --g6-lags on runs 1 to 3 and S8 as written: accepted. The paired reading on DEV is not the gate.
5. KP-017's restriction does not apply: the coordinator read the six programs, and their fields are close,
   quote_volume, btc(close) and weekday. KP-020 applies as the plan says.
6. Budget: the cap of 14 runs stands (12 planned, 2 in reserve). One run at a time (a top30 run needs free
   memory; a refusal for memory is not a run and is repeated later).
7. Stage 2 starts only after this plan and its programs are on the remote. Its parts (run log, amendments, screen
   outcome per hypothesis, DEV observations, recommendation) are appended below this section.
8. Two stale texts the researcher found: STATE.md's "Next" (mended with this commit) and the heading of
   CONSTITUTION section 13 (kernel text; filed as KP-024).

## Sandbox run log (round 1), filled in during stage 2

(Appended below version 1 and the coordinator's rulings, so that the 52,751 bytes committed as 48e12d0 stay an
unchanged prefix. Every run is listed; run numbers follow the order table of version 1, and numbers not listed were
not due under its conditions. C/G = costs / avg gross. Funding paid / received are the gross flows of the KP-018
block; the net printed on the "rebalances" line is in the note, minus = received. Each output is saved as ASCII in
the session scratch folder, gen003_r1/run_NN_<name>.txt.)

| # | program | params (non-default only) | DEV Sharpe | dir. changes | avg gross | names held | costs | C/G | funding paid / received (gross) | G2 DEV | G4 DEV | next30 DEV | r(1), r(2), r(3) | paired (A of 10; B) | years + (of printed) | note |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | H1 gen003_weekend_share | (default n=336, d=5.0), --g6-lags | -1.348 | 1791 | 0.833 | 25.0 of 28.0 | 0.1720 | 0.206 | 0.2911 / 0.2916 | -2.004 | -1.756 | 0.217 (100 symbols) | -0.033, -0.049, 0.009 (max 0.009, under the limit) | 8 of 10 (p 0.818); B -1.740, stale median -0.789 | 0 of 3 (2020 -0.080 SR -0.518; 2021 -0.300 SR -1.313; 2022 -0.300 SR -2.468) | PSR(0) 0.011, total -0.549, maxDD 0.580, avg net 0.002, funding net -0.0005, rebalances 668, liquidated False, 75 symbols, lookback 739 h, stage 1 PASS (25 cuts). Speed-limit rows 2020-08-10 14:00 to 2022-06-30 22:00; paired lags 30 to 262 days, decisions 2021-06-30 23:00 to 2022-06-30 22:00. Wall time 167.7 s (20:44:19 to 20:47:07 +08:00); free memory before the run 1,407,392 KB physical, 9,092,128 KB virtual. Fails S2 (wrong sign), S3, S4, S5 and S8: H1 DROPPED; runs 4, 5 and 6 not made |
| 2 | H2 gen003_heavy_hours | (default n=336, k=168), --g6-lags | -0.256 | 1675 | 0.833 | 25.1 of 28.0 | 0.2286 | 0.274 | 0.3908 / 0.3992 | -1.030 | -0.705 | 0.007 (100 symbols) | -0.020, -0.003, -0.059 (max -0.003, under the limit) | 9 of 10 (p 0.909); B -1.200, stale median -0.865 | 1 of 3 (2020 0.080 SR 0.667; 2021 -0.062 SR -0.164; 2022 -0.163 SR -1.725) | PSR(0) 0.343, total -0.152, maxDD 0.345, avg net 0.000, funding net -0.0084, rebalances 600, liquidated False, 75 symbols, lookback 739 h, stage 1 PASS (25 cuts). Same speed-limit and paired spans as run 1. Wall time 177.0 s; free memory before 2,419,396 KB physical, 8,771,560 KB virtual. Fails S2 (wrong sign), S3, S4, S5 and S8: H2 DROPPED; runs 7, 8 and 9 not made |
| 3 | H3 gen003_storm_share | (default n=336, k=168), --g6-lags | 0.349 | 1695 | 0.829 | 25.1 of 28.0 | 0.2217 | 0.267 | 0.3807 / 0.3729 | -0.379 | -0.071 | -0.740 (100 symbols) | 0.032, -0.017, -0.033 (max 0.032, under the limit) | 6 of 10 (p 0.636); B -0.813, stale median -0.073 | 2 of 3 (2020 0.115 SR 0.832; 2021 -0.047 SR -0.088; 2022 0.065 SR 0.696) | PSR(0) 0.711, total 0.132, maxDD 0.210, avg net -0.004, funding net 0.0078 (paid), rebalances 573, liquidated False, 75 symbols, lookback 739 h, stage 1 PASS (25 cuts). Same spans as run 1. Wall time 152.9 s; free memory before 2,321,512 KB physical, 8,462,044 KB virtual. Fails S2 (0.349 < 0.6), S4, S5, S6 and S8: H3 DROPPED; runs 10, 11 and 12 not made |

Total sandbox runs made in round 1: 3 (of the 12 planned and the cap of 14); none from the reserve; no stage-1
rejection, no kernel fault, no refusal, nothing on stderr; every run exit 0, full stage 1 (25 truncation cuts), one
at a time, each started only after the one before had ended, 152.9 to 177.0 s each (wall time of run 1: 2 min 48 s).
Before every run the coordinator's memory rule of stage 2 (at least 1,000,000 KB physical and 4,000,000 KB virtual
free) was met. The benchmark line printed by every run (equal-weight long of the in-play members): DEV Sharpe 0.619,
maxDD 0.847, as in generation 2. ledger/sandbox_log.jsonl now has 46 rows (43 + 3), each with status ok, its
logged readings equal to the printed ones and its source_sha256 equal to the committed file's; `omr.ledger verify`
OK, all six chains; `omr.kernel_lock verify` OK, sealed (core 0.05, top30 0.1). Generation 3 has used 3 of 60
sandbox runs.

## Amendments (round 1), stage 2

none: no program text, param, default, screen item or run condition was changed, and the reserve was not used.

## Screen outcome per hypothesis (round 1; stage 2, DEV, read from the run log above)

| H | S1 (PASS; X >= 30; G >= 0.5; L False; H >= 15) | S2 (S >= 0.6, registered sign) | S3 (years + >= 2 of 3) | S4 (G4 DEV > 0) | S5 (G2 DEV > 0) | S6 (next30 DEV > 0) | S7 (r(1..3) each <= 0.40) | S8 (A <= 4 and B > 0) | S9 (placebo < 0.5 S) | S10 (corners) | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| H1 gen003_weekend_share | pass (PASS; 1791; 0.833; False; 25.0) | FAIL (-1.348, wrong sign) | FAIL (0 of 3) | FAIL (-1.756) | FAIL (-2.004) | pass (0.217) | pass (-0.033, -0.049, 0.009) | FAIL (A 8; B -1.740) | not run | not run | DROPPED |
| H2 gen003_heavy_hours | pass (PASS; 1675; 0.833; False; 25.1) | FAIL (-0.256, wrong sign) | FAIL (1 of 3: 2020) | FAIL (-0.705) | FAIL (-1.030) | pass (0.007) | pass (-0.020, -0.003, -0.059) | FAIL (A 9; B -1.200) | not run | not run | DROPPED |
| H3 gen003_storm_share | pass (PASS; 1695; 0.829; False; 25.1) | FAIL (0.349 < 0.6) | pass (2 of 3: 2020, 2022) | FAIL (-0.071) | FAIL (-0.379) | FAIL (-0.740) | pass (0.032, -0.017, -0.033) | FAIL (A 6; B -0.813) | not run | not run | DROPPED |

By the order table a default that fails any of S1 to S8 ends its hypothesis, so no placebo (S9) and no corner (S10)
was run for any of them.

Against each pre-registered DEV falsifier:
- H1: falsified on DEV. The weekend part of the week's residual move did not reverse relative to the weekday part:
  the registered book lost (DEV Sharpe -1.348), in all three DEV years, and also failed both stresses and the paired
  reading. No sign is flipped.
- H2: falsified on DEV. The registered book had the wrong sign (-0.256), small, positive only in 2020; it failed both
  stresses and the paired reading. No sign is flipped.
- H3: falsified on DEV. The sign was the registered one (0.349; 2020 and 2022H1 positive, 2021 slightly negative),
  but below the liveness bar, negative under doubled costs (-0.071) and under the funding stress (-0.379), negative
  on next30 (-0.740), and the paired reading failed (6 of 10 stale copies at least as good; the book's median Sharpe
  on the common names -0.813 over the last 365 days of DEV).

## DEV observations (round 1; NOT hypotheses, never to be submitted from this plan)

- H1 lost by more than one Sharpe unit in every DEV year: in the top30 cross-section of DEV, holding the week's
  residual move fixed, the coins whose move was made more on the weekend did BETTER the following week than those
  whose move was made more on weekdays. That is the opposite of the thin-weekend reversal registered. The plan
  forbids flipping a sign and no mirror was run; a mirror (continuation of the weekend part, or equivalently,
  because the book is orthogonal to the week's move, reversal of the weekday part) would descend from this result,
  and DEV is spent as a screen for it. On next30 the registered book read +0.217, the other sign from top30; one
  reading, not a pattern. WEAK: one DEV period, one default.
- H2 showed nothing usable in either direction: -0.256 with the registered sign, and a mirror would pay the same
  0.229 of costs. Its sign agrees with the direction of LESSONS 17 and 21 (heavy, one-sided activity went with
  continuation on DEV), but the size is small. WEAK.
- H3 had the registered sign but too little size: a rough additive split (compounding ignored) puts its price P&L
  before costs and funding at about 0.36 of equity over DEV (total 0.132 + costs 0.2217 + net funding paid 0.0078),
  less than twice its costs; its next30 reading was negative. WEAK.
- Costs were inside the plan's estimates: 0.172 to 0.229 of equity over DEV (estimate 0.15 to 0.25), 0.206 to 0.274
  per unit of avg gross (estimate 0.19 to 0.29), 573 to 668 rebalances in 912 days. A book whose beta is
  re-estimated every hour but reaches the targets only through a weekly bar paid weekly-book costs (round 1 of
  generation 2: 0.137 to 0.231): the weekly decision bounded the turnover as designed (LESSONS 24 does not apply to
  this construction).
- The 21-day knownness span cost about three names: 25.0 to 25.1 held of 28.0 in play, avg gross 0.83.
- Speed limit: every r(j) was between -0.059 and 0.032, as designed for a ranking re-drawn every week.
- G2 cost these books more than G4 did, on all three: their Sharpe fell by 0.66, 0.77 and 0.73 under the funding
  stress against 0.41, 0.45 and 0.42 under doubled costs. None reads funding, but each paid and received 0.29 to 0.40
  of equity in gross funding over DEV, one and a half to two times the gross flows of generation 2's H1 (row 41:
  0.20 / 0.18), and
  G2 charges half of each (0.29 to 0.40 of equity over DEV). A design yardstick next to rows 40 and 41, not a
  measured cause: for a dollar-neutral top30 book that holds a full book through DEV, G2 is the binding stress.
- Paired readings: all three books lost on the common names over the last 365 days of DEV (B -1.740, -1.200,
  -0.813), so the comparison with their stale copies meant nothing there (S8's second clause).
- WEAK throughout: one DEV period, one default each, one researcher session; nothing here is a parameter
  recommendation.

## Recommendation (round 1)

NONE. By the pre-registered selection rule a hypothesis is eligible only if it passes every screen item S1 to S10.
H1 failed S2, S3, S4, S5 and S8; H2 failed S2, S3, S4, S5 and S8; H3 failed S2, S4, S5, S6 and S8. No program from
version 1 is recommended for a counted submission; no KP-017 or KP-020 measurement is needed for this round. The
DEV-only placebos (gen003_diag_*) were not run and are never to be submitted. Generation 3 stands at 0 of 5 counted
submissions and 3 of 60 sandbox runs; M is unchanged at 6.

---

# Generation 3 - PLAN, version 2 (round 2, pre-registered 2026-11-26 before any round-2 sandbox run)

Researcher session for generation 3, round 2, stage 1 (read, think, pre-register). Unit: top30. A fresh session:
generations 0 to 2 and round 1 are known to it only through the files listed below. The date in the heading is local
time (+08:00); the UTC time is in the last line of this version.

- Kernel: semantic 7d923e7e2375986dc12df4e54c20049bf214d90b49544be64d0665e24e6c3194 (40 files), text
  b74122f3f9821056bbb5217ece9526d7068207d61f5941f47f5118c16fcd5209 (39 files) (`python -m omr.status`: kernel OK
  d09812fdec752a17, sealed). Sealed G6 thresholds: core 0.05, top30 0.10. Data research_hash 28d9084a8c5c7659...,
  validated, snapshot_end 2026-11-18 10:00 UTC.
- Ledger when this was written: M = 6 counted trials (generation 0: 4, generation 1: 1, generation 2: 1), N 5.90, rho
  0.021, Tier 1: 0, pool 0 of 5, last census none, one uncounted stage-1 rejection (generation 0). `omr.ledger verify`
  OK, all six chains (trials 12 rows, stage1_log 1, kernel_history 12, calibration_log 6, sandbox_log 46,
  val_access_log 29); `omr.kernel_lock verify` OK (sealed, core 0.05, top30 0.1). Generation 3: 0 of 5 counted, 3 of
  60 sandbox runs (round 1).
- Read, in this order: RESEARCH_PLAYBOOK.md (all; sections 3, 4, 4b and 5 with care); LESSONS.md (all 43); STATE.md
  (all, with "Where things stand" and "Open decisions for the human"); this file's version 1 with the coordinator's
  rulings and its stage-2 parts, and generations/gen003/REPORT.md; generations/gen002/REPORT.md (all four rounds, the
  counted trial and the closing note); generations/gen002/PLAN.md version 2 in full (H5 to H7: screen, rulings, run
  log, screen outcome, observations, recommendation) and the coordinator's decision before the counted run; version 1
  in full; of version 3 its disclosures and screen; of version 4 its first part (to its screen and the head of H11) and
  its run log, screen outcome, observations and recommendation; LANGUAGE.md (all; sections 3, 6, 7 and 10 with care);
  CONSTITUTION.md sections 4 to 7 and 13; rows 43 to 45 of ledger/sandbox_log.jsonl (0-indexed; file lines 44 to 46)
  in full; `python -m omr.status`, `python -m omr.ledger summary` (trial rows only), `omr.ledger verify`,
  `omr.kernel_lock verify`.
- Kernel source read only to learn how the tool behaves: omr/lang.py (the Program fields, parse and parse_file, the
  window and param rules, the tf_last / tf_mean checks, lookback_hours), omr/sandbox.py (what a top30 run prints and
  logs), omr/upipeline.py (dev_speed_limit, dev_names_held and dev_paired_lags only: the rows and lags each reading
  uses, and when the paired reading is refused). Program shapes: strategies/gen003_storm_share.omr,
  gen003_diag_midweek_share.omr, gen002_resid_momentum.omr, gen002_resid_skew.omr; omr/programs/ucal_xs_momentum.omr
  and kernel_kitchen_sink_tf.omr. Code, not data or results.
- Not opened: anything under data/, ledger/returns/, ledger/trials/, _build/, audits/, every calibration file, and
  KERNEL_PROPOSALS.md. Rows 40 and 41 of the sandbox log are known to this session only through version 1's table.
  No VAL number exists for any program below. No round-2 sandbox run has been made and no project program was run on
  data: the only program run was a parse-only check (omr.lang.parse_file, whose constant probe runs on the kernel's
  synthetic probe panel) from a script in the session scratch folder (gen003_r2/parse_check.py; the files were written
  by gen003_r2/write_programs.py, ASCII with LF).
- Files of this version: this version 2, appended, and six new program files (three candidates, three DEV-only
  controls). Everything before this version (62,735 bytes, sha256 55701bdfea0e84fd...) is unchanged; no earlier
  program file was changed.

Three hypotheses, numbered on from version 1. All three are CONTINUATION rules written after DEV results, under the
coordinator's frame for this round; none is a new mechanism. All are dollar neutral (cs_demean; gross 1 by cs_scale),
all change their weights once a WEEK (every input reaches the targets only through `tf_mean(., weekly)` or
`tf_last(., weekly)`), and none reads funding8h, funding_mean, mark_close or index_close.

| H | program | the move whose continuation is claimed | formation; holding | descends from | family |
|---|---|---|---|---|---|
| H4 | gen003_multiweek_momentum | the coin's residual move of the last m = 3 weeks, in units of its residual volatility | 3 weeks (G5: 2 or 4); 1 week | LESSONS 16 and 23 (with 26 and 43) | relative |
| H5 | gen003_jump_continuation | the uncentred skewness of the coin's last 21 daily residual returns: recent up-jumps against recent crash days | 21 days (G5: 17 to 25); 1 week | LESSONS 21 | other |
| H6 | gen003_week_continuation | the coin's residual move of the last week, in units of the week's residual volatility (round 1's x) | 1 week; 1 week | LESSONS 16 | relative |

H4 and H6 are ONE mechanism (gradual absorption of coin-specific news) at two horizons: they get one set of
diagnostics between them, and at most one of them can be recommended. H5 is a second channel (attention after extreme
days). Not in this round, as the frame says: the mirrors of round 1's H1 and H2 (continuation of the weekend part or of
the heavy-hour part of a week's move). None of the three is a composition of the week's move (round 1's construction):
H6 trades round 1's x itself, and H4 and H5 rank whole moves.

## What I read and had seen before writing (numbers known to this session)

- Every DEV number of generation 2 (KP-015 kernel, unit top30, defaults unless stated; costs = equity over DEV; years
  + of 2020, 2021, 2022H1), as tabled in version 1, and the per-year rows of the four rules this version descends
  from or leans on (generations/gen002/PLAN.md, run logs of versions 1 and 2):

  | round, program | DEV Sharpe | costs | funding paid (minus = received) | per year: return (Sharpe) 2020; 2021; 2022H1 | other |
  |---|---|---|---|---|---|
  | 1 H1 resid_reversal (1-week residual, reversal sign) | -1.566 | 0.1369 | 0.0212 | -0.514 (-4.046); -0.208 (-0.638); -0.074 (-0.493) | avg gross 0.866, 2849 dir. changes, 921 rebalances |
  | 1 H4 absorbed_flow | -1.251 | 0.1649 | 0.0145 | -0.026 (-0.150); -0.361 (-1.830); -0.142 (-1.478) | |
  | 2 H5 resid_skew (21-day residual skew, lottery sign) | -1.906 | 0.1404 | 0.0057 | -0.376 (-2.528); -0.481 (-2.133); -0.168 (-0.989) | avg gross 0.823, 2645 dir. changes, 1152 rebalances |
  | 2 H7 prior_month_reversal (weeks 8 to 4 back) | 0.381 | 0.1772 | 0.0117 | -0.099 (-0.647); 0.044 (0.292); 0.238 (2.172) | |
  | 2 H6 resid_momentum (4 weeks, BTC beta, daily) | 0.945 | 0.3299 | -0.0764 | 0.682 (3.217); 0.281 (0.976); -0.237 (-2.221) | neighbours m=3 0.955, m=5 0.923, n=24 1.039, n=36 1.069; each lost 2022H1 (Sharpe -1.84 to -2.70); costs 0.313 to 0.380; received 0.074 to 0.094 |

  The other generation-2 rows (version 1's table): H2 activity_fade 0.172, H3 small_tickets -0.211, H8 premium_shock
  0.823, H9 funding_shock 1.197, H10 unrewarded_premium 0.980, H11 averaged_funding_shock 1.492 (corners 1.286 /
  1.805, stale copy 0.032, twin 1.466), H12 averaged_unrewarded_shift 0.731 (0.8 corner 0.249). Every run printed the
  benchmark (equal-weight long of the in-play members) at DEV Sharpe 0.619, maxDD 0.847.
- Round 1 of this generation (rows 43 to 45, read in full, and version 1's run log): H1 weekend_share -1.348 (costs
  0.1720; funding paid / received 0.2911 / 0.2916; G2 -2.004; G4 -1.756; next30 0.217; r(1..3) -0.033, -0.049, 0.009;
  paired 8 of 10, B -1.740; names held 25.0 of 28.0; years + 0 of 3, 2022H1 Sharpe -2.468); H2 heavy_hours -0.256
  (0.2286; 0.3908 / 0.3992; G2 -1.030; G4 -0.705; next30 0.007; paired 9 of 10, B -1.200); H3 storm_share 0.349
  (0.2217; 0.3807 / 0.3729; G2 -0.379; G4 -0.071; next30 -0.740; paired 6 of 10, B -0.813). Lookback 739 h each; 573
  to 668 rebalances. Speed-limit rows from 2020-08-10 14:00; paired lags 30 to 262 days, decisions 2021-06-30 23:00 to
  2022-06-30 22:00.
- The KP-018 readings of rows 40 and 41 (version 1's table): gen002_averaged_funding_shock 1.492 (G2 0.735, G4 1.165,
  next30 0.637, funding paid / received 0.388 / 0.544); gen002_resid_reversal -1.566 (G2 -2.179, G4 -2.022, next30
  -1.030, funding 0.198 / 0.177, r(1..3) about 0, paired 1 of 10 with B -0.066 and stale median -0.544, names held
  27.9 of 28.0). Row 41 is the weekly residual REVERSAL, so its next30 reading (-1.030) says that a one-week residual
  continuation book would very likely read positive on next30 too: it is known for H6 and bears on H4.
- The aggregate VAL rows in `omr.ledger summary` (six trials; VAL Sharpe -0.531, -0.770, 0.384, -0.323, 0.830 and
  -0.249; none Tier 1), generation 2's counted trial in full as reported (G1, G2, G4, G5, G6, G7 failed; G6 p 0.571),
  and STATE.md's BTC/ETH benchmark over VAL (0.921).

## The frame of this round, and how this plan answers it

The coordinator's frame: fifteen pre-registered market-neutral top30 ideas failed their DEV screens; every bet against
a recent move lost or earned too little and the DEV-positive price books all continue a recent move (LESSONS 16, 17,
21, 23, 26, 39, 43); no counted trial has ever been spent on that pattern because each continuation rule was written
after a DEV result. This round may pre-register such rules on five conditions, answered for each hypothesis in its own
section and summarised here:

- (a) Each rule says it descends from DEV results and lists the DEV numbers that shaped it (each hypothesis, item a).
- (b) Each gives a reason beyond those numbers: the mechanism, who is on the other side and why it would persist after
  mid-2022, and what I recall from outside this project, for and against, with how sure I am (section "Outside
  evidence" and each hypothesis, item b).
- (c) Each is built with the weekly tools, and its costs and funding flows are estimated against LESSONS 19, 24, 41
  and 42 (section "What a top30 idea must clear" and item c).
- (d) The DEV screen is fixed now, uses the kernel's readings as drop conditions, and states for each rule which
  readings are already predictable from known numbers (and so are not evidence even when passed) and how the known
  weak spot (2022H1 for multi-week residual momentum, LESSONS 23) is treated: by NO special item, neither stricter nor
  looser (section "DEV screen" and item d).
- (e) At most two programs can be recommended (at most one of H4 and H6); for each, what a VAL pass and a VAL failure
  would teach (item e).

What this plan does NOT do. It registers no rule built to avoid 2022H1 (no crash filter, no market-state switch, no
skip of the latest days, no cap on single coins, no blend with the reversal of the month before last, LESSONS 22),
because each would be shaped on a known DEV number. It registers no new mechanism (the frame allowed one): the
candidates I could build (liquidity shocks, a session clientele, nearness to a recent high, a capital-gains overhang)
are either compositions or continuation proxies close to H4, or have no clear sign; a weak extra idea would spend a
DEV draw and runs for little (notes, (c)).

## What a top30 idea must clear (playbook 4b, LANGUAGE.md 10, CONSTITUTION 13), and how these programs meet it

- Costs (12.5 bps per side). Weekly rank books paid 0.137 to 0.231 of equity over DEV (LESSONS 19); round 1's weekly
  books built from hourly residuals through tf_mean paid 0.172 to 0.229 (C/G 0.21 to 0.27; LESSONS 41), although their
  beta is re-estimated every hour: the weekly bar bounds the turnover. LESSONS 24 (a daily-updated beta multiplying a
  multi-week return made generation 2's H6 cost 0.31 to 0.38) does not apply here: in H4 and H6 the beta reaches the
  targets only through weekly bins, and in H5 the daily residual moments reach them only through a weekly sample. A
  book's costs are about (a) the change of the rank targets from week to week, plus (b) the drift traded back between
  weekly decisions and (c) names entering, leaving or dropping out of play. For a ranking re-drawn independently every
  week (H6, as round 1's books) (a) is about 4/3 of gross per week; for a formation window that shares a share s of
  its data with last week's, (a) falls to about sqrt(1 - s) of that, while (b) and (c) stay. Estimates (equity over
  DEV; C/G in brackets; not computed on any data):
  - H6: as round 1's books, 0.17 to 0.23 (0.21 to 0.27). Under G4: 0.34 to 0.46.
  - H4 (3 weekly bins, 2 of 3 shared: (a) about 0.58 of H6's): 0.12 to 0.18 (0.15 to 0.22). Under G4: 0.24 to 0.36.
  - H5: generation 2's daily form cost 0.1404 (its 21-day skew moves mostly when a large day enters or leaves the
    window); a weekly sample of the same path cannot have a larger total variation of the targets than the daily path
    (the weekly change is the sum of the week's daily changes), so 0.09 to 0.15 (0.11 to 0.18). Under G4: 0.18 to 0.30.
- Funding stress (G2). None of the books reads funding, but each holds a full dollar-neutral book and pays and receives
  funding on it: round 1's books paid and received 0.29 to 0.40 of equity each over DEV, rows 40 and 41 0.18 to 0.54.
  G2 charges half of the gross paid plus half of the gross received, which cost those books 0.61 to 0.77 Sharpe units on
  DEV against 0.33 to 0.46 for G4 (LESSONS 42). Expect the same here: G2 is the binding stress, and a DEV Sharpe of
  about 0.8 is needed before either stress for S5. Net funding: on DEV recent losers carried higher funding (LESSONS
  27), so continuation books RECEIVED funding (generation 2's H6: 0.074 to 0.094 of equity) and part of their DEV
  Sharpe is funding that G2 halves; expected net receipt H4 0.03 to 0.09, H6 about 0.02 (the mirror of H1's 0.0212
  paid), H5 about 0.006 (the mirror of 0.0057). A book that pays or receives funding without reading it is not
  funding-driven (ruling of 2026-11-23, generation 2 round 2, (2)).
- What the parents suggest (NOT evidence: stated only so that the coordinator can see which items are likely to bind):
  removing the parents' costs and funding from their DEV Sharpe and charging the estimates above gives, very roughly,
  H4 about 1.0 to 1.4, H5 about 1.1 to 1.6 (of which an unknown part is drift, S9), H6 about 0.7 to 1.1, so that S5
  (G2) may bind for H6 and could for H4, and S3 and S8 may bind for H4 (2022H1). These are guesses from other
  constructions; the screen below does not use them.
- Timing (G6) and the speed limit. G6 compares the book with its own weights 30 days to about 18 months earlier. The
  claim of each book is about the last one to three weeks. H6's stale copies hold weekly moves at least four weeks old;
  H4's first stale copy (30 days) holds the formation of weeks 7.3 to 4.3 back, which on generation 2's H7 (LESSONS 22)
  tended to reverse on DEV, and later copies are close to independent; H5's copies hold the skewness of 21-day windows
  that ended at least 30 days earlier, which share no day with the current window. A lasting per-coin tilt (a coin
  that is ALWAYS a residual winner, BTC against the unit's mean in a period of rising BTC dominance) is held by the
  copies too and earns no timing credit, and the speed-limit statistic removes each name's mean. One lag step is 621
  hours: H6's and H4's formation windows (168 and 504 hours at the defaults, 672 at H4's m = 4 corner) and H5's 21-day
  window (504 hours) do not overlap with their own windows one step earlier, except H4 at m = 4 (51 hours); only the
  beta windows reach further back, a second-order effect. Expected r(1..3) near 0, perhaps slightly negative (S7 reads
  them).
- Lookback (limit 2,160 hours; every window param at its high bound; parse check): H4 1,243 h (405 for the hourly beta,
  + 334 for the weekly bin, + 504 for three more bins at m = 4); H5 1,605 h (daily log return 71, + 600 for the beta,
  + 600 for the moments, + 334 for the weekly sample); H6 739 h (round 1's).
- Cross-sections and knownness. A cs_* needs at least 10 in-play names with a known input, else it is unknown for
  every name (the unit holds about 28 in play). The beta of H4 and H6 uses cs_mean of the hourly returns INSIDE its
  window, so a coin is known only after it has been in play on every hour of the beta window and of the bins: about
  14 days + 1 week (H6)
  or + 3 weeks (H4) at the defaults. H5 chains a 21-day daily beta into 21-day moments and a weekly sample: about 6 to
  7 weeks (generation 2's H5 held avg gross 0.823); a daily bar needs every hour of its day known, so one unusable hour
  removes a day from both windows. A name with one unusable hour or one stale funding settlement drops out for as long
  as its windows span, and a market-wide unknown hour would flatten the book for as long. Named in advance; S1's
  names-held reading shows it (round 1: 25 of 28 for a 21-day span). G6 does not credit recent entrants either.
- G8 runs the rule on ranks 31 to 60: residuals, volatility ratios, skewness and ranks mean the same there.
- G7: with the unit's seasoning and these warm-ups 2020 is a short bucket (H5 shortest); in effect four of the five
  later buckets must be positive.
- Literals and G5: no program has a jitterable literal (n_literals 0). H4 has n (integer; G5 values 269 to 403) and m
  (integer: 3 x U(0.8, 1.2) rounds to 2, 3 or 4 and an unchanged 3 moves by 1, so every G5 variant has m = 2 or 4); H5
  has n (21; G5 17 to 25); H6 has n (as H4). The DEV corners (S10) are the corners at which every param sits at the
  same G5 end: H4 (269, 2) and (403, 4); H5 n = 17 and 25; H6 n = 269 and 403. Mixed corners are not read.
- Funding and basis: no program reads funding8h, funding_mean, mark_close or index_close, so the KP-017 restriction of
  playbook 4b does not apply. KP-020 applies as to every top30 program: a Tier-1 result is measured per program in null
  worlds before it enters the pool. These books are built to be cheap to trade, the case the unit's 3% bound has not
  measured (LESSONS 38).
- Calendar: no program uses hour or weekday.

## Disclosures that apply to every hypothesis

- The author model has read this market's history through DEV, VAL and the vault, and this session has read every DEV
  number listed above and the aggregate VAL rows. No rule names a date, a coin, a price level or a remembered event;
  every tunable number is a declared param. That does not remove hindsight from the CHOICE of ideas (KP-010), which is
  sharper this round than in any earlier one: all three rules were chosen BECAUSE DEV showed continuation. Their DEV
  numbers are therefore not evidence for them, and only a counted VAL run can test them.
- What I remember about VAL (July 2022 to June 2025) that touches a continuation book: BTC's share of crypto market
  value rose through most of VAL and most altcoins lagged it (a residual-momentum book would often hold BTC long
  against the unit's mean: a persistent tilt, which G6's stale copies share); runs that lasted weeks (SOL through
  2023, memecoin waves in spring 2023 and from late 2023 into 2024, AI tokens early in 2024); FTT's collapse over
  several days in November 2022; on the other side, my impression that altcoin rotations in 2024 and 2025 were short
  and choppy, and that many tokens with large unlocks fell steadily. These memories lean toward continuation, a bias I
  name; I do not remember the VAL result of any cross-sectional momentum, skewness or MAX book, in crypto or elsewhere.
- What I remember about DEV (2020 to June 2022): DeFi tokens in summer 2020; the 2021 runs of SOL, AVAX, LUNA, FTM and
  of gaming and metaverse coins late in 2021, each over weeks; the crash of 19 May 2021; the sell-off from November
  2021 into January 2022; LUNA rising into April 2022 and collapsing in May 2022 (a residual winner going to zero
  inside one week, which is consistent with generation 2's H6 losing 2022H1; it did not shape any rule here: there is
  no crash filter and no single-coin cap); Celsius and Three Arrows in June 2022.
- At most TWO programs are recommended for a counted submission whatever DEV says (selection rule). LESSONS 12, 14, 37
  and 38: a true Sharpe-1.5 book passes Tier 1 only 68 to 82% of the time in this unit, G6 tests timing and not luck,
  and every counted trial raises M forever.
- Defaults are fixed now and never changed after a run. Corners are a robustness check (the G5 ends), not a search; a
  better corner does not move the default. No sign is ever flipped: a negative DEV Sharpe drops a hypothesis.

## Outside evidence on cross-sectional continuation (recalled without network; for and against; how sure)

For continuation:
- Liu, Tsyvinski and Wu, "Common Risk Factors in Cryptocurrency" (Journal of Finance, 2022): cross-sectional momentum
  in a broad coin universe (well over a thousand coins above a small size floor, about 2014 to 2018) at formation
  windows of one to four weeks with one-week holding; a crypto factor model with market, size and momentum. Sure of
  the paper and of momentum at one to four weeks (about 75%); I believe their momentum factor sorts on about three
  weeks of past returns (about 55%). Weakness for this project: a broad, small-coin universe before 2019, not large
  perps after 2022.
- Liu and Tsyvinski, "Risks and Returns of Cryptocurrency" (Review of Financial Studies, 2021): strong time-series
  momentum of the aggregate crypto market at one to several weeks and a role for investor attention (about 75%).
  Time-series, not cross-sectional.
- Zaremba, Bilgin, Long, Mercik and Szczygielski (International Review of Financial Analysis, about 2021), on
  short-term reversal and momentum in crypto: short-term reversal concentrated in small, illiquid coins and
  continuation among the large, liquid ones (about 50% on the large-coin detail). If right, it favours continuation in
  a top30.
- Tzouvanas, Kizys and Tsend-Ayush (Economics Letters, 2020): short-term momentum in major cryptocurrencies at weekly
  horizons (about 45%). Dobrynskaya, "Cryptocurrency momentum and reversal" (about 2021 to 2023): momentum up to two to
  four weeks and reversal after about a month (about 45%; it agrees in shape with generation 2's H6 and H7 on DEV,
  which is why I name it and do not lean on it).
- Li, Urquhart, Wang and Zhang, "MAX momentum in cryptocurrency markets" (International Review of Financial Analysis,
  about 2021): coins with high maximum daily returns kept outperforming, the opposite of the equity MAX effect (about
  60% on the direction). For H5.
- Other markets (sure unless stated): momentum in US stocks (Jegadeesh and Titman 1993) and across asset classes
  (Asness, Moskowitz and Pedersen 2013); time-series momentum (Moskowitz, Ooi and Pedersen 2012); currency momentum
  (Menkhoff, Sarno, Schmeling and Schrimpf 2012); industry momentum, including at one month (Moskowitz and Grinblatt
  1999; about 75%); residual momentum with about half the volatility of total momentum and fewer crashes (Blitz, Huij
  and Martens 2011; Gutierrez and Pirinsky 2007; about 85%); stronger continuation when information arrives gradually
  (Da, Gurun and Warachka 2014, about 80%); left-tail momentum, stocks with large recent losses keep losing (Atilgan,
  Bali, Demirtas and Gunaydin 2020; about 60%; for H5's short side). Theory: gradual diffusion of news (Hong and Stein
  1999), the disposition effect as a source of underreaction (Grinblatt and Han 2005), attention-driven buying (Barber
  and Odean 2008).

Against continuation:
- Grobys and Sapkota, "Cryptocurrencies and momentum" (Economics Letters, 2019): no significant cross-sectional
  momentum among about 140 coins, 2014 to 2018, at monthly horizons (about 60%).
- Short-term reversal: in stocks at one week to one month (Jegadeesh 1990; Lehmann 1990; sure); in crypto at daily
  horizons in many studies (about 65%), and in this project round 1's H3 read a small reversal of the storm-hour part.
- Momentum crashes in sharp rebounds after market declines (Daniel and Moskowitz 2016; Grundy and Martin 2001; sure).
  Crypto has many such rebounds and sector reversals.
- Decay after publication (McLean and Pontiff 2016: anomaly returns about a quarter lower out of sample and about half
  lower after publication; about 85%). The crypto momentum papers circulated from about 2018 to 2020, so VAL lies after
  them, in a market with more professional market makers and quantitative funds than in 2020 and 2021.
- For H5: the equity MAX and skewness effects have the opposite sign (Bali, Cakici and Whitelaw 2011; Barberis and
  Huang 2008; Boyer, Mitton and Vorkink 2010; Amaya, Christoffersen, Jacobs and Vasquez 2015, weekly realised skewness
  predicting negatively; sure for the first and second, about 75% for the others), and I recall a crypto paper on
  lottery-like demand (Grobys and Junttila, about 2021) whose sign I do not remember reliably (about 40% that it was
  the equity sign).
- The instrument: in this unit's no-skill worlds the calibration's momentum family loses to its costs (LESSONS 13).
  That is about null worlds, not about markets, but it says that a continuation book with no edge here dies of costs.

How sure overall: the outside support for cross-sectional crypto continuation at one to four weeks is real but comes
from broad universes before 2020; for the largest perps after mid-2022 I recall no published result in either
direction. My prior that H4's claim holds in VAL net of these costs is modest, well under even odds; for H5 lower; for
H6 lower again, because of its costs.

---

## H4. gen003_multiweek_momentum

- Family relative. Kind portfolio. Unit top30. Dollar neutral, gross 1. A weekly series (bins from Monday 00:00 UTC,
  visible at the bar that opens Sunday 23:00, traded at the Monday 00:00 open).
- Rule: for each coin in play, e = its hourly return net of its rolling 14-day hourly beta to the unit's mean (round
  1's e); z = the mean of e over the last m = 3 complete weekly bins divided by the root mean square of e over the same
  bins (the coin's 3-week residual return in units of its residual volatility; up to the factor sqrt(504), common to
  every coin, a t-statistic). Weight: + the cross-sectional rank of z, demeaned, scaled to gross 1. Long the coins with
  the largest residual move of the last three weeks for their volatility, short the smallest.
- Program (default pre-registered; strategies/gen003_multiweek_momentum.omr):

      n = param(336, 268, 404)       # hours in the rolling hourly beta to the unit's mean return (14 days)
      m = param(3, 2, 4)             # weekly bins in the formation window (3 weeks)
      r = ret(close, 1)
      mk = cs_mean(r)
      e = r - corr(r, mk, n) * std(r, n) / std(mk, n) * mk
      z = sma(tf_mean(e, weekly), m) / sqrt(sma(tf_mean(e * e, weekly), m))
      signal = cs_scale(cs_demean(cs_rank(z)))

  2 params (integers; G5 values n = 269 to 403 and m = 2 or 4), 0 jitterable literals, 33 nodes, lookback 1,243 h.
  Parse check OK; canonical sha256 9797096e40cdea4e...; file sha256 41d9ff30219bbba0....
- Hypothesis: a coin's residual move of the last three weeks, in units of its residual volatility, continues over the
  following week.
- Mechanism: gradual absorption of coin-specific news. News about an altcoin (a product, a listing, a partnership, a
  sector narrative, an unlock, a hack) reaches a fragmented clientele (regional and social-media communities, retail on
  several venues, funds that cover few coins) over days to weeks; capital rotates into a narrative in stages (from the
  largest coins to the next tier); trend-following funds and retail bots add with a lag; holders sell winners too early
  and keep losers too long (the disposition effect), which slows adjustment both ways. Prices therefore adjust in
  steps, and the part of the move still to come is what the book collects (Hong and Stein 1999; Grinblatt and Han
  2005). Why the residual: a market move is not news about one coin, and the beta part of total momentum is what
  crashes when the market turns (Grundy and Martin 2001; Daniel and Moskowitz 2016); residual momentum is the steadier
  form in equities (Blitz, Huij and Martens 2011). Why the unit's mean and not BTC: BTC is a member, and the unit's
  mean is the altcoin market the coins move with. Why scaled by residual volatility: the rank then reads how unusual
  the move was for that coin, so the extremes are not simply the most volatile coins.
- Other side, and why it can persist after mid-2022: liquidity providers and market makers who lean against moves;
  early profit-takers in winners and dip-buyers in losers; project treasuries and early investors selling into
  strength. The clientele that makes adjustment slow (retail, attention-driven, leveraged, spread over venues and
  languages) is structural in altcoin perps and was still dominant after 2022; arbitrage capital is limited by
  momentum's crash risk and by squeeze and funding risk when shorting. Why it might not persist: a market with more
  professional market makers and quantitative funds after 2021, and publication (outside evidence, against).
- (a) Written AFTER DEV results; the DEV numbers that shaped it: the sign, from LESSONS 16 (generation 2's weekly
  residual reversal, DEV Sharpe -1.566, negative in all three years) and LESSONS 23 (generation 2's 4-week residual
  momentum, 0.945 at its default and 0.923 to 1.069 at four neighbours); the construction, from LESSONS 24 (H6's costs
  of 0.31 to 0.38 with a daily-updated beta), 41 (weekly bins from hourly residuals cost like weekly books) and 42 (G2
  binds: a formation that shares data from week to week is cheaper than a one-week ranking); the cap of the formation
  at four weeks, partly from LESSONS 22 (generation 2's H7: the residual of weeks 8 to 4 back reversed a little on DEV,
  0.381); and round 1's e (its cost and names-held readings). NOT shaped by the 2022H1 losses of generation 2's H6: no
  crash filter, no state switch, no skipped days, no exclusion.
- (b) Reason beyond those numbers: the mechanism above and the outside evidence (for: Liu, Tsyvinski and Wu at one to
  four weeks; Zaremba and co-authors for large coins; residual and cross-asset momentum; against: Grobys and Sapkota,
  short-term reversal, crashes, decay after publication). m = 3 is the middle of the one-to-four-week range of the
  crypto evidence, and G5's variants (2 and 4) stay inside it; n = 14 days is round 1's value.
- (c) Costs and funding: weekly targets, three overlapping bins: 0.12 to 0.18 of equity over DEV (C/G 0.15 to 0.22),
  0.24 to 0.36 under G4; gross funding paid and received 0.25 to 0.40 each, net received 0.03 to 0.09; G2 should cost
  0.6 to 0.8 Sharpe units on DEV. LESSONS 24's cost driver is absent by construction.
- (d) Known weak on DEV: every setting of generation 2's H6 lost in 2022H1 (Sharpe -1.84 to -2.70), and H4 will very
  likely lose 2022H1 too. The screen treats it with the items every top30 idea has had, unchanged: S3 (two of three
  years; its outcome for H4 is predictable, 2020 and 2021 positive, and it is NOT evidence) and S8 (A <= 4 and B > 0
  over the last 365 days of DEV, half of which is the known weak half-year: S8 may drop H4 for that reason and is kept
  as it was). It is not tightened to H6's three of three (that outcome is known: it would stop H4 for a reason LESSONS
  23 already records, and the round would learn nothing); it is not loosened (no item is dropped or relaxed because of
  2022H1). Readings nobody has seen for this rule: its costs and names held (S1, S4, S5), next30 for a multi-week
  residual continuation book (S6; row 41 bears on it), the speed limit (S7), the paired comparison A (S8), the plain
  control (S9) and the corners in this construction (S10; H6's neighbours suggest positive).
- Relation to LESSONS 23 ("a screen it failed is not reopened by registering it again"): generation 2's H6 stays not
  eligible, and nothing of its outcome changes. H4 is a different program (the unit's mean instead of BTC; a rolling
  14-day hourly beta instead of a 30-day daily one updated every day; a formation built from weekly bins of hourly
  residuals instead of the weekly close; the residual's own root mean square instead of a 30-day daily volatility;
  m = 3 with G5 at 2 and 4 instead of m = 4; targets once a week instead of on the hourly grid), registered under this
  round's frame with the common screen. But it is the same IDEA (residual momentum over about a month), and its DEV
  numbers will be close to H6's. Open question 1 asks the coordinator to rule before run 1.
- (e) What a VAL pass would teach: residual continuation at two to four weeks survived out of sample in the top30,
  after costs and both stresses, with timing credit over its own stale copies, robust to G5's m = 2 and 4, and on
  next30 too: the first out-of-sample evidence for the one pattern DEV kept showing, and the first Tier-1 candidate,
  subject to the KP-020 measurement in null worlds before the pool. What a VAL failure would teach: the canonical form
  of the DEV pattern did not carry into VAL. The gates say how: a VAL Sharpe at or below zero, or G6 failed, means the
  DEV continuation was a feature of 2020 to mid-2022 or a tilt, and the project should build no further price
  continuation variants in this unit without new information (a new input or a new mechanism); G1 failed with a VAL
  Sharpe of about 0.5 to 0.9 and every other gate passed is not conclusive (LESSONS 12: power); G2 alone points to
  the funding environment; G8 alone to the universe.
- What I remember that could bias it: the VAL and DEV memories listed in the disclosures (BTC's rising share as a
  tilt; multi-week runs in both periods; LUNA's collapse in May 2022). Nothing I remember gives the VAL result of a
  residual momentum book.
- Falsifier. DEV (not submitted): S1 to S10 (a negative DEV Sharpe drops it, never flipped). Counted (VAL): falsified
  if G1 (PSR(0) < 0.90), G2 (funding-stress Sharpe <= 0), G4 (2x costs <= 0), G5, G6 (p > 0.10, or the speed limit),
  G7, G8 (next30 Sharpe <= 0) or G10 fails: any Tier-1 gate. Named risks: a momentum crash in a sharp rebound or sector
  reversal; a residual winner collapsing on the long side; G2; G7.
- DEV exploration (at most 4 runs): the default with --g6-lags (run 1); if it passes S1 to S8, the control
  gen003_diag_plain_multiweek (run 4), then the corners (n, m) = (269, 2) and (403, 4) (runs 5 and 6).

## H5. gen003_jump_continuation

- Family other. Kind portfolio. Unit top30. Dollar neutral, gross 1. A weekly series: the daily skewness is sampled at
  the last hour of each weekly bin (the Sunday daily close, visible at the bar that opens Sunday 23:00, traded at the
  Monday 00:00 open).
- Rule: generation 2's H5 (strategies/gen002_resid_skew.omr) with the sign reversed and a weekly sample, nothing else
  changed: for each coin in play, r = the daily log return; mk = the unit's mean of r; beta = the coin's beta to mk over
  the last n daily rows; e = r - beta x mk, each row with its own trailing beta; skew = sma(e^3, n) / sma(e^2, n)^1.5,
  the uncentred realised skewness of e over the last n = 21 daily rows. Weight: + the cross-sectional rank of the
  weekly sample of skew, demeaned, scaled to gross 1. Long the coins whose recent residual days were most right-skewed
  (up-jumps), short the most left-skewed (crash days).
- Program (default pre-registered; strategies/gen003_jump_continuation.omr):

      n = param(21, 16, 26)          # daily rows for the beta and for the skewness (3 weeks)
      d = daily(close)
      r = logret(d, 1)
      mk = cs_mean(r)
      beta = corr(r, mk, n) * std(r, n) / std(mk, n)
      e = r - beta * mk
      m2 = sma(e * e, n)
      m3 = sma(e * e * e, n)
      skew = tf_last(m3 / (m2 * sqrt(m2)), weekly)
      signal = cs_scale(cs_demean(cs_rank(skew)))

  1 param (integer; G5 values 17 to 25), 0 jitterable literals, 42 nodes, lookback 1,605 h. Parse check OK; canonical
  sha256 a2df80abd8ffaaa2...; file sha256 9438e3184a5256d3....
- Hypothesis: coins whose last three weeks of daily residual returns were right-skewed outperform the rest of the unit
  over the following week, and coins whose residual days were left-skewed underperform.
- Mechanism: attention after extreme days, and slow unfolding of the news behind them. A large up-day (a listing, a
  partnership, a viral story) draws attention; attention-driven traders buy what catches their eye (Barber and Odean
  2008), and in crypto they arrive over days and weeks, through social media, exchange promotions and listings on more
  venues, many of them leveraged longs. A crash day often marks bad news whose consequences unfold over weeks (a hack,
  an insolvency, a delisting, a large holder leaving), and holders are slow to sell (the disposition effect): left-tail
  momentum. The skewness is uncentred: it is about the centred skewness plus 3 times the residual drift (mean over root
  mean square) of the same days, so part of H5 is residual momentum over 21 days. S9 (the drift control) asks that the
  jump part add something on DEV; otherwise H5 is momentum in another form and H4 already tests that.
- Other side, and why it can persist: lottery-averse contrarians and short sellers who fade a jump (the equity MAX
  logic: overpriced lottery coins should lag); dip-buyers on crash days. Attention cascades and leveraged chasing are
  structural in crypto retail and were stronger, not weaker, in the memecoin waves after 2022; shorting a coin after a
  pump is costly (squeezes, funding spikes), a limit to arbitrage.
- (a) Written AFTER generation 2's H5 result; the DEV numbers that shaped it: LESSONS 21 (DEV Sharpe -1.906 for the
  lottery sign, negative in all three years: Sharpe -2.53, -2.13 and -0.99), H5's costs (0.1404), avg gross (0.823)
  and funding (0.0057 paid), and LESSONS 41 (the weekly sample). Its form is H5's exactly (same residual, n = 21 with
  range 16 to 26, the uncentred skewness): only the sign and the weekly sample differ, so nothing was tuned.
- (b) Reason beyond those numbers: the mechanism above; for: MAX momentum in crypto (Li, Urquhart, Wang and Zhang),
  left-tail momentum in stocks for the short side, and continuation among large coins (Zaremba and co-authors); against:
  the equity MAX and skewness effects (opposite sign), a crypto lottery paper whose sign I do not remember reliably,
  and memecoin pumps that collapsed within weeks. My support for H5 is weaker than for H4 (one crypto paper against a
  large equity literature).
- (c) Costs and funding: 0.09 to 0.15 of equity over DEV (C/G 0.11 to 0.18), 0.18 to 0.30 under G4; gross funding
  0.25 to 0.40 each, net near zero; G2 should cost 0.6 to 0.8 Sharpe units on DEV.
- (d) Known weak on DEV: nothing in the per-year rows (the parent lost in every year, so S3 is predictable and not
  evidence; S2 too). The known risk is that the parent's DEV result was largely residual drift, answered by S9, which
  nobody has run. Also known: the parent's long knownness span (avg gross 0.823), read by S1. Unseen: next30 for any
  skewness book (S6), the speed limit (S7), the paired comparison (S8), the drift control (S9), the corners (S10) and
  the costs of the weekly sample (S1, S4, S5).
- (e) What a VAL pass would teach: continuation after extreme residual days (attention) survived out of sample; with
  S9 passed on DEV it is a channel distinct from H4's gradual drift. What a failure would teach: the sign of LESSONS 21
  and the crypto MAX-momentum result did not carry into VAL. Read with H4 if both are submitted: H4 passes and H5 fails,
  gradual drift continues and jumps do not (as Da, Gurun and Warachka would predict); H5 passes and H4 fails,
  attention and not diffusion; both fail, no price continuation out of sample in this unit.
- What I remember that could bias it: from VAL, memecoin pumps (spring 2023; late 2023 into 2024) whose first jumps
  were followed by days or weeks of gains and then by collapses, listing pumps, and FTT's crash days followed by
  further falls; from DEV, DOGE's jumps in early 2021 followed by more, LUNA's crash days in May 2022 (left-tail
  continuation), the crash of May 2021. These lean toward the registered sign, a bias I name; I remember no number for
  a skewness- or MAX-sorted book in VAL.
- Falsifier. DEV: S1 to S10 (never flipped). Counted (VAL): as H4. Named risks: pump-and-dump reversals on the long
  side; capitulation rebounds on the short side; a long knownness span (names held, G10); G7.
- DEV exploration (at most 4 runs): the default with --g6-lags (run 2); if it passes S1 to S8, the control
  gen003_diag_resid_drift (run 7), then the corners n = 17 and n = 25 (runs 8 and 9).

## H6. gen003_week_continuation

- Family relative. Kind portfolio. Unit top30. Dollar neutral, gross 1. A weekly series, as H4.
- Rule: round 1's x with the continuation sign: for each coin in play, z = the mean of e over the last weekly bin
  divided by its root mean square over the same bin (e as in H4). Weight: + the cross-sectional rank of z, demeaned,
  scaled to gross 1. Long last week's largest residual movers for their volatility, short the smallest.
- Program (default pre-registered; strategies/gen003_week_continuation.omr):

      n = param(336, 268, 404)       # hours in the rolling hourly beta to the unit's mean return (14 days)
      r = ret(close, 1)
      mk = cs_mean(r)
      e = r - corr(r, mk, n) * std(r, n) / std(mk, n) * mk
      z = tf_mean(e, weekly) / sqrt(tf_mean(e * e, weekly))
      signal = cs_scale(cs_demean(cs_rank(z)))

  1 param (integer; G5 values 269 to 403), 0 jitterable literals, 31 nodes, lookback 739 h. Parse check OK; canonical
  sha256 9338c83c86ecc527...; file sha256 a894843fcfeb9c3e.... Round 1's books were built orthogonal to this x; H6
  ranks x itself (cs_demean in round 1's x does not change its rank).
- Hypothesis: a coin's residual move of the last week, in units of the week's residual volatility, continues over the
  following week.
- Mechanism: H4's, at its shortest horizon: the part of a coin's news that the clientele absorbs in the week after the
  move is larger than the price pressure that reverts in that week. In stocks the one-week to one-month horizon is
  where reversal lives (liquidity provision); the claim is that among crypto's largest perps continuation dominates
  there, as LESSONS 16 showed on DEV and as Liu, Tsyvinski and Wu (one-week formation) and Zaremba and co-authors (large
  coins) reported outside it.
- Other side, and why it can persist: as H4; here also the liquidity providers who earn the short-term reversal
  premium elsewhere.
- (a) Written AFTER generation 2's round 1 result; the DEV numbers that shaped it: LESSONS 16 (DEV Sharpe -1.566 for
  the weekly residual reversal, Sharpe -4.05, -0.64 and -0.49 by year; costs 0.1369; funding 0.0212 paid); row 41's
  readings of that reversal rule (next30 -1.030; G2 -2.179; G4 -2.022; paired 1 of 10 with B -0.066; r(1..3) about
  0); round 1's x and its books' costs (0.172 to 0.229) and names held (25 of 28).
- (b) Reason beyond those numbers: as H4, at one week; against it in particular: short-term reversal in stocks and at
  daily horizons in crypto, and its costs.
- (c) Costs and funding: x is re-drawn every week, so it costs like round 1's books, 0.17 to 0.23 of equity over DEV
  (C/G 0.21 to 0.27), 0.34 to 0.46 under G4, the most of the three; gross funding 0.25 to 0.40 each, net received about
  0.02; G2 0.6 to 0.8 Sharpe units. S4 and S5 are the items most likely to stop it: a one-week continuation book may
  not pay its costs and the funding stress even if the effect is real, which is why H4, not H6, is the first program of
  this mechanism.
- (d) Known on DEV: its next30 reading is largely predictable from row 41 (the reversal read -1.030 there), so S6 is
  not evidence for H6; per year the parent lost in all three years, so the mirror's price part is positive in all
  three, and after costs 2021 and 2022H1 are uncertain (S3 partly predictable). Unseen: the costs and stresses of this
  construction (S1, S4, S5), S7, S8, S9 and S10.
- (e) What a VAL pass would teach: the founding DEV observation of the continuation pattern (a week's residual move
  continues) held out of sample, net of weekly re-drawing costs and the funding stress. What a failure would teach:
  one-week continuation does not exist after mid-2022 or does not pay its costs in this unit.
- What I remember that could bias it: as H4.
- Falsifier. DEV: S1 to S10 (never flipped). Counted (VAL): as H4. Named risks: costs (G4), G2, crashes, G7.
- DEV exploration (at most 4 runs): the default with --g6-lags (run 3); its control gen003_diag_plain_week and its
  corners n = 269 and n = 403 (runs 4 to 6) ONLY if H4's default failed one of S1 to S8 and H6's default passed S1 to
  S8 (one set of diagnostics per mechanism; H4 first).

---

## DEV-only controls (never to be submitted; each file's first line and hypothesis line say so)

Researcher's tools in the line of round 1's placebos and generation 2's plain controls. Each is its hypothesis's
program with the hypothesis's distinguishing part removed; its DEV Sharpe is read against the hypothesis's default (S9);
its other numbers mean nothing.

- strategies/gen003_diag_plain_multiweek.omr (H4's control): `x = sma(tf_mean(r - mk, weekly), m)`, ranked with the
  continuation sign, m = param(3, 2, 4). r - mk has the same rank as r on every bin (mk is one number for every coin in
  an hour), so it is plain 3-week momentum on the same weekly bins (close to the calibration momentum family's shape,
  ranked and re-decided weekly), with no beta and no volatility scaling; mk keeps the knownness tied to play. It does
  not need H4's 14-day beta window, so it holds a recent entrant (or a name back from a hole) about two weeks earlier
  than H4: a coverage difference named now, visible in the names-held readings of both runs. 1 param, 0 literals, 14
  nodes, lookback 840 h; canonical sha256 a36ad1b98ac78299...; file sha256 8139df1df0b2e3c3....
- strategies/gen003_diag_plain_week.omr (H6's control): `x = tf_mean(r - mk, weekly)`, ranked with the continuation
  sign: plain one-week continuation, no params, 0 literals, 13 nodes, lookback 336 h (the same coverage difference);
  canonical sha256 db2dc180bc6fba8a...; file sha256 e21a0faf5ac087d0....
- strategies/gen003_diag_resid_drift.omr (H5's control): H5 with the skewness replaced by the drift of the same daily
  residuals, `t = tf_last(sma(e, n) / sqrt(sma(e * e, n)), weekly)`, ranked with the continuation sign, n = param(21,
  16, 26): the same windows, knownness and weekly sample. 1 param, 0 literals, 34 nodes, lookback 1,605 h; canonical
  sha256 b38be4354792818c...; file sha256 c9a9bae05b74ecb9....

No price-neutral twin and no hand-made speed-limit or stale-copy diagnostic is written: the sandbox prints G6's speed
limit and paired comparison for every top30 run (KP-018), and these books ARE price books.

## DEV screen (round 2), fixed now, before any number

A hypothesis is eligible only if it passes every item, in the sandbox (full stage 1, no --quick). Numbers are taken as
printed, from the lines named in version 1's screen ("stage 1: ... direction changes (DEV) X ... -> PASS"; "DEV Sharpe
S ..."; "rebalances ... avg gross G ... costs C  liquidated L"; the per-year rows; the KP-018 block, with
--g6-lags its paired lines). Items S1 to S5, S7, S8 and S10 are round 1's, at round 1's thresholds; S6 is tightened for
these rules and S9 is a control in place of round 1's placebo. Nothing is loosened.

- S1 at the default: stage 1 PASS as written (parse, constant probe, truncation and start-cut self-checks), X >= 30,
  G >= 0.5, L False, and names held H >= 15.
- S2 at the default: S >= 0.6 with the registered (continuation) sign. A negative S drops the hypothesis; no sign is
  flipped. Liveness only: for all three rules S2's outcome is predictable from their parents and is not evidence.
- S3 at the default: the year's return > 0 in at least two of the three DEV years printed (2020, 2021, 2022).
- S4 at the default (G4's reading): the DEV Sharpe under doubled costs > 0.
- S5 at the default (G2's reading): the DEV Sharpe under the funding stress > 0.
- S6 at the default (G8's reading), TIGHTENED: the next30 DEV Sharpe is printed (no code) and >= 0.3 (round 1: > 0).
  Why: for a rule written after DEV results its top30 DEV numbers are not evidence, and next30 (ranks 31 to 60, the
  same period) is the cross-section in which these rules' own readings are least known; it is asked to reach at least
  half of S2's liveness bar of 0.6. Known in advance: row 41 (the weekly reversal read -1.030 on next30) makes a
  positive reading likely for H6 and bears on H4.
- S7 at the default (G6's speed limit as G6 computes it): r(1), r(2) and r(3) are printed and each is <= 0.40; a reason
  line in place of the readings fails S7.
- S8 at the default (--g6-lags): A <= 4 (at most 4 of the 10 stale copies at least as good as the book) AND B > 0 (the
  book's own median Sharpe on the common names over the ten lags is positive). A refused reading fails S8.
- S9 control: the hypothesis's DEV Sharpe at its default (S) is greater than its control's DEV Sharpe at the control's
  default (H4: gen003_diag_plain_multiweek, m = 3; H5: gen003_diag_resid_drift, n = 21; H6: gen003_diag_plain_week).
  For H4 and H6: the residual and the scaling must add to plain continuation on DEV, else the rule's own claim
  (coin-specific news, not the market through beta) has no DEV support. For H5: the jump part must add to the drift of
  the same days, else H5 is residual momentum in another form.
- S10 at both G5 corners: DEV Sharpe > 0 AND the DEV Sharpe under doubled costs (G4's reading) > 0 at each. H4: (n, m)
  = (269, 2) and (403, 4). H5: n = 17 and n = 25. H6: n = 269 and n = 403.

Which readings are already predictable from known numbers (and so are NOT evidence even when passed), and which have
not been seen by anyone:

| item | H4 | H5 | H6 |
|---|---|---|---|
| S2 | predictable (generation 2's H6 and the mirror of its H1) | predictable (mirror of generation 2's H5) | predictable (mirror of generation 2's H1) |
| S3 | predictable: 2020 and 2021 positive, 2022H1 likely negative | predictable: likely 3 of 3 | partly: 2020 positive, the others uncertain after costs |
| S1, S4, S5 | unseen (new construction's costs, names held and gross funding flows) | unseen (the weekly sample's costs) | unseen |
| S6 | partly (row 41 bears on it) | unseen | largely predictable (row 41) |
| S7, S8 | unseen; S8's B partly exposed to the known 2022H1 weakness | unseen | unseen |
| S9 | unseen | unseen | unseen |
| S10 | partly (generation 2's H6 neighbours were positive) | unseen | unseen |

Why this is not fitting the screen to known numbers. The screen is round 1's screen item for item, at its thresholds,
fixed for every top30 idea before this round's frame existed and before any continuation rule was chosen, and it only
adds requirements (S6, S9). It treats the known weak spot of H4 (2022H1) with no item of its own: a stricter per-year
item would stop H4 for a reason already recorded (LESSONS 23), and a looser one, or S8 without its B clause, would let
it through for a reason already known; keeping the common items is the choice that uses the known numbers least, as
version 4 of generation 2 argued for its S5. Where an item's outcome is predictable, the table says so, and the plan
does not count it as support. The items that carry information are the unseen ones, above all S6, S8, S9 and S10.
What the screen cannot do: show that a rule written after DEV results works. It can only drop; whether a survivor gets
a counted trial is the coordinator's decision.

Order and economy: the three defaults run first, each once, with --g6-lags, and that one run carries every reading of
S1 to S8. A default that fails any of S1 to S8 ends its hypothesis. Diagnostics: H4 and H6 share ONE set (H4 first):
the control and corners of H4 if H4 passed S1 to S8; otherwise those of H6 if H6 passed S1 to S8; otherwise none. H5's
control runs if H5 passed S1 to S8. A control runs before its corners; the corners run only if S9 passed, in order,
stopping at the first that fails S10.

## Run order and budget (round 2, decided before any run)

| order | run | runs only if |
|---|---|---|
| 1 | H4 default gen003_multiweek_momentum (n = 336, m = 3), with --g6-lags | - |
| 2 | H5 default gen003_jump_continuation (n = 21), with --g6-lags | - |
| 3 | H6 default gen003_week_continuation (n = 336), with --g6-lags | - |
| 4 | control gen003_diag_plain_multiweek (m = 3); or, in its place, gen003_diag_plain_week | run 1 passed S1 to S8; the alternative only if run 1 failed one of S1 to S8 and run 3 passed S1 to S8 |
| 5, 6 | the corners of the hypothesis of run 4: H4 (n, m) = (269, 2), then (403, 4); or H6 n = 269, then n = 403 | run 4 passed S9; run 6 only if run 5 passed S10 |
| 7 | control gen003_diag_resid_drift (n = 21) | run 2 passed S1 to S8 |
| 8, 9 | H5 corners n = 17, then n = 25 | run 7 passed S9; run 9 only if run 8 passed S10 |

`--g6-lags` is used on runs 1 to 3 only (the defaults), where S8 reads it. Command form (from the project root, venv
Python): `.venv\Scripts\python.exe -m omr.sandbox strategies\gen003_multiweek_momentum.omr --g6-lags`; a corner
`.venv\Scripts\python.exe -m omr.sandbox strategies\gen003_multiweek_momentum.omr --set n=269 --set m=2`; a control
`.venv\Scripts\python.exe -m omr.sandbox strategies\gen003_diag_plain_multiweek.omr`. Full stage 1 on every run, one
run at a time (a top30 run needs free memory; a refusal for memory is not a run and is repeated later).

Planned: at most 9 sandbox runs. Reserve: 2 runs for an honest restatement after a stage-1 rejection the parse check
cannot see (the activity floor or a self-check; the constant probe already ran with the parse check), each a recorded
amendment of one of the forms playbook section 4 lists, never a change of logic or of a default. Cap for this round: 11
(the frame allows 16); generation 3 would then have used at most 14 of 60. A kernel_fault, or a refusal the plan does
not cover, stops the round. Every run goes into the log, including runs that fail.

Logged per run: DEV Sharpe, PSR(0), total return, maxDD, direction changes, rebalances, avg gross, avg net, costs, C/G,
funding paid (net), liquidated, the per-year rows, the number of symbols ever in the unit, the lookback; the KP-018
readings: r(1) to r(3) and their max with the decision rows, next30 DEV Sharpe (and symbols, or its code), funding paid
and received (gross), G2 and G4 DEV Sharpes, names held and in play; on runs 1 to 3 the paired reading (A of 10, p, B,
the stale median, the lag range and decision span); for a control or a corner its DEV Sharpe against the default's.

## Selection rule (round 2)

- A hypothesis is eligible only if it passes every screen item, S1 to S10.
- At most TWO programs are recommended for a counted run: at most one of H4 and H6 (one mechanism; only the one that
  had the diagnostics can be eligible), and H5.
- If the coordinator submits only one of two recommended programs, the plan's order is the momentum program (H4, or H6
  in its place) before H5, for reasons fixed now and not from DEV numbers: it is the canonical form of the pattern DEV
  kept showing, its outside support is broader, and H5 rests on one crypto paper against a large equity literature.
- If H4 (or H6) and H5 are both recommended, the coordinator should know that they share a momentum component (H5's
  uncentred skewness carries about 3 times the residual drift of the same 21 days; S9 asks only that the jump part
  adds on DEV), so their VAL outcomes will be correlated while M rises by two.
- None eligible means none recommended; that is a result and is recorded as one.
- No recommendation needs the KP-017 measurement (no funding or basis input). KP-020 applies after a counted trial: a
  Tier-1 result is measured per program in null worlds before it enters the pool. A recommended program is submitted
  only at its declared defaults, unchanged, after the coordinator's source read (playbook section 5).
- DEV Sharpe is a liveness check, not a ranking. The controls (gen003_diag_*) are never submitted.

## Notes and open questions for the coordinator (written with the plan)

Rulings asked for before run 1:
1. LESSONS 23 and H4. LESSONS 23 says a screen a rule failed "is not reopened by registering it again". H4 is a new
   program (section H4, "Relation to LESSONS 23") but the same idea as generation 2's H6, and its DEV numbers will be
   close. Is registering it under this round's frame, with the common screen (not H6's strict per-year item),
   acceptable? If not, H4 and its control are withdrawn by an amendment written before run 1; H6 is then the only
   program of the mechanism (runs 4 to 6 become H6's, under the same conditions), and the planned runs fall by 1.
2. H5 as the exact sign mirror of generation 2's H5, sampled weekly (LESSONS 17 and 21 allow a later plan to register a
   mirror if it says so): acceptable? If not, H5 and its control are withdrawn before run 1 and the runs fall by 4.
3. H6 ranks round 1's x itself, which round 1 held orthogonal on purpose because LESSONS 16 had spent DEV for it:
   acceptable under the frame?
4. The screen: round 1's items at round 1's thresholds, S6 tightened to next30 >= 0.3, S9 as a control comparison, and
   no item added, tightened or loosened for the known 2022H1 weakness of multi-week residual momentum. In particular:
   S3 stays two of three years for H4, and S8 keeps its B clause though half of its window is 2022H1. Accepted?
5. The three controls as DEV-only measurements (as round 1's placebos), counted toward the cap, never submitted; and
   the plain controls' coverage difference (they hold recent entrants about two weeks earlier than H4 and H6).
6. One set of diagnostics for the mechanism of H4 and H6, H4 first, as in generation 2's round 3 (H8 and H9).
7. --g6-lags on runs 1 to 3, and S8 as in round 1.
8. KP-017's restriction does not apply: the programs read close only (with daily(close) in H5 and its control);
   KP-020 applies.
9. The budget: 9 planned and 2 in reserve, cap 11.
10. The order of the two programs if only one is submitted (selection rule).

Notes:
- For the source read (playbook section 5): H4's z divides the mean of e over m weekly bins by the root mean square of
  e over the same bins (two series of the same coin and bins; a t-statistic up to a common factor); H5 is generation
  2's H5 (whose source the coordinator read in round 2) with the sign reversed and tf_last at a weekly bin's end of a
  dimensionless daily series (not of a calendar field); H6 is round 1's x. The controls' r - mk ranks like r on every
  bin; mk is there to tie the knownness to play, and it is no constant, threshold or scale. No program uses hour,
  weekday, a near-constant, a tiny-param scale or algebra across a comparison; there is no comparison at all.
- The parse check's OK lines include the constant probe (omr.lang.parse_file runs it on the 12-symbol top30 probe
  panel). The activity floor and the self-checks remain for the sandbox.
- What I could not do in stage 1: no sandbox run and no synthetic turnover model; the cost estimates rest on round 1's
  and generation 2's measured books, scaled by the overlap of the formation windows, not on a computation. The rough
  DEV Sharpes given as what the parents suggest are guesses from other constructions.
- Ideas considered and not registered, with the reason: (a) a blend of 2-to-4-week momentum with reversal of the month
  before last (Dobrynskaya's shape, generation 2's H6 and H7): it would hedge exactly the known 2022H1 loss, so it
  would be shaped on DEV numbers; (b) crash protection for momentum (volatility-scaled books, Barroso and Santa-Clara
  2015; market-state switches): motivated here only by the known 2022H1 loss; (c) a new mechanism: liquidity shocks
  (Bali, Peng, Shen and Tang 2014; no clear sign in perps, and close to generation 2's activity fade), a session
  clientele (a composition, close to round 1's banned mirrors), nearness to a recent high or a capital-gains overhang
  (continuation proxies close to H4, and the 90-day lookback is far from the 52-week high of the evidence); (d) flow
  continuation, the mirror of LESSONS 17: its parent's price edge, net of the same costs paid again, implies a DEV
  Sharpe of only about 0.5 for the mirror, under S2 and far under what G2 needs; (e) any funding or premium form
  (LESSONS 27 and 34).
- What I saw that disagrees with another part of the materials (no kernel defect found):
  (a) RESEARCH_PLAYBOOK section 3 asks for 3 to 5 hypotheses, the frame for 2 to 4; this plan has 3, inside both.
  (b) LESSONS 23 ("a screen it failed is not reopened by registering it again") against this round's frame, which
      invites rules descended from DEV results and names LESSONS 23's 2022H1 rows as something the screen must deal
      with: open question 1.
  (c) CONSTITUTION section 13's heading still reads "NOT in force until the human approves the re-key" (filed as
      KP-024; unchanged).
  (d) STATE.md's "Where things stand" has no bullet for generation 3's round 1; it is in the "Now" paragraph of
      "Next" (and in the report).
  (e) The brief's "rows 43 to 45" of the sandbox log are 0-indexed (file lines 44 to 46), as generations/gen003/
      REPORT.md counts them.
  (f) git status at the end of stage 1: the six new program files untracked and generations/gen003/PLAN.md modified
      (this append); this session made no git write.

Stage-2 parts (run log, amendments, screen outcome per hypothesis, DEV observations, recommendation) are not written
here; they follow the coordinator's rulings, appended below them.

Pre-registration (version 2): 2026-11-26T13:29:57Z; no round-2 sandbox run has been made.

## Coordinator's rulings before round 2's run 1 (2026-11-26; appended by the coordinator, nothing above is changed)

The coordinator read version 2's programs, screen, run order, selection rule and questions before any round-2
sandbox run. The six new program files parse (lookbacks 336 to 1,605 hours); the sandbox log stands at 46 rows,
none of round 2.

1. LESSONS 23 and H4: accepted under this round's frame, and the tension is recorded here. Lesson 23 forbids
   registering a rule again to get past a screen it failed. This round does something else, in the open: it asks
   whether the one pattern DEV keeps showing gets a single honest test out of sample. H4's DEV readings that are
   predictable from its parents (S2, S3) are not evidence and will not be read as such; the items nobody has
   seen (the stresses, next30, the paired reading, the control, the corners) can only drop it.
2. H5, the sign mirror of generation 2's H5 sampled weekly: accepted on the same terms. Its outside support is
   the thinnest of the three, as the plan says.
3. H6, round 1's x with the continuation sign: accepted on the same terms.
4. The screen as written: accepted (round 1's items at round 1's thresholds, S6 tightened to 0.3, S9 as a control
   comparison, no item of its own for 2022H1; S3 stays two of three years and S8 keeps its B clause).
5. The three controls: allowed as DEV-only measurements; they count toward the cap and are never submitted. The
   difference in coverage between a plain control and its hypothesis is noted as a confound of S9.
6. One set of diagnostics for the mechanism of H4 and H6, H4 first: accepted.
7. --g6-lags on runs 1 to 3 and S8 as in round 1: accepted. The paired reading on DEV is not the gate.
8. KP-017's restriction does not apply: the coordinator read the six programs, and they read close only (H5 and
   its control through daily(close)). KP-020 applies.
9. Budget: 9 planned runs and 2 in reserve, cap 11. One run at a time; start a run when at least 1,000,000 KB of
   physical memory and 4,000,000 KB of commit headroom are free.
10. The order if only one program is submitted (the momentum program before H5): agreed. And stricter than the
    plan: at most ONE program of this round gets a counted trial without a further decision. A second needs its
    own decision of the coordinator, with its reasons recorded before its run, because the two would share a
    momentum component while M rises by two.
11. A survivor is not thereby submitted. Before any counted run the coordinator reads the survivor's section in
    full (its reason beyond the DEV numbers, what a pass and a failure in VAL would teach), records the decision
    in this file, and tells the human.
12. Stage 2 starts only after this plan and its programs are on the remote. Its parts are appended below.
