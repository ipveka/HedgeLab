import yfinance as yf
import pandas as pd
import numpy as np
import requests
import feedparser
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import streamlit as st
from textblob import TextBlob

# Import logger
try:
    from ..utils.logger import logger
except ImportError:
    from utils.logger import logger

class MarketDataProvider:
    """Provides market data from various free sources"""
    
    def __init__(self):
        self.cache_duration = 15  # minutes
        self.rate_limit_delay = 1.0  # seconds between API calls
        self.last_api_call = 0
        logger.info("MarketDataProvider initialized")
        
    @st.cache_data(ttl=900)  # 15 minutes cache
    def get_stock_data(_self, symbol: str, period: str = "1y") -> pd.DataFrame:
        """Get stock data from Yahoo Finance"""
        start_time = time.time()
        logger.info(f"Fetching stock data for {symbol}, period: {period}")
        
        try:
            # Rate limiting
            current_time = time.time()
            time_since_last_call = current_time - _self.last_api_call
            if time_since_last_call < _self.rate_limit_delay:
                sleep_time = _self.rate_limit_delay - time_since_last_call
                logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f}s")
                time.sleep(sleep_time)
            
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period)
            data.reset_index(inplace=True)
            data['Symbol'] = symbol
            
            _self.last_api_call = time.time()
            response_time = time.time() - start_time
            
            logger.api_call(f"yfinance_stock_data_{symbol}", "SUCCESS", response_time)
            logger.info(f"Successfully fetched {len(data)} records for {symbol}")
            
            return data
        except Exception as e:
            response_time = time.time() - start_time
            error_msg = str(e)
            
            logger.api_call(f"yfinance_stock_data_{symbol}", "FAILED", response_time, error_msg)
            
            # Check for rate limiting
            if "Too Many Requests" in error_msg or "Rate limited" in error_msg:
                logger.rate_limit(f"yfinance_stock_data_{symbol}")
                st.warning(f"Rate limited for {symbol}. Using cached data if available.")
            
            # Fallback to mock data if available
            if MOCK_DATA_AVAILABLE and mock_market_data:
                logger.data_fallback(f"stock_data_{symbol}", error_msg)
                st.warning(f"Using mock data for {symbol} (real data unavailable)")
                return mock_market_data.get_stock_data(symbol, period)
            else:
                logger.error(f"Error fetching data for {symbol}: {e}")
                st.error(f"Error fetching data for {symbol}: {e}")
                return pd.DataFrame()
    
    @st.cache_data(ttl=900)
    def get_multiple_stocks(_self, symbols: List[str], period: str = "1y") -> pd.DataFrame:
        """Get data for multiple stocks"""
        all_data = []
        for symbol in symbols:
            data = _self.get_stock_data(symbol, period)
            if not data.empty:
                all_data.append(data)
        
        if all_data:
            return pd.concat(all_data, ignore_index=True)
        return pd.DataFrame()
    
    @st.cache_data(ttl=3600)  # 1 hour cache
    def get_market_indices(_self) -> Dict[str, float]:
        """Get major market indices"""
        start_time = time.time()
        logger.info("Fetching market indices")
        
        try:
            indices = {
                'S&P 500': '^GSPC',
                'NASDAQ': '^IXIC',
                'Dow Jones': '^DJI',
                'Russell 2000': '^RUT',
                'VIX': '^VIX'
            }
            
            results = {}
            rate_limit_hit = False
            
            for name, symbol in indices.items():
                try:
                    # Rate limiting
                    current_time = time.time()
                    time_since_last_call = current_time - _self.last_api_call
                    if time_since_last_call < _self.rate_limit_delay:
                        sleep_time = _self.rate_limit_delay - time_since_last_call
                        logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f}s")
                        time.sleep(sleep_time)
                    
                    logger.debug(f"Fetching {name} ({symbol})")
                    ticker = yf.Ticker(symbol)
                    data = ticker.history(period="2d")
                    
                    _self.last_api_call = time.time()
                    
                    if not data.empty:
                        current = data['Close'].iloc[-1]
                        previous = data['Close'].iloc[-2]
                        change = ((current - previous) / previous) * 100
                        results[name] = {
                            'value': current,
                            'change': change,
                            'symbol': symbol
                        }
                        logger.debug(f"Successfully fetched {name}: {current:.2f} ({change:+.2f}%)")
                    else:
                        logger.warning(f"No data returned for {name}")
                        
                except Exception as e:
                    error_msg = str(e)
                    logger.api_call(f"yfinance_index_{symbol}", "FAILED", None, error_msg)
                    
                    # Check for rate limiting
                    if "Too Many Requests" in error_msg or "Rate limited" in error_msg:
                        logger.rate_limit(f"yfinance_index_{symbol}")
                        rate_limit_hit = True
                        st.warning(f"Rate limited for {name}. Using cached data if available.")
                    else:
                        logger.warning(f"Error fetching {name}: {e}")
                        st.warning(f"Error fetching {name}: {e}")
            
            response_time = time.time() - start_time
            
            if results:
                logger.api_call("yfinance_market_indices", "SUCCESS", response_time)
                logger.info(f"Successfully fetched {len(results)} market indices")
            else:
                logger.api_call("yfinance_market_indices", "FAILED", response_time, "No indices fetched")
            
            # If rate limited or no results, try fallback
            if not results or rate_limit_hit:
                if MOCK_DATA_AVAILABLE and mock_market_data:
                    logger.data_fallback("market_indices", "Rate limited or no data")
                    st.warning("Using mock market indices (real data unavailable)")
                    return mock_market_data.get_market_indices()
            
            return results
            
        except Exception as e:
            response_time = time.time() - start_time
            logger.api_call("yfinance_market_indices", "FAILED", response_time, str(e))
            
            # Fallback to mock data
            if MOCK_DATA_AVAILABLE and mock_market_data:
                logger.data_fallback("market_indices", str(e))
                st.warning("Using mock market indices (real data unavailable)")
                return mock_market_data.get_market_indices()
            else:
                logger.error(f"Error fetching market indices: {e}")
                st.error(f"Error fetching market indices: {e}")
                return {}
    
    @st.cache_data(ttl=3600)
    def get_treasury_rates(_self) -> Dict[str, float]:
        """Get Treasury rates"""
        try:
            treasury_symbols = {
                '3M': '^IRX',
                '10Y': '^TNX',
                '30Y': '^TYX'
            }
            
            results = {}
            for name, symbol in treasury_symbols.items():
                try:
                    ticker = yf.Ticker(symbol)
                    data = ticker.history(period="2d")
                    if not data.empty:
                        current = data['Close'].iloc[-1]
                        previous = data['Close'].iloc[-2]
                        change = current - previous
                        results[name] = {
                            'value': current,
                            'change': change
                        }
                except Exception as e:
                    st.warning(f"Error fetching {name} Treasury: {e}")
                    
            return results
        except Exception as e:
            # Fallback to mock data
            if MOCK_DATA_AVAILABLE and mock_market_data:
                st.warning("Using mock treasury rates (real data unavailable)")
                return mock_market_data.get_treasury_rates()
            else:
                st.error(f"Error fetching treasury rates: {e}")
                return {}
    
    @st.cache_data(ttl=3600)
    def get_commodities(_self) -> Dict[str, float]:
        """Get commodity prices"""
        try:
            commodities = {
                'Gold': 'GC=F',
                'Silver': 'SI=F',
                'Oil (WTI)': 'CL=F',
                'Natural Gas': 'NG=F'
            }
            
            results = {}
            for name, symbol in commodities.items():
                try:
                    ticker = yf.Ticker(symbol)
                    data = ticker.history(period="2d")
                    if not data.empty:
                        current = data['Close'].iloc[-1]
                        previous = data['Close'].iloc[-2]
                        change = ((current - previous) / previous) * 100
                        results[name] = {
                            'value': current,
                            'change': change
                        }
                except Exception as e:
                    st.warning(f"Error fetching {name}: {e}")
                    
            return results
        except Exception as e:
            # Fallback to mock data
            if MOCK_DATA_AVAILABLE and mock_market_data:
                st.warning("Using mock commodities data (real data unavailable)")
                return mock_market_data.get_commodities()
            else:
                st.error(f"Error fetching commodities: {e}")
                return {}
    
    @st.cache_data(ttl=1800)  # 30 minutes cache
    def get_financial_news(_self, limit: int = 20) -> List[Dict]:
        """Get financial news from RSS feeds"""
        try:
            news_sources = [
                'https://feeds.finance.yahoo.com/rss/2.0/headline',
                'https://www.cnbc.com/id/100003114/device/rss/rss.html',
                'https://www.marketwatch.com/rss/topstories'
            ]
            
            all_news = []
            for source in news_sources:
                try:
                    feed = feedparser.parse(source)
                    for entry in feed.entries[:limit//len(news_sources)]:
                        # Simple sentiment analysis
                        sentiment = TextBlob(entry.title + " " + entry.get('summary', '')).sentiment.polarity
                        
                        all_news.append({
                            'title': entry.title,
                            'summary': entry.get('summary', '')[:200] + '...',
                            'link': entry.link,
                            'published': entry.get('published', ''),
                            'sentiment': sentiment,
                            'source': source.split('/')[2]  # Extract domain
                        })
                except Exception as e:
                    st.warning(f"Error fetching news from {source}: {e}")
            
            # Sort by publication date (newest first)
            all_news.sort(key=lambda x: x.get('published', ''), reverse=True)
            return all_news[:limit]
        except Exception as e:
            # Fallback to mock data
            if MOCK_DATA_AVAILABLE and mock_market_data:
                st.warning("Using mock news data (real data unavailable)")
                return mock_market_data.get_financial_news(limit)
            else:
                st.error(f"Error fetching news: {e}")
                return []
    
    def get_stock_info(_self, symbol: str) -> Dict:
        """Get detailed stock information"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Clean and extract relevant information
            stock_info = {
                'symbol': symbol,
                'name': info.get('longName', symbol),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', 0),
                'price_to_book': info.get('priceToBook', 0),
                'dividend_yield': info.get('dividendYield', 0),
                'beta': info.get('beta', 0),
                'eps': info.get('trailingEps', 0),
                'revenue_growth': info.get('revenueGrowth', 0),
                'profit_margins': info.get('profitMargins', 0),
                'current_price': info.get('currentPrice', 0),
                'target_price': info.get('targetMeanPrice', 0),
                'recommendation': info.get('recommendationMean', 0)
            }
            
            return stock_info
        except Exception as e:
            # Fallback to mock data
            if MOCK_DATA_AVAILABLE and mock_market_data:
                st.warning(f"Using mock stock info for {symbol} (real data unavailable)")
                return mock_market_data.get_stock_info(symbol)
            else:
                st.error(f"Error fetching stock info for {symbol}: {e}")
                return {}
    
    @st.cache_data(ttl=3600)
    def get_yield_curve(_self) -> pd.DataFrame:
        """Get yield curve data"""
        try:
            maturities = {
                '1M': '^IRX',  # 3-month used as proxy
                '3M': '^IRX',
                '6M': '^IRX',
                '1Y': '^IRX',
                '2Y': '^TNX',  # 10-year used as proxy
                '3Y': '^TNX',
                '5Y': '^TNX',
                '7Y': '^TNX',
                '10Y': '^TNX',
                '20Y': '^TYX',  # 30-year used as proxy
                '30Y': '^TYX'
            }
            
            yield_data = []
            for maturity, symbol in maturities.items():
                try:
                    ticker = yf.Ticker(symbol)
                    data = ticker.history(period="1d")
                    if not data.empty:
                        rate = data['Close'].iloc[-1]
                        # Simple interpolation for missing maturities
                        if maturity in ['1M', '6M', '1Y']:
                            rate = rate * (0.5 + 0.1 * ['1M', '6M', '1Y'].index(maturity))
                        elif maturity in ['2Y', '3Y', '5Y', '7Y']:
                            rate = rate * (0.7 + 0.1 * ['2Y', '3Y', '5Y', '7Y'].index(maturity))
                        elif maturity in ['20Y']:
                            rate = rate * 0.95
                            
                        yield_data.append({
                            'maturity': maturity,
                            'rate': rate,
                            'years': {'1M': 0.08, '3M': 0.25, '6M': 0.5, '1Y': 1, '2Y': 2, 
                                    '3Y': 3, '5Y': 5, '7Y': 7, '10Y': 10, '20Y': 20, '30Y': 30}[maturity]
                        })
                except Exception as e:
                    st.warning(f"Error fetching yield for {maturity}: {e}")
            
            return pd.DataFrame(yield_data)
        except Exception as e:
            # Fallback to mock data
            if MOCK_DATA_AVAILABLE and mock_market_data:
                st.warning("Using mock yield curve data (real data unavailable)")
                return mock_market_data.get_yield_curve()
            else:
                st.error(f"Error fetching yield curve: {e}")
                return pd.DataFrame()

# Global market data provider instance
market_data = MarketDataProvider()

# Import mock data as fallback
try:
    from .mock_data import mock_market_data
    MOCK_DATA_AVAILABLE = True
except ImportError:
    MOCK_DATA_AVAILABLE = False
    mock_market_data = None 