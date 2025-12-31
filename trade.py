"""
Momentum HOD Strategy Backtester - Small Cap Edition
Filters: Price $1-$10, Float < 30M shares, Relative Volume > 2x
"""

import pandas as pd
import numpy as np
from datetime import datetime, time
import pytz

class MomentumHODStrategy:
    def __init__(self):
        self.scan_start_time = time(10, 0)  # 10 AM EST (avoid first 30 min)
        self.scan_end_time = time(14, 0)    # 2 PM EST
        self.rsi_threshold = 60
        self.stop_loss_pct = 0.05  # 5% stop loss (OPTIMIZED)
        self.take_profit_pct = 0.10  # 10% (OPTIMIZED)
        self.hod_proximity_pct = 0.10  # Within 10% of HOD
        
        # Trailing stop configuration (OPTIMIZED)
        self.trailing_stop_pct = 0.05  # 5% trailing stop
        self.scale_out_target = 0.08  # Take 67% profit at 8% (OPTIMIZED)
        
        # Position sizing
        self.position_size_dollars = 1000  # $1000 per trade
        
        # Small-cap filters
        self.min_price = 1.0
        self.max_price = 10.0
        self.max_float = 30_000_000  # 30M shares
        self.min_relative_volume = 2.0  # 2x average
        
        self.watchlist = {}
        self.positions = {}
        self.trades = []
        self.stock_info = {}
        self.ema_touch_tracker = {}
        self.ema_confirmation_tracker = {}
        self.est = pytz.timezone('America/New_York')
        
        # Daily criteria tracking for historical screening
        self.daily_criteria_met = {}  # {symbol: {date: bool}}
    
    def calculate_rsi(self, prices, period=14):
        deltas = np.diff(prices)
        seed = deltas[:period+1]
        up = seed[seed >= 0].sum()/period
        down = -seed[seed < 0].sum()/period
        rs = up/down if down != 0 else 0
        rsi = np.zeros_like(prices)
        rsi[:period] = 100. - 100./(1. + rs)
        
        for i in range(period, len(prices)):
            delta = deltas[i-1]
            upval = delta if delta > 0 else 0
            downval = -delta if delta < 0 else 0
            up = (up*(period-1) + upval)/period
            down = (down*(period-1) + downval)/period
            rs = up/down if down != 0 else 0
            rsi[i] = 100. - 100./(1. + rs)
        return rsi
    
    def calculate_ema(self, prices, period):
        ema = np.zeros_like(prices)
        ema[0] = prices[0]
        multiplier = 2 / (period + 1)
        for i in range(1, len(prices)):
            ema[i] = (prices[i] * multiplier) + (ema[i-1] * (1 - multiplier))
        return ema
    
    def calculate_macd(self, prices):
        ema12 = self.calculate_ema(prices, 12)
        ema26 = self.calculate_ema(prices, 26)
        macd_line = ema12 - ema26
        signal_line = self.calculate_ema(macd_line, 9)
        return macd_line, signal_line
    
    def calculate_indicators(self, df):
        data = df.copy()
        data['rsi'] = self.calculate_rsi(data['close'].values)
        macd, signal = self.calculate_macd(data['close'].values)
        data['macd'] = macd
        data['macd_signal'] = signal
        data['ema_9'] = self.calculate_ema(data['close'].values, 9)
        data['ema_50'] = self.calculate_ema(data['close'].values, 50)
        data['ema_100'] = self.calculate_ema(data['close'].values, 100)
        
        # Calculate VWAP
        data['vwap'] = (data['volume'] * (data['high'] + data['low'] + data['close']) / 3).cumsum() / data['volume'].cumsum()
        
        data['avg_volume'] = data['volume'].rolling(window=20).mean()
        data['is_red'] = data['close'] < data['open']
        data['date'] = data.index.date
        data['hod'] = data.groupby('date')['high'].cummax()
        data['dist_from_hod'] = (data['hod'] - data['close']) / data['hod']
        
        # Calculate relative volume
        data['cumulative_volume'] = data.groupby('date')['volume'].cumsum()
        bars_elapsed = data.groupby('date').cumcount() + 1
        data['avg_volume_at_time'] = data.groupby(data.index.time)['volume'].transform(lambda x: x.expanding().mean())
        data['expected_volume'] = data['avg_volume_at_time'] * bars_elapsed
        data['relative_volume'] = data['cumulative_volume'] / data['expected_volume'].replace(0, 1)
        
        return data
    
    def meets_criteria(self, symbol, price, rvol):
        """Check if stock meets all filtering criteria"""
        if price < self.min_price or price > self.max_price:
            return False
        
        if rvol < self.min_relative_volume:
            return False
        
        if symbol in self.stock_info:
            float_shares = self.stock_info[symbol].get('float', float('inf'))
            if float_shares > self.max_float:
                return False
        
        return True
    
    def check_daily_criteria(self, symbol, daily_df):
        """
        Check if stock met criteria for each of the past 10 days
        Returns dict with date -> bool mapping
        """
        if daily_df is None or daily_df.empty or len(daily_df) < 10:
            return {}
        
        results = {}
        
        # Get float info (doesn't change daily)
        float_shares = self.stock_info.get(symbol, {}).get('float', float('inf'))
        if float_shares > self.max_float:
            # If float is too high, stock never meets criteria
            return {date.date(): False for date in daily_df.index[-10:]}
        
        # Check last 10 days
        for date in daily_df.index[-10:]:
            row = daily_df.loc[date]
            
            # Check price range
            price_ok = self.min_price <= row['Close'] <= self.max_price
            
            # Check relative volume (daily volume vs 20-day average)
            rvol_ok = False
            if 'rel_volume' in row and not pd.isna(row['rel_volume']):
                rvol_ok = row['rel_volume'] >= self.min_relative_volume
            
            # Stock meets criteria if both conditions are met
            results[date.date()] = price_ok and rvol_ok
        
        return results
    
    def meets_criteria_for_date(self, symbol, check_date):
        """Check if stock met criteria on a specific date"""
        if symbol not in self.daily_criteria_met:
            return False
        return self.daily_criteria_met[symbol].get(check_date, False)
    
    def has_momentum(self, df, idx, symbol):
        if idx < 20:
            return False
        row = df.iloc[idx]
        
        # Check criteria
        if not self.meets_criteria(symbol, row['close'], row['relative_volume']):
            return False
        
        return (row['close'] > row['ema_9'] and 
                row['macd'] > row['macd_signal'] and 
                row['volume'] >= row['avg_volume'] * 0.8)
    
    def is_near_hod(self, df, idx):
        return df.iloc[idx]['dist_from_hod'] <= self.hod_proximity_pct
    
    def check_ema_touch_and_bounce(self, df, idx, symbol):
        """
        Check if price touched 9 EMA and has 2 consecutive closes above it (stronger confirmation)
        """
        if idx < 3:
            return False
        
        current = df.iloc[idx]
        prev = df.iloc[idx - 1]
        prev2 = df.iloc[idx - 2]
        
        # Check if price touched or went below 9 EMA 2-3 bars ago
        ema_9_prev2 = prev2['ema_9']
        touched_ema = prev2['low'] <= ema_9_prev2 <= prev2['high'] or prev2['close'] <= ema_9_prev2
        
        # Require 2 consecutive closes above 9 EMA for stronger confirmation
        prev_closes_above = prev['close'] > prev['ema_9']
        current_closes_above = current['close'] > current['ema_9']
        
        if touched_ema and prev_closes_above and current_closes_above:
            # Mark that this stock has touched and bounced with confirmation
            if symbol not in self.ema_touch_tracker:
                self.ema_touch_tracker[symbol] = True
                self.ema_confirmation_tracker[symbol] = 2  # 2 consecutive closes
            return True
        
        return False
    
    def check_entry_conditions(self, df, idx, symbol):
        if idx < 20:
            return False
        
        row = df.iloc[idx]
        
        # Must have touched and bounced off 9 EMA
        if not self.check_ema_touch_and_bounce(df, idx, symbol):
            return False
        
        # Require cumulative volume > 5M by entry time
        if row['cumulative_volume'] < 5_000_000:
            return False
        
        # Require volume surge on entry bar (1.5x average)
        if row['volume'] < row['avg_volume'] * 1.5:
            return False
        
        # RSI < 60
        if np.isnan(row['rsi']) or row['rsi'] >= self.rsi_threshold:
            return False
        
        # MACD > Signal
        if row['macd'] <= row['macd_signal']:
            return False
        
        # Red volume < avg volume
        if row['is_red'] and row['volume'] >= row['avg_volume']:
            return False
        
        return True
    
    def is_scanning_time(self, timestamp):
        if timestamp.tz is None:
            timestamp = self.est.localize(timestamp)
        else:
            timestamp = timestamp.astimezone(self.est)
        current_time = timestamp.time()
        return self.scan_start_time <= current_time <= self.scan_end_time
    
    def enter_position(self, symbol, entry_price, timestamp):
        stop_loss = entry_price * (1 - self.stop_loss_pct)
        take_profit = entry_price * (1 + self.take_profit_pct)
        scale_out_price = entry_price * (1 + self.scale_out_target)
        
        # Calculate shares based on $1000 position size
        shares = int(self.position_size_dollars / entry_price)
        
        self.positions[symbol] = {
            'entry_price': entry_price,
            'entry_time': timestamp,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'scale_out_price': scale_out_price,
            'shares': shares,
            'remaining_shares': shares,
            'scaled_out': False,
            'highest_price': entry_price,
            'trailing_stop_active': False
        }
        position_value = shares * entry_price
        print(f"[{timestamp.strftime('%Y-%m-%d %H:%M')}] ENTER {symbol} @ ${entry_price:.2f} | {shares} shares (${position_value:.2f}) | SL: ${stop_loss:.2f} (-3%) | Scale-out: ${scale_out_price:.2f} (50% @ 6%)")
    
    def exit_position(self, symbol, exit_price, timestamp, reason, shares=None):
        if symbol not in self.positions:
            return
        position = self.positions[symbol]
        
        # If shares not specified, exit entire position
        if shares is None:
            shares = position['remaining_shares']
        
        pnl = (exit_price - position['entry_price']) * shares
        pnl_pct = (exit_price / position['entry_price'] - 1) * 100
        
        self.trades.append({
            'symbol': symbol,
            'entry_time': position['entry_time'],
            'entry_price': position['entry_price'],
            'exit_time': timestamp,
            'exit_price': exit_price,
            'shares': shares,
            'pnl': pnl,
            'pnl_pct': pnl_pct,
            'reason': reason
        })
        
        # Update remaining shares
        position['remaining_shares'] -= shares
        
        # If position fully closed, remove it
        if position['remaining_shares'] <= 0:
            del self.positions[symbol]
            print(f"[{timestamp.strftime('%Y-%m-%d %H:%M')}] EXIT {symbol} @ ${exit_price:.2f} | {reason} | PnL: ${pnl:.2f} ({pnl_pct:.2f}%) | FULL EXIT")
        else:
            print(f"[{timestamp.strftime('%Y-%m-%d %H:%M')}] PARTIAL EXIT {symbol} @ ${exit_price:.2f} | {reason} | PnL: ${pnl:.2f} ({pnl_pct:.2f}%) | {position['remaining_shares']} shares remaining")
    
    def backtest(self, data_dict):
        print("=" * 80)
        print("Momentum HOD Strategy Backtest")
        print("=" * 80)
        
        prepared_data = {}
        for symbol, df in data_dict.items():
            if df.empty:
                continue
            prepared_data[symbol] = self.calculate_indicators(df)
        
        if not prepared_data:
            print("No valid data!")
            return pd.DataFrame()
        
        all_timestamps = sorted(set().union(*[set(df.index) for df in prepared_data.values()]))
        
        # Identify the last trading day
        last_date = max(ts.date() for ts in all_timestamps)
        market_close_time = time(15, 55)  # Close all positions by 3:55 PM EST
        
        for timestamp in all_timestamps:
            # Get the date for this timestamp to check daily criteria
            current_date = timestamp.date()
            current_time = timestamp.time()
            is_last_day = current_date == last_date
            
            # Close all positions before market close EVERY day at 3:55 PM EST
            if current_time >= market_close_time:
                for symbol in list(self.positions.keys()):
                    df = prepared_data[symbol]
                    if timestamp in df.index:
                        current_price = df.loc[timestamp, 'close']
                        self.exit_position(symbol, current_price, timestamp, "MARKET_CLOSE")
                continue
            
            # Don't take new trades on the last day
            if not is_last_day:
                if self.is_scanning_time(timestamp):
                    for symbol, df in prepared_data.items():
                        if timestamp not in df.index:
                            continue
                        
                        # Check if stock met criteria on this specific date
                        if not self.meets_criteria_for_date(symbol, current_date):
                            continue
                        
                        idx = df.index.get_loc(timestamp)
                        if self.has_momentum(df, idx, symbol) and self.is_near_hod(df, idx):
                            if symbol not in self.watchlist:
                                self.watchlist[symbol] = timestamp
                                price = df.iloc[idx]['close']
                                rvol = df.iloc[idx]['relative_volume']
                                float_info = self.stock_info.get(symbol, {})
                                float_str = f"{float_info.get('float', 0)/1_000_000:.1f}M" if 'float' in float_info else "N/A"
                                print(f"[{timestamp.strftime('%Y-%m-%d %H:%M')}] Added {symbol} | ${price:.2f} | RVol: {rvol:.2f}x | Float: {float_str} | Met daily criteria")
                
                for symbol in list(self.watchlist.keys()):
                    if symbol in self.positions:
                        continue
                    df = prepared_data[symbol]
                    if timestamp not in df.index:
                        continue
                    idx = df.index.get_loc(timestamp)
                    if self.check_entry_conditions(df, idx, symbol):
                        # Enter at current close price (after bounce confirmation)
                        entry_price = df.iloc[idx]['close']
                        self.enter_position(symbol, entry_price, timestamp)
                        # Clear the trackers after entry
                        if symbol in self.ema_touch_tracker:
                            del self.ema_touch_tracker[symbol]
                        if symbol in self.ema_confirmation_tracker:
                            del self.ema_confirmation_tracker[symbol]
            
            for symbol in list(self.positions.keys()):
                df = prepared_data[symbol]
                if timestamp not in df.index:
                    continue
                current_price = df.loc[timestamp, 'close']
                position = self.positions[symbol]
                
                # Update highest price for trailing stop
                if current_price > position['highest_price']:
                    position['highest_price'] = current_price
                
                # Check for scale-out at 8% profit (67% of position) - OPTIMIZED
                if not position['scaled_out'] and current_price >= position['scale_out_price']:
                    shares_to_sell = int(position['shares'] * 0.67)  # Sell 67% (OPTIMIZED)
                    self.exit_position(symbol, current_price, timestamp, "SCALE_OUT_8%", shares=shares_to_sell)
                    position['scaled_out'] = True
                    position['trailing_stop_active'] = True
                    print(f"[{timestamp.strftime('%Y-%m-%d %H:%M')}] {symbol} trailing stop activated at 5%")
                
                # Calculate trailing stop price
                if position['trailing_stop_active']:
                    trailing_stop_price = position['highest_price'] * (1 - self.trailing_stop_pct)
                else:
                    trailing_stop_price = position['stop_loss']
                
                # Check exit conditions
                if current_price <= trailing_stop_price:
                    reason = "TRAILING_STOP" if position['trailing_stop_active'] else "STOP_LOSS"
                    self.exit_position(symbol, current_price, timestamp, reason)
                elif current_price >= position['take_profit'] and not position['scaled_out']:
                    # Full exit at take profit if we haven't scaled out yet
                    self.exit_position(symbol, current_price, timestamp, "TAKE_PROFIT")
        
        for symbol in list(self.positions.keys()):
            df = prepared_data[symbol]
            self.exit_position(symbol, df.iloc[-1]['close'], df.index[-1], "END_OF_DATA")
        
        if self.trades:
            trades_df = pd.DataFrame(self.trades)
            self.print_summary(trades_df)
            return trades_df
        else:
            print("\nNo trades executed")
            return pd.DataFrame()
    
    def print_summary(self, trades_df):
        print("\n" + "=" * 80)
        print("BACKTEST SUMMARY")
        print("=" * 80)
        total = len(trades_df)
        wins = len(trades_df[trades_df['pnl'] > 0])
        losses = len(trades_df[trades_df['pnl'] < 0])
        win_rate = (wins / total * 100) if total > 0 else 0
        print(f"Total Trades: {total}")
        print(f"Winning: {wins} | Losing: {losses}")
        print(f"Win Rate: {win_rate:.2f}%")
        print(f"Total PnL: ${trades_df['pnl'].sum():.2f}")
        print(f"Average PnL: ${trades_df['pnl'].mean():.2f}")
        print("=" * 80)


