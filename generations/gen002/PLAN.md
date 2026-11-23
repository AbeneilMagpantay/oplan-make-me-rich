# Generation 2 - PLAN (version 1, pre-registered 2026-11-23 before any generation-2 sandbox run)

Researcher session for generation 2, stage 1 (read, think, pre-register). Unit: top30.

- Kernel: semantic 5ea66b0fb79ca267d3c8de22d203976aab3bca5634b22e026b13687c69eb2687, text
  1366fb8fd0b6976839a3e6b16e40c402291c0154bb8ccfeae24bcd6848c72924 (`python -m omr.status`: kernel OK
  bcc4b1aa255b4679, sealed). Sealed G6 thresholds: core 0.10, top30 0.10. Data research_hash
  28d9084a8c5c7659..., validated.
- Ledger when this was written: M = 5 counted trials (generation 0: 4, generation 1: 1), N 4.86, rho 0.035,
  Tier 1: 0, pool 0 of 5, one uncounted stage-1 rejection. `omr.kernel_lock verify` OK; `omr.ledger verify`
  OK (all six chains).
- Read: RESEARCH_PLAYBOOK.md (with section 4b), LANGUAGE.md (all, with section 10), CONSTITUTION.md
  sections 3, 4, 6, 7 and 13, LESSONS.md (1 to 15), generations/gen000/REPORT.md, generations/gen001/REPORT.md
  and PLAN.md, STATE.md, the trial rows of `omr.ledger summary`, `omr.status`; program shapes
  omr/programs/ucal_xs_momentum.omr, ucal_xs_reversal.omr, ucal_xs_carry.omr, kernel_noise_top30.omr and
  strategies/gen00*.omr. Kernel source was read only to learn how the language and the sandbox behave:
  omr/sandbox.py (what it prints), omr/engine.py (avg gross and avg net are of HELD positions), omr/lang.py
  (a cs_* keeps its input's timeframe; mixed timeframes join on the hourly grid).
- Not opened: anything under data/, ledger/returns/, ledger/trials/, _build/, audits/, and every calibration
  file. No VAL number exists for any program below. No sandbox run has been made for generation 2.

Four hypotheses. All are market neutral (cs_demean: dollar neutral; cs_scale: gross 1), all read WEEKLY bars
and so rebalance once a week, none reads funding (KP-017), none reads mark or index prices.

| H | program | input | prediction | family |
|---|---|---|---|---|
| H1 | gen002_resid_reversal | last week's return net of its BTC-beta part, over own daily volatility | residual losers beat residual winners next week | meanrev |
| H2 | gen002_activity_fade | this week's trade count over its own m-week mean | coins with activity bursts lag, quiet coins lead | flow |
| H3 | gen002_small_tickets | this week's USD per trade over its own m-week mean | shrinking tickets lag, growing tickets lead | flow |
| H4 | gen002_absorbed_flow | this week's taker-buy share over its own m-week mean, orthogonal to the week's return | unexplained taker buying lags, unexplained taker selling leads | flow |

## What a top30 idea must clear (playbook 4b, LANGUAGE.md 10, CONSTITUTION 13), and how these programs meet it

- Costs. 12.5 bps per side. A rank-weighted book whose ranks are independent from week to week trades about
  4/3 of its gross per week (sum of |w_new - w_old|), so about 0.09 of gross per year, 0.17 at G4's doubled
  costs. A dollar-neutral rank book over about 30 coins has an idiosyncratic volatility of very roughly 0.15
  to 0.25 a year, so these costs are of the order of 0.4 Sharpe units (0.8 doubled). Passing G1 (VAL PSR(0)
  >= 0.90 over three years, a net Sharpe of about 0.8) then needs a gross Sharpe of about 1.2, and G4 a gross
  Sharpe above about 0.8. These rough numbers are written down now so that DEV readings are judged against
  them; the sandbox prints the actual costs. Daily re-ranking would multiply the costs by about 2 to 4, and a
  signal rolling on hourly rows is far worse (each hour's small re-rank is traded once any name crosses the
  engine's 0.01 band). That is why every rank here comes from weekly bars (H1's beta and volatility read daily
  bars and move slowly).
- Speed. G6's speed limit fails a book whose weights correlate above 0.5 with its own weights one lag step
  (25.9 days) earlier, each name's mean removed. Each signal is built from the last one or two weeks against a
  baseline of at most 6 weeks (H1: 45 days at the param's high), so the part that moves the ranks has no window
  overlap at 26 days; what could still correlate is the persistent part of the inputs. The DEV diagnostic D-ACF
  (below) measures an upper bound of that correlation before anything is submitted.
- Lookback (limit 2,160 h, params at their highs; parse check): H1 1,127 h; H2, H3, H4 1,175 h.
- Cross-sections: a cs_* needs at least 10 in-play names with a known input. A weekly bin is known only if
  every hour in it is known, so a name with one unknown hour drops out for m + 1 weeks; a market-wide missing
  hour would flatten the whole book for as long. Named in advance; the sandbox's avg gross shows it (S1).
- G8 runs the rule on ranks 31 to 60. Every input here is a ratio to the coin's own past or a cross-sectional
  rank, so the rule means the same there.
- G7: the unit needs 10 seasoned members and these programs 2 to 7 weeks of history, so 2020 is a short
  bucket; four of the six buckets must be positive.
- Funding: no program reads funding8h or funding_mean (KP-017). None reads index_close or mark_close either:
  the perp-index basis is the input the funding rate is computed from, and the top30 null worlds did not model
  index prices (CONSTITUTION 13: the index bars follow the mark bars, "no program reads them"), so a
  basis-driven book would sit in the same unmeasured corner as a funding-driven one.
- Literals and G5: none of the four programs has a jitterable literal (n_literals 0) and each has exactly one
  integer param. G5 therefore moves only that param. For m = 4 every jitter variant is m = 3 or m = 5 (4 x
  U(0.8, 1.2) rounds to 3, 4 or 5, and an unchanged 4 moves by 1); for n = 30 it is 24 to 36. The DEV
  neighbours below are exactly those values, so S3 is a DEV reading of what G5 will ask in VAL.

## Disclosures that apply to every hypothesis

- The author model has read this market's history through DEV, VAL and the vault. No rule below names a date,
  a coin, a price level or a remembered event; every tunable number is a declared param. That does not remove
  hindsight from the CHOICE of ideas (KP-010); each hypothesis states what I remember that could bias it.
- What I remember about VAL that touches every market-neutral top30 book: BTC's share of crypto market value
  rose through most of VAL and most altcoins lagged BTC; memecoin waves (2023, 2024) in which a few coins rose
  for weeks; single-coin collapses (FTT in November 2022 is the one I remember clearly). A book with a
  persistent tilt toward BTC and the largest coins would have collected the first. None of the four programs
  has a size or beta input, but a tilt can arise indirectly (named under H3). G6 compares the book with its own
  stale copies, which carry the same tilt, and D-ACF counts a tilt as correlation (it removes no per-name
  mean), so a tilt-driven book should show at D-ACF or at G6.
- Priority. At most TWO programs are recommended for counted submission whatever DEV says, and at most one of
  H2 and H3 (they share the retail-attention mechanism). LESSONS 12 and 14: a true Sharpe-1.5 book passes Tier
  1 only 68 to 82% of the time in this unit, G6 does not protect against luck, and every counted trial raises M
  forever.
- Defaults are fixed now and are never changed after a run. The neighbours are a robustness check (the G5
  values), not a search; a better neighbour does not move the default.

## Common DEV screen (decided now, before any number)

A hypothesis is recommended for counted submission only if, in the sandbox (full stage 1, no --quick):
- S1 at its default it passes stage 1 as written (parse, constant probe, truncation and start-cut checks)
  with at least 30 DEV direction changes, and its avg gross is at least 0.5 (it holds positions over at least
  about half of DEV);
- S2 at its default the DEV Sharpe is >= 0.6 with the pre-registered sign. No sign is ever flipped: a negative
  DEV Sharpe drops the hypothesis;
- S3 the DEV Sharpe is > 0 at both G5 neighbours (H1: n = 24 and n = 36; H2 to H4: m = 3 and m = 5);
- S4 at its default, DEV total return minus DEV costs is > 0 (a rough DEV reading of G4: the return would stay
  positive with the costs paid twice);
- S5 at its default, the net return is positive in at least two of the DEV years the sandbox prints (2020,
  2021, 2022);
- S6 the D-ACF diagnostic ratio (section "DEV-only controls") is <= 0.40;
- S7 (H1 only) H1's DEV Sharpe at its default is above that of the control gen002_diag_plain_reversal.

Order and economy: the default runs first. If it fails S1, S2 or S4, the hypothesis is dropped and its
neighbours are not run. The control runs only if H1 has passed S1 to S5. D-ACF runs only for a hypothesis
that has passed S1 to S5 (and S7 for H1).
Selection: if more than two pass, or if both H2 and H3 pass, the one with the higher MINIMUM DEV Sharpe over
its three runs (default and both neighbours) is preferred: robustness, not the peak. If none passes, none is
recommended; that is a result and is recorded as one.
DEV Sharpe is a liveness check, not a ranking beyond this rule.

---

## H1. gen002_resid_reversal

- Family meanrev. Kind portfolio. Unit top30. Dollar neutral, gross 1.
- Rule: every week (weekly bins from Monday 00:00 UTC; a bin becomes visible at the Sunday 23:00 bar and is
  traded at the Monday 00:00 open), for each coin in play: resid = the coin's last weekly return minus beta x
  BTC's weekly return, beta = correlation x volatility ratio of daily returns against BTC over the last n days;
  z = resid / the coin's daily-return volatility over the same n days. Weight: minus the cross-sectional rank
  of z, demeaned, scaled to gross 1. Long the largest residual losers, short the largest residual winners.
  Beta and volatility update at each daily close, so ranks can shift a little between weeks; the weekly return
  dominates the turnover.
- Program (default pre-registered; strategies/gen002_resid_reversal.omr):

      n = param(30, 20, 45)          # daily rows for the BTC beta and the coin's volatility
      d = daily(close)
      db = daily(btc(close))
      r = ret(d, 1)
      rb = ret(db, 1)
      vol = std(r, n)
      beta = corr(r, rb, n) * vol / std(rb, n)
      resid = ret(weekly(close), 1) - beta * ret(weekly(btc(close)), 1)
      z = resid / vol
      signal = cs_scale(cs_demean(-cs_rank(z)))

  1 param (integer; G5 range 24 to 36), 0 jitterable literals, 37 nodes, lookback 1,127 h. The weights are an
  hourly-grid series (daily and weekly bars mixed).
- Hypothesis: a coin's weekly return net of its BTC-beta part, measured in units of its own volatility, partly
  reverses over the following week.
- Mechanism: price pressure from flow that carries no information. In USDT perps leverage is high and
  liquidation is automatic: a cascade of liquidations, a run of stop orders or a retail stampede into a story
  moves one coin by more than any change in what patient holders think it is worth, and the excess partly
  reverts once the forced flow is done. The reverter is paid for supplying liquidity when it is scarce (the
  short-term reversal as a liquidity-provision return: Lehmann 1990, Nagel 2012). Two choices aim the ranking at
  that pressure: (1) the BTC-beta part of the week's move is removed, because a market move is information about
  the whole asset class, and in equities the residual reversal is much stronger than the raw one for the same
  reason (Da, Liu and Schaumburg 2014); (2) dividing by the coin's own volatility ranks how unusual the move was
  for that coin, so the extremes are not simply the most volatile coins every week.
- Other side: liquidated traders and margin calls, stop-loss flow, late chasers of a move. Why it can persist:
  forced flow is a structural product of leverage in perps, and capital willing to buy a coin during a cascade is
  scarce exactly then; the position is risky (some collapses do not revert), which is the premium's reason.
- Costs: weekly returns are close to independent week to week, so about 4/3 of gross traded per week, about
  0.09 a year and 0.17 doubled (S4 checks it on DEV).
- Relation to earlier trials and lessons: the calibration family ucal_xs_reversal (raw n-day returns on daily
  bars, 3 to 20 days, re-ranked every day) is a no-skill family of the calibration; LESSONS 13 says such books
  lose after costs in the no-skill worlds, where costs rather than G6 stop them. H1 differs from it in exactly
  the three choices that are the hypothesis: weekly re-ranking (a third to a quarter of the daily book's
  costs), the BTC-beta residual and the volatility scaling. The DEV-only control gen002_diag_plain_reversal
  (raw weekly return, the same weekly re-ranking) isolates (1) and (2): if H1 does not beat it on DEV (S7), the
  residual adds nothing measurable, H1 is the calibration family's shape at a weekly speed, and it is not
  recommended. Answers LESSONS 8 to 11 (dollar neutral; G6 credits only timing). The only earlier
  mean-reversion trial, gen000_rsi_meanrev_ls (c6ea0c6759f7482e; single coin, 4h RSI, 311 DEV direction
  changes), lost in DEV and VAL (LESSONS 3): a different, time-series, high-turnover design.
- What I remember that could bias it: the crypto papers I remember disagree. Liu, Tsyvinski and Wu (2022)
  report cross-sectional MOMENTUM at one to four weeks in a broad coin universe; other work (I recall Zaremba
  and co-authors, 2021, without being sure of the detail) finds short-term reversal concentrated in small,
  illiquid coins, which a top30 excludes. I do not remember any result for a weekly beta-residual reversal on
  Binance perps in 2022 to 2025. From VAL I remember single-coin collapses (FTT, November 2022), in which a
  long-the-losers book loses, and memecoin runs (2023, 2024) that lasted weeks, in which a short-the-winners
  book loses. These memories argue AGAINST H1; none argues for it. They did not shape the rule: there is no
  crash filter and no per-coin cap beyond the rank weighting.
- Falsifier. DEV (not submitted): S1 to S7. Counted (VAL): falsified if G1 (PSR(0) < 0.90), G4 (2x costs <= 0),
  G6 (p > 0.10, or the speed limit), G8 (next30 Sharpe <= 0), or any other Tier-1 gate fails. G7 (gains in one
  period) is the named risk of a reversal book exposed to single-coin collapses.
- DEV exploration (at most 5 runs): default n = 30; then n = 24 and n = 36; then the control; then D-ACF
  (gen002_diag_acf_resid_reversal, k = 621 hours).

## H2. gen002_activity_fade

- Family flow. Kind portfolio. Unit top30. Dollar neutral, gross 1.
- Rule: every week, shock = this week's number of trades / the mean of the last m weekly trade counts (this
  week included). Weight: minus the cross-sectional rank of shock, demeaned, scaled to gross 1: short the coins
  whose activity jumped most above their own recent normal, long those whose activity fell most below it.
- Program (default pre-registered; strategies/gen002_activity_fade.omr):

      m = param(4, 3, 6)             # weeks in the activity baseline
      act = weekly(trades)
      shock = act / sma(act, m)
      signal = cs_scale(cs_demean(-cs_rank(shock)))

  1 param (integer; G5 values 3 and 5), 0 jitterable literals, 11 nodes, lookback 1,175 h. The weights are a
  weekly series.
- Hypothesis: coins whose weekly trade count jumps far above their own recent normal underperform the rest of
  the unit over the following week; coins whose activity falls below normal outperform.
- Mechanism: attention. A jump in the number of trades marks a burst of attention (a story on social media, a
  listing elsewhere, an exchange campaign, a big move). Attention-driven traders buy more than they sell: they
  choose among the few things they notice when buying but can sell only what they hold (Barber and Odean 2008);
  in USDT perps they are leveraged and mostly long. Their demand lifts the price above where it settles once
  attention moves to the next coin. Coins whose activity fell below normal are out of the spotlight: the
  neglected, cheap side.
- Other side: market makers and patient sellers who short into the burst; on the long side, holders leaving
  the neglected coin for the hot one. Why it can persist: attention is scarce and moves from coin to coin, the
  arriving traders are new each time, and shorting a coin while attention is still rising is risky (squeezes).
- Why trade counts: they carry no price, so the shock is not mechanically tied to the week's return (quote
  volume rises with the price; base volume falls with it).
