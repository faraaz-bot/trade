# Momentum HOD Trading Strategy

A sophisticated momentum-based day trading strategy for small-cap stocks, featuring automated screening, backtesting, optimization, and visualization tools.

## 🎯 Strategy Overview

**Target**: Small-cap stocks with strong momentum
- **Price Range**: $1-$10
- **Float**: <30M shares
- **Relative Volume**: >2x average
- **Entry**: 9 EMA bounce with momentum confirmation
- **Exit**: Optimized multi-tier system

### Optimized Parameters (Tested on 1,280 combinations)

- **Stop Loss**: 5%
- **Take Profit**: 10%
- **Scale-Out**: 67% at 8% profit
- **Trailing Stop**: 5%
- **Win Rate**: 75% (Expected: 72.7%)
- **Average P&L**: $45.81 per trade

## 📁 Repository Structure

```
trade/
├── trade.py                    # Main strategy implementation
├── dashboards/                 # Visualization tools
│   ├── dashboard.py           # Interactive 1-minute charts
│   ├── trading_dashboard.py   # Alternative dashboard
│   └── generate_quant_report.py # Quantitative analysis
├── optimizers/                 # Parameter optimization
│   └── optimize_stops.py      # Exit strategy optimizer
├── results/                    # Backtest outputs
│   ├── backtest_results.csv   # Latest backtest results
│   ├── optimization_results.csv # Optimizer output
│   └── optimizer_output.log   # Detailed logs
├── docs/                       # Documentation
│   ├── DAILY_CRITERIA_SCREENING.md
│   ├── DASHBOARD_README.md
│   ├── QUANT_ANALYSIS_REPORT.md
│   └── optimized_result.md
└── venv/                       # Python virtual environment
```

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
cd ~/trade

# Activate virtual environment
source venv/bin/activate

# Install dependencies (if needed)
pip install yfinance finvizfinance pandas numpy plotly pytz
```

### Running the Strategy

```bash
# Run with automatic Finviz screening
python3 trade.py

# Run with specific symbols
python3 trade.py SYMBOL1 SYMBOL2 SYMBOL3
```

### Generate Dashboard

```bash
# Create interactive charts for all trades
python3 dashboards/dashboard.py
```

### Optimize Parameters

```bash
# Test 1,280 parameter combinations
python3 optimizers/optimize_stops.py
```

## 📊 Features

### 1. Automated Stock Screening
- **Finviz Integration**: Automatically finds stocks matching criteria
- **Multi-Factor Filtering**: Price, float, volume, relative volume
- **Daily Criteria Tracking**: Validates stocks met criteria on each trading day

### 2. Entry Conditions
- ✅ Price touches and bounces off 9 EMA (2 consecutive closes above)
- ✅ Cumulative volume >5M by entry time
- ✅ Volume surge on entry bar (1.5x average)
- ✅ RSI <60
- ✅ MACD > Signal
- ✅ Near HOD (within 10%)
- ✅ Close > 9 EMA
- ✅ Red candle volume < average volume

### 3. Exit Strategy (Optimized)
- **Initial Stop Loss**: 5% below entry
- **Scale-Out**: Sell 67% at 8% profit
- **Trailing Stop**: 5% from highest price (activated after scale-out)
- **Take Profit**: Full exit at 10% if no scale-out

### 4. Risk Management
- **Position Sizing**: $1,000 per trade
- **Market Close**: All positions closed by 3:55 PM EST
- **No Last-Day Entries**: Prevents overnight risk

### 5. Visualization
- **Interactive Charts**: 1-minute candlesticks with indicators
- **Entry/Exit Markers**: Visual trade points
- **Multiple Indicators**: EMA 9/50/100, VWAP, MACD, RSI
- **Trade Analytics**: Win rate, P&L, profit factor

## 📈 Performance Metrics

### Latest Backtest Results
- **Total Trades**: 8
- **Win Rate**: 75%
- **Total P&L**: $366.51
- **Average P&L**: $45.81
- **Best Trade**: +$133.97 (20.07%)
- **Profit Factor**: 2.98

### Stocks Traded
- **EQ**: 2 trades (100% win rate)
- **DRMA**: 1 trade (loss)
- **SOPA**: 5 trades (80% win rate)

## 🔧 Configuration

### Strategy Parameters (in `trade.py`)

```python
# Scanning window
self.scan_start_time = time(10, 0)  # 10 AM EST
self.scan_end_time = time(14, 0)    # 2 PM EST

