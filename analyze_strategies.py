#!/usr/bin/env python3
"""
전략 신호 빈도 분석 스크립트
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# strategies 모듈 import
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from strategies import STRATEGIES

def analyze_signal_frequency():
    """전략별 신호 발생 빈도 분석"""
    
    tickers = ['AAPL', 'TSLA', 'MSFT']
    period = '2y'  # 2년 데이터
    
    print("=" * 60)
    print("📊 전략별 신호 발생 빈도 분석")
    print("=" * 60)
    
    for ticker in tickers:
        print(f"\n🎯 {ticker} 분석")
        print("-" * 30)
        
        try:
            # 데이터 다운로드
            data = yf.download(ticker, period=period, progress=False)
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.droplevel(1)
            
            print(f"데이터 기간: {len(data)}일 ({data.index[0].strftime('%Y-%m-%d')} ~ {data.index[-1].strftime('%Y-%m-%d')})")
            
            # 각 전략별 분석
            analyze_trend_following(data, ticker)
            analyze_rsi_strategy(data, ticker)
            analyze_breakout_strategy(data, ticker)
            
        except Exception as e:
            print(f"❌ {ticker} 분석 실패: {e}")

def analyze_trend_following(data, ticker):
    """추세 추종 전략 분석"""
    print(f"\n📈 추세 추종 전략 (이동평균 교차)")
    
    # 다양한 매개변수로 테스트
    params = [
        (10, 20, "단기"),
        (20, 50, "중기"), 
        (50, 200, "장기")
    ]
    
    for short, long, desc in params:
        try:
            short_ma = data['Close'].rolling(short).mean()
            long_ma = data['Close'].rolling(long).mean()
            
            # 교차점 찾기
            golden_cross = (short_ma > long_ma) & (short_ma.shift(1) <= long_ma.shift(1))
            death_cross = (short_ma < long_ma) & (short_ma.shift(1) >= long_ma.shift(1))
            
            golden_count = golden_cross.sum()
            death_count = death_cross.sum()
            total_signals = golden_count + death_count
            
            avg_interval = len(data) / total_signals if total_signals > 0 else 0
            
            print(f"  {desc} ({short}/{long}일): {total_signals}회 (평균 {avg_interval:.1f}일 간격)")
            
        except Exception as e:
            print(f"  {desc} 분석 실패: {e}")

def analyze_rsi_strategy(data, ticker):
    """RSI 전략 분석"""
    print(f"\n📊 RSI 전략")
    
    try:
        # RSI 계산
        def calculate_rsi(prices, period=14):
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            return 100 - (100 / (1 + rs))
        
        rsi = calculate_rsi(data['Close'], 14)
        
        # 과매수/과매도 신호
        oversold_signals = (rsi < 30).sum()
        overbought_signals = (rsi > 70).sum()
        total_signals = oversold_signals + overbought_signals
        
        avg_interval = len(data) / total_signals if total_signals > 0 else 0
        
        print(f"  과매도 (<30): {oversold_signals}회")
        print(f"  과매수 (>70): {overbought_signals}회")
        print(f"  총 신호: {total_signals}회 (평균 {avg_interval:.1f}일 간격)")
        
    except Exception as e:
        print(f"  RSI 분석 실패: {e}")

def analyze_breakout_strategy(data, ticker):
    """돌파 전략 분석"""
    print(f"\n🚀 돌파 전략")
    
    try:
        periods = [10, 20, 30]
        
        for period in periods:
            high_breakout = data['Close'] > data['High'].rolling(period).max().shift(1)
            low_breakdown = data['Close'] < data['Low'].rolling(period).min().shift(1)
            
            breakout_count = high_breakout.sum()
            breakdown_count = low_breakdown.sum()
            total_signals = breakout_count + breakdown_count
            
            avg_interval = len(data) / total_signals if total_signals > 0 else 0
            
            print(f"  {period}일 돌파: {total_signals}회 (평균 {avg_interval:.1f}일 간격)")
            
    except Exception as e:
        print(f"  돌파 전략 분석 실패: {e}")

def analyze_market_conditions():
    """시장 상황 분석"""
    print(f"\n\n🌍 시장 상황 분석")
    print("=" * 30)
    
    try:
        # S&P 500으로 전체 시장 상황 파악
        spy = yf.download('SPY', period='1y', progress=False)
        if isinstance(spy.columns, pd.MultiIndex):
            spy.columns = spy.columns.droplevel(1)
        
        # 최근 3개월, 6개월, 1년 수익률
        periods = [
            (90, "3개월"),
            (180, "6개월"), 
            (252, "1년")
        ]
        
        current_price = spy['Close'].iloc[-1]
        
        print("S&P 500 수익률:")
        for days, desc in periods:
            if len(spy) > days:
                past_price = spy['Close'].iloc[-days]
                return_pct = ((current_price / past_price) - 1) * 100
                print(f"  최근 {desc}: {return_pct:+.2f}%")
        
        # 변동성 분석
        returns = spy['Close'].pct_change()
        volatility = returns.std() * np.sqrt(252) * 100
        print(f"\n연간 변동성: {volatility:.2f}%")
        
        # 추세 분석
        ma_20 = spy['Close'].rolling(20).mean().iloc[-1]
        ma_50 = spy['Close'].rolling(50).mean().iloc[-1]
        ma_200 = spy['Close'].rolling(200).mean().iloc[-1]
        
        print(f"\n현재 추세:")
        print(f"  현재가: ${current_price:.2f}")
        print(f"  20일 이평: ${ma_20:.2f}")
        print(f"  50일 이평: ${ma_50:.2f}")
        print(f"  200일 이평: ${ma_200:.2f}")
        
        if current_price > ma_20 > ma_50 > ma_200:
            trend = "강한 상승세"
        elif current_price > ma_50 > ma_200:
            trend = "상승세"
        elif current_price < ma_20 < ma_50 < ma_200:
            trend = "강한 하락세"
        elif current_price < ma_50 < ma_200:
            trend = "하락세"
        else:
            trend = "혼조세/횡보"
            
        print(f"  판단: {trend}")
        
    except Exception as e:
        print(f"시장 분석 실패: {e}")

def suggest_improvements():
    """개선 방안 제안"""
    print(f"\n\n💡 거래 횟수 증대 방안")
    print("=" * 30)
    
    suggestions = [
        "1. 단기 전략 추가:",
        "   - 5/10일 이동평균 교차",
        "   - RSI 임계값 조정 (75/25 → 65/35)",
        "   - 볼린저 밴드 단기 전략",
        "",
        "2. 다중 시간대 분석:",
        "   - 4시간, 1일, 1주 차트 조합",
        "   - 단기 신호 + 장기 추세 확인",
        "",
        "3. 변동성 기반 전략:",
        "   - ATR(평균 실가 범위) 활용",
        "   - 변동성 돌파 전략",
        "",
        "4. 여러 지표 조합:",
        "   - MACD + RSI 동시 신호",
        "   - 이동평균 + 거래량 확인",
        "",
        "5. 리스크 관리:",
        "   - 손절매/익절매 자동화",
        "   - 포지션 사이징",
    ]
    
    for suggestion in suggestions:
        print(suggestion)

if __name__ == "__main__":
    analyze_signal_frequency()
    analyze_market_conditions() 
    suggest_improvements()
    
    print(f"\n\n🔧 즉시 적용 가능한 해결책:")
    print("1. strategies/strategies.py에서 매개변수 조정")
    print("2. 더 민감한 전략 추가")
    print("3. 다중 전략 동시 사용")