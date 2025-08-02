#!/usr/bin/env python3
"""
HedgeLab Application Runner
Simple script to start the HedgeLab Streamlit application
"""

import os
import sys
import subprocess
from pathlib import Path

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

def run_hedgelab():
    """Run the HedgeLab application"""
    print("🚀 Starting HedgeLab...")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not Path("main.py").exists():
        print("❌ main.py not found. Please run this script from the HedgeLab directory.")
        return False
    
    # Check and run setup if needed
    if not check_and_setup():
        print("\n❌ Setup failed. Please run 'python setup.py' manually.")
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