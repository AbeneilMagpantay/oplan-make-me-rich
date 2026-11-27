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

## Sandbox run log (round 2), filled in during stage 2

(Appended below version 2 and the coordinator's round-2 rulings, so that the 127,710 bytes committed as afce52a stay an
unchanged prefix. Every run is listed; run numbers follow version 2's order table, and numbers not listed were not due
under its conditions. C/G = costs / avg gross. Funding paid / received are the gross flows of the KP-018 block; the net
printed on the "rebalances" line is in the note, minus = received. Each output is saved as ASCII in the session scratch
folder, gen003_r2/run_NN_<name>.txt, written by gen003_r2/run_sandbox.py, which only calls `python -m omr.sandbox`.)

| # | program | params (non-default only) | DEV Sharpe | dir. changes | avg gross | names held | costs | C/G | funding paid / received (gross) | G2 DEV | G4 DEV | next30 DEV | r(1), r(2), r(3) | paired (A of 10; B) | years + (of printed) | note |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | H4 gen003_multiweek_momentum | (default n=336, m=3), --g6-lags | 0.541 | 1074 | 0.818 | 23.5 of 28.0 | 0.2399 | 0.293 | 0.5096 / 0.5701 | -0.015 | 0.314 | -0.100 (100 symbols) | -0.054, -0.061, -0.024 (max -0.024, under the limit) | 9 of 10 (p 0.909); B -1.431, stale median -0.590 | 2 of 3 (2020 0.412 SR 2.015; 2021 0.375 SR 1.176; 2022 -0.328 SR -2.716) | PSR(0) 0.801, total 0.305, CAGR 0.113, maxDD 0.400, avg net -0.000, funding net -0.0604 (received), rebalances 652, liquidated False, 75 symbols, lookback 1243 h, stage 1 PASS (25 cuts). Speed-limit rows 2020-08-24 14:00 to 2022-06-30 22:00; paired lags 30 to 262 days, decisions 2021-06-30 23:00 to 2022-06-30 22:00. Wall time 140.3 s (22:02:03 to 22:04:23 +08:00); free memory before the run 3,375,284 KB physical, 14,249,056 KB virtual. Fails S2 (0.541 < 0.6), S5, S6 and S8: H4 DROPPED; runs 4 to 6 not due for H4 |
| 2 | H5 gen003_jump_continuation | (default n=21), --g6-lags | 0.705 | 1047 | 0.801 | 22.2 of 28.0 | 0.2386 | 0.298 | 0.5443 / 0.5347 | 0.105 | 0.447 | -0.820 (100 symbols) | -0.107, -0.062, 0.018 (max 0.018, under the limit) | 10 of 10 (p 1.000); B -1.785, stale median -0.689 | 2 of 3 (2020 0.467 SR 2.384; 2021 0.239 SR 0.891; 2022 -0.226 SR -2.289) | PSR(0) 0.869, total 0.406, CAGR 0.146, maxDD 0.341, avg net 0.000, funding net 0.0096 (paid), rebalances 609, liquidated False, 75 symbols, lookback 1605 h, stage 1 PASS (25 cuts). Speed-limit rows 2020-09-07 14:00 to 2022-06-30 22:00; paired spans as run 1. Wall time 84.0 s (22:04:35 to 22:05:59); free memory before 3,509,304 KB physical, 14,460,360 KB virtual. Fails S6 and S8: H5 DROPPED; runs 7 to 9 not made |
| 3 | H6 gen003_week_continuation | (default n=336), --g6-lags | 0.836 | 1780 | 0.833 | 25.1 of 28.0 | 0.3754 | 0.451 | 0.5741 / 0.5988 | 0.305 | 0.501 | -0.314 (100 symbols) | -0.006, -0.010, 0.022 (max 0.022, under the limit) | 5 of 10 (p 0.545); B -0.757, stale median -0.588 | 2 of 3 (2020 0.691 SR 2.933; 2021 0.080 SR 0.401; 2022 -0.122 SR -0.674) | PSR(0) 0.911, total 0.604, CAGR 0.208, maxDD 0.284, avg net -0.000, funding net -0.0247 (received), rebalances 647, liquidated False, 75 symbols, lookback 739 h, stage 1 PASS (25 cuts). Speed-limit rows 2020-08-10 14:00 to 2022-06-30 22:00; paired spans as run 1. Wall time 133.8 s (22:06:29 to 22:08:43); free memory before 3,597,288 KB physical, 14,531,536 KB virtual. Fails S6 and S8: H6 DROPPED; the alternative runs 4 to 6 (H6's control and corners) not due |

Total sandbox runs made in round 2: 3 (of the 9 planned and the cap of 11); none from the reserve; no stage-1 rejection,
no kernel fault, no refusal, nothing on stderr; every run exit 0, full stage 1 (25 truncation cuts), one at a time, each
started only after the one before had ended and after the memory reading of the coordinator's rule (at least 1,000,000
KB physical and 4,000,000 KB virtual free; 3.4 to 3.6 million and 14.2 to 14.5 million were free). The benchmark line
printed by every run (equal-weight long of the in-play members): DEV Sharpe 0.619, maxDD 0.847, as in round 1 of this
generation and in generation 2. ledger/sandbox_log.jsonl now has 49 rows (46 + 3), rows 46 to 48 (0-indexed), each with
status ok, stage1 full, its logged readings equal to the printed ones and its source_sha256 equal to the committed
file's; `omr.ledger verify` OK, all six chains; `omr.kernel_lock verify` OK, sealed (core 0.05, top30 0.1). Generation 3
has used 6 of 60 sandbox runs.

By the order table: run 4 needed run 1 to pass S1 to S8 (its alternative, H6's control, needed run 3 to pass them), and
run 7 needed run 2 to pass them. None did, so no control (runs 4 and 7) and no corner (runs 5, 6, 8 and 9) was due.

## Amendments (round 2), stage 2

none: no program text, param, default, screen item or run condition was changed, and the reserve was not used.

## Screen outcome per hypothesis (round 2; stage 2, DEV, read from the run log above)

"pred." = the plan's table called the item's outcome predictable from known numbers (so a pass is not evidence);
"partly" = partly predictable; "unseen" = no one had seen it.

| H | S1 (PASS; X >= 30; G >= 0.5; L False; H >= 15) | S2 (S >= 0.6, continuation sign) | S3 (years + >= 2 of 3) | S4 (G4 DEV > 0) | S5 (G2 DEV > 0) | S6 (next30 DEV >= 0.3) | S7 (r(1..3) each <= 0.40) | S8 (A <= 4 and B > 0) | S9 (S > control) | S10 (corners) | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| H4 gen003_multiweek_momentum | pass (PASS; 1074; 0.818; False; 23.5), unseen | FAIL (0.541), pred. | pass (2020, 2021; 2022H1 -0.328 as predicted), pred. | pass (0.314), unseen | FAIL (-0.015) | FAIL (-0.100) | pass (-0.054, -0.061, -0.024), unseen | FAIL (A 9; B -1.431) | not run | not run | DROPPED |
| H5 gen003_jump_continuation | pass (PASS; 1047; 0.801; False; 22.2), unseen | pass (0.705), pred. | pass (2020, 2021; 2022H1 -0.226), pred. | pass (0.447), unseen | pass (0.105), unseen | FAIL (-0.820) | pass (-0.107, -0.062, 0.018), unseen | FAIL (A 10; B -1.785) | not run | not run | DROPPED |
| H6 gen003_week_continuation | pass (PASS; 1780; 0.833; False; 25.1), unseen | pass (0.836), pred. | pass (2020, 2021; 2022H1 -0.122), partly | pass (0.501), unseen | pass (0.305), unseen | FAIL (-0.314) | pass (-0.006, -0.010, 0.022), unseen | FAIL (A 5; B -0.757) | not run | not run | DROPPED |

By the order table a default that fails any of S1 to S8 ends its hypothesis, so no control (S9) and no corner (S10) was
run for any of them. Two outcomes the plan's table had called predictable did not come out as the plan expected: H4's S2
(the parents suggested about 1.0 to 1.4; it read 0.541) and H6's S6 (called largely predictable from row 41 as positive;
it read -0.314). H5's S3 passed, but with 2 of 3 years where the plan expected 3 of 3.

Against each pre-registered DEV falsifier:
- H4: falsified on DEV. The 3-week residual continuation book had the registered sign (0.541) but below the liveness
  bar; it was negative under the funding stress (-0.015) and on next30 (-0.100), and on the last 365 days of DEV it
  lost on the common names (B -1.431) while 9 of its 10 stale copies did at least as well. 2022H1 lost (Sharpe
  -2.716), as known in advance for this idea; it was not the item that decided (S3 passed).
- H5: falsified on DEV. The jump-continuation book had the registered sign (0.705) and stayed positive under both
  stresses (G2 0.105, G4 0.447), but read -0.820 on next30, and on the last 365 days of DEV it lost on the common names
  (B -1.785) with all 10 stale copies at least as good. S9 (the drift control) was never due, so whether its DEV result
  was jumps or drift is not known.
- H6: falsified on DEV. The one-week residual continuation book had the registered sign (0.836) and stayed positive
  under both stresses (G2 0.305, G4 0.501), but read -0.314 on next30, and on the last 365 days of DEV it lost on the
  common names (B -0.757) with 5 of its 10 stale copies at least as good.

## DEV observations (round 2; NOT hypotheses, never to be submitted from this plan)

- All three continuation books had the registered sign on DEV, and all three earned it early: by year their Sharpe was
  2.0 to 2.9 in 2020, 0.4 to 1.2 in 2021 and -0.7 to -2.7 in 2022H1, and each lost on the common names over the last
  365 days of DEV (paired reading, B -0.76 to -1.79). On these weekly, cost-bearing constructions the DEV continuation
  of LESSONS 16, 21, 23 and 43 was concentrated in 2020 and was gone by the last year of DEV. WEAK: one DEV period, one
  default each, and rules written after DEV results.
- All three read negative on next30 (-0.100, -0.820, -0.314): ranks 31 to 60 did not continue the moves after costs on
  DEV. Row 41 had read the one-week residual REVERSAL at -1.030 on next30, so in that unit both signs of the one-week
  rule lost after costs on DEV; the plan's expectation that H6's next30 was predictable from row 41 was wrong, because a
  mirror pays the costs again. WEAK.
- The DEV Sharpes were well below what the parents suggested (H4 0.541 against about 1.0 to 1.4; H5 0.705 against 1.1 to
  1.6; H6 0.836 against 0.7 to 1.1, inside). A rough additive split (compounding ignored) puts the price P&L before
  costs and funding at about 0.48 (H4: 0.305 + 0.2399 - 0.0604), 0.65 (H5: 0.406 + 0.2386 + 0.0096) and 0.95 (H6: 0.604
  + 0.3754 - 0.0247) of equity over DEV, about 2.0, 2.7 and 2.5 times their costs.
- Costs were far above the plan's estimates: 0.2399 (estimate 0.12 to 0.18), 0.2386 (0.09 to 0.15) and 0.3754 (0.17 to
  0.23) of equity over DEV, C/G 0.29, 0.30 and 0.45 (estimates 0.15 to 0.22, 0.11 to 0.18, 0.21 to 0.27), with 609 to
  652 rebalances, as many as round 1's books (573 to 668) but larger trades. The weekly-sampled skewness book cost more
  than generation 2's daily-updated form of the same statistic (0.2386 against 0.1404, the opposite sign): the plan's
  argument that a weekly sample cannot cost more (the weekly change of the targets is the sum of their daily changes)
  bounds the targets' path but not the costs, which include the drift traded back between decisions. Suggestive cause,
  NOT measured: a continuation book holds the movers, which keep moving and stay volatile, and a target held for a week
  is traded back against their drift on every rebalance, while a daily-updated target partly follows it. A design
  yardstick next to LESSONS 19, 24 and 41: weekly continuation books cost 0.29 to 0.45 per unit of gross on DEV.
- They also paid and received more gross funding, in sum, than any earlier top30 book read by the sandbox: 0.51 to
  0.60 of equity each way over DEV, 1.08 to 1.17 paid plus received (round 1's books 0.58 to 0.79; row 40 0.93, row 41
  0.38); net small (H4 received 0.060, H6 0.025, H5 paid 0.010). Not measured why; a book long and short the recent
  movers holds coins with large funding of either sign. G2 again cost more Sharpe than G4 (0.556, 0.600 and 0.531
  against 0.227, 0.258 and 0.335; LESSONS 42).
