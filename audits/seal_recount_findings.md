# Independent recount of the KP-015 seal (core 0.10, top30 0.10)

Auditor: independent subagent, read-only. Date 2026-11-23.
Inputs (sha256 of the bytes on disk):
- ledger/calibration_5ea66b0fb79ca267.json   a1ee5cfb86dda2b8b538cb7d685d0614ea3bfa516e84993620ccd7822b5ec0a5 (5517336 bytes)
- ledger/ucalibration_5ea66b0fb79ca267.json  24896cd3f99d84250668e93f5c043f3eb6153042c683b29bc415972c03cbcd61 (1938335 bytes)

## Verdict: AGREE

From the stored rows alone, with my own code written from CONSTITUTION.md section 8 (and 13), the rule chooses
core 0.10 and top30 0.10, with oracle power at true Sharpe 1.5 >= 50% in every cell and every oracle level within
0.1. Every stored summary, both stored verdicts, the seal block in kernel.lock, the calibration_log rows and the
last kernel_history row agree with my numbers (1053 field comparisons, 0 differences). No blocker found.
The core margin is thin: under core null A at 0.10 there is no spare pass (44/1498 = 2.937%; 45 would be 3.004%).

## How the recount was done

The rule as I read it from the text (section 8, lines 285-322; section 13, lines 598-607):
- per unit and null: designed pairs = worlds ordered x families (core 300 x 5, top30 200 x 3); a row's status
  "not_submitted" = never submitted; submitted rows end evaluated, liquidated, or fault (anything else);
- Tier 1 at threshold t = evaluated AND G1, G2, G3, G4, G5, G7, G10 all true AND perm_p <= t (G8 not run);
- pooled rate = Tier-1 / evaluated (<= 3%), family rate = family Tier-1 / family evaluated (<= 6%; no evaluated
  pair fails); evidence floors: every family evaluated/designed >= 50%, the null >= 75%; faults/submitted <= 3%;
  a null that misses a floor or the fault bound fails every threshold; rows must be exactly the design;
- chosen = the largest of 0.025/0.05/0.10 passing under both nulls; then power (Tier-1 / oracle worlds) at that
  threshold >= 50% at level 1.5 for both speeds under both nulls, every level's mean VAL Sharpe within 0.1 of
  nominal; otherwise nothing is sealed (no fall-back to a lower threshold).
All comparisons in exact fractions (p as k/201 or k/21; rates as integer ratios). Gate booleans were also
re-derived from gate_values by the section-7 rules (G1 psr >= 0.90, G2/G3/G4 > 0, G5 median >= 0.5 x base and
>= 75% positive, G7 >= 4 positive and largest share <= 0.5, G10 >= 12): 0 mismatches in every row.

## Recount tables

### Core (designed 300 per family per null)

Null A                     submitted evaluated liquidated fault not_sub DEV+   T1@0.025 T1@0.05 T1@0.10
gen000_donchian_ls             300      300        0        0      0     266       1        9      14
gen000_funding_carry           299      299        0        0      1     186       2        4       5
gen000_rsi_meanrev_ls          300      300        0        0      0     177       5        5       6
gen000_sma_cross_ls            299      299        0        0      1     264       1        1       6
gen000_voltarget_trend_ls      300      300        0        0      0     251       1        7      13
TOTAL                         1498     1498        0        0      2    1144      10       26      44
pooled rate: 10/1498 = 0.0067, 26/1498 = 0.0174, 44/1498 = 0.0294 (bound 0.03)
largest family rate: 0.025 rsi 5/300 = 0.0167; 0.05 donchian 9/300 = 0.0300; 0.10 donchian 14/300 = 0.0467
floors: pooled 1498/1500 = 0.9987; families 1.0, 0.9967, 1.0, 0.9967, 1.0; faults 0/1498

