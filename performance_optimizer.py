"""
Performance optimization module for S&P 500 Dashboard
Focuses on UI responsiveness, network efficiency, and API optimization
"""

import streamlit as st
import pandas as pd
import time
import threading
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import queue
import asyncio
from functools import lru_cache

class PerformanceOptimizer:
    def __init__(self):
        self.ui_state = {}
        self.debounce_timers = {}
        self.request_queue = queue.Queue()
        self.batch_size = 50  # Optimal batch size for API requests
        
    def debounce_user_input(self, key: str, value: any, delay: float = 0.5):
        """Debounce user input to prevent excessive API calls"""
        if key in self.debounce_timers:
            self.debounce_timers[key].cancel()
        
        timer = threading.Timer(delay, self._execute_debounced_action, args=[key, value])
        self.debounce_timers[key] = timer
        timer.start()
    
    def _execute_debounced_action(self, key: str, value: any):
        """Execute the debounced action after delay"""
        if key == 'search_query':
            self._update_search_results(value)
        elif key == 'company_selection':
            self._update_company_data(value)
    
    def optimize_dataframe_display(self, df: pd.DataFrame, max_rows: int = 1000) -> pd.DataFrame:
        """Optimize dataframe for display performance"""
        if df.empty:
            return df
        
        # Limit rows for UI performance
        if len(df) > max_rows:
            df = df.head(max_rows)
        
        # Optimize data types for memory efficiency
        for col in df.columns:
            if df[col].dtype == 'object':
                # Convert to category if low cardinality
                if df[col].nunique() / len(df) < 0.5:
                    df[col] = df[col].astype('category')
            elif df[col].dtype == 'float64':
                # Downcast floats where possible
                df[col] = pd.to_numeric(df[col], downcast='float')
        
        return df
    
    def batch_api_requests(self, symbols: List[str], fetch_function, max_workers: int = 10):
        """Optimize API requests using batching and parallel processing"""
        if not symbols:
            return pd.DataFrame()
        
        # Split symbols into optimal batches
        batches = [symbols[i:i + self.batch_size] for i in range(0, len(symbols), self.batch_size)]
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all batches
            future_to_batch = {
                executor.submit(fetch_function, batch): batch 
                for batch in batches
            }
            
            # Process completed requests
            for future in as_completed(future_to_batch):
                try:
                    batch_result = future.result(timeout=30)  # 30s timeout per batch
                    if not batch_result.empty:
                        results.append(batch_result)
                except Exception as e:
                    st.warning(f"Batch request failed: {str(e)}")
        
        # Combine results
        if results:
            return pd.concat(results, ignore_index=True)
        return pd.DataFrame()
    
    def implement_virtual_scrolling(self, data: pd.DataFrame, page_size: int = 20):
        """Implement virtual scrolling for large datasets"""
        if 'page_number' not in st.session_state:
            st.session_state.page_number = 0
        
        total_pages = (len(data) - 1) // page_size + 1 if len(data) > 0 else 0
        
        # Navigation controls
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if st.button("◀ Previous", disabled=st.session_state.page_number == 0):
                st.session_state.page_number -= 1
                st.rerun()
        
        with col2:
            st.write(f"Page {st.session_state.page_number + 1} of {total_pages}")
        
        with col3:
            if st.button("Next ▶", disabled=st.session_state.page_number >= total_pages - 1):
                st.session_state.page_number += 1
                st.rerun()
        
        # Return current page data
        start_idx = st.session_state.page_number * page_size
        end_idx = start_idx + page_size
        return data.iloc[start_idx:end_idx]
    
    def optimize_chart_rendering(self, chart_data: pd.DataFrame, max_points: int = 1000):
        """Optimize chart data for better rendering performance"""
        if len(chart_data) <= max_points:
            return chart_data
        
        # Sample data intelligently
        step = len(chart_data) // max_points
        optimized_data = chart_data.iloc[::step].copy()
        
        # Always include the last point
        if len(chart_data) > 0:
            optimized_data = pd.concat([optimized_data, chart_data.tail(1)])
        
        return optimized_data.drop_duplicates().reset_index(drop=True)
    
    def lazy_load_component(self, component_key: str, load_function, *args, **kwargs):
        """Implement lazy loading for expensive components"""
        if f"{component_key}_loaded" not in st.session_state:
            st.session_state[f"{component_key}_loaded"] = False
        
        if f"{component_key}_data" not in st.session_state:
            st.session_state[f"{component_key}_data"] = None
        
        # Show placeholder until user interaction
        if not st.session_state[f"{component_key}_loaded"]:
            if st.button(f"Load {component_key.replace('_', ' ').title()}", key=f"load_{component_key}"):
                with st.spinner(f"Loading {component_key}..."):
                    st.session_state[f"{component_key}_data"] = load_function(*args, **kwargs)
                    st.session_state[f"{component_key}_loaded"] = True
                st.rerun()
        else:
            return st.session_state[f"{component_key}_data"]
    
    def optimize_session_state(self):
        """Clean up session state to prevent memory bloat"""
        keys_to_clean = []
        current_time = time.time()
        
        for key in st.session_state:
            if key.endswith('_timestamp'):
                # Remove data older than 30 minutes
                if current_time - st.session_state[key] > 1800:
                    base_key = key.replace('_timestamp', '')
                    keys_to_clean.extend([key, base_key])
        
        for key in keys_to_clean:
            if key in st.session_state:
                del st.session_state[key]
    
    def implement_request_deduplication(self, request_key: str, ttl: int = 300):
        """Prevent duplicate API requests within TTL window"""
        current_time = time.time()
        
        if f"{request_key}_last_request" in st.session_state:
            last_request_time = st.session_state[f"{request_key}_last_request"]
            if current_time - last_request_time < ttl:
                return False  # Skip request
        
        st.session_state[f"{request_key}_last_request"] = current_time
        return True  # Allow request
    
    def compress_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Compress dataframe for better memory usage"""
        for col in df.select_dtypes(include=['object']):
            if df[col].nunique() / len(df) < 0.5:  # Low cardinality
                df[col] = df[col].astype('category')
        
        for col in df.select_dtypes(include=['int64']):
            df[col] = pd.to_numeric(df[col], downcast='integer')
        
        for col in df.select_dtypes(include=['float64']):
            df[col] = pd.to_numeric(df[col], downcast='float')
        
        return df
    
    def get_performance_metrics(self) -> Dict:
        """Get current performance metrics"""
        return {
            'session_state_size': len(st.session_state),
            'active_debounce_timers': len(self.debounce_timers),
            'request_queue_size': self.request_queue.qsize(),
            'memory_usage': self._estimate_memory_usage()
        }
    
    def _estimate_memory_usage(self) -> str:
        """Estimate current memory usage of session state"""
        total_size = 0
        for key, value in st.session_state.items():
            if isinstance(value, pd.DataFrame):
                total_size += value.memory_usage(deep=True).sum()
        
        return f"{total_size / 1024 / 1024:.1f} MB"

def get_performance_optimizer():
    """Get or create performance optimizer from session state"""
    if 'performance_optimizer' not in st.session_state:
        st.session_state.performance_optimizer = PerformanceOptimizer()
    return st.session_state.performance_optimizer