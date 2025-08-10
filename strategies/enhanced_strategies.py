import pandas as pd
import numpy as np
from backtesting import Strategy
from backtesting.lib import crossover


class ShortTermTrendStrategy(Strategy):
    """단기 추세 전략 - 5일/20일 이동평균"""
    short_ma = 5
    long_ma = 20
    
    def init(self):
        close = pd.Series(self.data.Close, index=self.data.index)
        self.ma_short = self.I(lambda: close.rolling(self.short_ma).mean())
        self.ma_long = self.I(lambda: close.rolling(self.long_ma).mean())
    
    def next(self):
        if crossover(self.ma_short, self.ma_long):
            if self.position.is_short:
                self.position.close()
            self.buy()
        elif crossover(self.ma_long, self.ma_short):
            if self.position.is_long:
                self.position.close()
            self.sell()


class SwingRSIStrategy(Strategy):
    """스윙 RSI 전략 - 더 빈번한 거래를 위한 RSI"""
    rsi_period = 14
    rsi_upper = 65
    rsi_lower = 35
    
    def init(self):
        def calculate_rsi(close_prices):
            delta = close_prices.diff()
            gain = delta.where(delta > 0, 0).rolling(window=self.rsi_period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=self.rsi_period).mean()
            rs = gain / loss
            return 100 - (100 / (1 + rs))
        
        close = pd.Series(self.data.Close, index=self.data.index)
        self.rsi = self.I(lambda: calculate_rsi(close))
    
    def next(self):
        if len(self.rsi) < self.rsi_period:
            return
        
        current_rsi = self.rsi[-1]
        if np.isnan(current_rsi):
            return
        
        if current_rsi < self.rsi_lower and not self.position:
            self.buy()
        elif current_rsi > self.rsi_upper and self.position:
            self.position.close()


class FastMACDStrategy(Strategy):
    """빠른 MACD 전략 - 단기 신호"""
    fast_period = 8
    slow_period = 18
    signal_period = 7
    
    def init(self):
        close = pd.Series(self.data.Close, index=self.data.index)
        ema_fast = close.ewm(span=self.fast_period).mean()
        ema_slow = close.ewm(span=self.slow_period).mean()
        macd_line = ema_fast - ema_slow
        self.macd = self.I(lambda: macd_line)
        self.signal = self.I(lambda: macd_line.ewm(span=self.signal_period).mean())
    
    def next(self):
        if crossover(self.macd, self.signal):
            if self.position.is_short:
                self.position.close()
            self.buy()
        elif crossover(self.signal, self.macd):
            if self.position.is_long:
                self.position.close()
            self.sell()


class MomentumSwingStrategy(Strategy):
    """모멘텀 스윙 전략"""
    momentum_period = 8
    threshold = 0.012
    
    def init(self):
        close = pd.Series(self.data.Close, index=self.data.index)
        self.momentum = self.I(lambda: (close / close.shift(self.momentum_period)) - 1)
        self.sma_filter = self.I(lambda: close.rolling(10).mean())
    
    def next(self):
        if len(self.momentum) < self.momentum_period + 1:
            return
        
        current_momentum = self.momentum[-1]
        current_price = self.data.Close[-1]
        
        if (current_momentum > self.threshold and 
            current_price > self.sma_filter[-1] and 
            not self.position):
            self.buy()
        elif ((current_momentum < -self.threshold or 
               current_price < self.sma_filter[-1] * 0.98) and 
              self.position):
            self.position.close()


class BollingerSwingStrategy(Strategy):
    """볼린저 밴드 스윙 전략"""
    period = 15
    std_mult = 1.8
    
    def init(self):
        close = pd.Series(self.data.Close, index=self.data.index)
        sma = close.rolling(self.period).mean()
        std = close.rolling(self.period).std()
        
        self.sma = self.I(lambda: sma)
        self.upper = self.I(lambda: sma + (std * self.std_mult))
        self.lower = self.I(lambda: sma - (std * self.std_mult))
    
    def next(self):
        price = self.data.Close[-1]
        
        # 하단 밴드 근처에서 매수 (반등 기대)
        if price < self.lower[-1] * 1.01 and not self.position:
            self.buy()
        # 상단 밴드 근처 또는 중심선 아래로 하락시 매도
        elif (price > self.upper[-1] * 0.99 or 
              price < self.sma[-1]) and self.position:
            self.position.close()


