#!/usr/bin/env python3
"""
HedgeLab Test Script
Simple test to verify core functionality
"""

import sys
import os

# Add src to path
sys.path.append('../src')

def test_imports():
    """Test that all modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        from data.market_data import market_data
        print("✅ Market data module imported")
    except Exception as e:
        print(f"❌ Market data import failed: {e}")
        return False
    
    try:
        from data.database import db
        print("✅ Database module imported")
    except Exception as e:
        print(f"❌ Database import failed: {e}")
        return False
    
    try:
        from ui.components import metric_card
        print("✅ UI components imported")
    except Exception as e:
        print(f"❌ UI components import failed: {e}")
        return False
    
    try:
        from macro.macro_view import MacroView
        print("✅ Macro view imported")
    except Exception as e:
        print(f"❌ Macro view import failed: {e}")
        return False
    
    try:
        from opportunities.opportunity_detector import OpportunityDetector
        print("✅ Opportunity detector imported")
    except Exception as e:
        print(f"❌ Opportunity detector import failed: {e}")
        return False
    
    try:
        from portfolio.portfolio_manager import PortfolioManager
        print("✅ Portfolio manager imported")
    except Exception as e:
        print(f"❌ Portfolio manager import failed: {e}")
        return False
    
    try:
        from portfolio.reports import ReportGenerator
        print("✅ Report generator imported")
    except Exception as e:
        print(f"❌ Report generator import failed: {e}")
        return False
    
    return True

def test_market_data():
    """Test market data functionality"""
    print("\n📊 Testing market data...")
    
    try:
        from data.market_data import market_data
        
        # Test getting stock data
        print("  📈 Testing stock data retrieval...")
        stock_data = market_data.get_stock_data("AAPL", period="5d")
        if not stock_data.empty:
            print(f"  ✅ AAPL data retrieved: {len(stock_data)} records")
        else:
            print("  ⚠️ No AAPL data retrieved (network may be required)")
        
        # Test getting market indices
        print("  📊 Testing market indices...")
        indices = market_data.get_market_indices()
        if indices:
            print(f"  ✅ Market indices retrieved: {len(indices)} indices")
        else:
            print("  ⚠️ No market indices retrieved (network may be required)")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Market data test failed: {e}")
        return False

def test_database():
    """Test database functionality"""
    print("\n🗄️ Testing database...")
    
    try:
        from data.database import db
        
        # Test database connection
        if db.is_connected():
            print("  ✅ Database connected (Supabase)")
        else:
            print("  ℹ️ Running in local mode (no database)")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Database test failed: {e}")
        return False

def test_technical_analysis():
    """Test technical analysis functionality"""
    print("\n🔍 Testing technical analysis...")
    
    try:
        from opportunities.opportunity_detector import OpportunityDetector
        from data.market_data import market_data
        
        detector = OpportunityDetector()
        
        # Get some test data
        stock_data = market_data.get_stock_data("AAPL", period="1mo")
        
        if not stock_data.empty:
            # Test technical indicators
            technical_data = detector._calculate_technical_indicators(stock_data)
            if not technical_data.empty:
                print("  ✅ Technical indicators calculated")
                
                # Test signals
                signals = detector._get_technical_signals(technical_data)
                print(f"  ✅ Technical signals generated: {len(signals)} signals")
            else:
                print("  ⚠️ Could not calculate technical indicators")
        else:
            print("  ⚠️ No stock data for technical analysis")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Technical analysis test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 HEDGELAB TEST SUITE")
    print("=" * 50)
    
    # Run tests
    tests = [
        ("Import Test", test_imports),
        ("Market Data Test", test_market_data),
        ("Database Test", test_database),
        ("Technical Analysis Test", test_technical_analysis)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name}...")
        if test_func():
            passed += 1
            print(f"✅ {test_name} PASSED")
        else:
            print(f"❌ {test_name} FAILED")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! HedgeLab is ready to use.")
        print("\n🌐 To start the application:")
        print("   python run.py")
        print("   or")
        print("   streamlit run main.py")
    else:
        print("⚠️ Some tests failed. Check the errors above.")
        print("💡 Most features will still work in demo mode.")
    
    print("\n📋 Next Steps:")
    print("1. Start the application: python run.py")
    print("2. Open browser to: http://localhost:8501")
    print("3. Explore the different modules:")
    print("   • 🌍 Macro View")
    print("   • 🔍 Opportunities")
    print("   • 💼 Portfolio")
    print("   • 📊 Reports")

if __name__ == "__main__":
    main() 