# Generation 4 - PLAN (version 1, round 1, a tier premise test, pre-registered 2026-11-27 before any generation-4 sandbox run)

Researcher session for generation 4, round 1, stage 1. A fresh session: everything it knows of the project comes from
the files named below. This round does not look for a rule to submit; it tests one premise with the tools as they are.

## Head

- Kernel: `omr.status` OK d09812fdec752a17, semantic 7d923e7e2375986d, text b74122f3f9821056, sealed (G6 core 0.05,
  top30 0.10); `omr.kernel_lock verify` OK. Data research_hash 28d9084a8c5c7659, validated, snapshot_end 2026-11-18.
- Ledger: M = 6 (generation 0: 4, 1: 1, 2: 1, 3: 0), N 5.90, rho 0.021, Tier 1 0, pool 0 of 5, one uncounted stage-1
  rejection; `omr.ledger verify` OK, six chains. Sandbox log 83 rows; generation 4 has used 0 of its 60 runs.
- Read: KERNEL_PROPOSALS.md (the entries of 2026-11-26 and 2026-11-27, the last one with care); RESEARCH_PLAYBOOK.md
  (all; 3, 4, 4b, 5 and 8b with care); generations/META_REVIEW_2026-11-26.md (all); LESSONS.md (1 to 61); LANGUAGE.md
  (all); CONSTITUTION.md 4 to 7 and 13; generations/gen003/REPORT.md (all five rounds and the close); generations/gen003/
  PLAN.md version 5 (head, ideas, rulings, run log, screen outcome, DEV observations). Code, read only: omr/upipeline.py
  (next30_score, Blocked, run_targets), omr/sandbox.py (the KP-018 readings), omr/constants.py (universe constants),
  omr/lang.py (parse_file, the checker, the lookback rule). Shapes: the programs of round 3 to 5.
- Not opened: data/, ledger/returns/, ledger/trials/, calibration files, audits/. No project program was run on data:
  only `omr.status`, `omr.ledger summary`, `omr.ledger verify`, `omr.kernel_lock verify`, a parse-only check (scratch
  gen004_r1/parse_check.py; omr.lang.parse_file) and two scripts that read ledger/sandbox_log.jsonl only (sbtable.py,
  sbcorr.py).
- Numbers seen before writing: every DEV number of generations 2 and 3 (REPORTs, run logs, sandbox rows), the review's
  tables, the VAL rows of the six counted trials, and ALL 42 logged next30 DEV Sharpes, listed here (top30 DEV / next30
  DEV; sandbox rows 40, 41 and 43 to 82):
  - positive (16): X-08 price_delay -0.255 / 1.302; W-02 cost_basis 1.049 / 0.755; Y-13 noise_state_reversal -0.369 /
    0.711; W-10 basis_instability -0.188 / 0.670; averaged_funding_shock 1.492 / 0.637; W-01 high_anchor 1.558 / 0.601;
    X-02 vwap_twap_gap 0.220 / 0.520; Y-05 noise_ratio -1.051 / 0.456; H1 weekend_share -1.348 / 0.217; X-09
    state_continuation 1.619 / 0.106; W-09 volume_trend -0.375 / 0.105; X-01 taker_vwap_gap -2.514 / 0.059; W-03
    vol_shock -0.276 / 0.057; W-11 ensemble 0.372 / 0.029; Y-10 premium_commonality -0.676 / 0.020; H2 heavy_hours
    -0.256 / 0.007.
  - negative (26): X-07 convexity_shift -0.493 / -2.031; X-03 impact_asymmetry -0.781 / -1.504; W-05 us_session_shift
    -0.537 / -1.372; resid_reversal -1.566 / -1.030; W-07 wick_absorption -0.932 / -0.902; jump_continuation 0.705 /
    -0.820; Y-03 beta_instability 0.657 / -0.780; Y-04 volume_cv 0.140 / -0.754; Y-06 wick_share -0.653 / -0.751; H3
    storm_share 0.349 / -0.740; Y-07 vol_feedback -0.899 / -0.738; X-06 flow_toxicity -0.307 / -0.620; Y-12
    leverage_state_kurtosis -0.897 / -0.520; W-06 weekend_tilt -2.343 / -0.511; Y-02 vol_of_vol -0.153 / -0.505; W-08
    decoupling -0.179 / -0.502; X-04 informed_flow -0.744 / -0.446; Y-11 ensemble 0.009 / -0.433; Y-09
    volume_commonality 0.588 / -0.429; W-04 illiquidity_shock -0.156 / -0.407; X-10 stress_reversal -0.340 / -0.381;
    Y-01 kurtosis -0.891 / -0.371; Y-08 volume_coupling 0.152 / -0.346; week_continuation 0.836 / -0.314;
    multiweek_momentum 0.541 / -0.100; X-05 stealth_flow -1.085 / -0.055.
  - Across the 42 (sbcorr.py): next30 mean -0.265, standard deviation 0.661; correlation with the same program's top30
    DEV Sharpe 0.244; same sign in 23 of 42. A spread of 0.66 is about what sampling noise alone gives one number over
    2.5 years (0.63): the log shows no sign of real dispersion of skill on next30 so far.
- No DEV or VAL number exists for any program below. Files of this version: this text and ten new programs,
  strategies/gen004_t01_* to gen004_t10_*. Nothing else in the project was written.

## The premise and the reading rule (quoted from KERNEL_PROPOSALS.md, entry of 2026-11-27, unchanged)

The premise: "there is more to find where a small account is not at a disadvantage", in the coins ranked below the top
30. The rule, as the decision fixed it before any idea was written:

> The reading rule, fixed now, before any idea is written. Let k be the number of the round's ideas whose next30 DEV
> Sharpe is 1.0 or more with the registered sign. With no
> edge at all, one such reading in about 18 is expected by chance, and three or more of twelve in about 3 rounds of
> 100. So: k of 3 or more: the coordinator proposes the build of a unit for the less liquid tier to the human, with the
> round's numbers and the costs. k of 2 or fewer: the place gap is closed as a front for these data, no unit is
> proposed, and the coordinator goes on to the information gap by a desk study of which other data are free, long
> enough and clean enough to be admitted.

How I apply it (no change of the rule): the registered sign is the sign of each program's signal line as written; a
next30 reading of -1.0 or less does not count; a next30 run that gives no Sharpe (no_unit, liquidated) counts as below
1.0. k is counted over the ten ideas registered here. With ten ideas and no edge (one in 18 each), k of 3 or more comes
about 2 times in 100 (binomial, my arithmetic), a little less often than with twelve.

## What a next30 DEV Sharpe is, and what it is not

How it is made (omr/sandbox.py and omr/upipeline.py, read only). After the top30 readings, the sandbox releases the
top30 panel and calls `next30_score(prog, params, ud, end=DEV_END, keep=True)`, G8's own function, on the universe data
loaded under the dev_end ceiling. The panel is `Blocked(ud, "next30")`: every symbol ever ranked 31 to 60 by median
daily quote volume over the previous 90 days, membership reconstituted at each month from DEV bars only, evaluated in
3-month blocks; 100 symbols are ever in next30 on DEV. The same program text runs unchanged: every `cs_*` ranks, centres
or averages across the next30 coins in play (at least 10 with a known, finite input), so "the unit's mean" and the
beta-neutral projection of the programs below are next30 quantities; `btc()` is still the real BTCUSDT, which is not a
member of next30. The engine trades DEV start to DEV end at the top30 cost rate, 12.5 bps per side, with funding, and
the Sharpe is that of the daily net returns. A month with fewer than 10 symbols ranked 31 to 60 (fewer than 40 eligible
coins) has no next30 unit and the book is flat (omr/universe.py). The panel starts 2019-12-31 and a month's membership
reads the 97 days before it, so no unit exists before May 2020, and next30 may have had no unit in further 2020 months
(not measured: I may not read data); its live span is probably shorter than DEV's 2.5 years.

What it is: ONE number over about 2.5 years of daily returns, with a standard error of roughly 0.6 (one over the square
root of the years); after the top30 cost rate; with no stress reading (no G2, G4, names held or paired reading is taken
on next30); of a program written for another unit. What it is not: a gate (G8 asks only for a positive Sharpe over
DEV and VAL), a measure of what trading these coins costs, or evidence about VAL. One reading of 1.0 is 1.6 standard
errors from zero and comes by chance about once in 18; that is why the rule counts ideas instead of reading one, and
why three different mechanisms reading 1.0 would mean something one would not.

## How the ideas were chosen (design rules of this round, fixed before writing)

1. The mechanism must scale with what distinguishes ranks 31 to 60: fewer market makers and arbitrageurs per coin, a
   larger share of retail and leveraged perp traders, thinner spot books behind the index. Each idea says who is on
   the other side and why it would persist there.
2. Timing, not tilt: every measure is information one to six weeks old, re-estimated each week. No level characteristic
   is registered (an illiquidity level from a high-low spread estimator, idiosyncratic volatility): G6's stale copies
   hold the same tilt, so a unit built on one would fail G6 whatever next30 read. Size and volume levels cannot be
   ranked at all (a `cs_*` needs a dimensionless input).
3. Every book: kind portfolio, unit top30, decided once a week (a weekly series visible at the bar that opens Sunday
   23:00 UTC, traded at the Monday 00:00 open), dollar neutral, gross 1, rank weights, no sparse book. Nine of ten are
   also beta neutral by generation 3 round 5's projection (w = z - (mean(z bd) / mean(bd bd)) bd, bd the centred daily
   beta to BTC over nb = 42 days; it sets their lookback at 1,605 hours); T-02 is dollar neutral only, like Y-13 and
   X-10, whose construction it shares. The `cs_*` stays outside every window except T-04's market factor, so an
   entrant to next30 (membership churns more there) is ranked from its first visible weekly bin.
4. Source read (playbook 5): no numeric literal in any file (n_literals 0 in all ten); no calendar field; same-unit
   ratios appear only as measured series (the ticket size, the premium), read through their changes, never as a
   constant, threshold or scale.
5. No form whose next30 reading is logged, no mirror or close relative of one; at most two ideas from the family of
   the three positive limits-to-arbitrage readings (X-08, Y-05, Y-13), marked "family seen"; at most three per class.

Canonical tier mechanisms NOT registered, and why: one-week reversal (both signs logged: -1.030 reversed, -0.314
continued); lottery, MAX and skew (the mirror of jump_continuation, -0.820, would be a flipped reading); illiquidity and
size levels (rule 2); the one-to-two-month reversal and attention bursts in trades or ticket size (closed classes
#16, #12, #13 of the stop list; their next30 was never logged; question 3); funding or premium contrarian forms (closed;
averaged_funding_shock logged at 0.637); coskewness and downside beta (mirrors of X-07, -2.031); downside illiquidity
(mirror of X-03, -1.504); session parts of the week's move (closed decompositions; W-05 -1.372); liquidity risk through
commonality (Y-09, -0.429); a lead from the top 30 to ranks 31 to 60 (a top30 program run on next30 sees no top30 coin,
so the tools cannot test it).

## The ideas