class BreakoutSwingStrategy(Strategy):
    """돌파 스윙 전략 - 단기 고점/저점 돌파"""
    lookback_period = 12
    volume_confirm = True
    
    def init(self):
        high = pd.Series(self.data.High, index=self.data.index)
        low = pd.Series(self.data.Low, index=self.data.index)
        volume = pd.Series(self.data.Volume, index=self.data.index)
        
        self.recent_high = self.I(lambda: high.rolling(self.lookback_period).max())
        self.recent_low = self.I(lambda: low.rolling(self.lookback_period).min())
        self.avg_volume = self.I(lambda: volume.rolling(20).mean()) if self.volume_confirm else None
    
    def next(self):
        current_price = self.data.Close[-1]
        current_volume = self.data.Volume[-1] if hasattr(self.data, 'Volume') else 1
        
        # 볼륨 확인 (옵션)
        volume_ok = True
        if self.volume_confirm and self.avg_volume is not None:
            volume_ok = current_volume > self.avg_volume[-1] * 1.2
        
        # 상승 돌파
        if (current_price > self.recent_high[-2] and 
            volume_ok and 
            not self.position):
            self.buy()
        # 하락 돌파 또는 손절
        elif (current_price < self.recent_low[-2] or 
              (self.position and current_price < self.recent_low[-5])) and self.position:
            self.position.close()


class TripleMaSwingStrategy(Strategy):
    """삼중 이동평균 스윙 전략"""
    short_ma = 5
    medium_ma = 12
    long_ma = 25
    
    def init(self):
        close = pd.Series(self.data.Close, index=self.data.index)
        self.short_sma = self.I(lambda: close.rolling(self.short_ma).mean())
        self.medium_sma = self.I(lambda: close.rolling(self.medium_ma).mean())
        self.long_sma = self.I(lambda: close.rolling(self.long_ma).mean())
    
    def next(self):
        # 모든 이동평균이 상승 정렬이고 가격이 단기MA 위에 있을 때 매수
        if (self.short_sma[-1] > self.medium_sma[-1] > self.long_sma[-1] and
            self.data.Close[-1] > self.short_sma[-1] and
            not self.position):
            self.buy()
        
        # 단기MA가 중기MA 아래로 떨어지거나 가격이 중기MA 아래로 떨어질 때 매도
        elif ((self.short_sma[-1] < self.medium_sma[-1] or 
               self.data.Close[-1] < self.medium_sma[-1]) and 
              self.position):
            self.position.close()


class ScalpingStrategy(Strategy):
    """스캘핑 전략 - 매우 단기"""
    fast_ema = 3
    slow_ema = 8
    rsi_period = 9
    
    def init(self):
        close = pd.Series(self.data.Close, index=self.data.index)
        
        self.ema_fast = self.I(lambda: close.ewm(span=self.fast_ema).mean())
        self.ema_slow = self.I(lambda: close.ewm(span=self.slow_ema).mean())
        
        # 빠른 RSI
        def calculate_rsi(close_prices):
            delta = close_prices.diff()
            gain = delta.where(delta > 0, 0).ewm(span=self.rsi_period).mean()
            loss = (-delta.where(delta < 0, 0)).ewm(span=self.rsi_period).mean()
            rs = gain / loss
            return 100 - (100 / (1 + rs))
        
        self.rsi = self.I(lambda: calculate_rsi(close))
    
    def next(self):
        if len(self.rsi) < self.rsi_period:
            return
        
        current_rsi = self.rsi[-1]
        if np.isnan(current_rsi):
            return
        
        # EMA 크로스오버 + RSI 필터
        if (crossover(self.ema_fast, self.ema_slow) and 
            current_rsi < 60 and not self.position):
            self.buy()
        elif (crossover(self.ema_slow, self.ema_fast) or 
              current_rsi > 70) and self.position:
            self.position.close()


