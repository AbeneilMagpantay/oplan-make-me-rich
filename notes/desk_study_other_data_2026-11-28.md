# Desk study: which other data could be admitted (CONSTITUTION 3.2)

Status: COMPLETE (2026-11-28). Started 2026-11-27, resumed 2026-11-28 after a usage stop. Analyst, read-only on the project. All listings and probes by
scripts in `desk_study\scripts\` (stdlib Python, run with -I); raw S3 listings cached in
`desk_study\listings\`. No data row dated after 2022-06-30 was downloaded or read.

Groups done: A, B, C, D, E, F, G; short list (section 2), rejected (3), evidence (4), judgement (5),
changes since KP-015 (6), owner questions (7). No sample data file was downloaded: every fact comes from
listings, documentation, HEAD requests or endpoint probes returning at most a few rows dated 2020-2021.

Marks: V = verified on a page, listing or endpoint I fetched (2026-11-27 or 2026-11-28; URL in the source
list S-n). D = the source's own documentation says so (URL given). U = unverified, general knowledge.
"(proj)" = verified by the project's own KP-015 feasibility study of 2026-11-19
(`notes/kp015_feasibility.md`, `notes/kp015_tables_v2.txt`), not re-done here.

Admission criteria (CONSTITUTION 3.2): (a) history covering DEV and VAL (from about 2020-01-01 to today);
(b) knowable-time stamps with a conservative lag; (c) same source live at decision time; (d) free or
cost approved; (e) revision check possible. Usefulness (G6): only information that changes within days to
a few weeks is creditable; a slow level cannot pass.

## 1. Table of candidates

Columns: (a) history 2020-01 to today | (b) knowable-time stamps | (c) live | (d) free, no account |
(e) revision risk | per-coin coverage incl. delisted | FAST/SLOW | outside evidence.

### A. Binance public archive (data.binance.vision) beyond what the kernel uses

| # | source | (a) history | (b) stamps | (c) live | (d) free | (e) revision | per-coin / delisted | speed | evidence |
|---|---|---|---|---|---|---|---|---|---|
| A1 | USD-M `metrics` (OI, top-trader and global long/short ratios, taker ratio; 5-min) | FAIL: BTCUSDT from 2020-09-01, ETH/SOL and other names from 2021-12-01 V(S1) | create_time = end of 5-min period D(proj) | archive about 1 day late V(S1); REST keeps 30 days only: startTime in 2021 refused, code -1130 V(S2) | yes V | HIGH: BTC 2020-09..2021-11 first written 2026-03; 2024-03..2026-11 rewritten again in 2026-07/08 and 2026-11 (409 files) V(S1) | 1,064 symbol folders; delisted present (LUNAUSDT, FTTUSDT, SRMUSDT) V(S1) | FAST (OI changes) | see section 4 |
| A2 | USD-M `aggTrades` / `trades` (every trade; size, side) | aggTrades from 2020-01 (BTCUSDT, LINKUSDT); trades from 2019-09 (BTCUSDT) V(S3) | trade time in ms D(S10) | archive daily files about 1 day late V(S3); REST aggTrades live U | yes V | MEDIUM: single monthly files rewritten years later (BTCUSDT 2020-03 rewritten 2024-11; 2023-05 and 2023-10 rewritten 2026-10) V(S3) | delisted present (LUNAUSDT 2021-01..2022-05) V(S3) | FAST | none found that survives costs (section 4) |
| A3 | USD-M `bookDepth` | FAIL: from 2023-01-01 V(S4) | - | yes V | yes | - | - | FAST | - |
| A4 | USD-M `bookTicker` | FAIL: 2023-05-16 to 2024-03-30 only V(S4) | - | FAIL: stopped V | yes | - | - | FAST | - |
| A5 | `liquidationSnapshot` | FAIL: COIN-M only, BTCUSD_PERP 2023-06-25 to 2024-10-14; no USD-M folder exists V(S5) | - | FAIL: stopped V | yes | - | - | FAST | - |
| A6 | USD-M `premiumIndexKlines` 1h | from 2020-01 (BTCUSDT) V(S3) | bar open time D(proj) | yes V | yes | low-medium: some 2022-23 months rewritten in 2023 V(S3) | per coin | FAST | stop list: premium/funding contrarian closed; the kernel already has mark and index |
| A7 | SPOT `klines` 1h (OHLC, volume, quote volume, trades, taker buy volume) | YES: BTCUSDT 2017-08, LINKUSDT 2019-01, DOGEUSDT 2019-07, FTTUSDT 2019-12, SOLUSDT 2020-08 (its spot listing month) to 2026-10 V(S6) | bar open time; ms before 2025, microseconds from 2025-01-01 D(S10) | monthly files 4 to 9 days after month end V(S6); REST api.binance.com serves 2020 hours V(S7) | yes, no key V | LOW-MEDIUM: initial backfill written 2021-06-22, later months once; one rewrite (all 2022-03 files rewritten 2022-09-02) V(S6) | ALL 152 perpetuals listed by 2022-06-30 have a spot USDT folder; in a 40-name sample spot started on or before the perp in 40 of 40, but 9 spot pairs ended before their perp V(S31); delisted spot pairs present (SRM, BTT, KEEP, MITH, BTCST, ANC, UST, MIR, TORN, LEND, BCHSV, VEN) V(S8); 3,767 spot folders, 776 USDT-quoted V(S8); name reuse trap: LUNAUSDT spot runs 2020-08 to 2026-10 (old LUNA then LUNA 2.0) V(S6)/U | FAST (volume, taker flow, trade counts in spot vs perp) | section 4 |
| A8 | SPOT `aggTrades` | from 2017-08 (BTCUSDT) V(S6) | ms/us D | yes | yes | low-medium: 3 old files rewritten 2022/2024 V(S6) | as A7 | FAST | as A2 |
| A9 | COIN-M perps and quarterly contracts (term structure) | partial: BTCUSD_PERP from 2020-08; first quarterly expiry 2020-09-25 (BTC, ETH, ADA, LINK); 14 bases only; USD-M quarterlies BTC/ETH only from 2021-03 expiry V(S9) | bar open time | yes V | yes | low | 50 COIN-M perps; quarterlies 14 bases | SLOW (basis level) / FAST changes duplicate funding-premium | stop list (basis/premium) |
| A10 | Options: `BVOLIndex`, `EOHSummary` | FAIL: BVOLIndex from 2023-06-20; EOHSummary 2023-05-18 to 2023-10-23 only, 5 underlyings V(S9) | - | BVOL yes, EOH no V | yes | - | BTC/ETH/BNB/XRP/DOGE only | FAST (market-wide) | - |
| A11 | REST `/futures/data/basis` | odd: PERPETUAL served 2020-01 rows despite the 30-day doc text; CURRENT_QUARTER empty for 2020 V(S2) | - | yes | yes | unknown (no archive) | per pair | as A6 | stop list |

### B. Other venues

Note: from this machine, TLS to public.bybit.com, okx.com, kraken.com (support pages), api.exchange.coinbase.com
and api-pub.bitfinex.com failed certificate verification (both the local Python and the web-fetch tool:
"unable to verify the first certificate"). I did not try to work around it. Those cells are "could not
verify" (cnv).

| # | source | (a) history | (b) stamps | (c) live | (d) free | (e) revision | per-coin / delisted | speed | evidence |
|---|---|---|---|---|---|---|---|---|---|
| B1 | Bybit public archive (public.bybit.com: daily trade files) | cnv; a vendor (Tardis) says Bybit linear contracts from 2020-05-28, inverse from 2019-11-07 U(S13) | trade time U | cnv | yes, no key U | cnv | linear USDT contracts sparse before 2021 U | FAST (but same information as Binance tape) | none |
| B2 | OKX historical data page | cnv | - | cnv | U (page said to need no login, unverified) | cnv | U | - | none |
| B3 | BitMEX (public.bitmex.com) | trades/quotes from 2014 U | - | FAIL: "Trading ceased on 23 September 2026 at 04:00 UTC. All exchange services have ended." V(S12) | - | - | XBT/ETH and few alts U | - | - |
| B4 | Deribit DVOL (30-day implied vol index, BTC and ETH) | FAIL for DEV: first daily value 2021-03-24 V(S14) | index value at resolution end U | yes, public endpoint, no key V(S14) | yes V | low U | market-wide, BTC/ETH only | FAST | some evidence for vol-risk, not for cross-section |
| B5 | Kraken downloadable OHLCVT | cnv (support page blocked); quarterly zip on a file host U | - | REST OHLC 720 bars only U | free U | U | Kraken listings only | FAST | none |
| B6 | Coinbase public candles ("Coinbase premium") | cnv (TLS); history from 2015 for BTC-USD U | candle start U | U | free, no key U | low U | few altcoins listed in 2020 U; XRP suspended 2021-01 U | FAST | Coinbase premium: practitioner claims only, no peer-reviewed cross-sectional evidence found |
| B7 | Bitfinex stats (margin longs/shorts) | cnv (TLS) | - | U | free, no key U | U | BTC, ETH and a handful of alts U | FAST | none for cross-section |
| B8 | HTX (Huobi) | not checked (no public bulk archive known) U | - | - | - | - | - | - | - |
| B9 | Upbit (Korea) public candles, KRW markets (Korea premium, Korean volume share) | KRW-BTC from 2017, 2020 rows served V(S15); but SOL, DOGE, AVAX have no 2020 candles (listed later) V(S15) | candle UTC start time V | yes, no key V | yes V | U | FAIL: only 62 of the 152 perps listed by 2022-06-30 have a CURRENT Upbit KRW market; delisted markets return 404 "Code not found" (KRW-LUNA, KRW-MATIC) V(S15): a survivor-only panel | FAST | Korea premium studied for BTC (Choi, Lehar, Stauffer), not as a cross-sectional weekly predictor; none found |

### C. On-chain and fundamentals

| # | source | (a) history | (b) stamps | (c) live | (d) free | (e) revision | per-coin / delisted | speed | evidence |
|---|---|---|---|---|---|---|---|---|---|
| C1 | Coin Metrics community (API and GitHub CSVs): active addresses, tx count, supply, market cap, MVRV | YES for covered assets: btc 2009, eth 2015, link 2017, ada 2017, doge 2013, xrp 2013, ftt 2019, srm 2020-07, uni 2020-09 V(S16) | daily, UTC day; publication lag not stated: assume the day's value usable 1 day + after the UTC day ends U | API answered without key V(S16); GitHub says "The archives are updated daily" D(S17) | free, no key V; licence CC BY-NC 4.0 D(S17) | MEDIUM-HIGH: "sets of available assets and metrics can be changed at any time" D(S17); on-chain metrics are re-derived when methodology changes U; no vintages | FAIL on coverage: network metrics (AdrActCnt) for 138 assets, only 45 of the 152 perps listed by 2022-06-30; none for SOL or LUNA; exchange flows (FlowInExNtv) for 2 assets only V(S16). Delisted FTT, SRM present V | SLOW (activity levels); changes are noisy | on-chain network factors: Liu and Tsyvinski (2021) find network growth relates to returns at weekly horizons for BTC (time series), cross-sectional evidence weak; none after costs found |
| C2 | DefiLlama (TVL per chain/protocol, stablecoin supply, fees) | TVL from about 2018-2019 for early protocols U | daily snapshots U | free hosts "never read a key and are rate limited" D(S18) | yes D | HIGH: history is recomputed when a protocol adapter changes U; no vintages U | per DeFi token or chain only (part of top30), mapping coin to protocol needed | SLOW (TVL level); flows faster | TVL/market-cap is a value ratio (slow, fails G6); none found for weekly timing |
| C3 | blockchain.com charts (BTC on-chain: tx count, hash rate, etc.) | from 2009, 2020 rows served V(S19) | daily U | yes V (Last-Modified today) | free, no key V | U | BTC only (market-wide) | mostly SLOW | none useful for a cross-section |
| C4 | Blockchair dumps | raw chain tables from genesis U | - | U | free at throttled speed U | low (raw blocks) | a few chains only U | needs heavy derivation | none |
| C5 | Glassnode | - | - | - | FAIL: API needs the Professional plan; "Advanced" gets a Light API with "14 days of history, daily (1d) resolution only, 50 calls per day" D(S20) | - | - | - | - |
| C6 | CryptoQuant | FAIL: free Basic plan has "3 years historic data", "Low metric resolution (Daily)" D(S21); account and key needed | - | - | account | - | - | - | exchange-flow claims are vendor marketing |
| C7 | Santiment | FAIL (c): free plan data "delayed by 30 days" ("30-day lag in Sanbase"); Pro 49 USD/month D(S22) | - | - | account | - | - | - | - |
| C8 | IntoTheBlock | not checked; free tier is dashboard only U | - | - | account U | - | - | - | - |
| C9 | Etherscan / Dune | U | - | - | FAIL (d): API key (Etherscan) or account (Dune) needed U | - | - | - | - |

### D. Attention and sentiment

| # | source | (a) history | (b) stamps | (c) live | (d) free | (e) revision | per-coin / delisted | speed | evidence |
|---|---|---|---|---|---|---|---|---|---|
| D1 | Wikimedia pageviews API (per article, daily) | YES: from 2015-07-01 (Bitcoin) V(S23) | UTC day; daily data published about a day later U; lag proposal: usable from the bar after 23:00 UTC of the next day | yes V | free, no key V; BUT policy: automated clients must send a User-Agent with "some way of contacting you, the operator" or "may be blocked without notice" D(S24); my generic client got HTTP 429 after about 12 requests V(S23) | MEDIUM: the "automated" agent class was added 2020-04-29 and earlier data was NOT reclassified, so "user" views change definition inside DEV D(S25); per-article counts do not follow redirects D(S26), so renamed articles break the series | POOR mapping: Cardano_(blockchain_platform), Polkadot_(cryptocurrency), Binance_Coin, BNB_(cryptocurrency), Chainlink_(blockchain) all 404 for 2020; "Chainlink" 2 views (a redirect) V(S23); a coin-to-article map is a hand-made, hindsight-prone choice; delisted coins keep articles U | FAST (attention spikes) | attention predicts BTC returns in time series (Liu and Tsyvinski 2021, Google searches); cross-sectional attention evidence mixed (section 4) |
| D2 | Google Trends | U: 2004+ but values are re-scaled per query and re-sampled on every request U | - | no official free API U | free web, scraping against terms U | FAIL (e): not point-in-time; numbers change between requests U | per keyword, ambiguous names | FAST | Liu and Tsyvinski 2021 (BTC, time series) |
| D3 | GDELT 2.0 (news events, GKG themes/tone, 15-min files) | YES: from 2015-02-19 D(S27); 2020-01-01 file exists V(S28) | file time stamp; Last-Modified of the 2020-01-01 00:00 file is 2019-12-31 23:50, i.e. written in real time and never rewritten V(S28) | yes, lastupdate.txt minutes old V(S28) | free, no key V; licence not stated on the fetched page | LOW for raw files (immutable, md5 in the file list) V(S28) | per keyword/organisation; small coins rarely in the news; GKG zip about 5 MB per 15 min (2020), so about 175 GB per year | FAST | news tone and crypto: BTC time series only; none cross-sectional after costs found |
| D4 | alternative.me Fear and Greed (BTC, daily) | from 2018-02 U (history start not stated on the page) | daily update, time not stated D(S29) | yes D | free; "You must properly acknowledge the source of the data" D(S29) | U: proprietary, weights changed (surveys "currently paused") D(S29) | market-wide only | FAST but mostly price-derived (volatility 25%, momentum/volume 25%, dominance 10%) D(S29) | contrarian-sentiment claims are practitioner lore; none rigorous found |
| D5 | GitHub activity (GH Archive hourly files) | YES: hourly files from 2011; 2020-01-01-0 written 2020-01-01 01:05 V(S30) | event time | yes U | free V | LOW (immutable) V | needs a coin-to-repository map (hand-made) | SLOW (development activity) | developer activity: weak, slow; fails G6 by nature |
| D6 | Reddit / X | Pushshift closed to the public in 2023 U; X API paid U | - | FAIL (c)/(d) U | FAIL U | - | - | FAST | - |
| D7 | Crypto news archives (CryptoPanic, CoinDesk etc.) | U | - | U | API keys / paid U | - | - | FAST | - |

### E. Market-wide state

| # | source | (a) history | (b) stamps | (c) live | (d) free | (e) revision | coverage | speed | evidence |
|---|---|---|---|---|---|---|---|---|---|
| E1 | FRED CSV download (VIXCLS, DTWEXBGS broad dollar, DEXKOUS KRW, etc.) | YES (VIX from 1990, dollar 2006) U; 2020 rows served V(S34) | observation date; VIX published after US close U; H.10 dollar series posted weekly U; lag proposal: VIX next UTC day 23:00, H.10 series +7 days | yes, files modified 2026-11-23..25 V(S34) | free, no key V | LOW for VIX U; ALFRED vintages allow a revision check D/U | market-wide | FAST | crypto-equity co-movement since 2020 is documented U; as a switch for a crypto cross-section: none found |
| E2 | CBOE VIX_History.csv | YES U | daily | yes, Last-Modified 2026-11-26 V(S35) | free U (terms not fetched) | LOW U | market-wide | FAST | as E1 |
| E3 | CFTC Commitments of Traders, CME bitcoin (code 133741; legacy and TFF) | YES: report 2019-12-31 present (CME futures since 2017-12) V(S36) | as of Tuesday, "released at 3:30 p.m. Eastern time", "usually on Friday" D(S37); lag proposal: visible from Saturday 00:00 UTC | yes, dataset modified 2026-11-20 V(S36) | free, no key (Socrata) V | LOW-MEDIUM: occasional CFTC corrections U; check by re-download and stored-row compare | market-wide (BTC; ETH contract later U) | weekly, FAST-ish | practitioner claims only; one 2022 analysis found commercials' net position inversely correlated with price; no rigorous test found (S38) |
| E4 | CME futures basis | U | - | - | FAIL (d): no free historical source known; CME DataMine is paid U | - | BTC/ETH | SLOW level | basis = carry (stop list) |
| E5 | Equity indices (FRED SP500, NASDAQCOM) | FRED SP500 limited to about 10 years by licence U | daily | yes U | free U | LOW | market-wide | FAST | as E1 |

### F. Supply, market cap and events

| # | source | (a) history | (b) stamps | (c) live | (d) free | (e) revision | coverage | speed | evidence |
|---|---|---|---|---|---|---|---|---|---|
| F1 | CoinGecko free API | FAIL: "Public API users are limited to querying historical data within the past 365 days" V(S39) | - | yes | key/plan for history | - | broad | - | - |
| F2 | CoinPaprika free API | FAIL: "Getting daily historical data before 2025-11-27 ... is not allowed in this plan" V(S40) | - | yes | plan for history | - | broad | - | - |
| F3 | CoinMarketCap historical snapshots (weekly pages since 2013) | YES as pages U | snapshot date U | yes U | FAIL (terms): "strictly for your personal, non-commercial use"; prohibits "data mining, crawling, "scraping", robot or similar automated" access D(S41) | U (circulating supply restated by CMC) | about all coins U | market cap = size, SLOW | size is a slow level, fails G6 |
| F4 | Coin Metrics supply / market cap | see C1: SplyCur 45 of 152 early perps; PriceUSD 141 V(S16) | daily | yes | CC BY-NC 4.0 D | medium | partial | SLOW (supply changes are scheduled, slow) | - |
| F5 | Token unlock schedules (Tokenomist/TokenUnlocks, CryptoRank) | FAIL: no free point-in-time archive of schedules as known at the time U | - | paid/key U | FAIL U | HIGH (schedules edited) U | partial | FAST around events | Keyrock industry study (16,000+ events, about 90% followed by declines, reported second-hand; S42); one small event study CAR -15% over [-30,+30] days, tradable signal weak (S42) |
| F6 | Exchange listing/delisting announcements (Binance announcement pages) | U | release time stamps exist U | U | undocumented endpoint; terms not fetched U | U | events only | FAST (hours to days) | listing effects decay within days U; top30 already sees delistings in klines |
| F7 | Stablecoin supply / mints (DefiLlama stablecoins, Coin Metrics) | YES U | daily | yes D(S18) | free, no key D | MEDIUM U | market-wide | FAST-ish | Griffin and Shams (2020, Tether 2017-18) contested by later work U; none for switching a cross-section |

### G. Other sources found

| # | source | verdict |
|---|---|---|
| G1 | Tardis.dev free samples (first day of each month free) | FAIL (a): not continuous; full history paid U |
| G2 | CoinGlass / Coinalyze (aggregated OI, liquidations, long/short across venues) | FAIL (d): API key, CoinGlass paid U; history depth and revision policy unknown U |
| G3 | Hyperliquid, dYdX (on-chain perps, public data) | FAIL (a): start 2023 / 2021 U |
| G4 | Kaiko, Amberdata, Laevitas, CryptoCompare | FAIL (d): paid or key U |
| G5 | Binance REST basis endpoint (`/futures/data/basis`) serving 2020 rows | a curiosity (V, S2): same information as premium/index, stop list |

Binance archive sizes (zipped, from listings, V): metrics about 21 to 26 MB per symbol for 5 years;
aggTrades USD-M BTCUSDT 45.3 GB (82 months), LINKUSDT 8.3 GB, LUNAUSDT 3.5 GB; trades USD-M BTCUSDT 70.8 GB;
spot aggTrades BTCUSDT 59.5 GB; spot klines 1h 2.4 to 4.7 MB per symbol for its whole life (so about 0.3 to
0.5 GB for 150 symbols, about 13,000 monthly files plus checksums); bookTicker BTCUSDT 52.6 GB for 10
months.

## 2. Short list (at most three)

Only one source passes (a) to (e) cleanly AND carries fast per-coin information. Two more are listed
because they nearly pass; both are weak.

### SL-1. Binance SPOT klines 1h (A7): PASSES (a), (b), (c), (e); (d) free, under the same Binance terms as the kernel's own data (section 1A)

- First dates (V, S6/S31): BTCUSDT 2017-08, LINKUSDT 2019-01, DOGEUSDT 2019-07, FTTUSDT 2019-12, SOLUSDT 2020-08
  (the month SOL listed); in a 40-name sample the spot pair started on or before the perpetual every time. All
  152 perpetuals listed by 2022-06-30 have a spot USDT folder, delisted ones included (V, S8).
- What it adds: the same coin's SPOT activity (quote volume, trade count, taker-buy volume) next to the
  perpetual's. Nothing in the kernel today sees the spot market's volume or flow (the index price is a
  multi-venue spot PRICE only).
- Adapter: freq 1h; same 12 columns as klines; open time in ms until 2024-12, MICROSECONDS from
  2025-01-01 (D, S10), so the parser must branch on the date or the magnitude; `visible_from` = its own bar
  (as klines: usable from that bar's close; I would add nothing more, the bar closes at the same instant);
  a missing hour = unknown (KNOWN false), never filled with zero volume, because a spot pair can stop while
  the perpetual trades (WAVES, LINA, BNX, STMX, REEF, BTS, SRM, BTCST ended in spot first, V S31).
  Symbol map: perp 1000-prefixed names map to the unprefixed spot pair (1000SHIBUSDT -> SHIBUSDT, V S31);
  name reuse must be guarded: LUNAUSDT spot runs 2020-08 to 2026-10 although the old LUNA ended in May 2022
  (V S6), so a join is valid only where spot close / perp close stays within a tolerance (for example 5%) on
  the same hour; otherwise KNOWN false. New fields (suggested): `spot_quote_volume`, `spot_trades`,
  `spot_taker_buy_quote_volume` (unit P V, N, P V). Ratios to the perp's quote volume are dimensionless, so
  the language's scale rules hold.
- Download: about 2.4 to 4.7 MB zipped per symbol for its whole life (V), so about 0.3 to 0.5 GB and about
  13,000 monthly files plus checksums for 150 symbols; the current month from daily files or REST
  `api.binance.com/api/v3/klines` (2020 hours served, V S7).
- Revision check: the kernel's own stored-row comparison (every later download must reproduce stored rows,
  as for klines); one archive-vs-REST month compared at download (as KP-015 did for index); watch S3
  LastModified (history so far: backfill written 2021-06-22, one rewrite of every 2022-03 file on
  2022-09-02, otherwise written once, V S6).
- Hypotheses (fast enough for G6; each is a weekly top30 book, so see the stop-list caveat below):
  - H-S1 "leverage share shift": per coin, log(perp quote volume / spot quote volume) over the last 7 days
    minus the same over the previous 8 weeks; short the coins whose perp share rose most, long those whose
    spot share rose most. Mechanism: leveraged demand is fragile and unwinds; spot-led demand is not.
    Outside evidence: NONE found for this ratio as a predictor (S44); related only: perp-spot price
    deviations track leveraged end-user demand (He, Manela, Ross, von Wachter, S44). Size: none reported.
  - H-S2 "spot flow ahead of perp flow": spot taker-buy share minus perp taker-buy share over 7 days; long
    the highest. Mechanism: spot buyers hold the coin and are less levered. Named confound: cash-and-carry
    (buy spot, sell perp) produces the same reading with no directional content, so the sign is uncertain.
    Outside evidence: NONE found cross-sectionally; order-flow imbalance is known to predict returns only
    over minutes to hours (U). Size: none.
  - H-S3 "market leverage gate": the cross-sectional median of H-S1's ratio as a market state that switches
    a top30 book on only after a market-wide jump in perp share (deleveraging to come), in the spirit of the
    meta-review's agenda item 3. Outside evidence: NONE found.
- Stop-list caveat (read this): H-S1 and H-S2 are weekly market-neutral rank books on a volume/flow
  quantity, which is the FORM the playbook closed (8b). The input is new (no participant-specific secret,
  but unseen by this project and unspent on DEV). Whether a new input reopens a closed form is a ruling for
  the coordinator/owner (Q4). H-S3 is a gate, not a rank book.

### SL-2. Wikimedia pageviews per article, daily (D1): NEARLY passes; fails (d) as practised and (e) in part

- First date 2015-07-01 (V, S23); live and free without a key (V); per coin, FAST.
- Blocking issues: (1) the operator's policy asks automated clients for a User-Agent with contact details,
  and a generic client was rate-limited after about 12 requests (V, S23/S24), so a pilot needs the owner's
  consent to send a contact (Q2); (2) the "automated" agent class was added 2020-04-29 and earlier traffic
  was not reclassified (D, S25): "user" views change definition inside DEV, so any level or ratio crossing
  April 2020 is contaminated (use agent=all-agents and accept bots, or start DEV features in May 2020);
  (3) counts do not follow redirects (D, S26), so a renamed article breaks its series; (4) the coin-to-
  article map is hand-made and hindsight-prone; of 11 titles tried for 2020, 5 obvious ones did not exist
  (Cardano_(blockchain_platform), Polkadot_(cryptocurrency), Binance_Coin, BNB_(cryptocurrency),
  Chainlink_(blockchain)) (V, S23). Coverage of the 152 early perps is unknown; my guess is half or less (U).
- Adapter: daily; `visible_from` = the 1h bar opening at 00:00 UTC two days after the view day (a day's
  counts are normally published within about a day, U, so a 24-hour safety margin on top); a missing day =
  unknown. Download: one request per article per range, a few hundred requests in total, under 10 MB.
- Revision check: re-request a fixed sample of past article-days monthly and compare with stored values
  (the API has no vintages); store the first-seen value.
- Hypotheses:
  - H-W1 "attention spike fade": 7-day views / 8-week median views; short the highest, long the lowest,
    weekly. Mechanism: attention-driven buying (the Barber-Odean channel) overprices for days to weeks.
    Evidence: ElBahrawy et al. 2019 report a views-informed strategy beat baselines 2015-2019, no figures,
    no costs, no out-of-sample test (S43); Liu and Tsyvinski 2021 find attention (Google) predicts BTC
    returns POSITIVELY over 1 to 6 weeks (time series, U), i.e. the opposite sign at market level. Mixed
    theses (S45). No size after costs anywhere.
  - H-W2 "attention not yet priced": abnormal view growth in weeks with a small absolute return; long.
    Evidence: NONE found.

### SL-3. CFTC Commitments of Traders, CME bitcoin (E3): passes (a) to (e) as a MARKET-WIDE weekly state; low value

- First report used here 2019-12-31 (V, S36; contract since 2017-12, U); free Socrata API without key (V);
  release Friday 15:30 Eastern for the Tuesday position (D, S37).
- Adapter: weekly event dataset; `visible_from` = Saturday 00:00 UTC after the release (covers EST/EDT and
  a late release); a delayed release (holidays, the 2025 US government shutdown, U) simply arrives later.
  Size: kilobytes. Revision check: re-download all rows each week and compare with stored rows.
- Hypothesis H-C1: switch a top30 book on only in weeks after a large drop in leveraged-fund / non-commercial
  net length (forced deleveraging). Evidence: practitioner claims only; one analysis found commercials'
  position inversely related to price (S38). Caveat: after 2024 CME positioning is dominated by the
  ETF-basis trade (U), so the meaning of the series changed inside VAL/VAULT. A market-wide gate cannot by
  itself make a cross-sectional book; it can only remove bad weeks.

## 3. Rejected sources (one line each, criterion)

- A1 Binance metrics (OI, long/short ratios, taker ratio): (a) BTC from 2020-09, others from 2021-12; (e) rewritten repeatedly, again in 2026-11; REST 30 days only. (Same verdict as KP-015; still true.)
- A2/A8 aggTrades/trades (large-trade imbalance, size distribution): passes (a)-(d), (e) workable, but 0.5 to 1 TB zipped for 150 symbols (extrapolated from BTC 45 GB, LINK 8 GB, LUNA 3.5 GB; U), and its new content is a flow book of the closed class; ticket size already tried (#13).
- A3 bookDepth: (a) from 2023-01. A4 bookTicker: (a)/(c) 2023-05 to 2024-03 only. A5 liquidationSnapshot: (a)/(c) COIN-M only, 2023-06 to 2024-10.
- A6 premiumIndexKlines, A9 COIN-M quarterly basis, A11 REST basis: stop list (premium/basis), duplicates mark/index.
- A10 Binance options BVOL/EOH: (a) from 2023.
- B1 Bybit, B2 OKX, B5 Kraken, B6 Coinbase, B7 Bitfinex: could not verify (TLS failure from this machine); on general knowledge none covers the top30 cross-section from 2020 with positioning data.
- B3 BitMEX: (c) exchange closed 2026-09-23.
- B4 Deribit DVOL: (a) from 2021-03-24; BTC/ETH only.
- B9 Upbit: survivorship (delisted markets return 404) and coverage (62 of 152).
- C1 Coin Metrics: coverage 45 of 152 for network data, SLOW, CC BY-NC 4.0. C2 DefiLlama: (e) recomputed history (U), SLOW, partial. C3 blockchain.com: BTC only, SLOW. C4 Blockchair: heavy derivation, few chains. C5-C9 Glassnode, CryptoQuant, Santiment, IntoTheBlock, Etherscan/Dune: (d) or (a)/(c) (3-year history, 30-day lag, plan or key).
- D2 Google Trends: (e) not point-in-time. D3 GDELT: formally passes (a)-(e) (immutable 15-minute files), but per-coin coverage poor, about 175 GB per year to process, no evidence. D4 Fear and Greed: market-wide, mostly price-derived, proprietary weights. D5 GitHub: SLOW. D6/D7 Reddit, X, news APIs: (c)/(d).
- E1/E2/E5 FRED, CBOE, equity indices: pass (a)-(e) as market-wide states; no evidence they switch a crypto cross-section; same tier as SL-3.
- E4 CME basis: (d). F1 CoinGecko, F2 CoinPaprika: (a) on free plans (365 days / 1 year). F3 CoinMarketCap: terms forbid scraping; size is SLOW. F5 token unlocks: no free point-in-time archive. F6 listing announcements: undocumented endpoint, effects decay in days. F7 stablecoin supply: market-wide, contested evidence.
- G1-G4 Tardis free days, CoinGlass/Coinalyze, Hyperliquid/dYdX, Kaiko etc.: (a) or (d).

## 4. Outside evidence, summarised

- Open interest and long/short ratios as cross-sectional predictors: none found (S44); one paper finds OI
  is misquoted by large exchanges (S44). Irrelevant anyway: the data fail (a) and (e).
- Spot vs perpetual volume or flow as a cross-sectional weekly predictor: none found (S44).
- Attention (Wikipedia/Google): BTC time-series evidence positive at 1 to 6 weeks (U); one Wikipedia
  strategy paper without costs or out-of-sample test (S43); student theses mixed (S45). No cross-sectional
  result after costs found.
- CFTC positioning: practitioner commentary only (S38).
- Token unlocks: an industry study and a small event study (S42); the data are not freely available.
- The strongest documented cross-sectional crypto signal is the futures basis (Chi et al., S44) - a carry
  level the scorer cannot credit and the playbook has closed.

## 5. Sober judgement

Nothing here is likely to move a weekly top30 book to a true Sharpe of 1.5 after costs. The only clean new
input is Binance spot activity, and it is as public as the perpetual data: it does not close the
"information gap" the review named, it only adds a second view of the same participants' flows, and no
published work shows that it predicts which coins beat which over a week. Attention data are fast but
messy (definition break in April 2020, hand-made article map, contact requirement), and the evidence is
weak and partly of the opposite sign. Market-wide states (COT, VIX) can at best remove bad weeks from a
book that already has an edge. My estimate (not a measurement): well under one chance in ten that any
hypothesis above clears the project's bar in VAL.

How to find out cheaply BEFORE any kernel build: a DEV-only offline study of SL-1. Download only the spot
1h monthly files dated up to 2022-06 for the symbols that were ever top30 members in DEV (about 0.1 to
0.2 GB), read perpetual DEV rows only through the kernel's own loaders with the `dev_end` ceiling (the
precedent KP-028 set for a study), freeze the feature script and the signs of H-S1 to H-S3 before the first
run, and apply the bar the playbook already uses: pre-cost DEV Sharpe at least 1.85 (better 2.5, for decay),
the last 365 days of DEV positive, at most 1 of 20 stale copies (lags about 26 days) as good as the book,
next30 positive. DEV is unspent for spot inputs, which is the one real advantage. Cost: a few hours, no
re-key, no VAL row. If H-S1 to H-S3 all fail, close the spot front and do not build. A Wikipedia pilot only
if the owner agrees to send a contact (Q2), and only for names whose article exists under a rule fixed in
advance.

## 6. Notes on what changed since the project's KP-015 study (2026-11-19)

- metrics: the November 2026 rewrite continues (409 BTCUSDT files 2024-03-04..2026-11-26 rewritten in
  2026-11, V S1); first dates unchanged.
- Binance Vision dataset terms dated 2026-08-26 now exist (section 1A); they bind the kernel's existing data.
- The forward-only recorder `tools/record_metrics.py` has never written its log: the folder `records/`
  does not exist in the project tree (checked read-only 2026-11-28). So no forward copy of OI or ratios is
  being built.

## 7. Questions for the owner

- Q1 (terms, all Binance data): the Binance Vision dataset terms of 2026-08-26 license the archive under
  CC BY-NC-SA 4.0, permit "algorithmic historical backtesting for purely personal non-production research"
  and exclude "live proprietary trading execution". This covers the kernel's present klines, funding, mark
  and index files as well as any new archive dataset. Do you accept this as it stands, or do you want the
  live REST API's own terms checked or advice taken? (Reported, not interpreted.)
- Q2 (Wikimedia): its policy asks automated clients to identify themselves with contact details. Will you
  allow a contact (an email or web page of yours) in requests for a pilot? Without it, generic clients are
  throttled (HTTP 429 seen).
- Q3 (paid data): is there any budget for data? Only one price was read (Santiment Pro 49 USD/month).
  Glassnode needs its Professional plan for API access; CryptoQuant's free plan has 3 years of daily data;
  aggregated OI/liquidation vendors (CoinGlass, Coinalyze, Kaiko, Tardis) need keys or payment. None was
  checked for history before 2021 or for a revision policy.
- Q4 (stop list): does the closed form "weekly market-neutral rank book on volume or flow" stay closed for
  NEW inputs (spot volume, page views), or was it closed only for the perpetual-only inputs it was measured
  on? This decides whether H-S1 and H-S2 may be registered.
- Q5 (forward recording): KP-015 decided to store OI and long/short ratios forward-only, but nothing has been
  recorded (no `records/` folder). Start recording now? It can never enter DEV or VAL, only the forward period.
- Q6 (network): TLS to Bybit, OKX, Kraken, Coinbase and Bitfinex failed certificate checks from this
  machine. If you want those venues verified, it needs another network or a check of the local proxy.

## Sources (URLs fetched)

- S1: https://s3-ap-northeast-1.amazonaws.com/data.binance.vision?prefix=data/futures/um/daily/metrics/BTCUSDT/ (and ETHUSDT, SOLUSDT, LUNAUSDT, FTTUSDT, SRMUSDT; folder count with delimiter=/ on data/futures/um/daily/metrics/), listed 2026-11-27; the XML listing with `&marker=` paging still works.
- S2: https://fapi.binance.com/futures/data/openInterestHist (also globalLongShortAccountRatio, takerlongshortRatio) with startTime 2021-01-01: HTTP 400 code -1130 "parameter 'startTime' is invalid", 2026-11-27. /futures/data/basis?pair=BTCUSDT&contractType=PERPETUAL&period=1d with a 2020-01 window: 5 rows dated 2020-01-01..05.
- S3: S3 listings of data/futures/um/monthly/aggTrades/{BTCUSDT,LINKUSDT,LUNAUSDT}/, data/futures/um/monthly/trades/BTCUSDT/, data/futures/um/monthly/premiumIndexKlines/BTCUSDT/1h/ (LastModified per file compared with the data month), 2026-11-27.
- S4: S3 listings of data/futures/um/daily/bookDepth/BTCUSDT/, data/futures/um/daily/bookTicker/BTCUSDT/, data/futures/um/monthly/bookTicker/BTCUSDT/, 2026-11-27.
- S5: S3 listing of data/futures/um/daily/ (folders: aggTrades, bookDepth, bookTicker, indexPriceKlines, klines, markPriceKlines, metrics, premiumIndexKlines, trades) and data/futures/cm/daily/liquidationSnapshot/BTCUSD_PERP/, 2026-11-27.
- S6: S3 listings of data/spot/monthly/klines/{BTCUSDT,LINKUSDT,DOGEUSDT,SOLUSDT,LUNAUSDT,FTTUSDT}/1h/ and data/spot/monthly/aggTrades/BTCUSDT/, 2026-11-27.
- S7: https://api.binance.com/api/v3/klines?symbol=LINKUSDT&interval=1h with a 2020-01-01 window: 4 rows from 2020-01-01 00:00, 2026-11-27.
- S8: S3 listing of data/spot/monthly/klines/ (all symbol folders) matched against the 678 symbol names of data/manifest.json (names and first_bar only), 2026-11-27.
- S9: S3 listings of data/futures/cm/monthly/klines/, data/futures/um/monthly/klines/ (dated contracts), data/option/daily/BVOLIndex/BTCBVOLUSDT/, data/option/daily/EOHSummary/*, data/futures/cm/daily/metrics/BTCUSD_PERP/ (from 2021-07-08), 2026-11-27.
- S10: https://raw.githubusercontent.com/binance/binance-public-data/master/README.md (fetched 2026-11-28): spot kline columns are Open time, Open, High, Low, Close, Volume, Close time, Quote asset volume, Number of trades, Taker buy base asset volume, Taker buy quote asset volume, Ignore; "The timestamp for SPOT Data from January 1st 2025 onwards will be in microseconds."; "new daily data becoming available the next day and new monthly data at the first monday of the month"; code licence MIT, dataset use governed by TERMS_AND_CONDITIONS.
- S11: https://raw.githubusercontent.com/binance/binance-public-data/master/TERMS_AND_CONDITIONS.md (fetched 2026-11-28), "BINANCE VISION DATASET TERMS", Version 1.0, last updated August 26, 2026. See section 1A below.

### 1A. Binance Vision dataset terms (applies to A1-A11 AND to the kernel's existing klines, funding, mark and index files)

Reported, not interpreted (no legal advice). From S11:
- 3.1: "Datasets are provided to you under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International Public License."
- 3.3: where the licence and the terms both impose obligations, "the stricter obligation shall apply".
- 3.4: "Commercial licensing is strictly excluded under this agreement;" (commercial use needs a separate enterprise licence).
- 4.1: permitted non-commercial uses include "academic research, non-monetized open educational projects" and "algorithmic historical backtesting for purely personal non-production research".
- 4.2: the data may not be used for "live proprietary trading execution, automated commercial order generation" (or selling signals).
- 2.4: data "derived from, calculated with, or extracted from the Datasets, including derivative indicators" is governed by the terms.
- 7.1 / 7.2: abide by "all posted rate limits, automated script guidelines, and download protocols"; no "scraping routines, scripts, or continuous automated queries designed to circumvent rate restrictions".
These terms are dated 2026-08-26, i.e. after the kernel's v1 download design. Whether a forward test that
reads the live REST API (not the archive) and a person trading his own 1,000 USD fall under 4.1 or 4.2 is a
question for the owner (section 7, Q1). The live REST market-data API has its own terms (not fetched).

- S12: https://www.bitmex.com/ (public.bitmex.com redirects there), fetched 2026-11-28: "Trading ceased on 23 September 2026 at 04:00 UTC." "All exchange services have ended." The S3 listing of public.bitmex.com returned HTTP 403.
- S13: https://docs.tardis.dev/historical-data-details/bybit (via search result summary; vendor's own coverage, not the Bybit archive).
- S14: https://www.deribit.com/api/v2/public/get_volatility_index_data?currency=BTC&resolution=1D with window 2020-06-01..2021-06-01, no key: 70 rows, first 2021-03-24, 2026-11-27.
- S15: https://api.upbit.com/v1/candles/days?market=KRW-BTC&to=2020-01-06T00:00:00Z (rows 2020-01-01..05); https://api.upbit.com/v1/market/all (302 KRW markets now); KRW-LUNA and KRW-MATIC: HTTP 404 "Code not found"; KRW-SOL/DOGE/AVAX: no candles in 2020-06..2020-12. 2026-11-27/28.
- S16: https://community-api.coinmetrics.io/v4/catalog/asset-metrics?metrics=AdrActCnt,TxCnt,SplyCur,CapMrktCurUSD,FlowInExNtv,SplyExNtv,CapMVRVCur,PriceUSD and /v4/catalog/assets?assets=btc,eth,link,doge,sol,xrp,ada,uni,luna,ftt,srm (metadata only), and /v4/timeseries/asset-metrics for link 2020-01-01, no key, 2026-11-27/28.
- S17: https://github.com/coinmetrics/data (README), fetched 2026-11-28: "made available under the CC BY-NC 4.0 license"; "The archives are updated daily"; "sets of available assets and metrics can be changed at any time". The docs at docs.coinmetrics.io now redirect to a login page at kb.talostrading.com.
- S18: https://api-docs.defillama.com/ (fetched 2026-11-28): free hosts api.llama.fi, coins.llama.fi, stablecoins.llama.fi, yields.llama.fi "never read a key and are rate limited". No terms or revision statement on that page.
- S19: https://api.blockchain.info/charts/n-transactions?timespan=5days&start=2020-01-01&format=json, 2026-11-27.
- S20: https://docs.glassnode.com/basic-api/api-key (fetched 2026-11-28).
- S21: https://cryptoquant.com/pricing (fetched 2026-11-28).
- S22: https://app.santiment.net/pricing (fetched 2026-11-28).
- S23: https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/user/Bitcoin/daily/20150101/20150705 (first item 2015070100) and 2020-01-01..03 for 38 candidate titles; after about 12 requests HTTP 429, stopped. 2026-11-27/28.
- S24: https://foundation.wikimedia.org/wiki/Policy:Wikimedia_Foundation_User-Agent_Policy (fetched 2026-11-28).
- S25: https://doc.wikimedia.org/generated-data-platform/aqs/analytics-api/changelog.html and https://phabricator.wikimedia.org/T238363 (via search summary 2026-11-28): automated agent type added 2020-04-29, earlier traffic not reclassified.
- S26: https://doc.wikimedia.org/generated-data-platform/aqs/analytics-api/concepts/page-views.html (fetched 2026-11-28): "Redirects ... aren't counted as views of the actual page."
- S27: https://blog.gdeltproject.org/gdelt-2-0-our-global-world-in-realtime/ (fetched 2026-11-28).
- S28: http://data.gdeltproject.org/gdeltv2/lastupdate.txt (file names, sizes, md5) and HEAD of http://data.gdeltproject.org/gdeltv2/20200101000000.gkg.csv.zip (5,288,568 bytes, Last-Modified 2019-12-31 23:50:20 GMT), 2026-11-27.
- S29: https://alternative.me/crypto/fear-and-greed-index/ (fetched 2026-11-28); https://alternative.me/crypto/api/ (general API terms).
- S30: HEAD https://data.gharchive.org/2020-01-01-0.json.gz (15,670,114 bytes, last-modified 2020-01-01 01:05:06 GMT), 2026-11-27.
- S31: S3 listings for 40 perpetuals listed by 2022-06-30 (10 chosen: LUNA, FTT, SRM, SC, BTT, KEEP, MATIC, 1000SHIB, ANC, BTCST; 30 drawn at random, seed 7): data/spot/monthly/klines/<SYM>/1h/ against first_bar/last_bar in data/manifest.json. Spot first month <= perp first month in 40 of 40; spot ends BEFORE the perpetual for WAVES (2024-06), LINA (2025-03), BNX (2025-03), STMX (2025-02), REEF (2024-08), BTS (2023-12), SRM (2022-11), BTCST (2022-11), ATA (2026-05). 2026-11-28.
- S34: https://fred.stlouisfed.org/graph/fredgraph.csv?id=VIXCLS&cosd=2020-01-01&coed=2020-01-08 (also DTWEXBGS, DEXKOUS), no key, 2026-11-27.
- S35: HEAD https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv, 2026-11-27.
- S36: https://publicreporting.cftc.gov/resource/6dca-aqww.json?cftc_contract_market_code=133741 (legacy) and gpe5-46if (TFF), 2019-12-25..2020-01-20: reports 2019-12-31, 2020-01-07, 2020-01-14, "BITCOIN - CHICAGO MERCANTILE EXCHANGE", 2026-11-27.
- S37: https://www.cftc.gov/MarketReports/CommitmentsofTraders/ReleaseSchedule/index.htm (fetched 2026-11-28).
- S38: https://stockcharts.com/articles/tac/2022/10/cot-report-data-work-backwards-358.html (via search summary 2026-11-28).
- S39: https://api.coingecko.com/api/v3/coins/chainlink/market_chart/range (2020 window, no key): HTTP 401, error 10012, 2026-11-27.
- S40: https://api.coinpaprika.com/v1/tickers/btc-bitcoin/historical?start=2020-01-01: HTTP 402, 2026-11-27.
- S41: https://coinmarketcap.com/terms/ (fetched 2026-11-28), sections 2.1, 4.4, 5.1, 6.1.
- S42: https://crypto.news/token-unlocks-almost-always-negative-for-price-keyrocks-study-reveals/ and related coverage (via search summary 2026-11-28); primary Keyrock report not read.
- S43: https://arxiv.org/abs/1902.04517 (ElBahrawy, Alessandretti, Baronchelli 2019, Frontiers in Blockchain 2:12), abstract fetched 2026-11-28: views-informed strategy "performs better, in terms of returns on investment" than baselines "for most of the covered period" (July 2015 to January 2019); no figures, costs or out-of-sample test in the abstract.
- S44: search summaries 2026-11-28 on spot/futures volume and on open interest as cross-sectional predictors: no paper found testing either. Closest: He, Manela, Ross, von Wachter, "Fundamentals of Perpetual Futures" https://arxiv.org/abs/2212.06888 (perp-spot deviations linked to leveraged end-user demand; pricing, not a weekly predictor); Chi, Hao, Hu, Ran (2023), risk factors in crypto futures (basis is the strongest cross-sectional signal, 2017-2021) https://acfr.aut.ac.nz/__data/assets/pdf_file/0010/686755/6b-Yeguang-Chi.pdf; Giagkiozis and Said, open interest misquoted by large exchanges https://arxiv.org/abs/2310.14973; Riksbank WP 413 (volume carries predictive information; reversal concentrated in low-volume coins) https://www.riksbank.se/globalassets/media/rapporter/working-papers/2022/no.-413-trading-volume-and-liquidity-provision-in-cryptocurreny-markets.pdf.
- S45: search summary 2026-11-28 on attention and crypto returns: student theses with mixed results (Erasmus: https://thesis.eur.nl/pub/67084/Investor-Attention-in-the-Cryptocurrency-Market-Sven-Konijn-456579.pdf), ElBahrawy et al. (S43). Liu and Tsyvinski (2021, Review of Financial Studies, "Risks and Returns of Cryptocurrency": Google search attention predicts BTC returns over 1 to 6 weeks, time series) is from general knowledge, U.

## Coordinator's note (2026-11-28; appended by the coordinator, nothing above is changed)

- This is the analyst's note as delivered, saved from the session's scratch folder. By its own statement the
  analyst changed no project file, read no data row dated after 2022-06-30 and put no personal detail in any
  request; the project tree was clean before and after its work (git status).
- Checked by the coordinator on 2026-11-28: the dataset terms quoted in section 1A, fetched again from the same
  address (title, version 1.0, "Last Updated: August 26, 2026", and clauses 3.1, 4.1, 4.2, 2.4, 7.1, 7.2 as
  quoted); and the recorder's state (tools/record_metrics.py exists; there is no records/ folder;
  notes/kp015_build_evidence.md says it was never run against the network).
- One correction. Section 1A says the terms are dated "after the kernel's v1 download design". The project
  began on 2026-11-18, so the terms are older than the project; the project had simply not read them. Nothing
  else in the note depends on this.
- The certificate failures of group B (Bybit, OKX, Kraken, Coinbase, Bitfinex) were not worked around and are
  not to be. They may be blocks at the network provider; that is the coordinator's guess and is not verified.
  The note's conclusion does not rest on those venues.
- Every cell marked U is the analyst's general knowledge and is to be read as unverified.
- What follows from the note is in KERNEL_PROPOSALS.md (KP-029, open) and in STATE.md.
