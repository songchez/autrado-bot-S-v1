import pandas as pd
import numpy as np
from backtesting import Strategy
from backtesting.lib import crossover


class UltraFastEMAStrategy(Strategy):
    """초고속 EMA 크로스 전략 - 매우 민감"""
    fast_ema = 2
    slow_ema = 5
    
    def init(self):
        close = pd.Series(self.data.Close, index=self.data.index)
        self.ema_fast = self.I(lambda: close.ewm(span=self.fast_ema).mean())
        self.ema_slow = self.I(lambda: close.ewm(span=self.slow_ema).mean())
    
    def next(self):
        if crossover(self.ema_fast, self.ema_slow):
            if self.position.is_short:
                self.position.close()
            self.buy()
        elif crossover(self.ema_slow, self.ema_fast):
            if self.position.is_long:
                self.position.close()
            self.sell()


class PriceActionStrategy(Strategy):
    """가격 행동 기반 전략 - 매우 짧은 기간"""
    lookback = 3
    threshold = 0.005  # 0.5% 움직임
    
    def init(self):
        close = pd.Series(self.data.Close, index=self.data.index)
        high = pd.Series(self.data.High, index=self.data.index)
        low = pd.Series(self.data.Low, index=self.data.index)
        
        # 최근 최고/최저가
        self.recent_high = self.I(lambda: high.rolling(self.lookback).max())
        self.recent_low = self.I(lambda: low.rolling(self.lookback).min())
        # 변화율
        self.price_change = self.I(lambda: close.pct_change())
    
    def next(self):
        if len(self.data.Close) < self.lookback:
            return
            
        current_price = self.data.Close[-1]
        price_change = self.price_change[-1]
        
        # 상승 모멘텀 + 최고가 근처
        if (price_change > self.threshold and 
            current_price >= self.recent_high[-2] * 0.999 and 
            not self.position):
            self.buy()
        
        # 하락 모멘텀 + 최저가 근처 또는 손절
        elif ((price_change < -self.threshold and 
               current_price <= self.recent_low[-2] * 1.001) or
              (self.position and price_change < -self.threshold * 2)) and self.position:
            self.position.close()


class MicroTrendStrategy(Strategy):
    """마이크로 트렌드 전략 - 매우 짧은 추세"""
    short_period = 3
    long_period = 8
    volume_confirm = False
    
    def init(self):
        close = pd.Series(self.data.Close, index=self.data.index)
        self.short_sma = self.I(lambda: close.rolling(self.short_period).mean())
        self.long_sma = self.I(lambda: close.rolling(self.long_period).mean())
        
        # 추세 강도
        self.trend_strength = self.I(lambda: (self.short_sma / self.long_sma) - 1)
        
        if self.volume_confirm and hasattr(self.data, 'Volume'):
            volume = pd.Series(self.data.Volume, index=self.data.index)
            self.avg_volume = self.I(lambda: volume.rolling(10).mean())
    
    def next(self):
        if len(self.data.Close) < self.long_period:
            return
        
        current_trend = self.trend_strength[-1]
        prev_trend = self.trend_strength[-2] if len(self.trend_strength) > 1 else 0
        
        # 볼륨 확인
        volume_ok = True
        if (self.volume_confirm and hasattr(self.data, 'Volume') and 
            self.avg_volume is not None):
            volume_ok = self.data.Volume[-1] > self.avg_volume[-1]
        
        # 상승 추세 전환
        if (current_trend > 0.002 and prev_trend <= 0.002 and 
            volume_ok and not self.position):
            self.buy()
        
        # 하락 추세 전환 또는 추세 약화
        elif ((current_trend < -0.002 and prev_trend >= -0.002) or
              (current_trend < 0.001 and self.position)) and self.position:
            self.position.close()


class HighFrequencyMeanReversionStrategy(Strategy):
    """고빈도 평균회귀 전략"""
    period = 5
    std_threshold = 1.0  # 매우 낮은 임계값
    
    def init(self):
        close = pd.Series(self.data.Close, index=self.data.index)
        self.sma = self.I(lambda: close.rolling(self.period).mean())
        self.std = self.I(lambda: close.rolling(self.period).std())
        self.z_score = self.I(lambda: (close - self.sma) / self.std)
    
    def next(self):
        if len(self.data.Close) < self.period:
            return
        
        current_z = self.z_score[-1]
        if np.isnan(current_z):
            return
        
        # 평균 하회시 매수 (반등 기대)
        if current_z < -self.std_threshold and not self.position:
            self.buy()
        
        # 평균 상회시 매도 또는 너무 많이 하락시 손절
        elif (current_z > self.std_threshold or 
              current_z < -self.std_threshold * 2) and self.position:
            self.position.close()


