"""
Comprehensive Strategy Optimizer
Tests combinations of: stop loss, take profit, scale-out %, trailing stop
"""

import pandas as pd
import numpy as np
from datetime import datetime, time
import pytz
import yfinance as yf
from itertools import product
import sys

# Import the strategy class
from trade import MomentumHODStrategy, fetch_data, screen_stocks_finviz


def run_backtest_with_params(data_dict, stop_loss_pct, take_profit_pct, 
                             scale_out_pct, scale_out_target, trailing_stop_pct):
    """Run backtest with specific exit parameters - uses ORIGINAL entry logic"""
    
    # Create strategy and run normal backtest with original entry logic
    strategy = MomentumHODStrategy()
    
    # Override ONLY the exit parameters
    strategy.stop_loss_pct = stop_loss_pct
    strategy.take_profit_pct = take_profit_pct
    strategy.trailing_stop_pct = trailing_stop_pct
    strategy.scale_out_target = scale_out_target
    
    # Store scale_out_pct for later use
    scale_out_percentage = scale_out_pct
    
    prepared_data = {}
    for symbol, df in data_dict.items():
        if df.empty:
            continue
        prepared_data[symbol] = strategy.calculate_indicators(df)
    
    if not prepared_data:
        return None
    
    all_timestamps = sorted(set().union(*[set(df.index) for df in prepared_data.values()]))
    
    # Identify the last trading day
    last_date = max(ts.date() for ts in all_timestamps)
    market_close_time = time(15, 55)
    
    for timestamp in all_timestamps:
        current_date = timestamp.date()
        current_time = timestamp.time()
        is_last_day = current_date == last_date
        
        # Close all positions before market close on last day
        if is_last_day and current_time >= market_close_time:
            for symbol in list(strategy.positions.keys()):
                df = prepared_data[symbol]
                if timestamp in df.index:
                    current_price = df.loc[timestamp, 'close']
                    strategy.exit_position(symbol, current_price, timestamp, "MARKET_CLOSE")
            continue
        
        # Don't take new trades on the last day - USE ORIGINAL ENTRY LOGIC
        if not is_last_day:
            if strategy.is_scanning_time(timestamp):
                for symbol, df in prepared_data.items():
                    if timestamp not in df.index:
                        continue
                    
                    idx = df.index.get_loc(timestamp)
                    # Use ORIGINAL entry logic from trade.py
                    if strategy.has_momentum(df, idx, symbol) and strategy.is_near_hod(df, idx):
                        if symbol not in strategy.watchlist:
                            strategy.watchlist[symbol] = timestamp
            
            for symbol in list(strategy.watchlist.keys()):
                if symbol in strategy.positions:
                    continue
                df = prepared_data[symbol]
                if timestamp not in df.index:
                    continue
                idx = df.index.get_loc(timestamp)
                # Use ORIGINAL entry conditions from trade.py
                if strategy.check_entry_conditions(df, idx, symbol):
                    entry_price = df.iloc[idx]['close']
                    strategy.enter_position(symbol, entry_price, timestamp)
                    if symbol in strategy.ema_touch_tracker:
                        del strategy.ema_touch_tracker[symbol]
                    if symbol in strategy.ema_confirmation_tracker:
                        del strategy.ema_confirmation_tracker[symbol]
        
        for symbol in list(strategy.positions.keys()):
            df = prepared_data[symbol]
            if timestamp not in df.index:
                continue
            current_price = df.loc[timestamp, 'close']
            position = strategy.positions[symbol]
            
            if current_price > position['highest_price']:
                position['highest_price'] = current_price
            
            # Scale out at target price with custom percentage
            if not position['scaled_out'] and current_price >= position['scale_out_price']:
                shares_to_sell = int(position['shares'] * scale_out_percentage)
                if shares_to_sell > 0:
                    strategy.exit_position(symbol, current_price, timestamp, 
                                         f"SCALE_OUT_{int(scale_out_target*100)}%", 
                                         shares=shares_to_sell)
                    position['scaled_out'] = True
                    position['trailing_stop_active'] = True
            
            # Calculate trailing stop price
            if position['trailing_stop_active']:
                trailing_stop_price = position['highest_price'] * (1 - trailing_stop_pct)
            else:
                trailing_stop_price = position['stop_loss']
            
            # Check exit conditions
            if current_price <= trailing_stop_price:
                reason = "TRAILING_STOP" if position['trailing_stop_active'] else "STOP_LOSS"
                strategy.exit_position(symbol, current_price, timestamp, reason)
            elif current_price >= position['take_profit'] and not position['scaled_out']:
                # Full exit at take profit if we haven't scaled out yet
                strategy.exit_position(symbol, current_price, timestamp, "TAKE_PROFIT")
    
    # Close any remaining positions
    for symbol in list(strategy.positions.keys()):
        df = prepared_data[symbol]
        strategy.exit_position(symbol, df.iloc[-1]['close'], df.index[-1], "END_OF_DATA")
    
    if strategy.trades:
        trades_df = pd.DataFrame(strategy.trades)
        
        # Calculate additional metrics
        wins = trades_df[trades_df['pnl'] > 0]
        losses = trades_df[trades_df['pnl'] < 0]
        
        return {
            'stop_loss': stop_loss_pct,
            'take_profit': take_profit_pct,
            'scale_out_pct': scale_out_pct,
            'scale_out_target': scale_out_target,
            'trailing_stop': trailing_stop_pct,
            'total_trades': len(trades_df),
            'wins': len(wins),
            'losses': len(losses),
            'win_rate': len(wins) / len(trades_df) * 100 if len(trades_df) > 0 else 0,
            'total_pnl': trades_df['pnl'].sum(),
            'avg_pnl': trades_df['pnl'].mean(),
            'avg_win': wins['pnl'].mean() if len(wins) > 0 else 0,
            'avg_loss': losses['pnl'].mean() if len(losses) > 0 else 0,
            'max_win': trades_df['pnl'].max(),
            'max_loss': trades_df['pnl'].min(),
            'profit_factor': abs(wins['pnl'].sum() / losses['pnl'].sum()) if len(losses) > 0 and losses['pnl'].sum() != 0 else 0,
            'avg_win_pct': wins['pnl_pct'].mean() if len(wins) > 0 else 0,
            'avg_loss_pct': losses['pnl_pct'].mean() if len(losses) > 0 else 0,
            'expectancy': trades_df['pnl'].mean() if len(trades_df) > 0 else 0
        }
    else:
        return None