Null B                     submitted evaluated liquidated fault not_sub DEV+   T1@0.025 T1@0.05 T1@0.10
gen000_donchian_ls             300      300        0        0      0     256       2        7      11
gen000_funding_carry           300      300        0        0      0     229       0        1       3
gen000_rsi_meanrev_ls          300      300        0        0      0     145       1        2       2
gen000_sma_cross_ls            300      300        0        0      0     255       0        1       7
gen000_voltarget_trend_ls      300      300        0        0      0     245       3        7      12
TOTAL                         1500     1500        0        0      0    1130       6       18      35
pooled rate: 6/1500 = 0.0040, 18/1500 = 0.0120, 35/1500 = 0.0233
largest family rate: 0.025 voltarget 3/300 = 0.010; 0.05 donchian and voltarget 7/300 = 0.0233; 0.10 voltarget 12/300 = 0.040
floors: all 1.0; faults 0/1500

Core oracle (200 worlds per cell; one rho per cell)
cell             rho        mean VAL Sharpe  T1@0.025 T1@0.05 T1@0.10   G6 pass @0.025/0.05/0.10
A fast  1.0   0.075125        1.001431         114      114     114        149/167/183
A fast  1.5   0.101625        1.498377         168      168     168        192/197/198
A slow  1.0   0.246           1.001227          83      101     113         98/119/144
A slow  1.5   0.361           1.504056         150      166     171        160/180/190
B fast  1.0   0.102625        1.000502         126      126     126        170/182/190
B fast  1.5   0.133375        1.501528         181      181     181        193/196/197
B slow  1.0   0.29            0.999869          78      100     109         90/116/141
B slow  1.5   0.4305          1.500310         152      162     171        155/168/186
Rule: qualifying 0.025, 0.05, 0.10 (no failure under either null) -> 0.10; power at 1.5 and 0.10:
A fast 168/200 = 0.840, A slow 171/200 = 0.855, B fast 181/200 = 0.905, B slow 171/200 = 0.855; all levels within
0.1 -> CORE 0.10.

### top30 (designed 200 per family per null)

Null A                     submitted evaluated liquidated fault not_sub DEV+   T1@0.025 T1@0.05 T1@0.10
ucal_xs_carry                  149      149        0        0     51      14       0        0       0
ucal_xs_momentum               200      199        1        0      0      92       0        0       0
ucal_xs_reversal               200      199        1        0      0      59       0        0       0
TOTAL                          549      547        2        0     51     165       0        0       0
floors: pooled 547/600 = 0.9117; families 0.745, 0.995, 0.995; faults 0/549

Null B                     submitted evaluated liquidated fault not_sub DEV+   T1@0.025 T1@0.05 T1@0.10
ucal_xs_carry                  166      166        0        0     34      44       0        0       0
ucal_xs_momentum               200      200        0        0      0     111       0        0       0
ucal_xs_reversal               176      176        0        0     24      70       0        0       1
TOTAL                          542      542        0        0     58     225       0        0       1
pooled rate at 0.10: 1/542 = 0.00185; reversal family 1/176 = 0.00568; all other rates 0
floors: pooled 542/600 = 0.9033; families 0.83, 1.00, 0.88; faults 0/542
(The one Tier-1 row is ucal_xs_reversal under null B with p = 2/21 = 0.0952: it is the only top30 null row that
passes every gate but G6, in either null.)

top30 oracle (100 worlds per cell, level 1.5 only; one rho per cell)
cell        rho        mean VAL Sharpe  T1@0.025 T1@0.05 T1@0.10   G6 pass @0.025/0.05/0.10
A fast   0.061375        1.501914          0       69      82          0/73/90
A slow   0.098           1.500270          0       62      74          0/66/80
B fast   0.071125        1.499682          0       66      70          0/87/92
B slow   0.107125        1.499091          0       48      68          0/54/79
Rule: qualifying 0.025, 0.05, 0.10 -> 0.10; power at 0.10: A fast 0.82, A slow 0.74, B fast 0.70, B slow 0.68;
levels within 0.1 -> TOP30 0.10. (At 0.05 B slow would be 48/100 < 0.5, and 0.025 is unreachable because p >= 1/21.)

## Comparisons (item 3, 4, 5)

- Stored null summaries (n_pairs, n_submitted, n_evaluated, n_not_submitted, liquidated, fault, designed,
  n_dev_positive, per_family, submitted_status, stage1_draws, and per threshold tier1, pass_rate,
  pass_rate_submitted, pass_rate_all_pairs, pass_rate_dev_positive, family_pass_rate, passer_families, the passers
  list with params/perm_p/val_sharpe, gate_pass_rate_submitted), stored oracle summaries (n, not_evaluated, mean,
  power, tier1, gate_pass_rate; rhos and tuning rho equal the rows' rho; tuning achieved = rows' mean within 1e-9),
  and both stored verdicts (every key): all equal to my recount. 0 differences.
