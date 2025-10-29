"""
Remember App 채용 정보 크롤러 (Enhanced Version)

각 채용 공고의 상세 정보를 추출하는 개선된 버전입니다.
- 기본 정보: ID, 공고명, 회사명, 직군, 직무
- 상세 정보: 주요업무, 자격요건, 우대사항, 혜택
- 추가 정보: 기술스택, 보상금, 마감일
"""

import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
from datetime import datetime
import time
import re
from urllib.parse import urljoin, urlparse, parse_qs


class RememberJobCrawlerEnhanced:
    def __init__(self, url="https://career.rememberapp.co.kr/job/postings"):
        self.base_url = "https://career.rememberapp.co.kr"
        self.url = url
        self.jobs = []
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

    def extract_job_id_from_url(self, url):
        """URL에서 채용 공고 ID 추출"""
        try:
            # /job/detail/1234 형식
            match = re.search(r'/job/(?:detail|posting)/(\d+)', url)
            if match:
                return match.group(1)
            # ?id=1234 형식
            parsed = urlparse(url)
            query_params = parse_qs(parsed.query)
            if 'id' in query_params:
                return query_params['id'][0]
        except:
            pass
        return None

    def get_job_links(self):
        """메인 페이지에서 채용 공고 링크 목록 추출"""
        print(f"메인 페이지 접속 중: {self.url}")

        try:
            response = requests.get(self.url, headers=self.headers, timeout=30)
            response.raise_for_status()
            response.encoding = 'utf-8'

            soup = BeautifulSoup(response.text, 'html.parser')

            # HTML 저장 (디버깅용)
            with open("page_source_main.html", "w", encoding="utf-8") as f:
                f.write(soup.prettify())
            print("메인 페이지 소스를 'page_source_main.html'에 저장했습니다.")

            job_links = set()

            # 다양한 패턴으로 링크 찾기
            # 패턴 1: /job/detail/, /job/posting/ 등
            for link in soup.find_all('a', href=True):
                href = link['href']
                if any(pattern in href for pattern in ['/job/detail', '/job/posting', '/position/', '/recruit/']):
                    full_url = urljoin(self.base_url, href)
                    job_links.add(full_url)

            print(f"\n총 {len(job_links)}개의 채용 공고 링크를 찾았습니다.")

            return list(job_links)

        except requests.exceptions.RequestException as e:
            print(f"메인 페이지 접근 오류: {e}")
            return []
        except Exception as e:
            print(f"링크 추출 중 오류: {e}")
            import traceback
            traceback.print_exc()
            return []

    def extract_detail_info(self, soup, url):
        """상세 페이지에서 정보 추출"""
        job_info = {
            'job_id': self.extract_job_id_from_url(url),
            'url': url,
            'title': '',
            'company': '',
            'job_category': '',
            'job_position': '',
            'main_tasks': '',
            'qualifications': '',
            'preferred_qualifications': '',
            'benefits': '',
            'tech_stack': [],
            'reward': '',
            'deadline': '',
            'location': '',
            'employment_type': '',
            'experience_level': '',
            'salary': '',
            'crawled_at': datetime.now().isoformat()
        }

        try:
            # 공고 제목
            title_selectors = [
                soup.find('h1'),
                soup.find('h2'),
                soup.find(class_=re.compile(r'title|heading|position.*name', re.I)),
                soup.find(attrs={'data-cy': 'job-title'}),
            ]
            for selector in title_selectors:
                if selector:
                    job_info['title'] = selector.get_text(strip=True)
                    break

            # 회사명
            company_selectors = [
                soup.find(class_=re.compile(r'company.*name', re.I)),
                soup.find(attrs={'data-cy': 'company-name'}),
                soup.find('a', href=re.compile(r'/company/')),
            ]
            for selector in company_selectors:
                if selector:
                    job_info['company'] = selector.get_text(strip=True)
                    break

            # 직군/직무
            category_keywords = ['직군', '직무', '포지션', 'category', 'position']
            for keyword in category_keywords:
                elem = soup.find(text=re.compile(keyword, re.I))
                if elem and elem.parent:
                    # 다음 형제 요소나 부모의 다음 요소에서 값 찾기
                    parent = elem.parent
                    next_elem = parent.find_next_sibling()
                    if next_elem:
                        value = next_elem.get_text(strip=True)
                        if '직군' in keyword or 'category' in keyword.lower():
                            job_info['job_category'] = value
                        elif '직무' in keyword or 'position' in keyword.lower():
                            job_info['job_position'] = value

            # 주요 업무
            tasks_keywords = ['주요업무', '주요 업무', '담당업무', '업무내용', 'responsibilities', 'main tasks']
            for keyword in tasks_keywords:
                elem = soup.find(text=re.compile(keyword, re.I))
                if elem:
                    # 해당 섹션의 내용 추출
                    section = elem.find_parent(['div', 'section', 'li'])
                    if section:
                        # 리스트 항목들 찾기
                        items = section.find_all(['li', 'p'])
                        if items:
                            job_info['main_tasks'] = '\n'.join([item.get_text(strip=True) for item in items])
                        else:
                            job_info['main_tasks'] = section.get_text(strip=True)
                        break

            # 자격 요건
            qual_keywords = ['자격요건', '자격 요건', '지원자격', 'qualifications', 'requirements']
            for keyword in qual_keywords:
                elem = soup.find(text=re.compile(keyword, re.I))
                if elem:
                    section = elem.find_parent(['div', 'section', 'li'])
                    if section:
                        items = section.find_all(['li', 'p'])
                        if items:
                            job_info['qualifications'] = '\n'.join([item.get_text(strip=True) for item in items])
                        else:
                            job_info['qualifications'] = section.get_text(strip=True)
                        break

            # 우대 사항
            pref_keywords = ['우대사항', '우대 사항', '우대조건', 'preferred', 'nice to have']
            for keyword in pref_keywords:
                elem = soup.find(text=re.compile(keyword, re.I))
                if elem:
                    section = elem.find_parent(['div', 'section', 'li'])
                    if section:
                        items = section.find_all(['li', 'p'])
                        if items:
                            job_info['preferred_qualifications'] = '\n'.join([item.get_text(strip=True) for item in items])
                        else:
                            job_info['preferred_qualifications'] = section.get_text(strip=True)
                        break

            # 혜택
            benefit_keywords = ['혜택', '복지', 'benefits', 'perks']
            for keyword in benefit_keywords:
                elem = soup.find(text=re.compile(keyword, re.I))
                if elem:
                    section = elem.find_parent(['div', 'section', 'li'])
                    if section:
                        items = section.find_all(['li', 'p'])
                        if items:
                            job_info['benefits'] = '\n'.join([item.get_text(strip=True) for item in items])
                        else:
                            job_info['benefits'] = section.get_text(strip=True)
                        break

            # 기술 스택
            tech_keywords = ['기술스택', '기술 스택', '사용기술', 'tech stack', 'skills']
            for keyword in tech_keywords:
                elem = soup.find(text=re.compile(keyword, re.I))
                if elem:
                    section = elem.find_parent(['div', 'section'])
                    if section:
                        # 기술 태그나 배지 찾기
                        tags = section.find_all(['span', 'button', 'div'], class_=re.compile(r'tag|badge|skill|tech', re.I))
                        if tags:
                            job_info['tech_stack'] = [tag.get_text(strip=True) for tag in tags]
                        else:
                            tech_text = section.get_text(strip=True)
                            # 쉼표나 공백으로 구분된 기술들 추출
                            job_info['tech_stack'] = [t.strip() for t in re.split(r'[,\n]', tech_text) if t.strip()]
                        break

            # 마감일
            deadline_keywords = ['마감', '지원기한', 'deadline', 'due date']
            for keyword in deadline_keywords:
                elem = soup.find(text=re.compile(keyword, re.I))
                if elem and elem.parent:
                    parent = elem.parent
                    next_elem = parent.find_next_sibling()
                    if next_elem:
                        job_info['deadline'] = next_elem.get_text(strip=True)
                        break

            # 근무 지역
            location_keywords = ['근무지', '위치', '근무지역', 'location']
            for keyword in location_keywords:
                elem = soup.find(text=re.compile(keyword, re.I))
                if elem and elem.parent:
                    parent = elem.parent
                    next_elem = parent.find_next_sibling()
                    if next_elem:
                        job_info['location'] = next_elem.get_text(strip=True)
                        break

            # 고용 형태
            employment_keywords = ['고용형태', '채용형태', 'employment type']
            for keyword in employment_keywords:
                elem = soup.find(text=re.compile(keyword, re.I))
                if elem and elem.parent:
                    parent = elem.parent
                    next_elem = parent.find_next_sibling()
                    if next_elem:
                        job_info['employment_type'] = next_elem.get_text(strip=True)
                        break

            # 경력
            experience_keywords = ['경력', 'experience']
            for keyword in experience_keywords:
                elem = soup.find(text=re.compile(keyword, re.I))
                if elem and elem.parent:
                    parent = elem.parent
                    next_elem = parent.find_next_sibling()
                    if next_elem:
                        job_info['experience_level'] = next_elem.get_text(strip=True)
                        break

            # 보상금/연봉
            salary_keywords = ['연봉', '급여', '보상금', 'salary', 'compensation', 'reward']
            for keyword in salary_keywords:
                elem = soup.find(text=re.compile(keyword, re.I))
                if elem and elem.parent:
                    parent = elem.parent
                    next_elem = parent.find_next_sibling()
                    if next_elem:
                        text = next_elem.get_text(strip=True)
                        if '보상금' in keyword or 'reward' in keyword:
                            job_info['reward'] = text
                        else:
                            job_info['salary'] = text
                        break

        except Exception as e:
            print(f"상세 정보 추출 중 오류: {e}")

        return job_info

    def crawl_job_detail(self, url, index, total):
        """개별 채용 공고 상세 정보 크롤링"""
        print(f"\n[{index}/{total}] 크롤링 중: {url}")

        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            response.encoding = 'utf-8'

            soup = BeautifulSoup(response.text, 'html.parser')

            # 첫 번째 상세 페이지만 저장 (디버깅용)
            if index == 1:
                with open("page_source_detail.html", "w", encoding="utf-8") as f:
                    f.write(soup.prettify())
                print("  → 상세 페이지 소스를 'page_source_detail.html'에 저장했습니다.")

            job_info = self.extract_detail_info(soup, url)

            print(f"  ✓ {job_info['title'] or '제목 없음'}")
            if job_info['company']:
                print(f"    회사: {job_info['company']}")

            return job_info

        except requests.exceptions.RequestException as e:
            print(f"  ✗ 페이지 접근 오류: {e}")
            return None
        except Exception as e:
            print(f"  ✗ 크롤링 오류: {e}")
            import traceback
            traceback.print_exc()
            return None

    def crawl(self, max_jobs=None):
        """전체 크롤링 프로세스 실행"""
        print("="*60)
        print("Remember App 채용 정보 크롤러 시작 (Enhanced Version)")
        print("="*60)

        # 1단계: 채용 공고 링크 수집
        job_links = self.get_job_links()

        if not job_links:
            print("\n채용 공고 링크를 찾을 수 없습니다.")
            print("page_source_main.html 파일을 확인하여 페이지 구조를 분석해주세요.")
            return []

        # 최대 수집 개수 제한
        if max_jobs:
            job_links = job_links[:max_jobs]
            print(f"\n최대 {max_jobs}개의 공고만 수집합니다.")

        # 2단계: 각 채용 공고 상세 정보 크롤링
        print(f"\n{'='*60}")
        print(f"상세 정보 크롤링 시작 (총 {len(job_links)}개)")
        print(f"{'='*60}")

        for idx, link in enumerate(job_links, 1):
            job_info = self.crawl_job_detail(link, idx, len(job_links))

            if job_info:
                self.jobs.append(job_info)

            # 서버 부하 방지를 위한 대기
            if idx < len(job_links):
                time.sleep(1)  # 1초 대기

        return self.jobs

    def save_to_json(self, filename="job_postings_detailed.json"):
        """결과를 JSON 파일로 저장"""
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.jobs, f, ensure_ascii=False, indent=2)
        print(f"\n결과를 {filename}에 저장했습니다.")

    def save_to_csv(self, filename="job_postings_detailed.csv"):
        """결과를 CSV 파일로 저장"""
        if self.jobs:
            # 기술스택은 리스트이므로 문자열로 변환
            jobs_for_csv = []
            for job in self.jobs:
                job_copy = job.copy()
                if isinstance(job_copy.get('tech_stack'), list):
                    job_copy['tech_stack'] = ', '.join(job_copy['tech_stack'])
                jobs_for_csv.append(job_copy)

            df = pd.DataFrame(jobs_for_csv)
            df.to_csv(filename, index=False, encoding="utf-8-sig")
            print(f"결과를 {filename}에 저장했습니다.")
        else:
            print("저장할 데이터가 없습니다.")

    def print_summary(self):
        """크롤링 결과 요약 출력"""
        print(f"\n{'='*60}")
        print(f"크롤링 완료!")
        print(f"총 {len(self.jobs)}개의 채용 공고 상세 정보를 수집했습니다.")
        print(f"{'='*60}\n")

        if self.jobs:
            print("수집된 필드:")
            sample = self.jobs[0]
            for key, value in sample.items():
                has_data = "✓" if value else "✗"
                print(f"  {has_data} {key}")


def main():
    """메인 실행 함수"""
    crawler = RememberJobCrawlerEnhanced()

    # 크롤링 실행 (테스트 시 max_jobs=5 등으로 제한 가능)
    crawler.crawl(max_jobs=10)  # 최대 10개만 수집 (전체는 max_jobs=None)

    # 결과 요약 출력
    crawler.print_summary()

    # 결과 저장
    if crawler.jobs:
        crawler.save_to_json()
        crawler.save_to_csv()
    else:
        print("수집된 채용 공고가 없습니다.")
        print("page_source_main.html과 page_source_detail.html 파일을 확인하여")
        print("페이지 구조를 분석해주세요.")


if __name__ == "__main__":
    main()
