# Remember App 채용 정보 크롤러

Remember App의 채용 공고 페이지에서 정보를 자동으로 수집하는 Python 크롤러입니다.

## 기능

- Remember App 채용 페이지 자동 크롤링
- JavaScript 렌더링 페이지 지원 (Playwright 사용)
- JSON 및 CSV 형식으로 데이터 저장
- 채용 공고 제목, 설명, 위치, URL 등 정보 추출

## 설치 방법

### 빠른 설치 (macOS/Linux)

자동 설치 스크립트 사용:

```bash
chmod +x setup.sh
./setup.sh
```

### 수동 설치

#### 1. 가상 환경 생성 및 활성화

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

#### 2. 패키지 설치

```bash
pip install -r requirements.txt
```

#### 3. Playwright 브라우저 설치 (선택사항)

`crawler.py` (Playwright 버전)을 사용하려는 경우:

```bash
playwright install chromium
```

간단한 버전(`crawler_simple.py`)만 사용한다면 이 단계는 생략 가능합니다.

## 사용 방법

### 기본 사용법

1. **가상 환경 활성화** (매번 실행 전 필요):

```bash
source venv/bin/activate  # macOS/Linux
# 또는
venv\Scripts\activate  # Windows
```

2. **크롤러 실행**:

두 가지 버전의 크롤러가 제공됩니다:

#### 옵션 1: 간단한 크롤러 (권장 - 빠른 시작)

Playwright 설치 없이 바로 실행 가능:

```bash
python crawler_simple.py
```

#### 옵션 2: Playwright 기반 크롤러

JavaScript 렌더링이 필요한 최신 웹사이트에 적합:

```bash
python crawler.py
```

3. **작업 완료 후 가상 환경 종료**:

```bash
deactivate
```

실행하면 다음 파일들이 생성됩니다:
- `job_postings.json` - JSON 형식의 채용 정보
- `job_postings.csv` - CSV 형식의 채용 정보
- `page_source.html` - 페이지 소스 (디버깅용)

### 출력 데이터 형식

각 채용 공고는 다음 정보를 포함합니다:

```json
{
  "title": "채용 공고 제목",
  "description": "채용 공고 설명",
  "location": "위치/부서 정보",
  "url": "채용 공고 상세 페이지 URL",
  "full_text": "전체 텍스트",
  "crawled_at": "크롤링 시간"
}
```

## 문제 해결

### 403 Forbidden 에러가 발생하는 경우

일부 웹사이트는 자동화된 요청을 차단합니다. 이 경우:

1. **Playwright 버전 사용**: `crawler.py`는 실제 브라우저를 사용하므로 차단을 우회할 수 있습니다.
2. **요청 간격 추가**: 코드에 `time.sleep()`을 추가하여 요청 속도를 낮춥니다.
3. **User-Agent 변경**: 크롤러 코드의 헤더를 수정합니다.
4. **VPN 사용**: 다른 IP 주소에서 시도합니다.

### 채용 공고를 찾을 수 없는 경우

크롤러는 여러 선택자 패턴을 시도하며, 실패할 경우 `page_source.html` 파일을 생성합니다.
이 파일을 확인하여 페이지 구조를 분석하고 필요시 `crawler.py`의 선택자를 수정할 수 있습니다.

웹사이트가 클라이언트 사이드 렌더링을 사용하는 경우, `crawler.py` (Playwright 버전)를 사용해야 합니다.

### 크롤러 커스터마이징

`crawler.py` 파일에서 다음을 수정할 수 있습니다:
- URL 변경: `RememberJobCrawler` 클래스 초기화 시 URL 파라미터 수정
- 선택자 패턴: `crawl()` 메서드 내의 `query_selector` 부분 수정
- 최대 수집 개수: `job_cards[:20]` 부분의 숫자 변경

## 주의사항

- 웹 크롤링 시 대상 웹사이트의 이용 약관을 확인하세요
- 서버에 과도한 부하를 주지 않도록 주의하세요
- robots.txt 파일을 확인하고 준수하세요

## 라이선스

MIT
