"""
Quantitative Analysis Report Generator
Automatically generates comprehensive analysis from backtest results
"""

import pandas as pd
import numpy as np
from datetime import datetime


def generate_quant_report(trades_df, output_file='QUANT_ANALYSIS_REPORT.md'):
    """Generate comprehensive quantitative analysis report"""
    
    if trades_df.empty:
        print("No trades to analyze!")
        return
    
    # Calculate statistics
    total_trades = len(trades_df)
    winning_trades = len(trades_df[trades_df['pnl'] > 0])
    losing_trades = len(trades_df[trades_df['pnl'] < 0])
    breakeven_trades = len(trades_df[trades_df['pnl'] == 0])
    
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
    
    total_pnl = trades_df['pnl'].sum()
    avg_pnl = trades_df['pnl'].mean()
    
    wins = trades_df[trades_df['pnl'] > 0]
    losses = trades_df[trades_df['pnl'] < 0]
    
    total_wins = wins['pnl'].sum() if len(wins) > 0 else 0
    total_losses = abs(losses['pnl'].sum()) if len(losses) > 0 else 1
    
    avg_win = wins['pnl'].mean() if len(wins) > 0 else 0
    avg_loss = losses['pnl'].mean() if len(losses) > 0 else 0
    
    profit_factor = total_wins / total_losses if total_losses > 0 else 0
    
    largest_win = trades_df['pnl'].max()
    largest_loss = trades_df['pnl'].min()
    
    std_dev = trades_df['pnl'].std()
    sharpe = (avg_pnl / std_dev) if std_dev > 0 else 0
    
    # Per-symbol analysis
    symbol_stats = []
    for symbol in trades_df['symbol'].unique():
        symbol_trades = trades_df[trades_df['symbol'] == symbol]
        symbol_wins = len(symbol_trades[symbol_trades['pnl'] > 0])
        symbol_total = len(symbol_trades)
        symbol_win_rate = (symbol_wins / symbol_total * 100) if symbol_total > 0 else 0
        
        symbol_stats.append({
            'symbol': symbol,
            'trades': symbol_total,
            'win_rate': symbol_win_rate,
            'total_pnl': symbol_trades['pnl'].sum(),
            'avg_pnl': symbol_trades['pnl'].mean(),
            'best_trade': symbol_trades['pnl'].max()
        })
    
    symbol_df = pd.DataFrame(symbol_stats).sort_values('total_pnl', ascending=False)
    
    # Exit reason analysis
    exit_stats = trades_df.groupby('reason').agg({
        'pnl': ['count', 'mean', 'sum'],
        'symbol': 'count'
    }).reset_index()
    
    # Generate report
    report = f"""# COMPREHENSIVE QUANTITATIVE BACKTEST ANALYSIS REPORT

**Strategy:** Momentum HOD Strategy (Small Cap Edition)  
**Period:** {trades_df['entry_time'].min().strftime('%B %d')}-{trades_df['exit_time'].max().strftime('%d, %Y')}  
**Criteria:** Price $1-$10, Float <30M shares, RVol >2x  
**Generated:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

---

## EXECUTIVE SUMMARY

| Metric | Value |
|--------|-------|
| **Total Trades** | {total_trades} |
| **Winning Trades** | {winning_trades} ({win_rate:.2f}%) |
| **Losing Trades** | {losing_trades} ({losing_trades/total_trades*100:.2f}%) |
| **Total P&L** | **${total_pnl:.2f}** |
| **Average P&L per Trade** | ${avg_pnl:.2f} |
| **Largest Win** | ${largest_win:.2f} |
| **Largest Loss** | ${largest_loss:.2f} |
| **Profit Factor** | {profit_factor:.2f} |
| **Sharpe Ratio (estimated)** | {sharpe:.2f} |

---

## DETAILED PERFORMANCE METRICS

### Win/Loss Statistics

| Category | Count | Percentage | Total P&L | Avg P&L |
|----------|-------|------------|-----------|---------|
| **Winning Trades** | {winning_trades} | {win_rate:.2f}% | ${total_wins:.2f} | ${avg_win:.2f} |
| **Losing Trades** | {losing_trades} | {losing_trades/total_trades*100:.2f}% | ${total_losses:.2f} | ${avg_loss:.2f} |
| **Breakeven Trades** | {breakeven_trades} | {breakeven_trades/total_trades*100:.2f}% | $0.00 | $0.00 |

### Risk Metrics

| Metric | Value |
|--------|-------|
| **Profit Factor** | {profit_factor:.2f} (Total Wins / Total Losses) |
| **Win Rate** | {win_rate:.2f}% |
| **Average Win** | ${avg_win:.2f} |
| **Average Loss** | ${avg_loss:.2f} |
| **Win/Loss Ratio** | {abs(avg_win/avg_loss) if avg_loss != 0 else 0:.2f} |
| **Expectancy** | ${avg_pnl:.2f} per trade |
| **Standard Deviation** | ${std_dev:.2f} |
| **Maximum Drawdown** | ${largest_loss:.2f} (single trade) |

### Return Distribution

| Percentile | P&L % |
|------------|-------|
| **95th** | {trades_df['pnl_pct'].quantile(0.95):.2f}% |
| **75th** | {trades_df['pnl_pct'].quantile(0.75):.2f}% |
| **50th (Median)** | {trades_df['pnl_pct'].median():.2f}% |
| **25th** | {trades_df['pnl_pct'].quantile(0.25):.2f}% |
| **5th** | {trades_df['pnl_pct'].quantile(0.05):.2f}% |

---

## TOP PERFORMERS

### Best Stocks by Total P&L (Top 10)

| Symbol | Trades | Win Rate | Total P&L | Avg P&L | Best Trade |
|--------|--------|----------|-----------|---------|------------|
"""
    
    # Add top 10 performers
    for _, row in symbol_df.head(10).iterrows():
        report += f"| **{row['symbol']}** | {row['trades']} | {row['win_rate']:.1f}% | **${row['total_pnl']:.2f}** | ${row['avg_pnl']:.2f} | ${row['best_trade']:.2f} |\n"
    
    report += f"""
### Worst Stocks by Total P&L (Bottom 10)

| Symbol | Trades | Win Rate | Total P&L | Avg P&L | Worst Trade |
|--------|--------|----------|-----------|---------|-------------|
"""
    
    # Add bottom 10 performers
    for _, row in symbol_df.tail(10).iterrows():
        worst_trade = trades_df[trades_df['symbol'] == row['symbol']]['pnl'].min()
        report += f"| **{row['symbol']}** | {row['trades']} | {row['win_rate']:.1f}% | **${row['total_pnl']:.2f}** | ${row['avg_pnl']:.2f} | ${worst_trade:.2f} |\n"
    
    # Exit reason analysis
    report += f"""
---

## EXIT STRATEGY ANALYSIS

| Exit Reason | Count | % of Total | Avg P&L | Win Rate |
|-------------|-------|------------|---------|----------|
"""
    
    for reason in trades_df['reason'].unique():
        reason_trades = trades_df[trades_df['reason'] == reason]
        reason_count = len(reason_trades)
        reason_pct = (reason_count / total_trades * 100)
        reason_avg_pnl = reason_trades['pnl'].mean()
        reason_wins = len(reason_trades[reason_trades['pnl'] > 0])
        reason_win_rate = (reason_wins / reason_count * 100) if reason_count > 0 else 0
        
        report += f"| **{reason}** | {reason_count} | {reason_pct:.2f}% | ${reason_avg_pnl:.2f} | {reason_win_rate:.2f}% |\n"
    
    report += f"""
---

## STATISTICAL ANALYSIS

### P&L Distribution

```
Mean:           ${avg_pnl:.2f}
Median:         ${trades_df['pnl'].median():.2f}
Std Deviation:  ${std_dev:.2f}
Skewness:       {trades_df['pnl'].skew():.2f}
Kurtosis:       {trades_df['pnl'].kurtosis():.2f}
```

### Risk-Adjusted Returns

**Sharpe Ratio Analysis:**
```
Average Return per Trade: ${avg_pnl:.2f}
Standard Deviation: ${std_dev:.2f}
Sharpe Ratio: {sharpe:.2f} per trade
```

---

## POSITION SIZING RECOMMENDATIONS

### Kelly Criterion

```
Win Rate: {win_rate:.2f}%
Avg Win: ${avg_win:.2f}
Avg Loss: ${avg_loss:.2f}
Kelly %: {((win_rate/100) - ((100-win_rate)/100) / (abs(avg_win/avg_loss) if avg_loss != 0 else 1)) * 100:.1f}%
```

**Recommendation:** Use half-Kelly for conservative approach

---

## STRATEGY STRENGTHS

1. **{'Positive' if total_pnl > 0 else 'Negative'} Expectancy:** ${avg_pnl:.2f} per trade
2. **Win Rate:** {win_rate:.2f}% ({'Above' if win_rate > 50 else 'Below'} 50%)
3. **Profit Factor:** {profit_factor:.2f} ({'Profitable' if profit_factor > 1 else 'Unprofitable'})
4. **Total Profit:** ${total_pnl:.2f}

---

## RECOMMENDATIONS FOR LIVE TRADING

### DO:
1. Start with small position sizes (1-2% of capital)
2. Track every trade in a journal
3. Review performance weekly
4. Focus on high-probability setups (stocks with >{win_rate:.0f}% win rate)
5. Implement strict risk management

### DON'T:
1. Overtrade - stick to best setups only
2. Revenge trade after losses
3. Ignore stop losses
4. Risk more than 5% of capital on any single trade

---

## CONCLUSION

The strategy {'demonstrates a positive edge' if total_pnl > 0 else 'needs optimization'} with:
- **{win_rate:.1f}% win rate**
- **${total_pnl:.2f} total profit** over {total_trades} trades
- **{profit_factor:.2f} profit factor**

**Risk Disclaimer:** Past performance does not guarantee future results. Always use proper risk management.

---

*Report generated automatically by generate_quant_report.py*
"""
    
    # Save report
    with open(output_file, 'w') as f:
        f.write(report)
    
    print(f"\nQuantitative analysis report saved to {output_file}")
    return output_file


if __name__ == "__main__":
    # Load backtest results
    try:
        trades_df = pd.read_csv('backtest_results.csv')
        trades_df['entry_time'] = pd.to_datetime(trades_df['entry_time'])
        trades_df['exit_time'] = pd.to_datetime(trades_df['exit_time'])
        
        generate_quant_report(trades_df)
    except FileNotFoundError:
        print("Error: backtest_results.csv not found!")
        print("Run the backtest first: python trade.py or python dashboard.py")
