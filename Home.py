"""
Momentum HOD Trading Strategy - Multi-Page Dashboard
Main landing page with navigation to different features
"""

import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Momentum HOD Strategy",
    page_icon="chart_with_upwards_trend",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        padding-top: 2rem;
    }
    h1 {
        font-weight: 300;
        letter-spacing: -1px;
    }
    .stMetric {
        background-color: white;
        padding: 1rem;
        border-radius: 4px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Header
st.title("Momentum HOD Trading Strategy")
st.caption("Optimized small-cap momentum trading • 75% win rate • $45.81 avg P&L")

st.markdown("---")

# Welcome content
st.header("Welcome to the Trading Dashboard")

st.markdown("""
This multi-page application provides comprehensive tools for backtesting and analyzing 
the Momentum HOD (High of Day) trading strategy optimized for small-cap stocks.
""")

# Feature cards
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Backtest Runner")
    st.markdown("""
    **Interactive backtesting with customizable parameters**
    
    Features:
    - Auto-screen stocks using Finviz
    - Manual symbol selection
    - Adjustable exit parameters
    - Real-time backtest execution
    - 4 interactive charts:
      - Cumulative P&L
      - P&L distribution
      - Win/Loss split
      - Performance by symbol
    - CSV export
    
    Navigate to **Backtest Runner** in the sidebar to get started.
    """)

with col2:
    st.subheader("2. Trade Analysis")
    st.markdown("""
    **Professional TradingView-style analysis dashboard**
    
    Features:
    - View all historical trades
    - Sort and filter capabilities
    - 4-panel technical charts:
      - Candlestick + EMAs + VWAP
      - Volume analysis
      - MACD indicators
      - RSI with levels
    - Entry/Exit markers
    - Dark theme
    
    Navigate to **Trade Analysis** in the sidebar to view trades.
    """)

st.markdown("---")

# Strategy overview
st.header("Strategy Overview")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Optimized Stop Loss", "5.0%")
    st.caption("Based on 1,280 parameter combinations")

with col2:
    st.metric("Optimized Take Profit", "10.0%")
    st.caption("Maximum profit target")

with col3:
    st.metric("Expected Win Rate", "75%")
    st.caption("Historical performance")

st.markdown("---")

# Quick start guide
st.header("Quick Start Guide")

st.markdown("""
### For New Users:

1. **Navigate to Backtest Runner** (sidebar)
   - Choose Auto-Screen or Manual symbol selection
   - Adjust exit parameters if desired (or use optimized defaults)
   - Click "Run Backtest"
   - View results in interactive charts

2. **Navigate to Trade Analysis** (sidebar)
   - View all historical trades
   - Filter by symbol or exit reason
   - Select any trade to see detailed chart
   - Analyze entry/exit points with technical indicators

### Strategy Criteria:

**Entry Requirements:**
- Price: $1-$10
- Float: <30M shares
- Relative Volume: >2x average
- 9 EMA bounce with 2 closes above
- Cumulative volume >5M
- Volume surge 1.5x on entry
- RSI <60, MACD > Signal
- Near HOD (within 10%)

**Exit Strategy:**
- Scale out 67% at 8% profit
- Trail remaining 33% with 5% stop
- Full exit at 10% take profit
- 5% initial stop loss
- Close all positions by 3:55 PM EST
""")

st.markdown("---")

# Footer
st.caption("Strategy v2.0 (Optimized) | GitHub: faraaz-bot/trade")
st.caption("Use the sidebar to navigate between different features")
