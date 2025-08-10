import os
import sys
from datetime import datetime, date

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from backtesting import Backtest

# 상위 디렉토리의 strategies 모듈을 import하기 위해 경로 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies import TrendFollowing
from utils.data_provider import DataProvider


def create_returns_chart(trades):
    if trades is not None and not trades.empty:
        returns = trades["ReturnPct"] * 100
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.hist(returns, bins=20, edgecolor="black", alpha=0.7, color='steelblue')
        ax.set_title("Trade Returns Distribution", fontsize=16, fontweight='bold')
        ax.set_xlabel("Return (%)", fontsize=12)
        ax.set_ylabel("Frequency", fontsize=12)
        ax.grid(True, alpha=0.3)
        return fig
    return None


def main():
    st.set_page_config(
        page_title="Stock Backtesting Bot",
        page_icon="📈",
        layout="wide"
    )
    
    st.title("📈 Stock Backtesting Bot")
    st.markdown("Trend following strategy using moving averages")
    
    # Sidebar for inputs
    st.sidebar.header("Backtest Parameters")
    
    # Market selection
    market = st.sidebar.selectbox(
        "Market",
        options=["US", "KRX"],
        index=0,
        help="Select market: US (NASDAQ/NYSE) or KRX (Korean stocks)"
    )
    
    # Ticker input with market-specific help
    if market == "KRX":
        ticker_help = "Enter Korean stock code (e.g., 005930 for Samsung, 035420 for NAVER)"
        default_ticker = "005930"
    else:
        ticker_help = "Enter US stock symbol (e.g., AAPL, TSLA)"
        default_ticker = "AAPL"
    
    ticker = st.sidebar.text_input("Stock Ticker", value=default_ticker, help=ticker_help)
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=date(2010, 1, 1))
    with col2:
        end_date = st.date_input("End Date", value=date(2023, 12, 31))
    
    st.sidebar.subheader("Moving Average Parameters")
    short_ma = st.sidebar.number_input("Short MA Period", min_value=5, max_value=200, value=50)
    long_ma = st.sidebar.number_input("Long MA Period", min_value=10, max_value=500, value=200)
    
    st.sidebar.subheader("Trading Parameters")
    cash = st.sidebar.number_input("Initial Cash ($)", min_value=1000, value=10000)
    commission = st.sidebar.slider("Commission (%)", min_value=0.0, max_value=1.0, value=0.2, step=0.1) / 100
    
    run_button = st.sidebar.button("🚀 Run Backtest", type="primary")
    
    # Main content area
    if run_button:
        if short_ma >= long_ma:
            st.error("Short MA period must be less than Long MA period!")
            return
            
        # Get market info and validate ticker
        market_info = DataProvider.get_market_info(ticker)
        normalized_ticker = market_info['normalized_ticker']
        
        # Display market info
        with st.sidebar:
            st.markdown("---")
            st.markdown("### 📊 Market Info")
            st.write(f"**Ticker:** {normalized_ticker}")
            st.write(f"**Market:** {market_info['market']}")
            st.write(f"**Exchange:** {market_info['exchange']}")
            st.write(f"**Currency:** {market_info['currency']}")
            if 'korean_name' in market_info:
                st.write(f"**Korean Name:** {market_info['korean_name']}")
        
        with st.spinner(f"Downloading {normalized_ticker} data and running backtest..."):
            try:
                # Download data using DataProvider
                data = DataProvider.download_data(ticker, start=start_date, end=end_date, market=market, progress=False)
                
                if data is None or data.empty:
                    st.error(f"No data downloaded for {normalized_ticker}. Please check the ticker symbol and dates.")
                    return
                
                # Set strategy parameters
                TrendFollowing.short_ma = int(short_ma)
                TrendFollowing.long_ma = int(long_ma)
                
                # Run backtest
                bt = Backtest(data, TrendFollowing, cash=cash, commission=commission)
                stats = bt.run()
                trades = stats["_trades"] if "_trades" in stats else None
                
                # Display results
                st.success(f"Backtest completed successfully for {normalized_ticker}!")
                
                # Add monitoring button
                col_monitor, _ = st.columns([2, 3])
                with col_monitor:
                    if st.button("📈 Apply for Monitoring", type="secondary"):
                        # Store monitoring configuration
                        monitoring_config = {
                            'ticker': normalized_ticker,
                            'market': market_info['market'],
                            'strategy': 'TrendFollowing',
                            'parameters': {
                                'short_ma': int(short_ma),
                                'long_ma': int(long_ma)
                            },
                            'added_date': datetime.now().isoformat(),
                            'status': 'active',
                            'cash': cash,
                            'commission': commission
                        }
                        
                        # Save to session state (in production, save to persistent storage)
                        if 'monitoring_list' not in st.session_state:
                            st.session_state.monitoring_list = []
                        
                        # Check if already exists
                        existing = next((item for item in st.session_state.monitoring_list 
                                       if item['ticker'] == normalized_ticker and item['strategy'] == 'TrendFollowing'), None)
                        
                        if existing:
                            st.warning(f"⚠️ {normalized_ticker} is already being monitored with TrendFollowing strategy")
                        else:
                            st.session_state.monitoring_list.append(monitoring_config)
                            st.success(f"✅ {normalized_ticker} added to monitoring list!")
                
                # Key metrics in columns
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Return", f"{stats['Return [%]']:.2f}%")
                    st.metric("CAGR", f"{stats['CAGR [%]']:.2f}%")
                
                with col2:
                    st.metric("Win Rate", f"{stats['Win Rate [%]']:.2f}%")
                    st.metric("# Trades", f"{stats['# Trades']}")
                
                with col3:
                    st.metric("Sharpe Ratio", f"{stats['Sharpe Ratio']:.2f}")
                    st.metric("Max Drawdown", f"{stats['Max. Drawdown [%]']:.2f}%")
                
                with col4:
                    st.metric("Buy & Hold Return", f"{stats['Buy & Hold Return [%]']:.2f}%")
                    st.metric("Profit Factor", f"{stats['Profit Factor']:.2f}")
                
                # Charts section
                st.header("📊 Analysis")
                
                chart_col1, chart_col2 = st.columns(2)
                
                with chart_col1:
                    # Price chart with moving averages
                    st.subheader("Price & Moving Averages")
                    chart_data = data['Close'].tail(252)  # Last year
                    ma_short_data = chart_data.rolling(int(short_ma)).mean()
                    ma_long_data = chart_data.rolling(int(long_ma)).mean()
                    
                    chart_df = pd.DataFrame({
                        'Price': chart_data,
                        f'MA{int(short_ma)}': ma_short_data,
                        f'MA{int(long_ma)}': ma_long_data
                    })
                    st.line_chart(chart_df)
                
                with chart_col2:
                    # Returns distribution
                    st.subheader("Trade Returns Distribution")
                    fig = create_returns_chart(trades)
                    if fig:
                        st.pyplot(fig)
                        plt.close(fig)
                    else:
                        st.info("No trades to display")
                
                # Detailed statistics
                st.header("📋 Detailed Results")
                
                # Strategy comparison
                comparison_data = {
                    "Metric": ["Return", "Volatility", "Sharpe Ratio", "Max Drawdown"],
                    "Strategy": [
                        f"{stats['Return [%]']:.2f}%",
                        f"{stats['Volatility (Ann.) [%]']:.2f}%",
                        f"{stats['Sharpe Ratio']:.2f}",
                        f"{stats['Max. Drawdown [%]']:.2f}%"
                    ],
                    "Buy & Hold": [
                        f"{stats['Buy & Hold Return [%]']:.2f}%",
                        "N/A",
                        "N/A",
                        "N/A"
                    ]
                }
                
                st.table(pd.DataFrame(comparison_data))
                
                # Download section
                st.header("💾 Export Results")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("📄 Download Detailed Stats"):
                        stats_str = str(stats)
                        st.download_button(
                            label="Download Stats as TXT",
                            data=stats_str,
                            file_name=f"{ticker}_backtest_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                            mime="text/plain"
                        )
                
                with col2:
                    if trades is not None and not trades.empty:
                        if st.button("📊 Download Trade Data"):
                            csv = trades.to_csv(index=False)
                            st.download_button(
                                label="Download Trades as CSV",
                                data=csv,
                                file_name=f"{ticker}_trades_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                mime="text/csv"
                            )
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
    
    # Information sidebar
    with st.sidebar:
        st.markdown("---")
        st.markdown("### ℹ️ About")
        st.markdown("""
        This backtesting bot uses a simple trend-following strategy:
        - **Buy Signal**: Short MA crosses above Long MA
        - **Sell Signal**: Long MA crosses above Short MA
        - **Default**: 50-day & 200-day moving averages
        """)
        
        st.markdown("### 📚 Tips")
        st.markdown("""
        - Lower commission rates favor more frequent trading
        - Longer MA periods reduce trade frequency
        - Compare strategy returns with Buy & Hold
        - Consider transaction costs in real trading
        """)


if __name__ == "__main__":
    main()