#!/usr/bin/env python3
"""
Standalone Volume Bot
A simplified, standalone version of the volume generation bot without Docker dependencies.
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import json
import logging
from typing import Dict, Any, List, Tuple, Optional
import ccxt.async_support as ccxt
from dotenv import load_dotenv

# Import refactored modules
from constants import *
from config_validator import ConfigValidator, ConfigValidationError
from order_manager import OrderManager
from market_data import MarketDataProvider
from price_strategy import PriceStrategy

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VolumeConfig:
    """Configuration for standalone volume bot"""
    
    # Exchange Configuration
    EXCHANGE = os.getenv('EXCHANGE', DEFAULT_EXCHANGE)
    BASE_ASSET = os.getenv('BASE_ASSET', DEFAULT_BASE_ASSET)
    QUOTE_ASSET = os.getenv('QUOTE_ASSET', DEFAULT_QUOTE_ASSET)
    TRADING_PAIR = os.getenv('TRADING_PAIR', f'{BASE_ASSET}/{QUOTE_ASSET}')
    
    # Exchange API Configuration
    API_KEY = os.getenv('API_KEY', 'your_api_key_here')
    API_SECRET = os.getenv('API_SECRET', 'your_api_secret_here')
    SANDBOX_MODE = os.getenv('SANDBOX_MODE', 'false').lower() == 'true'
    
    # Bot Configuration
    DRY_RUN = os.getenv('DRY_RUN', 'true').lower() == 'true'
    
    # Volume Strategy Configuration
    TARGET_VOLUME_USDT_PER_HOUR = float(os.getenv('TARGET_VOLUME_USDT_PER_HOUR', str(DEFAULT_TARGET_VOLUME_USDT_PER_HOUR)))
    PRICE_WALK_DIRECTION = os.getenv('PRICE_WALK_DIRECTION', DEFAULT_PRICE_WALK_DIRECTION)
    MAX_PRICE_DEVIATION = float(os.getenv('MAX_PRICE_DEVIATION', str(DEFAULT_MAX_PRICE_DEVIATION)))
    ORDER_FREQUENCY = int(os.getenv('ORDER_FREQUENCY', str(DEFAULT_ORDER_FREQUENCY_SECONDS)))
    
    # Order Sizing Configuration
    MIN_ORDER_RATIO = float(os.getenv('MIN_ORDER_RATIO', str(DEFAULT_MIN_ORDER_RATIO)))
    MAX_ORDER_RATIO = float(os.getenv('MAX_ORDER_RATIO', str(DEFAULT_MAX_ORDER_RATIO)))
    SIZE_RANDOMIZATION = float(os.getenv('SIZE_RANDOMIZATION', str(DEFAULT_SIZE_RANDOMIZATION)))
    
    # Timing Configuration
    TIMING_RANDOMIZATION = float(os.getenv('TIMING_RANDOMIZATION', str(DEFAULT_TIMING_RANDOMIZATION)))
    BURST_PROBABILITY = float(os.getenv('BURST_PROBABILITY', str(DEFAULT_BURST_PROBABILITY)))
    QUIET_PROBABILITY = float(os.getenv('QUIET_PROBABILITY', str(DEFAULT_QUIET_PROBABILITY)))
    
    # Safety Configuration
    MIN_ORDER_VALUE_USDT = float(os.getenv('MIN_ORDER_VALUE_USDT', str(DEFAULT_MIN_ORDER_VALUE_USDT)))
    MAX_SPREAD_THRESHOLD = float(os.getenv('MAX_SPREAD_THRESHOLD', str(DEFAULT_MAX_SPREAD_THRESHOLD)))
    CANCEL_PREVIOUS_ORDERS = os.getenv('CANCEL_PREVIOUS_ORDERS', 'true').lower() == 'true'
    
    @classmethod
    def get_exchange_config(cls) -> Dict[str, Any]:
        """Get validated exchange configuration"""
        config = {
            'exchange': cls.EXCHANGE.lower(),
            'trading_pair': cls.TRADING_PAIR,
            'sandbox': cls.SANDBOX_MODE,
            'api_key': cls.API_KEY,
            'secret': cls.API_SECRET
        }
        
        # Validate configuration
        try:
            return ConfigValidator.validate_exchange_config(config)
        except ConfigValidationError as e:
            logger.error(f"Exchange configuration error: {e}")
            raise
    
    @classmethod
    def get_strategy_config(cls) -> Dict[str, Any]:
        """Get validated strategy configuration from environment"""
        config = {
            'target_volume_usdt_per_hour': cls.TARGET_VOLUME_USDT_PER_HOUR,
            'price_walk_direction': cls.PRICE_WALK_DIRECTION,
            'max_price_deviation': cls.MAX_PRICE_DEVIATION,
            'order_frequency': cls.ORDER_FREQUENCY,
            'min_order_ratio': cls.MIN_ORDER_RATIO,
            'max_order_ratio': cls.MAX_ORDER_RATIO,
            'size_randomization': cls.SIZE_RANDOMIZATION,
            'timing_randomization': cls.TIMING_RANDOMIZATION,
            'burst_probability': cls.BURST_PROBABILITY,
            'quiet_probability': cls.QUIET_PROBABILITY,
            'min_order_value_usdt': cls.MIN_ORDER_VALUE_USDT,
            'max_spread_threshold': cls.MAX_SPREAD_THRESHOLD,
            'cancel_previous_orders': cls.CANCEL_PREVIOUS_ORDERS
        }
        
        # Validate configuration
        try:
            return ConfigValidator.validate_strategy_config(config)
        except ConfigValidationError as e:
            logger.error(f"Strategy configuration error: {e}")
            raise
    
    @classmethod
    def validate_environment(cls) -> List[str]:
        """Validate environment variables and return warnings"""
        return ConfigValidator.validate_environment_variables()

class VolumeGenerationStrategy:
    """Standalone volume generation strategy using modular components"""
    
    def __init__(self, exchange: ccxt.Exchange, symbol: str, config: Dict = None):
        self.exchange = exchange
        self.symbol = symbol
        self.config = config or {}
        
        # Initialize modular components
        self.market_data_provider = MarketDataProvider(exchange, symbol)
        self.order_manager = OrderManager(exchange, symbol)
        self.price_strategy = PriceStrategy(
            self.config.get('price_walk_direction', DEFAULT_PRICE_WALK_DIRECTION),
            self.config.get('max_price_deviation', DEFAULT_MAX_PRICE_DEVIATION)
        )
        
        # Volume generation parameters
        self.target_volume_usdt_per_hour = self.config.get('target_volume_usdt_per_hour', DEFAULT_TARGET_VOLUME_USDT_PER_HOUR)
        self.order_frequency = self.config.get('order_frequency', DEFAULT_ORDER_FREQUENCY_SECONDS)
        
        # Order sizing parameters
        self.min_order_ratio = self.config.get('min_order_ratio', DEFAULT_MIN_ORDER_RATIO)
        self.max_order_ratio = self.config.get('max_order_ratio', DEFAULT_MAX_ORDER_RATIO)
        self.size_randomization = self.config.get('size_randomization', DEFAULT_SIZE_RANDOMIZATION)
        
        # Timing parameters
        self.timing_randomization = self.config.get('timing_randomization', DEFAULT_TIMING_RANDOMIZATION)
        self.burst_probability = self.config.get('burst_probability', DEFAULT_BURST_PROBABILITY)
        self.quiet_probability = self.config.get('quiet_probability', DEFAULT_QUIET_PROBABILITY)
        
        # Safety parameters
        self.min_order_value_usdt = self.config.get('min_order_value_usdt', DEFAULT_MIN_ORDER_VALUE_USDT)
        self.max_spread_threshold = self.config.get('max_spread_threshold', DEFAULT_MAX_SPREAD_THRESHOLD)
        self.cancel_previous_orders = self.config.get('cancel_previous_orders', True)
        
        # State tracking
        self.last_order_time = None
        self.volume_generated_today_usdt = 0.0
        self.order_count = 0
        
        logger.info(f"Volume strategy initialized: ${self.target_volume_usdt_per_hour:.2f} USDT/hour, direction={self.price_strategy.price_walk_direction}")
        logger.info(f"Order cancellation: {'enabled' if self.cancel_previous_orders else 'disabled'}")
    
    async def get_market_data(self) -> Dict:
        """Get market data for volume generation"""
        return await self.market_data_provider.get_market_data()
    
    def calculate_next_price_target(self, current_price: float) -> float:
        """Calculate the next price target based on walk direction"""
        return self.price_strategy.calculate_next_price_target(current_price)
    
    def determine_order_side(self, current_price: float, target_price: float) -> str:
        """Determine order side based on price target"""
        return self.price_strategy.determine_order_side(current_price, target_price)
    
    def calculate_order_size(self, available_balance: float, market_data: Dict, current_price: float = None) -> float:
        """Calculate order size with minimum USDT value and liquidity considerations"""
        base_ratio = np.random.uniform(self.min_order_ratio, self.max_order_ratio)
        base_size = available_balance * base_ratio
        
        randomization_factor = 1 + np.random.uniform(-self.size_randomization, self.size_randomization)
        order_size = base_size * randomization_factor
        
        # Consider liquidity using market data provider
        orderbook = market_data.get('orderbook', {})
        liquidity = self.market_data_provider.get_available_liquidity(orderbook)
        max_liquidity_size = min(liquidity['bid_volume'], liquidity['ask_volume']) * LIQUIDITY_USAGE_RATIO
        
        if max_liquidity_size > 0:
            order_size = min(order_size, max_liquidity_size)
        
        # Ensure minimum USDT order value
        if current_price and current_price > 0:
            min_size_for_usdt = self.min_order_value_usdt / current_price
            order_size = max(order_size, min_size_for_usdt)
        else:
            order_size = max(order_size, 1.0)  # Fallback minimum 1 unit
        
        return order_size
    
    def should_place_order(self) -> bool:
        """Check if it's time to place next order with timing randomization"""
        if not self.last_order_time:
            return True
        
        elapsed = (datetime.now() - self.last_order_time).total_seconds()
        base_interval = self.order_frequency
        randomized_interval = base_interval * (1 + np.random.uniform(-self.timing_randomization, self.timing_randomization))
        
        # Market regime adjustments using constants
        if np.random.random() < self.burst_probability:
            randomized_interval *= BURST_MODE_INTERVAL_MULTIPLIER
        elif np.random.random() < self.quiet_probability:
            randomized_interval *= QUIET_MODE_INTERVAL_MULTIPLIER
        
        return elapsed >= randomized_interval
    
    async def cancel_open_orders(self) -> int:
        """Cancel all open orders and return count of cancelled orders"""
        return await self.order_manager.cancel_open_orders()
    
    async def cleanup_completed_orders(self) -> int:
        """Check and remove completed orders from tracking"""
        return await self.order_manager.cleanup_completed_orders()
    
    async def should_trade(self, market_data: Dict, available_balance: float = 0.0) -> Tuple[bool, float, Dict]:
        """Determine if trade should be placed"""
        try:
            if not market_data:
                return False, 0.0, {'error': 'No market data'}
            
            if not self.should_place_order():
                return False, 0.0, {'waiting_for_timing': True}
            
            # Cancel any existing open orders before placing new one (if enabled)
            if self.cancel_previous_orders:
                await self.cancel_open_orders()
            
            ticker = market_data.get('ticker', {})
            current_price = ticker.get('last', 0)
            if current_price <= 0:
                return False, 0.0, {'error': 'Invalid current price'}
            
            target_price = self.calculate_next_price_target(current_price)
            order_side = self.determine_order_side(current_price, target_price)
            order_size = self.calculate_order_size(available_balance, market_data, current_price)
            
            # Check spread using market data provider
            orderbook = market_data.get('orderbook', {})
            spread = self.market_data_provider.calculate_spread(orderbook)
            spread_ok = spread <= self.max_spread_threshold
            confidence = 0.7 if spread_ok else 0.3
            should_place = confidence > 0.5 and spread_ok
            
            # Volume target check (now in USDT)
            volume_rate_usdt = self.volume_generated_today_usdt / max(1, (datetime.now().hour + 1))  # USDT per hour so far
            behind_target = volume_rate_usdt < self.target_volume_usdt_per_hour * 0.8  # 80% of target
            
            # Adjust confidence based on volume target
            if behind_target:
                confidence += 0.2  # Higher confidence if behind target
            
            analysis_data = {
                'current_price': current_price,
                'target_price': target_price,
                'order_side': order_side,
                'order_size': order_size,
                'order_value_usdt': order_size * current_price,
                'spread': spread,
                'spread_ok': spread_ok,
                'volume_rate_usdt': volume_rate_usdt,
                'behind_target': behind_target,
                'strategy_type': 'volume_generation'
            }
            
            if should_place:
                self.last_order_time = datetime.now()
                self.order_count += 1
                order_value_usdt = order_size * current_price
                self.volume_generated_today_usdt += order_value_usdt
            
            return should_place, confidence, analysis_data
            
        except Exception as e:
            logger.error(f"Error in trade decision: {e}")
            return False, 0.0, {'error': str(e)}

