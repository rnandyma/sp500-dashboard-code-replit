"""
Loading indicators and offline mode management for S&P 500 Dashboard
Provides comprehensive loading states, offline capabilities, and error recovery
"""

import streamlit as st
import pandas as pd
import time
from typing import Optional, Dict, Any, Callable
from datetime import datetime, timedelta
import json
import os

class LoadingManager:
    def __init__(self):
        self.loading_states = {}
        self.offline_cache_dir = ".offline_cache"
        self.ensure_offline_cache_dir()
        
    def ensure_offline_cache_dir(self):
        """Create offline cache directory if it doesn't exist"""
        if not os.path.exists(self.offline_cache_dir):
            os.makedirs(self.offline_cache_dir)
    
    def show_loading_indicator(self, key: str, message: str = "Loading...", 
                             progress: Optional[float] = None):
        """Display enhanced loading indicator with progress"""
        st.session_state[f"{key}_loading"] = True
        
        if progress is not None:
            st.progress(progress, text=f"{message} ({int(progress * 100)}%)")
        else:
            # Simple spinner without skeleton to avoid interference
            with st.spinner(message):
                pass
    
    def show_simple_loading(self, message: str = "Loading..."):
        """Show simple loading message"""
        st.info(f"🔄 {message}")
    
    def show_data_loading_placeholder(self):
        """Show loading placeholder for data"""
        st.info("📊 Loading data...")
    
    def show_chart_loading_placeholder(self):
        """Show loading placeholder for charts"""
        st.info("📈 Loading charts...")
    
    def hide_loading_indicator(self, key: str):
        """Hide loading indicator"""
        if f"{key}_loading" in st.session_state:
            st.session_state[f"{key}_loading"] = False
    
    def with_loading(self, key: str, func: Callable, message: str = "Loading...", 
                    *args, **kwargs):
        """Execute function with loading indicator"""
        try:
            # Use streamlit's built-in spinner for simplicity
            with st.spinner(message):
                result = func(*args, **kwargs)
            return result
        except Exception as e:
            self.handle_error(key, str(e))
            return None
    
    def handle_error(self, operation: str, error_message: str, 
                    recovery_options: Optional[Dict] = None):
        """Display comprehensive error handling with recovery options"""
        st.error(f"❌ Error in {operation}: {error_message}")
        
        # Check if offline data is available
        offline_data = self.get_offline_data(operation)
        if offline_data is not None:
            st.warning("🔄 Using offline data from previous session")
            return offline_data
        
        # Provide recovery options
        if recovery_options:
            st.info("🛠️ Recovery Options:")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🔄 Retry", key=f"retry_{operation}"):
                    st.rerun()
            
            with col2:
                if st.button("📱 Offline Mode", key=f"offline_{operation}"):
                    self.enable_offline_mode()
                    st.rerun()
            
            with col3:
                if st.button("🏠 Reset", key=f"reset_{operation}"):
                    self.reset_application_state()
                    st.rerun()
        
        return None
    
    def save_offline_data(self, key: str, data: Any):
        """Save data for offline access"""
        try:
            file_path = os.path.join(self.offline_cache_dir, f"{key}.json")
            
            # Convert DataFrame to dict if necessary
            if isinstance(data, pd.DataFrame):
                data_to_save = {
                    'data': data.to_dict('records'),
                    'columns': data.columns.tolist(),
                    'timestamp': datetime.now().isoformat(),
                    'type': 'dataframe'
                }
            else:
                data_to_save = {
                    'data': data,
                    'timestamp': datetime.now().isoformat(),
                    'type': type(data).__name__
                }
            
            with open(file_path, 'w') as f:
                json.dump(data_to_save, f, default=str)
                
        except Exception as e:
            print(f"Error saving offline data for {key}: {e}")
    
    def get_offline_data(self, key: str) -> Optional[Any]:
        """Retrieve offline data if available"""
        try:
            file_path = os.path.join(self.offline_cache_dir, f"{key}.json")
            
            if not os.path.exists(file_path):
                return None
            
            with open(file_path, 'r') as f:
                saved_data = json.load(f)
            
            # Check if data is not too old (24 hours)
            saved_time = datetime.fromisoformat(saved_data['timestamp'])
            if datetime.now() - saved_time > timedelta(hours=24):
                return None
            
            # Reconstruct DataFrame if necessary
            if saved_data.get('type') == 'dataframe':
                return pd.DataFrame(saved_data['data'])
            else:
                return saved_data['data']
                
        except Exception as e:
            print(f"Error loading offline data for {key}: {e}")
            return None
    
    def enable_offline_mode(self):
        """Enable offline mode with saved data"""
        st.session_state.offline_mode = True
        st.success("🔄 Offline mode enabled. Using cached data.")
    
    def disable_offline_mode(self):
        """Disable offline mode"""
        st.session_state.offline_mode = False
        st.success("🌐 Online mode enabled.")
    
    def is_offline_mode(self) -> bool:
        """Check if application is in offline mode"""
        return getattr(st.session_state, 'offline_mode', False)
    
    def reset_application_state(self):
        """Reset application to initial state"""
        # Clear session state except essential items
        keys_to_keep = ['data_fetcher', 'analytics', 'cache_manager', 
                       'performance_monitor', 'ux_enhancements', 'performance_optimizer']
        
        keys_to_remove = [key for key in st.session_state.keys() 
                         if key not in keys_to_keep]
        
        for key in keys_to_remove:
            del st.session_state[key]
        
        st.success("🔄 Application reset successfully!")
    
    def show_connection_status(self):
        """Display connection status in sidebar"""
        with st.sidebar:
            st.markdown("---")
            st.subheader("🌐 Connection Status")
            
            if self.is_offline_mode():
                st.error("📱 Offline Mode")
                if st.button("🌐 Go Online"):
                    self.disable_offline_mode()
                    st.rerun()
            else:
                st.success("🌐 Online")
                if st.button("📱 Go Offline"):
                    self.enable_offline_mode()
                    st.rerun()
            
            # Show offline data availability
            offline_files = self.get_offline_data_info()
            if offline_files:
                with st.expander("📁 Offline Data Available"):
                    for file_info in offline_files:
                        st.write(f"• {file_info['name']} ({file_info['age']})")
    
    def get_offline_data_info(self) -> list:
        """Get information about available offline data"""
        info = []
        try:
            if os.path.exists(self.offline_cache_dir):
                for filename in os.listdir(self.offline_cache_dir):
                    if filename.endswith('.json'):
                        file_path = os.path.join(self.offline_cache_dir, filename)
                        modified_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                        age = datetime.now() - modified_time
                        
                        if age.days > 0:
                            age_str = f"{age.days} days ago"
                        elif age.seconds > 3600:
                            age_str = f"{age.seconds // 3600} hours ago"
                        else:
                            age_str = f"{age.seconds // 60} minutes ago"
                        
                        info.append({
                            'name': filename.replace('.json', ''),
                            'age': age_str
                        })
        except Exception:
            pass
        
        return info
    
    def progressive_data_loading(self, data_sources: list, 
                               progress_callback: Optional[Callable] = None):
        """Load data progressively with progress updates"""
        total_sources = len(data_sources)
        results = {}
        
        for i, (key, source_func, args) in enumerate(data_sources):
            progress = (i + 1) / total_sources
            
            if progress_callback:
                progress_callback(progress, f"Loading {key}...")
            
            try:
                result = source_func(*args) if args else source_func()
                results[key] = result
                
                # Save for offline access
                if result is not None:
                    self.save_offline_data(key, result)
                    
            except Exception as e:
                # Try offline data
                offline_result = self.get_offline_data(key)
                if offline_result is not None:
                    results[key] = offline_result
                    st.warning(f"Using offline data for {key}")
                else:
                    st.error(f"Failed to load {key}: {str(e)}")
                    results[key] = None
        
        return results

def get_loading_manager():
    """Get or create loading manager from session state"""
    if 'loading_manager' not in st.session_state:
        st.session_state.loading_manager = LoadingManager()
    return st.session_state.loading_manager