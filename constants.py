"""
Constants for the standalone volume bot
"""

# Default configuration values
DEFAULT_TARGET_VOLUME_USDT_PER_HOUR = 100.0
DEFAULT_MAX_PRICE_DEVIATION = 0.01
DEFAULT_ORDER_FREQUENCY_SECONDS = 60
DEFAULT_MIN_ORDER_RATIO = 0.001
DEFAULT_MAX_ORDER_RATIO = 0.005
DEFAULT_SIZE_RANDOMIZATION = 0.3
DEFAULT_TIMING_RANDOMIZATION = 0.5
DEFAULT_BURST_PROBABILITY = 0.05
DEFAULT_QUIET_PROBABILITY = 0.15
DEFAULT_MIN_ORDER_VALUE_USDT = 5.0
DEFAULT_MAX_SPREAD_THRESHOLD = 0.05

# Order and balance limits
MAX_BALANCE_USAGE_RATIO = 0.1  # Max 10% of balance per order
ORDER_SIDE_ALTERNATE_PROBABILITY = 0.8  # 80% chance to alternate order sides

# Price calculation factors
BASE_PRICE_STEP_RATIO = 0.001  # 0.1% of current price as base step
PRICE_RANDOMIZATION_FACTOR = 0.5

# Market making parameters
LIQUIDITY_USAGE_RATIO = 0.5  # Use max 50% of available liquidity
PRICE_ADJUSTMENT_PROBABILITY = 0.7  # 70% chance to adjust side based on price target

# Timing and cleanup intervals
ORDER_PLACEMENT_CHECK_INTERVAL = 5  # seconds
ORDER_CLEANUP_INTERVAL = 300  # 5 minutes
BALANCE_WARNING_WAIT = 30  # seconds to wait when balance is low
ERROR_RETRY_WAIT = 30  # seconds to wait after errors

# Market regime multipliers
BURST_MODE_INTERVAL_MULTIPLIER = 0.3
QUIET_MODE_INTERVAL_MULTIPLIER = 3.0

# Order status tracking
COMPLETED_ORDER_STATUSES = ['closed', 'filled', 'canceled']

# Exchange configuration
SUPPORTED_EXCHANGES = ['binance', 'gate']
DEFAULT_EXCHANGE = 'binance'
DEFAULT_BASE_ASSET = 'ETH'
DEFAULT_QUOTE_ASSET = 'USDT'

# Price walk directions
PRICE_WALK_DIRECTIONS = ['up', 'down', 'sideways', 'random']
DEFAULT_PRICE_WALK_DIRECTION = 'sideways'