# KERNEL PROPOSALS

Requests for kernel changes, for the human to decide. The research loop appends here; it never
edits the kernel. Format per entry: date, problem, evidence, proposed change, expected effect on pass
rates, status.

## 2026-11-18 (build session) KP-001 Liquidation check on mark price, not last-trade wicks

- Problem: the genesis liquidation check used last-trade bar high/low; the ETHUSDT perp printed a
  high of 323.00 against an open of 95.73 on 2020-03-13 02:00 UTC (mark high 119.47).
- Change made: `mark_klines` admitted; the liquidation check uses mark high/low relative to the mark
  open of the same bar, last-price fallback where a bar has no mark data; 2.5% rule kept.
- Status: CLOSED 2026-11-18 (approved by the coordinator; pre-genesis, zero trials evaluated).

## 2026-11-18 (build session) KP-002 Model the exchange-side protective stop

- Problem: CONSTITUTION section 11 requires a reduce-only protective stop on every live position;
  the v1 engine does not model it.
- Proposed change: kernel v2 engine option for a stop at a fixed distance, with fills at the stop
  level or the bar open if gapped through.
- Status: open (required before any live use).

## 2026-11-18 (build session) KP-003 Confirm the denominator of the null pass rate

- Problem: the threshold rule's denominator was ambiguous (counted pairs vs all pairs) while
  ~25-29% of null pairs failed activity in stage 2.
- Status: CLOSED 2026-11-19 by the FINAL PRE-GENESIS ORDER: the denominator is SUBMITTED pairs.
  Activity is now a free stage-1 filter (`activity_dev`), a pair is submitted only if one of its 20
  draws passes stage 1, and the rule is applied in code by the seal (CONSTITUTION section 8).

## 2026-11-18 (build session) KP-004 Mark-bar quality and maintenance tiers

- Problem: about 3,000 mark bars per symbol have fewer than 3,600 sampled seconds (partial
  sampling), and Binance applies tiered maintenance margins by position size; v1 uses a flat 2.5%
  and treats partial mark bars as complete.
- Proposed change: report partial bars as a separate class, and model the maintenance tier for the
  deploy-scale position size before any live use.
- Status: open (low priority at gross <= 1).

## 2026-11-18 (build session) KP-005 Calibrate G8

- Problem: synthetic worlds carry only the core symbols, so G8 is never exercised in calibration;
  null pass rates are upper bounds and G8's false-veto rate on real edges is unknown.
- Proposed change: extend null A/B worlds to the extended perps (same day blocks and coins) and
  report the G8 pass rate of the oracles.
- Status: open.

## 2026-11-18 (build session) KP-006 Position-encoded calendars

- Problem: a Python strategy could encode remembered history through bar positions (`len(bars)`,
  cumulative counters).
- Status: CLOSED 2026-11-19: no strategy code exists. The language has no index, position, bar
  count, date or cumulative quantity; every window is bounded (<= 5,000 bars, <= 400 days); a
  program's only time inputs are hour and weekday of the decision time. Property tests check
  identical signals under whole-week time shifts on 220 random programs. (Remembered history
  through the CHOICE of structure and parameters remains: KP-010.)

## 2026-11-18 (build session) KP-007 Attribute allowlist is name-based

- Status: CLOSED 2026-11-19: the attribute allowlist and the Python parser it guarded are deleted.
  `.omr` programs have no attributes at all (an attribute is rejected as `node` or `call`); every
  audit payload is a rejected-text regression test (tests/test_exploits.py).

## 2026-11-18 (build session) KP-008 Outdated docstring in omr/strategy_api.py

- Status: CLOSED 2026-11-19: `omr/strategy_api.py` is deleted (with the child runner, the allowlist
  and the Python strategies; archived in `archive/kernel_2317921c_python_sandbox.zip`).

## 2026-11-19 (build session) KP-009 The ledger head needs an external anchor

- Problem: `ledger/HEAD.json` anchors each hash chain's row count and head hash, but it lives in the
  same folder. Anyone with write access can rewrite a chain from any row and regenerate HEAD.json
  consistently; truncating trials.jsonl and HEAD.json together would silently lower M.
- Addressed operationally (2026-11-19): the project is its own git repository (branch main, private
  remote on GitHub). `ledger/` (all chains and HEAD.json), `kernel.lock`, `data/manifest.json` and
  `data/validation.json` are tracked; the coordinator commits and pushes at every gate, so each
  pushed commit is an anchor of the chain heads outside the folder. A rewrite of a chain after a push
  shows up as a diff against the remote. Research sessions make no git writes.
- Remaining (optional kernel change): `ledger verify` could compare HEAD.json with the latest pushed
  commit itself instead of relying on the coordinator's review of the diff.
- Status: addressed operationally by the coordinator's commits; kernel-side check open.

## 2026-11-19 (build session) KP-010 Remembered history through choice of structure and params

- Problem: the language removes dates, positions and price levels, but the researcher (an LLM
  trained on market history to about mid-2026) can still choose a structure and default params that
  fit remembered VAL-period behaviour (e.g. a lookback that happens to time 2022-2024 regimes). No
  static or dynamic check can see this; G5 (jitter) and G6 (timing permutation) only weaken it.
- Proposed change: none in the kernel. Keep forward results as the judge (CONSTITUTION sections 11
  and 12); consider requiring forward days before pool-to-live promotion to scale with the number of
  counted trials of the family.
- Status: open (documentation of a residual risk).
