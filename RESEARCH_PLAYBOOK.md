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

## 5. Submit: at most 5 counted submissions per generation (enforced by the evaluator)

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
