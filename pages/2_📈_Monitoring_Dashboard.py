import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data_provider import DataProvider

def load_monitoring_data():
    """Load monitoring data from persistent storage"""
    monitoring_file = 'monitoring_data.json'
    
    # Initialize from session state if available
    if 'monitoring_list' in st.session_state:
        return st.session_state.monitoring_list
    
    # Try to load from file
    if os.path.exists(monitoring_file):
        try:
            with open(monitoring_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Error loading monitoring data: {e}")
    
    return []

def save_monitoring_data(monitoring_list):
    """Save monitoring data to persistent storage"""
    monitoring_file = 'monitoring_data.json'
    
    try:
        with open(monitoring_file, 'w', encoding='utf-8') as f:
            json.dump(monitoring_list, f, indent=2, ensure_ascii=False)
        
        # Update session state
        st.session_state.monitoring_list = monitoring_list
        
    except Exception as e:
        st.error(f"Error saving monitoring data: {e}")

def get_status_color(status):
    """Get color for status indicator"""
    colors = {
        'active': '🟢',
        'paused': '🟡', 
        'error': '🔴',
        'stopped': '⚫'
    }
    return colors.get(status, '⚫')

def format_parameters(params):
    """Format strategy parameters for display"""
    if not params:
        return "No parameters"
    
    formatted = []
    for key, value in params.items():
        formatted.append(f"{key}: {value}")
    
    return ", ".join(formatted)

def main():
    st.set_page_config(
        page_title="Monitoring Dashboard",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("📊 Monitoring Management Dashboard")
    st.markdown("Manage all your active monitoring strategies")
    
    # Load monitoring data
    monitoring_list = load_monitoring_data()
    
    if not monitoring_list:
        st.info("🔍 No monitoring strategies found. Run some backtests and add them to monitoring!")
        
        # Show example of how to add monitoring
        with st.expander("How to add monitoring"):
            st.markdown("""
            1. Go to the **Stock Backtesting Bot** page
            2. Configure and run a backtest
            3. Click the **"📈 Apply for Monitoring"** button in the results
            4. Your strategy will appear here for management
            """)
        return
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    active_count = len([m for m in monitoring_list if m['status'] == 'active'])
    paused_count = len([m for m in monitoring_list if m['status'] == 'paused'])
    error_count = len([m for m in monitoring_list if m['status'] == 'error'])
    total_count = len(monitoring_list)
    
    with col1:
        st.metric("Total Strategies", total_count)
    with col2:
        st.metric("Active", active_count, delta=active_count)
    with col3:
        st.metric("Paused", paused_count, delta=paused_count if paused_count > 0 else None)
    with col4:
        st.metric("Errors", error_count, delta=error_count if error_count > 0 else None)
    
    st.markdown("---")
    
    # Monitoring list management
    st.header("🎯 Active Monitoring Strategies")
    
    # Bulk actions
    col_bulk1, col_bulk2, col_bulk3 = st.columns(3)
    
    with col_bulk1:
        if st.button("▶️ Resume All Paused"):
            updated = False
            for item in monitoring_list:
                if item['status'] == 'paused':
                    item['status'] = 'active'
                    updated = True
            if updated:
                save_monitoring_data(monitoring_list)
                st.rerun()
    
    with col_bulk2:
        if st.button("⏸️ Pause All Active"):
            updated = False
            for item in monitoring_list:
                if item['status'] == 'active':
                    item['status'] = 'paused'
                    updated = True
            if updated:
                save_monitoring_data(monitoring_list)
                st.rerun()
    
    with col_bulk3:
        if st.button("🗑️ Clear All Stopped", type="secondary"):
            original_count = len(monitoring_list)
            monitoring_list = [item for item in monitoring_list if item['status'] != 'stopped']
            if len(monitoring_list) < original_count:
                save_monitoring_data(monitoring_list)
                st.rerun()
    
    st.markdown("---")
    
    # Individual monitoring items
    items_to_remove = []
    items_updated = False
    
    for i, item in enumerate(monitoring_list):
        with st.expander(
            f"{get_status_color(item['status'])} {item['ticker']} - {item['strategy']} "
            f"({item['market']} Market)",
            expanded=(item['status'] in ['active', 'error'])
        ):
            # Item details
            col_info1, col_info2 = st.columns(2)
            
            with col_info1:
                st.write(f"**Ticker:** {item['ticker']}")
                st.write(f"**Strategy:** {item['strategy']}")
                st.write(f"**Market:** {item['market']} Market")
                st.write(f"**Status:** {item['status'].title()}")
            
            with col_info2:
                st.write(f"**Parameters:** {format_parameters(item.get('parameters', {}))}")
                st.write(f"**Initial Cash:** ${item.get('cash', 'N/A'):,}")
                st.write(f"**Commission:** {item.get('commission', 0)*100:.2f}%")
                st.write(f"**Added:** {datetime.fromisoformat(item['added_date']).strftime('%Y-%m-%d %H:%M')}")
            
            # Control buttons
            col_btn1, col_btn2, col_btn3, col_btn4, col_btn5 = st.columns(5)
            
            with col_btn1:
                if item['status'] == 'paused':
                    if st.button("▶️ Resume", key=f"resume_{i}"):
                        item['status'] = 'active'
                        items_updated = True
                elif item['status'] == 'active':
                    if st.button("⏸️ Pause", key=f"pause_{i}"):
                        item['status'] = 'paused'
                        items_updated = True
            
            with col_btn2:
                if st.button("⏹️ Stop", key=f"stop_{i}"):
                    item['status'] = 'stopped'
                    items_updated = True
            
            with col_btn3:
                if st.button("🔧 Edit", key=f"edit_{i}"):
                    st.info("Edit functionality coming soon!")
            
            with col_btn4:
                if st.button("📊 View Results", key=f"results_{i}"):
                    st.info("Results view coming soon!")
            
            with col_btn5:
                if st.button("🗑️ Remove", key=f"remove_{i}", type="secondary"):
                    items_to_remove.append(i)
    
    # Apply changes
    if items_to_remove:
        # Remove items in reverse order to maintain indices
        for i in sorted(items_to_remove, reverse=True):
            monitoring_list.pop(i)
        save_monitoring_data(monitoring_list)
        st.rerun()
    
    if items_updated:
        save_monitoring_data(monitoring_list)
        st.rerun()
    
    # Add new monitoring manually
    st.markdown("---")
    st.header("➕ Add New Monitoring")
    
    with st.expander("Add Monitoring Manually"):
        with st.form("add_monitoring"):
            col_form1, col_form2 = st.columns(2)
            
            with col_form1:
                new_market = st.selectbox("Market", options=["US", "KRX"])
                new_ticker = st.text_input("Ticker")
                new_strategy = st.selectbox("Strategy", options=["TrendFollowing"])
                
            with col_form2:
                new_cash = st.number_input("Initial Cash", min_value=1000, value=10000)
                new_commission = st.slider("Commission (%)", min_value=0.0, max_value=1.0, value=0.2, step=0.1)
                
                if new_strategy == "TrendFollowing":
                    short_ma = st.number_input("Short MA", min_value=5, max_value=200, value=50)
                    long_ma = st.number_input("Long MA", min_value=10, max_value=500, value=200)
            
            if st.form_submit_button("Add to Monitoring"):
                if new_ticker:
                    # Validate ticker
                    if DataProvider.validate_ticker(new_ticker, new_market):
                        market_info = DataProvider.get_market_info(new_ticker)
                        normalized_ticker = market_info['normalized_ticker']
                        
                        new_config = {
                            'ticker': normalized_ticker,
                            'market': new_market,
                            'strategy': new_strategy,
                            'parameters': {
                                'short_ma': int(short_ma),
                                'long_ma': int(long_ma)
                            } if new_strategy == "TrendFollowing" else {},
                            'added_date': datetime.now().isoformat(),
                            'status': 'active',
                            'cash': new_cash,
                            'commission': new_commission / 100
                        }
                        
                        # Check if already exists
                        existing = next((item for item in monitoring_list 
                                       if item['ticker'] == normalized_ticker and item['strategy'] == new_strategy), None)
                        
                        if existing:
                            st.error(f"⚠️ {normalized_ticker} with {new_strategy} strategy is already being monitored")
                        else:
                            monitoring_list.append(new_config)
                            save_monitoring_data(monitoring_list)
                            st.success(f"✅ {normalized_ticker} added to monitoring!")
                            st.rerun()
                    else:
                        st.error(f"❌ Invalid ticker: {new_ticker}")
                else:
                    st.error("Please enter a ticker symbol")

if __name__ == "__main__":
    main()