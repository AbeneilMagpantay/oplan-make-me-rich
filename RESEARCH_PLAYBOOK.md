# RESEARCH PLAYBOOK

The protocol a researcher session follows. This file is GENOME: the meta-review (step 8) may edit
it. The kernel (`omr/`, `tests/`, `CONSTITUTION.md`, `LANGUAGE.md`, `requirements.txt`) is never
edited by a researcher session.

All commands run from the project root with the venv Python (`.venv\Scripts\python.exe`).

## 1. Status

    python -m omr.status
    python -m omr.ledger verify
    python -m omr.kernel_lock verify

If the kernel lock (or its seal) or a ledger chain fails, stop and report to the human. Do not
"fix" it.

## 2. Read

- `LESSONS.md` (what the evidence supports so far)
- the last two `generations/genNNN/REPORT.md`
- `python -m omr.ledger summary` (every counted trial) and `ledger/stage1_log.jsonl` (rejections)
- `STATE.md`

Read trial ROWS (`ledger summary`, `status`) only. Never open `ledger/returns/` or the detail files in
`ledger/trials/`: VAL performance is stored only in aggregate on purpose, so that later generations
cannot fit VAL's period-by-period history (CONSTITUTION section 9).

## 3. Pre-register: write `generations/genNNN/PLAN.md` BEFORE any evaluation

The evaluator refuses generation N without `generations/genNNN/PLAN.md`, and records the PLAN's
sha256 in every counted trial (so editing the plan after a result is visible). 3 to 5 hypotheses.
For each:
- the rule as the exact program text (or its signal line), params with declared ranges;
- mechanism: why would this edge exist and persist, and who is on the other side of the trade;
- falsifier: which result would make you drop it;
- relation to earlier trials (new idea, variation of trial X, answer to a lesson).

A hypothesis written after looking at VAL numbers is not a hypothesis.

## 4. Write the program and explore on DEV only

- One file per hypothesis: `strategies/genNNN_<idea>.omr`, `name = "genNNN_<idea>"` (= the file
  stem). The language is in LANGUAGE.md; copy the shape of the gen-0 files. Shape:

      name = "gen001_example"
      family = "trend"
      kind = "single"
      hypothesis = "..."
      n = param(20, 10, 40)
      d = daily(close)
      signal = sign(d - sma(d, n))

- Rules that bite: at most 6 params (no zero default; the range must contain 0.8 to 1.2 times the
  default; integer params also default +/- 1); windows and lags are integer params or the literal
  1; body numbers are integers -10..10 or +-0.5 (anything else is a param); units must match
  (`close > 0` is rejected, `ret(close, 1) > 0` is fine; quote volume / volume is a price);
  `signal` must be dimensionless. A rejected file names the rule, line and column.
- Literals are parameters too: every body literal except 0 (and except window arguments) is
  jittered by G5 exactly like a declared param, at most 8 per program. Constants built without
  literals (`x / x`, `rank(x, 1)`, a `where` whose condition never changes) are rejected by the
  constant probe (`constant_subexpression`); anything that dodges the probe is evasion, and the
  source audit reports it. `lag(lag(x, 1), 1)` is rejected (`nested_unit_window`): use an integer
  param for a longer lag.
- Honest forms the probe rejects, and how to restate them: `open / lag(close, 1) - 1` (exactly 0
  where the open equals the previous close) -> `(open - lag(close, 1)) / close`;
  `exp(where(rare, 1, 0))` or `rank(where(rare, 1, 0), n)` (a non-zero constant when the event never
  fires on the probe panel) -> use the event series `where(rare, 1, 0)` itself (a zero series is
  accepted) or scale it by a param.
- Locality: every value is computed from a bounded trailing window; a program is flat until ALL of
  its parts have their history (one uniform warm-up), so the longest window decides when it starts
  trading. `ema` remembers 5n rows, `rsi` and `atr` 10n; `hold(..., h)` rebuilds its state from flat
  over the last h bars - choose h long enough that positions re-synchronise within it (the sandbox
  shows when the program is known). Nothing can tell where it is in history; do not try.
- The program cannot see dates, bar positions or price levels; only hour and weekday of the
  decision time. Do not try to encode remembered history through the choice of structure and
  parameters either (KP-010): forward results will judge it.
- kind single: the program runs on each core perp alone, weight = signal / 2. kind portfolio: one
  panel, cross-sectional functions `cs_*` allowed, weights scaled to gross <= 1.
- Activity: at least 20 direction changes in DEV (stage 1, `activity_dev`, free) and at least 12 in
  VAL (gate G10). A direction change = a symbol's state sign(w) (0 when |w| <= 0.01) changes from
  one decision bar to the next. The sandbox prints the DEV count.
- Explore freely with the sandbox (DEV only, uncounted, the same stage-1 checks):

      python -m omr.sandbox strategies/genNNN_idea.omr --set n=30

- Do not try to see VAL any other way. Do not write scripts that read `data/` (the quarantine is
  procedural for session code; CONSTITUTION section 2).

## 4b. Unit top30 (added 2026-11-23 by the coordinator, when the KP-015 kernel was sealed)

`unit = "top30"` trades the point-in-time top 30 USDT perpetuals by volume. Read LANGUAGE.md section 10
before writing a top30 program. What decides whether a top30 idea can pass at all:

