import streamlit as st
import os
import sys
from datetime import datetime

# 프로젝트 루트 경로 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from live_trading.live_trading_bot import create_alert_systems
from utils.monitoring_storage import MonitoringStorage

def main():
    st.set_page_config(
        page_title="Settings - Backtest Bot",
        page_icon="⚙️",
        layout="wide"
    )
    
    st.title("⚙️ Settings & Configuration")
    st.markdown("Configure your backtesting and monitoring preferences")
    
    # 탭으로 구분
    tab1, tab2, tab3, tab4 = st.tabs(["🔔 Alerts", "📊 Monitoring", "🔧 System", "ℹ️ Info"])
    
    with tab1:
        st.header("🔔 Alert Configuration")
        st.markdown("Set up email and Telegram notifications for trading signals")
        
        # 이메일 설정
        st.subheader("📧 Email Alerts")
        with st.expander("Email Configuration", expanded=True):
            st.markdown("""
            **To set up email alerts:**
            1. Create a `.env` file in the project root
            2. Add your Gmail app password (not your regular password)
            3. Configure the following variables:
            """)
            
            st.code("""
# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
            """)
            
            st.info("📘 **Gmail App Password Setup**: Go to Google Account Settings > Security > 2-Step Verification > App passwords")
        
        # 텔레그램 설정
        st.subheader("📱 Telegram Alerts")
        with st.expander("Telegram Configuration", expanded=True):
            st.markdown("""
            **To set up Telegram alerts:**
            1. Create a bot using @BotFather on Telegram
            2. Get your chat ID by messaging your bot
            3. Add to your `.env` file:
            """)
            
            st.code("""
# Telegram Configuration  
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
            """)
            
            st.info("📘 **Get Chat ID**: Send `/start` to your bot, then visit `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`")
        
        # 알림 테스트
        st.subheader("🧪 Test Alerts")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📧 Test Email Alert", type="secondary"):
                try:
                    alert_systems = create_alert_systems()
                    email_alerts = [a for a in alert_systems if type(a).__name__ == 'EmailAlert']
                    
                    if email_alerts:
                        test_signals = {
                            'TrendFollowing': {
                                'action': 'BUY',
                                'price': 150.00,
                                'timestamp': datetime.now(),
                                'confidence': 0.85
                            }
                        }
                        email_alerts[0].send_signal_alert('TEST', test_signals)
                        st.success("✅ Email test sent successfully!")
                    else:
                        st.error("❌ Email not configured. Check your .env file.")
                        
                except Exception as e:
                    st.error(f"❌ Email test failed: {e}")
        
        with col2:
            if st.button("📱 Test Telegram Alert", type="secondary"):
                try:
                    alert_systems = create_alert_systems()
                    telegram_alerts = [a for a in alert_systems if type(a).__name__ == 'TelegramBot']
                    
                    if telegram_alerts:
                        test_signals = {
                            'TrendFollowing': {
                                'action': 'BUY', 
                                'price': 150.00,
                                'timestamp': datetime.now(),
                                'confidence': 0.85
                            }
                        }
                        telegram_alerts[0].send_signal_alert('TEST', test_signals)
                        st.success("✅ Telegram test sent successfully!")
                    else:
                        st.error("❌ Telegram not configured. Check your .env file.")
                        
                except Exception as e:
                    st.error(f"❌ Telegram test failed: {e}")
    
    with tab2:
        st.header("📊 Monitoring Settings")
        
        # 모니터링 통계
        try:
            storage = MonitoringStorage()
            stats = storage.get_monitoring_stats()
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Configs", stats['total'])
            with col2:
                st.metric("Active", stats['active'])
            with col3:
                st.metric("Paused", stats['paused'])
            with col4:
                st.metric("Errors", stats['error'])
            
            # 모니터링 설정
            st.subheader("🔧 Monitoring Configuration")
            
            col_set1, col_set2 = st.columns(2)
            
            with col_set1:
                update_interval = st.slider(
                    "Update Interval (seconds)",
                    min_value=60,
                    max_value=1800,
                    value=300,
                    step=60,
                    help="How often to check for new signals"
                )
            
            with col_set2:
                max_configs = st.number_input(
                    "Max Monitoring Configs",
                    min_value=1,
                    max_value=100,
                    value=20,
                    help="Maximum number of monitoring configurations"
                )
            
            # 데이터베이스 관리
            st.subheader("🗄️ Database Management")
            
            col_db1, col_db2, col_db3 = st.columns(3)
            
            with col_db1:
                if st.button("🧹 Clean Stopped Configs"):
                    removed_count = storage.cleanup_stopped_configs()
                    if removed_count > 0:
                        st.success(f"✅ Removed {removed_count} stopped configurations")
                    else:
                        st.info("ℹ️ No stopped configurations to clean")
            
            with col_db2:
                if st.button("⏸️ Pause All Active"):
                    updated_count = storage.bulk_update_status('active', 'paused')
                    if updated_count > 0:
                        st.success(f"✅ Paused {updated_count} active configurations")
                    else:
                        st.info("ℹ️ No active configurations to pause")
            
            with col_db3:
                if st.button("▶️ Resume All Paused"):
                    updated_count = storage.bulk_update_status('paused', 'active')
                    if updated_count > 0:
                        st.success(f"✅ Resumed {updated_count} paused configurations")
                    else:
                        st.info("ℹ️ No paused configurations to resume")
        
        except Exception as e:
            st.error(f"Error loading monitoring settings: {e}")
    
    with tab3:
        st.header("🔧 System Information")
        
        # 파일 경로 정보
        st.subheader("📁 File Paths")
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        paths_info = {
            "Project Root": project_root,
            "Monitoring Data": os.path.join(project_root, "monitoring_data.json"),
            "Trading Logs": os.path.join(project_root, "trading_bot.log"),
            "Environment File": os.path.join(project_root, ".env")
        }
        
        for name, path in paths_info.items():
            exists = "✅" if os.path.exists(path) else "❌"
            st.write(f"**{name}**: {exists} `{path}`")
        
        # 시스템 상태
        st.subheader("💻 System Status")
        
        # Python 버전 및 패키지 확인
        import platform
        import pkg_resources
        
        system_info = {
            "Python Version": platform.python_version(),
            "Platform": platform.platform(),
            "Architecture": platform.architecture()[0]
        }
        
        for key, value in system_info.items():
            st.write(f"**{key}**: {value}")
        
        # 중요 패키지 버전
        st.subheader("📦 Package Versions")
        important_packages = ['streamlit', 'yfinance', 'pandas', 'matplotlib']
        
        for package in important_packages:
            try:
                version = pkg_resources.get_distribution(package).version
                st.write(f"**{package}**: {version}")
            except:
                st.write(f"**{package}**: Not installed")
    
    with tab4:
        st.header("ℹ️ About Backtest Bot v1")
        
        st.markdown("""
        ### 🎯 Enhanced Multi-Strategy Backtesting Platform
        
        This application provides comprehensive backtesting and real-time monitoring capabilities for multiple trading strategies across different markets.
        
        #### 🚀 Key Features:
        - **Multi-Strategy Support**: 10+ built-in trading strategies
        - **Multi-Market Coverage**: US (NASDAQ/NYSE) and Korean (KRX) markets  
        - **Real-Time Monitoring**: Live signal detection with alerts
        - **Multi-Language Interface**: English and Korean support
        - **Advanced Analytics**: Detailed performance metrics and visualizations
        
        #### 📊 Supported Markets:
        - **US Markets**: NASDAQ, NYSE (stocks like AAPL, GOOGL, TSLA)
        - **Korean Markets**: KRX, KOSPI, KOSDAQ (stocks like 005930, 035420)
        
        #### 🔔 Alert Systems:
        - **Email Notifications**: Gmail SMTP integration
        - **Telegram Alerts**: Real-time messaging through Telegram bots
        
        #### 🛠️ Technical Stack:
        - **Frontend**: Streamlit for interactive web interface
        - **Data**: yfinance for market data retrieval  
        - **Backtesting**: Custom backtesting engine with multiple strategies
        - **Storage**: JSON-based configuration persistence
        - **Notifications**: Email (SMTP) and Telegram integration
        
        #### 📝 Version Information:
        - **Version**: 1.0 Enhanced
        - **Last Updated**: 2025-08-10
        - **Features**: KRX Support + Real-time Monitoring + Multi-language
        
        ---
        
        ### 🎯 How to Use:
        1. **Backtesting**: Configure strategies and run historical analysis
        2. **Monitoring**: Add successful strategies to real-time monitoring  
        3. **Alerts**: Set up email/Telegram for signal notifications
        4. **Analysis**: Review performance metrics and optimize parameters
        
        ### 🔧 Support:
        For technical support or feature requests, please check the project documentation or contact the development team.
        """)
        
        # 프로젝트 구조 표시
        with st.expander("📁 Project Structure"):
            st.code("""
backtest-bot-v1/
├── main_app.py                 # Main application entry point
├── pages/
│   ├── 1_📊_Backtesting.py    # Multi-strategy backtesting
│   ├── 2_📈_Monitoring_Dashboard.py  # Real-time monitoring management
│   └── 3_⚙️_Settings.py       # Configuration and settings
├── strategies/                 # Trading strategy implementations
├── utils/                      # Utility modules
│   ├── data_provider.py       # Multi-market data handling
│   └── monitoring_storage.py   # Persistent storage management
├── live_trading/              # Real-time monitoring system
└── config/                    # Configuration management
            """)

if __name__ == "__main__":
    main()