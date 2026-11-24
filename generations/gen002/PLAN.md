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

## Notes for the coordinator (round 2): coordinator's rulings, 2026-11-23 UTC (2026-11-24 +08:00)

Received after version 2 was committed and pushed unchanged as b64b229 (PLAN.md sha256 0b97cf86e3fadb5a...;
version 1's first 35,535 bytes verified unchanged) and before round 2's run 1; recorded here before any round-2
sandbox run. Everything from here on is APPENDED to version 2: the 71,114 bytes committed as b64b229 stay an
unchanged prefix, so the empty run-log table and the "(none)" under "Amendments (round 2)" above are the
pre-registered headers, and the run log, the amendments (if any) and the outcome follow below.
(1) H7's speed-limit reading by H6's diagnostic (gen002_diag_acf_resid_momentum) is ACCEPTED as a proxy; it is
reported as a proxy, and the speed limit stays a named risk of H7. (2) A program that does not read funding is not
"funding-driven" merely because its book pays or receives funding: allowed. (3) Mark and index prices (mark_close,
index_close) stay out of this generation in every form. (4) The choice of neighbours for the two-param programs
(each param's two G5 ends, the other at its default) is accepted as registered. (5) The coordinator has read the
source of H5, H6 and H7 (playbook section 5): nothing to change.

## Sandbox run log (round 2), filled in during stage 2

(Appended here, below the pre-registered empty table, so that the file committed as b64b229 stays an unchanged
prefix. Every run is listed; run numbers follow the order table of version 2, and numbers not listed were not due
under its conditions.)

| # | program | params (non-default only) | DEV Sharpe | DEV dir. changes | avg gross | avg net | costs | total return | years + (of printed) | note |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | H5 gen002_resid_skew | (default n=21) | -1.906 | 2645 | 0.823 | 0.000 | 0.1404 | -0.730 | 0 of 3 (2020 -0.376 SR -2.528; 2021 -0.481 SR -2.133; 2022 -0.168 SR -0.989) | PSR(0) 0.000, maxDD 0.745, rebalances 1152, funding paid 0.0057, 75 symbols, lookback 1271 h, 78.7 s. Fails S2 (wrong sign), S4 (-0.730 - 0.1404 < 0) and S5; H5 DROPPED, runs 2, 3 and 15 not made |
| 4 | H7 gen002_prior_month_reversal | (default m=4, n=30) | 0.381 | 1894 | 0.866 | 0.000 | 0.1772 | 0.164 | 2 of 3 (2020 -0.099 SR -0.647; 2021 0.044 SR 0.292; 2022 0.238 SR 2.172) | PSR(0) 0.727, maxDD 0.201, rebalances 838, funding paid 0.0117, 75 symbols, lookback 2015 h, 73.6 s. Fails S2 (0.381 < 0.6) and S4 (0.164 - 0.1772 = -0.013); H7 DROPPED, runs 5 to 8 not made |
| 9 | H6 gen002_resid_momentum | (default m=4, n=30) | 0.945 | 1871 | 0.865 | 0.000 | 0.3299 | 0.643 | 2 of 3 (2020 0.682 SR 3.217; 2021 0.281 SR 0.976; 2022 -0.237 SR -2.221) | PSR(0) 0.930, maxDD 0.324, rebalances 885, funding paid -0.0764 (received), 75 symbols, lookback 1175 h, 80.7 s. Passes S1, S2 (a necessary condition only, not evidence) and S4 (0.643 - 0.3299 = 0.313); FAILS H6's S5 (all three years needed). Runs 10 to 13 due by the order table (its conditions are S1, S2, S4) |
| 10 | H6 gen002_resid_momentum | m=3 | 0.955 | 2013 | 0.866 | 0.000 | 0.3799 | 0.697 | 2 of 3 (2020 0.703 SR 3.204; 2021 0.306 SR 1.014; 2022 -0.237 SR -1.839) | PSR(0) 0.932, maxDD 0.358, rebalances 896, funding paid -0.0743, 75 symbols, 83.7 s. H6's S3 item met (>= 0.6; 0.697 - 0.3799 = 0.317 > 0) |
| 11 | H6 gen002_resid_momentum | m=5 | 0.923 | 1895 | 0.865 | 0.000 | 0.3131 | 0.627 | 2 of 3 (2020 0.603 SR 2.920; 2021 0.393 SR 1.235; 2022 -0.271 SR -2.699) | PSR(0) 0.927, maxDD 0.328, rebalances 870, funding paid -0.0935, 75 symbols, 104.3 s. Met (0.627 - 0.3131 = 0.314) |
| 12 | H6 gen002_resid_momentum | n=24 | 1.039 | 2082 | 0.866 | 0.001 | 0.3675 | 0.728 | 2 of 3 (2020 0.695 SR 3.214; 2021 0.392 SR 1.285; 2022 -0.268 SR -2.517) | PSR(0) 0.947, maxDD 0.345, rebalances 915, funding paid -0.0789, 75 symbols, 93.0 s. Met (0.728 - 0.3675 = 0.361) |
| 13 | H6 gen002_resid_momentum | n=36 | 1.069 | 1836 | 0.865 | 0.000 | 0.3320 | 0.775 | 2 of 3 (2020 0.708 SR 3.293; 2021 0.341 SR 1.126; 2022 -0.225 SR -2.045) | PSR(0) 0.952, maxDD 0.307, rebalances 856, funding paid -0.0745, 75 symbols, 86.8 s. Met (0.775 - 0.3320 = 0.443). Run 14 (control) not due: H6 did not pass S1 to S5. Run 16 (D-ACF of H6, H7's proxy) not due: H6 did not pass S1 to S5 and S7, and H7 did not pass S1 to S5 |

Total sandbox runs made in round 2: 7 (of the 16 planned and the cap of 19); none from the reserve; no stage-1
rejection, no kernel fault, no refusal. Every run: full stage 1 (25 truncation cuts), exit 0, nothing on stderr,
73.6 to 104.3 s. Before every run the kernel's memory estimate printed "fits now True" (estimate 0.79 GiB, wanted
free 1.18 GiB, free 1.46 to 3.02 GiB). The benchmark line printed by every run (equal-weight long of the in-play
members): DEV Sharpe 0.619, maxDD 0.847, as in round 1. ledger/sandbox_log.jsonl now has 29 rows (22 + 7).

## Amendments (round 2), stage 2

(none: no program text, param, default, screen item or run condition was changed)

## Screen outcome per hypothesis (round 2; stage 2, DEV, read from the run log above)

| H | S1 (dir. changes >= 30; avg gross >= 0.5) | S2 (DEV Sharpe >= 0.6, registered sign) | S3 (neighbours) | S4 (total - costs > 0) | S5 (years +) | S6 (D-ACF R <= 0.40) | S7 (H6 > control) | verdict |
|---|---|---|---|---|---|---|---|---|
| H5 gen002_resid_skew | pass (2645; 0.823) | FAIL (-1.906, wrong sign) | not run | FAIL (-0.730 - 0.1404 = -0.870) | FAIL (0 of 3) | not run | n/a | DROPPED |
| H7 gen002_prior_month_reversal | pass (1894; 0.866) | FAIL (0.381) | not run | FAIL (0.164 - 0.1772 = -0.013) | pass (2 of 3: 2021, 2022) | not run (proxy not due) | n/a | DROPPED |
| H6 gen002_resid_momentum | pass (1871; 0.865) | pass as a necessary condition only (0.945; not evidence) | pass, H6's strict form: m=3 0.955 (0.317), m=5 0.923 (0.314), n=24 1.039 (0.361), n=36 1.069 (0.443) | pass (0.643 - 0.3299 = 0.313) | FAIL, H6's strict form (2 of 3; 2022 -0.237, SR -2.221) | not run (not due) | not run (control not due) | NOT ELIGIBLE |

Against each pre-registered DEV falsifier:
- H5: falsified on DEV. The rank against residual skewness lost in all three DEV years (DEV Sharpe -1.906): coins
  with right-skewed residual days outperformed and left-skewed coins underperformed on DEV.
- H7: falsified on DEV. The sign was the registered one, but the size (0.381) was below the liveness bar and the
  return did not cover a second payment of costs.
- H6: not eligible. It met S1, S2 (as a necessary condition), its strict S3 at all four neighbours and S4, and
  failed its strict S5: the default lost in 2022H1 (-0.237, Sharpe -2.221), as did every neighbour. Because S1 to
  S5 were not all passed, its control (S7) and its speed-limit diagnostic (S6) were not due, so whether the BTC-beta
  residual adds anything over plain momentum, and how close H6 is to the speed limit, were not measured.

## DEV observations (round 2; NOT hypotheses, never to be submitted from this plan)

- H5's loss was large and in every DEV year. On DEV, a coin's recent residual up-jumps went with outperformance and
  its crash days with underperformance: the lottery sign failed, as did round 1's two bets against the week's move
  (LESSONS 16 and 17). The plan forbids flipping a sign; no mirror was run. A mirror of H5 would be a continuation
  rule and would fall under the provisions of LESSONS 16 and 17, with DEV already spent for it.
- H6's DEV numbers were close to one another over the five settings (Sharpe 0.92 to 1.07; total minus costs 0.31 to
  0.44) and all five lost in 2022H1 (Sharpe -1.8 to -2.7). These numbers are not evidence (H6 was written after round
  1's DEV result), and nothing here changes its default or makes it eligible.
- Costs were far above the plan's estimates for the two weekly-formation books: H6 paid 0.31 to 0.38 of equity over
  DEV (about 0.125 to 0.15 a year) and H7 0.177 (about 0.07 a year), against 0.03 to 0.06 a year estimated; H5 paid
  0.140 (about 0.056 a year, inside its estimate). Possible causes, NOT measured: the BTC term of an m-week residual
  (beta x BTC's m-week return) is large, so the daily update of beta moves the residuals and the ranks every day;
  and a continuation book's holdings drift away from their targets as its winners keep moving, which the engine
  trades back. H6 also received funding over DEV (0.074 to 0.094 of equity).
- All three books held positions over most of DEV (avg gross 0.82 to 0.87; 75 symbols ever in the unit); H7's
  9 weekly bins did not flatten it for long on DEV.
- WEAK: one DEV period, one researcher session; nothing here is a parameter recommendation.

## Recommendation (round 2)

NONE. By the pre-registered selection rule a hypothesis is eligible only if it passes every screen item that
applies to it: H5 failed S2, S4 and S5; H7 failed S2 and S4; H6 failed its strict S5. No program from version 2 is
recommended for a counted submission. The DEV-only controls (gen002_diag_*) are never to be submitted.

---

# Generation 2 - PLAN, version 3 (round 3, pre-registered 2026-11-24 before any round-3 sandbox run)

Researcher session for generation 2, round 3, stage 1 (read, think, pre-register). Unit: top30. A fresh session:
rounds 1 and 2 are known to it only through the files listed below. The date in the heading is local time
(+08:00); the UTC time is in the last line of this version.

- Kernel: semantic 5ea66b0fb79ca267d3c8de22d203976aab3bca5634b22e026b13687c69eb2687 (39 files), text
  1366fb8fd0b6976839a3e6b16e40c402291c0154bb8ccfeae24bcd6848c72924 (35 files) (`python -m omr.status`: kernel OK
  bcc4b1aa255b4679, sealed). Sealed G6 thresholds: core 0.10, top30 0.10. Data research_hash 28d9084a8c5c7659...,
  validated, snapshot_end 2026-11-18 10:00 UTC.
- Ledger when this was written: M = 5 counted trials (generation 0: 4, generation 1: 1, generation 2: 0 of 5), N
  4.86, rho 0.035, Tier 1: 0, pool 0 of 5, last census none, one uncounted stage-1 rejection (generation 0).
  `omr.kernel_lock verify` OK (sealed, core 0.1, top30 0.1); `omr.ledger verify` OK, all six chains (trials 10
  rows, stage1_log 1, kernel_history 10, calibration_log 4, sandbox_log 29, val_access_log 22). Sandbox runs used
  in generation 2 so far: 11 of 60 (round 1: 4, round 2: 7).
- Read: RESEARCH_PLAYBOOK.md (all, with section 4b), LANGUAGE.md (all; sections 5, 6 and 10 for funding8h,
  funding_mean, mark_close and index_close, their freshness rules and their lookback leaves), CONSTITUTION.md
  sections 4 to 7 and 13, LESSONS.md (1 to 26), generations/gen002/REPORT.md (both rounds), this file's versions 1
  and 2 with their run logs, screen outcomes and recommendations, generations/gen001/REPORT.md,
  generations/gen000/REPORT.md, KERNEL_PROPOSALS.md entry KP-017 only, STATE.md, the trial rows of `omr.ledger
  summary`, `omr.status`; program shapes omr/programs/ucal_xs_carry.omr, ucal_xs_momentum.omr,
  kernel_noise_top30.omr, strategies/gen000_funding_carry.omr and every strategies/gen002_*.omr of rounds 1 and 2.
  Kernel source read only to learn how the tool behaves: omr/sandbox.py (it prints avg gross, avg net, the funding
  paid as ONE net number, the costs and the per-year rows), omr/engine.py (funding: at each settlement open, equity
  -= the drifted position held into that open x the settled rate; under G2's stress payments x1.5 and receipts
  x0.5; a rebalance trades every name to target once any name is more than 0.01 off), omr/lang.py (lookback leaves:
  index_close and mark_close 7 h, funding8h 17 h, funding_mean(n) 8n h; timeframe functions take a field or
  btc(field); the Program fields). Also read for the same purpose, beyond the three files the brief named, and
  stated here for that reason: the funding parts of omr/datasets.py (a settlement at hour t is visible from the
  close of the bar that opens at t, one hour after the engine has charged it, so no program knows a rate before it
  pays or receives it), of omr/interp.py (funding8h = rate x 8 / interval; funding_mean = the mean of the last n
  settlements as 8-hour rates, held until the next) and a few constants of omr/constants.py (DEV and VAL dates, the
  0.01 band). These are code, not data or results.
- Not opened: anything under data/, ledger/returns/, ledger/trials/, _build/, audits/, and every calibration file.
  No VAL number exists for any program below. No round-3 sandbox run has been made.
- Versions 1 and 2 above are unchanged byte for byte (the first 80,097 bytes of this file, sha256
  f31172f414ad274f...). No earlier program file was changed; round 3 adds eleven new files (three candidates and
  eight DEV-only diagnostics).

Three hypotheses, numbered on from version 2. All are market neutral (dollar neutral), and all read the inputs
opened in this round. By the coordinator's ruling of 2026-11-24 they may be pre-registered and explored on DEV,
and a COUNTED submission of any of them (each reads funding_mean or index_close) also needs the coordinator's
KP-017 measurement of how the timing gate G6 behaves for funding-driven books. None uses hour or weekday.

| H | program | input | prediction | family |
|---|---|---|---|---|
| H8 | gen002_premium_shock | the perp premium over the spot index at daily closes: the median of the last 14 days minus the median of the last 42 | coins whose premium rose above their own norm lag, coins whose premium fell below it lead | carry |
| H9 | gen002_funding_shock | settled funding: the mean of the last 42 settlements minus the mean of the last 126 (14 against 42 days at 8-hour settlements) | coins whose funding rose above their own norm lag, coins whose funding fell below it lead | carry |
| H10 | gen002_unrewarded_premium | the 14-day median premium net of the part that a cross-sectional fit on the 14-day return explains | coins with more premium than their recent move explains lag, coins with less lead | carry |

H8 and H9 test one mechanism (a change in crowded leverage unwinds) with two measurements of it, so at most one of
them is screened to the end and recommended (selection rule). H10 is a different mechanism (leverage that the price
has not rewarded) and combines the basis with a price input.

## What a funding or basis book must clear in unit top30

- Costs. 12.5 bps per side. Round 1's weekly rank books paid 0.055 to 0.092 of equity a year, round 2's books
  with a daily-moving part 0.07 to 0.15 (LESSONS 19, 24): the turnover of an hourly-grid signal is set by its
  fastest-moving part. A dollar-neutral rank book here has a volatility of roughly 0.2 to 0.26 a year, so 0.1 a
  year of costs is about 0.4 to 0.5 Sharpe units, twice that under G4. The three programs are built to move slowly:
  - H8 and H10 read the premium only at daily closes (one snapshot a day, the 23:00 bar's close, through
    `daily(close)` and `daily(index_close)`), so their weights change once a day, traded at the 00:00 open. H8 ranks
    a difference of two medians; a median moves only when the entering or the leaving snapshot crosses it, so it is
    stickier than a mean.
  - H9 reads funding_mean, which changes at each settlement (every 8 hours on DEV) by 1/42 of the difference
    between the newest and the oldest settlement in its window: a smooth path, whose small steps the engine's 0.01
    band absorbs.
  - An hourly mean of the premium would be the better measurement, but on hourly rows it would re-rank every hour,
    and there is no way to average an hourly expression into a daily or weekly bar (KP-019). That is why the
    premium is sampled at daily closes and smoothed by a median over days.
- What a no-skill funding book looks like here (LESSONS 13 to 15, KP-017). In the calibration's null worlds every
  funding rate is multiplied by a fair sign coin per settlement hour, so no funding is predictable, and the carry
  family (ucal_xs_carry: minus the linear funding level over 3 to 30 settlements, re-ranked at every settlement)
  loses its costs; G1 stops it. But G6 alone passed that losing book in 53 of 166 pairs at 0.10 under null B (about
  16 expected). The suspected reason: G6 compares the book with its own stale copies by Sharpe, each paying its own
  costs, and of two losing books the one with the larger flows at its actual timing has the less negative Sharpe.
  So every hypothesis here is built to be:
  - CHEAP: a cost ceiling (S9) next to the doubled-cost reading (S4).
  - A PRICE claim, not only a funding claim: G2 halves receipts and adds half again to payments, and a book whose
    advantage over its stale copies were only its larger funding flows is exactly the case KP-017 has not
    measured. Each hypothesis claims that its input predicts RELATIVE PRICE moves, with the funding it receives as
    a bonus; S8 asks that the DEV return stays positive with the whole net funding flow taken out.
  - A TIMING claim: each says what its stale copies hold and why they would earn less, and a DEV-only stale copy
    (S7, new in this version) checks it.
- Speed limit. G6 fails a book whose weights correlate above 0.5 (each name's mean removed) with its own weights
  one or more lag steps (25.9 days) earlier. A carry book on the funding LEVEL holds the same high-funding coins
  month after month. H8 and H9 therefore rank the CHANGE against the coin's own 42-day norm: a coin's lasting level
  drops out, and only the last two weeks' departure from it is ranked. Their 14-day windows and the windows 26 days
  earlier do not overlap, and the 42-day norm of today contains the recent window of 26 days ago, which pulls the
  correlation down. H10 ranks a level (net of the return) and is the most exposed of the three to the speed limit.
  The D-ACF diagnostic (S6) measures an upper bound for each.
- Lookback (limit 2,160 h, params at their highs; parse check): H8 1,253 h; H9 1,216 h; H10 455 h. Diagnostics:
  stale copies 2,117 h (H8), 2,080 h (H9), 1,319 h (H10); price-neutral twins 1,253 h (H8), 1,216 h (H9); D-ACF
  2,021 h (H8), 1,962 h (H9), 1,223 h (H10).
- Cross-sections. A cs_* needs at least 10 in-play names with a known input. H8 needs every one of its last 42 daily
  snapshots known (a daily bin is known only if all 24 of its hours are, and index_close is known while its bar is
  at most 6 hours old), so a name with a hole in its klines or a gap of more than 6 hours in its index bars drops
  out for up to 42 days; H10 needs 14 known days and 15 known daily closes; H9 needs its last 126 settlements inside
  the last 1,008 hours, so one missing settlement takes a name out for up to 42 days. The sandbox does not print how
  many names a book holds, so this coverage loss is a named risk that DEV shows only if the unit falls below 10
  names (avg gross, S1).
- G8 runs the rule on ranks 31 to 60. The inputs are ratios to the index, rates or ranks, so the rule means the same
  there; funding and premiums are more extreme further down the ranking.
- G7: with 90-day seasoning and 42 days of history, 2020 is a short bucket; in effect four of the five later
  buckets must be positive.
- Literals and G5: no program has a jitterable literal (n_literals 0). G5 multiplies every param by its own
  U(0.8, 1.2) at once. The DEV neighbours (S3) are the two corners where all params sit at the same G5 end together
  (all at about 0.8 x default, all at about 1.2 x default); mixed corners are not read.
- No calendar sampling and no hour or weekday indicator (KP-019 is not worked around).

## Disclosures that apply to every hypothesis

- The author model has read this market's history through DEV, VAL and the vault, and this session has read rounds
  1 and 2's DEV numbers. No rule below names a date, a coin, a price level or a remembered event; every tunable
  number is a declared param. That does not remove hindsight from the CHOICE of ideas (KP-010); each hypothesis
  states what I remember that could bias it.
- What I remember about funding and premiums in VAL (July 2022 to June 2025), touching every book here: funding low
  and often negative in the 2022H2 bear (after LUNA, Three Arrows, Celsius, FTX), low through most of 2023, very
  high in February and March 2024 (spot ETF inflows, memecoin runs), low in mid-2024, high again in November and
  December 2024, lower in 2025 with negative stretches. These levels move together across coins, which the
  cross-sectional ranks remove. Structural changes: Binance moved many contracts to 4-hour funding and changed caps
  in 2023 and 2024 (funding8h normalises the rate, but a funding_mean window of n settlements then covers half the
  hours: H9, named); Ethena's basis trade grew large in 2024 and compressed BTC and ETH funding. Single-coin
  collapses with deeply negative funding (FTT, November 2022); memecoins entering the top of the volume ranking in
  2023 and 2024 with high funding during runs that lasted weeks before collapsing; squeezes of heavily shorted coins,
  none of which I can name among top30 members. I do not remember the result of any cross-sectional funding or basis
  book in VAL.
- What I remember about DEV (2020 to June 2022), touching every book here: the 2021 manias (DOGE in spring 2021,
  gaming and metaverse coins late in 2021) with very high funding for weeks while prices kept rising, then crashes
  (May 2021 above all); DeFi tokens in 2020 likewise; LUNA in May 2022, whose funding and premium fell deeply
  negative as it went to zero.
- What this project's DEV results say about funding (read in the run logs above, so known to this session): residual
  moves continued rather than reversed (LESSONS 16, 21, 23, 26); aggressive taker buying beyond the week's return
  went with continuation (LESSONS 17). And the funding paid by round 1 and 2's books: H6, long residual winners and
  short residual losers, RECEIVED 0.074 to 0.094 of equity over DEV; H1 and H7, both long recent residual losers,
  PAID 0.021 and 0.012. So on DEV recent losers tended to carry higher funding than recent winners, and a book short
  high or rising funding may ride DEV's continuation on DEV for a reason that is not its hypothesis. That is why
  S10 (a price-neutral twin of H8 and H9) and H10's construction (orthogonal to the coin's own recent move) exist.
- The clamp. I remember Binance's funding formula as the average premium index plus clamp(0.01% - premium,
  -0.05%, +0.05%) per 8 hours, so a coin whose premium stays inside a band of about -0.04% to +0.06% pays exactly the
  default 0.01%. That memory shaped H9's weighting (ties at a shock of exactly 0) and the choice of the premium as
  the input of H8 and H10. It is a rule of the exchange, not a memory of any period's prices, and it is not verified
  on data.
- The literature I remember on crypto carry: Schmeling, Schrimpf and Todorov ("Crypto carry", BIS, about 2023):
  carry is high when trend-chasing investors lever up, and high carry precedes sell-offs and liquidations; He,
  Manela, Ross and von Wachter ("Fundamentals of perpetual futures", about 2022): large perp-spot gaps that
  arbitrage closes only slowly; Christin, Routledge, Soska and Zetlin-Jones ("The crypto carry trade", about 2022).
  As I remember them these are mostly time-series results on BTC and ETH, not a top30 cross-section; they favour the
  registered (contrarian) direction of all three hypotheses, a bias I name.
- At most TWO programs are recommended for a counted submission whatever DEV says, at most one of H8 and H9, and
  each only as "eligible, subject to the KP-017 measurement". LESSONS 12 and 14: a true Sharpe-1.5 book passes
  Tier 1 only 68 to 82% of the time in this unit, G6 does not protect against luck, and every counted trial raises
  M forever.
- Defaults are fixed now and are never changed after a run. Neighbours are a robustness check (G5 corners), not a
  search; a better neighbour does not move the default. No sign is ever flipped.

## DEV screen (round 3), fixed now, before any number

A hypothesis is eligible only if it passes every item that applies to it, in the sandbox (full stage 1, no
--quick). S1 to S6 are the items of versions 1 and 2 (S1 and S3 tightened); S7 to S10 are new and only add
requirements. The sandbox lines each item reads: "stage 1: ... direction changes (DEV) X ... -> PASS"; "DEV Sharpe S
... total T ..."; "rebalances ... avg gross G  avg net N  funding paid F  costs C  liquidated L"; the per-year rows.

- S1 at its default: stage 1 PASS as written (parse, constant probe, truncation and start-cut self-checks), X >=
  30, G >= 0.5, and L False.
- S2 at its default: S >= 0.6 with the registered sign. A negative S drops the hypothesis; no sign is flipped.
- S3 at both G5 corners: S > 0 AND T - C > 0 at each (tightened from S > 0 alone). H8: (a, b) = (11, 34) and
  (17, 50). H9: (a, b, size) = (34, 101, 0.08) and (50, 151, 0.12). H10: n = 11 and n = 17.
- S4 at its default: T - C > 0 (a rough DEV reading of G4: still positive with the costs paid twice).
- S5 at its default: the year's return > 0 in at least two of the three DEV years printed (2020, 2021, 2022).
- S6 speed limit: the D-ACF ratio R = N / G of the hypothesis's diagnostic (3 decimals each) <= 0.40. R is an upper
  bound of the gate's statistic: it does not remove each name's mean, and even without lasting per-name parts it
  reads about a third above the correlation for rank-shaped weights (for two uniformly spread weight rows with a
  small correlation c, sum w w' / sum |w| |w'| is about 4c / 3). So S6 is stricter than the gate, most of all for
  H10, whose weights keep a lasting per-name part. It stays at version 1's 0.40; it is not loosened.
- S7 timing (new): the DEV Sharpe of the hypothesis's stale copy (gen002_diag_stale_*: its own default weights from
  30 days earlier, held now on the names in play now, re-centred to net zero, not rescaled) is below 0.5 x S. The
  copy pays its own costs, as in G6. 30 days is G6's shortest lag before its random phase, so this copy is the most
  similar one G6 can draw; if it earns half as well as the book, the book's return is not a timing return. One copy
  over DEV against G6's 20 over VAL: a necessary reading, not a proof.
- S8 funding stress (new): at its default, T - |F| > 0: the DEV return stays positive with the whole net funding
  flow taken out. Why: G2 multiplies receipts by 0.5 and payments by 1.5, so it costs 0.5 x (gross received + gross
  paid), at least 0.5 x |F|, and the sandbox prints only the net F. Taking out all of |F| covers the stress when the
  smaller of the two gross flows is at most half of |F|, as for a book that mostly receives. It is also the item that
  asks for a PRICE edge rather than collected funding.
- S9 cost ceiling (new): at its default, C <= 0.25 of equity over DEV (about 0.10 a year, inside the range of books
  with a daily-moving part, LESSONS 24). Why: KP-017, a funding book must be cheap to trade; S4 alone would admit a
  book whose costs are large next to its volatility.
- S10 price-neutral twin (new; H8 and H9 only): the DEV Sharpe of the hypothesis's twin (gen002_diag_twin_*: the
  rank of the same shock, regressed across coins on each coin's 14-day log return, the residual held with the
  registered sign) is at least 0.5 x S. Why: on DEV recent losers carried higher funding (disclosures above), so a
  book against rising funding or premium can lean on DEV's continuation of recent moves; if taking the
  return-aligned part out of the shock costs the book more than half its DEV Sharpe, its DEV result is not evidence
  for leverage information. H10 needs no twin: it is built orthogonal to its own 14-day return.