# 향상된 전략 딕셔너리
ENHANCED_STRATEGIES = {
    "ShortTermTrendStrategy": {
        "class": ShortTermTrendStrategy,
        "name": {"English": "Short-Term Trend", "한국어": "단기 추세"},
        "description": {
            "English": "Fast trend following using 5/20 day moving averages for frequent signals.",
            "한국어": "5일/20일 이동평균을 사용한 빠른 추세 추종 전략으로 빈번한 신호 생성."
        },
        "params": {
            "short_ma": {"min": 3, "max": 10, "default": 5, "name": {"English": "Short MA", "한국어": "단기 이평"}},
            "long_ma": {"min": 15, "max": 30, "default": 20, "name": {"English": "Long MA", "한국어": "장기 이평"}}
        }
    },
    "SwingRSIStrategy": {
        "class": SwingRSIStrategy,
        "name": {"English": "Swing RSI", "한국어": "스윙 RSI"},
        "description": {
            "English": "RSI strategy optimized for swing trading with 65/35 levels for more signals.",
            "한국어": "65/35 레벨을 사용한 스윙 트레이딩 최적화 RSI 전략."
        },
        "params": {
            "rsi_period": {"min": 10, "max": 20, "default": 14, "name": {"English": "RSI Period", "한국어": "RSI 기간"}},
            "rsi_upper": {"min": 60, "max": 75, "default": 65, "name": {"English": "Overbought", "한국어": "과매수 기준"}},
            "rsi_lower": {"min": 25, "max": 40, "default": 35, "name": {"English": "Oversold", "한국어": "과매도 기준"}}
        }
    },
    "FastMACDStrategy": {
        "class": FastMACDStrategy,
        "name": {"English": "Fast MACD", "한국어": "빠른 MACD"},
        "description": {
            "English": "Accelerated MACD with 8/18/7 periods for quick signal generation.",
            "한국어": "8/18/7 기간을 사용한 빠른 신호 생성을 위한 가속 MACD."
        },
        "params": {
            "fast_period": {"min": 6, "max": 12, "default": 8, "name": {"English": "Fast Period", "한국어": "빠른 기간"}},
            "slow_period": {"min": 15, "max": 25, "default": 18, "name": {"English": "Slow Period", "한국어": "느린 기간"}},
            "signal_period": {"min": 5, "max": 10, "default": 7, "name": {"English": "Signal", "한국어": "시그널"}}
        }
    },
    "MomentumSwingStrategy": {
        "class": MomentumSwingStrategy,
        "name": {"English": "Momentum Swing", "한국어": "모멘텀 스윙"},
        "description": {
            "English": "Momentum-based swing strategy with trend filter for better entries.",
            "한국어": "더 나은 진입을 위한 추세 필터가 있는 모멘텀 기반 스윙 전략."
        },
        "params": {
            "momentum_period": {"min": 5, "max": 15, "default": 8, "name": {"English": "Momentum Period", "한국어": "모멘텀 기간"}},
            "threshold": {"min": 0.005, "max": 0.025, "default": 0.012, "name": {"English": "Threshold", "한국어": "임계값"}}
        }
    },
    "BollingerSwingStrategy": {
        "class": BollingerSwingStrategy,
        "name": {"English": "Bollinger Swing", "한국어": "볼린저 스윙"},
        "description": {
            "English": "Bollinger Bands swing strategy with 15-period and 1.8 std deviation.",
            "한국어": "15기간과 1.8 표준편차를 사용한 볼린저 밴드 스윙 전략."
        },
        "params": {
            "period": {"min": 10, "max": 25, "default": 15, "name": {"English": "Period", "한국어": "기간"}},
            "std_mult": {"min": 1.5, "max": 2.5, "default": 1.8, "name": {"English": "Std Multiplier", "한국어": "표준편차 배수"}}
        }
    },
    "BreakoutSwingStrategy": {
        "class": BreakoutSwingStrategy,
        "name": {"English": "Breakout Swing", "한국어": "돌파 스윙"},
        "description": {
            "English": "Short-term breakout strategy using 12-period highs and lows.",
            "한국어": "12기간 고점과 저점을 사용한 단기 돌파 전략."
        },
        "params": {
            "lookback_period": {"min": 8, "max": 20, "default": 12, "name": {"English": "Lookback", "한국어": "조회 기간"}}
        }
    },
    "TripleMaSwingStrategy": {
        "class": TripleMaSwingStrategy,
        "name": {"English": "Triple MA Swing", "한국어": "삼중 이평 스윙"},
        "description": {
            "English": "Triple moving average swing with 5/12/25 periods for trend confirmation.",
            "한국어": "추세 확인을 위한 5/12/25 기간의 삼중 이동평균 스윙."
        },
        "params": {
            "short_ma": {"min": 3, "max": 8, "default": 5, "name": {"English": "Short MA", "한국어": "단기 이평"}},
            "medium_ma": {"min": 10, "max": 18, "default": 12, "name": {"English": "Medium MA", "한국어": "중기 이평"}},
            "long_ma": {"min": 20, "max": 35, "default": 25, "name": {"English": "Long MA", "한국어": "장기 이평"}}
        }
    },
    "ScalpingStrategy": {
        "class": ScalpingStrategy,
        "name": {"English": "Scalping", "한국어": "스캘핑"},
        "description": {
            "English": "Ultra short-term strategy using 3/8 EMA crossover with RSI filter.",
            "한국어": "RSI 필터와 함께 3/8 EMA 교차를 사용한 초단기 전략."
        },
        "params": {
            "fast_ema": {"min": 2, "max": 5, "default": 3, "name": {"English": "Fast EMA", "한국어": "빠른 EMA"}},
            "slow_ema": {"min": 6, "max": 12, "default": 8, "name": {"English": "Slow EMA", "한국어": "느린 EMA"}},
            "rsi_period": {"min": 7, "max": 15, "default": 9, "name": {"English": "RSI Period", "한국어": "RSI 기간"}}
        }
    }
}