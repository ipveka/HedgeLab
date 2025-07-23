import os
import pandas as pd
from typing import Optional, Dict, List, Any
from datetime import datetime, date
import streamlit as st

# Try to import Supabase, but handle gracefully if not available
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    Client = None

class Database:
    _instance = None
    _client: Optional[Client] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._client is None:
            self.connect()
    
    def connect(self):
        """Initialize Supabase client"""
        if not SUPABASE_AVAILABLE:
            st.warning("Supabase not available. Using local storage mode.")
            self._client = None
            return
            
        try:
            url = os.getenv("SUPABASE_URL")
            key = os.getenv("SUPABASE_KEY")
            
            if not url or not key:
                st.warning("Supabase credentials not found. Using local storage mode.")
                self._client = None
                return
                
            self._client = create_client(url, key)
            st.success("✅ Connected to Supabase database")
        except Exception as e:
            st.error(f"Failed to connect to database: {e}")
            self._client = None
    
    @property
    def client(self) -> Optional[Client]:
        return self._client
    
    def is_connected(self) -> bool:
        return self._client is not None

    # Market Data Operations
    def save_market_data(self, data: pd.DataFrame) -> bool:
        """Save market data to database"""
        if not self.is_connected():
            return False
            
        try:
            records = data.to_dict('records')
            for record in records:
                # Convert datetime objects to strings
                if 'date' in record and isinstance(record['date'], (datetime, date)):
                    record['date'] = record['date'].isoformat()
                    
            result = self._client.table('market_data').upsert(records).execute()
            return True
        except Exception as e:
            st.error(f"Error saving market data: {e}")
            return False
    
    def get_market_data(self, symbol: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """Retrieve market data from database"""
        if not self.is_connected():
            return pd.DataFrame()
            
        try:
            query = self._client.table('market_data').select('*').eq('symbol', symbol)
            
            if start_date:
                query = query.gte('date', start_date)
            if end_date:
                query = query.lte('date', end_date)
                
            result = query.execute()
            return pd.DataFrame(result.data)
        except Exception as e:
            st.error(f"Error retrieving market data: {e}")
            return pd.DataFrame()

    # Opportunities Operations
    def save_opportunity(self, opportunity: Dict[str, Any]) -> bool:
        """Save opportunity to database"""
        if not self.is_connected():
            return False
            
        try:
            # Convert datetime objects to strings
            if 'date' in opportunity and isinstance(opportunity['date'], (datetime, date)):
                opportunity['date'] = opportunity['date'].isoformat()
                
            result = self._client.table('opportunities').insert(opportunity).execute()
            return True
        except Exception as e:
            st.error(f"Error saving opportunity: {e}")
            return False
    
    def get_opportunities(self, strategy: str = None, limit: int = 100) -> pd.DataFrame:
        """Retrieve opportunities from database"""
        if not self.is_connected():
            return pd.DataFrame()
            
        try:
            query = self._client.table('opportunities').select('*').limit(limit)
            
            if strategy:
                query = query.eq('strategy', strategy)
                
            result = query.order('date', desc=True).execute()
            return pd.DataFrame(result.data)
        except Exception as e:
            st.error(f"Error retrieving opportunities: {e}")
            return pd.DataFrame()

    # Portfolio Operations
    def save_trade(self, trade: Dict[str, Any]) -> bool:
        """Save trade to database"""
        if not self.is_connected():
            return False
            
        try:
            # Convert datetime objects to strings
            if 'timestamp' in trade and isinstance(trade['timestamp'], datetime):
                trade['timestamp'] = trade['timestamp'].isoformat()
                
            result = self._client.table('trades').insert(trade).execute()
            return True
        except Exception as e:
            st.error(f"Error saving trade: {e}")
            return False
    
    def get_trades(self, symbol: str = None) -> pd.DataFrame:
        """Retrieve trades from database"""
        if not self.is_connected():
            return pd.DataFrame()
            
        try:
            query = self._client.table('trades').select('*')
            
            if symbol:
                query = query.eq('symbol', symbol)
                
            result = query.order('timestamp', desc=True).execute()
            return pd.DataFrame(result.data)
        except Exception as e:
            st.error(f"Error retrieving trades: {e}")
            return pd.DataFrame()
    
    def get_positions(self) -> pd.DataFrame:
        """Retrieve current positions from database"""
        if not self.is_connected():
            return pd.DataFrame()
            
        try:
            result = self._client.table('positions').select('*').execute()
            return pd.DataFrame(result.data)
        except Exception as e:
            st.error(f"Error retrieving positions: {e}")
            return pd.DataFrame()
    
    def update_position(self, symbol: str, quantity: float, avg_cost: float, pnl: float) -> bool:
        """Update position in database"""
        if not self.is_connected():
            return False
            
        try:
            position_data = {
                'symbol': symbol,
                'quantity': quantity,
                'avg_cost': avg_cost,
                'pnl': pnl,
                'updated_at': datetime.now().isoformat()
            }
            
            result = self._client.table('positions').upsert(position_data).execute()
            return True
        except Exception as e:
            st.error(f"Error updating position: {e}")
            return False

    # Portfolio Performance Operations
    def save_portfolio_performance(self, performance: Dict[str, Any]) -> bool:
        """Save portfolio performance data"""
        if not self.is_connected():
            return False
            
        try:
            if 'date' in performance and isinstance(performance['date'], (datetime, date)):
                performance['date'] = performance['date'].isoformat()
                
            result = self._client.table('portfolio_performance').upsert(performance).execute()
            return True
        except Exception as e:
            st.error(f"Error saving portfolio performance: {e}")
            return False
    
    def get_portfolio_performance(self, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """Retrieve portfolio performance data"""
        if not self.is_connected():
            return pd.DataFrame()
            
        try:
            query = self._client.table('portfolio_performance').select('*')
            
            if start_date:
                query = query.gte('date', start_date)
            if end_date:
                query = query.lte('date', end_date)
                
            result = query.order('date', desc=True).execute()
            return pd.DataFrame(result.data)
        except Exception as e:
            st.error(f"Error retrieving portfolio performance: {e}")
            return pd.DataFrame()

# Global database instance
db = Database() 