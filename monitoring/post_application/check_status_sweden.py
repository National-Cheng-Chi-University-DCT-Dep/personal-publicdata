"""
瑞典 Universityadmissions.se 申請進度監控
監控登入後的個人申請頁面，抓取申請狀態
"""

import asyncio
import os
import sys
from typing import Dict, List, Any, Optional
from pathlib import Path
from playwright.async_api import async_playwright, Browser, Page
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent.parent))
from monitoring.base_monitor import BaseMonitor


class SwedenApplicationMonitor(BaseMonitor):
    """監控瑞典 Universityadmissions.se 申請進度"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化監控器"""
        super().__init__(config)
        self.username = os.getenv('SWEDEN_USERNAME')
        self.password = os.getenv('SWEDEN_PASSWORD')
        self.base_url = 'https://www.universityadmissions.se'
        self.login_url = f'{self.base_url}/intl/start'
        self.playwright = None
        self.browser: Optional[Browser] = None
        
        if not self.username or not self.password:
            self.logger.warning("瑞典帳號密碼未設定，請設定 SWEDEN_USERNAME 和 SWEDEN_PASSWORD 環境變數")
    
    async def login(self, page: Page) -> bool:
        """
        登入 Universityadmissions.se
        
        Args:
            page: Playwright Page 物件
            
        Returns:
            是否成功登入
        """
        try:
            self.logger.info("開始登入 Universityadmissions.se")
            
            # 導航至登入頁面
            await page.goto(self.login_url, timeout=30000)
            await page.wait_for_timeout(2000)
            
            # 點擊登入按鈕（可能需要先點擊 "Log in" 連結）
            try:
                # 尋找並點擊登入連結
                login_link = await page.wait_for_selector('a[href*="login"], button:has-text("Log in")', timeout=5000)
                if login_link:
                    await login_link.click()
                    await page.wait_for_timeout(2000)
            except:
                self.logger.info("未找到登入連結，可能已在登入頁面")
            
            # 填寫帳號
            username_field = await page.wait_for_selector(
                'input[type="text"], input[type="email"], input[name*="user"], input[name*="email"]',
                timeout=10000
            )
            await username_field.fill(self.username)
            self.logger.info("已填寫帳號")
            
            # 填寫密碼
            password_field = await page.wait_for_selector(
                'input[type="password"]',
                timeout=5000
            )
            await password_field.fill(self.password)
            self.logger.info("已填寫密碼")
            
            # 點擊登入按鈕
            login_button = await page.wait_for_selector(
                'button[type="submit"], input[type="submit"], button:has-text("Log in")',
                timeout=5000
            )
            await login_button.click()
            self.logger.info("已點擊登入按鈕")
            
            # 等待登入完成（等待 URL 變更或特定元素出現）
            try:
                # 等待導航完成或特定元素出現
                await page.wait_for_url('**/my-pages/**', timeout=15000)
                self.logger.info("✅ 登入成功")
                return True
            except:
                # 備用檢查：等待包含使用者資訊的元素
                try:
                    await page.wait_for_selector('.user-info, .account-info, [class*="user"]', timeout=10000)
                    self.logger.info("✅ 登入成功（透過元素檢測）")
                    return True
                except:
                    self.logger.error("登入可能失敗，未偵測到預期的頁面元素")
                    # 儲存截圖以供除錯
                    await self.debug_screenshot(page, 'login_failed')
                    return False
        
        except Exception as e:
            self.logger.error(f"登入過程發生錯誤: {e}")
            await self.debug_screenshot(page, 'login_error')
            raise
    
    async def navigate_to_applications(self, page: Page) -> bool:
        """
        導航至「我的申請」頁面
        
        Args:
            page: Playwright Page 物件
            
        Returns:
            是否成功導航
        """
        try:
            self.logger.info("導航至「我的申請」頁面")
            
            # 尋找「我的申請」或類似的連結
            try:
                # 常見的連結文字
                link_texts = [
                    'My applications',
                    'My pages',
                    'Applications',
                    'Mina sidor',  # 瑞典語
                ]
                
                for text in link_texts:
                    try:
                        link = await page.wait_for_selector(f'a:has-text("{text}")', timeout=3000)
                        if link:
                            await link.click()
                            await page.wait_for_timeout(2000)
                            self.logger.info(f"已點擊「{text}」連結")
                            break
                    except:
                        continue
                
                # 等待頁面載入
                await page.wait_for_load_state('networkidle', timeout=10000)
                
                return True
            
            except:
                self.logger.warning("未找到「我的申請」連結，可能已在正確頁面")
                return True
        
        except Exception as e:
            self.logger.error(f"導航時發生錯誤: {e}")
            await self.debug_screenshot(page, 'navigation_error')
            return False
    
    async def extract_application_status(self, page: Page) -> List[Dict[str, Any]]:
        """
        抓取申請狀態
        
        Args:
            page: Playwright Page 物件
            
        Returns:
            申請狀態清單
        """
        try:
            self.logger.info("開始抓取申請狀態")
            
            # 等待申請列表載入
            await page.wait_for_timeout(3000)
            
            applications = []
            
            # 嘗試多種可能的選擇器
            selectors = [
                '.application-item',
                '.application',
                '[class*="application"]',
                'tr[class*="application"]',  # 如果是表格格式
                '.course-item',
            ]
            
            application_elements = None
            for selector in selectors:
                try:
                    application_elements = await page.query_selector_all(selector)
                    if application_elements and len(application_elements) > 0:
                        self.logger.info(f"使用選擇器 '{selector}' 找到 {len(application_elements)} 個申請項目")
                        break
                except:
                    continue
            
            if not application_elements:
                self.logger.warning("未找到申請項目，嘗試分析整個頁面")
                
                # 取得頁面內容進行分析
                content = await page.content()
                
                # 儲存頁面內容以供除錯
                debug_file = Path('logs') / f'sweden_page_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
                debug_file.parent.mkdir(parents=True, exist_ok=True)
                with open(debug_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.logger.info(f"頁面內容已儲存至: {debug_file}")
                
                # 截圖
                await self.debug_screenshot(page, 'no_applications_found')
                
                return [{
                    'status': 'no_data',
                    'message': 'No application items found on the page',
                    'checked_at': datetime.now().isoformat()
                }]
            
            # 抓取每個申請項目的資訊
            for i, app_element in enumerate(application_elements):
                try:
                    # 嘗試抓取各個欄位
                    school_name = await self.extract_text(app_element, [
                        '.school-name',
                        '.university-name',
                        '[class*="school"]',
                        '[class*="university"]',
                        'h3',
                        'h4',
                    ])
                    
                    program_name = await self.extract_text(app_element, [
                        '.program-name',
                        '.course-name',
                        '[class*="program"]',
                        '[class*="course"]',
                        'h4',
                        'h5',
                    ])
                    
                    status = await self.extract_text(app_element, [
                        '.status',
                        '.application-status',
                        '[class*="status"]',
                        'span.badge',
                        '.label',
                    ])
                    
                    application_data = {
                        'school': school_name or f'School {i+1}',
                        'program': program_name or 'Unknown Program',
                        'status': status or 'Unknown Status',
                        'checked_at': datetime.now().isoformat()
                    }
                    
                    # 嘗試抓取額外資訊
                    try:
                        # 申請編號
                        app_id = await self.extract_text(app_element, [
                            '.application-id',
                            '[class*="id"]',
                        ])
                        if app_id:
                            application_data['application_id'] = app_id
                        
                        # 申請日期
                        applied_date = await self.extract_text(app_element, [
                            '.date',
                            '.applied-date',
                            '[class*="date"]',
                        ])
                        if applied_date:
                            application_data['applied_date'] = applied_date
                    except:
                        pass
                    
                    applications.append(application_data)
                    self.logger.info(f"抓取到申請: {school_name} - {program_name} - {status}")
                
                except Exception as e:
                    self.logger.error(f"抓取第 {i+1} 個申請項目時發生錯誤: {e}")
                    continue
            
            if not applications:
                self.logger.warning("未能抓取到任何申請資訊")
                await self.debug_screenshot(page, 'no_data_extracted')
            
            return applications
        
        except Exception as e:
            self.logger.error(f"抓取申請狀態時發生錯誤: {e}")
            await self.debug_screenshot(page, 'extraction_error')
            return [{
                'status': 'error',
                'error': str(e),
                'checked_at': datetime.now().isoformat()
            }]
    
    async def extract_text(self, element, selectors: List[str]) -> Optional[str]:
        """
        從元素中使用多個選擇器嘗試抓取文字
        
        Args:
            element: Playwright Element
            selectors: 選擇器清單
            
        Returns:
            抓取到的文字，若未找到則回傳 None
        """
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
        """
        儲存截圖用於除錯
        
        Args:
            page: Playwright Page 物件
            name: 截圖名稱
        """
        try:
            screenshot_dir = Path('logs/screenshots')
            screenshot_dir.mkdir(parents=True, exist_ok=True)
            
            screenshot_path = screenshot_dir / f'{name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
            await page.screenshot(path=str(screenshot_path), full_page=True)
            self.logger.info(f"截圖已儲存: {screenshot_path}")
        except Exception as e:
            self.logger.error(f"儲存截圖失敗: {e}")
    
    async def run_async(self) -> bool:
        """
        執行監控（非同步版本）
        
        Returns:
            是否成功
        """
        try:
            # 檢查帳密
            if not self.username or not self.password:
                self.logger.error("未設定瑞典帳號密碼")
                return False
            
            self.logger.info("=== 開始監控瑞典申請狀態 ===")
            
            # 啟動 Playwright
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=True  # 生產環境使用 True，測試時可改為 False
            )
            
            # 建立瀏覽器上下文
            context = await self.browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                viewport={'width': 1920, 'height': 1080}
            )
            page = await context.new_page()
            
            # 1. 登入
            login_success = await self.login(page)
            if not login_success:
                self.logger.error("登入失敗")
                await context.close()
                await self.browser.close()
                await self.playwright.stop()
                return False
            
            # 2. 導航至申請頁面
            nav_success = await self.navigate_to_applications(page)
            if not nav_success:
                self.logger.error("導航失敗")
                await context.close()
                await self.browser.close()
                await self.playwright.stop()
                return False
            
            # 3. 抓取申請狀態
            new_status = await self.extract_application_status(page)
            
            # 4. 載入舊狀態
            old_status = self.load_saved_status('sweden_applications')
            
            # 5. 偵測變更
            if self.detect_changes(old_status, {'applications': new_status}):
                self.logger.info("⚠️ 偵測到狀態變更")
                
                # 發送通知
                self.send_notification({
                    'type': 'sweden_status_change',
                    'platform': 'Universityadmissions.se',
                    'old_status': old_status.get('applications', []),
                    'new_status': new_status,
                    'timestamp': datetime.now().isoformat()
                })
            else:
                self.logger.info("ℹ️ 狀態無變更")
            
            # 6. 儲存新狀態
            self.save_status('sweden_applications', {
                'applications': new_status,
                'last_checked': datetime.now().isoformat()
            })
            
            # 7. 更新 application_status.yml
            self.update_application_status_yml(new_status)
            
            # 8. 清理
            await context.close()
            await self.browser.close()
            await self.playwright.stop()
            
            self.logger.info("=== 監控完成 ===")
            return True
        
        except Exception as e:
            self.logger.error(f"監控執行失敗: {e}")
            
            # 確保清理資源
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
        """
        更新 application_status.yml 檔案
        
        Args:
            applications: 申請狀態清單
        """
        try:
            status_file = 'source_data/application_status.yml'
            data = self.load_yaml(status_file)
            
            # 尋找瑞典平台的資料
            for platform in data.get('applications', []):
                if platform.get('platform') == 'universityadmissions.se':
                    platform['schools'] = applications
                    platform['last_checked'] = datetime.now().isoformat()
                    break
            
            # 儲存更新
            self.save_yaml(data, status_file)
            self.logger.info(f"已更新 {status_file}")
        
        except Exception as e:
            self.logger.error(f"更新 application_status.yml 失敗: {e}")
    
    def run(self) -> bool:
        """
        執行監控（同步包裝）
        
        Returns:
            是否成功
        """
        return asyncio.run(self.run_async())


def main():
    """主函式"""
    print("=== 瑞典申請狀態監控 ===\n")
    
    monitor = SwedenApplicationMonitor()
    success = monitor.run()
    
    if success:
        print("\n✅ 監控完成")
    else:
        print("\n❌ 監控失敗")
        sys.exit(1)


if __name__ == '__main__':
    main()

