import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
import time
from typing import List, Optional, Dict
from cache_manager import get_cache_manager
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests_cache

class DataFetcher:
    def __init__(self):
        self.cache_manager = get_cache_manager()
        self.max_workers = 15  # Increased for better parallel performance
        self.request_delay = 0.05  # Reduced delay for faster requests
        self.timeout = 8  # Faster timeout for failed requests
        
        # Initialize HTTP session with caching
        self.session = requests_cache.CachedSession(
            'yfinance_cache',
            expire_after=300,  # 5 minutes HTTP cache
            allowable_methods=['GET', 'POST'],
            allowable_codes=[200, 400, 404]
        )
        
        # Lazy load symbols to improve startup time
        self._symbols_cache = None
        
    def get_sp500_companies_list(self) -> pd.DataFrame:
        """Get S&P 500 companies list with names and symbols - with caching"""
        # Check cache first
        cached_data = self.cache_manager.get_cached_data('companies_list')
        if cached_data is not None:
            print(f"Using cached S&P 500 companies list ({len(cached_data)} companies)")
            return cached_data
        
        try:
            # Get S&P 500 list from Wikipedia
            url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
            tables = pd.read_html(url)
            sp500_table = tables[0]
            
            # Create a clean dataframe with Symbol and Security (company name)
            companies_df = pd.DataFrame({
                'Symbol': sp500_table['Symbol'].str.replace('.', '-'),
                'Company': sp500_table['Security']
            })
            
            # Sort alphabetically by company name
            companies_df = companies_df.sort_values('Company').reset_index(drop=True)
            
            # Cache the result
            self.cache_manager.cache_data(companies_df, 'companies_list')
            
            print(f"Successfully fetched {len(companies_df)} S&P 500 companies from Wikipedia")
            return companies_df
            
        except Exception as e:
            print(f"Error fetching S&P 500 companies: {e}")
            print("Using fallback company list...")
            
            # Fallback list with company names
            fallback_data = {
                'Symbol': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'UNH', 'JNJ', 'JPM'],
                'Company': ['Apple Inc.', 'Microsoft Corporation', 'Alphabet Inc.', 'Amazon.com Inc.', 
                          'NVIDIA Corporation', 'Meta Platforms Inc.', 'Tesla Inc.', 'UnitedHealth Group Inc.',
                          'Johnson & Johnson', 'JPMorgan Chase & Co.']
            }
            fallback_df = pd.DataFrame(fallback_data)
            # Cache fallback data with shorter expiry
            self.cache_manager.cache_data(fallback_df, 'companies_list')
            return fallback_df

    def _get_sp500_symbols(self) -> List[str]:
        """Fetch S&P 500 symbols from Wikipedia"""
        try:
            # Get S&P 500 list from Wikipedia
            url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
            tables = pd.read_html(url)
            sp500_table = tables[0]
            
            # Extract symbols and company names
            symbols = sp500_table['Symbol'].tolist()
            
            # Clean symbols (remove dots and special characters that might cause issues)
            cleaned_symbols = []
            for symbol in symbols:
                # Replace dots with dashes for Yahoo Finance compatibility
                cleaned_symbol = str(symbol).replace('.', '-')
                # Skip problematic symbols that are known to cause issues
                if cleaned_symbol not in ['BRK-B', 'BERKB']:  # BRK.B causes issues
                    cleaned_symbols.append(cleaned_symbol)
            
            print(f"Successfully fetched {len(cleaned_symbols)} S&P 500 symbols from Wikipedia")
            return cleaned_symbols
            
        except Exception as e:
            # Fallback to a comprehensive list of S&P 500 symbols
            print(f"Error fetching S&P 500 symbols: {e}")
            print("Using fallback symbol list...")
            return [
                'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'UNH', 'JNJ', 'JPM',
                'V', 'PG', 'XOM', 'HD', 'CVX', 'MA', 'PFE', 'ABBV', 'LLY', 'BAC',
                'KO', 'AVGO', 'PEP', 'TMO', 'COST', 'MRK', 'WMT', 'ACN', 'ABT', 'CSCO',
                'DHR', 'VZ', 'ADBE', 'NKE', 'TXN', 'NEE', 'LIN', 'CRM', 'RTX', 'NFLX',
                'AMD', 'ORCL', 'CMCSA', 'PM', 'T', 'HON', 'QCOM', 'UPS', 'LOW', 'IBM',
                'SPGI', 'CAT', 'INTU', 'AMGN', 'GS', 'BKNG', 'ISRG', 'TJX', 'AXP', 'SYK',
                'DE', 'NOW', 'UBER', 'PGR', 'BLK', 'VRTX', 'GILD', 'MDLZ', 'ADP', 'ADI',
                'REGN', 'CB', 'CI', 'SO', 'SCHW', 'MMC', 'LRCX', 'ZTS', 'BSX', 'ETN',
                'MU', 'DUK', 'SHW', 'EOG', 'EQIX', 'PYPL', 'ITW', 'AON', 'CSX', 'CMG',
                'MAR', 'FCX', 'NSC', 'ORLY', 'MCK', 'SNPS', 'CDNS', 'APH', 'ADSK', 'KLAC',
                'WM', 'GD', 'TGT', 'USB', 'HCA', 'CL', 'FI', 'PSA', 'ECL', 'NOC',
                'NXPI', 'SLB', 'EMR', 'WMB', 'PXD', 'FTNT', 'MCHP', 'GM', 'F', 'AMT',
                'CCI', 'SBUX', 'MNST', 'TFC', 'O', 'PNC', 'SPG', 'KMI', 'PAYX', 'ROST',
                'DXCM', 'ICE', 'MCO', 'MSI', 'TRV', 'AJG', 'CME', 'AFL', 'BDX', 'CTAS',
                'TEL', 'COF', 'MET', 'CARR', 'SYY', 'WELL', 'GWW', 'HLT', 'AEP', 'ALL',
                'VRSK', 'EXC', 'YUM', 'FAST', 'PRU', 'CTSH', 'A', 'HSY', 'AZO', 'EL',
                'PCAR', 'CPRT', 'OTIS', 'IDXX', 'EW', 'CMI', 'GIS', 'DD', 'KDP', 'VICI',
                'EA', 'IQV', 'CSGP', 'BIIB', 'ROK', 'GLW', 'HIG', 'DLTR', 'KMB', 'FANG',
                'ABC', 'RMD', 'HPQ', 'ANSS', 'EBAY', 'EXR', 'XEL', 'ED', 'WBA', 'MPWR',
                'WAB', 'FITB', 'ROP', 'AWK', 'KEYS', 'ENPH', 'DOW', 'AVB', 'GEHC', 'CDW',
                'MTB', 'PPG', 'VMC', 'TSCO', 'CBRE', 'WEC', 'FTV', 'STZ', 'K', 'ZBH',
                'MLM', 'BR', 'ETR', 'CHD', 'STLD', 'HBAN', 'RF', 'HPE', 'TYL', 'ES',
                'NUE', 'LH', 'MAA', 'TROW', 'NTAP', 'PKI', 'GRMN', 'STE', 'TMUS', 'FE',
                'AEE', 'EXPD', 'TDG', 'DTE', 'LDOS', 'AVY', 'NVR', 'ULTA', 'TTWO', 'POOL',
                'LVS', 'EXPE', 'SWK', 'HOLX', 'LYB', 'NTRS', 'CAH', 'IP', 'AKAM', 'CNP',
                'CF', 'LUV', 'DFS', 'MOS', 'URI', 'UAL', 'CTVA', 'CE', 'CMS', 'NI',
                'COO', 'JBHT', 'J', 'CLX', 'LKQ', 'CHRW', 'LEN', 'ALB', 'BALL', 'SWKS',
                'SJM', 'JKHY', 'NDSN', 'WRB', 'BF-B', 'DGX', 'FBHS', 'FRT', 'OMC', 'TXT',
                'CINF', 'ZBRA', 'ALGN', 'CAG', 'MKC', 'AMCR', 'ATO', 'NRG', 'PFG', 'KIM',
                'HSIC', 'PNR', 'EVRG', 'TECH', 'INCY', 'IEX', 'VTRS', 'ALLE', 'MGM', 'FMC',
                'TPG', 'REG', 'UDR', 'CPT', 'BXP', 'ARE', 'ESS', 'INVH', 'EQR', 'WDC',
                'PEAK', 'ILMN', 'MRNA', 'SEDG', 'EPAM', 'GEN', 'CTLT', 'WST', 'CZR', 'SMCI',
                'DVN', 'SOLV', 'TPR', 'LUMN', 'QRVO', 'BEN', 'MOH', 'TAP', 'ZION', 'NCLH',
                'HAS', 'AIZ', 'PARA', 'DISH', 'NEWS', 'WYNN', 'BWA', 'HRL', 'BBWI', 'IPG',
                'FOXA', 'FOX', 'VFC', 'WBA', 'HII', 'DXC', 'PAYC', 'LW', 'JNPR', 'MHK',
                'FFIV', 'AAL', 'PENN', 'RHI', 'NWS', 'DVA', 'CRL', 'AOS', 'KMX', 'NVST',
                'HSIC', 'FSLR', 'CMA', 'AMTM', 'ANET', 'BLDR', 'GNRC', 'APTV', 'WHR', 'CBOE',
                'BMRN', 'UHS', 'FDS', 'CPB', 'NWSA', 'CCL', 'RCL', 'DAL', 'AAP', 'GPS',
                'VNO', 'CTXS', 'HWM', 'NLOK', 'PVH', 'RL', 'SEE', 'MTCH', 'ETSY', 'SBNY'
            ]
    
    def get_sp500_data(self) -> pd.DataFrame:
        """Fetch current data for all S&P 500 companies"""
        try:
            # Split symbols into smaller chunks to avoid rate limits
            chunk_size = 25  # Balanced chunk size for efficiency vs rate limits
            symbol_chunks = [self.sp500_symbols[i:i + chunk_size] 
                           for i in range(0, len(self.sp500_symbols), chunk_size)]
            
            all_data = []
            
            for chunk in symbol_chunks:
                chunk_data = self._fetch_chunk_data(chunk)
                if not chunk_data.empty:
                    all_data.append(chunk_data)
                
                # Add delay between chunks to avoid rate limits
                if len(symbol_chunks) > 1:  # Only add delay if there are multiple chunks
                    time.sleep(1.5)  # Reasonable delay
                print(f"Processed chunk {len(all_data)}/{len(symbol_chunks)} - {len(chunk_data) if not chunk_data.empty else 0} companies added")
            
            if all_data:
                final_df = pd.concat(all_data, ignore_index=True)
                print(f"Successfully fetched data for {len(final_df)} companies out of {len(self.sp500_symbols)} requested")
                
                # Check for critical missing stocks and retry them
                critical_stocks = ['NVDA', 'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA']
                missing_critical = [stock for stock in critical_stocks if stock not in final_df['Symbol'].values]
                
                if missing_critical:
                    print(f"Retrying critical missing stocks: {missing_critical}")
                    retry_data = self._fetch_chunk_data(missing_critical)
                    if not retry_data.empty:
                        final_df = pd.concat([final_df, retry_data], ignore_index=True)
                        print(f"Successfully added {len(retry_data)} critical stocks")
                
                return final_df
            else:
                raise Exception("No data could be fetched for any symbols")
                
        except Exception as e:
            raise Exception(f"Error fetching S&P 500 data: {str(e)}")
    
    def _fetch_chunk_data(self, symbols: List[str]) -> pd.DataFrame:
        """Fetch data for a chunk of symbols"""
        chunk_data = []
        
        for symbol in symbols:
            try:
                # Get stock info
                stock = yf.Ticker(symbol)
                
                # Add minimal delay between individual stock requests
                time.sleep(0.05)
                
                # Get current data (last 2 days to calculate changes)
                hist = stock.history(period="5d")
                
                if len(hist) >= 2:
                    # Current and previous day data
                    current = hist.iloc[-1]
                    previous = hist.iloc[-2]
                    
                    # Get additional info
                    info = stock.info
                    
                    # Calculate metrics
                    daily_change = current['Close'] - previous['Close']
                    daily_change_pct = (daily_change / previous['Close']) * 100
                    volume_change_pct = ((current['Volume'] - previous['Volume']) / previous['Volume']) * 100 if previous['Volume'] > 0 else 0
                    
                    # Estimate buy/sell volume based on price movement and volume
                    # This is an approximation as actual buy/sell data requires level 2 data
                    if daily_change > 0:
                        # Price went up - estimate more buying pressure
                        buy_volume_ratio = 0.6 + (min(abs(daily_change_pct), 10) / 100) * 0.3  # 60-90% buy volume for gainers
                    elif daily_change < 0:
                        # Price went down - estimate more selling pressure
                        buy_volume_ratio = 0.4 - (min(abs(daily_change_pct), 10) / 100) * 0.3  # 10-40% buy volume for losers
                    else:
                        # No price change - assume balanced
                        buy_volume_ratio = 0.5
                    
                    estimated_buy_volume = current['Volume'] * buy_volume_ratio
                    estimated_sell_volume = current['Volume'] * (1 - buy_volume_ratio)
                    
                    # Calculate previous day estimates for comparison
                    if previous['Close'] > hist.iloc[-3]['Close'] if len(hist) > 2 else True:
                        prev_buy_ratio = 0.6
                    else:
                        prev_buy_ratio = 0.4
                    
                    prev_estimated_buy_volume = previous['Volume'] * prev_buy_ratio
                    prev_estimated_sell_volume = previous['Volume'] * (1 - prev_buy_ratio)
                    
                    # Calculate buy/sell volume changes
                    buy_volume_change_pct = ((estimated_buy_volume - prev_estimated_buy_volume) / prev_estimated_buy_volume) * 100 if prev_estimated_buy_volume > 0 else 0
                    sell_volume_change_pct = ((estimated_sell_volume - prev_estimated_sell_volume) / prev_estimated_sell_volume) * 100 if prev_estimated_sell_volume > 0 else 0
                    
                    # Create data row
                    data_row = {
                        'Symbol': symbol,
                        'Company': info.get('longName', symbol),
                        'Price': current['Close'],
                        'Daily_Change': daily_change,
                        'Daily_Change_Pct': daily_change_pct,
                        'Volume': current['Volume'],
                        'Previous_Volume': previous['Volume'],
                        'Volume_Change_Pct': volume_change_pct,
                        'Estimated_Buy_Volume': estimated_buy_volume,
                        'Estimated_Sell_Volume': estimated_sell_volume,
                        'Buy_Volume_Change_Pct': buy_volume_change_pct,
                        'Sell_Volume_Change_Pct': sell_volume_change_pct,
                        'Buy_Sell_Ratio': buy_volume_ratio,
                        'Market_Cap': info.get('marketCap', 0),
                        'Sector': info.get('sector', 'Unknown'),
                        'Industry': info.get('industry', 'Unknown'),
                        'Open': current['Open'],
                        'High': current['High'],
                        'Low': current['Low'],
                        'Previous_Close': previous['Close']
                    }
                    
                    chunk_data.append(data_row)
                    
            except Exception as e:
                print(f"Error fetching data for {symbol}: {e}")
                # Add longer delay if rate limited
                if "Rate limited" in str(e) or "Too Many Requests" in str(e):
                    print("Rate limit detected, waiting 10 seconds...")
                    time.sleep(10)
                elif "404" in str(e) or "delisted" in str(e):
                    # Symbol might be delisted, just skip it
                    pass
                continue
        
        return pd.DataFrame(chunk_data)
    
    def get_market_overview_data(self) -> pd.DataFrame:
        """Get sector-based data for market overview - with caching"""
        # Define sector-based company groups
        sector_companies = {
            'Technology': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NFLX', 'ADBE', 'CRM', 'ORCL', 'CSCO', 'INTC', 'IBM', 'HPQ', 'QCOM'],
            'Semiconductor/AI': ['NVDA', 'AMD', 'TSM', 'AVGO', 'TXN', 'ADI', 'MRVL', 'KLAC', 'LRCX', 'AMAT', 'MU', 'MCHP', 'ON', 'SWKS'],
            'Finance': ['JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'V', 'MA', 'AXP', 'BLK', 'SPGI', 'COF', 'USB', 'PNC'],
            'Healthcare': ['UNH', 'JNJ', 'PFE', 'LLY', 'ABT', 'TMO', 'DHR', 'BMY', 'AMGN', 'GILD', 'CVS', 'MRK', 'MDT', 'ISRG'],
            'Consumer': ['TSLA', 'HD', 'WMT', 'PG', 'KO', 'PEP', 'COST', 'NKE', 'MCD', 'SBUX', 'TGT', 'LOW', 'DIS', 'AMZN']
        }
        
        # Flatten all companies into one list
        all_companies = []
        for companies in sector_companies.values():
            all_companies.extend(companies)
        
        # Remove duplicates while preserving order
        unique_companies = list(dict.fromkeys(all_companies))
        
        # Check cache first
        cached_data = self.cache_manager.get_cached_data('market_overview', unique_companies)
        if cached_data is not None:
            print(f"Using cached market overview data ({len(cached_data)} companies)")
            return cached_data
        
        try:
            # Fetch fresh data
            data = self.get_selected_companies_data(unique_companies)
            
            # Cache the result
            if not data.empty:
                self.cache_manager.cache_data(data, 'market_overview', unique_companies)
                print(f"Successfully fetched and cached market overview data for {len(data)} companies")
            
            return data
        except Exception as e:
            print(f"Error fetching market overview data: {e}")
            return pd.DataFrame()
    
    def get_sector_performance(self, market_data: pd.DataFrame) -> dict:
        """Analyze performance by sectors"""
        try:
            # Define sector mappings
            sector_companies = {
                'Technology': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NFLX', 'ADBE', 'CRM', 'ORCL', 'CSCO', 'INTC', 'IBM', 'HPQ', 'QCOM'],
                'Semiconductor/AI': ['NVDA', 'AMD', 'TSM', 'AVGO', 'TXN', 'ADI', 'MRVL', 'KLAC', 'LRCX', 'AMAT', 'MU', 'MCHP', 'ON', 'SWKS'],
                'Finance': ['JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'V', 'MA', 'AXP', 'BLK', 'SPGI', 'COF', 'USB', 'PNC'],
                'Healthcare': ['UNH', 'JNJ', 'PFE', 'LLY', 'ABT', 'TMO', 'DHR', 'BMY', 'AMGN', 'GILD', 'CVS', 'MRK', 'MDT', 'ISRG'],
                'Consumer': ['TSLA', 'HD', 'WMT', 'PG', 'KO', 'PEP', 'COST', 'NKE', 'MCD', 'SBUX', 'TGT', 'LOW', 'DIS', 'AMZN']
            }
            
            sector_analysis = {}
            
            for sector_name, symbols in sector_companies.items():
                # Filter data for this sector
                sector_data = market_data[market_data['Symbol'].isin(symbols)].copy()
                
                if not sector_data.empty:
                    # Get top 5 gainers and losers for each sector
                    top_gainers = sector_data.nlargest(5, 'Daily Change %')[['Symbol', 'Company', 'Daily Change %', 'Current Price']]
                    top_losers = sector_data.nsmallest(5, 'Daily Change %')[['Symbol', 'Company', 'Daily Change %', 'Current Price']]
                    
                    # Calculate sector averages
                    avg_change = sector_data['Daily Change %'].mean()
                    sector_volume = sector_data['Volume'].sum()
                    
                    sector_analysis[sector_name] = {
                        'top_gainers': top_gainers,
                        'top_losers': top_losers,
                        'avg_change': avg_change,
                        'total_volume': sector_volume,
                        'companies_count': len(sector_data)
                    }
            
            return sector_analysis
        except Exception as e:
            print(f"Error analyzing sector performance: {e}")
            return {}

    def get_selected_companies_data(self, symbols: List[str]) -> pd.DataFrame:
        """Get detailed data for selected companies only - with caching and optimization"""
        if not symbols:
            return pd.DataFrame()
        
        # Check cache first
        cached_data = self.cache_manager.get_cached_data('company_data', symbols)
        if cached_data is not None:
            print(f"Using cached data for {len(cached_data)} companies")
            return cached_data
        
        try:
            # Use optimized parallel fetching
            data = self._fetch_parallel_data(symbols)
            
            # Cache the result if successful
            if not data.empty:
                self.cache_manager.cache_data(data, 'company_data', symbols)
                print(f"Successfully fetched and cached data for {len(data)} companies")
            
            return data
                
        except Exception as e:
            print(f"Error fetching selected companies data: {e}")
            return pd.DataFrame()
    
    def _fetch_parallel_data(self, symbols: List[str]) -> pd.DataFrame:
        """Fetch data using parallel processing with rate limit handling"""
        all_data = []
        
        # Create smaller batches for parallel processing
        batch_size = 3  # Small batches to avoid overwhelming the API
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all batches
            future_to_batch = {}
            
            for i in range(0, len(symbols), batch_size):
                batch = symbols[i:i + batch_size]
                future = executor.submit(self._fetch_batch_with_retry, batch)
                future_to_batch[future] = batch
            
            # Collect results as they complete
            for future in as_completed(future_to_batch):
                batch = future_to_batch[future]
                try:
                    batch_data = future.result()
                    if batch_data:
                        all_data.extend(batch_data)
                except Exception as e:
                    print(f"Error fetching batch {batch}: {e}")
                
                # Add delay between completed batches
                time.sleep(self.request_delay)
        
        if all_data:
            return pd.DataFrame(all_data)
        else:
            return pd.DataFrame()
    
    def _fetch_batch_with_retry(self, symbols: List[str], max_retries: int = 3) -> List[Dict]:
        """Fetch a batch of symbols with exponential backoff retry"""
        for attempt in range(max_retries):
            try:
                # Add delay before each attempt
                if attempt > 0:
                    delay = (2 ** attempt) + (attempt * 0.1)  # Exponential backoff
                    time.sleep(delay)
                    print(f"Retrying batch {symbols} (attempt {attempt + 1})")
                
                return self._fetch_individual_stocks(symbols)
                
            except Exception as e:
                if "Rate limit" in str(e) or "Too Many Requests" in str(e):
                    if attempt < max_retries - 1:
                        continue  # Retry with backoff
                else:
                    print(f"Non-rate-limit error for batch {symbols}: {e}")
                    break
        
        # Return empty list if all retries failed
        print(f"Failed to fetch data for batch {symbols} after {max_retries} attempts")
        return []
    
    def _fetch_individual_stocks(self, symbols: List[str]) -> List[Dict]:
        """Fetch individual stock data efficiently"""
        all_data = []
        
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                
                # Get recent data for price calculations
                hist = ticker.history(period="5d")
                if hist.empty:
                    continue
                
                current_price = hist['Close'].iloc[-1]
                prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
                
                # Calculate daily change
                daily_change = current_price - prev_close
                daily_change_pct = (daily_change / prev_close * 100) if prev_close != 0 else 0
                
                # Get volume data
                current_volume = hist['Volume'].iloc[-1] if len(hist) > 0 else 0
                prev_volume = hist['Volume'].iloc[-2] if len(hist) > 1 else current_volume
                
                # Estimate buy/sell volume (simplified approach)
                volume_change = current_volume - prev_volume
                buy_volume = current_volume * 0.6 if daily_change >= 0 else current_volume * 0.4
                sell_volume = current_volume - buy_volume
                
                # Get company info
                info = ticker.info
                
                # Get P/E ratio
                pe_ratio = info.get('trailingPE', None)
                if pe_ratio is None:
                    pe_ratio = info.get('forwardPE', None)
                
                company_data = {
                    'Symbol': symbol,
                    'Company': info.get('longName', symbol),
                    'Current Price': current_price,
                    'Daily Change': daily_change,
                    'Daily Change %': daily_change_pct,
                    'Volume': current_volume,
                    'Volume Change': volume_change,
                    'Est. Buy Volume': buy_volume,
                    'Est. Sell Volume': sell_volume,
                    'Market Cap': info.get('marketCap', 0),
                    'P/E Ratio': pe_ratio,
                    'Sector': info.get('sector', 'Unknown')
                }
                
                all_data.append(company_data)
                
                # Small delay between individual stocks
                time.sleep(0.05)
                
            except Exception as e:
                print(f"Error fetching data for {symbol}: {e}")
                # Add longer delay if rate limited
                if "Rate limited" in str(e) or "Too Many Requests" in str(e):
                    raise e  # Re-raise to trigger retry logic
                continue
        
        return all_data

    def get_historical_data(self, symbols: List[str], period: str) -> pd.DataFrame:
        """Fetch historical data for selected symbols with specified period - with caching"""
        if not symbols:
            return pd.DataFrame()
        
        # Check cache first
        cached_data = self.cache_manager.get_cached_data('historical_data', symbols, period=period)
        if cached_data is not None:
            print(f"Using cached historical data for {len(symbols)} companies ({period})")
            return cached_data
        
        try:
            all_historical = []
            
            for symbol in symbols:
                try:
                    stock = yf.Ticker(symbol)
                    # For very short periods, also try intraday data
                    if period in ['1d', '2d']:
                        hist = stock.history(period="5d", interval="1h")  # Get hourly data for better resolution
                        if not hist.empty:
                            # Keep only recent data points
                            hist = hist.tail(48)  # Last 48 hours of hourly data
                    else:
                        hist = stock.history(period=period)
                    
                    if not hist.empty:
                        hist['Symbol'] = symbol
                        hist['Date'] = hist.index
                        hist = hist.reset_index(drop=True)
                        all_historical.append(hist)
                        
                except Exception as e:
                    print(f"Error fetching historical data for {symbol}: {e}")
                    continue
            
            if all_historical:
                historical_df = pd.concat(all_historical, ignore_index=True)
                
                # Cache the result
                self.cache_manager.cache_data(historical_df, 'historical_data', symbols, period=period)
                print(f"Successfully fetched and cached historical data for {len(symbols)} companies ({period})")
                
                return historical_df
            else:
                return pd.DataFrame()
                
        except Exception as e:
            print(f"Error fetching historical data: {e}")
            return pd.DataFrame()
    
    def get_company_info(self, symbol: str) -> dict:
        """Get detailed information for a specific company"""
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            
            # Get recent price data
            hist = stock.history(period="1d")
            current_price = hist['Close'].iloc[-1] if not hist.empty else 0
            
            return {
                'symbol': symbol,
                'name': info.get('longName', symbol),
                'current_price': current_price,
                'market_cap': info.get('marketCap', 0),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),
                'employees': info.get('fullTimeEmployees', 0),
                'website': info.get('website', ''),
                'description': info.get('longBusinessSummary', ''),
                'pe_ratio': info.get('forwardPE', 0),
                'dividend_yield': info.get('dividendYield', 0),
                'beta': info.get('beta', 0),
                '52_week_high': info.get('fiftyTwoWeekHigh', 0),
                '52_week_low': info.get('fiftyTwoWeekLow', 0)
            }
            
        except Exception as e:
            raise Exception(f"Error fetching company info for {symbol}: {str(e)}")
