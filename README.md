# HedgeLab - Professional Investment Management Platform

![HedgeLab](https://img.shields.io/badge/HedgeLab-Professional%20Trading-blue)
![Python](https://img.shields.io/badge/Python-3.8%2B-green)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-red)
![License](https://img.shields.io/badge/License-MIT-yellow)

**HedgeLab** is a professional-grade investment management platform built with Streamlit. It provides institutional-quality tools for market analysis, opportunity detection, portfolio management, and performance reporting.

## 🌟 Features

### 🌍 Macro Economic View
- **Global Market Overview**: Real-time indices (S&P 500, NASDAQ, Dow Jones, Russell 2000, VIX)
- **Treasury Yield Curve**: Live yield curve analysis with inversion detection
- **Commodities Tracking**: Gold, Silver, Oil, Natural Gas prices
- **Economic News Feed**: Aggregated financial news with sentiment analysis
- **Market Sentiment**: Fear & Greed index based on VIX levels

### 🔍 Opportunity Detection
- **Technical Analysis**: RSI, MACD, Moving Averages, Bollinger Bands
- **Fundamental Screening**: P/E ratios, growth metrics, value indicators  
- **Sentiment Analysis**: News sentiment, social media buzz indicators
- **Custom Scanners**: Technical signals, value stocks, growth stocks, momentum plays
- **Backtesting**: Strategy performance validation

### 💼 Portfolio Management
- **Trade Logging**: Complete trade history with P&L tracking
- **Position Management**: Real-time position tracking and valuation
- **Performance Analytics**: Returns, Sharpe ratio, drawdown analysis
- **Risk Management**: Portfolio risk metrics and alerts
- **Real-time P&L**: Live profit/loss calculations

### 📊 Professional Reporting
- **PDF Reports**: Professional investment reports with charts
- **Excel Exports**: Detailed spreadsheets for further analysis
- **Performance Analytics**: Comprehensive performance breakdowns
- **Tax Reporting**: Capital gains/losses for tax purposes

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/HedgeLab.git
cd HedgeLab

# Run the setup script
python setup.py
```

### 2. Configuration (Optional)

Edit the `.env` file to add your API keys:

```env
# Supabase (for cloud database - optional)
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# Reddit API (for sentiment analysis - optional)
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
```

### 3. Run the Application

```bash
# Start HedgeLab
python run.py

# Or directly with Streamlit
streamlit run main.py
```

### 4. Access the Application

Open your browser and navigate to: `http://localhost:8501`

## 📋 Usage Guide

### Getting Started
1. **Explore Macro View**: Start with the global market overview
2. **Scan for Opportunities**: Use the opportunity detector to find potential trades
3. **Log Trades**: Record your trades using the portfolio manager
4. **Monitor Performance**: Track your portfolio's performance over time
5. **Generate Reports**: Create professional reports for analysis

### Key Workflows

#### 1. Market Analysis Workflow
```
Macro View → Market Indices → News Sentiment → Opportunity Scanner
```

#### 2. Trading Workflow  
```
Opportunity Detection → Technical Analysis → Trade Logging → Position Tracking
```

#### 3. Performance Review Workflow
```
Portfolio Overview → Performance Analytics → Report Generation
```

## 🛠️ Technical Architecture

### Project Structure
```
hedgelab/
├── src/
│   ├── macro/           # Economic dashboard
│   ├── opportunities/   # Stock screening  
│   ├── portfolio/      # Trading & performance
│   ├── data/           # Data providers
│   └── ui/            # Shared components
├── main.py            # Application entry point
├── requirements.txt   # Dependencies
└── setup.py          # Setup script
```

### Tech Stack
- **Frontend**: Streamlit for interactive web interface
- **Data Visualization**: Plotly for professional charts
- **Market Data**: Yahoo Finance (free, no API key required)
- **Database**: Supabase (optional) or local storage
- **News**: RSS feeds from major financial sources
- **Sentiment**: TextBlob for basic sentiment analysis
- **Technical Analysis**: TA-Lib indicators
- **Reports**: ReportLab for PDF generation

### Data Sources
- **Market Data**: Yahoo Finance (free)
- **News**: Yahoo Finance, CNBC, MarketWatch RSS feeds
- **Economic Data**: Federal Reserve Economic Data (FRED)
- **Social Sentiment**: Reddit API (optional)

## 🔧 Configuration

### Database Options

#### Option 1: Local Storage (Default)
No setup required. Data stored locally.

#### Option 2: Supabase Cloud Database
1. Create account at [supabase.com](https://supabase.com)
2. Create new project
3. Add URL and key to `.env` file
4. Database tables will be created automatically

### API Keys (All Optional)

#### Reddit API (for sentiment analysis)
1. Create Reddit app at [reddit.com/prefs/apps](https://reddit.com/prefs/apps)
2. Add client ID and secret to `.env`

#### News API (for premium news)
1. Get API key from [newsapi.org](https://newsapi.org)
2. Add to `.env` file

## 📊 Sample Data

HedgeLab works immediately with demo data. For full functionality:

1. **Demo Mode**: Works with Yahoo Finance data (no setup required)
2. **Live Mode**: Add API keys for enhanced features
3. **Cloud Mode**: Use Supabase for data persistence

## 🚨 Risk Disclaimer

**Important**: HedgeLab is for educational and analytical purposes only. 

- Not financial advice
- Past performance doesn't guarantee future results  
- Trading involves substantial risk of loss
- Consult with financial professionals before making investment decisions
- Users are responsible for their own trading decisions

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup
```bash
# Clone the repository
git clone https://github.com/yourusername/HedgeLab.git
cd HedgeLab

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt

# Run in development mode
streamlit run main.py
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check the in-app help sections
- **Issues**: Report bugs on [GitHub Issues](https://github.com/yourusername/HedgeLab/issues)
- **Discussions**: Join our [GitHub Discussions](https://github.com/yourusername/HedgeLab/discussions)

## 🎯 Roadmap

- [ ] Machine learning price predictions
- [ ] Options trading analysis
- [ ] Cryptocurrency support
- [ ] Advanced risk models
- [ ] Mobile app
- [ ] API integrations with brokers
- [ ] Multi-portfolio support
- [ ] Team collaboration features

## 📈 Performance Standards

HedgeLab is designed for professional use:

- **Load Time**: < 2 seconds
- **Real-time Updates**: During market hours
- **Data Caching**: 15-minute intervals
- **UI Quality**: Bloomberg-terminal inspired design
- **Workflow**: Complete analysis → detection → trading → reporting pipeline

---

**Built with ❤️ for professional traders and investment managers**

*HedgeLab - Where professional investment management meets modern technology*
