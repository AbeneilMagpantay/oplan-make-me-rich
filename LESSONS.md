# LESSONS

Only what the evidence supports, with its source. No real VAL result has been
read yet (generation 0 not run), so there are no market lessons. Everything below
is about the measuring instrument, from the final calibration on the hardened
pipeline (`ledger/calibration_43099ad9550d2be7.json`) and from DEV-only checks.

1. The pipeline rarely passes a strategy with no edge, even after DEV
   overfitting (best of 20 random parameter draws by DEV Sharpe): at G6 0.025,
   4/373 counted pairs pass Tier 1 under null A (day bootstrap) and 1/355 under
   null B (real order, daily sign flips). The passers were 2 RSI mean-reversion
   and 2 funding-carry draws (A) and 1 Donchian draw (B). G6 is the binding gate:
   it passes 1.9% (A) / 1.1% (B) of evaluated null pairs, while G3 (DEV Sharpe > 0)
   passes 83% / 76% - DEV selection works, it just does not carry into VAL timing.
2. A real edge is not guaranteed to pass. Noisy oracles with a known true VAL
   Sharpe of 1.5 pass Tier 1 in 80% (fast, 1-day) / 62% (slow, 20-day) of null-A
   worlds and 84% / 79% of null-B worlds. At a true Sharpe of 1.0 they pass only
   53% / 25% (A) and 56% / 37% (B). The limiting gates are G1 (PSR >= 0.90 over
   three years) and, for slow signals, G6.
3. Trading costs are material at high turnover: a 1-day oracle with no edge
   (rho = 0) averages a VAL Sharpe of -0.49 (null A) / -0.60 (null B) from costs.
4. The activity floor (40 decisions in DEV+VAL, 10 in VAL) rejects slow
   parameterisations: 55-63 of 100 best-of-20 SMA-cross draws and 61-72 of 100
   funding-carry draws failed it. On real DEV data the gen-0 SMA cross (20/100)
   makes only 16 decisions in DEV, so it needs at least 24 in VAL to pass.
5. With liquidation checked on mark price, no synthetic run liquidated in the
   final calibration (the v1 last-price rule had failed about 35% of SMA-cross
   planted pairs on one ETHUSDT wick).
6. All five gen-0 files pass stage 1 on real DEV data (determinism, lookahead on
   218-502 cuts, time-shift and scale invariance) through child processes, in
   6-11 s each.
7. The independent review showed the v1 tripwires were easy to defeat (kernel
   monkeypatching, memoised outputs, NaN columns, hardcoded dates, sparse cheats,
   exception-text leaks). All 14 reproduced against the pre-hardening kernel;
   each now has a regression test that the hardened kernel passes. The threat
   model still says plainly: tripwires, not a sandbox.