class VolumeBreakoutScalpStrategy(Strategy):
    """볼륨 돌파 스캘핑 전략"""
    volume_period = 10
    price_period = 5
    volume_threshold = 1.5
    price_threshold = 0.003  # 0.3%
    
    def init(self):
        close = pd.Series(self.data.Close, index=self.data.index)
        
        if hasattr(self.data, 'Volume'):
            volume = pd.Series(self.data.Volume, index=self.data.index)
            self.avg_volume = self.I(lambda: volume.rolling(self.volume_period).mean())
            self.volume_ratio = self.I(lambda: volume / self.avg_volume)
        else:
            self.avg_volume = None
            self.volume_ratio = None
            
        self.price_change = self.I(lambda: close.pct_change(self.price_period))
    
    def next(self):
        if len(self.data.Close) < max(self.volume_period, self.price_period):
            return
        
        price_move = self.price_change[-1] if not np.isnan(self.price_change[-1]) else 0
        
        # 볼륨 확인 (있는 경우만)
        volume_spike = True
        if self.volume_ratio is not None:
            volume_spike = self.volume_ratio[-1] > self.volume_threshold
        
        # 상승 돌파 + 볼륨 급증
        if (price_move > self.price_threshold and 
            volume_spike and not self.position):
            self.buy()
        
        # 하락 돌파 또는 소폭 반전시 매도
        elif ((price_move < -self.price_threshold) or
              (self.position and price_move < -self.price_threshold/2)) and self.position:
            self.position.close()


# 초단기 전략 메타데이터
ULTRA_SHORT_STRATEGIES = {
    "UltraFastEMAStrategy": {
        "class": UltraFastEMAStrategy,
        "name": {"English": "Ultra Fast EMA", "한국어": "초고속 EMA"},
        "description": {
            "English": "Ultra-fast EMA crossover (2/5) for maximum trading frequency.",
            "한국어": "최대 거래 빈도를 위한 초고속 EMA 교차 (2/5)."
        },
        "params": {
            "fast_ema": {"min": 2, "max": 5, "default": 2, "name": {"English": "Fast EMA", "한국어": "빠른 EMA"}},
            "slow_ema": {"min": 3, "max": 8, "default": 5, "name": {"English": "Slow EMA", "한국어": "느린 EMA"}}
        }
    },
    "PriceActionStrategy": {
        "class": PriceActionStrategy,
        "name": {"English": "Price Action Scalp", "한국어": "프라이스 액션 스캘핑"},
        "description": {
            "English": "Price action scalping based on short-term momentum and breakouts.",
            "한국어": "단기 모멘텀과 돌파를 기반으로 한 프라이스 액션 스캘핑."
        },
        "params": {
            "lookback": {"min": 2, "max": 5, "default": 3, "name": {"English": "Lookback", "한국어": "조회 기간"}},
            "threshold": {"min": 0.002, "max": 0.01, "default": 0.005, "name": {"English": "Threshold", "한국어": "임계값"}}
        }
    },
    "MicroTrendStrategy": {
        "class": MicroTrendStrategy,
        "name": {"English": "Micro Trend", "한국어": "마이크로 추세"},
        "description": {
            "English": "Micro trend following with 3/8 period SMA for frequent signals.",
            "한국어": "빈번한 신호를 위한 3/8 기간 SMA 마이크로 추세 추종."
        },
        "params": {
            "short_period": {"min": 2, "max": 5, "default": 3, "name": {"English": "Short Period", "한국어": "단기 기간"}},
            "long_period": {"min": 6, "max": 12, "default": 8, "name": {"English": "Long Period", "한국어": "장기 기간"}}
        }
    },
    "HighFrequencyMeanReversionStrategy": {
        "class": HighFrequencyMeanReversionStrategy,
        "name": {"English": "HF Mean Reversion", "한국어": "고빈도 평균회귀"},
        "description": {
            "English": "High-frequency mean reversion with low threshold for frequent trades.",
            "한국어": "빈번한 거래를 위한 낮은 임계값의 고빈도 평균회귀."
        },
        "params": {
            "period": {"min": 3, "max": 8, "default": 5, "name": {"English": "Period", "한국어": "기간"}},
            "std_threshold": {"min": 0.5, "max": 2.0, "default": 1.0, "name": {"English": "Std Threshold", "한국어": "표준편차 임계값"}}
        }
    },
    "VolumeBreakoutScalpStrategy": {
        "class": VolumeBreakoutScalpStrategy,
        "name": {"English": "Volume Scalp", "한국어": "볼륨 스캘핑"},
        "description": {
            "English": "Volume-based scalping with breakout confirmation.",
            "한국어": "돌파 확인이 있는 볼륨 기반 스캘핑."
        },
        "params": {
            "volume_period": {"min": 5, "max": 15, "default": 10, "name": {"English": "Volume Period", "한국어": "볼륨 기간"}},
            "price_period": {"min": 3, "max": 8, "default": 5, "name": {"English": "Price Period", "한국어": "가격 기간"}},
            "volume_threshold": {"min": 1.2, "max": 2.5, "default": 1.5, "name": {"English": "Volume Threshold", "한국어": "볼륨 임계값"}},
            "price_threshold": {"min": 0.001, "max": 0.008, "default": 0.003, "name": {"English": "Price Threshold", "한국어": "가격 임계값"}}
        }
    }
}