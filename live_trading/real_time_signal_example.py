"""
실시간 신호 감지 시스템 예시 구현
이 파일은 실제 거래 신호를 감지하고 알림을 보내는 기본적인 구조를 제공합니다.
"""

import yfinance as yf
import pandas as pd
import time
import smtplib
import requests
import json
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
import sys
import os

# 상위 디렉토리의 strategies 모듈을 import하기 위해 경로 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies import ALL_STRATEGIES as STRATEGIES

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SignalDetector:
    """실시간 신호 감지 클래스"""
    
    def __init__(self, strategy_class, params):
        self.strategy_class = strategy_class
        self.params = params
        self.last_signal = None
        
        # 전략 매개변수 설정
        for param_key, param_value in params.items():
            setattr(self.strategy_class, param_key, param_value)
    
    def get_signal_state(self, data):
        """현재 데이터에서 신호 상태 확인"""
        if len(data) < 100:  # 충분한 데이터가 없으면 HOLD
            return 'HOLD'
            
        try:
            # 간단한 이동평균 교차 로직 (예시)
            if hasattr(self.strategy_class, 'short_ma') and hasattr(self.strategy_class, 'long_ma'):
                short_ma = data['Close'].rolling(self.strategy_class.short_ma).mean()
                long_ma = data['Close'].rolling(self.strategy_class.long_ma).mean()
                
                if short_ma.iloc[-1] > long_ma.iloc[-1] and short_ma.iloc[-2] <= long_ma.iloc[-2]:
                    return 'BUY'
                elif short_ma.iloc[-1] < long_ma.iloc[-1] and short_ma.iloc[-2] >= long_ma.iloc[-2]:
                    return 'SELL'
            
            # RSI 기반 신호 (예시)
            if hasattr(self.strategy_class, 'rsi_upper') and hasattr(self.strategy_class, 'rsi_lower'):
                rsi = self.calculate_rsi(data['Close'], 14)
                if rsi.iloc[-1] < self.strategy_class.rsi_lower:
                    return 'BUY'
                elif rsi.iloc[-1] > self.strategy_class.rsi_upper:
                    return 'SELL'
                    
        except Exception as e:
            logger.error(f"Signal calculation error: {e}")
            
        return 'HOLD'
    
    def calculate_rsi(self, prices, period=14):
        """RSI 계산"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def check_signal(self, data):
        """신호 변화 체크"""
        try:
            current_signal = self.get_signal_state(data)
            
            # 신호 변화가 있고, HOLD가 아닌 경우에만 알림
            if current_signal != self.last_signal and current_signal != 'HOLD':
                signal_info = {
                    'action': current_signal,
                    'price': float(data['Close'].iloc[-1]),
                    'timestamp': datetime.now(),
                    'confidence': self.calculate_confidence(data, current_signal)
                }
                
                self.last_signal = current_signal
                return signal_info
                
        except Exception as e:
            logger.error(f"Error checking signal: {e}")
            
        return None
    
    def calculate_confidence(self, data, signal):
        """신호 신뢰도 계산 (0.0 ~ 1.0)"""
        try:
            # 볼륨 기반 신뢰도
            avg_volume = data['Volume'].rolling(20).mean().iloc[-1]
            current_volume = data['Volume'].iloc[-1]
            volume_confidence = min(current_volume / avg_volume, 2.0) / 2.0
            
            # 추세 강도 기반 신뢰도 (예시)
            price_change = (data['Close'].iloc[-1] - data['Close'].iloc[-5]) / data['Close'].iloc[-5]
            trend_confidence = min(abs(price_change) * 10, 1.0)
            
            return (volume_confidence + trend_confidence) / 2
            
        except:
            return 0.5


class EmailAlert:
    """이메일 알림 클래스"""
    
    def __init__(self, smtp_server, port, email, password):
        self.smtp_server = smtp_server
        self.port = port
        self.email = email
        self.password = password
    
    def send_signal_alert(self, ticker, signals):
        """신호 알림 이메일 발송"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email
            msg['To'] = self.email
            msg['Subject'] = f"🚨 거래 신호 발생: {ticker}"
            
            # HTML 이메일 본문 생성
            body = self.create_email_body(ticker, signals)
            msg.attach(MIMEText(body, 'html', 'utf-8'))
            
            with smtplib.SMTP(self.smtp_server, self.port) as server:
                server.starttls()
                server.login(self.email, self.password)
                server.send_message(msg)
                
            logger.info(f"Email alert sent for {ticker}")
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
    
    def create_email_body(self, ticker, signals):
        """이메일 본문 생성"""
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .header {{ background-color: #f4f4f4; padding: 20px; text-align: center; }}
                .signal {{ margin: 20px; padding: 15px; border: 1px solid #ddd; }}
                .buy {{ background-color: #e8f5e8; }}
                .sell {{ background-color: #ffe8e8; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>🎯 거래 신호: {ticker}</h2>
                <p>발생 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        """
        
        for strategy_name, signal in signals.items():
            action_class = "buy" if signal['action'] == 'BUY' else "sell"
            emoji = "📈" if signal['action'] == 'BUY' else "📉"
            
            html += f"""
            <div class="signal {action_class}">
                <h3>{emoji} {strategy_name}</h3>
                <p><strong>신호:</strong> {signal['action']}</p>
                <p><strong>가격:</strong> ${signal['price']:.2f}</p>
                <p><strong>신뢰도:</strong> {signal['confidence']:.1%}</p>
            </div>
            """
        
        html += """
            <div style="margin: 20px; padding: 15px; background-color: #fff3cd;">
                <p><strong>⚠️ 주의사항:</strong></p>
                <ul>
                    <li>이 신호는 자동으로 생성된 것으로, 투자 결정에 참고용으로만 사용하세요.</li>
                    <li>실제 투자 전에 추가적인 분석과 검토가 필요합니다.</li>
                    <li>손실에 대한 책임은 투자자 본인에게 있습니다.</li>
                </ul>
            </div>
        </body>
        </html>
        """
        
        return html


class TelegramBot:
    """텔레그램 봇 클래스"""
    
    def __init__(self, bot_token, chat_id):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{bot_token}"
    
    def send_signal_alert(self, ticker, signals):
        """텔레그램 신호 알림"""
        try:
            message = f"🎯 <b>{ticker}</b> 거래 신호\n"
            message += f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            
            for strategy_name, signal in signals.items():
                emoji = "🟢" if signal['action'] == 'BUY' else "🔴"
                message += f"{emoji} <b>{strategy_name}</b>\n"
                message += f"📊 신호: <code>{signal['action']}</code>\n"
                message += f"💰 가격: <code>${signal['price']:.2f}</code>\n"
                message += f"🎯 신뢰도: <code>{signal['confidence']:.1%}</code>\n\n"
            
            message += "⚠️ <i>이 신호는 참고용입니다. 투자는 신중히 결정하세요.</i>"
            
            self.send_message(message)
            logger.info(f"Telegram alert sent for {ticker}")
            
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")
    
    def send_message(self, text):
        """텔레그램 메시지 발송"""
        url = f"{self.api_url}/sendMessage"
        payload = {
            'chat_id': self.chat_id,
            'text': text,
            'parse_mode': 'HTML'
        }
        return requests.post(url, json=payload)


class RealTimeMonitor:
    """실시간 모니터링 클래스"""
    
    def __init__(self, tickers, strategies_config, alert_systems, update_interval=300):
        self.tickers = tickers
        self.strategies_config = strategies_config
        self.alert_systems = alert_systems
        self.update_interval = update_interval  # 5분 간격
        self.signal_detectors = {}
        
        # 각 전략별 신호 감지기 초기화
        for strategy_name, config in strategies_config.items():
            strategy_class = STRATEGIES[strategy_name]['class']
            self.signal_detectors[strategy_name] = SignalDetector(
                strategy_class, config['params']
            )
    
    def get_latest_data(self, ticker, period="5d", interval="5m"):
        """최신 데이터 가져오기"""
        try:
            data = yf.download(ticker, period=period, interval=interval, progress=False)
            
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.droplevel(1)
                
            return data
            
        except Exception as e:
            logger.error(f"Error fetching data for {ticker}: {e}")
            return None
    
    def check_signals_for_ticker(self, ticker):
        """특정 티커의 신호 체크"""
        data = self.get_latest_data(ticker)
        if data is None or data.empty:
            return {}
        
        signals = {}
        for strategy_name, detector in self.signal_detectors.items():
            try:
                signal = detector.check_signal(data)
                if signal:
                    signals[strategy_name] = signal
                    logger.info(f"Signal detected: {ticker} - {strategy_name} - {signal['action']}")
                    
            except Exception as e:
                logger.error(f"Error checking {strategy_name} for {ticker}: {e}")
        
        return signals
    
    def send_alerts(self, ticker, signals):
        """알림 발송"""
        for alert_system in self.alert_systems:
            try:
                alert_system.send_signal_alert(ticker, signals)
            except Exception as e:
                logger.error(f"Alert system error: {e}")
    
    def run_single_check(self):
        """단일 체크 실행"""
        logger.info("Starting signal check cycle...")
        
        for ticker in self.tickers:
            try:
                signals = self.check_signals_for_ticker(ticker)
                
                if signals:
                    logger.info(f"Signals found for {ticker}: {list(signals.keys())}")
                    self.send_alerts(ticker, signals)
                    
            except Exception as e:
                logger.error(f"Error processing {ticker}: {e}")
        
        logger.info("Signal check cycle completed")
    
    def run_continuous_monitoring(self):
        """지속적인 모니터링 실행"""
        logger.info("Starting continuous monitoring...")
        
        while True:
            try:
                self.run_single_check()
                logger.info(f"Waiting {self.update_interval} seconds...")
                time.sleep(self.update_interval)
                
            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Unexpected error in monitoring loop: {e}")
                time.sleep(60)  # 1분 대기 후 재시작


# 사용 예시
if __name__ == "__main__":
    # 설정 정보
    CONFIG = {
        'tickers': ['AAPL', 'TSLA', 'MSFT', 'GOOGL'],
        'strategies': {
            'TrendFollowing': {
                'params': {'short_ma': 20, 'long_ma': 50}
            },
            'RSIStrategy': {
                'params': {'rsi_period': 14, 'rsi_upper': 70, 'rsi_lower': 30}
            }
        },
        'alerts': {
            'email': {
                'smtp_server': 'smtp.gmail.com',
                'port': 587,
                'email': 'your_email@gmail.com',
                'password': 'your_app_password'  # Gmail 앱 비밀번호
            },
            'telegram': {
                'bot_token': 'YOUR_BOT_TOKEN',
                'chat_id': 'YOUR_CHAT_ID'
            }
        },
        'update_interval': 300  # 5분
    }
    
    # 알림 시스템 초기화
    alert_systems = []
    
    if CONFIG['alerts']['email']['email'] != 'your_email@gmail.com':
        alert_systems.append(EmailAlert(**CONFIG['alerts']['email']))
    
    if CONFIG['alerts']['telegram']['bot_token'] != 'YOUR_BOT_TOKEN':
        alert_systems.append(TelegramBot(**CONFIG['alerts']['telegram']))
    
    # 모니터링 시스템 시작
    if alert_systems:
        monitor = RealTimeMonitor(
            tickers=CONFIG['tickers'],
            strategies_config=CONFIG['strategies'],
            alert_systems=alert_systems,
            update_interval=CONFIG['update_interval']
        )
        
        # 단일 체크 실행 (테스트용)
        print("Running single check...")
        monitor.run_single_check()
        
        # 지속적인 모니터링 시작 (실제 운영용)
        # monitor.run_continuous_monitoring()
    else:
        print("No alert systems configured. Please update CONFIG with your credentials.")