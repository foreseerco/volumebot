"""
Configuration validation for the standalone volume bot
"""

import os
from typing import Dict, Any, List, Optional
from constants import *


class ConfigValidationError(Exception):
    """Custom exception for configuration validation errors"""
    pass


class ConfigValidator:
    """Validates and normalizes configuration for the volume bot"""
    
    @staticmethod
    def validate_exchange_config(config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate exchange configuration"""
        exchange = config.get('exchange', '').lower()
        
        if not exchange:
            raise ConfigValidationError("Exchange must be specified")
        
        if exchange not in SUPPORTED_EXCHANGES:
            raise ConfigValidationError(f"Unsupported exchange: {exchange}. Supported: {SUPPORTED_EXCHANGES}")
        
        if not config.get('api_key'):
            raise ConfigValidationError("API key is required")
        
        if not config.get('secret'):
            raise ConfigValidationError("API secret is required")
        
        if not config.get('trading_pair'):
            raise ConfigValidationError("Trading pair is required")
        
        return config
    
    @staticmethod
    def validate_strategy_config(config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and normalize strategy configuration"""
        validated = {}
        
        # Target volume validation
        target_volume = config.get('target_volume_usdt_per_hour', DEFAULT_TARGET_VOLUME_USDT_PER_HOUR)
        if target_volume <= 0:
            raise ConfigValidationError("Target volume must be positive")
        validated['target_volume_usdt_per_hour'] = float(target_volume)
        
        # Price walk direction validation
        direction = config.get('price_walk_direction', DEFAULT_PRICE_WALK_DIRECTION)
        if direction not in PRICE_WALK_DIRECTIONS:
            raise ConfigValidationError(f"Invalid price walk direction: {direction}. Must be one of {PRICE_WALK_DIRECTIONS}")
        validated['price_walk_direction'] = direction
        
        # Price deviation validation
        max_deviation = config.get('max_price_deviation', DEFAULT_MAX_PRICE_DEVIATION)
        if not (0 < max_deviation <= 0.1):  # Max 10% deviation
            raise ConfigValidationError("Max price deviation must be between 0 and 0.1 (10%)")
        validated['max_price_deviation'] = float(max_deviation)
        
        # Order frequency validation
        frequency = config.get('order_frequency', DEFAULT_ORDER_FREQUENCY_SECONDS)
        if frequency < 1:
            raise ConfigValidationError("Order frequency must be at least 1 second")
        validated['order_frequency'] = int(frequency)
        
        # Order ratio validations
        min_ratio = config.get('min_order_ratio', DEFAULT_MIN_ORDER_RATIO)
        max_ratio = config.get('max_order_ratio', DEFAULT_MAX_ORDER_RATIO)
        
        if not (0 < min_ratio <= 1):
            raise ConfigValidationError("Min order ratio must be between 0 and 1")
        if not (0 < max_ratio <= 1):
            raise ConfigValidationError("Max order ratio must be between 0 and 1")
        if min_ratio >= max_ratio:
            raise ConfigValidationError("Min order ratio must be less than max order ratio")
        
        validated['min_order_ratio'] = float(min_ratio)
        validated['max_order_ratio'] = float(max_ratio)
        
        # Randomization factor validations
        size_rand = config.get('size_randomization', DEFAULT_SIZE_RANDOMIZATION)
        timing_rand = config.get('timing_randomization', DEFAULT_TIMING_RANDOMIZATION)
        
        if not (0 <= size_rand <= 1):
            raise ConfigValidationError("Size randomization must be between 0 and 1")
        if not (0 <= timing_rand <= 1):
            raise ConfigValidationError("Timing randomization must be between 0 and 1")
        
        validated['size_randomization'] = float(size_rand)
        validated['timing_randomization'] = float(timing_rand)
        
        # Probability validations
        burst_prob = config.get('burst_probability', DEFAULT_BURST_PROBABILITY)
        quiet_prob = config.get('quiet_probability', DEFAULT_QUIET_PROBABILITY)
        
        if not (0 <= burst_prob <= 1):
            raise ConfigValidationError("Burst probability must be between 0 and 1")
        if not (0 <= quiet_prob <= 1):
            raise ConfigValidationError("Quiet probability must be between 0 and 1")
        
        validated['burst_probability'] = float(burst_prob)
        validated['quiet_probability'] = float(quiet_prob)
        
        # Minimum order value validation
        min_value = config.get('min_order_value_usdt', DEFAULT_MIN_ORDER_VALUE_USDT)
        if min_value <= 0:
            raise ConfigValidationError("Minimum order value must be positive")
        validated['min_order_value_usdt'] = float(min_value)
        
        # Spread threshold validation
        spread_threshold = config.get('max_spread_threshold', DEFAULT_MAX_SPREAD_THRESHOLD)
        if not (0 < spread_threshold <= 1):
            raise ConfigValidationError("Max spread threshold must be between 0 and 1")
        validated['max_spread_threshold'] = float(spread_threshold)
        
        # Boolean settings
        validated['cancel_previous_orders'] = config.get('cancel_previous_orders', True)
        
        return validated
    
    @staticmethod
    def validate_environment_variables() -> List[str]:
        """Validate required environment variables and return warnings"""
        warnings = []
        
        required_vars = ['API_KEY', 'API_SECRET']
        for var in required_vars:
            if not os.getenv(var):
                warnings.append(f"Environment variable {var} is not set")
        
        # Check for default placeholder values
        api_key = os.getenv('API_KEY', '')
        if 'your_api_key_here' in api_key:
            warnings.append("API_KEY appears to be a placeholder value")
        
        api_secret = os.getenv('API_SECRET', '')
        if 'your_api_secret_here' in api_secret:
            warnings.append("API_SECRET appears to be a placeholder value")
        
        return warnings