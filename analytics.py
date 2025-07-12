import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime, timedelta

class Analytics:
    def __init__(self):
        pass
    
    def calculate_market_metrics(self, df: pd.DataFrame) -> Dict:
        """Calculate overall market performance metrics"""
        try:
            if df.empty:
                return {}
            
            total_companies = len(df)
            gainers = len(df[df['Daily_Change_Pct'] > 0])
            losers = len(df[df['Daily_Change_Pct'] < 0])
            unchanged = total_companies - gainers - losers
            
            avg_change = df['Daily_Change_Pct'].mean()
            median_change = df['Daily_Change_Pct'].median()
            
            total_volume = df['Volume'].sum()
            avg_volume = df['Volume'].mean()
            
            volatility = df['Daily_Change_Pct'].std()
            
            # Market cap weighted average
            total_market_cap = df['Market_Cap'].sum()
            weighted_avg_change = (df['Daily_Change_Pct'] * df['Market_Cap']).sum() / total_market_cap if total_market_cap > 0 else 0
            
            return {
                'total_companies': total_companies,
                'gainers': gainers,
                'losers': losers,
                'unchanged': unchanged,
                'gainers_pct': (gainers / total_companies) * 100,
                'losers_pct': (losers / total_companies) * 100,
                'avg_change': avg_change,
                'median_change': median_change,
                'weighted_avg_change': weighted_avg_change,
                'total_volume': total_volume,
                'avg_volume': avg_volume,
                'volatility': volatility,
                'total_market_cap': total_market_cap
            }
            
        except Exception as e:
            print(f"Error calculating market metrics: {e}")
            return {}
    
    def get_top_performers(self, df: pd.DataFrame, n: int = 10) -> Dict[str, pd.DataFrame]:
        """Get top and bottom performers by different metrics"""
        try:
            if df.empty:
                return {}
            
            return {
                'top_gainers': df.nlargest(n, 'Daily_Change_Pct'),
                'top_losers': df.nsmallest(n, 'Daily_Change_Pct'),
                'highest_volume': df.nlargest(n, 'Volume'),
                'highest_volume_change': df.nlargest(n, 'Volume_Change_Pct'),
                'most_volatile': df.reindex(df['Daily_Change_Pct'].abs().sort_values(ascending=False).index).head(n)
            }
            
        except Exception as e:
            print(f"Error getting top performers: {e}")
            return {}
    
    def sector_analysis(self, df: pd.DataFrame) -> pd.DataFrame:
        """Analyze performance by sector"""
        try:
            if df.empty or 'Sector' not in df.columns:
                return pd.DataFrame()
            
            sector_stats = df.groupby('Sector').agg({
                'Daily_Change_Pct': ['mean', 'median', 'std', 'count'],
                'Volume': ['sum', 'mean'],
                'Market_Cap': ['sum', 'mean'],
                'Volume_Change_Pct': 'mean'
            }).round(2)
            
            # Flatten column names
            sector_stats.columns = ['_'.join(col).strip() for col in sector_stats.columns]
            
            # Calculate additional metrics
            sector_stats['Gainers'] = df[df['Daily_Change_Pct'] > 0].groupby('Sector').size().reindex(sector_stats.index, fill_value=0)
            sector_stats['Losers'] = df[df['Daily_Change_Pct'] < 0].groupby('Sector').size().reindex(sector_stats.index, fill_value=0)
            sector_stats['Gainer_Ratio'] = sector_stats['Gainers'] / sector_stats['Daily_Change_Pct_count']
            
            return sector_stats.reset_index()
            
        except Exception as e:
            print(f"Error in sector analysis: {e}")
            return pd.DataFrame()
    
    def volume_analysis(self, df: pd.DataFrame) -> Dict:
        """Analyze volume patterns and relationships"""
        try:
            if df.empty:
                return {}
            
            # Volume vs price change correlation
            price_volume_corr = df['Daily_Change_Pct'].corr(df['Volume_Change_Pct'])
            
            # High volume threshold (top 25%)
            high_volume_threshold = df['Volume'].quantile(0.75)
            high_volume_stocks = df[df['Volume'] >= high_volume_threshold]
            
            # Volume change categories
            high_volume_increase = len(df[df['Volume_Change_Pct'] > 50])
            high_volume_decrease = len(df[df['Volume_Change_Pct'] < -50])
            
            # Average performance by volume categories
            low_volume_performance = df[df['Volume'] < df['Volume'].quantile(0.25)]['Daily_Change_Pct'].mean()
            high_volume_performance = high_volume_stocks['Daily_Change_Pct'].mean()
            
            return {
                'price_volume_correlation': price_volume_corr,
                'high_volume_threshold': high_volume_threshold,
                'high_volume_stocks_count': len(high_volume_stocks),
                'high_volume_increase_count': high_volume_increase,
                'high_volume_decrease_count': high_volume_decrease,
                'low_volume_avg_performance': low_volume_performance,
                'high_volume_avg_performance': high_volume_performance,
                'total_market_volume': df['Volume'].sum(),
                'avg_volume_change': df['Volume_Change_Pct'].mean()
            }
            
        except Exception as e:
            print(f"Error in volume analysis: {e}")
            return {}
    
    def calculate_moving_averages(self, historical_data: pd.DataFrame, periods: List[int] = [5, 10, 20, 50]) -> pd.DataFrame:
        """Calculate moving averages for historical data"""
        try:
            if historical_data.empty:
                return pd.DataFrame()
            
            result = historical_data.copy()
            
            for period in periods:
                if len(result) >= period:
                    result[f'MA_{period}'] = result['Close'].rolling(window=period).mean()
            
            return result
            
        except Exception as e:
            print(f"Error calculating moving averages: {e}")
            return pd.DataFrame()
    
    def detect_unusual_activity(self, df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """Detect stocks with unusual price or volume activity"""
        try:
            if df.empty:
                return {}
            
            # Define thresholds for unusual activity
            price_change_threshold = df['Daily_Change_Pct'].std() * 2
            volume_change_threshold = df['Volume_Change_Pct'].std() * 2
            
            # Unusual price movements
            unusual_price_up = df[df['Daily_Change_Pct'] > price_change_threshold]
            unusual_price_down = df[df['Daily_Change_Pct'] < -price_change_threshold]
            
            # Unusual volume activity
            unusual_volume_up = df[df['Volume_Change_Pct'] > volume_change_threshold]
            unusual_volume_down = df[df['Volume_Change_Pct'] < -volume_change_threshold]
            
            # Combined unusual activity (both price and volume)
            combined_unusual = df[
                (abs(df['Daily_Change_Pct']) > price_change_threshold) &
                (abs(df['Volume_Change_Pct']) > volume_change_threshold)
            ]
            
            return {
                'unusual_price_up': unusual_price_up,
                'unusual_price_down': unusual_price_down,
                'unusual_volume_up': unusual_volume_up,
                'unusual_volume_down': unusual_volume_down,
                'combined_unusual': combined_unusual
            }
            
        except Exception as e:
            print(f"Error detecting unusual activity: {e}")
            return {}
    
    def calculate_risk_metrics(self, df: pd.DataFrame) -> Dict:
        """Calculate risk-related metrics"""
        try:
            if df.empty:
                return {}
            
            # Value at Risk (VaR) - 5% worst case
            var_5 = df['Daily_Change_Pct'].quantile(0.05)
            var_1 = df['Daily_Change_Pct'].quantile(0.01)
            
            # Maximum drawdown
            max_gain = df['Daily_Change_Pct'].max()
            max_loss = df['Daily_Change_Pct'].min()
            
            # Volatility metrics
            volatility = df['Daily_Change_Pct'].std()
            
            # Risk-adjusted returns (assuming risk-free rate of 2% annually, ~0.008% daily)
            risk_free_rate = 0.008
            excess_returns = df['Daily_Change_Pct'] - risk_free_rate
            sharpe_ratio = excess_returns.mean() / volatility if volatility > 0 else 0
            
            return {
                'var_5_percent': var_5,
                'var_1_percent': var_1,
                'max_gain': max_gain,
                'max_loss': max_loss,
                'volatility': volatility,
                'sharpe_ratio': sharpe_ratio,
                'risk_free_rate': risk_free_rate
            }
            
        except Exception as e:
            print(f"Error calculating risk metrics: {e}")
            return {}
