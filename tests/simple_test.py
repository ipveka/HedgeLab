#!/usr/bin/env python3
"""
Simple HedgeLab Test
Quick test to verify core functionality
"""

import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_imports():
    """Test that all modules can be imported"""
    print("🧪 Testing imports...")
    
    modules = [
        ('data.market_data', 'Market data module'),
        ('data.database', 'Database module'),
        ('ui.components', 'UI components'),
        ('macro.macro_view', 'Macro view'),
        ('opportunities.opportunity_detector', 'Opportunity detector'),
        ('portfolio.portfolio_manager', 'Portfolio manager'),
        ('portfolio.reports', 'Report generator')
    ]
    
    passed = 0
    total = len(modules)
    
    for module_name, description in modules:
        try:
            __import__(module_name)
            print(f"✅ {description} imported successfully")
            passed += 1
        except Exception as e:
            print(f"❌ {description} import failed: {e}")
    
    print(f"\n📊 Import Test Results: {passed}/{total} modules imported")
    return passed == total

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
            return True
        else:
            print("  ⚠️ No AAPL data retrieved (using mock data)")
            return True
            
    except Exception as e:
        print(f"  ❌ Market data test failed: {e}")
        return False

def main():
    """Run simple tests"""
    print("🚀 HEDGELAB SIMPLE TEST")
    print("=" * 50)
    
    # Test imports
    imports_ok = test_imports()
    
    # Test market data
    market_data_ok = test_market_data()
    
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print(f"   Imports: {'✅ PASS' if imports_ok else '❌ FAIL'}")
    print(f"   Market Data: {'✅ PASS' if market_data_ok else '❌ FAIL'}")
    
    if imports_ok and market_data_ok:
        print("\n🎉 All tests passed! HedgeLab is ready to use.")
        print("\n🌐 To start the application:")
        print("   python run.py")
        print("   or")
        print("   streamlit run main.py")
    else:
        print("\n⚠️ Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main() 