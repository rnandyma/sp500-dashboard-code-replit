"""
Performance monitoring and optimization tools for the S&P 500 dashboard
"""

import streamlit as st
import time
from typing import Dict, List
from cache_manager import get_cache_manager

class PerformanceMonitor:
    def __init__(self):
        self.cache_manager = get_cache_manager()
        self.load_times = {}
    
    def start_timer(self, operation: str):
        """Start timing an operation"""
        self.load_times[operation] = time.time()
    
    def end_timer(self, operation: str) -> float:
        """End timing an operation and return duration"""
        if operation in self.load_times:
            duration = time.time() - self.load_times[operation]
            del self.load_times[operation]
            return duration
        return 0.0
    
    def display_cache_stats(self):
        """Display cache statistics in sidebar"""
        with st.sidebar:
            with st.expander("📊 Performance Stats", expanded=False):
                cache_stats = self.cache_manager.get_cache_stats()
                
                st.write("**Cache Status:**")
                st.write(f"• Total cached items: {cache_stats['total_cached_items']}")
                
                if cache_stats['cache_breakdown']:
                    st.write("**Cache by type:**")
                    for data_type, count in cache_stats['cache_breakdown'].items():
                        st.write(f"• {data_type}: {count} items")
                
                # Cache management buttons
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("🗑️ Clear Cache", help="Clear all cached data"):
                        self.cache_manager.invalidate_cache()
                        st.success("Cache cleared!")
                        st.rerun()
                
                with col2:
                    if st.button("🧹 Cleanup", help="Remove expired cache entries"):
                        expired_count = self.cache_manager.cleanup_expired_cache()
                        if expired_count > 0:
                            st.success(f"Removed {expired_count} expired items")
                        else:
                            st.info("No expired items found")
                        st.rerun()
                
                # Performance metrics
                if hasattr(st.session_state, 'performance_optimizer'):
                    perf_metrics = st.session_state.performance_optimizer.get_performance_metrics()
                    st.write("**Performance:**")
                    st.write(f"• Session state: {perf_metrics['session_state_size']} items")
                    st.write(f"• Memory usage: {perf_metrics['memory_usage']}")
                    
                    if st.button("🚀 Optimize", help="Optimize performance"):
                        st.session_state.performance_optimizer.optimize_session_state()
                        st.success("Performance optimized!")
                        st.rerun()
    
    def show_loading_performance(self, operation: str, duration: float, cached: bool = False):
        """Show loading performance metrics"""
        status_color = "🟢" if cached else "🔵"
        status_text = "Cached" if cached else "Fresh"
        
        if duration < 1:
            time_text = f"{duration*1000:.0f}ms"
        else:
            time_text = f"{duration:.1f}s"
        
        st.success(f"{status_color} {operation} completed in {time_text} ({status_text})")
    
    def optimize_data_loading(self) -> Dict[str, str]:
        """Provide optimization recommendations"""
        cache_stats = self.cache_manager.get_cache_stats()
        recommendations = {}
        
        if cache_stats['total_cached_items'] == 0:
            recommendations['cache'] = "Consider enabling data caching for better performance"
        
        if cache_stats['total_cached_items'] > 100:
            recommendations['cleanup'] = "Cache is getting large, consider running cleanup"
        
        return recommendations

def get_performance_monitor():
    """Get or create performance monitor from session state"""
    if 'performance_monitor' not in st.session_state:
        st.session_state.performance_monitor = PerformanceMonitor()
    return st.session_state.performance_monitor