def screen_stocks_finviz(strategy):
    """Use Finviz to screen for stocks meeting criteria"""
    try:
        from finvizfinance.screener.overview import Overview
    except ImportError:
        print("ERROR: finvizfinance not installed!")
        print("Install it with: pip install finvizfinance")
        return []
    
    print("\n" + "=" * 80)
    print("SCREENING STOCKS WITH FINVIZ")
    print("=" * 80)
    print(f"Criteria: Price $1-$20, RVol>2x, Avg Volume>500K")
    print(f"Additional: Float<{strategy.max_float/1_000_000:.0f}M, 5M volume at entry (verified after)")
    print("-" * 80)
    
    try:
        fviz = Overview()
        # Optimized filters for momentum HOD strategy
        # Note: We check 5M volume at entry time in code, not in Finviz
        filters_dict = {
            'Price': '$1 to $20',
            'Relative Volume': 'Over 2',
            'Average Volume': 'Over 500K',  # Ensures potential for 5M intraday
        }
        
        fviz.set_filter(filters_dict=filters_dict)
        df_screen = fviz.screener_view()
        
        if df_screen is None or df_screen.empty:
            print("No stocks found matching criteria")
            return []
        
        # Get all symbols - we'll filter by float when fetching data
        symbols = df_screen['Ticker'].tolist()
        print(f"Found {len(symbols)} stocks from Finviz (Price $1-$20, RVol>2x)")
        print(f"Note: Float <100M will be verified when fetching data")
        print(f"Symbols: {', '.join(symbols[:20])}")
        if len(symbols) > 20:
            print(f"... and {len(symbols) - 20} more")
        
        return symbols
        
    except Exception as e:
        print(f"Error screening with Finviz: {e}")
        print("Falling back to manual symbol list...")
        return []


