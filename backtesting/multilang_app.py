import streamlit as st
import yfinance as yf
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from datetime import datetime, date
import sys
import os

# 상위 디렉토리의 strategies 모듈을 import하기 위해 경로 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies import TrendFollowing


# 언어별 텍스트 정의
LANGUAGES = {
    "English": {
        "page_title": "Stock Backtesting Bot",
        "page_icon": "📈",
        "title": "📈 Stock Backtesting Bot",
        "subtitle": "Trend following strategy using moving averages",
        "sidebar_header": "Backtest Parameters",
        "ticker_label": "Stock Ticker",
        "ticker_help": "Enter stock symbol (e.g., AAPL, TSLA)",
        "start_date": "Start Date",
        "end_date": "End Date",
        "ma_header": "Moving Average Parameters",
        "short_ma": "Short MA Period",
        "long_ma": "Long MA Period",
        "trading_header": "Trading Parameters",
        "initial_cash": "Initial Cash ($)",
        "commission": "Commission (%)",
        "run_button": "🚀 Run Backtest",
        "downloading": "Downloading {} data and running backtest...",
        "ma_error": "Short MA period must be less than Long MA period!",
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
        "price_ma": "Price & Moving Averages",
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
        "about": "ℹ️ About",
        "about_text": """
This backtesting bot uses a simple trend-following strategy:
- **Buy Signal**: Short MA crosses above Long MA
- **Sell Signal**: Long MA crosses above Short MA
- **Default**: 50-day & 200-day moving averages
        """,
        "tips": "📚 Tips",
        "tips_text": """
- Lower commission rates favor more frequent trading
- Longer MA periods reduce trade frequency
- Compare strategy returns with Buy & Hold
- Consider transaction costs in real trading
        """,
        "language": "Language"
    },
    "한국어": {
        "page_title": "주식 백테스팅 봇",
        "page_icon": "📈",
        "title": "📈 주식 백테스팅 봇",
        "subtitle": "이동평균을 이용한 추세 추종 전략",
        "sidebar_header": "백테스트 매개변수",
        "ticker_label": "주식 티커",
        "ticker_help": "주식 심볼을 입력하세요 (예: AAPL, TSLA)",
        "start_date": "시작일",
        "end_date": "종료일",
        "ma_header": "이동평균 매개변수",
        "short_ma": "단기 이동평균 기간",
        "long_ma": "장기 이동평균 기간",
        "trading_header": "거래 매개변수",
        "initial_cash": "초기 자본 ($)",
        "commission": "수수료 (%)",
        "run_button": "🚀 백테스트 실행",
        "downloading": "{} 데이터 다운로드 및 백테스트 실행 중...",
        "ma_error": "단기 이동평균 기간은 장기 이동평균 기간보다 작아야 합니다!",
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
        "price_ma": "가격 및 이동평균",
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
        "about": "ℹ️ 정보",
        "about_text": """
이 백테스팅 봇은 간단한 추세 추종 전략을 사용합니다:
- **매수 신호**: 단기 이동평균이 장기 이동평균을 상향 돌파
- **매도 신호**: 장기 이동평균이 단기 이동평균을 상향 돌파
- **기본값**: 50일 및 200일 이동평균
        """,
        "tips": "📚 팁",
        "tips_text": """
- 낮은 수수료율은 빈번한 거래에 유리합니다
- 긴 이동평균 기간은 거래 빈도를 줄입니다
- 전략 수익률을 매수 후 보유와 비교해보세요
- 실제 거래시 거래 비용을 고려하세요
        """,
        "language": "언어"
    }
}


class TrendFollowing(Strategy):
    short_ma = 50
    long_ma = 200

    def init(self):
        self.ma_short = self.I(lambda x: pd.Series(x).rolling(self.short_ma).mean(), self.data.Close)
        self.ma_long = self.I(lambda x: pd.Series(x).rolling(self.long_ma).mean(), self.data.Close)

    def next(self):
        if crossover(self.ma_short, self.ma_long):
            self.buy()
        elif crossover(self.ma_long, self.ma_short):
            self.sell()


def set_korean_font():
    """한국어 폰트 설정"""
    try:
        # macOS에서 사용 가능한 한국어 폰트들
        korean_fonts = ['AppleGothic', 'Apple SD Gothic Neo', 'Malgun Gothic', 'NanumGothic']
        
        for font in korean_fonts:
            try:
                plt.rcParams['font.family'] = font
                return
            except:
                continue
                
        # 폰트를 찾지 못한 경우 기본 설정
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


def get_language_dict(language):
    """선택된 언어의 딕셔너리 반환"""
    return LANGUAGES.get(language, LANGUAGES["English"])


