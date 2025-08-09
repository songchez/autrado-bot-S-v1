# 🚀 실시간 투자 신호 시스템 구축 가이드

## 시스템 아키텍처

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Data Sources   │ -> │ Signal Engine   │ -> │ Alert System    │
│                 │    │                 │    │                 │
│ • Yahoo Finance │    │ • Strategy      │    │ • Email         │
│ • Alpha Vantage │    │ • Signal        │    │ • Slack         │
│ • 한국투자증권   │    │   Detection     │    │ • Telegram      │
│ • 키움증권      │    │ • Multi-ticker  │    │ • KakaoTalk     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                  |
                       ┌─────────────────┐
                       │ Trading Engine  │
                       │                 │
                       │ • Auto Trading  │
                       │ • Risk Mgmt     │
                       │ • Portfolio     │
                       └─────────────────┘
```

## 1단계: 실시간 데이터 수집 및 신호 감지

### 필요한 패키지
```python
# requirements_live.txt
streamlit
yfinance
websocket-client
schedule
smtplib  # 이메일
requests  # Slack, Telegram
APScheduler  # 스케줄링
redis  # 캐싱
sqlalchemy  # 데이터베이스
pandas-ta  # 기술적 지표
```

### 핵심 기능 구현 방향

#### A) 실시간 데이터 모니터링
```python
import yfinance as yf
import time
from datetime import datetime
import pandas as pd

class RealTimeMonitor:
    def __init__(self, tickers, strategies, update_interval=60):
        self.tickers = tickers  # ['AAPL', 'TSLA', 'MSFT']
        self.strategies = strategies
        self.update_interval = update_interval
        
    def get_latest_data(self, ticker, period="1d", interval="1m"):
        """실시간 데이터 수집"""
        return yf.download(ticker, period=period, interval=interval)
    
    def check_signals(self, ticker, data):
        """각 전략별 신호 체크"""
        signals = {}
        for strategy_name, strategy in self.strategies.items():
            signal = strategy.check_signal(data)
            if signal:
                signals[strategy_name] = signal
        return signals
    
    def run_monitoring(self):
        """모니터링 루프 실행"""
        while True:
            for ticker in self.tickers:
                data = self.get_latest_data(ticker)
                signals = self.check_signals(ticker, data)
                
                if signals:
                    self.send_alerts(ticker, signals)
                    
            time.sleep(self.update_interval)
```

#### B) 신호 감지 클래스 개선
```python
class SignalDetector:
    def __init__(self, strategy_class, params):
        self.strategy_class = strategy_class
        self.params = params
        
    def check_signal(self, data):
        """실시간 신호 체크"""
        if len(data) < max(self.params.values()):
            return None
            
        # 마지막 2개 데이터로 신호 변화 체크
        prev_data = data[:-1]
        curr_data = data
        
        prev_signal = self.get_signal_state(prev_data)
        curr_signal = self.get_signal_state(curr_data)
        
        # 신호 변화가 있을 때만 알림
        if prev_signal != curr_signal:
            return {
                'action': curr_signal,  # 'BUY', 'SELL', 'HOLD'
                'price': data['Close'].iloc[-1],
                'timestamp': datetime.now(),
                'confidence': self.calculate_confidence(data)
            }
        return None
```

## 2단계: 알림 시스템 구현

### A) 이메일 알림
```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailAlert:
    def __init__(self, smtp_server, port, email, password):
        self.smtp_server = smtp_server
        self.port = port
        self.email = email
        self.password = password
    
    def send_signal_alert(self, ticker, signals):
        msg = MIMEMultipart()
        msg['From'] = self.email
        msg['To'] = self.email
        msg['Subject'] = f"🚨 거래 신호: {ticker}"
        
        body = self.format_signal_message(ticker, signals)
        msg.attach(MIMEText(body, 'html'))
        
        with smtplib.SMTP(self.smtp_server, self.port) as server:
            server.starttls()
            server.login(self.email, self.password)
            server.send_message(msg)
```

### B) 텔레그램 봇
```python
import requests

class TelegramBot:
    def __init__(self, bot_token, chat_id):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{bot_token}"
    
    def send_message(self, text):
        url = f"{self.api_url}/sendMessage"
        payload = {
            'chat_id': self.chat_id,
            'text': text,
            'parse_mode': 'HTML'
        }
        return requests.post(url, json=payload)
    
    def send_signal_alert(self, ticker, signals):
        message = f"🎯 <b>{ticker}</b> 거래 신호\n\n"
        for strategy, signal in signals.items():
            emoji = "🟢" if signal['action'] == 'BUY' else "🔴"
            message += f"{emoji} <b>{strategy}</b>\n"
            message += f"신호: {signal['action']}\n"
            message += f"가격: ${signal['price']:.2f}\n"
            message += f"시간: {signal['timestamp'].strftime('%Y-%m-%d %H:%M')}\n\n"
        
        self.send_message(message)
```

## 3단계: 실제 거래 연동 (한국 시장)

### A) 한국투자증권 API 연동 예시
```python
import requests
import json
from datetime import datetime

