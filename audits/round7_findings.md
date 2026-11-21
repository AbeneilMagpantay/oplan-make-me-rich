# Audit round 7, part 1 - commit e4e44e2 (KP-015 fix pass 4) - LIGHT work only

Copy: review7\kern = 142 blobs of e4e44e2 (git-blob hashes verified, setup7.py); data/ tracked files in
tracked_data\. Every probe ran under run_capped.ps1 (kills above ~420 MB; peaks 222-306 MB). Project untouched.
Scripts and outputs: review7\p01..p05b (+ _out.txt).

## Verdict per item
A data hole fill: SOUND on the checksum / life / held-hour rules and on the sampled data; three LOW findings
  (A1 permanent .missing markers, A2 daily pins never compared, A3 crash window between file replace and
  manifest write).
B U3 known-and-finite cross-sections: SOUND (p04).
C U7 funding freshness: SOUND (p04).
D U6 12-symbol probe: SOUND by reading (+ round-6 cases now parse, builder tests); NOTE below.
E U5 symbol table in the research hash and fingerprint: SOUND (p04).
F U8 sandbox log order, old-seal rekey, block_overlap_cells: SOUND by reading.
G pass-3 lookback / test_blocks / _check_overlap: SOUND by reading (round-6 p10: block_overlap can fail).
H U2 worlds: construction SOUND (p03: activity, membership, DEV view exact); one MEDIUM design finding (H1
  null A fallback days destroy the shared-day cross-section) and two notes for the calibration's reach (H2, H3).
Design review: the circular form of e4e44e2 HAS a look-ahead through its mask (p05b, demonstrated); the paired
  lag form has no such path; asymmetries and blind spots listed below; experiments for part 2 at the end.