Order and economy: the defaults run first. If a default fails S1, S2, S4, S5, S8 or S9, the hypothesis is dropped
and nothing else is run for it. Otherwise its corners run in order and stop at the first that fails S3. The
diagnostics run only for a hypothesis that passed S1 to S5, S8 and S9, one at a time, each only if the one before
passed its item: the stale copy (S7), then the twin (S10, H8 or H9), then the D-ACF (S6). Of H8 and H9, only ONE
gets diagnostics (the FIRST, defined under the run order): one mechanism gets one set of diagnostics, because a
second set would be a second draw on DEV for the same claim.

---

## H8. gen002_premium_shock

- Family carry. Kind portfolio. Unit top30. Dollar neutral, gross 1. A daily series (bins from 00:00 UTC, visible
  at the 23:00 bar, traded at the 00:00 open).
- Rule: for each coin in play, bd = (close - index_close) / index_close at each daily close, the perp's premium over
  its spot index (the basis as LANGUAGE.md section 5 defines it). shock = the median of the last a = 14 daily
  premiums minus the median of the last b = 42. Weight: minus the cross-sectional rank of shock, demeaned, scaled to
  gross 1. Short the coins whose premium rose most above their own six-week norm, long those whose premium fell most
  below it.
- Program (default pre-registered; strategies/gen002_premium_shock.omr):

      a = param(14, 11, 17)          # daily premium snapshots in the recent median (two weeks)
      b = param(42, 33, 51)          # daily premium snapshots in the coin's own norm (six weeks)
      bd = (daily(close) - daily(index_close)) / daily(index_close)
      shock = median(bd, a) - median(bd, b)
      signal = cs_scale(cs_demean(-cs_rank(shock)))

  2 params (integers; G5 values a = 11 to 17 and b = 34 to 50, never the defaults themselves), 0 jitterable
  literals, 18 nodes, lookback 1,253 h.
