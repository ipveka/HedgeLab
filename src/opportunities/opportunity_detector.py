import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import ta
from src.data.market_data import market_data
from src.data.database import db
from src.ui.components import (
    display_opportunities_table, filter_sidebar, loading_spinner,
    create_candlestick_chart, metric_card, format_currency, format_percentage
)

class OpportunityDetector:
    """Detect trading opportunities using technical, fundamental, and sentiment analysis"""
    
    def __init__(self):
        self.market_provider = market_data
        self.database = db
        
        # Popular stocks for screening
        self.watchlist = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX',
            'AMD', 'INTC', 'CRM', 'ORCL', 'IBM', 'PYPL', 'ADBE', 'NOW',
            'JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'V', 'MA',
            'JNJ', 'PFE', 'UNH', 'ABBV', 'MRK', 'LLY', 'TMO', 'ABT',
            'XOM', 'CVX', 'COP', 'SLB', 'OXY', 'KMI', 'EOG', 'PXD'
        ]
    
    def render(self):
        """Render the opportunity detection dashboard"""
        st.markdown("## 🔍 Opportunity Detection")
        st.markdown("---")
        
        # Filters
        filters = filter_sidebar("opportunities")
        
        # Main content tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "🔍 Scanner", 
            "📊 Technical Analysis", 
            "💰 Fundamental Analysis", 
            "📰 Sentiment Analysis"
        ])
        
        with tab1:
            self._render_opportunity_scanner(filters)
        
        with tab2:
            self._render_technical_analysis()
        
        with tab3:
            self._render_fundamental_analysis()
        
        with tab4:
            self._render_sentiment_analysis()
    
    def _render_opportunity_scanner(self, filters: Dict[str, Any]):
        """Render the main opportunity scanner"""
        st.markdown("### 🔍 Opportunity Scanner")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            scan_type = st.selectbox(
                "Scan Type",
                ["Technical Signals", "Value Stocks", "Growth Stocks", "Momentum Stocks"]
            )
        
        with col2:
            market_cap = st.selectbox(
                "Market Cap",
                ["All", "Large Cap (>10B)", "Mid Cap (2B-10B)", "Small Cap (<2B)"]
            )
        
        with col3:
            if st.button("🚀 Run Scan", type="primary"):
                with loading_spinner("Scanning for opportunities..."):
                    opportunities = self._run_opportunity_scan(scan_type, filters)
                    st.session_state['last_scan_results'] = opportunities
        
        # Display results
        if 'last_scan_results' in st.session_state:
            opportunities = st.session_state['last_scan_results']
            
            if not opportunities.empty:
                st.markdown(f"### 📊 Found {len(opportunities)} Opportunities")
                
                # Summary metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    avg_signal = opportunities['signal_strength'].mean()
                    metric_card("Avg Signal Strength", f"{avg_signal:.2f}")
                
                with col2:
                    strong_signals = len(opportunities[opportunities['signal_strength'] >= 0.7])
                    metric_card("Strong Signals", str(strong_signals))
                
                with col3:
                    top_gain = opportunities['potential_gain'].max() if 'potential_gain' in opportunities.columns else 0
                    metric_card("Top Potential Gain", format_percentage(top_gain))
                
                with col4:
                    sectors = opportunities['sector'].nunique() if 'sector' in opportunities.columns else 0
                    metric_card("Sectors Covered", str(sectors))
                
                # Opportunities table
                display_opportunities_table(opportunities)
                
                # Save to database
                if st.button("💾 Save Results to Database"):
                    self._save_opportunities_to_db(opportunities)
            else:
                st.info("No opportunities found matching your criteria. Try adjusting filters.")
    
    def _render_technical_analysis(self):
        """Render technical analysis section"""
        st.markdown("### 📊 Technical Analysis")
        
        # Stock selection
        symbol = st.text_input("Enter Stock Symbol", value="AAPL").upper()
        
        if symbol:
            with loading_spinner(f"Loading data for {symbol}..."):
                stock_data = self.market_provider.get_stock_data(symbol, period="6mo")
            
            if not stock_data.empty:
                # Calculate technical indicators
                technical_data = self._calculate_technical_indicators(stock_data)
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    # Candlestick chart
                    fig = create_candlestick_chart(technical_data, f"{symbol} Price Chart")
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Technical signals
                    signals = self._get_technical_signals(technical_data)
                    
                    st.markdown("#### Technical Signals")
                    for signal_name, signal_data in signals.items():
                        color = "🟢" if signal_data['signal'] == "BUY" else "🔴" if signal_data['signal'] == "SELL" else "🟡"
                        st.markdown(f"{color} **{signal_name}**: {signal_data['signal']}")
                        st.markdown(f"   Strength: {signal_data['strength']:.2f}")
                
                # Technical indicators table
                st.markdown("#### Technical Indicators")
                latest = technical_data.iloc[-1]
                
                indicators_df = pd.DataFrame({
                    'Indicator': ['RSI', 'MACD', 'Moving Avg (20)', 'Moving Avg (50)', 'Bollinger Upper', 'Bollinger Lower'],
                    'Value': [
                        f"{latest['RSI']:.2f}",
                        f"{latest['MACD']:.4f}",
                        f"${latest['MA20']:.2f}",
                        f"${latest['MA50']:.2f}",
                        f"${latest['BB_upper']:.2f}",
                        f"${latest['BB_lower']:.2f}"
                    ],
                    'Signal': [
                        "Oversold" if latest['RSI'] < 30 else "Overbought" if latest['RSI'] > 70 else "Neutral",
                        "Bullish" if latest['MACD'] > latest['MACD_signal'] else "Bearish",
                        "Above" if latest['Close'] > latest['MA20'] else "Below",
                        "Above" if latest['Close'] > latest['MA50'] else "Below",
                        "Approaching" if latest['Close'] > latest['BB_upper'] * 0.98 else "Normal",
                        "Approaching" if latest['Close'] < latest['BB_lower'] * 1.02 else "Normal"
                    ]
                })
                
                st.dataframe(indicators_df, use_container_width=True, hide_index=True)
            else:
                st.error(f"No data found for {symbol}")
    
    def _render_fundamental_analysis(self):
        """Render fundamental analysis section"""
        st.markdown("### 💰 Fundamental Analysis")
        
        symbol = st.text_input("Enter Stock Symbol for Fundamental Analysis", value="AAPL").upper()
        
        if symbol:
            with loading_spinner(f"Loading fundamental data for {symbol}..."):
                stock_info = self.market_provider.get_stock_info(symbol)
            
            if stock_info:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("#### Valuation Metrics")
                    metric_card("P/E Ratio", f"{stock_info.get('pe_ratio', 'N/A'):.2f}" if isinstance(stock_info.get('pe_ratio'), (int, float)) else "N/A")
                    metric_card("Price/Book", f"{stock_info.get('price_to_book', 'N/A'):.2f}" if isinstance(stock_info.get('price_to_book'), (int, float)) else "N/A")
                    metric_card("Market Cap", format_currency(stock_info.get('market_cap', 0)))
                
                with col2:
                    st.markdown("#### Profitability")
                    profit_margin = stock_info.get('profit_margins', 0)
                    metric_card("Profit Margin", format_percentage(profit_margin * 100) if isinstance(profit_margin, (int, float)) else "N/A")
                    
                    eps = stock_info.get('eps', 0)
                    metric_card("EPS", f"${eps:.2f}" if isinstance(eps, (int, float)) else "N/A")
                    
                    revenue_growth = stock_info.get('revenue_growth', 0)
                    metric_card("Revenue Growth", format_percentage(revenue_growth * 100) if isinstance(revenue_growth, (int, float)) else "N/A")
                
                with col3:
                    st.markdown("#### Risk & Returns")
                    beta = stock_info.get('beta', 0)
                    metric_card("Beta", f"{beta:.2f}" if isinstance(beta, (int, float)) else "N/A")
                    
                    div_yield = stock_info.get('dividend_yield', 0)
                    metric_card("Dividend Yield", format_percentage(div_yield * 100) if isinstance(div_yield, (int, float)) else "N/A")
                    
                    target_price = stock_info.get('target_price', 0)
                    current_price = stock_info.get('current_price', 0)
                    if target_price and current_price:
                        upside = ((target_price - current_price) / current_price) * 100
                        metric_card("Analyst Upside", format_percentage(upside))
                
                # Fundamental scoring
                score = self._calculate_fundamental_score(stock_info)
                st.markdown("#### Fundamental Score")
                st.progress(score / 100)
                st.markdown(f"**Score: {score:.0f}/100**")
                
                # Investment thesis
                st.markdown("#### Investment Thesis")
                thesis = self._generate_investment_thesis(stock_info)
                st.markdown(thesis)
            else:
                st.error(f"No fundamental data found for {symbol}")
    
    def _render_sentiment_analysis(self):
        """Render sentiment analysis section"""
        st.markdown("### 📰 Sentiment Analysis")
        
        # News sentiment
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("#### Recent Market News Sentiment")
            news_data = self.market_provider.get_financial_news(limit=20)
            
            if news_data:
                # Calculate overall sentiment
                sentiments = [article.get('sentiment', 0) for article in news_data]
                avg_sentiment = np.mean(sentiments)
                
                sentiment_label = "Positive" if avg_sentiment > 0.1 else "Negative" if avg_sentiment < -0.1 else "Neutral"
                sentiment_color = "🟢" if avg_sentiment > 0.1 else "🔴" if avg_sentiment < -0.1 else "🟡"
                
                st.markdown(f"{sentiment_color} **Overall Sentiment: {sentiment_label}** (Score: {avg_sentiment:.3f})")
                
                # Sentiment distribution
                positive_count = sum(1 for s in sentiments if s > 0.1)
                negative_count = sum(1 for s in sentiments if s < -0.1)
                neutral_count = len(sentiments) - positive_count - negative_count
                
                sentiment_df = pd.DataFrame({
                    'Sentiment': ['Positive', 'Neutral', 'Negative'],
                    'Count': [positive_count, neutral_count, negative_count],
                    'Percentage': [
                        f"{(positive_count/len(sentiments)*100):.1f}%",
                        f"{(neutral_count/len(sentiments)*100):.1f}%",
                        f"{(negative_count/len(sentiments)*100):.1f}%"
                    ]
                })
                
                st.dataframe(sentiment_df, use_container_width=True, hide_index=True)
        
        with col2:
            st.markdown("#### Sentiment Indicators")
            
            # Fear & Greed Index (simplified)
            indices_data = self.market_provider.get_market_indices()
            if 'VIX' in indices_data:
                vix_value = indices_data['VIX']['value']
                fear_greed_score = max(0, min(100, 100 - (vix_value - 10) * 3))
                
                metric_card("Fear & Greed Index", f"{fear_greed_score:.0f}")
                metric_card("VIX Level", f"{vix_value:.2f}")
        
        # Top sentiment movers
        st.markdown("#### Top News by Sentiment")
        if news_data:
            # Sort by absolute sentiment score
            sorted_news = sorted(news_data, key=lambda x: abs(x.get('sentiment', 0)), reverse=True)
            
            for i, article in enumerate(sorted_news[:5]):
                with st.expander(f"#{i+1} - {article['title'][:60]}..."):
                    sentiment = article.get('sentiment', 0)
                    sentiment_emoji = "😊" if sentiment > 0.1 else "😟" if sentiment < -0.1 else "😐"
                    
                    st.markdown(f"**Sentiment:** {sentiment_emoji} {sentiment:.3f}")
                    st.markdown(f"**Summary:** {article['summary']}")
                    st.markdown(f"**Source:** {article['source']}")
                    st.markdown(f"**Published:** {article['published']}")
    
    def _run_opportunity_scan(self, scan_type: str, filters: Dict[str, Any]) -> pd.DataFrame:
        """Run opportunity scan based on selected criteria"""
        opportunities = []
        
        # Filter watchlist based on market cap if specified
        symbols_to_scan = self.watchlist.copy()
        
        for symbol in symbols_to_scan[:20]:  # Limit to 20 for demo
            try:
                stock_data = self.market_provider.get_stock_data(symbol, period="3mo")
                if stock_data.empty:
                    continue
                
                # Calculate technical indicators
                technical_data = self._calculate_technical_indicators(stock_data)
                latest = technical_data.iloc[-1]
                
                # Get stock info for fundamental data
                stock_info = self.market_provider.get_stock_info(symbol)
                
                # Apply scan type logic
                opportunity = None
                
                if scan_type == "Technical Signals":
                    opportunity = self._scan_technical_signals(symbol, technical_data, stock_info)
                elif scan_type == "Value Stocks":
                    opportunity = self._scan_value_stocks(symbol, stock_info)
                elif scan_type == "Growth Stocks":
                    opportunity = self._scan_growth_stocks(symbol, stock_info)
                elif scan_type == "Momentum Stocks":
                    opportunity = self._scan_momentum_stocks(symbol, technical_data, stock_info)
                
                if opportunity and opportunity['signal_strength'] >= filters.get('min_signal_strength', 0.5):
                    opportunities.append(opportunity)
            
            except Exception as e:
                st.warning(f"Error scanning {symbol}: {e}")
                continue
        
        return pd.DataFrame(opportunities)
    
    def _calculate_technical_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators for the stock data"""
        df = data.copy()
        
        # Moving averages
        df['MA20'] = ta.trend.sma_indicator(df['Close'], window=20)
        df['MA50'] = ta.trend.sma_indicator(df['Close'], window=50)
        
        # RSI
        df['RSI'] = ta.momentum.rsi(df['Close'], window=14)
        
        # MACD
        macd = ta.trend.MACD(df['Close'])
        df['MACD'] = macd.macd()
        df['MACD_signal'] = macd.macd_signal()
        df['MACD_hist'] = macd.macd_diff()
        
        # Bollinger Bands
        bb = ta.volatility.BollingerBands(df['Close'])
        df['BB_upper'] = bb.bollinger_hband()
        df['BB_lower'] = bb.bollinger_lband()
        df['BB_middle'] = bb.bollinger_mavg()
        
        # Volume indicators
        df['Volume_SMA'] = df['Volume'].rolling(window=20).mean()
        
        return df
    
    def _get_technical_signals(self, data: pd.DataFrame) -> Dict[str, Dict]:
        """Get technical signals from the data"""
        latest = data.iloc[-1]
        previous = data.iloc[-2]
        
        signals = {}
        
        # RSI Signal
        if latest['RSI'] < 30:
            signals['RSI'] = {'signal': 'BUY', 'strength': (30 - latest['RSI']) / 30}
        elif latest['RSI'] > 70:
            signals['RSI'] = {'signal': 'SELL', 'strength': (latest['RSI'] - 70) / 30}
        else:
            signals['RSI'] = {'signal': 'NEUTRAL', 'strength': 0.5}
        
        # MACD Signal
        if latest['MACD'] > latest['MACD_signal'] and previous['MACD'] <= previous['MACD_signal']:
            signals['MACD'] = {'signal': 'BUY', 'strength': 0.8}
        elif latest['MACD'] < latest['MACD_signal'] and previous['MACD'] >= previous['MACD_signal']:
            signals['MACD'] = {'signal': 'SELL', 'strength': 0.8}
        else:
            signals['MACD'] = {'signal': 'NEUTRAL', 'strength': 0.5}
        
        # Moving Average Signal
        if latest['Close'] > latest['MA20'] > latest['MA50']:
            signals['Moving Average'] = {'signal': 'BUY', 'strength': 0.7}
        elif latest['Close'] < latest['MA20'] < latest['MA50']:
            signals['Moving Average'] = {'signal': 'SELL', 'strength': 0.7}
        else:
            signals['Moving Average'] = {'signal': 'NEUTRAL', 'strength': 0.5}
        
        return signals
    
    def _scan_technical_signals(self, symbol: str, data: pd.DataFrame, stock_info: Dict) -> Optional[Dict]:
        """Scan for technical signals"""
        signals = self._get_technical_signals(data)
        latest = data.iloc[-1]
        
        # Calculate overall signal strength
        buy_signals = sum(1 for s in signals.values() if s['signal'] == 'BUY')
        total_signals = len(signals)
        signal_strength = buy_signals / total_signals if total_signals > 0 else 0
        
        if signal_strength >= 0.6:  # At least 60% buy signals
            return {
                'symbol': symbol,
                'strategy': 'Technical',
                'signal_strength': signal_strength,
                'price': latest['Close'],
                'change_pct': ((latest['Close'] - data.iloc[-2]['Close']) / data.iloc[-2]['Close']) * 100,
                'volume': latest['Volume'],
                'date': datetime.now(),
                'sector': stock_info.get('sector', 'Unknown'),
                'potential_gain': 15.0  # Estimated
            }
        
        return None
    
    def _scan_value_stocks(self, symbol: str, stock_info: Dict) -> Optional[Dict]:
        """Scan for value stocks"""
        pe_ratio = stock_info.get('pe_ratio', float('inf'))
        pb_ratio = stock_info.get('price_to_book', float('inf'))
        
        # Value criteria
        if pe_ratio and pe_ratio < 15 and pb_ratio and pb_ratio < 2:
            signal_strength = 1 - min(pe_ratio / 15, 1) * 0.5 - min(pb_ratio / 2, 1) * 0.5
            
            return {
                'symbol': symbol,
                'strategy': 'Value',
                'signal_strength': max(0.5, signal_strength),
                'price': stock_info.get('current_price', 0),
                'change_pct': 0,  # Would need historical data
                'volume': 0,
                'date': datetime.now(),
                'sector': stock_info.get('sector', 'Unknown'),
                'pe_ratio': pe_ratio,
                'pb_ratio': pb_ratio,
                'potential_gain': 20.0
            }
        
        return None
    
    def _scan_growth_stocks(self, symbol: str, stock_info: Dict) -> Optional[Dict]:
        """Scan for growth stocks"""
        revenue_growth = stock_info.get('revenue_growth', 0)
        profit_margin = stock_info.get('profit_margins', 0)
        
        if revenue_growth and revenue_growth > 0.15 and profit_margin and profit_margin > 0.1:
            signal_strength = min(revenue_growth * 2, 1) * 0.7 + min(profit_margin * 5, 1) * 0.3
            
            return {
                'symbol': symbol,
                'strategy': 'Growth',
                'signal_strength': max(0.5, signal_strength),
                'price': stock_info.get('current_price', 0),
                'change_pct': 0,
                'volume': 0,
                'date': datetime.now(),
                'sector': stock_info.get('sector', 'Unknown'),
                'revenue_growth': revenue_growth * 100,
                'profit_margin': profit_margin * 100,
                'potential_gain': 25.0
            }
        
        return None
    
    def _scan_momentum_stocks(self, symbol: str, data: pd.DataFrame, stock_info: Dict) -> Optional[Dict]:
        """Scan for momentum stocks"""
        if len(data) < 20:
            return None
        
        latest = data.iloc[-1]
        twenty_days_ago = data.iloc[-20]
        
        price_momentum = ((latest['Close'] - twenty_days_ago['Close']) / twenty_days_ago['Close']) * 100
        volume_momentum = latest['Volume'] / data['Volume'].tail(20).mean()
        
        if price_momentum > 10 and volume_momentum > 1.2:
            signal_strength = min(price_momentum / 20, 1) * 0.7 + min(volume_momentum / 2, 1) * 0.3
            
            return {
                'symbol': symbol,
                'strategy': 'Momentum',
                'signal_strength': max(0.5, signal_strength),
                'price': latest['Close'],
                'change_pct': price_momentum,
                'volume': latest['Volume'],
                'date': datetime.now(),
                'sector': stock_info.get('sector', 'Unknown'),
                'momentum_20d': price_momentum,
                'volume_ratio': volume_momentum,
                'potential_gain': 18.0
            }
        
        return None
    
    def _calculate_fundamental_score(self, stock_info: Dict) -> float:
        """Calculate fundamental score out of 100"""
        score = 0
        
        # P/E Ratio (20 points)
        pe_ratio = stock_info.get('pe_ratio', 0)
        if pe_ratio and 5 <= pe_ratio <= 20:
            score += 20
        elif pe_ratio and pe_ratio < 30:
            score += 10
        
        # Profit Margin (20 points)
        profit_margin = stock_info.get('profit_margins', 0)
        if profit_margin and profit_margin > 0.15:
            score += 20
        elif profit_margin and profit_margin > 0.05:
            score += 10
        
        # Revenue Growth (20 points)
        revenue_growth = stock_info.get('revenue_growth', 0)
        if revenue_growth and revenue_growth > 0.15:
            score += 20
        elif revenue_growth and revenue_growth > 0.05:
            score += 10
        
        # Price to Book (15 points)
        pb_ratio = stock_info.get('price_to_book', 0)
        if pb_ratio and pb_ratio < 1.5:
            score += 15
        elif pb_ratio and pb_ratio < 3:
            score += 8
        
        # Dividend Yield (10 points)
        div_yield = stock_info.get('dividend_yield', 0)
        if div_yield and div_yield > 0.02:
            score += 10
        elif div_yield and div_yield > 0:
            score += 5
        
        # Beta (stability) (15 points)
        beta = stock_info.get('beta', 1)
        if beta and 0.5 <= beta <= 1.2:
            score += 15
        elif beta and beta <= 1.5:
            score += 8
        
        return score
    
    def _generate_investment_thesis(self, stock_info: Dict) -> str:
        """Generate simple investment thesis"""
        name = stock_info.get('name', 'This company')
        sector = stock_info.get('sector', 'its sector')
        
        pe_ratio = stock_info.get('pe_ratio', 0)
        profit_margin = stock_info.get('profit_margins', 0)
        revenue_growth = stock_info.get('revenue_growth', 0)
        
        thesis = f"{name} operates in the {sector} sector. "
        
        if pe_ratio and pe_ratio < 15:
            thesis += "The stock appears undervalued based on its P/E ratio. "
        elif pe_ratio and pe_ratio > 30:
            thesis += "The stock trades at a premium valuation. "
        
        if profit_margin and profit_margin > 0.15:
            thesis += "The company demonstrates strong profitability margins. "
        
        if revenue_growth and revenue_growth > 0.1:
            thesis += "Revenue growth indicates expanding business operations. "
        
        thesis += "Consider this analysis alongside current market conditions and your risk tolerance."
        
        return thesis
    
    def _save_opportunities_to_db(self, opportunities: pd.DataFrame):
        """Save opportunities to database"""
        try:
            for _, opportunity in opportunities.iterrows():
                self.database.save_opportunity(opportunity.to_dict())
            st.success(f"Saved {len(opportunities)} opportunities to database!")
        except Exception as e:
            st.error(f"Error saving to database: {e}")

# For testing purposes
if __name__ == "__main__":
    detector = OpportunityDetector()
    detector.render() 