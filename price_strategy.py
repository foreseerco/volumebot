"""
Price calculation strategies for the standalone volume bot
"""

import numpy as np
import logging
from typing import Dict
from constants import (
    BASE_PRICE_STEP_RATIO,
    PRICE_RANDOMIZATION_FACTOR,
    ORDER_SIDE_ALTERNATE_PROBABILITY,
    PRICE_ADJUSTMENT_PROBABILITY
)

logger = logging.getLogger(__name__)


class PriceStrategy:
    """Handles price target calculation and order side determination"""
    
    def __init__(self, price_walk_direction: str, max_price_deviation: float):
        self.price_walk_direction = price_walk_direction
        self.max_price_deviation = max_price_deviation
        self.price_walk_step = 0
        self.last_order_side = None
    
    def calculate_next_price_target(self, current_price: float) -> float:
        """Calculate the next price target based on walk direction"""
        try:
            base_step = current_price * BASE_PRICE_STEP_RATIO
            randomization = np.random.uniform(-PRICE_RANDOMIZATION_FACTOR, PRICE_RANDOMIZATION_FACTOR) * base_step
            
            if self.price_walk_direction == 'up':
                step = base_step * (1 + np.random.uniform(0, 1)) + randomization
                target_price = current_price + step
            elif self.price_walk_direction == 'down':
                step = base_step * (1 + np.random.uniform(0, 1)) + randomization
                target_price = current_price - step
            elif self.price_walk_direction == 'sideways':
                amplitude = base_step * 2
                self.price_walk_step += np.random.uniform(0.1, 0.3)
                oscillation = amplitude * np.sin(self.price_walk_step) + randomization
                target_price = current_price + oscillation
            else:  # random
                direction = np.random.choice([-1, 1])
                step = base_step * np.random.uniform(0.5, 2.0) * direction + randomization
                target_price = current_price + step
            
            # Clamp to deviation limits
            max_price = current_price * (1 + self.max_price_deviation)
            min_price = current_price * (1 - self.max_price_deviation)
            target_price = np.clip(target_price, min_price, max_price)
            
            return target_price
        except Exception as e:
            logger.error(f"Error calculating price target: {e}")
            return current_price
    
    def determine_order_side(self, current_price: float, target_price: float) -> str:
        """Determine order side based on price target and alternation strategy"""
        if self.last_order_side is None:
            side = np.random.choice(['buy', 'sell'])
        else:
            # High probability to alternate
            if np.random.random() < ORDER_SIDE_ALTERNATE_PROBABILITY:
                side = 'sell' if self.last_order_side == 'buy' else 'buy'
            else:
                side = self.last_order_side
        
        # Adjust based on price target
        if target_price > current_price and side == 'sell':
            if np.random.random() < PRICE_ADJUSTMENT_PROBABILITY:
                side = 'buy'
        elif target_price < current_price and side == 'buy':
            if np.random.random() < PRICE_ADJUSTMENT_PROBABILITY:
                side = 'sell'
        
        self.last_order_side = side
        return side