Classes: A slow diffusion (T-01); L liquidity provision (T-02); B perp leverage dynamics (T-03, T-04, T-05); C retail
composition by trade size (T-06, T-07, T-10); V attention timing of volume (T-08, T-09). Family seen: T-01, T-02.
Reading funding or the basis (allowed in this premise test; any later submission subject to KP-017): T-03, T-05, T-10
(index_close), T-04 (funding8h). Expected correlations: T-03 with T-05 (both rank co-movement of the daily premium
change; in rising markets returns and volume move together), moderate; T-06 with T-10 (ticket size against returns and
against the premium, which moves with returns), moderate; T-03 with T-10, low to moderate; T-08 with T-09 (both read
volume against earlier moves), moderate; T-03 with T-04 (both short leverage-driven coins), low; T-01 and T-02 with the
rest, low. In the worst case B and C behave as two bets, not six. Nodes and lookbacks are from the parse check, window
params at their high bounds. The shared bar arithmetic (playbook 8b, top30): needed before costs in VAL = 0.74 + drag
for G1's line, 1.5 + drag for decent odds. Drag = the Sharpe 1x costs take (the expected G4 drop), from the yardsticks
of LESSONS 50, 54 and 59 (beta-neutral weekly books on 4- to 6-week measures dropped 0.23 to 0.37). On next30 the same
turnover probably costs less Sharpe (its books are more volatile), and real costs there may exceed 12.5 bps; the cost
lines say what a doubled rate would take.

### T-01 gen004_t01_btc_catchup (class A, slow diffusion; FAMILY SEEN; no funding or basis)
- Rule: dl = corr(r1, lb) - corr(lr, b1) over n hours, X-08's estimator with j = 25 (BTC's moves of the previous day);
  s = the sign of BTC's log return over the last j hours; both sampled weekly. After a BTC rise long the slowest
  followers and short the leaders, after a fall the reverse: `z = cs_demean(cs_rank(dl)) * s`, then beta neutral,
  `signal = cs_scale(w)`. j = param(25, 20, 30), n = param(504, 403, 605), nb = param(42, 33, 51). 68 nodes, 1,605 h.
- Mechanism and tier: a coin that follows BTC with a lag of hours to a day has not priced BTC's Sunday move at the
  Monday open and catches up early in the week. Lags are longer where fewer market makers and cross-asset desks quote
  the coin against BTC, which is ranks 31 to 60. Other side: slow quoters and holders who reprice late. It persists
  because the catch-up per coin is small next to the costs of a large account and the books are too thin to take size.
- Nearest logged: X-08 price_delay, 1.302 (long delayed coins every week, a 2-hour delay over 2 weeks). Not predictable
  from it: the book's sign is set each week by BTC's last-day move, so an unconditional delay premium, which is what
  X-08 may have earned, enters only in proportion to how much more often BTC's Sunday-day return was up than down; the
  delay is measured over a day, not two hours; the book is beta neutral.
- On top30 I expect less (liquid names catch up within hours): near zero. Nothing is an answer.
- Costs: the whole book reverses when s flips (about half the weeks, estimate) on top of the weekly rank changes, so
  costs of about 1.5 to 2 times a weekly rank book: drag 0.50 (registered; 1.24 / 2.00 before costs in VAL); a doubled
  rate takes about another 0.5. The costliest idea of the round.
- Outside evidence: Hou and Moskowitz (2005), Hou (2007), US equities: neglected and small firms respond late to
  market and industry news. Lead from BTC to altcoins at intraday horizons is widely reported; I cannot name one paper
  with certainty. At a weekly horizon: none.
- Bias: X-08's next30 reading (and Y-05's, Y-13's) is why this family was chosen; that is the label. The direction
  after a BTC move is the one the mechanism gives, not tuned.

### T-02 gen004_t02_impact_reversal (class L, liquidity provision; FAMILY SEEN; STATE-CONDITIONAL; no funding or basis)
- Rule: y = W-04's price-impact shock (absolute daily return per unit of quote volume, 1 week over 6 weeks), x = W-04's
  1-week log return in volatility units, both weekly. `signal = cs_scale(cs_demean(-cs_rank(y) * cs_rank(x)))`: reverse
  the week's move where impact rose, continue it where impact fell. k = param(7, 5, 9), n = param(42, 33, 51). 35 nodes,
  1,605 h. Dollar neutral only.
- Mechanism and tier: reversal is the price of liquidity provision and is largest where and when liquidity providers
  are scarce (Nagel 2012; Avramov, Chordia and Goyal 2006). A move made while the book was thin is mostly pressure; a
  move made on deep trading is mostly news. Ranks 31 to 60 have fewer market makers, so their withdrawals are larger
  and the pressure behind a thin move bigger. Other side: traders who demand immediacy in a thin book (liquidations,
  retail market orders); it persists because providing liquidity in thin alts is risky and capital for it is scarce.
- Nearest logged: W-04 illiquidity_shock, -0.407 (the same y and x: long y made orthogonal to x); Y-13, 0.711 (a
  liquidity proxy times the move); resid_reversal, -1.030; X-10, -0.381. Not predictable: the y x x interaction is
  orthogonal by construction to W-04's linear book and to the plain move book; Y-13's state was the level of noise,
  this one is the change of price impact; X-10's state was market-wide. Family seen: an illiquidity proxy decides the
  reversal, Y-13's flavour.
