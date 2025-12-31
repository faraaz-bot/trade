"""
Professional TradingView-Style Trading Dashboard
Displays all trades with interactive charts and entry/exit markers
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Page configuration
st.set_page_config(
    page_title="Trade Analysis",
    page_icon="chart_with_upwards_trend",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for TradingView-style dark theme
st.markdown("""
<style>
    .main {
        background-color: #131722;
    }
    .stApp {
        background-color: #131722;
    }
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown {
        color: #D1D4DC !important;
    }
    .stDataFrame {
        background-color: #1E222D;
    }
    div[data-testid="stMetricValue"] {
        font-size: 28px;
        color: #2962FF;
    }
    div[data-testid="stMetricLabel"] {
        color: #787B86;
    }
    .profit {
        color: #26A69A !important;
        font-weight: bold;
    }
    .loss {
        color: #EF5350 !important;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_trades():
    """Load trades from backtest results"""
    try:
        df = pd.read_csv('backtest_results.csv')
        df['entry_time'] = pd.to_datetime(df['entry_time'])
        df['exit_time'] = pd.to_datetime(df['exit_time'])
        return df
    except FileNotFoundError:
        return pd.DataFrame()

@st.cache_data(ttl=300)
def get_stock_data(symbol, start_date, end_date):
    """Fetch stock data for charting"""
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(start=start_date, end=end_date, interval="1m")
        if df.empty:
            # Fallback to daily data if minute data not available
            df = ticker.history(start=start_date, end=end_date, interval="1d")
        return df
    except:
        return pd.DataFrame()

def calculate_indicators(df):
    """Calculate technical indicators"""
    if df.empty:
        return df
    
    # EMA calculations
    df['EMA_9'] = df['Close'].ewm(span=9, adjust=False).mean()
    df['EMA_50'] = df['Close'].ewm(span=50, adjust=False).mean()
    df['EMA_100'] = df['Close'].ewm(span=100, adjust=False).mean()
    
    # MACD
    ema12 = df['Close'].ewm(span=12, adjust=False).mean()
    ema26 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = ema12 - ema26
    df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']
    
    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # VWAP
    df['VWAP'] = (df['Volume'] * (df['High'] + df['Low'] + df['Close']) / 3).cumsum() / df['Volume'].cumsum()
    
    return df

def create_chart(symbol, trade_data, stock_df):
    """Create TradingView-style chart with indicators"""
    
    # Create subplots
    fig = make_subplots(
        rows=4, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.5, 0.15, 0.15, 0.2],
        subplot_titles=('Price', 'Volume', 'MACD', 'RSI')
    )
    
    # Candlestick chart
    fig.add_trace(
        go.Candlestick(
            x=stock_df.index,
            open=stock_df['Open'],
            high=stock_df['High'],
            low=stock_df['Low'],
            close=stock_df['Close'],
            name='Price',
            increasing_line_color='#26A69A',
            decreasing_line_color='#EF5350'
        ),
        row=1, col=1
    )
    
    # EMAs
    fig.add_trace(go.Scatter(x=stock_df.index, y=stock_df['EMA_9'], 
                             name='EMA 9', line=dict(color='#2962FF', width=1)), row=1, col=1)
    fig.add_trace(go.Scatter(x=stock_df.index, y=stock_df['EMA_50'], 
                             name='EMA 50', line=dict(color='#FF6D00', width=1)), row=1, col=1)
    fig.add_trace(go.Scatter(x=stock_df.index, y=stock_df['EMA_100'], 
                             name='EMA 100', line=dict(color='#9C27B0', width=1)), row=1, col=1)
    
    # VWAP
    fig.add_trace(go.Scatter(x=stock_df.index, y=stock_df['VWAP'], 
                             name='VWAP', line=dict(color='#FDD835', width=1, dash='dash')), row=1, col=1)
    
    # Entry and Exit markers
    for _, trade in trade_data.iterrows():
        # Entry marker (green arrow up)
        fig.add_trace(go.Scatter(
            x=[trade['entry_time']],
            y=[trade['entry_price']],
            mode='markers+text',
            marker=dict(symbol='triangle-up', size=15, color='#26A69A'),
            text=[f"BUY<br>${trade['entry_price']:.2f}"],
            textposition="bottom center",
            textfont=dict(color='#26A69A', size=10),
            name='Entry',
            showlegend=False
        ), row=1, col=1)
        
        # Exit marker (red arrow down)
        fig.add_trace(go.Scatter(
            x=[trade['exit_time']],
            y=[trade['exit_price']],
            mode='markers+text',
            marker=dict(symbol='triangle-down', size=15, color='#EF5350'),
            text=[f"SELL<br>${trade['exit_price']:.2f}<br>{trade['pnl_pct']:.1f}%"],
            textposition="top center",
            textfont=dict(color='#EF5350', size=10),
            name='Exit',
            showlegend=False
        ), row=1, col=1)
    
    # Volume bars
    colors = ['#26A69A' if close >= open else '#EF5350' 
              for close, open in zip(stock_df['Close'], stock_df['Open'])]
    fig.add_trace(
        go.Bar(x=stock_df.index, y=stock_df['Volume'], name='Volume',
               marker_color=colors, showlegend=False),
        row=2, col=1
    )
    
    # MACD
    fig.add_trace(go.Scatter(x=stock_df.index, y=stock_df['MACD'], 
                             name='MACD', line=dict(color='#2962FF', width=1)), row=3, col=1)
    fig.add_trace(go.Scatter(x=stock_df.index, y=stock_df['MACD_Signal'], 
                             name='Signal', line=dict(color='#FF6D00', width=1)), row=3, col=1)
    
    # MACD Histogram
    colors_macd = ['#26A69A' if val >= 0 else '#EF5350' for val in stock_df['MACD_Hist']]
    fig.add_trace(go.Bar(x=stock_df.index, y=stock_df['MACD_Hist'], 
                         name='Histogram', marker_color=colors_macd, showlegend=False), row=3, col=1)
    
    # RSI
    fig.add_trace(go.Scatter(x=stock_df.index, y=stock_df['RSI'], 
                             name='RSI', line=dict(color='#2962FF', width=1)), row=4, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="#EF5350", row=4, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="#26A69A", row=4, col=1)
    
    # Update layout for TradingView style
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='#131722',
        plot_bgcolor='#1E222D',
        font=dict(color='#D1D4DC', family='Arial'),
        height=900,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        xaxis_rangeslider_visible=False,
        hovermode='x unified'
    )
    
    # Update axes
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#2A2E39')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#2A2E39')
    
    return fig

