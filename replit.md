# S&P 500 Dashboard

## Overview

This is a real-time financial dashboard application built with Streamlit that provides comprehensive S&P 500 market analysis and visualization. The application fetches live stock data for all 500+ companies, calculates market metrics including buy/sell volume tracking, and presents interactive charts and analytics with daily gains/losses monitoring.

## Recent Changes (January 2025)

✓ **Enhanced Data Coverage**: Fixed Wikipedia scraping to display all 500+ S&P 500 companies instead of just 52, with optimized rate limit handling (487+ companies successfully loaded)
✓ **Buy/Sell Volume Tracking**: Added estimated buy and sell volume changes from previous day for each stock
✓ **New Analytics Section**: Created Buy/Sell Volume Analysis with top movers and ratio distributions
✓ **Enhanced Data Table**: Added buy/sell volume columns to interactive company data view with flexible sorting options (Top/Bottom Performers, Alphabetical, Volume, Market Cap)
✓ **Improved Dependencies**: Added lxml, beautifulsoup4, html5lib for robust data fetching
✓ **Comprehensive Fallback**: 400+ symbol fallback list ensures data availability even if Wikipedia fails
✓ **Selective Company Loading**: Changed to display all 500 companies alphabetically without auto-fetching price data
✓ **User-Controlled Data Fetching**: Users now select specific companies to track and manually trigger data loading
✓ **Integrated Company Selection**: Removed sidebar, integrated company selection directly in main dashboard with quick preset buttons
✓ **Prevented Auto-Refresh**: Eliminated automatic data fetching that caused unwanted page reloads
✓ **Market Overview Section**: Added top 10 gainers and losers display using 40 major S&P 500 companies for real-time market sentiment (auto-loads by default)
✓ **Dual Dashboard Mode**: Complete company list for selection + market overview for top performers analysis
✓ **Historical Price Tracking**: Added comprehensive time period options (1 day, 1 week, 1 month, 3 months, 6 months, YTD, 1 year, 5 years)
✓ **Advanced Analytics**: Price trends, volume trends, and performance summary tables for selected time periods
✓ **Auto-Loading Historical Data**: Historical charts and analysis automatically display when companies are selected, no additional button clicks needed
✓ **Seamless Auto-Loading**: Company data, charts, and historical analysis load automatically upon selection - no manual buttons required
✓ **Unified Search Interface**: Single search bar filters company list and enables direct selection from filtered results without separate interfaces
✓ **Checkbox Selection**: Direct checkbox selection in company table rows - no dropdown menus, just check the companies you want to analyze
✓ **Two-Column Layout**: All companies on left with checkboxes, selected companies tracking table on right sorted alphabetically
✓ **Merged Selection Logic**: Quick selection buttons (Tech Giants, Financial, etc.) now add to existing manually selected companies instead of replacing them
✓ **Complete Historical Analysis**: Historical price tracking now defaults to ALL selected companies instead of just the first 3, with option to customize
✓ **Search Error Handling**: Clear error messages when searched company is not part of S&P 500 index, with helpful suggestions
✓ **Sector-Based Market Analysis**: Organized top gainers/losers by sectors (Technology, Semiconductor/AI, Finance, Healthcare, Consumer) for better market sentiment
✓ **P/E Ratio Integration**: Added P/E ratio column to selected companies performance summary for valuation analysis
✓ **Paginated Company Display**: Shows 20 companies by default with dropdown to select 20/50/100/200/All companies for better performance
✓ **Bi-directional Company Removal**: Companies removed from selected list automatically uncheck in the main company list and update all related data
✓ **Move-Based Selection System**: Selected companies move from left to right panel, deselected companies move back to left panel alphabetically
✓ **Smart Caching System**: Intelligent data caching with timestamps, expiration, and automatic invalidation for improved performance
✓ **Parallel Data Fetching**: Multi-threaded data retrieval with rate limit handling and exponential backoff retry logic
✓ **Cache-Optimized Loading**: Historical data, company lists, and market overview data cached to reduce API calls and improve speed
✓ **Enhanced User Experience**: Interactive loading skeletons, animated metric cards, progress bars, and enhanced alerts for better visual feedback
✓ **Interactive Help System**: Built-in help sections, tooltips, keyboard shortcuts, and guided user experience for easier navigation
✓ **Visual Enhancement**: Gradient headers, section dividers, enhanced styling, and improved chart appearance for professional look
✓ **Smart Error Handling**: Enhanced error messages with clear instructions and recovery suggestions for better user guidance
✓ **Performance Optimization**: Implemented comprehensive UI and network optimizations for faster response times
✓ **Network Efficiency**: Added HTTP session caching, request batching, and optimized API call patterns
✓ **Memory Management**: Smart session state cleanup, dataframe compression, and virtual scrolling for large datasets
✓ **Chart Optimization**: Intelligent data sampling for smoother chart rendering with large datasets
✓ **Request Deduplication**: Prevents redundant API calls within TTL windows to reduce network overhead
✓ **Advanced Loading Indicators**: Progressive loading with skeleton screens, progress bars, and real-time status updates
✓ **Offline Mode Support**: Complete offline functionality with cached data access when network is unavailable
✓ **Comprehensive Error Recovery**: Smart error handling with retry options, offline fallback, and application reset capabilities
✓ **Connection Status Management**: Real-time online/offline status display with manual mode switching
✓ **Persistent Offline Storage**: Automatic data caching for offline access with 24-hour expiration and file management

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

