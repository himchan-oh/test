"""
Remember App 채용 정보 크롤러 (Simple Version)

requests와 BeautifulSoup을 사용하는 간단한 버전입니다.
JavaScript 렌더링이 필요 없는 경우 이 버전을 사용하세요.
"""

import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
from datetime import datetime


class RememberJobCrawlerSimple:
    def __init__(self, url="https://career.rememberapp.co.kr/job/postings"):
        self.url = url
        self.jobs = []

    def crawl(self):
        """채용 공고 정보를 크롤링합니다."""
        print(f"페이지 접속 중: {self.url}")

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        try:
            response = requests.get(self.url, headers=headers, timeout=30)
            response.raise_for_status()
            response.encoding = 'utf-8'

            print("채용 공고 정보 추출 중...")

            soup = BeautifulSoup(response.text, 'html.parser')

            # HTML을 파일로 저장 (디버깅용)
            with open("page_source.html", "w", encoding="utf-8") as f:
                f.write(soup.prettify())
            print("페이지 소스를 'page_source.html'에 저장했습니다.")

            # 다양한 선택자 패턴 시도
            job_cards = []

            # 패턴 1: 일반적인 job/posting 클래스
            patterns = [
                {'selector': 'div', 'class_contains': 'job'},
                {'selector': 'div', 'class_contains': 'posting'},
                {'selector': 'article', 'class_contains': 'job'},
                {'selector': 'article', 'class_contains': 'posting'},
                {'selector': 'li', 'class_contains': 'job'},
                {'selector': 'li', 'class_contains': 'item'},
                {'selector': 'div', 'class_contains': 'card'},
                {'selector': 'a', 'href_contains': 'job'},
                {'selector': 'a', 'href_contains': 'posting'},
            ]

            for pattern in patterns:
                if 'class_contains' in pattern:
                    elements = soup.find_all(
                        pattern['selector'],
                        class_=lambda x: x and pattern['class_contains'] in x.lower() if x else False
                    )
                elif 'href_contains' in pattern:
                    elements = soup.find_all(
                        pattern['selector'],
                        href=lambda x: x and pattern['href_contains'] in x.lower() if x else False
                    )

                if elements:
                    print(f"'{pattern}' 패턴으로 {len(elements)}개의 요소를 찾았습니다.")
                    job_cards = elements
                    break

            if not job_cards:
                print("\n채용 공고 요소를 찾을 수 없습니다.")
                print("페이지 구조를 분석하기 위해 모든 링크와 주요 요소를 추출합니다...\n")

                # 모든 링크 찾기
                all_links = soup.find_all('a', href=True)
                print(f"페이지에서 {len(all_links)}개의 링크를 찾았습니다.")

                # 제목 태그 찾기
                headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                print(f"페이지에서 {len(headings)}개의 제목을 찾았습니다.\n")

                if headings:
                    print("발견된 제목들:")
                    for i, h in enumerate(headings[:10], 1):
                        print(f"{i}. {h.get_text(strip=True)[:100]}")

            print(f"\n찾은 채용 공고 수: {len(job_cards)}")

            # 각 채용 공고 정보 추출
            for idx, card in enumerate(job_cards[:20]):  # 최대 20개까지만
                try:
                    # 제목 추출
                    title_elem = card.find(['h1', 'h2', 'h3', 'h4'])
                    if not title_elem:
                        title_elem = card.find(class_=lambda x: x and ('title' in x.lower() or 'name' in x.lower()) if x else False)
                    title = title_elem.get_text(strip=True) if title_elem else "제목 없음"

                    # 설명 추출
                    desc_elem = card.find(class_=lambda x: x and ('description' in x.lower() or 'desc' in x.lower()) if x else False)
                    if not desc_elem:
                        desc_elem = card.find('p')
                    description = desc_elem.get_text(strip=True) if desc_elem else ""

                    # 링크 추출
                    link_elem = card if card.name == 'a' else card.find('a')
                    href = ""
                    if link_elem and link_elem.get('href'):
                        href = link_elem['href']
                        if href and not href.startswith('http'):
                            href = f"https://career.rememberapp.co.kr{href}"

                    # 위치/부서 정보
                    location_elem = card.find(class_=lambda x: x and ('location' in x.lower() or 'team' in x.lower() or 'department' in x.lower()) if x else False)
                    location = location_elem.get_text(strip=True) if location_elem else ""

                    # 전체 텍스트 추출
                    full_text = card.get_text(strip=True)

                    job_info = {
                        "title": title,
                        "description": description,
                        "location": location,
                        "url": href,
                        "full_text": full_text,
                        "crawled_at": datetime.now().isoformat()
                    }

                    self.jobs.append(job_info)
                    print(f"{idx + 1}. {title}")

                except Exception as e:
                    print(f"공고 {idx + 1} 처리 중 오류: {e}")
                    continue

        except requests.exceptions.RequestException as e:
            print(f"웹 페이지 접근 오류: {e}")
        except Exception as e:
            print(f"크롤링 중 오류 발생: {e}")
            import traceback
            traceback.print_exc()

        return self.jobs

    def save_to_json(self, filename="job_postings.json"):
        """결과를 JSON 파일로 저장합니다."""
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.jobs, f, ensure_ascii=False, indent=2)
        print(f"\n결과를 {filename}에 저장했습니다.")

    def save_to_csv(self, filename="job_postings.csv"):
        """결과를 CSV 파일로 저장합니다."""
        if self.jobs:
            df = pd.DataFrame(self.jobs)
            df.to_csv(filename, index=False, encoding="utf-8-sig")
            print(f"결과를 {filename}에 저장했습니다.")
        else:
            print("저장할 데이터가 없습니다.")

    def print_summary(self):
        """크롤링 결과 요약을 출력합니다."""
        print(f"\n{'='*50}")
        print(f"크롤링 완료!")
        print(f"총 {len(self.jobs)}개의 채용 공고를 수집했습니다.")
        print(f"{'='*50}\n")


def main():
    """메인 실행 함수"""
    print("Remember App 채용 정보 크롤러 시작 (Simple Version)\n")

    crawler = RememberJobCrawlerSimple()

    # 크롤링 실행
    crawler.crawl()

    # 결과 요약 출력
    crawler.print_summary()

    # 결과 저장
    if crawler.jobs:
        crawler.save_to_json()
        crawler.save_to_csv()
    else:
        print("수집된 채용 공고가 없습니다.")
        print("page_source.html 파일을 확인하여 페이지 구조를 분석해주세요.")


if __name__ == "__main__":
    main()
