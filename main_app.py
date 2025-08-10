import streamlit as st
import os
import sys

# 프로젝트 루트 경로 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    st.set_page_config(
        page_title="Backtest Bot v1",
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 메인 페이지 콘텐츠
    st.title("🎯 Enhanced Backtest Bot v1")
    st.markdown("### Welcome to the Multi-Strategy Backtesting & Monitoring Platform")
    
    st.markdown("""
    ## 🚀 Features / 기능
    
    ### 📊 Multi-Strategy Backtesting / 다중 전략 백테스팅
    - **10+ Trading Strategies**: Trend Following, RSI, MACD, Bollinger Bands, and more
    - **Multi-Market Support**: US (NASDAQ/NYSE) and Korean (KRX/KOSPI/KOSDAQ) markets
    - **Parameter Optimization**: Fine-tune strategy parameters for better performance
    - **Multi-Language Support**: English and Korean interface
    
    ### 📈 Real-Time Monitoring / 실시간 모니터링
    - **Live Signal Detection**: Monitor your strategies in real-time
    - **Alert Systems**: Email and Telegram notifications
    - **Portfolio Management**: Track multiple tickers and strategies
    - **Status Monitoring**: Active, paused, and error state management
    
    ### 🌏 Market Coverage / 시장 지원
    - **US Markets**: NASDAQ, NYSE with US stock symbols
    - **Korean Markets**: KRX, KOSPI, KOSDAQ with Korean stock codes
    - **Auto-Detection**: Automatic market detection based on ticker format
    - **Currency Support**: USD for US stocks, KRW for Korean stocks
    
    ---
    
    ## 🔧 How to Get Started / 시작하기
    
    1. **📊 Backtesting**: Use the sidebar to navigate to "Backtesting" page
       - Choose your market (US or KRX)
       - Select a trading strategy
       - Configure parameters and run backtest
       - Add successful strategies to monitoring
    
    2. **📈 Monitoring**: Access the "Monitoring Dashboard" page
       - View all active monitoring configurations
       - Pause, resume, or remove strategies
       - Check real-time status updates
    
    3. **⚙️ Configuration**: Set up email and Telegram alerts
       - Configure your notification preferences
       - Test alert systems
    
    ---
    
    ## 📚 Supported Strategies / 지원 전략
    
    - **Trend Following**: Moving average crossover strategies
    - **RSI Strategy**: Relative Strength Index based signals  
    - **MACD Strategy**: Moving Average Convergence Divergence
    - **Bollinger Bands**: Volatility-based mean reversion
    - **Breakout Strategy**: Price breakout detection
    - **Golden Cross**: Classic 50/200 day MA crossover
    - **And more**: Additional momentum and mean-reversion strategies
    
    ---
    
    ### 🎯 Navigate using the sidebar to start backtesting and monitoring!
    """)
    
    # 사이드바에 네비게이션 안내
    with st.sidebar:
        st.markdown("## 🧭 Navigation / 탐색")
        st.markdown("""
        **Pages / 페이지:**
        - 📊 **Backtesting**: Run strategy backtests
        - 📈 **Monitoring Dashboard**: Manage live monitoring
        - ⚙️ **Settings**: Configure alerts and preferences
        
        **Quick Start / 빠른 시작:**
        1. Go to Backtesting page
        2. Select market and strategy  
        3. Run backtest
        4. Add to monitoring
        5. Check Monitoring Dashboard
        """)
        
        # 현재 모니터링 상태 표시
        try:
            from utils.monitoring_storage import MonitoringStorage
            storage = MonitoringStorage()
            stats = storage.get_monitoring_stats()
            
            if stats['total'] > 0:
                st.markdown("---")
                st.markdown("### 📊 Current Status")
                st.metric("Active Monitoring", stats['active'])
                st.metric("Total Configurations", stats['total'])
        except:
            pass

if __name__ == "__main__":
    main()