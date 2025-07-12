"""
Smart caching system for S&P 500 dashboard
Handles data caching with timestamps, expiration, and intelligent invalidation
"""

import pandas as pd
import time
import pickle
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import streamlit as st

class CacheManager:
    def __init__(self, cache_dir: str = ".cache"):
        """Initialize cache manager with specified cache directory"""
        self.cache_dir = cache_dir
        self.memory_cache = {}
        self.cache_expiry = {
            'companies_list': 3600,  # 1 hour - company list changes rarely
            'market_overview': 300,  # 5 minutes - market data for overview
            'company_data': 60,      # 1 minute - individual company data
            'historical_data': 1800, # 30 minutes - historical data
            'sector_data': 300       # 5 minutes - sector analysis
        }
        
        # Create cache directory if it doesn't exist
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
    
    def _get_cache_key(self, data_type: str, symbols: List[str] = None, **kwargs) -> str:
        """Generate unique cache key based on data type and parameters"""
        key_parts = [data_type]
        
        if symbols:
            # Sort symbols for consistent key generation
            sorted_symbols = sorted(symbols)
            if len(sorted_symbols) > 10:
                # For large symbol lists, use hash for shorter keys
                import hashlib
                symbols_hash = hashlib.md5(''.join(sorted_symbols).encode()).hexdigest()[:8]
                key_parts.append(f"symbols_{len(sorted_symbols)}_{symbols_hash}")
            else:
                key_parts.append('_'.join(sorted_symbols))
        
        # Add other parameters
        for key, value in sorted(kwargs.items()):
            key_parts.append(f"{key}_{value}")
        
        return '_'.join(key_parts)
    
    def _is_cache_valid(self, cache_key: str, data_type: str) -> bool:
        """Check if cached data is still valid based on expiry time"""
        if cache_key not in self.memory_cache:
            return False
        
        cached_time = self.memory_cache[cache_key].get('timestamp', 0)
        expiry_seconds = self.cache_expiry.get(data_type, 300)
        
        return (time.time() - cached_time) < expiry_seconds
    
    def get_cached_data(self, data_type: str, symbols: List[str] = None, **kwargs) -> Optional[pd.DataFrame]:
        """Retrieve cached data if available and valid"""
        cache_key = self._get_cache_key(data_type, symbols, **kwargs)
        
        # Check memory cache first
        if self._is_cache_valid(cache_key, data_type):
            return self.memory_cache[cache_key]['data']
        
        # Check disk cache for larger datasets
        if data_type in ['companies_list', 'historical_data']:
            disk_cache_path = os.path.join(self.cache_dir, f"{cache_key}.pkl")
            if os.path.exists(disk_cache_path):
                try:
                    with open(disk_cache_path, 'rb') as f:
                        cached_item = pickle.load(f)
                    
                    if self._is_cache_valid_disk(cached_item['timestamp'], data_type):
                        # Load back to memory cache
                        self.memory_cache[cache_key] = cached_item
                        return cached_item['data']
                except Exception:
                    # Remove corrupted cache file
                    os.remove(disk_cache_path)
        
        return None
    
    def _is_cache_valid_disk(self, cached_time: float, data_type: str) -> bool:
        """Check if disk-cached data is still valid"""
        expiry_seconds = self.cache_expiry.get(data_type, 300)
        return (time.time() - cached_time) < expiry_seconds
    
    def cache_data(self, data: pd.DataFrame, data_type: str, symbols: List[str] = None, **kwargs):
        """Cache data with timestamp"""
        cache_key = self._get_cache_key(data_type, symbols, **kwargs)
        
        cached_item = {
            'data': data,
            'timestamp': time.time(),
            'data_type': data_type
        }
        
        # Always cache in memory
        self.memory_cache[cache_key] = cached_item
        
        # Cache to disk for larger datasets
        if data_type in ['companies_list', 'historical_data']:
            disk_cache_path = os.path.join(self.cache_dir, f"{cache_key}.pkl")
            try:
                with open(disk_cache_path, 'wb') as f:
                    pickle.dump(cached_item, f)
            except Exception:
                pass  # Fail silently if disk cache fails
    
    def invalidate_cache(self, data_type: str = None, symbols: List[str] = None):
        """Invalidate specific cached data or all cache"""
        if data_type is None:
            # Clear all cache
            self.memory_cache.clear()
            # Clear disk cache
            for file in os.listdir(self.cache_dir):
                if file.endswith('.pkl'):
                    try:
                        os.remove(os.path.join(self.cache_dir, file))
                    except Exception:
                        pass
        else:
            # Clear specific data type
            keys_to_remove = []
            for key in self.memory_cache.keys():
                if key.startswith(data_type):
                    if symbols is None or any(symbol in key for symbol in symbols):
                        keys_to_remove.append(key)
            
            for key in keys_to_remove:
                del self.memory_cache[key]
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics for monitoring"""
        total_items = len(self.memory_cache)
        cache_sizes = {}
        
        for key, item in self.memory_cache.items():
            data_type = item.get('data_type', 'unknown')
            if data_type not in cache_sizes:
                cache_sizes[data_type] = 0
            cache_sizes[data_type] += 1
        
        return {
            'total_cached_items': total_items,
            'cache_breakdown': cache_sizes,
            'cache_directory': self.cache_dir
        }
    
    def cleanup_expired_cache(self):
        """Remove expired cache entries"""
        current_time = time.time()
        expired_keys = []
        
        for key, item in self.memory_cache.items():
            data_type = item.get('data_type', 'unknown')
            expiry_seconds = self.cache_expiry.get(data_type, 300)
            
            if (current_time - item['timestamp']) > expiry_seconds:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.memory_cache[key]
        
        return len(expired_keys)

# Streamlit session state integration
def get_cache_manager() -> CacheManager:
    """Get or create cache manager from Streamlit session state"""
    if 'cache_manager' not in st.session_state:
        st.session_state.cache_manager = CacheManager()
    return st.session_state.cache_manager