- Design choices, each made for a reason stated before any run: (1) the premium, not settled funding, because
  funding is clamped at the default rate for any coin whose premium stays inside the exchange's band, so in calm
  periods most coins tie, while the premium keeps its information there; (2) the change against the coin's own
  norm, not the level, because a lasting level (some coins always trade at a premium) is held by G6's stale copies
  as much as by the book, earns no timing credit and slows the weights; (3) medians, because a daily snapshot whose
  index row is stale (allowed up to 6 hours) carries up to six hours of price move, many times a typical premium,
  and a mean would let one such snapshot set a rank for two weeks; (4) daily snapshots, for costs (section above);
  (5) two weeks against six: two weeks is the horizon of a leverage cycle in the mechanism below and halves the
  turnover of a one-week median; the norm is three times as long so that the recent window is a minority of it; and
  the stale copy (30 days) and the D-ACF (26 days) still fit under the 90-day limit.
- Hypothesis: a coin whose perp premium over the spot index has risen above its own recent norm underperforms the
  rest of the unit over the following weeks; a coin whose premium has fallen below its norm outperforms.
- Mechanism: the premium is the price of leverage on the perp. It rises when leveraged perp longs arrive faster
  than arbitrage capital absorbs them (retail trend-chasers use perps because they are the cheapest leverage), and
  the arbitrageurs who sell the perp to them hedge by buying spot, which passes the pressure into the spot price.
  When the leverage unwinds (stop-outs, liquidation cascades, funding costs eating margin) the arbitrageurs sell the
  spot again and the pressure reverses. The short side also collects the funding the new longs pay. A premium
  falling below its norm marks the mirror: perp shorts arriving (hedgers of unlocked, staked or airdropped tokens,
  bears) or leveraged longs leaving; the long side receives funding (or pays less) and gains when the hedges are
  lifted or the shorts are squeezed. In other words, perp-led moves (premium moving with the price) reverse and
  spot-led moves (price moving while the premium does not) continue: for one coin both cases come to minus the sign
  of the premium change, which is the rule.
- Who pays, why they keep paying, what the receiver is paid for: leveraged perp longs on the short side and perp
  shorts on the long side pay the funding. Leverage demand is a clientele feature of perps and hedgers need their
  hedge, while the arbitrage that would close a premium needs capital, and for a discount it needs borrowable spot,
  which is scarce for many altcoins. The receiver bears squeeze risk on the short side (a mania can carry a crowded
  coin much further) and single-coin collapse risk on the long side (a coin whose premium falls because informed
  holders hedge or flee), and both legs lose together when the whole market de-levers. Rank weights cap a name at
  about 1/15 of the gross.
- What its stale copies hold (the timing claim): G6's copies, at lags of 30 days and more, hold the premium shocks
  of one to eighteen months ago, whose 14-day windows no longer overlap the book's. If crowding unwinds within
  weeks, they hold coins whose leverage has already left, earn about nothing on price and collect less funding
  (their premium has normalised). If crowding regimes last for months, the copies earn too, and H8 fails S7 or G6,
  as it should.
- Costs: daily medians over 14 days; estimate 0.04 to 0.10 a year (0.10 to 0.25 over DEV). Funding: probably a net
  receiver (the short side holds the coins whose premium, and so funding, has risen). S4, S8 and S9 read both.
- Relation to earlier trials, lessons and rounds: the first program in this project to read index_close (the
  selftest program kernel_noise_top30 ranks the basis as meaningless noise). It differs from the calibration's carry
  family (minus the linear funding LEVEL, re-ranked at every settlement) in its input (the unclamped premium), in
  ranking a change against the coin's own norm, and in daily re-ranking; and from gen000_funding_carry
  (c30a93ef73a529bd, LESSONS 3: a single-coin time-series rule on the funding level with thresholds, lost in DEV and
  VAL). Answers LESSONS 13 to 15 (cheap, a price claim, a timing claim) and 19 and 24 (daily snapshots, medians).
  LESSONS 17 argues against it on DEV: aggressive taker buying beyond the week's return went with continuation, and
  a rising premium is also perp buying pressure. LESSONS 16, 21 and 26 (bets against recent moves lost) argue
  against it to the extent that a rising premium comes with a rising price; the funding paid by H1, H6 and H7 argues
  for it on DEV for the wrong reason (S10).
- What I remember that could bias it: the crypto-carry literature above (for the registered direction; mostly BTC
  and ETH time series). Commodity evidence on hedging pressure (de Roon, Nijman and Veld 2000) and basis momentum
  (Boons and Prado 2019) concerns futures curves, not perp premiums. From DEV: the 2021 manias, where H8's short side
  loses during the run-up and gains in the crash; LUNA in May 2022, which H8's long side would have held as its
  premium collapsed (against H8 in 2022H1). From VAL: the 2024 memecoin runs and the late-2024 rally (against H8
  during the runs, for it after), FTT (against its long side). None of it shaped the rule: there is no crash filter,
  no cap beyond the rank weighting, no coin and no date.
- Falsifier. DEV (not submitted): S1 to S10 (a wrong DEV sign drops it). Counted (VAL), only after the KP-017
  measurement: falsified if G1 (PSR(0) < 0.90), G2 (funding-stress Sharpe <= 0), G4 (2x costs <= 0), G6 (p > 0.10,
  or the speed limit), G8 (next30 Sharpe <= 0), or any other Tier-1 gate fails. Named risks: G7 and a single-coin
  collapse on the long side; coverage loss from index gaps.
- DEV exploration (at most 6 runs): default (a = 14, b = 42); then (11, 34) and (17, 50); then, if it is the FIRST
  of H8 and H9, the stale copy gen002_diag_stale_premium_shock (S7, k = 30 daily rows), the twin
  gen002_diag_twin_premium_shock (S10, m = 14 days) and the D-ACF gen002_diag_acf_premium_shock (S6, k = 26 daily
  rows).

## H9. gen002_funding_shock

- Family carry. Kind portfolio. Unit top30. Dollar neutral; no name above 0.1 of equity. An hourly-grid series that
  changes at funding settlements (every 8 hours on DEV) and is held in between.
- Rule: for each coin in play, shock = funding_mean(a) - funding_mean(b), with a = 42 and b = 126 settlements (each
  as an 8-hour rate; at 8-hour settlements the last 14 days against the last 42). Weight: size x minus the
  cross-sectional rank of shock (centred, in [-1, 1]), size = 0.1. The kernel scales the book down to gross 1 when
  its gross exceeds 1, which it does whenever the shocks are spread out (about 1.55 for 30 distinct ranks). Short
  the coins whose funding rose most above their own norm, long those whose funding fell most below it.
- Program (default pre-registered; strategies/gen002_funding_shock.omr):

      a = param(42, 33, 51)          # funding settlements in the recent mean (14 days at 8-hour settlements)
      b = param(126, 100, 152)       # funding settlements in the coin's own norm (42 days at 8-hour settlements)
      size = param(0.1, 0.08, 0.12)  # weight per unit of centred rank: no name above this size
      shock = funding_mean(a) - funding_mean(b)
      signal = size * cs_demean(-cs_rank(shock))

  3 params (a and b integers: G5 values a = 34 to 50, b = 101 to 151; size 0.08 to 0.12), 0 jitterable literals,
  9 nodes, lookback 1,216 h.
- Why size instead of cs_scale: settled funding is clamped, so a coin whose premium stayed inside the band for all
  42 days has a shock of exactly 0, and in calm stretches many coins tie there. cs_rank gives tied coins one average
  rank (close to 0 after centring); cs_scale would then put the whole gross on the few coins that differ (with one
  outlier and 29 ties, 0.5 of equity on one name). With size x rank no name exceeds 0.1, the book is small while the
  shocks tie, and it is scaled to gross 1 otherwise. For the coordinator's source read: size is a plain per-name
  size, not a near-constant, not a threshold and not used in a comparison; G5's jitter of it moves the gross of a
  tied book by up to 20% and does nothing to a book the kernel scales down.
- Hypothesis: a coin whose mean funding over the last two weeks has risen above its own six-week norm
  underperforms the rest of the unit over the following weeks; a coin whose funding has fallen below its norm
  outperforms.
- Mechanism: H8's, read from the settled funding. Funding is the time average of the premium over each settlement
  interval, clamped, so it is a precise, slow measure of crowded leverage that registers only crowding strong enough
  to leave the band; it is also exactly what a held position pays or receives. Who pays, why, and what the receiver
  bears: as in H8.
- What its stale copies hold: the funding shocks of one to eighteen months ago, as in H8. A coin with structurally
  high funding (lasting retail long demand) sits at its own norm and is not in the signal.
- Costs: smooth 8-hourly steps; estimate 0.03 to 0.08 a year (0.08 to 0.20 over DEV). Funding: probably a net
  receiver.
- Relation to earlier trials, lessons and rounds: the closest of the three to the calibration's carry family
  (ucal_xs_carry reads funding_mean too), and different from it in three ways that are the hypothesis: it ranks the
  CHANGE against the coin's own norm (the family takes the level), over 14 against 42 days (the family 1 to 10 days
  of level), with capped rank weights (the family is linear, so extreme rates dominate it). LESSONS 13 and 15 say
  what happens to the family in no-skill worlds; that is why H9 must earn on price (S8), be cheap (S9) and survive
  its twin (S10). gen000_funding_carry: LESSONS 3. The same relation to LESSONS 16, 17, 21 and 26 as H8.
- What I remember that could bias it: as H8, plus the clamp formula and the 4-hour intervals of 2023 and 2024 (in
  VAL a funding_mean window on a 4-hour coin spans 7 and 21 days instead of 14 and 42). Nothing shaped the rule
  beyond the clamp, which is a rule of the exchange.
