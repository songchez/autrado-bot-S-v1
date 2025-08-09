"""
공통 거래 전략 모듈

이 모듈은 백테스팅과 실시간 모니터링에서 공유하는 거래 전략들을 포함합니다.
"""

from .strategies import (
    # 기본 전략 클래스들
    TrendFollowing,
    RSIStrategy, 
    MACDStrategy,
    BollingerBandsStrategy,
    MeanReversionStrategy,
    GoldenCrossStrategy,
    BreakoutStrategy,
    DualMovingAverageStrategy,
    MomentumStrategy,
    TripleMovingAverageStrategy,
    
    # 전략 메타데이터
    STRATEGIES
)

from .active_strategies import (
    # 활발한 거래 전략들
    ShortTermTrend,
    SensitiveRSI,
    FastBreakout,
    MidTermTrend,
    VolumeBreakout,
    
    # 활발한 전략 메타데이터
    ACTIVE_STRATEGIES
)

# 모든 전략을 하나로 합침
ALL_STRATEGIES = {**STRATEGIES, **ACTIVE_STRATEGIES}

__all__ = [
    # 기본 전략
    'TrendFollowing',
    'RSIStrategy',
    'MACDStrategy', 
    'BollingerBandsStrategy',
    'MeanReversionStrategy',
    'GoldenCrossStrategy',
    'BreakoutStrategy',
    'DualMovingAverageStrategy',
    'MomentumStrategy',
    'TripleMovingAverageStrategy',
    'STRATEGIES',
    
    # 활발한 전략
    'ShortTermTrend',
    'SensitiveRSI', 
    'FastBreakout',
    'MidTermTrend',
    'VolumeBreakout',
    'ACTIVE_STRATEGIES',
    
    # 통합
    'ALL_STRATEGIES'
]