# Volume Bot

A professional-grade volume generation bot for cryptocurrency exchanges. Supports both standalone Python execution and containerized Docker deployment.

## Features

- **Flexible Deployment**: Runs as standalone Python application or Docker container
- **Professional Volume Generation**: Creates realistic trading volume through intelligent order placement
- **Advanced Price Strategies**: Supports upward, downward, sideways, and random price movements with sophisticated algorithms
- **Comprehensive Safety**: Multiple safeguards including dry-run mode, position limits, and spread monitoring
- **Production Ready**: Fully containerized with health checks, monitoring, and resource management
- **Modular Architecture**: Clean, maintainable codebase with comprehensive validation and error handling
- **Multi-Exchange Support**: Compatible with CCXT-supported exchanges

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and update with your API credentials:

```bash
cp .env.example .env
```

Edit `.env` with your exchange credentials:
```
API_KEY=your_actual_api_key
API_SECRET=your_actual_secret_key
EXCHANGE=binance  # or 'gate'
DRY_RUN=true      # Set to false for real trading
```

### 3. Run the Bot

#### Option A: Direct Python Execution
```bash
# Run main bot
python main.py

# Or run example strategies
python run_example.py
```

#### Option B: Docker (Recommended for Production)
```bash
# Build and run with docker-compose
docker-compose up --build

# Or run with regular Docker
docker build -t volume-bot .
docker run --env-file .env volume-bot
```

## Example Strategies

The `run_example.py` file provides pre-configured strategies:

1. **Conservative Volume** - Low market impact, $50 USDT/hour
2. **Moderate Volume** - Balanced approach, $100 USDT/hour  
3. **Aggressive Volume** - High market impact, $200 USDT/hour
4. **Upward Trend** - Gradual price increase, $150 USDT/hour
5. **Market Making** - Tight spread simulation, $80 USDT/hour

```bash
python run_example.py
# Select strategy from interactive menu
```

## Configuration

The bot supports various configuration options:

### Volume Parameters
- `target_volume_per_hour`: Target volume to generate per hour
- `price_walk_direction`: Direction of price movement ('up', 'down', 'sideways', 'random')
- `max_price_deviation`: Maximum price deviation (default: 1%)

### Order Parameters  
- `order_frequency`: Seconds between orders (default: 60)
- `min_order_ratio`: Minimum order size as ratio of balance (default: 0.1%)
- `max_order_ratio`: Maximum order size as ratio of balance (default: 0.5%)

### Safety Parameters
- `DRY_RUN`: Enable dry run mode (default: true)
- Built-in spread checking (max 5%)
- Position size limits
- Timing randomization
- **Order Management**: Automatic cancellation of previous orders to prevent pile-up

## Example Configurations

### Conservative Volume (Low Impact)
```python
volume_config = {
    'target_volume_per_hour': 500,
    'price_walk_direction': 'sideways',
    'max_price_deviation': 0.005,  # 0.5%
    'order_frequency': 120,         # 2 minutes
    'min_order_ratio': 0.001,      # 0.1%
    'max_order_ratio': 0.003       # 0.3%
}
```

### Moderate Volume (Balanced)
```python
volume_config = {
    'target_volume_per_hour': 1000,
    'price_walk_direction': 'sideways',
    'max_price_deviation': 0.01,   # 1%
    'order_frequency': 60,          # 1 minute
    'min_order_ratio': 0.001,      # 0.1%
    'max_order_ratio': 0.005       # 0.5%
}
```

### Aggressive Volume (High Impact)
```python
volume_config = {
    'target_volume_per_hour': 2000,
    'price_walk_direction': 'random',
    'max_price_deviation': 0.02,   # 2%
    'order_frequency': 30,          # 30 seconds
    'min_order_ratio': 0.002,      # 0.2%
    'max_order_ratio': 0.008       # 0.8%
}
```

## Safety Features

- **Dry Run Mode**: Test strategies without real money
- **Spread Monitoring**: Stops trading if spread > 5%
- **Position Limits**: Maximum 10% of balance per order
- **Error Handling**: Graceful error recovery
- **Logging**: Comprehensive operation logging
- **Order Management**: Prevents order pile-up by cancelling previous orders

## Order Management

The bot includes intelligent order management to prevent unnecessary order accumulation:

### Features:
- **Auto-cancellation**: Cancels previous orders before placing new ones (configurable)
- **Order tracking**: Tracks all open orders for proper cleanup
- **Periodic cleanup**: Automatically removes completed orders from tracking (every 5 minutes)
- **Final cleanup**: Cancels all remaining orders when bot stops

