# Generation 1 - PLAN (version 1, pre-registered 2026-11-19 before any generation-1 sandbox run)

Researcher session for generation 1. Inputs read: LANGUAGE.md, RESEARCH_PLAYBOOK.md, CONSTITUTION.md,
LESSONS.md, generations/gen000/PLAN.md and REPORT.md, strategies/gen000_*.omr, ledger/stage1_log.jsonl,
`python -m omr.status` (kernel semantic 7446278556aadd8f, sealed G6 0.10, M = 4, Tier 1: 0). No file
under data/, ledger/returns/ or ledger/trials/ was opened. No VAL number exists for any program below.

Five hypotheses, one per family (trend, relative, meanrev, volatility, flow); four of the five are
not trend-following. Every program is written below at its PRE-REGISTERED default. Exploration is DEV
only, with the sandbox, at most 6 runs per hypothesis for choosing params; every run goes into the
table at the bottom, including the values not chosen. Any change after the first run is an amendment
at the bottom of this file with its DEV-only reason.

## Disclosures that apply to every hypothesis

- The author model has read this market's history, including VAL and the vault. None of the rules
  below names a date, a price level, a remembered regime or a remembered event; every tunable number
  is a declared param or a plain literal (integers -10..10). That does not remove hindsight from the
  CHOICE of ideas (KP-010); only forward results can.
- Long-or-flat structure (H1, H3, H4, H5). Generation 0's REPORT states that holding BTC and ETH half
  each had a VAL Sharpe of 0.92. A long-or-flat rule therefore carries part of a drift whose VAL sign
  is already known to the author. This helps G1 only. It does not help G6: every circularly shifted
  copy of the weights carries the same average long exposure, so the timing permutation measures only
  WHEN the program is long. G6 is the gate that judges these four programs, and the coordinator should
  read their G1 in that light.
- Volatility sizing (H1, H4) is risk timing: with any positive drift, scaling exposure down when
  recent volatility is high lowers the variance of the actual run relative to shifted runs. That is a
  documented, legitimate form of timing (volatility-managed portfolios), but it is named here so that
  a G6 pass is not over-read as return prediction.
- Priority of the four long-or-flat programs: they are correlated with each other by construction
  (all long-biased). At most two of them will be recommended for counted submission whatever DEV says.

## Common DEV screen (decided now, before any number)

A candidate is recommended for counted submission only if, at its chosen defaults, in the sandbox:
1. it parses and passes the constant probe as written (or as restated by a recorded amendment);
2. DEV direction changes >= 30 (the floor is 20; the margin is for VAL's floor of 12 on 3 years);
3. DEV Sharpe > 0 at the chosen value AND at both neighbouring values tried (no isolated peak);
4. the chosen value is a round value from the pre-registered grid, not the DEV maximum by default;
   where the grid is flat the pre-registered default is kept.
DEV Sharpe is not ranked against other candidates beyond this screen; it is a liveness check.

---

## H1. gen001_tsmom_long_flat

- Family: trend. Kind: single.
- Rule: long, sized to a volatility target, when the close is above its close `n` days ago; flat
  otherwise. Never short.
- Program (defaults pre-registered):

      n = param(28, 14, 56)          # momentum lookback, daily bars
      vol_n = param(30, 15, 60)      # volatility lookback, daily bars
      target = param(0.5, 0.25, 1.0) # annualised volatility target
      d = daily(close)
      size = min2(1, target / realised_vol(d, vol_n))
      signal = where(ret(d, n) > 0, size, 0)

  3 params, 1 jitterable literal (the 1 in min2).
- Hypothesis: the sign of the trailing 4-week return predicts the next days' return of a crypto perp
  well enough that being long only after a positive 4-week return beats being long at shifted times.
- Mechanism: time-series momentum (slow diffusion of information, herding, leverage that builds
  gradually in up-moves and is cut abruptly in down-moves). Other side: early mean-reversion sellers in
  up-moves and dip buyers in down-moves; the program steps aside rather than taking the short side.
- Costs and funding: daily decisions on a 28-day return change state a few times a month at most;
  each change trades about 0.25-0.5 of equity per symbol at 7.5 bps. Funding is paid only while long;
  under the x1.5 funding stress the long periods must earn more than about 1.5 x the funding rate.
- Lesson answered: lessons 2 and 4 (gen-0 trend rules had positive DEV but failed G6; the symmetric
  rule paid to be short a drifting asset). This is a variation of trial 992b1aacbef67bb1's IDEA (trend
  plus volatility sizing) with a different signal (return sign, 28 days, not SMA-50) and no short side.
  Honest note: the gen-0 vol-target trend failed G6 at p 0.239; there is no evidence yet that removing
  the short side improves timing, only that it removes the cost of shorting drift.
