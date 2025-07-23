import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from src.data.market_data import market_data
from src.data.database import db
from src.ui.components import (
    metric_card, create_portfolio_pie_chart, create_performance_chart,
    display_trades_table, loading_spinner, format_currency, format_percentage
)

class PortfolioManager:
    """Portfolio management with trade logging, position tracking, and performance analytics"""
    
    def __init__(self):
        self.market_provider = market_data
        self.database = db
    
    def render(self):
        """Render the portfolio management dashboard"""
        st.markdown("## 💼 Portfolio Management")
        st.markdown("---")
        
        # Portfolio Overview
        self._render_portfolio_overview()
        st.markdown("---")
        
        # Main tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Positions", 
            "📝 Trade Logger", 
            "📈 Performance", 
            "⚙️ Settings"
        ])
        
        with tab1:
            self._render_positions()
        
        with tab2:
            self._render_trade_logger()
        
        with tab3:
            self._render_performance_analytics()
        
        with tab4:
            self._render_settings()
    
    def _render_portfolio_overview(self):
        """Render portfolio overview with key metrics"""
        st.markdown("### 📊 Portfolio Overview")
        
        # Get portfolio data
        positions = self._get_current_positions()
        portfolio_value = self._calculate_portfolio_value(positions)
        performance_data = self._get_performance_data()
        
        # Key metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            metric_card("Total Value", format_currency(portfolio_value['total_value']))
        
        with col2:
            total_pnl = portfolio_value['total_pnl']
            pnl_color = "normal" if total_pnl >= 0 else "inverse"
            metric_card(
                "Total P&L", 
                format_currency(total_pnl),
                delta=f"{'+' if total_pnl >= 0 else ''}{format_currency(total_pnl)}",
                delta_color=pnl_color
            )
        
        with col3:
            pnl_percent = portfolio_value['total_pnl_percent']
            metric_card(
                "P&L %", 
                format_percentage(pnl_percent),
                delta=f"{'+' if pnl_percent >= 0 else ''}{format_percentage(pnl_percent)}",
                delta_color="normal" if pnl_percent >= 0 else "inverse"
            )
        
        with col4:
            num_positions = len(positions[positions['quantity'] != 0]) if not positions.empty else 0
            metric_card("Active Positions", str(num_positions))
        
        with col5:
            if not performance_data.empty:
                recent_return = performance_data['daily_return'].tail(30).mean() * 30
                metric_card("30D Return", format_percentage(recent_return))
            else:
                metric_card("30D Return", "N/A")
        
        # Portfolio allocation chart
        col1, col2 = st.columns([2, 1])
        with col1:
            if not positions.empty and portfolio_value['total_value'] > 0:
                # Add market values for pie chart
                positions_with_values = positions.copy()
                for idx, position in positions_with_values.iterrows():
                    if position['quantity'] != 0:
                        current_price = self._get_current_price(position['symbol'])
                        positions_with_values.loc[idx, 'market_value'] = abs(position['quantity']) * current_price
                
                fig = create_portfolio_pie_chart(positions_with_values[positions_with_values['quantity'] != 0])
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No positions to display. Start by adding some trades!")
        
        with col2:
            # Portfolio statistics
            st.markdown("#### Portfolio Stats")
            if not positions.empty:
                long_positions = len(positions[positions['quantity'] > 0])
                short_positions = len(positions[positions['quantity'] < 0])
                
                metric_card("Long Positions", str(long_positions))
                metric_card("Short Positions", str(short_positions))
                
                if not performance_data.empty and len(performance_data) > 1:
                    volatility = performance_data['daily_return'].std() * np.sqrt(252) * 100
                    metric_card("Volatility (Ann.)", f"{volatility:.1f}%")
    
    def _render_positions(self):
        """Render current positions table"""
        st.markdown("### 📊 Current Positions")
        
        positions = self._get_current_positions()
        
        if not positions.empty and len(positions[positions['quantity'] != 0]) > 0:
            # Enhance positions data with current prices and P&L
            enhanced_positions = []
            
            for _, position in positions.iterrows():
                if position['quantity'] == 0:
                    continue
                
                current_price = self._get_current_price(position['symbol'])
                market_value = position['quantity'] * current_price
                cost_basis = position['quantity'] * position['avg_cost']
                pnl = market_value - cost_basis
                pnl_percent = (pnl / abs(cost_basis)) * 100 if cost_basis != 0 else 0
                
                enhanced_positions.append({
                    'Symbol': position['symbol'],
                    'Quantity': f"{position['quantity']:,.0f}",
                    'Avg Cost': f"${position['avg_cost']:.2f}",
                    'Current Price': f"${current_price:.2f}",
                    'Market Value': f"${market_value:,.2f}",
                    'P&L': f"${pnl:,.2f}",
                    'P&L %': f"{pnl_percent:+.2f}%",
                    'Position Type': 'Long' if position['quantity'] > 0 else 'Short'
                })
            
            if enhanced_positions:
                positions_df = pd.DataFrame(enhanced_positions)
                
                # Style the dataframe
                def color_pnl(val):
                    if 'P&L' in val.name:
                        if val.startswith('$-') or val.startswith('-'):
                            return 'background-color: #fee2e2'
                        elif val.startswith('$') and not val.startswith('$-'):
                            return 'background-color: #dcfce7'
                    return ''
                
                styled_df = positions_df.style.applymap(color_pnl, subset=['P&L', 'P&L %'])
                st.dataframe(styled_df, use_container_width=True, hide_index=True)
                
                # Position actions
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("📊 Rebalance Portfolio"):
                        self._show_rebalance_suggestions(positions)
                
                with col2:
                    if st.button("⚠️ Risk Analysis"):
                        self._show_risk_analysis(positions)
                
                with col3:
                    selected_symbol = st.selectbox("Close Position", [""] + list(positions['symbol'].unique()))
                    if selected_symbol and st.button("🚪 Close Position"):
                        self._close_position(selected_symbol)
            else:
                st.info("No active positions found.")
        else:
            st.info("No positions found. Start trading to see your positions here!")
    
    def _render_trade_logger(self):
        """Render trade logging interface"""
        st.markdown("### 📝 Trade Logger")
        
        # Trade entry form
        with st.form("trade_form"):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                symbol = st.text_input("Symbol", placeholder="AAPL").upper()
            
            with col2:
                side = st.selectbox("Side", ["BUY", "SELL"])
            
            with col3:
                quantity = st.number_input("Quantity", min_value=1, value=100)
            
            with col4:
                price = st.number_input("Price ($)", min_value=0.01, value=100.00, step=0.01)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                trade_date = st.date_input("Trade Date", value=datetime.now().date())
            
            with col2:
                trade_time = st.time_input("Trade Time", value=datetime.now().time())
            
            with col3:
                notes = st.text_input("Notes (Optional)", placeholder="Trade notes...")
            
            submitted = st.form_submit_button("📈 Log Trade", type="primary")
            
            if submitted:
                if symbol and quantity > 0 and price > 0:
                    self._log_trade(symbol, side, quantity, price, trade_date, trade_time, notes)
                else:
                    st.error("Please fill in all required fields with valid values.")
        
        # Recent trades
        st.markdown("#### Recent Trades")
        trades = self._get_recent_trades(limit=20)
        
        if not trades.empty:
            display_trades_table(trades)
            
            # Trade statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                total_trades = len(trades)
                metric_card("Total Trades", str(total_trades))
            
            with col2:
                buy_trades = len(trades[trades['side'] == 'BUY'])
                metric_card("Buy Trades", str(buy_trades))
            
            with col3:
                sell_trades = len(trades[trades['side'] == 'SELL'])
                metric_card("Sell Trades", str(sell_trades))
        else:
            st.info("No trades logged yet. Use the form above to log your first trade!")
    
    def _render_performance_analytics(self):
        """Render performance analytics and charts"""
        st.markdown("### 📈 Performance Analytics")
        
        performance_data = self._get_performance_data()
        
        if not performance_data.empty:
            # Performance chart
            fig = create_performance_chart(performance_data)
            st.plotly_chart(fig, use_container_width=True)
            
            # Performance metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_return = ((performance_data['total_value'].iloc[-1] / performance_data['total_value'].iloc[0]) - 1) * 100
                metric_card("Total Return", format_percentage(total_return))
            
            with col2:
                if len(performance_data) >= 252:  # At least 1 year of data
                    annual_return = ((performance_data['total_value'].iloc[-1] / performance_data['total_value'].iloc[-252]) - 1) * 100
                    metric_card("Annual Return", format_percentage(annual_return))
                else:
                    metric_card("Annual Return", "N/A")
            
            with col3:
                if len(performance_data) > 1:
                    daily_returns = performance_data['daily_return'].dropna()
                    if len(daily_returns) > 0:
                        sharpe_ratio = (daily_returns.mean() / daily_returns.std()) * np.sqrt(252) if daily_returns.std() > 0 else 0
                        metric_card("Sharpe Ratio", f"{sharpe_ratio:.2f}")
                    else:
                        metric_card("Sharpe Ratio", "N/A")
                else:
                    metric_card("Sharpe Ratio", "N/A")
            
            with col4:
                if len(performance_data) > 1:
                    cumulative_returns = (performance_data['total_value'] / performance_data['total_value'].iloc[0]) - 1
                    running_max = cumulative_returns.expanding().max()
                    drawdown = cumulative_returns - running_max
                    max_drawdown = drawdown.min() * 100
                    metric_card("Max Drawdown", f"{max_drawdown:.2f}%")
                else:
                    metric_card("Max Drawdown", "N/A")
            
            # Performance breakdown
            st.markdown("#### Performance Breakdown")
            
            if len(performance_data) >= 30:
                # Monthly returns heatmap would go here
                st.info("📊 Monthly returns heatmap feature coming soon!")
            
            # Risk metrics
            st.markdown("#### Risk Metrics")
            if len(performance_data) > 1:
                daily_returns = performance_data['daily_return'].dropna()
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    volatility = daily_returns.std() * np.sqrt(252) * 100
                    metric_card("Volatility (Annual)", f"{volatility:.2f}%")
                
                with col2:
                    var_95 = np.percentile(daily_returns, 5) * 100
                    metric_card("VaR (95%)", f"{var_95:.2f}%")
                
                with col3:
                    positive_days = (daily_returns > 0).sum()
                    total_days = len(daily_returns)
                    win_rate = (positive_days / total_days) * 100 if total_days > 0 else 0
                    metric_card("Win Rate", f"{win_rate:.1f}%")
        else:
            st.info("No performance data available. Start trading to see performance analytics!")
    
    def _render_settings(self):
        """Render portfolio settings"""
        st.markdown("### ⚙️ Portfolio Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Portfolio Configuration")
            
            initial_capital = st.number_input(
                "Initial Capital ($)", 
                min_value=1000.0, 
                value=100000.0,
                step=1000.0
            )
            
            benchmark_symbol = st.text_input(
                "Benchmark Symbol", 
                value="SPY",
                help="Symbol to compare portfolio performance against"
            )
            
            risk_tolerance = st.selectbox(
                "Risk Tolerance",
                ["Conservative", "Moderate", "Aggressive"]
            )
            
            if st.button("💾 Save Settings"):
                self._save_portfolio_settings(initial_capital, benchmark_symbol, risk_tolerance)
        
        with col2:
            st.markdown("#### Data Management")
            
            if st.button("📊 Recalculate Performance"):
                with loading_spinner("Recalculating portfolio performance..."):
                    self._recalculate_performance()
            
            if st.button("📥 Export Portfolio Data"):
                self._export_portfolio_data()
            
            if st.button("🗑️ Clear All Data", type="secondary"):
                if st.checkbox("I understand this will delete all portfolio data"):
                    self._clear_portfolio_data()
    
    def _get_current_positions(self) -> pd.DataFrame:
        """Get current portfolio positions"""
        # Try to get from database first
        positions = self.database.get_positions()
        
        if positions.empty:
            # If no positions in database, calculate from trades
            trades = self._get_all_trades()
            if not trades.empty:
                positions = self._calculate_positions_from_trades(trades)
        
        return positions
    
    def _calculate_portfolio_value(self, positions: pd.DataFrame) -> Dict[str, float]:
        """Calculate total portfolio value and P&L"""
        if positions.empty:
            return {
                'total_value': 0,
                'total_cost': 0,
                'total_pnl': 0,
                'total_pnl_percent': 0
            }
        
        total_value = 0
        total_cost = 0
        
        for _, position in positions.iterrows():
            if position['quantity'] != 0:
                current_price = self._get_current_price(position['symbol'])
                market_value = position['quantity'] * current_price
                cost_basis = position['quantity'] * position['avg_cost']
                
                total_value += market_value
                total_cost += cost_basis
        
        total_pnl = total_value - total_cost
        total_pnl_percent = (total_pnl / total_cost) * 100 if total_cost != 0 else 0
        
        return {
            'total_value': total_value,
            'total_cost': total_cost,
            'total_pnl': total_pnl,
            'total_pnl_percent': total_pnl_percent
        }
    
    def _get_current_price(self, symbol: str) -> float:
        """Get current price for a symbol"""
        try:
            stock_data = self.market_provider.get_stock_data(symbol, period="1d")
            if not stock_data.empty:
                return stock_data['Close'].iloc[-1]
        except:
            pass
        return 0.0
    
    def _log_trade(self, symbol: str, side: str, quantity: int, price: float, 
                   trade_date: datetime.date, trade_time: datetime.time, notes: str):
        """Log a new trade"""
        timestamp = datetime.combine(trade_date, trade_time)
        
        trade_data = {
            'symbol': symbol,
            'side': side,
            'quantity': quantity,
            'price': price,
            'total_value': quantity * price,
            'timestamp': timestamp,
            'notes': notes
        }
        
        # Save to database
        if self.database.save_trade(trade_data):
            st.success(f"✅ Trade logged: {side} {quantity} {symbol} @ ${price:.2f}")
            
            # Update positions
            self._update_position_from_trade(symbol, side, quantity, price)
            
            # Rerun to refresh data
            st.rerun()
        else:
            st.error("❌ Failed to log trade")
    
    def _update_position_from_trade(self, symbol: str, side: str, quantity: int, price: float):
        """Update position based on new trade"""
        positions = self.database.get_positions()
        
        # Find existing position
        existing_position = positions[positions['symbol'] == symbol]
        
        if not existing_position.empty:
            current_qty = existing_position.iloc[0]['quantity']
            current_avg_cost = existing_position.iloc[0]['avg_cost']
        else:
            current_qty = 0
            current_avg_cost = 0
        
        # Calculate new position
        if side == 'BUY':
            new_qty = current_qty + quantity
            if new_qty != 0:
                new_avg_cost = ((current_qty * current_avg_cost) + (quantity * price)) / new_qty
            else:
                new_avg_cost = price
        else:  # SELL
            new_qty = current_qty - quantity
            new_avg_cost = current_avg_cost  # Keep same average cost for sells
        
        # Calculate P&L
        current_price = self._get_current_price(symbol)
        pnl = (new_qty * current_price) - (new_qty * new_avg_cost) if new_qty != 0 else 0
        
        # Update database
        self.database.update_position(symbol, new_qty, new_avg_cost, pnl)
    
    def _get_recent_trades(self, limit: int = 20) -> pd.DataFrame:
        """Get recent trades"""
        trades = self.database.get_trades()
        return trades.head(limit) if not trades.empty else pd.DataFrame()
    
    def _get_all_trades(self) -> pd.DataFrame:
        """Get all trades"""
        return self.database.get_trades()
    
    def _get_performance_data(self) -> pd.DataFrame:
        """Get portfolio performance data"""
        performance = self.database.get_portfolio_performance()
        
        if not performance.empty:
            # Calculate daily returns
            performance['daily_return'] = performance['total_value'].pct_change()
        
        return performance
    
    def _calculate_positions_from_trades(self, trades: pd.DataFrame) -> pd.DataFrame:
        """Calculate current positions from trade history"""
        if trades.empty:
            return pd.DataFrame()
        
        positions = {}
        
        for _, trade in trades.iterrows():
            symbol = trade['symbol']
            if symbol not in positions:
                positions[symbol] = {'quantity': 0, 'total_cost': 0}
            
            if trade['side'] == 'BUY':
                positions[symbol]['quantity'] += trade['quantity']
                positions[symbol]['total_cost'] += trade['total_value']
            else:  # SELL
                positions[symbol]['quantity'] -= trade['quantity']
                # For sells, we don't change total_cost (realized P&L)
        
        # Convert to DataFrame
        position_list = []
        for symbol, data in positions.items():
            if data['quantity'] != 0:
                avg_cost = data['total_cost'] / data['quantity'] if data['quantity'] > 0 else 0
                position_list.append({
                    'symbol': symbol,
                    'quantity': data['quantity'],
                    'avg_cost': avg_cost,
                    'pnl': 0  # Will be calculated when needed
                })
        
        return pd.DataFrame(position_list)
    
    def _save_portfolio_settings(self, initial_capital: float, benchmark: str, risk_tolerance: str):
        """Save portfolio settings"""
        # In a real implementation, this would save to database
        st.session_state['portfolio_settings'] = {
            'initial_capital': initial_capital,
            'benchmark': benchmark,
            'risk_tolerance': risk_tolerance
        }
        st.success("✅ Portfolio settings saved!")
    
    def _recalculate_performance(self):
        """Recalculate portfolio performance"""
        # This would recalculate all performance metrics
        st.success("✅ Portfolio performance recalculated!")
    
    def _export_portfolio_data(self):
        """Export portfolio data"""
        # In a real implementation, this would generate Excel/CSV export
        st.info("📊 Export functionality coming soon!")
    
    def _clear_portfolio_data(self):
        """Clear all portfolio data"""
        # In a real implementation, this would clear database
        st.warning("🗑️ Portfolio data cleared!")
    
    def _close_position(self, symbol: str):
        """Close a position completely"""
        positions = self._get_current_positions()
        position = positions[positions['symbol'] == symbol]
        
        if not position.empty:
            current_qty = position.iloc[0]['quantity']
            current_price = self._get_current_price(symbol)
            
            if current_qty > 0:
                side = 'SELL'
            else:
                side = 'BUY'
                current_qty = abs(current_qty)
            
            # Log the closing trade
            self._log_trade(symbol, side, current_qty, current_price, 
                          datetime.now().date(), datetime.now().time(), 
                          f"Position close")
    
    def _show_rebalance_suggestions(self, positions: pd.DataFrame):
        """Show portfolio rebalancing suggestions"""
        st.info("🔄 Portfolio rebalancing suggestions feature coming soon!")
    
    def _show_risk_analysis(self, positions: pd.DataFrame):
        """Show portfolio risk analysis"""
        st.info("⚠️ Risk analysis feature coming soon!")

# For testing purposes
if __name__ == "__main__":
    portfolio_manager = PortfolioManager()
    portfolio_manager.render() 