class KISTrading:
    def __init__(self, app_key, app_secret, account_no):
        self.app_key = app_key
        self.app_secret = app_secret
        self.account_no = account_no
        self.base_url = "https://openapi.koreainvestment.com:9443"
        self.access_token = self.get_access_token()
    
    def get_access_token(self):
        """OAuth 토큰 획득"""
        url = f"{self.base_url}/oauth2/tokenP"
        headers = {"Content-Type": "application/json"}
        data = {
            "grant_type": "client_credentials",
            "appkey": self.app_key,
            "appsecret": self.app_secret
        }
        response = requests.post(url, headers=headers, data=json.dumps(data))
        return response.json()['access_token']
    
    def place_order(self, ticker, order_type, quantity, price=None):
        """주문 실행"""
        url = f"{self.base_url}/uapi/domestic-stock/v1/trading/order-cash"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "appkey": self.app_key,
            "appsecret": self.app_secret,
            "tr_id": "TTTC0802U" if order_type == 'BUY' else "TTTC0801U"
        }
        
        data = {
            "CANO": self.account_no,
            "ACNT_PRDT_CD": "01",
            "PDNO": ticker,
            "ORD_DVSN": "01",  # 시장가
            "ORD_QTY": str(quantity),
            "ORD_UNPR": str(price) if price else "0"
        }
        
        return requests.post(url, headers=headers, json=data)
```

## 4단계: 통합 거래 시스템

### 메인 거래 시스템 클래스
```python
class AutoTradingSystem:
    def __init__(self, config):
        self.config = config
        self.monitor = RealTimeMonitor(
            tickers=config['tickers'],
            strategies=config['strategies']
        )
        self.alerts = {
            'email': EmailAlert(**config['email']),
            'telegram': TelegramBot(**config['telegram'])
        }
        self.broker = KISTrading(**config['kis']) if config.get('auto_trade') else None
        self.positions = {}  # 포지션 관리
        
    def handle_signal(self, ticker, signals):
        """신호 처리 및 거래 실행"""
        # 1. 알림 발송
        for alert_system in self.alerts.values():
            alert_system.send_signal_alert(ticker, signals)
        
        # 2. 자동 거래 (옵션)
        if self.broker and self.config.get('auto_trade', False):
            for strategy_name, signal in signals.items():
                self.execute_trade(ticker, signal, strategy_name)
        
        # 3. 로그 저장
        self.log_signal(ticker, signals)
    
    def execute_trade(self, ticker, signal, strategy_name):
        """실제 거래 실행"""
        position_size = self.calculate_position_size(ticker, signal)
        
        if signal['action'] == 'BUY' and ticker not in self.positions:
            # 매수 주문
            result = self.broker.place_order(ticker, 'BUY', position_size)
            if result.status_code == 200:
                self.positions[ticker] = {
                    'quantity': position_size,
                    'entry_price': signal['price'],
                    'strategy': strategy_name,
                    'timestamp': signal['timestamp']
                }
                
        elif signal['action'] == 'SELL' and ticker in self.positions:
            # 매도 주문
            quantity = self.positions[ticker]['quantity']
            result = self.broker.place_order(ticker, 'SELL', quantity)
            if result.status_code == 200:
                # 포지션 정리 및 수익률 계산
                profit = self.calculate_profit(ticker, signal['price'])
                del self.positions[ticker]
                self.log_trade_result(ticker, profit)
```

## 5단계: 배포 및 운영

### A) Docker를 이용한 배포
```dockerfile
# Dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements_live.txt .
RUN pip install -r requirements_live.txt

COPY . .

CMD ["python", "main.py"]
```

### B) 클라우드 배포 (AWS/GCP)
- **AWS Lambda**: 서버리스 신호 감지
- **AWS SQS**: 신호 큐잉 시스템  
- **AWS RDS**: 거래 데이터 저장
- **AWS CloudWatch**: 모니터링 및 알림

### C) 24/7 모니터링 설정
```python
# main.py
import schedule
import time

def run_market_hours_monitoring():
    """장중 모니터링"""
    trading_system = AutoTradingSystem(config)
    trading_system.start_monitoring()

def run_after_hours_analysis():
    """장후 분석"""
    # 일일 성과 분석
    # 다음날 전략 준비
    pass

# 스케줄링
schedule.every().monday.at("09:00").do(run_market_hours_monitoring)
schedule.every().tuesday.at("09:00").do(run_market_hours_monitoring)
# ... 평일 모든 날

schedule.every().day.at("16:00").do(run_after_hours_analysis)

while True:
    schedule.run_pending()
    time.sleep(60)
```

## 보안 및 리스크 관리

### 1. API 키 보안
```python
# config.py
import os
from dotenv import load_dotenv

load_dotenv()

CONFIG = {
    'kis': {
        'app_key': os.getenv('KIS_APP_KEY'),
        'app_secret': os.getenv('KIS_APP_SECRET'),
        'account_no': os.getenv('KIS_ACCOUNT_NO')
    },
    'telegram': {
        'bot_token': os.getenv('TELEGRAM_BOT_TOKEN'),
        'chat_id': os.getenv('TELEGRAM_CHAT_ID')
    }
}
```

### 2. 리스크 관리 규칙
```python
class RiskManager:
    def __init__(self, max_position_size=0.1, max_daily_loss=0.05):
        self.max_position_size = max_position_size  # 10% 최대 포지션
        self.max_daily_loss = max_daily_loss        # 5% 최대 일일 손실
        
    def check_position_size(self, total_capital, signal_strength):
        """포지션 사이즈 계산"""
        base_size = total_capital * self.max_position_size
        adjusted_size = base_size * signal_strength  # 신호 강도에 따른 조정
        return min(adjusted_size, total_capital * 0.2)  # 최대 20% 제한
```

이런 방식으로 단계별로 발전시키면 백테스팅 봇을 실제 투자에 활용할 수 있는 완전한 시스템으로 구축할 수 있습니다.