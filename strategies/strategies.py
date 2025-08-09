import pandas as pd
import numpy as np
from backtesting import Strategy
from backtesting.lib import crossover


class TrendFollowing(Strategy):
    """이동평균 교차 추세 추종 전략"""
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


class RSIStrategy(Strategy):
    """RSI 과매수/과매도 전략"""
    rsi_period = 14
    rsi_upper = 70
    rsi_lower = 30

    def init(self):
        self.rsi = self.I(lambda x: pd.Series(x).rolling(self.rsi_period).apply(
            lambda data: 100 - (100 / (1 + (data.diff().clip(lower=0).mean() / 
                                       data.diff().clip(upper=0).abs().mean()))), raw=False), 
                         self.data.Close)

    def next(self):
        if self.rsi[-1] < self.rsi_lower and not self.position:
            self.buy()
        elif self.rsi[-1] > self.rsi_upper and self.position:
            self.sell()


class MACDStrategy(Strategy):
    """MACD 교차 전략"""
    fast_period = 12
    slow_period = 26
    signal_period = 9

    def init(self):
        close = pd.Series(self.data.Close)
        ema_fast = close.ewm(span=self.fast_period).mean()
        ema_slow = close.ewm(span=self.slow_period).mean()
        
        self.macd = self.I(lambda: ema_fast - ema_slow)
        self.signal = self.I(lambda: pd.Series(self.macd).ewm(span=self.signal_period).mean())

    def next(self):
        if crossover(self.macd, self.signal):
            self.buy()
        elif crossover(self.signal, self.macd):
            self.sell()


class BollingerBandsStrategy(Strategy):
    """볼린저 밴드 평균회귀 전략"""
    period = 20
    std_mult = 2

    def init(self):
        close = pd.Series(self.data.Close)
        self.sma = self.I(lambda: close.rolling(self.period).mean())
        std = close.rolling(self.period).std()
        self.upper = self.I(lambda: self.sma + (std * self.std_mult))
        self.lower = self.I(lambda: self.sma - (std * self.std_mult))

    def next(self):
        price = self.data.Close[-1]
        if price < self.lower[-1] and not self.position:
            self.buy()
        elif price > self.upper[-1] and self.position:
            self.sell()


class MeanReversionStrategy(Strategy):
    """평균회귀 전략 (단순)"""
    period = 20
    threshold = 2

    def init(self):
        close = pd.Series(self.data.Close)
        self.sma = self.I(lambda: close.rolling(self.period).mean())
        self.std = self.I(lambda: close.rolling(self.period).std())

    def next(self):
        price = self.data.Close[-1]
        deviation = (price - self.sma[-1]) / self.std[-1]
        
        if deviation < -self.threshold and not self.position:
            self.buy()
        elif deviation > self.threshold and self.position:
            self.sell()


class GoldenCrossStrategy(Strategy):
    """골든크로스/데드크로스 전략"""
    short_ma = 50
    long_ma = 200

    def init(self):
        close = pd.Series(self.data.Close)
        self.ma_short = self.I(lambda: close.rolling(self.short_ma).mean())
        self.ma_long = self.I(lambda: close.rolling(self.long_ma).mean())

    def next(self):
        if crossover(self.ma_short, self.ma_long):  # Golden Cross
            self.buy()
        elif crossover(self.ma_long, self.ma_short):  # Death Cross
            self.sell()


class BreakoutStrategy(Strategy):
    """돌파 전략"""
    period = 20

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


class DualMovingAverageStrategy(Strategy):
    """이중 이동평균 전략 (다른 구현)"""
    fast_ma = 10
    slow_ma = 30

    def init(self):
        close = pd.Series(self.data.Close)
        self.fast_sma = self.I(lambda: close.rolling(self.fast_ma).mean())
        self.slow_sma = self.I(lambda: close.rolling(self.slow_ma).mean())

    def next(self):
        if self.fast_sma[-1] > self.slow_sma[-1] and self.fast_sma[-2] <= self.slow_sma[-2]:
            self.buy()
        elif self.fast_sma[-1] < self.slow_sma[-1] and self.fast_sma[-2] >= self.slow_sma[-2]:
            self.sell()


