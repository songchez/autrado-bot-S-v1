import streamlit as st
import yfinance as yf
from backtesting import Backtest
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from datetime import datetime, date
import sys
import os

# 상위 디렉토리의 strategies 모듈을 import하기 위해 경로 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies import ALL_STRATEGIES as STRATEGIES
from utils.data_provider import DataProvider
from utils.monitoring_storage import MonitoringStorage


# 언어별 텍스트 정의 (기본 + 전략 관련)
LANGUAGES = {
    "English": {
        "page_title": "Multi-Strategy Backtesting Bot",
        "page_icon": "🎯",
        "title": "🎯 Multi-Strategy Backtesting Bot",
        "subtitle": "Choose from multiple trading strategies and optimize parameters",
        "sidebar_header": "Backtest Configuration",
        "strategy_selection": "Strategy Selection",
        "strategy_label": "Trading Strategy",
        "strategy_help": "Choose a trading strategy for backtesting",
        "strategy_description": "Strategy Description",
        "parameters_header": "Strategy Parameters",
        "ticker_label": "Stock Ticker",
        "ticker_help": "Enter stock symbol (e.g., AAPL, TSLA)",
        "start_date": "Start Date",
        "end_date": "End Date",
        "trading_header": "Trading Parameters",
        "initial_cash": "Initial Cash ($)",
        "commission": "Commission (%)",
        "run_button": "🚀 Run Backtest",
        "downloading": "Downloading {} data and running backtest with {}...",
        "no_data": "No data downloaded. Please check the ticker symbol and dates.",
        "success": "Backtest completed successfully!",
        "total_return": "Total Return",
        "cagr": "CAGR",
        "win_rate": "Win Rate",
        "num_trades": "# Trades",
        "sharpe_ratio": "Sharpe Ratio",
        "max_drawdown": "Max Drawdown",
        "buy_hold_return": "Buy & Hold Return",
        "profit_factor": "Profit Factor",
        "analysis": "📊 Analysis",
        "price_chart": "Price Chart with Indicators",
        "returns_dist": "Trade Returns Distribution",
        "no_trades": "No trades to display",
        "detailed_results": "📋 Detailed Results",
        "metric": "Metric",
        "strategy": "Strategy",
        "buy_hold": "Buy & Hold",
        "return": "Return",
        "volatility": "Volatility",
        "export": "💾 Export Results",
        "download_stats": "📄 Download Detailed Stats",
        "download_stats_btn": "Download Stats as TXT",
        "download_trades": "📊 Download Trade Data",
        "download_trades_btn": "Download Trades as CSV",
        "error": "An error occurred: {}",
        "about": "ℹ️ About Strategies",
        "tips": "📚 Strategy Tips",
        "tips_text": """
- **Trend Following**: Works best in trending markets
- **RSI**: Good for range-bound, volatile markets  
- **MACD**: Effective for medium-term trend changes
- **Bollinger Bands**: Ideal for mean-reverting assets
- **Breakout**: Suitable for momentum-driven moves
        """,
        "language": "Language",
        "strategy_comparison": "Strategy Comparison",
        "backtest_summary": "Backtest Summary",
        "total_trades": "Total Trades",
        "avg_trade": "Avg. Trade",
        "best_trade": "Best Trade",
        "worst_trade": "Worst Trade"
    },
    "한국어": {
        "page_title": "다중전략 백테스팅 봇",
        "page_icon": "🎯",
        "title": "🎯 다중전략 백테스팅 봇",
        "subtitle": "다양한 거래 전략 중 선택하고 매개변수를 최적화하세요",
        "sidebar_header": "백테스트 설정",
        "strategy_selection": "전략 선택",
        "strategy_label": "거래 전략",
        "strategy_help": "백테스팅할 거래 전략을 선택하세요",
        "strategy_description": "전략 설명",
        "parameters_header": "전략 매개변수",
        "ticker_label": "주식 티커",
        "ticker_help": "주식 심볼을 입력하세요 (예: AAPL, TSLA)",
        "start_date": "시작일",
        "end_date": "종료일",
        "trading_header": "거래 매개변수",
        "initial_cash": "초기 자본 ($)",
        "commission": "수수료 (%)",
        "run_button": "🚀 백테스트 실행",
        "downloading": "{} 데이터 다운로드 및 {} 전략으로 백테스트 실행 중...",
        "no_data": "데이터를 다운로드할 수 없습니다. 티커 심볼과 날짜를 확인해주세요.",
        "success": "백테스트가 성공적으로 완료되었습니다!",
        "total_return": "총 수익률",
        "cagr": "연평균성장률",
        "win_rate": "승률",
        "num_trades": "거래 횟수",
        "sharpe_ratio": "샤프 비율",
        "max_drawdown": "최대 손실",
        "buy_hold_return": "매수 후 보유 수익률",
        "profit_factor": "수익 요인",
        "analysis": "📊 분석",
        "price_chart": "가격 차트 및 지표",
        "returns_dist": "거래 수익률 분포",
        "no_trades": "표시할 거래가 없습니다",
        "detailed_results": "📋 상세 결과",
        "metric": "지표",
        "strategy": "전략",
        "buy_hold": "매수 후 보유",
        "return": "수익률",
        "volatility": "변동성",
        "export": "💾 결과 내보내기",
        "download_stats": "📄 상세 통계 다운로드",
        "download_stats_btn": "통계를 TXT로 다운로드",
        "download_trades": "📊 거래 데이터 다운로드",
        "download_trades_btn": "거래를 CSV로 다운로드",
        "error": "오류가 발생했습니다: {}",
        "about": "ℹ️ 전략 정보",
        "tips": "📚 전략 팁",
        "tips_text": """
- **추세 추종**: 추세가 명확한 시장에서 효과적
- **RSI**: 변동성이 큰 횡보장에서 유효
- **MACD**: 중기 추세 변화 포착에 효과적
- **볼린저 밴드**: 평균회귀 성향 자산에 이상적
- **돌파**: 모멘텀 중심 움직임에 적합
        """,
        "language": "언어",
        "strategy_comparison": "전략 비교",
        "backtest_summary": "백테스트 요약",
        "total_trades": "총 거래",
        "avg_trade": "평균 거래",
        "best_trade": "최고 거래",
        "worst_trade": "최악 거래"
    }
}


