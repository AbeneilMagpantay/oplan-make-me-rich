# LESSONS

Only what the evidence supports, with its source. No real VAL result has been read yet (generation 0
not run), so there are no market lessons. Everything below is about the measuring instrument, from
calibration v3 on the locked kernel with semantic hash 4598ef42 (locality, constant probe;
`ledger/calibration_4598ef4299ceb43c.json`, sealed) and from DEV-only checks. Earlier calibrations
(2c20fe77 and before) measured instruments that no longer exist.

1. The pipeline rarely passes a program with no edge, even after DEV overfitting (20 random
   parameter draws screened by activity, best DEV Sharpe submitted): at the sealed G6 threshold
   0.05, 14/499 submitted pairs pass Tier 1 under null A (day bootstrap; 5 vol-target, 4 funding
   carry, 3 Donchian, 2 RSI) and 4/500 under null B (real order, daily sign flips). At 0.10 null A
   reaches 16/499 = 3.2%, above the 3% rule, so 0.05 is the largest qualifying threshold. G6 is the
   binding gate (4.4% / 3.0% of submitted pairs pass it at 0.05); G3 (DEV Sharpe > 0) passes 77% /
   76%: DEV selection works, it does not carry into VAL timing. G8 was not run (upper bounds).
2. A real edge is not guaranteed to pass. Noisy oracles with a true mean VAL Sharpe of 1.5 pass Tier 1
   at 0.05 in 83% (fast, 1-day) / 81% (slow, 20-day) of null-A worlds and 91% / 81% of null-B worlds;
   at 1.0 only 60% / 49% (A) and 62% / 50% (B). Limiting gates: G1 (PSR >= 0.90 over three years)
   and, for slow signals, G6.
3. The DEV activity floor (20 direction changes) is a cheap filter: 28% (A) / 19% (B) of random
   baseline draws fail it; only 1 of 1,000 pairs had no draw passing. In VAL, G10 (12 changes)
   rejects 1.4% (A) / 13.8% (B) of submitted pairs.
4. On real DEV data the gen-0 SMA cross (20/100) makes only 16 direction changes, so it is expected
   to be an uncounted `activity_dev` rejection at generation 0; the other four baselines make 60 to
   311.
5. Locality changed nothing that mattered for the baselines on DEV: the windowed hold never binds
   at horizons of 60 days (Donchian) or 60 4h bars (RSI) and above, and the finite RSI flips no
   decision; the baselines simply start later (one uniform warm-up).
6. Bugs the tests found before any trial: pandas' rolling corr is not bit-exact under rescaling;
   rsi/atr/vol crashed on a coarse series with no complete bar yet; and (independent audit) an
   unbounded ema seeded at the frame start let a program read its bar index - closed by locality.
