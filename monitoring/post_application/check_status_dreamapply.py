"""
DreamApply 平台申請進度監控
監控 estonia.dreamapply.com 及其他使用 DreamApply 系統的學校
"""

import asyncio
import os
import sys
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
from playwright.async_api import async_playwright, Browser, Page, Response
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent.parent))
from monitoring.base_monitor import BaseMonitor


class DreamApplyMonitor(BaseMonitor):
    """監控 DreamApply 平台申請進度"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化監控器"""
        super().__init__(config)
        self.username = os.getenv('DREAMAPPLY_USERNAME')
        self.password = os.getenv('DREAMAPPLY_PASSWORD')
        self.base_url = 'https://estonia.dreamapply.com'
        self.login_url = f'{self.base_url}/account/login'
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.api_data = None  # 儲存攔截到的 API 資料
        
        if not self.username or not self.password:
            self.logger.warning("DreamApply 帳號密碼未設定，請設定 DREAMAPPLY_USERNAME 和 DREAMAPPLY_PASSWORD 環境變數")
    
    async def setup_api_interception(self, page: Page) -> None:
        """
        設定 API 請求攔截
        
        Args:
            page: Playwright Page 物件
        """
        async def handle_response(response: Response):
            """處理回應"""
            try:
                url = response.url
                
                # 攔截可能包含申請資料的 API 請求
                if any(keyword in url.lower() for keyword in ['application', 'status', 'api', 'data']):
                    if response.status == 200:
                        try:
                            data = await response.json()
                            self.logger.info(f"攔截到 API 回應: {url}")
                            
                            # 儲存可能相關的資料
                            if isinstance(data, (dict, list)):
                                if not self.api_data:
                                    self.api_data = {}
                                self.api_data[url] = data
                        except:
                            pass
            except Exception as e:
                self.logger.debug(f"處理回應時發生錯誤: {e}")
        
        page.on('response', handle_response)
    
    async def login(self, page: Page) -> bool:
        """
        登入 DreamApply
        
        Args:
            page: Playwright Page 物件
            
        Returns:
            是否成功登入
        """
        try:
            self.logger.info("開始登入 DreamApply")
            
            # 導航至登入頁面
            await page.goto(self.login_url, timeout=30000)
            await page.wait_for_timeout(2000)
            
            # 填寫帳號
            await page.fill('input[name="email"], input[type="email"], input[name="username"]', self.username)
            self.logger.info("已填寫帳號")
            
            # 填寫密碼
            await page.fill('input[name="password"], input[type="password"]', self.password)
            self.logger.info("已填寫密碼")
            
            # 點擊登入按鈕
            await page.click('button[type="submit"], input[type="submit"]')
            self.logger.info("已點擊登入按鈕")
            
            # 等待登入完成
            try:
                # 等待 URL 變更或 dashboard 元素出現
                await asyncio.wait_for(
                    asyncio.create_task(
                        page.wait_for_url('**/dashboard/**', timeout=15000)
                    ),
                    timeout=15
                )
                self.logger.info("✅ 登入成功")
                return True
            except asyncio.TimeoutError:
                # 備用檢查：查找 dashboard 相關元素
                try:
                    await page.wait_for_selector('.dashboard, [class*="dashboard"], .applications', timeout=5000)
                    self.logger.info("✅ 登入成功（透過元素檢測）")
                    return True
                except:
                    self.logger.error("登入可能失敗")
                    await self.debug_screenshot(page, 'dreamapply_login_failed')
                    return False
        
        except Exception as e:
            self.logger.error(f"登入過程發生錯誤: {e}")
            await self.debug_screenshot(page, 'dreamapply_login_error')
            raise
    
    async def try_api_approach(self, page: Page) -> Optional[List[Dict[str, Any]]]:
        """
        嘗試從攔截的 API 資料中提取申請資訊
        
        Args:
            page: Playwright Page 物件
            
        Returns:
            申請資料清單，若無法提取則回傳 None
        """
        if not self.api_data:
            return None
        
        try:
            self.logger.info("嘗試從 API 資料提取申請資訊")
            
            applications = []
            
            # 分析所有攔截到的 API 資料
            for url, data in self.api_data.items():
                if isinstance(data, list):
                    # 資料是陣列，可能直接是申請清單
                    for item in data:
                        if isinstance(item, dict) and any(key in item for key in ['application', 'status', 'program', 'university']):
                            app_data = self.parse_application_data(item)
                            if app_data:
                                applications.append(app_data)
                
                elif isinstance(data, dict):
                    # 資料是物件，可能包含申請清單
                    for key, value in data.items():
                        if isinstance(value, list):
                            for item in value:
                                if isinstance(item, dict):
                                    app_data = self.parse_application_data(item)
                                    if app_data:
                                        applications.append(app_data)
            
            if applications:
                self.logger.info(f"從 API 提取到 {len(applications)} 個申請")
                return applications
            
            return None
        
        except Exception as e:
            self.logger.error(f"從 API 提取資料時發生錯誤: {e}")
            return None
    
    def parse_application_data(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        解析單一申請資料
        
        Args:
            data: API 回傳的資料
            
        Returns:
            標準化的申請資料
        """
        try:
            # 嘗試提取各個欄位（可能的欄位名稱）
            school = (
                data.get('university') or
                data.get('institution') or
                data.get('school') or
                data.get('universityName') or
                'Unknown'
            )
            
            program = (
                data.get('program') or
                data.get('programme') or
                data.get('course') or
                data.get('programName') or
                'Unknown'
            )
            
            status = (
                data.get('status') or
                data.get('applicationStatus') or
                data.get('state') or
                'Unknown'
            )
            
            # 只有在至少有學校或課程資訊時才回傳
            if school != 'Unknown' or program != 'Unknown':
                return {
                    'school': school,
                    'program': program,
                    'status': status,
                    'application_id': data.get('id') or data.get('applicationId'),
                    'submitted_date': data.get('submittedAt') or data.get('createdAt'),
                    'checked_at': datetime.now().isoformat()
                }
            
            return None
        
        except Exception as e:
            self.logger.debug(f"解析申請資料時發生錯誤: {e}")
            return None
    
    async def extract_application_status_html(self, page: Page) -> List[Dict[str, Any]]:
        """
        從 HTML 抓取申請狀態（當 API 方式失敗時使用）
        
        Args:
            page: Playwright Page 物件
            
        Returns:
            申請狀態清單
        """
        try:
            self.logger.info("從 HTML 抓取申請狀態")
            
            applications = []
            
            # 等待內容載入
            await page.wait_for_timeout(3000)
            
            # 嘗試多種選擇器
            selectors = [
                '.application-item',
                '.application',
                '[class*="application"]',
                'tr.application-row',
                '.card',
            ]
            
            application_elements = None
            for selector in selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    if elements and len(elements) > 0:
                        application_elements = elements
                        self.logger.info(f"使用選擇器 '{selector}' 找到 {len(elements)} 個元素")
                        break
                except:
                    continue
            
            if not application_elements:
                self.logger.warning("未找到申請項目")
                await self.debug_screenshot(page, 'dreamapply_no_applications')
                return []
            
            # 抓取每個項目
            for i, element in enumerate(application_elements):
                try:
                    school = await self.extract_text(element, [
                        '.university', '.school', '[class*="university"]', 'h3', 'h4'
                    ])
                    
                    program = await self.extract_text(element, [
                        '.program', '.programme', '[class*="program"]', 'h4', 'h5'
                    ])
                    
                    status = await self.extract_text(element, [
                        '.status', '[class*="status"]', '.badge', '.label'
                    ])
                    
                    if school or program:
                        applications.append({
                            'school': school or f'School {i+1}',
                            'program': program or 'Unknown',
                            'status': status or 'Unknown',
                            'checked_at': datetime.now().isoformat()
                        })
                
                except Exception as e:
                    self.logger.error(f"抓取項目 {i+1} 時發生錯誤: {e}")
                    continue
            
            return applications
        
        except Exception as e:
            self.logger.error(f"從 HTML 抓取時發生錯誤: {e}")
            return []
    
    async def extract_text(self, element, selectors: List[str]) -> Optional[str]:
        """從元素中抓取文字"""
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
    
    async def run_async(self) -> bool:
        """執行監控"""
        try:
            if not self.username or not self.password:
                self.logger.error("未設定 DreamApply 帳號密碼")
                return False
            
            self.logger.info("=== 開始監控 DreamApply 申請狀態 ===")
            
            # 啟動 Playwright
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(headless=True)
            context = await self.browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            page = await context.new_page()
            
            # 設定 API 攔截
            await self.setup_api_interception(page)
            
            # 登入
            login_success = await self.login(page)
            if not login_success:
                await context.close()
                await self.browser.close()
                await self.playwright.stop()
                return False
            
            # 等待頁面完全載入
            await page.wait_for_load_state('networkidle', timeout=10000)
            await page.wait_for_timeout(3000)
            
            # 方法 1: 嘗試從 API 提取
            applications = await self.try_api_approach(page)
            
            # 方法 2: 如果 API 失敗，從 HTML 抓取
            if not applications:
                self.logger.info("API 方式未能提取資料，改用 HTML 抓取")
                applications = await self.extract_application_status_html(page)
            
            # 偵測變更
            old_status = self.load_saved_status('dreamapply_applications')
            if self.detect_changes(old_status, {'applications': applications}):
                self.logger.info("⚠️ 偵測到狀態變更")
                self.send_notification({
                    'type': 'dreamapply_status_change',
                    'platform': 'DreamApply',
                    'applications': applications,
                    'timestamp': datetime.now().isoformat()
                })
            
            # 儲存狀態
            self.save_status('dreamapply_applications', {
                'applications': applications,
                'last_checked': datetime.now().isoformat()
            })
            
            # 更新 YAML
            self.update_application_status_yml(applications)
            
            # 清理
            await context.close()
            await self.browser.close()
            await self.playwright.stop()
            
            self.logger.info("=== 監控完成 ===")
            return True
        
        except Exception as e:
            self.logger.error(f"監控執行失敗: {e}")
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
            return False
    
    def update_application_status_yml(self, applications: List[Dict[str, Any]]) -> None:
        """更新 application_status.yml"""
        try:
            status_file = 'source_data/application_status.yml'
            data = self.load_yaml(status_file)
            
            for platform in data.get('applications', []):
                if platform.get('platform') == 'estonia.dreamapply.com':
                    platform['schools'] = applications
                    platform['last_checked'] = datetime.now().isoformat()
                    break
            
            self.save_yaml(data, status_file)
            self.logger.info(f"已更新 {status_file}")
        except Exception as e:
            self.logger.error(f"更新 YAML 失敗: {e}")
    
    def run(self) -> bool:
        """同步包裝"""
        return asyncio.run(self.run_async())


def main():
    """主函式"""
    print("=== DreamApply 申請狀態監控 ===\n")
    
    monitor = DreamApplyMonitor()
    success = monitor.run()
    
    if success:
        print("\n✅ 監控完成")
    else:
        print("\n❌ 監控失敗")
        sys.exit(1)


if __name__ == '__main__':
    main()

