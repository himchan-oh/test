#!/bin/bash

echo "========================================"
echo "Remember App 크롤러 환경 설정"
echo "========================================"
echo ""

# 가상 환경 생성
echo "1. 가상 환경 생성 중..."
python3 -m venv venv

# 가상 환경 활성화
echo "2. 가상 환경 활성화 중..."
source venv/bin/activate

# 패키지 설치
echo "3. 필요한 패키지 설치 중..."
pip install --upgrade pip
pip install -r requirements-simple.txt

echo ""
echo "참고: Python 3.14를 사용하는 경우 Playwright가 설치되지 않을 수 있습니다."
echo "crawler_simple.py를 사용하시면 Playwright 없이 크롤링이 가능합니다."

echo ""
echo "========================================"
echo "설치 완료!"
echo "========================================"
echo ""
echo "크롤러를 실행하려면:"
echo ""
echo "1. 가상 환경 활성화:"
echo "   source venv/bin/activate"
echo ""
echo "2. 크롤러 실행:"
echo "   python crawler_simple.py"
echo ""
echo "   또는 Playwright 버전 (브라우저 설치 필요):"
echo "   playwright install chromium"
echo "   python crawler.py"
echo ""
echo "3. 종료할 때:"
echo "   deactivate"
echo ""