class StandaloneVolumeBot:
    """Standalone volume generation bot"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.exchange = None
        self.strategy = None
        self.running = False
        self.stats = {
            'total_orders': 0,
            'total_volume_usdt': 0.0,
            'start_time': None,
            'last_order': None
        }
    
    async def initialize_exchange(self):
        """Initialize exchange connection"""
        try:
            exchange_config = VolumeConfig.get_exchange_config()
            
            if exchange_config['exchange'] == 'gate':
                self.exchange = ccxt.gate({
                    'apiKey': exchange_config['api_key'],
                    'secret': exchange_config['secret'],
                    'sandbox': exchange_config['sandbox'],
                    'enableRateLimit': True,
                })
            else:
                raise ValueError(f"Unsupported exchange: {exchange_config['exchange']}")
            
            # Test connection
            await self.exchange.load_markets()
            logger.info(f"Connected to {exchange_config['exchange']} exchange")
            
            # Initialize strategy
            self.strategy = VolumeGenerationStrategy(
                self.exchange, 
                VolumeConfig.TRADING_PAIR, 
                self.config
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error initializing exchange: {e}")
            return False
    
    async def get_balance(self) -> float:
        """Get available balance"""
        try:
            balance = await self.exchange.fetch_balance()
            base_asset = VolumeConfig.BASE_ASSET
            return balance.get(base_asset, {}).get('free', 0.0)
        except Exception as e:
            logger.error(f"Error fetching balance: {e}")
            return 0.0
    
    async def execute_order(self, side: str, amount: float, price: float = None) -> Dict:
        """Execute order using order manager"""
        if not self.strategy:
            return {'error': 'Strategy not initialized'}
        
        return await self.strategy.order_manager.place_order(
            side, amount, price, VolumeConfig.DRY_RUN
        )
    
    async def run_volume_generation(self, duration_hours: Optional[int] = None):
        """Run volume generation for specified duration (None = infinite)"""
        if duration_hours:
            logger.info(f"Starting volume generation for {duration_hours} hours")
        else:
            logger.info("Starting infinite volume generation (Ctrl+C to stop)")
        
        self.running = True
        self.stats['start_time'] = datetime.now()
        
        end_time = datetime.now() + timedelta(hours=duration_hours) if duration_hours else None
        last_cleanup = datetime.now()
        
        while self.running and (end_time is None or datetime.now() < end_time):
            try:
                # Get market data
                market_data = await self.strategy.get_market_data()
                if not market_data:
                    await asyncio.sleep(10)
                    continue
                
                # Get balance
                balance = await self.get_balance()
                if balance <= 0:
                    logger.warning("No balance available")
                    await asyncio.sleep(60)
                    continue
                
                # Check if should trade
                should_trade, confidence, analysis = await self.strategy.should_trade(market_data, balance)
                
                if should_trade:
                    side = analysis['order_side']
                    price = analysis['current_price']
                    
                    # Apply balance limit first, then ensure minimum
                    max_balance_size = balance * MAX_BALANCE_USAGE_RATIO
                    requested_size = analysis['order_size']
                    
                    # If balance limit would make order too small, calculate minimum viable size
                    min_value = VolumeConfig.MIN_ORDER_VALUE_USDT
                    min_viable_size = min_value / price
                    
                    if max_balance_size < min_viable_size:
                        logger.warning(f"Balance too low: max {max_balance_size:.2f} tokens < min required {min_viable_size:.2f} tokens for ${min_value} USDT")
                        await asyncio.sleep(BALANCE_WARNING_WAIT)  # Wait longer for balance issues
                        continue
                    
                    # Use the larger of requested size or minimum size, but cap at balance limit
                    size = min(max(requested_size, min_viable_size), max_balance_size)
                    
                    # Final verification (should always pass now)
                    order_value_usdt = size * price
                    if order_value_usdt < min_value:
                        logger.error(f"Logic error: Order value {order_value_usdt:.2f} USDT still below minimum {min_value} USDT")
                        await asyncio.sleep(ERROR_RETRY_WAIT)
                        continue
                    
                    # Log order details before execution
                    logger.info(f"🔄 Preparing order: {side.upper()} {size:.2f} {VolumeConfig.BASE_ASSET} at {price:.8f} (${order_value_usdt:.2f} USDT)")
                    logger.info(f"📊 Current volume: ${self.stats['total_volume_usdt']:.2f} USDT | Target rate: ${VolumeConfig.TARGET_VOLUME_USDT_PER_HOUR:.2f} USDT/h")
                    
                    # Execute order
                    result = await self.execute_order(side, size, price)
                    
                    if 'error' not in result:
                        self.stats['total_orders'] += 1
                        self.stats['total_volume_usdt'] += order_value_usdt
                        self.stats['last_order'] = datetime.now()
                        
                        logger.info(f"Volume generated: ${self.stats['total_volume_usdt']:.2f} USDT")
                
                # Periodic cleanup of completed orders
                if (datetime.now() - last_cleanup).total_seconds() > ORDER_CLEANUP_INTERVAL:
                    if self.strategy:
                        await self.strategy.cleanup_completed_orders()
                    last_cleanup = datetime.now()
                
                # Wait before next check
                await asyncio.sleep(ORDER_PLACEMENT_CHECK_INTERVAL)
                
            except KeyboardInterrupt:
                logger.info("Interrupted by user")
                break
            except asyncio.CancelledError:
                logger.info("Operation cancelled by user")
                break
            except Exception as e:
                logger.error(f"Error in volume generation loop: {e}")
                await asyncio.sleep(ERROR_RETRY_WAIT)
        
        self.running = False
        
        # Final cleanup - cancel any remaining open orders
        if self.strategy and self.strategy.order_manager.get_open_order_count() > 0:
            logger.info("🧹 Final cleanup: cancelling remaining orders...")
            cancelled = await self.strategy.cancel_open_orders()
            if cancelled > 0:
                logger.info(f"✅ Cancelled {cancelled} remaining orders")
        
        logger.info("Volume generation completed")
        self.print_stats()
    
    def print_stats(self):
        """Print generation statistics"""
        if not self.stats['start_time']:
            return
        
        runtime = datetime.now() - self.stats['start_time']
        runtime_hours = runtime.total_seconds() / 3600
        
        print("\n" + "="*50)
        print("📊 VOLUME GENERATION STATISTICS")
        print("="*50)
        print(f"Runtime: {runtime}")
        print(f"Total Orders: {self.stats['total_orders']}")
        print(f"Total Volume: ${self.stats['total_volume_usdt']:.2f} USDT")
        if runtime_hours > 0:
            print(f"Volume/Hour: ${self.stats['total_volume_usdt']/runtime_hours:.2f} USDT/h")
        print(f"Last Order: {self.stats['last_order']}")
        print(f"Dry Run Mode: {'✅' if VolumeConfig.DRY_RUN else '❌'}")
        print("="*50)
    
    async def close(self):
        """Close exchange connection"""
        if self.exchange:
            await self.exchange.close()

async def main():
    """Main function"""
    print("🤖 Standalone Volume Bot")
    print("="*40)
    
    # Validate environment variables and show warnings
    warnings = VolumeConfig.validate_environment()
    if warnings:
        print("⚠️  Configuration Warnings:")
        for warning in warnings:
            print(f"   - {warning}")
        print()
    
    # Get configuration from environment  
    try:
        volume_config = VolumeConfig.get_strategy_config()
    except ConfigValidationError as e:
        print(f"❌ Configuration Error: {e}")
        return
    
    print(f"Exchange: {VolumeConfig.EXCHANGE}")
    print(f"Trading Pair: {VolumeConfig.TRADING_PAIR}")
    print(f"Target Volume: ${volume_config['target_volume_usdt_per_hour']:.2f} USDT/hour")
    print(f"Price Direction: {volume_config['price_walk_direction']}")
    print(f"Order Frequency: {volume_config['order_frequency']}s")
    print(f"Dry Run: {'✅' if VolumeConfig.DRY_RUN else '❌'}")
    print()
    
    # Initialize bot
    bot = StandaloneVolumeBot(volume_config)
    
    try:
        # Initialize exchange
        if not await bot.initialize_exchange():
            print("❌ Failed to initialize exchange")
            return
        
        print("✅ Exchange initialized successfully")
        
        # Run volume generation infinitely
        await bot.run_volume_generation()
        
    except KeyboardInterrupt:
        print("\n⏹️  Stopping bot...")
    except asyncio.CancelledError:
        print("\n⏹️  Bot operation cancelled")
    except Exception as e:
        logger.error(f"Error running bot: {e}")
    finally:
        await bot.close()
        print("👋 Bot stopped")

if __name__ == "__main__":
    asyncio.run(main())