- kernel.lock seal: g6_threshold {core 0.1, top30 0.1}; calibration_file / universe_calibration_file name the two
  artifacts; both sha256 equal the bytes on disk; semantic_hash = lock semantic 5ea66b0f...2687; null_pass_rate and
  power_at_1_5 equal my numbers exactly.
- calibration_log.jsonl: 4 rows, chain intact (my own check and the kernel's), HEAD anchor 4 rows / cb8988c3...
  matches. Exactly one row per artifact; its sha256 = the bytes on disk; its semantic_hash and research_hash = the
  artifact's.
- kernel_history.jsonl: 10 rows, chain intact, HEAD anchor matches. Last row: event seal, approved_by
  "omr.kernel_lock seal", all six SEAL_KEYS equal the lock's seal, new_semantic/new_text/new_combined = the lock,
  at = sealed_at 2026-11-23T09:56:08Z. Row -2: the re-key to semantic 5ea66b0f..., seal_kept false.
- python -m omr.kernel_lock verify: "KERNEL LOCK: OK ... sealed G6 core 0.1 top30 0.1" (exit 0).
  python -m omr.ledger verify: all six chains OK, "ledger verify: OK" (exit 0). Run with -B; no __pycache__ appeared.
- Acceptability (item 4): both artifacts have semantic_hash = lock semantic, text_hash = lock text, kernel_hash =
  lock combined, research_hash 28d9084a...9410 = data/manifest.json research_hash, synthetic_dry_run false,
  kernel_lock_verified true; sizes core 300/200, top30 200/100 (protocol and run_header); family program hashes =
  kernel.lock files (5 core, 3 top30). Core "protocol" equals calibrate.protocol_header(300, 200) key by key;
  top30 "run_header" equals ucalibrate.run_header(lock, manifest hash, FAMILIES, 200, 100, False) key by key,
  ALL 17 keys including the hashes and families (the seal itself skips those three). The top30 "protocol" block
  agrees with run_header on seeds, levels, speeds, draws, g6_lags, g6_memory_max and sizes. Cross-check after the
  recount: the kernel's own check_artifact / check_universe_artifact return no reason, design_problems is empty
  for both, decide_both gives {core 0.1, top30 0.1}, its per-unit verdicts equal the stored verdicts and its
  null_pass_rate, power and rule text equal the seal block.
- Byte form: both artifacts are ASCII, have no duplicate JSON keys, and are byte-identical to
  json.dumps(parsed, indent=1, sort_keys=True) with CRLF line ends (Path.write_text on Windows); .gitattributes is
  "* -text", so git stores the bytes unchanged.
- Commit: aaa0c7b "KP-015 sealed" holds both artifacts, calibration_log, kernel_history and kernel.lock in one
  commit; working tree clean; local kp015-build equals origin/kp015-build as last fetched (no network to confirm).
- Item 5, core vs the previous sealed artifact calibration_7446278556aadd8f.json: all 4600 rows (2 x 1500 null,
  2 x 800 oracle) match by key and are identical in EVERY field (0 rows differ, no row only in one file).
  Differences are only outside the rows: created_at, wall_seconds, kernel_hash, semantic_hash, text_hash,
  research_hash (cf26f534... -> 28d9084a...), protocol_version 3 -> 6, the protocol header gained opts,
  protocol_version and rho_grid; summaries gained 31 keys per null (no value changed); the verdict gained 63 keys
  and changed only "denominator" (submitted -> evaluated pairs) and the rule text. Oracle rhos, tuning and
  summaries identical. The core rows being bit-identical under a new research hash is consistent with the claim
  that the core is unchanged by KP-015.

## Differences found between text, code, stored summaries, log and seal

Stored summaries / verdicts / calibration log / seal block vs my recount: none.
Text vs code (none changes the outcome here):
1. Tolerances the text does not have: pooled and family rates "<= max + 1e-12" (omr/calibrate.py 660, 663),
   fault share "<= 0.03 + 1e-12" (calibrate.py 541), floors ">= floor - 1e-12" (calibrate.py 552), G6
   "p <= t + 1e-12" (omr/pipeline.py 531 tier_at, 438; omr/upipeline.py 1022). Immaterial: the nearest p values
   to the grid are 5/201, 10/201, 20/201, 1/21, 2/21 (>= 1.2e-4 away) and no rate is within 1e-12 of a bound.
2. Oracle level check: the code's mean VAL Sharpe is over evaluated rows with a finite Sharpe only, while power is
   over all rows of the cell (calibrate.py 495-499, ucalibrate.py 1074-1078); the text says "mean over those
   worlds". A liquidated oracle book would be dropped from the level check. Not triggered (all 1600 core and 400
   top30 oracle rows evaluated).
