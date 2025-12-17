# Fluxo

**AI Automation-as-a-Service for Web3 Intelligence**

Fluxo is a comprehensive Web3 intelligence platform that provides automated analysis, monitoring, and insights for cryptocurrency portfolios and DeFi positions. Built with AI agents, real-time data pipelines, and multi-source intelligence gathering, Fluxo helps users make informed decisions in the fast-moving world of decentralized finance.

## 🎯 What We're Building

Fluxo is an intelligent backend system that combines:

- **Multi-Agent AI Analysis**: Specialized AI agents for different aspects of Web3 (risk, social sentiment, market data, governance, etc.)
- **Real-Time Monitoring**: Continuous tracking of wallet activities, whale movements, and market conditions
- **Smart Alerts**: Proactive notifications for portfolio risks, opportunities, and significant events
- **Comprehensive Intelligence**: Integration of on-chain data, social sentiment, audit reports, and market analysis
- **Automated Insights**: AI-powered portfolio analysis and recommendations

## 🏗️ Architecture

### Core Components

1. **AI Agent System** - Specialized agents for different analysis types
2. **Data Pipeline** - Real-time ingestion from multiple sources (blockchain, social media, news)
3. **Alert Coordination** - Intelligent alert system with multi-wallet monitoring
4. **Portfolio Analysis** - Deep portfolio insights combining multiple data sources
5. **Task Queue** - Celery-based async processing for long-running analyses

### Technology Stack

- **Backend**: FastAPI (Python 3.12+)
- **Async Processing**: Celery + Redis
- **Database**: MongoDB (Motor async driver)
- **Blockchain**: Web3.py for on-chain data
- **AI**: Anthropic Claude, Google Gemini
- **Social Data**: Twitter, Reddit, Farcaster APIs
- **Web Server**: Uvicorn

## 🤖 AI Agent Capabilities

### 1. **Risk Analysis Agent** (`/agent/risk`)
- Portfolio risk assessment
- Contract audit checking
- Vulnerability detection
- Risk scoring and recommendations

### 2. **Social Sentiment Agent** (`/agent/social`, `/agent/sentiment`)
- Real-time sentiment analysis across Twitter, Reddit, Farcaster
- Token-specific sentiment tracking
- Trending narratives detection
- Platform-specific breakdowns

### 3. **On-Chain Analysis Agent** (`/agent/onchain`)
- Whale transaction monitoring
- Portfolio composition analysis
- Token holdings tracking
- Network activity monitoring

### 4. **Market Data Agent** (`/agent/market_data`)
- Price tracking and analysis
- Market trends identification
- Volume and liquidity analysis
- Historical data processing

### 5. **Research Agent** (`/agent/research`)
- Protocol research and analysis
- Market research reports
- Competitive analysis
- Emerging trends identification

### 6. **Governance Agent** (`/agent/governance`)
- DAO proposal tracking
- Voting analysis
- Governance participation metrics

### 7. **Yield Optimization Agent** (`/agent/yield`)
- Yield farming opportunities
- APY comparisons
- Risk-adjusted returns analysis

### 8. **Macro Analysis Agent** (`/agent/macro`)
- Broader market trends
- Macro economic factors
- Market correlation analysis

### 9. **Execution Agent** (`/agent/execution`)
- Transaction optimization
- Gas fee analysis
- Execution strategy recommendations

### 10. **Automation Agent** (`/agent/automation`)
- Automated trading strategies
- Rebalancing automation
- Condition-based actions

## 📊 Key Features

### Portfolio Management

```
GET /api/v1/agent/portfolio/portfolio?address=0x...
POST /api/v1/agent/portfolio/insights
POST /api/v1/agent/portfolio/insights/quick
```

- Complete portfolio overview
- AI-generated insights
- Risk assessment
- Social sentiment integration
- Quick analysis mode

### Alert System

```
POST /api/alerts/track-wallet?wallet_address=0x...
GET /api/alerts/alerts?wallet_address=0x...
POST /api/alerts/coordinate
POST /api/alerts/batch
```

