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

# FIX PASS 3 (2026-11-20): one membership per run, block_overlap, lookback of stale leaves

Defect (coordinator's review, confirmed by scratchpad/fable_probe_blocks.py): blocks were NOT equal to the whole
panel for programs with a window over a cs_* result. Blocked._eval recomputed the membership from each block's own
rows, so the warm-up rows had no known unit and every window reading a cs_* value across the block start was
unknown for window - 2 hours after each block start (46, 70 and 166 hours in the probe).

T1 (omr/upipeline.py, omr/universe.py):
a. A RUN on rows r0..r1 (base, truncation cut, start cut, jitter variant, G8) computes its membership once
   (Blocked.run_membership = ud.membership(ns[r0], ns[r1])); every block of the run takes its in-play mask from
   it (Blocked._eval(..., mem)). Blocked.inplay() uses the run's membership; start_cut_agrees() uses the cut
   run's for the cut run and the base run's for the base run.
b. universe.block_plan: a block's symbols are the band's members (full-grid membership) of every month touched by
   the decision rows of its evaluated range s0..e-1, warm-up included; no dependence on the previous block.
   Residual engine positions keep using Blocked._extra.
c. G8 (next30_score) goes through Blocked.unit, so it follows the same rule.
d. upipeline raises at import unless OVERLAP_HOURS (97 x 24 = 2,328) >= LOOKBACK_MAX_HOURS + 168 (2,328).
e. Self-check block_overlap (Blocked._runs / _check_overlap / _overlap_tail): in every blocked run, for each block
   after the first evaluated one, on the rows from (its first evaluated row + prog.lookback_hours) to the row
   before the block that the previous block also evaluated, raw and known are compared by symbol on the global
   columns (a symbol outside one block's panel must be unknown in the other); only the previous block's tail is
   kept. A mismatch raises KernelFault("block_overlap"): stage1_u returns code kernel_fault, fault block_overlap
   (uncounted), stage2_u returns status kernel_fault, reason block_overlap (counted).
The coordinator's probe after T1: all five programs IDENTICAL (control, sma over cs_demean, hold on cs_rank,
window over cs_mean, lag of cs_rank).

Checked and REFUTED before building on it: "a timeframe window counts complete bins only, so its memory is
unbounded in time across holes". Universe panels (and core frames) sit on a contiguous hourly grid: every bin
exists; a bin with an unknown hour is an UNKNOWN bar, not a dropped one, and to_h1 never falls back to an older
bar. A constructed case (scratchpad/tf_bins_counterexample.py: a January member with eight 6-day holes in
Oct-Nov, sma(daily(close), 70), lookback 2,039 h) was identical under half-year blocks. No stop was needed.

T3 (omr/lang.py lookback_hours): leaf hours: an hourly field, hour, weekday 1; mark_close, index_close 7 (the
6-hour staleness); funding8h 8; btc(f) = leaf f (was 1 for every btc(...)). A timeframe of h hours over a leaf of
l hours: 2h - 2 + l (was 2h - 1, which ignored the leaf's staleness under a timeframe). The rest of the table was
checked against the interpreter's knownness rules (known_run widths): rolling n - 1, ema 5n - 1, rsi and atr 10n
(m + 1 rows), lags and realised_vol n (n + 1 rows), corr n - 1, hold h - 1, funding_mean 8n (S1), windows over a
timeframe series (n - 1) x h, cs_* none, elementwise / where / comparisons the max of their inputs: no other row
under-reports. No existing program's lookback changed (strategies/*.omr and omr/programs/*.omr).

T2 tests (tests/test_blocks.py, all permanent):
- test_whole_panel_equals_blocks_for_windows_over_cross_sections (6 programs: sma over cs_demean, ema over cs_rank,
  hold on cs_rank, a window over cs_mean, zscore over cs_demean of a daily series, a program at the 2,160-hour
  limit): W, raw and known equal for one block, the production half-years, custom boundaries (mid-month, inside
  a hole, inside a member's first month back, a 10-day block; blocks built lazily) and the original FullPanel
  path; next30_score equal for months=None and months=3 (two programs).
- test_the_lookback_limit_program_is_at_the_limit: lookback_hours == 2,160.
- test_stage1_and_stage2_with_blocks_equal_one_block: W, raw, known of stage 1; every gate, metric, info and the
  daily returns of stage 2.
- test_the_old_per_block_membership_is_caught: with Blocked._eval monkeypatched to recompute the membership per
  block, the blocked run differs from the whole panel or raises block_overlap.
- test_block_overlap_fires_when_the_recorded_lookback_is_too_short (lookback forced to 3 h, true 144 h) and
  test_block_overlap_fires_when_a_window_under_reports (sma's extra rows forced to 0: recorded 49 h): both end
  through evaluate_file as stage-1 kernel_fault, fault block_overlap, nothing counted.
- test_block_overlap_is_silent_on_kernel_and_strategy_programs: every omr/programs and strategies/*.omr program
  that parses as top30 (the four top30 kernel programs, kernel_kitchen_sink, kernel_noise_portfolio,
  gen001_relmom_pair) runs blocked with no fault and equal to one block.
- test_lookback_is_a_true_upper_bound (10 programs: daily(mark_close), h4(index_close), daily(btc(mark_close)),
  btc(mark_close), sma over daily(mark_close), rsi, ema over mark_close, atr, hold over lags and mark_close,
  funding_mean + realised_vol; frames with mark and index gaps; 5 cuts each): from row c + lookback - 1 on the
  cut run is known exactly where the whole run is, with equal values.
- test_the_old_timeframe_rule_under_reports: with 2h - 1 for daily(mark_close), a cut before a mark gap is
  unknown in the cut run at a row the old lookback calls complete (the assertion can fail).

T4: data validate PASSED (0 failing counts; rewrote data/validation.json). Block sizes (real data): top30 12
six-month blocks, largest 60 symbols (was 66 with the previous-block union); next30 23 three-month blocks,
largest 88 (was 78: warm-up months' members are now included). Stage-2 estimates (real sizes): momentum /
reversal 730 MiB, carry 789 MiB, kernel_noise_top30 936 MiB. Measured (synthetic universe of 140 coins with
churn, tables on disk loaded per block, default options, ucal_xs_momentum, top30 85 / next30 115 distinct,
largest blocks 52 / 60): process peak 737 MiB, stage 2 107 s (the machine was shared with the auditor's run).
Unit availability unchanged (DEV 18,985 and VAL 26,303 unit hours, 100% at every lookback under S2).
Full suite after this pass: 759 passed, 0 failed, 0 skipped (906 s). python -m omr.ledger verify: OK.

# FIX PASS 4 (2026-11-20): rulings U1-U8 (audit round 6) and the follow-up rulings R-A, R-B

Base 973e413 (kp015-build). Build and test only: no re-key, calibration, seal, selftest or `omr.universe
members`; no git writes; the ledger untouched. `python -m omr.data universe` (three runs) and `data validate`
were run for U4 / R-A (they rewrote data/manifest.json, data/validation.json and stored tables).

U5 (omr/data.py): the sha256 of data/symbols.json (the file on disk, when the manifest stores the universe) is
folded into the research hash after the tables (compute_research_hash, hashes_streaming, research_hash_from_disk,
snapshot, download_universe) and into data_fingerprint, so a rebuilt table changes every trial id and unbinds
validation (and the seal). tests/test_data_integrity.py::test_u5_the_symbol_table_is_in_the_research_hash_and_the
_fingerprint: one class changed, then one `until` changed: two new research hashes, a new fingerprint,
validation_ok() False, a new trial id; the original file restores all of them. conftest make_disk_data folds it.

U4 + R-A (omr/data.py): `data universe` builds each universe symbol from its monthly files, finds every hour
missing inside its life (klines gap rows; grid hours without a mark or index bar), fetches the daily files of the
same archive for those days (fetch_daily: the published CHECKSUM is required and stored beside the zip and
re-verified at every use; a 404 is remembered by a marker; a file without CHECKSUM is not stored), and fills only
hours the table does not hold, inside the life (fill_from_daily). An hour already stored must be equal in every
column to the daily row, else DailyRevision: the run stops and nothing is written (tables are staged as
.parquet.new and moved only when no fetch failed and no revision was found). The sha256 of every daily file used
is pinned in the table's manifest entry (daily_files) with daily_rows_filled. R-A: the ten core / extended symbols
are filled by the same rule inside their stored klines grid (fill_core_tables: same snapshot end, no top-up, the
stored index table kept, every stored manifest key kept); `data update` (snapshot) applies the same fill so a
later update reproduces the filled tables. A table nothing was filled in is not rewritten (its pin stays).
Runs: run 1 stopped on 12 transient fetch failures (all KAVAUSDT; nothing written; a probe then fetched them
fine); run 2 stored the universe fill (1,302 tables rewritten); run 3 (after R-A) rewrote 13 tables (the ten mark
tables, LTCUSDT / SOLUSDT / XRPUSDT klines). No revision anywhere (every compared held hour equal). Daily files:
3,058 present and CHECKSUM-verified, 29,328 absent (404). research_hash now 28d9084a8c5c7659... (was d1b6ce5b8d0a0380).
Missing hours inside the lives, all stored symbols (before -> after), by region:
- klines: DEV 5,856 -> 0; VAL 1,970 -> 194; after VAL 57 -> 57 (60 symbols / 335 symbol-days -> 12 / 17).
- mark: warm-up 3,166 -> 3,166; DEV 9,021 -> 0; VAL 8,611 -> 31; after VAL 15,809 -> 41.
- index: warm-up 3,166 -> 3,166; DEV 1,197 -> 0; VAL 51,941 -> 36,257; after VAL 676,148 -> 662,684.
Core / extended symbols (hours filled by region): LTCUSDT, SOLUSDT, XRPUSDT klines DEV 120 each (2022-02-26..28,
2022-04-01..02); every other core klines table unchanged (BTCUSDT and ETHUSDT klines did NOT change). Mark bars
filled: BTCUSDT 216 (DEV 120, VAL 72, after VAL 24); ETHUSDT 72 (VAL 48, after VAL 24); AVAX, BNB, LINK 216
(DEV 120, VAL 72, after 24); SOL, XRP 192 (DEV 120, VAL 48, after 24); ADA, DOGE, LTC 72 (VAL 48, after 24).
BTCUSDT mark 2,538 and ETHUSDT mark 628 warm-up hours stay missing (before the archive's mark history; daily
files absent), and the same for their index bars.
Holes that could not be filled, up to VAL end: klines AERGOUSDT 2025-04-16 (11 h), BNXUSDT 2023-02-22 (14),
CTKUSDT 2025-04-30 (10), CVCUSDT 2025-05-16 (8), ICPUSDT 2022-09-22..27 (122), MAVIAUSDT 2025-03-26 (17),
TLMUSDT 2023-03-30 (12); mark AERGO, CTK, CVC the same days (11, 11, 9 h); index: 2019-09..12 pre-history and whole
months the archive does not have (DEV+VAL: BTCSTUSDT 16,820 h, COCOSUSDT 7,252, HNTUSDT 7,252, TOMOUSDT 4,321,
INITUSDT 196, SXTUSDT 148, NEWTUSDT 120, BABYUSDT 117, AERGO / CTK / CVC 11 / 11 / 9); after VAL 29k symbol-days,
mostly whole months of about 94 delisted names. The ACTIVE and seasoning rules are unchanged.
Membership (DEV bars only, no VAL row read): eligible 2022-02..07 = 128, 128, 131, 131, 131, 131 (was 128, 84,
131, 86, 131, 131). LUNAUSDT top30 every month 2021-05 .. 2022-05 (was 2021-05 .. 2022-02 and 2022-04).
SOLUSDT next30 2021-01, 2021-02, top30 every month 2021-03 .. 2022-07 (was out in 2022-03 and 2022-05; SOL ranks
4-5). data validate PASSED (0 failing counts); distinct top30 DEV 75 (was 78), DEV+VAL 134 (was 137); unit
availability unchanged (DEV 18,985, VAL 26,303 unit hours, 100% at every lookback).
Tests (tests/test_holefill.py): a hole filled from its daily file and a day without one staying a hole; a held
hour that differs stops (DailyRevision); only checksum-verified files are read, a bad checksum raises, nothing
outside the life is added; fetch_daily needs the CHECKSUM and remembers a 404 (no second request); the per-symbol
path counts holes before and after; R-A: a core table filled, every other row bit-identical, the grid and the
meta keys kept, a revised held bar stops.

U1 + R-B (omr/upipeline.py g6_books, g6_books_tie, g6_paired_p, ugates; constants G6_PAIRED_BOOK_TIE 1e-12,
G6_PAIRED_SHARPE_MARGIN 1e-9): as ruled. Detail keeps actual_val_sharpe_restarted (unmasked), adds
actual_common_mean (mean A_k Sharpe), shifted_mean (mean S_k), shifted_p95, ties. R-B: a pair within 1e-12 on
every cell is a tie (S >= A, no S run); otherwise S >= A when Sharpe(S) >= Sharpe(A) - 1e-9.
Tests (tests/test_g6_paired.py): random churn calendar (5 shifts, rows under 10 names and re-centred rows both
present): A_k and S_k hold exactly the mask names on every live row, their row nets equal the unmasked rows'
nets (1e-12), rows under 10 common names are flat in both, gross never exceeds the unmasked row's; the same on a
56-symbol synthetic churn panel; bit-identity with the pass-3 rule on a constant-membership 14-symbol panel (p,
the unmasked actual, the shifted mean equal; no tie and no shifted Sharpe inside the 1e-9 band, so the margin did
not change p); the spy: no weight on a symbol out of play or without a bar in any G6 run; ties and margin only
raise p.
STOP CASE (R-B): the equal-weight basket on the churn panel gives p = 0.524, not 1. Cause: 27 VAL rows where a
member is in play at the decision row but has no bar at the execution row (delistings). A_k's own set (tradable
now) drops that name's weight (row net 29/30) while S_k's own set (in play at the source row) keeps the full net
(1), so the books differ by about 1/30 per row there (max |A - S| 0.003-0.007): no tie, Sharpe(S) - Sharpe(A)
about +-1e-3. With A's own set = in play at the decision row (symmetric with S), 20 of 20 shifts are ties (p = 1);
scratchpad scripts rb_basket_diag.py and rb_variant.py. The basket test is xfail(strict) pending a ruling;
test_u1_the_basket_counterexample_to_r_b documents the case.

U3 (omr/interp.py cross_inplay): a cs_* is computed across the in-play symbols with a known AND finite input; the
at-least-10 rule counts those; an in-play symbol with a known non-finite input stays known with value NaN. Core
_cross unchanged. tests/test_cs_nonfinite.py (8): 0/0 for one symbol keeps the row (11 finite values equal the
direct cross-section of the 11, the 0/0 symbol a known NaN) for cs_mean / demean / scale / rank; a zero-volume
hour for every symbol makes the row unknown for everyone; three symbols 0/0 with 11 finite: known, the three NaN;
five 0/0 (9 finite): unknown. LANGUAGE section 10 updated.

U6 (omr/probe.py universe_panel): top30 programs are probed on 12 deterministic synthetic symbols (core A and B
first), all in play, unit known, through the in-play cross-section code; the core probe is unchanged.
tests/test_probe_top30.py (5): abs(cs_rank(x)) and cs_rank(x) * cs_rank(x) parse in top30 (and are rejected by the
two-symbol core probe); cs_rank(x) / cs_rank(x) and cs_demean(x) + hour / hour are still rejected; panel shape.

U7: funding8h is known only while the latest visible settlement is at most 2 x min(its interval, 8) hours old, in
every unit, computed where frames and panels are assembled from the full funding table (datasets.assemble_frame
column funding.fresh; FullPanel col funding.fresh = the R2 freshness); universe.funding_fresh caps the interval at
8 hours for R2 too; lookback leaf funding8h = 17. tests/test_funding_fresh.py (7): a 72-hour gap makes funding8h
unknown from 17 hours after the last settlement to the next one, and a window over it waits n rows; a 24-hour
interval is capped (known 16 hours); universe panels carry the same freshness and a window over funding8h waits
after a 3-month funding gap; lookback 17 / 36 / 17 / 37. tests/test_core_identity.py: 3 passed (synthetic world
and REAL DEV frames, after the R-A data and U7): the core unit stays bit-identical to b12df97 (no core funding gap
over 2 x min(interval, 8) in DEV for the ten).

U8: sandbox appends its log row before printing anything (status ok / kernel_fault with the fault); kernel_lock.
rekey copies seal keys with .get; Blocked counts the known cells block_overlap compared (stage-1 result
block_overlap_cells; the pending row's stage1 dict and top level, the final row for top30). Documents K4-K7:
costs "last usable close", inplay_matrix docstring, the research hash covers symbols.json, rekey. Tests:
tests/test_sandbox_log.py (2), tests/test_ledger_lock.py::test_u8_a_text_only_rekey_keeps_a_seal_made_before_the_
universe_keys, tests/test_blocks.py::test_u8_block_overlap_cells_are_counted_and_recorded (> 0 with blocks, 0 for
one block, equal in the evaluated and pending rows). Memory estimate: G6's VAL term 24 -> 52 bytes per cell.

U2 (omr/ucalibrate.py, rewritten): null worlds on the REAL membership calendar. Panel = every symbol ever in top30
from UNIVERSE_START to VAL end (the kernel's own rule on the real activity of every crypto perpetual, read with
the logged calibration handle; 134 symbols on the current data). USource keeps each symbol's real rows as
concatenated arrays (price ratios open / previous close, high / open, low / open, close / open; the five volume
columns; gap and active flags; the real Activity as activity_of computes it; funding settlements; per local day
whether all 24 hours are active and the day's settlements) and is shared with the workers through
multiprocessing shared memory (no copy per worker). UWorld draws one world (null A: one source day per world day
from the days UNIVERSE_START .. VAL end, shared by all symbols; a symbol not fully active on it takes a personal
fallback day from its own fully active days, generator [seed, 21, symbol index]; funding keeps the real day's
settlement times and intervals and takes the source day's rates in order, cycled, a source day without a
settlement replaced by one with, generator [seed, 23, symbol index]; null B: real order, one coin per day for all
symbols mirrors each symbol's demeaned path, funding unchanged) and builds a symbol's tables only when a block
asks for them (prices cumulated from the real first open; a present zero-trade bar flat; absent bars absent; mark
= index = the synthetic last-price bars of the present rows). world_udata gives the kernel the REAL Activity, so
its own membership rule reproduces the real calendar; dev_view is the same world under DEV end. Screening,
stage 1, stage 2 and the oracle run on the production six-month blocks; the oracle's z is demeaned across the
symbols with a return and standardised per symbol, weights over the in-play symbols. ConstUData is gone (a copy
lives in tests/test_universe.py as a test panel). The unlocked dry run builds a fully synthetic churn universe
(synthetic_churn_universe: staggered listings and delistings, volume = own price over its 90-day mean x a
mean-reverting regime; 170 symbols -> 149 ever in top30).
Tests (tests/test_ucalibrate.py, 11): families; for null A and B the world keeps every real row (index, the five
volume columns, is_gap, funding times and intervals) and gives exactly the real top30 members per month and the
same in-play mask (usable flags, unit sizes); null A: the world's day where a symbol is fully active, else one of
its own full days, close / open equal to the source hour's; zero-trade bars flat, absent bars absent, prices start
at the real first open; null A funding takes the source day's rates (cycled) on the real calendar; null B one coin
per day for every symbol (share 0.35-0.65), funding unchanged; the DEV view equals the full world under DEV end;
the shared-memory source gives identical worlds; one null world runs the protocol and every Blocked in it uses
the production months; the oracle on the same worlds is market neutral over in-play symbols, foresight pays, and
evaluate_weights_u runs on production blocks.
Measurement (scratchpad u2_measure.py; each task in its own spawned process attached to the shared source like a
worker; synthetic churn universe, 149 symbols ever in top30, 3.67 M source rows, source arrays 309 MiB shared):
- null world A 488.5 s, peak working set 1,318 MiB (peak private 1,440 MiB); null world B 511.3 s, 1,340 MiB
  (1,459 MiB). A worker's base after imports: 578 MiB private; after attaching the source 256 MiB working set.
- oracle (engine columns only in the oracle's blocks, a change made after the first measurement cut the peak from
  1,453 to 1,022 MiB with identical Sharpes): curve with 2 rhos 17.6 s, with 81 rhos 52.2 s (world + oracle build
  16.7 s, 0.44 s per rho), peak 1,022 MiB (1,168 private); power task (4 oracle evaluations with the paired G6,
  200 shifts) 472.8 s, peak 1,202 MiB (1,321 private).
- per oracle world: 2 speeds x (3 tuning calls x 16.7 s + 165 rhos x 0.44 s) + power = about 718 s.
Estimates (null world 500 s, oracle world 718 s; worker-hours, then wall time): (a) 150 worlds per null and 100
oracle worlds per null: 2 x 150 x 500 + 2 x 100 x 718 = 293,600 s = 81.6 worker-hours: about 20.4 h with 4
workers, 81.6 h with 1. (b) 300 and 200: 587,200 s = 163 worker-hours: about 41 h with 4 workers, 163 h with 1.
Workers: a worker peaks at about 1.46 GiB private (1.34 GiB working set), the shared source adds 0.31 GiB once and
the parent about 0.5 GiB. This machine has 14.8 GiB and 4 cores / 8 threads: with the auditor and other processes
closed (about 11 GiB free) memory allows 6-7 workers and the 4 cores make 4 the useful number; with today's
1.6-2.6 GiB free only 1 worker is safe.
Memory estimates for top30 trials (R3, new validation sizes, G6 term 52 bytes per VAL cell): ucal_xs_momentum /
reversal 809 MiB (was 730), carry 866 (789), kernel_noise_top30 1,012 (936); largest blocks top30 60, next30 88.

Full suite after this pass: 801 passed, 1 xfailed (the R-B basket test, strict), 0 failed, 0 skipped (1,155 s).
python -m omr.ledger verify: OK (ledger untouched). Core unit: tests/test_core_identity.py passed (synthetic world
and real DEV frames).
Files touched: omr/constants.py, data.py, datasets.py, evaluate.py, interp.py, kernel_lock.py, lang.py, probe.py,
sandbox.py, ucalibrate.py, universe.py, upipeline.py; tests/conftest.py, test_blocks.py, test_data_integrity.py,
test_ledger_lock.py, test_ucalibrate.py, test_universe.py and new test_cs_nonfinite.py, test_funding_fresh.py,
test_g6_paired.py, test_holefill.py, test_probe_top30.py, test_sandbox_log.py; CONSTITUTION.md, LANGUAGE.md,
KERNEL_PROPOSALS.md, STATE.md, notes/kp015_build_evidence.md; data/manifest.json, data/validation.json and the
stored tables (data universe / validate).

# FIX PASS 5 (2026-11-20): R-C paired lag G6, R-D calibration run, R-E null funding sign, R-F null A pools, R-G hole-fill hardening

Base e4e44e2 (kp015-build). Build and test only: no re-key, real calibration, seal or selftest; no git writes;
the ledger untouched; no program evaluated on real rows after DEV end; no VAL membership names in any output.

R-C (omr/upipeline.py g6_lags, g6_books, ugates): G6 in universe units is a causal paired LAG test. VAL row i is
decided at grid row g0 + i (g0 = VAL start - 1) and executed at VAL start + i; D = in play at the decision row,
ok = D and a usable bar at the execution row. Lags: perm_n integers uniform on [720, L // 2] from rng_perm
(KernelFault when L // 2 < 720 or fewer than L // 2 rows exist before g0). For lag k the source of row i is grid
row g0 + i - k (views of the whole-grid W and in-play mask; rows before VAL start for i < k; nothing after the
decision row, no wrap-around). mask = ok and in play at the source row; A_k = W[g0 + i] on mask, S_k =
W[g0 + i - k] on mask; symmetric re-centring to the net of each book's own full row (A: in play at its decision
row; S: in play at the source row) when that set has a name outside mask; flat under 10 mask names. Ties
(1e-12), the 1e-9 margin and the reuse of the plain actual run are unchanged. Detail adds lagged, lag_min,
lag_max (the smallest and largest lag drawn). Core G6 (omr/pipeline.py) unchanged. Memory estimate: G6's VAL
term 52 -> 42 bytes per cell (the actual and source rows are views now).
Tests (tests/test_g6_paired.py, 10, synthetic):
- T1 random whole-grid churn calendar, 6 lags (one reaching 1,500 rows before VAL): both books hold exactly the
  mask names on every live row; row nets equal the own rows' nets (A over D[i], S over the source row's in-play
  set, 1e-12); flat rows flat in both; gross never above the own row's gross; re-centred and flat rows occur.
- T2 causality, two inputs identical up to grid row r and different after it (membership, in-play flags,
  weights, bars): for 5 lags, A_k and S_k are identical on every VAL row executed at or before r. Negative
  control in the same test: the pass-4 circular form fails the check (leaks > 0).
- T3 a 14-symbol panel without churn and with every bar: exactly 1 + N engine runs on the VAL window (A_k is the
  plain actual for every lag), A_k = the plain actual and S_k = W[g0 + i - k] under ok, and the G6 value equals a
  plain lag test computed directly in the test; no tie and no lagged Sharpe inside the 1e-9 band.
- churn panel (56 symbols): book properties on 6 production lags, with re-centred rows.
- T4 the equal-weight basket on the churn panel (it has rows where a member has no bar at the execution row):
  p == 1.0 exactly (strict, no xfail; the pass-4 counterexample test removed).
- T5 the spy: no weight on a symbol out of play or without a bar in any G6 run; the detail keys.
- T6 500 lags inside [720, L // 2]; KernelFault with too little history before VAL and with a too short VAL.
- T7 a planted-foresight book (UOracle, rho 0.9, one-day speed) on the churn panel: p == 1 / (N + 1).
- ties and the margin only raise p.
Documents: CONSTITUTION section 13 (the lag form in plain words, why no future row; the calibration bullet:
the universe nulls keep the real membership calendar while prices are resampled, so they cannot show an effect
that needs membership to follow price, and the causal G6 is what excludes it), LANGUAGE section 10, KERNEL_
PROPOSALS KP-015, STATE.

R-D (omr/ucalibrate.py):
- D1 resume: every finished task (null world, oracle curve, oracle power) is appended and fsynced to a partial
  file (default ledger/ucalibration_<semantic16>.partial.jsonl; <out>.partial.jsonl for a dry run with --out)
  whose first line is the header (protocol version, semantic hash, research hash, families' sha256, seeds, world
  counts, levels, speeds, perm_n, draws, rho grid). Same header: finished tasks are skipped and their rows reused
  (a torn last line is ignored); another header: refused with a message and exit code 5 unless --restart. Rows
  are stored and used as cleaned JSON, so a resumed run and an uninterrupted one compute from identical objects.
  The partial file is deleted after the artifact is written (and logged for a real run). .gitignore:
  ledger/*.partial.jsonl.
- D2 memory preflight before the pool: available memory (upipeline's probe) against workers x WORKER_PEAK_BYTES
  (1.6 GiB, from M1) + the shared source; if it does not fit it prints how many workers fit and exits with code 4
  unless --force. --workers 0 runs every task in-process (tests, small dry runs).
- D3 the oracle is tuned and evaluated at true Sharpe 1.5 only (ULEVELS); oracle_summary / verdict_from_rows /
  decide_both use the levels present in each unit's artifact (on the core rows the summary equals
  omr.calibrate.oracle_summary). omr/calibrate.py and the core artifact are untouched.
- D4 defaults --worlds 200 --oracle-worlds 100 --workers 4.
- D5 progress lines: done / total (resumed count), elapsed, estimated time left in the phase.
- D6 UWorld.source_day_stats(): a deterministic count per world (the cache-dependent counter is gone).
Tests: tests/test_ucalibrate.py (Partial header binding and a torn line; an interrupted tiny synthetic dry run
- one family, one world per null, one oracle world, a 4-point rho grid, killed by an exception after three
recorded tasks - resumed to an artifact equal to the uninterrupted run's apart from created_at and wall_seconds,
the partial file removed, oracle rows and summary at level 1.5 only; the memory preflight refuses with exit code
4 and names how many workers fit; the defaults; source-day stats deterministic and independent of the table
cache); tests/test_ledger_lock.py::test_d3_decide_both_reads_the_levels_present_in_each_unit.
D6 numbers: see R-F (the share after R-F replaces the one asked for here; before R-F, on the same synthetic
source, 57.9% of the members-and-others symbol-days used the shared source day and 42.1% a fallback).

R-E (omr/ucalibrate.py UWorld): after the funding table is built as before (null A: the source day's rates for
that symbol; null B: the real rates), every rate is multiplied by a fair sign coin of its settlement hour, drawn
by the world's own generator ([seed, 31]) for every hour of the world, so every symbol settling at the same time
gets the same coin and coins at different times are independent. Oracle worlds are the same worlds.
PROTOCOL_VERSION 3. Tests (tests/test_ucalibrate.py::test_r_e_funding_sizes_kept_signs_shared_per_settlement_time,
both nulls): |rate| equals the construction without the coin row for row (and the recorded rates under null B),
intervals kept; two symbols settling at the same time carry the same factor and both signs occur; the same world
seed gives the same table and another seed a different one; the mean product of consecutive sign factors over a
symbol's table is below 0.05 in absolute value. Documents: the module docstring and the CONSTITUTION calibration
bullet (core calibration unchanged and why: core carry family mean VAL Sharpe -0.30 under null A, +0.07 under
null B; Tier-1 passes under null B 0, 1 and 3 of 300).

R-F (omr/ucalibrate.py USource._build_pools, UWorld): for every calendar month m, POOL(m) = the source days
(UNIVERSE_START .. VAL end) on which every top30 member of m (the kernel's own rule on the source, the
schedule every world reproduces) has 24 active hours, built once in the source and shared with the workers
(arrays day_pool, pool_days, pool_off). Every null A world day of month m draws its source day iid from POOL(m);
a month with no unit or a pool under 90 days (POOL_MIN_DAYS) draws from the whole period as before; a symbol
not fully active on the drawn day uses its personal fallback. The artifact's protocol block records
null_a_source_days: min_pool_days 90, pooled_months, months_whole_period_pool, smallest and median pool days;
the run header binds pool_min_days.
Tests (tests/test_ucalibrate.py): in every pooled month no member is on a fallback day and every member uses
the world's drawn day; the draws are deterministic per seed, change with the seed, lie in the month's pool, and
whole-period days stay in [UNIVERSE_START day, VAL end]; the kernel's rule on the world still gives the source's
top30 members month for month and the same in-play mask (both nulls); the DEV view still equals the full world.
Report (dry-run synthetic source, 149 symbols ever in top30, null A world 11000; mean over 62 months of the mean
pairwise correlation of that month's members' daily returns): source 0.359; null A before R-F 0.151; after R-F
0.359. Pools: 62 months pooled, 9 months on the whole-period pool (the 9 months before the first unit), smallest
pool 90 days, median 201. Symbol-days with an active bar: shared source day 56.7% before, 94.6% after (fallback
43.3% -> 5.4%, mostly non-members).

R-G (omr/data.py), none of which changes a stored row: G1 a `.missing` marker is written only for a day at least
7 days older than the request (MISSING_MARKER_MIN_AGE_DAYS; a younger 404 returns missing and is asked again).
G2 a daily file used for a table whose manifest entry pins a sha256 for that day must equal the pin, else
DailyPinMismatch (a DailyRevision: `data universe` stops before anything is written; fill_core_tables and the
snapshot raise). G3 commit_tables: the new manifest is written as manifest.json.new, a journal
(data/.commit_journal.json) lists the files, each replaced table is kept as <name>.parquet.old, the new tables are
moved in, the new manifest replaces the old one (the commit point), then the kept files and the journal are
removed; `data universe` now computes the research hash from the staged files before anything is moved, and
`data download / update` stage their tables and use the same commit. recover_commit() runs at the start of every
`python -m omr.data` command: before the commit point it restores ALL OLD (kept files back, new files and the new
manifest removed), after it ALL NEW (kept files removed), with one log line saying which.
Tests (tests/test_holefill.py): G1 a 5-day-old 404 leaves no marker and is asked again, a 7-day-old one is
remembered; G2 a matching pin fills, a different pin raises (also through fill_core_tables); G3 a scratch data
folder with a crash injected at each of the 8 commit steps (new manifest written, journal written, each of two
tables kept / moved, manifest replaced, cleanup): recover_commit gives ALL OLD for the six steps before the commit
point and ALL NEW for the two after it, every manifest entry's file matches its pin, no journal, kept or staged
file is left, and a second call finds nothing to do; an uninterrupted commit; `python -m omr.data` calls
recover_commit before its command.
Research hash before and after this pass: 28d9084a8c5c765930e9e77eadba8b1952e5c49c7f917f0493dac3ab24009410 (the
e4e44e2 value); `python -m omr.data verify`: OK; no file under data/ changed.

M1 (scratchpad u2_measure.py, each task in its own spawned worker attached to the shared source; dry-run
synthetic universe, 149 symbols ever in top30; final code):
- null world A 552.7 s, peak working set 1,255 MiB, peak private 1,382 MiB; null world B 509.7 s, 1,219 MiB
  (1,397 MiB private); oracle power task (level 1.5 only, 2 evaluations) 314.4 s, 1,103 MiB (1,250 MiB).
- oracle curves (unchanged by this pass, pass-4 measurement): 16.7 s per world and oracle build, 0.44 s per rho;
  level 1.5 only: 81 + 41 + 1 rhos and 3 builds per speed, about 104 s, so about 208 s per oracle world for both
  speeds; an oracle world about 522 s in all; a null world about 531 s (mean of A and B).
- 200 null worlds per null and 100 oracle worlds per null: 2 x 200 x 531 + 2 x 100 x 522 = 316,800 s = 88.0
  worker-hours, about 22 h with 4 workers. WORKER_PEAK_BYTES for the preflight: 1.6 GiB (measured 1.40 GiB).
M2 phase breakdown (seconds):
- null world A (3 families): world build 0.0 (built per block), block builds 64.0 (9 Blocked panels), 20
  screening draws x 3 families 19.8, stage 1 14.9, stage-2 evaluation and self-checks 10.6, G5 variants 22.5
  (36 variant signals; their engine runs are in the next item), gates other than G5 / G6 48.8 (base, stress,
  G5 engine runs, G7, benchmark), G6 371.9 with 1,203 engine runs on the VAL window (3 x (1 actual + 200 A_k +
  200 S_k): no lag reused the plain actual on the churn calendar, no tie), everything else 0.1.
- oracle power task: block builds 29.8, oracle setup 0.5, gates other than G6 30.2, G6 253.8 with 802 engine runs
  (2 x (1 + 200 + 200)), everything else 0.0.
M3 stage-2 memory estimates (data/validation.json sizes; G6 term 42 bytes per VAL cell): ucal_xs_momentum 778 MiB,
ucal_xs_reversal 778 MiB, ucal_xs_carry 835 MiB, kernel_noise_top30 982 MiB (pass 4: 809 / 809 / 866 / 1,012).

Full suite after this pass: 826 passed, 0 failed, 0 xfailed, 0 skipped (1,234 s). python -m omr.ledger verify: OK
(ledger untouched). No file under data/ changed (research hash 28d9084a8c5c7659...).
Files touched: omr/data.py, omr/ucalibrate.py, omr/upipeline.py; tests/test_g6_paired.py, test_holefill.py,
test_ledger_lock.py, test_ucalibrate.py; CONSTITUTION.md, LANGUAGE.md, KERNEL_PROPOSALS.md, STATE.md, .gitignore,
notes/kp015_build_evidence.md. (audits/AUDIT_LOG.md: the coordinator's own entry, not touched here.)

# FIX PASS 6 (2026-11-20): per-unit G6 threshold (R-H), incomplete artifacts, partial-file integrity, docs, run order

Base 32e32e0 (kp015-build). Build and light tests only so far (memory reserved for the auditor): no re-key,
calibration, seal or selftest; no git writes; the project ledger untouched; STATE.md, audits/ and kernel.lock not
touched.

F1 (R-H). omr/ucalibrate.py: decide_both(core_art, uni_art) gives each unit its own decision from its own stored
rows (unit_verdict -> verdict_from_rows -> calibrate.decide) and returns per_unit (both verdicts), chosen_threshold
{"core": x, "top30": y}, null_pass_rate and power_at_1_5_chosen per unit, and STOP with a reason naming the unit
when either unit has no qualifying threshold, power below POWER_MIN or a level outside its bound (RULE_PER_UNIT).
omr/kernel_lock.py: UNITS_SEALED; seal writes g6_threshold = {"core": x, "top30": y} (null_pass_rate and power_at_1_5
per unit) and refuses with the per-unit verdicts on STOP; thresholds_of / format_threshold; require_sealed returns
the mapping and exits (code 4, "KERNEL SEAL HAS NO PER-UNIT G6 THRESHOLD") when the stored value is not a mapping
with a number for both units; `kernel_lock verify` and omr/status.py print both thresholds. omr/evaluate.py: under
the sealed lock the threshold of the program's own unit is taken right after the parse (the lock, ledger-chain,
data and generation-plan refusals keep their order); the trial row's g6_threshold stays one float; require_lock=
False keeps an explicit float. omr/selftest.py: run() reads the per-unit mapping, pipeline_smoke gives each noise
program its own unit's threshold. F1 changes no result other than the threshold a unit is judged at: each unit's
verdict is exactly calibrate.decide on its own rows (the core's equals the previous core verdict; test_d3 shows the
level-aware summary equals calibrate.oracle_summary on the core rows).
Tests (light): tests/test_ledger_lock.py test_the_seal_needs_both_units_and_decides_each_unit_alone (e: the seal
writes the mapping), test_r_h_a (core at 0.10 with power 0.9 read there, top30 at 0.05 with power 0.8 read there;
the core power at 0.05 would have been 0.7), test_r_h_b (varying one unit's null rows never moves the other unit's
choice or verdict), test_r_h_c (top30 power below the minimum at its own threshold: STOP naming top30 only),
test_r_h_d (a unit with no qualifying threshold: STOP naming core), test_r_h_e (the seal refuses with the per-unit
verdicts), test_r_h_g (require_sealed refuses a float seal, a one-unit mapping and a non-number), the existing seal
tests moved to the mapping; tests/test_evaluate.py::test_r_h_f_evaluate_uses_the_programs_own_unit_threshold (core
0.10, top30 0.025 from the same sealed mapping; the row records one float; an unsealed lock still exits first).
F2. ucalibrate.artifact_gaps: a unit artifact without families, the null or oracle rows of a null, or level-1.5
oracle rows for a speed and null makes decide_both STOP with "<unit> artifact incomplete: ..." before
calibrate.decide is called (omr/calibrate.py untouched). Test: test_f2_an_incomplete_unit_artifact_stops_with_a_reason
(no level 1.5, a missing speed, a missing null, no oracle: STOP, no KeyError, the other unit still decided).
F3. ucalibrate.Partial: every record line carries "sha" (sha256 of the canonical JSON of {"key", "result"}); a line
that does not parse or whose sha does not match is discarded and counted in the resume log line; a file whose
last line was torn gets a newline before the next append; a key stored twice with different results raises
PartialMismatch (the same result twice is accepted). Tests (tests/test_ucalibrate.py): test_f3_a_torn_tail... (torn
tail, resume, append, second resume: all four tasks present), test_f3_a_flipped_character... (the damaged line is
discarded, its task missing so it runs again), test_f3_a_key_twice... (same result accepted, different result stops,
--restart clears).
F4. CONSTITUTION section 13 calibration bullet: universe null B funding is "rates as recorded before the sign coin";
the core calibration's null B in section 8 (line 271) still reads "funding unchanged" (it is the core text).
F5. CONSTITUTION section 13 (G6 paragraph) and LANGUAGE section 10: the two limits of the universe lag test
(entrants of less than k hours are in neither book; each book pays its own costs) and why the lag range stays 30
days to half the VAL length, with a pointer to audits/AUDIT_LOG.md round 7.
F6. ucalibrate.calibrate_run runs the oracle phases of both nulls first, logs the Tier-1 power per null, speed,
level and grid threshold (oracle_advisory), and when the power at the largest threshold is below POWER_MIN or a
level is outside its bound logs one prominent ADVISORY line (the seal rule will STOP whatever the null worlds give;
the run can be interrupted, the partial file keeps the work); no exit, no change to the artifact. Light test:
test_f6_oracle_phases_run_first_and_a_hopeless_power_is_announced (fabricated task results: call order curve,
curve, power x 2 nulls before the null phases; the advisory appears with power 0 and not with full power).
F7. PROTOCOL_VERSION 4 (per-unit seal rule, partial line sha, oracle phases first); the ucalibrate docstring;
CONSTITUTION section 8 (the rule is applied per unit since KP-015) and section 13 (seal bullet R-H, run order);
KERNEL_PROPOSALS KP-015 "fix pass 6".
Light test results: tests/test_ledger_lock.py 36 passed; tests/test_ucalibrate.py -k "f3 or d1_partial or
f6_oracle_phases or d4_defaults" 7 passed; tests/test_evaluate.py -k "r_h_f or unsealed" 2 passed;
tests/test_exploits.py + tests/test_structure.py 97 passed. Heavy tests (test_f6_the_artifact_does_not_depend_on_
the_phase_order, the rest of tests/test_ucalibrate.py, the full suite) wait for the coordinator.
F8 (R-I). omr/ucalibrate.py: USPEEDS = {"fast": UNIVERSE_FAST_DAYS, "slow": 20} with UNIVERSE_FAST_DAYS = 5
(confirmed by the coordinator; one constant); every use of the speeds as days inside ucalibrate (task_oracle_curve, task_oracle_power,
artifact_gaps, oracle_summary, oracle_advisory, calibrate_run, run_header's speeds_days, the artifact's protocol
block) reads USPEEDS; the names fast / slow are the core's, so calibrate.decide reads them. omr/calibrate.py
(SPEEDS 1 and 20) is untouched; omr/kernel_lock.py compares no speeds. Reason (audit round 7, 24 worlds with the
real membership structure, 40 lags, one rho per speed at mean VAL Sharpe 1.5): cost drag in Sharpe units 3.86 at
1 day, 1.50 at 3, 0.93 at 5, 0.64 at 7, 0.39 at 10, 0.29 at 20 days; Tier-1 of 24 at 0.025 / 0.05 / 0.10: 1 day
0 / 0 / 0 (G4 0 of 24), 5 days 18 / 18 / 19 (G4 20 of 24), 7 days 15 / 15 / 19, 10 days 15 / 18 / 20, 20 days
17 / 18 / 20; the rule fixed before the data (the fastest of 5, 7, 10 days with Tier-1 at least 0.65 at all three
thresholds) selects 5 days. Light test:
tests/test_ucalibrate.py::test_f8_the_universe_oracle_speeds_are_a_unit_constant (the header carries USPEEDS; the
curve and power tasks build the fast oracle with USPEEDS["fast"] days and the slow one with 20; calibrate.SPEEDS
is still 1 and 20). Text: CONSTITUTION section 13, LANGUAGE section 10 (turnover sentence), KERNEL_PROPOSALS, the
ucalibrate docstring.
F9 (R-J). omr/programs/ucal_xs_reversal.omr is now the mirror of ucal_xs_momentum on daily bars:
signal = cs_scale(cs_demean(-ret(daily(close), n))), n = param(7, 3, 20) (whole days, drawn by the same
calibrate.draw_params mechanism as the momentum's n; lookback 527 hours, inside the 90-day limit); the former
4-96 hour reversal was cost-dominated at 12.5 bps per side (VAL Sharpe -9.7 in the measured null world), could never
reach Tier 1 and sat outside the unit's certified holding periods. Texts: the ucalibrate docstring, CONSTITUTION
section 13 (family description), KERNEL_PROPOSALS. FP6-1 unit_verdict returns STOP "<unit> artifact malformed:
<type>: <message>" for a KeyError, TypeError or ValueError raised by a malformed row. FP6-2 KERNEL_PROPOSALS states
the round-7 sequence (READY, then NOT READY after the Tier-1 power measurement, fix pass 6 reviewed READY on the
working tree). FP6-3 kernel_lock.thresholds_of accepts a unit's value only if it is a G6_GRID value (within 1e-12);
require_sealed refuses anything else. FP6-4 kernel_lock uses C.UNITS (exactly ("core", "top30")). FP6-6 LANGUAGE
section 10 gives the exact figure (twice the gross traded a day, about 0.9 of the gross per year in costs,
2 x 12.5 bps x 365); CONSTITUTION section 13 says the 24 audit worlds had the real membership structure and
synthetic prices.

Final runs of fix pass 6 on the files committed as 4286abf (logs in the session scratch, read by the coordinator):
tests/test_ucalibrate.py 28 passed in 754.45 s; full suite 849 passed in 1744.60 s (0 failed, 0 skipped);
python -m omr.ledger verify OK (trials 10 rows, stage1_log 1, kernel_history 8, calibration_log 2, sandbox_log 18,
val_access_log 15); ledger/ and data/ unchanged. After the suite the coordinator reworded the turnover bullet of
LANGUAGE section 10 (tests/test_structure.py: 9 passed).

Pilot of the universe calibration (this block added by the coordinator, 2026-11-21). Command: the kernel's own
entry point through scratch/pilot_wrapper.py (it redirects the access log and the trial ledger path to scratch, so
the project's ledger gets no row): --unlocked-dry-run --out <scratch>/pilot_ucal.json --worlds 1 --oracle-worlds 4
--workers 1. The first attempt (2026-11-20 23:29) was refused by the memory preflight (1.6 GiB available, about
1.9 GiB needed) and was not forced. Second attempt 2026-11-21 00:54 with 5.9 GiB available: exit 0, wall time
3,747 s, one worker process (the multiprocessing path), oracle phases first, then the null worlds; artifact saved,
partial file removed. Dry-run source: the synthetic universe (170 symbols, panel 149; null A pools median 201 days,
smallest 90). Tuned rho at level 1.5 (achieved mean VAL Sharpe): null A fast 0.059125 (1.498), slow 0.09275
(1.500); null B fast 0.05675 (1.502), slow 0.091875 (1.499).
Tier-1 power, 4 oracle worlds per cell, at 0.025 / 0.05 / 0.10: null A fast 0.25 / 0.50 / 0.75; null A slow
0.25 / 0.25 / 0.25; null B fast 0.50 / 0.75 / 1.00; null B slow 0.75 / 0.75 / 0.75. The ADVISORY fired: "the seal
rule will STOP whatever the null worlds give (null A slow: power at 0.1 below 0.5)". G6 p values (realized VAL
Sharpe): A fast 0.0249 (1.78), 0.0348 (1.23), 0.2139 (1.48), 0.0896 (1.50); A slow 0.1443 (0.94, also fails G7),
0.1990 (1.50), 0.1393 (1.55), 0.0100 (2.01); B fast 0.0050 (1.55), 0.0050 (1.76), 0.0647 (1.32), 0.0448 (1.38);
B slow 0.0050 (2.06), 0.3234 (0.72, fails G1), 0.0249 (1.42), 0.0050 (1.80). Every other gate passed in the other
rows (G4 values at 5 days 0.39 to 0.91).
Null rows (1 world per null, 3 submitted pairs each): null A momentum n = 58 has DEV Sharpe 2.54, VAL Sharpe 3.28,
passes every other gate and has G6 p = 0.0945 (Tier-1 at 0.10: 1 of 3 pairs); null B momentum n = 60 has VAL
Sharpe 1.42 and p = 0.771; reversal and carry are negative in both. Unit verdict of the pilot artifact: STOP
(power below POWER_MIN at A/slow), as the advisory said.
Reading (coordinator): the pilot met the condition fixed before it ran (it finishes; power above zero in all four
cells) and is too small to estimate a cell (1 of 4 has a 95% interval of about 1% to 81%). But its slow rows are
worse than the audit's 24 real-structure worlds, which were measured without the null builders and with 40 lags
(4 of 8 pilot rows have 13% or more of the lags beating the actual book, against 4 of 24). The four cells are
therefore measured again on the real structure through the null builders before any re-key (audit round 7, X10).

Fix pass 7 (rulings R-K and R-L; working tree on 6d9fb34, kernel files as in 4286abf before this pass; unapproved,
not re-keyed). Before any edit the sha256 of the klines and funding frames of two symbols of one null B world
(seed 4, panel[1] and panel[4], untrimmed) of the test source was pinned at 6d9fb34:
e7ec7d09d5f3dc0176c2f766a1fcc2daf7e28037b1d5686bbc17829e4c96892e (the null B pin of test T4).
R-K (omr/ucalibrate.py). USource.build stores per symbol and local day "dret", the day's log return (the sum of its
24 rows' log(g * cr), 0.0 where the day is not full), concatenated like "full". _build_pools computes c_s (the
symbol's mean dret over ALL its full days with a finite return; 0.0 with no full day), and per set Q (each pool, then
the whole period [pool_lo, ND) as the last row) pool_adj[Q, s] = c_s - mean of s over the days of Q on which s is
full (0.0 when there is none); arrays sym_c and pool_adj (2-D, shape kept through to_shared / from_shared); meta
pools gains full_days_nonfinite, pool_adj_abs_max_per_day and pool_adj_member_sd_per_year_median (per pooled
month the SD, ddof 1, of pool_adj[pool, member] x 365 over that month's top30 members; the median over months);
main() logs the three once after the source is built. UWorld._build, null A only: every active row of a world day
on the SHARED branch gets G *= exp(pool_adj[Q, s] / 24), Q the set that global day draws from; fallback days and
the own-days branch (no full day) get nothing; HR, LR, CR, funding, the source days drawn, the generators and
null B are unchanged. PROTOCOL_VERSION 5 (a version-4 partial file is refused). Docstring: hour-of-day means are
deliberately not equalised. On the test source (tests/test_ucalibrate.py, synthetic churn universe, seed 4, 44
symbols): pool_adj_member_sd_per_year_median 0.6298582988457404, pool_adj_abs_max_per_day 0.01280302944513791,
full_days_nonfinite 0; on the dry-run synthetic universe 0.866286909508653 and 0.05240581067137142.
Tests (tests/test_ucalibrate.py): test_r_k_t1 (every set and symbol: mean over Q's full days + adjustment = c_s
within 1e-12; c_s = mean over all full days; no full day in Q -> 0), test_r_k_t2 (null A seed 17, ten symbols:
each sampled world day's log return = source day return + adjustment on the shared branch, = source day return
on the fallback branch, more than 20 and 5 days of each; every active row's high / low / close over open equals
its source row within 1e-12), test_r_k_t3 (per pooled month and member the expected day return under the
adjustment is c_s; without it the members' deviations have a nonzero spread), test_r_k_t4 (the null B pin
above, unchanged after the edits), test_r_k_t5 (a version-4 partial file is refused).
R-L (omr/constants.py, omr/calibrate.py, omr/ucalibrate.py, omr/kernel_lock.py). FAMILY_PASS_MAX = 0.06 next to
NULL_PASS_MAX. calibrate.null_summary adds n_dev_positive (submitted rows with status evaluated and G3 true) and
per threshold family_pass_rate (Tier-1 passes / the family's submitted pairs; None without a submitted pair) and
pass_rate_dev_positive (passes / n_dev_positive; None when 0; information only, KP-016). calibrate.decide: a
threshold qualifies only if under both nulls the pooled rate is not None and <= NULL_PASS_MAX + 1e-12 and every
family rate that is not None is <= FAMILY_PASS_MAX + 1e-12; the verdict adds family_pass_max, family_pass_rate
{null: {threshold: {family: rate}}}, null_pass_rate_dev_positive {null: {threshold: rate}} and
threshold_failures {threshold: [failed bounds]}; when nothing qualifies the reason names, per threshold, the bound
(pooled, or the family by name) and the null. RULE, RULE_PER_UNIT and both docstrings state the bound;
calibrate.PROTOCOL_VERSION 3 -> 4; the seal's refusal detail per unit adds family_pass_rate. On the stored core
rows of ledger/calibration_7446278556aadd8f.json (read only) the verdict is unchanged: chosen 0.1, qualifying
0.025 / 0.05 / 0.1; worst family at 0.10 4.67% under null A (14 of 300) and 4.00% under null B; rate over
DEV-positive pairs at 0.10 3.85% (A) and 3.10% (B), stored as information.
Tests: tests/test_calibrate.py test_r_l_a (pooled 1.5% at 0.10 but one family 7.5% under null A -> 0.05 chosen,
threshold_failures names "null A: family a"; a second family above 6% under null B at every threshold -> STOP
whose reason lists every threshold; a pooled failure is named as pooled), test_r_l_b (3 of 50 = 6% qualifies, 4 of
50 does not), test_r_l_c (a family with pairs but none submitted and a family with no pair are None and skipped),
test_r_l_d (pass_rate_dev_positive = passes / submitted evaluated rows with G3 true; replacing it by 0.99, None or
0 never changes the choice); tests/test_ledger_lock.py test_r_l_e (top30 summaries without family_pass_rate ->
"top30 artifact malformed: KeyError", core still 0.10), test_r_l_f (a top30 family at 2 of 30 = 6.67% at every
threshold, pooled 2.2%: top30 STOP; the seal refuses and its message carries family_pass_rate and the family).
Existing test expectations changed: none (no existing test pinned a null A world number; the hand-built seal
artifacts keep every family at or under 5%).
Texts: CONSTITUTION section 8 (protocol v4; the rule with the family bound; why a family bound and why 0.06) and
section 13 (null A: R-K; the seal bullet: R-L; "core unchanged but for the family bound"); KERNEL_PROPOSALS KP-015
"Fix pass 7" (the KP-016 entry untouched); LANGUAGE.md has no text on the rule or null A (unchanged).
Runs (logs in the session scratch): focused tests while building (R-K tests 5 passed in 3.30 s; tests/test_calibrate.py
+ tests/test_ledger_lock.py + tests/test_structure.py 63 passed in 13.57 s); tests/test_ucalibrate.py 33 passed in 547.77 s (wall 550 s; 28 before + 5 new); full
suite 860 passed in 1294.36 s (wall 1297 s; 849 before + 11 new) (0 failed, 0 skipped); python -m omr.ledger verify OK (trials 10 rows, stage1_log 1,
kernel_history 8, calibration_log 2, sandbox_log 18, val_access_log 15); ledger/ and data/ unchanged (git status
clean there; no file under ledger/, no table and nothing in data/raw to depth 2 newer than the start of the pass).
No calibration, seal, selftest or dry run was run in this pass; nothing was evaluated on real price rows.
sha256 of the changed kernel files:
  0e19b605b428d4fdf5da46aaf3e0c9747bb5e0299183597c62881edc97f3c999  CONSTITUTION.md
  419c3e2e4b92b73360f3c2a76027799265fbd23a0c137d61184bc5650f7b8238  omr/calibrate.py
  bd75261ddd817b7b87618636b3e35d7e043a2b39501d1099ef1c9bf3c13c1431  omr/constants.py
  c4d6689cdb462a25f2d3c3887c0a487087eefafec44204d8a80339cd397dc8ca  omr/kernel_lock.py
  b93892738eac13847737d4fd25d40788b213d6cbded3af0048a94d0fe5bfe04d  omr/ucalibrate.py
  d7cd66a074bf05d3e8ebf0be9ccbf62c5e36cbef2f34e808f68106cae88101b2  tests/test_calibrate.py
  236feb7c1e467aab26e70ba3fc7053f77e0f0820ce9b20cdb847cfb165cafe65  tests/test_ledger_lock.py
  a0cc5c9548895b4d11fc916b5a24712a83174127e43e1fd77408ea3d669882d9  tests/test_ucalibrate.py
KERNEL_PROPOSALS.md (not a kernel file): 650151d33d6a5a88126905b52469b9ec0b497b03859570611b1c32739d9795c5

Fix pass 7b (the coordinator's review of ead27c6; working tree, unapproved, not re-keyed). 7b-1: calibrate.decide is
fail-closed again. A pooled bound holds only when `r is not None and r <= NULL_PASS_MAX + 1e-12`; a family fails
when `fr is not None and not (fr <= FAMILY_PASS_MAX + 1e-12)`. So a NaN or +inf rate never qualifies (the fix pass 7
form `r > bound` let a NaN qualify). The failure text comes from calibrate._bound_failure, which never raises: a
number gives "0.0750 > FAMILY_PASS_MAX", None gives "rate missing (no submitted pair)", NaN or inf give "nan / inf
is not a finite rate". 7b-2: n_dev_positive counts a submitted evaluated row whose G3 is truthy
(bool(gates.get("G3")), as tier_at reads a gate), so a numpy.bool_ in memory counts as it does after JSON. The
pipeline hands over Python bool: omr/pipeline.py and omr/upipeline.py wrap every gate's "pass" in bool(...)
(G5, G7, G8 and G10 through pipeline.g5_rule / g7_rule / g8_rule / g10_rule, which return bool(...)); G6 is None
when no threshold is given (the calibration) and G8 is None when not run. So the stored n_dev_positive of a run
would not have differed; the change makes that independent of the type.
Tests (tests/test_calibrate.py): test_7b_1_a_rate_that_is_not_a_number_never_qualifies (a NaN pooled rate at 0.10
under null A, then +inf, then a NaN and an inf family rate under null B: 0.10 drops out each time and
threshold_failures names it; NaN at every threshold, pooled or family, gives STOP with chosen_threshold None; the
text helper on None and on a string), test_7b_2_a_numpy_g3_counts_and_the_new_fields_survive_the_stored_form
(numpy.bool_ True counts, False and None do not, a liquidated row does not; n_dev_positive, family_pass_rate,
pass_rate_dev_positive, pass_rate and tier1 equal on the in-memory rows and on json.loads(json.dumps(ledger.clean(
rows)))). Both tests fail when run against the ead27c6 version of omr/calibrate.py (checked in-process from
`git show`, nothing written).
7b-3 (the coordinator's second review): the positive form wherever a bound decides. calibrate.decide: an oracle level
is inside its bound only when `v is not None and abs(v - level) <= RHO_BOUND` (None, NaN, inf go into
oracle_level_outside_bound); a cell has enough power only when `p is not None and p >= POWER_MIN` (None, NaN go
into below_power_min); the reasons join the cell names, so they cannot raise. ucalibrate.oracle_advisory (log only):
the same two tests, so a NaN power or level is announced as a reason to expect a STOP. No tolerance was added (the
old code had none): power exactly POWER_MIN is enough, an achieved mean exactly RHO_BOUND away is inside.
Tests: tests/test_calibrate.py::test_7b_3_a_power_or_achieved_mean_that_is_not_a_number_stops (NaN or None power
at the chosen threshold -> STOP naming the cell; NaN, inf or None achieved mean -> STOP naming the level; power
exactly 0.5 passes, the next float below does not; with RHO_BOUND set to 0.125 an achieved mean exactly 0.125
away is inside and the next float outside is outside; around 1.5 + 0.1 with the real bound every float decides as
the old rule), tests/test_ucalibrate.py::test_7b_3_the_advisory_names_a_power_or_level_that_is_not_a_number (both
named; exactly at both bounds no STOP). Both tests fail against the ead27c6 versions of the two files (checked
in-process from `git show`, nothing written).
Re-read of the seal path (decide_both, unit_verdict, artifact_gaps, kernel_lock.seal, thresholds_of, tier_at, both
oracle summaries): no other bound in the negative form. thresholds_of (`abs(float(x) - g) <= 1e-12`), tier_at's
p value (`perm_p <= p_max + 1e-12`), artifact_gaps (_finite and == 1.5), the oracle summaries (finite Sharpe only;
power a count ratio) and decide_both / seal (STOP or a None threshold refuses) are fail-closed. Reported, not
changed (a different pattern): tier_at skips a gate whose stored value is None, so a stored row with, say,
"G3": null counts as passing G3 (the pipeline only leaves G6 and G8 None, but ledger.clean writes a NaN as null),
and it reads gates by truthiness, so a float NaN gate would pass; unit_verdict catches KeyError, TypeError and
ValueError but not AttributeError, so an evaluated row with "gates": null makes the seal raise instead of a STOP
(nothing is sealed either way).
Runs (logs in the session scratch): 7b-1/7b-2 tests 6 passed with the R-L tests in 2.76 s; after 7b-1/7b-2
tests/test_calibrate.py + tests/test_ledger_lock.py + tests/test_structure.py 65 passed in 13.37 s and a full suite
862 passed in 1659.99 s (0 failed, 0 skipped); after 7b-3:
tests/test_calibrate.py + tests/test_ledger_lock.py + tests/test_structure.py 66 passed in 24.60 s, the advisory
tests of tests/test_ucalibrate.py (f6 x 2, 7b_3) 3 passed; full suite on the final files 864 passed in 1710.89 s (wall 1714 s; 862 before + 2 new) (0 failed,
0 skipped); python -m omr.ledger verify OK; ledger/ and data/ unchanged.
sha256 of the changed kernel files (fix pass 7b as a whole):
  f35cf554fdade68e6e362c45ecc70b3f452045d1b5df557a376a6c5934b6319e  omr/calibrate.py
  87e735510faea1592ddb7a5e3a622c5be913abd08adf4990a7207d6a526b6f86  omr/ucalibrate.py
  b2cdaf7a476de2a98f1df471e05f7ac946334faecc6433efe31979d83912e578  tests/test_calibrate.py
  6f5f551a9ad5a039c8030ea1cd665d8e93a1e55acc0c3b3af4c008bf3a02c397  tests/test_ucalibrate.py

Fix pass 8, stage A (ruling R-M and FP8-2 to FP8-4; working tree on 2dd58a2, kernel files as at 58ba59e before this
pass; unapproved, not re-keyed; the full suite follows in stage B).
Before any edit (code at 58ba59e; the test source of tests/test_ucalibrate.py, 44 synthetic symbols): the draws
pick (null A seed 17) 413a4e1ba9aac100e26c4bbd937e50c7d85d6b1f08357d0340a18a17f14255e4, every symbol's
source_days (null A seed 17, concatenated) 53dd79441e6188c110c3a367a961ad229dbaa1d46d479398ccdc91c8535d6c82, flip
(null B seed 4) c4d6431be672a4a85a5304b38c991981b71fb3b474b5f845276afaf71714e0e9; they are unchanged after the edit
(test_r_m_t2). The spread of the expected day gross across the 44 symbols under the 58ba59e construction (SD of
(expected day gross - 1) x 365): null A 0.685 (whole-period set; median over the 62 pooled months' members 0.709),
null B 0.684 (members 0.709); after R-M zero within rounding (test_r_m_t3: largest relative deviation from G below
1e-12 under both nulls).
FP8-1, R-M (omr/ucalibrate.py). USource.build keeps per symbol and local day the full day's log gross (sum of the
24 rows' log(g * cr), NaN where not full) only long enough to build the pools (no "dret" or "sym_c" in the shared
spec any more). _build_pools: Qd = exp(sum) on a full day with a finite sum; G = the mean of Qd over all full
finite symbol-days (meta pools common_day_gross); M(s) over s's full finite days; M(Q, s) over the days of each set
Q (the pools, then the whole period [pool_lo, ND)); arrays pool_adj[j, k] = log G - log M(Q_j, s_k) and
fb_adj[k] = log G - log M(s_k), per day, 0.0 where undefined; meta pools gains common_day_gross,
shared_adj_abs_max_per_day, fallback_adj_abs_max_per_day, member_adj_sd_per_year_median (per pooled month the SD,
ddof 1, of pool_adj[pool, member] x 365; the median) and keeps full_days_nonfinite; the run-start log line states
R-M. UWorld._build, null A: every active row of a shared-branch day gets G_row *= exp(pool_adj[Q, s] / 24), of a
fallback day exp(fb_adj[s] / 24) (new), a symbol without a full day (okb None) nothing. Null B: today's mirror, then
per local day over its active rows with a finite lrt (n, x = sum of lrt - m) every active row of the day gets
G_row *= exp(log G / 24 - m - log(cosh x) / n) (log cosh as logaddexp(x, -x) - log 2). HR, LR, CR, the draws, the
pools, funding and its sign coin, G[0] = 1 are unchanged. PROTOCOL_VERSION 6. An active row with a non-finite lrt
(none on the test source or the dry-run universes; the real source is expected to have none): it is left out of n
and x, still gets the day factor (every active row does), and stays non-finite as before; a day without a finite
active row takes exp(log G / 24 - m).
Numbers. Test source: G 1.0013278978251412 a day; largest |shared adjustment| 0.015585327873645284 and |fallback
adjustment| 0.004068771989792309 (log, per day); median members' SD of the shared adjustment 0.9443732354893171 a
year; full_days_nonfinite 0. Dry-run synthetic universe (synthetic_source(), 170 symbols): G 1.00195493603859;
0.0526805549308387; 0.007142146291285913; 1.1322925403321595; 0. Reduced dry run below (60 symbols):
G 1.001740350457411; 0.09765208908491096; 0.005791119630101154; 1.0414527028913656; 0. Checks on the test source:
null A enumeration from the raw rows equals G to 6.7e-16 relative over every (set, symbol); null B day products
equal G ** (n / 24) * (1 +- tanh x) to 8.0e-15 relative over 60,547 days (30 partial). The day's factor sits on
the gap ratios of the day's own rows, so a position opened at a day's first open holds 23/24 of that day's factor
and 1/24 of the next day's; the expected gross of such a hold is exactly G while both days carry the same factor
and is off by at most (next factor / this factor) ^ (1/24) where the factor changes (a set boundary, a switch
between the shared and the fallback branch, null B's day term). Measured as the largest |log of next factor / this
factor| / 24 over every symbol and every pair of adjacent active days (stage B, scratch fp8_hold_boundary.py):
about 0.43% per hold on the reduced dry run (null A, seeds 11000-11002; null B 0.10%) and 0.08% on the test source
(null B; null A 0.05%, seeds 17, 11000, 11001); the stage A report's 0.4% and 0.07% were the bound from the largest
single adjustment (0.41% and 0.065%). A symbol's first day is outside the exact day property (G[0] = 1 is kept).
FP8-2 (omr/pipeline.py tier_at, the one implementation; omr/calibrate.py tier_at = pipeline.tier_at and
GATES = list(pipeline.TIER_GATES)). Shapes of the stored rows (the sealed core artifact, 3,000 null and 1,600
oracle rows; the pilot dry run): an evaluated row (null or oracle) has gates with exactly G1 G2 G3 G4 G5 G6 G7 G8
G10, G6 and G8 None, the others Python bool, and perm_p a number in [0, 1]; a row with any other status
(not_submitted, stage1_*, liquidated, kernel_fault) has no gates and no perm_p (by code; only not_submitted occurs
in the stored artifacts). The pipeline hands over Python bool for every gate (bool(...) everywhere). tier_at now
raises ValueError naming the row and the gate for an evaluated row whose gates is not a mapping, lacks a gate of
TIER_GATES but G6, holds a non-boolean there or a non-boolean non-None G6, G8 or other gate, or whose perm_p is not
a finite number in [0, 1]; G6's stored value is ignored (re-read from perm_p) and G8 counts when present. The
verdicts recomputed with the present code and with the 58ba59e code are byte-identical (no exception) on the sealed
core artifact (core 0.1, also through unit_verdict), the pilot dry run (top30 STOP, power at A/slow) and the fresh
reduced dry run below (top30 0.1). FP8-3: unit_verdict catches every Exception. FP8-4: null_advisory(rows_by_null,
worlds, fams, oracle) and run_tasks(..., on_progress=None); calibrate_run checks after every progress line of the
null phases and logs the counts and one ADVISORY block once, an error once as "null advisory unavailable"; the
order of tasks, the results and the artifact are unchanged; oracle_advisory takes an optional threshold.
Tests. Replaced: the R-K tests T1-T5 by R-M T1 (null A enumeration from raw rows, every set and symbol), T2 (world
rows carry exp(pool_adj / 24) or exp(fb_adj / 24), shapes, full days Qd x factor ** 24, the draws equal the
hashes above), T3 (the finding in miniature, both nulls), T4 (null B day products flipped / unflipped, full /
partial; flipped shapes; the new null B pin 50fe43f66e8c08bfd0b0b03ce5f8c13d309c2a2a4b148ef62530d620ced3e6a7, the
old pin e7ec7d09... no longer matches), T5 (a version-5 partial is refused). Changed to the rulings: test_f6's fake
run_tasks takes on_progress; tests/test_calibrate.py test_7b_2 (an evaluated row with G3 None is now malformed:
those rows became kernel_fault rows, and the G3 None case expects ValueError). Added: FP8-2 (18 malformed cases,
null and oracle row, through decide_both; numpy booleans and floats; the real shape read as the 58ba59e rule did;
a G8 that is not a boolean), FP8-3 (gates null, a row that is a number, a row without family), FP8-4 (counts and
dead thresholds, pooled and family, the largest open threshold's power; calibrate_run logs the advisory once and an
advisory error once). Runs: tests/test_ucalibrate.py 37 passed in 1041.88 s; tests/test_structure.py +
tests/test_calibrate.py + tests/test_ledger_lock.py 89 passed in 26.18 s. Reduced dry run (the kernel's entry
point through a scratch wrapper that points the access log and the trial ledger at the scratch folder and builds
the synthetic universe with 60 symbols instead of 170; --worlds 1 --oracle-worlds 1 --workers 0): exit 0 in
980.6 s; the R-M log line printed; oracle power 1.0 in all four cells; no null advisory (nothing dead); the
full-size dry run was not run. ledger/, data/, kernel.lock, audits/ and STATE.md unchanged.
sha256 of the changed kernel and test files:
  1964b4c0aa42b18309b0ef6f5c119029c67e7877f6ef4e4080f20fa42b19b6dd  CONSTITUTION.md
  d9bfa50683810a965e89193b3774c40065d338551d9adb1889962ae83d62d588  omr/calibrate.py
  f650b7fd9f0bf196c1c6a154ddcafab1ad21a3601043f2139ec40073926aa9d7  omr/pipeline.py
  9c6c46cb2f0d0f64af2f464b258c0baf1efe76c6c44ae21d0c04ea32473a27cb  omr/ucalibrate.py
  5cb0957be68e08cad2e2df45bc85b6cf5b22c660d6ab6a12c30a5db9bbd6a074  tests/test_calibrate.py
  12fd8e37d08a47a7e5660eeedec9e01450d30cd7718baaaa79baedb481e38633  tests/test_ledger_lock.py
  38aba87fa35d99ff4f708a684192557c6b5001c50043a790b3285b64ddf1ab43  tests/test_ucalibrate.py
KERNEL_PROPOSALS.md (not a kernel file): fcd2b6863cb872ba741a9552219860ff3612f46c2a40e61f1f6f0ee43a28800a
Fix pass 8, stage B (on 258c1a5). B-1: the held-position boundary above is now also stated in the R-M paragraph of
the omr/ucalibrate.py docstring. B-2: FP8-4 cases (a) to (d) are in test_fp8_4_the_null_advisory_reads_the_counts_so_far,
(e) in test_fp8_4_a_malformed_row_makes_the_advisory_unavailable_once_and_the_run_goes_on (now also: the run's
results equal those of a clean run), the advisory logged once with its counts in
test_fp8_4_calibrate_run_logs_the_null_advisory_once_with_the_counts; added (f)
test_fp8_4_the_pooled_bound_alone_makes_a_threshold_dead (families 4, 4 and 2 of a cap of 6, together 10 over 9:
0.10 dead by the pooled bound alone with 0.05 open, and every threshold dead when the passes are at every
threshold). Full suite on the final kernel and test files: 891 passed in 1585.34 s, 0 failed, 0 skipped; python -m
omr.ledger verify OK (trials 10, stage1_log 1, kernel_history 8, calibration_log 2, sandbox_log 18, val_access_log
15); ledger/, data/, kernel.lock, audits/ and STATE.md unchanged. sha256 of the files changed in stage B (kernel
and test files; this note changed too):
  1beb17bd8d052fb8671a7d5e76383fe6e979df59403f12e8996fa9782856a675  omr/ucalibrate.py
  744a593e3cb484e20942d4544ae90727407bc86c2f96bea5a6e878e30bf9f152  tests/test_ucalibrate.py

Fix pass 9, stage A (ruling R-N for the top30 G6, and text corrections; working tree on 97185b1, kernel files as at
1442b42 before this pass; unapproved, not re-keyed; the full suite follows in stage B).
R-N (a) (omr/upipeline.py g6_lags; omr/constants.py UNIVERSE_G6_LAGS = 20, provisional; pipeline.Opts.u_lags, the
core keeps perm_n = 200): lo = 30 days in hours, hi = L // 2, step = (hi - lo) // n, phase = rng.integers(0, step)
(the first and only draw of the lag generator), lags = lo + phase + step * arange(n); KernelFault "VAL too short
for the lag test" when hi < lo or step < 1, "not enough history before VAL for the lag test" when g0 - hi < 0;
returns (lags, step). On the VAL calendar L = 26,304 rows, hi = 13,152, step = 621 hours (25.9 days). p stays
g6_paired_p: (1 + lagged books at least as good) / (n + 1), ties and margin unchanged.
R-N (b) (g6_memory; UNIVERSE_G6_MEMORY_MAX = 0.5, provisional): for j = 1 .. n - 1, k = j * step, on the mask
ok & P_[g0 - k : g0 - k + L] (g6_books' common names; the books' rule that a row with fewer than 10 common names
is flat is not applied here, as ruled), per name with at least 2 mask rows its mean removed from both copies;
r_j = sum(a * s) / sqrt(sum(a * a) * sum(s * s)) over all such names and rows, 1.0 when undefined or not finite;
memory = max over j (0.0 when n < 2: no pair of copies). Sums: every column sum is a cumsum down the rows (as
_seq_rowsum, but by column), every sum across names a cumsum in column order, so no pairwise summation enters.
Peak memory of the computation: about four float64 and one boolean per VAL cell, under the 42 bytes per VAL cell
the R3 estimate already reserves for G6, and never held together with the lag books. In ugates: if not (memory <=
UNIVERSE_G6_MEMORY_MAX), p = 1.0 and no lag book is built or run (the plain actual run, kept in the detail, still
runs once); otherwise the lag loop as before over the n lags.
Records. The G6 gate record of top30 (res["gates"]["G6"], stored in the trial's detail file) is now {pass, value
(= p), threshold, lags, lag_step, memory, memory_max, memory_over_limit}; the detail's permutation block adds
lag_step, memory, memory_max, memory_over_limit (n = the lag count). The trial row in ledger/trials.jsonl is
unchanged (gates.G6 = pass, gate_values.G6 = p). A universe calibration row with status evaluated adds g6_memory,
g6_lag_step, g6_memory_over_limit (omr/ucalibrate.py g6_fields; omr/calibrate.py and tier_at untouched; a row
over the limit has perm_p 1.0). omr/ucalibrate.py: PROTOCOL_VERSION 7; the run header and the artifact's protocol
block carry g6_lags and g6_memory_max instead of perm_n; the docstring's G6 sentence and the corrected R-M reason.
Measured on the churn panel of tests/test_g6_paired.py (scratch fp9_explore.py): memory of momentum at n = 14 /
20 / 40 / 60 days 0.022 / 0.035 / 0.30 / 0.52; reversal (7 days) 0.016; carry (9 days) 0.014; the cross-sectional
oracle at 1 / 5 / 20 days 0.016 / 0.011 / 0.020; the equal-weight basket 0.91; a 60-day moving average of iid
noise 0.518; fresh iid weights every 20 days 0.072.
Texts: CONSTITUTION section 13 (G6 of top30: the lags, p / 21, 0.05 and 0.10 read, 0.025 unreachable, the speed
limit and its reason, the D2 measurement; the lag-range sentence; limits (1) and (2) kept; the corrected R-M
reason), section 12 (two limitations: a slow program cannot reach Tier 1 in top30; what G6 does and does not
protect against, and the core G6 not examined for the same effect); LANGUAGE section 10 (the speed-limit sentence
replaces the old lag-range sentence); KERNEL_PROPOSALS (fix pass 8 clause corrected; "Fix pass 9" entry); the
upipeline module docstring (its G6 line was still the pre-R-C wording).
Tests. tests/test_g6_paired.py: R-C T3, T5, T7 and the churn-books test now set Opts(u_lags=N) instead of
perm_n and unpack (lags, step); T4 (equal-weight basket) asserts that the basket is over the speed limit (p = 1)
and, with the limit lifted, that the lag test itself still gives p = 1; T6 is replaced by the R-N lag test
(equal spacing, phase range, every lag within [lo, hi], the single draw, determinism, both KernelFaults); new:
the memory against a plain-loop reference (names entering and leaving, a name in play for three rows), the
constructions (a) 60-day moving average over the limit with p = 1 and only the plain actual run, (b) fresh iid
weights every 20 days under the limit with the lag loop running, (c) a book that never changes (1.0), (d)
period = step (1.0 at j = 1) and period 2 x step with a sign flip (-1.0 at j = 1, 1.0 at j = 2), (e) a constant
long base plus a fast tilt under the limit, (f) a name in play for part of VAL only; p with no beat 1 / (n + 1)
and one beat 2 / (n + 1). tests/test_universe.py, tests/test_blocks.py, tests/test_ucalibrate.py: Opts(perm_n=x)
for top30 runs became Opts(u_lags=x) (same counts, same run time); a stored top30 trial's detail carries the G6
record; a calibration row carries the speed-limit fields (perm_p 1.0 when over the limit; tier_at reads it); the
protocol test refuses version-5 and version-6 partials (it was R-M T5). Runs: tests/test_g6_paired.py,
test_universe.py, test_blocks.py, test_selftest.py, test_probe_top30.py, test_record_metrics.py, test_evaluate.py,
test_ucalibrate.py together 145 passed in 1433.96 s; tests/test_structure.py, test_calibrate.py,
test_ledger_lock.py 89 passed in 21.91 s.
Reduced dry run (the fix pass 8 wrapper: 60 synthetic symbols, --worlds 1 --oracle-worlds 1 --workers 0, the access
log and trial ledger in the scratch folder): exit 0 in 599.4 s (fix pass 8: 980.6 s on the same settings; the
machine is loaded by the auditor's measurement either way); the oracle power phases took under a minute each
instead of about two; Tier-1 power 0 at 0.025 and 1.0 at 0.05 and 0.10 in all four cells (p = 1 / 21 = 0.048
cannot be below 0.025); null rows: memory 0.02 to 0.49, none over the limit; unit verdict 0.10, no STOP.
ledger/, data/, kernel.lock, audits/ and STATE.md unchanged.
sha256 of the changed kernel and test files:
  c9b4ae4edc269998ed81f534d16a1645db0b9e988f01c5217206336fc4bddc55  CONSTITUTION.md
  2f679b3a497e1b524e2f8eb4a3b58de5aef7f377cfb7623ad54d9071548ecd11  LANGUAGE.md
  0a2c2231bd420644036fc0cfbeb953361230cfa0a836ff5bb7c45af1b86eb357  omr/constants.py
  3f475642bf515a687aa607cf140e96659b6e8109e2e7a0a18f3d81067583a95e  omr/pipeline.py
  e5963af6b8d73f266479033b8c82b75dfc9271cc7395b140f1a59aa727596c9c  omr/ucalibrate.py
  009194b6a91c2000fe9f8da52be8f3bfbf6d4843327b1f542d589fc23e5b0e3e  omr/upipeline.py
  82679a25ef5a05e37799f3777f72756a1623cf294616eef3a45892f734741f92  tests/test_blocks.py
  9da0c94f37978ff2c473713babe99cb3afbc8292f191d756b682b6adf93385b4  tests/test_g6_paired.py
  5dccafc6da2b95a306e0c6fd8f87fc1ed2da932154ce22b5100cd6c9374e093d  tests/test_ucalibrate.py
  9aabd2b61f484c7ad35d35bc1d01c1bbe9317ae1c4a825b0438b9d206d523f45  tests/test_universe.py
KERNEL_PROPOSALS.md (not a kernel file): 83d616e741a5ebbc15c0130e6db9784ac1dcddfee7ed0d7867b4b804d4ab2ad2
Fix pass 9, stage B (on 9ca8b62, no kernel file changed). Full suite: 895 passed in 2050.87 s, 0 failed, 0 skipped
(891 at 1442b42 plus the 4 tests added in tests/test_g6_paired.py); python -m omr.ledger verify OK (trials 10,
stage1_log 1, kernel_history 8, calibration_log 2, sandbox_log 18, val_access_log 15); ledger/, data/, kernel.lock,
audits/ and STATE.md unchanged. UNIVERSE_G6_LAGS = 20 and UNIVERSE_G6_MEMORY_MAX = 0.5 stay provisional until the
auditor's measurement.
Fix pass 10, stage A (rulings R-O, R-P and R-Q; working tree on 8bfabc4, kernel files as at 9ca8b62 before this pass;
unapproved, not re-keyed; the full suite follows in stage B). R-O (top30 calibration worlds only): USource.build
requires mark_klines from get_tables (a missing key raises; an empty table means no mark bar) and keeps per row hm and
lm, the up and dn of datasets.liquidation_ratios where has_mark (NaN elsewhere), two shared row fields outside R-M's
day sums and pools; UWorld._build gives the world's mark bar high = open * HM and low = open * LM on active rows with
finite (HM, LM) (null A: the drawn source row's hm, lm; null B: hm, lm, mirrored as 1 / lm, 1 / hm on a flipped
row), else the world's last-price bar (bit for bit the kline's high and low); mark open and close are the world's;
index_klines is the same object. The real-source loader reads mark_klines with the same logged handle (a symbol
without a mark file gets an empty table, as datasets.load_liq treats it). Source meta "liq" (active rows, those
without a valid mark bar, the smallest effective low / open and the largest effective high / open) is printed once
per run and stored in the artifact (source_liq); tune_rho records per cell the liquidated (non-finite) tuning books
at the chosen rho and names them in the log line. The memory preflight counts the source arrays as they are, so the
two new row fields (16 bytes per source row) are in it; the worker peak constant is unchanged (the mark tables were
already built per world symbol). Universe PROTOCOL_VERSION 8. R-P (calibrate.decide, both units):
NULL_NOT_EVALUATED_MAX = 0.03; null_summary counts n_submitted_not_evaluated; a null above the bound (fail-closed on
the counts) fails every threshold with a named reason; the verdict carries null_not_evaluated_max and each null's
share; the null advisory marks every threshold dead once the not-evaluated pairs so far exceed the bound over worlds x
families. R-Q (both task_null): a screened draw liquidated on DEV (dev_liquidated) or with a DEV Sharpe otherwise
not finite (dev_sharpe_not_finite) is not a candidate; a pair without a candidate is not submitted; core
PROTOCOL_VERSION 5. Before the edit the klines and the mark tables of the null A (seed 17) and null B (seed 4) worlds
of the test source were pinned; after it both are unchanged (on that source the mark bars are the last-price bars).
Tests: R-O T1 to T6, T8, T9 and the advisory part of R-P T7 in tests/test_ucalibrate.py (the bad print: with its
ordinary mark bar a flipped null B day gives liq_up 1 / 0.9 and no liquidation of a 50% short; without the mark row
liq_up 500 and the short is liquidated); R-P T7 in tests/test_calibrate.py and tests/test_ledger_lock.py; R-Q TQ1 to
TQ4 for both units. Changed to the rulings: the shared-source round trip compares float arrays with equal_nan (hm, lm
hold NaN); the protocol test refuses versions 5 to 7 (was 5 and 6); test_d1 also checks the source_liq record and its
log line; test_r_l_d pins the core PROTOCOL_VERSION 5 (was 4). T9 covers the real-source loader with
datasets.load_raw and the symbol table replaced by recording fakes (no disk fixture exists for the loader). Runs,
one file after another: before R-Q, tests/test_ucalibrate.py 47 passed in 1165.35 s, test_calibrate.py 16 in 16.69 s,
test_universe.py 48 in 285.56 s, test_blocks.py 24 in 280.85 s, test_g6_paired.py 14 in 47.53 s,
test_ledger_lock.py 66 in 9.29 s, test_structure.py 9 in 5.65 s; after R-Q, test_calibrate.py 19 passed in 18.27 s,
test_ledger_lock.py 66 in 15.01 s, test_structure.py 9 in 7.07 s, test_ucalibrate.py 48 tests: 47 passed in 973.33 s in the file run; test_d1 failed there only because the builder edited tests/test_calibrate.py while it ran (the artifact's text hash covers tests/), and passed alone afterwards in 398.42 s. Reduced dry run (60
synthetic symbols, worlds 1, oracle worlds 1, in-process, through the scratch wrapper): exit 0 in 547.1 s (the first run, whose process started before R-Q: 560.3 s; fix pass 9: 599.4 s; the machine is shared with the auditor's runs); the R-O line printed (1,605,734 active rows, 0 without a valid mark bar on this synthetic universe, whose mark bars are its last-price bars; smallest effective low / open 0.948, largest high / open 1.059); 0 of 1 tuning books liquidated in every cell; Tier-1 power 0 at 0.025 and 1.0 at 0.05 and 0.10 in all four cells; every null pair evaluated (R-P shares 0 and 0); unit verdict 0.10, no STOP. "About a quarter"
(the speed limit's reason) stands only in audits/AUDIT_LOG.md, not in the kernel texts; recorded as corrected in
KERNEL_PROPOSALS. ledger/, data/, kernel.lock unchanged; audits/AUDIT_LOG.md and STATE.md were modified in the working
tree during this pass by someone else, not by the builder.
Fix pass 10, stage B (on 306eb8c, no kernel file changed; nothing was edited while the suite ran). Full suite: 910
passed in 2139.16 s, 0 failed, 0 skipped (895 at db32ce2 plus the 15 tests of fix pass 10: tests/test_ucalibrate.py
10, tests/test_calibrate.py 4, tests/test_ledger_lock.py 1); python -m omr.ledger verify OK (trials 10, stage1_log 1,
kernel_history 8, calibration_log 2, sandbox_log 18, val_access_log 15); ledger/, data/ and kernel.lock unchanged,
and STATE.md and audits/ equal to 306eb8c (git status clean before this paragraph).
Fix pass 11, stage A (ruling R-R with the amended item (e); working tree on 5d10da4, kernel and test files as at
306eb8c before this pass; unapproved, not re-keyed; the full suite follows in stage B). omr/constants.py: NULL_FAULT_MAX
0.03 (NULL_NOT_EVALUATED_MAX removed), FAMILY_EVALUATED_MIN 0.50, NULL_EVALUATED_MIN 0.75, CALIBRATION_WORLDS 300,
CALIBRATION_ORACLE_WORLDS 200, UNIVERSE_CALIBRATION_WORLDS 200, UNIVERSE_CALIBRATION_ORACLE_WORLDS 100.
omr/calibrate.py: null_summary(rows, families, designed) with the rates over evaluated pairs (pass_rate_submitted kept),
n_evaluated, n_submitted_liquidated, n_submitted_fault, designed_per_family and per-family evaluated counts;
fault_share, evidence_floors, design_problems, design_stop and protocol_header; decide fails a missing rate (no family
skipped), a floor not met and too many faults at every threshold and records the floors, the shares and the faults;
verdict_from_rows and main check the design before the rule; main refuses a real run with other sizes or a subset of
the families before any data access and writes protocol_header as "protocol"; PROTOCOL_VERSION 6. omr/ucalibrate.py:
unit_design and verdict_from_rows(art, unit) (the design first; unit_verdict passes the unit), null_summary with the
designed pairs in calibrate_run, the null advisory after R-R (its reading in _null_dead), main refuses a real run with
other sizes, checks the design before the rule and stores run_header (which now carries the options object) in the
artifact; PROTOCOL_VERSION 9. omr/kernel_lock.py: check_artifact and check_universe_artifact refuse other sizes and a
protocol header that is not the one the checking kernel writes for a real run of the protocol's size, key by key
after a JSON round trip (universe: semantic_hash, research_hash and families keep their own checks). On the sealed core
artifact (read only) the design holds and the verdict is unchanged: chosen 0.10, every family at least 299 of 300
evaluated, faults 0, the rates equal to the former submitted rates. Tests: tests/test_calibrate.py 24 passed in 18.18 s,
tests/test_ledger_lock.py 111 passed in 16.25 s, tests/test_structure.py 9 passed in 6.82 s, tests/test_ucalibrate.py 49
passed and 1 failed in 978.03 s (test_f6, whose nulls-first fake built null_summary without the designed pairs; the
fake was given them and the test passed alone: 1 passed, 49 deselected in 487.99s (0:08:07)). Reduced dry run (60 synthetic symbols, worlds 1, oracle worlds 1,
in-process, through the scratch wrapper): exit 0 in 576.1 s; every null pair evaluated (shares 1.0, faults 0); unit
verdict 0.10, no STOP.
Fix pass 11, stage B (on 305e2c6, no kernel or test file changed; nothing was edited while the suite ran). Full
suite: 962 passed in 1757.16s (0:29:17), 0 failed, 0 skipped (910 at 306eb8c plus 52: tests/test_ledger_lock.py 45, tests/test_calibrate.py 5,
tests/test_ucalibrate.py 2, counting the replaced R-P tests); python -m omr.ledger verify OK (trials 10, stage1_log 1,
kernel_history 8, calibration_log 2, sandbox_log 18, val_access_log 15); ledger/, data/ and kernel.lock unchanged.
