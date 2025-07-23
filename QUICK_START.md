# HedgeLab Quick Start Guide

## 🚀 Get Started in 3 Steps

### 1. Setup (Already Done!)
```bash
# Dependencies are already installed
# Environment file is already created
# Project structure is ready
```

### 2. Start the Application
```bash
# Option 1: Use the run script
python run.py

# Option 2: Direct Streamlit command
streamlit run main.py
```

### 3. Access HedgeLab
Open your browser and go to: **http://localhost:8501**

## 📋 What's Available

### 🌍 Macro Economic View
- **Real-time Market Indices**: S&P 500, NASDAQ, Dow Jones, Russell 2000, VIX
- **Treasury Yield Curve**: Live yield curve with inversion detection
- **Commodities**: Gold, Silver, Oil, Natural Gas prices
- **Economic News**: Aggregated financial news with sentiment analysis
- **Market Sentiment**: Fear & Greed index based on VIX

### 🔍 Opportunity Detection
- **Technical Analysis**: RSI, MACD, Moving Averages, Bollinger Bands
- **Stock Screening**: Value, growth, momentum, technical signals
- **Custom Scanners**: Multiple strategy filters
- **Signal Strength**: Quantified opportunity scoring

### 💼 Portfolio Management
- **Trade Logging**: Complete trade history with P&L tracking
- **Position Management**: Real-time position tracking
- **Performance Analytics**: Returns, Sharpe ratio, drawdown analysis
- **Risk Management**: Portfolio risk metrics

### 📊 Professional Reports
- **PDF Reports**: Professional investment reports
- **Excel Exports**: Detailed spreadsheets
- **Performance Analytics**: Comprehensive breakdowns
- **Tax Reporting**: Capital gains/losses

## 🎯 Key Features

✅ **Works Immediately**: No API keys required for basic functionality  
✅ **Free Data**: Yahoo Finance integration (no cost)  
✅ **Professional UI**: Bloomberg-inspired design  
✅ **Real-time Updates**: Live market data during trading hours  
✅ **Complete Workflow**: Analysis → Detection → Trading → Reporting  

## 🔧 Configuration (Optional)

### Add API Keys for Enhanced Features
Edit `.env` file:
```env
# Supabase (for cloud database)
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# Reddit API (for sentiment analysis)
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
```

### Database Setup (Optional)
1. Create Supabase account at [supabase.com](https://supabase.com)
2. Create new project
3. Run `init_database.sql` in Supabase SQL editor
4. Add credentials to `.env` file

## 🧪 Testing

Run the test suite to verify functionality:
```bash
python test_app.py
```

## 📁 Project Structure
```
hedgelab/
├── main.py              # Application entry point
├── run.py               # Application runner
├── setup.py             # Setup script
├── test_app.py          # Test suite
├── demo.py              # Demo script
├── requirements.txt     # Dependencies
├── init_database.sql    # Database schema
├── src/
│   ├── macro/           # Economic dashboard
│   ├── opportunities/   # Stock screening
│   ├── portfolio/      # Trading & performance
│   ├── data/           # Data providers
│   └── ui/            # Shared components
└── README.md           # Complete documentation
```

## 🚨 Important Notes

- **Educational Use**: This is for educational and analytical purposes only
- **Not Financial Advice**: Consult professionals before making investment decisions
- **Demo Mode**: Works without external APIs using Yahoo Finance data
- **Network Required**: Some features require internet connection for live data

## 🆘 Troubleshooting

### Application Won't Start
```bash
# Check dependencies
pip install -r requirements.txt

# Check Python version (3.8+ required)
python --version
```

### No Market Data
- Check internet connection
- Yahoo Finance may be temporarily unavailable
- Try refreshing the page

### Database Issues
- Application works in local mode without database
- Check Supabase credentials in `.env` file
- Verify database schema is created

## 🎉 You're Ready!

HedgeLab is now running and ready for professional investment analysis!

**Next Steps:**
1. Explore the Macro View for market overview
2. Use Opportunity Detection to find potential trades
3. Log trades in Portfolio Management
4. Generate reports for analysis

**Happy Trading! 📈** 