- Competing evidence, which is why the falsifier is directional: in US equities Gervais, Kaniel and
  Mingelgrin (2001) found the opposite sign (the high-volume return premium: visibility brings lasting new
  buyers). A DEV Sharpe below 0.6 drops H2, and a negative one is never turned into the opposite rule. H2 is
  probably correlated with reversal on pump weeks (bursts come with big moves); on capitulation weeks H1 buys
  the large loser and H2 shorts the burst. The two hypotheses disagree there, and DEV will show which, if
  either, holds.
- Costs: the shock is mostly new each week; with a 4-week baseline some ranks persist, so a little under H1's
  0.09 a year (S4 checks it).
- Relation to earlier trials and lessons: new idea; no counted trial reads trade counts. Answers LESSONS 8 to
  11 (neutral). The calibration families read returns and funding, not activity (LESSONS 13).
- What I remember that could bias it: memecoin waves in 2023 and 2024 in which activity surged and the coins
  kept rising for weeks before collapsing; the start of such a wave hurts H2, the end helps it. I do not
  remember any cross-sectional result for trade-count shocks in crypto, in or out of VAL.
- Falsifier. DEV: S1 to S6 (a wrong DEV sign drops it). Counted (VAL): falsified if G1, G4, G6 (or the speed
  limit), G8, or any other Tier-1 gate fails.
- DEV exploration (at most 4 runs): default m = 4; then m = 3 and m = 5; then D-ACF
  (gen002_diag_acf_activity_fade, k = 4 weeks).

## H3. gen002_small_tickets

