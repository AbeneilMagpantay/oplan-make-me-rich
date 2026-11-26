# Meta-review of the search, 2026-11-26 (generations 0 to 3; M = 6; no Tier 1)

Independent analyst, read-only. Read in full: LESSONS.md, STATE.md, RESEARCH_PLAYBOOK.md, KERNEL_PROPOSALS.md,
CONSTITUTION.md, LANGUAGE.md, omr/constants.py, the four REPORTs, the PLANs of generations 1 to 3 (gen 0's is
short and was read too). Run read-only: `omr.ledger summary`, `omr.status`, `omr.ledger verify` (OK, six chains).
Scripts in this folder read ledger/sandbox_log.jsonl (table.py) and only the `verdict` / `verdict_unit_only`
blocks of the two calibration artifacts (verdict.py). Not opened: data/, ledger/returns/, ledger/trials/.
"Estimate" marks my own arithmetic; every other number names its file. DEV = 2020-01-01 to 2022-06-30 = 912
days = 2.497 years; VAL = 1,096 days.

## 0. What matters most

1. The bar is about as high as the best number ever measured, and that number was in-sample. To have a
   reasonable (about 70%) chance of Tier 1, a top30 book needs a true VAL Sharpe of about 1.5 after costs.
   For a weekly book that means about 1.85 before costs. Before costs, the best top30 book measured directly on
   DEV read 1.82 (H11, sandbox row 40). The round-3 funding/premium books read about 1.7 to 1.9 on a crude
   estimate. Every price, volume or flow book read 1.17 or less (measured) or about 1.43 or less (crude). The
   one family that reached the bar on DEV earned about +0.16 before costs in VAL (trial 7eadbeeaf2adc98d).
2. DEV after-cost Sharpe has told almost nothing about VAL. Four DEV-to-VAL pairs: 1.168 to -0.531, 1.453 to
   0.384, 1.740 to 0.830, 1.499 to -0.249 (ledger rows; REPORTs). The two that stayed positive were long-biased
   books that rode a VAL drift (benchmark 0.921), and both failed G6.
3. Two flat charges in the scorer take more from a market-neutral top30 book than its edge has shown.
   (a) Costs of 12.5 bps per side take 0.23 to 0.46 Sharpe from weekly books (the G4 drop, rows 41 and 43 to 48).
   (b) G2 charges half of the gross funding PAID plus half of the gross funding RECEIVED, even for a book that
   never reads funding. On DEV that took 0.53 to 0.77 Sharpe, and it took more than G4 in 8 of 8 books (rows 40
   to 48). In VAL it took 0.45 from H11. I found no document that says what the 12.5 bps stands for (what
   account size, what order type), or why G2 is applied leg by leg instead of to net funding.
4. G6 and its speed limit exclude persistent premia by design (carry level, size, low-vol), and G2 halves
   funding income on top. So the best-documented crypto return source cannot pass. What remains for timing
   edges, given costs, the 90-day lookback and G6's 30-day stale copies: information 1 to 4 weeks old, traded
   about weekly, worth at least 1.85 Sharpe before costs. Eighteen top30 ideas found nothing near that.
   My judgement: run as it is now set up, the top30 search is unlikely to succeed. The weekly market-neutral
   rank-book class should be stopped.

## 1. The map

C/G = costs / average gross, over DEV, at 12.5 bps (top30), from the PLAN run logs. Funding is the gross paid /
received over DEV (KP-018 rows) where it was measured; otherwise the net amount (rec = received). Core rows give
DEV costs in equity, not per unit of gross; n/r = not reported. Holding = how often the targets change.

