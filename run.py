#!/usr/bin/env python3
"""
HedgeLab Application Runner
Simple script to start the HedgeLab Streamlit application
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import streamlit
        import pandas
        import plotly
        import yfinance
        print("✅ All core dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("💡 Run 'python setup.py' to install dependencies")
        return False

def run_hedgelab():
    """Run the HedgeLab application"""
    print("🚀 Starting HedgeLab...")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not Path("main.py").exists():
        print("❌ main.py not found. Please run this script from the HedgeLab directory.")
        return False
    
    # Check dependencies
    if not check_dependencies():
        return False
    
    # Check for .env file
    if not Path(".env").exists():
        print("⚠️  No .env file found. Running in demo mode.")
        print("💡 Run 'python setup.py' to create environment configuration")
    
    # Start Streamlit
    print("🌐 Starting Streamlit server...")
    print("📱 Application will open at: http://localhost:8501")
    print("🛑 Press Ctrl+C to stop the application")
    print("-" * 40)
    
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "main.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 HedgeLab stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting HedgeLab: {e}")
        return False
    
    return True

if __name__ == "__main__":
    run_hedgelab() 