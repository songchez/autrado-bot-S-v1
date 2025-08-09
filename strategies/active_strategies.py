"""
거래 횟수가 더 많은 활발한 전략들
기존 장기 전략의 거래 횟수 문제를 해결하기 위한 단기/중기 전략
"""

import pandas as pd
import numpy as np
from backtesting import Strategy
from backtesting.lib import crossover


class ShortTermTrend(Strategy):
    """단기 추세 전략 (10/20일 이평)"""
    short_ma = 10
    long_ma = 20

    def init(self):
        self.ma_short = self.I(lambda x: pd.Series(x).rolling(self.short_ma).mean(), self.data.Close)
        self.ma_long = self.I(lambda x: pd.Series(x).rolling(self.long_ma).mean(), self.data.Close)

    def next(self):
        if crossover(self.ma_short, self.ma_long):
            self.buy()
        elif crossover(self.ma_long, self.ma_short):
            self.sell()


class SensitiveRSI(Strategy):
    """민감한 RSI 전략 (65/35 기준)"""
    rsi_period = 14
    rsi_upper = 65  # 기존 70 → 65
    rsi_lower = 35  # 기존 30 → 35

    def init(self):
        self.rsi = self.I(lambda x: self._calculate_rsi(pd.Series(x), self.rsi_period), self.data.Close)

    def _calculate_rsi(self, prices, period):
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def next(self):
        if self.rsi[-1] < self.rsi_lower and not self.position:
            self.buy()
        elif self.rsi[-1] > self.rsi_upper and self.position:
            self.sell()


class FastBreakout(Strategy):
    """빠른 돌파 전략 (10일 기준)"""
    period = 10

    def init(self):
        high = pd.Series(self.data.High)
        low = pd.Series(self.data.Low)
        self.upper = self.I(lambda: high.rolling(self.period).max())
        self.lower = self.I(lambda: low.rolling(self.period).min())

    def next(self):
        if self.data.Close[-1] > self.upper[-2] and not self.position:
            self.buy()
        elif self.data.Close[-1] < self.lower[-2] and self.position:
            self.sell()


class MidTermTrend(Strategy):
    """중기 추세 전략 (5/15일 이평)"""
    short_ma = 5
    long_ma = 15

    def init(self):
        self.ma_short = self.I(lambda x: pd.Series(x).rolling(self.short_ma).mean(), self.data.Close)
        self.ma_long = self.I(lambda x: pd.Series(x).rolling(self.long_ma).mean(), self.data.Close)

    def next(self):
        if crossover(self.ma_short, self.ma_long):
            self.buy()
        elif crossover(self.ma_long, self.ma_short):
            self.sell()


class VolumeBreakout(Strategy):
    """거래량 돌파 전략"""
    price_period = 20
    volume_multiplier = 1.5

    def init(self):
        high = pd.Series(self.data.High)
        volume = pd.Series(self.data.Volume)
        self.resistance = self.I(lambda: high.rolling(self.price_period).max())
        self.avg_volume = self.I(lambda: volume.rolling(self.price_period).mean())

    def next(self):
        current_volume = self.data.Volume[-1]
        volume_threshold = self.avg_volume[-1] * self.volume_multiplier
        
        # 거래량 증가 + 저항선 돌파
        if (self.data.Close[-1] > self.resistance[-2] and 
            current_volume > volume_threshold and not self.position):
            self.buy()
        elif self.position and self.data.Close[-1] < self.data.Close[-5]:  # 5일 전보다 하락시 매도
            self.sell()


# 활발한 전략들의 메타데이터
ACTIVE_STRATEGIES = {
    "ShortTermTrend": {
        "class": ShortTermTrend,
        "name": {"English": "Short Term Trend", "한국어": "단기 추세"},
        "description": {
            "English": "Fast signals using 10/20-day moving averages (signals every ~18 days)",
            "한국어": "10/20일 이동평균 사용한 빠른 신호 (약 18일마다 신호)"
        },
        "expected_frequency": "High (20-30 signals/year)",
        "params": {
            "short_ma": {"min": 5, "max": 20, "default": 10, "name": {"English": "Short MA", "한국어": "단기 이평"}},
            "long_ma": {"min": 15, "max": 30, "default": 20, "name": {"English": "Long MA", "한국어": "장기 이평"}}
        }
    },
    "SensitiveRSI": {
        "class": SensitiveRSI,
        "name": {"English": "Sensitive RSI", "한국어": "민감한 RSI"},
        "description": {
            "English": "More frequent RSI signals using 65/35 thresholds (signals every ~4 days)",
            "한국어": "65/35 기준을 사용한 더 빈번한 RSI 신호 (약 4일마다 신호)"
        },
        "expected_frequency": "Very High (100+ signals/year)",
        "params": {
            "rsi_period": {"min": 5, "max": 20, "default": 14, "name": {"English": "RSI Period", "한국어": "RSI 기간"}},
            "rsi_upper": {"min": 60, "max": 80, "default": 65, "name": {"English": "Overbought", "한국어": "과매수 기준"}},
            "rsi_lower": {"min": 20, "max": 40, "default": 35, "name": {"English": "Oversold", "한국어": "과매도 기준"}}
        }
    },
    "FastBreakout": {
        "class": FastBreakout,
        "name": {"English": "Fast Breakout", "한국어": "빠른 돌파"},
        "description": {
            "English": "Quick breakout signals using 10-day highs/lows (signals every ~5 days)",
            "한국어": "10일 고저점 돌파를 이용한 빠른 신호 (약 5일마다 신호)"
        },
        "expected_frequency": "Very High (70-100 signals/year)",
        "params": {
            "period": {"min": 5, "max": 20, "default": 10, "name": {"English": "Lookback Period", "한국어": "확인 기간"}}
        }
    },
    "MidTermTrend": {
        "class": MidTermTrend,
        "name": {"English": "Mid Term Trend", "한국어": "중기 추세"},
        "description": {
            "English": "Very fast signals using 5/15-day moving averages (signals every ~10 days)",
            "한국어": "5/15일 이동평균을 사용한 매우 빠른 신호 (약 10일마다 신호)"
        },
        "expected_frequency": "Very High (35+ signals/year)",
        "params": {
            "short_ma": {"min": 3, "max": 10, "default": 5, "name": {"English": "Short MA", "한국어": "단기 이평"}},
            "long_ma": {"min": 10, "max": 20, "default": 15, "name": {"English": "Long MA", "한국어": "장기 이평"}}
        }
    },
    "VolumeBreakout": {
        "class": VolumeBreakout,  
        "name": {"English": "Volume Breakout", "한국어": "거래량 돌파"},
        "description": {
            "English": "Breakout with volume confirmation for higher quality signals",
            "한국어": "거래량 확인을 통한 고품질 돌파 신호"
        },
        "expected_frequency": "Medium (15-25 signals/year)",
        "params": {
            "price_period": {"min": 10, "max": 30, "default": 20, "name": {"English": "Price Period", "한국어": "가격 기간"}},
            "volume_multiplier": {"min": 1.2, "max": 2.5, "default": 1.5, "name": {"English": "Volume Multiplier", "한국어": "거래량 배수"}}
        }
    }
}