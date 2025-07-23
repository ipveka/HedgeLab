import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from src.data.market_data import market_data
from src.ui.components import (
    metric_card, create_line_chart, create_yield_curve_chart, 
    news_feed, loading_spinner, format_currency, format_percentage
)

class MacroView:
    """Macro economic dashboard showing market overview, yield curves, and economic indicators"""
    
    def __init__(self):
        self.market_provider = market_data
    
    def render(self):
        """Render the macro view dashboard"""
        st.markdown("## 🌍 Macro Economic View")
        st.markdown("---")
        
        # Market Overview Section
        self._render_market_overview()
        st.markdown("---")
        
        # Yield Curve Section
        col1, col2 = st.columns([2, 1])
        with col1:
            self._render_yield_curve()
        with col2:
            self._render_treasury_rates()
        
        st.markdown("---")
        
        # Commodities and News
        col1, col2 = st.columns([1, 1])
        with col1:
            self._render_commodities()
        with col2:
            self._render_economic_news()
    
    def _render_market_overview(self):
        """Render market indices overview"""
        st.markdown("### 📊 Global Market Overview")
        
        with loading_spinner("Loading market data..."):
            indices_data = self.market_provider.get_market_indices()
        
        if not indices_data:
            st.error("Unable to load market data. Please check your connection.")
            return
        
        # Display market indices in metric cards
        cols = st.columns(len(indices_data))
        for i, (name, data) in enumerate(indices_data.items()):
            with cols[i]:
                value = format_currency(data['value']) if name != 'VIX' else f"{data['value']:.2f}"
                change = format_percentage(data['change'])
                delta_color = "normal" if data['change'] >= 0 else "inverse"
                
                metric_card(
                    title=name,
                    value=value,
                    delta=f"{'+' if data['change'] >= 0 else ''}{change}",
                    delta_color=delta_color
                )
        
        # Market trend chart
        st.markdown("#### Market Trend (Last 30 Days)")
        selected_index = st.selectbox(
            "Select Index",
            list(indices_data.keys()),
            index=0
        )
        
        if selected_index in indices_data:
            symbol = indices_data[selected_index]['symbol']
            trend_data = self.market_provider.get_stock_data(symbol, period="1mo")
            
            if not trend_data.empty:
                fig = create_line_chart(
                    trend_data, 
                    'Date', 
                    'Close', 
                    f"{selected_index} - 30 Day Trend"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning(f"No trend data available for {selected_index}")
    
    def _render_yield_curve(self):
        """Render yield curve chart"""
        st.markdown("### 📈 Treasury Yield Curve")
        
        with loading_spinner("Loading yield curve data..."):
            yield_data = self.market_provider.get_yield_curve()
        
        if not yield_data.empty:
            fig = create_yield_curve_chart(yield_data)
            st.plotly_chart(fig, use_container_width=True)
            
            # Yield curve analysis
            if len(yield_data) >= 2:
                short_term = yield_data[yield_data['years'] <= 2]['rate'].mean()
                long_term = yield_data[yield_data['years'] >= 10]['rate'].mean()
                spread = long_term - short_term
                
                if spread > 0:
                    st.success(f"✅ Normal yield curve (spread: {spread:.2f}%)")
                elif spread < -0.5:
                    st.error(f"🚨 Inverted yield curve (spread: {spread:.2f}%)")
                else:
                    st.warning(f"⚠️ Flat yield curve (spread: {spread:.2f}%)")
        else:
            st.warning("Unable to load yield curve data")
    
    def _render_treasury_rates(self):
        """Render treasury rates"""
        st.markdown("### 🏛️ Treasury Rates")
        
        with loading_spinner("Loading treasury rates..."):
            treasury_data = self.market_provider.get_treasury_rates()
        
        if treasury_data:
            for name, data in treasury_data.items():
                change_text = f"{'+' if data['change'] >= 0 else ''}{data['change']:.3f}%"
                delta_color = "normal" if data['change'] >= 0 else "inverse"
                
                metric_card(
                    title=f"{name} Treasury",
                    value=f"{data['value']:.3f}%",
                    delta=change_text,
                    delta_color=delta_color
                )
        else:
            st.warning("Unable to load treasury rates")
    
    def _render_commodities(self):
        """Render commodities prices"""
        st.markdown("### 🛢️ Commodities")
        
        with loading_spinner("Loading commodity prices..."):
            commodities_data = self.market_provider.get_commodities()
        
        if commodities_data:
            for name, data in commodities_data.items():
                change_text = f"{'+' if data['change'] >= 0 else ''}{format_percentage(data['change'])}"
                delta_color = "normal" if data['change'] >= 0 else "inverse"
                
                # Format value based on commodity type
                if 'Gold' in name or 'Silver' in name:
                    value = f"${data['value']:.2f}/oz"
                elif 'Oil' in name:
                    value = f"${data['value']:.2f}/bbl"
                elif 'Gas' in name:
                    value = f"${data['value']:.3f}/MMBtu"
                else:
                    value = f"${data['value']:.2f}"
                
                metric_card(
                    title=name,
                    value=value,
                    delta=change_text,
                    delta_color=delta_color
                )
        else:
            st.warning("Unable to load commodity data")
    
    def _render_economic_news(self):
        """Render economic news feed"""
        st.markdown("### 📰 Financial News")
        
        with loading_spinner("Loading latest news..."):
            news_data = self.market_provider.get_financial_news(limit=10)
        
        if news_data:
            # News sentiment overview
            positive_news = sum(1 for article in news_data if article.get('sentiment', 0) > 0.1)
            negative_news = sum(1 for article in news_data if article.get('sentiment', 0) < -0.1)
            neutral_news = len(news_data) - positive_news - negative_news
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Positive", positive_news, delta=None)
            with col2:
                st.metric("Neutral", neutral_news, delta=None)
            with col3:
                st.metric("Negative", negative_news, delta=None)
            
            st.markdown("#### Latest Headlines")
            news_feed(news_data)
        else:
            st.warning("Unable to load news data")
    
    def _render_fear_greed_index(self):
        """Render Fear & Greed Index (simplified version using VIX)"""
        st.markdown("### 😰😊 Market Sentiment")
        
        indices_data = self.market_provider.get_market_indices()
        if 'VIX' in indices_data:
            vix_value = indices_data['VIX']['value']
            
            # Simple Fear & Greed calculation based on VIX
            if vix_value < 12:
                sentiment = "Extreme Greed"
                color = "#16a34a"
                score = 85
            elif vix_value < 17:
                sentiment = "Greed"
                color = "#65a30d"
                score = 70
            elif vix_value < 25:
                sentiment = "Neutral"
                color = "#eab308"
                score = 50
            elif vix_value < 35:
                sentiment = "Fear"
                color = "#ea580c"
                score = 30
            else:
                sentiment = "Extreme Fear"
                color = "#dc2626"
                score = 15
            
            # Create gauge chart
            fig = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = score,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Market Sentiment"},
                delta = {'reference': 50},
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': color},
                    'steps': [
                        {'range': [0, 25], 'color': "#fee2e2"},
                        {'range': [25, 75], 'color': "#fef3c7"},
                        {'range': [75, 100], 'color': "#dcfce7"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ))
            
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown(f"**Current Sentiment:** {sentiment}")
            st.markdown(f"**VIX Level:** {vix_value:.2f}")
        else:
            st.warning("Unable to calculate market sentiment")

# For testing purposes
if __name__ == "__main__":
    macro_view = MacroView()
    macro_view.render() 