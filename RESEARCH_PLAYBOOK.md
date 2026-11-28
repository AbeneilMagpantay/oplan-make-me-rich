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
- Your own series over a timeframe (kernel of 2026-11-26, KP-019): `tf_last(x, tf)` and `tf_mean(x, tf)` take
  a dimensionless series x and a bare timeframe name (`h2 h3 h4 h6 h8 h12 daily weekly`) and give x at the
  last hour of each complete bin, or its mean over the bin's hours (tf_mean needs an hourly x). The result is
  a series of that timeframe: it changes once per bin, is visible from the bin's last hourly bar, and rolling
  functions on it count bins (`sma(tf_last(x, daily), n)` averages n daily samples). A `cs_*` inside x ranks
  on every hour; a `cs_*` around the result ranks once per bin (LANGUAGE.md sections 6 and 10). The lookback
  is 2h - 2 hours for a bin of h hours, plus x's own. A funding window measured in hours is
  `sma(funding8h, n)`.
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
- The sealed G6 threshold is 0.10 in unit top30 and, since the kernel of 2026-11-26, 0.05 in unit core (the
  no-skill pass rate is now counted over the pairs with a positive DEV Sharpe; LESSONS 37). G6 tests timing,
  not luck: a book that earns a premium without timing passes it about 1 time in 10.
