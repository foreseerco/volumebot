"""
Market data fetching and analysis for the standalone volume bot
"""

import logging
from datetime import datetime
from typing import Dict, Optional
import ccxt.async_support as ccxt

logger = logging.getLogger(__name__)


class MarketDataProvider:
    """Provides market data and analysis"""
    
    def __init__(self, exchange: ccxt.Exchange, symbol: str):
        self.exchange = exchange
        self.symbol = symbol
    
    async def get_market_data(self) -> Optional[Dict]:
        """Get comprehensive market data for volume generation"""
        try:
            ticker = await self.exchange.fetch_ticker(self.symbol)
            orderbook = await self.exchange.fetch_order_book(self.symbol, limit=50)
            trades = await self.exchange.fetch_trades(self.symbol, limit=100)
            ohlcv = await self.exchange.fetch_ohlcv(self.symbol, '5m', limit=20)
            
            return {
                'ticker': ticker,
                'orderbook': orderbook,
                'trades': trades,
                'ohlcv': ohlcv,
                'timestamp': datetime.now()
            }
        except Exception as e:
            logger.error(f"Error fetching market data: {e}")
            return None
    
    def calculate_spread(self, orderbook: Dict) -> float:
        """Calculate bid-ask spread"""
        if not orderbook.get('bids') or not orderbook.get('asks'):
            return 0
        
        bid = orderbook['bids'][0][0]
        ask = orderbook['asks'][0][0]
        return (ask - bid) / bid if bid > 0 else 0
    
    def get_available_liquidity(self, orderbook: Dict) -> Dict[str, float]:
        """Get available liquidity on both sides"""
        if not orderbook.get('bids') or not orderbook.get('asks'):
            return {'bid_volume': 0, 'ask_volume': 0}
        
        return {
            'bid_volume': orderbook['bids'][0][1] if orderbook['bids'] else 0,
            'ask_volume': orderbook['asks'][0][1] if orderbook['asks'] else 0
        }