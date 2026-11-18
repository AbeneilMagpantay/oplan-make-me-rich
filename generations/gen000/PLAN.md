# Generation 0 - PLAN (pre-registered 2026-11-18, restated 2026-11-19 for the formula language and for locality; nothing has been scored: no VAL result exists)

Five fixed baselines, all kind "single" (the kernel trades each core perp, BTCUSDT and ETHUSDT,
alone on its own history, at weight = signal / 2). They are `.omr` programs (LANGUAGE.md) with the
rules and defaults of the pre-language Python strategies, except TWO RULES CHANGED BY THE KERNEL'S
LOCALITY RULE (FIX PASS 5, KP-012), decided before any result:
- gen000_donchian_ls: the position is the state machine re-run from flat over the last `horizon`
  daily bars (default 90, range 60..180) instead of an unbounded state machine;
- gen000_rsi_meanrev_ls: the RSI has finite memory (10 x period changes) and the position is the
  state machine re-run from flat over the last `horizon` 4h bars (default 84, range 60..180).
On the real DEV data these horizons never differ from an unbounded machine (a horizon of 60 or more
never binds), and both programs give the same weights as the Python versions on every DEV row where
they are known (they start later: one uniform warm-up). SMA cross and funding carry are bit-identical
to the Python versions; the vol-target trend differs by floating-point rounding only (at most
3.5e-15 in a weight). Params are fixed as written; no tuning. Each is evaluated exactly once on the
sealed kernel:

    python -m omr.evaluate strategies/<name>.omr --generation 0

Regions: DEV 2020-01-01 .. 2022-06-30 (uncounted), VAL 2022-07-01 .. 2025-06-30 (counted). Costs
7.5 bps per side, funding charged on the drifted position at each settlement, gross <= 1.
Liquidation is checked on MARK price (KP-001; last-price fallback only where a mark bar is
missing); a liquidated base run is a counted trial with final status `liquidated`. Tier 1 needs all
of G1-G8 and G10 (CONSTITUTION section 7), with the G6 threshold sealed by the calibration.

Activity rule (section 6 of the CONSTITUTION): a direction change is a decision bar where a
symbol's state sign(w) (0 when |w| <= 0.01) differs from the previous bar's. At least 20 in DEV
(stage 1, uncounted `activity_dev`) and at least 12 in VAL (gate G10). DEV counts on the real DEV
data (BTC + ETH, known before any VAL result): SMA cross 16 (8 + 8), Donchian 65 (34 + 31), RSI
mean-reversion 311, vol-target trend 92, funding carry 60. So gen000_sma_cross_ls, at its pre-registered defaults,
is expected to be rejected at stage 1 as `activity_dev` (uncounted; no VAL bar is read). That is
accepted as part of the instrument, not worked around by changing its params.

Common falsifier for every baseline: it fails at least one Tier-1 gate. A baseline that passes Tier 1
goes to the paper pool; that is "worth paper-trading", not "profitable".

## 1. gen000_sma_cross_ls (trend)

- Rule: `signal = sign(sma(daily(close), fast) - sma(daily(close), slow))`; fast=20 [5,60],
  slow=100 [50,250]. Daily bars are complete bars, visible from the 23:00 bar of their day.
- Hypothesis: crypto perps trend over weeks to months; being on the side of the medium-term trend
  earns more than the opposite side, net of costs and funding.
- Mechanism: slow diffusion of information, herding and leverage cycles. Other side: early
  mean-reversion traders, hedgers, and - when long in a bull market - the funding the long side pays.
- Falsified by: G1, G6, or a loss under funding stress (G2).

## 2. gen000_donchian_ls (trend)

- Rule: long when the daily close > highest high of the prior `entry` completed days; short when
  it is < the lowest low of the prior `entry`; a long exits to flat below the prior `exit`-day
  low, a short above the prior `exit`-day high; entries take priority (`hold(...)`).
  entry=20 [10,60], exit=10 [5,30].
- Hypothesis: range breakouts start moves that persist long enough to pay for false breakouts.
- Mechanism: stop-loss cascades and delayed participation. Other side: range traders fading the
  breakout.
- Locality: `horizon = param(90, 60, 180)`; `signal = hold(..., horizon)`.
- Falsified by: G1, G6, or G7 (profits concentrated in one bucket).

## 3. gen000_rsi_meanrev_ls (meanrev)

- Rule: on 4h bars, centred finite RSI r = (G - L) / (G + L) over the last 140 changes (Wilder
  weights, period 14), equal to (RSI - 50) / 50; state rebuilt over the last `horizon` = 84 bars. Long when r < -band,
  held until r > 0; short when r > band, held until r < 0; entries take priority. period=14 [7,28],
  band=0.4 [0.2,0.6] (= the Python band 20 RSI points, bounds 10..30).
- Hypothesis: short-horizon overreactions revert within days.
- Mechanism: liquidity provision against forced and impatient flow. Other side: traders who must
  trade now.
- Falsified by: G1, G4 (2x costs), G6.

## 4. gen000_voltarget_trend_ls (trend)

- Rule: direction = sign(daily close - SMA(ma_n)); size = min(1, target_vol / realised vol of the
  last vol_lookback daily log returns x sqrt(365)); signal = direction x size. ma_n=50 [20,150],
  vol_lookback=30 [10,90], target_vol=0.40 [0.2,0.8].
- Hypothesis: trend persistence plus volatility clustering; cutting size in high-volatility regimes
  improves risk-adjusted returns.
- Falsified by: G1 or G6; or G5 if the result depends on the exact vol target.

## 5. gen000_funding_carry (carry)

- Rule: f = mean of the last 21 funding settlements (8h-equivalent rates); -1 when f > 0.0003, +1
  when f < -0.0001, else flat. lookback=21 [6,90], hi=0.0003 [0.00015,0.001],
  lo=-0.0001 [-0.0005,0.0].
- Hypothesis: persistently high funding is a carry premium paid by crowded leveraged longs.
- Mechanism: demand for leveraged long exposure exceeds supply; the short side is paid to provide it.
- Falsified by: G1, G2 (funding stress), or the activity rules (flat most of the time at the
  0.0001 base rate).