## A - data hole fill (omr/data.py)
Reading: fill_from_daily reads only daily files that daily_file_ok accepts (zip AND stored CHECKSUM present and the
sha256 equal - a mismatch raises); fetch_daily verifies the published CHECKSUM before storing and stores nothing
without one ("nochecksum"). Daily rows are kept only inside [first, last] klines bar of the monthly rows, and the
monthly rows were already cut at `until`, so nothing outside the life or at/after `until` can enter. An hour the
monthly rows (universe) or the stored table (core ten) already hold must equal the daily row in every column,
else DailyRevision, which stops the whole run with every staged .parquet.new deleted. Tables are written only
after every fetch succeeded; an unchanged table keeps its file and pin.
Data check (p01_daily_check.py, p01_out.txt; counts only): 3,090 filled daily files are pinned in the manifest;
sample of 41 symbol-day-datasets (LUNAUSDT 2022-02-26..28 and SOLUSDT 2022-04-01..02 in klines, mark and index;
six BTCUSDT mark days; 10 DEV and 10 VAL/after-VAL others): 31 cached files present - CHECKSUM OK 31/31, manifest
pin equal 31/31, 733 hourly rows compared, equal 733, different 0, daily hours not stored 0, stored hours not in
the zip 0. The 10 others are the LUNA / SOL mark and index days: no daily file and no marker - those hours were
not holes (only their klines were), as expected.
- A1 LOW: a `.missing` marker is permanent. fetch_daily returns "cached-missing" whenever the marker exists and never
  asks again, so a day fetched before the archive published it (yesterday's file during `data update`) stays a
  hole for ever, in the core snapshot (fill_core_tables via _HoleFill) as well as in `data universe`. No instance
  today (p02_markers.py: 29,328 markers, 0 written within 7 days of the day they name). Fix: do not write a marker
  for a day less than N (e.g. 7) days old, or store the check date and retry after N days.
- A2 LOW: the daily_files sha256 pins are written to the manifest but never compared. A re-download that differs is
  caught only indirectly: for a universe symbol fill_from_daily compares daily rows with the MONTHLY rows only, so a
  changed daily file re-fills its hours and the difference is found by _revised against the stored table, which
  SKIPS that table with a log line while the run continues and rewrites the manifest for the rest (not the
  DailyRevision stop). Fix: compare each used file's sha256 with its pin and stop on a mismatch (or pass the stored
  table's previously filled rows into fill_from_daily as held hours).
- A3 LOW-MEDIUM: crash window. download_universe moves every staged file over its table (new.replace(p)) and only
  then writes data/manifest.json. A process that dies in between leaves tables whose bytes no longer match their
  manifest pins: every read fails closed (DataIntegrityError) - including the next `data universe`, which reads the
  previous table under the old pin - and the old bytes are gone, so recovery is manual. Fix: keep the replaced file
  as .parquet.old until the manifest is written (or journal the renames and recover at start).
- A4 NOTE: duplicate hours inside the daily files keep the first row silently (a differing duplicate is not
  flagged).

## B - U3 (omr/interp.py cross_inplay) - SOUND (p04_light.py, p04_out.txt)
14 in-play symbols: one 0/0 input -> row known 14/14, 13 finite, the 0/0 symbol a known NaN (cs_mean, cs_demean,
cs_scale, cs_rank); exactly 10 finite -> known; 9 finite -> unknown for everyone; an x/0 (inf before _clean) behaves
as a known NaN. Through sma(.,3) the NaN stays in its own column for 3 rows; lag moves it one row; a second cs_*
excludes it; hold treats it as a false condition (known); where(cs > -9, 1, 0) turns it into 0 (a program can see
that ITS OWN input was not finite - own data). Nothing reveals other symbols' membership or knownness: a row
below 10 finite inputs is unknown for everyone, and an unknown is not observable.

## C - U7 funding freshness - SOUND (p04)
funding_fresh: an 8 h settlement is fresh through 16 h exactly; interval NaN or 0 never fresh; 1 h -> 2 h; 4 h -> 8 h;
24 h capped -> 16 h. Core frames: assemble_frame's funding.fresh equals a naive "latest settlement at or before the
row, at most 16 h old" on a frame with a 3-day funding gap (71 stale rows). sma(funding8h, n <= 8): lookback 24
(17 + 7); start cuts 0 disagreements and 0 rows known in the base but unknown in the cut from cut + lookback - 1 on;
truncation cuts equal. FullPanel serves the R2 freshness as funding.fresh (same rule, table up to hi with every
earlier settlement). funding_mean is independent of it (S1 counts settlements).

## D - U6 (omr/probe.py universe_panel) - SOUND, one NOTE
12 synthetic symbols all in play, unit known everywhere; round-6 abs(cs_rank(x)) and cs_rank(x)^2 parse (builder
tests), x/x constants still rejected. NOTE: the probe panel fixes the number of in-play symbols at 12, so an
expression that depends only on that count (e.g. cs_mean(abs(cs_rank(x))), a function of k alone) is falsely
constant and rejected; it is an unusual program and the error is conservative. A real constant cannot pass unless
it moves on 12 synthetic symbols, as before.

## E - U5 - SOUND (p04, scratch disk fixture in the copy's own data folder)
With the manifest pinning the universe, changing one class or one `until` in symbols.json changes
research_hash_from_disk (and the fingerprint); restoring the file restores both; deleting symbols.json while pinned
fails closed (FileNotFoundError); adding the pin to a manifest written without it changes the hash (so
DiskProvider.check refuses until the manifest is rewritten).

## F - U8 - SOUND (reading)
sandbox: the log row is appended after the metrics are COMPUTED and before anything is printed; the kernel_fault
exit appends its row first; an exception before the append prints nothing; after the append the row exists.
kernel_lock.rekey copies seal keys with .get. Blocked._check_overlap returns the number of KNOWN cells compared
(previous block's known cells for symbols in both blocks); 0 for one block or a vacuous overlap; recorded in the
stage-1 result, the pending row and the final row.

## G - pass 3 - SOUND (reading)
lang.lookback_hours: btc(f) = leaf f; a timeframe of h hours over leaf l: 2h - 2 + l (daily(mark_close) 53 =
23 wait + 24 bin + 6 staleness); funding8h 17. tests/test_blocks.py covers windows over cs_* (6 programs, custom
boundaries inside holes and first months), next30 with months=None vs 3, stage 1 and 2 equality, the old per-block
membership caught, block_overlap firing on an under-reported lookback, every kernel/strategy top30 program silent,
lookback as an upper bound on 10 constructs with gaps. _overlap_tail / _check_overlap compare the rows from the
later block's first evaluated row + lookback to the row before it, by symbol, known channel and values.

## H - U2 worlds (omr/ucalibrate.py)
p03_ucal_world.py (synthetic_churn_universe seed 3, 28 symbols, all ever top30; peak 306 MB):
- SOUND: for null A and null B, activity_of on the world's own klines equals the source Activity for 28/28
  symbols; membership from it equals the source membership in 67/67 months (unit sizes 12-17); the DEV view's
  klines and funding equal the full world's up to DEV end for 28/28 symbols.
- H1 MEDIUM (design): null A shares a source day across symbols only when the symbol is fully active on the drawn
  day; otherwise it takes a personal fallback day. The draw is uniform over 2019-12-31 .. VAL end, so a symbol
  listed late (or with holes) falls back on most days: 33,408 fallback symbol-days in the 28-symbol source and the
  mean pairwise hourly-return correlation fell from 0.360 (source) to 0.137 (null A; null B 0.360). On the real
  panel (134 symbols, listings from 2019 to 2024) most symbol-days of late listings will be independent, so null A
  worlds carry far less common factor than reality. Fix: draw each world day's source day from the days on which
  the symbols alive on that world day are fully active (fallback only for genuine holes), and report the fallback
  share in the artifact.
- H2 (answer to design question 4): in both nulls membership comes from the REAL activity, so it no longer follows
  the null prices: corr(90-day log quote-volume change, 90-day log price change) 0.211 in the source, -0.062 null A,
  -0.026 null B. Any bias of the G6 that needs membership to depend on the traded returns (survivorship,
  persistence) is invisible to the calibration.
- H3 NOTE (reading): null B keeps the real funding in real order, so the carry family earns real, persistent
  funding (not luck); both nulls keep intraday structure (null A within the source day, null B as a mirrored path),
  so the short-term reversal family can earn real intraday autocorrelation. Both make null pass rates conservative
  (stricter threshold, lower power); size them on the real source in part 2.

## Design review of the PAIRED LAG test (on paper + p05b for question 1)
(1) Look-ahead. The CIRCULAR form of e4e44e2 takes rows i < k from the future: S_k's weights are decided after the
bar they trade (they encode that bar whenever the program's lookback exceeds the forward distance L - k, as in the
core's circular G6), and the mask ok[i] & D[(i-k) mod L] restricts A_k to names in play at a FUTURE row, whose
membership depends on returns after the decision row. Demonstration (p05b_lookahead.py; iid returns + per-symbol
drift, membership = top 30 by trailing 2,160-h return, equal-weight basket, the kernel's g6_books): on rows whose
source is 720-2,400 h ahead the future-masked basket earns +9.38e-5 per hour (se 0.61, 56 seed-lag pairs) more
than the same basket masked by the PAST source; 2,400-5,000 h ahead -0.15 (se 0.23); 5,000-9,000 h ahead +0.95
(se 0.38); overall +2.55 (se 0.34, 240 pairs). The paired LAG form takes every source from the past (a VAL row or
a DEV row before VAL), so neither book can contain information from after its decision row. The execution-bar
presence term of ok[i] is a one-bar look-ahead shared by both books (the engine needs it anyway); symmetric.
(2) Asymmetries for a no-skill program. Both books hold exactly the mask names, so concentration and the
persistence tilt (persistent members are high-drift names: p05 measured +1.1e-5/h for a lag-masked basket over the
plain basket) are common to both. Remaining asymmetries: (a) A's weights are current, S's are k old: when a book's
weights on persistent names depend on the returns that MADE them persist (momentum-like weights over a window
longer than k), A's relative weights already reflect the selection and S's do not; (b) entrants (in play now, not
k ago) are outside the mask in BOTH books, so the test never sees the program's bets on names younger than k;
(c) re-centring adds a constant per row; A re-centres on rows where D[i] has a name outside mask (entrants and
names without an execution bar), S where Ds[i] has one (leavers) - entrants and leavers have different return
profiles under volume-follows-price, so the re-centring constants carry different net tilts; (d) sources in DEV
for i < k: S then uses in-sample (DEV) decisions - not a look-ahead, but a program whose DEV and VAL weights
differ in distribution (gross, net, breadth) gets an S unlike A for reasons unrelated to timing; (e) slow programs:
S_k with k near 720 h stays correlated with A_k (power loss).
(3) Shapes. Small p without skill: books whose payoff comes from the persistence selection with weights built
over windows longer than k (a); books keyed on recent membership changes, where re-centring tilts differ (c).
Large p with skill: slow signals (e); skill concentrated in recent entrants (b); a book whose edge is in the
first weeks after a listing.
(4) Calibration reach: real calendar, resampled prices -> membership independent of null returns (H2), null A
cross-section weakened (H1), intraday and (null B) funding structure kept (H3). The calibration can measure the
test's size only where churn does not depend on the traded returns; it cannot detect (2a), (2c) or the
survivorship part of (3).
(5) Experiments for part 2: see below.

## Part 2 experiment plan (synthetic unless stated; one process; times measured on this machine)
X1 Circular vs paired lag, look-ahead in p: churn worlds with volume following price; no-skill programs incl. a
   long-lookback reversal (lookback 60-80 days) and slow momentum; p distribution for both forms. 20 worlds, about
   30 min.
X2 Size of the paired lag test (the main one): churn worlds tuned to 4-6 new members per month (more live symbols,
   stronger volume regimes), three membership variants - (a) volume follows price, (b) volume independent of price,
   (c) constant membership - in rising and falling markets; fixed programs: the three ucal families, slow momentum
   smoothed inside the cross-section, long basket, long-lookback reversal, an entrant-tilted book, a carry on
   persistent synthetic funding; the kernel's own ugates on production blocks. Record rejection rates at 0.025 /
   0.05 / 0.10 with binomial SE, mean p, KS distance to uniform, mean Sharpe(S_k) - Sharpe(A_k), gross and net of A_k
   and S_k, ties. About 60-80 s per world with 100 lags: 40 worlds per variant -> about 2 h for (a)+(b), 1 h for (c).
X3 Power: noisy cross-sectional oracle (as UOracle) at Sharpe 1.0 and 1.5, speeds 1 and 20 days, in the same churn
   worlds; paired lag vs circular. 20 worlds x 4 settings, about 1 h.
X4 Calibration fidelity: null A and B worlds built from a synthetic source WITH volume-follows-price churn; run X2's
   programs through the ucalibrate protocol and compare their null pass rates with X2(a)'s direct rates (does the
   calibration see the bias?). About 1 h.
X5 Null A fallback share and cross-section on the REAL panel (counts only, calibration handle; heavy source of
   about 1.3 GiB): fallback symbol-days by year and the real vs null A mean pairwise correlation. About 15 min once
   memory allows.
X6 DEV sources: paired lag with lags restricted to VAL sources (k <= i) vs the full rule, programs whose DEV and VAL
   breadth differ. About 20 min.

# PART 2 - commit 32e32e0 (fix pass 5): copy review7\kern32 (142 blobs verified, setup32.py)

## A. Review of the diff
A1 G6 lag code (omr/upipeline.py g6_lags, g6_books, ugates) - SOUND (reading). The source of VAL row i is grid
  row g0 + i - k (k from 720 h to L // 2, g6_lags faults when the grid has fewer rows before g0); the mask is
  ok[i] & P[g0 + i - k]; both own sets are the in-play rows they came from (A: P[g0 + i], S: P[g0 + i - k]);
  re-centring adds (own net - masked net) / n_mask with sequential sums; rows under 10 mask names flat in both;
  rows whose source precedes the unit have an empty mask (flat); the plain actual run is reused only when A_k
  equals it bit for bit; ties within 1e-12 and the 1e-9 margin only raise p; the detail records lag_min/max.
  The only post-decision input is the execution-bar flag inside ok[i], shared by both books. tests/
  test_g6_paired.py T2 can fail (the circular negative control is asserted to leak).
A2 ucalibrate resume (Partial) - SOUND with two LOW notes (p06_a_checks.py, p06_out.txt): the header binds protocol,
  semantic hash, research hash, dry-run flag, family hashes, seeds, world counts, levels, speeds, perm_n, draws,
  rho grid, fine points and pool size; another header is refused (worlds 3 -> 4: refused); results are
  returned in argument order from the stored rows, so the artifact does not depend on completion order or on
  interruptions; the partial is removed only after the artifact is written and logged.
  - A2a LOW: a torn last line has no newline, so the first record appended after a resume is glued to it and is
    lost again on the next read (that task reruns; deterministic, so harmless but wasteful). Fix: append a
    newline first when the file does not end with one.
  - A2b LOW: a duplicated key keeps the last value silently; the partial is plain JSON without a chain, so an
    edited partial flows into an artifact that log_calibration then logs - the same procedural trust as the
    seal itself (one pushed commit + independent recount). Fix: hash-chain the partial lines, or record each
    line's sha256 in the artifact.
A3 decide_both - SOUND (p06): core 1.0+1.5 with top30 1.5 passes; a top30 level outside its bound, power below
  0.5, a missing speed, a core 1.0 level outside its bound, and no qualifying threshold all STOP. A top30
  artifact with NO level-1.5 rows (none at all, or level 1.0 only) raises KeyError inside CB.decide instead of
  returning STOP - still refused (the seal fails), never a silent pass (LOW: make it a STOP reason).
A4 funding coin and monthly pools - SOUND (p07_ucal32.py, synthetic 28-symbol churn source): 6,471 settlement hours,
  0 hours in which two symbols got different coins; null A fallback symbol-days 1,757 of 33,533 (5.2%, was most
  days) and mean pairwise correlation 0.311 (source 0.360; 0.137 before the change); activity, membership
  (67/67 months) and DEV view (28/28) still exact for both nulls. Residual (reading): null A keeps intraday order
  within a source day and null B mirrors it, so a family can still earn real intraday autocorrelation (makes null
  pass rates conservative only).
A5 data.py G1-G3 - SOUND (p06): a 404 marker only for days >= 7 days old; a used daily file must equal its pin
  (DailyPinMismatch is a DailyRevision: stop before any write in `data universe`, an exception before any write
  in snapshot); commit journal: a crash simulated after EVERY step of commit_tables (manifest.new, journal, each
  keep-old and move-new, the manifest replace, cleanup) is recovered by recover_commit to all-old before the
  manifest replace and all-new after it, every table matching its manifest, no leftover file or journal.
  Recovery runs only at `python -m omr.data` start; until then readers fail closed (sha mismatch) - acceptable.
A6 documents - SOUND; NOTE: CONSTITUTION's calibration bullet still says null B "funding unchanged" before the
  sentence that adds the sign coin to both nulls.

## X7. Membership on the FILLED real data - SOUND (p08_x7_membership.py, p08_out.txt; counts only)
79 known months, 17,795 eligible symbol-months: 0 months with any difference between my independent
implementation and the kernel's (eligible set, top30, next30, order); removing rows at or after a month start
changes no month; the control (x1e6 volume over the 46 days before / from the month start) changes 12/12 / 0/12.

## X2 / X1 / X6 - size of the paired lag G6 (p09_x2.py, p09_results.jsonl, p09_summary_out.txt)
Synthetic worlds with NO timing skill (iid hourly returns = market factor with drift +-5e-5/h + constant per-symbol
drift + noise; funding iid); 100 symbols with staggered listings/delistings (lives 300-900 days); three variants:
vfp (quote volume follows price), indep (volume regime only; SAME price paths as vfp for reps 0-4, so the pair
isolates the volume link), const (30 symbols, constant membership: a plain lag test). Churn reached 2.0 new top30
members per VAL month (I could not reach 4-6 with a generator that fits in memory). 28 worlds: vfp 12, indep 10,
const 6 (half rising, half falling). Seven fixed no-skill programs; G6 from the kernel's own pieces (g6_lags,
g6_books, g6_books_tie, g6_paired_p) with 40 lags (production 200; p resolution 1/41); the kernel's own ugates p
was recomputed for mom in 10 worlds and equals mine in 10/10.
Rejection rates (p <= 0.025 / 0.05 / 0.10), all worlds of a variant:
- vfp (12): carry 0/0/1; lrev 1/2/2; mom, rev, slowmom, entrant 0/0/0; basket p = 1 (40/40 ties) in 12/12.
- indep (10): lrev 0/0/1; every other program 0/0/0; basket p = 1 in 10/10.
- const (6): carry 0/1/2; lrev 0/1/1; mom, rev, slowmom 0/0/0; basket and entrant p = 1 (ties).
Pooled over the 162 non-tie (program, world) p values: p <= 0.025 in 0.6%, <= 0.05 in 2.5%, <= 0.10 in 4.3%
(nominal 2.5 / 5 / 10): the test is CONSERVATIVE overall. Mean p by program: rev 0.76-0.86 (the actual reversal is
worse than its lagged copies: dSh(S - A) +0.6 to +1.4), entrant 0.38-0.41, mom 0.45-0.50, slowmom 0.48-0.55,
carry 0.33-0.42, lrev 0.46-0.55 (falling markets 0.29-0.36, rising 0.63). SE per cell at n = 6: 0.12 at a 10% rate.
Gross and net: both books have equal gross for every program except the entrant tilt, whose ACTUAL book keeps
1-2% of its gross (0.014 vs 0.599 for the lagged book: its longs are names not in play k hours earlier, removed
by the mask). That did not produce rejections (0/22 churn worlds at 0.10), but the test cannot credit a book whose
edge sits in recent entrants (power blind spot, see findings). Costs of A and S within a few percent; ties only
for constant books (basket; entrant under constant membership).
volume-follows-price vs independent (paired price paths): no difference in rejection rates (vfp lrev 2/12 vs
indep 1/10 at 0.10; everything else 0) - the causal construction holds.
X6 (sources restricted to VAL rows, rows i < k flat in both; slowmom and lrev in 20 worlds): 0 rejections at
0.025 and 0.05, lrev 2/16 at 0.10 in churn worlds; mean p 0.44-0.65 - the DEV-period sources do not change size.
X1 (the e4e44e2 circular form on the same lags, vfp, 8 worlds: basket, lrev, slowmom): the basket's p falls from
1 (lag form: ties) to a mean of 0.46 (no ties: the circular mask and re-centring break the identity), lrev 1/8
and slowmom 1/8 at 0.10. The circular form's look-ahead (part 1, p05b) did not show as a size excess at this
churn level; the reason for the change stands on the causality argument and p05b, not on these 8 worlds.

## P13 diagnostic: why rev gets p ~ 1 (p13_diag.py, p13_out.txt; 3 constant-membership worlds = plain lag test)
Per program: Sharpe of the actual A vs the mean of its 40 lagged copies S_k, with the production engine, with zero
costs, and with zero costs and no rebalance band; turnover and daily volatility of both.
- 24-hour reversal (rev): turnover A = S (7,635 vs 7,664), mean daily return A = S (-0.0088 vs -0.0089) but daily
  volatility A 0.0081-0.0083 vs S 0.0088: the cost-dominated actual looks WORSE (Sharpe -20.6 vs -19.1), S >= A
  in 97.5-100% of lags (p ~ 1). With zero costs the volatilities match (0.0087-0.0089) and S >= A in 40-85%.
- the mirror, a 24-hour momentum book (fmom, added here): volatility A 0.0092-0.0094 vs S 0.0088, so the actual
  looks BETTER: S >= A in 0%, 15%, 20% of lags; in the first world p = 1/41 = 0.024, below a 0.025 threshold,
  with no skill. With zero costs S >= A in 12.5%, 62.5%, 52.5%.
- slow books (mom, slowmom, carry, lrev): volatilities within 2%; differences come from the mean (one draw of A
  against 40 lags), no systematic cost effect.
Mechanism: the actual book trades on the very moves that make its daily P&L, so its daily trading costs covary
with that P&L (negatively for a contrarian book, positively for a momentum book); the lagged book trades on old
signals, so its costs do not. For books whose costs dominate, this changes the net-return volatility by -9% / +5%
and moves p to the extremes without any timing skill.

## X3 - power of the paired lag G6 (p10_x3.py, p10_results.jsonl, p10_out.txt) - first 10 worlds
The kernel's noisy oracle (UC.UOracle, signal rho z + noise on the future k-day return), rho bisected per world so
that the true VAL Sharpe is 1.50 (+-0.01); G6 from the kernel's own evaluate_weights_u (ugates) with 40 lags
(p resolution 1/41 = 0.024; production uses 200). Worlds: p09 vfp (churn ~2 new members / month) and const.
- 1-day speed: p = 1/41 (no lag beat the actual) in 10/10 worlds (6 vfp, 4 const).
- 20-day speed: const 4/4 at p = 1/41; vfp p = 0.024, 0.024, 0.024, 0.049, 0.049, 0.098 -> 3/6 at <= 0.025,
  5/6 at <= 0.05, 6/6 at <= 0.10.
- In churn worlds the MASK costs the actual book part of its edge: mean Sharpe of A_k (names also in play k hours
  earlier, re-centred) 0.66-1.46 at 1 day and 0.71-1.57 at 20 days, against 1.49-1.51 in constant worlds; the
  lagged copies average -2.9 to -3.9 (1 day: costs, no edge) and -0.01 to -0.57 (20 days).
Interim reading: power is ample at 1 day; at 20 days in churn worlds it sits near the POWER_MIN = 0.5 line at the
strictest threshold (0.025). Extension running: 14 more vfp worlds at Sharpe 1.5, then Sharpe 1.0.

## X3 - FINAL (p10_results.jsonl 24 worlds at Sharpe 1.5; p10_results_s1.0.jsonl 12 worlds at Sharpe 1.0; p10_summary_out.txt)
G6 rejection rate (power) with 40 lags; p values are multiples of 1/41 (0.024 = no lag beat the actual):
| true VAL Sharpe | world | 1-day: p<=0.025 / 0.05 / 0.10 | 20-day: p<=0.025 / 0.05 / 0.10 |
| 1.5 | churn (vfp) 20 | 20/20 / 20/20 / 20/20 | 7/20 (35%) / 13/20 (65%) / 18/20 (90%) |
| 1.5 | constant 4     | 4/4 / 4/4 / 4/4       | 4/4 / 4/4 / 4/4 |
| 1.0 | churn (vfp) 8  | 8/8 / 8/8 / 8/8       | 2/8 / 3/8 / 5/8 |
| 1.0 | constant 4     | 4/4 / 4/4 / 4/4       | 2/4 / 2/4 / 3/4 |
Production uses 200 lags (p <= 0.025 allows 4 of 200 lags to beat the actual, the 40-lag run allows none). From the
per-world counts of beating lags (0 of 40 in 7 worlds, 1 in 6, 2 in 4, 3/6/9 in one each) a binomial translation
gives a production-equivalent 20-day churn power at Sharpe 1.5 of about 45% at 0.025, 75% at 0.05, 90% at 0.10.

X3-F1 MEDIUM (power, design; no false-pass risk): in churn worlds the mask (names in play BOTH at the decision row
and k hours earlier) removes every name whose membership changed in between. With VAL = 3 years the lags run from
30 to 547 days (L // 2), so a typical lag drops a third or more of the top30. Measured: the oracle's actual book on
the mask averages Sharpe 0.98 (1-day) and 1.10 (20-day) instead of 1.50 (constant worlds: 1.50 exactly). At 1-day
the lagged copies are far worse (about -2.9: costs, no edge), so power stays 100%; at 20 days the lagged copies are
near 0 and the 20-day power at the strictest grid threshold (0.025) is about 35-45%, under POWER_MIN = 0.50. My worlds
churn about 2 new members per month; more churn on the real calendar lowers it further.
Consequence: if the calibration's null pass rates leave only 0.025 qualifying, decide_both will STOP on top30
20-day power (correctly - it measures this itself), or a real slow cross-sectional edge in a churning universe is
under-credited. Not a defect in the code; the owner should expect this before spending a long calibration run.
Smallest fix (optional, needs a size re-check like X2): cap the lag range, e.g. hi = min(L // 2, 180 * 24) in
upipeline.g6_lags (line 835), so the source and decision rows share more of the membership; or accept the risk and
let decide_both decide.

## X4 - calibration dry run: runs, crashes, resumes, finishes - SOUND (p12_x4.py, p12_out_crash.txt, p12_out_resume.txt,
## p12_check.py / p12_check_out.txt, p12_diff.py / p12_diff_out.txt)
The kernel's own entry point UC.main(["--unlocked-dry-run", "--out", <scratch>, "--worlds", "2", "--oracle-worlds",
"1", "--workers", "0"]) on the copy, with two disclosed reductions for time and memory: the synthetic churn universe
at 60 symbols instead of 170, and perm_n 40 instead of 200 (both enter the run header, so crash and resume runs
share them). Output, partial file and access log in scratch; --out means log_calibration is not called.
- Crash run: a simulated kill (KeyboardInterrupt raised right after the 3rd recorded task) at 6.4 min; the partial
  file holds the header and 3 task lines (null A worlds 11000, 11001; null B world 14000); shared-memory blocks
  released by the finally clause.
- Resume run (same command): "resuming: 3 finished tasks", ran only the missing null B world ("2/2 done (1
  resumed)"), the oracle curves (81 / 41 / 1 rhos per speed and null), the rho tuning (e.g. null B fast level 1.5:
  rho 0.05362 -> achieved 1.505) and the power tasks; saved the artifact and removed the partial; 7.0 min.
- The artifact's rows for the 3 pre-crash tasks equal the partial's rows field for field (0 differences over 9
  rows; the artifact orders rows by family). The unit verdict recomputed from the stored rows (verdict_from_rows)
  equals the stored verdict.
- The unit verdict is STOP (no threshold keeps the null pass rate <= 3%): meaningless at 2 worlds (6 rows per null,
  one pass = 17%). Reproducing the X2 rates: NOT FEASIBLE at this scale (2 worlds x 3 families per null against
  X2's 28 worlds x 7 programs, and different programs) - not attempted.
- Scale note (estimate, not measured at production size): one null world task took about 2 min serial at 60 symbols
  and 40 lags; production has 200 lags, about 134 panel symbols, 200 worlds per null and 100 oracle worlds, so the
  real run is in the tens of CPU-hours to days; the resume feature is what makes it practical.

## X5 - null A on the REAL panel (p11_x5.py, p11_out.txt; own read-only reader, counts and correlations only;
## correlations for DEV months only)
- Panel (every symbol ever a top30 member, UNIVERSE_START to VAL end, kernel rule): 134 symbols.
- Monthly pools: 62 months pooled, 8 months on the whole-period pool (no unit or pool under 90 days); smallest pool
  110 days, median 365 days.
- Null A source days (3 worlds, seeds 11000-11002): 169,774-169,791 symbol-days share the month's drawn day (98.2%),
  3,060-3,077 fall back (1.8%), 0 own. (The synthetic p07 source had 5.2% fallback.)
- Mean pairwise daily-return correlation of the month's top30 members, DEV months, by year:
  real 2020 0.642, 2021 0.601, 2022 (H1) 0.747; null A 0.669-0.681, 0.602-0.629, 0.593-0.637.
X5-N1 NOTE (null realism): the cross-section is restored on average (2020, 2021 match within 0.03-0.04), but a
stress regime's extra co-movement is not reproduced (2022 H1: 0.59-0.64 in null A vs 0.75 real), because a month's
source days are drawn from the whole UNIVERSE_START..VAL-end pool of fully active days, not from that month's
regime. A cross-sectional family therefore sees somewhat more dispersion in a null A crisis month than it would in
reality. Direction of the effect on the null pass rate is not established; small next to the round-6 problem (the
member correlation was 0.137 before this change). No fix required; a regime-local pool (e.g. days within +-6
months of the month) would be the refinement if wanted.

## P14 - real top30 churn, for X3-F1 (p14_churn.py, p14_out.txt; own read-only reader, kernel rule, counts and
## fractions only, no names)
- 63 months with a top30 unit. New members per month: DEV months 3.48 mean (median 3, max 13); VAL months 3.59 mean
  (median 3, max 9). My X2/X3 churn worlds had about 2.0 - the real calendar churns MORE.
- Share of a VAL month's top30 that was also top30 k days earlier (the membership part of the G6 mask): lag 30-90
  days 0.84 (min 0.57); 90-180 days 0.70 (min 0.50); 180-365 days 0.64 (min 0.40); 365-547 days 0.57 (min 0.33);
  about 0.65 averaged over the production lag range.
Reading for X3-F1: on the real calendar a typical G6 lag keeps about two thirds of the actual book's names, so the
20-day power measured in my churn worlds (about 35-45% at 0.025) is unlikely to be better on the real calendar. A
cap of 180 days would keep 0.70-0.84 instead of 0.57-0.65.

## C. Verdict on re-keying 32e32e0: READY (no CRITICAL or HIGH finding)
- MEDIUM 1: X3-F1 (20-day power of the paired lag G6 in a churning top30; upipeline.py:835 lag range, :858 mask).
  Not a false-pass risk; the calibration measures it and STOPs if power is short. If the owner wants the lag cap,
  it must go in BEFORE the re-key (any later change needs a new key and a new calibration).
- LOW: entrant blind spot (upipeline.py:858-868); cost/volatility non-exchangeability for cost-dominated fast books
  (upipeline.py:942-957); A2a torn line (ucalibrate.py:713-736); A2b unchained partial / duplicate keys
  (ucalibrate.py:721-726); A3 KeyError instead of STOP (ucalibrate.py:857 -> calibrate.py:490).
- NOTE: lrev per-program size 3/28 at 0.05; A4 intraday order; A5 recovery only at `python -m omr.data` start
  (data.py:1673); A6 CONSTITUTION.md:271 stale "funding unchanged"; X5-N1 crisis co-movement in null A; X1 no size
  excess of the circular form at 2/month churn; X4 production run time (estimate).

# X8 - power of the paired lag G6 on the REAL membership calendar (p15_x8.py, p15_summary.py)
Worlds: the real structure of the 134-symbol top30 panel (activity, usable bars, quote volumes, funding settlement
times and intervals, my own read-only reader) with SYNTHETIC prices and funding rates (iid market factor + constant
drift + noise, as X2 / X3; the source's real price ratios and rates are overwritten before any world is built),
built by the kernel's own world_udata over a UWorld subclass without resampling or flips.
Membership check: the kernel's rule on these worlds gives the real top30 calendar in 67 / 67 months (ordered
member lists and known flags equal to the rule on the real activity of every crypto perpetual).

## X8d - what a lag test on "today's members, earlier information" would keep (p15_out_d.txt, p15_x8d.json;
## counts only, 36 VAL months, one decision hour per VAL day, every whole-day lag in the band)
| lag band (days) | present mask: in play then (mean / min over months) | tradable then: usable bar + fresh funding (mean / min) |
| 30-89   | 0.807 / 0.642 | 1.000 / 1.000 |
| 90-179  | 0.692 / 0.578 | 0.969 / 0.912 |
| 180-364 | 0.633 / 0.469 | 0.872 / 0.775 |
| 365-547 | 0.567 / 0.367 | 0.773 / 0.614 |
(shares of the decision row's in-play names; mean in-play names per VAL row 29.9). The membership-based mask
matches P14's month-level overlap (0.84 / 0.70 / 0.64 / 0.57).

## X8a / X8b / X8c (p15_eval.jsonl 24 worlds, seeds 15000-15023; p15_out_eval.txt; p15_summary.py -> p15_summary_out.txt)
Method as the calibration: ONE rho per speed from the mean curve over the 24 worlds (fast 0.05190, slow 0.07953),
then the kernel's evaluate_weights_u (all gates; G8 not run; 40 lags). Realized VAL Sharpe mean 1.500 at both speeds
(SD over worlds, n-1: fast 0.63, slow 0.69; min-max 0.51-2.84 and 0.08-2.75).
| 24 worlds | G1 | G2 | G3 | G4 | G5 | G7 | G10 | G6 <= .025/.05/.10 | Tier-1 <= .025/.05/.10 |
| 1 day     | 21 | 24 | 23 | 0  | 24 | 24 | 24  | 24 / 24 / 24       | 0 / 0 / 0              |
| 20 days   | 21 | 22 | 24 | 23 | 24 | 23 | 24  | 17 / 18 / 20       | 17 / 18 / 20 (0.71 / 0.75 / 0.83) |
20-day lags beating the actual (of 40), per world: 0 in 17 worlds, then 1, 2, 3, 6, 8, 9, 15. The 200-lag translation
(per world, Jeffreys posterior for the share of beating lags; conservative for the 0-of-40 worlds) gives Tier-1
0.59 / 0.72 / 0.81. Mean curve, 1 day: Sharpe = -3.9 + 104 rho near the tuned rho (cost drag about 3.9 Sharpe units at
12.5 bps per side), so VAL Sharpe at doubled costs is about 1.5 - 3.9 < 0 in every world: G4 fails 24 / 24.
X8b (20 days, same weights, G6 only, lag rule patched in this process): uniform 30-365 days 15 / 18 / 21; log-uniform
30 days - L // 2 15 / 18 / 20; production 17 / 18 / 20 - neither reference arm is better.
X8c (20 days, production arm; mean Sharpe of the masked actual A_k / lagged copies S_k; share of in-play cells kept):
30-89 d 1.24 / -0.15 / 0.805; 90-179 d 1.25 / -0.25 / 0.695; 180-364 d 1.27 / -0.29 / 0.634; 365-547 d 1.12 / -0.21 /
0.567 (all arms pooled: 1.32 / 1.25 / 1.27 / 1.12).
Side check P17 (p17_disp.py, REAL DEV rows only, rates): cross-sectional SD of members' daily returns 0.030 / 0.047 /
0.036 (2020 / 2021 / 2022 H1) against 0.039 in the synthetic worlds; median idiosyncratic vol 0.62 against 0.75. The
synthetic worlds are not less dispersed than reality, so the cost drag (in Sharpe units) is not overstated.
X2 histogram check (p09_hist.py, p09_hist_out.txt): lrev (60-day memory) p is U-shaped (SD 0.34 vs 0.29 uniform;
4 / 28 in the lowest decile, 9 / 28 in the top two); 14-30-day books are not over-dispersed (SD 0.21-0.25).

X8-F1 HIGH (process; certain STOP): the top30 1-day oracle cannot pass G4 at true Sharpe 1.5, so top30 fast Tier-1
power is 0 / 24 and decide_both (ucalibrate.py:871-877, POWER_MIN at both speeds) STOPs with certainty, whatever the
G6 threshold. Not a false-pass risk. Fix: a cost-viable fast speed for the universe oracle (X9).
X3-F1 (MEDIUM) is CLOSED by X8: on the real calendar the 20-day Tier-1 power is 0.71 / 0.75 / 0.83 (> 0.50 at every
threshold); my lag-cap suggestion is withdrawn (the coordinator's over-dispersion argument holds, and X2's lrev shows
the effect already at 60-day memory).

## X9 - speed sweep for the universe oracle (p15_x8.py modes curve9 / eval9; p18_curves.jsonl, p18_eval.jsonl;
## p18_summary.py -> p18_summary_out.txt; same 24 real-structure worlds and method as X8a, 40 lags)
| speed | cost drag (Sharpe units, fit on rho <= 0.10) | rho at mean 1.5 | G1 | G2 | G3 | G4 | G5 | G7 | G10 | G6 .025/.05/.10 | Tier-1 .025/.05/.10 |
| 1 d  | 3.86 | 0.0519 | 21 | 24 | 23 | 0  | 24 | 24 | 24 | 24/24/24 | 0/0/0 |
| 3 d  | 1.50 | (curve only) | | | | | | | | | |
| 5 d  | 0.93 | 0.0532 | 22 | 24 | 24 | 20 | 24 | 23 | 24 | 20/21/23 | 18/18/19 (0.75/0.75/0.79) |
| 7 d  | 0.64 | 0.0554 | 19 | 22 | 24 | 20 | 24 | 24 | 24 | 16/17/21 | 15/15/19 (0.62/0.62/0.79) |
| 10 d | 0.39 | 0.0589 | 22 | 23 | 24 | 23 | 24 | 24 | 24 | 15/19/21 | 15/18/20 (0.62/0.75/0.83) |
| 20 d | 0.29 | 0.0795 | 21 | 22 | 24 | 23 | 24 | 23 | 24 | 17/18/20 | 17/18/20 (0.71/0.75/0.83) |
Realized VAL Sharpe mean 1.50 at every speed (SD 0.52-0.69). Mean G4 value (VAL Sharpe at doubled costs): 5 d 0.66,
7 d 0.87, 10 d 1.03. The pre-registered rule (fastest of 5 / 7 / 10 days with Tier-1 >= 0.65 at all three
thresholds) selects 5 DAYS. 7 days scores below 5 and 10 at two thresholds: sampling noise (SE about 0.10 at n = 24).
Margin note: the real panel's idiosyncratic vol is lower than the synthetic one (0.62 vs 0.75, P17), so the real
cost drag in Sharpe units is about 20% higher (5 d: about 1.1 instead of 0.93); expect top30 5-day power a few
points lower in the real calibration, still above 0.50 on these numbers; the oracle-first run order shows it early.

## C (restated at 22:45). Verdict for commit 32e32e0: NOT READY to re-key (supersedes the READY of 16:27, which
## predates X8)
What 32e32e0 would do in the calibration: run every phase of both units (tens of CPU-hours), then decide_both
STOPs with certainty: the top30 1-day oracle fails G4 in 24 / 24 worlds (cost drag 3.9 Sharpe units at 12.5 bps
per side), so top30 fast Tier-1 power is 0 < 0.50 at every threshold (X8-F1, HIGH). In addition the SHARED
threshold couples the units: the core qualifies 0.10 by one pass, so the top30 null rates could pull both units to a
lower threshold. Nothing false would be sealed; the cost is the run and a new key.
The fix pass must contain: (1) the universe oracle's fast speed changed to a cost-viable speed (5 days, X9), core
unchanged, everywhere the universe uses speeds (ucalibrate.py:663, 671-672, 833, 907, 922, 1007 use CB.SPEEDS as
days); (2) the G6 threshold decided per unit, each unit with its own power check, the seal failing if either unit
fails, and evaluation using the program's own unit's threshold; (3) an incomplete unit artifact giving STOP with a
reason (A3); (4) the rules text: top30 certified for holding periods of about 5 days and longer, and why.
Recommended in the same pass: A2a / A2b (partial file), oracle phases first with an advisory, CONSTITUTION:271.
Opinions (coordinator questions):
(i) fast speed by cost viability under G4: no objection. G4 and the cost rate encode the deployability standard; a
unit whose fastest certified holding period is set by that standard is coherent, provided the rules say plainly that
top30 certifies holding periods of about 5 days and longer and that faster cross-sectional books fail G4 by design
(not by test weakness). The choice was pre-registered; the residual is the 20% higher real cost drag noted above.
(ii) the cost-dominated reversal family in the null pass rate: not a must-change for correctness (the pooled rate is
a defined estimand, and the core pools too), but it dilutes the top30 rate by about one third (a family with 0 passes
in 1 of 3 families: pooled = 2/3 of the other two families' rate) and so can loosen the threshold choice by one grid
step. X8 / X9 show a stricter threshold costs little power (20 d 0.83 -> 0.75 -> 0.71; 5 d 0.79 -> 0.75 -> 0.75),
and with the unit now certified for >= 5-day holding a 4-96-hour family sits outside the certified domain. I recommend
re-ranging ucal_xs_reversal to the certified holding range in this pass, since a re-key is coming anyway; if the
coordinator keeps it, disclose the pooled rate without that family next to the per-family rates.

# FIX PASS 6 REVIEW (uncommitted working tree, base 32e32e0) - verdict READY for the re-key
Reviewed files (sha256, working tree, re-hashed unchanged at 22:38): fp6\sha256_reviewed.txt
  444f2a9f...503db4 omr/ucalibrate.py; 600a89fe...b63c omr/kernel_lock.py; 867edaf6...60de omr/evaluate.py;
  6462623b...bf3 omr/selftest.py; c7ee2a1f...a07a omr/status.py; 3181df1d...1868 tests/test_ucalibrate.py;
  79273216...4d9db tests/test_ledger_lock.py; dea6ca83...34da tests/test_evaluate.py; 8d13d65d...e142 CONSTITUTION.md;
  eca48b09...5da4 LANGUAGE.md; 1f9ad6fb...fcd4 KERNEL_PROPOSALS.md; 1a1ce62b...6af05 notes/kp015_build_evidence.md.
Method: git diff 32e32e0 (read only); a scratch copy kern_fp6 = kern32 + the 12 files (hashes equal); probes
p19_fp6.py (p19_out.txt); the builder's light tests in the copy (p19_tests.py: 45 passed, 19 deselected).
F1 per-unit threshold - SOUND. decide_both (ucalibrate.py:940) = unit_verdict on each artifact alone -> calibrate.decide
  on that unit's rows; probes: core 0.10 / top30 0.05 chosen independently; every top30 null pair made to pass ->
  top30 None, STOP naming top30, core still 0.10; core rows changed -> top30 still 0.05. seal (kernel_lock.py:379-387)
  refuses on STOP or any missing unit and writes {u: float}; require_sealed / thresholds_of (kernel_lock.py:412)
  refuse a float seal, a one-unit mapping, a bool or text; evaluate (evaluate.py:210-211) takes thresholds[prog.unit]
  right after the parse (prog.unit is validated against C.UNITS = UNITS_SEALED at parse, so no KeyError and never
  the other unit's value); refusal order unchanged (seal, ledger chains, data, generation plan, parse); the trial
  row records one float (evaluate.py:278); no other reader of the seal as a float (grep of every .py).
F2 incomplete artifact -> STOP with a reason - SOUND for what artifact_gaps (ucalibrate.py:911) lists (no level-1.5 rows
  for a speed, no oracle, empty null rows: STOP "top30 artifact incomplete: ...", the other unit still decided).
F3 Partial - SOUND. Round trip exact for NaN, +-inf, -0.0, 1e300, 5e-324, numpy float64 / float32 / int64 / bool,
  tuples, int dict keys (canonical is idempotent on its own output): 0 discarded, loaded == _plain(fresh). Torn tail:
  discarded 1, newline added, the next record survives. Flipped character: discarded, task reruns. Same result twice
  accepted, different results -> PartialMismatch. An edited line with a recomputed sha is ACCEPTED: the sha detects
  damage, not deliberate edits (same procedural trust as the seal).
F6 oracle first - SOUND by reading: tasks are keyed and seeded per task, rows sorted, the artifact written with sorted
  keys; the advisory flags power below POWER_MIN at the LARGEST threshold (power is monotone in the threshold, so this
  is a certain STOP) or a level outside its bound; no exit. The builder's heavy order test was not run (deferred).
F8 USPEEDS - SOUND: every universe use of the speeds as days reads USPEEDS (task_oracle_curve, task_oracle_power,
  oracle_summary, artifact_gaps, oracle_advisory, calibrate_run, run_header, artifact protocol); no CB.SPEEDS left in
  ucalibrate; calibrate.decide reads the names only; header binds speeds_days and PROTOCOL_VERSION 4; an old top30
  artifact is refused by its semantic hash. Texts (CONSTITUTION s8 / s13, LANGUAGE s10) match the code: per-unit seal,
  5 / 20 days and the reason, the two G6 limits, run order.
Findings:
- FP6-1 LOW (ucalibrate.py:931 unit_verdict): a MALFORMED (not incomplete) row still raises: a null row of an unknown
  family -> KeyError 'zzz'; an evaluated null row without gates -> KeyError 'gates'; an oracle row without level ->
  KeyError 'level'. The seal still refuses (exception, never a pass); artifacts are machine-written and logged. Fix:
  wrap verdict_from_rows in unit_verdict with except (KeyError, TypeError, ValueError) -> STOP "<unit> artifact
  malformed: <error>".
- FP6-2 LOW (text, KERNEL_PROPOSALS.md:264): "audit round 7 READY" is stale: the round-7 verdict on 32e32e0 was
  restated NOT READY after X8 (certain STOP on top30 fast power). Fix: say so.
- FP6-3 NOTE (kernel_lock.py:412): thresholds_of accepts any number (NaN, inf, 5) - not a regression (the old
  float(...) did too; only a hand-edited lock can hold one). Hardening: require each value in C.G6_GRID.
- FP6-4 NOTE (kernel_lock.py:48): UNITS_SEALED duplicates C.UNITS; a future unit would make evaluate raise KeyError
  (loud). Use C.UNITS.
- FP6-5 NOTE (ucalibrate.py Partial): a torn HEADER (crash during the first write) is refused as "belongs to another
  run" (needs --restart): safe, message misleading. Within one session record() of a key twice keeps the last value;
  the conflict shows at the next resume (cannot happen in run_tasks: each key runs once).
- FP6-6 NOTE (LANGUAGE.md:314): "pays roughly half its gross or more per year" understates full daily replacement:
  2 x 12.5 bps x 365 = about 91% of gross per year. CONSTITUTION.md:484 "24 audit worlds with the real membership
  structure" should add "and synthetic prices".
Residual (design, coordinator's decision): the cost-dominated ucal_xs_reversal family still dilutes the top30 null
pass rate (opinion ii). Not checked: the heavy F6 order test and the full suite; a dry or real calibration run on the
fix-pass-6 code; selftest end to end; the multiprocessing path; the real sealed core artifact (ledger not read).

# X10 - the four seal-rule oracle cells THROUGH the kernel's null builders (commit 4286abf; copy review7\kern86,
# setup86.py: 143 blobs written and re-hashed equal to the tree, 0 problems; script p20_x10.py, p20_summary.py)
Method: the kernel's own task functions run in one process (UC._SerialPool with UC._init on the source's shared
arrays), so every task is the calibration's code path; observation-only hooks record per evaluate_weights_u call the
lags, the share of in-play cells kept by the mask and the Sharpe of A_k / S_k (p20_lags_*.jsonl).

## Q1 - the pilot's oracle worlds (dry-run synthetic source, UC.synthetic_source(); p20_out_q1.txt, p20_q1_rows.jsonl,
## p20_q1_summary.txt)
Reproduction: UC.task_oracle_power with the pilot's seeds (A 17000-17003, B 18000-18003) and tuned rhos (from
pilot_ucal.json), 200 lags: all 16 p values equal the pilot's (e.g. A 17000 fast 0.0249 / slow 0.1443; B 18001 slow
0.3234), realized VAL Sharpe equal.
Source structure: dry-run synthetic source, panel 149, 5.89 new top30 members per VAL month (median 6, max 9); null A
pools median 201 days (min 90), fallback 5.4-5.6% of symbol-days. Real calendar: 3.59 per month; pools median 365.
Pooled lag bands (4 worlds per cell; keep = share of in-play cells kept by the mask; A_k = masked actual Sharpe;
S_k = lagged copies, mean and SD over lags; beat = lags with S_k >= A_k, of about 100 / 140 / 280 / 280):
| cell     | 30-89 d                 | 90-179 d                | 180-364 d               | 365-547 d               |
| A fast   | .673 1.14 / -.48 (.52) 0 | .483 1.03 / -.53 (.56) 4 | .392 0.61 / -.54 (.59) 27 | .299 0.49 / -.35 (.56) 38 |
| A slow   | .658 1.11 / -.23 (.69) 4 | .489 1.24 / -.72 (.45) 0 | .384 0.77 / -.37 (.60) 22 | .299 0.49 / -.17 (.55) 69 |
| B fast   | .673 1.44 / -.87 (.65) 0 | .484 1.16 / -.75 (.53) 0 | .391 0.79 / -.55 (.53) 2  | .299 0.69 / -.35 (.49) 18 |
| B slow   | .673 1.32 / -.18 (.52) 5 | .485 1.31 / -.30 (.64) 0 | .391 1.08 / -.19 (.52) 45 | .299 0.82 / -.40 (.64) 18 |
(each cell: keep, A_k / S_k mean (S_k SD), beat). Real calendar for comparison (X8c / X8d): keep 0.81 / 0.69 / 0.63 /
0.57; 20-day masked A_k 1.24 / 1.25 / 1.27 / 1.12 at mean VAL Sharpe 1.5.
Q1 answer: p is large in the three null A slow worlds because the MASKED ACTUAL book collapses at long lags, not
because the lagged copies earn. World 17000: realized VAL Sharpe 0.94 and A_k 0.29-0.67 at 180-547 d (28 beats);
17001: 365-547 d A_k 0.25 against S_k +0.09 (35 beats); 17002: 365-547 d A_k -0.04 against S_k -0.20 (27 beats).
91 of the 95 beating lags of null A slow are at 180-547 days, where the dry-run mask keeps 30-39% of the cells. S_k
is not higher under null A than under null B in any band (at most +0.09 in any world-band), so I see no null-A-
specific mechanism for the oracle; the null A / null B difference in A_k at long lags (0.49 vs 0.82) is within
chance at 4 worlds per cell (B 18001, VAL Sharpe 0.72, has p 0.32 for the same reason). Diagnosis: the dry-run
structure (5.9 new members a month, so the mask keeps 30% at a year) plus chance; the coordinator's hypothesis holds.

## X10 side analysis P21 - null A's monthly pools give the cross-section a membership-dependent drift (p21_pools.py,
## p21_out.txt; synthetic prices only)
Under null A a symbol's expected return in month m is its mean over POOL(m). Members' annualised mean return,
cross-sectional SD (mean over the 62 pooled months):
| source | pool means | whole-period means (what null B keeps) | pool minus whole | pool size median |
| real-structure (Q2 source) | 0.96 | 0.78 | 0.63 | 386 days |
| dry-run synthetic          | 1.15 | 0.77 | 0.88 | 198 days |
The pool-specific part (pool mean minus whole-period mean) of month m against month m-k, correlation over month m's
members, by lag band 30-89 / 90-179 / 180-364 / 365-547 days: real-structure 0.77 / 0.48 / 0.24 / 0.13; dry-run
0.72 / 0.32 / 0.01 / -0.15. So under null A a book that tilts toward recent winners holds a drift of about 0.6 a year
in cross-sectional SD that lagged copies of the same book share less and less with the lag: a timing-like edge with no
timing skill (the sampling noise of a finite pool, SE about 0.039 x 365 / sqrt(386) = 0.72 a year, plus the change of
pool when membership changes). Null B keeps only the constant whole-period drift, which every lag shares. This is the
mechanism the coordinator suspected for ucal_xs_momentum (Q3 measures it).

## Q3 - the calibration families in null worlds on the real-structure source (p20_q3p.py = p20_x10.py mode q3p, the
## kernel's task_null through UC.run_tasks; 12 worlds per null, seeds SEEDS["A"] + 0..11 = 11000-11011, SEEDS["B"] +
## 0..11 = 14000-14011; p20_q3_result.json, p20_q3_summary.txt; ran in parallel with Q2, started at 4,766 MB available)
Every pair was submitted (36 per null). Tier-1 at 0.025 / 0.05 / 0.10:
| family | null A | null B |
| ucal_xs_momentum | 5 / 6 / 8 of 12 (VAL Sharpe 2.07-4.16, every other gate passed in 12 / 12; p: 0.005 x5, 0.030, 0.070, 0.085, 0.149 x2, 0.174, 0.453; n 39-57) | 0 / 1 / 1 of 12 (VAL Sharpe 0.48-3.25; other gates passed 11 / 12; p 0.030, 0.189, 0.239, 0.403, 0.438, 0.647, 0.672, 0.677, 0.687, 0.771, 0.985, 1.000; n 49-60) |
| ucal_xs_reversal (R-J mirror) | 0 / 0 / 0 (VAL -4.12 to -2.10, fails G1-G5, G7) | 0 / 0 / 0 (VAL -3.41 to -1.47) |
| ucal_xs_carry | 0 / 0 / 0 (VAL -4.69 to -1.98) | 0 / 0 / 0 (VAL -4.31 to -2.32) |
Pooled null pass rate per submitted pair: null A 5/36 = 13.9%, 6/36 = 16.7%, 8/36 = 22.2%; null B 0/36, 1/36 = 2.8%,
1/36 = 2.8%. NULL_PASS_MAX is 3%: under null A NO threshold qualifies, so on this source the top30 rule STOPs whatever
the oracle cells give.
Answer: yes - in null A worlds ucal_xs_momentum earns a high Sharpe (median VAL 2.8) and its p values are skewed LOW
(5 of 12 at the minimum 1/201; under null B the same family's p values are skewed high, median 0.66). Mechanism (P21):
null A's monthly pools give each month's members a pool-specific mean return (cross-sectional SD about 0.6 a year)
that changes with membership; a 40-60-day momentum book tracks the current pool's means, its lagged copies 30-547
days back track older pools (correlation of the pool-specific part 0.77 / 0.48 / 0.24 / 0.13 by lag band), so the
actual book beats its lags with no timing skill. Under null B the drift is the symbol's constant whole-period mean,
which every lag shares, and p is not skewed low.

## X10 reference arm P22 - null A with the pool-specific mean removed (p22_fixA.py, p22_out12.txt, p22_result.json;
## my copy only, monkeypatched UWorld; NOT a code proposal, a test of the mechanism)
Change: in null A every active hour of a world day of month m gets (symbol's whole-period mean daily log return -
its mean over POOL(m)) / 24 added to its log return; the shared source day, the intraday path, the funding and
everything else are unchanged. Same source and the same 12 null A seeds as Q3, the kernel's task_null, momentum only.
| momentum, null A seeds 11000-11011 | Tier-1 .025 / .05 / .10 | p values | VAL Sharpe |
| kernel null A (Q3)                 | 5 / 6 / 8 of 12          | 0.005 x5, 0.030, 0.070, 0.085, 0.149 x2, 0.174, 0.453 | 2.07-4.16 (median 2.8) |
| pool mean removed (P22)            | 0 / 0 / 2 of 12          | 0.075, 0.080, 0.189, 0.234, 0.458, 0.527, 0.572, 0.667, 0.721, 0.796, 0.910, 0.940 | 1.18-3.66 (median 1.9) |
(seed 11000 under P22 fails G3.) With reversal and carry at 0 (they fail every Sharpe gate by 2-4 units, which this
change cannot reverse), the pooled null A pass rate becomes 0 / 0 / 2 of 36 (0 / 0 / 5.6%): 0.025 and 0.05 qualify.
The skew disappears and the family still earns its static drift (as under null B), which its lags share.

## Q2 - the four seal-rule cells on the REAL-STRUCTURE source THROUGH the kernel's null builders (p20_x10.py q2:
## UC.calibrate_run(pool, partial, fams, 0, 24) on UC._SerialPool, i.e. tune_rho over RHO_GRID + 41 fine points +
## achieved, task_oracle_power, oracle_summary, oracle_advisory; 200 lags; speeds 5 / 20 days; level 1.5; G8 not run;
## seeds SEEDS["oracle_A"] + 0..23 = 17000-17023, SEEDS["oracle_B"] + 0..23 = 18000-18023; p20_out_q2.txt,
## p20_q2_result.json, p20_lags_q2.jsonl, p20_q2_summary.txt; 282 min in one process)
Source: real activity, usable bars, volumes, funding times / intervals of the 134-symbol panel; prices and funding
rates overwritten by ONE synthetic draw (seed 15000: market factor +5e-5 / h, per-symbol drift, noise) before the
source arrays were shared; m (the null B mirror centre) recomputed from the synthetic returns. Churn 3.59 new
members per VAL month; null A pools: 62 pooled months, 8 on the whole period, smallest 110 days, median 365;
fallback 1.8% of symbol-days (worlds 17000-17002).
| cell | rho (achieved) | Sharpe at rho 0 | Tier-1 .025/.05/.10 | G6 | G1 | G2 | G3 | G4 | G5 | G7 | G10 |
| A fast | 0.048125 (1.497) | -0.69 | 17 / 19 / 19 | 19/23/24 | 20 | 22 | 24 | 19 | 24 | 23 | 24 |
| A slow | 0.088500 (1.500) | -0.52 | 14 / 17 / 19 | 14/17/20 | 20 | 22 | 24 | 22 | 24 | 23 | 24 |
| B fast | 0.048625 (1.500) | -0.73 | 17 / 20 / 20 | 19/23/23 | 21 | 22 | 23 | 21 | 24 | 23 | 24 |
| B slow | 0.073250 (1.500) | -0.17 | 14 / 15 / 17 | 16/19/21 | 23 | 23 | 20 | 23 | 24 | 20 | 24 |
Realized VAL Sharpe mean 1.50 in every cell (SD 0.61-0.68). Every p value with its VAL Sharpe: p20_q2_summary.txt.
Pooled lag bands (keep / masked A_k / S_k mean (SD) / beat), 30-89 | 90-179 | 180-364 | 365-547 days:
 A fast .805 1.31 -.75(.61) 0 | .691 1.24 -.71(.58) 6 | .633 1.21 -.66(.58) 19 | .567 1.17 -.60(.57) 29
 A slow .804 1.32 -.30(.61) 20 | .692 1.15 -.21(.68) 54 | .632 1.09 -.18(.56) 89 | .567 1.05 -.18(.58) 130
 B fast .805 1.38 -.72(.59) 6 | .693 1.31 -.68(.55) 7 | .633 1.21 -.67(.56) 14 | .567 1.13 -.60(.59) 25
 B slow .806 1.33 -.25(.54) 29 | .692 1.25 -.15(.55) 63 | .633 1.26 -.25(.60) 99 | .567 1.19 -.25(.55) 63
On the real calendar the mask keeps 0.81 / 0.69 / 0.63 / 0.57 and the masked actual stays at 1.05-1.38: the
pilot's null A slow collapse does not recur. Pre-registered reading: not every cell is >= 15 of 24 at all three
thresholds (A slow and B slow are 14 at 0.025) and no cell is <= 10 at 0.10 (minimum 17): MARGINAL. Odds for the owner:
the seal needs measured power >= 0.50 at the chosen threshold in all four cells (100 oracle worlds per null in the
real run); with 14 of 24 at 0.025 (posterior P(power < 0.5) about 0.2 per slow cell) the 0.025 outcome is close to a
coin flip for passing both slow cells; at 0.05 (17 and 15 of 24) the risk is about 0.1 per slow cell; at 0.10 small.
But see X10-F1: on this source the null A pass rate leaves no threshold at all.

## X10 verdict and finding
X10-F1 HIGH (design, ucalibrate.py USource._build_pools / UWorld null A, R-F of fix pass 5): null A's monthly pools give
each month's members a pool-specific mean return (cross-sectional SD about 0.6 a year, from the sampling noise of a
finite pool and from pool changes when membership changes) that decays with the lag (P21). A slow cross-sectional
momentum book holds it and its lagged copies hold less of it, so the paired lag test credits it as timing with no
timing skill: ucal_xs_momentum Tier-1 5 / 6 / 8 of 12 under null A (p 0.005 in 5 of 12) against 0 / 1 / 1 under null B;
the pooled null A pass rate 13.9 / 16.7 / 22.2% of submitted pairs exceeds NULL_PASS_MAX at every threshold, so the top30
rule STOPs. The pilot showed the same on the dry-run source (its only null A momentum pair passed at 0.10). Not a
false-pass risk (it makes the calibration stricter); it makes a useful seal unlikely. Real resampled prices should show
the same effect (real idiosyncratic vol 0.62 a year, pools about a year: pool-mean noise about 0.6 a year).
Smallest fix: in null A remove each symbol's pool-specific mean (add whole-period mean minus POOL(m) mean, per hour,
to the world's log returns; the shared source day, intraday path and funding unchanged). Reference arm P22: momentum
Tier-1 0 / 0 / 2 of 12 on the same seeds, p no longer skewed. Needs, before a re-key: a size re-check of the three
families under the fixed null A (as Q3) and the oracle cells under it (as Q2).
Verdict on fix pass 6 (4286abf) for the re-key: NOT READY. The oracle cells alone are marginal (above), but the null
A pass rate on the real-structure source leaves no qualifying threshold, so the calibration would STOP after its full
run. Fix X10-F1 first.
Not checked: anything on real price rows (forbidden); the fixed null A for the oracle and for carry / reversal; Q3 on
the dry-run source beyond the pilot's one world; the spawn-worker path (the in-process path reproduced the pilot's p
values exactly); the core unit; G8.

# X11 - fix pass 7 (commit ead27c6; copy review7\kernead, setupead.py: 143 blobs written and re-hashed equal, 0
# problems; delta x11\delta.diff; harness p23_x11.py with identical copies p23_s.py / p23_p.py)
Source for every measurement: the X10 real-structure source with the same synthetic draw (seed 15000). R-K's arrays
are derived from prices, so after the overwrite of the real ratios "dret" is recomputed from the SYNTHETIC ratios with
the kernel's own formula and USource._build_pools() is run again: no real-price quantity remains in the source (the
kernel's own build would otherwise have taken c_s and the pool means from the real VAL-period returns).

## Part A - R-L (calibrate.decide / null_summary, FAMILY_PASS_MAX = 0.06; p25_rl_probe.py, p25_out.txt)
Fabricated unit artifacts through ucalibrate.unit_verdict:
- momentum 14 of 200 at 0.10 (7%) with the two other families at 0: pooled 2.3% passes, the family bound fails at
  0.10 under both nulls and the unit chooses 0.05 (with the bound switched off: 0.10). 12 of 200 accepted, 13 refused.
- a family listed but never submitted, or listed without rows: skipped (it has no passes to hide).
- a row whose family is not in the artifact's families, or a text p value: STOP "artifact malformed" (FP6-1 path).
- NaN p values count as not passing (g6_paired_p cannot produce one; noted only).
- a NaN family rate in a HAND-MADE summary is ignored (not fail-closed) and numpy booleans in G3 are not counted as
  DEV-positive (0 of 600): both are the coordinator's 7b items; verdict_from_rows recomputes every rate from counts,
  so the seal path cannot meet a NaN rate today.
- seal path: decide_both -> unit_verdict -> verdict_from_rows -> calibrate.decide; kernel_lock.seal's refusal now
  carries family_pass_rate per unit. Old artifacts: the rule recomputes the family rates from the stored rows.
- texts: CONSTITUTION s8 / s13, the module docstrings and RULE / RULE_PER_UNIT say what decide does (pooled 3% AND
  every family <= 6% per its own submitted pairs, a family without a submitted pair skipped, failures named).
- the stated binomial reasoning checks out: accepted per null (<= 12 of 200) at a true family rate of 2.5% 0.998,
  4.5% 0.881, 5.0% 0.796, 9% 0.082, 10% 0.032; under both nulls 0.997 / 0.776 / 0.634 / 0.007 / 0.001.
Opinion on 0.06: sound as a cap on the dilution, but say plainly what it allows. In top30 only momentum passes the
other gates in null worlds, so its family rate at threshold t is G6's own false-pass rate at t: the bound makes the
unit choose 0.05 when momentum's p is close to uniform (0.10 is refused with probability 0.97 per null), so a no-skill
momentum-type top30 program keeps about a 5% chance of Tier-1, not the 3% the pooled bound was meant to give. A 3%
family bound (plus allowance) would force 0.025 in top30, where the slow oracle cells sit at 14 of 24. That is a
choice for the owner, not a defect; the texts should state the 5% consequence in one sentence.

## Part A - fix pass 7b (commit 58ba59e, parent ead27c6; x11\delta7b.diff), by reading
- decide: every bound is in the positive form (pooled: `not (r is not None and r <= bound)`; family: a None is still
  skipped, otherwise `not (fr <= bound)`; oracle level: `not (v is not None and |v - level| <= RHO_BOUND)`; power:
  `not (p is not None and p >= POWER_MIN)`), so None (pooled), NaN and inf fail; a text value raises TypeError at the
  comparison, which unit_verdict turns into the "malformed" STOP. _bound_failure only formats the message and never
  raises (math is imported). The DEV-positive count uses truthiness (numpy booleans count). oracle_advisory uses the
  same positive form. SOUND; it closes the two items of my P25 probe.
- My measurements on ead27c6 stand for 58ba59e: the text from `class USource` to `def world_udata` (USource, the pools,
  R-K, UWorld) has the same sha256 in both commits (fa8bb94858887def38fa1a649b8f62ea8485179e05e0a86bfd021293d4d6739a,
  20,256 characters); upipeline, universe, engine, pipeline, lang, interp and stats are unchanged (empty diff); the
  only ucalibrate hunk is oracle_advisory.
The two LOW items left open (my opinion):
1. tier_at (calibrate.py) skips a gate stored as None and reads the others by truthiness - LOW. It is wider than the
   builder's example: a gate KEY that is missing is not checked at all, so an oracle row with "gates": {} and a small
   p counts as Tier-1 (loose for power), and a null row likewise (strict for the null rate). gate_rates reads the same
   None as a FAIL, so the two disagree. Real rows always carry every gate key with a bool (only G6 / G8 are None).
   Smallest fix: tier_at requires every gate of GATES except G6 and G8 to be present and `is True` after JSON (or
   bool(v) for a numpy bool), and treats a missing key as a fail; artifact_gaps can name such rows.
2. unit_verdict does not catch AttributeError - LOW. More of the kind: any row that is not a dict (r.get on a number),
   "gates": null, "families" as a list. Nothing is sealed either way (the seal raises). Smallest fix: catch Exception
   in unit_verdict and return the "malformed" STOP with the exception's type and text.
I agree with the coordinator: both are outside what a real run writes and inside the seal's procedural trust (every
partial line has its sha256, the artifact's bytes must match the calibration log row, one pushed commit, an
independent recount); they can wait for one last small batch. Of the two, 1 is the one I would not leave out of that
batch, because in the loose direction it can only help a hand-edited artifact pass the power check.

## Part A - R-K (USource.build "dret", _build_pools "sym_c" / "pool_adj", UWorld._build; p24_rk_probe.py,
## p24_out_kern86.txt, p24_out_ead.txt)
My own enumeration from the source rows (hourly log(g * cr), my own full-day test, no kernel helper for R-K):
- c_s and adj(Q, s) equal the kernel's sym_c and pool_adj exactly (max difference 0; pool_adj 64 x 134 = 63 pools +
  the whole period).
- expected day log return of every symbol in every set Q under the fixed null A,
  P(shared) * (mean over Q's full days + adj) + P(fallback) * c_s, minus c_s: at most 3.5e-18 over 7,295 (set, symbol)
  pairs, members and non-members alike. Without R-K the same quantity had SD 0.98 a year (all symbols; members 0.63, P21).
- edge cases on this source: 2 symbols with full days before UNIVERSE_START (in c_s, as in their fallback; the shared
  draws start at pool_lo, as adj does); 0 symbols without a full day (such a symbol keeps its own days, c_s = 0, no
  adjustment - by reading); 9 (set, symbol) pairs with only 1-5 full days, |adj| up to 0.061 per day (exact in
  expectation, but a 6% daily shift on the rare shared day of a symbol that is mostly not a member); partial world days
  (1-23 active hours) 272 of 172,851 symbol-days (0.16%) get h/24 of adj; the first row of a symbol loses its 1/24
  (the kernel resets G[0] to 1 after the adjustment; 14 of 23 checked symbols start on a shared day) - NOTE only.
- draws unchanged: for seed 11000 the null A source day of every symbol-day equals the kern86 copy's (0 of 134 symbols
  differ); for seed 14000 the null B klines, funding and mark tables are byte-identical (0 of 134 differ).
- null A tables vs kern86 (23 symbols, 647,242 shared active rows): high/open, low/open, close/open equal (max
  difference 6.7e-16); the gap ratio changes by exactly exp(my adj / 24) on shared active rows and not elsewhere
  (max relative deviation 2.2e-16).
- spawn path: a one-worker spawn Pool with the kernel's _init on a 40-symbol dry-run source (pool_adj 55 x 40) gives
  the same curve task result as the in-process path, bit for bit ([1.33220, 2.20461]).
- the null B reproductions (repro mode): Q3 null B world 14000 (task_null) and Q2 null B world 18000
  (task_oracle_power) are identical to X10 on ead27c6, so the X10 null B cells and Q3 null B rows stand.
What R-K does not remove (members, pooled months, synthetic iid prices):
- pool-specific volatility: SD of log(pool vol / whole-period vol) 0.028 across members, correlated between month m
  and m-k 0.79 / 0.51 / 0.26 / 0.07 by lag band - the same decay as the old drift, but on this source only sampling
  noise of 3%. On real prices the pools are different stretches of history with different volatility regimes, so the
  spread will be larger; a book that scales positions by recent volatility would then hold a risk-timing edge that its
  lagged copies hold less of. The three calibration families do not scale by volatility. I cannot show the size of
  this on synthetic prices - NOTE.
- pool-specific cross-correlation: mean member correlation over pool days 0.32-0.41 (synthetic: sampling and
  membership mix); no lag-decaying expected-return channel for a market-neutral book that I can see.
- hour-of-day means: R-K spreads the correction evenly, so a pool's hour profile (here noise of about 0.008 /
  sqrt(386) = 0.0004 per hour) stays; trading it needs hourly rebalancing, which at 12.5 bps per side fails G4 (the
  1-day oracle already does) - not a Tier-1 channel.