# Exit parameters (OPTIMIZED)
self.stop_loss_pct = 0.05           # 5%
self.take_profit_pct = 0.10         # 10%
self.trailing_stop_pct = 0.05       # 5%
self.scale_out_target = 0.08        # 8%

# Filtering criteria
self.min_price = 1.0
self.max_price = 10.0
self.max_float = 30_000_000         # 30M shares
self.min_relative_volume = 2.0      # 2x average
```

## 📚 Documentation

- **[Daily Criteria Screening](docs/DAILY_CRITERIA_SCREENING.md)**: How the system validates stocks
- **[Dashboard Guide](docs/DASHBOARD_README.md)**: Using the visualization tools
- **[Quant Analysis](docs/QUANT_ANALYSIS_REPORT.md)**: Statistical analysis
- **[Optimization Results](docs/optimized_result.md)**: Parameter testing details

## 🛠️ Tools

### Main Strategy (`trade.py`)
- Core backtesting engine
- Finviz integration
- Daily criteria validation
- Position management

### Dashboard (`dashboards/dashboard.py`)
- Interactive Plotly charts
- 1-minute candlesticks
- Indicator overlays
- Trade markers

### Optimizer (`optimizers/optimize_stops.py`)
- Tests 1,280 parameter combinations
- Multi-metric evaluation (P&L, win rate, profit factor, expectancy)
- Composite scoring system
- CSV export of all results

### Quant Report (`dashboards/generate_quant_report.py`)
- Statistical analysis
- Performance metrics
- Trade distribution
- Risk/reward ratios

## 📝 Output Files

### Results Directory
- `backtest_results.csv`: Trade-by-trade results
- `optimization_results.csv`: All tested parameter combinations
- `optimizer_output.log`: Detailed optimization logs

### Dashboard Files
- `dashboard_[SYMBOL].html`: Interactive charts for each traded symbol

## ⚠️ Important Notes

1. **Historical Data Limitation**: yfinance provides ~7 days of 1-minute data
2. **Daily Criteria**: Stocks must meet criteria on the specific trading day
3. **No Lookahead Bias**: System validates criteria day-by-day
4. **Market Hours**: Only trades during 10 AM - 2 PM EST scanning window

## 🔄 Workflow

1. **Screen**: Finviz finds stocks matching criteria
2. **Filter**: Validate price, float, volume requirements
3. **Monitor**: Track stocks for momentum + HOD proximity
4. **Enter**: Execute on 9 EMA bounce with confirmation
5. **Manage**: Scale out at 8%, trail remaining position
6. **Exit**: Stop loss, trailing stop, or take profit
7. **Analyze**: Review results, optimize parameters

## 📊 Example Usage

```bash
# Full workflow
python3 trade.py                          # Run backtest
python3 dashboards/dashboard.py           # Generate charts
python3 dashboards/generate_quant_report.py  # Create analysis
python3 optimizers/optimize_stops.py      # Optimize parameters
```

## 🎓 Strategy Logic

The strategy combines multiple confirmation signals:

1. **Momentum Filter**: Stock must have strong momentum (close > EMA9, MACD > Signal)
2. **HOD Proximity**: Within 10% of high of day
3. **EMA Bounce**: Price touches 9 EMA and bounces with 2 consecutive closes above
4. **Volume Confirmation**: 5M+ cumulative volume, 1.5x surge on entry
5. **RSI Filter**: RSI <60 to avoid overbought conditions
6. **Red Candle Filter**: Red candles must have below-average volume

## 🏆 Optimization Process

The optimizer tested:
- **5** stop loss values (2% to 5%)
- **4** take profit values (5% to 10%)
- **4** scale-out percentages (25% to 67%)
- **4** scale-out targets (4% to 8%)
- **4** trailing stop values (3% to 6%)

**Total**: 1,280 combinations tested
**Winner**: 5% SL, 10% TP, 67% scale-out at 8%, 5% trail

## 📞 Support

For questions or issues, refer to the documentation in the `docs/` directory.

## 📄 License

This is a personal trading strategy implementation. Use at your own risk.

---

**Last Updated**: December 30, 2025
**Strategy Version**: 2.0 (Optimized)
**Win Rate**: 75%
**Avg P&L**: $45.81 per trade