def fetch_data(symbols, strategy):
    try:
        import yfinance as yf
    except ImportError:
        print("ERROR: Install yfinance first!")
        return {}
    
    print(f"\nFetching data for {len(symbols)} stocks...")
    print("-" * 80)
    
    data_dict = {}
    
    for i, symbol in enumerate(symbols, 1):
        try:
            print(f"[{i}/{len(symbols)}] Checking {symbol}...", end=" ")
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            price = info.get('currentPrice', info.get('regularMarketPrice', 0))
            float_shares = info.get('floatShares', info.get('sharesOutstanding', float('inf')))
            
            if price < strategy.min_price or price > strategy.max_price:
                print(f"Price ${price:.2f} out of range")
                continue
            
            if float_shares > strategy.max_float:
                print(f"Float {float_shares/1_000_000:.1f}M too high")
                continue
            
            strategy.stock_info[symbol] = {'price': price, 'float': float_shares}
            
            # Fetch 30 days of daily data for criteria checking
            daily_df = ticker.history(period="30d", interval="1d")
            if not daily_df.empty and len(daily_df) >= 20:
                # Calculate 20-day average volume
                daily_df['avg_volume_20'] = daily_df['Volume'].rolling(window=20).mean()
                # Calculate relative volume (daily volume / 20-day average)
                daily_df['rel_volume'] = daily_df['Volume'] / daily_df['avg_volume_20']
                
                # Check daily criteria for past 10 days
                criteria_results = strategy.check_daily_criteria(symbol, daily_df)
                strategy.daily_criteria_met[symbol] = criteria_results
                
                # Count how many days met criteria
                days_met = sum(1 for met in criteria_results.values() if met)
                print(f"Daily criteria: {days_met}/10 days", end=" ")
            
            # Fetch intraday data for backtesting (yfinance limit is ~8 days for 1m data)
            df = ticker.history(period="7d", interval="1m")
            if df.empty:
                print("No intraday data")
                continue
            
            df.columns = df.columns.str.lower()
            df = df[['open', 'high', 'low', 'close', 'volume']]
            est = pytz.timezone('US/Eastern')
            df.index = df.index.tz_convert(est)
            df = df.between_time('09:30', '16:00')
            data_dict[symbol] = df
            print(f"${price:.2f}, {float_shares/1_000_000:.1f}M float")
            
        except Exception as e:
            print(f"{e}")
    
    return data_dict


