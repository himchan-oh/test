"""
Remember App 채용 정보 크롤러

이 스크립트는 Remember App의 채용 공고 페이지에서 정보를 크롤링합니다.
"""

import asyncio
import json
from datetime import datetime
from playwright.async_api import async_playwright
import pandas as pd


class RememberJobCrawler:
    def __init__(self, url="https://career.rememberapp.co.kr/job/postings"):
        self.url = url
        self.jobs = []

    async def crawl(self):
        """채용 공고 정보를 크롤링합니다."""
        async with async_playwright() as p:
            # 브라우저 시작 (headless 모드)
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            print(f"페이지 접속 중: {self.url}")
            await page.goto(self.url, wait_until="networkidle")

            # 페이지가 완전히 로드될 때까지 대기
            await page.wait_for_timeout(3000)

            print("채용 공고 정보 추출 중...")

            # 채용 공고 카드 요소들 찾기
            # 일반적인 패턴들을 시도
            job_cards = await page.query_selector_all(
                'div[class*="job"], div[class*="posting"], '
                'article[class*="job"], article[class*="posting"], '
                'li[class*="job"], li[class*="posting"]'
            )

            if not job_cards:
                print("채용 공고를 찾을 수 없습니다. 페이지 HTML을 확인합니다...")
                # 페이지의 전체 HTML 구조 확인
                html_content = await page.content()

                # HTML을 파일로 저장
                with open("page_source.html", "w", encoding="utf-8") as f:
                    f.write(html_content)
                print("페이지 소스를 'page_source.html'에 저장했습니다.")

                # 다른 선택자 패턴 시도
                alternative_selectors = [
                    'div[class*="card"]',
                    'div[class*="item"]',
                    'a[href*="job"]',
                    'a[href*="posting"]',
                    '[role="article"]',
                    '[data-testid*="job"]',
                ]

                for selector in alternative_selectors:
                    elements = await page.query_selector_all(selector)
                    if elements:
                        print(f"'{selector}' 선택자로 {len(elements)}개의 요소를 찾았습니다.")
                        job_cards = elements
                        break

            print(f"찾은 채용 공고 수: {len(job_cards)}")

            # 각 채용 공고 정보 추출
            for idx, card in enumerate(job_cards[:20]):  # 최대 20개까지만
                try:
                    # 제목 추출
                    title_elem = await card.query_selector(
                        'h1, h2, h3, h4, [class*="title"], [class*="name"]'
                    )
                    title = await title_elem.inner_text() if title_elem else "제목 없음"

                    # 설명 추출
                    desc_elem = await card.query_selector(
                        '[class*="description"], [class*="desc"], p'
                    )
                    description = await desc_elem.inner_text() if desc_elem else ""

                    # 링크 추출
                    link_elem = await card.query_selector('a')
                    if link_elem:
                        href = await link_elem.get_attribute('href')
                        if href and not href.startswith('http'):
                            href = f"https://career.rememberapp.co.kr{href}"
                    else:
                        href = ""

                    # 위치/부서 정보
                    location_elem = await card.query_selector(
                        '[class*="location"], [class*="team"], [class*="department"]'
                    )
                    location = await location_elem.inner_text() if location_elem else ""

                    # 전체 텍스트 추출 (대체용)
                    full_text = await card.inner_text()

                    job_info = {
                        "title": title.strip(),
                        "description": description.strip(),
                        "location": location.strip(),
                        "url": href,
                        "full_text": full_text.strip(),
                        "crawled_at": datetime.now().isoformat()
                    }

                    self.jobs.append(job_info)
                    print(f"{idx + 1}. {title.strip()}")

                except Exception as e:
                    print(f"공고 {idx + 1} 처리 중 오류: {e}")
                    continue

            await browser.close()

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


async def main():
    """메인 실행 함수"""
    print("Remember App 채용 정보 크롤러 시작\n")

    crawler = RememberJobCrawler()

    try:
        # 크롤링 실행
        await crawler.crawl()

        # 결과 요약 출력
        crawler.print_summary()

        # 결과 저장
        if crawler.jobs:
            crawler.save_to_json()
            crawler.save_to_csv()
        else:
            print("수집된 채용 공고가 없습니다.")
            print("page_source.html 파일을 확인하여 페이지 구조를 분석해주세요.")

    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
