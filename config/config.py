"""
설정 관리 모듈
환경 변수와 기본 설정을 관리합니다.
"""

import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class Config:
    """설정 클래스"""
    
    # 이메일 설정
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS', '')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')
    
    # 텔레그램 설정
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')
    
    # 모니터링 설정
    TICKERS = os.getenv('TICKERS', 'AAPL,TSLA,MSFT').split(',')
    UPDATE_INTERVAL = int(os.getenv('UPDATE_INTERVAL', 300))  # 5분
    
    # 로그 설정
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # 전략 설정
    STRATEGIES_CONFIG = {
        'TrendFollowing': {
            'params': {
                'short_ma': int(os.getenv('TREND_SHORT_MA', 20)),
                'long_ma': int(os.getenv('TREND_LONG_MA', 50))
            }
        },
        'RSIStrategy': {
            'params': {
                'rsi_period': int(os.getenv('RSI_PERIOD', 14)),
                'rsi_upper': int(os.getenv('RSI_UPPER', 70)),
                'rsi_lower': int(os.getenv('RSI_LOWER', 30))
            }
        },
        'MACDStrategy': {
            'params': {
                'fast_period': int(os.getenv('MACD_FAST', 12)),
                'slow_period': int(os.getenv('MACD_SLOW', 26)),
                'signal_period': int(os.getenv('MACD_SIGNAL', 9))
            }
        }
    }
    
    @classmethod
    def validate_config(cls):
        """설정 유효성 검사"""
        errors = []
        
        if not cls.EMAIL_ADDRESS or '@' not in cls.EMAIL_ADDRESS:
            errors.append("올바른 이메일 주소를 설정해주세요 (EMAIL_ADDRESS)")
            
        if not cls.EMAIL_PASSWORD:
            errors.append("Gmail 앱 비밀번호를 설정해주세요 (EMAIL_PASSWORD)")
            
        if not cls.TELEGRAM_BOT_TOKEN:
            errors.append("텔레그램 봇 토큰을 설정해주세요 (TELEGRAM_BOT_TOKEN)")
            
        if not cls.TELEGRAM_CHAT_ID:
            errors.append("텔레그램 채팅 ID를 설정해주세요 (TELEGRAM_CHAT_ID)")
            
        return errors
    
    @classmethod
    def is_email_configured(cls):
        """이메일 설정 여부 확인"""
        return bool(cls.EMAIL_ADDRESS and cls.EMAIL_PASSWORD and '@' in cls.EMAIL_ADDRESS)
    
    @classmethod
    def is_telegram_configured(cls):
        """텔레그램 설정 여부 확인"""
        return bool(cls.TELEGRAM_BOT_TOKEN and cls.TELEGRAM_CHAT_ID)
    
    @classmethod
    def get_configured_alerts(cls):
        """설정된 알림 시스템 목록 반환"""
        alerts = []
        
        if cls.is_email_configured():
            alerts.append('email')
            
        if cls.is_telegram_configured():
            alerts.append('telegram')
            
        return alerts