| # | gen.rd | unit | idea | class | holding | DEV SR | C/G | funding | what stopped it |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 0 | core | sma_cross_ls | trend, time series | slow daily | - | n/r | n/r | stage 1 activity 16 < 20 (uncounted) |
| 2 | 0 | core | donchian_ls | trend breakout | daily | 1.168 | n/r | n/r | VAL -0.531; G1 0.178, G2, G4, G5, G6 p 0.866, G7 |
| 3 | 0 | core | rsi_meanrev_ls | mean reversion 4h | 4h | -1.238 | n/r | n/r | VAL -0.770; all gates but G10 |
| 4 | 0 | core | voltarget_trend_ls | trend, vol-sized | daily | 1.453 | n/r | n/r | VAL 0.384; G1 0.747, G6 p 0.239 |
| 5 | 0 | core | funding_carry | fade high funding (TS) | 8h | -0.388 | n/r | n/r | VAL -0.323; all gates but G10 |
| 6 | 1 | core | tsmom_long_flat | trend long/flat | ~16 d per flip | 1.740 | 0.129 eq | n/r | VAL 0.830, PSR 0.926; G6 only, p 0.279 |
| 7 | 1 | core | relmom_pair | BTC/ETH relative | daily | 0.735 | 0.223 eq | - | DEV: neighbour n=42 at -0.293 |
| 8 | 1 | core | capitulation_long | rare-event long | event | 0.462 | - | - | activity 12 to 16 on whole grid |
| 9 | 1 | core | calm_long | vol-regime long/flat | daily | 1.280 | 0.197 eq | - | DEV: neighbours 0.950/0.977 vs always-long control 1.020 |
| 10 | 1 | core | taker_flow_long | flow long/flat | daily | 0.825 | 0.326 eq | - | DEV: under benchmark 0.925 at every value |
| 11 | 2.1 | top30 | resid_reversal | 1-wk residual reversal | weekly | -1.566 | 0.158 | 0.198/0.177 | S2 sign, S4, S5 (0 of 3 years) |
| 12 | 2.1 | top30 | activity_fade | crowding: trade count | weekly | 0.172 | 0.195 | 0.014 paid | S2 (< 0.6), S4 -0.136 |
| 13 | 2.1 | top30 | small_tickets | crowding: ticket size | weekly | -0.211 | 0.270 | 0.049 rec | S2 sign, S4 |
| 14 | 2.1 | top30 | absorbed_flow | contrarian taker flow | weekly | -1.251 | 0.193 | 0.015 paid | S2 sign, S4, S5 |
| 15 | 2.2 | top30 | resid_skew | lottery (fade jumps) | daily | -1.906 | 0.171 | 0.006 paid | S2 sign, S4, S5 |
| 16 | 2.2 | top30 | prior_month_reversal | reversal, weeks 8-4 | weekly | 0.381 | 0.205 | 0.012 paid | S2, S4 -0.013 |
| 17 | 2.2 | top30 | resid_momentum | 4-wk continuation | weekly + daily beta | 0.945 | 0.381 | 0.076 rec | strict S5: 2022H1 SR -2.22 (all 5 settings 0.92-1.07) |
| 18 | 2.3 | top30 | premium_shock | crowded leverage, premium | daily | 0.823 | 0.586 | 0.143 rec | S4 -0.033; S9 costs 0.508 > 0.25 |
| 19 | 2.3 | top30 | funding_shock | crowded leverage, funding | 8-hourly | 1.197 | 0.521 | 0.282 rec | S9 costs 0.445 |
| 20 | 2.3 | top30 | unrewarded_premium | premium net of return | daily | 0.980 | 0.519 | 0.298 rec | S9 costs 0.450 |
| 21 | 2.4 | top30 | averaged_funding_shock | #19, rank averaged 16 d | small daily steps | 1.492 | 0.285 | 0.388/0.544 | passed 10 DEV items; VAL -0.249: G1 0.333, G2 -0.697, G4 -0.659, G5 0 of 12, G6 p 0.571, G7 |
| 22 | 2.4 | top30 | averaged_unrewarded_shift | #20, averaged, own norm | 4-hourly | 0.731 | 0.254 | 0.103 rec | S3: 0.8 corner T - C = -0.130 |
| 23 | 3.1 | top30 | weekend_share | composition, weekend part | weekly | -1.348 | 0.206 | 0.291/0.292 | S2 sign, S3, S4 -1.756, S5 -2.004, S8 |
| 24 | 3.1 | top30 | heavy_hours | composition, heavy hours | weekly | -0.256 | 0.274 | 0.391/0.399 | S2 sign, S3, S4 -0.705, S5 -1.030, S8 |
| 25 | 3.1 | top30 | storm_share | composition, storm hours | weekly | 0.349 | 0.267 | 0.381/0.373 | S2, S4 -0.071, S5 -0.379, S6 -0.740, S8 |
| 26 | 3.2 | top30 | multiweek_momentum | 3-wk continuation | weekly | 0.541 | 0.293 | 0.510/0.570 | S2, S5 -0.015, S6 -0.100, S8 (9 of 10; B -1.431) |
| 27 | 3.2 | top30 | jump_continuation | skew continuation | weekly | 0.705 | 0.298 | 0.544/0.535 | S6 -0.820, S8 (10 of 10; B -1.785) |
| 28 | 3.2 | top30 | week_continuation | 1-wk continuation | weekly | 0.836 | 0.451 | 0.574/0.599 | S6 -0.314, S8 (5 of 10; B -0.757) |