- Falsifier: DEV Sharpe <= 0 or DEV direction changes < 30 (not submitted); in VAL, G6 p > 0.10, or G1,
  or G2 (funding stress), or G7.

## H2. gen001_relmom_pair

- Family: relative. Kind: portfolio (market-neutral by construction: +0.5 / -0.5).
- Rule: long the coin whose trailing `n`-day log return, in units of its own `n`-day volatility, is
  higher; short the other.
- Program (default pre-registered):

      n = param(21, 10, 42)          # lookback, daily bars
      d = daily(close)
      strength = logret(d, n) / realised_vol(d, n)
      signal = cs_rank(strength)

  1 param, 0 jitterable literals. cs_rank over two symbols is -1 / +1 (0 on a tie); the portfolio
  scaling turns that into -0.5 / +0.5.
- Hypothesis: within the BTC/ETH pair, the coin with the stronger risk-adjusted 3-week return keeps
  outperforming the other over the following days.
- Mechanism: cross-sectional momentum, documented for crypto at 1-4 week horizons: capital rotates
  between coins slowly (narratives, fund flows, leverage moving from one coin to the other). Dividing
  by each coin's own volatility stops the rule from simply picking the higher-beta coin whenever the
  market rises. Other side: relative-value traders who fade the spread.
- Costs and funding: a switch trades 2.0 of notional (15 bps of equity); funding largely cancels
  between a long and a short perp; drift rebalancing is small. Removes the market drift from the
  question entirely, so G1 must come from timing alone.
- Lesson answered: the brief's note that holding both coins earns a drift a strategy gets no credit
  for; lesson 4 (trend timing failed G6) - this asks whether RELATIVE trend has timing where absolute
  trend did not. New idea, no earlier trial.
- Falsifier: DEV Sharpe <= 0 or DEV direction changes < 30 (not submitted); in VAL, G1 or G6 or G4
  (2x costs), or G8 (the alt pairs disagree).

## H3. gen001_capitulation_long

- Family: meanrev. Kind: single. Long-or-flat, selective.
- Rule: when the `drop_n`-day return is more than 2 standard deviations below its own `look`-day
  history AND the mean of the last `fund_n` funding settlements is negative, go long and stay long for
  `hold_n` hours after the last such trigger; otherwise flat.
- Program (defaults pre-registered):

      drop_n = param(5, 3, 10)       # length of the drop, daily bars
      look = param(120, 60, 240)     # history the drop is measured against, daily bars
      fund_n = param(9, 6, 21)       # funding settlements (9 = 3 days)
      hold_n = param(240, 120, 480)  # hours held after the last trigger (240 = 10 days)
      d = daily(close)
      deep = zscore(ret(d, drop_n), look) < -2
      crowded_short = funding_mean(fund_n) < 0
      trigger = where(deep and crowded_short, 1, 0)
      signal = where(rmax(trigger, hold_n) > 0, 1, 0)

  4 params, 3 jitterable literals (2, and the two 1s). The trigger mixes a daily series with the
  hourly funding series, so it lives on the hourly grid and `hold_n` counts hours.
- Hypothesis: a multi-day drop that is extreme for the coin's own recent history, at a time when
  shorts are paying longs, is followed by a rebound over the next ten days.