- Wallet tracking and monitoring
- Multi-agent coordination
- Batch processing for multiple wallets
- Customizable alert delivery
- x402 integration for decentralized delivery

### Complete Analysis

```
POST /api/v1/system/analyze-complete?wallet_address=0x...
POST /api/v1/system/analyze-batch
```

- End-to-end wallet analysis
- Risk + Audits + Social + AI insights
- Batch processing capabilities
- Comprehensive reporting

### Market Intelligence

```
GET /api/v1/daily/digest
POST /agent/analyze?timeframe=24h
GET /agent/narratives/{token_symbol}
```

- Daily crypto digest
- Sentiment analysis
- Trending narratives
- Multi-source news aggregation

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- Redis
- MongoDB
- Microsoft Visual C++ Build Tools (Windows)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/fluxo.git
cd fluxo
```

2. **Create virtual environment**
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**

Copy `.env.example` to `.env` and fill in required values:

```env
# Database
mongo_url=mongodb://localhost:27017/fluxo
database_url=mongodb://localhost:27017/fluxo

# Redis
redis_host=localhost
redis_port=6379
redis_password=

# Celery
celery_broker_url=redis://localhost:6379/0

# API Keys
anthropic_api_key=your_key_here
gemini_api_key=your_key_here
dune_api_key=your_key_here
twitter_bearer_token=your_key_here
reddit_client_id=your_key_here
reddit_client_secret=your_key_here

# Other
admin_email=fluxosageslab@gmail.com
```

5. **Run the server**
```bash
cd fluxo/backend
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`

### API Documentation

Once running, visit:
- **Interactive Docs**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`
- **OpenAPI JSON**: `http://127.0.0.1:8000/openapi.json`

## 📡 Data Sources

Fluxo integrates with multiple data sources:

- **Blockchain**: Web3 RPC nodes, Mantle Network
- **Social Media**: Twitter, Reddit, Farcaster
- **Market Data**: CoinDesk, price feeds
- **On-Chain Analytics**: Dune Analytics
- **Audit Data**: Protocol audit databases
- **News**: Crypto news aggregators like CoinDesk

## 🔄 Data Pipeline

The data pipeline continuously ingests, processes, and analyzes:

1. **Ingestion Layer**: Collects raw data from all sources
2. **Processing Layer**: Normalizes and enriches data
3. **Analysis Layer**: AI agents process and generate insights
4. **Storage Layer**: MongoDB for structured data, Redis for caching
5. **Alert Layer**: Triggers notifications based on analysis

## 🎯 Use Cases

### For Individual Users
- Monitor portfolio health in real-time
- Get AI-powered investment insights
- Receive proactive risk alerts
- Track social sentiment for holdings
- Discover yield opportunities

### For DeFi Protocols
- Monitor community sentiment
- Track governance participation
- Analyze competitor activity
- Identify market trends

### For Analysts
- Comprehensive market intelligence
- Multi-source data aggregation
- Automated research reports
- Historical trend analysis

## 🔐 Security Features

- Privacy Intelligence to avoid bots and front-running 
- Contract audit checking
- Risk assessment for holdings
- Vulnerability detection
- Smart contract analysis
- Wallet activity monitoring

## 🛣️ Roadmap

- [ ] Machine learning models for price prediction
- [ ] Advanced Privacy Intelligence integration
- [ ] Advanced portfolio optimization
- [ ] Multi-chain support expansion
- [ ] Enhanced AI reasoning capabilities
- [ ] Real-time WebSocket updates
- [ ] Mobile app integration
- [ ] Community features and social trading

## 📄 License


## 📞 Support

For questions and support:
- Documentation: `/docs`
- Issues: [GitHub Issues]
- Email: fluxosageslab@gmail.com

## 🙏 Acknowledgments

Built with:
- FastAPI
- Web3.py
- Celery
- MongoDB

---

**Version**: 1.0  
**Status**: Active Development  