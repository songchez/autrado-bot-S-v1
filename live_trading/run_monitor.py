#!/usr/bin/env python3
"""
실시간 신호 모니터링 실행 스크립트
"""

import os
import sys

# 상위 디렉토리의 config 모듈을 import하기 위해 경로 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from live_trading_bot import main

if __name__ == "__main__":
    print("🎯 실시간 신호 모니터링을 시작합니다...")
    main()