- What the sandbox prints for a top30 program since the kernel of 2026-11-26 (KP-018; DEV rows only, logged
  with the run): G6's speed-limit statistic at one, two and three lag steps of 621 hours (the limit is 0.5; on
  VAL G6 takes the largest over 19 steps, and an undefined correlation counts as over); the DEV Sharpe of the
  same program on next30 (G8's unit); funding paid and funding received, and the DEV Sharpe under G2's funding
  stress and under G4's doubled costs; the average number of names held. `--g6-lags` adds a DEV reading of
  G6's paired comparison (10 stale copies over the last 365 days of DEV). These replace the diagnostic
  programs generation 2 wrote by hand for the speed limit and the stale copy; twins and plain controls stay a
  researcher's tool. They are readings on DEV, not the gates: a program that read well on DEV failed six gates
  on VAL (LESSONS 34 and 35), so a reading can drop a hypothesis but is never the reason to submit one.
- Memory: the evaluator refuses a top30 run, uncounted, when the machine is short of free memory (about
  1.5 GiB for a small program).
- Not yet (KERNEL_PROPOSALS KP-017, from the recount of the seal): no program driven by funding
  (`funding8h`, `funding_mean`) or by the perp-index basis (`mark_close`, `index_close`) is submitted for a
  counted trial in unit top30 until the coordinator has run the KP-017 measurement and lifted this. In one
  kind of no-skill world the timing gate passed a losing funding-carry book far too often; until that is
  measured, such a pass could not be trusted. Such programs may be pre-registered and screened on DEV
  (ruling of 2026-11-24, generation 2 round 3); a plan then recommends them "subject to the KP-017
  measurement". Keep them cheap to trade: the finding concerns books dominated by their costs. The
  measurement is made per program (audits/AUDIT_LOG.md, 2026-11-24 and 25): it was run for
  gen002_averaged_funding_shock, which was then scored and failed on its merits; it lifts nothing for any
  other program.
- What generation 2 taught about screens (LESSONS 34 and 35): a DEV screen reads DEV only. A rule reshaped
  after a DEV result has DEV numbers that are not evidence; say so in the plan, and say what, beyond those
  numbers, makes it worth a counted trial.
- Before the pool (coordinator's rule of 2026-11-25; KERNEL_PROPOSALS KP-020): a Tier-1 result in unit top30
  is not admitted to the pool before the coordinator has run the per-program measurement in null worlds (the
  design of the KP-017 measurement, audits/AUDIT_LOG.md) and put both results to the human. The unit's 3%
  bound is measured on families that are expensive to trade, and G6 tests timing, not luck.

## 5. Submit: at most 5 counted submissions per generation (enforced by the evaluator)

Before ANY counted submission the coordinator reads the program text for the patterns the constant
probe cannot see: a threshold or scale built from same-unit field ratios (`mark_close / close`,
`taker_buy_volume / volume` used as a constant), from calendar fields averaged over a cycle
(`sma(hour, 25)`, small-offset averages such as `sma(hour + 0.5, n)` at n = 24) or over a bin
(`tf_mean(0.5 * hour, daily)`, `tf_mean(hour + funding8h, daily)`: the probe rejects only the bare
`tf_mean(hour, daily)`; `tf_last` of hour or weekday at a bin's end is a constant 0 or a clock), rounding-noise
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
- When a generation closes, the coordinator has the kernel's full test suite run (about 45 minutes; LESSONS
  36: a kernel test broke on a new generation's files and nobody saw it until the next kernel build).

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

## 8b. Meta-review of 2026-11-26 (early, after generation 3's round 2; generations/META_REVIEW_2026-11-26.md)

What changed in this playbook and why (coordinator, on the independent analyst's review of generations 0 to 3):

- Stopped, because the evidence closes them: weekly market-neutral rank books on price, volume or flow
  residuals in unit top30 (15 of the 18 top30 ideas; none reached even the in-sample bar, and continuation died
  on readings nobody had seen); top30 funding or premium contrarian forms (LESSONS 27 and 34); "long when X"
  switches in unit core (LESSONS 8 and 9); anything that replaces its book daily or faster (the cost rate alone
  takes more than any edge shown). No plan registers one of these.
- The bar check at registration (binding from now on). For every hypothesis the plan states, before any run: its
  estimated cost drag in Sharpe units; the Sharpe before costs it therefore needs in VAL (0.74 plus the drag to
  sit on G1's line, 1.5 plus the drag for the odds the calibration measured: about 1.85 for a weekly top30
  book); and the outside evidence that an effect of that size exists in liquid crypto after 2021. An effect
  documented below the bar is not registered. In the DEV screen the liveness item is no longer "DEV Sharpe at
  least 0.6": it is "DEV Sharpe before costs (the DEV Sharpe plus the drop under G4's reading) at least 1.5,
  AND the paired reading's book median over the last 365 days of DEV positive".
- Rules descended from a DEV result: registered only if the parent's DEV Sharpe before costs was at least 2.5
  (room for the decay seen between DEV and VAL), and said to be descended, as before.
- The last 12 months of DEV weigh as much as the whole period: an edge that sits in 2020 is not an edge.
- What a DEV screen is for: killing cheaply. It has not told VAL winners apart (LESSONS 35), so a survivor is
  still only a candidate.
- The direction after this review. Decided by delegation on 2026-11-26: no round of timing ideas until an idea
  passes the bar check, and a study of a premium unit (KP-028) first. SUPERSEDED on 2026-11-27 by the human's
  own direction ("lets still go ahead with the 30 coin"; account about 1,000 USD; KERNEL_PROPOSALS.md, entry
  of 2026-11-27): the search continues in unit top30, the study is stopped, and the rules above are amended
  as follows.
- Amended 2026-11-27. The stop list stands: nothing from a closed class is registered again. The bar check
  stands as arithmetic: every hypothesis states its cost drag and the Sharpe before costs it needs. Outside
  evidence is asked for and stated ("none" is an answer), but its absence no longer bars an idea: the human
  wants ideas that are not the obvious ones, and such ideas have no literature. What bars an idea is the
  screen.
- The wide screen (the form of a round from 2026-11-27). One plan registers ten to twelve ideas compactly: for
  each, the program, the mechanism in a few lines, why it is not one of the classes already closed, its cost
  drag and bar, what is remembered that could bias it. At most two ideas per mechanism class. ONE screen for
  all, fixed before any run: stage 1 passes with at least 30 direction changes, average gross at least 0.5,
  at least 15 names held, not liquidated; DEV Sharpe before costs (DEV Sharpe plus the drop under G4's
  reading) at least 1.5; G4's and G2's DEV readings positive; next30 DEV Sharpe at least 0.3; the speed-limit
  statistic at most 0.40 at one to three steps; in the paired reading at most 4 of 10 stale copies at least as
  good as the book AND the book's median Sharpe over the last 365 days of DEV positive; at least two of the
  three DEV years positive. One default run per idea, with --g6-lags. Only a survivor gets corners and a
  control, then the coordinator's reading and decision. A wide screen will let noise through more often than
  three ideas did: a survivor is a candidate for ONE counted trial, nothing more, and every counted trial
  raises M.

- The tier premise test (generation 4, round 1; decided by delegation on 2026-11-27, KERNEL_PROPOSALS.md entry
  of that date). A wide screen of about twelve ideas whose mechanism belongs to the less liquid coins. Each is
  written as a top30 program (the only universe unit there is) and gets one default run; its FIRST reading is
  the sandbox's next30 DEV Sharpe (ranks 31 to 60), its top30 screen W1 to W8 is read as well. No form whose
  next30 reading is already logged is registered again. The round's result is the count k of ideas with a
  next30 DEV Sharpe of 1.0 or more with the registered sign: three or more and the coordinator proposes a unit
  for the less liquid tier to the human; two or fewer and that front is closed. A next30 reading is one DEV
  number after the top30 cost rate, with no stress: it can justify a proposal, never a submission.
- Outcome of the tier premise test (2026-11-27; generations/gen004/REPORT.md, LESSONS 62 to 65): k = 2 of
  twelve, so the front is closed. No plan proposes a unit for ranks 31 to 60 on the strength of next30
  readings, and no mirror or close relative of that round's readings is registered (flipped, the strongly
  negative ones would be flipped readings, not discoveries). The next30 reading keeps its place as item five of
  the wide screen. The form is worth keeping: when a front would need a build, test its premise first with the
  tools as they are, under a count rule written before the ideas.

## 9. New data sources

Propose them in `KERNEL_PROPOSALS.md` with the data-admission evidence (CONSTITUTION section 3.2).
Never wire a source in yourself.

The desk study of 2026-11-28 (`notes/desk_study_other_data_2026-11-28.md`, LESSONS 66 to 68) checked 53
candidate sources against section 3.2. Read its table before proposing a source, and do not propose again
one it rejected without a new fact (a longer history, a changed licence, an archive of vintages). The one
source that passed, the spot market of the same coins, is filed as KP-029; nothing is built on it and no
study of it is run before the human's decision. Read a source's terms of use when it is proposed.

Outcome (2026-11-28; generations/gen004/REPORT.md round 2, LESSONS 69 to 73): by the human's decision the
premise of KP-029 was tested on DEV, outside the sandbox, by `studies/kp029/` (the kernel's own interpreter
and engine called from outside, the new data served through the loader argument, the plan and the code on the
remote before the first file was fetched). None of its three hypotheses passed; the spot front is closed and
the dataset is not proposed. The form is kept for any later source: a premise study before a build, its pass
rule and its data rules (what a missing hour means, what a guard is for) written before the data are opened.

## 10. The search is parked (2026-11-28)

After generation 4 the coordinator starts no round. Seventy-five ideas were screened or scored and none
passed; the less liquid coins and the spot-market data were each closed by a premise study. A researcher
session is ordered only when the human brings an idea of his own or decides to change what is searched or what
the scorer credits. A single idea of his is registered and run as one default run against the wide screen of
section 8b, with the stop list and the bar check as they stand.

## Never

- Never edit the kernel or anything under `ledger/` or `data/`.
- Never compute vault performance or any post-VAL performance outside the census.
- Never tune a program on VAL results and resubmit it as if it were new.
