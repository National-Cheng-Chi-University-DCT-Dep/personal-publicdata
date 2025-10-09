"""
Study.eu 課程搜尋爬蟲
從 Study.eu 抓取符合條件的碩士課程
"""

import asyncio
import json
import sys
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from playwright.async_api import async_playwright, Browser, Page

sys.path.append(str(Path(__file__).parent.parent))

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class StudyEuScraper:
    """Study.eu 爬蟲"""
    
    BASE_URL = 'https://www.study.eu'
    SEARCH_URL = f'{BASE_URL}/search'
    
    def __init__(self, keywords: List[str], countries: Optional[List[str]] = None):
        """初始化爬蟲"""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.keywords = keywords
        self.countries = countries or []
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.raw_data_dir = Path('discovery/raw_data')
        self.raw_data_dir.mkdir(parents=True, exist_ok=True)
    
    async def search_courses(self, page: Page, keyword: str) -> List[Dict[str, Any]]:
        """搜尋課程"""
        courses = []
        
        try:
            self.logger.info(f"搜尋關鍵字: {keyword}")
            
            # 構建搜尋 URL
            search_url = f"{self.SEARCH_URL}?q={keyword.replace(' ', '+')}&level=master"
            
            self.logger.info(f"訪問: {search_url}")
            await page.goto(search_url, timeout=30000, wait_until='networkidle')
            await page.wait_for_timeout(3000)
            
            # 等待搜尋結果
            try:
                await page.wait_for_selector('.program-card, [class*="course"], [class*="result"]', timeout=10000)
            except:
                self.logger.warning(f"未找到課程結果")
                return courses
            
            # 抓取課程
            page_courses = await self.extract_courses_from_page(page)
            courses.extend(page_courses)
            
            self.logger.info(f"關鍵字 '{keyword}' 找到 {len(courses)} 個課程")
            return courses
        
        except Exception as e:
            self.logger.error(f"搜尋課程時發生錯誤 ({keyword}): {e}")
            return courses
    
    async def extract_courses_from_page(self, page: Page) -> List[Dict[str, Any]]:
        """從當前頁面提取課程"""
        courses = []
        
        try:
            # 基於診斷結果更新（2025-10-09）
            selectors = [
                '[class*="result"]',     # ← 診斷確認有效（60 個元素）
                '[class*="card"]',       # ← 診斷確認有效（3 個元素）
                '.program-card',
                '.course-card',
                '[class*="ProgramCard"]',
                '[class*="course"]',
                'article'
            ]
            
            course_elements = None
            for selector in selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    if elements and len(elements) > 0:
                        course_elements = elements
                        break
                except:
                    continue
            
            if not course_elements:
                return courses
            
            for element in course_elements:
                try:
                    course_data = await self.extract_course_details(element)
                    if course_data:
                        courses.append(course_data)
                except:
                    continue
            
            return courses
        except Exception as e:
            self.logger.error(f"提取課程時發生錯誤: {e}")
            return courses
    
    async def extract_course_details(self, element) -> Optional[Dict[str, Any]]:
        """提取課程詳情"""
        try:
            program_name = await self.extract_text(element, ['h2', 'h3', '.title'])
            university = await self.extract_text(element, ['.university', '.school', '[class*="uni"]'])
            country = await self.extract_text(element, ['.country', '[class*="country"]'])
            city = await self.extract_text(element, ['.city', '[class*="city"]'])
            
            # 課程連結
            program_url = None
            link = await element.query_selector('a')
            if link:
                href = await link.get_attribute('href')
                if href:
                    program_url = href if href.startswith('http') else f"{self.BASE_URL}{href}"
            
            if program_name and university:
                return {
                    'program_name': program_name,
                    'university_name': university,
                    'country': country or 'Unknown',
                    'city': city or 'Unknown',
                    'program_url': program_url or '',
                    'source': 'Study.eu',
                    'scraped_at': datetime.now().isoformat()
                }
            
            return None
        except Exception as e:
            self.logger.error(f"提取詳情時發生錯誤: {e}")
            return None
    
    async def extract_text(self, element, selectors: List[str]) -> Optional[str]:
        """提取文字"""
        for selector in selectors:
            try:
                sub_element = await element.query_selector(selector)
                if sub_element:
                    text = await sub_element.inner_text()
                    if text and text.strip():
                        return text.strip()
            except:
                continue
        return None
    
    async def run_async(self) -> List[Dict[str, Any]]:
        """執行爬蟲"""
        all_courses = []
        
        try:
            self.logger.info("=== 開始爬取 Study.eu ===")
            
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(headless=True)
            context = await self.browser.new_context()
            page = await context.new_page()
            
            for keyword in self.keywords:
                courses = await self.search_courses(page, keyword)
                all_courses.extend(courses)
                await asyncio.sleep(3)
            
            # 去重
            seen_urls = set()
            unique_courses = []
            for course in all_courses:
                url = course.get('program_url', '')
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    unique_courses.append(course)
            
            self.logger.info(f"總共找到 {len(unique_courses)} 個獨特課程")
            
            self.save_raw_data(unique_courses)
            
            await context.close()
            await self.browser.close()
            await self.playwright.stop()
            
            return unique_courses
        except Exception as e:
            self.logger.error(f"爬蟲執行失敗: {e}")
            return []
    
    def run(self) -> List[Dict[str, Any]]:
        """同步包裝"""
        return asyncio.run(self.run_async())
    
    def save_raw_data(self, courses: List[Dict[str, Any]]) -> None:
        """儲存原始資料"""
        filename = self.raw_data_dir / f"studyeu_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump({
                    'source': 'Study.eu',
                    'scraped_at': datetime.now().isoformat(),
                    'total_courses': len(courses),
                    'keywords': self.keywords,
                    'courses': courses
                }, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"原始資料已儲存: {filename}")
        except Exception as e:
            self.logger.error(f"儲存原始資料失敗: {e}")


def main():
    """主函式"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Study.eu 課程搜尋爬蟲')
    parser.add_argument('--keywords', nargs='+', required=True, help='搜尋關鍵字')
    parser.add_argument('--countries', nargs='+', help='目標國家')
    
    args = parser.parse_args()
    
    print("=== Study.eu 課程搜尋 ===\n")
    
    scraper = StudyEuScraper(
        keywords=args.keywords,
        countries=args.countries
    )
    
    courses = scraper.run()
    print(f"\n✅ 找到 {len(courses)} 個課程")


if __name__ == '__main__':
    main()