def main():
    st.title("Trade Analysis")
    st.caption("Professional TradingView-style charts and trade analysis")
    st.markdown("---")
    
    # Load trades
    trades_df = load_trades()
    
    if trades_df.empty:
        st.warning("No trades found. Run a backtest first to generate trades.")
        st.info("Go to **Backtest Runner** page to run a backtest")
        return
    
    # Calculate metrics
    total_trades = len(trades_df)
    winning_trades = len(trades_df[trades_df['pnl'] > 0])
    losing_trades = len(trades_df[trades_df['pnl'] < 0])
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
    total_pnl = trades_df['pnl'].sum()
    avg_win = trades_df[trades_df['pnl'] > 0]['pnl'].mean() if winning_trades > 0 else 0
    avg_loss = trades_df[trades_df['pnl'] < 0]['pnl'].mean() if losing_trades > 0 else 0
    
    # Metrics row
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Trades", total_trades)
    with col2:
        st.metric("Win Rate", f"{win_rate:.1f}%")
    with col3:
        pnl_color = "normal" if total_pnl >= 0 else "inverse"
        st.metric("Total P&L", f"${total_pnl:.2f}", delta=f"{total_pnl:.2f}")
    with col4:
        st.metric("Avg Win", f"${avg_win:.2f}")
    with col5:
        st.metric("Avg Loss", f"${avg_loss:.2f}")
    
    st.markdown("---")
    
    # Sidebar for filtering and sorting
    with st.sidebar:
        st.header("Filters & Settings")
        
        # Sort options
        sort_by = st.selectbox(
            "Sort By",
            ["Biggest Winners", "Biggest Losers", "Most Recent", "Symbol"]
        )
        
        # Filter by symbol
        symbols = ['All'] + sorted(trades_df['symbol'].unique().tolist())
        selected_symbol = st.selectbox("Filter by Symbol", symbols)
        
        # Filter by reason
        reasons = ['All'] + sorted(trades_df['reason'].unique().tolist())
        selected_reason = st.selectbox("Filter by Exit Reason", reasons)
    
    # Apply filters
    filtered_df = trades_df.copy()
    if selected_symbol != 'All':
        filtered_df = filtered_df[filtered_df['symbol'] == selected_symbol]
    if selected_reason != 'All':
        filtered_df = filtered_df[filtered_df['reason'] == selected_reason]
    
    # Apply sorting
    if sort_by == "Biggest Winners":
        filtered_df = filtered_df.sort_values('pnl', ascending=False)
    elif sort_by == "Biggest Losers":
        filtered_df = filtered_df.sort_values('pnl', ascending=True)
    elif sort_by == "Most Recent":
        filtered_df = filtered_df.sort_values('exit_time', ascending=False)
    else:  # Symbol
        filtered_df = filtered_df.sort_values('symbol')
    
    # Display trades table
    st.subheader("Trade History")
    
    # Format the dataframe for display
    display_df = filtered_df.copy()
    display_df['Entry'] = display_df['entry_time'].dt.strftime('%Y-%m-%d %H:%M')
    display_df['Exit'] = display_df['exit_time'].dt.strftime('%Y-%m-%d %H:%M')
    display_df['Entry $'] = display_df['entry_price'].apply(lambda x: f"${x:.2f}")
    display_df['Exit $'] = display_df['exit_price'].apply(lambda x: f"${x:.2f}")
    display_df['P&L'] = display_df['pnl'].apply(lambda x: f"${x:.2f}")
    display_df['P&L %'] = display_df['pnl_pct'].apply(lambda x: f"{x:.2f}%")
    
    st.dataframe(
        display_df[['symbol', 'Entry', 'Exit', 'Entry $', 'Exit $', 'shares', 'P&L', 'P&L %', 'reason']],
        width='stretch',
        height=400
    )
    
    st.markdown("---")
    
    # Chart section
    st.subheader("Trade Charts")
    
    # Select trade to view
    trade_options = [
        f"{row['symbol']} - {row['entry_time'].strftime('%Y-%m-%d')} - P&L: ${row['pnl']:.2f} ({row['pnl_pct']:.1f}%)"
        for _, row in filtered_df.iterrows()
    ]
    
    if trade_options:
        selected_trade_idx = st.selectbox(
            "Select Trade to View Chart",
            range(len(trade_options)),
            format_func=lambda x: trade_options[x]
        )
        
        selected_trade = filtered_df.iloc[selected_trade_idx]
        
        # Fetch stock data
        symbol = selected_trade['symbol']
        start_date = selected_trade['entry_time'] - timedelta(days=1)
        end_date = selected_trade['exit_time'] + timedelta(days=1)
        
        with st.spinner(f'Loading chart for {symbol}...'):
            stock_df = get_stock_data(symbol, start_date, end_date)
            
            if not stock_df.empty:
                stock_df = calculate_indicators(stock_df)
                
                # Create single-trade dataframe for markers
                trade_data = pd.DataFrame([selected_trade])
                
                # Display chart
                fig = create_chart(symbol, trade_data, stock_df)
                st.plotly_chart(fig, width='stretch')
                
                # Trade details
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.info(f"**Entry:** {selected_trade['entry_time'].strftime('%Y-%m-%d %H:%M')}")
                    st.info(f"**Entry Price:** ${selected_trade['entry_price']:.2f}")
                with col2:
                    st.info(f"**Exit:** {selected_trade['exit_time'].strftime('%Y-%m-%d %H:%M')}")
                    st.info(f"**Exit Price:** ${selected_trade['exit_price']:.2f}")
                with col3:
                    st.info(f"**P&L:** ${selected_trade['pnl']:.2f}")
                    st.info(f"**P&L %:** {selected_trade['pnl_pct']:.2f}%")
                
                st.caption(f"**Exit Reason:** {selected_trade['reason']} | **Shares:** {selected_trade['shares']}")
            else:
                st.error(f"Could not load chart data for {symbol}")
    else:
        st.info("No trades match the current filters")

if __name__ == "__main__":
    main()
