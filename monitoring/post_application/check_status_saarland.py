"""
薩爾蘭大學申請進度監控
監控 apply.cs.uni-saarland.de 申請系統
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


class SaarlandMonitor(BaseMonitor):
    """監控薩爾蘭大學申請進度"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化監控器"""
        super().__init__(config)
        self.username = os.getenv('SAARLAND_USERNAME')
        self.password = os.getenv('SAARLAND_PASSWORD')
        self.base_url = 'https://apply.cs.uni-saarland.de'
        self.playwright = None
        self.browser: Optional[Browser] = None
        
        if not self.username or not self.password:
            self.logger.warning("薩爾蘭帳號密碼未設定，請設定 SAARLAND_USERNAME 和 SAARLAND_PASSWORD 環境變數")
    
    async def login(self, page: Page) -> bool:
        """
        登入薩爾蘭大學申請系統
        
        Args:
            page: Playwright Page 物件
            
        Returns:
            是否成功登入
        """
        try:
            self.logger.info("開始登入薩爾蘭大學申請系統")
            
            # 導航至首頁
            await page.goto(self.base_url, timeout=30000)
            await page.wait_for_timeout(2000)
            
            # 尋找並點擊登入連結
            try:
                login_link = await page.wait_for_selector('a:has-text("Login"), a:has-text("Sign in")', timeout=5000)
                if login_link:
                    await login_link.click()
                    await page.wait_for_timeout(2000)
            except:
                self.logger.info("可能已在登入頁面")
            
            # 填寫帳號
            await page.fill('input[name="username"], input[type="text"], input[type="email"]', self.username)
            self.logger.info("已填寫帳號")
            
            # 填寫密碼
            await page.fill('input[name="password"], input[type="password"]', self.password)
            self.logger.info("已填寫密碼")
            
            # 點擊登入按鈕
            await page.click('button[type="submit"], input[type="submit"]')
            self.logger.info("已點擊登入按鈕")
            
            # 等待登入完成
            try:
                await page.wait_for_load_state('networkidle', timeout=15000)
                
                # 檢查是否登入成功（查找使用者相關元素或確認不在登入頁面）
                current_url = page.url
                if 'login' not in current_url.lower():
                    self.logger.info("✅ 登入成功")
                    return True
                else:
                    self.logger.error("仍在登入頁面，登入可能失敗")
                    await self.debug_screenshot(page, 'saarland_login_failed')
                    return False
            
            except Exception as e:
                self.logger.warning(f"等待登入完成時發生錯誤: {e}")
                # 嘗試檢查是否實際上已登入
                await page.wait_for_timeout(3000)
                if 'login' not in page.url.lower():
                    self.logger.info("✅ 登入成功（備用檢查）")
                    return True
                return False
        
        except Exception as e:
            self.logger.error(f"登入過程發生錯誤: {e}")
            await self.debug_screenshot(page, 'saarland_login_error')
            raise
    
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
            
            # 尋找並導航至申請頁面
            try:
                # 可能的連結文字
                link_texts = [
                    'My Applications',
                    'Applications',
                    'Dashboard',
                    'My Account'
                ]
                
                for text in link_texts:
                    try:
                        link = await page.wait_for_selector(f'a:has-text("{text}")', timeout=3000)
                        if link:
                            await link.click()
                            await page.wait_for_timeout(2000)
                            self.logger.info(f"已點擊「{text}」")
                            break
                    except:
                        continue
            except:
                self.logger.info("可能已在申請頁面")
            
            # 等待內容載入
            await page.wait_for_load_state('networkidle', timeout=10000)
            await page.wait_for_timeout(3000)
            
            applications = []
            
            # 嘗試抓取申請資訊
            selectors = [
                '.application',
                '[class*="application"]',
                '.submission',
                'tr',
                '.card'
            ]
            
            application_elements = None
            for selector in selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    if elements and len(elements) > 0:
                        application_elements = elements
                        self.logger.info(f"找到 {len(elements)} 個可能的申請項目")
                        break
                except:
                    continue
            
            if not application_elements:
                self.logger.warning("未找到申請項目")
                
                # 儲存頁面內容以供分析
                content = await page.content()
                debug_file = Path('logs') / f'saarland_page_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
                debug_file.parent.mkdir(parents=True, exist_ok=True)
                with open(debug_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.logger.info(f"頁面內容已儲存: {debug_file}")
                
                await self.debug_screenshot(page, 'saarland_no_applications')
                
                # 回傳基本狀態
                return [{
                    'school': 'Saarland University',
                    'program': 'Computer Science (需手動確認)',
                    'status': 'No data found',
                    'checked_at': datetime.now().isoformat()
                }]
            
            # 抓取每個項目
            for i, element in enumerate(application_elements):
                try:
                    # 嘗試抓取文字內容
                    text_content = await element.inner_text()
                    
                    # 如果文字內容包含關鍵字，可能是申請項目
                    if any(keyword in text_content.lower() for keyword in ['application', 'status', 'submitted', 'program']):
                        
                        # 嘗試提取更詳細的資訊
                        status = 'Unknown'
                        if any(word in text_content.lower() for word in ['submitted', 'received']):
                            status = 'Submitted'
                        elif 'review' in text_content.lower():
                            status = 'Under Review'
                        elif 'accept' in text_content.lower():
                            status = 'Accepted'
                        elif 'reject' in text_content.lower():
                            status = 'Rejected'
                        
                        applications.append({
                            'school': 'Saarland University',
                            'program': 'Computer Science',
                            'status': status,
                            'details': text_content[:200],  # 前 200 字元
                            'checked_at': datetime.now().isoformat()
                        })
                        
                        self.logger.info(f"找到申請項目: {status}")
                        break  # 薩爾蘭通常只有一個申請
                
                except Exception as e:
                    self.logger.debug(f"處理項目 {i+1} 時發生錯誤: {e}")
                    continue
            
            # 如果沒找到特定項目，回傳基本狀態
            if not applications:
                applications = [{
                    'school': 'Saarland University',
                    'program': 'Computer Science',
                    'status': 'Monitoring active (no specific status detected)',
                    'checked_at': datetime.now().isoformat()
                }]
            
            return applications
        
        except Exception as e:
            self.logger.error(f"抓取申請狀態時發生錯誤: {e}")
            await self.debug_screenshot(page, 'saarland_extraction_error')
            return [{
                'school': 'Saarland University',
                'status': 'error',
                'error': str(e),
                'checked_at': datetime.now().isoformat()
            }]
    
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
                self.logger.error("未設定薩爾蘭帳號密碼")
                return False
            
            self.logger.info("=== 開始監控薩爾蘭大學申請狀態 ===")
            
            # 啟動 Playwright
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(headless=True)
            context = await self.browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            page = await context.new_page()
            
            # 登入
            login_success = await self.login(page)
            if not login_success:
                await context.close()
                await self.browser.close()
                await self.playwright.stop()
                return False
            
            # 抓取申請狀態
            applications = await self.extract_application_status(page)
            
            # 偵測變更
            old_status = self.load_saved_status('saarland_applications')
            if self.detect_changes(old_status, {'applications': applications}):
                self.logger.info("⚠️ 偵測到狀態變更")
                self.send_notification({
                    'type': 'saarland_status_change',
                    'platform': 'Saarland University',
                    'applications': applications,
                    'timestamp': datetime.now().isoformat()
                })
            
            # 儲存狀態
            self.save_status('saarland_applications', {
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
                if platform.get('platform') == 'apply.cs.uni-saarland.de':
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
    print("=== 薩爾蘭大學申請狀態監控 ===\n")
    
    monitor = SaarlandMonitor()
    success = monitor.run()
    
    if success:
        print("\n✅ 監控完成")
    else:
        print("\n❌ 監控失敗")
        sys.exit(1)


if __name__ == '__main__':
    main()