- Family flow. Kind portfolio. Unit top30. Dollar neutral, gross 1.
- Rule: every week, ticket = quote volume / number of trades (USD per trade); abn = ticket / its mean over the
  last m weeks (this week included). Weight: + the cross-sectional rank of abn, demeaned, scaled to gross 1:
  long the coins whose average ticket grew most against their own normal, short those whose ticket shrank most.
- Program (default pre-registered; strategies/gen002_small_tickets.omr):

      m = param(4, 3, 6)             # weeks in the ticket-size baseline
      ticket = weekly(quote_volume) / weekly(trades)
      abn = ticket / sma(ticket, m)
      signal = cs_scale(cs_demean(cs_rank(abn)))

  1 param (integer; G5 values 3 and 5), 0 jitterable literals, 13 nodes, lookback 1,175 h. Weekly series.
- Hypothesis: a coin whose average trade size in USD falls well below its own recent normal underperforms the
  rest of the unit over the following week; one whose trade size rises outperforms.
- Mechanism: who is trading. A falling average ticket in a coin means many more small trades: a crowd of small
  traders has arrived. In USDT perps they are mostly leveraged, trend-chasing and long-biased; their demand
  overprices the coin and their positions unwind later (stops, liquidations). A rising ticket means larger
  participants are trading it, and larger traders are on average better informed. Equity evidence on small
  trades: Kumar and Lee (2006), Hvidkjaer (2008: intense small-trade buying predicts underperformance), Barber,
  Odean and Zhu (2009).
- Other side: the crowd of small traders. Why it can persist: retail participation in perps comes in waves,
  and the informed side can lean against a wave only with limited capital.
- Caveat named before any run: a USD ticket rises mechanically with the price if traders keep their size in
  coins rather than in USD, which would tilt H3 toward last week's winners (a momentum leg). I chose USD because
  perps margin and order entry are in USDT. H3 shares its mechanism with H2 (an arriving crowd raises the trade
  count more than the quote volume); at most one of the two is recommended.
- Costs: about 0.07 to 0.09 a year (S4 checks it).
- Relation to earlier trials and lessons: new idea; no trial reads trade size. Answers LESSONS 8 to 11.
- What I remember that could bias it: no crypto result on ticket size that I can recall. From VAL I remember
  the spot ETF era (2024) bringing institutional money into BTC and ETH. If their tickets grew, H3 would tilt
  long BTC and ETH in 2024, a period in which BTC beat most altcoins: a tilt, not timing. G6's stale copies
  carry it, and D-ACF counts it.
- Falsifier. DEV: S1 to S6 (a wrong DEV sign drops it). Counted (VAL): falsified if G1, G4, G6 (or the speed
  limit), G8, or any other Tier-1 gate fails.
- DEV exploration (at most 4 runs): default m = 4; then m = 3 and m = 5; then D-ACF
  (gen002_diag_acf_small_tickets, k = 4 weeks).

## H4. gen002_absorbed_flow

- Family flow. Kind portfolio. Unit top30. Dollar neutral, gross 1.
- Rule: every week, share = taker-buy base volume / base volume (aggressive buying as a share of the week's
  volume); flow = share - its mean over the last m weeks (this week included). The cross-section of flow is
  regressed on the cross-section of the week's log return (both demeaned; b = slope); excess = flow - b x
  return is the aggressive buying the week's price move does not explain, uncorrelated with that return across
  coins by construction. Weight: minus the cross-sectional rank of excess, demeaned, scaled to gross 1: short
  the coins with the most unexplained aggressive buying, long those with the most unexplained aggressive
  selling.
- Program (default pre-registered; strategies/gen002_absorbed_flow.omr):

      m = param(4, 3, 6)             # weeks in the taker-share baseline
      share = weekly(taker_buy_volume) / weekly(volume)
      flow = share - sma(share, m)
      x = cs_demean(flow)
      y = cs_demean(logret(weekly(close), 1))
      b = cs_mean(x * y) / cs_mean(y * y)
      excess = x - b * y
      signal = cs_scale(cs_demean(-cs_rank(excess)))

  1 param (integer; G5 values 3 and 5), 0 jitterable literals, 34 nodes, lookback 1,175 h. Weekly series.
- Hypothesis: aggressive buying that a coin's weekly price move does not explain predicts underperformance
  against the unit over the following week, and unexplained aggressive selling predicts outperformance.
- Mechanism: in perps, aggressive (taker) orders come mostly from impatient traders: retail market orders,
  stops, liquidations (a liquidated long is a taker sell, a liquidated short a taker buy). Traders with lasting
  information prefer limit orders (Kaniel and Liu 2006). Aggressive buying normally lifts the price; if a coin
  saw more of it than its move explains, someone sold patiently into it, and that seller is more likely to be
  informed, so the price follows the patient side over the following week. The mirror holds for aggressive
  selling absorbed by patient buyers. Removing the return keeps H4 apart from momentum and from H1's reversal.
- Other side: the impatient takers whose flow was absorbed. Why it can persist: impatient flow is a property of
  the venue's clientele, and patient informed sellers do not announce themselves.
- For the coordinator's source read (playbook section 5): taker_buy_volume / volume is the SIGNAL input here (a
  deviation from the coin's own trailing mean, then a cross-sectional residual and a rank), not a constant,
  threshold or scale; it multiplies nothing and is compared with nothing. b is a cross-sectional regression
  slope (a ratio of two cross-sectional means of products of signals), recomputed every week.
- Costs: about 0.07 to 0.09 a year (S4 checks it).
- Relation to earlier trials and lessons: the only earlier flow program, gen001_taker_flow_long (single coin,
  long-or-flat on the raw taker share against its own average), was never submitted: no DEV timing content
  beyond the drift (LESSONS 10 and 11). H4 is cross-sectional and neutral, and it reads the part of the flow the
  price did NOT follow, as a contrarian signal.
- What I remember that could bias it: crypto-trader lore about "CVD divergence" (cumulative volume delta
  against price) that I have read; anecdote, no systematic result I can recall. From VAL I remember token
  unlocks in 2024 with early holders selling into demand, often patiently; if that shows in this measure it
  would favour H4 in VAL. Weak.
- Falsifier. DEV: S1 to S6 (a wrong DEV sign drops it). Counted (VAL): falsified if G1, G4, G6 (or the speed
  limit), G8, or any other Tier-1 gate fails.
- DEV exploration (at most 4 runs): default m = 4; then m = 3 and m = 5; then D-ACF
  (gen002_diag_acf_absorbed_flow, k = 4 weeks).

---

## DEV-only controls (never to be submitted; each file's hypothesis line says so)

- strategies/gen002_diag_plain_reversal.omr: `signal = cs_scale(cs_demean(-cs_rank(ret(weekly(close), 1))))`,
  no params. The raw weekly reversal, H1's control for S7.
- D-ACF, the speed-limit diagnostic: strategies/gen002_diag_acf_resid_reversal.omr,
  gen002_diag_acf_activity_fade.omr, gen002_diag_acf_small_tickets.omr, gen002_diag_acf_absorbed_flow.omr.
  Each computes w, the hypothesis's own weight row at its defaults (same text, same param ranges), and sets
  `signal = c * w * lag(w, k)` with c = param(20, 10, 30), only so that the positions are large against the
  engine's 0.01 band (no clipping: |w| stays near 0.1 at most).
  - What the sandbox then prints: avg gross = the mean over rows of sum_i |c w_i(t) w_i(t-k)| and avg net = the
    mean of sum_i c w_i(t) w_i(t-k) (held positions: engine.py sets gross = sum |h| / equity, net = sum h /
    equity; a scale-down above gross 1 changes both alike). Their ratio R = sum w w' / sum |w| |w'|, pooled over
    names and rows.
  - Why R is an upper bound of G6's statistic: (a) by Cauchy-Schwarz, sum |w| |w'| <= sqrt(sum w^2 sum w'^2),
    so R is at least the uncentred correlation when that is positive; (b) G6 removes each name's mean first;
    with w = name mean + varying part, the uncentred correlation lies between the varying part's correlation and
    1, so removing the means can only lower it.
  - Lag: one G6 lag step is (half of VAL - 30 days) / 20 = 25.9 days = 621 hours. H1's weights are an
    hourly-grid series, so k = param(621, 496, 746) hours. H2 to H4's weights are weekly series (a lag counts
    weeks; confirmed by the parse check's lookback, 1,175 + 5 x 168 = 2,015 h), so k = param(4, 3, 5) weeks = 28
    days, slightly longer than one step: a small liberal bias against the conservative ones of (a) and (b).
    lag(w, k) is known only where w was known on all k + 1 rows, so only names ranked continuously over the lag
    enter, which is close to G6's "in play at both rows".
  - Threshold (S6): R <= 0.40, a margin under the gate's 0.5. R is read from the two printed numbers (3
    decimals each). The diagnostic's Sharpe and returns mean nothing.
  - Lookback with the lag (params at their highs): 1,873 h (H1) and 2,015 h (H2 to H4), under 2,160.

## Exploration plan and run budget (decided before any run)

