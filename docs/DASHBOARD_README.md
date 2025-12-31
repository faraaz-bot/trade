# Professional Trading Dashboard

A TradingView-style dashboard for analyzing your trading backtest results with interactive charts and comprehensive trade analysis.

## Features

### 📊 **Unified Trade View**
- All trades displayed in a sortable, filterable table
- Sort by:
  - Biggest Winners
  - Biggest Losers
  - Most Recent
  - Symbol
- Filter by symbol and exit reason

### 📈 **Professional Charts**
- TradingView-style dark theme
- Interactive candlestick charts with:
  - **EMAs**: 9, 50, 100 period
  - **VWAP**: Volume Weighted Average Price
  - **Volume bars**: Color-coded (green/red)
  - **MACD**: With signal line and histogram
  - **RSI**: With overbought (70) and oversold (30) levels
- **Entry/Exit Markers**:
  - Green arrow up for entries with price
  - Red arrow down for exits with price and P&L%
  - Clear time and price labels

### 📉 **Performance Metrics**
- Total Trades
- Win Rate
- Total P&L
- Average Win
- Average Loss

## Installation

### 1. Install Required Packages

```bash
source venv/bin/activate
pip install streamlit plotly
```

### 2. Run a Backtest First

Generate trade data by running your backtest:

```bash
python trade.py
# or
python trade.py SYMBOL1 SYMBOL2 SYMBOL3
```

This creates `backtest_results.csv` which the dashboard reads.

## Usage

### Launch the Dashboard

```bash
streamlit run trading_dashboard.py
```

The dashboard will open in your default web browser at `http://localhost:8501`

### Navigation

1. **Metrics Overview** (Top)
   - View overall performance statistics

2. **Sidebar** (Left)
   - **Sort By**: Choose how to order trades
   - **Filter by Symbol**: View trades for specific stocks
   - **Filter by Exit Reason**: Analyze by exit type

3. **Trade History Table** (Middle)
   - Scrollable table with all trade details
   - Click column headers to sort

4. **Trade Charts** (Bottom)
   - Select any trade from dropdown
   - View detailed chart with all indicators
   - See entry/exit points marked clearly

### Chart Features

- **Zoom**: Click and drag on chart
- **Pan**: Hold shift and drag
- **Reset**: Double-click chart
- **Hover**: See detailed values at any point
- **Legend**: Click to show/hide indicators

## Dashboard Sections

### 1. Performance Metrics
```
Total Trades | Win Rate | Total P&L | Avg Win | Avg Loss
```

### 2. Trade History Table
Columns:
- Symbol
- Entry Time
- Exit Time
- Entry Price
- Exit Price
- Shares
- P&L ($)
- P&L (%)
- Exit Reason

### 3. Interactive Charts
Four panels:
1. **Price Chart**: Candlesticks + EMAs + VWAP + Entry/Exit markers
2. **Volume**: Color-coded volume bars
3. **MACD**: MACD line, Signal line, Histogram
4. **RSI**: RSI with 70/30 levels

## Tips

### Finding Best Trades
1. Sort by "Biggest Winners" to see your most profitable trades
2. Click on a trade to see the chart
3. Analyze what indicators aligned at entry

### Analyzing Losses
1. Sort by "Biggest Losers"
2. Review charts to identify patterns
3. Check exit reasons to understand what triggered stops

### Symbol Analysis
1. Filter by specific symbol
2. Review all trades for that stock
3. Identify if certain stocks perform better

### Exit Reason Analysis
1. Filter by exit reason (STOP_LOSS, TAKE_PROFIT, etc.)
2. See which exit types are most common
3. Optimize your exit strategy

## Color Coding

- **Green (#26A69A)**: Profits, bullish candles, entry markers
- **Red (#EF5350)**: Losses, bearish candles, exit markers
- **Blue (#2962FF)**: MACD, RSI, EMA 9
- **Orange (#FF6D00)**: EMA 50, MACD Signal
- **Purple (#9C27B0)**: EMA 100
- **Yellow (#FDD835)**: VWAP

## Keyboard Shortcuts

When viewing charts:
- **Scroll**: Zoom in/out
- **Shift + Drag**: Pan chart
- **Double-click**: Reset zoom
- **Click legend**: Toggle indicator visibility

## Troubleshooting

### "No trades found"
- Run `python trade.py` first to generate backtest results
- Ensure `backtest_results.csv` exists in the same directory

### Chart not loading
- Check internet connection (needs to fetch stock data)
- Try selecting a different trade
- Some older trades may not have minute data available

### Dashboard won't start
- Ensure streamlit is installed: `pip install streamlit`
- Check you're in the virtual environment: `source venv/bin/activate`
- Try: `streamlit run trading_dashboard.py --server.port 8502`

## Advanced Features

### Custom Time Ranges
The dashboard automatically fetches data around your trade times. For longer views, the code can be modified in `get_stock_data()`.

### Export Trades
The trade table can be copied directly from the browser for further analysis in Excel or other tools.

### Multiple Dashboards
Run multiple instances on different ports:
```bash
streamlit run trading_dashboard.py --server.port 8502
```

## Comparison to Old HTML Dashboards

### Old (HTML files):
- ❌ Static, non-interactive
- ❌ Separate file for each stock
- ❌ No sorting or filtering
- ❌ Basic styling

### New (Streamlit Dashboard):
- ✅ Fully interactive
- ✅ All trades in one place
- ✅ Sort and filter capabilities
- ✅ Professional TradingView-style design
- ✅ Real-time data fetching
- ✅ Comprehensive indicators
- ✅ Clear entry/exit markers

## Next Steps

1. Run backtests regularly to populate the dashboard
2. Use filters to identify patterns
3. Analyze winning vs losing trades
4. Refine your strategy based on insights
5. Track performance over time

---

**Note**: The dashboard reads from `backtest_results.csv`. Each time you run a new backtest, the dashboard will update with the latest results.
