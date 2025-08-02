# HedgeLab - Investment Analysis Tool (Work in Progress)

![Python](https://img.shields.io/badge/Python-3.8%2B-green)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-red)
![Status](https://img.shields.io/badge/Status-Work%20in%20Progress-orange)

> **Quick Start**: Run `python setup.py` then `python run.py` to get started!

**HedgeLab** is a personal learning project - a simple investment analysis tool built with Streamlit. It's designed to help me learn about financial markets, data analysis, and web development. This is definitely not professional-grade software!

## ⚠️ Important Disclaimers

- **This is a learning project** - not professional investment software
- **Work in progress** - features may be buggy or incomplete
- **Not financial advice** - just educational tools for learning
- **Use at your own risk** - I'm still learning, so please don't rely on this for real trading
- **Free data sources** - using Yahoo Finance which has rate limits

## 🌟 What I'm Trying to Build

### 🌍 Market Overview
- Basic market indices display (S&P 500, NASDAQ, etc.)
- Simple yield curve visualization
- Commodities prices (when data is available)
- News feed from financial sources
- Market sentiment indicators

### 🔍 Stock Analysis
- Basic technical indicators (RSI, MACD, moving averages)
- Simple stock screening tools
- News sentiment analysis (very basic)
- Custom filters for finding stocks

### 💼 Portfolio Tracking
- Simple trade logging
- Basic position tracking
- Performance calculations
- Risk metrics (basic ones)

### 📊 Reports
- PDF report generation (learning ReportLab)
- Excel exports
- Performance summaries

## 🚀 Getting Started (Simple Setup)

### Prerequisites
- Python 3.8 or higher
- pip package manager

### 1. Quick Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/HedgeLab.git
cd HedgeLab

# Run the setup script (installs dependencies)
python setup.py
```

### 2. Configuration (Optional)

The app works without any API keys, but you can add some for extra features:

```env
# Supabase (optional - for cloud storage)
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# Reddit API (optional - for sentiment)
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
```

### 3. Run the Application

```bash
# Start the app (recommended)
python run.py

# Or directly with Streamlit
streamlit run main.py

# Or run the demo first
python demo.py
```

### 4. Access the Application

Open your browser and go to: `http://localhost:8501`

## 📋 How to Use (Basic Guide)

### Getting Started
1. **Check Macro View**: See what the overall market looks like
2. **Try Opportunity Detection**: Look for stocks that might be interesting
3. **Log Some Trades**: Practice tracking hypothetical trades
4. **Check Performance**: See how your portfolio is doing
5. **Generate Reports**: Try the reporting features

### What to Expect
- **Transparent API Limits**: Clear messages when Yahoo Finance rate limits are hit
- **Simple UI**: Basic Streamlit interface - easy to use
- **Learning Focus**: This is about understanding the concepts, not professional trading
- **Rate Limit Handling**: Built-in protection and clear error messages

## 🛠️ Technical Stuff (For Developers)

### Project Structure
```
hedgelab/
├── src/
│   ├── macro/           # Market overview stuff
│   ├── opportunities/   # Stock screening  
│   ├── portfolio/      # Trade tracking
│   ├── data/           # Data fetching
│   └── ui/            # UI components
├── main.py            # Main app file
├── requirements.txt   # Python packages needed
└── setup.py          # Setup helper
```

### What I'm Using
- **Frontend**: Streamlit (easy to learn)
- **Charts**: Plotly (nice looking graphs)
- **Market Data**: Yahoo Finance (free, but rate limited)
- **Database**: Supabase (optional) or just local files
- **News**: RSS feeds (simple and free)
- **Sentiment**: TextBlob (basic sentiment analysis)
- **Technical Analysis**: TA library (standard indicators)

### Data Sources
- **Market Data**: Yahoo Finance (free, rate limited)
- **News**: RSS feeds from financial sites
- **Error Handling**: Clear messages when APIs are unavailable

## 🔧 Configuration Options

### Database (Optional)
- **Local Storage**: Works out of the box, no setup needed
- **Supabase**: If you want cloud storage (optional)

### API Keys (All Optional)
- **Reddit**: For social sentiment (optional)
- **News API**: For premium news (optional)

## 📊 Data and Limitations

### What Works
- Basic market data (when Yahoo Finance cooperates)
- Clear error messages when APIs are rate limited
- Simple technical analysis
- Basic portfolio tracking

### What Doesn't Work Well
- Real-time data (rate limited)
- Advanced features (still learning)
- Professional-grade analysis (this is a learning project)
- Mobile optimization (desktop only)

## 🚨 Important Warnings

**Please understand this is a learning project:**

- **Not financial advice** - I'm learning, not advising
- **Educational only** - Don't use for real trading decisions
- **Bugs expected** - Still working on it
- **Limited data** - Using free APIs with restrictions
- **Basic features** - Nothing advanced here

## 🤝 Contributing (If You Want to Help)

I'm learning, so any help is appreciated! But please understand this is a personal learning project.

### Development Setup
```bash
# Clone the repository
git clone https://github.com/yourusername/HedgeLab.git
cd HedgeLab

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run main.py
```

## 📄 License

MIT License - feel free to use this code for learning.

## 🆘 Getting Help

- **Issues**: Report bugs on GitHub (but remember this is a learning project)
- **Questions**: GitHub Discussions (I'll try to help, but I'm learning too)

## 🎯 What I'm Working On

- [ ] Fixing bugs (there are probably many)
- [ ] Improving the UI (making it less basic)
- [ ] Adding more features (slowly, as I learn)
- [ ] Better error handling (when APIs fail)
- [ ] Better documentation

## 📈 Current Status

This is very much a work in progress:

- **Load Time**: Sometimes slow (learning optimization)
- **Data Updates**: When APIs work (often rate limited)
- **UI Quality**: Basic but functional
- **Features**: Basic ones work, advanced ones in progress

---

**Built as a learning project - not professional software!**

*HedgeLab - A simple tool for learning about investment analysis*

**Remember: This is educational software, not professional investment advice!**
