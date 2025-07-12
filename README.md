# S&P 500 Dashboard

A comprehensive real-time financial dashboard built with Streamlit for S&P 500 market analysis and visualization.

## Features

### Core Functionality
- **Real-time Stock Data**: Live data for all 500+ S&P 500 companies
- **Market Overview**: Sector-based analysis with top gainers/losers
- **Company Selection**: Interactive move-based selection system
- **Historical Analysis**: Price tracking from 1 day to 5 years
- **Buy/Sell Volume Tracking**: Estimated volume changes from previous day

### Advanced Features
- **Smart Caching**: Intelligent data caching with automatic expiration
- **Performance Optimization**: Network efficiency and request deduplication
- **Offline Mode**: Complete offline functionality with cached data
- **Error Recovery**: Smart error handling with retry and reset options
- **Enhanced UX**: Loading indicators, animations, and interactive help

### Analytics
- **Market Metrics**: Comprehensive market performance calculations
- **P/E Ratio Integration**: Valuation analysis for selected companies
- **Volume Analysis**: Buy/sell volume patterns and relationships
- **Risk Metrics**: Volatility and risk-related calculations
- **Sector Performance**: Industry-based market analysis

## Technology Stack

- **Frontend**: Streamlit web framework
- **Data Processing**: pandas, numpy
- **Visualization**: Plotly (interactive charts)
- **Data Source**: Yahoo Finance API (yfinance)
- **Caching**: Custom caching system with SQLite
- **Performance**: Multi-threading, request batching

## Project Structure

```
├── app.py                    # Main Streamlit application
├── data_fetcher.py          # Data retrieval and API management
├── analytics.py             # Market calculations and metrics
├── cache_manager.py         # Smart caching system
├── performance_optimizer.py # Performance and network optimization
├── loading_manager.py       # Loading states and offline mode
├── performance_monitor.py   # Performance tracking
├── ux_enhancements.py       # User experience improvements
├── utils.py                 # Utility functions
├── pyproject.toml          # Python dependencies
└── replit.md               # Project documentation
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd s&p-500-dashboard
```

2. Install dependencies:
```bash
uv install
# or
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run app.py --server.port 5000
```

## Usage

### Getting Started
1. The dashboard loads with a market overview showing top gainers/losers by sector
2. Use the search bar to find specific companies or browse the complete list
3. Select companies using checkboxes - they move to the "Selected Companies" panel
4. Data and charts load automatically when companies are selected

### Company Selection
- **Quick Selection**: Use preset buttons (Tech Giants, Financial, etc.)
- **Search**: Filter companies by name or symbol
- **Pagination**: View 20/50/100/200 or all companies
- **Move-based System**: Selected companies move between panels

### Historical Analysis
- Choose time periods from 1 day to 5 years
- Automatic chart generation for selected companies
- Price trends and volume analysis
- Performance summary tables

### Offline Mode
- Automatic data caching for offline access
- Manual offline mode switching
- 24-hour cache expiration
- Connection status monitoring

## Configuration

### Environment Variables
```bash
# Optional: Add any API keys if needed
# Currently uses free Yahoo Finance API
```

### Streamlit Configuration
Create `.streamlit/config.toml`:
```toml
[server]
headless = true
address = "0.0.0.0"
port = 5000
```

## Performance Features

- **HTTP Session Caching**: 5-minute request caching
- **Request Batching**: Parallel data fetching with rate limiting
- **Memory Optimization**: Session state cleanup and compression
- **Chart Optimization**: Smart data sampling for large datasets
- **Virtual Scrolling**: Efficient handling of large company lists

## Development

### Adding New Features
1. Follow the modular architecture pattern
2. Add new functionality to appropriate modules
3. Update `replit.md` with architectural changes
4. Test performance impact with the built-in monitoring

### Code Style
- Use type hints where applicable
- Follow PEP 8 conventions
- Add docstrings for public functions
- Maintain separation of concerns

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For issues or questions, please create an issue in the repository.