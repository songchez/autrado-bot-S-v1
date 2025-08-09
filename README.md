# 🎯 통합 주식 거래 시스템

**백테스팅부터 실시간 신호까지 - 완전한 주식 거래 솔루션**

## 📋 프로젝트 개요

이 프로젝트는 두 가지 핵심 기능을 제공합니다:

1. **📊 백테스팅 시스템**: 10가지 전략으로 과거 데이터 분석 및 성과 검증
2. **🚨 실시간 신호 모니터링**: 실제 시장에서 거래 신호 감지 및 알림

## 🗂️ 프로젝트 구조

```
backtest-bot-v1/
├── 🎯 strategies/           # 공통 전략 모듈 ⭐
│   ├── __init__.py         # 전략 패키지 초기화
│   ├── base.py             # 기본 클래스 & 유틸리티
│   └── strategies.py       # 거래 전략들 (10가지)
│
├── 📊 backtesting/          # 백테스팅 관련
│   ├── multi_strategy_app.py # 메인 GUI 앱
│   ├── streamlit_app.py     # 단순 버전 GUI
│   ├── multilang_app.py     # 다국어 GUI
│   ├── backtesting_bot.py   # 콘솔 버전
│   └── run_gui.py          # GUI 실행 스크립트 ⭐
│
├── 🚨 live_trading/         # 실시간 모니터링
│   ├── live_trading_bot.py  # 메인 모니터링 봇
│   ├── real_time_signal_example.py # 신호 감지 엔진
│   └── run_monitor.py      # 모니터링 실행 스크립트 ⭐
│
├── ⚙️ config/              # 설정 관리
│   ├── config.py           # 설정 관리 클래스
│   └── .env.example        # 환경변수 템플릿
│
├── 📚 docs/                # 문서
│   ├── setup_guide.md      # Gmail/텔레그램 설정
│   ├── setup_instructions.md # 완전한 사용법
│   └── trading_system_guide.md # 시스템 아키텍처
│
├── 🎨 examples/            # 예제 (향후 확장)
├── 📄 requirements.txt     # 패키지 의존성
├── 📄 pyproject.toml      # UV 프로젝트 설정
├── 📄 README.md           # 이 파일
└── 📄 USAGE.md            # 상세 사용법
```

## 🚀 빠른 시작

### 1️⃣ 백테스팅 GUI 실행

```bash
# 방법 1: 스크립트로 실행 (권장)
python backtesting/run_gui.py

# 방법 2: 직접 실행
cd backtesting
uv run streamlit run multi_strategy_app.py
```

**결과**: 브라우저에서 http://localhost:8501 열림

### 2️⃣ 실시간 신호 모니터링 시작

```bash
# 1. 환경설정 (최초 1회)
cp config/.env.example .env
# .env 파일에 Gmail/텔레그램 정보 입력

# 2. 모니터링 시작
python live_trading/run_monitor.py
```

**결과**: 텔레그램으로 실시간 거래 신호 수신

## 📊 백테스팅 시스템

### 🎯 지원 전략 (10가지)

| 전략명 | 설명 | 적합한 시장 |
|--------|------|-------------|
| **추세 추종** | 이동평균 교차 | 추세 시장 |
| **RSI** | 과매수/과매도 | 횡보 시장 |
| **MACD** | 모멘텀 교차 | 중기 추세 |
| **볼린저 밴드** | 평균회귀 | 변동성 시장 |
| **평균회귀** | 표준편차 기반 | 안정적 자산 |
| **골든크로스** | 50/200일선 | 장기 추세 |
| **돌파** | 고저점 돌파 | 모멘텀 시장 |
| **이중 이동평균** | 단기 교차 | 활발한 시장 |
| **모멘텀** | 가격 모멘텀 | 강한 추세 |
| **삼중 이동평균** | 3선 정렬 | 확실한 추세 |

### 🌐 다국어 지원
- **English**: 영어 인터페이스
- **한국어**: 한글 인터페이스

## 🚨 실시간 신호 모니터링

### 📱 알림 시스템
- **📧 이메일**: Gmail SMTP 연동
- **📱 텔레그램**: 봇을 통한 즉시 알림

### 🔔 알림 예시
```
🎯 AAPL 거래 신호
⏰ 2024-01-15 14:30:25

🟢 TrendFollowing
📊 신호: BUY
💰 가격: $150.25
🎯 신뢰도: 85%
```

## 🛠️ 설치 및 설정

### 📦 패키지 설치
```bash
# UV 사용 (권장)
uv sync

# 또는 pip 사용
pip install -r requirements.txt
```

### ⚙️ 환경 설정
1. **환경변수 파일 생성**: `cp config/.env.example .env`
2. **Gmail 설정** (선택): 앱 비밀번호 발급
3. **텔레그램 봇 설정** (선택): 봇 토큰 및 Chat ID 확보

자세한 설정: [docs/setup_guide.md](docs/setup_guide.md)

## 🎮 사용법

### 백테스팅
```bash
python backtesting/run_gui.py
# → http://localhost:8501 접속
```

### 실시간 모니터링  
```bash
python live_trading/run_monitor.py --test    # 테스트
python live_trading/run_monitor.py           # 실행
```

## ⚠️ 주의사항

1. **투자 참고용**: 모든 신호는 참고용으로만 사용하세요
2. **리스크 관리**: 손실 감수 범위 내에서만 투자하세요
3. **지속적인 검토**: 시장 상황에 따라 전략을 조정하세요
4. **보안**: `.env` 파일을 공개 저장소에 올리지 마세요
5. **개인 책임**: 모든 투자 결정과 그에 따른 책임은 개인에게 있습니다

---

<div align="center">

**⭐ 유용하다면 Star를 눌러주세요!**

**Made with ❤️ for traders**

</div>
# autrado-bot-S-v1