- Holding period. Costs are 12.5 bps per side on every symbol: a book that replaces itself every day pays
  about 0.9 of its gross per year, and 1.8 at the doubled costs of G4. Design for holding periods of days
  to weeks. The timing gate G6 is calibrated in this unit for books that turn over in about 5 to 20 days,
  and it fails a program whose weights are still correlated above 0.5 with its own weights about 26 days
  earlier, so a signal that is one slow average over most of the lookback is too slow.
- Lookback: the program's total lookback must not exceed 90 days (`lookback_exceeds_seasoning`).
- Cross-sections: a `cs_*` needs at least 10 in-play symbols with a known input; a symbol with a hole in
  its window drops out until the window is clean.
- G8 runs the same program on the next 30 symbols (ranks 31 to 60).
- The sealed G6 threshold is 0.10 in unit top30 and 0.10 in unit core. G6 tests timing, not luck: a book
  that earns a premium without timing passes it about 1 time in 10.
- Memory: the evaluator refuses a top30 run, uncounted, when the machine is short of free memory (about
  1.5 GiB for a small program).
- Not yet (KERNEL_PROPOSALS KP-017, from the recount of the seal): no program driven by funding
  (`funding8h`, `funding_mean`) or by the perp-index basis (`mark_close`, `index_close`) is submitted for a
  counted trial in unit top30 until the coordinator has run the KP-017 measurement and lifted this. In one
  kind of no-skill world the timing gate passed a losing funding-carry book far too often; until that is
  measured, such a pass could not be trusted. Such programs may be pre-registered and screened on DEV
  (ruling of 2026-11-24, generation 2 round 3); a plan then recommends them "subject to the KP-017
  measurement". Keep them cheap to trade: the finding concerns books dominated by their costs.

## 5. Submit: at most 5 counted submissions per generation (enforced by the evaluator)

Before ANY counted submission the coordinator reads the program text for the patterns the constant
probe cannot see: a threshold or scale built from same-unit field ratios (`mark_close / close`,
`taker_buy_volume / volume` used as a constant), from calendar fields averaged over a cycle
(`sma(hour, 25)`, small-offset averages such as `sma(hour + 0.5, n)` at n = 24), rounding-noise
constants (`sma(hour + e, n) - e`), a sign cliff tuned to the probe panel's fixed seed, a scale such
as `1 / (1 + k)` with a tiny param, or by algebra across a comparison (both sides multiplied by the
same series). A program using them is not submitted. The researcher's inputs are trial rows and `status` only.

    python -m omr.evaluate strategies/genNNN_idea.omr --generation NNN

- The generation must be the ledger's highest or the next one; the 6th counted trial of a generation
  is refused before any row is written.
- A submission that passes stage 1 becomes one counted trial forever the moment its pending row is
  written, whatever happens in stage 2, and raises M for every later DSR. Submit only what PLAN.md
  pre-registered, at its declared defaults (the evaluator always uses the defaults).
- A stage-1 rejection (parse rule, `activity_dev`) is logged in `ledger/stage1_log.jsonl` and not
  counted: fix it in the sandbox. `kernel_fault` (stage 1 or 2) is a KERNEL bug: stop and report it.
  A `liquidated` final status IS counted and reveals no metric. Do not retry variations of a program
  that failed on its merits.
- Identity is the canonical program (names, layout and comments do not matter) + the SEMANTIC
  kernel hash + research_hash: re-submitting the same logic under the same semantic kernel returns
  the existing row; any change of logic or defaults is a new trial.

## 6. Report: write `generations/genNNN/REPORT.md`, update `LESSONS.md` and `STATE.md`

The evaluator refuses generation N + 1 until `generations/genNNN/REPORT.md` exists. The cap of 5 paces
the work; it is not a budget: every counted trial raises M in every later DSR.

- Results table straight from the ledger rows (gates P/F, PSR(0), DSR, M, N, n_literals, g5_vacuous).
  No per-period VAL numbers (none are stored for the researcher).
- A verdict per hypothesis against its pre-registered falsifier.
- LESSONS.md takes only what the evidence supports, with trial ids. Mark anything suggestive but
  unproven as such.

## 7. Pool decisions

    python -m omr.pool list
    python -m omr.pool admit <trial_id> --reason "..." [--replace <member>]
    python -m omr.census

Only Tier-1 trials of the current semantic kernel hash. At most 5 members; replacing one must be
explicit and justified. Run the census after pool changes.

## 8. Every 5th generation: meta-review

Review the whole ledger: which families and ideas pass or fail at which gates, how forward results
compare with backtests, and what the stage-1 log says. Then:
- edit this playbook (level-2 improvement), with a dated note of what changed and why;
- file kernel change requests in `KERNEL_PROPOSALS.md` for the human (problem, evidence, proposed
  change, expected effect on pass rates) - including new fields or functions for the language.

## 9. New data sources

Propose them in `KERNEL_PROPOSALS.md` with the data-admission evidence (CONSTITUTION section 3.2).
Never wire a source in yourself.

## Never

- Never edit the kernel or anything under `ledger/` or `data/`.
- Never compute vault performance or any post-VAL performance outside the census.
- Never tune a program on VAL results and resubmit it as if it were new.
