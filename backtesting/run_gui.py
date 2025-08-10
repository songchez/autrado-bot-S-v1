#!/usr/bin/env python3
"""
백테스팅 GUI 실행 스크립트
"""

import os
import sys
import subprocess

def run_streamlit_app():
    """Enhanced Streamlit 백테스팅 앱 실행"""
    # 프로젝트 루트에서 main_app.py 찾기
    project_root = os.path.dirname(os.path.dirname(__file__))
    main_app_path = os.path.join(project_root, 'main_app.py')
    
    # main_app.py가 있으면 사용, 없으면 기존 앱 사용
    if os.path.exists(main_app_path):
        app_path = main_app_path
        print("🚀 Enhanced Multi-Page App을 실행합니다...")
    else:
        app_path = os.path.join(os.path.dirname(__file__), 'multi_strategy_app.py')
        print("🎯 기본 Multi-Strategy App을 실행합니다...")
    
    try:
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', app_path
        ], check=True)
    except KeyboardInterrupt:
        print("\n✅ 백테스팅 GUI가 종료되었습니다.")
    except subprocess.CalledProcessError as e:
        print(f"❌ 실행 오류: {e}")

if __name__ == "__main__":
    print("🎯 백테스팅 GUI를 시작합니다...")
    print("브라우저에서 http://localhost:8501 으로 접속하세요")
    print("종료하려면 Ctrl+C를 누르세요\n")
    
    run_streamlit_app()