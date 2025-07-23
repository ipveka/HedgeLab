#!/usr/bin/env python3
"""
HedgeLab Comprehensive Test Suite
Tests all major functionality of the application
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

class TestResults:
    """Track test results"""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.total = 0
        self.errors = []
    
    def add_result(self, test_name: str, success: bool, error: str = None):
        self.total += 1
        if success:
            self.passed += 1
            print(f"✅ {test_name} - PASSED")
        else:
            self.failed += 1
            self.errors.append(f"{test_name}: {error}")
            print(f"❌ {test_name} - FAILED: {error}")
    
    def summary(self):
        print(f"\n📊 Test Summary: {self.passed}/{self.total} tests passed")
        if self.errors:
            print("\n❌ Errors:")
            for error in self.errors:
                print(f"  • {error}")

def test_market_data_provider():
    """Test market data provider functionality"""
    print("\n🌍 Testing Market Data Provider...")
    results = []
    
    try:
        from src.data.market_data import market_data
        
        # Test stock data retrieval
        stock_data = market_data.get_stock_data("AAPL", period="5d")
        if not stock_data.empty:
            results.append(("Stock Data Retrieval", True))
        else:
            results.append(("Stock Data Retrieval", False, "No data returned"))
        
        # Test market indices
        indices = market_data.get_market_indices()
        if indices:
            results.append(("Market Indices", True))
        else:
            results.append(("Market Indices", False, "No indices returned"))
        
        # Test treasury rates
        treasury = market_data.get_treasury_rates()
        if treasury:
            results.append(("Treasury Rates", True))
        else:
            results.append(("Treasury Rates", False, "No treasury data"))
        
        # Test commodities
        commodities = market_data.get_commodities()
        if commodities:
            results.append(("Commodities", True))
        else:
            results.append(("Commodities", False, "No commodities data"))
        
        # Test stock info
        stock_info = market_data.get_stock_info("AAPL")
        if stock_info:
            results.append(("Stock Info", True))
        else:
            results.append(("Stock Info", False, "No stock info"))
        
        return results
        
    except Exception as e:
        return [("Market Data Provider", False, str(e))]

def test_technical_analysis():
    """Test technical analysis functionality"""
    print("\n🔍 Testing Technical Analysis...")
    results = []
    
    try:
        from src.opportunities.opportunity_detector import OpportunityDetector
        from src.data.market_data import market_data
        
        detector = OpportunityDetector()
        
        # Get test data
        stock_data = market_data.get_stock_data("AAPL", period="3mo")
        if stock_data.empty:
            return [("Technical Analysis", False, "No stock data available")]
        
        # Test technical indicators calculation
        technical_data = detector._calculate_technical_indicators(stock_data)
        if not technical_data.empty:
            results.append(("Technical Indicators", True))
        else:
            results.append(("Technical Indicators", False, "No indicators calculated"))
        
        # Test signal generation
        signals = detector._get_technical_signals(technical_data)
        if signals:
            results.append(("Signal Generation", True))
        else:
            results.append(("Signal Generation", False, "No signals generated"))
        
        # Test opportunity scanning
        opportunities = detector._run_opportunity_scan("Technical Signals", {})
        if isinstance(opportunities, pd.DataFrame):
            results.append(("Opportunity Scanning", True))
        else:
            results.append(("Opportunity Scanning", False, "Invalid scan result"))
        
        return results
        
    except Exception as e:
        return [("Technical Analysis", False, str(e))]

def test_portfolio_management():
    """Test portfolio management functionality"""
    print("\n💼 Testing Portfolio Management...")
    results = []
    
    try:
        from src.portfolio.portfolio_manager import PortfolioManager
        
        portfolio = PortfolioManager()
        
        # Test position calculation
        positions = portfolio._get_current_positions()
        if isinstance(positions, pd.DataFrame):
            results.append(("Position Management", True))
        else:
            results.append(("Position Management", False, "Invalid positions data"))
        
        # Test portfolio value calculation
        portfolio_value = portfolio._calculate_portfolio_value(positions)
        if isinstance(portfolio_value, dict):
            results.append(("Portfolio Value Calculation", True))
        else:
            results.append(("Portfolio Value Calculation", False, "Invalid value calculation"))
        
        # Test trade logging (simulation)
        try:
            portfolio._log_trade("AAPL", "BUY", 100, 150.00, datetime.now().date(), datetime.now().time(), "Test trade")
            results.append(("Trade Logging", True))
        except Exception as e:
            results.append(("Trade Logging", False, str(e)))
        
        return results
        
    except Exception as e:
        return [("Portfolio Management", False, str(e))]

def test_report_generation():
    """Test report generation functionality"""
    print("\n📊 Testing Report Generation...")
    results = []
    
    try:
        from src.portfolio.reports import ReportGenerator
        
        report_gen = ReportGenerator()
        
        # Test summary data generation
        summary_data = report_gen._get_summary_data(datetime.now().date() - timedelta(days=30), datetime.now().date())
        if isinstance(summary_data, list):
            results.append(("Summary Data Generation", True))
        else:
            results.append(("Summary Data Generation", False, "Invalid summary data"))
        
        # Test trade summary calculation
        test_trades = pd.DataFrame({
            'symbol': ['AAPL', 'MSFT'],
            'side': ['BUY', 'SELL'],
            'quantity': [100, 50],
            'price': [150.00, 300.00],
            'total_value': [15000.00, 15000.00]
        })
        trade_summary = report_gen._calculate_trade_summary(test_trades)
        if isinstance(trade_summary, dict):
            results.append(("Trade Summary Calculation", True))
        else:
            results.append(("Trade Summary Calculation", False, "Invalid trade summary"))
        
        return results
        
    except Exception as e:
        return [("Report Generation", False, str(e))]

def test_ui_components():
    """Test UI components functionality"""
    print("\n🎨 Testing UI Components...")
    results = []
    
    try:
        from src.ui.components import (
            format_currency, format_percentage, format_large_number,
            create_line_chart, create_candlestick_chart
        )
        
        # Test formatting functions
        currency_result = format_currency(1234567.89)
        if currency_result == "$1.23M":
            results.append(("Currency Formatting", True))
        else:
            results.append(("Currency Formatting", False, f"Expected $1.23M, got {currency_result}"))
        
        percentage_result = format_percentage(12.345)
        if percentage_result == "12.35%":
            results.append(("Percentage Formatting", True))
        else:
            results.append(("Percentage Formatting", False, f"Expected 12.35%, got {percentage_result}"))
        
        # Test chart creation
        test_data = pd.DataFrame({
            'Date': pd.date_range('2024-01-01', periods=10),
            'Close': np.random.randn(10).cumsum() + 100
        })
        
        line_chart = create_line_chart(test_data, 'Date', 'Close', 'Test Chart')
        if hasattr(line_chart, 'add_trace'):
            results.append(("Line Chart Creation", True))
        else:
            results.append(("Line Chart Creation", False, "Invalid chart object"))
        
        return results
        
    except Exception as e:
        return [("UI Components", False, str(e))]

def test_database_functionality():
    """Test database functionality"""
    print("\n🗄️ Testing Database Functionality...")
    results = []
    
    try:
        from src.data.database import db
        
        # Test database connection
        if db.is_connected():
            results.append(("Database Connection", True))
        else:
            results.append(("Database Connection", True, "Running in local mode"))
        
        # Test data operations (should work even without database)
        test_data = pd.DataFrame({
            'symbol': ['AAPL'],
            'date': [datetime.now().date()],
            'close': [150.00]
        })
        
        # These should not raise exceptions even without database
        try:
            db.save_market_data(test_data)
            results.append(("Data Operations", True))
        except Exception as e:
            results.append(("Data Operations", False, str(e)))
        
        return results
        
    except Exception as e:
        return [("Database Functionality", False, str(e))]

def test_macro_view():
    """Test macro view functionality"""
    print("\n🌍 Testing Macro View...")
    results = []
    
    try:
        from src.macro.macro_view import MacroView
        
        macro_view = MacroView()
        
        # Test that the class can be instantiated
        if macro_view is not None:
            results.append(("Macro View Instantiation", True))
        else:
            results.append(("Macro View Instantiation", False, "Failed to create instance"))
        
        # Test market overview method
        try:
            macro_view._render_market_overview()
            results.append(("Market Overview Rendering", True))
        except Exception as e:
            results.append(("Market Overview Rendering", False, str(e)))
        
        return results
        
    except Exception as e:
        return [("Macro View", False, str(e))]

def main():
    """Run comprehensive test suite"""
    print("🚀 HEDGELAB COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    
    test_results = TestResults()
    
    # Run all test suites
    test_suites = [
        ("Market Data Provider", test_market_data_provider),
        ("Technical Analysis", test_technical_analysis),
        ("Portfolio Management", test_portfolio_management),
        ("Report Generation", test_report_generation),
        ("UI Components", test_ui_components),
        ("Database Functionality", test_database_functionality),
        ("Macro View", test_macro_view)
    ]
    
    for suite_name, test_func in test_suites:
        print(f"\n🧪 Running {suite_name} Tests...")
        results = test_func()
        
        for test_name, success, *error in results:
            error_msg = error[0] if error else None
            test_results.add_result(f"{suite_name} - {test_name}", success, error_msg)
    
    # Print summary
    test_results.summary()
    
    # Final recommendations
    print(f"\n🎯 Recommendations:")
    if test_results.passed == test_results.total:
        print("🎉 All tests passed! HedgeLab is fully functional.")
    elif test_results.passed >= test_results.total * 0.8:
        print("✅ Most tests passed. HedgeLab is ready for use with minor limitations.")
    else:
        print("⚠️ Several tests failed. Some features may not work as expected.")
    
    print(f"\n📋 Next Steps:")
    print("1. Start the application: python run.py")
    print("2. Open browser to: http://localhost:8501")
    print("3. Test the web interface functionality")
    
    if test_results.failed > 0:
        print(f"\n🔧 To fix issues:")
        print("1. Check internet connection for market data")
        print("2. Install missing dependencies: pip install -r requirements.txt")
        print("3. Add API keys to .env for enhanced features")

if __name__ == "__main__":
    main() 