# KP-015 build evidence (2026-11-19)

Working tree only. Base commit 521687f (omr/ identical to b12df97). No re-key, no calibration run, no seal,
no real selftest, no git write, ledger untouched (`git status ledger/ kernel.lock` clean; `python -m omr.ledger
verify` -> `ledger verify: OK`). `python -m omr.kernel_lock verify` FAILS on the working tree, as expected
until the approved re-key (changed kernel files; also delete omr/__pycache__ before re-keying).

## Files

New kernel: omr/universe.py (A1 symbol table + listing, A2 activity, B membership, membership counts),
omr/upipeline.py (unit top30 pipeline: panel, stage1_u, stage2_u, ugates, G8 next30, loaders),
omr/ucalibrate.py (F), omr/programs/ucal_xs_momentum.omr, ucal_xs_reversal.omr, ucal_xs_carry.omr,
kernel_noise_top30.omr.
Changed kernel: constants.py (universe constants), data.py (index_klines, streaming research hash and
validate, universe download, snapshot keeps universe tables, membership counts in validate), datasets.py
(index_klines registered, in PROGRAM_EXTRA), engine.py (universe core + reference; core untouched),
interp.py (Panel, index_close, in-play cs_), lang.py (unit header, index_close, lookback_hours, D3),
evaluate.py (unit dispatch, unit and lookback_hours in rows), sandbox.py (top30), selftest.py (noise top30),
kernel_lock.py (seal over both units), probe.py (deterministic index bars), calibrate.py (index field of
core null worlds = mark bars; nothing else), access.py (for_membership).
Docs: LANGUAGE.md section 10 (+ header and identity notes), CONSTITUTION.md section 13, KERNEL_PROPOSALS.md
KP-015 build note, STATE.md.
Tests: tests/test_universe.py, test_ucalibrate.py, test_core_identity.py (+ ref_core_runner.py,
ref_kernel_b12df97.zip = `git archive b12df97 omr`), test_record_metrics.py; updated conftest.py,
test_ledger_lock.py, test_selftest.py, test_access_log.py, test_data_integrity.py, test_exploits.py.
Outside the kernel: tools/record_metrics.py. Data: data/symbols.json (new, pinned in the manifest; needs a
`!data/symbols.json` line in .gitignore to be tracked - NOT edited by me), data/manifest.json,
data/validation.json rewritten by the kernel commands.
Line endings: my patch scripts first wrote CRLF; every source file was normalised back to LF bytes (two
test files that contain an intentional CR byte were restored from 521687f).

## A. Data

Symbol table (`python -m omr.universe symbols`, exchangeInfo server time 2026-11-19 03:00 UTC; archive listing
of data.binance.vision via its public S3 bucket endpoint, cached under data/raw/listings):
- 1080 monthly / 1083 daily klines folders; 918 names match ^[0-9A-Z]+USDT$ (164 others excluded: 52 dated
  delivery, 18 *SETTLED copies, 94 other quote assets or names).
- crypto_perpetual 678 (all with monthly files; NU, ANT, MDT reused by TradFi: crypto rows end at the TradFi
  onboard hour), tradfi_perpetual 234, index_contract 6 (DEFI, BTCDOM, ALL in exchangeInfo; BLUEBIRD,
  DOTECO, FOOTBALL absent), other 1 (PREDICTUSDT, pre-market). 26 ended names absent from exchangeInfo are
  crypto by rule R2. The study's 686 includes 8 names with daily files only (listed Nov 2026).

