import pandas as pd
import numpy as np
from typing import Union

def format_number(num: Union[int, float]) -> str:
    """Format large numbers with appropriate suffixes (K, M, B, T)"""
    try:
        if pd.isna(num) or num == 0:
            return "0"
        
        num = float(num)
        
        if abs(num) >= 1e12:
            return f"{num/1e12:.2f}T"
        elif abs(num) >= 1e9:
            return f"{num/1e9:.2f}B"
        elif abs(num) >= 1e6:
            return f"{num/1e6:.2f}M"
        elif abs(num) >= 1e3:
            return f"{num/1e3:.2f}K"
        else:
            return f"{num:.2f}"
    except:
        return str(num)

def format_percentage(pct: Union[int, float]) -> str:
    """Format percentage with proper sign and precision"""
    try:
        if pd.isna(pct):
            return "0.00%"
        
        pct = float(pct)
        if pct > 0:
            return f"+{pct:.2f}%"
        else:
            return f"{pct:.2f}%"
    except:
        return str(pct)

def format_currency(amount: Union[int, float]) -> str:
    """Format currency amounts"""
    try:
        if pd.isna(amount):
            return "$0.00"
        
        amount = float(amount)
        if abs(amount) >= 1e9:
            return f"${amount/1e9:.2f}B"
        elif abs(amount) >= 1e6:
            return f"${amount/1e6:.2f}M"
        elif abs(amount) >= 1e3:
            return f"${amount/1e3:.2f}K"
        else:
            return f"${amount:.2f}"
    except:
        return str(amount)

def get_color_for_change(change: Union[int, float]) -> str:
    """Get color code for change values (green for positive, red for negative)"""
    try:
        if pd.isna(change):
            return "#000000"  # Black for neutral/unknown
        
        change = float(change)
        if change > 0:
            return "#00C851"  # Green
        elif change < 0:
            return "#FF4444"  # Red
        else:
            return "#000000"  # Black for zero
    except:
        return "#000000"

def calculate_percentage_change(current: Union[int, float], previous: Union[int, float]) -> float:
    """Calculate percentage change between two values"""
    try:
        if pd.isna(current) or pd.isna(previous) or previous == 0:
            return 0.0
        
        current = float(current)
        previous = float(previous)
        
        return ((current - previous) / previous) * 100
    except:
        return 0.0

def safe_divide(numerator: Union[int, float], denominator: Union[int, float], default: float = 0.0) -> float:
    """Safely divide two numbers, returning default if division by zero"""
    try:
        if pd.isna(numerator) or pd.isna(denominator) or denominator == 0:
            return default
        
        return float(numerator) / float(denominator)
    except:
        return default

def clean_symbol(symbol: str) -> str:
    """Clean stock symbol for API compatibility"""
    try:
        if pd.isna(symbol):
            return ""
        
        # Convert to string and strip whitespace
        symbol = str(symbol).strip().upper()
        
        # Replace common characters that might cause issues
        symbol = symbol.replace('.', '-')
        
        return symbol
    except:
        return str(symbol)

def validate_data_completeness(df: pd.DataFrame, required_columns: list) -> dict:
    """Validate that DataFrame has required columns and check data completeness"""
    try:
        results = {
            'is_valid': True,
            'missing_columns': [],
            'empty_columns': [],
            'data_quality_score': 0.0,
            'total_rows': len(df),
            'issues': []
        }
        
        if df.empty:
            results['is_valid'] = False
            results['issues'].append("DataFrame is empty")
            return results
        
        # Check for missing required columns
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            results['is_valid'] = False
            results['missing_columns'] = missing_cols
            results['issues'].append(f"Missing required columns: {missing_cols}")
        
        # Check for empty columns
        for col in required_columns:
            if col in df.columns and df[col].isna().all():
                results['empty_columns'].append(col)
                results['issues'].append(f"Column '{col}' is completely empty")
        
        # Calculate data quality score
        if required_columns:
            available_cols = [col for col in required_columns if col in df.columns]
            total_cells = len(df) * len(available_cols)
            
            if total_cells > 0:
                non_null_cells = sum(df[col].notna().sum() for col in available_cols)
                results['data_quality_score'] = (non_null_cells / total_cells) * 100
        
        return results
        
    except Exception as e:
        return {
            'is_valid': False,
            'error': str(e),
            'issues': [f"Error during validation: {str(e)}"]
        }

def get_market_status() -> dict:
    """Get current market status (open/closed) - simplified version"""
    try:
        from datetime import datetime, time
        import pytz
        
        # Get current time in Eastern timezone (NYSE timezone)
        et_timezone = pytz.timezone('US/Eastern')
        current_time = datetime.now(et_timezone)
        
        # Market hours: 9:30 AM - 4:00 PM ET, Monday-Friday
        market_open = time(9, 30)
        market_close = time(16, 0)
        
        is_weekday = current_time.weekday() < 5  # Monday = 0, Friday = 4
        current_time_only = current_time.time()
        
        is_open = (is_weekday and 
                  market_open <= current_time_only <= market_close)
        
        return {
            'is_open': is_open,
            'current_time': current_time.strftime('%Y-%m-%d %H:%M:%S %Z'),
            'is_weekday': is_weekday,
            'market_open_time': '09:30 ET',
            'market_close_time': '16:00 ET'
        }
        
    except Exception as e:
        return {
            'is_open': None,
            'error': str(e),
            'current_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }
