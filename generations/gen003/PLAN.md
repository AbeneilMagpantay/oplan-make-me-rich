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