| order | run | runs only if |
|---|---|---|
| 1 | H1 default (n = 30) | - |
| 2, 3 | H1 n = 24, n = 36 | run 1 passed S1, S2, S4 |
| 4 | H2 default (m = 4) | - |
| 5, 6 | H2 m = 3, m = 5 | run 4 passed S1, S2, S4 |
| 7 | H3 default (m = 4) | - |
| 8, 9 | H3 m = 3, m = 5 | run 7 passed S1, S2, S4 |
| 10 | H4 default (m = 4) | - |
| 11, 12 | H4 m = 3, m = 5 | run 10 passed S1, S2, S4 |
| 13 | control gen002_diag_plain_reversal | H1 passed S1 to S5 |
| 14 to 17 | D-ACF of each hypothesis still standing | it passed S1 to S5 (and S7 for H1) |

Command form (from the project root, venv Python): `python -m omr.sandbox strategies/gen002_resid_reversal.omr`
and `python -m omr.sandbox strategies/gen002_resid_reversal.omr --set n=24`; full stage 1 on every run.

Planned: at most 17 sandbox runs. Reserve: 3 runs for an honest restatement after a stage-1 rejection the
parse check cannot see (the constant probe or activity), each a recorded amendment of one of the forms the
playbook lists in section 4, never a change of logic or of a default. Cap for this generation: 20 of the 60
allowed. Every run goes into the log below, including runs that fail.

Logged per run: DEV Sharpe, PSR(0), total return, maxDD, direction changes, avg gross, avg net, costs,
funding paid, rebalances, the per-year rows, the number of symbols ever in the unit, the lookback; for D-ACF
the ratio R.

## Sandbox run log

(filled in during stage 2; every run, chosen or not)

| # | program | params (non-default only) | DEV Sharpe | DEV dir. changes | avg gross | avg net | costs | total return | years + (of printed) | note |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | H1 gen002_resid_reversal | (default n=30) | -1.566 | 2849 | 0.866 | 0.000 | 0.1369 | -0.644 | 0 of 3 (2020 -0.514 SR -4.046; 2021 -0.208 SR -0.638; 2022 -0.074 SR -0.493) | PSR(0) 0.006, maxDD 0.686, rebalances 921, funding paid 0.0212, 75 symbols, lookback 1127 h, 78 s. Fails S2 (wrong sign) and S4; H1 DROPPED, runs 2, 3 and 13 not made |
| 4 | H2 gen002_activity_fade | (default m=4) | 0.172 | 1635 | 0.854 | -0.001 | 0.1669 | 0.031 | 2 of 3 (2020 -0.189 SR -1.098; 2021 0.130 SR 0.564; 2022 0.125 SR 1.063) | PSR(0) 0.607, maxDD 0.319, rebalances 625, funding paid 0.0141, 75 symbols, lookback 1175 h, 67 s. Fails S2 (0.172 < 0.6) and S4 (0.031 - 0.1669 < 0); H2 DROPPED, runs 5 and 6 not made |
| 7 | H3 gen002_small_tickets | (default m=4) | -0.211 | 1648 | 0.856 | 0.001 | 0.2309 | -0.172 | 2 of 3 (2020 0.241 SR 1.445; 2021 0.005 SR 0.160; 2022 -0.336 SR -3.453) | PSR(0) 0.369, maxDD 0.485, rebalances 581, funding paid -0.0486 (received), 75 symbols, lookback 1175 h, 86 s. Fails S2 (wrong sign) and S4 (-0.172 - 0.2309 < 0); H3 DROPPED, runs 8 and 9 not made |
| 10 | H4 gen002_absorbed_flow | (default m=4) | -1.251 | 1850 | 0.854 | 0.001 | 0.1649 | -0.466 | 0 of 3 (2020 -0.026 SR -0.150; 2021 -0.361 SR -1.830; 2022 -0.142 SR -1.478) | PSR(0) 0.023, maxDD 0.528, rebalances 575, funding paid 0.0145, 75 symbols, lookback 1175 h, 80 s. Fails S2 (wrong sign) and S4 (-0.466 - 0.1649 < 0); H4 DROPPED, runs 11 and 12 not made |

Run numbers follow the plan's order table; numbers not listed were not due under its conditions. Total sandbox
runs made: 4 (of the 17 planned and the cap of 20); none from the reserve; no stage-1 rejection, no kernel fault,
no refusal. Every run: full stage 1 (25 truncation cuts), exit 0, nothing on stderr, 67 to 86 s. The
benchmark line printed by every run (equal-weight long of the in-play members): DEV Sharpe 0.619, maxDD 0.847.

## Amendments

(none)

## Notes for the coordinator (written with the plan)

- D-ACF reads DEV only, through the sandbox, and is never submitted. It measures a property of the
  researcher's own weights that the sandbox does not print. If the coordinator rules it out before stage 2, S6
  is removed by an amendment written before any run, and the speed limit stays an unmeasured risk.
- The basis (close against index_close) was left out on purpose, as funding-adjacent under KP-017 (see the
  first section). The playbook does not say whether it counts as funding-driven.

Coordinator's rulings, 2026-11-23, received after the plan was committed and pushed unchanged as fd19943
(PLAN.md sha256 38d5d4a6...) and before run 1 (recorded here before any generation-2 sandbox run):
(1) the D-ACF diagnostics are ALLOWED as DEV-only measurements; their runs count toward the sandbox cap, they
are never submitted, and S6 stays as written; R is reported as a DEV proxy only (G6 reads VAL rows). (2) The
perp-index basis stays OUT of this generation, together with funding (KP-017), as the plan has it. (3) The
coordinator has read the source of the four candidates (playbook section 5): nothing to change. (4) The
requests about the sandbox (printing the speed-limit statistic and a next30 reading) and about aggregating
expressions over a timeframe will be filed as kernel proposals for the human after the generation; they are
not to be worked around.

Pre-registration: 2026-11-23T11:02:09Z; no sandbox run has been made for generation 2.

---

## Screen outcome per hypothesis (stage 2, DEV, appended after the runs; read from the run log above)

Each hypothesis was run once, at its pre-registered default. Each failed S2 and S4 there, so by the plan's
order its neighbours (S3), H1's control (S7) and its D-ACF (S6) were not due and were not run. No program text,
param or default was changed; there is no amendment.

| H | S1 (dir. changes >= 30; avg gross >= 0.5) | S2 (DEV Sharpe >= 0.6, sign as registered) | S3 | S4 (total - costs > 0) | S5 (years + of 3) | S6 | S7 | verdict |
|---|---|---|---|---|---|---|---|---|
| H1 gen002_resid_reversal | pass (2849; 0.866) | FAIL (-1.566, wrong sign) | not run | FAIL (-0.644 - 0.1369 = -0.781) | FAIL (0 of 3) | not run | not run (control not due) | DROPPED |
| H2 gen002_activity_fade | pass (1635; 0.854) | FAIL (0.172) | not run | FAIL (0.031 - 0.1669 = -0.136) | pass (2 of 3: 2021, 2022) | not run | n/a | DROPPED |
| H3 gen002_small_tickets | pass (1648; 0.856) | FAIL (-0.211, wrong sign) | not run | FAIL (-0.172 - 0.2309 = -0.403) | pass (2 of 3: 2020, 2021) | not run | n/a | DROPPED |
| H4 gen002_absorbed_flow | pass (1850; 0.854) | FAIL (-1.251, wrong sign) | not run | FAIL (-0.466 - 0.1649 = -0.631) | FAIL (0 of 3) | not run | n/a | DROPPED |

Against each pre-registered DEV falsifier:
- H1: falsified on DEV. The weekly residual reversal lost in all three DEV years (2020 Sharpe -4.05).
- H2: falsified on DEV. The sign was the one registered, but the size (0.172) was below the liveness bar and the
  return did not cover a second payment of costs.
- H3: falsified on DEV (wrong sign; the loss sits in 2022H1, Sharpe -3.45).
- H4: falsified on DEV (wrong sign; 2021 Sharpe -1.83, 2022H1 -1.48).

## DEV observations (stage 2; NOT hypotheses, never to be submitted from this plan)

- H1 and H4 lost by more than one Sharpe unit with the registered sign. On DEV, the top30 cross-section tended
  to CONTINUE a week's beta-residual move rather than reverse it. Aggressive flow beyond what the week's return
  explains also went with continuation, not with the patient side. The plan forbids flipping a sign, and no
  mirror was run. A mirror pays the same costs as the original, so its DEV Sharpe would be well below the size
  of these losses. A weekly residual-momentum rule would also sit close to the calibration's momentum family
  (LESSONS 13). If a later generation pre-registers such a mirror, DEV is no longer an out-of-sample screen for
  it: the author has seen this result, and only the counted VAL run could test it.
- Costs over DEV: 0.137 to 0.231 of equity in about 2.5 years, i.e. about 0.055 to 0.092 a year, as the plan
  estimated (H3, whose ranks turn over most, paid the most).
- All four books held positions over most of DEV (avg gross 0.854 to 0.866; 75 symbols ever in the unit), so a
  market-wide missing hour did not flatten the weekly books for long.
