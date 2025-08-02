#!/usr/bin/env python3
"""
HedgeLab Demo Script
Demonstrates core functionality without the Streamlit interface
"""

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime, timedelta

def check_and_setup():
    """Check if setup is needed and run it if necessary"""
    print("🔧 Checking HedgeLab setup...")
    
    # Check if we're in the right directory
    if not Path("setup.py").exists():
        print("❌ setup.py not found. Please run from HedgeLab directory.")
        return False
    
    # Check if main dependencies are installed
    try:
        import streamlit
        import pandas
        import plotly
        import yfinance
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("🔧 Running setup to install dependencies...")
        
        try:
            result = subprocess.run([sys.executable, "setup.py"], 
                                  capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                print("✅ Setup completed successfully")
                return True
            else:
                print(f"❌ Setup failed: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            print("❌ Setup timed out")
            return False
        except Exception as e:
            print(f"❌ Setup error: {e}")
            return False

# Add src to path for imports
sys.path.append('src')

def demo_market_data():
    """Demo market data functionality"""
    print("🌍 MARKET DATA DEMO")
    print("=" * 50)
    
    try:
        from data.market_data import market_data
        
        # Get market indices
        print("📊 Fetching market indices...")
        indices = market_data.get_market_indices()
        
        if indices:
            for name, data in indices.items():
                change_symbol = "📈" if data['change'] >= 0 else "📉"
                print(f"{change_symbol} {name}: ${data['value']:,.2f} ({data['change']:+.2f}%)")
        else:
            print("⚠️ Could not fetch market data (API rate limit or network issue)")
            print("💡 Please wait a few minutes before trying again")
        
        print()
        
        # Get stock data
        print("📈 Fetching AAPL stock data...")
        stock_data = market_data.get_stock_data("AAPL", period="5d")
        
        if not stock_data.empty:
            latest = stock_data.iloc[-1]
            print(f"📊 AAPL Latest: ${latest['Close']:.2f}")
            print(f"📅 Date: {latest['Date'].strftime('%Y-%m-%d')}")
            print(f"📊 Volume: {latest['Volume']:,.0f}")
        else:
            print("⚠️ Could not fetch AAPL data (API rate limit or network issue)")
            print("💡 Please wait a few minutes before trying again")
            
    except Exception as e:
        print(f"❌ Error in market data demo: {e}")
    
    print()

def demo_technical_analysis():
    """Demo technical analysis functionality"""
    print("🔍 TECHNICAL ANALYSIS DEMO")
    print("=" * 50)
    
    try:
        from opportunities.opportunity_detector import OpportunityDetector
        
        detector = OpportunityDetector()
        
        # Get stock data and calculate indicators
        print("📊 Analyzing AAPL technical indicators...")
        
        from data.market_data import market_data
        stock_data = market_data.get_stock_data("AAPL", period="3mo")
        
        if not stock_data.empty:
            # Calculate technical indicators
            technical_data = detector._calculate_technical_indicators(stock_data)
            
            if not technical_data.empty:
                latest = technical_data.iloc[-1]
                
                print(f"📈 Current Price: ${latest['Close']:.2f}")
                print(f"📊 RSI: {latest['RSI']:.2f}")
                print(f"📊 20-day MA: ${latest['MA20']:.2f}")
                print(f"📊 50-day MA: ${latest['MA50']:.2f}")
                
                # Get signals
                signals = detector._get_technical_signals(technical_data)
                print("\n🎯 Technical Signals:")
                for signal_name, signal_data in signals.items():
                    emoji = "🟢" if signal_data['signal'] == "BUY" else "🔴" if signal_data['signal'] == "SELL" else "🟡"
                    print(f"{emoji} {signal_name}: {signal_data['signal']} (Strength: {signal_data['strength']:.2f})")
            else:
                print("⚠️ Could not calculate technical indicators (no data available)")
        else:
            print("⚠️ Could not fetch stock data for analysis (API rate limit or network issue)")
            print("💡 Please wait a few minutes before trying again")
            
    except Exception as e:
        print(f"❌ Error in technical analysis demo: {e}")
    
    print()

def demo_portfolio_simulation():
    """Demo portfolio functionality with simulated data"""
    print("💼 PORTFOLIO SIMULATION DEMO")
    print("=" * 50)
    
    try:
        # Simulate some trades
        trades = [
            {"symbol": "AAPL", "side": "BUY", "quantity": 100, "price": 150.00, "date": "2024-01-15"},
            {"symbol": "MSFT", "side": "BUY", "quantity": 50, "price": 300.00, "date": "2024-01-20"},
            {"symbol": "GOOGL", "side": "BUY", "quantity": 25, "price": 2800.00, "date": "2024-01-25"},
            {"symbol": "AAPL", "side": "SELL", "quantity": 50, "price": 155.00, "date": "2024-02-01"}
        ]
        
        print("📝 Simulated Trade History:")
        for trade in trades:
            total_value = trade['quantity'] * trade['price']
            print(f"📈 {trade['date']}: {trade['side']} {trade['quantity']} {trade['symbol']} @ ${trade['price']:.2f} = ${total_value:,.2f}")
        
        print("\n💰 Simulated Current Positions:")
        positions = {
            "AAPL": {"quantity": 50, "avg_cost": 150.00},
            "MSFT": {"quantity": 50, "avg_cost": 300.00},
            "GOOGL": {"quantity": 25, "avg_cost": 2800.00}
        }
        
        total_value = 0
        for symbol, position in positions.items():
            market_value = position['quantity'] * position['avg_cost'] * 1.05  # Simulate 5% gain
            total_value += market_value
            pnl = market_value - (position['quantity'] * position['avg_cost'])
            pnl_pct = (pnl / (position['quantity'] * position['avg_cost'])) * 100
            
            print(f"📊 {symbol}: {position['quantity']} shares @ ${position['avg_cost']:.2f} avg cost")
            print(f"   💰 Market Value: ${market_value:,.2f} | P&L: ${pnl:,.2f} ({pnl_pct:+.1f}%)")
        
        print(f"\n📈 Total Portfolio Value: ${total_value:,.2f}")
        print(f"💰 Total P&L: ${total_value * 0.05:,.2f} (+5.0%)")
        
    except Exception as e:
        print(f"❌ Error in portfolio demo: {e}")
    
    print()

def demo_database_connection():
    """Demo database connection"""
    print("🗄️ DATABASE CONNECTION DEMO")
    print("=" * 50)
    
    try:
        from data.database import db
        
        if db.is_connected():
            print("✅ Successfully connected to Supabase database")
        else:
            print("ℹ️ Running in local storage mode (no database connection)")
            print("💡 Add SUPABASE_URL and SUPABASE_KEY to .env for cloud database")
        
    except Exception as e:
        print(f"❌ Error testing database connection: {e}")
    
    print()

def main():
    """Run all demos"""
    print("🚀 HEDGELAB FUNCTIONALITY DEMO")
    print("=" * 70)
    print("Welcome to HedgeLab - A Simple Investment Learning Tool")
    print("This demo showcases the basic functionality without the web interface")
    print("=" * 70)
    print()
    
    # Check and run setup if needed
    if not check_and_setup():
        print("\n❌ Setup failed. Please run 'python setup.py' manually.")
        return False
    
    print()
    
    # Run demos
    demo_market_data()
    demo_technical_analysis()
    demo_portfolio_simulation()
    demo_database_connection()
    
    print("🎉 DEMO COMPLETED!")
    print("=" * 50)
    print("✅ HedgeLab demo completed successfully!")
    print("🌐 To start the web interface, run: python run.py")
    print("📖 Or use: streamlit run main.py")
    print("🔗 Then open: http://localhost:8501")
    print()
    print("📋 Basic Features Available:")
    print("• 🌍 Market Overview - Simple market indices and news")
    print("• 🔍 Stock Analysis - Basic technical indicators")
    print("• 💼 Portfolio Tracking - Simple trade logging")
    print("• 📊 Basic Reports - Simple PDF/Excel exports")
    print()
    print("💡 Tip: Uses free Yahoo Finance data - clear error messages when rate limited!")
    print("🚨 Disclaimer: This is a learning project. Not financial advice.")

if __name__ == "__main__":
    main() 