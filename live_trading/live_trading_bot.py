#!/usr/bin/env python3
"""
실시간 거래 신호 모니터링 봇
사용법: python live_trading_bot.py
"""

import sys
import signal
import time
from datetime import datetime
import logging
import os

# 상위 디렉토리의 config 모듈을 import하기 위해 경로 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import Config
from real_time_signal_example import RealTimeMonitor, EmailAlert, TelegramBot
from utils.monitoring_storage import MonitoringStorage

# 로깅 설정
def setup_logging():
    """로깅 설정"""
    log_level = getattr(logging, Config.LOG_LEVEL.upper(), logging.INFO)
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('trading_bot.log', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)


def create_alert_systems():
    """알림 시스템 생성"""
    alert_systems = []
    
    # 이메일 알림 시스템
    if Config.is_email_configured():
        try:
            email_alert = EmailAlert(
                smtp_server=Config.SMTP_SERVER,
                port=Config.SMTP_PORT,
                email=Config.EMAIL_ADDRESS,
                password=Config.EMAIL_PASSWORD
            )
            alert_systems.append(email_alert)
            print(f"✅ 이메일 알림 설정됨: {Config.EMAIL_ADDRESS}")
        except Exception as e:
            print(f"❌ 이메일 알림 설정 실패: {e}")
    
    # 텔레그램 알림 시스템  
    if Config.is_telegram_configured():
        try:
            telegram_bot = TelegramBot(
                bot_token=Config.TELEGRAM_BOT_TOKEN,
                chat_id=Config.TELEGRAM_CHAT_ID
            )
            alert_systems.append(telegram_bot)
            print(f"✅ 텔레그램 알림 설정됨: Chat ID {Config.TELEGRAM_CHAT_ID}")
        except Exception as e:
            print(f"❌ 텔레그램 알림 설정 실패: {e}")
    
    return alert_systems


def signal_handler(signum, frame):
    """프로그램 종료 시그널 처리"""
    print("\n🛑 프로그램을 종료합니다...")
    sys.exit(0)


def print_banner():
    """시작 배너 출력"""
    print("=" * 60)
    print("🎯 Enhanced 실시간 모니터링 봇 (Storage 통합)")
    print("=" * 60)


def print_help():
    """도움말 출력"""
    print("""
🚀 실시간 거래 신호 봇 사용법

1. 환경 설정:
   - .env.example 파일을 .env로 복사
   - Gmail 앱 비밀번호와 텔레그램 봇 정보 입력
   
2. 실행:
   python live_trading_bot.py
   
3. 테스트 실행:
   python live_trading_bot.py --test
   
4. 설정 확인:
   python live_trading_bot.py --config
   
자세한 설정 방법은 setup_guide.md 파일을 참조하세요.
    """)


def run_configuration_check():
    """설정 확인 및 테스트 (Storage 통합)"""
    print("🔧 설정 확인 중...")
    
    # Storage 확인
    try:
        storage = MonitoringStorage()
        stats = storage.get_monitoring_stats()
        print(f"💾 Storage OK: {stats['total']} total configurations")
    except Exception as e:
        print(f"❌ Storage 오류: {e}")
        return False
    
    print("✅ 기본 설정이 완료되었습니다!")
    return True


def run_test_mode():
    """테스트 모드 실행 (Storage 통합)"""
    print("🧪 테스트 모드로 실행합니다...")
    
    # Storage 상태 확인
    storage = MonitoringStorage()
    summary = storage.get_monitoring_stats()
    print(f"📊 Storage Status: {summary}")
    
    # 알림 시스템 생성
    alert_systems = create_alert_systems()
    
    if alert_systems:
        # 테스트 신호 발송
        test_signals = {
            'TrendFollowing': {
                'action': 'BUY',
                'price': 150.25,
                'timestamp': datetime.now(),
                'confidence': 0.85
            }
        }
        
        print("📤 테스트 알림을 발송합니다...")
        for alert_system in alert_systems:
            try:
                alert_system.send_signal_alert('AAPL', test_signals)
                print(f"✅ {type(alert_system).__name__} 테스트 성공")
            except Exception as e:
                print(f"❌ {type(alert_system).__name__} 테스트 실패: {e}")
    else:
        print("⚠️ 설정된 알림 시스템이 없습니다.")
    
    print("🧪 테스트 완료!")


def run_live_monitoring():
    """실제 모니터링 실행 (Storage 통합)"""
    logger = setup_logging()
    
    print_banner()
    
    # 알림 시스템 생성
    alert_systems = create_alert_systems()
    
    # 모니터링 시스템 생성 (Storage 통합)
    monitor = RealTimeMonitor(
        alert_systems=alert_systems,
        update_interval=Config.UPDATE_INTERVAL,
        use_storage=True
    )
    
    # 모니터링 요약 정보 출력
    summary = monitor.get_monitoring_summary()
    if summary.get('total_active', 0) == 0:
        print("❌ 활성된 모니터링 설정이 없습니다.")
        print("💡 Streamlit 대시보드에서 모니터링을 추가하세요.")
        return
    
    print(f"📊 Active Monitoring: {summary['total_active']} configurations")
    print(f"💹 Tickers: {', '.join(summary['active_tickers'])}")
    print(f"🚀 Strategies: {', '.join(summary['active_strategies'])}")
    
    print("🚀 실시간 모니터링을 시작합니다...")
    print("중단하려면 Ctrl+C를 누르세요.\n")
    
    try:
        # 첫 번째 체크 실행
        monitor.run_single_check()
        
        # 지속적인 모니터링 시작
        monitor.run_continuous_monitoring()
        
    except KeyboardInterrupt:
        logger.info("사용자에 의해 모니터링이 중단되었습니다.")
        print("\n✅ 모니터링이 안전하게 종료되었습니다.")
    except Exception as e:
        logger.error(f"예상치 못한 오류 발생: {e}")
        print(f"\n❌ 오류 발생: {e}")


def main():
    """메인 함수"""
    # 시그널 핸들러 등록
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 명령줄 인자 처리
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        
        if arg in ['--help', '-h']:
            print_help()
            return
        elif arg in ['--test', '-t']:
            run_test_mode()
            return
        elif arg in ['--config', '-c']:
            run_configuration_check()
            return
        else:
            print(f"알 수 없는 옵션: {arg}")
            print_help()
            return
    
    # 기본 실행: 실시간 모니터링
    run_live_monitoring()


if __name__ == "__main__":
    main()