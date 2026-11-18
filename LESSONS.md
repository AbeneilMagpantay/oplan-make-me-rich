# LESSONS

Only what the evidence supports, with its source. No real VAL result has been read yet (generation 0
not run), so there are no market lessons. Everything below is about the measuring instrument, from
calibration v3 on the locked formula-language kernel 2c20fe77
(`ledger/calibration_2c20fe7752b64de2.json`, sealed) and from DEV-only checks. The lessons of the
retired Python-sandbox instrument (kernel 2317921c) are superseded.

1. The pipeline rarely passes a program with no edge, even after DEV overfitting (20 random
   parameter draws, best DEV Sharpe among the stage-1 passers submitted): at the sealed G6 threshold
   0.025, 6/499 submitted pairs pass Tier 1 under null A (day bootstrap; 4 RSI mean-reversion, 2
   funding carry) and 1/500 under null B (real order, daily sign flips; 1 Donchian). G6 is the
   binding gate (1.8% / 1.2% of submitted pairs pass it); G3 (DEV Sharpe > 0) passes 78% / 76%:
   DEV selection works, it does not carry into VAL timing. G8 was not run (upper bounds).
2. 0.05 missed the 3% rule by one passer under null A (16/499 = 3.21%; null B 1.2%).
3. A real edge is not guaranteed to pass. Noisy oracles with a true mean VAL Sharpe of 1.5 pass Tier 1
   in 83% (fast, 1-day) / 72% (slow, 20-day) of null-A worlds and 91% / 79% of null-B worlds; at 1.0
   only 60% / 43% (A) and 62% / 38% (B). Limiting gates: G1 (PSR >= 0.90 over three years) and, for
   slow signals, G6.
4. The DEV activity floor (20 direction changes) is a cheap filter: 28% (A) / 19% (B) of random
   baseline draws fail it; only 1 of 1,000 pairs had no draw passing. In VAL, G10 (12 changes)
   rejects 1.4% (A) / 13.8% (B) of submitted pairs.
5. On real DEV data the gen-0 SMA cross (20/100) makes only 16 direction changes, so it is expected
   to be an uncounted `activity_dev` rejection at generation 0; the other four baselines make 60 to
   311.
6. The five `.omr` baselines reproduce the old Python strategies weight for weight (synthetic data
   and real DEV, defaults and random draws). Property tests on 220 random programs found two kernel
   defects before the lock (pandas' rolling corr is not bit-exact under rescaling; rsi/atr/vol crashed
   on a coarse series with no complete bar yet); both fixed.
