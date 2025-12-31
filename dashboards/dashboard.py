"""
Interactive Trading Dashboard
Displays 1-minute charts with indicators and entry/exit points
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
from datetime import datetime
import pytz
from trade import MomentumHODStrategy, fetch_data


def create_trade_chart(symbol, df, trades_df, strategy):
    """Create interactive chart for a single stock with all indicators"""
    
    # Filter trades for this symbol
    symbol_trades = trades_df[trades_df['symbol'] == symbol]
    
    if symbol_trades.empty:
        print(f"No trades found for {symbol}")
        return None
    
    # Create subplots: Candlestick + EMAs + VWAP, MACD, RSI
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        subplot_titles=(f'{symbol} - 1 Minute Chart', 'MACD', 'RSI'),
        row_heights=[0.6, 0.2, 0.2]
    )
    
    # Main candlestick chart
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name='Price',
            increasing_line_color='green',
            decreasing_line_color='red'
        ),
        row=1, col=1
    )
    
    # Add EMAs
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['ema_9'],
            name='EMA 9',
            line=dict(color='blue', width=1.5)
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['ema_50'],
            name='EMA 50',
            line=dict(color='orange', width=1.5)
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['ema_100'],
            name='EMA 100',
            line=dict(color='purple', width=1.5)
        ),
        row=1, col=1
    )
    
    # Add VWAP
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['vwap'],
            name='VWAP',
            line=dict(color='yellow', width=2, dash='dash')
        ),
        row=1, col=1
    )
    
    # Add entry and exit markers
    for _, trade in symbol_trades.iterrows():
        # Entry marker (green arrow up)
        fig.add_trace(
            go.Scatter(
                x=[trade['entry_time']],
                y=[trade['entry_price']],
                mode='markers+text',
                marker=dict(
                    symbol='triangle-up',
                    size=15,
                    color='lime',
                    line=dict(color='darkgreen', width=2)
                ),
                text=['BUY'],
                textposition='top center',
                textfont=dict(size=10, color='darkgreen'),
                name=f"Entry ${trade['entry_price']:.2f}",
                showlegend=False
            ),
            row=1, col=1
        )
        
        # Exit marker (red arrow down)
        exit_color = 'red' if trade['pnl'] < 0 else 'lime'
        fig.add_trace(
            go.Scatter(
                x=[trade['exit_time']],
                y=[trade['exit_price']],
                mode='markers+text',
                marker=dict(
                    symbol='triangle-down',
                    size=15,
                    color=exit_color,
                    line=dict(color='darkred' if trade['pnl'] < 0 else 'darkgreen', width=2)
                ),
                text=[f"SELL\n{trade['reason']}\n{trade['pnl_pct']:.1f}%"],
                textposition='bottom center',
                textfont=dict(size=8, color='darkred' if trade['pnl'] < 0 else 'darkgreen'),
                name=f"Exit ${trade['exit_price']:.2f}",
                showlegend=False
            ),
            row=1, col=1
        )
    
    # MACD subplot
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['macd'],
            name='MACD',
            line=dict(color='blue', width=1)
        ),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['macd_signal'],
            name='Signal',
            line=dict(color='red', width=1)
        ),
        row=2, col=1
    )
    
    # MACD histogram
    macd_hist = df['macd'] - df['macd_signal']
    colors = ['green' if val >= 0 else 'red' for val in macd_hist]
    fig.add_trace(
        go.Bar(
            x=df.index,
            y=macd_hist,
            name='MACD Hist',
            marker_color=colors,
            opacity=0.3
        ),
        row=2, col=1
    )
    
    # RSI subplot
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['rsi'],
            name='RSI',
            line=dict(color='purple', width=1.5)
        ),
        row=3, col=1
    )
    
    # RSI reference lines
    fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.5, row=3, col=1)
    fig.add_hline(y=60, line_dash="dash", line_color="orange", opacity=0.5, row=3, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.5, row=3, col=1)
    
    # Update layout
    fig.update_layout(
        title=f'{symbol} Trading Dashboard - {len(symbol_trades)} Trade(s)',
        xaxis_rangeslider_visible=False,
        height=900,
        showlegend=True,
        hovermode='x unified',
        template='plotly_dark'
    )
    
    # Update y-axes labels
    fig.update_yaxes(title_text="Price ($)", row=1, col=1)
    fig.update_yaxes(title_text="MACD", row=2, col=1)
    fig.update_yaxes(title_text="RSI", row=3, col=1)
    fig.update_xaxes(title_text="Time", row=3, col=1)
    
    return fig


def create_dashboard(strategy, data_dict, trades_df):
    """Create dashboard for all traded symbols"""
    
    if trades_df.empty:
        print("No trades to display!")
        return
    
    # Get unique symbols that were traded
    traded_symbols = trades_df['symbol'].unique()
    
    print(f"\n{'='*80}")
    print(f"CREATING INTERACTIVE DASHBOARD FOR {len(traded_symbols)} SYMBOL(S)")
    print(f"{'='*80}\n")
    
    for symbol in traded_symbols:
        print(f"Generating chart for {symbol}...")
        
        # Get the data for this symbol
        if symbol not in data_dict:
            print(f"  No data available for {symbol}")
            continue
        
        df = data_dict[symbol]
        
        # Create the chart
        fig = create_trade_chart(symbol, df, trades_df, strategy)
        
        if fig:
            # Save to HTML file
            filename = f"dashboard_{symbol}.html"
            fig.write_html(filename)
            print(f"  Saved to {filename}")
            
            # Show trade summary for this symbol
            symbol_trades = trades_df[trades_df['symbol'] == symbol]
            total_pnl = symbol_trades['pnl'].sum()
            win_rate = (len(symbol_trades[symbol_trades['pnl'] > 0]) / len(symbol_trades) * 100)
            
            print(f"  Trades: {len(symbol_trades)} | Win Rate: {win_rate:.1f}% | Total PnL: ${total_pnl:.2f}")
    
    # Create summary dashboard with all symbols
    print(f"\n{'='*80}")
    print("TRADE SUMMARY")
    print(f"{'='*80}")
    
    summary_data = []
    for symbol in traded_symbols:
        symbol_trades = trades_df[trades_df['symbol'] == symbol]
        summary_data.append({
            'Symbol': symbol,
            'Trades': len(symbol_trades),
            'Wins': len(symbol_trades[symbol_trades['pnl'] > 0]),
            'Losses': len(symbol_trades[symbol_trades['pnl'] < 0]),
            'Win Rate %': len(symbol_trades[symbol_trades['pnl'] > 0]) / len(symbol_trades) * 100,
            'Total PnL': symbol_trades['pnl'].sum(),
            'Avg PnL': symbol_trades['pnl'].mean(),
            'Best Trade': symbol_trades['pnl'].max(),
            'Worst Trade': symbol_trades['pnl'].min()
        })
    
    summary_df = pd.DataFrame(summary_data)
    print(summary_df.to_string(index=False))
    
    print(f"\n{'='*80}")
    print(f"Dashboard files created successfully!")
    print(f"  Open dashboard_[SYMBOL].html files in your browser to view charts")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    import sys
    from trade import screen_stocks_finviz
    
    print("=" * 80)
    print("Trading Dashboard Generator")
    print("Criteria: Price $1-$10, Float <30M, RVol >2x")
    print("=" * 80)
    
    strategy = MomentumHODStrategy()
    
    # Check if user provided symbols
    if len(sys.argv) > 1:
        symbols = sys.argv[1:]
        print(f"\nUsing {len(symbols)} symbols from command line: {', '.join(symbols)}")
    else:
        # Use Finviz to automatically screen for stocks
        print("\nUsing Finviz to automatically screen stocks...")
        symbols = screen_stocks_finviz(strategy)
        
        if not symbols:
            print("\nFinviz screening failed or returned no results")
            print("Falling back to default test symbols...")
            symbols = ['BKKT', 'WKHS', 'CHPT', 'KOSS', 'CTRM', 'SENS']
    
    # Fetch data
    data_dict = fetch_data(symbols, strategy)
    
    if not data_dict:
        print("\nNo stocks passed filters!")
        print("Try providing different symbols that meet the criteria:")
        print("  Price: $1-$10")
        print("  Float: <30M shares")
        print("\nExample: python dashboard.py SYMBOL1 SYMBOL2 SYMBOL3")
        exit(1)
    
    print(f"\n{len(data_dict)} stocks passed filters and have data")
    
    # Prepare data with indicators before backtesting
    prepared_data = {}
    for symbol, df in data_dict.items():
        if not df.empty:
            prepared_data[symbol] = strategy.calculate_indicators(df)
    
    # Run backtest
    results = strategy.backtest(data_dict)
    
    if results.empty:
        print("\nNo trades were executed")
        print("This could mean:")
        print("- No stocks met momentum + HOD criteria during scanning hours")
        print("- Entry conditions (RSI, MACD, Volume) were not satisfied")
        print("- Try different stocks or adjust strategy parameters")
        exit(1)
    
    # Save results
    results.to_csv('backtest_results.csv', index=False)
    print(f"\nResults saved to backtest_results.csv")
    
    # Create dashboard with prepared data (includes indicators)
    create_dashboard(strategy, prepared_data, results)
    
    # Generate quantitative analysis report
    from generate_quant_report import generate_quant_report
    generate_quant_report(results)