- Mechanism: forced deleveraging. Liquidations and margin calls sell regardless of price and push it
  below where unforced holders value it; negative funding says the leveraged long side has been
  flushed and the short side is now the crowded, paying side. Other side: liquidated longs, forced
  sellers, and late shorts who pay funding and get squeezed.
- Costs and funding: few trades (each round trip 15 bps of the traded weight); while long with
  negative funding the program RECEIVES funding (halved under the stress, still not paid).
- Lesson answered: lesson 3 (the 4h RSI mean reversion lost in DEV with 311 direction changes). This
  is the opposite design: rare, large, selective entries, long only, and conditioned on a crowding
  measure instead of a price oscillator. Funding is used as a CROWDING condition, not as carry (the
  gen-0 carry rule lost in DEV and VAL).
- Falsifier: DEV direction changes < 30 or DEV Sharpe <= 0 (not submitted); in VAL, G1, G6, G7
  (gains concentrated in one bucket is the obvious risk of a rare-event rule), or G10 (fewer than 12
  VAL direction changes).

## H4. gen001_calm_long

- Family: volatility. Kind: single. Long-or-flat.
- Rule: long, sized to a volatility target, while short-term realised volatility is below long-term
  realised volatility; flat while short-term volatility is above it.
- Program (defaults pre-registered):

      fast = param(10, 5, 20)        # short volatility window, daily bars
      slow = param(60, 30, 120)      # long volatility window, daily bars
      target = param(0.5, 0.25, 1.0) # annualised volatility target
      d = daily(close)
      vf = realised_vol(d, fast)
      vs = realised_vol(d, slow)
      size = min2(1, target / vf)
      signal = where(vf < vs, size, 0)

  3 params, 1 jitterable literal.
- Hypothesis: a perp earns its drift mainly while its volatility is falling or below normal, and
  loses while volatility is rising above normal.
- Mechanism: volatility feedback and leverage. Rising volatility raises margin requirements,
  triggers risk-limit cuts by volatility-targeting holders and liquidations, which sell; falling
  volatility lets the same holders add exposure. Other side: holders forced to de-risk in turbulence
  (the program is out) and those adding in calm (the program is with them). Uses no price direction.
- Costs and funding: daily decisions; the volatility ratio is smoother than price, so few switches.
  Funding paid only while long.
- Lesson answered: lesson 2 (the only gen-0 survivor of the costs was the vol-sized rule). This keeps
  volatility as the ONLY input, to test whether volatility state times exposure without any trend.
- Falsifier: DEV direction changes < 30 or DEV Sharpe <= 0 (not submitted); in VAL, G6 (the sizing is
  risk timing; the on/off switch must add to it), G1, G2, G7.

## H5. gen001_taker_flow_long

- Family: flow. Kind: single. Long-or-flat.
- Rule: long while the share of aggressive (taker) buying in daily volume, averaged over the last
  `fast` days, is above its `slow`-day average; flat otherwise.
- Program (defaults pre-registered):

      fast = param(3, 2, 6)          # recent flow window, daily bars
      slow = param(30, 15, 60)       # normal flow window, daily bars
      share = daily(taker_buy_volume) / daily(volume)
      signal = where(sma(share, fast) > sma(share, slow), 1, 0)

  2 params, 1 jitterable literal. The taker-buy share is used as the SIGNAL (compared with its own
  trailing average), not as a constant, threshold or scale.
- Hypothesis: several days of above-normal aggressive buying predict positive returns over the
  following days.
- Mechanism: informed or determined buyers split their demand over days and pay the spread to get
  filled; passive sellers absorb it and reprice gradually, so the price impact of persistent order
  flow is not complete on the day it is seen. Other side: passive limit sellers and market makers who
  provide the liquidity and lean against it.
- Costs and funding: the 3-day average turns over often; each switch trades 0.5 of equity per
  symbol (3.75 bps of equity). DEV direction changes will show whether turnover is too high.