if __name__ == "__main__":
    import sys
    
    print("=" * 80)
    print("Small-Cap Momentum HOD Strategy ($2-$20, Float<100M, RVol>2x)")
    print("=" * 80)
    
    strategy = MomentumHODStrategy()
    
    # Check if user provided symbols via command line
    if len(sys.argv) > 1:
        # User provided symbols as command line arguments
        symbols = sys.argv[1:]
        print(f"\nUsing {len(symbols)} symbols from command line")
    else:
        # Use Finviz to automatically screen for stocks
        print("\nUsing Finviz to automatically screen stocks...")
        symbols = screen_stocks_finviz(strategy)
        
        if not symbols:
            print("\nFinviz screening failed or returned no results")
            print("Please provide symbols manually:")
            print("Example: python trade.py SYMBOL1 SYMBOL2 SYMBOL3 ...")
            exit(1)
    
    data = fetch_data(symbols, strategy)
    
    if not data:
        print("\nNo stocks passed filters!")
        print("\nTroubleshooting:")
        print("1. Many stocks may be outside the $2-$20 price range")
        print("2. Float data might not be available for all stocks")
        print("3. Try providing your own list of symbols that you know meet the criteria")
        print("\nExample: python trade.py BKKT IONQ RKLB SPCE")
        exit(1)
    
    print(f"\n{len(data)} stocks passed filters and have data")
    
    results = strategy.backtest(data)
    
    if not results.empty:
        results.to_csv('backtest_results.csv', index=False)
        print(f"\nResults saved to backtest_results.csv")
        print("\nTrade Details:")
        print(results.to_string())
    else:
        print("\nNo trades were executed")
        print("This could mean:")
        print("- No stocks met momentum + HOD criteria during scanning hours")
        print("- Entry conditions (RSI, MACD, Volume) were not satisfied")
        print("- Try different stocks or adjust strategy parameters")
