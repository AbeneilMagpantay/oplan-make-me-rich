# KP-015 feasibility study (2026-11-19)

What history exists in Binance's public bulk archive for the proposed data expansion, established by
listing the archive and opening sample files. Nothing in the kernel was changed. Full tables:
`notes/kp015_tables_v2.txt`. Where a statement rests on one sample file it says so.

## 1. Open interest and long/short ratios (`metrics` files)

- Sampling every 5 minutes, 288 rows a day. Columns: open interest (contracts and value), top-trader
  account ratio, top-trader position ratio, all-account ratio, taker buy/sell volume ratio.
- History: BTCUSDT from 2020-09-01; the other nine current symbols from 2021-12-01. No missing days.
- Against the development period (2020-01-01 to 2022-06-30): BTCUSDT 73% covered, the other nine 23%
  (only the last seven months). The test period is fully covered.
- Defects: about 19 to 22 days per symbol have no ratio columns (2021-12-31 to mid-January 2022, and
  single days); BTCUSDT 2020-09-01 has every row twice (one file opened); recent files are unsorted.
- NOT REVISION-SAFE. 2021-12 to 2023-06 was first written in a June 2023 backfill; BTCUSDT's 2020-09 to
  2021-11 first appeared on 2026-03-18; 2024-03 to 2026-06 was rewritten in July and August 2026, and
  part of it again in the week of this study. The archive shows only the latest write, so whether the
  contents changed cannot be checked.
- Live: the REST endpoints keep 30 days only, so a live system must record these itself; the archive
  publishes each day about one day later.

Conclusion: not admissible as research data under the admission rules (history does not cover the
development period, and "not revised after the fact" cannot be shown). Usable only forward, from
copies the project stores itself with first-seen hashes.

## 2. Index price and premium index (basis)

- 1h klines from each symbol's listing month to the present with no missing month; BTCUSDT 2020-01
  has all 744 hours and matches what the REST endpoint serves today (one month checked).
- Live from REST with no stated history limit.

Conclusion: admissible, subject to the project's own stored-row revision check from the first download.

## 3. A point-in-time universe of USDT perpetuals

- 686 crypto USDT perpetuals have files. Live at each January 1st: 3 (2020), 79 (2021), 134 (2022),
  146 (2023), 242 (2024), 344 (2025), 538 (2026). Only BTC, ETH and BCH existed until September 2020.
- 159 contracts ended before 2026-10; their files are still in the archive (LUNAUSDT downloaded and
  checked; SCUSDT, FTTUSDT, AGIXUSDT, OCEANUSDT, SRMUSDT, LENDUSDT, MATICUSDT, EOSUSDT listed).
- Traps that would corrupt a naive universe:
  - PADDING: after a delisting the archive keeps writing monthly files with a frozen price, zero
    volume and zero trades (128 of 137 delisted contracts). File presence is not membership.
  - 237 of the 924 `*USDT` names are TradFi perpetuals (shares, metals, oil), indistinguishable by name.
  - Names reused (NUUSDT, ANTUSDT, MDTUSDT), contracts relisted under the same name with padding in
    between (CTK, CVC, CVX, ICP, LIT, MAVIA, MDT, SLP, TLM), 1000-prefixed contracts (two coexist with
    an unprefixed version), renames (LEND to AAVE, MATIC to POL and others, inferred from names and
    dates), and index contracts (DEFIUSDT, BTCDOMUSDT and others).
- Size of the whole crypto universe at 1h: klines 645 MB zipped, mark klines about 346 MB, funding
  about 23 MB; about 1 GB and 66,000 files.

Conclusion: feasible. Membership must be computed from trading activity in the klines (never from
file presence), with an explicit classification of contract types and a seasoning period; a
cross-section is thin before 2021.

## 4. What else the study showed

Kline files of the project's ten current symbols were themselves rewritten in batches in 2021,
2023-24 and August 2024 (19 to 30 monthly files per symbol). The project's manifest pins the bytes it
downloaded; a stored-row comparison on every later download is what makes any dataset revision-safe.
