# AUDIT LOG

One entry per audit round. Auditor: an independent Opus auditor working on a copy of the tree; from
round 3 also the coordinator's own read of the core modules.

## Round 1 - 2026-11-18 - Python-sandbox kernel, before hardening
- Verdict: NOT READY. 6 critical: the kernel was reachable through an import; file access through
  whitelisted modules; memoised outputs beat the lookahead test; a NaN column skipped every
  lookahead cut; VAL numbers were readable without a counted trial; hard-coded dates passed.
- Fixed by: the hardening build (child runner, allowlist, two-stage count-before-exposure, VAL handles).

## Round 2 - 2026-11-18 to 19 - hardened kernel 2317921c
- Verdict: NOT READY. 4 critical: pandas string dispatch escaping the child; a file-backed memo;
  stored data rewritten between stages; epoch arithmetic undoing the fixed time shifts. Also G8
  failing every strategy on real data, and the G6 denominator.
- Answered by: replacing Python strategies with the interpreted formula language (no strategy code is
  executed), hash-at-read data, the G8 fix and the submitted-pair denominator.

## Round 3 - 2026-11-19 - commit c891061 (kernel 2c20fe77)
- Verdict: NOT READY. 1 critical: a bar-position clock through an infinite-memory filter seeded at
  the frame start (a remembered-calendar program reached Tier 1 on a synthetic world). 1 high:
  constants built without literals. 3 medium: seal accepted a hand-edited artifact; the dry run read
  real VAL bars; one-line PLAN.md opened a generation.
- Coordinator's read: literals escaping the jitter; a redirectable VAL access log; VAL returns by
  period in stored detail; quote-volume units; a parser crash on huge literals.
- Answered by: FIX PASS 4 and 5 - locality by construction (known channel, finite memory, windowed
  hold, fixed-order windows, start-cut self-checks), jittered literals, the constant probe, the
  two-part lock, the calibration log, the synthetic dry run, the REPORT rule.

## Round 4 - 2026-11-19 - commit adf910b (semantic 4598ef42)
- Verdict: READY, no critical or high. Residuals documented: near-constants, the seal forgeable
  locally, report content not checked, a custom data provider.
- Coordinator's read: the probe's NaN gap (`hour / hour`), its false rejections of rare-event rules,
  mark_close windows blanked by single missing bars.
- Fixed in: FIX PASS 6 (refined probe, stale-limited mark_close, probe_fault, 300/200-world
  calibration, documents).

## Round 5 - 2026-11-19 - commit d2c2d4f (semantic 74462785)
- Verdict: READY, no critical, high or medium.
- Independent recount of `ledger/calibration_7446278556aadd8f.json`: null A 10, 26, 44 of 1,498 and
  null B 6, 18, 35 of 1,500 at 0.025 / 0.05 / 0.10; the rule gives 0.10; null A at 0.10 is one pair
  from the 3.0% limit (95% interval about 2.2% to 3.9%). Artifact, calibration-log row and seal are
  in d2c2d4f.
- Two low, text-only items: KERNEL_PROPOSALS KP-014 (open; needs the human's approval).
