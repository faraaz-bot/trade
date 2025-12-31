"""
Momentum HOD Trading Strategy - Streamlit Dashboard
Minimalist UI for backtesting and analysis
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import sys

# Import strategy components
from trade import MomentumHODStrategy, fetch_data, screen_stocks_finviz

# Page configuration
st.set_page_config(
    page_title="Momentum HOD Strategy",
    page_icon="chart_with_upwards_trend",
    layout="wide"
)

# Minimalist CSS
st.markdown("""
<style>
    /* Clean, minimal design */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
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
    .stButton>button {
        width: 100%;
        border-radius: 4px;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'results' not in st.session_state:
    st.session_state.results = None
if 'data' not in st.session_state:
    st.session_state.data = None

# Header
st.title("Momentum HOD Strategy")
st.caption("Optimized small-cap momentum trading • 75% win rate • $45.81 avg P&L")

# Sidebar
with st.sidebar:
    st.header("Configuration")
    
    with st.expander("Stock Selection", expanded=True):
        method = st.radio("Method", ["Auto-Screen", "Manual"], label_visibility="collapsed")
        
        if method == "Manual":
            symbols_input = st.text_input("Symbols (comma-separated)", "SOPA, EQ")
            symbols = [s.strip().upper() for s in symbols_input.split(",") if s.strip()]
        else:
            symbols = None
            st.caption("Uses Finviz: Price $1-$20, RVol>2x")
    
    with st.expander("Exit Parameters"):
        stop_loss = st.slider("Stop Loss %", 1.0, 10.0, 5.0, 0.5) / 100
        take_profit = st.slider("Take Profit %", 5.0, 20.0, 10.0, 1.0) / 100
        scale_target = st.slider("Scale-Out Target %", 4.0, 12.0, 8.0, 1.0) / 100
        scale_pct = st.slider("Scale-Out %", 25, 100, 67, 5) / 100
        trailing = st.slider("Trailing Stop %", 3.0, 10.0, 5.0, 0.5) / 100
    
    st.divider()
    
    run_btn = st.button("Run Backtest", type="primary", use_container_width=True)

# Main content
if run_btn:
    with st.spinner("Running backtest..."):
        # Create strategy
        strategy = MomentumHODStrategy()
        strategy.stop_loss_pct = stop_loss
        strategy.take_profit_pct = take_profit
        strategy.trailing_stop_pct = trailing
        strategy.scale_out_target = scale_target
        
        # Get symbols
        if symbols is None:
            symbols = screen_stocks_finviz(strategy)
            if not symbols:
                st.error("No stocks found")
                st.stop()
        
        # Fetch data
        data = fetch_data(symbols, strategy)
        if not data:
            st.error("No valid data")
            st.stop()
        
        # Run backtest
        results = strategy.backtest(data)
        
        # Store results
        st.session_state.results = results
        st.session_state.data = data
        
        if not results.empty:
            st.success(f"{len(results)} trades executed")
            st.rerun()
        else:
            st.warning("No trades executed")

# Display results
if st.session_state.results is not None and not st.session_state.results.empty:
    results = st.session_state.results
    
    # Metrics row
    col1, col2, col3, col4, col5 = st.columns(5)
    
    total = len(results)
    wins = len(results[results['pnl'] > 0])
    win_rate = (wins / total * 100) if total > 0 else 0
    total_pnl = results['pnl'].sum()
    avg_pnl = results['pnl'].mean()
    
    with col1:
        st.metric("Trades", total)
    with col2:
        st.metric("Win Rate", f"{win_rate:.1f}%")
    with col3:
        st.metric("Total P&L", f"${total_pnl:.2f}")
    with col4:
        st.metric("Avg P&L", f"${avg_pnl:.2f}")
    with col5:
        losses = total - wins
        pf = abs(results[results['pnl'] > 0]['pnl'].sum() / 
                results[results['pnl'] < 0]['pnl'].sum()) if losses > 0 else 0
        st.metric("Profit Factor", f"{pf:.2f}")
    
    st.divider()
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["Charts", "Trades", "By Symbol"])
    
    with tab1:
        # Cumulative P&L Chart
        st.subheader("Cumulative P&L")
        
        results_sorted = results.sort_values('exit_time').copy()
        results_sorted['cumulative_pnl'] = results_sorted['pnl'].cumsum()
        
        fig = go.Figure()
        
        # Add cumulative P&L line
        fig.add_trace(go.Scatter(
            x=results_sorted['exit_time'],
            y=results_sorted['cumulative_pnl'],
            mode='lines+markers',
            name='P&L',
            line=dict(color='#2E86AB', width=2),
            marker=dict(size=8),
            fill='tozeroy',
            fillcolor='rgba(46, 134, 171, 0.1)'
        ))
        
        # Add zero line
        fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
        
        fig.update_layout(
            height=400,
            margin=dict(l=0, r=0, t=30, b=0),
            hovermode='x unified',
            showlegend=False,
            plot_bgcolor='white',
            xaxis=dict(showgrid=True, gridcolor='#f0f0f0'),
            yaxis=dict(showgrid=True, gridcolor='#f0f0f0', title='P&L ($)')
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # P&L Distribution
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("P&L Distribution")
            
            fig_hist = go.Figure()
            fig_hist.add_trace(go.Histogram(
                x=results['pnl'],
                nbinsx=20,
                marker_color='#2E86AB',
                opacity=0.7
            ))
            fig_hist.update_layout(
                height=300,
                margin=dict(l=0, r=0, t=10, b=0),
                showlegend=False,
                plot_bgcolor='white',
                xaxis=dict(title='P&L ($)', showgrid=True, gridcolor='#f0f0f0'),
                yaxis=dict(title='Count', showgrid=True, gridcolor='#f0f0f0')
            )
            st.plotly_chart(fig_hist, use_container_width=True)
        
        with col2:
            st.subheader("Win/Loss Split")
            
            fig_pie = go.Figure(data=[go.Pie(
                labels=['Wins', 'Losses'],
                values=[wins, losses],
                marker_colors=['#06D6A0', '#EF476F'],
                hole=0.5,
                textinfo='label+percent',
                textfont_size=14
            )])
            fig_pie.update_layout(
                height=300,
                margin=dict(l=0, r=0, t=10, b=0),
                showlegend=False
            )
            st.plotly_chart(fig_pie, use_container_width=True)
    
    with tab2:
        st.subheader("Trade Details")
        
        # Format dataframe
        display_df = results.copy()
        display_df['entry_time'] = pd.to_datetime(display_df['entry_time']).dt.strftime('%m/%d %H:%M')
        display_df['exit_time'] = pd.to_datetime(display_df['exit_time']).dt.strftime('%m/%d %H:%M')
        display_df['entry_price'] = display_df['entry_price'].apply(lambda x: f"${x:.2f}")
        display_df['exit_price'] = display_df['exit_price'].apply(lambda x: f"${x:.2f}")
        display_df['pnl'] = display_df['pnl'].apply(lambda x: f"${x:.2f}")
        display_df['pnl_pct'] = display_df['pnl_pct'].apply(lambda x: f"{x:.2f}%")
        
        # Color code P&L
        def color_pnl(val):
            if '$-' in val:
                return 'background-color: #ffebee'
            else:
                return 'background-color: #e8f5e9'
        
        styled_df = display_df.style.applymap(color_pnl, subset=['pnl'])
        
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
        
        # Download button
        csv = results.to_csv(index=False)
        st.download_button(
            "Download CSV",
            csv,
            f"trades_{datetime.now().strftime('%Y%m%d')}.csv",
            "text/csv",
            use_container_width=True
        )
    
    with tab3:
        st.subheader("Performance by Symbol")
        
        # Group by symbol
        symbol_perf = results.groupby('symbol').agg({
            'pnl': ['count', 'sum', 'mean']
        }).round(2)
        symbol_perf.columns = ['Trades', 'Total P&L', 'Avg P&L']
        
        # Add win rate
        symbol_perf['Wins'] = results.groupby('symbol').apply(
            lambda x: len(x[x['pnl'] > 0])
        )
        symbol_perf['Win Rate'] = (symbol_perf['Wins'] / symbol_perf['Trades'] * 100).round(1)
        symbol_perf['Win Rate'] = symbol_perf['Win Rate'].apply(lambda x: f"{x}%")
        
        # Format
        symbol_perf['Total P&L'] = symbol_perf['Total P&L'].apply(lambda x: f"${x:.2f}")
        symbol_perf['Avg P&L'] = symbol_perf['Avg P&L'].apply(lambda x: f"${x:.2f}")
        
        st.dataframe(symbol_perf, use_container_width=True)
        
        # Bar chart by symbol
        symbol_totals = results.groupby('symbol')['pnl'].sum().sort_values(ascending=True)
        
        fig_bar = go.Figure()
        colors = ['#06D6A0' if x > 0 else '#EF476F' for x in symbol_totals.values]
        
        fig_bar.add_trace(go.Bar(
            y=symbol_totals.index,
            x=symbol_totals.values,
            orientation='h',
            marker_color=colors,
            text=[f"${x:.2f}" for x in symbol_totals.values],
            textposition='outside'
        ))
        
        fig_bar.update_layout(
            height=max(300, len(symbol_totals) * 50),
            margin=dict(l=0, r=0, t=10, b=0),
            showlegend=False,
            plot_bgcolor='white',
            xaxis=dict(title='Total P&L ($)', showgrid=True, gridcolor='#f0f0f0'),
            yaxis=dict(showgrid=False)
        )
        
        st.plotly_chart(fig_bar, use_container_width=True)

else:
    # Welcome screen
    st.info("Configure settings in the sidebar and click 'Run Backtest' to start")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Current Stop Loss", "5.0%")
        st.caption("Optimized parameter")
    
    with col2:
        st.metric("Current Take Profit", "10.0%")
        st.caption("Optimized parameter")
    
    with col3:
        st.metric("Expected Win Rate", "75%")
        st.caption("Based on optimization")
    
    st.divider()
    
    st.subheader("Quick Start")
    st.markdown("""
    1. **Configure** exit parameters in sidebar (or use optimized defaults)
    2. **Select** stocks (Auto-Screen recommended)
    3. **Run** backtest
    4. **Analyze** results in the charts and tables
    5. **Export** results as CSV
    """)
    
    st.subheader("Strategy Highlights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Entry Criteria**
        - 9 EMA bounce with 2 closes above
        - Cumulative volume >5M
        - Volume surge 1.5x on entry
        - RSI <60, MACD > Signal
        - Near HOD (within 10%)
        """)
    
    with col2:
        st.markdown("""
        **Exit Strategy**
        - Scale out 67% at 8% profit
        - Trail remaining 33% with 5% stop
        - Full exit at 10% take profit
        - 5% initial stop loss
        - Close all by 3:55 PM EST
        """)

# Footer
st.divider()
st.caption("Strategy v2.0 (Optimized) | GitHub: faraaz-bot/trade")