class MomentumStrategy(Strategy):
    """모멘텀 전략"""
    period = 14
    threshold = 0.02  # 2% threshold

    def init(self):
        close = pd.Series(self.data.Close)
        self.momentum = self.I(lambda: (close / close.shift(self.period)) - 1)

    def next(self):
        if self.momentum[-1] > self.threshold and not self.position:
            self.buy()
        elif self.momentum[-1] < -self.threshold and self.position:
            self.sell()


class TripleMovingAverageStrategy(Strategy):
    """삼중 이동평균 전략"""
    short_ma = 5
    medium_ma = 15
    long_ma = 30

    def init(self):
        close = pd.Series(self.data.Close)
        self.short_sma = self.I(lambda: close.rolling(self.short_ma).mean())
        self.medium_sma = self.I(lambda: close.rolling(self.medium_ma).mean())
        self.long_sma = self.I(lambda: close.rolling(self.long_ma).mean())

    def next(self):
        # 모든 이동평균이 상승 정렬시 매수
        if (self.short_sma[-1] > self.medium_sma[-1] > self.long_sma[-1] and 
            not self.position):
            self.buy()
        # 모든 이동평균이 하락 정렬시 매도
        elif (self.short_sma[-1] < self.medium_sma[-1] < self.long_sma[-1] and 
              self.position):
            self.sell()