### Configuration:
```env
CANCEL_PREVIOUS_ORDERS=true  # Enable auto-cancellation (default: true)
```

### Behavior:
- **Enabled**: Each new order cancels previous unfilled orders
- **Disabled**: Orders accumulate naturally (may pile up)
- **Dry Run**: Order tracking works but no real cancellations occur

## Architecture (Post-Refactoring)

The codebase has been refactored into modular components:

### Core Modules:
- **`constants.py`**: All configuration constants and default values
- **`config_validator.py`**: Configuration validation and error handling
- **`order_manager.py`**: Order placement, tracking, and cleanup
- **`market_data.py`**: Market data fetching and analysis  
- **`price_strategy.py`**: Price target calculation and order side logic
- **`main.py`**: Main orchestration and bot logic
- **`run_example.py`**: Example configurations and strategy templates

### Benefits:
- **Modularity**: Each component has a single responsibility
- **Testability**: Components can be tested independently
- **Maintainability**: Easier to modify and extend functionality
- **Validation**: Comprehensive configuration validation with helpful error messages
- **Consistency**: Standardized error handling and logging patterns

## Docker Deployment

The bot is fully dockerized for easy deployment and isolation.

### Docker Features:
- **Multi-stage build** for optimized image size
- **Non-root user** for enhanced security
- **Health checks** for container monitoring
- **Resource limits** to prevent resource exhaustion
- **Volume mounting** for persistent logs
- **Environment-based configuration**

### Quick Docker Start:
```bash
# 1. Copy and configure environment
cp .env.example .env
# Edit .env with your settings

# 2. Build and run
docker-compose up --build

# 3. Run in background
docker-compose up -d

# 4. View logs
docker-compose logs -f

# 5. Stop
docker-compose down
```

### Docker Commands:
```bash
# Build image
docker build -t volume-bot .

# Run with environment file
docker run --env-file .env volume-bot

# Run with individual environment variables
docker run -e API_KEY=your_key -e API_SECRET=your_secret volume-bot

# Run in background with restart policy
docker run -d --restart unless-stopped --env-file .env volume-bot

# View container logs
docker logs volume-bot
```

### Docker Environment Variables:
All configuration can be set via environment variables. See `.env.example` for a complete list.

## Project Structure

```
volume-bot/
├── main.py                    # Main bot application
├── run_example.py            # Example strategy configurations
├── constants.py              # Configuration constants
├── config_validator.py       # Configuration validation
├── order_manager.py          # Order management and tracking
├── market_data.py           # Market data fetching
├── price_strategy.py        # Price calculation strategies
├── requirements.txt         # Python dependencies
├── .env.example            # Environment template
├── .gitignore             # Git ignore rules
├── Dockerfile             # Docker container definition
├── docker-compose.yml     # Docker orchestration
├── docker-entrypoint.sh   # Docker startup script
├── test-docker-setup.py   # Docker validation tests
└── README.md              # This file
```

## Supported Exchanges

Currently supports:
- Binance (primary)
- Gate.io (tested)
- Other CCXT exchanges (may require minor adjustments)

## ⚠️ DISCLAIMER AND RISK WARNING

**FOR EDUCATIONAL AND TESTING PURPOSES ONLY**

This software is provided for educational and testing purposes only. It is not intended for production trading or commercial use.

### **No Liability**
The authors and contributors of this software are **NOT RESPONSIBLE** for any financial losses, damages, or other consequences that may result from using this software. Use at your own risk.

### **Professional Market Making Services**
For comprehensive, production-ready market making services, please contact us at **contact@foreseer.co**

### **Important Safety Guidelines**
- Always start with `DRY_RUN=true`
- Use small amounts when testing with real funds
- Understand market impact of volume generation
- Comply with exchange terms of service
- Consider regulatory implications
- Never use with funds you cannot afford to lose

## Monitoring

The bot provides real-time statistics:
- Total orders executed
- Volume generated
- Runtime statistics  
- Order success rate

## Stopping the Bot

Press `Ctrl+C` to gracefully stop the bot. It will:
- Complete current operations
- Display final statistics
- Close exchange connections properly

## Donations

If you find this project helpful, consider supporting development:

**Ethereum/BSC/Polygon:** `0xE4C92f5614CCfE84e4DB57a86e5147805d928046`