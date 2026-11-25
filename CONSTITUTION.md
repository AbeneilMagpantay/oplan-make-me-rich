# CONSTITUTION v1 (perpetual futures, formula language)

This file is part of the KERNEL. It changes only through a re-key (section 10). Every number below
is mirrored in `omr/constants.py`, except the G6 threshold, which is written into `kernel.lock` by
the calibration seal (section 8). If they ever disagree, the code is what ran and the disagreement
is a kernel bug.

## 1. Purpose

A research system that looks for trading strategies on USDT-margined perpetual futures and says
"no edge" honestly when there is none. Later sessions run generations: an LLM researcher reads the
ledger and lessons, pre-registers hypotheses, writes strategy PROGRAMS (`.omr`, LANGUAGE.md),
submits them to the evaluator, records the results, and promotes passers to a forward-tested paper
pool.

The loop improves strategies (level 1) and its own research playbook (level 2). It must never be
able to raise its score by weakening the measuring instrument. Enemies, in order: (1) backtest
overfitting and multiple testing, (2) lookahead, (3) unrealistic costs. Small, correct and
auditable beats feature-rich.

Nothing in this system trades real money. Kernel v1 contains no exchange credentials and no
order-placement code.

## 2. Kernel, genome and threat model

KERNEL (immutable to the loop): EVERY file under `omr/` (including the programs in
`omr/programs/`) and `tests/`, plus `CONSTITUTION.md`, `LANGUAGE.md` and `requirements.txt`. Their
sha256 hashes are recorded in `kernel.lock`; any other file appearing under `omr/` or `tests/`
(a `__pycache__` included) fails verification. The lock has two parts with their own hashes: the
SEMANTIC part (everything under `omr/` and `requirements.txt`: what runs) and the TEXT part
(`CONSTITUTION.md`, `LANGUAGE.md`, everything under `tests/`: what describes and checks it). Trial
identity and the calibration seal bind to the SEMANTIC hash. Every re-key and the seal append a
hash-chained row to `ledger/kernel_history.jsonl`. `kernel_lock verify` also compares the installed
package versions (from the environment's `*.dist-info` metadata) and the running Python with the
exact pins in `requirements.txt`. The evaluator refuses a lock that does not verify or is not
sealed; sandbox, pool and census refuse a lock that does not verify. The research environment
never writes bytecode (`sys.dont_write_bytecode` set by a `.pth` file in the venv).

GENOME (the loop may write): `strategies/`, `generations/`, `LESSONS.md`, `RESEARCH_PLAYBOOK.md`,
`STATE.md`, `KERNEL_PROPOSALS.md`.

The loop never edits the kernel, never edits `ledger/` or `data/` by hand, never adds a data source
itself, and never computes vault performance.

Threat model. **No strategy code is executed.** A strategy is a `.omr` text program in a small
formula language (LANGUAGE.md); the kernel parses it with `ast.parse`, walks the tree with its own
checker (only names, numeric literals, calls to the language's functions, `+ - * /`, unary minus,
`not`, `and`/`or` and single comparisons exist), and evaluates the checked tree with its own
interpreter. There is no import, attribute, subscript, string, loop, file, process or eval path for
a program to reach. So:
(a) lookahead, calendar dependence and scale dependence are excluded by construction. LOCALITY: every
    definite value at bar t is a function of a bounded trailing window of data, computed from that
    window alone in a fixed order, and whether history is sufficient is a separate KNOWN channel that
    a program cannot observe (LANGUAGE.md section 7): there is no index, date or bar count, every
    recursive function has finite memory, `hold` is re-run from flat over a bounded window, and a
    row without full history has no definite value anywhere. A program therefore cannot derive where
    it is in history from the frame (the audit's first-bar-impulse clock is a regression test). The
    truncation and start-cut self-checks verify this of the kernel's own functions on every trial.
    Units make the signal invariant to price and volume levels. A program can still react to market
    EVENTS its author remembers (KP-010);
(b) a program cannot see, store or leak anything: its only output is a signal array;
(c) ANY scored run on VAL bars is a counted trial (the single exception is the kernel selftest,
    section 9);
(d) the VAL quarantine for HUMAN-OR-SESSION code (scripts, notebooks, an LLM session with shell
    access) is PROCEDURAL: VAL handles (section 9) and private data readers are tripwires against
    honest mistakes, not a security boundary against someone with write access to the folder. A
    determined author can still read VAL bars outside the kernel - for example with a custom data
    provider passed to the evaluator that reads the stored files directly, or with a script that
    opens data/ - and the kernel cannot prevent it. Forward results, measured after a program is
    frozen, are the last line of defence.

## 3. Data and regions

Instruments: Binance USD-M linear perpetuals.
- Core universe (traded in research): BTCUSDT, ETHUSDT.
- Extended universe (veto only, survivorship-biased): SOLUSDT, BNBUSDT, XRPUSDT, ADAUSDT,
  DOGEUSDT, LTCUSDT, LINKUSDT, AVAXUSDT.

Bars: 1h OHLCV, UTC, indexed by bar OPEN time. Stored on a complete hourly grid; a missing bar
becomes the previous close for open/high/low/close, volume-type columns 0, `is_gap = True`.

Regions (bar open time, UTC, inclusive):

| region | from | to | rule |
|---|---|---|---|
| warm-up | first bar (BTC 2019-09-08, ETH 2019-11-27) | 2019-12-31 23:00 | indicator input only, no positions |
| DEV | 2020-01-01 00:00 | 2022-06-30 23:00 | free sandbox, uncounted |
| VAL | 2022-07-01 00:00 | 2025-06-30 23:00 | counted: any scored run of a program on VAL bars is one trial forever |
| VAULT | 2025-07-01 00:00 | 2026-11-18 09:00 (build snapshot end) | never computed in kernel v1 |
| FORWARD | bars after a program's birth (and after VAULT end) | - | measured only by the census |

Loaders take an explicit ceiling: `dev_end`, `val_end`, or `latest`. Any ceiling beyond DEV end
needs a ledger-issued ValHandle (section 9). Only `omr/data.py` and `omr/census.py` may name
`latest` (tested).

Every stored file is hashed AT THE MOMENT IT IS READ and must equal its sha256 in
`data/manifest.json` (a file missing from the manifest is refused); the same bytes are then parsed.
The readers are private to the data layer (`omr/data.py`, `omr/datasets.py`; tested). The manifest
records per dataset and symbol the source, rows, gaps, the REST-vs-bulk cross-check, mark-price
coverage and the sha256, plus `research_hash` (sha256 over every stored row visible at or before VAL
end). An update checks the stored files first and refuses on any mismatch; an update that would
change a stored row writes nothing and stops.

`python -m omr.data validate` checks every dataset, symbol and region (warm-up, DEV, VAL, VAULT,
after) for finite and positive prices, OHLC consistency, finite non-negative volumes, unique
sorted hourly timestamps, finite funding with positive intervals, mark coverage and gap bars; it
prints and stores COUNTS only (`data/validation.json`, bound to the data fingerprint: the
research_hash and every file hash). The evaluator refuses to run without a passing validation of
the current files. If validation fails on real data, nothing is filled in: the human decides.

### 3.1 Dataset registry and point-in-time alignment

The data layer is a registry of dataset adapters (`omr/datasets.py`). Each declares its name,
frequency, history start, source, fields, and `visible_from(row)` = the open time of the 1h bar
from whose CLOSE the row may be used. One kernel function, `align_to_grid`, puts rows on the 1h
grid and never shows a row before its `visible_from` bar.

v1 datasets:
- `klines` (1h): Binance USD-M bulk klines, REST for the 2019 warm-up and the hours after the last
  bulk file. Visible from its own bar.
- `funding` (event): Binance USD-M bulk fundingRate, REST for the 2019 backfill and the current
  month; settlement times rounded to the hour; a rate settled at t is visible from the bar that
  opens at t. A missing interval is the gap to the previous settlement (first row: 8 hours).
- `mark_klines` (1h, KP-001): Binance USD-M bulk markPriceKlines, REST for the backfill (from
  2019-12-23 11:00) and the hours after the last bulk file; missing mark bars stay missing. The field
  `mark_close` is the close of the last mark bar at or before the row and is known while that bar is
  at most MARK_MAX_STALE_HOURS = 6 hours old.

Every program frame carries the klines columns, `funding_rate` (settled at that bar's open, else 0;
used by the engine), `funding.rate/interval_hours/new` and `mark_klines.open/high/low/close/new`
(as of the latest visible row). The language exposes them as the fields of LANGUAGE.md section 5.

### 3.2 Data admission

A new dataset enters only by a kernel re-key, after it shows: (a) history covering DEV and VAL;
(b) timestamps as of when each value was knowable, with a conservative lag; (c) the same source live
at decision time; (d) it is free, or its cost was approved by the human; (e) a revision check. The
researcher proposes sources in `KERNEL_PROPOSALS.md`; it never wires one in itself. A new field or
function of the language is a kernel change of the SEMANTIC part (every trial identity changes).

## 4. Engine and costs

Linear perpetuals, signed weights, no leverage above 1x gross anywhere in research.

- Weight = signed notional / equity, each in [-1, 1], gross sum(|w|) <= 1. By rule (LANGUAGE.md
  section 7) the signal is clipped to [-1, 1] and portfolio weights are scaled down to gross 1; an
  out-of-range signal is never a failure.
- The weight decided at the close of bar t is executed at the open of bar t+1. Returns are
  open-to-open. Cash earns 0.
- Holdings drift with prices. Order at every bar open: 1. mark to the open; 2. funding: equity
  changes by -sum(h_i x rate_i) on the drifted position coming into that open; 3. rebalance: if ANY
  |target - drifted weight| > 0.01, trade ALL assets to target; cost = traded notional x (5.5 bps
  taker fee + 2 bps slippage) per side, deducted from equity.
- Liquidation check, per bar, on MARK price: worst-case intrabar equity with every long at the
  bar's mark low and every short at its mark high, relative to the mark open of the same bar; where
  a bar has no mark data, last-price low/high relative to the last-price open. Worst-case equity at
  or below 2.5% of gross notional flags liquidation. In the base run this ends the trial with final
  status `liquidated` (counted, no metric); in jitter, stress, permutation and extended-universe
  runs it scores that run as Sharpe = -infinity (an extended unit is coded `liquidated`).
- Cost stress = 2x costs. Funding stress = funding paid x1.5, received x0.5.
- Daily returns: equity sampled at the 00:00 UTC opens BEFORE any trade there; a run's first day
  starts at its first bar (capital 1.0), its last day ends at the post-trade equity of its last bar.
- `deploy_scale = min(1, 0.20 / max drawdown over DEV+VAL)` is recorded on every evaluated trial.
- A numba-compiled inner loop (no on-disk cache) and an independent pure-Python reference agree to
  1e-10, including liquidating paths and paths where equity reaches 0 (tested).

## 5. Statistics

On DAILY net returns, 365-day annualisation, risk-free 0.
- Sharpe = mean / std(ddof=1) x sqrt(365); 0 when std < 1e-12.
- PSR(SR*) = Phi((SR - SR*) x sqrt(n-1) / sqrt(1 - g3 x SR + ((g4-1)/4) x SR^2)), SR per day.
- DSR = PSR(SR0), SR0 = max(0, sqrt(V) x [(1-g) x PhiInv(1-1/N) + g x PhiInv(1-1/(N e))]),
  g = 0.5772156649, N = rho + (1-rho) x M. M = every counted trial including the current one
  (pending, incomplete, liquidated and kernel_fault trials count). V (variance of per-day VAL
  Sharpes, floored at 1/(n-1)) and rho (mean pairwise correlation of VAL daily returns, clipped to
  [0,1]) use only counted trials with stored returns.

## 6. Evaluation (two stages: count before exposure)

`python -m omr.evaluate strategies/<name>.omr --generation N`.

Preconditions (refused before any row): the kernel lock verifies and is sealed; the ledger chains
and HEAD anchors are intact; the stored data equal the manifest and are validated; N equals the
highest generation in the trial ledger or that plus one (0 for an empty ledger);
`generations/genNNN/PLAN.md` exists, and for N >= 1 `generations/gen(N-1)/REPORT.md` exists;
generation N has fewer than 5 counted trials. The cap PACES the work; it does not limit attempts over
time. The protection against many attempts is the count M: every counted trial raises M in every
later DSR, forever. The code checks only that PLAN.md and REPORT.md EXIST (and records the PLAN's
sha256); their content is not checked by code.

Stage 1, UNCOUNTED, on DEV-only frames (warm-up + DEV, no handle):
1. Parse and static checks (LANGUAGE.md), the constant probe and the nested-window rule included.
   A rejection is `parse:<rule>` with line and column.
2. Identity and dedupe: trial id = sha256(canonical program + SEMANTIC kernel hash +
   research_hash)[:16]. An identical trial returns the existing row and is not counted again.
   The evaluator always evaluates the declared defaults.
3. Signals on DEV (each symbol on its own history for kind single; the panel for kind portfolio).
4. Truncation self-check: the program is re-evaluated on data cut at 24 random rows between the
   bar before DEV start and DEV end, plus DEV end; every row up to each cut must be identical
   (values and known; NaN equal to NaN). Start-cut self-check: 6 cuts in the first 60% of the DEV
   frame; every frame, BTC included, loses its rows before the cut; wherever the cut run is known,
   the full run must be known and bit-identical. Cut seeds come from fresh OS entropy and are
   stored afterwards. A mismatch, or any interpreter exception, is `kernel_fault` (the functions are
   causal and local by construction, so this is a kernel bug to report, never a property of the
   program).
5. Activity in DEV: per symbol, state = sign(w) where |w| > 0.01, else 0; a direction change is a
   decision row whose state differs from the previous row's; the sum over symbols must be >= 20
   (`activity_dev`).
A stage-1 rejection is ONE row in `ledger/stage1_log.jsonl` (hash-chained); nothing enters the
trial ledger and nothing is counted.

Then a COUNTED `pending` row is appended to `ledger/trials.jsonl`, flushed and fsynced. It holds the
trial id, generation, the sha256 of the generation's PLAN.md, the semantic, text and combined
kernel hashes, research_hash, the canonical text, params, node count, number of jitterable
literals, and the python / numpy / pandas / numba / pyarrow / scipy versions; the frozen source copy `ledger/sources/<id>.omr` is written before it.
The pending row issues the trial's ValHandle.

Stage 2, COUNTED, on DEV+VAL frames: every frame is hash-verified at read again; signals are
recomputed and the DEV rows (values and known) must equal stage 1 bit for bit (else final status
`kernel_fault`, reason `dev_rows_changed`); 3 start cuts over the first 90% of the full frame must
agree (else `kernel_fault`, reason `start_cut`); then the engine, liquidation, metrics, gates (section 7), the result
files (`ledger/returns/<id>.parquet`, `ledger/trials/<id>.json`) and the final row. Final statuses:
`evaluated` (with tier), `liquidated`, `kernel_fault`. ANY unexpected exception in stage 2 (an
interrupt included) writes the final row `kernel_fault` with the exception type and no metric; a
pending row is never left behind by an exception.

## 7. Gates and tiers

All on the one continuous DEV+VAL run unless stated. Tier 1 ("paper-eligible") needs ALL of G1-G8
and G10.

| gate | rule |
|---|---|
| G1 | VAL PSR(0) >= 0.90 |
| G2 | funding stress (paid x1.5, received x0.5): VAL Sharpe > 0 |
| G3 | DEV Sharpe > 0 |
| G4 | VAL Sharpe at 2x costs > 0 |
| G5 | jitter: 12 variants; EVERY param x U(0.8, 1.2) (ints rounded; an int left unchanged by rounding moves by 1 with a random sign; clipped to bounds) AND every body literal other than 0 (window/lag/count arguments excluded) x its own U(0.8, 1.2) - a literal is an implicit parameter, not a free constant (at most 8 per program; a name computed once shares its jittered value); draw order params (declaration order) then literals (source order); median VAL Sharpe >= 0.5 x base VAL Sharpe AND >= 75% with VAL Sharpe > 0. A program with neither params nor jitterable literals passes and the trial records `g5_vacuous`. Only the median and fraction positive are stored. |
| G6 | timing permutation on VAL: 200 circular shifts of the VAL weight matrix against VAL prices (offsets uniform in [30 days, length - 30 days], all assets together, funding on the price timeline, engine restarted flat at VAL start for actual and shifted alike); p = (1 + #(shifted Sharpe >= actual)) / 201 <= the SEALED threshold (section 8) |
| G7 | sub-periods 2020, 2021, 2022, 2023, 2024, 2025H1: net return > 0 in at least 4, AND the largest bucket log return <= 50% of the sum of positive bucket log returns |
| G8 | extended-universe veto. Kind single: the program on each extended perp alone at full weight; kind portfolio: on the disjoint tuples (SOL,BNB), (XRP,ADA), (DOGE,LTC), (LINK,AVAX). Each unit from its OWN first bar (its own warm-up, flat until its signal exists), DEV start at the earliest, to VAL end; btc(...) stays the real BTC. A unit with < 2 years of scored history is coded `short_history`, a liquidated unit `liquidated`; coded units count as NOT positive. Median Sharpe > 0 AND at least half > 0. No exception is swallowed. |
| G10 | activity in VAL: direction changes (section 6, step 5) >= 12 |

G9 (at most 6 params) is retired as a gate: the parser enforces it. Information only: the benchmark
(constant long 1/K per core symbol through the same engine) VAL Sharpe and max drawdown, beta,
annualised alpha and PSR(0) of the beta-hedged residual.

## 8. Calibration (core protocol v7, unit top30 protocol v10) and the seal

The G6 threshold is not a constant. The sequence is fixed: lock the kernel (re-key) ->
`python -m omr.calibrate` on the LOCKED kernel (it refuses otherwise; the artifact records
`kernel_lock_verified: true` and the locked SEMANTIC hash; the sha256 of the artifact's bytes is
appended to the hash-chained `ledger/calibration_log.jsonl`) -> `python -m omr.kernel_lock seal
--calibration <artifact>`. The seal re-applies the rule in code to the artifact's stored per-pair
rows and, only if the rule passes, writes the threshold, the artifact's sha256 and the semantic hash
into `kernel.lock` and `ledger/kernel_history.jsonl`. It refuses an artifact without a
calibration_log row for exactly its bytes (a hand-edited artifact), one not from the verified
locked semantic kernel, not on the stored data, or whose families are not the kernel's baseline
programs. `verify` fails if the sealed artifact changes or loses its log row. The evaluator refuses
an unsealed lock. A text-only re-key keeps the seal; a semantic re-key removes it.
`--unlocked-dry-run --out <file>` runs the protocol on FULLY SYNTHETIC prices, reads no real bar
after DEV end, and can never be sealed.

The calibration measures the real stage-1 and stage-2 pipeline functions, in-process, on synthetic
worlds built from the real core data on the real calendar (klines, mark bars and funding together),
read under a logged calibration handle; nothing enters the trial ledger:
- Null A: whole UTC days drawn iid with replacement from DEV+VAL, the same day for both core
  symbols. Destroys multi-day predictability.
- Null B: the real day order; per UTC day one fair coin (shared by both core symbols) mirrors that
  day's demeaned hourly log-return path, r' = -(r - m) + m (high/low excursions swap; mark bars
  likewise; funding unchanged). Keeps real volatility dynamics, destroys direction across days.
- DEV-overfit protocol, 300 worlds per null x the five kernel baseline programs
  (`omr/programs/gen000_*.omr`, hash-locked; `--families` accepts nothing else): 20 parameter sets
  drawn from the declared ranges are SCREENED with the DEV signals and the activity rule only; the
  activity passer with the best DEV Sharpe gets the full stage 1 (truncation and start-cut
  self-checks) and is SUBMITTED to stage 2; none -> nothing submitted. A draw liquidated on DEV (or
  whose DEV Sharpe is otherwise not a finite number) is never a candidate and so never submitted
  (fix pass 10, R-Q; both units); a pair without a candidate is not submitted. Null pass rate
  = Tier-1 passes / DEV-POSITIVE EVALUATED pairs (evaluated with G3, a positive DEV Sharpe, true; KP-016: a
  researcher does not spend a counted trial on a program with a negative DEV Sharpe, which fails G3 with
  certainty). Every gate value and G6 p is stored (G8 not run: no extended universe; G8 can only veto, so the
  rates are upper bounds). In the top30 calibration every evaluated row also stores, per lag, the statistics of
  the books G6 ran (g6_lag_detail, KP-017; information, no symbol, date or price).
- Noisy-oracle power: per asset sign(rho z_future + sqrt(1 - rho^2) eps), re-decided every k days
  (fast k = 1, slow k = 20), weight = signal / K, injected after the interpreter into the gates
  (G5 passes, no params). On 200 fresh worlds per null and speed, rho is tuned per speed and level so the
  ACHIEVED mean VAL Sharpe over those worlds is within 0.1 of the nominal 1.0 / 1.5 (reported).
- Rule: the G6 threshold is the LARGEST of 0.025 / 0.05 / 0.10 whose null pass rate (over the
  DEV-positive evaluated pairs, KP-016) is <= 3.0% under BOTH nulls and at which no single family's null
  pass rate (its Tier-1 passes / its own EVALUATED pairs; a family without an evaluated pair fails) exceeds
  6% (FAMILY_PASS_MAX, fix pass 7, R-L) under either null; a null with fewer than 100 DEV-positive evaluated
  pairs (DEV_POSITIVE_MIN, KP-016) fails every threshold, because at 100 the 3% bound admits three passes
  while over a small denominator a single world would decide the threshold, and a refusal is the honest
  answer there; then oracle power at true Sharpe 1.5 must be >= 50% for both speeds
  under both nulls, with every oracle level within 0.1 of nominal. If none qualifies or the power rule
  fails, nothing is sealed, generation 0 cannot run, and the human decides; the verdict names, for each
  threshold, the bound (pooled, or the family by name) and the null that failed. Since KP-015 the rule
  is applied to EACH unit on its own rows and the seal holds one threshold per unit (section 13).
  Why a family bound: the pooled rate is diluted by families that cannot pass in a null world (in the
  top30 null worlds of fix pass 7 reversal and carry never passed, so 3% over all evaluated pairs would have
  allowed the one family that could pass 9%; the DEV-positive denominator of KP-016 removes the pairs that
  fail G3, not the DEV-positive pairs of a family that never passes the other gates). The family bound stays
  over a family's evaluated pairs: over its DEV-positive pairs it would be ill-conditioned (in the sealed
  top30 rows the carry family has 14 under null A). Why 0.06: the conventional 5% level plus a sampling
  allowance; with 200 worlds a family with a true rate of 4.5% is accepted in about 88% of runs per null, one with 9% is
  refused in about 91%. The family bound can only lower a threshold. What it permits: a family that
  passes every other gate in null worlds may reach Tier 1 in up to 6% of its own evaluated pairs, above
  the pooled 3%. The artifact also stores, per
  threshold, the pooled rates over all evaluated and over all submitted pairs and the family rates over
  DEV-positive pairs (information; the rule does not read them).
  Fix pass 11 (R-R, which replaces the cap of fix pass 10's R-P): (a) the pooled and the family rates
  are Tier-1 passes over EVALUATED pairs (since KP-016 the pooled rate over the DEV-positive ones among
  them; a submitted pair that ends liquidated or in a fault leaves the
  denominator, as a pair never submitted does), and a rate without an evaluated pair fails, so no family
  is skipped. (b) Evidence floors: under each null every family must end with at least 50%
  (FAMILY_EVALUATED_MIN) of its designed pairs evaluated, and the null as a whole with at least 75%
  (NULL_EVALUATED_MIN); designed pairs are the worlds ordered for the null, never the rows present.
  (c) At most 3% (NULL_FAULT_MAX) of the candidate pairs may end in a fault: a submitted pair that ends
  neither evaluated nor liquidated (a kernel fault or anything unknown), or a pair whose chosen draw fails
  stage 1 (KP-017 item 3: the screen and stage 1 apply the same activity rule to the same weights, so such a
  failure is a self-check fault); the share is counted over the submitted pairs plus those chosen draws. A
  null that misses (b), (c) or the DEV-positive floor fails every threshold; every bound
  holds only when its counts are proper and the share is inside it, and the verdict records the floors,
  every share and the faults. (d) The stored rows must be exactly the protocol's design: one null row
  per seed and family and one oracle row per seed, speed and level, with the module's seeds; a missing,
  double or foreign row stops the unit. Every evaluated row's p must lie on its lattice, k / 201 in the core
  unit and k / 21 in top30 (KP-017 item 4); a row off its lattice stops the unit as malformed. (e) The seal
  refuses a calibration whose protocol header is not
  the one the locked kernel itself writes for a real run of the protocol's size (core 300 null worlds and
  200 oracle worlds per null; top30 200 and 100), compared key by key: the sizes, the seeds, the levels and
  speeds, the draws, the rho grid, the options object and every other field that fixes the run, because a
  run can change some of them at run time and the semantic hash does not pin that. (f) A real run with
  other sizes is refused before any data is read; only a dry run may be smaller. Why R-R replaces the
  cap: after R-Q a liquidation on DEV makes a pair "not submitted", so a breakage could show only as
  pairs never submitted, which the former rule skipped, and thin evidence read as safety. And the cap on
  liquidated pairs was a hard stop that one real bar after DEV end moves by several points, although a
  liquidated no-skill book is a non-pass in the real evaluation as well.

The current seal, its artifact and its numbers are in `kernel.lock` and STATE.md.

A SEAL COUNTS only when the artifact, its calibration_log row and the sealed kernel.lock are in ONE
commit pushed by the coordinator, and an independent auditor has recomputed the null and oracle
counts and the rule from the artifact's stored rows. `log_calibration` is a public function, so the
log alone proves nothing about who produced an artifact.

## 9. Ledger, VAL access, selftest, pool and census

- `ledger/trials.jsonl` and `ledger/stage1_log.jsonl`: append-only, hash-chained (prev_hash,
  row_hash); `ledger/HEAD.json` anchors each chain's row count and head hash and is checked by
  `ledger verify` and the evaluator. Outside the folder, the project is a git repository with a
  private remote: the coordinator commits and pushes `ledger/`, `kernel.lock` and the data manifest
  after every re-key and every generation, so each push anchors the chain heads (KP-009; `ledger
  verify` itself checks only the in-folder anchor). `python -m omr.ledger verify` reports a pending
  row without a final row, and any result file no row references, as `incomplete` (still counted).
- VAL access: every loader and pipeline entry point that touches bars after DEV end requires a
  ValHandle. The ledger issues one when it appends a pending row; calibration, census and selftest
  get one only with an explicit purpose logged in `ledger/val_access_log.jsonl`. A call without a
  handle raises. The VAL access log is the audit trail and is NEVER redirected (a temporary ledger
  leaves it alone); a disk load of real VAL bars with a trial handle whose pending row is not in the
  REAL trial ledger is logged there (kind `temp_ledger_trial`, trial id, source sha256) before any
  frame is returned. `data validate` reads all rows inside the data layer and prints counts only.
- No time-resolved VAL performance is stored: trial rows and detail files keep only aggregate VAL
  metrics; the per-year table keeps calendar years ending by DEV end, and the G7 buckets keep their
  return only if they end by DEV end (later buckets: name and day count; the gate value is
  n_positive and largest_share). The daily returns file exists for the DSR and is read by the kernel
  only; the researcher reads trial rows and `status`, never `ledger/returns` or `ledger/trials/`.
- Selftest, `python -m omr.selftest`: THE SINGLE EXCEPTION to "any scored run on VAL bars is a
  counted trial". Under a logged `selftest` handle it (1) runs the five baselines and two kitchen-sink
  programs using every field, timeframe and function (the second, kernel_kitchen_sink_tf, tf_last and
  tf_mean) on real DEV+VAL frames, checking shape,
  alignment, finiteness and bounds only (nothing scored); (2) runs two kernel NOISE programs
  (`omr/programs/kernel_noise_*.omr`) through the complete evaluate path into a temporary ledger
  that is deleted afterwards, asserting finite metrics and gate inputs, every G8 unit scored, p in
  (0, 1], activity above both thresholds, the daily-return length, stage-2 DEV rows equal to
  stage 1, and a clean `ledger verify`. It prints ONLY `OK` or the failed assertion and file:line;
  no metric leaves it.
- Paper pool: at most 5 members, Tier-1 trials evaluated under the CURRENT semantic kernel hash;
  replacement must be explicit; every change is a hash-chained row in `ledger/pool_log.jsonl`.
- Census: updates the data, then for each pool member parses the frozen program (hash-checked; its
  canonical form and semantic kernel hash must match the current ones) and runs it flat from birth on post-birth bars
  only. Birth = the later of the trial's born_at and its pool admission, rounded up to the next bar
  open, and never before the bar after VAULT end. Forward daily returns (intervals ending at a 00:00
  open) are stored raw and at deploy_scale. Idempotent.

## 10. Kernel change procedure

1. The researcher files a request in `KERNEL_PROPOSALS.md` (problem, evidence, proposed change,
   expected effect). It never edits the kernel.
2. The human (or the coordinator acting for the human, recorded as such) reviews and makes or
   accepts the change; tests pass.
3. `python -m omr.kernel_lock rekey --reason "..." --approved-by "<who>"`. A re-key of the TEXT
   part only (documents, tests) keeps the seal and needs no calibration. A re-key that changes the
   SEMANTIC part removes the seal: `python -m omr.calibrate` runs again on the locked kernel and
   `seal` writes the new threshold before any trial can be evaluated.
4. What a re-key does: trial identity includes the SEMANTIC hash. A text-only re-key keeps every
   trial id (re-submitting an identical program returns the existing row). A semantic re-key
   changes every trial id: earlier trials stay counted in M, re-submitting a program is a new counted
   trial, and pool members evaluated under the old semantic hash can no longer be admitted or
   censused until re-evaluated.
5. If a kernel bug is found after real VAL results were seen, it is fixed, re-keyed with the reason,
   and the before/after results are reported openly.

## 11. LIVE requirements (defined now, implemented in later kernels)

A strategy may trade real money only when ALL hold:
1. At least 60 days forward in the paper pool.
2. Its forward result is not below the 5th percentile of block-bootstrapped same-length windows of
   its own VAL returns.
3. A one-time VAULT check that returns pass/fail only, with every query logged (kernel v2).
4. DSR >= 0.95 on VAL + forward at the then-current trial count.
5. Explicit human approval.

Live risk limits the loop can never change:
- Perpetual futures on the approved venue only. Live gross exposure = deploy_scale by default; any
  increase is the human's decision, with a hard ceiling of 2.0 gross.
- A dedicated sub-account (or isolated margin) holding only the bot's capital.
- API key trade-only, withdrawals disabled, IP-restricted.
- Per-strategy capital cap set by the human.
- An exchange-side reduce-only protective stop on every position, modelled in the engine before any
  live use (kernel v2 item).
- Halts, as defaults the human confirms before live: per-strategy halt (and demotion from the pool)
  at 20% drawdown from peak; account daily-loss halt at 4%.
- A `HALT` kill-switch file checked before every order.
- The bot runs on an always-on host, not a personal PC.

## 12. Known limitations

- VAL quarantine is procedural for human or session code (section 2 d).
- The LLM researcher's training data covers market history to about mid-2026, so every pre-birth
  backtest, the vault included, is optimistic. Locality removes every way to read the position in
  history from the frame, but remembered history can still enter through the CHOICE of structure
  and parameters and through reactions to remembered market events (KP-010). Only FORWARD is clean.
- Scale invariance is bit-exact for power-of-two rescale factors and otherwise exact up to
  floating-point ties.
- The constant probe evaluates numeric nodes on a two-year synthetic panel: a node constant on real
  data but varying on the panel is not caught, and a legitimate node that never varies on the panel
  is rejected (the author must restate it).
- A text- or news-reading signal cannot be honestly backtested; it can only be judged forward (and
  the language has no such input).
- The extended universe is survivorship-biased, so it may only veto.
- Two highly correlated core assets give a small effective sample.
- Funding and prices are Binance's; another live venue will differ slightly.
- Leverage is structurally excluded at gross <= 1. The liquidation check uses 1h mark-price bars;
  real liquidation happens tick by tick with tiered maintenance margins, so the 2.5% rule is an
  approximation. Where mark bars are missing the check falls back to last-trade highs/lows.
- Fills are bar-based at the next open with fixed costs; no order book, no partial fills.
- Between the coordinator's pushes the ledger's hash chain is anchored only inside the folder, and
  `ledger verify` does not itself compare with the remote (KP-009).
- The constant probe catches EXACT constants built without literals (`x / x`, `hour / hour`,
  `rank(x, 1)`, `sign(close * 2)`, `tf_mean(hour, daily)`). It does not catch NEAR-constants (`mark_close / close`,
  `sma(hour, 25)`, `tf_mean(hour + funding8h, daily)`, sums of such ratios used as a scale), a tf_mean of a
  calendar field scaled by a literal (`tf_mean(0.5 * hour, daily)`) or thresholds hidden by multiplying both sides
  of a comparison by the same series; these are deliberate, visible in the text, and left to the
  coordinator's source read before every counted submission (KP-010).
- In top30 a program whose weights change slowly cannot reach Tier 1: G6's speed limit (section 13)
  fails a book whose weights are still correlated above 0.5 with its own weights a lag step (about 26
  days) or more earlier, so books slower than about 50 days are not tested for timing in this unit.
- What G6 does and does not protect against in top30: at 0.10 a book that earns a steady premium
  without any timing passes G6 about 1 time in 10 (that is the test's level; with three years of VAL
  the gate cannot be both stricter and sensitive), and G6 does not protect against plain luck in VAL,
  because stale copies do not share the actual book's luck; that rate is what the null worlds measure
  and the seal bounds. The core unit's G6 (200 circular shifts) has not been examined for the same
  effect; its seal measured its families' rates in worlds that keep each symbol's drift.
- In the top30 null worlds the funding sign coin (R-E) can put the carry family short a name whose real
  funding was strongly negative; with a real up-wick on that name (2022-05-11 13:00, about 4.9 times the
  open by mark) every draw of such a pair is liquidated on DEV and the pair is not submitted (about a
  quarter of the null A carry pairs in the pilot), so the carry family's null pass rate is conditional on
  surviving DEV.
- Liquidations in the top30 null worlds after R-O come from real mark wicks meeting concentrated books
  (the calibration families scale their weights by signal without a cap per name), and the null pass rate
  is taken over the pairs that end evaluated.

## 13. KP-015: the universe unit top30 (built 2026-11-19; NOT in force until the human approves the re-key)

- Data: data/symbols.json (python -m omr.universe symbols; pinned by sha256 in the manifest) classifies
  every USDT-quoted perpetual name of the archive; only crypto perpetuals can be members. python -m
  omr.data universe downloads their monthly 1h klines, funding, mark and index klines (checksums
  verified, resumable) and admits index_klines (the ten core symbols included) into the one research
  hash, which also covers the sha256 of data/symbols.json (fix pass 4); the stored-row revision check
  applies to every table from this download on. data validate
  covers every table and adds membership and unit-availability COUNTS (no handle, nothing logged).
- A program declares `unit = "top30"` (kind portfolio); LANGUAGE.md section 10 states membership,
  in-play, cross-sections and the 90-day lookback limit. Fix pass (2026-11-19): seasoning = first active
  bar at least 90 days before the month and no 7-day run without an active bar inside those 90 days (a
  shorter archive hole does not restart it); in play also needs fresh funding (latest settlement no older
  than twice its interval); no *_SETTLED folder is read. Fix pass 2: funding_mean is known only when its
  last n settlements fall inside the last 8n hours, in every unit (the core stays bit-identical); in top30
  a cs_* computes across the in-play symbols with a known input and is known when at least 10 exist; a
  bar present with zero trades is usable while its zero-trade run is at most 24 (the hour 2024-10-28
  20:00 UTC has zero trades in all 320 listed symbols); a top30 program is evaluated in six-month blocks,
  bit-identical to the whole panel, with the engine's positions, equity and funding carried across. Fix
  pass 3: a run computes its membership once from its own rows and every block of the run uses it (blocks
  hold the members of every month their evaluated rows touch); the self-check `block_overlap` (stage 1:
  an uncounted kernel fault, stage 2: a counted one) compares each block's warm-up with the previous
  block's result; lookback_hours counts the staleness of mark_close / index_close under a timeframe and
  under btc(). Fix pass 4: G6 in top30 became a paired common-names test (fix pass 5: the causal lag
  form below); a cs_* counts only
  known AND finite inputs (a known non-finite input is a known NaN); `data universe` fills every hour
  missing inside a universe symbol's life from the daily files of the same archive (checksum required,
  pinned in the manifest; an hour already stored must equal the daily row, otherwise the download stops
  as a revision; the ten core and extended symbols are filled by the same rule inside their stored klines
  grid, with no top-up and the same snapshot end, and `data update` applies the same fill); the sha256 of
  data/symbols.json
  is part of the research hash and of the validation fingerprint; funding8h is known only while its settlement is at most 2 x min(interval, 8) hours old, in
  every unit (lookback leaf 17), and the in-play freshness caps the interval at 8 hours too; top30
  programs are probed on a 12-symbol in-play panel. The core unit is unchanged and bit-identical
  to the kernel of commit b12df97 (tests/test_core_identity.py).
- Engine for top30 and next30: 12.5 bps per side on every symbol; a position whose next bar is missing
  is closed at its last usable close (possibly a zero-trade bar's frozen price) with that cost; targets of unavailable or out-of-play symbols are 0;
  funding and the mark-price liquidation check per symbol; gross <= 1 across the unit.
- Gates for top30: G1-G5, G7 and G10 as in section 7. G6 (fix pass 5) is a causal PAIRED LAG test. It
  asks whether the program's weights at the time it decided do better over VAL than the SAME program's
  own weights from k hours earlier, traded at the same times. VAL row i is decided at the row before VAL
  start + i and executed at VAL start + i. For each of 20 lags k, equally spaced from 30 days plus one
  random phase to half of VAL (fix pass 9, R-N: the step is (half of VAL - 30 days) / 20, about 26 days),
  the lagged book at row i is the program's own weight row from k hours BEFORE that
  decision (for the first k rows of VAL that is a row before VAL start); no row after the decision is
  ever used, and nothing wraps around. Both books hold only the names common to the row: tradable now (in
  play at the decision row with a usable bar at the execution row) and in play at the lagged row. Each
  book is re-centred to the net of the full weight row it came from (its own in-play set) when that set
  has a name outside the common names (every common name gets (own net - masked net) / number of common
  names, sums sequential in column order, no gross rescaling); a row with fewer than 10 common names is
  flat in both books. Both books run through the engine restarted at VAL start (a liquidated run scores
  -inf); p = (1 + #(lagged >= actual)) / 21, where the lagged book counts as >= when the two books
  are equal within 1e-12 on every cell (a tie, no second engine run) or its Sharpe is >= the actual
  Sharpe - 1e-9 (both can only raise p). So 0.05 means that no stale copy did as well as the actual
  book and 0.10 that at most one did; 0.025 cannot be reached in this unit (power there is 0, so the
  seal cannot choose it). Where no row of the actual book differs from the actual weights the actual run
  is reused. Speed limit (R-N): before any lag run, the correlation between the program's weights and
  its own weights j lag steps earlier (on the names tradable now and in play at the earlier row, each
  name's mean over the rows compared removed from both) must be at most 0.5 for every j from 1 to 19; otherwise
  G6 fails (p = 1) and no lag book is run; an undefined correlation (a book that never changes) counts
  as above the limit. Why: stale copies of a slow book are not independent comparisons, and three years
  of VAL cannot test a book slower than about 50 days for timing. What was measured (audits/AUDIT_LOG.md,
  round 7, X12-prep): for a book with a 37 to 60 day window the correlation of two lagged Sharpe ratios
  is +0.87 at 0 to 10 days apart, +0.50 at 10 to 25, +0.07 at 25 to 50 and about zero beyond, so the
  former 200 uniform lags held only about 11 to 14 independent values, and a book earning a premium
  without timing was first among its copies about 1 time in 13 at any threshold under 0.08 and first or
  second about 1 time in 6 at 0.10. Why no future row: the names common to a row must be known at the decision
  (a source row from the future would keep only names that will still be members later, a survivor
  filter). Two limits, stated plainly (numbers: audits/AUDIT_LOG.md, round 7): (1) the books are compared
  only on names in play at both rows, so positions in names that entered the unit less than k hours
  before are left out of both books; a book whose edge sits in recent entrants is not credited for it,
  and with the real turnover of members a slow strategy has less power here than in the core unit. (2)
  Each book pays its own costs, so for a book whose costs are large next to its volatility the
  comparison is distorted (such books fail G1-G4 anyway). The lag range stays 30 days to half of VAL:
  with lags about 26 days apart the copies of a book that meets the speed limit are close to independent
  comparisons, and a shorter range would leave too few of them. The core unit's G6 is unchanged. G8: the
  same program on unit next30 must have a positive Sharpe over its DEV+VAL span.
- The seal (section 8) needs BOTH calibrations: omr.calibrate (core, unchanged but for the family
  bound of fix pass 7, R-L, which the rule applies in both units) and omr.ucalibrate
  (top30, fix pass 4: null worlds on the REAL membership calendar - every symbol ever in top30 keeps
  its real present and absent hours, trades and volumes, so the kernel's own rule reproduces the real
  monthly schedule, usable flags and unit sizes; only prices are resampled, as open-relative ratios
  cumulated from the real first open, a present zero-trade bar flat; null A draws one source day per
  world day for all symbols, in a month with a unit from the days on which every top30 member of that
  month is fully active (fix pass 5; a pool under 90 days falls back to the whole period), a symbol not
  fully active on it uses a personal fallback day; funding keeps
  the real settlement calendar with the source day's rates; null B mirrors every symbol's demeaned path
  with one coin per day, funding rates as recorded before the sign coin below; fix pass 8 (R-M, which
  replaces fix pass 7's R-K): in both nulls every symbol has ONE expected day gross G on every world
  day, G = the mean over all fully active symbol-days of the source of the day gross (the product of
  the day's 24 hourly close / previous close ratios). A world that keeps each symbol's sample mean as
  its expected return holds a permanent difference between symbols, whether that mean was luck or not,
  which a slow momentum book collects: there ranking on past returns is a real forecast, so it is a
  premium world, not a no-skill world (corrected in fix pass 9; audits/AUDIT_LOG.md, X12-prep). Simple day returns
  are equalised, not log returns, because positions are held between rebalances. Null A: every active
  hour of a shared-branch day drawn from the set Q (the month's pool, or the whole period) has its open /
  previous close ratio multiplied by (G / M(Q, s))^(1/24), M(Q, s) the symbol's mean day gross over Q's
  fully active days, and every active hour of a fallback day by (G / M(s))^(1/24), M(s) its mean over
  all its fully active days. Null B: on a day with n active hours and x the day's sum of (hourly log
  return - m), every active hour is multiplied by G^(1/24) exp(-m) cosh(x)^(-1/n) on either face of the
  coin, so the day's gross is G^(n/24) (1 + tanh x) or G^(n/24) (1 - tanh x), G^(n/24) in expectation
  whatever the path. Every bar keeps its shape (high, low and close over open); hour-of-day means and the
  path inside a source day are kept by design; the draws and the funding are unchanged; the core unit's
  nulls are unchanged (audits/AUDIT_LOG.md, round 7, X10 and X11); fix pass 10 (R-O): a null world's
  liquidation check reads what the real evaluation reads, the source's mark wicks (mark high / open and
  low / open, mirrored on a flipped null B day) on every active row whose source row has a valid mark bar,
  else the world's last-price wicks; a world row without trades stays flat although the real evaluation
  would read its mark wick, and the index bars follow the mark bars (no program reads them)
  (audits/AUDIT_LOG.md, round 7, X12: two real last-price bad prints, mirrored, had liquidated most null B
  books); three hash-locked
  cross-sectional families (momentum and reversal on daily returns, n from 3 to 60 and from 3 to 20 days -
  the reversal mirrors the momentum since fix pass 6 - and funding carry), the same
  screen-and-submit protocol on the production block path, a cross-sectional noisy oracle at two speeds
  on the same worlds, tuned and evaluated at true Sharpe 1.5 only, the level the rule reads). The top30
  calibration runs 200 null worlds and 100 oracle worlds per null (fix pass 11, R-R: the seal refuses other
  sizes). The universe oracle's speeds (fix pass 6, R-I) are fast = 5 days and slow = 20 days; the core keeps 1 and
  20. At 12.5 bps per side the oracle's cost drag in Sharpe units is 3.86 at 1 day, 1.50 at 3, 0.93 at 5,
  0.64 at 7, 0.39 at 10 and 0.29 at 20 days, so no 1-day book with net Sharpe 1.5 keeps a positive Sharpe
  at doubled costs: on 24 audit worlds with the real membership structure and synthetic prices G4 passed
  0 of 24 and Tier-1 was
  0 at every threshold at 1 day, while at 5 days Tier-1 was 18 / 18 / 19 of 24 at 0.025 / 0.05 / 0.10 (G4
  20 of 24; audits/AUDIT_LOG.md, round 7). 5 days is the fastest of 5, 7 and 10 days with Tier-1 at least
  0.65 at all three thresholds, the rule fixed before the sweep. The unit is therefore certified for
  holding periods of about 5 days and longer; faster books are expected to fail G4, which doubles costs.
  The
  universe nulls keep the REAL membership calendar while prices are resampled, so they cannot show an
  effect that needs membership to follow price; the causal construction of G6 is what excludes it.
  Fix pass 5: in the universe null worlds every funding rate is multiplied by a fair sign coin drawn per
  settlement hour (the same coin for every symbol settling then), so no funding payment can be predicted
  from earlier funding and no carry can be earned; sizes, intervals and times are kept. The core
  calibration is unchanged: there its carry effect was small (core carry family mean VAL Sharpe -0.30
  under null A, +0.07 under null B; Tier-1 passes under null B 0, 1 and 3 of 300 at the three
  thresholds). The universe run is resumable (finished tasks in a partial file bound to the kernel,
  data and protocol, every line with its own sha256) and checks memory before it starts. Fix pass 6: it
  runs the oracle phases of both nulls FIRST and then logs the oracle power per null, speed and threshold;
  if the power at the largest threshold is below 50%, or an oracle level misses its bound, it logs that
  the seal rule will stop whatever the null worlds give (the run may be interrupted; the partial file
  keeps the finished work; the artifact does not depend on the order). Fix pass 8: during the null phases
  it logs the same warning once when the Tier-1 passes so far already exceed what the pooled or a family
  bound allows at every threshold, or when the largest threshold still open lacks oracle power (log only;
  fix pass 11: also when a family or the null can no longer reach its evidence floor or the faults exceed
  their bound).
- The seal, fix pass 6 (R-H): the G6 threshold is decided PER UNIT, each unit by the section-8 rule on its
  OWN stored rows: the largest of 0.025 / 0.05 / 0.10 whose null pass rate (over that unit's DEV-positive
  evaluated pairs, KP-016) is <= 3% under both of that unit's nulls and at which no family of that unit
  passes more than 6% of its own evaluated pairs under either of them (fix pass 7, R-L), every null of that
  unit with at least DEV_POSITIVE_MIN DEV-positive evaluated pairs, then oracle power at true Sharpe 1.5 >= 50% for both speeds under both of its nulls at
  that unit's threshold, every oracle level present within its bound. The two units use different G6
  constructions and have different null distributions, so one unit's rows never move the other's
  threshold. Both units seal or neither (a STOP names the unit). kernel.lock holds {"core": x, "top30":
  y}; omr.evaluate applies the threshold of the program's own unit, and the trial row records that one
  number.
- The selftest scores kernel_noise_top30 through the full path as well.
- Memory (R3, S4): before the pending row of a top30 trial the evaluator estimates stage 2's bytes from
  counts in data/validation.json (rows, distinct top30 and next30 symbols, the symbols of every block) and
  the program's fields and statements, and refuses, UNCOUNTED (`memory_insufficient` in the stage-1 log),
  unless the operating system reports at least 1.5 times that as available. Only the columns the program
  and the engine read are loaded, per block and per symbol window; G8's next30 blocks are evaluated one at
  a time and dropped before the top30 blocks are built.
- Data checks (R4): omr.evaluate recomputes the research hash over every stored table on every run;
  the sandbox relies on the per-file sha256 check at read.
- Open interest and long/short ratios are NOT research data; tools/record_metrics.py (outside the
  kernel) stores them forward with first-seen hashes; the kernel never reads them.