def set_korean_font():
    """한국어 폰트 설정"""
    try:
        korean_fonts = ['AppleGothic', 'Apple SD Gothic Neo', 'Malgun Gothic', 'NanumGothic']
        for font in korean_fonts:
            try:
                plt.rcParams['font.family'] = font
                return
            except:
                continue
        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['axes.unicode_minus'] = False
    except:
        pass


def create_returns_chart(trades, lang_dict):
    """수익률 분포 차트 생성"""
    if trades is not None and not trades.empty:
        set_korean_font()
        returns = trades["ReturnPct"] * 100
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.hist(returns, bins=20, edgecolor="black", alpha=0.7, color='steelblue')
        ax.set_title(lang_dict["returns_dist"], fontsize=16, fontweight='bold')
        ax.set_xlabel(f"{lang_dict['return']} (%)", fontsize=12)
        ax.set_ylabel("빈도" if "한국어" in str(lang_dict) else "Frequency", fontsize=12)
        ax.grid(True, alpha=0.3)
        return fig
    return None


def create_price_chart(data, strategy_name, params, lang_dict):
    """가격 차트와 지표 표시"""
    set_korean_font()
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # 가격 데이터 플롯
    ax.plot(data.index, data.Close, label='가격' if "한국어" in str(lang_dict) else 'Price', 
            color='black', linewidth=1)
    
    # 전략별 지표 추가
    if strategy_name in ["TrendFollowing", "GoldenCrossStrategy", "DualMovingAverageStrategy"]:
        short_ma = params.get('short_ma', params.get('fast_ma', 10))
        long_ma = params.get('long_ma', params.get('slow_ma', 30))
        
        ma_short = data.Close.rolling(short_ma).mean()
        ma_long = data.Close.rolling(long_ma).mean()
        
        ax.plot(data.index, ma_short, label=f'MA{short_ma}', alpha=0.7)
        ax.plot(data.index, ma_long, label=f'MA{long_ma}', alpha=0.7)
        
    elif strategy_name == "TripleMovingAverageStrategy":
        short_ma = params.get('short_ma', 5)
        medium_ma = params.get('medium_ma', 15)
        long_ma = params.get('long_ma', 30)
        
        ma_short = data.Close.rolling(short_ma).mean()
        ma_medium = data.Close.rolling(medium_ma).mean()
        ma_long = data.Close.rolling(long_ma).mean()
        
        ax.plot(data.index, ma_short, label=f'MA{short_ma}', alpha=0.7)
        ax.plot(data.index, ma_medium, label=f'MA{medium_ma}', alpha=0.7)
        ax.plot(data.index, ma_long, label=f'MA{long_ma}', alpha=0.7)
        
    elif strategy_name == "BollingerBandsStrategy":
        period = params.get('period', 20)
        std_mult = params.get('std_mult', 2)
        
        sma = data.Close.rolling(period).mean()
        std = data.Close.rolling(period).std()
        upper = sma + (std * std_mult)
        lower = sma - (std * std_mult)
        
        ax.plot(data.index, sma, label=f'SMA{period}', color='orange')
        ax.plot(data.index, upper, label='Upper Band', color='red', alpha=0.5)
        ax.plot(data.index, lower, label='Lower Band', color='green', alpha=0.5)
        ax.fill_between(data.index, lower, upper, alpha=0.1)
    
    ax.set_title(lang_dict["price_chart"], fontsize=16, fontweight='bold')
    ax.set_xlabel('날짜' if "한국어" in str(lang_dict) else 'Date', fontsize=12)
    ax.set_ylabel('가격' if "한국어" in str(lang_dict) else 'Price', fontsize=12)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    return fig