Sources: gen000/REPORT.md; gen001/PLAN.md run log (DEV costs) and REPORT.md; gen002/PLAN.md run logs and
REPORT.md; gen003/PLAN.md run logs and REPORT.md; sandbox rows 40 to 48 (gross funding; row 41 is #11 re-run);
`omr.ledger summary` (VAL rows).

What the evidence closes, and how firmly:
- Long-biased "long when X" switches on BTC/ETH: closed, firm for this setup. Two VAL trials had positive Sharpe
  (0.384, 0.830). Both failed G6 because their shifted copies earned as much (LESSONS 8, 9).
- Textbook core mean reversion and funding carry (time series): closed. They lost on DEV and in VAL (#3, #5).
- Top30 contrarian crowded leverage (funding/premium shock): closed by one VAL trial. The trial failed six gates,
  G5 had 0 of 12 variants positive, and the book earned about +0.16 before costs. Moderate firmness: one rule,
  shaped on DEV. DEV is also partly spent for this input (LESSONS 27).
- Weekly top30 continuation (#17, #26 to #28): closed on DEV by readings nobody had seen (next30 negative in 3
  of 3; paired last-365-day median negative in 3 of 3). The edge sat in 2020 (Sharpe 2.0 to 2.9) and was gone by
  2022H1. Never VAL-tested, but these unseen readings are stronger than the in-sample ones.
- Bets against a recent move (#11, #14, #15, #16, #23 to #25) and crowding activity proxies (#12, #13): each
  closed on DEV, one default each. Taken one by one this is WEAK. Taken together, seven forms that bet against
  recent moves lost or earned too little. That is a consistent DEV pattern, not seven accidents.

## 2. The bar

### 2.1 What the gates ask, in numbers
- G1, VAL PSR(0) >= 0.90. PSR(0) = Phi(SR x sqrt(n-1) / ...). With n = 1,096 days, the annual Sharpe S gives z ~
  S x sqrt(1095/365) = 1.732 S (the skew and kurtosis term is negligible at a daily Sharpe of about 0.05). So
  G1 needs a VAL net Sharpe of about 1.2816 / 1.732 = 0.74. Check against the ledger: 0.830 gives 0.925 (row:
  0.926); -0.249 gives 0.333 (row: 0.333). This is the line where the point estimate passes. A book whose TRUE
  Sharpe is 0.74 passes G1 half the time.
- G4: VAL Sharpe > 0 at doubled costs. G2: VAL Sharpe > 0 with funding paid x1.5 and received x0.5, per symbol
  and per settlement (CONSTITUTION 4; constants.py lines 39-40). G5: the median of 12 jitter variants is >= 0.5 x
  base and at least 75% of them are positive. G7: at least 4 of 6 calendar buckets positive; in top30 that is in
  effect 4 of the 5 later buckets, because the 2020 bucket is short (KP-017 text item). G8: next30 Sharpe > 0.
- G6 in top30 (CONSTITUTION 13): p <= 0.10 means at most 1 of 20 stale copies (lags 30 days to about 18 months,
  step 621 h) did as well. The speed limit fails any book whose weights correlate above 0.5 with its own weights
  one or more steps (about 26 days) earlier. Together with the 90-day lookback (LANGUAGE 10), the edge has to
  come from information about 1 to 4 weeks old, and it must be worth more than the same rule's month-old picks.

### 2.2 What costs take (top30, 12.5 bps per side; constants.py line 132)
| holding | cost per year per unit of gross | Sharpe it takes at 1x costs |
|---|---|---|
| daily, full replacement | 2 x 365 x 0.00125 = 0.91 | 3.86 (oracle, CONSTITUTION 13) |
| daily-changing ranks (#18 to #20) | 0.21 to 0.24 measured (C/G / 2.497) | not read; estimate 0.7 to 0.9 (2x the weekly drops) |
| averaged rank (#21, #22) | 0.10 to 0.11 measured | 0.33 on DEV (row 40); 0.41 in VAL (#21's trial) |
| weekly, ranks re-drawn | 4/3 x 52.2 x 0.00125 = 0.087; measured 0.063 to 0.18 | 0.23 to 0.46 measured (G4 drop, rows 41, 43-48) |
| monthly / 20-day | 4/3 x 12.2 x 0.00125 = 0.020, plus drift and churn | 0.29 (oracle at 20 d); no book measured |
Below weekly, costs probably stop falling much. Two pieces do not depend on how often targets change: names
entering, leaving or dropping out of play (about 0.1 of #21's 0.285 C/G, LESSONS 32, "not measured"), and drift
traded back (about 0.03 a day per unit of gross, gen002 PLAN v4). Together that is about 0.04 + 0.014 per year
per unit of gross (estimate), so a monthly book would land near 0.07, not 0.02.

### 2.3 What G4 and G2 took from the books measured
| book (sandbox row) | DEV SR | G4 drop | G2 drop | pre-cost DEV SR (SR + G4 drop) | gross funding per unit gross per yr |
|---|---|---|---|---|---|
| #21 averaged_funding_shock (40) | 1.492 | 0.327 | 0.757 | 1.82 | 0.49 |
| #11 resid_reversal (41) | -1.566 | 0.456 | 0.613 | -1.11 | 0.17 |
| #23 weekend_share (43) | -1.348 | 0.409 | 0.656 | -0.94 | 0.28 |
| #24 heavy_hours (44) | -0.256 | 0.449 | 0.774 | 0.19 | 0.38 |
| #25 storm_share (45) | 0.349 | 0.420 | 0.728 | 0.77 | 0.36 |
| #26 multiweek_momentum (46) | 0.541 | 0.227 | 0.556 | 0.77 | 0.53 |
| #27 jump_continuation (47) | 0.705 | 0.259 | 0.600 | 0.96 | 0.54 |
| #28 week_continuation (48) | 0.836 | 0.335 | 0.530 | 1.17 | 0.56 |
| #21 in VAL (trial row, REPORT) | -0.249 | 0.410 | 0.448 | about +0.16 | - |
How the last column is computed: (paid + received) / average gross / 2.497. If every name sat at the default
rate of 0.01% per 8 h (gen002 PLAN v3, the researcher's recollection, not verified), a dollar-neutral book would
pay and receive 3 x 365 x 0.0001 = 0.11 per year per unit of gross, and G2 would charge half of that, 0.055.
DEV's flows ran 1.6 to 5 times that default level (estimate). So G2 binds on DEV readings (screen item S5). In
VAL it took 0.45, under G1's line of 0.74, so for a book that passes G1, G2 binds only if VAL funding looks like
DEV's.
Crude pre-cost DEV Sharpe for books without KP-018 readings, computed as SR x (T + C) / T: #17 1.43, #18 1.70,
#19 1.92, #20 1.76, #22 1.13, #16 0.79. On rows where a measurement exists, this method reads 0.05 to 0.2 too
high (#21 gives 1.86 against 1.82 measured; #28 gives 1.36 against 1.17).

### 2.4 What the calibration measured (verdict blocks only)
- Top30 (ucalibration_7d923e7e2375986d.json, verdict_unit_only): sealed at 0.10. Power at a true net Sharpe of
  1.5 is 0.82 / 0.74 (null A, fast / slow) and 0.70 / 0.68 (null B). Fast = 5 days and slow = 20 days of holding.
  No-skill Tier-1 rate over DEV-positive pairs: 0 of 165 (A) and 1 of 225 (B, the reversal family). Not known:
  any level below 1.5 (no 1.0 cell exists, LESSONS 12), and the no-skill rate for a book that is cheap to trade
  (KP-020). The families lose to their costs (mean VAL Sharpe -0.5 to -1.9, LESSONS 13). With costs switched
  off, the KP-017 worlds gave 1 Tier-1-like pass among 58 DEV-positive cases, with an upper 95% bound of about 10%
  (KP-020).
- Core (calibration_7d923e7e2375986d.json, verdict): sealed at 0.05. No-skill rate is 2.27% (A) and 1.59% (B) at
  0.05; this is an upper bound because G8 is not run (CONSTITUTION 8). Power at 1.5 is 0.84 / 0.83 (A) and
  0.905 / 0.81 (B); at 1.0 it is only 0.50 to 0.63 (LESSONS 37; the 1.0 cells are outside the verdict block).
- G1 alone at a true Sharpe S passes about Phi((S - 0.74) x 1.732) of the time (estimate, i.i.d. normal):
  0.91 at 1.5, 0.67 at 1.0, 0.50 at 0.74. The top30 Tier-1 power of 0.68 to 0.82 at 1.5 suggests a true 1.0 book
  passes about half the time (estimate, by analogy with core's 0.50 to 0.63).

### 2.5 The bar, stated
For unit top30, as VAL truths (not DEV readings):
- Holding about one week: at least 0.74 + about 0.35 = 1.1 before costs just to sit on G1's line, and about
  1.5 + 0.35 = 1.85 before costs for a 70 to 80% chance of Tier 1.
- Holding about 3 to 4 weeks (still inside the speed limit if formation is under about 3 weeks): about 1.0 for
  the line and about 1.75 for decent odds. Little gain, because churn and drift remain.
- Ranks re-drawn daily without averaging (#18 to #20): about 1.5 for the line and about 2.3 for decent odds.
  Rank-averaged forms (#21) took weekly-like drags (0.33 on DEV, 0.41 in VAL).
- Full replacement every day: impossible. G4 alone would need more than 7.7 (2 x 3.86).
- G2 adds a requirement only if VAL funding turns DEV-like (drops of 0.53 to 0.77).
Against this, no top30 book reached 1.85 before costs on DEV, in sample, except perhaps #19 (crude 1.92) and #21
(1.82). Their family earned about 0.16 before costs in VAL. The best price-only book read 1.17 measured (#28)
or 1.43 crude (#17), and both were continuation rules written after DEV results. With the decay of section 0,
point 2, an idea would need roughly 2.5 to 3.5 before costs on DEV to expect 1.5 in VAL (estimate: it assumes
VAL keeps 40 to 60% of DEV).

Unit core at 0.05: costs are 7.5 bps per side (5.5 bps taker fee + 2 bps slippage, CONSTITUTION 4). That is 0.55
per year per unit of gross for a daily flip, 0.078 for a weekly flip, and tsmom paid 0.129 over DEV. Costs do
not bind in core; G6 does: p <= 0.05 means at most 9 of 200 circular shifts did as well. A long-biased rule's
shifts keep its drift. tsmom's 0.830 had 28% of its shifts at least as good. If the shifted Sharpes were roughly
normal with mean about 0.6 (my assumption), their spread would be about 0.4, and p <= 0.05 would need a VAL
Sharpe of about 1.3. A symmetric timing rule needs a true timing Sharpe of 1.0 to 1.5 for 50 to 90% power. No
core rule has shown timing beyond drift: gen 1's "switch adds 0.9 Sharpe over its control" on DEV did not
survive G6 in VAL.

## 3. What is left

What the arithmetic rules out before any idea is chosen:
- Intraday and hour-of-day trading in either unit. A daily round trip costs 0.91 (top30) or 0.55 (core) per
  year per unit of gross.
- Daily re-ranked top30 books: 2.3 or more before costs for decent odds.
- Persistent characteristics (carry level, size, beta, low volatility). G6's stale copies hold the same tilt,
  and the speed limit fails slow books.
- Edges in recent entrants. G6 leaves out names that entered less than k hours before (CONSTITUTION 13, limit 1).
- Formation windows over about 8 weeks (the 90-day lookback). That excludes 6-to-12-month momentum and
  52-week-high analogues.

Stop (my recommendation):
- Weekly market-neutral rank books on price, volume and flow residuals in top30. That is 15 of the 18 top30
  ideas. None reached even the in-sample bar, and the continuation pattern died on unseen readings.
- Top30 funding/premium contrarian forms: lesson 34, DEV spent (lesson 27), and the KP-017 restriction.
- "Long when X" switches in core (lesson 9).

Ranked agenda. Every item has a LOW prior; I rank by cheapness of falsification and headroom on the arithmetic.
1. Calendar timing in core: a weekday/weekend or session schedule on BTC/ETH with at most 2 position changes a
   week. Mechanism: clienteles and liquidity by calendar (TradFi hours, US-hours ETF flow, thin weekends), as a
   time-series rule, which has not been tried; gen 3 tried calendar only as a top30 composition. Why it could
   clear the bar: costs are about 2 x 52 x 0.00075 = 0.078 per year per unit of gross (estimate); funding is paid
   only while long; and G6's circular shifts at hour offsets break the schedule's alignment, so a real calendar
   effect gets honest credit while drift gets none. Cheap falsifier: 1 to 2 DEV runs. The book's DEV Sharpe
   must beat an always-long control of the same average exposure by about 1.0 or more (lesson 11), positive in
   all 3 DEV years, with the sign fixed beforehand. Hindsight: medium to high, since ETF-era weekday flow and
   weekend crashes are remembered (gen003 PLAN v1 disclosures), and the choice of schedule is the KP-010
   channel.
2. Crowded leverage in core, as a time series at market level: the BTC/ETH premium over the index, or the funding
   shock against its own norm, symmetric long/short. Mechanism: leverage cycles. The literature the researchers
   cite is time series on BTC/ETH (gen002 PLAN v3), and index_close is admitted for the core symbols. Why it
   could clear: core costs; and the top30-only KP-017 restriction does not apply. Falsifier: one DEV run per
   form, positive in all 3 years, and a G2-like reading at least break-even. Against it: #5 (fading high funding
   in time series) lost on DEV and in VAL, and #21 failed in VAL. Hindsight: high (2024 funding spikes).
3. Sparse forced-flow liquidity provision in top30: hold a neutral book only after market-wide stress (a
   BTC-variance trigger), flat otherwise. Mechanism: reversal pays most when liquidity vanishes (Nagel 2012, as
   cited in gen003 PLAN). Why it could clear: a book in the market a fraction f of the weeks pays costs and funding
   in proportion to f, while its volatility scales with sqrt(f), so its cost and G2 drags shrink by sqrt(f). It
   beats the every-week book before costs if quiet weeks carry less than sqrt(f) / (1 + sqrt(f)) of the
   post-stress edge, a third at f = 1/4 (estimate). #25 had the registered sign when spread over every week
   (0.349, pre-cost 0.77). Falsifier: one run with pre-cost >= 1.5, next30 > 0,
   B > 0, and the largest DEV year at most half the sum (a G7 proxy). Hindsight: high. It descends from #25's
   result, and LUNA and FTX storms (against the long side) are remembered. Few events make G7 a risk.
4. An ensemble of 3 to 4 pre-registered, near-uncorrelated weekly signals in one program, so trades net. Pure
   arithmetic: k signals at Sharpe S give about S x sqrt(k) at less than k times the costs, so three at 1.0
   before costs give about 1.7. Falsifier: each component shows its registered sign with B > 0, combined with
   fixed equal weights, in one run. Risk: it hides multiple testing inside one trial. Do it only with
   components that have outside evidence; today none has shown an out-of-sample edge.
5. Slower top30 books (3 to 4 weeks) on inputs not yet read: position in the 90-day range, quote-volume trend,
   change in high-low range. The cost drag would be about 0.15 to 0.3. This is the lowest prior: these are
   mostly continuation proxies (gen003 PLAN v2 note c), and continuation died in 2022H1.
Decision rule I suggest: at most two more rounds, drawn from items 1 to 3. If neither gives a book with a
pre-cost DEV Sharpe of 1.5 or more and B > 0, pause research until the owner answers Q1, Q2 and Q4.

## 4. Questions for the owner (not proposals to loosen)

Any semantic change costs a build, an audit, a re-key and both calibrations: about 13 machine hours (KP-016:
top30 11.8 h and core 0.7 h with three workers; the batch re-key took 12.5 h and 73 min). It also re-ids every
trial.

Q1. What does 12.5 bps per side stand for?
- Evidence: core is 5.5 bps fee + 2 bps slippage (CONSTITUTION 4). Top30 is 5.5 + 7 (constants.py line 132,
  comment "C2"), with no derivation in any file I read. No file gives an account size or an order type.
  CONSTITUTION 11 leaves the capital cap to the human. The rate takes 0.23 to 0.46 Sharpe from weekly books; at
  half the rate, about half of that would come back (estimate). That would not have saved #21, which earned
  about 0.16 before costs. My recollection, unverified: Binance's base taker fee for USD-M futures is about 4.5
  to 5 bps, and maker about 2 bps.
- What would settle it: the owner states the intended account size and whether execution is taker or maker.
  Then spreads and impact for top30 names at that size are measured forward (outside the kernel, like
  tools/record_metrics.py).
- What would be lost: enemy 3, "unrealistic costs" (CONSTITUTION 1). And the top30 seal rests on no-skill books
  losing to their costs (LESSONS 13, 38). Lower costs raise null pass rates. The threshold could fall to 0.05,
  where one power cell read 0.48 (STATE), below POWER_MIN 0.50, and then the seal STOPs. A cost change would
  need KP-020 alongside it.

Q2. Is G2 meant to tax books that pay and receive equally?
- Evidence: the stress is applied per leg (paid x1.5, received x0.5). For a neutral book, it amounts to a
  standing charge of half its gross funding flows. On DEV it took 0.53 to 0.77 Sharpe, more than G4 in 8 of 8
  books; in VAL it took 0.45 from #21. It is not a market scenario. A market-wide rise in funding lifts what the
  short leg receives as much as what the long leg pays. On DEV, S5 (G2's reading) helped drop #23 to #26.
- What would settle it: the owner's intent. If the purpose is "do not live on received funding", a stress on NET
  funding (net received x0.5, net paid x1.5) keeps that protection; #18 to #20 took 30 to 53% of their return
  from funding (gen002 REPORT, round 3) and would still be stressed.
- What would be lost: the per-leg tax covers a venue whose funding differs on both legs at once (CONSTITUTION 12
  says Binance-only). Nothing else that I can see.

Q3. Is the top30 no-skill bound good enough for cheap books (KP-020)?
- Evidence: the bound was measured on daily families that lose to costs (0 of 165 and 1 of 225 at 0.10).
  Researchers now write weekly books. With costs off, the evidence is a point estimate of 1 in 58 and an upper
  95% bound of about 10%. The interim per-program null-world check exists (playbook 4b).
- What would settle it: weekly-anchored families (KP-020), with a pilot first; it adds about 1/5 more top30 time
  per family. Risk: the threshold may move to 0.05, and the 0.48 cell then threatens the seal. Nothing is lost;
  this adds protection.

Q4 (mine). Is the goal timing skill only, or any robust net return?
- Evidence: G6 credits only an edge that its 30-day-to-18-month-old copies lack. The speed limit fails books
  that are slower than about 50 days (CONSTITUTION 12). G2 halves funding received. So carry, size, low-vol and
  premium-level books cannot pass by construction (LESSONS 14; gen003 PLAN v1 note d). That is deliberate
  protection against riding drift (lesson 9). It also excludes the best-documented return source in crypto.
- What would settle it: the owner states the objective. Premia would need a different guard, for example a
  longer forward period scaled to the family (KP-010's suggestion). The cost is a gate redesign plus
  calibration. What would be lost: G6's protection against drift and tilt.

Q5 (mine, low priority). Is "trade ALL names when ANY is 0.01 off" right for 30 names?
- Evidence: weekly books rebalanced 573 to 668 times in 912 days, although their targets changed about 130
  times (gen003 run logs). So about 440 to 540 rebalances happened between decisions, each trading every name.
  Measured C/G (up to 0.45) exceeds the target-change estimate of 0.22 by up to 0.23. Drift is estimated at only
  about 0.03 of that (gen002 PLAN v4), so most of the excess is churn or is unexplained. A per-name band would
  probably save 0.1 Sharpe or less (estimate).
- What would settle it: a cost decomposition on DEV. Nothing is lost in protection.

Q6 (mine). Does the owner accept missing about half of true Sharpe-1.0 edges?
- Evidence: core power at 1.0 is 0.50 to 0.63 (LESSONS 37), and top30 has no measurement. If 1.0 is the
  realistic ceiling in liquid crypto after 2021, the instrument rejects about half of the real edges it is shown.
  The forward rules (60 days, DSR >= 0.95 at live, CONSTITUTION 11) are a second guard.

## 5. The process

- Cost per idea. Top30: 18 ideas in 28 sandbox runs (1.6 per idea). 15 of the 18 were settled by their single
  default run. #17 took 5 runs, #22 took 2, and #21 took 6 runs plus one counted trial. Runs take 67 to 177 s
  (logs). Core, gen 1: 5 ideas in 18 runs. The sandbox log's 49 rows are 18 (gen 1) + 22 (gen 2) + 3
  (verification, rows 40-42) + 6 (gen 3). Compute is trivial. The real cost is six researcher sessions and the
  coordinator's rulings: "a round costs about one usage window" (KERNEL_PROPOSALS, 2026-11-25).
- What the fixed screens bought. 17 of 18 ideas were stopped without spending a VAL bar, so M rose by 1 rather
  than by up to 18, and nothing was tuned after the fact. What they could not buy: the one survivor passed 10
  items and failed 6 gates in VAL (lesson 35). Screens on DEV readings cannot tell VAL winners apart, so their
  value lies in killing cheaply, not in selecting.
- What the KP-018 readings bought. In gen 3, every verdict came from one run. The unseen readings (next30, and
  the paired median over the last 365 days of DEV) killed the continuation pattern, which DEV's in-sample numbers
  had kept alive for four rounds. In gen 2, hand-made diagnostics cost 3 extra runs and squeezed lookback.
- Change 1, a bar check at registration. Each hypothesis states its estimated cost drag, the pre-cost VAL Sharpe
  it needs (0.74 + drag for the line, 1.5 + drag for decent odds), and outside evidence that an effect of that
  size exists in liquid crypto after 2021. Effects documented below the bar are not registered. Replace S2's
  "0.6 after costs" with "pre-cost DEV Sharpe (SR + G4 drop) >= 1.5 and B > 0", fixed in advance. This would
  have dropped every top30 book except #21. It would not have saved #21's trial; its gain is that ideas with no
  path to the bar would stop at registration instead of using up a round.
- Change 2, one DEV look per mechanism. A round may register a rule descended from a DEV result only if the
  parent's pre-cost DEV Sharpe is 2.5 or more (enough room for 40% decay). Gen 2 round 4 and gen 3 round 2 were
  descended rounds: 2 of the 6 top30 rounds and the only counted trial, both failing as lesson 35 predicted.
  Neither parent would have qualified (#19 crude 1.92; continuation parents 1.43 or less).
- DEV itself is a weak screen for VAL. Continuation earned Sharpe 2 to 3 in 2020 and was negative by 2022H1, and
  DEV funding ran 1.6 to 5 times the default. Weight the last 12 months of DEV (B) as heavily as the full period.

## 6. Contradictions and stale texts found

- omr/constants.py line 125 calls UNIVERSE_G6_LAGS and UNIVERSE_G6_MEMORY_MAX "PROVISIONAL (to be confirmed by
  measurement before the re-key)". KERNEL_PROPOSALS fix pass 9 says the same. audits/AUDIT_LOG.md line 687 records
  the K = 20 choice as standing, and the kernel has been sealed twice since. This is a stale comment, like KP-023.
- The top30 verdict lists 0.025 as "qualifying". CONSTITUTION 13 says 0.025 cannot be reached in top30 (p
  lattice k/21, so the minimum is 0.048). The pass rate at 0.025 is therefore trivially zero. Harmless, because
  the rule picks the largest threshold, but misleading to a reader.
- LESSONS 42 says a top30 idea "needs a DEV Sharpe of about 0.7 before either stress". The measured G2 drops
  reach 0.774 (row 44), and gen003 PLAN v2 uses "about 0.8".
- LESSONS 23 ("a screen it failed is not reopened by registering it again") against gen 3 round 2's frame, which
  re-registered the same idea (recorded in ruling 1 of that round).
- Already filed: CONSTITUTION 13's heading "NOT in force" (KP-024); the NULL_FAULT_MAX comment (KP-023); the
  playbook's 3 to 5 hypotheses against the briefs' 2 to 4.

## 7. Coordinator's note (2026-11-26; appended by the coordinator, nothing above is changed)

The review above is the independent analyst's text, saved unchanged. The coordinator checked its key numbers
against the ledger rows, the sandbox log and the seal's recount: G1's line (0.74), the power cells of both
units, the DEV-to-VAL pairs and the G2 and G4 drops of rows 40 to 48 are as stated.

Accepted, and acted on in RESEARCH_PLAYBOOK.md (section 8b) with this commit:
- The map and the bar (sections 1 and 2).
- The stop list of section 3: no further round registers a weekly market-neutral rank book on price, volume or
  flow residuals in top30, a top30 funding or premium contrarian form, or a "long when X" switch in core.
- The two process changes of section 5: the bar check at registration, and the limit on rules descended from a
  DEV result.

Not decided here, because they are the human's: the direction of the search after this review (the agenda of
section 3 and its decision rule), and the questions of section 4. They are put to the human as open decisions
9 to 11 in STATE.md. No research round is started and nothing in the kernel is changed before the human answers.

Filed from sections 4 and 6 in KERNEL_PROPOSALS.md, all open: KP-025 (G2 charges both funding legs of a book
that pays and receives equally), KP-026 (the rebalance rule trades every name when any name is outside its
band), KP-027 (two stale texts in the kernel).

The coordinator's own reading, for the record: the search has not failed for lack of trying or through a fault
of the scorer. The scorer did what it was built for, twice in one day: it stopped six rules at the cost of six
short runs. What the evidence does not show, anywhere, is an edge. Lower costs or a gentler funding stress would
not have changed one verdict so far.