def main():
    print("=" * 80)
    print("COMPREHENSIVE STRATEGY OPTIMIZER")
    print("=" * 80)
    print("Testing: Stop Loss, Take Profit, Scale-Out %, Trailing Stop")
    print("=" * 80)
    
    # Get data first - ONLY use Finviz screening
    print("\nScreening stocks with Finviz...")
    strategy = MomentumHODStrategy()
    
    symbols = screen_stocks_finviz(strategy)
    if not symbols:
        print("\n❌ No symbols found from Finviz screening!")
        print("The screener looks for: Price $1-$20, RVol>2x, Avg Volume>500K")
        print("Try again when market conditions produce qualifying stocks.")
        return
    
    data = fetch_data(symbols, strategy)
    
    if not data:
        print("\n❌ No valid data!")
        print("Try providing symbols that meet criteria:")
        print("  python optimize_stops.py SYMBOL1 SYMBOL2 SYMBOL3")
        return
    
    print(f"\n✓ {len(data)} stocks with valid data")
    print("\n" + "=" * 80)
    print("TESTING PARAMETER COMBINATIONS")
    print("=" * 80)
    
    # Define parameter ranges to test
    stop_loss_range = [0.02, 0.025, 0.03, 0.04, 0.05]  # 2% to 5%
    take_profit_range = [0.05, 0.06, 0.08, 0.10]  # 5% to 10%
    scale_out_pct_range = [0.25, 0.33, 0.50, 0.67]  # 25%, 33%, 50%, 67% of position
    scale_out_target_range = [0.04, 0.05, 0.06, 0.08]  # 4% to 8% profit target
    trailing_stop_range = [0.03, 0.04, 0.05, 0.06]  # 3% to 6%
    
    print(f"\nParameter Ranges:")
    print(f"  Stop Loss: {[f'{x*100:.1f}%' for x in stop_loss_range]}")
    print(f"  Take Profit: {[f'{x*100:.1f}%' for x in take_profit_range]}")
    print(f"  Scale-Out %: {[f'{x*100:.0f}%' for x in scale_out_pct_range]}")
    print(f"  Scale-Out Target: {[f'{x*100:.1f}%' for x in scale_out_target_range]}")
    print(f"  Trailing Stop: {[f'{x*100:.1f}%' for x in trailing_stop_range]}")
    
    total_combinations = (len(stop_loss_range) * len(take_profit_range) * 
                         len(scale_out_pct_range) * len(scale_out_target_range) * 
                         len(trailing_stop_range))
    
    print(f"\nTotal combinations to test: {total_combinations}")
    print("This may take a while...\n")
    
    results = []
    current = 0
    
    for stop_loss, take_profit, scale_pct, scale_target, trailing in product(
        stop_loss_range, take_profit_range, scale_out_pct_range, 
        scale_out_target_range, trailing_stop_range
    ):
        current += 1
        
        # Skip invalid combinations
        if scale_target >= take_profit:  # Scale-out target should be less than take profit
            continue
        if trailing > stop_loss:  # Trailing stop shouldn't be wider than initial stop
            continue
        
        print(f"[{current}/{total_combinations}] SL:{stop_loss*100:.1f}% TP:{take_profit*100:.1f}% "
              f"ScaleOut:{scale_pct*100:.0f}%@{scale_target*100:.1f}% Trail:{trailing*100:.1f}%", 
              end=" ")
        
        result = run_backtest_with_params(data, stop_loss, take_profit, 
                                         scale_pct, scale_target, trailing)
        
        if result:
            results.append(result)
            print(f"✓ {result['total_trades']} trades, P&L: ${result['total_pnl']:.2f}, "
                  f"WR: {result['win_rate']:.1f}%, PF: {result['profit_factor']:.2f}")
        else:
            print("✗ No trades")
    
    if not results:
        print("\n❌ No valid results!")
        print("\nThis means no trades were executed with any parameter combination.")
        print("Possible reasons:")
        print("  - Stocks didn't meet daily criteria during backtest period")
        print("  - No momentum setups occurred in the data")
        print("  - Try different stocks or a different time period")
        return
    
    # Convert to DataFrame and sort
    results_df = pd.DataFrame(results)
    
    print("\n" + "=" * 80)
    print("OPTIMIZATION RESULTS")
    print("=" * 80)
    
    # Sort by different metrics
    print("\n💰 TOP 10 BY TOTAL P&L:")
    print("-" * 80)
    top_pnl = results_df.nlargest(10, 'total_pnl')
    for idx, row in top_pnl.iterrows():
        print(f"SL:{row['stop_loss']*100:.1f}% TP:{row['take_profit']*100:.1f}% "
              f"ScaleOut:{row['scale_out_pct']*100:.0f}%@{row['scale_out_target']*100:.1f}% "
              f"Trail:{row['trailing_stop']*100:.1f}% | "
              f"P&L: ${row['total_pnl']:.2f} | WR: {row['win_rate']:.1f}% | "
              f"Trades: {row['total_trades']:.0f} | PF: {row['profit_factor']:.2f}")
    
    print("\n🎯 TOP 10 BY WIN RATE:")
    print("-" * 80)
    top_wr = results_df.nlargest(10, 'win_rate')
    for idx, row in top_wr.iterrows():
        print(f"SL:{row['stop_loss']*100:.1f}% TP:{row['take_profit']*100:.1f}% "
              f"ScaleOut:{row['scale_out_pct']*100:.0f}%@{row['scale_out_target']*100:.1f}% "
              f"Trail:{row['trailing_stop']*100:.1f}% | "
              f"WR: {row['win_rate']:.1f}% | P&L: ${row['total_pnl']:.2f} | "
              f"Trades: {row['total_trades']:.0f} | PF: {row['profit_factor']:.2f}")
    
    print("\n📊 TOP 10 BY PROFIT FACTOR:")
    print("-" * 80)
    top_pf = results_df.nlargest(10, 'profit_factor')
    for idx, row in top_pf.iterrows():
        print(f"SL:{row['stop_loss']*100:.1f}% TP:{row['take_profit']*100:.1f}% "
              f"ScaleOut:{row['scale_out_pct']*100:.0f}%@{row['scale_out_target']*100:.1f}% "
              f"Trail:{row['trailing_stop']*100:.1f}% | "
              f"PF: {row['profit_factor']:.2f} | P&L: ${row['total_pnl']:.2f} | "
              f"WR: {row['win_rate']:.1f}% | Trades: {row['total_trades']:.0f}")
    
    print("\n⚡ TOP 10 BY EXPECTANCY (Avg P&L per Trade):")
    print("-" * 80)
    top_exp = results_df.nlargest(10, 'expectancy')
    for idx, row in top_exp.iterrows():
        print(f"SL:{row['stop_loss']*100:.1f}% TP:{row['take_profit']*100:.1f}% "
              f"ScaleOut:{row['scale_out_pct']*100:.0f}%@{row['scale_out_target']*100:.1f}% "
              f"Trail:{row['trailing_stop']*100:.1f}% | "
              f"Expectancy: ${row['expectancy']:.2f} | P&L: ${row['total_pnl']:.2f} | "
              f"WR: {row['win_rate']:.1f}% | Trades: {row['total_trades']:.0f}")
    
    print("\n" + "=" * 80)
    print("BEST OVERALL PARAMETERS")
    print("=" * 80)
    
    best = results_df.loc[results_df['total_pnl'].idxmax()]
    print(f"\n🏆 HIGHEST TOTAL P&L:")
    print(f"  Stop Loss: {best['stop_loss']*100:.1f}%")
    print(f"  Take Profit: {best['take_profit']*100:.1f}%")
    print(f"  Scale-Out: {best['scale_out_pct']*100:.0f}% at {best['scale_out_target']*100:.1f}% profit")
    print(f"  Trailing Stop: {best['trailing_stop']*100:.1f}%")
    print(f"  Total P&L: ${best['total_pnl']:.2f}")
    print(f"  Win Rate: {best['win_rate']:.1f}%")
    print(f"  Total Trades: {best['total_trades']:.0f}")
    print(f"  Avg Win: ${best['avg_win']:.2f} ({best['avg_win_pct']:.2f}%)")
    print(f"  Avg Loss: ${best['avg_loss']:.2f} ({best['avg_loss_pct']:.2f}%)")
    print(f"  Profit Factor: {best['profit_factor']:.2f}")
    print(f"  Expectancy: ${best['expectancy']:.2f}")
    
    # Find balanced parameters using composite score
    print("\n" + "=" * 80)
    print("BALANCED PARAMETERS (Composite Score)")
    print("=" * 80)
    
    # Normalize metrics and create composite score
    results_df['norm_pnl'] = (results_df['total_pnl'] - results_df['total_pnl'].min()) / (results_df['total_pnl'].max() - results_df['total_pnl'].min())
    results_df['norm_wr'] = results_df['win_rate'] / 100
    results_df['norm_pf'] = (results_df['profit_factor'] - results_df['profit_factor'].min()) / (results_df['profit_factor'].max() - results_df['profit_factor'].min())
    results_df['norm_exp'] = (results_df['expectancy'] - results_df['expectancy'].min()) / (results_df['expectancy'].max() - results_df['expectancy'].min())
    
    # Composite score: 30% P&L, 25% Win Rate, 25% Profit Factor, 20% Expectancy
    results_df['composite_score'] = (
        results_df['norm_pnl'] * 0.30 +
        results_df['norm_wr'] * 0.25 +
        results_df['norm_pf'] * 0.25 +
        results_df['norm_exp'] * 0.20
    )
    
    best_balanced = results_df.loc[results_df['composite_score'].idxmax()]
    print(f"\n🎯 RECOMMENDED PARAMETERS:")
    print(f"  Stop Loss: {best_balanced['stop_loss']*100:.1f}%")
    print(f"  Take Profit: {best_balanced['take_profit']*100:.1f}%")
    print(f"  Scale-Out: {best_balanced['scale_out_pct']*100:.0f}% at {best_balanced['scale_out_target']*100:.1f}% profit")
    print(f"  Trailing Stop: {best_balanced['trailing_stop']*100:.1f}%")
    print(f"  Expected P&L: ${best_balanced['total_pnl']:.2f}")
    print(f"  Expected Win Rate: {best_balanced['win_rate']:.1f}%")
    print(f"  Profit Factor: {best_balanced['profit_factor']:.2f}")
    print(f"  Expectancy: ${best_balanced['expectancy']:.2f}")
    print(f"  Composite Score: {best_balanced['composite_score']:.3f}")
    
    # Save results
    results_df.to_csv('optimization_results.csv', index=False)
    print(f"\n✓ Full results saved to optimization_results.csv")
    
    print("\n" + "=" * 80)
    print("HOW TO APPLY THESE PARAMETERS")
    print("=" * 80)
    print(f"\nUpdate trade.py with the recommended parameters:")
    print(f"  self.stop_loss_pct = {best_balanced['stop_loss']}")
    print(f"  self.take_profit_pct = {best_balanced['take_profit']}")
    print(f"  self.trailing_stop_pct = {best_balanced['trailing_stop']}")
    print(f"  self.scale_out_target = {best_balanced['scale_out_target']}")
    print(f"\nIn enter_position(), update scale-out calculation:")
    print(f"  shares_to_sell = int(position['shares'] * {best_balanced['scale_out_pct']})")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