- WEAK: one DEV period, one default each; nothing here is a parameter recommendation.

## Recommendation

NONE. By the pre-registered selection rule no hypothesis passed the DEV screen (every default failed S2 and
S4), so no program from this plan is recommended for a counted submission in generation 2. The DEV-only
controls (gen002_diag_*) are never to be submitted.

---

# Generation 2 - PLAN, version 2 (round 2, pre-registered 2026-11-24 before any round-2 sandbox run)

Researcher session for generation 2, round 2, stage 1 (read, think, pre-register). Unit: top30. A fresh session:
round 1 is known to it only through the files listed below. The date in the heading is local time (+08:00); the
UTC time is in the last line.

- Kernel: semantic 5ea66b0fb79ca267d3c8de22d203976aab3bca5634b22e026b13687c69eb2687 (39 files), text
  1366fb8fd0b6976839a3e6b16e40c402291c0154bb8ccfeae24bcd6848c72924 (35 files) (`python -m omr.status`: kernel OK
  bcc4b1aa255b4679, sealed). Sealed G6 thresholds: core 0.10, top30 0.10. Data research_hash 28d9084a8c5c7659...,
  validated, snapshot_end 2026-11-18 10:00 UTC.
- Ledger when this was written: M = 5 counted trials (generation 0: 4, generation 1: 1, generation 2: 0 of 5), N
  4.86, rho 0.035, Tier 1: 0, pool 0 of 5, last census none, one uncounted stage-1 rejection (generation 0).
  `omr.kernel_lock verify` OK (sealed, core 0.1, top30 0.1); `omr.ledger verify` OK, all six chains (trials 10
  rows, stage1_log 1, kernel_history 10, calibration_log 4, sandbox_log 22, val_access_log 22). Sandbox runs used
  in generation 2 so far: 4 of 60 (round 1).
- Read: RESEARCH_PLAYBOOK.md (all, with section 4b), LANGUAGE.md (all, with section 10), CONSTITUTION.md sections
  4 to 7 and 13, LESSONS.md (1 to 20), this file's version 1 with its run log, screen outcome and recommendation,
  generations/gen002/REPORT.md, generations/gen001/REPORT.md, generations/gen000/REPORT.md, STATE.md, the trial
  rows of `omr.ledger summary`, `omr.status`; program shapes omr/programs/ucal_xs_momentum.omr,
  ucal_xs_reversal.omr, ucal_xs_carry.omr, kernel_noise_top30.omr and every strategies/gen002_*.omr of round 1.
  Kernel source read only to learn how the tool behaves: omr/sandbox.py (what it prints), omr/engine.py (a
  rebalance trades ALL names to target once any name is more than 0.01 off; avg gross and avg net are of held
  positions), omr/lang.py (timeframe functions take only a field or btc(field); a cs_* keeps its input's
  timeframe; mixing timeframes gives the hourly grid; lookback rules; lang.parse runs the constant probe).
- Not opened: anything under data/, ledger/returns/, ledger/trials/, _build/, audits/, and every calibration file.
  No VAL number exists for any program below. No round-2 sandbox run has been made.
- Version 1 above is unchanged byte for byte (its first 35,535 bytes, sha256 abb4530b36d183da...). Round 1's
  program files are unchanged; round 2 adds six new files (three candidates, three DEV-only controls).

Three hypotheses, numbered on from version 1. All are market neutral (cs_demean: dollar neutral; cs_scale: gross
1), all are residual to a market move, none reads funding, mark or index prices, none uses hour or weekday.

| H | program | input | prediction | family |
|---|---|---|---|---|
| H5 | gen002_resid_skew | realised skewness of the coin's daily log returns net of its beta to the unit's mean, last n = 21 days | right-skewed coins (recent up-jumps) lag, left-skewed coins (recent crash days) lead | other |
| H6 | gen002_resid_momentum | last m = 4 weeks' return net of its BTC-beta part, over own daily volatility | residual winners keep leading, residual losers keep lagging (CONTINUATION; written after round 1's DEV result) | relative |
| H7 | gen002_prior_month_reversal | the same residual for the m weeks BEFORE the last m weeks (weeks 8 to 4 ago at m = 4) | last month's-but-one residual winners lag, its losers lead | meanrev |

Which of these is a mirror of round 1: H6 is a continuation rule and falls under the provisions of LESSONS 16 and
17 (section H6 below). H5 and H7 owe nothing to round 1's DEV numbers: H5 reads a higher moment that round 1 never
used, and H7 is a reversal at a horizon (4 to 8 weeks back, the last 4 skipped) about which round 1's one-week
result says nothing.

## What a top30 idea must clear, and what a no-skill book looks like here