The application follows a modular Python architecture with clear separation of concerns:

### Frontend Architecture
- **Framework**: Streamlit web framework for rapid dashboard development
- **Visualization**: Plotly for interactive charts and graphs
- **Layout**: Wide layout with sidebar controls for user interaction
- **State Management**: Streamlit session state for data persistence across interactions

### Backend Architecture
- **Data Layer**: Modular data fetching using yfinance API
- **Analytics Engine**: Custom analytics module for market calculations
- **Utility Functions**: Helper functions for data formatting and presentation

## Key Components

### 1. Data Fetcher (`data_fetcher.py`)
- **Purpose**: Retrieves real-time S&P 500 stock data
- **Data Source**: Yahoo Finance API via yfinance library
- **Symbol Management**: Automatically fetches current S&P 500 company list from Wikipedia
- **Error Handling**: Fallback to hardcoded symbol list if Wikipedia fetch fails
- **API Optimization**: Implements chunking strategy to handle large symbol sets efficiently

### 2. Analytics Engine (`analytics.py`)
- **Purpose**: Calculates comprehensive market performance metrics
- **Metrics Calculated**:
  - Market breadth (gainers/losers/unchanged)
  - Average and median price changes
  - Market cap weighted averages
  - Volume statistics
  - Market volatility
- **Data Processing**: Uses pandas for efficient numerical computations

### 3. Main Application (`app.py`)
- **Purpose**: Streamlit dashboard interface
- **Features**:
  - Real-time data refresh capability
  - Interactive visualizations
  - Market overview metrics
  - Company-specific analysis
- **Session Management**: Maintains data state between user interactions

### 4. Utility Functions (`utils.py`)
- **Purpose**: Data formatting and presentation helpers
- **Functions**:
  - Number formatting with K/M/B/T suffixes
  - Percentage formatting with proper signs
  - Currency formatting
  - Color coding for performance indicators

## Data Flow

1. **Data Acquisition**: Application fetches S&P 500 company symbols from Wikipedia
2. **Market Data Retrieval**: yfinance API calls retrieve real-time stock data in chunks
3. **Data Processing**: Raw market data is processed and metrics are calculated
4. **Analytics Computation**: Market performance indicators are generated
5. **Visualization**: Processed data is rendered through Plotly charts in Streamlit interface
6. **User Interaction**: Dashboard updates based on user controls and refresh requests

## External Dependencies

### Core Libraries
- **streamlit**: Web application framework
- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computing
- **plotly**: Interactive visualization library
- **yfinance**: Yahoo Finance API wrapper

### Data Sources
- **Wikipedia**: S&P 500 company list retrieval
- **Yahoo Finance**: Real-time stock market data

### API Considerations
- Rate limiting handled through chunked requests
- Fallback mechanisms for data source failures
- Error handling for network issues

## Deployment Strategy

### Development Environment
- Python-based application suitable for local development
- Streamlit's built-in development server for testing
- Modular structure allows for easy testing of individual components

### Production Considerations
- **Hosting**: Compatible with Streamlit Cloud, Heroku, or any Python hosting platform
- **Performance**: Implements data caching strategies through session state
- **Scalability**: Chunked API requests prevent rate limiting issues
- **Monitoring**: Built-in error handling and user feedback mechanisms

### Configuration Requirements
- No database setup required (uses external APIs)
- Minimal configuration - primarily external API dependencies
- Environment variables may be needed for API keys in production

The application is designed to be lightweight and self-contained, with minimal setup requirements while providing comprehensive financial market analysis capabilities.