3. Stale docstring: calibrate.py line 50 says the family rate is "per its own submitted pairs"; the text and the
   code (calibrate.py 478) use evaluated pairs.
4. A stage-1 failure of the chosen draw is stored as submitted=false, status "stage1_<code>" (calibrate.py
   396-398, ucalibrate.py 849-851): it counts as not submitted and can never enter the 3% fault bound (c), only the
   floors. Section 6 calls a stage-1 truncation mismatch a kernel fault. Not triggered (no stage1_* rows).
5. tier_at checks perm_p in [0, 1] but not that it is on the k/201 or k/21 lattice (pipeline.py 527-531). My
   recount checked: every evaluated row's p is on its lattice.
6. "Not on the stored data" is checked against data/manifest.json's research_hash (kernel_lock.py 415), not by
   recomputing the hash from the data files (the evaluator does that). I did the same; not recomputed.
7. For top30 the seal compares run_header key by key (kernel_lock.py 369-373); the artifact's "protocol" block is
   only checked for sizes (kernel_lock.py 337-345) and seeds (calibrate.py 622). Consistent with the task's reading
   of (e); noted because the protocol block carries data-derived meta that nothing compares.

## Findings by severity

Blockers: none.

Should fix:
S1. top30 G6 is far from its nominal level for the carry family under null B (item 8 below): 53/166 rows have
    p <= 0.10 (nominal 2/21 -> expected 15.8; binomial P(X >= 53) = 1e-15) and 31/166 have p = 1/21 (expected 7.9;
    P = 7e-11); the whole p distribution is shifted (median k about 4 of 21; only 7 rows at k >= 15 against 55
    expected). It does not move the seal (no carry row passes G1, G2, G4, G5 or G7 in either null), but it shows the
    paired lag test is anti-conservative for at least one no-skill book type, and the calibration cannot measure
    the conditional rate for a carry-like book that passes the other gates. CONSTITUTION.md 527-529 (limit (2):
    "such books fail G1-G4 anyway") understates the size and does not state the direction. omr/upipeline.py
    1012-1020 (paired loop), 933-941 (g6_paired_p). Suggest an audit measurement with keep_detail on a few null B
    carry worlds (per-lag Sharpes, the two books' volatility and costs) before relying on top30 G6 for carry-like
    programs; a paired statistic on the difference series (A_k - S_k) would not reward a variance difference.

Notes:
N1. Core margin: under null A at 0.10 the seal holds with zero spare passes (44/1498 = 2.937%; 45/1498 = 3.004%).
    Two rows passing every other gate have p = 21/201 = 0.1045, correctly excluded; nothing sits exactly at 20/201.
N2. Under the open KP-016 denominator the core would get 0.05, not 0.10 (item 6).
N3. Items 1-7 of the text-vs-code list above.
N4. The G5 jitter median is stored as the string "-inf" in 17 top30 rows (null A 1, null B 16) (ledger.clean); the
    rule reads booleans only, but any numeric reader must convert it.
N5. The top30 calibration ran in two processes (VAL access handles 2026-11-22T17:05:34Z and 17:34:54Z; the
    artifact's wall_seconds covers the second only). The resume design says the artifact is the same; not verified.
    The core ran once (handle 2026-11-23T05:23:48Z). No other calibration handle since the re-key.
N6. The re-key itself was approved by delegation (kernel.lock approved_by); its validity was not assessed here.

## Item 6 (information, KP-016): Tier-1 over evaluated DEV-positive pairs (G3 true)

Core          null A (1144 DEV+)                         null B (1130 DEV+)
t=0.025   10/1144 = 0.0087                            6/1130 = 0.0053
t=0.05    26/1144 = 0.0227                           18/1130 = 0.0159
t=0.10    44/1144 = 0.0385  (> 0.03)                 35/1130 = 0.0310  (> 0.03)
per family (passes / DEV+), A at 0.025/0.05/0.10: donchian 1,9,14 /266; carry 2,4,5 /186; rsi 5,5,6 /177;
  sma 1,1,6 /264; voltarget 1,7,13 /251.
per family, B at 0.025/0.05/0.10: donchian 2,7,11 /256; carry 0,1,3 /229; rsi 1,2,2 /145; sma 0,1,7 /255;
  voltarget 3,7,12 /245.
Variant (i) family bound over evaluated pairs: qualifying 0.025, 0.05 -> 0.05.
Variant (ii) family bound over DEV-positive pairs: largest family rate at 0.05 is donchian A 9/266 = 0.034 -> 0.05.
Core power at 0.05: A fast 168/200 = 0.840, A slow 166/200 = 0.830, B fast 181/200 = 0.905, B slow 162/200 = 0.810.

top30         null A (165 DEV+: carry 14, momentum 92, reversal 59)   null B (225 DEV+: carry 44, momentum 111, reversal 70)
t=0.025   0/165                                                    0/225
t=0.05    0/165                                                    0/225
t=0.10    0/165                                                    1/225 = 0.0044 (reversal 1/70 = 0.014)
Both variants: qualifying 0.025, 0.05, 0.10 -> 0.10; power as sealed (0.82, 0.74, 0.70, 0.68).
(The rates over DEV-positive pairs equal the artifacts' stored pass_rate_dev_positive.)

## Item 7 (attack): what was checked, all clean

Exactly one null row per (seed, family) and one oracle row per (seed, speed, level) over the module seeds (core
1000/4000/7000/8000, top30 11000/14000/17000/18000), no missing, double or foreign row, every row's null field its
own; statuses only evaluated / liquidated / not_submitted, submitted flag consistent with status; every Tier gate a
Python bool, G6 and G8 None; gate booleans follow from gate_values; gate_values.G6 = perm_p, G3 = dev_sharpe,
G1 = psr0, G10 = direction_changes_val; every perm_p on its lattice (k/201, k/21) and in range; no p at a grid
boundary; val/dev Sharpe and psr finite in every evaluated row; params inside the declared ranges of the hash-locked
programs (names and integer types too); stage-1 codes sum to 20 screened draws, a not-submitted row has no
candidate and a submitted row at least one; top30: every row's g6_lag_step 621 (= (13152 - 720) // 20), the
over-limit flag agrees with g6_memory > 0.5 in every row (one null row over the limit: momentum, null B, seed
14166, memory 0.5285, perm_p 1.0; no oracle row over, max oracle memory 0.097), oracle rows G5 vacuous with
G5 value None, one rho per oracle cell; every stored summary follows from the rows.

## Item 8: ucal_xs_carry under top30 null B passes G6 alone far above the nominal level

Measured (stored rows only):
- p histogram (k in p = k/21) of the 166 evaluated carry rows, null B: k=1: 31, 2: 22, 3: 14, 4: 20, 5: 10, 6: 12,
  7: 12, 8: 11, 9: 7, 10: 10, 11: 2, 12: 4, 13: 3, 14: 1, 15: 3, 16: 1, 18: 2, 19: 1. Exchangeable books would give
  about 7.9 per bin. The shift is of the whole distribution, not a tail of special rows.
- Null A carry (149 rows) is the opposite: fewer extremes than nominal (k <= 2: 6, expected 14.2, P(X <= 6) = 0.01;
  k >= 19: 3, expected 21.3), a hump in the middle. Momentum and reversal are near nominal in both nulls (p <= 0.10:
  null A 10/199 and 11/199; null B 12/200 and 17/176, of which 16 G6-alone).
- No carry row passes G1, G2, G4, G5 or G7 under either null; all 166 null B carry VAL Sharpes are negative
  (median -1.6 for p <= 0.10, -2.0 otherwise). The book is cost-dominated: VAL Sharpe minus the 2x-cost Sharpe
  (one extra unit of costs) is about 1.77 Sharpe units in both groups; momentum 0.43-0.79, reversal 0.63-0.85.
  Funding flows are large too: VAL Sharpe minus the funding-stress Sharpe is about 0.49.
- The low-p carry rows are NOT distinguished by n (medians 23 vs 26; the excess is present in every n bucket),
  g6_memory (0.029 vs 0.034, all far below 0.5, none over the limit), g6_lag_step (621 in all), rebalances
  (9227 vs 9151), direction changes (VAL 24217 vs 22915, DEV 11610 vs 11090), cost drag or funding drag. They have
  a less negative VAL Sharpe and psr (the generic "luck not shared by stale copies" correlation, seen in every
  family), and the excess is present among DEV-positive (11/44) and DEV-negative (42/122) rows alike.
- The carry book's direction-change rate grows over time: about 12.7 per day in DEV and 22.1 per day in VAL (null B
  medians), so the lagged copies (weights 26 to 548 days older) carry, if anything, LESS turnover than the actual.
- From the code (read, not run): null B keeps every symbol's real funding rates in their real order, each times a
  fair coin per settlement hour shared by the symbols settling then (ucalibrate.py 465-467, 604-630); null A takes
  the rates of a random source day per world day (ucalibrate.py 611-627). top30 G6 compares, for each of 20 lags,
  the actual book A_k and the stale book S_k, both restricted to the names common to the row and re-centred, each
  run through the engine with its own costs (upipeline.py 897-925, 1012-1020); p = (1 + #(Sharpe(S_k) >=
  Sharpe(A_k) - 1e-9 or tie)) / 21. Each lag has its OWN paired actual A_k, so the 20 comparisons are not ranks
  among 21 exchangeable books.

Conjecture (most plausible; not tested, no evaluation was run):
(a) Cause. A systematic per-pair advantage of the actual carry book over its stale copies that comes from costs,
    not timing: the documented limit (2) (each book pays its own costs; CONSTITUTION.md 527-529) with a direction.
    Both books have zero expected gross P&L (signs are coins) and similar costs, so Sharpe is about
    -cost / volatility, and the book with the LARGER volatility has the less negative Sharpe. The actual carry book
    is built from the last 3-30 settlements, so it is aligned with the current cross-section of funding
    magnitudes, which in null B keep their real persistence; a copy 26-548 days stale is aligned with an older,
    partly decorrelated cross-section, so its funding-flow variance on the common names is smaller. With a cost
    drag near 1.8 Sharpe units, a modest volatility ratio moves Sharpe by several tenths, and because this
    advantage is common to all 20 pairs it shifts the whole count toward 0. Null A destroys the persistence of the
    funding cross-section (random source days), which is consistent with no excess there (the hump in null A is
    what partly independent pairwise comparisons give when no common advantage exists); momentum and reversal have
    a cost drag 2-4 times smaller, consistent with no visible effect. Alternatives I cannot exclude from the rows:
    (i) a masking asymmetry (A_k drops recent entrants, which in null B keep their real, often extreme funding;
    S_k drops names that have since left; both are re-centred, adding turnover that differs between the books);
    (ii) a timing leak of the funding coin into the actual book, which I judge unlikely: a leak would make the
    actual carry book earn funding (all 166 VAL Sharpes are negative) and would put almost every row at p = 1/21,
    not 31 of 166. What would decide it: per-lag Sharpes, volatilities and costs of A_k and S_k (keep_detail) on a
    few null B carry worlds, and the same worlds with costs at zero.
(b) Books that pass every other gate. If (a) is right, yes, it can raise G6's pass rate above nominal for such a
    book: the advantage is cost x (1/vol_stale - 1/vol_actual) in Sharpe units and exists whenever the actual
    weights are better aligned than their stale copies with a P&L source whose magnitude is persistent but whose
    sign is not predictable (funding in any carry book; volatility for books loading on recent movers). It shrinks
    with the cost drag, so it is smaller for a book that passes G4 (2x costs) than for this family, but it does not
    vanish; with a real positive edge the larger volatility works the other way on the edge term, so the net sign
    for a skilled book is not determined. The seal does not measure this for carry-like books: carry passes none of
    G1/G2/G4/G5/G7 in either null, so its 0% family rate comes from the other gates, not from G6. For the price
    families the measured G6-alone rates are close to nominal, so no material effect is measured for them. A
    researcher's slower or cheaper carry variant (fewer cost units) could pass the other gates when lucky and
    would then inherit an unmeasured G6 advantage.

## What I did NOT check

- No evaluation, calibration, seal, selftest or sandbox was run; no price file was read; the research hash was
  compared with data/manifest.json, not recomputed from the data.
- Whether the rows are what the pipeline would produce (determinism of a rerun, resume equality of the top30 run,
  the null builders' correctness, the engine) - only the rows' internal consistency and the rule.
- The item-8 mechanism (conjecture only).
- The remote state of origin (no network); the content of the seal commit beyond the files' presence and hashes.
- The validity of the delegated re-key approval; audits/AUDIT_LOG.md and the coordinator's own recount (not read,
  as instructed).

## Script files (the auditor's scratch folder seal_recount)

recount.py       4d9e083ccba014db97c820ee54a62f5ca9c9db2450d42938429051c0eb03e0c0  independent recount from the text (no kernel import)
recount_out.json e20914ff1cbf9bca6a95140d3751412d823a042d5cbe265d2e6e772961bb1d14  its output
compare.py       dce5c0a0ea646e24c7a4dde37f1df22fe2d581eb1f4d111eb62e86b993f16040  summaries, verdicts, seal, logs, own chain check
header_check.py  8b992c0e51e43b1661caa9cf43c165862c4a35c8156eee658e360ed0c1bdd853  headers vs kernel; kernel cross-check after the recount
row_diff.py      94e4dbe52ab0952b21910c898ad8de19b8b4710aa1bad3bb53fbd7293d306ea8  core rows vs previous sealed artifact
row_diff2.py     64616d76ff3c5c50c7e9441164f6abdf1e3bd6b300b70ead4307c8dabe716135  non-row block differences classified
kp016.py         b4aba589984ca15925403e2a7c288daf9bdc695e0b1695863750a8c536b650ef  item 6
item8.py         b858e738331aec826b36a216a957e545186ff4a487d795928bf7b2a904f5f632  item 8 statistics from stored rows
binom.py         26e589e27047922da684f6967f4d4d1f5f3a2f065f2ae68f8c4925477fd61ada  binomial tails for item 8
attack.py        b569c642572679b0c0c1c769ccbcfeda6d1f477d7475b686293cd9f95b679c23  item 7 extra checks
bytes_check.py   6e7975bf71a85892a53ef0cc036c3850c8dbc382b92521e8f07bb805817a68b4  byte form, duplicate keys
access_peek.py   8019f504597e5f6932b448df9e93993416b74c5bb63e1543aa9b3b5c5d75a1a6  VAL access rows since the re-key
explore.py       c490c9ecd7a04a814529d7a9f708bf95966d37db27b12ed4bbe597382b96ab76  structure survey
survey.py        f205ef4b891526cd8087c2c2c0410fdc9980894bf0332904a89b942677ea4b1c  row keys and statuses
survey2.py       4660e4bb8b0a5221ee99daad98ecf05b10f357f6221dfa4d4610dd7d8dcde71a  stored summary shapes
gv_peek.py       d72014b7aa692ffbd1bb65ffad2ec6c1796847babe0876fa18f6f4fd8fb2080f  gate_values shapes
strpeek.py       a81238cde14c441a62f5489f71c4dd0a47b6194109521ccc9b6003fd56222eae  string-typed numbers
peek_lock.py     48b307461ce78ef5d6faf013399d2fce29e7c0cbfb6c9266d3497260a81ea1f1  lock, logs, HEAD, manifest hash
Commands run in the project: python -B -m omr.kernel_lock verify; python -B -m omr.ledger verify;
git --no-optional-locks status / log / show --stat / branch -vv / rev-parse (read-only).