- Lesson answered: lesson 3 (non-trend signals lost to costs and in DEV); the brief's suggestion of
  flow fields. New idea, no earlier trial. Its correlation with price momentum is an open question;
  if DEV shows it only replicates H1 it will not be recommended.
- Falsifier: DEV Sharpe <= 0, or DEV direction changes so high that 2x costs would dominate (more
  than about 400), or fewer than 30 (not submitted); in VAL, G1, G4 (2x costs), G6.

---

## Exploration plan (DEV only, decided before any run)

Per hypothesis: run the default first. If it parses and is active, try the two round neighbours of
the main horizon param from this grid, keeping the others at their defaults:
- H1 n in {14, 28, 56}; if needed vol_n in {30, 60}.
- H2 n in {10, 21, 42}.
- H3 drop_n in {3, 5, 10}; if activity is too low, hold_n is not lengthened to manufacture activity -
  a too-rare trigger is a finding, recorded as such.
- H4 fast in {5, 10, 20} (slow 60).
- H5 fast in {2, 3, 5}; slow in {15, 30, 60}.
Budget: at most 6 runs per hypothesis for choosing params, at most 60 sandbox runs in total.

## Sandbox run log

(filled in as runs happen; every run, chosen or not)

Reference printed by every run: benchmark (long 1/K each) DEV Sharpe 0.925, maxDD 0.766.
"avg gross" for a single program is the sum over BTC and ETH of |signal| / 2.

| # | hypothesis | params (non-default only) | DEV Sharpe | DEV dir. changes | other | note |
|---|---|---|---|---|---|---|
| 1 | H1 tsmom_long_flat | (default n=28) | 1.740 | 116 | maxDD 0.289, avg gross 0.411, costs 0.129, 2022H1 SR -1.594 | CHOSEN (default kept) |
| 2 | H1 | n=14 | 1.720 | 183 | maxDD 0.324, costs 0.155 | neighbour, positive |
| 3 | H1 | n=56 | 1.308 | 58 | maxDD 0.347, costs 0.064 | neighbour, positive |
| 4 | H2 relmom_pair | (default n=21) | 0.735 | 142 | maxDD 0.269, costs 0.223, 2775 rebalances | default; fails screen 3 (see run 6) |
| 5 | H2 | n=10 | 0.738 | 232 | maxDD 0.239, costs 0.275 | neighbour, positive |
| 6 | H2 | n=42 | -0.293 | 98 | maxDD 0.522, 2020 and 2021 both negative | neighbour NEGATIVE: screen 3 fails |
| 7 | H3 capitulation_long | (default) | 0.462 | 16 | avg gross 0.056 | activity_dev (16 < 20) |
| 8 | H3 | drop_n=3 | 0.298 | 12 | avg gross 0.041 | activity_dev |
| 9 | H3 | drop_n=10 | 0.394 | 16 | avg gross 0.061 | activity_dev; trigger too rare on the whole grid |
| 10 | H4 calm_long | (default fast=10) | 1.280 | 149 | maxDD 0.467, avg gross 0.455, costs 0.197 | default kept |
| 11 | H4 | fast=5 | 0.950 | 293 | maxDD 0.590, costs 0.350 | neighbour, positive |
| 12 | H4 | fast=20 | 0.977 | 118 | maxDD 0.524, costs 0.108 | neighbour, positive |
| 13 | H5 taker_flow_long | (default fast=3) | 0.825 | 357 | maxDD 0.533, avg gross 0.511, costs 0.326 | below the benchmark while long half the time |
| 14 | H5 | fast=2 | 0.365 | 486 | maxDD 0.637, costs 0.318 | neighbour, positive |
| 15 | H5 | fast=5 | 0.951 | 264 | maxDD 0.502, costs 0.294 | neighbour, positive; about equal to the benchmark |
| 16 | control (A1) diag_volsized_long | (default vol_n=30) | 0.832 | 0 | maxDD 0.659, avg gross 0.668 | H1's control; activity_dev by design |
| 17 | control (A1) | vol_n=10 | 1.020 | 0 | maxDD 0.643, avg gross 0.696 | H4's control; activity_dev by design |
| 18 | H1 | vol_n=60 | 1.678 | 116 | maxDD 0.273, costs 0.105 | sizing-window robustness (plan grid); positive |