- The speed-limit readings were near zero (-0.107 to 0.022), as designed. Names held 23.5, 22.2 and 25.1 of 28.0: the
  longer knownness spans of H4 (about 5 weeks) and H5 (6 to 7 weeks) cost one to three names more than round 1's 21-day
  span. Direction changes 1074 (H4), 1047 (H5) and 1780 (H6).
- WEAK throughout: one DEV period, one default each, one researcher session, rules written after DEV results; nothing
  here is a parameter recommendation, and no corner or control was run.

## Recommendation (round 2)

NONE. By the pre-registered selection rule a hypothesis is eligible only if it passes every screen item S1 to S10. H4
failed S2, S5, S6 and S8; H5 failed S6 and S8; H6 failed S6 and S8. No program from version 2 is recommended for a
counted submission, so the coordinator's ruling (10) (at most one counted trial from this round without a further
decision) and ruling (11) do not come into play; no KP-017 or KP-020 measurement is needed for this round. The DEV-only
controls (gen003_diag_*) were not run and are never to be submitted. Generation 3 stands at 0 of 5 counted
submissions and 6 of 60 sandbox runs; M is unchanged at 6.

---

# Generation 3 - PLAN, version 3 (round 3, the wide screen, pre-registered 2026-11-27 before any round-3 sandbox run)

Researcher session for generation 3, round 3, stage 1. Unit top30. A fresh session: everything it knows of the project
comes from the files below. Date local (+08:00); UTC in the last line. Appended below version 2 and its stage-2 parts;
the 139,818 bytes before this line (sha256 5efd3dfa569d66c5...) are unchanged.

- Kernel: `omr.status` OK d09812fdec752a17, semantic 7d923e7e2375986d, text b74122f3f9821056, sealed (G6 core 0.05,
  top30 0.10). Data research_hash 28d9084a8c5c7659, validated, snapshot_end 2026-11-18 10:00 UTC.
- Ledger: M = 6 (generation 0: 4, 1: 1, 2: 1, 3: 0 of 5), N 5.90, rho 0.021, Tier 1 0, pool 0 of 5, one uncounted
  stage-1 rejection. Sandbox log 49 rows; generation 3 has used 6 of 60 sandbox runs.
- Read: RESEARCH_PLAYBOOK.md (all; 3, 4, 4b, 5, 8b with care), generations/META_REVIEW_2026-11-26.md (all),
  LESSONS.md (46), LANGUAGE.md (all), CONSTITUTION.md 4 to 7 and 13, generations/gen003/REPORT.md (rounds 1 and 2),
  generations/gen003/PLAN.md (version 1's head and screen, both rounds' rulings, run logs, screen outcomes, DEV
  observations, recommendations), rows 43 to 48 of ledger/sandbox_log.jsonl, KERNEL_PROPOSALS.md entry of 2026-11-27,
  STATE.md lines 295 to 327, `omr.status`, `omr.ledger summary`. Kernel code read only for how the tool behaves:
  omr/lang.py (parse rules, lookback), omr/sandbox.py (what a top30 run prints), omr/upipeline.py (dev_speed_limit,
  dev_names_held, dev_paired_lags). Shapes: strategies/gen003_*.omr, gen002_averaged_funding_shock, gen002_small_tickets.
- Not opened: data/, ledger/returns/, ledger/trials/, calibration files, audits/. No project program was run on data:
  only `omr.status`, `omr.ledger summary` and a parse-only check (scratch gen003_r3/parse_check.py; omr.lang.parse_file).
- Numbers seen before writing: every DEV number of generation 2 and of generation 3 rounds 1 and 2 (their readings in
  REPORT.md, the run logs and sandbox rows 43 to 48), the review's tables (rows 40 to 48, the bar), and the VAL rows of
  the six counted trials. No VAL or DEV number exists for any program below.
- Files of this version: this text and eleven new programs, strategies/gen003_w01_* to gen003_w11_*. Nothing else.

Three facts from the kernel's code and rules shaped the list (behaviour, not results):
1. W1 reads "names held" as the mean, over DEV rows with any name in play, of names with a weight other than 0, and
   "avg gross" over all DEV rows. A book flat more than about 45% of the time fails W1 whatever it earns. So no sparse
   book is registered; where state matters, it enters the signal and the book stays in the market.
2. The speed limit's step is 621 h = 3 weeks + 117 h. Over j = 1 to 19 the lag lands within 6 to 15 hours of a whole
   number of weeks several times (j = 3: +15 h; j = 10: -6 h; j = 13: +9 h). A weight path periodic in hour or weekday
   is therefore correlated with its own lagged copy: a calendar SCHEDULE fails G6 by construction in top30 (the review's
   agenda item 1 was for unit core, whose G6 has no such limit). Here calendar fields only select which hours of a
   volume series feed a weekly bin (W-05, W-06); the weights change once a week.
3. A cs_* inside a rolling window (the hourly beta to the unit's mean) makes entrants wait for in-play history and drops
   a name for weeks after one unusable hour. Only W-03 and W-11 keep it; the others use own-norm ratios or btc().

Considered, not registered: market timing of the basket (G6's paired copies keep each row's net, so a net-long book's
stale copies earn the same drift; only a fast-flipping net gets credit, and each flip trades the whole book; every
weekly timing input I found was a funding contrarian or a trend form already failed in core); funding-reading ideas
(each one I could write was a contrarian funding or premium form, or carry level); stress-conditioned reversal (sparse,
and descended from #25 whose pre-cost DEV Sharpe 0.77 is under the 2.5 rule); a pure weekday or hour schedule (fact 2).

## The screen, fixed now, the same for every idea (W1 to W8)

W1 stage 1 passes with at least 30 direction changes, average gross at least 0.5, at least 15 names held on average, not
liquidated; W2 DEV Sharpe before costs (the DEV Sharpe plus the drop under G4's reading, i.e. DEV Sharpe + (DEV Sharpe -
G4 DEV Sharpe)) at least 1.5; W3 G4's DEV reading positive; W4 G2's DEV reading positive; W5 next30 DEV Sharpe at least
0.3; W6 the speed-limit statistic at most 0.40 at each of one to three steps (a reason line fails); W7 in the paired
reading at most 4 of 10 stale copies at least as good as the book AND the book's median Sharpe over the last 365 days of
DEV positive (a refused reading fails); W8 at least two of the three DEV years positive. A wrong sign is a failure; no
sign is ever flipped; no default is changed after a run.

Numbers are taken as the sandbox prints them (full stage 1, no --quick, with --g6-lags): the stage-1 line, "DEV
Sharpe", "rebalances ... avg gross ... liquidated", the per-year rows (2020, 2021, 2022; a year is positive when its
return is above 0), and the KP-018 block (r(1) to r(3), next30, G2 and G4 on DEV, names held, the paired reading A of 10
and book median B). Every idea's registered sign is the sign of its signal line; a negative DEV Sharpe fails W2.

## The bar, shared arithmetic (playbook 8b)

- Cost drag = the Sharpe that 1x costs take, i.e. the expected G4 drop. Measured for weekly top30 rank books: 0.23 to
  0.46 (rows 41, 43 to 48). Registered here: 0.40 for a ranking re-drawn every week; 0.30 for one whose decision
  averages two or more weeks of input or changes only partly week to week; 0.25 for a slow reference-level book (churn
  and drift remain, about 0.07 a year per unit of gross, review 2.2); 0.35 for the combination.
- Sharpe needed in VAL before costs: 0.74 + drag for G1's line, 1.5 + drag for decent odds. Drag 0.25: 0.99 / 1.75;
  0.30: 1.04 / 1.80; 0.35: 1.09 / 1.85; 0.40: 1.14 / 1.90.
- G2 takes another 0.5 to 0.8 on DEV from any full book (LESSONS 42); W4 asks only that its DEV reading stay positive.
- W2's 1.5 is a floor, not the bar: with the DEV-to-VAL decay the review estimates (VAL keeps 40 to 60% of DEV), 2.5 to
  3.5 before costs on DEV would be needed to expect 1.5 in VAL. A pass is a candidate for one counted trial, nothing more.

## Disclosures for every idea

- The author model has read this market's history through DEV, VAL and the vault, and this session every DEV number of
  generations 2 and 3. No rule names a date, coin, price level or event; every tunable number is a declared param (no
  file has a jitterable literal). That does not remove hindsight from the CHOICE of ideas (KP-010).
