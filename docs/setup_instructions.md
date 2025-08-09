# 🎯 실시간 거래 신호 봇 설정 및 실행 가이드

## 📋 단계별 설정 방법

### 1단계: 환경 설정 파일 생성

```bash
# .env.example을 .env로 복사
cp .env.example .env
```

`.env` 파일을 열고 아래 정보를 입력하세요:

```env
# Gmail 설정
EMAIL_ADDRESS=your_gmail@gmail.com
EMAIL_PASSWORD=your_16_digit_app_password

# 텔레그램 설정  
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789

# 모니터링할 종목 (쉼표로 구분)
TICKERS=AAPL,TSLA,MSFT,GOOGL,NVDA

# 업데이트 간격 (초)
UPDATE_INTERVAL=300
```

### 2단계: Gmail 앱 비밀번호 설정

1. **Gmail 계정 로그인** → **Google 계정 관리**
2. **보안** → **2단계 인증** 활성화
3. **앱 비밀번호** 생성
   - 앱: 메일
   - 기기: 기타 (Trading Bot)
   - **16자리 비밀번호를 .env 파일에 입력**

### 3단계: 텔레그램 봇 생성

1. **텔레그램에서 @BotFather 검색**
2. **새 봇 생성**:
   ```
   /newbot
   봇 이름: My Trading Signal Bot
   사용자명: my_trading_signal_bot
   ```
3. **토큰을 .env 파일에 입력**
4. **Chat ID 확인**:
   - 봇과 채팅 시작 (아무 메시지 전송)
   - 브라우저에서 방문: `https://api.telegram.org/bot<토큰>/getUpdates`
   - Chat ID를 .env 파일에 입력

### 4단계: 봇 실행 및 테스트

```bash
# 설정 확인
python live_trading_bot.py --config

# 알림 테스트
python live_trading_bot.py --test

# 실제 모니터링 시작
python live_trading_bot.py
```

## 🚀 실행 명령어

| 명령어 | 설명 |
|--------|------|
| `python live_trading_bot.py` | 실시간 모니터링 시작 |
| `python live_trading_bot.py --test` | 알림 시스템 테스트 |
| `python live_trading_bot.py --config` | 설정 확인 |
| `python live_trading_bot.py --help` | 도움말 보기 |

## 📊 모니터링 현황

실행하면 다음과 같은 정보가 표시됩니다:

```
============================================================
🎯 실시간 거래 신호 모니터링 봇
============================================================
📊 모니터링 종목: AAPL, TSLA, MSFT, GOOGL, NVDA
⏰ 업데이트 간격: 300초
📈 활성 전략: 3개
🔔 알림 시스템: email, telegram
============================================================
```

## 🔔 알림 예시

### 이메일 알림
- **제목**: 🚨 거래 신호 발생: AAPL
- **내용**: HTML 형식의 상세 신호 정보

### 텔레그램 알림
```
🎯 AAPL 거래 신호
⏰ 2024-01-15 14:30:25

🟢 TrendFollowing
📊 신호: BUY
💰 가격: $150.25
🎯 신뢰도: 85%

⚠️ 이 신호는 참고용입니다. 투자는 신중히 결정하세요.
```

## ⚙️ 고급 설정

### 전략 매개변수 조정

`.env` 파일에 추가 설정:

```env
# 추세 추종 전략
TREND_SHORT_MA=20
TREND_LONG_MA=50

# RSI 전략
RSI_PERIOD=14
RSI_UPPER=70
RSI_LOWER=30

# MACD 전략
MACD_FAST=12
MACD_SLOW=26
MACD_SIGNAL=9
```

### 로그 레벨 설정

```env
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
```

## 🛑 주의사항

1. **투자 참고용**: 자동 생성 신호는 참고용으로만 사용
2. **리스크 관리**: 손실 감수 범위 내에서만 투자
3. **지속적인 모니터링**: 시장 상황 변화에 따른 전략 조정 필요
4. **보안**: .env 파일을 GitHub 등에 업로드하지 마세요

## 🔧 문제 해결

### 일반적인 오류

1. **ImportError**: `pip install python-dotenv` 실행
2. **이메일 전송 실패**: Gmail 앱 비밀번호 재확인
3. **텔레그램 실패**: 봇 토큰과 Chat ID 재확인
4. **데이터 수집 실패**: 인터넷 연결 및 종목 심볼 확인

### 로그 확인

```bash
# 실시간 로그 확인
tail -f trading_bot.log
```

## 📈 다음 단계

1. **클라우드 배포**: AWS, GCP에서 24/7 실행
2. **웹 대시보드**: 실시간 신호 현황 시각화
3. **자동 거래**: 브로커 API 연동
4. **성과 추적**: 신호 정확도 및 수익률 분석