def get_language_dict(language):
    """선택된 언어의 딕셔너리 반환"""
    return LANGUAGES.get(language, LANGUAGES["English"])


def render_strategy_parameters(strategy_key, lang_dict, language):
    """전략별 매개변수 입력 UI 렌더링"""
    strategy_info = STRATEGIES[strategy_key]
    params = {}
    
    st.subheader(lang_dict["parameters_header"])
    
    for param_key, param_info in strategy_info["params"].items():
        param_name = param_info["name"][language]
        
        if isinstance(param_info["default"], float):
            value = st.slider(
                param_name,
                min_value=param_info["min"],
                max_value=param_info["max"],
                value=param_info["default"],
                step=0.1 if param_info["max"] <= 10 else 0.01
            )
        else:
            value = st.number_input(
                param_name,
                min_value=param_info["min"],
                max_value=param_info["max"],
                value=param_info["default"]
            )
        
        params[param_key] = value
    
    return params


def main():
    # 세션 상태 초기화
    if 'language' not in st.session_state:
        st.session_state.language = 'English'
    
    # 언어 선택
    with st.sidebar:
        language = st.selectbox(
            "🌐 Language / 언어",
            options=list(LANGUAGES.keys()),
            index=list(LANGUAGES.keys()).index(st.session_state.language)
        )
        st.session_state.language = language
    
    # 언어 딕셔너리 가져오기
    lang = get_language_dict(language)
    
    st.set_page_config(
        page_title=lang["page_title"],
        page_icon=lang["page_icon"],
        layout="wide"
    )
    
    st.title(lang["title"])
    st.markdown(lang["subtitle"])
    
    # 사이드바 설정
    st.sidebar.header(lang["sidebar_header"])
    
    # 전략 선택
    st.sidebar.subheader(lang["strategy_selection"])
    
    strategy_options = {STRATEGIES[k]["name"][language]: k for k in STRATEGIES.keys()}
    selected_strategy_name = st.sidebar.selectbox(
        lang["strategy_label"],
        options=list(strategy_options.keys()),
        help=lang["strategy_help"]
    )
    
    selected_strategy_key = strategy_options[selected_strategy_name]
    strategy_info = STRATEGIES[selected_strategy_key]
    
    # 전략 설명 표시
    with st.sidebar.expander(lang["strategy_description"]):
        st.write(strategy_info["description"][language])
    
    # 전략 매개변수
    strategy_params = render_strategy_parameters(selected_strategy_key, lang, language)
    
    # 기본 설정
    st.sidebar.markdown("---")
    
    # 시장 선택 추가
    market = st.sidebar.selectbox(
        "🌍 Market / 시장" if language == "한국어" else "🌍 Market",
        options=["US", "KRX"],
        index=0,
        help="Select market: US (NASDAQ/NYSE) or KRX (Korean stocks)" if language == "English" else "시장 선택: 미국 (NASDAQ/NYSE) 또는 한국 (KRX)"
    )
    
    # 시장별 기본값과 도움말 설정
    if market == "KRX":
        default_ticker = "005930"  # 삼성전자
        ticker_help_en = "Enter Korean stock code (e.g., 005930 for Samsung, 035420 for NAVER)"
        ticker_help_ko = "한국 주식 코드를 입력하세요 (예: 005930 삼성전자, 035420 네이버)"
    else:
        default_ticker = "AAPL"
        ticker_help_en = "Enter US stock symbol (e.g., AAPL, TSLA)"
        ticker_help_ko = "미국 주식 심볼을 입력하세요 (예: AAPL, TSLA)"
    
    ticker_help = ticker_help_ko if language == "한국어" else ticker_help_en
    ticker = st.sidebar.text_input(lang["ticker_label"], value=default_ticker, help=ticker_help)
    
    # 인터벌 선택 추가
    st.sidebar.subheader("🕐 Time Interval / 시간 인터벌" if language == "한국어" else "🕐 Time Interval")
    
    interval_options = {
        "1d": "1 Day / 1일" if language == "한국어" else "1 Day",
        "1h": "1 Hour / 1시간" if language == "한국어" else "1 Hour", 
        "4h": "4 Hours / 4시간" if language == "한국어" else "4 Hours",
        "15m": "15 Minutes / 15분" if language == "한국어" else "15 Minutes",
        "5m": "5 Minutes / 5분" if language == "한국어" else "5 Minutes"
    }
    
    selected_interval_display = st.sidebar.selectbox(
        "Select Interval" if language == "English" else "인터벌 선택",
        options=list(interval_options.values()),
        index=0,
        help="Choose time interval for backtesting. Shorter intervals provide more trading opportunities." if language == "English" else "백테스트 시간 인터벌을 선택하세요. 짧은 인터벌은 더 많은 거래 기회를 제공합니다."
    )
    
    # Get actual interval code
    interval = [k for k, v in interval_options.items() if v == selected_interval_display][0]
    
    # 날짜 범위 조정 (인터벌에 따라)
    if interval in ['5m', '15m', '1h']:
        # 단기 인터벌은 최근 30일만 지원
        from datetime import timedelta
        default_start = date.today() - timedelta(days=30)
        default_end = date.today() - timedelta(days=1)
        date_help = "Short intervals: Max 30 days" if language == "English" else "단기 인터벌: 최대 30일"
    elif interval == '4h':
        # 4시간은 최근 90일
        from datetime import timedelta
        default_start = date.today() - timedelta(days=90)
        default_end = date.today() - timedelta(days=1)
        date_help = "4-hour interval: Max 90 days" if language == "English" else "4시간 인터벌: 최대 90일"
    else:
        # 일봉은 긴 기간 가능
        default_start = date(2020, 1, 1)
        default_end = date(2023, 12, 31)
        date_help = "Daily interval: Long periods available" if language == "English" else "일봉: 긴 기간 사용 가능"
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_date = st.date_input(lang["start_date"], value=default_start, help=date_help)
    with col2:
        end_date = st.date_input(lang["end_date"], value=default_end, help=date_help)
    
    st.sidebar.subheader(lang["trading_header"])
    cash = st.sidebar.number_input(lang["initial_cash"], min_value=1000, value=10000)
    commission = st.sidebar.slider(lang["commission"], min_value=0.0, max_value=1.0, value=0.2, step=0.1) / 100
    
    run_button = st.sidebar.button(lang["run_button"], type="primary")
    
    # 메인 콘텐츠
    if run_button:
        # 시장 정보 표시
        market_info = DataProvider.get_market_info(ticker)
        normalized_ticker = market_info['normalized_ticker']
        
        # 사이드바에 시장 정보 표시
        with st.sidebar:
            st.markdown("---")
            st.markdown("### 📊 Market Info / 시장 정보")
            st.write(f"**Ticker:** {normalized_ticker}")
            st.write(f"**Market:** {market_info['market']}")
            st.write(f"**Exchange:** {market_info['exchange']}")
            st.write(f"**Currency:** {market_info['currency']}")
            if 'korean_name' in market_info:
                st.write(f"**Korean Name:** {market_info['korean_name']}")
        
        with st.spinner(lang["downloading"].format(normalized_ticker, selected_strategy_name)):
            try:
                # DataProvider를 사용해서 데이터 다운로드 (인터벌 지원)
                data = DataProvider.download_data(
                    ticker, start=start_date, end=end_date, interval=interval, market=market, progress=False
                )
                
                if data is None or data.empty:
                    st.error(lang["no_data"])
                    return
                
                # 전략 클래스 가져오기 및 매개변수 설정
                strategy_class = strategy_info["class"]
                
                # 동적으로 전략 매개변수 설정
                for param_key, param_value in strategy_params.items():
                    setattr(strategy_class, param_key, param_value)
                
                # 백테스트 실행
                bt = Backtest(data, strategy_class, cash=cash, commission=commission)
                stats = bt.run()
                trades = stats["_trades"] if "_trades" in stats else None
                
                # 결과 표시 (인터벌 정보 포함)
                st.success(f"{lang['success']} (Interval: {selected_interval_display}, Total bars: {len(data)})")
                
                # 모니터링 추가 버튼
                col_monitor, col_spacer = st.columns([3, 2])
                with col_monitor:
                    monitor_btn_text = "📈 모니터링에 추가" if language == "한국어" else "📈 Add to Monitoring"
                    if st.button(monitor_btn_text, type="secondary"):
                        try:
                            # MonitoringStorage 사용해서 저장
                            storage = MonitoringStorage()
                            
                            monitoring_config = {
                                'ticker': normalized_ticker,
                                'market': market_info['market'],
                                'strategy': selected_strategy_key,
                                'parameters': strategy_params,
                                'added_date': datetime.now().isoformat(),
                                'status': 'active',
                                'cash': cash,
                                'commission': commission
                            }
                            
                            success = storage.add_monitoring_config(monitoring_config)
                            
                            if success:
                                success_msg = f"✅ {normalized_ticker}이(가) 모니터링 목록에 추가되었습니다!" if language == "한국어" else f"✅ {normalized_ticker} added to monitoring list!"
                                st.success(success_msg)
                            else:
                                warning_msg = f"⚠️ {normalized_ticker}은(는) 이미 {selected_strategy_key} 전략으로 모니터링 중입니다." if language == "한국어" else f"⚠️ {normalized_ticker} is already being monitored with {selected_strategy_key} strategy."
                                st.warning(warning_msg)
                                
                        except Exception as e:
                            error_msg = f"❌ 모니터링 추가 중 오류 발생: {e}" if language == "한국어" else f"❌ Error adding to monitoring: {e}"
                            st.error(error_msg)
                
                # 백테스트 요약 (인터벌 정보 포함)
                st.subheader(f"{lang['backtest_summary']} - {selected_interval_display}")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(lang["total_return"], f"{stats['Return [%]']:.2f}%")
                    st.metric(lang["win_rate"], f"{stats['Win Rate [%]']:.2f}%")
                
                with col2:
                    st.metric(lang["cagr"], f"{stats['CAGR [%]']:.2f}%")
                    st.metric(lang["num_trades"], f"{stats['# Trades']}")
                
                with col3:
                    st.metric(lang["sharpe_ratio"], f"{stats['Sharpe Ratio']:.2f}")
                    st.metric(lang["max_drawdown"], f"{stats['Max. Drawdown [%]']:.2f}%")
                
                with col4:
                    st.metric(lang["buy_hold_return"], f"{stats['Buy & Hold Return [%]']:.2f}%")
                    st.metric(lang["profit_factor"], f"{stats['Profit Factor']:.2f}")
                
                # 차트 분석
                st.header(lang["analysis"])
                
                chart_col1, chart_col2 = st.columns(2)
                
                with chart_col1:
                    # 가격 차트와 지표
                    st.subheader(f"{lang['price_chart']} ({selected_interval_display})")
                    
                    # 인터벌에 따라 차트 기간 조정
                    if interval in ['5m', '15m']:
                        chart_data = data.tail(288)  # 1일 치 데이터 (5분봉 기준)
                    elif interval == '1h':
                        chart_data = data.tail(168)  # 1주 치 데이터
                    elif interval == '4h':
                        chart_data = data.tail(180)  # 30일 치 데이터
                    else:
                        chart_data = data.tail(252)  # 1년 치 데이터 (일봉)
                    
                    price_fig = create_price_chart(chart_data, selected_strategy_key, strategy_params, lang)
                    st.pyplot(price_fig)
                    plt.close(price_fig)
                
                with chart_col2:
                    # 수익률 분포
                    st.subheader(lang["returns_dist"])
                    returns_fig = create_returns_chart(trades, lang)
                    if returns_fig:
                        st.pyplot(returns_fig)
                        plt.close(returns_fig)
                    else:
                        st.info(lang["no_trades"])
                
                # 상세 결과
                st.header(lang["detailed_results"])
                
                # 거래 통계
                if trades is not None and not trades.empty:
                    trade_col1, trade_col2, trade_col3, trade_col4 = st.columns(4)
                    
                    with trade_col1:
                        st.metric(lang["total_trades"], len(trades))
                    with trade_col2:
                        st.metric(lang["avg_trade"], f"{trades['ReturnPct'].mean() * 100:.2f}%")
                    with trade_col3:
                        st.metric(lang["best_trade"], f"{trades['ReturnPct'].max() * 100:.2f}%")
                    with trade_col4:
                        st.metric(lang["worst_trade"], f"{trades['ReturnPct'].min() * 100:.2f}%")
                
                # 전략 vs Buy & Hold 비교
                st.subheader(lang["strategy_comparison"])
                comparison_data = {
                    lang["metric"]: [lang["return"], lang["volatility"], lang["sharpe_ratio"], lang["max_drawdown"]],
                    lang["strategy"]: [
                        f"{stats['Return [%]']:.2f}%",
                        f"{stats['Volatility (Ann.) [%]']:.2f}%",
                        f"{stats['Sharpe Ratio']:.2f}",
                        f"{stats['Max. Drawdown [%]']:.2f}%"
                    ],
                    lang["buy_hold"]: [
                        f"{stats['Buy & Hold Return [%]']:.2f}%",
                        "N/A",
                        "N/A",
                        "N/A"
                    ]
                }
                st.table(pd.DataFrame(comparison_data))
                
                # 다운로드 섹션
                st.header(lang["export"])
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button(lang["download_stats"]):
                        stats_str = str(stats)
                        st.download_button(
                            label=lang["download_stats_btn"],
                            data=stats_str,
                            file_name=f"{ticker}_{selected_strategy_key}_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                            mime="text/plain"
                        )
                
                with col2:
                    if trades is not None and not trades.empty:
                        if st.button(lang["download_trades"]):
                            csv = trades.to_csv(index=False)
                            st.download_button(
                                label=lang["download_trades_btn"],
                                data=csv,
                                file_name=f"{ticker}_{selected_strategy_key}_trades_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                mime="text/csv"
                            )
                
            except Exception as e:
                st.error(lang["error"].format(str(e)))
                st.exception(e)  # 디버깅용
    
    # 정보 사이드바
    with st.sidebar:
        st.markdown("---")
        st.markdown(f"### {lang['about']}")
        
        # 사용 가능한 전략 목록
        st.markdown("**" + ("사용 가능한 전략:" if language == "한국어" else "Available Strategies:") + "**")
        for strategy_key in STRATEGIES.keys():
            st.markdown(f"• {STRATEGIES[strategy_key]['name'][language]}")
        
        st.markdown(f"### {lang['tips']}")
        st.markdown(lang["tips_text"])


if __name__ == "__main__":
    main()