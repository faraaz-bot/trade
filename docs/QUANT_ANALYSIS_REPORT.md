# COMPREHENSIVE QUANTITATIVE BACKTEST ANALYSIS REPORT

**Strategy:** Momentum HOD Strategy (Small Cap Edition)  
**Period:** December 19-30, 2025  
**Criteria:** Price $1-$10, Float <30M shares, RVol >2x  
**Generated:** December 30, 2025 at 07:13 PM

---

## EXECUTIVE SUMMARY

| Metric | Value |
|--------|-------|
| **Total Trades** | 199 |
| **Winning Trades** | 99 (49.75%) |
| **Losing Trades** | 97 (48.74%) |
| **Total P&L** | **$828.10** |
| **Average P&L per Trade** | $4.16 |
| **Largest Win** | $218.95 |
| **Largest Loss** | $-144.50 |
| **Profit Factor** | 1.23 |
| **Sharpe Ratio (estimated)** | 0.08 |

---

## DETAILED PERFORMANCE METRICS

### Win/Loss Statistics

| Category | Count | Percentage | Total P&L | Avg P&L |
|----------|-------|------------|-----------|---------|
| **Winning Trades** | 99 | 49.75% | $4433.51 | $44.78 |
| **Losing Trades** | 97 | 48.74% | $3605.41 | $-37.17 |
| **Breakeven Trades** | 3 | 1.51% | $0.00 | $0.00 |

### Risk Metrics

| Metric | Value |
|--------|-------|
| **Profit Factor** | 1.23 (Total Wins / Total Losses) |
| **Win Rate** | 49.75% |
| **Average Win** | $44.78 |
| **Average Loss** | $-37.17 |
| **Win/Loss Ratio** | 1.20 |
| **Expectancy** | $4.16 per trade |
| **Standard Deviation** | $52.93 |
| **Maximum Drawdown** | $-144.50 (single trade) |

### Return Distribution

| Percentile | P&L % |
|------------|-------|
| **95th** | 20.07% |
| **75th** | 6.44% |
| **50th (Median)** | 0.00% |
| **25th** | -3.37% |
| **5th** | -5.06% |

---

## TOP PERFORMERS

### Best Stocks by Total P&L (Top 10)

| Symbol | Trades | Win Rate | Total P&L | Avg P&L | Best Trade |
|--------|--------|----------|-----------|---------|------------|
| **SOPA** | 17 | 70.6% | **$494.38** | $29.08 | $130.85 |
| **CETX** | 8 | 50.0% | **$454.30** | $56.79 | $218.95 |
| **ONTF** | 2 | 100.0% | **$372.82** | $186.41 | $190.92 |
| **EQ** | 11 | 63.6% | **$217.18** | $19.74 | $110.41 |
| **AP** | 2 | 100.0% | **$207.89** | $103.95 | $173.44 |
| **MMA** | 4 | 100.0% | **$179.38** | $44.84 | $77.35 |
| **OPAL** | 6 | 66.7% | **$127.07** | $21.18 | $81.26 |
| **ILAG** | 3 | 66.7% | **$100.94** | $33.65 | $100.48 |
| **DEVS** | 2 | 100.0% | **$73.20** | $36.60 | $42.09 |
| **AUNA** | 2 | 100.0% | **$66.70** | $33.35 | $36.18 |

### Worst Stocks by Total P&L (Bottom 10)

| Symbol | Trades | Win Rate | Total P&L | Avg P&L | Worst Trade |
|--------|--------|----------|-----------|---------|-------------|
| **USEA** | 2 | 0.0% | **$-93.27** | $-46.64 | $-58.41 |
| **RPID** | 4 | 0.0% | **$-104.03** | $-26.01 | $-33.20 |
| **LPCN** | 3 | 0.0% | **$-110.31** | $-36.77 | $-38.00 |
| **ORIS** | 5 | 40.0% | **$-126.83** | $-25.37 | $-78.84 |
| **ASRT** | 4 | 0.0% | **$-127.21** | $-31.80 | $-36.97 |
| **NBY** | 14 | 35.7% | **$-128.04** | $-9.15 | $-73.54 |
| **ASTI** | 4 | 0.0% | **$-142.10** | $-35.52 | $-38.73 |
| **BOXL** | 8 | 25.0% | **$-149.67** | $-18.71 | $-57.16 |
| **BRLS** | 8 | 50.0% | **$-181.66** | $-22.71 | $-144.50 |
| **DRMA** | 6 | 0.0% | **$-296.47** | $-49.41 | $-67.87 |

---

## EXIT STRATEGY ANALYSIS

| Exit Reason | Count | % of Total | Avg P&L | Win Rate |
|-------------|-------|------------|---------|----------|
| **SCALE_OUT_6%** | 43 | 21.61% | $46.04 | 100.00% |
| **STOP_LOSS** | 90 | 45.23% | $-39.63 | 0.00% |
| **TRAILING_STOP** | 40 | 20.10% | $51.20 | 100.00% |
| **END_OF_DATA** | 26 | 13.07% | $14.11 | 61.54% |

---

## STATISTICAL ANALYSIS

### P&L Distribution

```
Mean:           $4.16
Median:         $0.00
Std Deviation:  $52.93
Skewness:       1.31
Kurtosis:       3.00
```

### Risk-Adjusted Returns

**Sharpe Ratio Analysis:**
```
Average Return per Trade: $4.16
Standard Deviation: $52.93
Sharpe Ratio: 0.08 per trade
```

---

## POSITION SIZING RECOMMENDATIONS

### Kelly Criterion

```
Win Rate: 49.75%
Avg Win: $44.78
Avg Loss: $-37.17
Kelly %: 8.0%
```

**Recommendation:** Use half-Kelly for conservative approach

---

## STRATEGY STRENGTHS

1. **Positive Expectancy:** $4.16 per trade
2. **Win Rate:** 49.75% (Below 50%)
3. **Profit Factor:** 1.23 (Profitable)
4. **Total Profit:** $828.10

---

## RECOMMENDATIONS FOR LIVE TRADING

### ✅ DO:
1. Start with small position sizes (1-2% of capital)
2. Track every trade in a journal
3. Review performance weekly
4. Focus on high-probability setups (stocks with >50% win rate)
5. Implement strict risk management

### ❌ DON'T:
1. Overtrade - stick to best setups only
2. Revenge trade after losses
3. Ignore stop losses
4. Risk more than 5% of capital on any single trade

---

## CONCLUSION

The strategy demonstrates a positive edge with:
- **49.7% win rate**
- **$828.10 total profit** over 199 trades
- **1.23 profit factor**

**Risk Disclaimer:** Past performance does not guarantee future results. Always use proper risk management.

---

*Report generated automatically by generate_quant_report.py*