- Remembered DEV events: 19 May 2021; the Saturday crash of 4 December 2021; January 2022; LUNA's collapse in May 2022
  (a volatility shock, decoupled, far below its high, on heavy volume); Celsius and Three Arrows in June 2022; the 2021
  memecoin waves (volume surges, weekend activity, decoupled rallies). Remembered DEV readings: residual continuation
  strong in 2020 and gone by 2022H1 (#26 to #28); the weekend part of a week's move persisted (#23); residual up-jumps
  continued (#15, #27); every bet against a recent move lost or earned too little; a contrarian one-week trade-count
  burst read +0.172 (#12).
- Remembered VAL: BTC's share rising, altcoins lagging; memecoin waves 2023 to 2024; FTT in November 2022; US spot ETFs
  from January 2024 concentrating BTC and ETH flow in US hours; weekend shocks (March 2023, 4 to 5 August 2024). I
  remember no result of any book below, in VAL or anywhere.
- Eleven ideas against one screen let noise through more often than three did (KERNEL_PROPOSALS, 2026-11-27).

## The ideas

All eleven: kind portfolio, unit top30, rank weights cs_scale(cs_demean(cs_rank(.))) (W-11: a sum of ranks), dollar
neutral, gross 1, decided once a week (a weekly series visible at the bar that opens Sunday 23:00 UTC, traded at the
Monday 00:00 open). Lookbacks at every window param's high bound, from the parse check.

### W-01 gen003_w01_high_anchor (class A, reference price)
- Rule: dd = log(daily close / highest daily high of the last n days) / annualised daily vol over n days, at the
  Sunday close; long the coins nearest their high, short the farthest.
- Program: n = param(42, 33, 51); `dd = log(d / rmax(daily(high), n)) / realised_vol(d, n)`;
  `signal = cs_scale(cs_demean(cs_rank(tf_last(dd, weekly))))`. 17 nodes, lookback 1,605 h.
- Mechanism: anchoring on the recent high (George and Hwang 2004): traders sell into a known high and hesitate to bid
  through it, so news that lifts a coin toward it is priced slowly; far below it, loss-averse holders delay selling.
  Other side: anchored sellers near highs, reluctant sellers far below.
- Why not one of the 28: none read a price against a reference level; they ranked returns over a window. It is
  correlated with multi-week continuation (a coin near its high has risen): question 3.
- Drag 0.25 (slow reference, partial weekly change) -> before costs in VAL 0.99 line / 1.75 odds.
- Outside evidence: equities, many markets, an effect that does not reverse; crypto: I recall reports of a 52-week or
  all-time-high proximity effect, unverified, size after 2021 unknown.
- Bias: LUNA sat far below its high while collapsing (short leg); in 2022H1 near-high coins were the less fallen, so
  the book carries a defensive tilt in crashes (the vol scaling tempers it). W6 risk: a 6-week reference may hold r(1)
  near 0.3 to 0.4.

### W-02 gen003_w02_cost_basis (class A, reference price)
- Rule: cost = the n-day VWAP (sum of daily quote volume / sum of daily base volume); gain = log(close / cost) / annualised
  daily vol over n days, at the Sunday close; long the largest unrealised gain, short the largest loss.
- Program: n = param(28, 22, 34); `cost = rsum(daily(quote_volume), n) / rsum(daily(volume), n)`;
  `gain = log(d / cost) / realised_vol(d, n)`; signal as W-01 on gain. 22 nodes, lookback 1,197 h.
- Mechanism: the disposition effect (Grinblatt and Han 2005): profit-taking holds down coins above the average cost of
  recent buyers, reluctance to realise losses props up coins below; the gap closes later. Other side: disposition-prone
  holders, a large share of crypto's retail.
- Why not one of the 28: the first program to read price against a volume-weighted price; correlated with W-01 and
  with continuation (question 3).
- Drag 0.25 -> 0.99 / 1.75.
- Outside evidence: equities (Grinblatt and Han 2005; Frazzini 2006); crypto: realised price and MVRV as BTC time-series
  indicators (practitioner use), nothing cross-sectional that I know.
- Bias: as W-01. The 4-week window is shorter than W-01's so that the book is not one slow average (W6).

### W-03 gen003_w03_vol_shock (class B, shocks to risk and liquidity)
- Rule: e = the hourly residual to the unit's mean (14-day hourly beta, as in rounds 1 and 2); v = the week's mean of
  e squared; shock = v / mean of v over the last m weeks (this one included); short the largest, long the smallest.
- Program: n = param(336, 268, 404), m = param(4, 3, 5); `v = tf_mean(e * e, weekly)`;
  `signal = cs_scale(cs_demean(-cs_rank(v / sma(v, m))))`. 30 nodes, lookback 1,411 h.
- Mechanism: attention and lottery demand: a jump in a coin's own volatility draws retail and leveraged long interest
  that overprices it for weeks (Barber and Odean; the idiosyncratic-volatility puzzle). Other side: attention buyers.
- Why not one of the 28: unsigned; it ranks the size of the residual's second moment, not its direction, its skew
  (#15, #27) or the hours a move was made in (#23 to #25).
- Drag 0.40 -> 1.14 / 1.90.
- Outside evidence: equities, Ang, Hodrick, Xing and Zhang (2006); crypto: mixed in what I recall (IVOL and MAX results
  of both signs); nothing after 2021 I can cite.
- Bias: up-jumps continued on DEV (#15, #27), which works against the short leg when the shock is a pump; LUNA's
  collapse is a shock in its favour. Names held: entrants wait about six weeks (fact 3).

### W-04 gen003_w04_illiquidity_shock (class B, shocks to risk and liquidity)
- Rule: y = (mean absolute daily log return over k days / over n days) / (mean daily quote volume over k days / over n
  days); x = the k-day log return / annualised vol; both at the Sunday close; z = y net of a cross-sectional fit on x
  on every bin; long the largest z, short the smallest.
- Program: k = param(7, 5, 9), n = param(42, 33, 51);
  `y = tf_last((sma(a, k) / sma(a, n)) / (sma(q, k) / sma(q, n)), weekly)`, `z = yd - cs_mean(xd * yd) / cs_mean(xd * xd) * xd`;
  `signal = cs_scale(cs_demean(cs_rank(z)))`. 48 nodes, lookback 1,605 h.
- Mechanism: illiquidity is priced (Amihud 2002): when market makers withdraw from one coin, its price moves more per
  dollar traded, it is marked down, and holders are paid a higher return for the risk. Held orthogonal to the week's
  move, so the book is not a reversal book. Other side: liquidity demanders forced to trade a thin book.
- Why not one of the 28: no earlier program reads price impact per unit of volume; orthogonal to the move by
  construction (round 1's technique, a new input).
- Drag 0.40 -> 1.14 / 1.90.
- Outside evidence: equities strong (Amihud 2002; Pastor and Stambaugh 2003); crypto: an illiquidity premium reported in
  the cross-section (recalled, among them Wei 2018), mostly in small coins; size in a top 30 after 2021 unknown.
- Bias: the impact measure rises with the coin's volatility, so W-04 may be W-03's mirror in part; the screen reads
  each alone, and selection takes at most one of class B.

### W-05 gen003_w05_us_session_shift (class C, calendar clientele of volume)
- Rule: rv = hourly quote volume / its own trailing w-hour mean; s = the share of the week's rv in decision-time hours
  a to b (default 15 to 21: bars opening 14:00 to 20:00 UTC); shift = s / mean of s over the last m weeks; long the
  largest shift, short the smallest.
- Program: a = param(15, 12, 18), b = param(21, 16, 26), w = param(168, 134, 202), m = param(4, 3, 5);
  `s = tf_mean(where(us, rv, 0), weekly) / tf_mean(rv, weekly)`; `signal = cs_scale(cs_demean(cs_rank(s / sma(s, m))))`.
  28 nodes, lookback 1,208 h.
- Mechanism: session clientele: US-hour trading carries Western and institutional participants whose buying is spread
  over weeks; a coin whose activity migrates toward US hours is gaining that buyer. Other side: Asian-hour holders and
  passive liquidity selling into slow new demand.
- Why not one of the 28: calendar on VOLUME, not on the move (#23 to #25 were compositions of the move); not an
  activity level or burst (#12, #13).
- Drag 0.40 -> 1.14 / 1.90.
- Outside evidence: none on returns; crypto's intraday volume pattern is documented descriptively only.
- Bias: I remember the ETF-era US-hour flow in BTC and ETH (VAL, 2024). G5 moves the window (a 12 to 18, b 17 to 25);
  the corners read both ends.

### W-06 gen003_w06_weekend_tilt (class C, calendar clientele of volume)
- Rule: s = the share of the week's rv (as W-05) at decision-time weekday >= d (default 5.0: bars opening Friday 23:00
  to Sunday 22:00 UTC); tilt = s / mean over the last m weeks; short the largest tilt, long the smallest.
- Program: d = param(5.0, 4.0, 6.0), w = param(168, 134, 202), m = param(4, 3, 5);
  `s = tf_mean(where(weekday >= d, rv, 0), weekly) / tf_mean(rv, weekly)`;
  `signal = cs_scale(cs_demean(-cs_rank(s / sma(s, m))))`. 24 nodes, lookback 1,208 h.
- Mechanism: weekends are retail hours (desks and market makers thin); a coin whose trading tilts to the weekend is
  carried by a retail crowd that overprices it. Other side: retail weekend speculators.
- Why not one of the 28: the weekend share of VOLUME, not of the move (#23 ranked the weekend part of the residual move).
- Drag 0.40 -> 1.14 / 1.90.
- Outside evidence: none on returns.
- Bias: on DEV the weekend part of the MOVE persisted (#23); if weekend volume travels with weekend moves, that pattern
  works against this sign. I register the sign the mechanism gives. d as a float param as in round 1's ruling 2 (G5
  draws Sunday only about half the time; corners 4.5 and 5.5).

### W-07 gen003_w07_wick_absorption (class D, intrabar absorption)
- Rule: per hour, (open + close - high - low) / close = (lower wick - upper wick) / close; z = its mean over the last m
  weeks / the mean hourly range (high - low) / close over the same weeks; long the largest z, short the smallest.
- Program: m = param(2, 1, 3); `w = (open + close - high - low) / close`, `g = (high - low) / close`;
  `z = sma(tf_mean(w, weekly), m) / sma(tf_mean(g, weekly), m)`. 27 nodes, lookback 671 h.
- Mechanism: a lower wick is aggressive selling absorbed by resting bids within the hour; repeated over weeks it marks
  a patient large buyer accumulating, whose demand outlasts the week (upper wicks: passive distribution). Other side:
  takers and stop-runs selling into resting bids.
- Why not one of the 28: reads where the bar's body sits in its range, independent of the body's direction; no top30
  program has read high or low.
- Drag 0.30 (two weeks averaged) -> 1.04 / 1.80.
- Outside evidence: none academic that I know (chart lore; Lo, Mamaysky and Wang 2000 found modest content in patterns).
- Bias: nothing specific that I can name, which is no protection.

### W-08 gen003_w08_decoupling (class E, comovement)
- Rule: c = the correlation of the coin's hourly returns with BTC's over the last k hours minus over the last n hours
  (1 against 6 weeks), at the week's last hour; short the most decoupled, long the most re-coupled.
- Program: k = param(168, 134, 202), n = param(1008, 806, 1210);
  `c = tf_last(corr(r, rb, k) - corr(r, rb, n), weekly)`; `signal = cs_scale(cs_demean(cs_rank(c)))`. 18 nodes,
  lookback 1,545 h. BTC's own c is about 0 (mid-rank).
- Mechanism: a coin that stops moving with the market has a story of its own; attention traders bid it beyond value
  and it gives that back as attention fades (Barber and Odean; Da, Engelberg and Gao). Other side: attention buyers.
- Why not one of the 28: comovement, unsigned; no earlier program read a correlation.
- Drag 0.40 -> 1.14 / 1.90.
- Outside evidence: none on returns (the comovement literature, e.g. Barberis, Shleifer and Wurgler 2005, describes it).
- Bias: LUNA decoupled while collapsing (helps); 2021 memecoins decoupled while rising (hurts).

### W-09 gen003_w09_volume_trend (class F, slow attention flow)
- Rule: t = the mean daily quote volume over the last k days / over n days (2 against 8 weeks), at the Sunday daily
  bar; long the largest rise, short the largest fall.
- Program: k = param(14, 11, 17), n = param(56, 44, 68); `t = tf_last(sma(q, k) / sma(q, n), weekly)`;
  `signal = cs_scale(cs_demean(cs_rank(t)))`. 13 nodes, lookback 1,989 h.
- Mechanism: capital and attention reach a coin over weeks; trading that grows against its two-month norm marks
  participants still arriving (the visibility premium of Gervais, Kaniel and Mingelgrin 2001). Other side: holders and
  liquidity providers who sell before the inflow is spent.
- Why not one of the 28: slower formation (2 against 8 weeks) on quote volume with the inflow sign; #12 was a one-week
  trade-count burst, contrarian. The review lists "quote-volume trend" as not yet read (question 4).
- Drag 0.30 -> 1.04 / 1.80.
- Outside evidence: for, GKM 2001 (equities, weekly volume shocks); against, Lee and Swaminathan 2000 (high volume as
  glamour, lower later returns). Crypto: none I trust.
- Bias: #12's contrarian sign read +0.172 on DEV, so the weekly mirror of this sign lost a little on DEV; I register
  the sign the mechanism gives. W6 risk: the 8-week norm.

### W-10 gen003_w10_basis_instability (class G, leverage instability; READS index_close)
- Rule: p = (close - index_close) / index_close; v = the week's mean absolute hourly change of p / the week's mean
  absolute hourly return; instability = v / mean over the last m weeks; short the largest, long the smallest.
- Program: m = param(4, 3, 5);
  `v = tf_mean(abs(delta(p, 1)), weekly) / tf_mean(abs(ret(close, 1)), weekly)`;
  `signal = cs_scale(cs_demean(-cs_rank(v / sma(v, m))))`. 24 nodes, lookback 1,014 h.
- Playbook 4b (KP-017): screened on DEV; recommended only "subject to the per-program measurement".
- Mechanism: a premium that churns more than the price means leveraged perp traders dominate and arbitrage capital is
  short; such episodes end in deleveraging that weighs on the price. Other side: leveraged perp speculators.
- Why not one of the 28: the premium's level and sign are not read (#18, #20, #22 ranked its level or shock,
  contrarian); this is its noise relative to the price's. Adjacent to a closed class (question 5).
- Drag 0.40 -> 1.14 / 1.90.
- Outside evidence: none.
- Bias: premium and funding contrarian books were positive on DEV (#18 to #21) and #21 failed in VAL; if instability
  travels with premium spikes, W-10 inherits that DEV pattern.

### W-11 gen003_w11_ensemble (class H, combination whose trades net)
- Rule: cs_rank(W-01's dd) - cs_rank(W-03's shock) + cs_rank(W-07's z), re-centred and scaled to gross 1; each part
  exactly as in its own file, at the same defaults.
- Program: n = param(42, 33, 51), b = param(336, 268, 404), m = param(4, 3, 5), j = param(2, 1, 3);
  `signal = cs_scale(cs_demean(cs_rank(dd) - cs_rank(v / sma(v, m)) + cs_rank(z)))`. 71 nodes, lookback 1,605 h.
- Mechanism: none new: three information sets (reference price, own-volatility shock, intrabar absorption), close to
  independent; k signals of Sharpe S give about S x sqrt(k) while their trades partly net (review agenda item 4).
- Why not one of the 28: no earlier program combined signals; none of its parts is from a closed class.
- Drag 0.35 -> 1.09 / 1.85.
- Outside evidence: the arithmetic only; each part as in its section.
- Bias: all three parts' biases. It hides no test only because each part is read alone in this round; a pass of W-11
  with its parts failing would be a pass of the combination only.

## Run order and budget (decided now)

- Runs 1 to 11: the defaults, in the order W-01 to W-11 (the combination last), each
  `python -m omr.sandbox strategies/gen003_wNN_<idea>.omr --g6-lags`, one at a time under the coordinator's memory rule.
  Every default runs, whatever the earlier ones read.
- Then corners, only for ideas that passed W1 to W8, in the selection order below: the 0.8 corner, then the 1.2 corner
  (`--set`), each needing a positive DEV Sharpe AND a positive G4 DEV reading; stop that idea at its first failure. At
  most 6 corner runs; if more than three ideas pass W1 to W8, corners for the first three in the selection order.
- Corners (integers rounded; a param left unchanged by rounding moves by 1; W-06's d as in round 1):

  | idea | 0.8 corner | 1.2 corner |
  |---|---|---|
  | W-01 | n=34 | n=50 |
  | W-02 | n=22 | n=34 |
  | W-03 | n=269, m=3 | n=403, m=5 |
  | W-04 | k=6, n=34 | k=8, n=50 |
  | W-05 | a=12, b=17, w=134, m=3 | a=18, b=25, w=202, m=5 |
  | W-06 | d=4.5, w=134, m=3 | d=5.5, w=202, m=5 |
  | W-07 | m=1 | m=3 |
  | W-08 | k=134, n=806 | k=202, n=1210 |
  | W-09 | k=11, n=45 | k=17, n=67 |
  | W-10 | m=3 | m=5 |
  | W-11 | n=34, b=269, m=3, j=1 | n=50, b=403, m=5, j=3 |

- Reserve: 2 runs, only for an honest restatement after a stage-1 rejection of a default (the restated file is
  recorded as an amendment before its run). Cap 19 runs (11 + 6 + 2), so generation 3 would have used at most 25 of 60.
- No placebo or control run is registered (question 8). No counted run is part of this plan.

## Selection rule (fixed now; the DEV Sharpe ranks nothing beyond the screen)

- Eligible: passes W1 to W8 at the default and both corners.
- Order: (1) A in the paired reading, fewest stale copies at least as good first (the reading built like G6, the gate
  that has stopped every top30 book so far); (2) the registered cost drag, smallest first (W-01 and W-02 0.25; W-07 and
  W-09 0.30; W-11 0.35; the rest 0.40); (3) the run order.
- Take the first eligible idea; then the next eligible idea of another class that shares no component with it (W-11
  shares components with W-01, W-03 and W-07). At most two. W-10 only "subject to the KP-017 measurement".
- A recommendation is not a submission: the coordinator reads the program and decides; at most one counted trial
  without a further decision; any top30 pass is measured per program in null worlds before the pool (KP-020).
- If nothing is eligible, the recommendation is NONE.

## Questions for the coordinator

1. W1 and sparse books: W1 fails any book flat more than about 45% of DEV rows (fact 1), so the "in the market only in
   stated states" form cannot pass this screen. Intended? None is registered.
2. Calendar schedules and the speed limit (fact 2): is the reading right that a weekday or hour schedule fails G6 by
   construction in top30? It is why calendar enters only as a selector of hours (W-05, W-06).
3. W-01 and W-02 rank a price against a reference (recent high, recent VWAP). In equities both are distinct from
   return momentum, but they are correlated with it. Do they count as the closed continuation form?
4. W-09 is the slower, opposite-sign relative of #12 (crowding by activity) and the review's "quote-volume trend".
   Closed or open?
5. W-10 reads index_close and ranks the premium's noise, not its level or shock. Is it a closed "premium contrarian
   form"? If open, confirmed as screen-only under KP-017?
6. Calendar thresholds as params (W-05's a and b, W-06's d) with hour and weekday as selectors of a volume series: the
   same standing as round 1's rulings 1 and 2?
7. W-11 repeats three of the round's own books in one program. Acceptable as one of the eleven, with the selection rule
   taking it or its parts but not both?
8. Playbook 8b gives a survivor "corners and a control"; the order's budget names corners only. If a control is
   wanted for a survivor, which (a placebo per idea was not registered) and from which budget?

Written 2026-11-27 02:50 +08:00 (2026-11-26 18:50 UTC), before any round-3 sandbox run.

## Coordinator's rulings before round 3's run 1 (2026-11-27; appended by the coordinator, nothing above is changed)

The coordinator read version 3 and the eleven programs (the source read of playbook section 5: no constant,
threshold or scale built from a calendar field or a same-unit ratio; hour and weekday appear only as selectors
of hours of a volume series) before any round-3 sandbox run. All eleven parse (lookbacks 671 to 1,989 hours);
the sandbox log stands at 49 rows, none of round 3.

1. W1 and sparse books: intended for this round. The screen is fixed for eleven books that stay in the market.
   A book that is in the market only in stated states needs a W1 of its own, fixed in the plan that registers it.
2. Calendar schedules and the speed limit: the reading is right, and it is as G6 means it. A weight path that
   repeats with the week is its own stale copy, so a schedule gets no credit in top30. A calendar field may
   select which hours of a data series feed a bin, as in W-05 and W-06.
3. W-01 and W-02: open, with a condition fixed now. They are not forms already run, but they move with
   continuation, whose readings on next30 and over the last 365 days of DEV are known and negative. For either
   of them W1 to W8 and both corners are not enough: before any recommendation one control is run from this
   round's budget, strategies/gen003_diag_plain_multiweek.omr with --set m=4 (plain four-week continuation,
   sampled weekly; registered in round 2 and never run), and the survivor's DEV Sharpe before costs must exceed
   the control's DEV Sharpe before costs by at least 0.5. Otherwise it is continuation in another form and is
   not recommended.
4. W-09: open. It has the opposite sign and a slower window than the activity fade of generation 2, whose small
   positive DEV reading argues against it rather than for it.
5. W-10: open as a new form (the premium's noise, not its level or its shock), and screen-only under KP-017: a
   survivor is not submitted before the per-program measurement, which the coordinator runs.
6. Calendar thresholds as params (W-05's a and b, W-06's d): accepted, with the standing of round 1's rulings 1
   and 2. G5 moves the edges of the session and of the weekend, and the programs must stand that.
7. W-11: accepted as one of the eleven. The selection rule takes it or its parts, never both. If it passes
   where none of its parts does, that is the arithmetic of a combination and is read as no more.
8. Controls: none in general for this round, except the one of ruling 3. Before any decision on a counted trial
   the coordinator may order one further DEV run for the survivor, recorded as an amendment before it runs.
9. Budget: the cap of 19 runs stands (11 defaults, at most 6 corner runs, 2 in reserve; the control of ruling 3
   comes out of the 6 or the 2). One run at a time; a run starts when at least 1,000,000 KB of physical memory
   and 4,000,000 KB of commit headroom are free.
10. The price of width, to be kept in mind when the outcome is read: eleven ideas meet one screen. If that
    screen let a no-skill book through 3 times in 100, one of eleven would pass by luck about 28 times in 100.
    A survivor is a candidate for one counted trial at most, and the number of ideas screened in the round goes
    into the record of that decision.
11. Stage 2 starts only after this plan and its programs are on the remote and the kernel's strategy test has
    passed with the new files in place. Its parts are appended below.

## Sandbox run log (round 3), filled in during stage 2

(Appended below the coordinator's round-3 rulings, so that the 169,613 bytes committed as 92d1a5a stay an unchanged
prefix. Every run is listed, in the registered order. Each command was `python -m omr.sandbox
strategies/gen003_wNN_<idea>.omr --g6-lags` at the defaults, full stage 1 (25 truncation cuts), one at a time, started
only after the memory reading of ruling 9 (free physical 2.8 to 5.9 million KB, virtual 10.4 to 12.6 million KB). Output
saved as ASCII in the session scratch folder, gen003_r3/run_NN_<name>.txt, by gen003_r3/run_sandbox.py, which only
calls the sandbox. Pre-cost = DEV Sharpe + (DEV Sharpe - G4 DEV). Years: return sign and Sharpe for 2020, 2021,
2022H1. Costs: equity over DEV, with C/G = costs / avg gross. Funding: gross paid / received over DEV.)

| # | idea | DEV SR | G4 DEV | G2 DEV | pre-cost | next30 | r(1), r(2), r(3) | A of 10; B | years + (SR 2020 / 2021 / 2022H1) | names held | avg gross | dir. ch. | costs (C/G) | funding paid / recv |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | W-01 high_anchor | 1.558 | 1.296 | 0.888 | 1.820 | 0.601 | 0.129, -0.080, -0.032 | 6; -0.549 | 2 (3.721 / 1.831 / -2.093) | 27.7 of 28.0 | 0.855 | 1198 | 0.3024 (0.354) | 0.7320 / 0.7938 |
| 2 | W-02 cost_basis | 1.049 | 0.794 | 0.438 | 1.304 | 0.755 | -0.026, -0.092, -0.013 | 9; -0.761 | 2 (3.469 / 0.787 / -2.290) | 27.7 | 0.854 | 1359 | 0.3138 (0.367) | 0.6814 / 0.7632 |
| 3 | W-03 vol_shock | -0.276 | -0.612 | -0.833 | 0.060 | 0.057 | -0.123, -0.028, 0.003 | 0; 1.331 | 1 (-1.491 / 0.046, return -0.031 / 0.500) | 22.8 | 0.808 | 1514 | 0.1536 (0.190) | 0.2654 / 0.2580 |
| 4 | W-04 illiquidity_shock | -0.156 | -0.530 | -0.875 | 0.218 | -0.407 | -0.108, -0.057, -0.015 | 1; 0.915 | 1 (-1.548 / -0.276 / 1.240) | 27.7 | 0.854 | 1705 | 0.1597 (0.187) | 0.3199 / 0.3056 |
| 5 | W-05 us_session_shift | -0.537 | -0.961 | -1.224 | -0.113 | -1.372 | -0.079, -0.013, -0.050 | 1; 0.574 | 1 (-0.568 / -1.771 / 1.491) | 27.6 | 0.857 | 2040 | 0.1771 (0.207) | 0.3076 / 0.3058 |
| 6 | W-06 weekend_tilt | -2.343 | -2.754 | -2.981 | -1.932 | -0.511 | -0.030, 0.022, -0.006 | 8; -0.816 | 0 (-2.837 / -3.281 / -0.658) | 27.7 | 0.854 | 2187 | 0.1268 (0.148) | 0.2110 / 0.1997 |
| 7 | W-07 wick_absorption | -0.932 | -1.225 | -1.660 | -0.639 | -0.902 | 0.083, 0.037, 0.035 | 7; -1.154 | 1 (-0.527 / -2.153 / 1.457) | 27.6 | 0.852 | 1266 | 0.1126 (0.132) | 0.3073 / 0.2819 |
| 8 | W-08 decoupling | -0.179 | -0.525 | -0.823 | 0.167 | -0.502 | -0.096, -0.034, 0.027 | 0; 0.980 | 1 (-0.938 / 0.011, return -0.032 / 0.378) | 27.6 | 0.855 | 1750 | 0.1655 (0.194) | 0.3193 / 0.3105 |
| 9 | W-09 volume_trend | -0.375 | -0.595 | -1.003 | -0.155 | 0.105 | -0.083, -0.194, -0.010 | 10; -2.147 | 1 (2.138 / -0.932 / -2.357) | 27.7 | 0.854 | 1155 | 0.1571 (0.184) | 0.4307 / 0.4791 |
| 10 | W-10 basis_instability | -0.188 | -0.568 | -0.861 | 0.192 | 0.670 | -0.101, -0.013, 0.006 | 9; -2.010 | 0 (-0.221 / -0.253 / 0.011, return -0.009) | 27.6 | 0.853 | 1904 | 0.1964 (0.230) | 0.3507 / 0.3544 |
| 11 | W-11 ensemble | 0.372 | 0.025 | -0.275 | 0.719 | 0.029 | -0.009, 0.023, 0.018 | 2; 0.248 | 2 (1.424 / -0.152 / 0.174) | 22.9 | 0.811 | 1321 | 0.2102 (0.259) | 0.3964 / 0.3933 |

Every run: stage 1 PASS, exit 0, nothing on stderr, not liquidated, 75 symbols ever in the unit, next30 over 100
symbols, benchmark (equal-weight long of the in-play members) DEV Sharpe 0.619, maxDD 0.847. Wall times 82.0 to 232.9 s.
Other printed numbers (PSR(0); total; maxDD; rebalances): W-01 0.993, 1.215, 0.292, 571; W-02 0.953, 0.777, 0.386, 602;
W-03 0.332, -0.219, 0.477, 691; W-04 0.403, -0.129, 0.355, 574; W-05 0.203, -0.297, 0.521, 611; W-06 0.000, -0.767,
0.798, 650; W-07 0.067, -0.405, 0.517, 570; W-08 0.389, -0.159, 0.399, 597; W-09 0.276, -0.264, 0.503, 634; W-10
0.384, -0.155, 0.352, 583; W-11 0.721, 0.153, 0.252, 754. Stale-copy medians in the paired reading: -0.528, -0.437,
-0.684, -0.735, -1.047, -0.504, 0.354, -0.237, -0.401, -0.285, 0.043. Speed-limit rows from 2020-07-20 14:00 (2020-08-31
for W-03 and W-11) to 2022-06-30 22:00; paired lags 30 to 262 days, decisions 2021-06-30 23:00 to 2022-06-30 22:00.

Total sandbox runs in round 3: 11 of the cap of 19 (11 defaults; no corner, no control, no reserve). No stage-1
rejection, no kernel fault, no refusal. ledger/sandbox_log.jsonl now has 60 rows (49 + 11), rows 49 to 59 (0-indexed),
each status ok, stage1 full, its logged readings equal to the printed ones and its source_sha256 equal to the committed
file's; `omr.ledger verify` OK, all six chains; `omr.kernel_lock verify` OK, sealed (core 0.05, top30 0.1). Generation
3 has used 17 of 60 sandbox runs.

By the run order, corners were due only for ideas that passed W1 to W8, and the control of ruling 3 only if W-01 or
W-02 passed its corners. None passed W1 to W8, so no corner and no control was run.

## Amendments (round 3), stage 2

none: no program text, param, default, screen item or run condition was changed, and the reserve was not used.

## Screen outcome per idea (round 3)

| idea | W1 | W2 (pre-cost >= 1.5) | W3 (G4 > 0) | W4 (G2 > 0) | W5 (next30 >= 0.3) | W6 (r <= 0.40) | W7 (A <= 4, B > 0) | W8 (years) | first failed | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| W-01 high_anchor | pass | pass (1.820) | pass | pass | pass | pass | FAIL (6; -0.549) | pass (2) | W7 | dropped |
| W-02 cost_basis | pass | FAIL (1.304) | pass | pass | pass | pass | FAIL (9; -0.761) | pass (2) | W2 | dropped |
| W-03 vol_shock | pass | FAIL (sign: -0.276) | FAIL | FAIL | FAIL (0.057) | pass | pass (0; 1.331) | FAIL (1) | W2 | dropped |
| W-04 illiquidity_shock | pass | FAIL (sign: -0.156) | FAIL | FAIL | FAIL | pass | pass (1; 0.915) | FAIL (1) | W2 | dropped |
| W-05 us_session_shift | pass | FAIL (sign: -0.537) | FAIL | FAIL | FAIL | pass | pass (1; 0.574) | FAIL (1) | W2 | dropped |
| W-06 weekend_tilt | pass | FAIL (sign: -2.343) | FAIL | FAIL | FAIL | pass | FAIL (8; -0.816) | FAIL (0) | W2 | dropped |
| W-07 wick_absorption | pass | FAIL (sign: -0.932) | FAIL | FAIL | FAIL | pass | FAIL (7; -1.154) | FAIL (1) | W2 | dropped |
| W-08 decoupling | pass | FAIL (sign: -0.179) | FAIL | FAIL | FAIL | pass | pass (0; 0.980) | FAIL (1) | W2 | dropped |
| W-09 volume_trend | pass | FAIL (sign: -0.375) | FAIL | FAIL | FAIL (0.105) | pass | FAIL (10; -2.147) | FAIL (1) | W2 | dropped |
| W-10 basis_instability | pass | FAIL (sign: -0.188) | FAIL | FAIL | pass (0.670) | pass | FAIL (9; -2.010) | FAIL (0) | W2 | dropped |
| W-11 ensemble | pass | FAIL (0.719) | pass (0.025) | FAIL (-0.275) | FAIL (0.029) | pass | pass (2; 0.248) | pass (2) | W2 | dropped |

Against each registered falsifier ("the DEV screen fails; the sign is never flipped"): all eleven falsified on DEV.
Eight had the wrong sign over DEV (W-03 to W-10). W-01 was the only idea to clear the pre-cost floor, the stresses,
next30 and the speed limit, and it failed the paired reading: on the last 365 days of DEV it lost on the common names
(B -0.549) and 6 of 10 stale copies did at least as well.

## DEV observations (round 3; NOT hypotheses, never to be submitted from this plan)

- Two time profiles. The books that lean toward recent winners (W-01 and W-02 rank price against a recent reference;
  W-09 ranks volume growth, which goes with rising prices) earned in 2020 (SR 2.1 to 3.7) and lost in 2022H1 (SR -2.1
  to -2.4) and on the last 365 days (B -0.55 to -2.15), the profile of round 2's continuation books (LESSONS 44). The
  unsigned or move-orthogonal books (W-03, W-04, W-05, W-07, W-08) lost in 2020 and earned in 2022H1 (SR 0.38 to 1.49);
  four of them had a positive book median on the last 365 days with stale copies negative (A 0 to 1, B 0.57 to 1.33).
  No registered book earned in both halves of DEV. A rule built on this split would descend from this result. WEAK.
- Unlike round 2's continuation books, W-01 and W-02 read positive on next30 (0.601, 0.755), and W-01 kept 0.888 under
  G2 and 1.296 under G4. Its failure was the last year of DEV, which ruling 3's concern pointed at. WEAK.
- W-06 lost in every DEV year (-2.343, the largest absolute Sharpe of the round): coins whose share of volume moved
  toward the weekend did BETTER the next week, in the direction of round 1's H1 (the weekend part of the move
  persisted, LESSONS 39). DEV is spent as a screen for the mirror. WEAK.
- Costs: W-01 and W-02 paid 0.302 and 0.314 of equity over DEV (C/G 0.35 and 0.37), like the continuation books
  (LESSONS 45), although their reference moves slowly; their G4 drops (0.262, 0.255) still matched the registered drag
  of 0.25, because their volatility was higher. The unsigned weekly books cost 0.113 to 0.196 (C/G 0.13 to 0.23), the
  cheapest weekly top30 books read so far; their G4 drops were 0.29 to 0.42.
- Funding: W-01 and W-02 paid and received 0.73 / 0.79 and 0.68 / 0.76 of equity in gross funding over DEV, the largest
  flows of any top30 book read by the sandbox (G2 drops 0.670 and 0.611); the unsigned books 0.20 to 0.35 each way.
- Speed limit: every reading between -0.194 and 0.129; W-01's six-week reference read 0.129 at one step, under the
  0.3 to 0.4 the plan feared. Names held 27.6 to 27.7 of 28.0 for every book without a cs_* inside a window, 22.8 and
  22.9 for W-03 and W-11 (fact 3 of the plan).
- W-11 read 0.372 (pre-cost 0.719; 2020 SR 1.424, 2022H1 0.174): its early-earning part (W-01) and its late-earning
  parts (W-03 and W-07, which lost early) partly cancelled. WEAK.
- WEAK throughout: one DEV period, one default each, one researcher session; nothing here is a parameter
  recommendation, and no corner or control was run.

## Recommendation (round 3)

NONE. By the pre-registered selection rule an idea is eligible only if it passes W1 to W8 at the default and both
corners. No idea passed W1 to W8 (W-01 failed W7; the other ten failed W2 first), so no corner was run, the control of
ruling 3 was not due, and no program from version 3 is recommended. No KP-017 or KP-020 measurement is needed for this
round. Generation 3 stands at 0 of 5 counted submissions and 17 of 60 sandbox runs; M is unchanged at 6.

Correction to the first DEV observation above (same session, found on re-reading before the report; nothing above is
changed): "No registered book earned in both halves of DEV" holds for the ten single-idea books. The combination W-11
was positive in 2020 (SR 1.424) and, barely, in 2022H1 (SR 0.174), its parts' opposite profiles cancelling; its DEV
Sharpe was 0.372 and it failed W2. The recommendation is unchanged: NONE.

# Generation 3 - PLAN, version 4 (round 4, the second wide screen, pre-registered 2026-11-27 before any round-4 sandbox run)

Researcher session for generation 3, round 4, stage 1. Unit top30. A fresh session: everything it knows of the project
comes from the files below. Appended below version 3 and its stage-2 parts; the 180,229 bytes before this line (sha256
7b27f7c6ea7c621c...) are unchanged.

- Kernel: `omr.status` OK d09812fdec752a17, semantic 7d923e7e2375986d, text b74122f3f9821056, sealed (G6 core 0.05,
  top30 0.10). Data research_hash 28d9084a8c5c7659, validated, snapshot_end 2026-11-18 10:00 UTC.
- Ledger: M = 6 (generation 0: 4, 1: 1, 2: 1, 3: 0 of 5), N 5.90, rho 0.021, Tier 1 0, pool 0 of 5, one uncounted
  stage-1 rejection. Sandbox log 60 rows; generation 3 has used 17 of 60 sandbox runs.
- Read: RESEARCH_PLAYBOOK.md (all; 3, 4, 4b, 5 and 8b with care), generations/META_REVIEW_2026-11-26.md (all),
  LESSONS.md (51), LANGUAGE.md (all), CONSTITUTION.md 4 to 7 and 13, generations/gen003/REPORT.md (rounds 1 to 3),
  generations/gen003/PLAN.md version 3 in full (facts, ideas, rulings, run log, screen outcome, DEV observations,
  correction), rows 49 to 59 of ledger/sandbox_log.jsonl, `omr.status`, `omr.ledger summary`. Kernel code read only for
  what the parser returns (omr/lang.py: Program, parse_file). Shapes: strategies/gen003_w01, w03, w04, w05, w08 and the
  two plain controls of round 2 (gen003_diag_plain_multiweek, gen003_diag_plain_week).
- Not opened: data/, ledger/returns/, ledger/trials/, calibration files, audits/. No project program was run on data:
  only `omr.status`, `omr.ledger summary` and a parse-only check (scratch gen003_r4/parse_check.py; omr.lang.parse_file).
- Numbers seen before writing: every DEV number of generations 2 and 3 (REPORTs, run logs, sandbox rows 40 to 59), the
  review's tables and bar, and the VAL rows of the six counted trials. No VAL or DEV number exists for any program below.
- Files of this version: this text and eleven new programs, strategies/gen003_x01_* to gen003_x11_*. Nothing else.

Facts from the kernel's rules that shaped the list (behaviour, not results):
1. cs_scale(x) divides by sum(abs(x)), so a row-constant market state s in cs_scale(cs_demean(s * y)) survives only as
   its sign: the route-(b) books keep gross 1 in both states and stay in the market (W1); no state can thin them.
2. No program puts a cs_* inside a rolling window (round 3, fact 3): every cross-section is taken on a weekly series, so
   names held should stay near round 3's 27.6 of 28. States and betas come from btc() series only.
3. A lag with the literal 1 around a return with the literal 1 is a hidden window (nested_unit_window), and a lag param
   needs default - 1 >= 1 inside its range: X-08 takes the lagged move as logret(x, j) - logret(x, 1) with j = 3 (the
   two hours before the current one), so G5 moves it between one and three hours, never to an empty window.
4. tf_mean takes only a dimensionless series: flow enters as the imbalance share (2 x taker-buy - total) / total quote
   volume, written without a literal; taker-side VWAPs come from weekly sums (taker_buy_quote_volume / taker_buy_volume
   has the unit of price; the taker-sell side is the rest of the volume).
5. weekly(close) on the hourly grid holds the last completed week and switches at the bin's last hour (X-02's caveat).

Considered, not registered: funding-reading forms (each I could write was contrarian, a carry level, or the funding x
return interaction of #20); a spot-perp lead split of the move (a composition of the move); a variance-ratio rank (no
sign I can defend unsigned; signed, a coin-state composition of the move); net flow in BTC's down hours minus its up
hours (it ranks a flow beta, a persistent tilt whose sign follows the market); a factor-momentum switch on continuation
(the market-state form was kept: its outside evidence is about momentum itself); W-01 conditioned on a state (descended
from W-01's result, pre-cost 1.820 < 2.5, and aimed at its known W7 failure); a non-equal combination of this round's
ideas (it hides tests inside one program).

## The screen, fixed now, the same for every idea (W1 to W8)

W1 stage 1 passes with at least 30 direction changes, average gross at least 0.5, at least 15 names held on average, not
liquidated; W2 DEV Sharpe before costs (the DEV Sharpe plus the drop under G4's reading, i.e. DEV Sharpe + (DEV Sharpe -
G4 DEV Sharpe)) at least 1.5; W3 G4's DEV reading positive; W4 G2's DEV reading positive; W5 next30 DEV Sharpe at least
0.3; W6 the speed-limit statistic at most 0.40 at each of one to three steps (a reason line fails); W7 in the paired
reading at most 4 of 10 stale copies at least as good as the book AND the book's median Sharpe over the last 365 days of
DEV positive (a refused reading fails); W8 at least two of the three DEV years positive. A wrong sign is a failure; no
sign is ever flipped; no default is changed after a run. No sparse book (a book flat much of the time fails W1; the
state must enter the signal while the book stays in the market).

Numbers are taken as the sandbox prints them (full stage 1, no --quick, with --g6-lags): the stage-1 line, "DEV
Sharpe", "rebalances ... avg gross ... liquidated", the per-year rows (2020, 2021, 2022; a year is positive when its
return is above 0), and the KP-018 block (r(1) to r(3), next30, G2 and G4 on DEV, names held, the paired reading A of 10
and book median B). Every idea's registered sign is the sign of its signal line; a negative DEV Sharpe fails W2.

## The bar, shared arithmetic (playbook 8b)

- Cost drag = the Sharpe that 1x costs take, i.e. the expected G4 drop. Measured for weekly top30 books: 0.23 to 0.46
  (review 2.3); in round 3, 0.29 to 0.42 for unsigned weekly books (C/G 0.13 to 0.23, LESSONS 50) and 0.26 for the
  reference books; 0.23 to 0.34 for round 2's continuation books (C/G 0.29 to 0.45, LESSONS 45). Registered here:
  - 0.40: a rank re-drawn every week from one week's input (X-01, X-02, X-04, X-05, X-06, X-10);
  - 0.30: a rank from two-week or longer windows, sampled weekly (X-03, X-07, X-08);
  - 0.35: X-09, a continuation-type book plus whole-book flips when its state changes (estimate 10 to 20 flips over
    DEV, each trading twice the gross: 0.01 to 0.02 a year per unit of gross);
  - 0.25: X-11, slow beta ranks whose turnover is mostly state flips (estimate 30 to 45 over DEV, about 0.04 a year per
    unit of gross), on a beta spread more volatile than a rank book of the same gross.
- Sharpe needed in VAL before costs: 0.74 + drag for G1's line, 1.5 + drag for decent odds. Drag 0.25: 0.99 / 1.75;
  0.30: 1.04 / 1.80; 0.35: 1.09 / 1.85; 0.40: 1.14 / 1.90.
- G2 takes another 0.5 to 0.8 on DEV from any full book (LESSONS 42); W4 asks only that its DEV reading stay positive.
- W2's 1.5 is a floor, not the bar: with the decay the review estimates, 2.5 to 3.5 before costs on DEV would be needed
  to expect 1.5 in VAL. For the three route-(b) ideas the DEV readings are partly predictable (below), so a pass says
  even less. A pass is a candidate for one counted trial, nothing more.

## Disclosures for every idea

- The author model has read this market's history through DEV, VAL and the vault, and this session every DEV number of
  generations 2 and 3. No rule names a date, coin, price level or event; every tunable number is a declared param (no
  file has a jitterable literal). That does not remove hindsight from the CHOICE of ideas (KP-010).
- Remembered DEV path: the 2020 to 2021 bull with the May 2021 crash, the 2022 bear (January, LUNA in May, Celsius and
  Three Arrows in June). The sign of BTC's 2-week and 8-week returns through DEV is therefore roughly known to the
  author, and so are VAL's broad phases (2022H2 bear with FTX, 2023 recovery, 2024 rally with the spot ETFs): for the
  route-(b) states this is the KP-010 channel at its widest. Remembered DEV readings: all of LESSONS 39 to 50.
- Microstructure: I remember no result of any rule like X-01 to X-08, in crypto or elsewhere, in VAL or anywhere.
- Eleven ideas against one screen: if a no-skill book passed it 3 times in 100, one of eleven would pass by luck about
  28 times in 100 (round 3's ruling 10).

## The ideas

All eleven: kind portfolio, unit top30, rank weights cs_scale(cs_demean(cs_rank(.))) (X-09 to X-11 times a state's
sign), dollar neutral, gross 1, decided once a week (a weekly series visible at the bar that opens Sunday 23:00 UTC,
traded at the Monday 00:00 open). No funding, mark or index input in any of them: playbook 4b's funding restriction does
not arise; KP-020 does for any pass. imb = the hour's taker imbalance, (taker-buy - taker-sell) quote volume / quote
volume; rr = the hour's return minus BTC's. "Net of the move" = round 3's W-04 fit: on every weekly bin the score is
replaced by its residual on x, the week's (X-03: m weeks') log return over annualised daily volatility of n days.
Classes I to N are route (a), S1 to S3 route (b). Lookbacks at every window param's high bound, from the parse check.

### X-01 gen003_x01_taker_vwap_gap (route (a), class I: volume at price)
- Rule: g = (taker-buy VWAP - taker-sell VWAP) / (high - low) over the weekly bin, net of the move; short the largest,
  long the smallest. n = param(28, 22, 34); `g = (bq / bv - (q - bq) / (v - bv)) / (weekly(high) - weekly(low))` on
  weekly sums. 56 nodes, lookback 1,197 h.
- Mechanism: takers who buy more as the price rises and sell more as it falls are positive-feedback traders (De Long,
  Shleifer, Summers and Waldmann 1990); the chase premium they pay fades. Other side: patient sellers into the chase.
- Not one of the 39: it reads at what prices each side traded, not the flow's size or sign (#14, core's taker flow) nor
  the move or its parts.
- Both markets: chasing is measured on both sides and net of the week's move; nothing in it needs a rising market.
- Drag 0.40 -> before costs in VAL 1.14 line / 1.90 odds. Outside evidence: theory only; none on returns that I know.
- Bias: nothing specific I can name. Risk: in quiet weeks the gap is small against the range (noise).

### X-02 gen003_x02_vwap_twap_gap (route (a), class I: volume at price)
- Rule: g = (VWAP - TWAP) / range over the weekly bin, all relative to the previous week's close, net of the move; short
  the largest (volume at the week's highs), long the smallest. n = param(28, 22, 34);
  `twap = tf_mean(close / weekly(close), weekly)`,
  `vwap = weekly(quote_volume) / weekly(volume) / lag(weekly(close), 1)`.
  58 nodes, lookback 1,197 h. Caveat (fact 5): the TWAP's last hour reads its own close (weight 1/168).
- Mechanism: heavy trading at a week's upper prices is late demand absorbed by sellers (distribution); at its lower
  prices, forced supply absorbed by patient buyers (accumulation); the absorbing side is the better informed. Other
  side: late buyers at highs, capitulating sellers at lows.
- Not one of the 39: W-02 compared the CLOSE with a 4-week VWAP (a reference price) and #24 split the MOVE by heavy
  hours; this is the covariance of volume with the price level inside the week, with no closing price in it.
- Both markets: net of the move, symmetric legs. Drag 0.40 -> 1.14 / 1.90. Outside evidence: none academic (chart lore).
- Bias: W-07, another "absorption" story (wicks), lost on DEV (-0.932). The selection takes at most one of class I.

### X-03 gen003_x03_impact_asymmetry (route (a), class J: liquidity asymmetry)
- Rule: over the last m weekly bins, bu = mean rr in net-buying hours / mean imb in them, se = the same in net-selling
  hours; a = (bu - se) / (|bu| + |se|), net of the m-week move; long the largest. m = param(2, 1, 3),
  n = param(28, 22, 34); `bu = sma(tf_mean(where(imb > 0, rr, 0), weekly), m) / sma(tf_mean(where(imb > 0, imb, 0),
  weekly), m)`. 90 nodes, lookback 1,197 h.
- Mechanism: market makers thin the side of the book where they fear informed flow (Glosten and Milgrom 1985): a thinner
  offer than bid says liquidity providers expect buyers to be right. Other side: sellers trading into the deep bid.
- Not one of the 39: W-04 read the size of price impact against its norm (unsigned); this is the difference between the
  impact of buying and of selling, a signed measure no earlier program read.
- Both markets: moves relative to BTC and net of the coin's own move; the asymmetry can point either way in any market.
- Drag 0.30 -> 1.04 / 1.80. Outside evidence: buys move equity prices more than sells (Chan and Lakonishok 1993; Saar
  2001), a description, not a forecast; none on returns. Bias: nothing specific.

### X-04 gen003_x04_informed_flow (route (a), class K: information in flow)
- Rule: score = c x f at the week's last hour, c = corr(previous hour's imb, this hour's rr) over n hours, f = the
  week's mean imb; long the largest. n = param(672, 537, 807); `c = tf_last(corr(lag(imb, 1), rr, n), weekly)`. 28 nodes,
  lookback 1,142 h.
- Mechanism: flow whose impact persists carries information (Kyle 1985; Hasbrouck 1991) and this week's net direction is
  not yet fully priced; flow whose impact reverses is liquidity trading whose pressure fades. Other side: liquidity
  providers to informed flow; the takers of reverting flow.
- Not one of the 39: #14 ranked flow net of the week's return (contrarian) and core's taker_flow_long went with the flow
  level; here the flow's sign is weighted by its measured informativeness, which flips it where c < 0 (question 5).
- Both markets: both terms are coin-specific (rr relative to BTC); symmetric legs.
- Drag 0.40 -> 1.14 / 1.90. Outside evidence: order-flow predictability in crypto at minutes to hours (recalled,
  unverified); none at a week. Bias: LESSONS 17 (flow net of return continued on DEV); where c > 0 the book leans that
  way. Noise: c's standard error over 672 hours is about 0.04.

### X-05 gen003_x05_stealth_flow (route (a), class K: information in flow)
- Rule: s = volume-weighted imb in the week's quiet hours (quote volume under its own trailing w-hour median) minus in
  its other hours, net of the move; long the largest. w = param(168, 134, 202), n = param(28, 22, 34). 77 nodes,
  lookback 1,197 h.
- Mechanism: stealth trading (Barclay and Warner 1993): informed traders work orders when they are least seen and move
  the price least; the busy hours carry the crowd. Other side: passive sellers in quiet books; the crowd in busy hours.
- Not one of the 39: #24 split the MOVE by heavy hours (contrarian); this splits the FLOW by quiet hours, net of the
  move; not a level or burst of activity (#12, #13), not a calendar share (W-05, W-06).
- Both markets: a difference between two flows of the same coin, net of its move; symmetric.
- Drag 0.40 -> 1.14 / 1.90. Outside evidence: for, Barclay and Warner 1993 (equities); against, Admati and Pfleiderer
  1988 (informed traders cluster in busy hours). None in crypto. Bias: busy-hour flow travels with busy-hour moves, so
  -hf leans against them, #24's sign (DEV -0.256).

### X-06 gen003_x06_flow_toxicity (route (a), class L: adverse-selection premium)
- Rule: t = the week's mean of |imb| x sqrt(trades / its own trailing w-hour mean); shock = t / its mean over m weekly
  bins; long the largest. w = param(168, 134, 202), m = param(4, 3, 5). 24 nodes, lookback 1,208 h.
- Mechanism: a rise in informed trading makes uninformed holders mark the coin down and demand more to hold it (Easley,
  Hvidkjaer and O'Hara 2002; Easley and O'Hara 2004). Other side: liquidity providers facing informed takers. The trade
  factor removes the one-sidedness that fewer trades alone produce (random signs give |imb| about 1/sqrt(trades)).
- Not one of the 39: no program read the one-sidedness of flow; but it is a shock against the coin's own norm like W-03
  and W-04, and the trade count enters it (#12): question 4.
- Both markets: unsigned; nothing in it depends on direction.
- Drag 0.40 -> 1.14 / 1.90. Outside evidence: the PIN premium in equities, disputed (Duarte and Young 2009 trace it to
  illiquidity); crypto none. Bias: W-04 (long when liquidity providers bear more risk) had the wrong sign (-0.156).

### X-07 gen003_x07_convexity_shift (route (a), class M: asymmetric comovement)
- Rule: conv = (up-beta - down-beta to BTC over k hours) - (the same over n hours) at the week's last hour; short the
  largest, long the smallest. k = param(336, 268, 404), n = param(1344, 1075, 1613); up-beta = sma(where(rb > 0, r x rb,
  0)) / sma(where(rb > 0, rb x rb, 0)), down-beta on the other hours. 63 nodes, lookback 1,948 h.
- Mechanism: upside participation is overpaid (coskewness, Harvey and Siddique 2000); a coin that has lately turned
  concave must pay to be held. Other side: leveraged speculators wanting coins that rise with BTC more than they fall.
- Not one of the 39: W-08 read the change of the plain correlation; this reads the asymmetry of beta between BTC's rises
  and falls; #15 and #27 read the coin's own skewness, not its co-movement (question 6).
- Both markets: direction-free but volatility-dependent: while the asymmetry persists the book is short convexity and
  loses on large BTC moves of either sign; stated, not hidden.
- Drag 0.30 -> 1.04 / 1.80. Outside evidence: coskewness and downside beta are priced in equities (Harvey and Siddique
  2000; Ang, Chen and Xing 2006) as characteristics, not as shifts; crypto none I can verify. Bias: nothing specific.

### X-08 gen003_x08_price_delay (route (a), class N: delayed response)
- Rule: dl = corr(coin's hourly log return, BTC's log return over the j - 1 hours before) - corr(coin's over those
  hours, BTC's hourly) over n hours, at the week's last hour; long the most delayed, short the leaders.
  j = param(3, 2, 4), n = param(336, 268, 404). 27 nodes, lookback 742 h.
- Mechanism: price delay (Hou and Moskowitz 2005): coins whose prices take market news late are followed by fewer
  arbitrageurs and market makers, and holders are paid for that neglect. Other side: no loser by design; a premium.
- Not one of the 39: no earlier program read a lagged correlation; W-08's decoupling was contemporaneous (question 6).
- Both markets: the lag structure is direction-free; the follower-minus-leader form removes own autocorrelation.
- Drag 0.30 -> 1.04 / 1.80. Outside evidence: strong in equities, as a persistent characteristic, which G6 does not
  credit; only its week-to-week change is tested. In a top 30 followed by arbitrage bots it is likely tiny.
- Bias: nothing specific.

### X-09 gen003_x09_state_continuation (route (b), class S1: market-direction state; DEV-informed)
- Rule: s x rank(x), s = sign of BTC's ls-day log return, x = the coin's k-day log return over its own daily volatility
  of k days. k = param(21, 16, 26), ls = param(56, 44, 68). 22 nodes, lookback 2,013 h.
- DEV-informed (LESSONS 44 and 48: winner-leaning books earned in 2020 and lost in 2022H1). Its readings over all of DEV
  and by year are partly predictable from #26 (2020 SR 2.015, 2022H1 -2.716) and are NOT evidence.
- Reason for the conditioning, from outside this project: Cooper, Gutierrez and Hameed (2004): US equity momentum
  earned after up markets (about 0.9% a month, as I recall) and lost after down markets; Daniel and Moskowitz (2016):
  momentum crashes in rebounds after bear markets, when past losers are the high-beta names. Mechanism: overconfidence
  and inflows after gains feed continuation; after losses, forced deleveraging overshoots in the losers. How sure:
  moderate for equities at monthly horizons; low for crypto at a week; no crypto test I can verify.
- Not one of the 39 only through the switch: in each state it holds a closed form (continuation, or its reversal)
  (question 1). #26 had a positive DEV Sharpe, so the reversal half is not the mirror of a losing book.
- Drag 0.35 -> 1.09 / 1.85. Control: the run order's route-(b) condition (question 3).
- Bias: the author roughly knows when BTC's 8-week return was positive in DEV and VAL; ls = 56 days (8 weeks) was
  chosen as a round slow window inside the 90-day lookback (2,013 h at its high bound), not from a remembered path.

### X-10 gen003_x10_stress_reversal (route (b), class S2: volatility state; DEV-informed)
- Rule: s x rank(x), s = sign(BTC's daily volatility over b days - over a days) (+1 calm, -1 stressed), x = the k-day
  log return over own daily volatility of a days. k = param(7, 5, 9), a = param(14, 11, 17), b = param(56, 44, 68).
  26 nodes, lookback 2,013 h.
- DEV-informed (LESSONS 44 and 48). One-week continuation (#28) and one-week reversal (#11) both lost in 2022H1, so its
  yearly rows are less predictable than X-09's; they are not evidence either way.
- Reason for the conditioning: Nagel (2012): the return to short-term reversal (liquidity provision) rises with market
  volatility as liquidity supply shrinks; Hameed, Kang and Viswanathan (2010): reversal is strongest after market
  declines. How sure: moderate for equity reversal in high-volatility states; low for the calm continuation half and
  for crypto at a week.
- Not one of the 39 only through the switch: one-week continuation when calm, its reversal under stress; the calm half
  has the sign of #11's mirror (#11 lost in all years; #28 registered that sign after it): question 2.
- Drag 0.40 -> 1.14 / 1.90. Control: the run order's route-(b) condition. Bias: DEV's stress episodes are remembered
  (March 2020, May 2021, 2022).

### X-11 gen003_x11_trend_beta (route (b), class S3: market-trend state through beta; DEV-informed)
- Rule: s x rank(bt), s = sign of BTC's ls-day log return, bt = the coin's hourly beta to BTC over n hours (corr x std
  ratio). n = param(672, 537, 807), ls = param(14, 11, 17). 29 nodes, lookback 1,142 h.
- DEV-informed: in 2020 the winners were largely the high-beta coins, so its up-state half resembles the winner-leaning
  books of LESSONS 48; its readings are partly predictable and not evidence.
- Reason for the conditioning: time-series momentum of the crypto market at one to four weeks (Liu and Tsyvinski 2021,
  data to 2018; Moskowitz, Ooi and Pedersen 2012 across assets). Against it, here: core's trend rules showed no timing
  beyond drift in VAL (LESSONS 4, 8, 9). How sure: low.
- Not one of the 39: a beta tilt alone is a persistent characteristic (no G6 credit); signed by the state it is a
  dollar-neutral market-timing book, which no top30 program was; core's trend switches were long-biased (question 8).
- Drag 0.25 -> 0.99 / 1.75. Risk: W6 if the state stays one-signed for months (beta ranks persist). Bias: as X-09.

## Run order and budget (decided now)

- Runs 1 to 11: the defaults, in the order X-01 to X-11 (route (b) last), each
  `python -m omr.sandbox strategies/gen003_xNN_<idea>.omr --g6-lags`, one at a time under the coordinator's memory rule.
  Every default runs, whatever the earlier ones read.
- Then corners, only for ideas that passed W1 to W8, in the selection order below: the 0.8 corner, then the 1.2 corner
  (`--set`), each needing a positive DEV Sharpe AND a positive G4 DEV reading; stop that idea at its first failure. At
  most 6 corner runs; if more than three ideas pass W1 to W8, corners for the first three in the selection order.
- Corners (integers rounded; a param left unchanged by rounding moves by 1):

  | idea | 0.8 corner | 1.2 corner |
  |---|---|---|
  | X-01 | n=22 | n=34 |
  | X-02 | n=22 | n=34 |
  | X-03 | m=1, n=22 | m=3, n=34 |
  | X-04 | n=538 | n=806 |
  | X-05 | w=134, n=22 | w=202, n=34 |
  | X-06 | w=134, m=3 | w=202, m=5 |
  | X-07 | k=269, n=1075 | k=403, n=1613 |
  | X-08 | j=2, n=269 | j=4, n=403 |
  | X-09 | k=17, ls=45 | k=25, ls=67 |
  | X-10 | k=6, a=11, b=45 | k=8, a=17, b=67 |
  | X-11 | n=538, ls=11 | n=806, ls=17 |

- Control, route (b) only, a condition fixed now (question 3): before X-09 or X-10 can be recommended, its state-free
  control runs at its default (X-09: strategies/gen003_diag_plain_multiweek.omr, plain 3-week continuation; X-10:
  strategies/gen003_diag_plain_week.omr, plain one-week continuation; both registered in round 2 and never run), and
  the survivor's DEV Sharpe before costs must exceed the control's by at least 0.5. X-11 has no state-free form that is
  not a persistent tilt; none is registered for it. A control run comes out of the 6 corner runs or the reserve.
- Reserve: 2 runs, only for an honest restatement after a stage-1 rejection of a default (the restated file is recorded
  as an amendment before its run). Cap 19 runs (11 + 6 + 2), so generation 3 would have used at most 36 of 60.
- No counted run is part of this plan.

## Selection rule (fixed now; the DEV Sharpe ranks nothing beyond the screen)

- Eligible: passes W1 to W8 at the default and both corners; for X-09 and X-10 also the control condition above.
- Order: (1) route (a) before route (b), because route (b)'s DEV readings are partly predictable; (2) A in the paired
  reading, fewest stale copies at least as good first (the reading built like G6); (3) the registered cost drag,
  smallest first; (4) the run order.
- Take the first eligible idea; then the next eligible idea of another class (class I holds X-01 and X-02, class K holds
  X-04 and X-05; every other idea is its own class). At most two; at most one of route (b).
- A recommendation is not a submission: the coordinator reads the program and decides; at most one counted trial
  without a further decision; any top30 pass is measured per program in null worlds before the pool (KP-020). No
  program here reads funding or the basis, so no KP-017 measurement is asked for.
- If nothing is eligible, the recommendation is NONE.

## Questions for the coordinator

1. Route (b) and closed inputs: X-09 and X-10 hold a closed form in each state (continuation, or its reversal) and are
   new only through the state switch; X-11 holds a beta tilt, a persistent characteristic, signed by the state. Are they
   accepted as route (b)? And playbook 8b limits rules descended from a DEV result to parents with a pre-cost DEV
   Sharpe of at least 2.5 (X-09's nearest parents #26 0.77 and W-01 1.82; X-10's #28 1.17): does this order's route-(b)
   frame (at most three, each said to be DEV-informed) supersede that limit for these three?
2. X-10's calm half has the sign of the mirror of #11, a book that lost in all three DEV years (LESSONS 16); round 2
   registered that sign as #28 after it. Held only in calm states, is it a mirror under this order's rule?
3. Route-(b) control: accept the condition written in the run order (state-free control at its default, the survivor's
   pre-cost at least 0.5 above the control's, from the corner budget or the reserve)? Any control wanted for X-11?
4. X-06 reads an input no program has read (flow one-sidedness, normalised by the trade count), but as a shock against
   the coin's own norm, like W-03 and W-04, with trades inside it (#12). Open, or a closed shock or activity form? If
   closed, the round has ten ideas and its cap becomes 18.
5. X-01 to X-06 read taker volumes. The stop list names weekly books on "flow residuals"; none of these ranks flow net
   of the return (#14) or the flow level. X-04 weights the week's flow by its measured informativeness, so where flow has
   been informative it leans with the flow (the direction of #14's mirror, LESSONS 17). Open as written?
6. X-07 (beta asymmetry) and X-08 (lead-lag) read co-movement with BTC, whose decoupling form (W-08) is closed. They are
   labelled two classes (M and N); if they count as one, that class holds two. Open?
7. Is X-02's TWAP caveat (fact 5: the bin's last hour reads its own close, a 1/168 weight) acceptable as written, or
   should the TWAP be restated before any run?
8. X-11 is market timing through a dollar-neutral beta spread; core's G6 found no timing beyond drift in three trend
   trials (LESSONS 4, 8). Kept at low odds as the third route-(b) slot: keep, or strike before the runs?

Written 2026-11-27 09:55 +08:00 (2026-11-27 01:55 UTC), before any round-4 sandbox run.

## Coordinator's rulings before round 4's run 1 (2026-11-27; appended by the coordinator, nothing above is changed)

The coordinator read version 4's head, screen, run order, selection rule and questions, and every one of the
eleven programs (the source read of playbook section 5: no constant, threshold or scale built from a calendar
field or a same-unit ratio; each market state is the sign of a real BTC series; the taker imbalance is written
as buy + buy - total instead of 2 x buy - total, a fixed identity and not a tuned number, so nothing is hidden
from G5), before any round-4 sandbox run. All eleven parse (lookbacks 742 to 2,013 hours); the sandbox log
stands at 60 rows, none of round 4.

1. Route (b): X-09 and X-10 are route (b) and are accepted on the frame's terms. For these seats only, the
   frame sets aside playbook 8b's rule that a descended idea needs a parent of 2.5 before costs: that rule
   guards a single parent's descendant, while a state-conditional form is a new construction whose fit to DEV
   is partly by design. That is exactly why its readings over the whole of DEV and by year are not evidence,
   why the control of ruling 3 applies, and why any counted trial would have to rest on the reason from outside
   this project and on the items the design cannot fix.
2. X-10's calm half: not a banned mirror. A mirror is a sign flip of a book that failed; X-10 switches between
   two forms that were both registered and both failed on their own (round 2's one-week continuation and
   generation 2's one-week reversal), which is what route (b) is for.
3. The control condition for X-09 and X-10: accepted as written (a survivor's DEV Sharpe before costs must
   exceed its state-free control's by at least 0.5; the controls gen003_diag_plain_multiweek at its default
   and gen003_diag_plain_week, from the corner budget or the reserve).
4. X-06: open. It ranks a shock in the one-sidedness of flow, an input no program has ranked; it stands close
   to the closed shock forms, and that is recorded with any decision about it.
5. X-01 to X-05: open. They are new measures built from the taker fields, not the closed forms (contrarian
   taker flow net of the week's return; crowding by activity). X-04 leans partly the way of the mirror of
   generation 2's absorbed-flow book where its correlation is positive; that too is recorded with any decision.
6. X-07 and X-08: open next to the closed decoupling form (an asymmetry of beta and a lead-lag are other
   quantities than a change of correlation).
7. X-02's TWAP caveat: accepted (the last hour of a bin enters with a weight of 1/168 and the week's move is
   taken out of the measure).
8. X-11: STRUCK by the coordinator before any run. A dollar-neutral book that is long high beta when BTC trends
   up and short it when BTC trends down is a bet on the market's trend placed through beta. Symmetric trend
   rules on BTC and ETH have had their counted trials in unit core and failed (generation 0: VAL Sharpe -0.531
   with G6 p 0.866 for the long/short breakout; LESSONS 4 and 8), and the same bet through another door is a
   closed class. The file stays in the repository as registered and struck; it is never run.
9. So the round has TEN ideas, X-01 to X-10. Budget: 10 default runs, at most 6 corner or control runs, 2 in
   reserve; cap 18 (generation 3 would end at most at 35 of 60). One run at a time; a run starts when at least
   1,000,000 KB of physical memory and 4,000,000 KB of commit headroom are free.
10. The price of width holds as in round 3: ten ideas meet one screen, and two of them were shaped with DEV's
    two regimes in view. A survivor is a candidate for one counted trial at most; the number of ideas screened
    and, for a route (b) survivor, its DEV-informed design go into the record of that decision.
11. Stage 2 starts only after this plan and its programs are on the remote and the kernel's strategy test has
    passed with the new files in place. Its parts are appended below.


## Sandbox run log (round 4), filled in during stage 2

(Appended below the coordinator's round-4 rulings, so that the 212,289 bytes committed as ec5a3c9 stay an unchanged
prefix. Every run is listed, in the registered order; X-11 was struck by ruling 8 and not run. Each command was
`python -m omr.sandbox strategies/gen003_xNN_<idea>.omr --g6-lags` at the defaults, full stage 1 (25 truncation cuts),
one at a time, started only after the memory reading of ruling 9 (free physical 2.08 to 4.74 million KB, virtual 10.4
to 12.4 million KB). Output saved as ASCII in the session scratch folder, gen003_r4/run_NN_<name>.txt, by
gen003_r4/run_one.py, which only calls the sandbox. Pre-cost = DEV Sharpe + (DEV Sharpe - G4 DEV). Years: return sign
and Sharpe for 2020, 2021, 2022H1. Costs: equity over DEV, with C/G = costs / avg gross. Funding: gross paid / received.)

| # | idea | DEV SR | G4 DEV | G2 DEV | pre-cost | next30 | r(1), r(2), r(3) | A of 10; B | years + (SR 2020 / 2021 / 2022H1) | names held | avg gross | dir. ch. | costs (C/G) | funding paid / recv |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | X-01 taker_vwap_gap | -2.514 | -2.893 | -3.226 | -2.135 | 0.059 | 0.006, -0.008, 0.026 | 9; -2.274 | 0 (-2.685 / -2.042 / -3.496) | 27.7 of 28.0 | 0.855 | 1833 | 0.1221 (0.143) | 0.2410 / 0.2331 |
| 2 | X-02 vwap_twap_gap | 0.220 | -0.163 | -0.445 | 0.603 | 0.520 | -0.023, -0.021, -0.014 | 6; -0.482 | 2 (0.578 / 0.626 / -0.841) | 27.6 | 0.855 | 1830 | 0.2634 (0.308) | 0.4509 / 0.4699 |
| 3 | X-03 impact_asymmetry | -0.781 | -1.024 | -1.446 | -0.538 | -1.504 | 0.173, 0.024, 0.059 | 10; -0.182 | 0 (-2.164 / -0.606 / 0.099, return -0.008) | 26.5 | 0.855 | 1197 | 0.0931 (0.109) | 0.2853 / 0.2347 |
| 4 | X-04 informed_flow | -0.744 | -1.038 | -1.497 | -0.450 | -0.446 | 0.049, 0.004, -0.020 | 5; -0.444 | 0 (-1.905 / -0.327 / -0.481) | 26.7 | 0.854 | 1192 | 0.1088 (0.127) | 0.2959 / 0.2520 |
| 5 | X-05 stealth_flow | -1.085 | -1.536 | -1.907 | -0.634 | -0.055 | 0.035, -0.010, -0.030 | 10; -1.030 | 0 (-0.317 / -1.852 / -0.391) | 27.6 | 0.853 | 1853 | 0.1679 (0.197) | 0.3297 / 0.3135 |
| 6 | X-06 flow_toxicity | -0.307 | -0.678 | -1.009 | 0.064 | -0.620 | -0.116, -0.040, 0.055 | 6; -1.181 | 1 (1.690 / -1.109 / -1.005) | 27.7 | 0.856 | 1755 | 0.2061 (0.241) | 0.4299 / 0.4124 |
| 7 | X-07 convexity_shift | -0.493 | -0.814 | -1.176 | -0.172 | -2.031 | -0.098, -0.058, -0.004 | 4; 1.051 | 1 (-0.571 / -1.054 / 0.928) | 27.7 | 0.854 | 1530 | 0.1385 (0.162) | 0.3066 / 0.2981 |
| 8 | X-08 price_delay | -0.255 | -0.557 | -0.932 | 0.047 | 1.302 | -0.044, 0.003, 0.008 | 1; 0.752 | 2 (1.055 / -1.600 / 0.846) | 27.6 | 0.854 | 1455 | 0.1629 (0.191) | 0.3627 / 0.3887 |
| 9 | X-09 state_continuation | 1.619 | 1.359 | 1.032 | 1.879 | 0.106 | -0.072, -0.016, -0.061 | 2; 0.579 | 3 (2.312 / 1.532 / 1.025) | 27.6 | 0.855 | 1433 | 0.3138 (0.367) | 0.6226 / 0.6874 |
| 10 | X-10 stress_reversal | -0.340 | -0.683 | -0.910 | 0.003 | -0.381 | -0.029, -0.015, -0.016 | 8; -0.576 | 1 (0.719 / -1.088 / -0.130) | 27.7 | 0.855 | 2031 | 0.2236 (0.262) | 0.3724 / 0.3740 |

Every run: stage 1 PASS, exit 0, nothing on stderr, not liquidated, 75 symbols ever in the unit, next30 over 100
symbols, benchmark (equal-weight long of the in-play members) DEV Sharpe 0.619, maxDD 0.847. Wall times 95.0 to 528.2 s
(X-05 429.3 s and X-07 528.2 s, longer than the expected two to four minutes; no error). Other printed numbers (PSR(0);
total; maxDD; rebalances): X-01 0.000, -0.742, 0.749, 591; X-02 0.634, 0.061, 0.351, 638; X-03 0.114, -0.399, 0.510,
611; X-04 0.119, -0.346, 0.428, 623; X-05 0.042, -0.424, 0.529, 581; X-06 0.312, -0.201, 0.474, 618; X-07 0.218, -0.286,
0.494, 627; X-08 0.345, -0.190, 0.473, 593; X-09 0.995, 1.661, 0.178, 636; X-10 0.294, -0.273, 0.512, 647. Stale-copy
medians in the paired reading: -0.078, -0.138, 0.752, -0.410, -0.215, -0.835, -0.075, -0.040, -0.541, 0.267. Speed-limit
rows from 2020-07-20 14:00 to 2022-06-30 22:00; paired lags 30 to 262 days, decisions 2021-06-30 23:00 to 2022-06-30
22:00.

Total sandbox runs in round 4: 10 of the cap of 18 (10 defaults; no corner, no control, no reserve). No stage-1
rejection, no kernel fault, no refusal. ledger/sandbox_log.jsonl now has 70 rows (60 + 10), rows 60 to 69 (0-indexed),
each status ok, stage1 full, its logged readings equal to the printed ones and its source_sha256 equal to the committed
file's; `omr.ledger verify` OK, all six chains; `omr.kernel_lock verify` OK, sealed (core 0.05, top30 0.1). Generation
3 has used 27 of 60 sandbox runs.

By the run order, corners were due only for ideas that passed W1 to W8, and the route-(b) control only for X-09 or X-10
after passing its corners. None passed W1 to W8, so no corner and no control was run.

## Amendments (round 4), stage 2

none: no program text, param, default, screen item or run condition was changed, and the reserve was not used.

## Screen outcome per idea (round 4)

| idea | W1 | W2 (pre-cost >= 1.5) | W3 (G4 > 0) | W4 (G2 > 0) | W5 (next30 >= 0.3) | W6 (r <= 0.40) | W7 (A <= 4, B > 0) | W8 (years) | first failed | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| X-01 taker_vwap_gap | pass | FAIL (sign: -2.514) | FAIL | FAIL | FAIL (0.059) | pass | FAIL (9; -2.274) | FAIL (0) | W2 | dropped |
| X-02 vwap_twap_gap | pass | FAIL (0.603) | FAIL | FAIL | pass (0.520) | pass | FAIL (6; -0.482) | pass (2) | W2 | dropped |
| X-03 impact_asymmetry | pass | FAIL (sign: -0.781) | FAIL | FAIL | FAIL | pass | FAIL (10; -0.182) | FAIL (0) | W2 | dropped |
| X-04 informed_flow | pass | FAIL (sign: -0.744) | FAIL | FAIL | FAIL | pass | FAIL (5; -0.444) | FAIL (0) | W2 | dropped |
| X-05 stealth_flow | pass | FAIL (sign: -1.085) | FAIL | FAIL | FAIL | pass | FAIL (10; -1.030) | FAIL (0) | W2 | dropped |
| X-06 flow_toxicity | pass | FAIL (sign: -0.307) | FAIL | FAIL | FAIL | pass | FAIL (6; -1.181) | FAIL (1) | W2 | dropped |
| X-07 convexity_shift | pass | FAIL (sign: -0.493) | FAIL | FAIL | FAIL | pass | pass (4; 1.051) | FAIL (1) | W2 | dropped |
| X-08 price_delay | pass | FAIL (sign: -0.255) | FAIL | FAIL | pass (1.302) | pass | pass (1; 0.752) | pass (2) | W2 | dropped |
| X-09 state_continuation | pass | pass (1.879) | pass | pass | FAIL (0.106) | pass | pass (2; 0.579) | pass (3) | W5 | dropped |
| X-10 stress_reversal | pass | FAIL (sign: -0.340) | FAIL | FAIL | FAIL | pass | FAIL (8; -0.576) | FAIL (1) | W2 | dropped |
| X-11 trend_beta | - | - | - | - | - | - | - | - | - | struck before any run (ruling 8); never run |

Against each registered falsifier ("the DEV screen fails; the sign is never flipped"): all ten falsified on DEV. Eight
had the wrong sign over DEV (X-01, X-03 to X-08, X-10); X-02 had the registered sign but read under the pre-cost floor
(0.603). X-09 passed every item but W5: next30 read 0.106 against the floor of 0.3.

## DEV observations (round 4; NOT hypotheses, never to be submitted from this plan)

- X-09, the market-state continuation book, read well on every item its design could shape (pre-cost 1.879, G4 1.359,
  G2 1.032, positive in all three DEV years, paired 2 of 10 with B 0.579) and failed the one item it could not shape:
  next30 0.106. The plan had called its DEV and yearly readings partly predictable; they were. WEAK.
- X-01 lost in every DEV year (-2.514, the largest absolute Sharpe of the round): coins whose takers bought at higher
  prices than they sold, net of the week's move, did better the next week. Its next30 reading was +0.059 (the registered
  sign, near zero), so the reverse did not show in ranks 31 to 60. DEV is spent as a screen for the mirror. WEAK.
- Both halves of DEV: X-09 earned in 2020, 2021 and 2022H1; X-08 earned in 2020 and 2022H1 but lost in 2021 (SR -1.600)
  and over DEV; no route-(a) book was positive over DEV with the registered sign except X-02 (0.220, 2020 and 2021
  positive, 2022H1 negative). X-07 and X-08 read like round 3's unsigned books on the last 365 days (book medians 1.051
  and 0.752, stale copies negative) while losing over DEV. WEAK.
- Costs: the taker-imbalance and co-movement books cost 0.093 to 0.168 of equity over DEV (C/G 0.11 to 0.20; X-02 0.263,
  X-06 0.206), among the cheapest weekly top30 books read; their G4 drops were 0.24 to 0.45. X-09 cost 0.314 (C/G 0.37)
  and paid and received 0.62 / 0.69 in gross funding, like round 2's continuation books. G2 drops 0.57 to 0.82 in every
  book, larger than the G4 drop in all ten.
- Speed limit: every reading between -0.116 and 0.173; names held 26.5 to 27.7 of 28.0.
- WEAK throughout: one DEV period, one default each, one researcher session; nothing here is a parameter
  recommendation, and no corner or control was run.

## Recommendation (round 4)

NONE. By the pre-registered selection rule an idea is eligible only if it passes W1 to W8 at the default and both
corners (and, for X-09 and X-10, the control condition). No idea passed W1 to W8 (X-09 failed W5; the other nine failed
W2 first), so no corner and no control was run and no program from version 4 is recommended. No KP-017 or KP-020
measurement is needed for this round. Generation 3 stands at 0 of 5 counted submissions and 27 of 60 sandbox runs; M is
unchanged at 6.
