# COMPREHENSIVE QUANTITATIVE BACKTEST ANALYSIS REPORT

**Strategy:** Momentum HOD Strategy (Small Cap Edition)  
**Period:** December 22-30, 2025  
**Criteria:** Price $1-$10, Float <30M shares, RVol >2x  
**Generated:** December 30, 2025 at 09:53 PM

---

## EXECUTIVE SUMMARY

| Metric | Value |
|--------|-------|
| **Total Trades** | 8 |
| **Winning Trades** | 6 (75.00%) |
| **Losing Trades** | 2 (25.00%) |
| **Total P&L** | **$366.51** |
| **Average P&L per Trade** | $45.81 |
| **Largest Win** | $133.97 |
| **Largest Loss** | $-57.75 |
| **Profit Factor** | 4.36 |
| **Sharpe Ratio (estimated)** | 0.64 |

---

## DETAILED PERFORMANCE METRICS

### Win/Loss Statistics

| Category | Count | Percentage | Total P&L | Avg P&L |
|----------|-------|------------|-----------|---------|
| **Winning Trades** | 6 | 75.00% | $475.61 | $79.27 |
| **Losing Trades** | 2 | 25.00% | $109.10 | $-54.55 |
| **Breakeven Trades** | 0 | 0.00% | $0.00 | $0.00 |

### Risk Metrics

| Metric | Value |
|--------|-------|
| **Profit Factor** | 4.36 (Total Wins / Total Losses) |
| **Win Rate** | 75.00% |
| **Average Win** | $79.27 |
| **Average Loss** | $-54.55 |
| **Win/Loss Ratio** | 1.45 |
| **Expectancy** | $45.81 per trade |
| **Standard Deviation** | $71.38 |
| **Maximum Drawdown** | $-57.75 (single trade) |

### Return Distribution

| Percentile | P&L % |
|------------|-------|
| **95th** | 20.98% |
| **75th** | 20.07% |
| **50th (Median)** | 13.46% |
| **25th** | 4.20% |
| **5th** | -5.55% |

---

## TOP PERFORMERS

### Best Stocks by Total P&L (Top 10)

| Symbol | Trades | Win Rate | Total P&L | Avg P&L | Best Trade |
|--------|--------|----------|-----------|---------|------------|
| **SOPA** | 5 | 80.0% | **$344.19** | $68.84 | $133.97 |
| **EQ** | 2 | 100.0% | **$80.07** | $40.04 | $55.92 |
| **DRMA** | 1 | 0.0% | **$-57.75** | $-57.75 | $-57.75 |

### Worst Stocks by Total P&L (Bottom 10)

| Symbol | Trades | Win Rate | Total P&L | Avg P&L | Worst Trade |
|--------|--------|----------|-----------|---------|-------------|
| **SOPA** | 5 | 80.0% | **$344.19** | $68.84 | $-51.35 |
| **EQ** | 2 | 100.0% | **$80.07** | $40.04 | $24.15 |
| **DRMA** | 1 | 0.0% | **$-57.75** | $-57.75 | $-57.75 |

---

## EXIT STRATEGY ANALYSIS

| Exit Reason | Count | % of Total | Avg P&L | Win Rate |
|-------------|-------|------------|---------|----------|
| **SCALE_OUT_8%** | 3 | 37.50% | $104.57 | 100.00% |
| **TRAILING_STOP** | 3 | 37.50% | $53.97 | 100.00% |
| **STOP_LOSS** | 2 | 25.00% | $-54.55 | 0.00% |

---

## STATISTICAL ANALYSIS

### P&L Distribution

```
Mean:           $45.81
Median:         $61.31
Std Deviation:  $71.38
Skewness:       -0.45
Kurtosis:       -0.91
```

### Risk-Adjusted Returns

**Sharpe Ratio Analysis:**
```
Average Return per Trade: $45.81
Standard Deviation: $71.38
Sharpe Ratio: 0.64 per trade
```

---

## POSITION SIZING RECOMMENDATIONS

### Kelly Criterion

```
Win Rate: 75.00%
Avg Win: $79.27
Avg Loss: $-54.55
Kelly %: 57.8%
```

**Recommendation:** Use half-Kelly for conservative approach

---

## STRATEGY STRENGTHS

1. **Positive Expectancy:** $45.81 per trade
2. **Win Rate:** 75.00% (Above 50%)
3. **Profit Factor:** 4.36 (Profitable)
4. **Total Profit:** $366.51

---

## RECOMMENDATIONS FOR LIVE TRADING

### DO:
1. Start with small position sizes (1-2% of capital)
2. Track every trade in a journal
3. Review performance weekly
4. Focus on high-probability setups (stocks with >75% win rate)
5. Implement strict risk management

### DON'T:
1. Overtrade - stick to best setups only
2. Revenge trade after losses
3. Ignore stop losses
4. Risk more than 5% of capital on any single trade

---

## CONCLUSION

The strategy demonstrates a positive edge with:
- **75.0% win rate**
- **$366.51 total profit** over 8 trades
- **4.36 profit factor**

**Risk Disclaimer:** Past performance does not guarantee future results. Always use proper risk management.

---

*Report generated automatically by generate_quant_report.py*