- Costs. 12.5 bps per side. Round 1's weekly rank books paid 0.055 to 0.092 of equity a year (LESSONS 19) and
  had an annual volatility of roughly 0.2 to 0.26 (from their printed Sharpe and returns), so their costs cost
  about 0.25 to 0.4 Sharpe units, twice that under G4. G1 (VAL PSR(0) >= 0.90 over three years of VAL) needs a
  net Sharpe of about 0.75, so a gross Sharpe of about 1.0 to 1.2. Turnover is therefore part of the design:
  - H6 and H7 rank m-week returns on weekly bars: consecutive weekly rankings share 3 of their 4 weeks, so the
    weights change by about half as much per week as a book whose ranks are new every week (sqrt(2 x 1/4) against
    sqrt(2) in units of the weight's spread). Estimate 0.03 to 0.06 a year. Beta and volatility move daily, as in
    round 1's H1, which was the cheapest of the four books (0.137 over DEV).
  - H5 is a daily series, but its rank moves mostly when a large day enters or leaves the 21-day window, so it is
    lumpy rather than continuous. Estimate 0.05 to 0.15 a year; S4 decides.
  - A daily re-ranked book of the calibration's shape (2-week momentum re-ranked daily) changes by about
    7 x sqrt(2/14) = 2.6 units a week against about 0.7 for H6 and H7.
- What a no-skill book looks like here (LESSONS 12 to 14). In the calibration's no-skill worlds every symbol has
  the same expected return, so a rank book earns nothing before costs and loses its costs; G1 then fails nearly
  always, and the no-skill families passed Tier 1 in 1 of 1,089 evaluated pairs. G6 alone passes such a book about
  1 time in 10: G6 compares the book with its OWN stale copies (lags of 30 days to half of VAL), so it does not
  protect against luck; G1, G4, G5, G8 and the count M do. What G6 does stop is a book whose return comes from
  holding the same names as its stale copies (a persistent tilt or a slow characteristic premium). Each hypothesis
  below is therefore written as a TIMING claim, and each says what its stale copies hold:
  - H5: the jump information of the last 3 weeks matters for the next weeks; a stale copy holds the skew of a
    window that no longer overlaps. A persistent tilt (some coins always right-skewed) is shared by the copies and
    earns no G6 credit.
  - H6: the last month's residual move predicts better than the residual moves of 1 to 18 months ago. Its first
    stale copies (lags of 30 to 56 days) hold the residual momentum of weeks 8 to 4 back, which is close to minus
    H7. If crypto momentum lasts many months, the stale copies earn too and H6 fails G6.
  - H7: the residual move of weeks 8 to 4 back predicts reversal better than the moves of older windows.
- Speed limit (G6 fails a book whose weights correlate above 0.5 with its own weights one lag step, 25.9 days,
  earlier, each name's mean removed). H5: a 21-day window of residuals; 26 days later the windows no longer
  overlap. H6: a 28-day formation; 26 days later the windows share 2 days (9 days at m = 5). H7: the same as H6,
  shifted back by m weeks. The persistent part of each input is what could still correlate; the DEV-only
  diagnostic D-ACF measures an upper bound (it removes no name mean), as in version 1.
- Lookback (limit 2,160 h, params at their highs; parse check): H5 1,271 h; H6 1,175 h; H7 2,015 h. D-ACF of H5
  2,039 h; of H6 1,921 h. H7 leaves no room for a 26-day lag under the limit (2,015 + 621 > 2,160); its speed-limit
  reading is a proxy (section H7).
- Cross-sections. A cs_* needs at least 10 in-play names with a known input. H5 computes the unit's mean return
  (cs_mean) INSIDE its windows: a cs_* is known only for in-play names, so a coin gets a known skew only after
  about 2n - 1 = 41 days in play (21-day beta windows chained into a 21-day skew window). Month-start entrants
  therefore trade from their second month on; G6 does not credit recent entrants either. H6 and H7 read windows
  of per-symbol fields only (as round 1's H1), so membership history does not matter to them; but a weekly bin
  is known only if every hour of it is known, so a name with one unknown hour drops out for m + 1 = 5 weekly bins
  (H6) or 2m + 1 = 9 (H7), and a market-wide unknown hour would flatten H7 for about 9 weeks. Named in advance;
  S1's avg gross shows it on DEV (round 1's weekly books held 0.85 to 0.87).
- G8 runs the rule on ranks 31 to 60. Every input is a residual, a ratio or a rank, so the rule means the same
  there.
- G7: the unit needs 10 seasoned members, and H7 needs about 12 weeks of history, so 2020 is a short bucket;
  in effect four of five buckets must be positive.
- Funding and basis: no program reads funding8h, funding_mean, index_close or mark_close (KP-017 and the ruling
  of 2026-11-23). Like every book, each pays or receives funding on what it holds; that is P&L, not an input.
- Literals and G5: no program has a jitterable literal (n_literals 0). H5 has one integer param (n = 21: every
  G5 variant is an n from 17 to 25 other than 21). H6 and H7 have two (m = 4: every G5 variant has m = 3 or m = 5,
  because 4 x U(0.8, 1.2) rounds to 3, 4 or 5 and an unchanged 4 moves by 1; n = 30: 24 to 36). The DEV
  neighbours below are those values.
- No calendar sampling. None of the programs freezes an hourly expression with hour or weekday indicators: that
  would work around KP-019, which the ruling of 2026-11-23 forbids.

## Disclosures that apply to every hypothesis

- The author model has read this market's history through DEV, VAL and the vault, and this session has read round
  1's DEV numbers (one-week residual continuation, continuation of unexplained aggressive flow, weak activity and
  ticket-size results). No rule below names a date, a coin, a price level or a remembered event; every tunable
  number is a declared param. That does not remove hindsight from the CHOICE of ideas (KP-010); each hypothesis
  states what I remember that could bias it.
- What I remember about VAL that touches every market-neutral top30 book (as in version 1): BTC's share of crypto
  market value rose through most of VAL and most altcoins lagged BTC; ETH lost ground to BTC over most of it;
  memecoin waves (2023, 2024) in which a few coins rose for weeks; single-coin collapses (FTT, November 2022).
  These memories favour continuation (H6) and argue against reversal (H7); for H5 they cut both ways.
- At most TWO programs are recommended for a counted submission whatever DEV says. LESSONS 12 and 14: a true
  Sharpe-1.5 book passes Tier 1 only 68 to 82% of the time in this unit, G6 does not protect against luck, and
  every counted trial raises M forever.
- Defaults are fixed now and are never changed after a run. Neighbours are a robustness check (the G5 values), not
  a search; a better neighbour does not move the default. No sign is ever flipped.

## DEV screen (round 2), fixed now, before any number

A hypothesis is recommended for a counted submission only if it passes every item that applies to it, in the
sandbox (full stage 1, no --quick). The numbers each item reads are named.

- S1 at its default: stage 1 passes as written (parse, constant probe, truncation and start-cut self-checks; the
  line "stage 1: ... -> PASS"), DEV direction changes >= 30, and avg gross >= 0.5.
- S2 at its default: DEV Sharpe >= 0.6 with the registered sign. A negative DEV Sharpe drops the hypothesis; no
  sign is flipped. For H6 S2 is necessary but is NOT evidence (its DEV is partly known from round 1, run 1).
- S3 neighbours (the G5 values): H5 at n = 17 and n = 25, H7 at m = 3, m = 5, n = 24 and n = 36: DEV Sharpe > 0 at
  each. H6 (stricter, because its default's DEV Sharpe is not evidence): at m = 3, m = 5, n = 24 and n = 36, DEV
  Sharpe >= 0.6 AND (total return - costs) > 0 at each.
- S4 at its default: DEV total return minus DEV costs > 0 (a rough DEV reading of G4: still positive with the
  costs paid twice).
- S5 at its default: net return positive in at least two of the three DEV years the sandbox prints (2020, 2021,
  2022); H6: in all three.
- S6 D-ACF ratio R = avg net / avg gross of the diagnostic (3 decimals each) <= 0.40: H5 from
  gen002_diag_acf_resid_skew; H6 from gen002_diag_acf_resid_momentum; H7 from the same diagnostic as a proxy
  (section H7).
- S7 (H6 only): H6's DEV Sharpe at its default is above that of the control gen002_diag_plain_momentum at its
  default (m = 4). Nobody has run plain weekly momentum, or any m-week version, in this unit.

For H6 the readings that carry weight are S3, S4 at five settings, S6 and S7: none of them has been seen.

Order and economy: the default runs first. If it fails S1, S2 or S4, the hypothesis is dropped and nothing else is
run for it. Neighbours run in the listed order and stop at the first that fails S3 (the hypothesis is then
dropped). The control runs only if H6 has passed S1 to S5. A D-ACF runs only for a hypothesis that has passed S1
to S5 (H6: and S7); the H6 diagnostic also runs, once, if H7 has passed S1 to S5.

---

## H5. gen002_resid_skew

- Family other. Kind portfolio. Unit top30. Dollar neutral, gross 1. A daily series (bins from 00:00 UTC, visible
  at the 23:00 bar, traded at the 00:00 open).
- Rule: for each coin in play, r = the daily log return; mk = the unit's equal-weighted mean of r (cs_mean over the
  in-play coins); beta = the coin's beta to mk over the last n daily rows (correlation x volatility ratio); e = r -
  beta x mk, each row with its own trailing beta; skew = sma(e^3, n) / sma(e^2, n)^1.5, the uncentred realised
  skewness of e over the last n rows. Weight: minus the cross-sectional rank of skew, demeaned, scaled to gross 1.
  Short the coins whose recent residual days were most right-skewed (up-jumps), long those most left-skewed
  (crash days).
- Program (default pre-registered; strategies/gen002_resid_skew.omr):

      n = param(21, 16, 26)          # daily rows for the beta and for the skewness
      d = daily(close)
      r = logret(d, 1)
      mk = cs_mean(r)
      beta = corr(r, mk, n) * std(r, n) / std(mk, n)
      e = r - beta * mk
      m2 = sma(e * e, n)
      m3 = sma(e * e * e, n)
      skew = m3 / (m2 * sqrt(m2))
      signal = cs_scale(cs_demean(-cs_rank(skew)))

  1 param (integer; G5 range 17 to 25), 0 jitterable literals, 41 nodes, lookback 1,271 h.
- Design choices, each made for a reason stated before any run: (1) log returns, because simple returns of a
  lognormal coin are mechanically right-skewed in proportion to its volatility, which would turn H5 into a
  volatility sort; (2) residual to the market, because on a market jump day a coin with beta above 1 moves more
  than the mean, and with beta set to 1 a market jump would leak into the skew of high- and low-beta coins and make
  H5 a bet on market reversal through beta; (3) the unit's mean rather than BTC as the market, because BTC is a
  member, its residual against itself is zero up to rounding, and skewness is a ratio, so rounding noise would put
  BTC at a random extreme rank every day (no coin equals the unit's mean); (4) a rolling beta (each row its own
  trailing beta) rather than one beta fixed over the window, because the fixed-window residual moments need the
  binomial coefficients 2 and 3, which would be jitterable literals (G5 would perturb an identity whose terms
  nearly cancel, and the second moment could turn negative), and writing 3x as x + x + x would dodge the literal
  rule; (5) n = 21 (three weeks), the longest default for which the D-ACF diagnostic still fits under the 90-day
  limit (two chained 21-day windows plus a 26-day lag: 2,039 h at the highs).
- Hypothesis: coins whose recent daily residual returns were right-skewed underperform the rest of the unit over
  the following weeks; left-skewed coins outperform.
- Mechanism: lottery preference. Investors who overweight small chances of large gains overpay for right-skewed
  payoffs (Barberis and Huang 2008; Kumar 2009 on lottery stocks). Evidence in equities: Bali, Cakici and Whitelaw
  (2011), the MAX effect; Amaya, Christoffersen, Jacobs and Vasquez (2015), weekly realised skewness predicting the
  next week's return with a negative sign; Bollerslev, Li, Patton and Quaedvlieg (2020), signed jump variation, also
  negative. In USDT perps leverage makes a right-skewed coin more lottery-like still, and a coin that just jumped
  draws attention and leveraged longs hoping for a repeat. On the long side, coins with recent crash days are
  shunned (disaster aversion) and must offer a premium; the book bears that crash risk.
- Other side: lottery-seeking leveraged longs on the short side; holders dumping a crashed coin on the long side.
  Why it can persist: it rests on a preference, shorting a right-skewed coin is exposed to squeezes (a limit to
  arbitrage), and the long side's crash risk is real, which is why it would pay.
- Costs: about 0.05 to 0.15 a year (S4 checks it).
- Relation to earlier trials and lessons: new idea; no counted trial, no round-1 program and no calibration family
  reads a higher moment. Answers LESSONS 8 to 11 (neutral; G6 credits only timing) and 13 to 14 (a timing claim,
  not a characteristic). Round 1's DEV observation (LESSONS 16: a week's residual move tended to continue) argues
  somewhat AGAINST H5 on DEV, since its short side includes coins that jumped up recently; it did not shape H5.
