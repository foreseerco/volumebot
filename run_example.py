#!/usr/bin/env python3
"""
Example configurations for the standalone volume bot
Run different volume generation strategies
"""

import asyncio
from main import StandaloneVolumeBot, VolumeConfig

async def run_conservative_volume():
    """Run conservative volume generation (low market impact)"""
    print("🟢 Starting Conservative Volume Strategy")
    print("Target: $50 USDT/hour, 0.5% max deviation")
    
    config = {
        'target_volume_usdt_per_hour': 50.0,
        'price_walk_direction': 'sideways',
        'max_price_deviation': 0.005,  # 0.5%
        'order_frequency': 120,        # 2 minutes
        'min_order_ratio': 0.001,     # 0.1%
        'max_order_ratio': 0.003,     # 0.3%
        'timing_randomization': 0.8,   # High randomization
        'burst_probability': 0.02,     # Low burst activity
        'quiet_probability': 0.2,      # More quiet periods
        'min_order_value_usdt': 5.0,
        'max_spread_threshold': 0.05
    }
    
    bot = StandaloneVolumeBot(config)
    
    try:
        if await bot.initialize_exchange():
            await bot.run_volume_generation()  # Run infinitely
    finally:
        await bot.close()

async def run_moderate_volume():
    """Run moderate volume generation (balanced approach)"""
    print("🟡 Starting Moderate Volume Strategy")
    print("Target: $100 USDT/hour, 1% max deviation")
    
    config = {
        'target_volume_usdt_per_hour': 100.0,
        'price_walk_direction': 'sideways',
        'max_price_deviation': 0.01,   # 1%
        'order_frequency': 60,         # 1 minute
        'min_order_ratio': 0.001,     # 0.1%
        'max_order_ratio': 0.005,     # 0.5%
        'timing_randomization': 0.5,   # Moderate randomization
        'burst_probability': 0.05,     # Some burst activity
        'quiet_probability': 0.1,      # Some quiet periods
        'min_order_value_usdt': 5.0,
        'max_spread_threshold': 0.05
    }
    
    bot = StandaloneVolumeBot(config)
    
    try:
        if await bot.initialize_exchange():
            await bot.run_volume_generation()  # Run infinitely
    finally:
        await bot.close()

async def run_aggressive_volume():
    """Run aggressive volume generation (high market impact)"""
    print("🔴 Starting Aggressive Volume Strategy")
    print("Target: $200 USDT/hour, 2% max deviation")
    print("⚠️ WARNING: High market impact strategy!")
    
    config = {
        'target_volume_usdt_per_hour': 200.0,
        'price_walk_direction': 'random',
        'max_price_deviation': 0.02,   # 2%
        'order_frequency': 30,         # 30 seconds
        'min_order_ratio': 0.002,     # 0.2%
        'max_order_ratio': 0.008,     # 0.8%
        'timing_randomization': 0.3,   # Low randomization
        'burst_probability': 0.15,     # More burst activity
        'quiet_probability': 0.05,     # Fewer quiet periods
        'min_order_value_usdt': 5.0,
        'max_spread_threshold': 0.05
    }
    
    bot = StandaloneVolumeBot(config)
    
    try:
        if await bot.initialize_exchange():
            await bot.run_volume_generation()  # Run infinitely
    finally:
        await bot.close()

async def run_upward_trend():
    """Run volume generation with upward price bias"""
    print("📈 Starting Upward Trend Volume Strategy")
    print("Target: $150 USDT/hour, gradual price increase")
    
    config = {
        'target_volume_usdt_per_hour': 150.0,
        'price_walk_direction': 'up',
        'max_price_deviation': 0.015,  # 1.5%
        'order_frequency': 45,         # 45 seconds
        'min_order_ratio': 0.0015,    # 0.15%
        'max_order_ratio': 0.006,     # 0.6%
        'timing_randomization': 0.4,
        'burst_probability': 0.08,
        'quiet_probability': 0.08,
        'min_order_value_usdt': 5.0,
        'max_spread_threshold': 0.05
    }
    
    bot = StandaloneVolumeBot(config)
    
    try:
        if await bot.initialize_exchange():
            await bot.run_volume_generation()  # Run infinitely
    finally:
        await bot.close()

async def run_market_making_simulation():
    """Simulate market making with balanced buy/sell orders"""
    print("⚖️ Starting Market Making Simulation")
    print("Target: $80 USDT/hour, tight spread simulation")
    
    config = {
        'target_volume_usdt_per_hour': 80.0,
        'price_walk_direction': 'sideways',
        'max_price_deviation': 0.008,  # 0.8%
        'order_frequency': 90,         # 1.5 minutes
        'min_order_ratio': 0.0008,    # 0.08%
        'max_order_ratio': 0.004,     # 0.4%
        'timing_randomization': 0.6,   # Good randomization
        'burst_probability': 0.03,     # Low burst
        'quiet_probability': 0.15,     # Regular quiet periods
        'size_randomization': 0.2,     # Less size variation
        'min_order_value_usdt': 5.0,
        'max_spread_threshold': 0.05
    }
    
    bot = StandaloneVolumeBot(config)
    
    try:
        if await bot.initialize_exchange():
            await bot.run_volume_generation()  # Run infinitely
    finally:
        await bot.close()

def print_menu():
    """Print strategy selection menu"""
    print("\n🤖 Standalone Volume Bot - Strategy Examples")
    print("="*50)
    print("1. Conservative Volume ($50 USDT/hour)")
    print("2. Moderate Volume ($100 USDT/hour)")
    print("3. Aggressive Volume ($200 USDT/hour) ⚠️")
    print("4. Upward Trend ($150 USDT/hour)")
    print("5. Market Making ($80 USDT/hour)")
    print("6. Exit")
    print("="*50)
    print(f"Current Settings:")
    print(f"  Exchange: {VolumeConfig.EXCHANGE}")
    print(f"  Pair: {VolumeConfig.TRADING_PAIR}")
    print(f"  Dry Run: {'✅' if VolumeConfig.DRY_RUN else '❌'}")
    print(f"  Min Order: ${VolumeConfig.MIN_ORDER_VALUE_USDT} USDT")
    print("="*50)

async def main():
    """Main menu for strategy selection"""
    
    while True:
        print_menu()
        
        try:
            choice = input("\nSelect strategy (1-6): ").strip()
            
            if choice == '1':
                await run_conservative_volume()
            elif choice == '2':
                await run_moderate_volume()
            elif choice == '3':
                if not VolumeConfig.DRY_RUN:
                    confirm = input("⚠️ This is a high-impact strategy. Are you sure? (yes/no): ")
                    if confirm.lower() != 'yes':
                        continue
                await run_aggressive_volume()
            elif choice == '4':
                await run_upward_trend()
            elif choice == '5':
                await run_market_making_simulation()
            elif choice == '6':
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please select 1-6.")
                continue
                
        except KeyboardInterrupt:
            print("\n⏹️ Interrupted by user")
            break
        except asyncio.CancelledError:
            print("\n⏹️ Operation cancelled")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            continue
            
        # Ask if user wants to run another strategy
        if input("\nRun another strategy? (y/n): ").lower() != 'y':
            break

if __name__ == "__main__":
    asyncio.run(main())