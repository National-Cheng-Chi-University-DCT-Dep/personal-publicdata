"""
Mastersportal.com 課程搜尋爬蟲
從 Mastersportal.com 抓取符合條件的碩士課程
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


class MastersPortalScraper:
    """Mastersportal.com 爬蟲"""
    
    BASE_URL = 'https://www.mastersportal.com'
    SEARCH_URL = f'{BASE_URL}/search/master/'
    
    def __init__(self, keywords: List[str], countries: Optional[List[str]] = None):
        """
        初始化爬蟲
        
        Args:
            keywords: 搜尋關鍵字清單
            countries: 目標國家清單（可選）
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.keywords = keywords
        self.countries = countries or []
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.raw_data_dir = Path('discovery/raw_data')
        self.raw_data_dir.mkdir(parents=True, exist_ok=True)
    
    async def search_courses(self, page: Page, keyword: str) -> List[Dict[str, Any]]:
        """
        搜尋課程
        
        Args:
            page: Playwright Page 物件
            keyword: 搜尋關鍵字
            
        Returns:
            課程清單
        """
        courses = []
        
        try:
            self.logger.info(f"搜尋關鍵字: {keyword}")
            
            # 構建搜尋 URL
            search_url = f"{self.SEARCH_URL}?q={keyword.replace(' ', '+')}"
            if self.countries:
                # 加入國家篩選
                country_param = '&'.join([f'ct[]={c}' for c in self.countries])
                search_url += f"&{country_param}"
            
            self.logger.info(f"訪問: {search_url}")
            await page.goto(search_url, timeout=30000, wait_until='networkidle')
            await page.wait_for_timeout(3000)
            
            # 等待搜尋結果載入
            try:
                await page.wait_for_selector('.StudyCard, .study-card, [class*="course"], [class*="program"]', timeout=10000)
            except:
                self.logger.warning(f"未找到課程卡片，可能沒有結果或頁面結構已變更")
                await self.debug_screenshot(page, f'mastersportal_no_results_{keyword}')
                return courses
            
            # 處理分頁
            page_num = 1
            max_pages = 10  # 限制最多爬取頁數
            
            while page_num <= max_pages:
                self.logger.info(f"處理第 {page_num} 頁")
                
                # 抓取當前頁面的課程
                page_courses = await self.extract_courses_from_page(page)
                courses.extend(page_courses)
                
                self.logger.info(f"第 {page_num} 頁找到 {len(page_courses)} 個課程")
                
                # 檢查是否有下一頁
                try:
                    next_button = await page.query_selector('a[rel="next"], button:has-text("Next"), .pagination .next')
                    if next_button:
                        await next_button.click()
                        await page.wait_for_load_state('networkidle', timeout=15000)
                        await page.wait_for_timeout(2000)
                        page_num += 1
                    else:
                        self.logger.info("沒有更多頁面")
                        break
                except:
                    self.logger.info("到達最後一頁")
                    break
            
            self.logger.info(f"關鍵字 '{keyword}' 共找到 {len(courses)} 個課程")
            return courses
        
        except Exception as e:
            self.logger.error(f"搜尋課程時發生錯誤 ({keyword}): {e}")
            await self.debug_screenshot(page, f'mastersportal_error_{keyword}')
            return courses
    
    async def extract_courses_from_page(self, page: Page) -> List[Dict[str, Any]]:
        """從當前頁面提取課程資訊"""
        courses = []
        
        try:
            # 嘗試多種可能的選擇器
            selectors = [
                '.StudyCard',
                '.study-card',
                '[class*="CourseCard"]',
                '[class*="ProgramCard"]',
                'article[class*="course"]',
                '.search-result-item'
            ]
            
            course_elements = None
            for selector in selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    if elements and len(elements) > 0:
                        course_elements = elements
                        self.logger.info(f"使用選擇器 '{selector}' 找到 {len(elements)} 個課程")
                        break
                except:
                    continue
            
            if not course_elements:
                self.logger.warning("未找到課程元素")
                return courses
            
            # 提取每個課程的資訊
            for element in course_elements:
                try:
                    course_data = await self.extract_course_details(element, page)
                    if course_data:
                        courses.append(course_data)
                except Exception as e:
                    self.logger.error(f"提取課程詳情時發生錯誤: {e}")
                    continue
            
            return courses
        
        except Exception as e:
            self.logger.error(f"從頁面提取課程時發生錯誤: {e}")
            return courses
    
    async def extract_course_details(self, element, page: Page) -> Optional[Dict[str, Any]]:
        """提取單一課程的詳細資訊"""
        try:
            # 程式名稱
            program_name = await self.extract_text(element, [
                '.program-name', '.course-name', 'h2', 'h3', '[class*="title"]'
            ])
            
            # 大學名稱
            university = await self.extract_text(element, [
                '.university-name', '.institution', '[class*="university"]', '[class*="school"]'
            ])
            
            # 國家
            country = await self.extract_text(element, [
                '.country', '[class*="country"]', '.location'
            ])
            
            # 城市
            city = await self.extract_text(element, [
                '.city', '[class*="city"]'
            ])
            
            # 學費
            tuition = await self.extract_text(element, [
                '.tuition', '.fee', '[class*="tuition"]', '[class*="fee"]'
            ])
            
            # 課程連結
            program_url = None
            link = await element.query_selector('a[href*="/programmes/"], a[href*="/program/"]')
            if link:
                href = await link.get_attribute('href')
                if href:
                    program_url = href if href.startswith('http') else f"{self.BASE_URL}{href}"
            
            # 如果找到基本資訊，回傳課程資料
            if program_name and university:
                course_data = {
                    'program_name': program_name,
                    'university_name': university,
                    'country': country or 'Unknown',
                    'city': city or 'Unknown',
                    'tuition_info': tuition or 'N/A',
                    'program_url': program_url or '',
                    'source': 'Mastersportal',
                    'scraped_at': datetime.now().isoformat()
                }
                
                # 嘗試訪問詳細頁面獲取更多資訊
                if program_url:
                    detailed_info = await self.fetch_detailed_info(page, program_url)
                    if detailed_info:
                        course_data.update(detailed_info)
                
                return course_data
            
            return None
        
        except Exception as e:
            self.logger.error(f"提取課程詳情時發生錯誤: {e}")
            return None
    
    async def fetch_detailed_info(self, page: Page, url: str) -> Optional[Dict[str, Any]]:
        """訪問詳細頁面獲取更多資訊"""
        try:
            # 開啟新分頁
            new_page = await page.context.new_page()
            await new_page.goto(url, timeout=20000, wait_until='networkidle')
            await new_page.wait_for_timeout(2000)
            
            details = {}
            
            # 嘗試抓取 IELTS 要求
            ielts_text = await self.extract_text(new_page, [
                'text=IELTS', '[class*="ielts"]', '[class*="english"]'
            ])
            if ielts_text:
                details['ielts_requirement'] = ielts_text
                # 嘗試解析分數
                import re
                scores = re.findall(r'(\d+\.?\d*)', ielts_text)
                if scores:
                    details['ielts_overall'] = float(scores[0])
            
            # 截止日期
            deadline = await self.extract_text(new_page, [
                '[class*="deadline"]', 'text=Deadline', '[class*="apply-by"]'
            ])
            if deadline:
                details['application_deadline'] = deadline
            
            # 學費詳細資訊
            tuition_detail = await self.extract_text(new_page, [
                '[class*="tuition"]', '[class*="fee"]', 'text=Tuition'
            ])
            if tuition_detail:
                details['tuition_detail'] = tuition_detail
            
            await new_page.close()
            return details
        
        except Exception as e:
            self.logger.warning(f"無法獲取詳細資訊 ({url}): {e}")
            return None
    
    async def extract_text(self, element, selectors: List[str]) -> Optional[str]:
        """從元素中提取文字"""
        for selector in selectors:
            try:
                if selector.startswith('text='):
                    # 使用文字選擇器
                    sub_element = await element.query_selector(f'//{selector[5:]}')
                else:
                    sub_element = await element.query_selector(selector)
                
                if sub_element:
                    text = await sub_element.inner_text()
                    if text and text.strip():
                        return text.strip()
            except:
                continue
        return None
    
    async def debug_screenshot(self, page: Page, name: str) -> None:
        """儲存除錯截圖"""
        try:
            screenshot_dir = Path('logs/screenshots')
            screenshot_dir.mkdir(parents=True, exist_ok=True)
            screenshot_path = screenshot_dir / f'{name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
            await page.screenshot(path=str(screenshot_path), full_page=True)
            self.logger.info(f"截圖已儲存: {screenshot_path}")
        except Exception as e:
            self.logger.error(f"儲存截圖失敗: {e}")
    
    async def run_async(self) -> List[Dict[str, Any]]:
        """執行爬蟲"""
        all_courses = []
        
        try:
            self.logger.info("=== 開始爬取 Mastersportal.com ===")
            
            # 啟動 Playwright
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(headless=True)
            context = await self.browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            page = await context.new_page()
            
            # 對每個關鍵字進行搜尋
            for keyword in self.keywords:
                courses = await self.search_courses(page, keyword)
                all_courses.extend(courses)
                
                # 避免過度頻繁的請求
                await asyncio.sleep(3)
            
            # 去重（根據 program_url）
            seen_urls = set()
            unique_courses = []
            for course in all_courses:
                url = course.get('program_url', '')
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    unique_courses.append(course)
                elif not url:
                    unique_courses.append(course)
            
            self.logger.info(f"總共找到 {len(unique_courses)} 個獨特課程")
            
            # 儲存原始資料
            self.save_raw_data(unique_courses)
            
            # 清理
            await context.close()
            await self.browser.close()
            await self.playwright.stop()
            
            return unique_courses
        
        except Exception as e:
            self.logger.error(f"爬蟲執行失敗: {e}")
            if self.browser:
                try:
                    await self.browser.close()
                except:
                    pass
            if self.playwright:
                try:
                    await self.playwright.stop()
                except:
                    pass
            return []
    
    def run(self) -> List[Dict[str, Any]]:
        """同步包裝"""
        return asyncio.run(self.run_async())
    
    def save_raw_data(self, courses: List[Dict[str, Any]]) -> None:
        """儲存原始資料"""
        filename = self.raw_data_dir / f"mastersportal_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump({
                    'source': 'Mastersportal.com',
                    'scraped_at': datetime.now().isoformat(),
                    'total_courses': len(courses),
                    'keywords': self.keywords,
                    'countries': self.countries,
                    'courses': courses
                }, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"原始資料已儲存: {filename}")
        except Exception as e:
            self.logger.error(f"儲存原始資料失敗: {e}")


def main():
    """主函式"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Mastersportal.com 課程搜尋爬蟲')
    parser.add_argument('--keywords', nargs='+', required=True, help='搜尋關鍵字')
    parser.add_argument('--countries', nargs='+', help='目標國家')
    
    args = parser.parse_args()
    
    print("""
╔══════════════════════════════════════════════════════════╗
║         Mastersportal.com 課程搜尋                      ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    scraper = MastersPortalScraper(
        keywords=args.keywords,
        countries=args.countries
    )
    
    courses = scraper.run()
    
    print(f"\n✅ 完成！找到 {len(courses)} 個課程")
    print(f"原始資料已儲存至: discovery/raw_data/")


if __name__ == '__main__':
    main()