- What I remember that could bias it: the crypto evidence I recall conflicts. I recall a paper titled "MAX
  momentum in cryptocurrency markets" (Li, Urquhart, Wang and Zhang, about 2021) reporting that coins with a high
  maximum daily return kept outperforming (the opposite sign), and work on lottery demand in crypto (I recall
  Grobys and Junttila, 2021) that I remember, less surely, with the equity sign. Left-tail momentum in equities
  (Atilgan, Bali, Demirtas and Gunaydin 2020: stocks with large recent losses keep losing) argues against the long
  side. From DEV I remember the LUNA collapse (May 2022), in which a long-the-crash-day book holds a coin going to
  zero, and 2021 memecoin jumps that continued for days. From VAL I remember FTT (November 2022; the long side
  loses) and memecoin waves in 2023 and 2024 whose first jumps were followed by weeks of gains (the short side loses)
  and then by collapses (the short side gains). I do not remember any net result. Nothing I remember argues for H5.
  None of it shaped the rule: there is no crash filter and no per-coin cap beyond the rank weighting.
- Falsifier. DEV (not submitted): S1 to S6 (a wrong DEV sign drops it). Counted (VAL): falsified if G1 (PSR(0) <
  0.90), G4 (2x costs <= 0), G6 (p > 0.10, or the speed limit), G8 (next30 Sharpe <= 0), or any other Tier-1 gate
  fails. Named risk: G7 and the long side in a single-coin collapse.
- DEV exploration (at most 4 runs): default n = 21; then n = 17 and n = 25; then D-ACF
  (gen002_diag_acf_resid_skew, k = 26 daily rows).

## H6. gen002_resid_momentum (a continuation rule, written after round 1's DEV result)

- Family relative. Kind portfolio. Unit top30. Dollar neutral, gross 1.
- Rule: every week (weekly bins from Monday 00:00 UTC, visible at the Sunday 23:00 bar, traded at the Monday 00:00
  open), for each coin in play: resid = the coin's return over the last m weeks minus beta x BTC's return over the
  same weeks; beta = correlation x volatility ratio of daily returns against BTC over the last n days; z = resid /
  the coin's daily-return volatility over the same n days. Weight: + the cross-sectional rank of z, demeaned, scaled
  to gross 1. Beta and volatility update at each daily close. BTC's own residual is zero up to rounding, which puts
  BTC at the middle rank (z is a level divided by a volatility, not a ratio of two noises).
- Program (default pre-registered; strategies/gen002_resid_momentum.omr):

      m = param(4, 3, 5)             # weeks in the formation window
      n = param(30, 20, 45)          # daily rows for the BTC beta and the coin's volatility
      d = daily(close)
      db = daily(btc(close))
      r = ret(d, 1)
      rb = ret(db, 1)
      vol = std(r, n)
      beta = corr(r, rb, n) * vol / std(rb, n)
      resid = ret(weekly(close), m) - beta * ret(weekly(btc(close)), m)
      z = resid / vol
      signal = cs_scale(cs_demean(cs_rank(z)))

  2 params (integers; G5 values m = 3 or 5, n = 24 to 36), 0 jitterable literals, 36 nodes, lookback 1,175 h. The
  weights are an hourly-grid series (daily and weekly bars mixed).
- Hypothesis: a coin's return over the last month net of its BTC-beta part, in units of its own volatility,
  continues over the following weeks.
- Mechanism: underreaction. Coin-specific news diffuses slowly through a fragmented clientele (Hong and Stein
  1999), and holders sell winners too early and keep losers too long (the disposition effect; Grinblatt and Han
  2005, Frazzini 2006), so prices adjust in steps. The BTC-beta part is removed because a market move is not
  coin-specific news, and because the beta tilt of total momentum is what drives momentum crashes after market
  turns (Grundy and Martin 2001; Daniel and Moskowitz 2016); residual momentum has about half the volatility of
  total momentum in equities (Blitz, Huij and Martens 2011). Volatility scaling ranks how unusual the move was for
  that coin. Crypto: Liu, Tsyvinski and Wu (2022) report a cross-sectional momentum factor at one to four weeks.
- Other side: early profit-takers in winners, dip buyers averaging into losers, mean-reversion market makers,
  shorts fading a rally. Why it can persist: the behaviour is a property of the clientele; momentum's crash risk
  (reduced, not removed, by the residual) is the reason not everyone trades it.
- The provisions of LESSONS 16 and 17, point by point:
  (a) This hypothesis was written AFTER round 1's DEV result: version 1, run 1, the weekly residual REVERSAL (H1,
      the same beta and volatility machinery with a one-week return, n = 30) lost on DEV (Sharpe -1.566, negative
      in all three DEV years). H6 is not the exact mirror (that would be m = 1, outside the declared range of 3 to
      5), but its DEV result is partly predictable from run 1.
  (b) Its default's DEV Sharpe is therefore NOT evidence. S2 stays as a necessary condition only. The screen
      rests on readings nobody has seen: the four neighbours, each held to the liveness bar 0.6 and to S4 (S3,
      stricter than for H5 and H7); the plain control (S7); the costs paid twice at five settings (S4 and S3); the
      speed-limit diagnostic (S6). S5 is also stricter (all three DEV years), though per-year signs are partly
      predictable too.
  (c) How it differs from the calibration's momentum family (ucal_xs_momentum: the raw n-day return, n 3 to 60, on
      daily bars, re-ranked every day, linear weights concentrated in the largest movers): H6 removes the BTC-beta
      part, scales by volatility, weights by rank, and re-ranks once a week on a 4-week formation, so its
      rankings change by about a quarter as much per week as a daily re-ranked 2-week book (section "What a top30
      idea must clear"). Why it would survive costs: estimated 0.03 to 0.06 a year, about 0.1 to 0.25 Sharpe units
      (0.2 to 0.5 doubled), against a gross Sharpe that would have to be about 1.0. In the no-skill worlds the
      calibration family loses its costs (LESSONS 13); H6 would too, and that is what G1, G4 and M are for.
- G6 is H6's main named risk: H6 can pass only if the last month's residual predicts better than older residuals
  (short-lived momentum); its first stale copies hold roughly minus H7.
- What I remember that could bias it: the Liu-Tsyvinski-Wu result covers a broad universe with many small coins
  over 2014 to 2018; I believe the effect was weaker among large coins and later, but I do not remember it
  reliably. From VAL: BTC gaining on most altcoins, ETH losing ground to BTC for most of the period, memecoin runs
  lasting weeks, FTT falling over several days. All of these favour a momentum book, as a tilt or as
  continuation; I do not remember a number for any cross-sectional crypto momentum book in VAL. These memories
  argue FOR H6, and that is a bias I name. G6's stale copies carry a persistent tilt (BTC over altcoins, ETH under
  BTC) as much as the book does, and the speed-limit statistic removes each name's mean, so a tilt alone should
  not pass G6. m = 4 is the middle of the one-to-four-week range and halves the turnover of a one-week book; n = 30
  is round 1's H1 value; neither comes from VAL.
- Falsifier. DEV: S1 to S7 with H6's stricter S3 and S5. Counted (VAL): falsified if G1, G4, G6 (or the speed
  limit), G8, or any other Tier-1 gate fails.
- DEV exploration (at most 7 runs): default (m = 4, n = 30); then m = 3, m = 5, n = 24, n = 36; then the control
  gen002_diag_plain_momentum; then D-ACF (gen002_diag_acf_resid_momentum, k = 621 hours).

## H7. gen002_prior_month_reversal

- Family meanrev. Kind portfolio. Unit top30. Dollar neutral, gross 1.
- Rule: every week, for each coin in play: resid = the coin's return over the m weeks that ended m weeks ago
  (weeks t-2m to t-m; at m = 4 the month before last month) minus beta x BTC's return over the same weeks; beta
  and the volatility scale are the coin's current ones (daily returns against BTC over the last n days, as in H6);
  z = resid / volatility. Weight: minus the cross-sectional rank of z, demeaned, scaled to gross 1. The most recent m
  weeks are skipped on purpose.
- Program (default pre-registered; strategies/gen002_prior_month_reversal.omr):

      m = param(4, 3, 5)             # weeks in the formation window, and weeks skipped before it
      n = param(30, 20, 45)          # daily rows for the BTC beta and the coin's volatility
      d = daily(close)
      db = daily(btc(close))
      r = ret(d, 1)
      rb = ret(db, 1)
      vol = std(r, n)
      beta = corr(r, rb, n) * vol / std(rb, n)
      resid = lag(ret(weekly(close), m), m) - beta * lag(ret(weekly(btc(close)), m), m)
      z = resid / vol
      signal = cs_scale(cs_demean(-cs_rank(z)))

  2 params (integers; G5 values m = 3 or 5, n = 24 to 36), 0 jitterable literals, 39 nodes, lookback 2,015 h (the
  closest of the three to the 2,160-hour limit). One param sets both the window and the skip, so the G5 variants
  are weeks 6 to 3 back (m = 3) and weeks 10 to 5 back (m = 5).
- Hypothesis: a coin's BTC-beta residual return over the month before last month partly reverses over the
  following weeks.
