import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import time

from data_fetcher import DataFetcher
from analytics import Analytics
from utils import format_number, format_percentage, get_color_for_change
from cache_manager import get_cache_manager
from performance_monitor import get_performance_monitor
from ux_enhancements import get_ux_enhancements
from performance_optimizer import get_performance_optimizer
from loading_manager import get_loading_manager

# Page configuration
st.set_page_config(
    page_title="S&P 500 Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for green checkboxes and table header formatting
st.markdown("""
<style>
/* Target all possible Streamlit checkbox variations when checked */
.stCheckbox input:checked ~ div,
.stCheckbox input:checked + div,
.stCheckbox input:checked ~ div > div,
.stCheckbox input:checked + div > div,
div[data-testid="stCheckbox"] input:checked ~ div,
div[data-testid="stCheckbox"] input:checked + div,
div[data-testid="stCheckbox"] input:checked ~ div > div,
div[data-testid="stCheckbox"] input:checked + div > div {
    background-color: #28a745 !important;
    border-color: #28a745 !important;
    color: white !important;
}

/* Target checkbox containers when checked */
div[data-testid="stCheckbox"]:has(input:checked) > div,
div[data-testid="stCheckbox"]:has(input:checked) > div > div,
div[data-testid="stCheckbox"]:has(input:checked) div[role="checkbox"],
.stCheckbox:has(input:checked) > label > div > div,
.stCheckbox:has(input:checked) > label > div > div > div {
    background-color: #28a745 !important;
    border-color: #28a745 !important;
}

/* Force override all checkbox backgrounds when checked */
[data-testid="stCheckbox"] input:checked ~ * {
    background-color: #28a745 !important;
    border-color: #28a745 !important;
}

/* Prevent table header wrapping and improve display */
.stMarkdown > div > p {
    white-space: nowrap !important;
    font-size: 13px !important;
    margin: 0.2rem 0 !important;
}

[data-testid="column"] div p strong {
    white-space: nowrap !important;
    font-size: 13px !important;
}

/* Make columns more compact */
[data-testid="column"] {
    padding: 0.25rem !important;
}

/* Target specific checkbox elements */
div[role="checkbox"][aria-checked="true"],
div[data-baseweb="checkbox"][aria-checked="true"],
div[data-baseweb="checkbox"]:has(input:checked) {
    background-color: #28a745 !important;
    border-color: #28a745 !important;
}

/* Override Streamlit's theme colors specifically */
.stApp [data-testid="stCheckbox"] input:checked + div {
    background-color: #28a745 !important;
    border-color: #28a745 !important;
}

/* SVG checkmark styling */
div[data-testid="stCheckbox"] svg,
.stCheckbox svg {
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'data_fetcher' not in st.session_state:
    st.session_state.data_fetcher = DataFetcher()
if 'analytics' not in st.session_state:
    st.session_state.analytics = Analytics()
if 'cache_manager' not in st.session_state:
    st.session_state.cache_manager = get_cache_manager()
if 'performance_monitor' not in st.session_state:
    st.session_state.performance_monitor = get_performance_monitor()
if 'ux_enhancements' not in st.session_state:
    st.session_state.ux_enhancements = get_ux_enhancements()
if 'performance_optimizer' not in st.session_state:
    st.session_state.performance_optimizer = get_performance_optimizer()
if 'loading_manager' not in st.session_state:
    st.session_state.loading_manager = get_loading_manager()
if 'companies_list' not in st.session_state:
    st.session_state.companies_list = None
if 'selected_companies_data' not in st.session_state:
    st.session_state.selected_companies_data = None
if 'market_overview_data' not in st.session_state:
    st.session_state.market_overview_data = None

# Main title
st.title("📈 S&P 500 Daily Performance Dashboard")
st.caption("Real-time market analysis and portfolio tracking")

# Load companies list once with performance monitoring
if st.session_state.companies_list is None:
    st.session_state.performance_monitor.start_timer("companies_list")
    with st.spinner("Loading S&P 500 companies list..."):
        try:
            st.session_state.companies_list = st.session_state.data_fetcher.get_sp500_companies_list()
            duration = st.session_state.performance_monitor.end_timer("companies_list")
            # Check if data was cached by looking for cache message
        except Exception as e:
            st.error(f"Error loading companies list: {str(e)}")
            st.stop()

# Display performance stats in sidebar
st.session_state.performance_monitor.display_cache_stats()

# Show connection status and offline capabilities
st.session_state.loading_manager.show_connection_status()

# Optimize session state periodically
st.session_state.performance_optimizer.optimize_session_state()

# Main dashboard content
if st.session_state.companies_list is not None:
    # Initialize session state variables
    if 'selected_companies' not in st.session_state:
        st.session_state.selected_companies = []
    if 'search_query' not in st.session_state:
        st.session_state.search_query = ""
    if 'display_count' not in st.session_state:
        st.session_state.display_count = 20
    
    # Enhanced header with help section
    col_header, col_help = st.columns([3, 1])
    
    with col_header:
        st.header("🔍 Search & Select Companies for Analysis")
    
    with col_help:
        st.session_state.ux_enhancements.create_interactive_help_section()
    
    # Add section divider
    st.session_state.ux_enhancements.create_section_divider()
    
    # Search input with filtering
    search_query = st.text_input(
        "Search companies by name or ticker:", 
        value=st.session_state.search_query,
        placeholder="Type NVIDIA, AAPL, tech, bank, etc. and press Enter to filter the list below",
        help="Press Enter after typing to filter the company list below and select from results"
    )
    
    # Update search query in session state
    if search_query != st.session_state.search_query:
        st.session_state.search_query = search_query
    
    # Display count selector
    col_search, col_count = st.columns([3, 1])
    
    with col_count:
        display_options = [20, 50, 100, 200, "All"]
        selected_display = st.selectbox(
            "Show companies:",
            options=display_options,
            index=0,
            help="Select how many companies to display in the table"
        )
        
        if selected_display != st.session_state.display_count:
            st.session_state.display_count = selected_display
    
    # Filter companies based on search
    if search_query:
        filtered_companies = st.session_state.companies_list[
            st.session_state.companies_list['Company'].str.contains(search_query, case=False) |
            st.session_state.companies_list['Symbol'].str.contains(search_query, case=False)
        ].copy()
        
        if len(filtered_companies) > 0:
            st.write(f"📊 Found **{len(filtered_companies)}** companies matching '{search_query}'")
        else:
            st.error(f"❌ No companies found matching '{search_query}'. The searched company is not part of the S&P 500 index.")
            st.info("💡 Try searching for companies like: AAPL, Microsoft, Amazon, Tesla, or browse all companies below.")
            # Show all companies when no matches found
            filtered_companies = st.session_state.companies_list.copy()
    else:
        filtered_companies = st.session_state.companies_list.copy()
    
    # Apply display limit
    total_companies = len(filtered_companies)
    if st.session_state.display_count == "All":
        display_companies = filtered_companies.copy()
        st.write(f"📊 Showing all **{total_companies}** companies")
    else:
        display_companies = filtered_companies.head(st.session_state.display_count).copy()
        if search_query:
            st.write(f"📊 Showing **{len(display_companies)}** of **{total_companies}** matching companies")
        else:
            st.write(f"📊 Showing **{len(display_companies)}** of **{total_companies}** S&P 500 companies")
    
    # Quick selection buttons
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("🏆 Top 10 by Market Cap"):
            # Merge with existing selections
            new_selections = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'AVGO', 'LLY', 'WMT']
            st.session_state.selected_companies = list(set(st.session_state.selected_companies + new_selections))
            st.rerun()
    with col2:
        if st.button("🔥 Tech Giants"):
            # Merge with existing selections
            new_selections = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META']
            st.session_state.selected_companies = list(set(st.session_state.selected_companies + new_selections))
            st.rerun()
    with col3:
        if st.button("🏦 Financial Sector"):
            # Merge with existing selections
            new_selections = ['JPM', 'BAC', 'WFC', 'GS', 'MS', 'C']
            st.session_state.selected_companies = list(set(st.session_state.selected_companies + new_selections))
            st.rerun()
    with col4:
        if st.button("🧹 Clear Selection"):
            st.session_state.selected_companies = []
            st.rerun()
    
    # Initialize selected companies list - will be populated by checkboxes
    selected_companies = []
    
    # Filter available companies (remove already selected ones)
    available_companies = display_companies[~display_companies['Symbol'].isin(st.session_state.selected_companies)].copy()
    
    # Create two-column layout: Available companies on left, selected companies on right
    left_col, right_col = st.columns([3, 2])
    
    with left_col:
        # Display available companies table with checkboxes
        if search_query:
            st.subheader(f"🔍 Available Companies ({len(available_companies)} companies)")
        else:
            st.subheader("📋 Available S&P 500 Companies")
        
        # Track companies to move to selected list
        companies_to_select = []
        
        # Create checkbox selection interface
        if not available_companies.empty:
            # Create columns for the table with checkboxes - adjusted widths
            checkbox_col, symbol_col, company_col = st.columns([0.4, 0.8, 3.8])
            
            with checkbox_col:
                st.write("**✓**")
            with symbol_col:
                st.write("**Symbol**")
            with company_col:
                st.write("**Company**")
            
            # Create checkboxes for each available company
            for idx, row in available_companies.iterrows():
                checkbox_col, symbol_col, company_col = st.columns([0.4, 0.8, 3.8])
                
                with checkbox_col:
                    # Create checkbox to select company
                    selected = st.checkbox(
                        f"Select {row['Symbol']}", 
                        value=False,
                        key=f"select_{row['Symbol']}_{len(st.session_state.selected_companies)}",
                        label_visibility="collapsed"
                    )
                    
                    if selected:
                        companies_to_select.append(row['Symbol'])
                
                with symbol_col:
                    st.write(row['Symbol'])
                
                with company_col:
                    st.write(row['Company'])
            
            # Move selected companies to the selected list
            if companies_to_select:
                st.session_state.selected_companies.extend(companies_to_select)
                st.session_state.selected_companies = sorted(list(set(st.session_state.selected_companies)))
                st.rerun()
        else:
            st.write("All companies have been selected.")
    
    with right_col:
        # Display selected companies table
        st.subheader("📊 Selected Companies")
        
        if st.session_state.selected_companies:
            # Create dataframe of selected companies with full names
            selected_df = st.session_state.companies_list[
                st.session_state.companies_list['Symbol'].isin(st.session_state.selected_companies)
            ].copy()
            
            # Sort alphabetically by company name
            selected_df = selected_df.sort_values('Company')
            
            # Display count
            st.write(f"**Total Selected:** {len(st.session_state.selected_companies)}")
            
            # Track companies to move back to available list
            companies_to_deselect = []
            
            # Create column headers - adjusted widths for better display
            deselect_col, symbol_col, company_col = st.columns([0.4, 0.7, 3.9])
            
            with deselect_col:
                st.write("**✗**")
            with symbol_col:
                st.write("**Symbol**")
            with company_col:
                st.write("**Company**")
            
            # Create checkboxes for each selected company
            for idx, row in selected_df.iterrows():
                deselect_col, symbol_col, company_col = st.columns([0.4, 0.7, 3.9])
                
                with deselect_col:
                    # Checkbox to deselect company
                    deselect = st.checkbox(
                        f"Remove {row['Symbol']}", 
                        value=False,
                        key=f"deselect_{row['Symbol']}_{len(st.session_state.selected_companies)}",
                        label_visibility="collapsed"
                    )
                    
                    if deselect:
                        companies_to_deselect.append(row['Symbol'])
                
                with symbol_col:
                    st.write(row['Symbol'])
                
                with company_col:
                    st.write(row['Company'])
            
            # Move deselected companies back to available list
            if companies_to_deselect:
                # Remove from selected list
                st.session_state.selected_companies = [comp for comp in st.session_state.selected_companies if comp not in companies_to_deselect]
                
                # Clear the data cache to force refresh
                if 'selected_companies_data' in st.session_state:
                    st.session_state.selected_companies_data = None
                
                # Force page refresh to update both panels
                st.rerun()
        else:
            st.session_state.ux_enhancements.show_enhanced_alert(
                "Select companies from the left panel to start your analysis. Use the search bar to find specific companies or try the quick selection buttons below.",
                "info",
                "Get Started"
            )
    
    # Auto-load data when companies are selected with performance monitoring
    if st.session_state.selected_companies:
        # Check if we need to fetch new data
        if ('selected_companies_data' not in st.session_state or 
            st.session_state.selected_companies_data is None or
            len(st.session_state.selected_companies_data) != len(st.session_state.selected_companies)):
            
            try:
                def load_selected_data():
                    return st.session_state.data_fetcher.get_selected_companies_data(st.session_state.selected_companies)
                
                # Check offline mode first
                if st.session_state.loading_manager.is_offline_mode():
                    offline_data = st.session_state.loading_manager.get_offline_data("selected_companies")
                    if offline_data is not None:
                        st.session_state.selected_companies_data = offline_data
                        st.info(f"📱 Using offline data for {len(st.session_state.selected_companies)} companies")
                    else:
                        st.warning("📱 No offline data available for selected companies")
                        st.session_state.selected_companies_data = pd.DataFrame()
                else:
                    st.session_state.performance_monitor.start_timer("selected_companies")
                    
                    selected_data = st.session_state.loading_manager.with_loading(
                        "selected_companies", 
                        load_selected_data, 
                        f"Loading data for {len(st.session_state.selected_companies)} companies..."
                    )
                    
                    duration = st.session_state.performance_monitor.end_timer("selected_companies")
                    
                    if selected_data is not None and not selected_data.empty:
                        st.session_state.selected_companies_data = selected_data
                        # Save for offline access
                        st.session_state.loading_manager.save_offline_data("selected_companies", selected_data)
                        
                        cached = "cached" in str(selected_data.to_string()).lower()
                        st.session_state.performance_monitor.show_loading_performance(
                            "Company data loading", duration, cached
                        )
                        
                        # Show quick stats cards
                        st.session_state.ux_enhancements.create_section_divider("Portfolio Overview")
                        st.session_state.ux_enhancements.create_quick_stats_cards(st.session_state.selected_companies_data)
                    else:
                        st.session_state.loading_manager.handle_error(
                            "selected_companies", 
                            "No data could be retrieved for the selected companies", 
                            {"retry": True, "offline": True}
                        )
                        st.session_state.selected_companies_data = pd.DataFrame()
                        
            except Exception as e:
                st.session_state.loading_manager.handle_error(
                    "selected_companies", 
                    str(e), 
                    {"retry": True, "offline": True, "reset": True}
                )
    else:
        # Clear data when no companies selected
        st.session_state.selected_companies_data = None
    
    # Enhanced status display
    if st.session_state.selected_companies:
        progress = min(100, (len(st.session_state.selected_companies) / 20) * 100)
        st.session_state.ux_enhancements.show_progress_bar(
            progress, 
            f"Portfolio Status: {len(st.session_state.selected_companies)} companies selected"
        )
    
    # Enhanced Market Overview Section
    st.session_state.ux_enhancements.create_section_divider("Market Overview")
    
    col_market_header, col_refresh = st.columns([3, 1])
    with col_market_header:
        st.header("📊 Market Overview - Top Performers")
    
    with col_refresh:
        if st.button("🔄 Refresh Market Data", help="Get the latest market data"):
            # Clear market overview cache to force refresh
            st.session_state.cache_manager.invalidate_cache('market_overview')
            st.session_state.market_overview_data = None
            st.rerun()
    
    # Auto-load market overview data with enhanced loading and error recovery
    if 'market_overview_data' not in st.session_state or st.session_state.market_overview_data is None:
        try:
            def load_market_data():
                return st.session_state.data_fetcher.get_market_overview_data()
            
            # Check offline mode first
            if st.session_state.loading_manager.is_offline_mode():
                offline_data = st.session_state.loading_manager.get_offline_data("market_overview")
                if offline_data is not None:
                    st.session_state.market_overview_data = offline_data
                    st.info("📱 Using offline market overview data")
                else:
                    st.warning("📱 No offline market data available")
                    st.session_state.market_overview_data = pd.DataFrame()
            else:
                st.session_state.performance_monitor.start_timer("market_overview")
                
                market_data = st.session_state.loading_manager.with_loading(
                    "market_overview", 
                    load_market_data, 
                    "Loading market overview data..."
                )
                
                duration = st.session_state.performance_monitor.end_timer("market_overview")
                
                if market_data is not None and not market_data.empty:
                    st.session_state.market_overview_data = market_data
                    # Save for offline access
                    st.session_state.loading_manager.save_offline_data("market_overview", market_data)
                    
                    cached = "cached" in str(market_data.to_string()).lower()
                    st.session_state.performance_monitor.show_loading_performance(
                        "Market overview loading", duration, cached
                    )
                else:
                    st.session_state.loading_manager.handle_error(
                        "market_overview", 
                        "Unable to load market overview data", 
                        {"retry": True, "offline": True}
                    )
                    st.session_state.market_overview_data = pd.DataFrame()
                    
        except Exception as e:
            st.session_state.loading_manager.handle_error(
                "market_overview", 
                str(e), 
                {"retry": True, "offline": True, "reset": True}
            )
            st.session_state.market_overview_data = pd.DataFrame()
    
    # Display sector-based market overview
    if st.session_state.market_overview_data is not None and not st.session_state.market_overview_data.empty:
        overview_df = st.session_state.market_overview_data
        
        # Get sector performance analysis
        sector_analysis = st.session_state.data_fetcher.get_sector_performance(overview_df)
        
        if sector_analysis:
            # Create tabs for each sector
            sector_names = list(sector_analysis.keys())
            tabs = st.tabs([f"📊 {sector}" for sector in sector_names])
            
            for idx, (sector_name, sector_data) in enumerate(sector_analysis.items()):
                with tabs[idx]:
                    # Sector summary metrics
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        avg_change = sector_data['avg_change']
                        color = "normal" if avg_change >= 0 else "inverse"
                        st.metric(
                            "Sector Average", 
                            f"{avg_change:+.2f}%",
                            delta=f"{avg_change:.2f}%"
                        )
                    
                    with col2:
                        st.metric("Companies Analyzed", sector_data['companies_count'])
                    
                    with col3:
                        total_volume = sector_data['total_volume']
                        st.metric("Total Volume", format_number(total_volume))
                    
                    # Top gainers and losers for this sector
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("🔥 Top 5 Gainers")
                        if not sector_data['top_gainers'].empty:
                            gainers_display = sector_data['top_gainers'].copy()
                            gainers_display['Daily Change %'] = gainers_display['Daily Change %'].apply(lambda x: f"+{x:.2f}%")
                            gainers_display['Current Price'] = gainers_display['Current Price'].apply(lambda x: f"${x:.2f}")
                            st.dataframe(gainers_display, hide_index=True, use_container_width=True)
                        else:
                            st.write("No gainers data available")
                    
                    with col2:
                        st.subheader("📉 Top 5 Losers")
                        if not sector_data['top_losers'].empty:
                            losers_display = sector_data['top_losers'].copy()
                            losers_display['Daily Change %'] = losers_display['Daily Change %'].apply(lambda x: f"{x:.2f}%")
                            losers_display['Current Price'] = losers_display['Current Price'].apply(lambda x: f"${x:.2f}")
                            st.dataframe(losers_display, hide_index=True, use_container_width=True)
                        else:
                            st.write("No losers data available")
        else:
            st.warning("Unable to load sector analysis data.")

# Show selected companies data if available
if st.session_state.selected_companies_data is not None and not st.session_state.selected_companies_data.empty:
    df = st.session_state.selected_companies_data
    
    st.header("📊 Selected Companies Performance")
    
    # Summary metrics for selected companies
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        gainers = len(df[df['Daily Change %'] > 0])
        st.metric("Gainers", gainers, f"{gainers/len(df)*100:.1f}%")
    
    with col2:
        losers = len(df[df['Daily Change %'] < 0])
        st.metric("Losers", losers, f"{losers/len(df)*100:.1f}%")
    
    with col3:
        avg_change = df['Daily Change %'].mean()
        st.metric("Average Change", format_percentage(avg_change), 
                 delta=f"{avg_change:.2f}%")
    
    with col4:
        total_volume = df['Volume'].sum()
        st.metric("Total Volume", format_number(total_volume))
    
    # Selected companies performance table
    st.header("📈 Price & Volume Analysis")
    
    # Format the data for display
    display_df = df.copy()
    display_df['Current Price'] = display_df['Current Price'].apply(lambda x: f"${x:.2f}")
    display_df['Daily Change'] = display_df['Daily Change'].apply(lambda x: f"${x:+.2f}")
    display_df['Daily Change %'] = display_df['Daily Change %'].apply(lambda x: f"{x:+.2f}%")
    display_df['Volume'] = display_df['Volume'].apply(format_number)
    display_df['Volume Change'] = display_df['Volume Change'].apply(lambda x: f"{x:+.0f}")
    display_df['Est. Buy Volume'] = display_df['Est. Buy Volume'].apply(format_number)
    display_df['Est. Sell Volume'] = display_df['Est. Sell Volume'].apply(format_number)
    display_df['Market Cap'] = display_df['Market Cap'].apply(format_number)
    display_df['P/E Ratio'] = display_df['P/E Ratio'].apply(lambda x: f"{x:.2f}" if pd.notnull(x) and x > 0 else "N/A")
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # Volume vs Price visualization
    if len(df) > 1:
        st.header("📊 Volume vs Price Analysis")
        
        fig = px.scatter(df, x='Volume Change', y='Daily Change %', 
                        hover_data=['Symbol', 'Company'], 
                        labels={'Volume Change': 'Volume Change', 
                               'Daily Change %': 'Price Change (%)'},
                        title="Volume Change vs Price Change for Selected Companies")
        fig.update_traces(marker=dict(opacity=0.7, size=10))
        st.plotly_chart(fig, use_container_width=True)
    
    # Buy/Sell Volume comparison
    if len(df) > 0:
        st.header("💰 Buy vs Sell Volume Estimation")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Buy Volume chart
            fig_buy = px.bar(df, x='Symbol', y='Est. Buy Volume',
                            title="Estimated Buy Volume by Company")
            fig_buy.update_traces(marker_color='green', opacity=0.7)
            st.plotly_chart(fig_buy, use_container_width=True)
            
        with col2:
            # Sell Volume chart  
            fig_sell = px.bar(df, x='Symbol', y='Est. Sell Volume',
                             title="Estimated Sell Volume by Company")
            fig_sell.update_traces(marker_color='red', opacity=0.7)
            st.plotly_chart(fig_sell, use_container_width=True)
    
    # Historical Price Tracking Section
    st.header("📈 Historical Price Tracking")
    
    # Time period selector
    col1, col2 = st.columns([1, 3])
    
    with col1:
        period_options = {
            "1 Day": "2d",  # Use 2d to get at least 2 data points for comparison
            "1 Week": "1wk", 
            "1 Month": "1mo",
            "3 Months": "3mo",
            "6 Months": "6mo",
            "YTD": "ytd",
            "1 Year": "1y",
            "5 Years": "5y"
        }
        
        selected_period_name = st.selectbox(
            "Select Time Period",
            options=list(period_options.keys()),
            index=2  # Default to 1 Month
        )
        selected_period = period_options[selected_period_name]
    
    with col2:
        # Company selector for historical analysis - default to all selected companies
        if len(df) > 0:
            default_symbols = df['Symbol'].tolist()  # Default to ALL selected companies
        else:
            default_symbols = []
            
        historical_symbols = st.multiselect(
            "Select companies for historical price tracking",
            options=df['Symbol'].tolist() if len(df) > 0 else [],
            default=default_symbols,
            help="All selected companies are included by default. Remove any you don't want to see in the historical charts."
        )
    
    # Auto-load and display historical data when companies are selected
    if historical_symbols:
        try:
            def load_historical_data():
                return st.session_state.data_fetcher.get_historical_data(historical_symbols, selected_period)
            
            # Check offline mode first
            cache_key = f"historical_{selected_period}_{len(historical_symbols)}"
            if st.session_state.loading_manager.is_offline_mode():
                offline_data = st.session_state.loading_manager.get_offline_data(cache_key)
                if offline_data is not None:
                    historical_data = offline_data
                    st.info(f"📱 Using offline historical data ({selected_period_name})")
                else:
                    st.warning(f"📱 No offline historical data available for {selected_period_name}")
                    historical_data = pd.DataFrame()
            else:
                historical_data = st.session_state.loading_manager.with_loading(
                    "historical_data", 
                    load_historical_data, 
                    f"Loading {selected_period_name.lower()} historical data for {len(historical_symbols)} companies..."
                )
                
                if historical_data is not None:
                    # Save for offline access
                    st.session_state.loading_manager.save_offline_data(cache_key, historical_data)
                else:
                    historical_data = pd.DataFrame()
            
            if not historical_data.empty:
                # Price trend chart
                if selected_period_name == "1 Day":
                    # For 1-day data, show hourly trends
                    fig_price = px.line(
                        historical_data, 
                        x='Date', 
                        y='Close', 
                        color='Symbol',
                        title=f"Intraday Price Trends - Last 48 Hours",
                        labels={'Close': 'Stock Price ($)', 'Date': 'Time'}
                    )
                else:
                    fig_price = px.line(
                        historical_data, 
                        x='Date', 
                        y='Close', 
                        color='Symbol',
                        title=f"Price Trends - {selected_period_name}",
                        labels={'Close': 'Stock Price ($)', 'Date': 'Date'}
                    )
                fig_price.update_layout(height=500)
                st.plotly_chart(fig_price, use_container_width=True)
                
                # Volume trend chart
                fig_volume = px.line(
                    historical_data, 
                    x='Date', 
                    y='Volume', 
                    color='Symbol',
                    title=f"Volume Trends - {selected_period_name}",
                    labels={'Volume': 'Trading Volume', 'Date': 'Date'}
                )
                fig_volume.update_layout(height=400)
                st.plotly_chart(fig_volume, use_container_width=True)
                
                # Performance summary table
                st.subheader(f"Performance Summary - {selected_period_name}")
                
                summary_data = []
                for symbol in historical_symbols:
                    symbol_data = historical_data[historical_data['Symbol'] == symbol]
                    if len(symbol_data) > 1:
                        start_price = symbol_data['Close'].iloc[0]
                        end_price = symbol_data['Close'].iloc[-1]
                        price_change = end_price - start_price
                        price_change_pct = (price_change / start_price) * 100
                        
                        high_price = symbol_data['High'].max()
                        low_price = symbol_data['Low'].min()
                        avg_volume = symbol_data['Volume'].mean()
                        
                        summary_data.append({
                            'Symbol': symbol,
                            'Start Price': f"${start_price:.2f}",
                            'End Price': f"${end_price:.2f}",
                            'Change': f"${price_change:+.2f}",
                            'Change %': f"{price_change_pct:+.2f}%",
                            'High': f"${high_price:.2f}",
                            'Low': f"${low_price:.2f}",
                            'Avg Volume': format_number(avg_volume)
                        })
                
                if summary_data:
                    summary_df = pd.DataFrame(summary_data)
                    st.dataframe(summary_df, use_container_width=True, hide_index=True)
                    
            else:
                st.warning("No historical data could be retrieved for the selected companies and time period.")
                
        except Exception as e:
            st.session_state.loading_manager.handle_error(
                "historical_data", 
                str(e), 
                {"retry": True, "offline": True}
            )
    else:
        st.info("Historical charts and analysis will appear here once you select companies for tracking.")

else:
    st.write("Select companies from the sidebar and click 'Get Data' to see detailed price movements and volume analysis.")

# Footer
st.markdown("---")
st.markdown("*Data provided by Yahoo Finance. This dashboard is for informational purposes only.*")