- On top30: weaker or negative (the week's move tended to continue in top30 early in DEV). Nothing is an answer.
- Costs: two weekly ranks multiplied, like Y-13 (C/G 0.253): drag 0.40 (1.14 / 1.90); doubled, another 0.40.
- Outside evidence: Nagel (2012), Avramov, Chordia and Goyal (2006), US equities; Zaremba et al. (2021), crypto: short-
  term reversal among small and illiquid coins (daily). Against: Campbell, Grossman and Wang (1993) find that HIGH-volume
  moves reverse; here they continue.
- Bias: both signs of the plain 1-week move read negative on next30 after costs, so a split is the one way left for the
  week's move to read well; that and Y-13 are why it is labelled. Remembered: thin alt rallies in 2021 that gave back.

### T-03 gen004_t03_premium_feedback (class B, perp leverage; READS index_close)
- Rule: p = (daily close - daily index close) / daily index close; c = corr(delta(p, 1), rd) over k days, rd the daily
  log return; weekly. Short the highest c, long the lowest, beta neutral. k = param(28, 22, 34), nb. 52 nodes, 1,605 h.
- Mechanism and tier: where the perp premium widens with the price and narrows with it, leveraged perp traders set the
  price and spot arbitrage is too thin to anchor it; such prices overshoot and give back (liquidity spirals,
  Brunnermeier and Pedersen 2009). Arbitrage capacity per coin is smallest in the less liquid coins (the spot coin is
  harder to borrow, the index venues thinner). Other side: leveraged perp traders who chase; it persists while basis
  capital for small coins is scarce.
- Nearest logged: W-10 basis_instability, 0.670 (short a RISE in |change of p| / |return| against the coin's own 4-week
  norm); Y-10 premium_commonality, 0.020. Not predictable: W-10 ranks the change of an unsigned churn ratio with its
  level removed; T-03 ranks the level of a signed daily correlation of the premium with the coin's own price; Y-10 ranks
  co-movement with the market's premium, not with the coin's price.
- On top30: weaker (more arbitrage capital): near zero. Nothing is an answer.
- Costs: a 4-week correlation re-estimated weekly, like Y-03 and Y-09 (C/G 0.18 to 0.19): drag 0.30 (1.04 / 1.80);
  doubled, another 0.30.
- Outside evidence: perp-spot deviations are larger and arbitrage less complete in less liquid coins (He, Manela, Ross
  and von Wachter 2022, as I recall); no test of this measure against returns.
- Bias: generation 2's contrarian premium books were positive on DEV and failed in VAL; W-10's next30 reading is known.

### T-04 gen004_t04_leverage_loading (class B, perp leverage; READS funding8h)
- Rule: fd = the coin's daily mean of funding8h; fm = the unit's mean of delta(fd, 1) (the market's leverage factor; on
  next30 the mean over ranks 31 to 60); c = corr(rd - rbd, fm) over k days, rd - rbd the coin's daily return minus
  BTC's; weekly. Short the highest c, long the lowest, beta neutral. k = param(28, 22, 34), nb. 51 nodes, 1,605 h. No
  coin is ranked on its own funding. fm is known only for coins in play, so an entrant waits k days (names held lower).
- Mechanism and tier: coins that outperform when the market's leverage builds are bid up by leverage-constrained
  buyers and dumped when it unwinds (Frazzini and Pedersen 2014); prices in the less liquid perps are set more by
  leverage. Other side: leveraged speculators; it persists with leverage constraints and lottery demand.
- Nearest logged: Y-12, -0.520 (the unit's funding trend as a STATE for a kurtosis book); averaged_funding_shock, 0.637
  (a coin's own funding shock, contrarian). Not predictable: no logged run ranks a loading on the unit's daily funding
  changes, and no coin's own funding level or shock enters.
- On top30: weaker. Nothing is an answer.
- Costs: drag 0.30 (1.04 / 1.80); doubled, another 0.30.
- Outside evidence: Frazzini and Pedersen (2014), equities and other markets. Against: Adrian, Etula and Muir (2014)
  find exposure to (broker-dealer) leverage shocks earns a POSITIVE premium. The sign is uncertain; it is registered
  from the overpricing story.
- Bias: remembered: alt funding spikes in the 2021 pumps; LUNA's leverage in 2022. Funding sits at the exchange's
  default rate for days (as I recall the rule), so fm is small and noisy in calm months.

### T-05 gen004_t05_premium_volume (class B, perp leverage; READS index_close)
- Rule: p as T-03; dq = the daily log change of quote volume; c = corr(delta(p, 1), dq) over k days; weekly. Short the
  highest c, long the lowest, beta neutral. k = param(28, 22, 34), nb. 55 nodes, 1,605 h.
- Mechanism and tier: trading bursts with a widening premium are leveraged entry on the perp; bursts with a narrowing
  premium are deleveraging or spot-led trading. The first leaves a coin crowded, the second has dumped it. Thin spot
  arbitrage lets this matter more in the less liquid coins. Other side: leveraged entrants.
- Nearest logged: W-10, 0.670; Y-10, 0.020; Y-08 volume_coupling, -0.346 (hourly volume with |return|); and the closed
  premium_shock form (contrarian on the premium against its 6-week norm; next30 never logged). Not predictable: the
  co-movement of premium changes with volume changes is neither the premium's level or shock, nor churn per unit of
  price movement, nor volume with |return|; a coin can rank high with no net premium change over the window. Adjacent
  to the closed premium-shock class in spirit (crowded leverage); registered because no premium level is ranked
  (question 5).
- On top30: weaker. Nothing is an answer.
- Costs: drag 0.30 (1.04 / 1.80); doubled, another 0.30.
- Outside evidence: none.
- Bias: as T-03.

### T-06 gen004_t06_rally_tickets (class C, retail composition; no funding or basis)
- Rule: tk = daily quote volume / daily number of trades (USD per trade); c = corr(logret(tk, 1), rd) over k days;
  weekly. Long the highest c (rallies carried by larger tickets), short the lowest (rallies carried by smaller ones),
  beta neutral. k = param(28, 22, 34), nb. 49 nodes, 1,605 h. The ticket size's level is never read.
- Mechanism and tier: who carries a coin's rallies: larger tickets (better informed or better capitalised) or smaller
  ones (retail chasing, who leave it overpriced). The retail share, and the weight of single large holders, are larger
  in ranks 31 to 60. Other side: retail chasers; it persists while retail keeps chasing.
- Nearest logged: no logged run reads trades on next30 except X-06 flow_toxicity, -0.620 (trades as a weight on flow
  one-sidedness); Y-08, -0.346. The closed small_tickets (a ticket-size shock, contrarian) was never read on next30.
  Not predictable: a correlation of ticket-size changes with returns is neither a ticket shock nor activity with |return|.
- On top30: weaker. Nothing is an answer.
- Costs: drag 0.30 (1.04 / 1.80); doubled, another 0.30.
- Outside evidence: Barber, Odean and Zhu (2009), US equities: small-trade imbalances herd and later reverse. Against:
  Kaniel, Saar and Titman (2008): individuals provide liquidity. Crypto: none.
- Bias: a large market order filled against many resting orders counts as many trades, so liquidation days shrink
  tickets mechanically; disclosed, not corrected. small_tickets read -0.211 in top30 (known).

### T-07 gen004_t07_move_tickets (class C, retail composition; no funding or basis; the round's stretch)
- Rule: c = corr(logret(tk, 1), |rd|) over k days; weekly. Long the highest c, short the lowest, beta neutral.
  k = param(28, 22, 34), nb. 50 nodes, 1,605 h. The unsigned form of T-06.
- Mechanism and tier: a coin whose big days pull in a crowd of small tickets has an attention-driven retail clientele
  that overprices it (Barber and Odean 2008); one whose big days bring larger tickets is moved by informed traders.
  Attention clienteles are larger in ranks 31 to 60. Other side: attention traders.
- Nearest logged: Y-08 volume_coupling, -0.346 (long hourly volume levels moving with |return|). Not predictable: the
  log change of tk is the log change of volume minus that of trades, so the common coupling of activity with |return|
  (Y-08's quantity) largely cancels and composition is left; daily changes, not hourly levels.
- On top30: weaker. Nothing is an answer.
- Costs: drag 0.30 (1.04 / 1.80); doubled, another 0.30.
- Outside evidence: Barber and Odean (2008) for attention; none on trade size.
- Bias: the fill mechanics of T-06 weigh more here (big days are liquidation days). The weakest idea of the round.

### T-08 gen004_t08_volume_lead (class V, attention timing; no funding or basis)
- Rule: ql = the log change of quote volume over the j - 1 days before today, al = |the log return over those days|
  (j = 3, written as a difference of windows); c = corr(ql, |rd|) - corr(al, dq) over k days; weekly. Long the highest
  c (volume runs ahead of big moves), short the lowest (volume trails them), beta neutral. j = param(3, 2, 4),
  k = param(42, 33, 51), nb. 62 nodes, 1,677 h.
- Mechanism and tier: informed volume comes before price moves (Easley and O'Hara 1992; Blume, Easley and O'Hara 1994),
  attention volume comes after them; late, attention-driven clienteles that overprice are larger in ranks 31 to 60.
  Other side: late attention traders.
- Nearest logged: Y-08, -0.346 (contemporaneous coupling); X-08, 1.302 (lead and lag of returns against BTC). Not
  predictable: a lead-lag between a coin's own volume and volatility, with the contemporaneous part differenced out;
  BTC does not enter. Not counted as family seen: it is no price delay and no noise measure.
- On top30: weaker. Nothing is an answer.
- Costs: 6-week windows move slowly: drag 0.25 (0.99 / 1.75); doubled, another 0.25.
- Outside evidence: theory, and Llorente, Michaely, Saar and Wang (2002) on volume and return dynamics; crypto: none.
- Bias: nothing specific I can name. G5's jitter of j to 2 makes the lag one day.

### T-09 gen004_t09_gain_chasing (class V, attention timing; no funding or basis)
- Rule: rl = the coin's log return over the j - 1 days before today; c = corr(rl, dq) over k days; weekly. Short the
  highest c (trading rises after gains, falls after losses), long the lowest, beta neutral. j = param(3, 2, 4),
  k = param(42, 33, 51), nb. 51 nodes, 1,677 h. The coin's own recent move is not ranked.
- Mechanism and tier: a clientele that buys what has just risen pushes a coin above value, and it gives back; such
  trend-chasing clienteles are larger in ranks 31 to 60. Other side: the chasers.
- Nearest logged: W-09 volume_trend, 0.105 (long 2-week over 8-week volume growth); Y-08, -0.346. Not predictable: a
  signed relation of earlier returns to later volume changes is neither a volume growth rate nor a coupling.
- On top30: weaker. Nothing is an answer.
- Costs: drag 0.25 (0.99 / 1.75); doubled, another 0.25.
- Outside evidence: Seasholes and Wu (2007), Shanghai: attention-grabbing price-limit hits draw individual buying that
  reverses; Barber and Odean (2008). Crypto: none.
- Bias: remembered: alt rallies drawing volume in 2021.

### T-10 gen004_t10_premium_tickets (class C, retail composition; READS index_close)
- Rule: c = corr(logret(tk, 1), delta(p, 1)) over k days, tk as T-06 and p as T-03; weekly. Long the highest c (the
  premium widens on days of larger tickets), short the lowest (it widens on days of smaller tickets), beta neutral.
  k = param(28, 22, 34), nb. 57 nodes, 1,605 h.
- Mechanism and tier: a premium built on small-ticket days is retail leverage piling into the perp, which overprices
  the coin; one built on large-ticket days is capitalised demand. Retail leverage weighs most in the less liquid perps.
  Other side: retail leveraged longs.
- Nearest logged: W-10, 0.670; Y-10, 0.020. Not predictable: no logged run combines trade size with the premium.
- On top30: weaker. Nothing is an answer.
- Costs: drag 0.30 (1.04 / 1.80); doubled, another 0.30.
- Outside evidence: none.
- Bias: as T-03 and T-06.

## The top30 screen W1 to W8 (for information; copied from playbook 8b as numbered in generation 3)

W1 stage 1 passes with at least 30 direction changes, average gross at least 0.5, at least 15 names held on average, not
liquidated; W2 DEV Sharpe before costs (the DEV Sharpe plus the drop under G4's reading, i.e. DEV Sharpe + (DEV Sharpe -
G4 DEV Sharpe)) at least 1.5; W3 G4's DEV reading positive; W4 G2's DEV reading positive; W5 next30 DEV Sharpe at least
0.3; W6 the speed-limit statistic at most 0.40 at each of one to three steps (a reason line fails); W7 in the paired
reading at most 4 of 10 stale copies at least as good as the book AND the book's median Sharpe over the last 365 days of
DEV positive (a refused reading fails); W8 at least two of the three DEV years positive. A wrong sign is a failure; no
sign is ever flipped; no default is changed after a run. No sparse book.

Numbers are taken as the sandbox prints them (full stage 1, no --quick, with --g6-lags): the stage-1 line, "DEV Sharpe",
"rebalances ... avg gross ... liquidated", the per-year rows (2020, 2021, 2022; a year is positive when its return is
above 0), and the KP-018 block (r(1) to r(3), next30, G2 and G4 on DEV, names held, the paired reading A of 10 and book
median B). An idea that passes W1 to W8 is handled as in generation 3: its corners (below), then the coordinator's
reading; never a submission by this plan. A pass of the top30 screen does not change k, and k does not change the
screen.

## Run order and budget (decided now)

- Runs 1 to 10: the defaults in the order T-01 to T-10, each `python -m omr.sandbox strategies/gen004_tNN_<idea>.omr
  --g6-lags`, full stage 1, one at a time under the coordinator's memory rule. Every default runs, whatever the earlier
  ones read. The next30 line of each run is the round's reading; the rest of the output is the top30 screen.
- Then, only for an idea that passed W1 to W8: the 0.8 corner, then the 1.2 corner (`--set`), each needing a positive
  DEV Sharpe AND a positive G4 DEV reading; stop an idea at its first failure. At most 4 such runs; if more than two
  ideas pass, the first two in this order: an idea that reads neither funding nor the basis first, then the run order.
  Corners do not enter k.
- Corners (integers rounded; a param left unchanged by rounding moves by 1):

  | idea | 0.8 corner | 1.2 corner |
  |---|---|---|
  | T-01 | j=20, n=403, nb=34 | j=30, n=605, nb=50 |
  | T-02 | k=6, n=34 | k=8, n=50 |
  | T-03, T-04, T-05, T-06, T-07, T-10 | k=22, nb=34 | k=34, nb=50 |
  | T-08, T-09 | j=2, k=34, nb=34 | j=4, k=50, nb=50 |

- Reserve: 2 runs, only for an honest restatement after a stage-1 rejection of a default (an amendment recorded before
  its run; the restated idea keeps its number and its registered sign). Cap 16 runs (10 + 4 + 2): generation 4 would
  stand at most at 16 of 60. No counted run and no recommendation for a counted trial is part of this plan. The product
  of the round is the table of the ten next30 readings and k.

## Questions for the coordinator

1. Ten ideas, not twelve. After the stop list, the 42 logged readings and their relatives, the space I could fill with
   honest tier mechanisms was thin; T-07 is a stretch and I say so. With ten, k of 3 or more comes about 2 times in 100
   with no edge. Accept ten, or strike T-07 (nine would be under the brief's ten)?
2. Family seen: T-01 (a delay measure, its sign set by BTC's last-day move) and T-02 (an illiquidity proxy deciding a
   reversal). T-08 is a lead-lag, but of a coin's volume against its own volatility, and is not counted. Agreed?
3. The stop list was treated as binding, so two canonical tier mechanisms are absent: the one-to-two-month reversal
   (generation 2's #16 form) and attention bursts in trades or ticket size (#12, #13). Their next30 readings were never
   logged, and they sit nearer the literature's small-coin effects than anything above. If you rule that the stop list
   does not bind a next30 premise test, they can be registered in a version 2 before any run.
4. Level characteristics were excluded by design (rule 2). A next30 reading of a level book (say a high-low spread
   estimator, long the illiquid) would show whether the tier carries a level premium that G6 would not credit. Not
   registered; should one be run for information, outside k?
5. Four ideas read the basis or funding (T-03, T-04, T-05, T-10). T-05 stands next to the closed premium-shock class in
   spirit, though it ranks no premium level or shock. Open as written?
6. Beta neutrality in nine of ten (generation 3 round 5's projection, accepted then as a neutrality constraint): accepted
   again? T-04's entrants wait 28 days in play (its market factor is known only for coins in play): acceptable?
7. Budget: 10 defaults, at most 4 corner runs, 2 in reserve; cap 16.
8. The count: a next30 run that gives no Sharpe counts as below 1.0, and a reading of -1.0 or less does not count.
   Agreed?

Written 2026-11-27 19:02 +08:00 (2026-11-27 11:02 UTC), before any generation-4 sandbox run.

## Coordinator's rulings before run 1 (2026-11-27; appended by the coordinator, nothing above is changed)

The coordinator read the plan's ideas and questions and every one of the ten programs (the source read of
playbook section 5: no constant, threshold or scale built from a calendar field or a same-unit ratio; the
ticket size is quote volume over trades, a series; T-01's state is the sign of a real BTC return), before any
generation-4 sandbox run. All ten parse (lookbacks 1,605 to 1,677 hours); the sandbox log stands at 83 rows,
none of generation 4.

1. Ten ideas, T-07 among them: accepted. A weak idea adds a likely zero to k and nothing else.
2. T-01 and T-02 are "family seen"; T-08 is not (it ranks whether volume leads moves, another quantity than a
   price delay behind BTC). If k reaches 3 only with both family-seen ideas among the three, the proposal to
   the human says so.
3. The two closed top30 forms whose next30 reading was never logged: they are added to THIS round, now, before
   any run, and not left for a second version decided after results. They run as registered in generation 2,
   unchanged and at their defaults, and count toward k with their registered signs: T-11 =
   strategies/gen002_prior_month_reversal.omr (reversal of the month before last; liquidity provision is the
   textbook case for less liquid assets) and T-12 = strategies/gen002_activity_fade.omr (fading an activity
   burst). The stop list of playbook 8b closes them for a top30 registration; a premise test submits nothing.
   So the round has TWELVE ideas, and with no edge three or more of twelve reach 1.0 in about 3 rounds of 100.
4. A book on the level of illiquidity, for information only: no. A level is a persistent premium, which G6 does
   not credit; it could not become a rule of the unit this test is about.
5. T-05: open (the comovement of premium changes with volume changes is not a contrarian premium shock); it
   reads the basis, as T-03 and T-10 do, and T-04 reads funding. All four are marked; nothing is submitted.
6. Beta neutrality: accepted as in generation 3's round 5 (a neutrality constraint, DEV-informed in motive).
   T-04's entrants waiting 28 days: accepted.
7. Budget: 12 default runs, at most 4 corner runs for an idea that passes the top30 screen W1 to W8, 2 in
   reserve; cap 18 of generation 4's 60. One run at a time; a run starts when at least 1,000,000 KB of physical
   memory and 4,000,000 KB of commit headroom are free.
8. A run that prints no next30 Sharpe (a code in its place) counts as below 1.0.
9. The reading rule stands as decided (KERNEL_PROPOSALS.md, entry of 2026-11-27): k = the number of the twelve
   with a next30 DEV Sharpe of 1.0 or more with the registered sign; 3 or more and a unit for the less liquid
   tier is proposed to the human; 2 or fewer and the front is closed. The researcher's own expectation,
   recorded before any number: k = 0 most likely.
10. Stage 2 starts only after this plan and its programs are on the remote and the kernel's strategy test has
    passed with the new files in place. Its parts are appended below.

## Sandbox run log (round 1), filled in during stage 2

(Appended below the coordinator's rulings, so that the 36,075 bytes committed as e116ad8 stay an unchanged prefix.
Every run is listed, in the registered order. Each command was `python -m omr.sandbox strategies/<file>.omr --g6-lags`
at the defaults, full stage 1 (25 truncation cuts), one at a time, started only after the memory reading of ruling 7
(free physical 2.96 to 5.30 million KB, virtual 10.54 to 10.79 million KB). Output saved as ASCII in the session scratch
folder, gen004_r1/run_NN_<name>.txt, by gen004_r1/run_round1.py, which only calls the sandbox. Pre-cost = DEV Sharpe +
(DEV Sharpe - G4 DEV). Years: the number of 2020, 2021, 2022H1 with a return above 0. Costs: equity over DEV, with
C/G = costs / avg gross.)

| # | idea | next30 DEV | top30 DEV | G4 DEV | G2 DEV | pre-cost | r(1), r(2), r(3) | A of 10; B | years + (SR 2020 / 2021 / 2022H1) | names held | costs (C/G) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | T-01 btc_catchup | -0.568 | -0.544 | -0.950 | -1.223 | -0.138 | -0.009, -0.015, -0.014 | 6; -0.952 | 0 (-0.156 / -0.648 / -0.817) | 27.7 | 0.1924 (0.225) |
| 2 | T-02 impact_reversal | 1.259 | -0.984 | -1.340 | -1.519 | -0.628 | -0.014, -0.007, -0.004 | 4; -0.563 | 0 (-0.560 / -1.736 / -0.521) | 27.7 | 0.1911 (0.222) |
| 3 | T-03 premium_feedback | -1.402 | 0.565 | 0.300 | -0.141 | 0.830 | 0.078, -0.039, -0.053 | 6; -0.268 | 2 (1.267 / 1.313 / -1.615) | 27.7 | 0.1832 (0.215) |
| 4 | T-04 leverage_loading | 0.394 | -0.407 | -0.676 | -1.077 | -0.138 | 0.024, -0.035, -0.013 | 0; 0.778 | 1 (-0.343 / -1.083 / 1.754) | 22.7 | 0.1129 (0.138) |
| 5 | T-05 premium_volume | -1.078 | -0.063 | -0.335 | -0.773 | 0.209 | -0.022, -0.088, -0.002 | 6; -0.105 | 1 (-0.369 / 0.417 / -0.625) | 27.7 | 0.1418 (0.166) |
| 6 | T-06 rally_tickets | 0.020 | 0.094 | -0.174 | -0.638 | 0.362 | 0.032, -0.030, -0.051 | 9; -1.499 | 2 (0.679 / 0.961 / -2.527) | 27.7 | 0.1539 (0.180) |
| 7 | T-07 move_tickets | 0.095 | -0.582 | -0.866 | -1.386 | -0.298 | 0.053, -0.022, -0.016 | 9; -1.768 | 1 (0.795 / -1.217 / -1.191) | 27.7 | 0.1344 (0.157) |
| 8 | T-08 volume_lead | -0.981 | 0.220 | -0.067 | -0.642 | 0.507 | 0.223, -0.132, -0.089 | 1; 1.779 | 2 (-1.567 / 0.686 / 2.250) | 27.7 | 0.1103 (0.129) |
| 9 | T-09 gain_chasing | 0.554 | 1.102 | 0.862 | 0.344 | 1.342 | 0.274, -0.066, -0.083 | 5; -0.187 | 2 (0.743 / 2.325 / -0.926) | 27.7 | 0.1669 (0.196) |
| 10 | T-10 premium_tickets | 1.559 | -1.431 | -1.727 | -2.200 | -1.135 | -0.031, -0.086, 0.004 | 6; -1.254 | 0 (-1.279 / -1.760 / -1.112) | 27.7 | 0.1002 (0.117) |
| 11 | T-11 prior_month_reversal | -0.790 | 0.381 | 0.057 | -0.297 | 0.705 | 0.030, -0.085, -0.002 | 8; -0.658 | 2 (-0.647 / 0.292 / 2.172) | 27.9 | 0.1772 (0.205) |
| 12 | T-12 activity_fade | -0.332 | 0.172 | -0.140 | -0.457 | 0.484 | -0.165, -0.014, 0.007 | 1; 0.899 | 2 (-1.098 / 0.564 / 1.063) | 27.7 | 0.1669 (0.195) |

Every run: stage 1 PASS, exit 0, nothing on stderr, not liquidated, 75 symbols ever in the unit, next30 over 100
symbols (a Sharpe printed for all twelve, no code), names held of 28.0 in play, benchmark (equal-weight long of the
in-play members) DEV Sharpe 0.619, maxDD 0.847. Wall times 79.2 to 211.2 s. Other printed numbers (direction changes;
avg gross; rebalances; PSR(0); maxDD; gross funding paid / received): T-01 2001, 0.854, 599, 0.189, 0.346, 0.3228 /
0.3371; T-02 2093, 0.859, 871, 0.065, 0.685, 0.2949 / 0.3070; T-03 1130, 0.853, 597, 0.810, 0.256, 0.4439 / 0.5054; T-04
979, 0.816, 617, 0.260, 0.451, 0.2961 / 0.3072; T-05 1190, 0.856, 604, 0.461, 0.291, 0.3616 / 0.3928; T-06 1141, 0.855,
594, 0.559, 0.294, 0.4015 / 0.4139; T-07 1145, 0.854, 591, 0.176, 0.428, 0.3811 / 0.3920; T-08 1067, 0.855, 555, 0.636,
0.285, 0.3254 / 0.3127; T-09 980, 0.853, 578, 0.952, 0.233, 0.4825 / 0.5058; T-10 1165, 0.855, 570, 0.011, 0.515, 0.2822
/ 0.2725; T-11 1894, 0.866, 838, 0.727, 0.201, 0.3687 / 0.3570; T-12 1635, 0.854, 625, 0.607, 0.319, 0.3466 / 0.3325.
Speed-limit rows from 2020-07-20 14:00 (2020-08-24 for T-04; 2020-07-17 for T-11) to 2022-06-30 22:00; paired lags 30 to 262 days,
decisions 2021-06-30 23:00 to 2022-06-30 22:00. Year rows are counted by their return, as fixed; no year row had a
return and a Sharpe of opposite signs.

Total sandbox runs in round 1: 12 of the cap of 18 (12 defaults; no corner, no reserve). No stage-1 rejection, no
kernel fault, no refusal. ledger/sandbox_log.jsonl now has 95 rows (83 + 12), rows 83 to 94 (0-indexed), each written
by the sandbox, its logged next30, top30, G2, G4, names held, speed limit and paired readings equal to the printed ones.
Generation 4 has used 12 of 60 sandbox runs. No idea passed W1 to W8, so no corner was due.

## Amendments (round 1), stage 2

none: no program text, param, default, screen item or run condition was changed, and the reserve was not used.

## The round's reading: next30 and k

| idea | next30 DEV Sharpe | 1.0 or more with the registered sign | family seen |
|---|---|---|---|
| T-01 btc_catchup | -0.568 | no | yes |
| T-02 impact_reversal | 1.259 | YES | yes |
| T-03 premium_feedback | -1.402 | no | no |
| T-04 leverage_loading | 0.394 | no | no |
| T-05 premium_volume | -1.078 | no | no |
| T-06 rally_tickets | 0.020 | no | no |
| T-07 move_tickets | 0.095 | no | no |
| T-08 volume_lead | -0.981 | no | no |
| T-09 gain_chasing | 0.554 | no | no |
| T-10 premium_tickets | 1.559 | YES | no |
| T-11 prior_month_reversal | -0.790 | no | no |
| T-12 activity_fade | -0.332 | no | no |

k = 2 (T-02 and T-10). One of the two is family seen (T-02); T-10 reads the basis (index_close). Every one of the
twelve printed a next30 Sharpe, so ruling 8 did not come into play. By the rule fixed in advance (KERNEL_PROPOSALS.md,
entry of 2026-11-27; ruling 9), k of 2 or fewer: the place gap is closed as a front for these data and no unit for the
less liquid tier is proposed. With no edge, two or more of twelve reach 1.0 in about 14 rounds of 100 (binomial, one
in 18 each; my arithmetic): the count is in the range chance gives.

## Top30 screen outcome per idea (information)

| idea | W1 | W2 (pre-cost >= 1.5) | W3 (G4 > 0) | W4 (G2 > 0) | W5 (next30 >= 0.3) | W6 (r <= 0.40) | W7 (A <= 4, B > 0) | W8 (years) | first failed |
|---|---|---|---|---|---|---|---|---|---|
| T-01 | pass | FAIL (sign: -0.544) | FAIL | FAIL | FAIL (-0.568) | pass | FAIL (6; -0.952) | FAIL (0) | W2 |
| T-02 | pass | FAIL (sign: -0.984) | FAIL | FAIL | pass (1.259) | pass | FAIL (4; -0.563) | FAIL (0) | W2 |
| T-03 | pass | FAIL (0.830) | pass | FAIL | FAIL (-1.402) | pass | FAIL (6; -0.268) | pass (2) | W2 |
| T-04 | pass | FAIL (sign: -0.407) | FAIL | FAIL | pass (0.394) | pass | pass (0; 0.778) | FAIL (1) | W2 |
| T-05 | pass | FAIL (sign: -0.063) | FAIL | FAIL | FAIL (-1.078) | pass | FAIL (6; -0.105) | FAIL (1) | W2 |
| T-06 | pass | FAIL (0.362) | FAIL | FAIL | FAIL (0.020) | pass | FAIL (9; -1.499) | pass (2) | W2 |
| T-07 | pass | FAIL (sign: -0.582) | FAIL | FAIL | FAIL (0.095) | pass | FAIL (9; -1.768) | FAIL (1) | W2 |
| T-08 | pass | FAIL (0.507) | FAIL | FAIL | FAIL (-0.981) | pass | pass (1; 1.779) | pass (2) | W2 |
| T-09 | pass | FAIL (1.342) | pass | pass | pass (0.554) | pass | FAIL (5; -0.187) | pass (2) | W2 |
| T-10 | pass | FAIL (sign: -1.431) | FAIL | FAIL | pass (1.559) | pass | FAIL (6; -1.254) | FAIL (0) | W2 |
| T-11 | pass | FAIL (0.705) | pass | FAIL | FAIL (-0.790) | pass | FAIL (8; -0.658) | pass (2) | W2 |
| T-12 | pass | FAIL (0.484) | FAIL | FAIL | FAIL (-0.332) | pass | pass (1; 0.899) | pass (2) | W2 |

All twelve failed W2 first: six with the wrong sign in top30 over DEV (T-01, T-02, T-04, T-05, T-07, T-10), six with the
registered sign under the pre-cost floor (T-09 1.342, T-03 0.830, T-11 0.705, T-08 0.507, T-12 0.484, T-06 0.362). T-09
came closest: it failed W2 and W7 only. No corner and no control was due; nothing is recommended, as the plan fixed.

## DEV observations (round 1; NOT hypotheses)

- The twelve next30 readings: mean -0.106, standard deviation 0.929, 6 positive, 4 at 0.3 or more, 2 at 1.0 or more, 2
  at -1.0 or less; range -1.402 to 1.559. The 42 logged before: mean -0.265, standard deviation 0.661, 16 positive, 8 at
  0.3 or more, 1 at 1.0 or more, 4 at -1.0 or less. All 54: mean -0.229, 3 at 1.0 or more (X-08, T-10, T-02). The
  round's spread is wider than one number's sampling noise (about 0.63; for twelve draws the spread itself would read
  0.63 give or take about 0.13); suggestive only, and it cuts both ways (the three B ideas read -1.402, 0.394, -1.078).
- Tiers disagreed more than before: across the twelve the correlation of the top30 and next30 DEV Sharpes of the same
  program was -0.589 (same sign in 4 of 12), against +0.244 over the 42 logged (23 of 42). The two readings that counted
  both came with a top30 book that lost in every DEV year (T-02 -0.984, T-10 -1.431), the profile of X-08, Y-05 and Y-13
  before; the books with the best top30 readings (T-09 1.102, T-03 0.565, T-11 0.381) read 0.554, -1.402 and -0.790 on
  next30. No rule earned in both tiers at the size the rule asks.
- DEV is now spent on next30 for the mirrors of the strongly negative readings (T-03 short premium feedback -1.402, T-05
  -1.078, T-08 -0.981): flipped, they would be flipped readings, not discoveries.
- The two closed top30 forms added by ruling 3 read negative on next30 (prior-month reversal -0.790, activity fade
  -0.332); the textbook liquidity-provision case did not show in ranks 31 to 60 at the month-before-last horizon.
- Costs: 0.100 to 0.192 of equity over DEV (C/G 0.117 to 0.225); G4 drops 0.240 to 0.406, G2 drops 0.535 to 0.862 (larger
  than G4's in all twelve). T-01, whose whole book reverses when BTC's last-day sign flips, cost 0.192 (C/G 0.225), less
  than the 1.5 to 2 times a rank book the plan estimated; its G4 drop (0.406) was the largest. T-04's names held were
  22.7 of 28.0, the 28-day wait of entrants, as expected. Speed limit -0.165 to 0.274 at one to three steps.
- WEAK throughout: one DEV period, one default each, one researcher session; a next30 reading is one DEV number after
  the top30 cost rate with no stress; nothing here is a parameter recommendation, and no corner was run.

# PLAN version 2 (round 2: the spot premise study, KP-029), stage 1, written 2026-11-28 before any spot file exists here

(Appended below version 1 and its round-1 record, so that the 46,323 bytes before it (sha256 a507a4d9aaeb5291...) stay an
unchanged prefix. Researcher session for generation 4, round 2, stage 1; a fresh session that knows the project only from
the files named below.)

## Head (version 2)

- What: a premise study of the spot market of the same coins (Binance spot klines 1h: quote volume, taker-buy quote
  volume) on DEV only, OUTSIDE the sandbox and the kernel, under the rule KP-029 fixed in advance. Why: admitting the
  dataset is a re-key (a build, audits, about 13 machine hours), so its premise is tested first with the tools as they
  are, as round 1 tested the tier premise. By whose decision: the human's of 2026-11-28 ("Run the cheap check"), ordered as
  round 2 by the coordinator. This is stage 1 (plan, code, validation); stage 2 (download, runs) is ordered separately,
  after this version and studies/kp029/ are committed and on the remote.
- Kernel: omr.status OK d09812fdec752a17, semantic 7d923e7e2375986d, sealed (top30 0.10); omr.kernel_lock verify OK before
  and after. Data research_hash 28d9084a8c5c7659, validated. Ledger M = 6. Sandbox log 95 rows, unchanged: the study writes
  no sandbox or ledger row and imports neither omr.sandbox nor omr.evaluate.
- Read: KP-028, KP-029 and the two entries after it; the desk study note (2, 4, 5, coordinator's note); the playbook 4, 4b,
  5, 8b, 9; version 1 and its record; generation 3's S10, corner and control rulings; CONSTITUTION 3 to 7, 13; LANGUAGE 5
  to 7, 10; LESSONS 44 to 68; read-only code: omr/sandbox.py, upipeline.py, interp.py, universe.py, datasets.py,
  engine.py, pipeline.py, stats.py, lang.py, kernel_lock.py, tests/test_structure.py, tests/conftest.py.
- Not opened: data/ except through the kernel's loaders under dev_end; ledger/returns/, ledger/trials/; no spot file, no
  Binance address; _build/kp029_study/ does not exist. Run: a parse check of the eight study programs (all pass, constant
  probe included), validate_evaluator.py (exact, below), synthetic_tests.py (22 of 22), spot_plan.py, and pytest
  tests/test_structure.py -q (9 passed with the new folder in place). Numbers seen: all of version 1 and of generation 3's
  plans; no number of any spot hypothesis exists, and none can before stage 2.
- Files: this text and studies/kp029/ (README.md; kp029_spot.py, kp029_features.py, kp029_eval.py; programs/ with four
  hypotheses and four controls; validate_evaluator.py and validation_stage1.json; synthetic_tests.py; spot_plan.py and
  spot_symbols.json; download_spot.py and run_study.py, not run). Nothing else was written.

## The rule fixed in advance (KERNEL_PROPOSALS.md, KP-029, quoted unchanged)

> a hypothesis passes if it meets the wide screen of playbook 8b as far as that can be computed outside the sandbox, with
> the floor before costs raised from 1.5 to 1.85, AND then holds at its corners, AND beats its control (the same book with
> the perpetual's own volume or flow in place of the spot input: the new data must add to what the kernel already has). If
> at least one hypothesis passes, the coordinator brings the human the proposal to admit the dataset, with the numbers. If
> none passes, the spot front is closed, the dataset is not proposed, and the search is parked.

By the human's decision a pass first goes to an independent auditor of the study. The exact form is in "The pass rule
made exact"; nothing in it is looser than these words.

## The evaluation path

Finding. The kernel's scoring functions take a weight matrix, not a program: Blocked.run / run_targets (the universe
engine: costs, funding, liquidation check, rebalance band), dev_speed_limit, dev_names_held and dev_paired_lags take W
(with stage 1's known channel and the in-play mask); only the weights (Blocked.unit, stage1_u) and next30_score need a
program. So no evaluator that mirrors the engine was written.

The path. The hypotheses are programs of the kernel's own language (studies/kp029/programs/*.omr), computed by the
kernel's interpreter, block path and stage 1. The language has no spot field, so the study serves spot through two SLOTS
of the perpetual klines table, for study programs only:

    volume := SPOT quote volume (USDT);  taker_buy_volume := SPOT taker-buy quote volume (USDT); same coin, same hour.

They are filled through the UData loader hook (omr.upipeline.UData(loader=...), a constructor argument): the study's
loader (kp029_features.study_udata) returns the kernel's own tables of the symbol, as load_udata("dev_end") reads them,
with those two columns replaced. Nothing of the kernel is copied, replaced or patched; every other column, the membership,
in-play mask, funding, mark and index tables and every engine column stay the kernel's. kp029_eval then makes the
sandbox's calls in its order: stage1_u (24 random truncation cuts + DEV end, start cuts, block_overlap, activity),
Blocked.run, stats.summary and per_year, the benchmark, dev_speed_limit, dev_names_held, the G2 and G4 runs
(dev_sharpe_of), dev_paired_lags, then next30_score(end = DEV end) after the top30 panel is released.

Why: (1) guard D1 (KNOWN channel, windows, tf_last, in-play cs_*, uniform warm-up, weight rule, execution at the next
open) holds by construction, and the kernel's stage-1 self-checks run on every study program; (2) the study's own
look-ahead surface shrinks to joining one spot row to the perpetual row of the same hour; (3) the books are built as the
registered weekly programs are (costs and turnover compare) and as programs after an admission would be (two fields
renamed). The price: the slot map must be kept in mind; every study program states it and kp029_features.SLOTS holds it.

Validation (studies/kp029/validate_evaluator.py; output validation_stage1.json; about 105 s per program). Three registered
weekly top30 programs of different construction (a price against its high; a market-state switch; a beta-neutral
correlation book), weights from the kernel's interpreter and full stage 1 (25 cuts, 7 start cuts, all OK), scored through
kp029_eval, against the sandbox's logged rows 49, 68 and 91 (kernel d09812fdec752a17) and the numbers the plans printed:

| reading | W-01 high_anchor (n 42) | X-09 state_continuation (k 21, ls 56) | T-09 gain_chasing (j 3, k 42, nb 42) |
|---|---|---|---|
| DEV Sharpe | 1.557518 = | 1.618957 = | 1.101843 = |
| G4 / G2 DEV | 1.295576 / 0.887789 = | 1.359318 / 1.032097 = | 0.862005 / 0.344343 = |
| next30 DEV (symbols) | 0.600567 (100) = | 0.106355 (100) = | 0.554196 (100) = |
| speed r(1), r(2), r(3) | 0.129146, -0.080298, -0.032382 = | -0.071830, -0.015997, -0.060955 = | 0.274324, -0.066449, -0.083110 = |
| paired A of 10; p; B; stale median | 6; 0.636364; -0.549138; -0.528415 = | 2; 0.272727; 0.579133; -0.540789 = | 5; 0.545455; -0.187036; -0.413398 = |
| names held / in play | 27.664138 / 28.038348 = | 27.628740 / 28.038348 = | 27.734935 / 28.038348 = |
| direction changes; rebalances | 1198; 571 = | 1433; 636 = | 980; 578 = |
| funding paid / received | 0.731965 / 0.793809 = | 0.622642 / 0.687370 = | 0.482490 / 0.505771 = |
| years SR 2020 / 2021 / 2022H1 (printed) | 3.721 / 1.831 / -2.093 = | 2.312 / 1.532 / 1.025 = | 0.743 / 2.325 / -0.926 = |
| avg gross; costs (printed) | 0.855; 0.3024 = | 0.855; 0.3138 = | 0.853; 0.1669 = |

"=": every logged reading reproduced exactly (difference 0.0 in floating point over all 60 logged values compared, 20 per
program, the speed-limit start row included; the table shows 6 decimals); the printed numbers to the digits printed;
benchmark 0.619 / maxDD 0.847 as printed. With the spot wrapper and no spot data, each program's weights and engine run
are bit-identical to the kernel's.

Screen readings: W1 (stage1_u's self-checks and activity, direction changes, Run.gross, dev_names_held, Run.liquidated),
W2 to W4 (Blocked.run, dev_sharpe_of at costs x2 and at funding paid x1.5 / received x0.5), W5 (next30_score on the
study's UData; the spot of next30 coins is downloaded too), W6 (dev_speed_limit), W7 (dev_paired_lags) are each
reproduced exactly above; W8 (stats.per_year) to the printed digits with every sign equal. NOT COMPUTABLE: none of the
eight. The sandbox's log row and printout are replaced by studies/kp029/run_log.jsonl and run_study.py's print.

## The hypotheses

Base rate, plainly: of the 46 ideas put to the wide screen so far, none passed, at a floor before costs of 1.5; this
screen's is 1.85. The desk study's analyst put the chance that a rule on these data clears the bar on held-back data at
well under one in ten, and found no published evidence that spot against perpetual volume or flow says which coins beat
which over a week (S44). My expectation, recorded before any number: no hypothesis passes.

Shared construction (all eight programs): kind portfolio, unit top30, decided once a week (a weekly series visible at the
bar that opens Sunday 23:00 UTC, traded at the Monday 00:00 open), rank weights, dollar neutral and beta neutral by
generation 3 round 5's projection (bd = the centred daily beta to BTC over nb days; w = z - (mean(z bd) / mean(bd bd)) bd),
gross 1; only H-S3 and its control are gated (with their own W1). No funding, mark or index input (KP-017 does not bear);
no numeric literal but the gate value 1 of H-S3 and C-S3; lookback 1,605 hours in all eight (the beta window); a spot
window reaches at most 43 days back; spot enters only as ratios of slots or as log changes, so no ratio mixes units. As
windows and bins need every hour known, ONE missing or guarded spot hour removes that coin from the weekly decisions whose
inputs hold it: 6 for H-S1 and H-S3 at their defaults (synthetic test 8a; lag's window includes its own rows, LANGUAGE.md
6), 2 for H-S2, 5 or 6 for H-S4; a market-wide missing hour leaves those decisions flat. The controls lose the same coins.

The controls (one rule): the hypothesis with the spot input DROPPED, all else unchanged. Read literally ("the perpetual's
own volume or flow in place of the spot input") a contrast of spot against perpetual is zero, so the perpetual's part is
kept: the book the kernel can already build. Each control reads the spot term only through where(spot_term > 0,
perp_term, perp_term), whose value is the perpetual term and which is known only where the spot term is: the control holds
the same coins in the same weeks (coverage matched), so a hypothesis cannot beat it by which coins have spot data.

### H-S1 kp029_hs1_share_shift: trading moving from spot to the perpetual, bet against (the desk study's H-S1)
- Feature: xp = log(the perpetual's mean daily quote volume over the last k days / its mean over the n days before them,
  lag(sma(qp, n), k)); xs the same for spot; x = xp - xs (the change of the log perp-to-spot volume ratio), weekly. Sign:
  SHORT the largest x, long the smallest. k = param(7, 5, 9), n = param(28, 22, 34), nb = param(42, 33, 51).
- Mechanism: a rise of the perpetual's share is new leveraged demand (or shorting), fragile, unwound at the next stress; a
  rise of the spot share is buying by holders, unlevered. Other side: leveraged perpetual traders.
- Changed from the desk study: the reference is the 4 weeks before the last week, not 8 (half the weeks a missing spot
  hour keeps a coin out; faster for G6), excluding the last week (lag), as the desk study's words do.
- Bar check: drag 0.35 (lessons 54, 59: 0.23 to 0.45; activity_fade, a one-week input, 0.31): 1.09 before costs in VAL for
  G1's line, 1.85 for decent odds; DEV floor 1.85 (W2).
- Outside evidence: none for this ratio; related only: He, Manela, Ross, von Wachter (perp-spot deviations track leveraged
  demand; pricing, not a weekly predictor).
- Bias: bets AGAINST pressure lost in every DEV year in top30 (lesson 56); the perpetual's own volume books read -0.375
  (W-09) and +0.172 (activity_fade), next to C-S1. The sign is the mechanism's. Remembered: perpetual-led pumps of 2021.
- Control C-S1 kp029_cs1_perp_volume_shift: x = xp, short the largest, coverage matched through xs. Corners: 0.8 (k 6, n 22,
  nb 34); 1.2 (k 8, n 34, nb 50).

### H-S2 kp029_hs2_spot_flow: aggressive buying on spot against aggressive buying on the perpetual (the desk study's H-S2)
- Feature: ss = spot taker-buy quote volume / spot quote volume over the last k days (sums of daily bins); sp the same on
  the perpetual; x = ss - sp, weekly. ONE sign: LONG the largest x, short the smallest. k = param(7, 5, 9), nb as H-S1.
- Mechanism: aggressive spot buyers hold unlevered, so their pressure persists; aggressive buying on the perpetual is
  leveraged and unwinds (H-S1's story on signed flow). The named confound has the OPPOSITE sign: cash-and-carry (buy spot,
  sell the perpetual when the premium is rich) raises x when perpetual longs are crowded. A negative reading fails.
- Bar check: drag 0.40 (one-week taker measures re-ranked weekly; lesson 54: 0.24 to 0.45): 1.14 / 1.90 in VAL. Outside
  evidence: none cross-sectionally (order-flow imbalance predicts over minutes to hours). Bias: the perpetual's taker books
  read strongly on DEV (lesson 53: -2.514 in every year); C-S2 is a taker-share book of another construction.
- Control C-S2 kp029_cs2_perp_flow: SHORT the largest sp (the perpetual part of x), coverage matched through ss. Corners:
  0.8 (k 6, nb 34); 1.2 (k 8, nb 50).

### H-S3 kp029_hs3_leverage_gate: a market-wide gate on the same ratio (the desk study's H-S3)
- The book it gates, named in advance: H-S1's, unchanged. The gate: m = the unit's mean of H-S1's x over the coins in play
  at the weekly decision; ON for the week when m > 0 (the market's trading moved toward the perpetuals), flat otherwise.
- Mechanism: after a market-wide build-up of perpetual trading the unwinding falls hardest on the coins whose own share
  rose most; after a move toward spot there is little to unwind. Bar check: ON about half the weeks, costs and volatility
  both roughly halve: drag 0.35 (1.09 / 1.85). Outside evidence: none. Bias: the leverage flushes of May 2021 and May 2022
  are the picture the gate is drawn from, and they are DEV.
- Control C-S3 kp029_cs3_volume_gate: C-S1's book, ON when the unit's mean of xp > 0 (spot dropped from book and gate),
  coverage matched. Corners as H-S1. Its own W1: see the pass rule.

### H-S4 kp029_hs4_rally_carrier: which market carries the rallies (added)
- Feature: dsh = the daily log change of the perp-to-spot quote-volume ratio (logret(daily(quote_volume), 1) -
  logret(daily(volume), 1)); c = corr(dsh, rd, k), rd the daily log return; weekly. SHORT the largest c (up days come with
  trading moving to the perpetual), long the smallest. k = param(28, 22, 34), nb.
- Mechanism: rises carried by leveraged perpetual buying overshoot and give back; rises carried by spot buying are bought
  by holders. Round 1's T-06 construction (who carries the rallies) on the venue instead of the ticket size. Bar check: a
  4-week correlation re-estimated weekly (T-06 dropped 0.27 under G4): drag 0.30 (1.04 / 1.80). Outside evidence: none.
  Bias: T-06 read 0.094 in top30 on DEV (known).
- Control C-S4 kp029_cs4_volume_return: c = corr(daily log change of the perpetual's own quote volume, rd, k), short the
  largest, coverage matched through the spot term's correlation. Corners: 0.8 (k 22, nb 34); 1.2 (k 34, nb 50).

Expected correlations: H-S3 with H-S1 high (its ON weeks); H-S1 with H-S4 moderate; H-S2 with the others low to moderate;
each control with its hypothesis moderate to high. At worst two bets (volume share, signed flow), not four. Classes: L,
leverage share (H-S1, its gate H-S3, H-S4); F, venue of the flow (H-S2).

## The pass rule made exact (fixed now; studies/kp029/kp029_eval.py holds the same numbers)

A hypothesis PASSES when (a), (b) and (c) all hold, every run among them with its truncation test passed.

(a) The screen at its default (playbook 8b's wide screen, items as numbered in version 1, the floor raised):

| item | threshold (all on DEV, at the default) |
|---|---|
| W1 | the kernel's stage 1 passes (no self-check fault; activity >= 20); direction changes >= 30; avg gross (Run.gross mean over DEV) >= 0.5; names held >= 15; not liquidated. H-S3 only (a gated book): direction changes >= 30, not liquidated, ON in 25% to 75% of the DEV decision hours with a unit, and over the ON hours avg gross >= 0.5 and names held >= 15 (ON less than a quarter of the time is too sparse to read; more than three quarters is H-S1 by another name) |
| W2 | DEV Sharpe + (DEV Sharpe - G4 DEV Sharpe) >= 1.85 |
| W3 | G4 DEV Sharpe > 0 |
| W4 | G2 DEV Sharpe > 0 |
| W5 | next30 DEV Sharpe >= 0.3 (a code in place of a Sharpe fails) |
| W6 | r(1), r(2), r(3) each <= 0.40 (a reason line in place of the values fails) |
| W7 | at most 4 of 10 stale copies at least as good AND the book median over the last 365 days of DEV > 0 (a refused reading fails) |
| W8 | at least two of 2020, 2021, 2022H1 with a return above 0 |

A wrong sign is a failure; no sign is flipped; no default is changed after a run; numbers are read unrounded from the row.

(b) Its corners: generation 3's rule S10 (generations/gen003/PLAN.md line 235; applied in rounds 3 to 5 and in version 1):
the 0.8 and the 1.2 corner, every param at the same G5 end (integers rounded; a param left unchanged by rounding moves by
1), each with DEV Sharpe > 0 AND G4 DEV Sharpe > 0. The corners are listed with each hypothesis.

(c) Its control: the hypothesis's DEV Sharpe before costs at its default must exceed its control's DEV Sharpe before costs
at the control's default by at least 0.5: generation 3's number (rounds 3, 4 and 5, ruling 3 each) and the coordinator's
suggestion. One DEV Sharpe carries a standard error of about 0.65; a hypothesis and its coverage-matched control share the
perpetual term, so their difference is measured more tightly (about 0.5 to 0.65 at a return correlation of 0.5 to 0.7);
0.5 asks the spot input to add about one such error ON TOP of a 1.85 floor. A control is never screened on its own.

Void: a run whose study truncation test fails, or whose kernel stage 1 faults, has no reading; it is fixed by an amendment
written before a re-run from the reserve. If at least one hypothesis passes, the coordinator has the study audited and then
brings the human the proposal; if none passes, the spot front is closed and the search is parked.

## Look-ahead guards (built in stage 1)

- D1 timing = the kernel's KNOWN channel, by construction (above): a spot bar is final at its close, as a klines bar; a
  weekly decision uses the bin closing at the Sunday 23:00 bar; positions take effect at the next open (the kernel's engine).
- D2 the study truncation test (kp029_eval.truncation_test), run in stage 2 for every hypothesis, control and corner BEFORE
  any reading is computed: 6 fixed cuts (decision bars 2020-08-16, 2021-04-11 and 2021-12-19 23:00; 2020-12-13 22:00, an
  hour before one; mid-week 2021-08-18 13:00 and 2022-05-10 07:00) and 2 random DEV hours (fresh entropy, seed logged). At
  each cut every perpetual and spot row after it is dropped, the slots are re-derived from what is left, the program is
  evaluated by the kernel's block path up to the cut, and weights, raw values and known flags of every row up to it must
  equal the full run's bit for bit; a failure makes the run void. The kernel's own 25-cut self-check runs as well.
- D3 synthetic proofs (synthetic_tests.py; 15 synthetic perpetuals, one 1000-prefixed, synthetic spot): 22 of 22 pass.
  Changing every perpetual and spot row after a cut (three cuts) leaves every weight, raw value and known flag at or
  before it identical while later rows change. The truncation test passes on the honest path (8 cuts) and FAILS on a
  deliberate one-hour look-ahead. One missing spot hour (2021-03-10 12:00) removes that coin from exactly the six weekly
  decisions 2021-03-14 to 04-18, the other 14 stay known; the same hour with ZERO volume keeps it known; a spot close 6%
  off acts as a missing hour (4% off is kept); S3 on spot (the 25th zero-trade hour unknown). Also: the ceiling (no month
  outside 2019-12 .. 2022-06 can be named, later rows dropped, a stored 2022-07 file or a checksum mismatch stops the
  loader), the CSV parser, the symbol map, slot isolation (a perpetual-only program is bit-identical through the wrapper),
  and the whole stage-2 path on H-S1 into a temporary log, the coverage count finding a planted market-wide missing hour.
- D4 the join guard: a spot row is used only when spot close x multiplier lies within 5% of the perpetual's close of the
  same hour, else both slots are unknown; spot bars follow the kernel's rule S3; rows with a non-finite or non-positive
  close, a negative volume or a taker-buy volume above the volume are dropped (unknown) and counted; 1000XXXUSDT (and
  1000000XXXUSDT) map to spot XXXUSDT with multiplier 1000 (1e6) in the guard only; quote volumes are compared in USDT.
- D5 the ceiling, hard-coded in kp029_spot.py: no URL of a month after 2022-06 (or before 2019-12) can be built; a stored
  file of such a month stops the loader; rows after 2022-06-30 23:00 UTC are dropped on load; every zip is checked against
  its .CHECKSUM at download and at every read. 2019-12 is the only warm-up month (the universe grid starts 2019-12-31).

## The download (stage 2; download_spot.py --go)

- What (studies/kp029/spot_symbols.json, from the kernel's DEV membership): 114 perpetuals ever a member on DEV (75 of
  top30, 100 of next30), 114 spot pairs, one 1000-prefixed (1000SHIBUSDT -> SHIBUSDT), each with a folder in the desk
  study's cached listing. Months per pair: from the month holding (first member month - 97 days, the block warm-up that
  covers the 90-day lookback) to the last member month, within 2019-12 .. 2022-06: 1,911 zips and 1,911 .CHECKSUM files.
- Size about 68 MB (35.5 KB per zip, the mean of 170 such files of six pairs in the cached listings) plus 0.2 MB of
  checksums. Time: 3,822 requests, plus one per month the archive does not hold (a 404 on the checksum, then no zip
  request), strictly one at a time with a pause of at least 0.25 s: about 32 to 45 minutes.
- Rules: data.binance.vision only; User-Agent research-data-client/1.0, nothing identifying; one connection; a file kept
  only when its sha256 equals its checksum; resumable; outcomes logged (no data row) in _build/kp029_study/spot/. Without
  --go it fetches nothing.
- Before the first evaluation `run_study.py --coverage` counts the spot data only (no book): per perpetual the active hours
  of its window, spot rows present, slots known after the guard, and the hours at which 80% or more of the pairs have no
  row (market-wide), into studies/kp029/spot_coverage.json; no evaluation runs before that file exists.

## Run order and budget (decided now; run_study.py enforces it)

- First the download and the coverage count; neither evaluates anything.
- Runs 1 to 4: the defaults in the order H-S1, H-S2, H-S3, H-S4 (`.venv\Scripts\python.exe -I studies\kp029\run_study.py
  <stem>`), one at a time under the memory floor (1,000,000 KB physical, 4,000,000 KB commit). Every default runs, whatever
  the earlier ones read.
- Then, only for a hypothesis that passed the screen at its default, in run order: its control, then the 0.8 corner, then
  the 1.2 corner, stopping at its first failure (the control first: one run decides whether the spot input adds anything).
  At most 3 runs per survivor, 12 in all.
- Reserve: 2 runs, only to re-run a void or faulted run after an amendment. Cap 18 evaluations. Every evaluation, failed
  and void ones included, is a row of studies/kp029/run_log.jsonl (time, hypothesis, parameters, every reading, screen
  items, truncation cuts and result, the sha256 of every study file, kernel hash, versions). The verdict: `run_study.py
  --summary`. Nothing here is a counted trial or a recommendation for one; a pass leads to an audit and a proposal.

## Questions for the coordinator

1. The spot slots are filled through the UData loader hook, a kernel constructor argument; no kernel code is replaced and
   perpetual-only programs are bit-identical through it. Acceptable, or is it a patch in your reading?
2. Controls coverage matched through where(spot_term > 0, perp_term, perp_term), or on the perpetual's own coverage? The
   matched form is the stricter test of content.
3. H-S3's own W1 (ON in 25% to 75% of the decision hours; gross and names over the ON hours). Accept?
4. Four hypotheses, three in one class if H-S3 (H-S1's book under a gate) counts as its own idea. Accept, or strike H-S4
   or H-S3? Fewer ideas, fewer chances for noise to pass.
5. Market-wide spot outages stay unknown (KP-029) and cost six weekly decisions of H-S1 and H-S3 each. I propose to proceed
   strictly, report the coverage count before the first evaluation, and let W1 decide. Or a rule for them now?
6. H-S1's reference window 4 weeks instead of the desk study's 8 (coverage, speed). Accept?
7. Budget: 4 defaults, at most 12 control and corner runs, 2 in reserve; cap 18.
8. Tracked outputs: validation_stage1.json and spot_symbols.json now; spot_coverage.json and run_log.jsonl in stage 2.

Written 2026-11-28 14:21 +08:00, before any spot file was downloaded, opened or listed for content, and before any study
hypothesis was evaluated.

## Coordinator's rulings before any spot file (version 2; 2026-11-28; appended by the coordinator, nothing above is changed)

The coordinator read version 2 whole, the four hypotheses and one control as programs, the spot rules and the slot
builder (studies/kp029/kp029_spot.py, kp029_features.py) line by line, and searched the evaluator, the runner and the
downloader for any write outside the study, any import of the sandbox or the evaluator and any ceiling other than
DEV's: none. The kernel's engine, activity and membership read open, high, low, close, trades and the gap flag, never
the two slot columns (omr/upipeline.py, ENGINE_KLINE_COLS). The mechanical gate: the 46,323 bytes of version 1 and its
record unchanged; the lock verifies, sealed; the ledger chains verify; the sandbox log at 95 rows;
_build/kp029_study/ does not exist; every study file ASCII with LF. No spot data file has been downloaded or opened
by anyone in this project: the desk study and stage 1 used file listings only.

1. The slots through the loader hook: ACCEPTED. No byte of the kernel changes, and a perpetual-only program is
   bit-identical through the wrapper. Conditions: study programs stay under studies/kp029/programs/, never under
   strategies/, never given to omr.sandbox or omr.evaluate, and each states the slot map in its head, as they do.
2. Controls matched to the hypothesis's coverage: ACCEPTED as designed (the stricter test of what the spot input adds).
3. and 4. H-S3 AND ITS CONTROL C-S3 ARE STRUCK, before any run. Playbook 8b allows at most two ideas of one mechanism
   class and the leverage-share class has three; H-S3 would need a screen item of its own, and the rule fixed in
   advance is one screen for all with nothing looser; and by the plan's own note its gate is drawn from DEV's two
   leverage flushes. The study has THREE hypotheses, in this order: H-S1, H-S2, H-S4. Their two program files are
   removed so that nothing can run them; the text above stays as the record.
5. MARKET-WIDE SPOT OUTAGES: a rule now, not "let W1 decide". KP-029's words "unknown, never zero volume" were written
   for a spot pair that has stopped. An hour in which the spot exchange itself was down is another case: every pair's
   volume in that hour WAS zero, and everybody knew it at the time. Left unknown, each such hour would take the whole
   book out of five or six weekly decisions, and the study would then measure the exchange's maintenance calendar
   instead of the premise. The rule:
   - A spot OUTAGE HOUR is an hour, at or after the first row of the stored spot BTCUSDT table, for which that table
     has no row (BTCUSDT trades in every hour the spot exchange is open). It is known at the close of that hour.
   - At an outage hour a spot pair that has no row of its own gets a synthetic row: zero trades, zero quote volume,
     zero taker-buy quote volume, provided the pair has a real row at some earlier hour. Rule S3 then decides
     usability exactly as for any present zero-trade bar (so at most 24 non-trading hours in a row; outage hours and
     absent hours count in the run), and the price guard takes its verdict from the pair's last real row instead of
     comparing a price that does not exist.
   - Everything else is as written: an absent spot hour that is NOT an outage hour stays unknown (a pair not yet
     listed, halted, ended, or a row dropped by the cleaning); a real row is always used as it is.
   - The rule reads only rows at or before the hour, so the truncation test must pass with it; the synthetic tests
     get a market-wide outage (zero-filled, the cross-section kept), an outage longer than 24 hours (unknown from
     the 25th hour), and a stopped pair at a later outage hour (unknown).
   - The coverage count reports the outage hours, their blocks and the longest block, and at outage hours the share
     of the other stored pairs with a real row in the 24 hours before that have no row either. TRIPWIRE, fixed now:
     if that share is under 95% over all outage hours, or a block is longer than 24 hours, or there are more than
     200 outage hours on DEV, the runner stops after the coverage count and the researcher reports to the
     coordinator before any evaluation. Otherwise the runs go on without a stop.
   Known side effect, accepted: an outage lowers every pair's spot volume of that day together, which moves the
   daily share change of every coin the same way on two days of H-S4's 28.
6. THE PRICE GUARD: 20%, not 5%. The guard is there to catch another coin under the same name or a wrong price
   multiplier, and those put the two prices apart by far more than 20%. A tolerance that ordinary stress can reach
   would take a coin out of five or six weekly decisions for one stressed hour, after exactly the events the
   hypotheses are about. For the record, and before the pre-registration: on the kernel's own DEV rows of the 114
   perpetuals (in-play hours, the kernel's loaders, DEV ceiling) count the hours at which the perpetual's close is
   more than 2%, 5%, 10% and 20% from its index close, with the number of coins and of distinct weeks touched, and
   put the table in the amendment. If more than 20 coin-hours exceed 20%, stop and report before anything else.
7. H-S1's reference window of 4 weeks instead of the desk study's 8: ACCEPTED (decided before data, with its reasons).
8. Budget: 3 defaults; for a hypothesis that passes the screen at its default its control, then the 0.8 corner,
   then the 1.2 corner, stopping at the first failure (at most 9); 2 in reserve for a void or faulted run after a
   written amendment. Cap 14 evaluations.
9. Tracked: validation_stage1.json and spot_symbols.json now; spot_coverage.json and run_log.jsonl in stage 2. The
   spot files stay under _build/ and are never committed.
10. The pass rule stands as made exact above (one screen for all, the floor before costs 1.85, corners by rule S10,
    the control beaten by at least 0.5 before costs, every run with its truncation test passed). A pass is not a
    result for the human until an independent auditor has checked the study; no pass, and the spot front is closed
    and the search is parked, as he was told. No default, sign, window or rule is changed after the first spot file
    is opened; the reserve is for void runs only.
11. The researcher's amendment for rulings 3 to 6 and 8 (the code, the tests, the guard table) is appended below
    and gated by the coordinator. Stage 2 starts only after this plan, the amendment and studies/kp029/ are
    committed and on the remote.

## Coordinator's ruling on the guard table (version 2; 2026-11-28; appended by the coordinator, nothing above is changed)

The researcher stopped at ruling 6 as ordered, before any other amendment and before any spot file. Its table, from
the kernel's own DEV rows (114 perpetuals, 927,748 in-play coin-hours, the perpetual's close against the kernel's
index close; studies/kp029/guard_table.py and guard_table.json):

| perpetual close against index close | coin-hours | coins | weeks |
|---|---|---|---|
| more than 2% apart | 363 | 77 | 26 |
| more than 5% apart | 185 | 55 | 12 |
| more than 10% apart | 99 | 27 | 5 |
| more than 20% apart | 33 | 8 | 3 |
| more than 25%, 30%, 50% apart | 27, 17, 14 | | |

The 33 hours beyond 20% are three events: the crash hour of 2021-05-19 (six coins, one hour each, up to 0.436), seven
hours of one coin on 2021-11-11 (up to 0.271), and twenty hours of LUNA's collapse on 2022-05-11 to 13 (ratios of 24
and 159; all 14 hours beyond 50% are these). None of them is another coin under the same name or a wrong multiplier:
they are the same coin under stress, which is what the guard must let through. The first plan's 5% would have taken
up to 55 coins out of five or six weekly decisions each.

6 (revised). THE PRICE GUARD IS 50%: a spot row is used when spot close x multiplier lies within 50% of the
   perpetual's close of the same hour (a ratio from 0.5 to 1.5). Its one job is identity. A wrong multiplier is a
   factor of 1000, and another coin is off by some factor hour after hour; the same coin under stress stayed inside
   50% in every in-play hour of DEV except the last days of a collapse, where "unknown" is the right answer. The
   number is set on the kernel's own rows of the perpetual and the index, before any spot file exists here; the index
   is a stand-in for the spot price, and the real spot closes may sit nearer to the perpetual.
   The stop of ruling 6 ("more than 20 coin-hours beyond the tolerance") is met at 50% (14) and is spent: there is no
   further stop on this table.
   In its place, in the coverage count: the number of in-play coin-hours the guard rejects on the real spot rows,
   and the pairs with more than 24 rejected hours. TRIPWIRE, fixed now: more than 5 such pairs means the symbol map
   is wrong somewhere; the runner then stops after the coverage count, before any evaluation, for an amendment of
   the map only. No tolerance, window, sign or default is changed after the first spot file is opened.
   guard_table.py and guard_table.json are tracked with the study.
   Everything else in the rulings above stands; the researcher's amendment follows below.

## Amendment after the coordinator's rulings (stage 1b; 2026-11-28; appended by the researcher, nothing above is changed)

The 81,043 bytes above (sha256 3d7d98c6b786a1c9...) are unchanged. Still no spot file, no _build/kp029_study/, no Binance
address, no hypothesis evaluated; no kernel file, ledger/ or data/ touched.

What changed, by file (studies/kp029/):
- programs/: kp029_hs3_leverage_gate.omr and kp029_cs3_volume_gate.omr DELETED (rulings 3, 4). The six others: head
  comments only (the outage zero row of ruling 5, the 50% guard of ruling 6); bodies, params and canonical forms
  unchanged; all six parse with the constant probe (lookback 1,605 h).
- kp029_features.py: GUARD_TOL 0.50 (spot close x multiplier / perpetual close within 0.5 .. 1.5). The outage rule
  (slot_detail), on the pair's own hourly grid: an outage hour is an hour at or after the first stored spot BTCUSDT
  row with no BTCUSDT row; a pair with no stored row of its own there gets a synthetic row (trades, quote volume,
  taker-buy quote volume 0) if it has a real row at an earlier hour; S3 (omr.universe.usable_of) then decides, outage
  and absent hours counting in the run; a synthetic row takes the guard verdict of the pair's last real row; any other
  absent hour stays unknown; a real row is used as it is. Every input reads rows at or before the hour; inject cuts
  the BTCUSDT table with the pair's and the perpetual's rows, so the truncated and the full run see the same outage
  hours on every row up to the cut.
- kp029_spot.py: the spot stores also keep each pair's stored open times before cleaning (raw_index): "has a row".
- kp029_eval.py: H-S3's own W1 and the gate readings removed (one screen for all); guard_table.py added to the files
  whose sha256 every run logs.
- run_study.py: three hypotheses (H-S1, H-S2, H-S4) and their controls; cap 14 enforced (3 defaults, at most 9
  control and corner runs, 2 in reserve). --coverage now reports the outage hours, their blocks and the longest, the
  share at outage hours of the other stored pairs with a real row in the 24 hours before that have no row either, and
  per perpetual on its in-play hours (the kernel's top30 and next30 masks) the real, synthetic and known slots and the
  hours the 50% guard rejects on real rows. Tripwires: share under 95%, a block over 24 h, over 200 outage hours on
  DEV, more than 5 pairs with more than 24 rejected in-play hours. Any of them writes "stop": true into
  spot_coverage.json, and every evaluation is then refused (coverage_gate) for a report to the coordinator.
- synthetic_tests.py: BTCUSDT is now one of the 15 synthetic perpetuals (the outage reference); the guard tests moved
  to 50%; new tests 11 (outages) and 12 (coverage and the runner's refusals); 31 of 31 checks pass.
- README.md: the rules, files and stage-2 order above. guard_table.py and guard_table.json: as the ruling quotes them,
  unchanged since; tracked.

Guard table (studies/kp029/guard_table.py; the kernel's DEV rows, 114 perpetuals, 927,748 in-play coin-hours,
perpetual close against the kernel's index close): beyond 2% 363 coin-hours (77 coins, 26 weeks); beyond 5% 185 (55,
12); beyond 10% 99 (27, 5); beyond 20% 33 (8, 3); beyond 25%, 30%, 50% 27, 17, 14 (the 14 all LUNA, 2022-05-12/13).

Tests (stage 1b): synthetic_tests.py 31 of 31 checks pass (the 3 h market-wide outage keeps every coin in every weekly decision
with zero, known slots; the 30 h outage is unknown from its 25th hour; a pair stopped a month before an outage stays
unknown; BTCUSDT itself gets a zero row at an outage hour; an absent hour that is not an outage stays unknown; the
truncation test passes with cuts inside and just after a 3 h and a 30 h outage; each tripwire sets the stop flag; the
runner refuses on the flag, without the coverage file and at the cap). validate_evaluator.py: the three programs reproduce exactly again (all 60 logged values, difference 0.0; the printed numbers to their digits; the wrapper bit-identical).
tests/test_structure.py -q: 9 passed. omr.kernel_lock verify: OK, sealed. Parse check: six of six.

Download plan: unchanged (spot_symbols.json: 114 perpetuals, 114 pairs, 1,911 monthly files). BTCUSDT's window,
2020-01 .. 2022-06, is the union of every pair's window, so the outage reference covers every hour the study reads.

Stage 2, in this order (from the project root; one at a time, memory floor checked by the scripts):

    .venv\Scripts\python.exe -I studies\kp029\download_spot.py --go
    .venv\Scripts\python.exe -I studies\kp029\run_study.py --coverage
      (STOP printed: report to the coordinator; every evaluation is refused)
    .venv\Scripts\python.exe -I studies\kp029\run_study.py kp029_hs1_share_shift
    .venv\Scripts\python.exe -I studies\kp029\run_study.py kp029_hs2_spot_flow
    .venv\Scripts\python.exe -I studies\kp029\run_study.py kp029_hs4_rally_carrier
      then for each hypothesis whose default passed the screen, in that order, stopping at its first failure:
    .venv\Scripts\python.exe -I studies\kp029\run_study.py <its control: kp029_cs1_perp_volume_shift,
      kp029_cs2_perp_flow or kp029_cs4_volume_return>
    .venv\Scripts\python.exe -I studies\kp029\run_study.py <hypothesis> --label corner08
    .venv\Scripts\python.exe -I studies\kp029\run_study.py <hypothesis> --label corner12
    .venv\Scripts\python.exe -I studies\kp029\run_study.py --summary

Written 2026-11-28 15:24 +08:00, before any spot file was downloaded or opened.
