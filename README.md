# Oplan Make me Rich - perpetual-futures research kernel v1 (formula language)

A research system that tests trading-strategy ideas on Binance USDT-margined perpetual futures
(BTCUSDT and ETHUSDT, with eight other perps used only to veto) and reports, as honestly as it can,
whether an idea has an edge. It is built to make "no edge" the easy answer.

It does not trade. There are no exchange keys and no order code in this build.

## Layout

| path | what | who may change it |
|---|---|---|
| `omr/` | kernel: data, language (parser + interpreter), engine, statistics, evaluator, ledger, calibration, selftest, pool, census | re-key only |
| `omr/programs/` | kernel programs: the five baselines (calibration families), the kitchen-sink and two noise programs (selftest) | re-key only |
| `tests/` | kernel tests (incl. the trusted Python reference baselines `tests/ref_gen0.py`) | re-key only |
| `CONSTITUTION.md`, `LANGUAGE.md` | the rules and the strategy language | re-key only |
| `requirements.txt` | exact pins of every package and the Python version | re-key only |
| `strategies/` | strategy programs (`.omr`) | research loop |
| `generations/` | per-generation PLAN.md and REPORT.md | research loop |
| `LESSONS.md`, `STATE.md`, `RESEARCH_PLAYBOOK.md`, `KERNEL_PROPOSALS.md` | research notes and protocol | research loop |
| `ledger/` | trials, stage-1 log, returns, pool, census, calibration, kernel history, VAL access log | kernel commands only |
| `data/` | stored market data, manifest, validation counts | `omr.data` only |
| `kernel.lock` | kernel file hashes and the calibration seal | `omr.kernel_lock` only |
| `archive/` | the retired Python-sandbox kernel (2317921c), for the record | - |

## Commands

Run from the project root with the venv interpreter, e.g. `.venv\Scripts\python.exe -m omr.status`.

    python -m omr.status                            kernel + seal, data, trial counts (M, N, rho), pool, census
    python -m omr.sandbox <prog.omr> [--set k=v]    DEV-only exploration with the stage-1 checks, not a trial
    python -m omr.evaluate <prog.omr> --generation N stage 1 (DEV, uncounted) then a counted trial (VAL)
    python -m omr.ledger verify | summary           hash chains and file hashes / trial list
    python -m omr.pool list | admit | remove        paper pool (max 5, Tier 1 only)
    python -m omr.census                            update data, forward results of pool members
    python -m omr.selftest                          prints OK or the failed assertion (the one VAL exception)
    python -m omr.calibrate                         instrument calibration on the LOCKED kernel
    python -m omr.kernel_lock verify | hash | rekey | seal --calibration FILE
    python -m omr.data download | update [--admit NAME] | verify | validate | summary
    python -m pytest tests -q

Setup on a new machine: create a Python 3.12.6 venv, `pip install -r requirements.txt`, put a file
`omr_no_bytecode.pth` containing `import sys; sys.dont_write_bytecode = True` into the venv's
site-packages (the lock fails on any `__pycache__` under `omr/` or `tests/`), then
`python -m omr.data download` and `python -m omr.data validate`.

## How a strategy is run

It is not run. A strategy is a `.omr` program in a small formula language (LANGUAGE.md): headers,
up to 6 params, and `name = expression` lines over price/volume/funding fields, timeframes and a
fixed set of causal functions, ending in `signal = ...`. The kernel parses the text with its own
checker (types, units, limits) and evaluates it with its own interpreter; no strategy code is
compiled, executed or imported. The evaluator runs an uncounted DEV-only stage first, then writes a
counted `pending` ledger row, and only then reads VAL bars. See CONSTITUTION sections 2 and 6.

## Honest expectations

- Most strategies will fail. The gates are set so that a strategy with no real edge passes rarely;
  that also means many weak real edges fail.
- Every backtest here, the vault included, is optimistic: the language model that writes programs
  has read about this market history. Only forward results, measured after a program is frozen,
  are clean.
- A Tier-1 pass means "worth paper-trading", nothing more. Nothing here implies profit.
- Nothing here trades real money. The live requirements in CONSTITUTION section 11 are written down,
  not implemented.
