"""CONSTITUTION v1 constants (perps, formula language). Kernel module.

Every number the evaluator uses lives here, except the G6 threshold, which is set by the
calibration rule and written into kernel.lock by `python -m omr.kernel_lock seal`. Changing any
of these is a kernel change and needs a human-approved re-key.
"""

# Trial identity uses the SEMANTIC kernel hash (omr/** and requirements.txt; omr.kernel_lock), so any
# change to the code or constants that run changes every trial id.

# ---------------------------------------------------------------- universe
# USDT-margined linear perpetuals (Binance USD-M). Engine and evaluator read
# these lists; neither hardcodes a symbol or a universe size.
CORE = ("BTCUSDT", "ETHUSDT")
EXTENDED = ("SOLUSDT", "BNBUSDT", "XRPUSDT", "ADAUSDT",
            "DOGEUSDT", "LTCUSDT", "LINKUSDT", "AVAXUSDT")
ALL_SYMBOLS = CORE + EXTENDED
BTC = "BTCUSDT"

# ---------------------------------------------------------------- regions
# Bar OPEN times, UTC, inclusive. Bars before DEV_START are warm-up input only.
DEV_START = "2020-01-01 00:00"
DEV_END = "2022-06-30 23:00"
VAL_START = "2022-07-01 00:00"
VAL_END = "2025-06-30 23:00"
VAULT_START = "2025-07-01 00:00"
# VAULT_END = last complete hour of the build snapshot (fixed at build time).
VAULT_END = "2026-11-18 09:00"

BAR = "1h"

# ---------------------------------------------------------------- engine
FEE_PER_SIDE = 0.00055        # 5.5 bps taker
SLIPPAGE_PER_SIDE = 0.0002    # 2 bps
COST_RATE = FEE_PER_SIDE + SLIPPAGE_PER_SIDE   # 7.5 bps per side on traded notional
COST_STRESS_MULT = 2.0
REBALANCE_BAND = 0.01         # rebalance ALL when any |target - drifted| > band
LIQUIDATION_FRAC = 0.025      # worst intrabar equity <= 2.5% of gross notional -> liquidation
FUNDING_STRESS_PAY = 1.5      # G2: funding paid x1.5
FUNDING_STRESS_RECV = 0.5     # G2: funding received x0.5
DEPLOY_RISK_BUDGET = 0.20     # deploy_scale = min(1, 0.20 / maxDD(DEV+VAL))

# ---------------------------------------------------------------- statistics
PERIODS_PER_YEAR = 365        # daily returns, calendar days
EULER_GAMMA = 0.5772156649

# ---------------------------------------------------------------- stage 1 (uncounted)
TRUNCATION_CUTS = 24          # random cuts for the program truncation self-check (plus DEV end)
START_CUTS_DEV = 6            # stage 1: start cuts over the first START_CUT_SPAN of the DEV frame
START_CUT_SPAN = 0.6
START_CUTS_VAL = 3            # stage 2: start cuts on the full frame (first START_CUT_SPAN_VAL of it)
START_CUT_SPAN_VAL = 0.9
# finite memory of the recursive functions (rows of memory per unit of n; LANGUAGE.md section 6)
EMA_MEMORY = 5
RSI_MEMORY = 10
ATR_MEMORY = 10
# mark_close = close of the last mark bar at or before the row, known while that bar is at most this old
MARK_MAX_STALE_HOURS = 6
# constant probe: jitter draws (literals and non-window params) that may move a constant node
PROBE_JITTER_DRAWS = 3
PROBE_JITTER_SEED = 20261120
DIRECTION_TOL = 0.01          # |weight| above this has a direction (sign); otherwise flat
MIN_DIRECTION_CHANGES_DEV = 20    # stage 1: activity_dev
MAX_COUNTED_PER_GENERATION = 5

# ---------------------------------------------------------------- gates
G1_PSR_MIN = 0.90
JITTER_N = 12
JITTER_LO = 0.8
JITTER_HI = 1.2
JITTER_MEDIAN_FRAC = 0.5
JITTER_POSITIVE_FRAC = 0.75
PERM_N = 200
PERM_MIN_OFFSET_DAYS = 30
G7_BUCKETS = (
    ("2020", "2020-01-01 00:00", "2020-12-31 23:00"),
    ("2021", "2021-01-01 00:00", "2021-12-31 23:00"),
    ("2022", "2022-01-01 00:00", "2022-12-31 23:00"),
    ("2023", "2023-01-01 00:00", "2023-12-31 23:00"),
    ("2024", "2024-01-01 00:00", "2024-12-31 23:00"),
    ("2025H1", "2025-01-01 00:00", "2025-06-30 23:00"),
)
G7_MIN_POSITIVE = 4
G7_MAX_SHARE = 0.5
G8_MIN_YEARS = 2.0
G10_MIN_DIRECTION_CHANGES_VAL = 12
MAX_PARAMS = 6

# ---------------------------------------------------------------- calibration rule (applied by the seal)
G6_GRID = (0.025, 0.05, 0.10)
NULL_PASS_MAX = 0.03          # per SUBMITTED pair, under BOTH nulls
POWER_MIN = 0.50              # oracle power at true Sharpe 1.5, both speeds, both nulls

# ---------------------------------------------------------------- pool
POOL_MAX = 5

# ---------------------------------------------------------------- universe units (KP-015)
# Header `unit`: "core" (default; the two-coin unit above, unchanged) or "top30" (kind portfolio).
UNITS = ("core", "top30")
UNIVERSE_START = "2019-12-31 00:00"     # first hour of every universe panel: one day before DEV start (the
                                        # first DEV bar needs a decision row); membership is known from the
                                        # first month at least 97 days later
UNIVERSE_SEASONING_DAYS = 90            # B2: first active bar at least this many days before the month
UNIVERSE_RELIST_GAP_DAYS = 7            # R1a: 7+ consecutive days without an active bar inside those 90 days
                                        # restart the seasoning (a relisting); a shorter hole does not
UNIVERSE_ACTIVE_DAYS = 30               # B2: activity measured over the previous 30 days ...
UNIVERSE_ACTIVE_FRAC = 0.95             # ... active on at least 95% of those hours
UNIVERSE_LIQ_DAYS = 90                  # B3: median daily quote volume over the previous 90 days
UNIVERSE_TOP = 30                       # top30 = ranks 1-30, next30 = ranks 31-60
UNIVERSE_MIN_MEMBERS = 10               # fewer eligible members -> no unit that month (programs flat)
UNIVERSE_MIN_CS = 10                    # S2: a cs_ result needs >= 10 in-play symbols with a known input
UNIVERSE_ZERO_TRADE_MAX = 24            # S3: a zero-trade bar is usable while its zero-trade run is <= 24
UNIVERSE_BLOCK_MONTHS = 6               # S4: universe units are evaluated in blocks of 6 calendar months
UNIVERSE_BLOCK_MONTHS_G8 = 3            # G8's next30 blocks (evaluated once, streamed): 3 calendar months
UNIVERSE_COST_RATE = 0.00055 + 0.0007   # C2: 12.5 bps per side on every symbol of top30 / next30
LOOKBACK_MAX_HOURS = UNIVERSE_SEASONING_DAYS * 24   # D3: a top30 program's total lookback limit
INDEX_MAX_STALE_HOURS = 6               # index_close: known while its index bar is at most this old
DOWNLOAD_PAUSE_S = 0.05                 # pause after every archive request (per worker)
