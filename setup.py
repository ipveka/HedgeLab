#!/usr/bin/env python3
"""
HedgeLab Setup Script
Run this script to set up your HedgeLab environment
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during {description}: {e}")
        print(f"Output: {e.output}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def create_env_file():
    """Create .env file from template"""
    env_template = """# HedgeLab Environment Configuration
# Copy this file to .env and fill in your actual values

# Supabase Configuration (Optional - for cloud database)
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_anon_key_here

# Reddit API Configuration (Optional - for sentiment analysis)
REDDIT_CLIENT_ID=your_reddit_client_id_here
REDDIT_CLIENT_SECRET=your_reddit_client_secret_here
REDDIT_USER_AGENT=HedgeLab/1.0

# News API Configuration (Optional - for premium news sources)
NEWS_API_KEY=your_news_api_key_here

# Database Configuration (Optional - for custom database)
DATABASE_URL=postgresql://username:password@localhost:5432/hedgelab
"""
    
    env_file = Path(".env")
    if not env_file.exists():
        with open(env_file, "w") as f:
            f.write(env_template)
        print("✅ Created .env file - please edit it with your API keys")
    else:
        print("✅ .env file already exists")

def setup_hedgelab():
    """Main setup function"""
    print("🚀 Welcome to HedgeLab Setup!")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Install dependencies
    if not run_command("pip install -r requirements.txt", "Installing dependencies"):
        print("💡 Tip: Try using 'pip3 install -r requirements.txt' or create a virtual environment")
        return False
    
    # Create environment file
    create_env_file()
    
    # Create necessary directories
    directories = ["data", "logs", "exports"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    print("\n🎉 HedgeLab setup completed successfully!")
    print("\n📋 Next Steps:")
    print("1. Edit the .env file with your API keys (optional)")
    print("2. Run the application: streamlit run main.py")
    print("3. Open your browser to http://localhost:8501")
    
    print("\n📖 Documentation:")
    print("• Yahoo Finance data is free and works without API keys")
    print("• Supabase is optional for cloud database storage")
    print("• Reddit API is optional for sentiment analysis")
    print("• All features work in demo mode without external APIs")
    
    return True

if __name__ == "__main__":
    setup_hedgelab() 