# 전략 정보 딕셔너리
STRATEGIES = {
    "TrendFollowing": {
        "class": TrendFollowing,
        "name": {"English": "Trend Following", "한국어": "추세 추종"},
        "description": {
            "English": "Uses moving average crossover to follow trends. Buy when short MA crosses above long MA.",
            "한국어": "이동평균 교차를 이용해 추세를 추종합니다. 단기 이동평균이 장기 이동평균을 상향 돌파시 매수."
        },
        "params": {
            "short_ma": {"min": 5, "max": 100, "default": 50, "name": {"English": "Short MA", "한국어": "단기 이평"}},
            "long_ma": {"min": 50, "max": 300, "default": 200, "name": {"English": "Long MA", "한국어": "장기 이평"}}
        }
    },
    "RSIStrategy": {
        "class": RSIStrategy,
        "name": {"English": "RSI Strategy", "한국어": "RSI 전략"},
        "description": {
            "English": "Buy when RSI is oversold (<30) and sell when overbought (>70).",
            "한국어": "RSI가 과매도(<30)일 때 매수, 과매수(>70)일 때 매도하는 전략."
        },
        "params": {
            "rsi_period": {"min": 5, "max": 50, "default": 14, "name": {"English": "RSI Period", "한국어": "RSI 기간"}},
            "rsi_upper": {"min": 60, "max": 90, "default": 70, "name": {"English": "Overbought", "한국어": "과매수 기준"}},
            "rsi_lower": {"min": 10, "max": 40, "default": 30, "name": {"English": "Oversold", "한국어": "과매도 기준"}}
        }
    },
    "MACDStrategy": {
        "class": MACDStrategy,
        "name": {"English": "MACD Strategy", "한국어": "MACD 전략"},
        "description": {
            "English": "Buy when MACD crosses above signal line, sell when it crosses below.",
            "한국어": "MACD가 시그널선을 상향 돌파시 매수, 하향 돌파시 매도."
        },
        "params": {
            "fast_period": {"min": 5, "max": 20, "default": 12, "name": {"English": "Fast EMA", "한국어": "빠른 지수이평"}},
            "slow_period": {"min": 15, "max": 40, "default": 26, "name": {"English": "Slow EMA", "한국어": "느린 지수이평"}},
            "signal_period": {"min": 5, "max": 15, "default": 9, "name": {"English": "Signal", "한국어": "시그널"}}
        }
    },
    "BollingerBandsStrategy": {
        "class": BollingerBandsStrategy,
        "name": {"English": "Bollinger Bands", "한국어": "볼린저 밴드"},
        "description": {
            "English": "Mean reversion strategy using Bollinger Bands. Buy at lower band, sell at upper band.",
            "한국어": "볼린저 밴드를 이용한 평균회귀 전략. 하단 밴드에서 매수, 상단 밴드에서 매도."
        },
        "params": {
            "period": {"min": 10, "max": 50, "default": 20, "name": {"English": "Period", "한국어": "기간"}},
            "std_mult": {"min": 1.0, "max": 3.0, "default": 2.0, "name": {"English": "Std Multiplier", "한국어": "표준편차 배수"}}
        }
    },
    "MeanReversionStrategy": {
        "class": MeanReversionStrategy,
        "name": {"English": "Mean Reversion", "한국어": "평균회귀"},
        "description": {
            "English": "Simple mean reversion strategy based on standard deviation from moving average.",
            "한국어": "이동평균으로부터의 표준편차를 기반으로 한 간단한 평균회귀 전략."
        },
        "params": {
            "period": {"min": 10, "max": 50, "default": 20, "name": {"English": "Period", "한국어": "기간"}},
            "threshold": {"min": 1.0, "max": 3.0, "default": 2.0, "name": {"English": "Threshold", "한국어": "임계값"}}
        }
    },
    "GoldenCrossStrategy": {
        "class": GoldenCrossStrategy,
        "name": {"English": "Golden Cross", "한국어": "골든크로스"},
        "description": {
            "English": "Classic Golden Cross (50MA > 200MA) and Death Cross strategy.",
            "한국어": "전통적인 골든크로스(50일선 > 200일선)와 데드크로스 전략."
        },
        "params": {
            "short_ma": {"min": 30, "max": 100, "default": 50, "name": {"English": "Short MA", "한국어": "단기 이평"}},
            "long_ma": {"min": 100, "max": 300, "default": 200, "name": {"English": "Long MA", "한국어": "장기 이평"}}
        }
    },
    "BreakoutStrategy": {
        "class": BreakoutStrategy,
        "name": {"English": "Breakout", "한국어": "돌파"},
        "description": {
            "English": "Buy on upward breakout from recent high, sell on downward breakout from recent low.",
            "한국어": "최근 고점을 상향 돌파시 매수, 최근 저점을 하향 돌파시 매도."
        },
        "params": {
            "period": {"min": 10, "max": 50, "default": 20, "name": {"English": "Lookback Period", "한국어": "확인 기간"}}
        }
    },
    "DualMovingAverageStrategy": {
        "class": DualMovingAverageStrategy,
        "name": {"English": "Dual Moving Average", "한국어": "이중 이동평균"},
        "description": {
            "English": "Short-term dual moving average crossover strategy for more frequent signals.",
            "한국어": "더 빈번한 신호를 위한 단기 이중 이동평균 교차 전략."
        },
        "params": {
            "fast_ma": {"min": 5, "max": 20, "default": 10, "name": {"English": "Fast MA", "한국어": "빠른 이평"}},
            "slow_ma": {"min": 20, "max": 50, "default": 30, "name": {"English": "Slow MA", "한국어": "느린 이평"}}
        }
    },
    "MomentumStrategy": {
        "class": MomentumStrategy,
        "name": {"English": "Momentum", "한국어": "모멘텀"},
        "description": {
            "English": "Buy when momentum is strong positive, sell when momentum turns negative.",
            "한국어": "모멘텀이 강한 양수일 때 매수, 음수로 전환시 매도."
        },
        "params": {
            "period": {"min": 5, "max": 30, "default": 14, "name": {"English": "Period", "한국어": "기간"}},
            "threshold": {"min": 0.01, "max": 0.05, "default": 0.02, "name": {"English": "Threshold (%)", "한국어": "임계값 (%)"}}
        }
    },
    "TripleMovingAverageStrategy": {
        "class": TripleMovingAverageStrategy,
        "name": {"English": "Triple Moving Average", "한국어": "삼중 이동평균"},
        "description": {
            "English": "Uses three moving averages for trend confirmation. All must align for signal.",
            "한국어": "추세 확인을 위해 세 개의 이동평균을 사용. 모든 이평선이 정렬되어야 신호 발생."
        },
        "params": {
            "short_ma": {"min": 3, "max": 10, "default": 5, "name": {"English": "Short MA", "한국어": "단기 이평"}},
            "medium_ma": {"min": 10, "max": 25, "default": 15, "name": {"English": "Medium MA", "한국어": "중기 이평"}},
            "long_ma": {"min": 25, "max": 50, "default": 30, "name": {"English": "Long MA", "한국어": "장기 이평"}}
        }
    }
}