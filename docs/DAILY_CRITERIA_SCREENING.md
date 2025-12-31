# Daily Criteria Screening - Implementation Guide

## Overview

Your trading system has been enhanced to check if stocks meet your criteria **every single day** for the past 10 days. Stocks are only eligible for trading on days when they meet the criteria.

## What Changed

### 1. **Daily Criteria Validation**
- The system now fetches 30 days of daily data for each stock
- Calculates daily relative volume (daily volume vs 20-day average)
- Checks if stock met criteria for each of the past 10 trading days
- Stores results in `daily_criteria_met` dictionary

### 2. **Day-by-Day Trading Logic**
- Before adding a stock to the watchlist, the system checks if it met criteria **on that specific date**
- If a stock doesn't meet criteria on Day 5, it won't be traded on Day 5 (even if it met criteria on Days 1-4)
- Each trading day is independent

### 3. **Criteria Checked Daily**
For each of the past 10 days, the system verifies:
- Price in range: $1-$10
- Relative Volume: >2x (daily volume vs 20-day average)
- Float: <30M shares (static, doesn't change)

## How It Works

### Data Fetching Process
```
1. Fetch 30 days of daily OHLCV data
2. Calculate 20-day average volume
3. Calculate daily relative volume for each day
4. Check criteria for past 10 days
5. Store results: {symbol: {date: True/False}}
6. Fetch 10 days of 1-minute intraday data for backtesting
```

### Backtest Process
```
For each timestamp in backtest:
  1. Get current date
  2. For each stock:
     - Check if stock met criteria on THIS date
     - If NO → skip stock for this day
     - If YES → proceed with momentum/HOD checks
  3. Only trade stocks that passed daily criteria
```

## Output Example

When running the script, you'll see:

```
[1/50] Checking SYMBOL... Daily criteria: 7/10 days $5.23, 15.2M float
```

This shows:
- The stock met criteria on 7 out of 10 days
- Current price and float information

During backtest:
```
[2024-12-23 10:15] Added SYMBOL | $5.45 | RVol: 2.3x | Float: 15.2M | Met daily criteria
```

The "Met daily criteria" confirms the stock qualified on that specific date.

## Key Benefits

1. **Historical Accuracy**: Only trades stocks that actually met criteria on each day
2. **No Lookahead Bias**: Doesn't use future information
3. **Day-by-Day Validation**: Each day is independent
4. **Transparent**: Shows how many days each stock met criteria

## Usage

Run the script normally:

```bash
# Using Finviz screening
python trade.py

# Or with manual symbols
python trade.py SYMBOL1 SYMBOL2 SYMBOL3
```

## Data Requirements

- **30 days of daily data**: Needed to calculate 20-day volume average
- **10 days of intraday data**: For the actual backtest
- **Float data**: From yfinance (static)

## Viewing Historical Criteria Data

The system stores daily criteria results in `strategy.daily_criteria_met`:

```python
{
    'SYMBOL1': {
        datetime.date(2024, 12, 20): True,
        datetime.date(2024, 12, 21): True,
        datetime.date(2024, 12, 22): False,  # Didn't meet criteria this day
        ...
    },
    'SYMBOL2': { ... }
}
```

You can access this data after running the backtest to see which stocks met criteria on which days.

## Example: Creating a Criteria Report

Add this code after the backtest to see a detailed report:

```python
# After: results = strategy.backtest(data)

print("\n" + "=" * 80)
print("DAILY CRITERIA REPORT")
print("=" * 80)

for symbol in strategy.daily_criteria_met:
    criteria_days = strategy.daily_criteria_met[symbol]
    days_met = sum(1 for met in criteria_days.values() if met)
    print(f"\n{symbol}: Met criteria on {days_met}/10 days")
    
    for date, met in sorted(criteria_days.items()):
        status = "PASS" if met else "FAIL"
        print(f"  {date}: {status}")
```

## Technical Details

### New Class Attributes
- `daily_criteria_met`: Dictionary storing daily criteria results

### New Methods
- `check_daily_criteria(symbol, daily_df)`: Validates criteria for past 10 days
- `meets_criteria_for_date(symbol, check_date)`: Checks if stock met criteria on specific date

### Modified Methods
- `fetch_data()`: Now fetches 30 days of daily data + 10 days of intraday data
- `backtest()`: Validates daily criteria before allowing trades

## Notes

- The system uses **10 days** of historical screening (configurable by changing the loop in `check_daily_criteria`)
- Requires at least **20 days** of historical data to calculate volume averages
- Float data is static and doesn't change daily
- Price and relative volume are checked daily

## Troubleshooting

**Q: Stock shows "0/10 days" met criteria**
- Check if price was outside $1-$10 range
- Verify relative volume was >2x on those days
- Ensure float is <30M shares

**Q: No trades executed**
- Stocks may not have met criteria on any of the backtest days
- Try stocks you know meet the criteria
- Check the daily criteria report to see which days passed

**Q: Want to see which specific days met criteria**
- Use the example code above to print a detailed report
- Access `strategy.daily_criteria_met` dictionary directly

## Summary

Your system now implements true day-by-day screening:
- Checks criteria for each of the past 10 days
- Only trades stocks on days they meet criteria
- No lookahead bias
- Transparent reporting of which days passed
- Historical accuracy maintained
