import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Dict, List, Any, Optional
from datetime import datetime

def metric_card(title: str, value: str, delta: str = None, delta_color: str = "normal") -> None:
    """Create a metric card with title, value, and optional delta"""
    with st.container():
        st.markdown(f"""
        <div class="metric-card">
            <h4 style="margin: 0; color: #64748b; font-size: 0.875rem;">{title}</h4>
            <h2 style="margin: 0.25rem 0; color: #1e293b;">{value}</h2>
            {f'<p style="margin: 0; color: {"#ef4444" if delta_color == "inverse" else "#10b981"}; font-size: 0.875rem;">{delta}</p>' if delta else ''}
        </div>
        """, unsafe_allow_html=True)

def create_candlestick_chart(data: pd.DataFrame, title: str = "Stock Price") -> go.Figure:
    """Create a candlestick chart"""
    fig = go.Figure(data=go.Candlestick(
        x=data['Date'],
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name="Price"
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title="Price ($)",
        template="plotly_white",
        showlegend=False,
        height=400
    )
    
    return fig

def create_line_chart(data: pd.DataFrame, x_col: str, y_col: str, title: str = "Chart") -> go.Figure:
    """Create a line chart"""
    fig = go.Figure(data=go.Scatter(
        x=data[x_col],
        y=data[y_col],
        mode='lines',
        line=dict(color='#3b82f6', width=2)
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title=x_col.title(),
        yaxis_title=y_col.title(),
        template="plotly_white",
        showlegend=False,
        height=400
    )
    
    return fig

def create_yield_curve_chart(yield_data: pd.DataFrame) -> go.Figure:
    """Create yield curve chart"""
    fig = go.Figure(data=go.Scatter(
        x=yield_data['years'],
        y=yield_data['rate'],
        mode='lines+markers',
        line=dict(color='#3b82f6', width=3),
        marker=dict(size=8, color='#1e40af')
    ))
    
    fig.update_layout(
        title="Treasury Yield Curve",
        xaxis_title="Maturity (Years)",
        yaxis_title="Yield (%)",
        template="plotly_white",
        showlegend=False,
        height=400
    )
    
    return fig

def create_portfolio_pie_chart(positions: pd.DataFrame) -> go.Figure:
    """Create portfolio allocation pie chart"""
    if positions.empty:
        fig = go.Figure()
        fig.update_layout(
            title="Portfolio Allocation",
            annotations=[{
                "text": "No positions to display",
                "x": 0.5, "y": 0.5,
                "showarrow": False,
                "font": {"size": 16}
            }],
            height=400
        )
        return fig
    
    fig = go.Figure(data=go.Pie(
        labels=positions['symbol'],
        values=positions['market_value'],
        hole=0.4
    ))
    
    fig.update_layout(
        title="Portfolio Allocation",
        template="plotly_white",
        height=400
    )
    
    return fig

def create_performance_chart(performance_data: pd.DataFrame) -> go.Figure:
    """Create portfolio performance chart"""
    if performance_data.empty:
        fig = go.Figure()
        fig.update_layout(
            title="Portfolio Performance",
            annotations=[{
                "text": "No performance data available",
                "x": 0.5, "y": 0.5,
                "showarrow": False,
                "font": {"size": 16}
            }],
            height=400
        )
        return fig
    
    fig = go.Figure()
    
    # Portfolio value
    fig.add_trace(go.Scatter(
        x=performance_data['date'],
        y=performance_data['total_value'],
        mode='lines',
        name='Portfolio Value',
        line=dict(color='#3b82f6', width=2)
    ))
    
    # Benchmark (if available)
    if 'benchmark_value' in performance_data.columns:
        fig.add_trace(go.Scatter(
            x=performance_data['date'],
            y=performance_data['benchmark_value'],
            mode='lines',
            name='Benchmark',
            line=dict(color='#ef4444', width=2, dash='dash')
        ))
    
    fig.update_layout(
        title="Portfolio Performance",
        xaxis_title="Date",
        yaxis_title="Value ($)",
        template="plotly_white",
        height=400
    )
    
    return fig

def display_opportunities_table(opportunities: pd.DataFrame) -> None:
    """Display opportunities in a formatted table"""
    if opportunities.empty:
        st.info("No opportunities found. Try adjusting your filters.")
        return
    
    # Format the dataframe for display
    display_df = opportunities.copy()
    
    # Format numeric columns
    if 'signal_strength' in display_df.columns:
        display_df['signal_strength'] = display_df['signal_strength'].round(2)
    if 'price' in display_df.columns:
        display_df['price'] = display_df['price'].apply(lambda x: f"${x:.2f}")
    if 'change_pct' in display_df.columns:
        display_df['change_pct'] = display_df['change_pct'].apply(lambda x: f"{x:.2f}%")
    
    # Rename columns for better display
    column_mapping = {
        'symbol': 'Symbol',
        'strategy': 'Strategy',
        'signal_strength': 'Signal Strength',
        'price': 'Price',
        'change_pct': 'Change %',
        'volume': 'Volume',
        'date': 'Date'
    }
    
    display_df = display_df.rename(columns=column_mapping)
    
    # Display with color coding for signal strength
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )

def display_trades_table(trades: pd.DataFrame) -> None:
    """Display trades in a formatted table"""
    if trades.empty:
        st.info("No trades found.")
        return
    
    # Format the dataframe for display
    display_df = trades.copy()
    
    # Format columns
    if 'price' in display_df.columns:
        display_df['price'] = display_df['price'].apply(lambda x: f"${x:.2f}")
    if 'quantity' in display_df.columns:
        display_df['quantity'] = display_df['quantity'].apply(lambda x: f"{x:,.0f}")
    if 'total_value' in display_df.columns:
        display_df['total_value'] = display_df['total_value'].apply(lambda x: f"${x:,.2f}")
    
    # Color code buy/sell
    def color_side(val):
        if val == 'BUY':
            return 'background-color: #dcfce7'
        elif val == 'SELL':
            return 'background-color: #fee2e2'
        return ''
    
    # Rename columns
    column_mapping = {
        'symbol': 'Symbol',
        'side': 'Side',
        'quantity': 'Quantity',
        'price': 'Price',
        'total_value': 'Total Value',
        'timestamp': 'Timestamp'
    }
    
    display_df = display_df.rename(columns=column_mapping)
    
    if 'Side' in display_df.columns:
        styled_df = display_df.style.applymap(color_side, subset=['Side'])
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
    else:
        st.dataframe(display_df, use_container_width=True, hide_index=True)

def news_feed(news_data: List[Dict]) -> None:
    """Display news feed with sentiment"""
    if not news_data:
        st.info("No news available at the moment.")
        return
    
    for article in news_data[:10]:  # Show top 10 articles
        with st.container():
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.markdown(f"**{article['title']}**")
                st.markdown(f"{article['summary']}")
                st.markdown(f"*Source: {article['source']} | {article['published']}*")
            
            with col2:
                sentiment = article.get('sentiment', 0)
                if sentiment > 0.1:
                    st.success("😊 Positive")
                elif sentiment < -0.1:
                    st.error("😟 Negative")
                else:
                    st.info("😐 Neutral")
            
            st.markdown("---")

def filter_sidebar(filter_type: str = "opportunities") -> Dict[str, Any]:
    """Create filter sidebar for different modules"""
    filters = {}
    
    with st.sidebar:
        st.markdown("### Filters")
        
        if filter_type == "opportunities":
            filters['strategy'] = st.selectbox(
                "Strategy",
                ["All", "Technical", "Fundamental", "Sentiment"],
                index=0
            )
            
            filters['min_signal_strength'] = st.slider(
                "Minimum Signal Strength",
                min_value=0.0,
                max_value=1.0,
                value=0.5,
                step=0.1
            )
            
            filters['sectors'] = st.multiselect(
                "Sectors",
                ["Technology", "Healthcare", "Finance", "Energy", "Consumer", "Industrial"]
            )
        
        elif filter_type == "portfolio":
            filters['date_range'] = st.date_input(
                "Date Range",
                value=[datetime.now().date()],
                max_value=datetime.now().date()
            )
            
            filters['position_type'] = st.selectbox(
                "Position Type",
                ["All", "Long", "Short"],
                index=0
            )
    
    return filters

def loading_spinner(text: str = "Loading..."):
    """Display loading spinner with text"""
    return st.spinner(text)

def success_message(message: str):
    """Display success message"""
    st.success(f"✅ {message}")

def error_message(message: str):
    """Display error message"""
    st.error(f"❌ {message}")

def warning_message(message: str):
    """Display warning message"""
    st.warning(f"⚠️ {message}")

def info_message(message: str):
    """Display info message"""
    st.info(f"ℹ️ {message}")

def format_currency(amount: float) -> str:
    """Format currency amount"""
    if abs(amount) >= 1e9:
        return f"${amount/1e9:.2f}B"
    elif abs(amount) >= 1e6:
        return f"${amount/1e6:.2f}M"
    elif abs(amount) >= 1e3:
        return f"${amount/1e3:.2f}K"
    else:
        return f"${amount:.2f}"

def format_percentage(value: float) -> str:
    """Format percentage value"""
    return f"{value:.2f}%"

def format_large_number(value: float) -> str:
    """Format large numbers with appropriate suffixes"""
    if abs(value) >= 1e9:
        return f"{value/1e9:.2f}B"
    elif abs(value) >= 1e6:
        return f"{value/1e6:.2f}M"
    elif abs(value) >= 1e3:
        return f"{value/1e3:.2f}K"
    else:
        return f"{value:.2f}" 