Total sandbox runs: 18 of 60. Per hypothesis: H1 4 (+1 control), H2 3, H3 3, H4 3 (+1 control), H5 3.
No program was rejected by the parser or the constant probe; the only stage-1 rejections were
`activity_dev` (H3 on its whole grid, and the control by design).

## Amendments

### A1 (after run 15): one DEV-only control, not a candidate

Reason (DEV only): H1, H4 and H5 all pass the formal screen, but H4's and H5's DEV Sharpes (0.95 to
1.28) are close to the long-both benchmark (0.925), and the long-or-flat disclosure above says G6
judges only WHEN they are long. Before choosing which long-or-flat programs to recommend, I want to
know how much of H1's and H4's DEV Sharpe is their volatility sizing alone. Control program
`strategies/gen001_diag_volsized_long.omr`: the same sizing, `min2(1, target / realised_vol(daily
close, vol_n))`, held long all the time (it has 0 direction changes, so it is rejected by
`activity_dev` and can never be a trial; the sandbox still prints its DEV Sharpe). Two runs:
vol_n=30 (H1's sizing) and vol_n=10 (H4's sizing). It will NOT be submitted and is not a hypothesis.
Read: if a program's DEV Sharpe is not clearly above its control's, its on/off switch shows no DEV
timing content and it is not recommended. H5 needs no control: its sizing is constant, so its control
is the printed benchmark (0.925), which it does not beat at any value tried.
These two runs count toward the 60-run limit and toward H1's and H4's 6-run limits.

### A2 (after run 18): DEV verdicts and the recommendation to the coordinator

No program text or default was changed after any run; every file in strategies/gen001_* is exactly as
pre-registered in version 1 (plus the A1 control, which is not a candidate).

| hypothesis | screen 1 parse/probe | screen 2 changes >= 30 | screen 3 neighbours > 0 | A1 control | verdict |
|---|---|---|---|---|---|
| H1 tsmom_long_flat | pass | pass (116) | pass (1.720, 1.308; vol_n=60 1.678) | 1.740 vs control 0.832: switch adds about +0.9 | RECOMMEND for counted submission at defaults |
| H2 relmom_pair | pass | pass (142) | FAIL (n=42 -0.293) | n/a | NOT recommended: isolated, falls over at 2x the lookback; also high drift-rebalancing cost (0.22 in DEV) |
| H3 capitulation_long | pass | FAIL (16; 12 and 16 on the grid) | n/a | n/a | NOT submittable: stage 1 would reject it (activity_dev). The trigger is too rare; not loosened to manufacture activity |
| H4 calm_long | pass | pass (149) | pass (0.950, 0.977) | 1.280 vs control 1.020 at the default only; both neighbours at or below the control | NOT recommended: the volatility switch shows little DEV timing beyond its sizing, and it is correlated with H1 |
| H5 taker_flow_long | pass | pass (357) | pass (0.365, 0.951) | constant sizing; control = benchmark 0.925, not beaten at any value | NOT recommended: no DEV timing content, highest DEV costs, fails the "only replicates drift" falsifier |

Recommendation: submit ONE program, gen001_tsmom_long_flat, at its declared defaults (n=28, vol_n=30,
target=0.5). Honest odds are modest: it is a trend rule, and both gen-0 trend rules had DEV Sharpes
above 1 and failed G6 in VAL (lessons 1 and 4); its DEV numbers are in-sample to the author's memory
of 2020-2022. Its G1 is helped by the known positive VAL drift (disclosure above); G6 and G7 are the
gates that decide it. `strategies/gen001_diag_volsized_long.omr` is a control and must never be
submitted.