def main():
    # 세션 상태 초기화
    if 'language' not in st.session_state:
        st.session_state.language = 'English'
    
    # 언어 선택 (사이드바 상단)
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
    
    # 사이드바 입력 필드
    st.sidebar.header(lang["sidebar_header"])
    
    ticker = st.sidebar.text_input(
        lang["ticker_label"], 
        value="AAPL", 
        help=lang["ticker_help"]
    )
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_date = st.date_input(lang["start_date"], value=date(2010, 1, 1))
    with col2:
        end_date = st.date_input(lang["end_date"], value=date(2023, 12, 31))
    
    st.sidebar.subheader(lang["ma_header"])
    short_ma = st.sidebar.number_input(lang["short_ma"], min_value=5, max_value=200, value=50)
    long_ma = st.sidebar.number_input(lang["long_ma"], min_value=10, max_value=500, value=200)
    
    st.sidebar.subheader(lang["trading_header"])
    cash = st.sidebar.number_input(lang["initial_cash"], min_value=1000, value=10000)
    commission = st.sidebar.slider(lang["commission"], min_value=0.0, max_value=1.0, value=0.2, step=0.1) / 100
    
    run_button = st.sidebar.button(lang["run_button"], type="primary")
    
    # 메인 콘텐츠
    if run_button:
        if short_ma >= long_ma:
            st.error(lang["ma_error"])
            return
            
        with st.spinner(lang["downloading"].format(ticker)):
            try:
                # 데이터 다운로드
                data = yf.download(ticker, start=start_date, end=end_date, progress=False)
                
                if data.empty:
                    st.error(lang["no_data"])
                    return
                
                # MultiIndex 컬럼 문제 수정
                if isinstance(data.columns, pd.MultiIndex):
                    data.columns = data.columns.droplevel(1)
                
                # 전략 매개변수 설정
                TrendFollowing.short_ma = int(short_ma)
                TrendFollowing.long_ma = int(long_ma)
                
                # 백테스트 실행
                bt = Backtest(data, TrendFollowing, cash=cash, commission=commission)
                stats = bt.run()
                trades = stats["_trades"] if "_trades" in stats else None
                
                # 결과 표시
                st.success(lang["success"])
                
                # 주요 지표 컬럼
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(lang["total_return"], f"{stats['Return [%]']:.2f}%")
                    st.metric(lang["cagr"], f"{stats['CAGR [%]']:.2f}%")
                
                with col2:
                    st.metric(lang["win_rate"], f"{stats['Win Rate [%]']:.2f}%")
                    st.metric(lang["num_trades"], f"{stats['# Trades']}")
                
                with col3:
                    st.metric(lang["sharpe_ratio"], f"{stats['Sharpe Ratio']:.2f}")
                    st.metric(lang["max_drawdown"], f"{stats['Max. Drawdown [%]']:.2f}%")
                
                with col4:
                    st.metric(lang["buy_hold_return"], f"{stats['Buy & Hold Return [%]']:.2f}%")
                    st.metric(lang["profit_factor"], f"{stats['Profit Factor']:.2f}")
                
                # 차트 섹션
                st.header(lang["analysis"])
                
                chart_col1, chart_col2 = st.columns(2)
                
                with chart_col1:
                    # 가격 차트와 이동평균
                    st.subheader(lang["price_ma"])
                    chart_data = data['Close'].tail(252)  # 마지막 1년
                    ma_short_data = chart_data.rolling(int(short_ma)).mean()
                    ma_long_data = chart_data.rolling(int(long_ma)).mean()
                    
                    chart_df = pd.DataFrame({
                        '가격' if language == '한국어' else 'Price': chart_data,
                        f'MA{int(short_ma)}': ma_short_data,
                        f'MA{int(long_ma)}': ma_long_data
                    })
                    st.line_chart(chart_df)
                
                with chart_col2:
                    # 수익률 분포
                    st.subheader(lang["returns_dist"])
                    fig = create_returns_chart(trades, lang)
                    if fig:
                        st.pyplot(fig)
                        plt.close(fig)
                    else:
                        st.info(lang["no_trades"])
                
                # 상세 통계
                st.header(lang["detailed_results"])
                
                # 전략 비교
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
                            file_name=f"{ticker}_backtest_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                            mime="text/plain"
                        )
                
                with col2:
                    if trades is not None and not trades.empty:
                        if st.button(lang["download_trades"]):
                            csv = trades.to_csv(index=False)
                            st.download_button(
                                label=lang["download_trades_btn"],
                                data=csv,
                                file_name=f"{ticker}_trades_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                mime="text/csv"
                            )
                
            except Exception as e:
                st.error(lang["error"].format(str(e)))
    
    # 정보 사이드바
    with st.sidebar:
        st.markdown("---")
        st.markdown(f"### {lang['about']}")
        st.markdown(lang["about_text"])
        
        st.markdown(f"### {lang['tips']}")
        st.markdown(lang["tips_text"])


if __name__ == "__main__":
    main()