- the months around a symbol's entry: their pools start after the entrant's listing; R-K now fixes the mean; volatility
  and correlation of that stretch remain as above.

## Part B - measurements on ead27c6 (= 58ba59e for the world builders), 200 lags, the kernel's task functions in one
## process; p23_size_summary.txt, p23_power_summary.txt, p23_pilot_summary.txt, p26_out.txt, p27_out.txt
S - size, all three families (null A seeds 11000-11023, p23_sizeA; null B: Q3 rows 14000-14011, reproduced exactly on
ead27c6, plus 14012-14023, p23_sizeB). Every pair submitted.
| null | family | Tier-1 .025 / .05 / .10 | DEV-positive |
| A | ucal_xs_momentum | 2 / 3 / 5 of 24 | 23 |
| A | ucal_xs_reversal | 0 / 0 / 0 | 0 |
| A | ucal_xs_carry    | 0 / 0 / 0 | 1 |
| B | ucal_xs_momentum | 0 / 1 / 2 of 24 | 24 |
| B | ucal_xs_reversal | 0 / 0 / 0 | 0 |
| B | ucal_xs_carry    | 0 / 0 / 0 | 1 |
Pooled (of 72 submitted): null A 2.8 / 4.2 / 6.9%, null B 0 / 1.4 / 2.8%. Family rate, momentum: null A 8.3 / 12.5 /
20.8%, null B 0 / 4.2 / 8.3%. Over DEV-positive pairs: null A 8.3 / 12.5 / 20.8%, null B 0 / 4.0 / 8.0%.
Null A momentum rows (seed n DEV VAL p, failed gates): 11000 54 -0.15 1.67 0.527 G3; 11001 55 1.12 3.63 0.478;
11002 44 1.57 1.95 0.229; 11003 49 1.27 1.15 0.940; 11004 56 1.51 1.95 0.567; 11005 51 0.94 1.42 0.910; 11006 51 0.27
1.73 0.796; 11007 46 1.55 2.62 0.0746; 11008 40 0.94 1.66 0.0746; 11009 50 1.33 2.09 0.731; 11010 39 1.75 2.43 0.189;
11011 57 3.01 1.91 0.667; 11012 47 1.07 2.14 0.692; 11013 34 1.52 1.20 0.881; 11014 49 0.81 1.39 0.627; 11015 30 1.12
1.86 0.110; 11016 45 0.78 1.30 0.950 G7; 11017 40 1.23 2.52 0.0199; 11018 56 1.44 1.97 0.891; 11019 44 0.81 2.08
0.0199; 11020 58 1.43 2.31 0.234; 11021 37 0.91 3.39 0.0348; 11022 59 1.08 1.83 0.637; 11023 58 1.17 1.81 0.493.
Null B momentum rows: in p23_size_summary.txt (p 0.0299 and 0.0846 are the only p <= 0.10; 14002 and 14016 fail G1).
11000-11011, momentum p (VAL Sharpe), Q3 on 4286abf | P22 | X11 on ead27c6: 11000 0.070 (2.63) | 0.527 (1.68) | 0.527
(1.67); 11001 0.005 (4.16) | 0.458 (3.66) | 0.478 (3.63); 11002 0.005 (3.01) | 0.234 | 0.229; 11003 0.149 | 0.940 |
0.940; 11004 0.085 | 0.572 | 0.567; 11005 0.453 | 0.910 | 0.910; 11006 0.149 | 0.796 | 0.796; 11007 0.005 | 0.080 |
0.075; 11008 0.030 | 0.075 | 0.075; 11009 0.174 | 0.721 | 0.731; 11010 0.005 | 0.189 | 0.189; 11011 0.005 | 0.667 |
0.667. R-K removes the X10 skew the way P22 did (Tier-1 at 0.10 on these 12 seeds: 8 -> 2).
Extension (not ordered; momentum only, same draws per family; p23_extA): null A 11024-11047 Tier-1 2 / 3 / 4 of 24
(p 0.0149 x2, 0.0448, 0.0896). Null A momentum over 48 worlds: 4 / 6 / 9 (8.3 / 12.5 / 18.8%); p U-shaped (9 of 48 at
<= 0.10, 7 of 48 at >= 0.90). Null B over 24: p concentrated (median 0.48; 2 of 24 at <= 0.10, 2 at >= 0.90).
Dry-run source (UC.synthetic_source(), momentum only, null A 11000-11011, p23_pilotA): 0 / 0 / 0 of 12 (5 fail G1).
P - power, null A cells under the fixed null A (seeds 17000-17023, the calibration's tune_rho and power tasks; null B
cells: Q2 world 18000 reproduced exactly on ead27c6, so X10's B cells stand):
| cell | rho (achieved) | Sharpe at rho 0 | Tier-1 .025/.05/.10 | G6 | G1 | G2 | G3 | G4 | G5 | G7 | G10 |
| A fast (X11) | 0.049125 (1.502) | -0.72 | 17 / 19 / 19 | 19/23/24 | 20 | 23 | 24 | 19 | 24 | 23 | 24 |
| A slow (X11) | 0.089125 (1.499) | -0.49 | 12 / 15 / 18 | 12/16/20 | 20 | 22 | 24 | 22 | 24 | 23 | 24 |
| B fast (X10) | 0.048625 (1.500) | -0.73 | 17 / 20 / 20 | 19/23/23 | 21 | 22 | 23 | 21 | 24 | 23 | 24 |
| B slow (X10) | 0.073250 (1.500) | -0.17 | 14 / 15 / 17 | 16/19/21 | 23 | 23 | 20 | 23 | 24 | 20 | 24 |
Lag bands, A slow (keep / A_k / S_k mean (SD) / beat): 30-89 d .804 1.28 -.36 (.60) 22 | 90-179 d .692 1.10 -.19 (.65) 66
| 180-364 d .632 1.05 -.18 (.56) 107 | 365-547 d .567 1.03 -.18 (.57) 133; A fast: .805 1.32 -.75 0 | .691 1.23 -.71 6 |
.633 1.20 -.66 21 | .567 1.15 -.61 33.

## Reading (the rule fixed in AUDIT_LOG, applied as written)
Size: momentum 2 of 24 at 0.025 (trigger 3) and 3 of 24 at 0.05 (trigger 4) under null A, 0 and 1 under null B: NOT
triggered. No reversal or carry pass. Power: A slow 12 and B slow 14 of 24 at 0.025 (< 15), no cell <= 10 at 0.10
(lowest 17): MARGINAL -> the owner, with the odds.

## X11-F1 HIGH (process; no false-pass risk): a momentum skew remains under the fixed null A, enough for the 6% family
## bound to stop the real calibration most of the time
Over 48 null A worlds momentum passes Tier-1 in 4 / 6 / 9 (8.3 / 12.5 / 18.8%) against the 2.5 / 5 / 10% a valid test
gives (4 or more of 48 at 2.5% has probability 0.035); under null B 0 / 1 / 2 of 24. The size trigger of the reading
(3 of 24 = 12.5%) is looser than the seal's own family bound (6% of about 200 pairs): a rate of 8% passes the reading
(about 2 of 24) but is accepted by the seal in only about 18% of runs per null. Mechanism, suggestive (P27, 6 worlds per
null): null A draws its days WITH replacement from a monthly pool of about a year, so a source day in a 50-day signal's
window recurs in the holding period with probability about 50 / |Q|; lagged signals drawn from other pools' stretches
share fewer such days. The 50-day momentum signal's cross-sectional IC with the next day's return falls from 0.025
(lags 0 and 60 days) to 0.020 (180 and 365 days) under null A and stays flat under null B (0.021 / 0.022 / 0.021 /
0.019); the constant drift gives the same IC at every lag. R-K equalises the expected return, not realised returns that
repeat. Smallest fix: draw null A source days WITHOUT replacement within a pool (one random permutation of POOL(m) per
world, consumed in order by the months that use that pool, renewed when exhausted), so that no source day recurs within
|Q| days; then re-run the size measurement (momentum, at least 48 null A worlds) and the two null A power cells.
Alternative: re-key now and let the rule decide, at the odds below.

## Seal odds (p26_odds.py, p26_out.txt)
Model: in top30 only momentum can pass in null worlds, so the binding bound is momentum <= 12 of ~200 per null; its
null A / null B Tier-1 bins from my 48 / 24 rows (Dirichlet, Jeffreys) drive a multinomial 200-world run; the unit
takes the largest threshold that passes under both nulls; each power cell's true power ~ Beta from its 24 worlds,
measured on 100 worlds, needing >= 0.50 in all four cells; the core unit seals with probability 0.95 (assumption from
the sealed core's margins: pooled 2.94% at 0.10, worst family 4.67%, power at 0.05 81-90.5%), independently.
Result: top30 threshold - none 0.72, 0.025 0.25, 0.05 0.03, 0.10 0.00; power passes all four cells given 0.025 in
0.28, given 0.05 in 0.74; P(top30 seals) 0.09; P(seal) about 0.09. If momentum's null rate were exactly the level (a
valid test), the same model gives 0.025 0.41 / 0.05 0.58 and P(top30 seals) 0.56. My estimate: about 0.1 (range 0.05
to 0.25 for other priors and for real prices behaving differently), most likely outcome a STOP naming "family
ucal_xs_momentum > FAMILY_PASS_MAX" under null A at every threshold; if a threshold qualifies, most likely 0.025.

## Verdict for the re-key at 58ba59e (ead27c6 + 7b): NOT READY in my judgment
The code is sound: R-K is exact per branch, the draws and null B are unchanged, the spawn path works, R-L and 7b do what
their texts say (two LOW items left open, see above). By the reading rule the measurement is MARGINAL (size not
triggered; power MARGINAL), so it goes to the owner with the odds; my own estimate of a successful seal is about 1 in
10, most likely ending in a STOP on the momentum family bound after the full run. I would fix X11-F1 first.
Not checked: anything on real price rows (forbidden; real prices may change both the skew and the power); the core
unit's re-run; G8; the full multiprocessing calibration (only a one-worker spawn task); the without-replacement fix
(proposed, not tested); X11-F1's mechanism beyond the 6-world IC check.
