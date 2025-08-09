"""
전략 기본 클래스 및 공통 유틸리티

이 모듈은 모든 전략이 공유하는 기본 클래스와 유틸리티 함수를 제공합니다.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import pandas as pd
import numpy as np
from backtesting import Strategy


class BaseStrategy(Strategy):
    """모든 전략의 기본 클래스"""
    
    @classmethod
    def get_default_params(cls) -> Dict[str, Any]:
        """기본 매개변수 반환"""
        return {}
    
    @classmethod
    def get_param_ranges(cls) -> Dict[str, Dict[str, Any]]:
        """매개변수 범위 반환 (최적화용)"""
        return {}
    
    @classmethod
    def get_description(cls) -> Dict[str, str]:
        """전략 설명 반환 (다국어 지원)"""
        return {
            "English": "Base strategy class",
            "한국어": "기본 전략 클래스"
        }


class StrategyValidator:
    """전략 유효성 검증 클래스"""
    
    @staticmethod
    def validate_params(strategy_class: type, params: Dict[str, Any]) -> List[str]:
        """매개변수 유효성 검증"""
        errors = []
        
        param_ranges = strategy_class.get_param_ranges()
        
        for param_name, param_value in params.items():
            if param_name in param_ranges:
                param_range = param_ranges[param_name]
                
                if 'min' in param_range and param_value < param_range['min']:
                    errors.append(f"{param_name}: 최솟값 {param_range['min']} 이상이어야 합니다.")
                
                if 'max' in param_range and param_value > param_range['max']:
                    errors.append(f"{param_name}: 최댓값 {param_range['max']} 이하여야 합니다.")
        
        return errors
    
    @staticmethod
    def validate_data(data: pd.DataFrame) -> List[str]:
        """데이터 유효성 검증"""
        errors = []
        
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing_columns = [col for col in required_columns if col not in data.columns]
        
        if missing_columns:
            errors.append(f"필수 컬럼이 없습니다: {missing_columns}")
        
        if len(data) < 100:
            errors.append("데이터가 너무 짧습니다. 최소 100개 이상의 데이터가 필요합니다.")
        
        if data.isnull().any().any():
            errors.append("데이터에 결측값이 있습니다.")
        
        return errors


class StrategyPerformanceAnalyzer:
    """전략 성과 분석 클래스"""
    
    @staticmethod
    def calculate_custom_metrics(stats: pd.Series, trades: pd.DataFrame) -> Dict[str, float]:
        """사용자 정의 성과 지표 계산"""
        metrics = {}
        
        if trades is not None and not trades.empty:
            # 승률별 세부 분석
            winning_trades = trades[trades['ReturnPct'] > 0]
            losing_trades = trades[trades['ReturnPct'] < 0]
            
            if len(winning_trades) > 0:
                metrics['Average_Win'] = winning_trades['ReturnPct'].mean() * 100
                metrics['Largest_Win'] = winning_trades['ReturnPct'].max() * 100
            
            if len(losing_trades) > 0:
                metrics['Average_Loss'] = losing_trades['ReturnPct'].mean() * 100
                metrics['Largest_Loss'] = losing_trades['ReturnPct'].min() * 100
            
            # 연속 승패 분석
            returns = trades['ReturnPct'].values
            wins = returns > 0
            losses = returns < 0
            
            # 최대 연속 승리
            max_consecutive_wins = StrategyPerformanceAnalyzer._max_consecutive(wins)
            max_consecutive_losses = StrategyPerformanceAnalyzer._max_consecutive(losses)
            
            metrics['Max_Consecutive_Wins'] = max_consecutive_wins
            metrics['Max_Consecutive_Losses'] = max_consecutive_losses
            
            # 월별 승률 (가능한 경우)
            if 'ExitTime' in trades.columns:
                trades_copy = trades.copy()
                trades_copy['Month'] = pd.to_datetime(trades_copy['ExitTime']).dt.to_period('M')
                monthly_win_rate = trades_copy.groupby('Month').apply(
                    lambda x: (x['ReturnPct'] > 0).mean() * 100
                ).mean()
                metrics['Average_Monthly_Win_Rate'] = monthly_win_rate
        
        return metrics
    
    @staticmethod
    def _max_consecutive(boolean_array: np.ndarray) -> int:
        """최대 연속 True 개수 계산"""
        if len(boolean_array) == 0:
            return 0
        
        max_count = 0
        current_count = 0
        
        for value in boolean_array:
            if value:
                current_count += 1
                max_count = max(max_count, current_count)
            else:
                current_count = 0
        
        return max_count


def calculate_technical_indicators(data: pd.DataFrame) -> Dict[str, pd.Series]:
    """기술적 지표 계산 유틸리티"""
    indicators = {}
    
    close = data['Close']
    
    # 이동평균선들
    for period in [5, 10, 20, 50, 100, 200]:
        indicators[f'SMA_{period}'] = close.rolling(period).mean()
        indicators[f'EMA_{period}'] = close.ewm(span=period).mean()
    
    # RSI
    def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    indicators['RSI_14'] = calculate_rsi(close, 14)
    
    # 볼린저 밴드
    sma_20 = close.rolling(20).mean()
    std_20 = close.rolling(20).std()
    indicators['BB_Upper'] = sma_20 + (std_20 * 2)
    indicators['BB_Lower'] = sma_20 - (std_20 * 2)
    indicators['BB_Middle'] = sma_20
    
    # MACD
    ema_12 = close.ewm(span=12).mean()
    ema_26 = close.ewm(span=26).mean()
    indicators['MACD'] = ema_12 - ema_26
    indicators['MACD_Signal'] = indicators['MACD'].ewm(span=9).mean()
    indicators['MACD_Histogram'] = indicators['MACD'] - indicators['MACD_Signal']
    
    return indicators