"""
User Experience Enhancement module for S&P 500 Dashboard
Provides improved UI components, animations, and interactive elements
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from typing import List, Dict, Optional
import time

class UXEnhancements:
    def __init__(self):
        self.load_custom_css()
    
    def load_custom_css(self):
        """Load enhanced CSS for better user experience"""
        st.markdown("""
        <style>
        /* Enhanced loading animations */
        @keyframes pulse {
            0% { opacity: 0.6; }
            50% { opacity: 1; }
            100% { opacity: 0.6; }
        }
        
        .loading-pulse {
            animation: pulse 1.5s ease-in-out infinite;
        }
        
        /* Enhanced card styling */
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1.5rem;
            border-radius: 12px;
            color: white;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease;
            margin: 10px 0;
        }
        
        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        }
        
        .positive-card {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        }
        
        .negative-card {
            background: linear-gradient(135deg, #fc4a1a 0%, #f7b733 100%);
        }
        
        /* Enhanced button styling */
        .stButton > button {
            border-radius: 20px;
            border: none;
            padding: 0.5rem 1.5rem;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }
        
        /* Progress bar enhancements */
        .custom-progress {
            height: 8px;
            border-radius: 4px;
            background: #e0e0e0;
            overflow: hidden;
            margin: 10px 0;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            border-radius: 4px;
            transition: width 0.3s ease;
        }
        
        /* Enhanced table styling */
        .dataframe td {
            border-radius: 4px;
            transition: background-color 0.2s ease;
        }
        
        .dataframe tr:hover td {
            background-color: #f8f9fa;
        }
        
        /* Tooltip styling */
        .tooltip {
            position: relative;
            display: inline-block;
            cursor: help;
        }
        
        .tooltip .tooltiptext {
            visibility: hidden;
            width: 200px;
            background-color: #555;
            color: #fff;
            text-align: center;
            border-radius: 6px;
            padding: 8px;
            position: absolute;
            z-index: 1;
            bottom: 125%;
            left: 50%;
            margin-left: -100px;
            opacity: 0;
            transition: opacity 0.3s;
            font-size: 12px;
        }
        
        .tooltip:hover .tooltiptext {
            visibility: visible;
            opacity: 1;
        }
        
        /* Section dividers */
        .section-divider {
            border: none;
            height: 2px;
            background: linear-gradient(90deg, transparent, #667eea, transparent);
            margin: 2rem 0;
        }
        
        /* Enhanced alerts */
        .custom-alert {
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
            border-left: 4px solid;
        }
        
        .alert-success {
            background-color: #d4edda;
            border-color: #28a745;
            color: #155724;
        }
        
        .alert-warning {
            background-color: #fff3cd;
            border-color: #ffc107;
            color: #856404;
        }
        
        .alert-info {
            background-color: #d1ecf1;
            border-color: #17a2b8;
            color: #0c5460;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def create_metric_card(self, title: str, value: str, change: Optional[float] = None, 
                          subtitle: str = "", icon: str = "📊"):
        """Create a simple metric card using Streamlit's built-in components"""
        # Use Streamlit's built-in metric component for simplicity
        if change is not None:
            delta_str = f"{change:+.2f}%"
            st.metric(
                label=f"{icon} {title}",
                value=value,
                delta=delta_str,
                help=subtitle if subtitle else None
            )
        else:
            st.metric(
                label=f"{icon} {title}",
                value=value,
                help=subtitle if subtitle else None
            )
    
    def show_progress_bar(self, progress: float, label: str = "Progress"):
        """Display an enhanced progress bar"""
        progress_html = f"""
        <div style="margin: 1rem 0;">
            <div style="margin-bottom: 0.5rem; font-weight: 500;">{label}</div>
            <div class="custom-progress">
                <div class="progress-fill" style="width: {progress}%;"></div>
            </div>
            <div style="text-align: right; font-size: 0.8rem; margin-top: 0.2rem;">{progress:.1f}%</div>
        </div>
        """
        st.markdown(progress_html, unsafe_allow_html=True)
    
    def create_interactive_tooltip(self, text: str, tooltip: str):
        """Create text with interactive tooltip"""
        tooltip_html = f"""
        <div class="tooltip">{text}
            <span class="tooltiptext">{tooltip}</span>
        </div>
        """
        st.markdown(tooltip_html, unsafe_allow_html=True)
    
    def show_loading_skeleton(self, rows: int = 5):
        """Display a simple loading indicator"""
        with st.container():
            st.info("📊 Loading data...")
            # Create simple placeholder rows using Streamlit components
            for i in range(rows):
                col1, col2, col3 = st.columns([1, 3, 1])
                with col1:
                    st.write("●●●")
                with col2:
                    st.write("●●●●●●●●●●●●●●●")
                with col3:
                    st.write("●●●")
    
    def create_section_divider(self, title: str = ""):
        """Create a simple section divider"""
        if title:
            st.subheader(f"📋 {title}")
        else:
            st.divider()
    
    def show_enhanced_alert(self, message: str, alert_type: str = "info", 
                          title: str = "", dismissible: bool = False):
        """Show alert using Streamlit's built-in components"""
        icons = {
            "success": "✅",
            "warning": "⚠️", 
            "error": "❌",
            "info": "ℹ️"
        }
        
        icon = icons.get(alert_type, "ℹ️")
        full_message = f"{icon} **{title}**\n\n{message}" if title else f"{icon} {message}"
        
        # Use Streamlit's built-in alert components
        if alert_type == "success":
            st.success(full_message)
        elif alert_type == "warning":
            st.warning(full_message)
        elif alert_type == "error":
            st.error(full_message)
        else:
            st.info(full_message)
    
    def create_quick_stats_cards(self, data: pd.DataFrame) -> None:
        """Create quick stats overview cards"""
        if data.empty:
            return
        
        # Calculate key metrics
        total_companies = len(data)
        avg_change = data['Daily Change %'].mean()
        total_volume = data['Volume'].sum()
        gainers = len(data[data['Daily Change %'] > 0])
        losers = len(data[data['Daily Change %'] < 0])
        
        # Create cards in columns
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            self.create_metric_card(
                "Companies", 
                str(total_companies), 
                None, 
                "Selected for analysis", 
                "🏢"
            )
        
        with col2:
            self.create_metric_card(
                "Avg Change", 
                f"{avg_change:.2f}%", 
                avg_change, 
                "Daily performance", 
                "📈" if avg_change > 0 else "📉"
            )
        
        with col3:
            gainers_pct = (gainers / total_companies) * 100 if total_companies > 0 else 0
            self.create_metric_card(
                "Gainers", 
                f"{gainers}", 
                gainers_pct, 
                f"{gainers_pct:.1f}% of portfolio", 
                "🟢"
            )
        
        with col4:
            volume_formatted = f"{total_volume/1e9:.1f}B" if total_volume > 1e9 else f"{total_volume/1e6:.1f}M"
            self.create_metric_card(
                "Total Volume", 
                volume_formatted, 
                None, 
                "Trading activity", 
                "📊"
            )
    
    def create_interactive_help_section(self):
        """Create an interactive help section"""
        with st.expander("💡 How to Use This Dashboard", expanded=False):
            st.markdown("""
            ### Quick Start Guide
            
            **1. Select Companies** 📊
            - Use the search bar to find specific companies
            - Check boxes next to companies to add them to your portfolio
            - Use quick selection buttons for common groups (Tech Giants, Finance, etc.)
            
            **2. Analyze Performance** 📈
            - View real-time price changes and volume data
            - Check market overview for sector-based analysis
            - Explore historical trends with different time periods
            
            **3. Monitor Your Portfolio** 👀
            - Selected companies move to the right panel
            - Remove companies by checking the boxes in the selected list
            - Data updates automatically when selections change
            
            **4. Performance Features** ⚡
            - Data is cached for faster loading
            - Check the sidebar for cache statistics
            - Clear cache if you need fresh data
            
            ### Tips for Better Performance
            - Start with fewer companies and add more as needed
            - Use the search function to quickly find specific stocks
            - Historical data loads automatically for selected companies
            """)
    
    def add_keyboard_shortcuts_info(self):
        """Add keyboard shortcuts information"""
        with st.expander("💡 Pro Tips", expanded=False):
            st.write("• Press Ctrl+F to search")
            st.write("• Scroll for more data") 
            st.write("• Check sidebar for cache stats")

def get_ux_enhancements():
    """Get or create UX enhancements from session state"""
    if 'ux_enhancements' not in st.session_state:
        st.session_state.ux_enhancements = UXEnhancements()
    return st.session_state.ux_enhancements