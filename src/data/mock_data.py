import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any

class MockMarketDataProvider:
    """Mock market data provider for testing and demo purposes"""
    
    def __init__(self):
        self.base_date = datetime.now()
    
    def get_stock_data(self, symbol: str, period: str = "1y") -> pd.DataFrame:
        """Generate mock stock data"""
        # Calculate number of days based on period
        if period == "1d":
            days = 1
        elif period == "5d":
            days = 5
        elif period == "1mo":
            days = 30
        elif period == "3mo":
            days = 90
        elif period == "6mo":
            days = 180
        else:  # 1y
            days = 365
        
        # Generate dates
        dates = pd.date_range(end=self.base_date, periods=days, freq='D')
        
        # Generate mock OHLCV data
        np.random.seed(hash(symbol) % 1000)  # Consistent data for same symbol
        
        # Start with a base price
        base_price = 100.0 if symbol == "AAPL" else 50.0
        
        # Generate price movements
        returns = np.random.normal(0.001, 0.02, days)  # Daily returns
        prices = [base_price]
        
        for ret in returns[1:]:
            new_price = prices[-1] * (1 + ret)
            prices.append(max(new_price, 1.0))  # Ensure price doesn't go below 1
        
        # Generate OHLCV data
        data = []
        for i, (date, close) in enumerate(zip(dates, prices)):
            # Generate OHLC from close price
            volatility = 0.02
            high = close * (1 + abs(np.random.normal(0, volatility)))
            low = close * (1 - abs(np.random.normal(0, volatility)))
            open_price = close * (1 + np.random.normal(0, volatility * 0.5))
            
            # Ensure OHLC relationships
            high = max(high, open_price, close)
            low = min(low, open_price, close)
            
            # Generate volume
            volume = int(np.random.uniform(1000000, 10000000))
            
            data.append({
                'Date': date,
                'Open': round(open_price, 2),
                'High': round(high, 2),
                'Low': round(low, 2),
                'Close': round(close, 2),
                'Volume': volume,
                'Symbol': symbol
            })
        
        return pd.DataFrame(data)
    
    def get_market_indices(self) -> Dict[str, float]:
        """Generate mock market indices"""
        indices = {
            'S&P 500': {'value': 4500.0, 'change': 0.5},
            'NASDAQ': {'value': 14000.0, 'change': 0.8},
            'Dow Jones': {'value': 35000.0, 'change': 0.3},
            'Russell 2000': {'value': 1800.0, 'change': -0.2},
            'VIX': {'value': 18.5, 'change': -2.1}
        }
        
        # Add symbols for reference
        for name in indices:
            indices[name]['symbol'] = f"^{name.replace(' ', '')}" if name != 'VIX' else '^VIX'
        
        return indices
    
    def get_treasury_rates(self) -> Dict[str, float]:
        """Generate mock treasury rates"""
        return {
            '3M': {'value': 5.25, 'change': 0.05},
            '10Y': {'value': 4.85, 'change': -0.02},
            '30Y': {'value': 4.95, 'change': 0.01}
        }
    
    def get_commodities(self) -> Dict[str, float]:
        """Generate mock commodities data"""
        return {
            'Gold': {'value': 1950.0, 'change': 0.8},
            'Silver': {'value': 24.5, 'change': 1.2},
            'Oil (WTI)': {'value': 75.0, 'change': -1.5},
            'Natural Gas': {'value': 2.85, 'change': 0.3}
        }
    
    def get_financial_news(self, limit: int = 20) -> List[Dict]:
        """Generate mock financial news"""
        news_items = [
            {
                'title': 'Federal Reserve Signals Potential Rate Cut',
                'summary': 'The Federal Reserve indicated today that it may consider cutting interest rates in the coming months as inflation continues to moderate...',
                'link': 'https://example.com/news1',
                'published': '2024-01-15T10:30:00Z',
                'sentiment': 0.3,
                'source': 'financial-news.com'
            },
            {
                'title': 'Tech Stocks Rally on Strong Earnings Reports',
                'summary': 'Major technology companies reported better-than-expected earnings, driving a broad market rally...',
                'link': 'https://example.com/news2',
                'published': '2024-01-15T09:15:00Z',
                'sentiment': 0.7,
                'source': 'market-watch.com'
            },
            {
                'title': 'Oil Prices Decline on Increased Supply',
                'summary': 'Crude oil prices fell today as OPEC+ announced increased production quotas...',
                'link': 'https://example.com/news3',
                'published': '2024-01-15T08:45:00Z',
                'sentiment': -0.2,
                'source': 'energy-news.com'
            },
            {
                'title': 'Treasury Yields Flatten as Investors Seek Safety',
                'summary': 'Investors moved into government bonds today, causing yields to decline across the curve...',
                'link': 'https://example.com/news4',
                'published': '2024-01-15T08:00:00Z',
                'sentiment': -0.1,
                'source': 'bond-market.com'
            },
            {
                'title': 'Retail Sales Exceed Expectations',
                'summary': 'Consumer spending remained strong in December, with retail sales growing 0.6%...',
                'link': 'https://example.com/news5',
                'published': '2024-01-15T07:30:00Z',
                'sentiment': 0.5,
                'source': 'economic-data.com'
            }
        ]
        
        return news_items[:limit]
    
    def get_stock_info(self, symbol: str) -> Dict:
        """Generate mock stock information"""
        # Generate consistent info based on symbol
        np.random.seed(hash(symbol) % 1000)
        
        base_price = 150.0 if symbol == "AAPL" else 300.0 if symbol == "MSFT" else 100.0
        
        return {
            'symbol': symbol,
            'name': f'{symbol} Corporation',
            'sector': 'Technology',
            'industry': 'Software',
            'market_cap': base_price * 1000000000,  # 1B shares
            'pe_ratio': np.random.uniform(15, 30),
            'price_to_book': np.random.uniform(2, 8),
            'dividend_yield': np.random.uniform(0, 0.03),
            'beta': np.random.uniform(0.8, 1.5),
            'eps': base_price * 0.05,
            'revenue_growth': np.random.uniform(0.05, 0.25),
            'profit_margins': np.random.uniform(0.1, 0.3),
            'current_price': base_price,
            'target_price': base_price * np.random.uniform(0.9, 1.2),
            'recommendation': np.random.uniform(1.5, 2.5)
        }
    
    def get_yield_curve(self) -> pd.DataFrame:
        """Generate mock yield curve data"""
        maturities = ['1M', '3M', '6M', '1Y', '2Y', '3Y', '5Y', '7Y', '10Y', '20Y', '30Y']
        years = [0.08, 0.25, 0.5, 1, 2, 3, 5, 7, 10, 20, 30]
        
        # Generate realistic yield curve
        base_rate = 5.0
        rates = []
        
        for i, year in enumerate(years):
            if year <= 1:
                rate = base_rate * (0.8 + 0.2 * year)
            elif year <= 10:
                rate = base_rate * (0.9 + 0.1 * (year - 1) / 9)
            else:
                rate = base_rate * (1.0 + 0.05 * (year - 10) / 20)
            
            # Add some noise
            rate += np.random.normal(0, 0.1)
            rates.append(max(rate, 0.1))  # Ensure positive rates
        
        return pd.DataFrame({
            'maturity': maturities,
            'rate': rates,
            'years': years
        })

# Global mock data provider instance
mock_market_data = MockMarketDataProvider() 