Download (`python -m omr.data universe`, 6 workers, 0.05 s pause, generic UA, end month 2026-10):
| dataset | planned | stored (checksum OK) | 404 | bytes |
|---|---|---|---|---|
| klines | 21,103 | 21,103 | 0 | 615.2 MB |
| mark_klines | 21,103 | 21,103 | 0 | 323.7 MB |
| funding | 21,103 | 19,726 | 1,377 | 20.7 MB |
| index_klines (ten core included, + Nov daily) | 21,900 | 20,986 | 914 | 354.4 MB |
| total | 85,379 | 83,088 | 2,291 | 1,314 MB |
0 failures, 0 without checksum, 0 revisions; 678 symbols stored; 404s: 1,340 funding and 902 index in padded
months; 37 funding months missing in trading months (ICP 14, TLM 12, BNX 10, QTUM 1; 2020-2023), 12 index
months (10 symbols, 2025-26). research_hash d1b6ce5b8d0a03809d6264b9b9e0b6d1be5629431c732c56470b25584e1125fd.
Stored parquet: klines 911 MB, mark 629 MB, index 687 MB, funding 39 MB (2,712 tables).

`python -m omr.data validate`: PASSED, 0 failing counts (ten core symbols per symbol as before; 668 universe
symbols summed: DEV klines rows 1,732,942 (active 1,713,607, gap rows 5,496), VAL rows 6,484,016 (active
6,066,846, gap 1,970); every price/volume/funding/timestamp count 0).

## B. Membership (from validate; counts only)

First month with a top30 unit: 2020-05 (11 members); 30 members from 2020-10; next30 from 2020-12.
| month | eligible | top30 | next30 |
|---|---|---|---|
| 2020-04 | 3 | 0 | 0 |
| 2020-05 | 11 | 11 | 0 |
| 2020-07 | 24 | 24 | 0 |
| 2020-10 | 31 | 30 | 0 |
| 2021-01 | 60 | 30 | 30 |
| 2021-07 | 105 | 30 | 30 |
| 2022-01 | 125 | 30 | 30 |
| 2022-02 | 128 | 30 | 30 |
| 2022-03..07 | 84, 85, 86, 85, 83 | 30 | 30 |
| 2022-08 | 134 | 30 | 30 |
| 2023-01 | 140 | 30 | 30 |
| 2024-01 | 199 | 30 | 30 |
| 2025-01 | 284 | 30 | 30 |
| 2025-07 | 374 | 30 | 30 |
Distinct symbols ever: top30 DEV 78, VAL 106, DEV+VAL 138; next30 DEV 98, VAL 197, DEV+VAL 217.

Unit availability (hours with a top30 unit; every in-play member active on all of its last L hours):
| region | hours | all members active | L=24h | 168h | 720h | 2160h |
|---|---|---|---|---|---|---|
| DEV | 18,985 | 18,421 | 18,985 | 18,985 | 18,985 | 18,985 |
| VAL | 26,303 | 24,653 | 26,280 | 26,136 | 25,584 | 24,144 |

