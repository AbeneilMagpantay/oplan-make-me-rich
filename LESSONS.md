# LESSONS

Only what the evidence supports, with its source. No real VAL result has been read yet (generation 0
not run), so there are no market lessons. Everything below is about the measuring instrument, from
calibration v3 on the locked kernel with semantic hash 74462785 (300 null worlds and 200 oracle
worlds per configuration; `ledger/calibration_7446278556aadd8f.json`, sealed) and from DEV-only
checks. Earlier calibrations measured instruments that no longer exist.

1. The pipeline rarely passes a program with no edge, even after DEV overfitting (20 random
   parameter draws screened by activity, best DEV Sharpe submitted): at the sealed G6 threshold 0.10,
   44/1,498 submitted pairs pass Tier 1 under null A (day bootstrap; 14 Donchian, 13 vol-target, 6
   SMA cross, 6 RSI, 5 carry) and 35/1,500 under null B (real order, daily sign flips). 0.10 sits one
   pass under the 3% rule for null A. G6 is the binding gate (8.0% / 8.3% of submitted pairs pass it
   at 0.10); G3 (DEV Sharpe > 0) passes 76% / 75%: DEV selection works, it does not carry into VAL
   timing. G8 was not run (upper bounds).
2. The threshold estimate is noisy at 100 worlds: 100 worlds per null gave 14/499 at 0.05 and 16/499
   at 0.10 (3.2%); 300 worlds give 26/1,498 (1.7%) and 44/1,498 (2.9%).
3. A real edge is not guaranteed to pass. Noisy oracles with a true mean VAL Sharpe of 1.5 pass Tier 1
   at 0.10 in 84% (fast, 1-day) / 85% (slow, 20-day) of null-A worlds and 91% / 85% of null-B worlds;
   at 1.0 only 57% / 56% (A) and 63% / 55% (B). Limiting gate: G1 (PSR >= 0.90 over three years).
4. The DEV activity floor (20 direction changes) is a cheap filter: 28% (A) / 19% (B) of random
   baseline draws fail it. In VAL, G10 (12 changes) rejects 1.1% (A) / 13.7% (B) of submitted pairs.
5. On real DEV data the gen-0 SMA cross (20/100) makes only 16 direction changes, so it is expected
   to be an uncounted `activity_dev` rejection at generation 0; the other four baselines make 60 to
   311.
6. Locality changed nothing that mattered for the baselines on DEV: the windowed hold never binds at
   horizons of 60 days (Donchian) or 60 4h bars (RSI) and above; the finite RSI flips no decision.
7. Bugs found before any trial: pandas' rolling corr is not bit-exact under rescaling; rsi/atr/vol
   crashed on a coarse series with no complete bar yet; an unbounded ema seeded at the frame start let
   a program read its bar index (closed by locality); a NaN-holed constant (`hour / hour`) passed the
   first constant probe (closed in FIX PASS 6).