- Falsifier. DEV: S1 to S10 (a wrong DEV sign drops it). Counted (VAL), only after the KP-017 measurement: as H8.
  Named risks: G7; coverage loss from a missing settlement (a name drops out for up to 42 days); a book that is
  small for long stretches (S1's avg gross shows it on DEV).
- DEV exploration (at most 6 runs): default (42, 126, 0.1); then (34, 101, 0.08) and (50, 151, 0.12); then, if it
  is the FIRST of H8 and H9, gen002_diag_stale_funding_shock (S7, k = 720 hours), gen002_diag_twin_funding_shock
  (S10, m = 14 days) and gen002_diag_acf_funding_shock (S6, k = 621 hours).

## H10. gen002_unrewarded_premium

- Family carry. Kind portfolio. Unit top30. Dollar neutral, gross 1. A daily series.
- Rule: for each coin in play, p = the median of its last n = 14 daily premiums (bd as in H8), r = its 14-day log
  return. Each day the cross-section of p is regressed on the cross-section of r (both demeaned; beta = cs_mean(x
  y) / cs_mean(x x)); e = p - beta x r is the premium that the coin's own recent move does not explain, uncorrelated
  with that move across coins by construction. Weight: minus the cross-sectional rank of e, demeaned, scaled to
  gross 1.
- Program (default pre-registered; strategies/gen002_unrewarded_premium.omr):

      n = param(14, 11, 17)          # days: the premium median and the return window
      bd = (daily(close) - daily(index_close)) / daily(index_close)
      p = median(bd, n)
      r = logret(daily(close), n)
      x = cs_demean(r)
      y = cs_demean(p)
      beta = cs_mean(x * y) / cs_mean(x * x)
      e = y - beta * x
      signal = cs_scale(cs_demean(-cs_rank(e)))

  1 param (integer; G5 values 11 to 17, never 14), 0 jitterable literals, 36 nodes, lookback 455 h.
- Hypothesis: a coin whose perp premium over the last two weeks is high for the return it has delivered
  underperforms the rest of the unit over the following weeks; a coin whose premium is low for its return
  outperforms.
- Mechanism: leverage that the price has not rewarded. Longs who keep paying a premium (and so funding) for a coin
  that has not moved as much as such a premium usually comes with are losing money to carry with nothing to show;
  they give up, are stopped out or liquidated, and their selling and the arbitrageurs' unwinding push the price down,
  while the short side collects their funding. A coin with a low premium for its return has rallied on spot demand
  (buyers who did not need leverage, more often informed or long-term) or has perp shorts paying against a move that
  went against them (squeeze fuel). The cross-sectional fit removes the part of the premium that simply follows the
  price, so the book is neither a momentum nor a reversal book over the 14 days: it holds the leverage, not the move.
- Who pays, why, what the receiver bears: as in H8; here the payers are the frustrated side (longs paying for
  exposure that has not paid them; shorts paying against a rally). Why they persist: the disposition to hold losing
  positions and keep paying their carry (Shefrin and Statman 1985), and the scarcity of capital willing to take the
  other side of a crowded perp.
- What its stale copies hold: month-old premium-versus-return gaps, which have resolved (positions closed,
  liquidated or rewarded) if the mechanism works over weeks. The lasting part (coins whose premium is structurally
  high for their return) is held by the copies as much as by the book and earns no timing credit; it is also why
  H10 is the most exposed of the three to the speed limit, and why S6, which counts that lasting part, may drop it
  where the gate would not.
- Costs: daily; the 14-day return changes every day, and through beta x r so does e. Estimate 0.06 to 0.12 a year
  (0.15 to 0.30 over DEV): the most likely of the three to fail S9.
- Relation to earlier trials, lessons and rounds: the first program in this project to combine the basis with a
  price input. Its construction (a cross-sectional regression slope recomputed every bar, the residual ranked with
  the contrarian sign) is round 1's H4 (gen002_absorbed_flow) applied to the premium instead of taker flow; H4 lost
  with the contrarian sign (LESSONS 17), which argues against H10 on DEV. Being orthogonal to the coin's own 14-day
  move answers LESSONS 16, 21, 23 and 26: DEV's continuation of recent moves cannot carry it through its screen,
  which is a conservative use of what is known about DEV, not a fit to it.
- What I remember that could bias it: no crypto result on the premium net of the return that I can recall. The
  neutralisation was chosen knowing that DEV rewarded continuation (LESSONS 16 to 26) and that recent losers carried
  higher funding on DEV; it removes the return-explained part, which makes DEV less flattering for a book short high
  premium, not more. From VAL as for H8 (FTT: a deeply negative premium with a deeply negative return; where it lands
  depends on the fit, and I do not know). Nothing I remember argues clearly for H10.
- Falsifier. DEV: S1 to S9 (a wrong DEV sign drops it). Counted (VAL), only after the KP-017 measurement: as H8.
  Named risks: S6 (the lasting per-name part) and S9 (costs); G7.
- DEV exploration (at most 5 runs): default n = 14; then n = 11 and n = 17; then gen002_diag_stale_unrewarded_premium
  (S7, k = 30 daily rows); then gen002_diag_acf_unrewarded_premium (S6, k = 26 daily rows).

---

## DEV-only diagnostics, round 3 (never to be submitted; each file's hypothesis line says so)

- Stale copies (S7; a technique new in this version, the coordinator's ruling is asked for below):
  strategies/gen002_diag_stale_premium_shock.omr, gen002_diag_stale_funding_shock.omr and
  gen002_diag_stale_unrewarded_premium.omr. Each computes w, the hypothesis's own weight row at its defaults (same
  text, same param ranges), and sets `signal = cs_demean(lag(w, k))`, k = 30 days (param(30, 24, 36) daily rows for
  H8 and H10; param(720, 576, 864) hours for H9, whose weights are an hourly-grid series). lag(w, k) is known only
  where w was known on all k + 1 rows, so the copy holds only names in play now whose weight was known all along
  since (close to G6's "tradable now and in play at the lagged row", a little stricter); cs_demean re-centres it to
  net zero across those names (G6 re-centres each book to the net of its own row); there is no gross rescaling (G6
  has none) other than the kernel's scale-down above gross 1, which H9's copy needs as H9 does. Its Sharpe is read
  against the default's; its other numbers mean nothing. The copy starts trading 30 days after the book. Limits: one
  copy at one lag over DEV against G6's 20 copies over VAL; the book in the comparison is the full book, not
  restricted to the copy's names.
- Price-neutral twins (S10; also new): strategies/gen002_diag_twin_premium_shock.omr and
  gen002_diag_twin_funding_shock.omr. Each takes s = cs_rank(shock) of the hypothesis at its defaults, regresses it
  across coins on x = the demeaned m-day log return (m = param(14, 11, 17), the hypothesis's recent window), and
  holds minus the residual: `signal = cs_scale(cs_demean(beta * x - s))` for H8 and `signal = size *
  cs_demean(beta * x - s)` for H9, beta = cs_mean(x s) / cs_mean(x x). For H9 the coins tied at a shock of 0 then
  carry small positions set by their return, which is what the fit needs to have no linear exposure to it.
- D-ACF (S6), as in versions 1 and 2 (`signal = c * w * lag(w, k)`, c = param(20, 10, 30), so that the positions are
  large against the engine's 0.01 band; R = avg net / avg gross = sum w w' / sum |w| |w'|):
  strategies/gen002_diag_acf_premium_shock.omr and gen002_diag_acf_unrewarded_premium.omr (daily series, k =
  param(26, 20, 32) daily rows), gen002_diag_acf_funding_shock.omr (hourly grid, k = param(621, 496, 746) hours;
  |w| <= 0.1, so |c w w'| <= 0.2).

## Run order and budget (round 3, decided before any run)

| order | run | runs only if |
|---|---|---|
| 1 | H8 default (a = 14, b = 42) | - |
| 2 | H9 default (a = 42, b = 126, size = 0.1) | - |
| 3 | H10 default (n = 14) | - |
| 4, 5 | H8 corners (a = 11, b = 34), then (a = 17, b = 50) | run 1 passed S1, S2, S4, S5, S8 and S9; run 5 only if run 4 passed S3 |
| 6, 7 | H9 corners (34, 101, 0.08), then (50, 151, 0.12) | run 2 passed S1, S2, S4, S5, S8 and S9; run 7 only if run 6 passed S3 |
| 8, 9 | H10 n = 11, then n = 17 | run 3 passed S1, S2, S4, S5, S8 and S9; run 9 only if run 8 passed S3 |
| 10, 11, 12 | stale copy (S7), then twin (S10), then D-ACF (S6), of the FIRST of H8 and H9 | it passed S1 to S5, S8 and S9; each run only if the one before passed its item |
| 13, 14 | stale copy (S7), then D-ACF (S6), of H10 | H10 passed S1 to S5, S8 and S9; run 14 only if run 13 passed S7 |

The FIRST of H8 and H9: if only one of them passed S1 to S5, S8 and S9, that one; if both did, the one with the
higher MINIMUM DEV Sharpe over its default and its two corners (robustness, not the peak; a tie goes to H8). The
other gets no diagnostic run and is not recommended.

Command form (from the project root, venv Python): `python -m omr.sandbox strategies/gen002_premium_shock.omr` and
`python -m omr.sandbox strategies/gen002_premium_shock.omr --set a=11 --set b=34`; full stage 1 on every run.

Planned: at most 14 sandbox runs. Reserve: 3 runs for an honest restatement after a stage-1 rejection the parse
check cannot see (the activity floor or a self-check; the constant probe already ran with the parse check), each a
recorded amendment of one of the forms the playbook lists in section 4, never a change of logic or of a default.
Cap for this round: 17 (the instruction allows 20); generation 2 would then have used at most 28 of 60. Every run
goes into the log, including runs that fail.

Logged per run: DEV Sharpe, PSR(0), total return, maxDD, direction changes, avg gross, avg net, costs, funding paid
(sign kept: negative = received), rebalances, liquidated, the per-year rows, the number of symbols ever in the
unit, the lookback; for a D-ACF the ratio R; for a stale copy or a twin its Sharpe against the default's. Stage 2
appends the run log (columns: # | program | params (non-default only) | DEV Sharpe | DEV dir. changes | avg gross |
avg net | costs | funding paid | total return | years + (of printed) | note), any amendments, the screen outcome per
hypothesis and the recommendation AFTER the last line of this version, so that this version stays an unchanged
prefix of the file.

## Selection rule (round 3)

- A hypothesis is eligible only if it passes every screen item that applies to it: S1 to S10 for H8 and H9, S1 to
  S9 for H10.
- At most one of H8 and H9 (one mechanism, two measurements): only the FIRST of them is screened to the end, and
  only it can be recommended.
- At most TWO programs are recommended: none; one of H8 and H9; H10; or one of H8 and H9 together with H10. If H8
  and H10 are both recommended, the coordinator should know that both read the same daily premium snapshots, so
  their books may be correlated (H10 is orthogonal to the coins' 14-day returns and H8 is not); H9 and H10 read
  different inputs.
- Each recommendation reads "eligible, subject to the KP-017 measurement": by the coordinator's ruling of 2026-11-24,
  a counted submission of a program reading funding8h, funding_mean, mark_close or index_close (all three here) also
  needs the coordinator's KP-017 measurement of how G6 behaves for funding-driven books. That measurement is not the
  researcher's to make. The coordinator's source read (playbook section 5) and the declared defaults, unchanged,
  apply as always.
- None eligible means none recommended; that is a result and is recorded as one.
- DEV Sharpe is a liveness check, not a ranking beyond these rules. The DEV-only diagnostics (gen002_diag_*) are
  never submitted.

## Notes for the coordinator (round 3, written with the plan)

- Rulings asked for: the stale copies (S7) and the price-neutral twins (S10) are DEV-only measurements of a new
  kind, alongside the D-ACF. If either is not allowed, its item is removed by an amendment written before run 1, the
  claim it would have measured stays unmeasured on DEV, and the planned runs fall by 2 (stale copies) or 1 (twin).
- For the source read (playbook section 5): (close - index_close) / index_close is the SIGNAL input of H8 and H10
  (ranked; in H10 also regressed across coins on the return), not a constant, threshold or scale; it multiplies
  nothing and is compared with nothing. H9's size is a plain per-name size (section H9). H10's beta, and the twins'
  beta, are cross-sectional regression slopes recomputed at every row, as in round 1's H4.
- The parse check's OK lines include the constant probe (omr.lang.parse_file runs it). The activity floor and the
  self-checks remain for the sandbox.
- What I found ambiguous, or what stopped an idea I would have liked to test:
  (a) The language cannot average an hourly expression into a daily or weekly bar (KP-019), so the premium can be
      read only as bin-close snapshots or as an hourly rolling mean that re-ranks every hour. A daily mean premium,
      the measurement I wanted for H8 and H10, is out of reach; so is a "next settlement" signal from the hourly
      premium (hourly, and too costly anyway).
  (b) funding8h normalises the rate to 8 hours, but a funding_mean window counts settlements, so the same n spans
      half the hours on a 4-hour coin (VAL). A funding window in hours would need a time-based function.
  (c) G2 cannot be read on DEV: the sandbox prints only the net funding, so S8 is a proxy. Printing the gross
      funding paid and received separately would make it exact (a possible addition to KP-018).
  (d) The sandbox does not print how many names a book holds, so coverage lost to data holes (a name drops out for
      as long as its window holds a hole) is invisible on DEV while the unit keeps 10 or more names.
  (e) D-ACF overstates the gate's statistic by about a third for rank weights even with no lasting per-name part,
      and more for a level-based book such as H10 (S6). The instruction allows reusing or tightening the earlier
      screens, so S6 stays at 0.40; the gate's own statistic on DEV (KP-018) would settle it.
  (f) Ideas stopped: open interest and long/short ratios, the natural crowding measures, are not research data
      (STATE.md); a funding-versus-return residual on SETTLED funding was dropped because the clamp makes many coins
      tie, and the residual of a tied coin is minus beta times its return, which would turn that book into a momentum
      or reversal book in calm periods (H10 uses the premium for that reason); a plain funding-level carry was not
      registered because it holds the same coins month after month (the speed limit, and no timing credit for a
      lasting tilt), and it is the calibration's own no-skill family.
  (g) Whether index_close bars are complete enough for a 42-day median of daily snapshots is a property of the data
      that this session may not look at; the only DEV sign of a problem would be the unit falling below 10 names.

Pre-registration (version 3): 2026-11-24T00:37:53Z; no round-3 sandbox run has been made.

## Notes for the coordinator (round 3): coordinator's rulings, received 2026-11-24 before round 3's run 1

Received after version 3 was committed and pushed unchanged as afb835b (PLAN.md 126,151 bytes, sha256
132f6f4b404381e0...; the first 80,097 bytes, versions 1 and 2, verified unchanged) and before round 3's run 1;
recorded here, 2026-11-24 about 08:40 UTC, before any round-3 sandbox run. Everything from here on is APPENDED to
version 3: the 126,151 bytes committed as afb835b stay an unchanged prefix, so the run log, the screen outcome, the
DEV observations and the recommendation follow below.
(1) The stale copies (S7) and the price-neutral twins (S10) are ALLOWED as DEV-only measurements, like the D-ACF.
Their runs count toward the cap, they are never submitted, and both items stay as written; each is reported as a DEV
reading, not as a proof. (2) The coordinator has read the source of H8, H9 and H10 (playbook section 5): nothing to
change; H9's `size` is accepted as a declared per-name size. (3) The researcher's reading of the funding parts of
omr/datasets.py and omr/interp.py and of a few constants is accepted (code, not data), as the plan states it. (4) A
recommendation reads "eligible, subject to the KP-017 measurement"; the coordinator runs that measurement only if a
candidate is eligible. (5) Notes (b), (c) and (d) (a funding window in hours; the sandbox printing gross funding paid
and received, and the number of names held) will be filed with KP-018 and KP-019 for the human; they are not to be
worked around.
Run conditions given with the rulings: one run at a time, full stage 1, the kernel's memory estimate checked before
every run (wait up to 20 minutes for "fits now True", else stop), each output saved as ASCII to the scratch folder;
a kernel_fault or a refusal the plan does not cover stops the round.

## Sandbox run log (round 3), filled in during stage 2

(Appended below version 3 and the rulings above, so that the file committed as afb835b stays an unchanged prefix.
Every run is listed; run numbers follow the order table of version 3, and numbers not listed were not due under its
conditions.)

| # | program | params (non-default only) | DEV Sharpe | DEV dir. changes | avg gross | avg net | costs | funding paid | total return | years + (of printed) | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | H8 gen002_premium_shock | (default a=14, b=42) | 0.823 | 4723 | 0.867 | 0.000 | 0.5081 | -0.1434 (received) | 0.475 | 3 of 3 (2020 0.260 SR 1.958; 2021 0.009 SR 0.159; 2022 0.160 SR 1.161) | PSR(0) 0.912, maxDD 0.332, rebalances 1085, liquidated False, 75 symbols, lookback 1253 h, 100.8 s. Fails S4 (0.475 - 0.5081 = -0.033) and S9 (0.5081 > 0.25); H8 DROPPED, runs 4 and 5 not made |
| 2 | H9 gen002_funding_shock | (default a=42, b=126, size=0.1) | 1.197 | 3803 | 0.853 | 0.000 | 0.4447 | -0.2821 (received) | 0.734 | 2 of 3 (2020 0.193 SR 1.467; 2021 0.657 SR 2.403; 2022 -0.123 SR -0.829) | PSR(0) 0.956, maxDD 0.249, rebalances 1975, liquidated False, 75 symbols, lookback 1216 h, 70.0 s. Passes S1, S2, S4 (0.289), S5, S8 (0.452); fails S9 (0.4447 > 0.25); H9 DROPPED, runs 6 and 7 not made |
| 3 | H10 gen002_unrewarded_premium | (default n=14) | 0.980 | 4068 | 0.867 | 0.000 | 0.4497 | -0.2975 (received) | 0.564 | 3 of 3 (2020 0.157 SR 1.101; 2021 0.313 SR 1.216; 2022 0.029 SR 0.383) | PSR(0) 0.941, maxDD 0.246, rebalances 1090, liquidated False, 75 symbols, lookback 455 h, 81.3 s. Passes S1, S2, S4 (0.114), S5, S8 (0.267); fails S9 (0.4497 > 0.25); H10 DROPPED, runs 8 and 9 not made |

No default passed S1, S2, S4, S5, S8 and S9 together, so by the order table no corner (runs 4 to 9), no stale copy,
no twin and no D-ACF (runs 10 to 14) was due; none was run. Total sandbox runs made in round 3: 3 (of the 14 planned
and the cap of 17); none from the reserve; no stage-1 rejection, no kernel fault, no refusal. Every run: full stage 1
(25 truncation cuts), exit 0, nothing on stderr, 70.0 to 100.8 s, one at a time. Before every run the kernel's memory
estimate printed "fits now True" (estimates 0.91, 0.82 and 0.93 GiB; wanted free 1.36, 1.23 and 1.39 GiB; free 1.99,
2.26 and 1.88 GiB). The benchmark line printed by every run (equal-weight long of the in-play members): DEV Sharpe
0.619, maxDD 0.847, as in rounds 1 and 2. ledger/sandbox_log.jsonl now has 32 rows (29 + 3); `omr.ledger verify` OK,
all six chains; `omr.kernel_lock verify` OK, sealed.

## Amendments (round 3), stage 2

(none: no program text, param, default, screen item or run condition was changed)

## Screen outcome per hypothesis (round 3; stage 2, DEV, read from the run log above)

| H | S1 (PASS; X >= 30; G >= 0.5; L False) | S2 (S >= 0.6, registered sign) | S3 (corners) | S4 (T - C > 0) | S5 (years +) | S6 (D-ACF R <= 0.40) | S7 (stale < 0.5 S) | S8 (T - abs(F) > 0) | S9 (C <= 0.25) | S10 (twin >= 0.5 S) | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| H8 gen002_premium_shock | pass (PASS; 4723; 0.867; False) | pass (0.823) | not run | FAIL (0.475 - 0.5081 = -0.033) | pass (3 of 3) | not run | not run | pass (0.475 - 0.1434 = 0.332) | FAIL (0.5081) | not run | DROPPED |
| H9 gen002_funding_shock | pass (PASS; 3803; 0.853; False) | pass (1.197) | not run | pass (0.734 - 0.4447 = 0.289) | pass (2 of 3: 2020, 2021) | not run | not run | pass (0.734 - 0.2821 = 0.452) | FAIL (0.4447) | not run | DROPPED |
| H10 gen002_unrewarded_premium | pass (PASS; 4068; 0.867; False) | pass (0.980) | not run | pass (0.564 - 0.4497 = 0.114) | pass (3 of 3) | not run | not run | pass (0.564 - 0.2975 = 0.267) | FAIL (0.4497) | n/a | DROPPED |

Against each pre-registered DEV falsifier:
- H8: falsified on DEV by its screen. The sign was the registered one (DEV Sharpe 0.823), but the book paid 0.508 of
  equity in costs over DEV, more than its total return of 0.475 (S4), and far above the ceiling of 0.25 (S9).
- H9: falsified on DEV by its screen. It met S1, S2, S4, S5 and S8 at its default (DEV Sharpe 1.197, 2022H1
  negative), and failed the cost ceiling S9 (0.445 > 0.25).
- H10: falsified on DEV by its screen. It met S1, S2, S4, S5 and S8 at its default (DEV Sharpe 0.980, positive in
  all three years), and failed the cost ceiling S9 (0.450 > 0.25).
- Not measured for any of them: the G5 corners (S3), the stale copies (S7), the price-neutral twins (S10) and the
  speed-limit diagnostics (S6). Whether these books' DEV returns were timing returns, leverage information or DEV's
  continuation of recent moves was therefore not read.

## DEV observations (round 3; NOT hypotheses, never to be submitted from this plan)

- All three defaults had the registered (contrarian) sign and DEV Sharpe 0.82 to 1.20, and all three were net
  RECEIVERS of funding: 0.143 (H8), 0.282 (H9) and 0.298 (H10) of equity over DEV, about 0.06 to 0.12 a year, which
  is 30 to 53% of their total returns. With all of that net funding taken out (S8) each stayed positive (0.332, 0.452,
  0.267). A rough additive split (compounding ignored) puts their price P&L before costs and funding at about 0.84,
  0.90 and 0.72 of equity over DEV. These are DEV readings at one default each. The readings that would have told a
  timing or leverage edge from DEV's known continuation (S7, S10) were not due, and the disclosures of version 3
  named that confound (on DEV recent losers carried higher funding); nothing here is evidence for the hypotheses.
- Costs were two to five times the plan's estimates: 0.508, 0.445 and 0.450 of equity over DEV (912 days), about
  0.18 to 0.20 a year, against estimates of 0.10 to 0.25, 0.08 to 0.20 and 0.15 to 0.30 over DEV. That is above every
  weekly book of rounds 1 and 2 (0.137 to 0.231) and above round 2's residual-momentum books (0.31 to 0.38). H8 and
  H10 change their targets once a day, yet rebalanced 1,085 and 1,090 times in 912 days; H9, whose funding means move
  by 1/42 of a step at each settlement, rebalanced 1,975 times. Direction changes were 3,803 to 4,723, against 1,635
  to 2,849 for the books of rounds 1 and 2. The cause is NOT measured. Candidates: rank weights move whenever two
  closely bunched values cross, so an input that moves slowly can still re-rank often (medians of daily snapshots
  whose cross-sectional spread is small; many coins bunched near the default funding rate); H10's residual also moves
  with a 14-day return that changes every day. The plan's arguments that a median is sticky and that 1/42 steps are
  smooth did not translate into low turnover.
- Per year: H9 lost in 2022H1 (-0.123, Sharpe -0.83); H8 was flat in 2021 (0.009); H10 was positive in all three
  years. H9's size cap did not shrink the book much (avg gross 0.853, against 0.867 for the two cs_scale books), so
  ties at the default funding were not dominant on DEV.
- DEV is now partly spent for these inputs: the author has seen that contrarian funding and premium books had
  positive DEV Sharpe before costs and that their costs, not their sign, stopped them. A later plan that registers a
  slower or cheaper version of H8, H9 or H10 must say it was written after this result; its DEV numbers would then not
  be evidence, and only its counted VAL run, after the KP-017 measurement, could test it.
- WEAK: one DEV period, one default each, one researcher session; nothing here is a parameter recommendation.

## Recommendation (round 3)

NONE. By the pre-registered selection rule a hypothesis is eligible only if it passes every screen item that applies
to it. Each default failed the cost ceiling S9 (costs 0.508, 0.445 and 0.450 of equity over DEV against 0.25), and H8
also failed S4; by the run order a hypothesis whose default fails S9 is dropped with nothing else run for it. No
program from version 3 is recommended for a counted submission, so the KP-017 measurement is not needed for this
round. The DEV-only diagnostics (gen002_diag_*) are never to be submitted.

---

# Generation 2 - PLAN, version 4 (round 4, pre-registered 2026-11-24 before any round-4 sandbox run)

Researcher session for generation 2, round 4, stage 1 (read, think, pre-register). Unit: top30. A fresh session:
rounds 1 to 3 are known to it only through the files listed below. The date in the heading is local time
(+08:00); the UTC time is in the last line of this version.

- Kernel: semantic 5ea66b0fb79ca267d3c8de22d203976aab3bca5634b22e026b13687c69eb2687 (39 files), text
  1366fb8fd0b6976839a3e6b16e40c402291c0154bb8ccfeae24bcd6848c72924 (35 files) (`python -m omr.status`: kernel OK
  bcc4b1aa255b4679, sealed). Sealed G6 thresholds: core 0.10, top30 0.10. Data research_hash 28d9084a8c5c7659...,
  validated, snapshot_end 2026-11-18 10:00 UTC.
- Ledger when this was written: M = 5 counted trials (generation 0: 4, generation 1: 1, generation 2: 0 of 5), N
  4.86, rho 0.035, Tier 1: 0, pool 0 of 5, last census none, one uncounted stage-1 rejection (generation 0).
  `omr.kernel_lock verify` OK (sealed, core 0.1, top30 0.1); `omr.ledger verify` OK, all six chains (trials 10
  rows, stage1_log 1, kernel_history 10, calibration_log 4, sandbox_log 32, val_access_log 22). Sandbox runs used
  in generation 2 so far: 14 of 60 (rounds 1 to 3: 4, 7 and 3).
- Read: RESEARCH_PLAYBOOK.md (all, with section 4b), LANGUAGE.md (all; sections 5, 6 and 10 for funding8h,
  mark_close, index_close, the timeframes and the cs_* functions), CONSTITUTION.md sections 4 to 7 and 13,
  LESSONS.md (all 29), generations/gen002/REPORT.md (all three rounds), this file from the heading of version 3
  to its end (version 3, its rulings, run log, screen outcome, DEV observations and recommendation; versions 1
  and 2 only through the report), KERNEL_PROPOSALS.md entry KP-017 only, STATE.md, the trial rows of
  `omr.ledger summary`, `omr.status`; the programs strategies/gen002_premium_shock.omr, gen002_funding_shock.omr,
  gen002_unrewarded_premium.omr and round 3's diagnostics gen002_diag_stale_*, gen002_diag_twin_* and
  gen002_diag_acf_{premium_shock, funding_shock, unrewarded_premium}.omr. Kernel source read only to learn how
  the tool behaves: omr/engine.py (the universe core: holdings drift with prices; a held name whose bar is
  missing is closed at its last usable close with costs; funding on the drifted position at each settlement
  open; a rebalance trades EVERY name to target once ANY name is more than 0.01 off, and costs the traded
  notional x 12.5 bps), omr/sandbox.py (what it prints), omr/lang.py (window and timeframe checks: a cs_* keeps
  its input's timeframe, an expression mixing two timeframes is hourly; the lookback rules). Also read for the
  same purpose, beyond the three files the brief named, and stated here for that reason: omr/windows.py (the
  rolling kernels: a rolling median sorts every window, so its cost grows with the window; this decided between
  hourly and 4-hourly premium snapshots for H12). Code, not data or results.
- Scratch computations, no market data, nothing in them is evidence about markets: synthetic panels of 30 coins
  (a slow AR(1) premium state per coin plus snapshot noise; and a clamped-funding world on an 8-hour grid), used
  only to compare the turnover and the 26-day weight correlation of round 3's forms with the round-4 forms, run
  through the engine's rule (0.01 band, every name traded, prices drifting 4% a day per coin). The snapshot
  noise was set so that round 3's H8 form reproduces about the turnover that round 3 measured on DEV (a cost
  reading, not a return reading). Scripts in the session scratch folder gen002r4/ (turnover_model.py to
  turnover_model8.py).
- Not opened: anything under data/, ledger/returns/, ledger/trials/, _build/, audits/, and every calibration
  file. No VAL number exists for any program below. No round-4 sandbox run has been made.
- Versions 1 to 3 above, with round 3's rulings, run log, screen outcome, observations and recommendation, are
  unchanged byte for byte (the first 136,056 bytes of this file, sha256 19c8ebcbb7c6262a...). No earlier program
  file was changed; round 4 adds eight new files (two candidates and six DEV-only diagnostics).

Two hypotheses, numbered on from version 3, ONE per mechanism of round 3. Both are market neutral (dollar
neutral) and contrarian on crowded leverage, with round 3's signs; neither is a continuation or momentum rule on
prices. Both read KP-017 inputs (H11 funding8h, H12 index_close), so a counted submission of either also needs
the coordinator's KP-017 measurement. Neither uses hour or weekday.

| H | program | mechanism (round 3) | input | what is new | family |
|---|---|---|---|---|---|
| H11 | gen002_averaged_funding_shock | H8/H9: a change in crowded leverage unwinds | settled funding: the 10-day time mean of funding8h minus its 28-day time mean | the cross-sectional rank is averaged over 16 days before it is held; windows in hours, not settlements | carry |
| H12 | gen002_averaged_unrewarded_shift | H10: leverage the price has not rewarded unwinds | the perp premium at every 4-hour close: its 10-day median minus the coin's own 28-day median, net of a cross-sectional fit on the 10-day return | the rank of the residual is averaged over 16 days; the premium is measured against the coin's own norm; six snapshots a day | carry |

## Both hypotheses were written AFTER round 3's DEV result

- Known to this session before any line of this version was written (round 3's run log, LESSONS 27 to 29): the
  three round-3 books had the registered contrarian sign on DEV (H8 0.823, H9 1.197, H10 0.980 after costs),
  received 0.143 to 0.298 of equity in funding, stayed positive with it removed, and cost 0.45 to 0.51 of equity
  over DEV (912 days), failing the ceiling of 0.25 (H8 also failed S4). Per year: H8 3 of 3 (2021 0.009), H9 2 of
  3 (2022H1 -0.123), H10 3 of 3 (2022H1 0.029). Their corners, stale copies, twins and D-ACF were never run.
- H11 and H12 average round 3's rank signals over time. Their DEV Sharpe is therefore NOT evidence: its sign and
  rough size follow from round 3's (the same signals, about six days staler on average, charged less). S2 is a
  liveness check only. The screen rests on readings nobody has taken: the costs of the new forms under the same
  ceiling (S9, tightened), the costs paid twice (S4), the costs paid twice with the funding removed (S8,
  tightened), the G5 corners (S3), the per-year item (S5), the stale copy (S7), the price-neutral twin (S10, now
  for both) and the speed limit (S6, D-ACF).
- DEV is partly spent for these inputs (LESSONS 27): only a counted VAL run, after the KP-017 measurement, could
  test either rule.

## Why round 3's books traded so much: the engine's rule, in numbers

- The engine (omr/engine.py) marks every holding to the open, charges funding on the drifted position, and
  rebalances when ANY name's target differs from its drifted weight by more than 0.01; it then trades EVERY name
  to target and pays 12.5 bps on the traded notional. So the costs are 0.00125 x (the total variation of the
  targets + the drift traded back + names closed and reopened). The 0.01 band decides WHEN a change is traded,
  hardly whether: with 30 names some name is over the band almost every day, so a target change that does not
  reverse within a day is traded at once.
- Round 3 measured H8 at costs 0.508 with avg gross 0.867 over 912 days: 406 x equity traded, 0.445 a day, about
  0.51 a day per unit of gross (H9 0.46, H10 0.455). A rank book of 30 names that is re-drawn independently trades
  about 4/3 of its gross; H8 traded about 0.38 of a full re-draw every day. The drift traded back is roughly the
  sum of |w| x the name's move against the book, about 0.03 a day per unit of gross for coins moving 3 to 4% a day
  against each other; the rest, about 0.45 a day, is the daily change of the rank targets. For rank weights the
  trade of a day is about (4/3) x sqrt(1 - rho), rho the correlation of today's rank vector with yesterday's;
  0.45 means rho near 0.89. An input that is 89% the same as yesterday still trades a third of the book every day,
  because the trade grows with the SQUARE ROOT of the change. This is LESSONS 28's candidate cause (closely
  bunched values re-rank) put in the engine's arithmetic; it is still not a measurement of the cause.
- Smoothing the INPUT (round 3's medians of daily snapshots, its 14-day funding means) did not help, because the
  rank of a smooth but bunched input still jitters (LESSONS 24, 28).

## The engineering answer: average the RANK over days, after the cross-section

- Both books hold s = sma(cs_rank(.), m), the cross-sectional rank averaged over the last m rows (16 days),
  re-centred (H12 also scaled to gross 1). From one row to the next s changes by (rank_t - rank_t-m) / m: at
  most 2/m of the rank range per name per row, whatever the input does, and a rank swap that reverses within the
  average cancels inside it instead of being traded twice.
- What it buys depends on how much of the daily re-ranking is jitter. For the lasting part of a ranking the
  turnover per unit of gross falls like 1/m; for jitter only like 1/sqrt(m), because averaging also shrinks a
  jittery book's gross, which is scaled back (H12) or leaves the book smaller (H11). In the synthetic worlds, run
  through the engine's rule, in which round 3's H8 form trades 0.29 to 0.42 a day per unit of gross (DEV: 0.51
  with everything the model leaves out): the round-4 form (a 10-day measurement, a 28-day norm, a 16-day rank
  average) traded 0.41 to 0.50 of round 3's form; its 0.8 corner 0.52 to 0.62 and its 1.2 corner 0.34 to 0.41;
  the same windows WITHOUT the rank average traded 1.19 to 1.29 times round 3's form, so the averaging is what
  does the work. In the clamped-funding worlds H11's form traded 0.39 to 0.79 of round 3's H9 form, the lower end
  where the settlement-to-settlement jitter is large enough to bring H9's form near the turnover it had on DEV.
- A first draft (a 7-day measurement and a 14-day average, the same 28-day norm) traded 0.47 to 0.55 of round
  3's form in the same worlds; it was replaced before any run by the longest average that the lookback leaves
  (below) and a measurement window of about a third of the norm, as in round 3 (14 of 42). In the same worlds the
  final form kept 0.67 to 0.89 of round 3's correlation with the current crowding state (the draft 0.78 to
  0.89). Both choices were made on synthetic panels only.
- Estimates (round 3's measured costs x those ratios; avg gross about 0.85): H12 about 0.18 to 0.24 of equity
  over DEV (round 3's H10: 0.450); H11 about 0.17 to 0.26 (H9: 0.445). Rebalances: about one a day, each small
  (round 3: 1.2 a day for the daily books, 2.2 for H9). The ceiling of 0.25 may still bind, H11 the more likely
  to meet it: that is the reading this round exists to take, and it is not moved.
- Tools not chosen, with reasons (each is an honest way to move a book less):
  - ema of the rank: it remembers 5n rows (lookback the diagnostics need), and for the same mean delay it trades
    about 40% more than sma (each row moves it by 2/(n+1) of the gap between the new rank and the average; sma
    moves by 1/n of the gap between the newest and the oldest rank).
  - median of the rank: its step has no bound (it jumps between order statistics of a jittering series).
  - hold bands on the rank: they need a re-synchronising horizon h (lookback the stale copy cannot spare), two
    thresholds as params, and an equal-weight book in which every name's weight changes whenever the count of
    names held changes; with jittery ranks the bands are crossed often unless they are wide.
  - weekly snapshots: weekly(close) and weekly(index_close) give ONE premium snapshot a week (one hour's premium,
    with up to six hours of index staleness, as a week's measurement), and weekly(funding8h) does not exist;
    sampling a derived series weekly is KP-019, not worked around.
  - flatter or coarser shapes: sign() trades a full weight at every crossing of the middle, where bunched names
    jitter most; a clipped or tanh shape needs a scale (cross-sectional, which jitters with the bunch, or a
    declared constant whose effect depends on a data scale this session may not look at), and for normally
    spread values clipping at one standard deviation saves only about 15% of the turnover per unit of gross.
- Lookback and the diagnostics. The averaging costs lookback, and the stale copy (+864 hours at its high bound)
  and the D-ACF (+746 or +752) need room after it, under 2,160 hours. So the norm is 28 days (round 3: 42) and
  the rank average 16 days, the longest whole number of days that leaves the stale copy inside the limit; the
  measurement window is 10 days (round 3: 14). Lookbacks: H11 1,283 hours, H12 1,277; stale copies 2,147 and
  2,141; D-ACF 2,029 and 2,029; twins 1,283 and 1,277. The centres of mass stay near round 3's: the recent part
  about 12.5 days back (5 days of the 10-day window plus 7.5 of the average; round 3's H8 and H9 at 7), the norm
  about 21.5 (round 3: 20.5 to 21).
- Speed limit. Both books rank a CHANGE against the coin's own norm, so a coin's lasting level drops out. In the
  synthetic worlds such books are ANTI-correlated with themselves one lag step back (R26 between -0.30 and -0.48
  at the defaults, -0.12 to -0.55 at the corners: the norm of today covers the recent window of 26 days ago), far
  from G6's limit of 0.5 and from S6's 0.40. A level book (H10's form) read R26 of 0.29 to 0.34 when averaged with
  no lasting per-coin part, 0.41 to 0.46 with a modest one and 0.60 to 0.65 with a large one (a few names held at
  the extremes for months put R near 0.4 on their own, since R removes no per-name mean): averaging a level book
  would have put the D-ACF at or over its limit. That is one of the two reasons why H12 measures the premium
  against the coin's own norm.
- G7: in effect four of the five later buckets must be positive (2020 is short). G8 runs the rule on ranks 31 to
  60: ranks and rates mean the same there.
- Literals and G5: no program has a jitterable literal (n_literals 0). The DEV corners (S3) are the two corners
  at which every param sits at the same G5 end; mixed corners are not read.
- No calendar sampling and no hour or weekday indicator (KP-019 is not worked around).

## Disclosures that apply to both hypotheses

- The author model has read this market's history through DEV, VAL and the vault, and this session has read
  rounds 1 to 3's DEV numbers. No rule names a date, a coin, a price level or a remembered event; every tunable
  number is a declared param. That does not remove hindsight from the CHOICE of ideas and forms (KP-010); each
  hypothesis states what I remember that could bias it.
- What I remember about funding and premiums in VAL (July 2022 to June 2025): funding low and often negative in
  the 2022H2 bear (after LUNA, Three Arrows, Celsius, FTX), low through most of 2023 with many coins at the
  default rate, very high in February and March 2024 and again in November and December 2024, lower in 2025 with
  negative stretches; Binance moved many contracts to 4-hour funding and changed caps in 2023 and 2024; Ethena's
  basis trade compressed BTC and ETH funding in 2024; single-coin collapses with deeply negative funding (FTT,
  November 2022); memecoins entering the top of the volume ranking in 2023 and 2024 with high funding during runs
  that lasted weeks before collapsing. I do not remember the result of any cross-sectional funding or basis book
  in VAL.
- What I remember about DEV (2020 to June 2022): DeFi tokens in 2020; the 2021 manias (DOGE in spring 2021, gaming
  and metaverse coins late in 2021) with very high funding for weeks while prices kept rising, then crashes (May
  2021 above all); LUNA in May 2022, whose funding and premium fell deeply negative as it went to zero.
- The clamp: I remember Binance's funding as the average premium index plus clamp(0.01% - premium, -0.05%,
  +0.05%) per 8 hours, so a coin whose premium stays inside a band of about -0.04% to +0.06% pays exactly the
  default 0.01%. That is why H11 keeps H9's per-name size (ties) and why H12 is built on the premium. A rule of
  the exchange, not a memory of prices, not verified on data.
- The literature I remember (as in version 3): Schmeling, Schrimpf and Todorov ("Crypto carry", BIS, about 2023);
  He, Manela, Ross and von Wachter ("Fundamentals of perpetual futures", about 2022); Christin, Routledge, Soska
  and Zetlin-Jones ("The crypto carry trade", about 2022). Mostly time-series results on BTC and ETH, not a top30
  cross-section; they favour the contrarian direction of both hypotheses, a bias I name.
- What this project's DEV results say (known to this session): residual moves continued rather than reversed
  (LESSONS 16, 21, 23, 26); on DEV recent losers carried higher funding than recent winners (round 2's H6 received
  funding, H1 and H7 paid it), so a book short rising funding or premium may ride DEV's continuation for a reason
  that is not its hypothesis. S10, now for both books, exists for that.
- Window lengths (10, 28 and 16 days) come from the lookback left by the diagnostics, from round 3's ratio of the
  recent window to the norm, and from the synthetic turnover comparison, not from a remembered cycle length. The
  engineering choices (rank averaging, 4-hour snapshots, hours instead of settlements) come from the engine's
  rule, the language and round 3's cost readings; the hours also from the remembered 4-hour intervals of VAL,
  named above.
- At most TWO programs are recommended whatever DEV says, one per mechanism, each only as "eligible, subject to
  the KP-017 measurement". LESSONS 12 and 14: a true Sharpe-1.5 book passes Tier 1 only 68 to 82% of the time in
  this unit, G6 does not protect against luck, and every counted trial raises M forever.
- Defaults are fixed now and are never changed after a run. Neighbours are a robustness check (G5 corners), not a
  search; a better neighbour does not move the default. No sign is ever flipped.

## DEV screen (round 4), fixed now, before any number

A hypothesis is eligible only if it passes every item, in the sandbox (full stage 1, no --quick). Every item of
version 3 is kept at least as strict: S8 and S9 are tightened, S10 is extended to H12, nothing is loosened. The
sandbox lines each item reads: "stage 1: ... direction changes (DEV) X ... -> PASS"; "DEV Sharpe S ... total T
..."; "rebalances ... avg gross G  avg net N  funding paid F  costs C  liquidated L"; the per-year rows. Numbers
are taken as printed.

- S1 at its default: stage 1 PASS as written (parse, constant probe, truncation and start-cut self-checks), X >=
  30, G >= 0.5, and L False. (Version 3's S1.)
- S2 at its default: S >= 0.6 with the registered sign. A negative S drops the hypothesis; no sign is flipped.
  Liveness only, not evidence (above).
- S3 at both G5 corners: S > 0 AND T - C > 0 at each. (Version 3's S3.) H11: (a, b, m, size) = (192, 538, 307,
  0.08) and (288, 806, 461, 0.12). H12: (a, b, m) = (48, 134, 77) and (72, 202, 115).
- S4 at its default: T - C > 0 (a rough DEV reading of G4: still positive with the costs paid twice). (Version
  3's S4.)
- S5 at its default: the year's return > 0 in at least two of the three DEV years printed (2020, 2021, 2022).
  Version 3's S5, kept and NOT tightened, for a reason stated now: the per-year signs of the averaged forms follow
  largely from round 3's per-year rows (H9 lost 2022H1; H8 was flat in 2021), so a stricter per-year item chosen
  now would be chosen knowing whom it stops (it would very likely stop H11, whose parent lost 2022H1, and not
  H12). Round 2's H6 got a strict item when only its mirror's rows were known; here the parents' own rows are
  known, and keeping version 3's item unchanged is the choice that uses them least.
- S6 speed limit: the D-ACF ratio R = N / G of the hypothesis's diagnostic (3 decimals each) <= 0.40. (Version
  3's S6, not loosened.) R removes no per-name mean; both books remove the coin's lasting level by construction.
- S7 timing: the DEV Sharpe of the hypothesis's stale copy (gen002_diag_stale_*: its own default weights from 30
  days earlier, held now on the names in play now, re-centred to net zero, not rescaled; it pays its own costs, as
  in G6) is below 0.5 x S. (Version 3's S7.) A limit stated now: for these change-based books the weights of 30
  days ago are expected to be partly OPPOSITE to today's (synthetic R26 below zero), so a pass is weak evidence of
  timing, while a failure is strong evidence against it. A copy at about 55 days, where G6's copies are close to
  independent, would be more informative but does not fit the 90-day lookback (notes, (a)).
- S8 funding and costs (tightened): at its default, T - |F| - C > 0. The DEV return stays positive with the whole
  net funding flow taken out AND the costs paid a second time. With T = P - C + (funding received), this asks
  that the price P&L P exceed twice the costs for a net receiver: a price claim that survives a rough reading of
  G2 and G4 together. Version 3 asked T - |F| > 0. Why: KP-017's finding concerns books dominated by their costs,
  and round 3's books took 30 to 53% of their return from funding.
- S9 cost ceiling (tightened): at its default, C <= 0.25 AND C <= 0.29 x G. The first clause is version 3's
  ceiling unchanged. The second holds the same cost per unit of gross (0.25 / 0.867, the gross of version 3's
  books), so that no book meets the ceiling by holding less: H11's per-name size form can stay below gross 1 when
  its averaged ranks are weak or tied.
- S10 price-neutral twin (H11 and, new, H12): the DEV Sharpe of the hypothesis's twin (gen002_diag_twin_*: on each
  row the hypothesis's rank regressed across coins on each coin's 26-day log return of 4-hour closes, the
  residual averaged over the same m and held with the registered sign, as the hypothesis holds its own) is at
  least 0.5 x S. Why for H12 too: it is orthogonal to the coin's 10-day return on each row, but its 16-day average
  is orthogonal to nothing; 26 days is the span of the measurement plus the average, for both books.

Order and economy: the defaults run first. If a default fails S1, S2, S4, S5, S8 or S9, the hypothesis is dropped
and nothing else is run for it. Otherwise its corners run in order and stop at the first that fails S3. The
diagnostics run only for a hypothesis that passed S1 to S5, S8 and S9, one at a time, each only if the one before
passed its item: the stale copy (S7), then the twin (S10), then the D-ACF (S6).

---

## H11. gen002_averaged_funding_shock

- Family carry. Kind portfolio. Unit top30. Dollar neutral; a name's weight is size x its centred averaged rank
  (about 0.1 at most); the kernel scales the book down to gross 1 when its gross exceeds 1. An hourly-grid
  series: the time means of funding8h slide every hour.
- Rule: for each coin in play, f = funding8h (the latest settled rate as an 8-hour rate, held until the next
  settlement). shock = sma(f, 240) - sma(f, 672): its time mean over the last 10 days minus over the last 28.
  s = the cross-sectional rank of shock averaged over the last 384 hours (16 days). Weight = size x minus s,
  re-centred. Short the coins whose funding rose most above their own four-week norm in the last weeks, long
  those whose funding fell most below it.
- Program (default pre-registered; strategies/gen002_averaged_funding_shock.omr):

      a = param(240, 192, 288)        # hours in the recent funding mean (10 days)
      b = param(672, 537, 807)        # hours in the coin's own norm (28 days)
      m = param(384, 307, 461)        # hours over which the cross-sectional rank is averaged (16 days)
      size = param(0.1, 0.08, 0.12)   # weight per unit of centred averaged rank
      shock = sma(funding8h, a) - sma(funding8h, b)
      s = sma(cs_rank(shock), m)
      signal = size * cs_demean(-s)

  4 params (a, b and m integers: G5 values a = 192 to 288, b = 538 to 806, m = 307 to 461, never the defaults
  themselves; size 0.08 to 0.12), 0 jitterable literals, 13 nodes, lookback 1,283 h.
- Mechanism: round 3's H8/H9 (a change in crowded leverage unwinds), measured as H9 measured it, on settled
  funding; who pays, why they keep paying and what the receiver bears are as written for H8 and H9 in version 3.
  In short: leveraged perp longs arriving faster than arbitrage capital absorbs them raise the premium and so the
  funding; when the leverage unwinds (stop-outs, liquidations, funding eating margin) the price pressure
  reverses, and the short side collects the funding meanwhile; a fall below the norm marks perp shorts arriving
  or longs leaving, the mirror.
- What is new and why it trades less:
  (1) The RANK, not the input, is averaged over 16 days: the target moves by at most 2/384 of the rank range per
      name per hour, and swaps among coins bunched near the default rate (the clamp) cancel inside the average.
      Round 3's H9 re-ranked at every settlement and traded 0.46 a day per unit of gross.
  (2) Windows in hours of funding8h instead of counts of settlements (funding_mean): a coin on 4-hour funding
      gets the same 10- and 28-day windows as an 8-hour coin (H9's 42 settlements would have covered 7 days on a
      4-hour coin; version 3, note (b)).
  (3) Shorter windows (10 and 28 days instead of 14 and 42), to leave lookback for the average, the stale copy
      and the D-ACF; the centres of mass stay near H9's (above).
  (4) Kept from H9: size x centred rank (no cs_scale), because tied coins would hand a cs_scale book's whole
      gross to the few coins that differ.
  Estimate: costs about 0.17 to 0.26 of equity over DEV (H9: 0.445); about one small rebalance a day (H9: 2.2).
  Funding: probably a net receiver, as H9 (0.282 received).
- Why funding and not the premium (H8) for this mechanism: (i) H12 carries H10's mechanism on the premium measured
  against the coin's own norm; were H11 the premium shock, H12 would be its price-neutral twin and the two
  candidates one claim; (ii) settled funding is the exchange's own average of the premium over the whole
  interval, so it carries no snapshot noise; (iii) it is what a held position pays. Against it, stated plainly:
  H9 is the measurement that had the higher DEV Sharpe in round 3 (1.197 against H8's 0.823), so the choice can
  look like choosing the DEV winner; the reason is (i). H9 also lost in 2022H1, and S5 is not tightened (above).
- What its stale copies hold: funding shocks of a month and more ago. With a 10-day window against a 28-day norm
  and a 16-day average, the copy at 26 to 30 days holds partly the opposite of today's book; copies beyond about
  45 days hold unrelated shocks. If crowding unwinds within weeks they earn about nothing on price and collect
  less funding; if crowding regimes last for months they earn too, and H11 fails S7 or G6, as it should.
- Relation to earlier trials, lessons and rounds: H9 (gen002_funding_shock) averaged and re-windowed, with the
  same input, sign and per-name size. It differs from the calibration's carry family (minus the linear funding
  LEVEL over 1 to 10 days, re-ranked at every settlement; LESSONS 13 and 15) in ranking a change against the
  coin's own norm and in the 16-day rank average, and from gen000_funding_carry (c30a93ef73a529bd, LESSONS 3).
  Answers LESSONS 27 to 29 (costs) and 24 and 28 (the rank of a smooth input jitters). The same relation to LESSONS
  16, 17, 21 and 26 as H8 and H9 (DEV's continuation argues against a contrarian book and, through funding, for
  it for the wrong reason: S10).
- What I remember that could bias it: the general disclosures; the clamp (why size is kept); the 4-hour intervals
  of 2023 and 2024 (why hours: a VAL memory; it makes the windows equal across coins and periods and encodes no
  price outcome); for DEV 2022H1, LUNA, whose funding fell deeply negative as it went to zero, which H11's long
  side would have held (H9 lost 2022H1); for VAL, many coins at the default rate in 2023 (H11 is small then, by
  the size form kept from H9), the high-funding runs of 2024 (against the short side during the runs, for it
  after), FTT (against the long side). There is no crash filter, no cap beyond the size, no coin and no date.
- Falsifier. DEV (not submitted): S1 to S10 (a wrong DEV sign drops it, never flipped). Counted (VAL), only after
  the KP-017 measurement: falsified if G1 (PSR(0) < 0.90), G2 (funding-stress Sharpe <= 0), G4 (2x costs <= 0), G6
  (p > 0.10, or the speed limit), G8 (next30 Sharpe <= 0), or any other Tier-1 gate fails. Named risks: S9 (the
  average may not cut enough), S5 (2022H1), G7, coverage loss from a missing settlement (a name drops out for up
  to 44 days), a single-coin collapse on the long side.
- DEV exploration (at most 6 runs): default (240, 672, 384, 0.1); then (192, 538, 307, 0.08) and (288, 806, 461,
  0.12); then the stale copy gen002_diag_stale_averaged_funding_shock (S7, k = 720 hours), the twin
  gen002_diag_twin_averaged_funding_shock (S10, q = 156 4-hour rows) and the D-ACF
  gen002_diag_acf_averaged_funding_shock (S6, k = 621 hours).

## H12. gen002_averaged_unrewarded_shift

- Family carry. Kind portfolio. Unit top30. Dollar neutral, gross 1. A 4-hour series (bins from 00:00 UTC, each
  visible in the hour its bin closes, traded at the next open).
- Rule: for each coin in play, bd = (close - index_close) / index_close at every 4-hour close (the basis as
  LANGUAGE.md section 5 defines it: the SIGNAL input, ranked and regressed, not a constant, threshold or scale).
  p = the median of the last 60 snapshots (10 days) minus the median of the last 168 (28 days): the premium
  against the coin's own norm. r = the coin's 10-day log return on 4-hour closes. Each 4-hour row the
  cross-section of p is regressed on the cross-section of r (both demeaned; beta = cs_mean(x y) / cs_mean(x x));
  e = p - beta x r is the premium shift that the coin's own move does not explain. s = the cross-sectional rank of
  e averaged over the last 96 rows (16 days). Weight: minus s, re-centred, scaled to gross 1.
- Program (default pre-registered; strategies/gen002_averaged_unrewarded_shift.omr):

      a = param(60, 48, 72)           # 4-hour snapshots in the recent premium median and the return window (10 days)
      b = param(168, 134, 202)        # 4-hour snapshots in the coin's own premium norm (28 days)
      m = param(96, 76, 116)          # 4-hour rows over which the cross-sectional rank is averaged (16 days)
      bd = (h4(close) - h4(index_close)) / h4(index_close)
      p = median(bd, a) - median(bd, b)
      r = logret(h4(close), a)
      x = cs_demean(r)
      y = cs_demean(p)
      beta = cs_mean(x * y) / cs_mean(x * x)
      e = y - beta * x
      s = sma(cs_rank(e), m)
      signal = cs_scale(cs_demean(-s))

  3 params (integers; G5 values a = 48 to 72, b = 134 to 202, m = 77 to 115, never the defaults), 0 jitterable
  literals, 41 nodes, lookback 1,277 h.
- Mechanism: round 3's H10 (leverage that the price has not rewarded unwinds); who pays, why, and what the receiver
  bears as in version 3. Longs who keep paying a rising premium (and so funding) for a coin that has not moved as
  much as such a premium usually comes with give up, are stopped out or liquidated, and their exit pushes the
  price down while the short side collects their funding; a premium that fell by more than the move explains marks
  a spot-led rally or perp shorts paying against a move that went against them (squeeze fuel). The fit removes
  the part of the shift that simply follows the price, so on each row the book is neither a momentum nor a
  reversal book over the 10 days: it holds the leverage, not the move.
- What is new and why:
  (1) The rank of the residual is averaged over 16 days (as H11). Round 3's H10 traded 0.455 a day per unit of
      gross: its daily median premium and its daily-changing 14-day return re-ranked the residual every day.
  (2) The premium is measured against the coin's OWN 28-day norm before the fit (H10 used its level). Two reasons,
      both stated before any run: a coin's lasting premium (index make-up, borrow scarcity, a standing clientele
      of hedgers) is not the crowding the mechanism is about; and a lasting per-coin tilt is held by G6's stale
      copies as much as by the book, earns no timing credit (the KP-017 case of a book that collects a premium
      without timing) and would put the D-ACF at or over S6's limit by itself (above). The cost of this choice: H12
      is a faster signal than H10 (a change, not a level), which works against S9.
  (3) Six snapshots a day (4-hour closes) instead of one: 60 and 168 snapshots in the two medians (H10: one
      median of 14 daily snapshots; H8: 14 and 42), so one stale or bad snapshot (an index row up to six hours
      old) weighs 1/60, not 1/14, and the medians move less from sampling. This is for measurement quality; in
      the noisiest synthetic worlds halving the snapshot noise lowered the turnover by only about 5%. A 4-hour
      rather than an hourly bin keeps the rolling medians (which sort every window) cheap enough for the
      self-checks.
  (4) 10 days for the recent median and the return (one window for both, as H10's 14) and 28 for the norm:
      lookback (above).
  Estimate: costs about 0.18 to 0.24 of equity over DEV (H10: 0.450); about one small rebalance a day. Funding:
  probably a net receiver, as H10 (0.298 received).
- Relation to round 3, and why it is not H11's twin: H12 is close to round 3's DEV-only twin of H8
  (gen002_diag_twin_premium_shock, never run): that twin regressed the RANK of H8's daily premium shock (14
  against 42 days) on the 14-day return; H12 regresses the shift itself (10 against 28 days, 4-hour snapshots) on
  the 10-day return, ranks the residual and averages the rank. That is why H11 carries the other mechanism on
  FUNDING: the two candidates share no input, and neither is the other's twin. Like H10, H12 is round 1's H4
  construction (a cross-sectional fit recomputed every row, the residual ranked with the contrarian sign) on
  another input; H4 lost with the contrarian sign (LESSONS 17), which argues against H12 on DEV.
- What its stale copies hold: premium shifts of a month and more ago, which have resolved if the mechanism works
  over weeks; the copy at 26 to 30 days holds partly the opposite of today's book.
- What I remember that could bias it: the general disclosures; no crypto result on the premium net of the return
  that I can recall; the coin's own norm was chosen knowing that an averaged level book would be slow (the speed
  limit) and that a lasting tilt is the KP-017 case; I do not know whether it helps or hurts on DEV or VAL. The
  fit was chosen knowing that DEV rewarded continuation (it removes the part explained by the 10-day return). From
  DEV: the 2021 manias (premiums rose with prices; the fit attributes part of that to the move); LUNA (premium and
  return collapsed together; where it lands depends on the fit). From VAL: as for H11. Nothing I remember argues
  clearly for H12.
- Falsifier. DEV: S1 to S10 (a wrong DEV sign drops it, never flipped). Counted (VAL), only after the KP-017
  measurement: as H11. Named risks: S9 (a faster signal than H10), S10, G7, coverage loss from index gaps (a hole
  in the klines or a gap of more than six hours in the index bars takes a name out for up to 44 days).
- DEV exploration (at most 6 runs): default (60, 168, 96); then (48, 134, 77) and (72, 202, 115); then
  gen002_diag_stale_averaged_unrewarded_shift (S7, k = 180 4-hour rows), gen002_diag_twin_averaged_unrewarded_shift
  (S10, q = 156 4-hour rows) and gen002_diag_acf_averaged_unrewarded_shift (S6, k = 156 4-hour rows).

---

## DEV-only diagnostics, round 4 (never to be submitted; each file's hypothesis line says so)

- Stale copies (S7), of the kind allowed in round 3: strategies/gen002_diag_stale_averaged_funding_shock.omr (w
  hourly, k = param(720, 576, 864) hours) and gen002_diag_stale_averaged_unrewarded_shift.omr (w a 4-hour series,
  k = param(180, 144, 216) rows = 30 days). Each computes w, the hypothesis's own weight row at its defaults (same
  text, same param ranges), and sets signal = cs_demean(lag(w, k)); its Sharpe is read against the default's, its
  other numbers mean nothing. Limits as in version 3, and the one stated under S7.
- Price-neutral twins (S10), of the kind allowed in round 3, both with q = param(156, 124, 188) 4-hour rows (26
  days): u = the hypothesis's cs_rank at its defaults; xq = cs_demean(logret(h4(close), q)); bq = cs_mean(xq u) /
  cs_mean(xq xq); s = sma(u - bq xq, m); s held exactly as the hypothesis holds its own (H11: size x
  cs_demean(-s); H12: cs_scale(cs_demean(-s))). So the twin is the book minus its averaged return-aligned part,
  with the same average and so about the same turnover (round 3's twins would have traded more than their books
  had they been run). For H11, u is hourly and xq a 4-hour series; they meet on the hourly grid.
- D-ACF (S6), as in versions 1 to 3 (signal = c x w x lag(w, k), c = param(20, 10, 30); R = avg net / avg gross
  = sum w w' / sum |w| |w'|): gen002_diag_acf_averaged_funding_shock.omr (k = param(621, 496, 746) hours) and
  gen002_diag_acf_averaged_unrewarded_shift.omr (k = param(156, 124, 188) 4-hour rows = 26 days).
- Parse check (grammar, params, units, the constant probe; no market data): all eight new files OK; lookbacks
  1,283 / 1,277 (candidates), 2,147 / 2,141 (stale copies), 1,283 / 1,277 (twins), 2,029 / 2,029 (D-ACF).

## Run order and budget (round 4, decided before any run)

| order | run | runs only if |
|---|---|---|
| 1 | H11 default (240, 672, 384, 0.1) | - |
| 2 | H12 default (60, 168, 96) | - |
| 3, 4 | H11 corners (192, 538, 307, 0.08), then (288, 806, 461, 0.12) | run 1 passed S1, S2, S4, S5, S8 and S9; run 4 only if run 3 passed S3 |
| 5, 6 | H12 corners (48, 134, 77), then (72, 202, 115) | run 2 passed S1, S2, S4, S5, S8 and S9; run 6 only if run 5 passed S3 |
| 7, 8, 9 | H11 stale copy (S7), then twin (S10), then D-ACF (S6) | H11 passed S1 to S5, S8 and S9; each run only if the one before passed its item |
| 10, 11, 12 | H12 stale copy (S7), then twin (S10), then D-ACF (S6) | H12 passed S1 to S5, S8 and S9; each run only if the one before passed its item |

Command form (from the project root, venv Python): `python -m omr.sandbox
strategies/gen002_averaged_funding_shock.omr` and `python -m omr.sandbox strategies/gen002_averaged_funding_shock.omr
--set a=192 --set b=538 --set m=307 --set size=0.08`; full stage 1 on every run. H11 slides two hourly means
(up to 807 rows) and averages hourly ranks over up to 461 rows; H12 sorts two rolling medians of up to 202 rows
per name: the runs may take longer than round 3's (70 to 101 s).

Planned: at most 12 sandbox runs. Reserve: 3 runs for an honest restatement after a stage-1 rejection the parse
check cannot see (the activity floor or a self-check; the constant probe already ran with the parse check), each
a recorded amendment of one of the forms the playbook lists in section 4, never a change of logic or of a
default. Cap for this round: 15 (the instruction allows 20); generation 2 would then have used at most 29 of 60.
Every run goes into the log, including runs that fail.

Logged per run: DEV Sharpe, PSR(0), total return, maxDD, direction changes, avg gross, avg net, costs, funding
paid (sign kept: negative = received), rebalances, liquidated, the per-year rows, the number of symbols ever in
the unit, the lookback; for a default also C / G (S9) and T - |F| - C (S8); for a D-ACF the ratio R; for a stale
copy or a twin its Sharpe against the default's. Stage 2 appends the run log (columns: # | program | params
(non-default only) | DEV Sharpe | DEV dir. changes | avg gross | avg net | costs | C/G | funding paid | total
return | years + (of printed) | note), any amendments, the screen outcome per hypothesis and the recommendation
AFTER the last line of this version, so that this version stays an unchanged prefix of the file.

## Selection rule (round 4)

- A hypothesis is eligible only if it passes every screen item: S1 to S10.
- At most TWO programs are recommended: none; H11; H12; or both (one per mechanism). If both are recommended, the
  coordinator should know that both respond to crowding (funding is the clamped average of the premium), so their
  books may be correlated, although they read different inputs and H12 is orthogonal to each coin's 10-day return
  on each row while H11 is not.
- Each recommendation reads "eligible, subject to the KP-017 measurement": both programs read funding8h or
  index_close, and by the coordinator's ruling of 2026-11-24 a counted submission of such a program also needs the
  coordinator's KP-017 measurement of how G6 behaves for funding-driven books. That measurement is not the
  researcher's to make. The coordinator's source read (playbook section 5) and the declared defaults, unchanged,
  apply as always.
- None eligible means none recommended; that is a result and is recorded as one.
- DEV Sharpe is a liveness check, not a ranking beyond these rules. The DEV-only diagnostics (gen002_diag_*) are
  never submitted.

## Notes for the coordinator (round 4, written with the plan)

- Rulings asked for: none new. The stale copies, twins and D-ACF are the kinds of DEV-only measurement allowed in
  round 3 (S10 is extended to H12, which only adds a requirement).
- For the source read (playbook section 5): H11's size is H9's plain per-name size (accepted in round 3), not a
  near-constant, threshold or scale, and used in no comparison. H12's (close - index_close) / index_close is the
  signal input (ranked and regressed), as in H8 and H10; beta (H12) and bq (twins) are cross-sectional regression
  slopes recomputed at every row, as in round 1's H4 and round 3's H10.
- The parse check's OK lines include the constant probe. The activity floor and the self-checks remain for the
  sandbox.
- What I found ambiguous, or what stopped a form I would have liked to use:
  (a) The 90-day lookback limit binds through the DEV-only diagnostics, not through the candidates (about 53
      days): the stale copy needs 36 more days at its high bound, so the norm is 28 days instead of round 3's 42
      and the rank average 16 days. For change-based books the stale copy at 30 days is weak (their weights 30
      days back are partly opposite); a copy at about 55 days, near-independent like most of G6's copies, would
      test timing better but needs 66 days at its high bound. A lookback allowance for DEV-only diagnostics, or
      the KP-018 sandbox readings, would settle both.
  (b) KP-019 again: sampling the averaged rank once a day or once a week would bound the turnover by
      construction; it is not available and is not worked around (no hour or weekday gating).
  (c) G6 and anti-correlated books: for a book whose weights are anti-correlated with its own weights 26 to 30
      days back, the first one or two of G6's 20 stale copies hold partly the opposite book and almost never do
      as well as a book that earns at all, so in effect the book is compared with 18 or 19 copies and p <= 0.10
      is a little easier to reach (about 2/19 instead of 2/21 under exchangeability). Small, but it concerns the
      gate's behaviour for exactly this kind of book; the KP-017 measurement could include one.
  (d) S8 and S9 are rough DEV readings of G2 and G4; the sandbox prints only the net funding (version 3, note
      (c), filed with KP-018).
  (e) The synthetic cost model was set to reproduce round 3's measured DEV turnover, so S9 is partly anticipated
      by design: the model was used to choose the averaging with margin and to reject a first draft, not to fit
      the ceiling, and the ceiling is not moved.
  (f) Forms stopped: an averaged level form of H10 (the D-ACF would read high from lasting names, and S6 is not
      loosened); a premium-shock H11 (it would make H12 its twin); linear weights in units of the default funding
      rate (a declared scale whose effect depends on data this session may not see); ema or hold bands
      (lookback); weekly snapshots of the premium (one hour a week as the measurement).

Pre-registration (version 4): 2026-11-24T09:25:04Z; no round-4 sandbox run has been made.