ARCHIVE HOLES (DEV, dev_end data): 2022-02-26..28 (48 symbols without any bar) and 2022-04-01..02 (49
symbols). Under the seasoning rule as built they restart the 90-day seasoning: 12 of February 2022's top30
(SOL, XRP, LTC, LUNA, NEAR, FTM, FIL, SAND, MANA, LRC, ONE, SUSHI) are not members from 2022-03 to 2022-07;
the top30 of those months keeps only 17-18 of February's members.
FUNDING GAPS: ICPUSDT is a top30 member in 10 DEV months (2021-09..2022-06) without a funding settlement in
its archive folder (the first listing's funding sits in ICPUSDT_SETTLED, which is not read); TLM in 2022-03.
A program reading funding is unknown (flat) whenever ICP is in play: ucal_xs_carry has weights on 12,206 of
the 18,985 DEV unit hours (momentum 18,985).

## Core bit-identity (hard requirement)

tests/test_core_identity.py runs tests/ref_core_runner.py in separate processes with the b12df97 kernel
(extracted from tests/ref_kernel_b12df97.zip) and with the working kernel, and compares byte for byte:
- synthetic world (BTC, ETH, 8 extended with late listings, to VAL end), 14 programs (the 11 strategies/*.omr
  + kernel_kitchen_sink, kernel_noise_single, kernel_noise_portfolio): stage-1 weights, full-grid weights and
  raw signal, stage-2 metrics, every gate value, info, daily returns: IDENTICAL (>= 8 evaluated).
- REAL DEV frames (dev_end, no handle): stage 1 (24 truncation + DEV end, 6 start cuts) weights and raw
  signal of the same 14 programs: IDENTICAL, no fault.
- the comparator itself fails on a one-ulp change (test_the_comparison_can_fail).
Also unchanged and green: test_baselines (real DEV vs the naive reference and the pre-language Python).

## Real DEV stage 1 of top30 kernel programs (dev_end, no handle, nothing logged)

load_udata(dev_end): 152 crypto perpetuals with DEV bars, 114 ever in top30/next30, 28.6 s. DEV top30 panel
78 symbols x 21,912 rows. Stage 1 with default options (24 truncation cuts + DEV end, 6 random start cuts +
the symbol cut):
| program | ok | fault | DEV direction changes | rows with weight | time |
|---|---|---|---|---|---|
| ucal_xs_momentum | yes | none | 4,516 | 18,985 / 21,912 | 4.7 s |
| kernel_noise_top30 | yes | none | 120,470 | 18,949 | 12.1 s |
| ucal_xs_carry | yes | none | 4,171 | 12,206 | 6.2 s |

## Timings (synthetic, single process)

Synthetic universe (52 coins + traps; 47-symbol top30 panel, 2019-12-31..2025-06-30), default options:
ucal_xs_momentum stage 1 3.3 s + stage 2 30.5 s; kernel_noise_top30 7.5 s + 36.6 s (G5 12 variants, G6 200
shifts, G8 next30, 3 VAL start cuts). Real data adds: research-hash check over all 2,712 stored tables 44 s
(every evaluation, core included), load_udata ~30 s (DEV) and about twice that under VAL; the real VAL panel
has 138 symbols (about 3x the synthetic one).
Universe calibration tasks (30-symbol synthetic panel, the ucalibrate dry-run source):
one null world (3 families x 20 screened draws, best submitted to full stage 1 and stage 2) 62.5 s; oracle
curve 5 rho values incl. world build 2.0 s; oracle power world (2 speeds x 2 levels, full gates) 40.8 s.
Estimate for 100 worlds per null and 100 oracle worlds per null: nulls 200 x 62.5 s = 12,500 s; rho tuning
(165 rho values per world, speed and null, about 0.2 s each, plus world builds) about 14,000 s; power
200 x 40.8 s = 8,200 s; total about 35,000 CPU-seconds (about 10 CPU-hours): about 2.5 to 3 hours on 4
workers (6 workers if memory allows: about 1.7 hours). Not started.

## Design decisions that differ from the order's literal text (for the audit)

1. IN PLAY = member AND its bar at that row is active (order: member). Literal reading: a member delisted
   mid-month (LUNA, May 2022) or any member's missing hour makes every cs_ result unknown, so the whole
   unit would be flat for the rest of the month. With the refinement the delisted member simply drops out
   (its next missing bar closes its position, C1). Locality is unaffected: activity at a row is row-local.
2. SEASONING = at least one active bar in each of the 91 days before the month (order: first active bar at
   least 90 days earlier). Needed so that a relisted name re-seasons (B4); it reads only a bounded window.
   Cost: a full-day archive hole restarts it too (the 2022 holes above).
3. A start cut that "removes a symbol's first bars" is placed 31 hours after the first bar of the panel
   symbol whose listing is nearest the middle of the DEV grid (inside a day, so inside a month); the other
   start cuts are random as for the core (and almost always fall inside a month).
4. Panel grid starts at UNIVERSE_START = 2019-12-31 00:00 (one day before DEV start, so the first DEV bar
   has a decision row); membership is unknown until the first month at least 91 days after it.
5. cs_ over a timeframe series uses the in-play symbols of the hour at which each bar becomes visible.
6. Benchmark for top30 (information only): equal-weight long of the in-play members.
7. Universe null worlds: mark and index bars = the synthetic last-price bars (wider wicks: conservative for
   liquidation); null B aligns the pool's last day with the world's last day and fills the few days before
   the pool start by iid draws. Core null worlds unchanged except that their (unused) index field holds the
   mark bars.
8. The membership builder's counts are produced by `data validate` (no handle, nothing logged), so no row was
   added to ledger/val_access_log.jsonl. `python -m omr.universe members` also exists and logs a
   `membership` handle row when run; it was not run.

## Items

A1 done; A2 done; A3 done (download 0 failures; data validate extended and PASSED); A4 done (one research
hash, streaming). B1-B4 done (tests: delisted padded trap, relisted re-seasons, TradFi and index never members,
membership unchanged by appended data and by cuts beyond its 91-day window; a cut inside it -> unknown).
C1-C3 done (universe engine + independent pure-Python reference, forced close at last close with cost).
D1-D5 done (unit header, in-play cs_, D3 `lookback_exceeds_seasoning` + `lookback_hours` in every trial row,
index_close, truncation and start-cut self-checks on universe panels incl. the symbol cut; a test shows the
start-cut check catches a membership that is known where its window was cut).
E done (G6 masking tested by spying on every shifted run; G8 = next30 Sharpe > 0).
F written and tested on synthetic panels (null A one source day for all symbols, null B one coin per day,
constant membership, protocol on one world, cross-sectional oracle market neutral with power); seal needs
both artifacts and applies decide_both (tests); NOT run for real.
G done (kernel_noise_top30 in the selftest's pipeline smoke; the synthetic selftest test and the disk-loader
selftest test pass; no real selftest run).
H done (tools/record_metrics.py; offline test with a fake archive; not run against the network; its tracked
log defaults to records/metrics_first_seen.jsonl, which does not exist yet).
Sandbox: top30 programs supported (not run: it writes ledger/sandbox_log.jsonl).
- Final suite: 715 passed, 0 failed, 0 skipped (369 s). omr/, tests/ and tools/ __pycache__ removed afterwards.

# FIX PASS (rulings R1-R5)

R1a done: seasoning = first active bar >= 90 days before the month (an active bar in [m-97d, m-90d]) and no
run of >= 7 day-blocks without an active bar reaching into the 90 days (a run that began earlier counts in
full); membership now reads 97 days. Edge tests: listed exactly 90 days before (in), one hour short (out),
6-day hole (in), 7-day hole (out), 7-day hole ending the day before the window (in), ending inside (out).
Real data: eligible 2022-02..07 = 128, 84, 131, 86, 131, 131 (March and May still lose the holed symbols
through the 95% activity rule, one month each).

R1b NOT merged (instruction: stop and tell). Scratch check (r1b_counterexample.py, R1b semantics
monkeypatched): 40 random start cuts each, disagreements: mixed 4h/8h funding_mean 0; mark_close with
missing mark bars 0; per-symbol holes 0; 60-day funding gap 0; 150-day funding gap then resumption 1
(cut at row 10872; 6,097 cells known in both runs with different values, from 3,023 rows after the cut).
Cause: funding_mean's knownness counts settlements since the frame start (unbounded memory), so after a
long gap the base run is known (old settlements) while the cut run is not. Every other function is bounded
by its static lookback, and the membership's 97-day read window keeps every cut run unknown for longer
than the 90-day lookback limit, so for them the sets are identical. With funding_mean known only when its
last n settlements lie within its own 8n hours (tested in the scratch only): 0 disagreements on the same
cases. The strict rule passes the same panels (tests/test_universe.py
test_strict_cross_sections_stay_local_with_holes_and_funding_gaps: per-symbol holes, a cut inside a hole,
a cut removing a symbol's first 30 hours, the 150-day funding gap; start and truncation cuts agree).

R2 done: tradable = member, active bar, latest funding settlement visible at the row no older than 2 x its
own interval; only tradable members are in play (weights 0, skipped by cs_). Member-months removed
(no tradable hour in the month): DEV ICPUSDT 9 (6,552 member-hours), TLMUSDT 1 (744); VAL none fully
(SOLUSDT 3 member-hours in one month). No _SETTLED folder is read.

Unit availability after R1a + R2 (hours with a top30 unit; strict = every in-play member clean over the
last L hours; R1b projection = at least 10 in-play members clean):
| region | hours | all members in play | strict 24h | 168h | 720h | 2160h | R1b-proj 720h | 2160h |
|---|---|---|---|---|---|---|---|---|
| DEV | 18,985 | 12,433 | 18,962 | 18,818 | 18,314 | 17,592 | 18,985 | 18,985 |
| VAL | 26,303 | 24,650 | 26,280 | 26,136 | 25,584 | 24,121 | 25,583 | 24,143 |
VAL loses one lookback after an hour with no active bar for any member (an exchange-wide gap): no rule
that keeps locality avoids that (the core treats such hours as known flat bars).

R3 done: estimate = max(top30 x A, next30 x (A - 3.125)) x rows x 8 + stored rows x 8 x columns + activity;
refusal `memory_insufficient` (uncounted stage-1 row) unless the OS reports >= 1.5 x. Needed columns only;
index_klines not loaded unless index_close is read; G8 (next30) evaluated and released first. Real sizes
(validation.json): rows 48,216, top30 137, next30 217 (the next30 panel is the larger), stored rows 6.1 M.
Estimates: momentum / reversal 1.98 GiB (refuse below 2.98 GiB free), carry 2.07 (3.11), kernel_noise_top30
2.63 (3.95). This machine reported 3.16 GiB free. Measured on synthetic panels (stage 2, default options):
top30 55 / next30 43: growth 340 MiB vs panel estimate 395 MiB, peak working set 1.0 GiB; top30 85 /
next30 115: growth 603 vs 693 MiB, peak 1.85 GiB. Extrapolated real peak for momentum: about 2.2 GiB.

R4 done: the sandbox never recomputed the research hash (it never called the evaluator's provider check);
now documented, and the top30 sandbox loads only the needed columns. Timed steps (DEV data): core sandbox
0.9-1.9 s; top30 sandbox 21.7 s (16.9 s loading 678 klines files + the panel tables). evaluate keeps the
44 s full check.

R5: add `!data/symbols.json` to .gitignore. Optional, for audit: the exchangeInfo response it was built
from (1.2 MB, sha256 pinned in symbols.json) needs three lines because data/raw is ignored as a folder:
`!data/raw/`, `data/raw/*`, `!data/raw/exchange_info_20261119T034149Z.json`.
- Fix-pass suite: 726 passed (full run) + the 3 locality tests added after it (test_universe.py 41 passed) = 729 tests, 0 failed, 0 skipped.

# FIX PASS 2 (S1-S5)

S1 done in EVERY unit: funding_mean is known only when its last n settlements fall inside the last 8n hours.
The core comparison with b12df97 stayed bit-identical (synthetic world: 14 programs, stage 1 + stage 2; real
DEV: stage 1 of the same 14) - tests/test_core_identity.py and test_baselines.py green with S1 applied.

S2 done: cs_ over the in-play (tradable) symbols whose input is known, known for them when >= 10 exist
(constant UNIVERSE_MIN_CS). Permanent tests: test_cross_sections_stay_local_with_holes_and_funding_gaps
(per-symbol bar holes, mixed 4h/8h funding, a 150-day funding gap then resumption; random start cuts, a cut
inside a hole, a cut removing a symbol's first 30 hours; truncation cuts; exact equality wherever the cut run
is known) and test_without_s1_the_funding_gap_breaks_cross_section_locality (the counterexample: with the
unbounded funding_mean the start-cut check fails - the assertion can fail).

S3: the market-wide hour is 2024-10-28 20:00 UTC: 320 symbols with a history, every row PRESENT with zero
trades, none absent (data validate count; it is the only such hour in DEV+VAL). Built: a bar is usable when
it has trades, or is present with zero trades and the run of non-active bars ending at it is <= 24 (absent
bars count in the run and are never usable); membership counts trades only; the history now runs to the last
stored row (causal: padding drops out after 24 bars, a held position closed at the frozen last price).

Unit availability after S2 + S3 (hours with a top30 unit; >= 10 in-play members whose last L hours are all
usable; the strict rule for comparison):
| region | hours | S2 24h | 168h | 720h | 2160h | strict 2160h |
|---|---|---|---|---|---|---|
| DEV | 18,985 | 18,985 | 18,985 | 18,985 | 18,985 | 17,592 |
| VAL | 26,303 | 26,303 | 26,303 | 26,303 | 26,303 | 26,280 |

S4 done: universe units in blocks (top30: 6 calendar months, cached; G8 next30: 3 months, streamed and
dropped), each evaluated from 97 days before the first hour of the month that holds its first decision;
block tables loaded per symbol and sliced to the block window (no data-layer cache on universe reads).
Portfolio gross in universe units summed sequentially in symbol-name order (np.sum's pairwise rounding
depended on the number of zero columns and broke bit-identity at the last bit; found by the block tests).
Engine: run_block_u carries positions, equity, the dead flag and the running funding total; a residual
position in a symbol outside a block's panel gets its own engine columns. Stage 2 keeps raw / known for DEV
rows only and checks start cuts block by block. Proof (tests/test_universe.py, synthetic): blocked ==
whole panel for W, raw, known and in-play (3 programs; block boundaries at half-years, inside HOLEUSDT's
3-day hole and inside RELISTUSDT's first month back; also a start cut inside the hole block and a
truncation inside that month); engine equity, pre, gross, net, events, funding, liquidation index and daily
returns; every gate value, metrics, info, detail and G8; stage 1 and stage 2 with blocks == one block.

Memory. Real sizes (data/validation.json): rows 48,216, top30 137 distinct (largest block 66), next30 217
distinct (largest 3-month block 78), activity 8.7 M rows. Stage-2 estimates: momentum / reversal 769 MiB,
carry 831 MiB, kernel_noise_top30 991 MiB (refuse below 1.5 x). Measured process peaks (synthetic universe
with churn, tables on disk loaded per block, default options): top30 85 / next30 115 distinct (largest
blocks 53 / 57): momentum 748 MiB (stage 2 60 s), kernel_noise_top30 852 MiB (105 s); before blocks the
same momentum run peaked at 1,852 MiB (whole panel, in-memory tables) and 922 MiB (blocks, no slicing).
Measured stage-2 growth is about 0.55 x the estimate, so the projected real peaks are about 0.85 GiB
(momentum) and about 1.0 GiB (kernel_noise_top30, the heaviest program).

Timings: real DEV (dev_end, no handle) with blocks: activity load 10 s (tables are now loaded per block);
stage 1 (25 truncation cuts, 7 start cuts) momentum 20.8 s, kernel_noise_top30 27.9 s, carry 21.6 s (carry
now has weights on all 18,985 DEV unit hours). Stage 2 on the synthetic universe: 60 s (momentum), 105 s
(kernel_noise_top30); a real stage 2 adds the 44 s research-hash check and per-block disk reads, and has
larger blocks, so about 2 to 4 minutes per top30 evaluation is expected. The universe calibration runs one
block per world (30 symbols), so its estimate is unchanged (about 10 CPU-hours for 100 worlds per null).
