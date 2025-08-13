"""
Order management for the standalone volume bot
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
import ccxt.async_support as ccxt
from constants import COMPLETED_ORDER_STATUSES

logger = logging.getLogger(__name__)


class OrderManager:
    """Manages order placement, tracking, and cleanup"""
    
    def __init__(self, exchange: ccxt.Exchange, symbol: str):
        self.exchange = exchange
        self.symbol = symbol
        self.open_orders: List[str] = []
    
    async def place_order(self, side: str, amount: float, price: float = None, dry_run: bool = True) -> Dict:
        """Place a limit or market order"""
        try:
            order_value_usdt = amount * price if price else 0
            
            if dry_run:
                logger.info(f"[DRY RUN] {side.upper()} {amount:.2f} at {price:.8f} (${order_value_usdt:.2f} USDT)")
                return {
                    'id': f'dry_run_{datetime.now().timestamp()}',
                    'symbol': self.symbol,
                    'side': side,
                    'amount': amount,
                    'price': price,
                    'value_usdt': order_value_usdt,
                    'status': 'closed',
                    'dry_run': True
                }
            else:
                if price:
                    order = await self.exchange.create_limit_order(self.symbol, side, amount, price)
                else:
                    order = await self.exchange.create_market_order(self.symbol, side, amount)
                
                # Track order ID for cancellation
                if order.get('id'):
                    self.open_orders.append(order['id'])
                    logger.info(f"📝 Tracking order {order['id']}")
                
                logger.info(f"Order executed: {side.upper()} {amount:.2f} at {price:.8f} (${order_value_usdt:.2f} USDT)")
                return order
                
        except Exception as e:
            logger.error(f"Error executing order: {e}")
            return {'error': str(e)}
    
    async def cancel_open_orders(self) -> int:
        """Cancel all open orders and return count of cancelled orders"""
        cancelled_count = 0
        
        if not self.open_orders:
            return cancelled_count
            
        logger.info(f"🚫 Cancelling {len(self.open_orders)} open orders...")
        
        orders_to_remove = []
        for order_id in self.open_orders[:]:
            try:
                await self.exchange.cancel_order(order_id, self.symbol)
                logger.info(f"✅ Cancelled order {order_id}")
                cancelled_count += 1
                orders_to_remove.append(order_id)
            except Exception as e:
                if 'not found' in str(e).lower() or 'already' in str(e).lower():
                    logger.info(f"📋 Order {order_id} already completed")
                    orders_to_remove.append(order_id)
                else:
                    logger.warning(f"❌ Failed to cancel order {order_id}: {e}")
        
        # Remove processed orders from tracking
        for order_id in orders_to_remove:
            if order_id in self.open_orders:
                self.open_orders.remove(order_id)
        
        if cancelled_count > 0:
            logger.info(f"🔄 Cancelled {cancelled_count} orders, {len(self.open_orders)} remaining")
        
        return cancelled_count
    
    async def cleanup_completed_orders(self) -> int:
        """Check and remove completed orders from tracking"""
        if not self.open_orders:
            return 0
            
        completed_count = 0
        orders_to_remove = []
        
        for order_id in self.open_orders[:]:
            try:
                order_status = await self.exchange.fetch_order(order_id, self.symbol)
                if order_status['status'] in COMPLETED_ORDER_STATUSES:
                    orders_to_remove.append(order_id)
                    completed_count += 1
                    logger.info(f"📋 Order {order_id} completed with status: {order_status['status']}")
            except Exception as e:
                if 'not found' in str(e).lower():
                    orders_to_remove.append(order_id)
                    completed_count += 1
                    logger.info(f"📋 Order {order_id} not found (likely completed)")
        
        # Remove completed orders from tracking
        for order_id in orders_to_remove:
            if order_id in self.open_orders:
                self.open_orders.remove(order_id)
        
        if completed_count > 0:
            logger.info(f"🧹 Cleaned up {completed_count} completed orders")
        
        return completed_count
    
    def get_open_order_count(self) -> int:
        """Get the number of open orders being tracked"""
        return len(self.open_orders)