- Mechanism: delayed overreaction. In the Hong and Stein (1999) model, slow news diffusion invites momentum
  traders, whose buying carries prices past value, and the excess reverts later. In crypto the cycle would be
  compressed into weeks: leveraged late chasers and slow trend rules (moving-average systems) are still long a
  month after a rally began, and supply meets the rally with a lag (project treasuries and early holders selling
  into strength). After a month of residual losses, forced and capitulating sellers are done.
- Other side: late momentum chasers and slow trend followers who entered after the first month; holders who
  capitulated late. Why it can persist: slow trend-following capital is large in this market, and supply responds to
  price with a delay.
- Why the skip: the fast reversal (the calibration's reversal family, 3 to 20 days with no skip; round 1's H1, one
  week) is what round 1 found absent on DEV. H7 claims nothing about the last m weeks.
- Costs: like H6 (3 of 4 weeks shared from week to week): about 0.03 to 0.06 a year (S4 checks it).
- Speed limit: the window of weeks 8 to 4 back and the window 26 days later share about 2 days. A D-ACF of H7
  itself cannot be written under the 90-day limit (2,015 h + a 621-h lag). Proxy: with the same m, H7's weights at t
  are close to minus H6's weights at t - m weeks (beta and volatility are taken at different times), so the
  correlation of H7's weights with their own values one lag step earlier is close to the same correlation for H6,
  which gen002_diag_acf_resid_momentum measures. S6 for H7 reads that diagnostic, and the plan calls it a proxy.
- Relation to earlier trials and lessons: not a mirror of round 1; its DEV result is unknown. It differs from the
  calibration's reversal family (raw returns, no skip, daily re-ranking) and from H1 (one week, no skip). With H6 it
  tests the term structure of residual predictability (continuation over the last month, reversal of the month
  before); either, both or neither can hold, and the two books are close to uncorrelated (their windows do not
  overlap at the defaults). Answers LESSONS 8 to 11 and 13 to 14 as above.
- What I remember that could bias it: the theory (Hong and Stein 1999); in equities, reversal at three to five years
  (De Bondt and Thaler 1985) and of momentum profits after a year (Jegadeesh and Titman 2001). For crypto I recall no
  evidence of reversal at one to two months, only a vague sense that crypto momentum decays within weeks. From VAL:
  most altcoins lagged BTC for long stretches and memecoin runs lasted months, so a book long the losers of the month
  before last would have lost on those trends; FTT stayed down after its collapse (the long side loses). My memory
  argues AGAINST H7.
- Falsifier. DEV: S1 to S6 (S6 by the proxy; a wrong DEV sign drops it). Counted (VAL): falsified if G1, G4, G6 (or
  the speed limit), G8, or any other Tier-1 gate fails. Named risks: G7, and a market-wide unknown hour flattening it
  for about 9 weeks (G10, G1).
- DEV exploration (at most 5 runs, plus the shared diagnostic): default (m = 4, n = 30); then m = 3, m = 5, n = 24,
  n = 36; then, if H6 has not already run it, gen002_diag_acf_resid_momentum as the proxy.

---

## DEV-only controls, round 2 (never to be submitted; each file's hypothesis line says so)

- strategies/gen002_diag_plain_momentum.omr: `signal = cs_scale(cs_demean(cs_rank(ret(weekly(close), m))))`,
  m = param(4, 3, 5). The raw m-week momentum with H6's weekly re-ranking, without the residual and the volatility
  scaling: H6's control for S7. Lookback 1,175 h.
- D-ACF, the speed-limit diagnostic, built as in version 1 (`signal = c * w * lag(w, k)`, c = param(20, 10, 30) so
  that positions are large against the engine's 0.01 band; R = avg net / avg gross = sum w w' / sum |w| |w'|,
  an upper bound of the gate's statistic; read from the two printed numbers):
  - strategies/gen002_diag_acf_resid_skew.omr: w = H5's weight row at its defaults (same text, same param range).
    H5's weights are a DAILY series, so k = param(26, 20, 32) daily rows (one lag step is 25.9 days). Lookback
    2,039 h.
  - strategies/gen002_diag_acf_resid_momentum.omr: w = H6's weight row at its defaults. An hourly-grid series, so
    k = param(621, 496, 746) hours, as in version 1's H1 diagnostic. Lookback 1,921 h. Also H7's proxy.
- Their Sharpe and returns mean nothing.

## Run order and budget (round 2, decided before any run)

| order | run | runs only if |
|---|---|---|
| 1 | H5 default (n = 21) | - |
| 2, 3 | H5 n = 17, then n = 25 | run 1 passed S1, S2, S4; run 3 only if run 2 passed S3 |
| 4 | H7 default (m = 4, n = 30) | - |
| 5 to 8 | H7 m = 3, m = 5, n = 24, n = 36, in this order | run 4 passed S1, S2, S4; each only if the one before passed S3 |
| 9 | H6 default (m = 4, n = 30) | - |
| 10 to 13 | H6 m = 3, m = 5, n = 24, n = 36, in this order | run 9 passed S1, S2, S4; each only if the one before passed H6's S3 |
| 14 | control gen002_diag_plain_momentum (m = 4) | H6 passed S1 to S5 |
| 15 | D-ACF gen002_diag_acf_resid_skew | H5 passed S1 to S5 |
| 16 | D-ACF gen002_diag_acf_resid_momentum | H6 passed S1 to S5 and S7, or H7 passed S1 to S5 (run once) |

Command form (from the project root, venv Python): `python -m omr.sandbox strategies/gen002_resid_skew.omr` and
`python -m omr.sandbox strategies/gen002_resid_skew.omr --set n=17`; full stage 1 on every run.

Planned: at most 16 sandbox runs. Reserve: 3 runs for an honest restatement after a stage-1 rejection the parse
check cannot see (the activity floor or a self-check; the constant probe already ran with the parse check), each a
recorded amendment of one of the forms the playbook lists in section 4, never a change of logic or of a default.
Cap for this round: 19 (the instruction allows 20); generation 2 would then have used at most 23 of 60. Every run
goes into the log below, including runs that fail.

Logged per run: DEV Sharpe, PSR(0), total return, maxDD, direction changes, avg gross, avg net, costs, funding paid,
rebalances, the per-year rows, the number of symbols ever in the unit, the lookback; for D-ACF the ratio R.

## Selection rule (round 2)

- A hypothesis is eligible only if it passes every screen item that applies to it.
- At most TWO programs are recommended for a counted run. If one or two are eligible, they are recommended. If all
  three are eligible, H5 and H7 are recommended and H6 is not, because H6's DEV numbers are not evidence and it
  ranks last by rule. DEV Sharpe is a liveness check, not a ranking.
- If H6 and H7 are both recommended, the coordinator should know that they are structurally linked (H7 is close to
  minus H6 lagged by m weeks): together they test one theory at two horizons.
- None eligible means none recommended; that is a result and is recorded as one.
- A recommended program is submitted only at its declared defaults, unchanged, after the coordinator's source read
  (playbook section 5). The DEV-only controls are never submitted.

## Sandbox run log (round 2)

(filled in during stage 2; every run, chosen or not)

| # | program | params (non-default only) | DEV Sharpe | DEV dir. changes | avg gross | avg net | costs | total return | years + (of printed) | note |
|---|---|---|---|---|---|---|---|---|---|---|

## Amendments (round 2)

(none)

## Notes for the coordinator (round 2, written with the plan)

- The parse check's OK lines include the constant probe: omr.lang.parse_file runs it by default (on the kernel's
  synthetic probe panel; no market data). The activity floor and the self-checks remain for the sandbox.
- H7's speed-limit reading is a proxy (H6's diagnostic), because H7's own lookback leaves no room for a 26-day lag
  under the 90-day limit. If the coordinator does not accept the proxy, S6 for H7 becomes an amendment written
  before run 4, and the speed limit stays an unmeasured risk for H7.
- Ideas stopped by the rules, not tested: (1) splitting a coin's return or volume by session (US hours against
  Asian hours) or weekend against weekday, a clientele idea in the spirit of overnight-versus-intraday returns in
  equities. Rolling hourly sums are legal but would re-rank every few hours (several times a weekly book's costs by
  my estimate), and freezing them weekly with hour or weekday indicators would work around KP-019, which ruling (4)
  forbids. (2) The exact window-fixed residual skewness for H5, which needs the binomial coefficients 2 and 3 as
  literals (see H5, design choice 4).
- Ambiguities: (a) whether a program that does not read funding but whose P&L includes funding (every book's does)
  counts as "funding-driven" under KP-017; I read it as allowed. (b) Whether mark_close alone, not set against
  close, is "built on the basis"; no program here reads it. (c) The playbook does not say how S3-type neighbours
  should be chosen for a program with two params (G5 moves both at once); version 2 runs each param's two G5 ends
  with the other at its default.

Pre-registration (version 2): 2026-11-23T23:46:18Z; no round-2 sandbox run has been made.
