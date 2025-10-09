"""
申請開放狀態監控
監控 schools.yml 中各校的申請頁面，偵測申請開放狀態變更
"""

import asyncio
import re
from typing import Dict, List, Any, Optional
from pathlib import Path
from playwright.async_api import async_playwright, Browser, Page
from datetime import datetime
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from monitoring.base_monitor import BaseMonitor


class ApplicationOpeningMonitor(BaseMonitor):
    """監控申請開放狀態"""
    
    # 申請開放相關的關鍵字
    OPEN_KEYWORDS = [
        'apply now',
        'application open',
        'application period',
        'submit application',
        'start application',
        'apply online',
        'application portal',
        'apply here',
        '立即申請',
        '開放申請',
        '申請入口'
    ]
    
    # 申請未開放的關鍵字
    CLOSED_KEYWORDS = [
        'application closed',
        'applications are closed',
        'not accepting applications',
        'coming soon',
        'opens on',
        'will open',
        '申請關閉',
        '尚未開放',
        '即將開放'
    ]
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化監控器"""
        super().__init__(config)
        self.schools_file = 'source_data/schools.yml'
        self.schools = []
        self.browser: Optional[Browser] = None
        self.playwright = None
    
    def load_schools(self) -> List[Dict[str, Any]]:
        """
        從 schools.yml 載入學校資料
        
        Returns:
            學校清單
        """
        data = self.load_yaml(self.schools_file)
        return data.get('schools', [])
    
    def detect_keywords(self, html_content: str, keywords: List[str]) -> bool:
        """
        在 HTML 內容中偵測關鍵字
        
        Args:
            html_content: HTML 內容
            keywords: 關鍵字清單
            
        Returns:
            是否找到關鍵字
        """
        # 轉為小寫進行不分大小寫的比對
        html_lower = html_content.lower()
        
        for keyword in keywords:
            if keyword.lower() in html_lower:
                self.logger.info(f"找到關鍵字: {keyword}")
                return True
        
        return False
    
    def analyze_html_structure(self, html_content: str) -> Dict[str, Any]:
        """
        分析 HTML 結構變化
        
        Args:
            html_content: HTML 內容
            
        Returns:
            分析結果
        """
        analysis = {
            'has_apply_button': False,
            'has_form': False,
            'has_date_info': False,
            'detected_dates': [],
            'apply_links': []
        }
        
        # 偵測申請按鈕
        apply_button_patterns = [
            r'<button[^>]*>.*?apply.*?</button>',
            r'<a[^>]*>.*?apply.*?</a>',
            r'class="[^"]*apply[^"]*"',
            r'id="[^"]*apply[^"]*"'
        ]
        
        for pattern in apply_button_patterns:
            if re.search(pattern, html_content, re.IGNORECASE):
                analysis['has_apply_button'] = True
                break
        
        # 偵測表單
        if re.search(r'<form[^>]*>.*?</form>', html_content, re.IGNORECASE | re.DOTALL):
            analysis['has_form'] = True
        
        # 偵測日期資訊
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{1,2}/\d{1,2}/\d{4}',  # DD/MM/YYYY or MM/DD/YYYY
            r'\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}'
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            analysis['detected_dates'].extend(matches)
        
        if analysis['detected_dates']:
            analysis['has_date_info'] = True
        
        # 偵測申請連結
        link_pattern = r'<a[^>]*href="([^"]*)"[^>]*>.*?apply.*?</a>'
        links = re.findall(link_pattern, html_content, re.IGNORECASE)
        analysis['apply_links'] = links
        
        return analysis
    
    async def check_school_status(self, school: Dict[str, Any], page: Page) -> Dict[str, Any]:
        """
        檢查單一學校的申請狀態
        
        Args:
            school: 學校資料
            page: Playwright Page 物件
            
        Returns:
            狀態資訊
        """
        school_name = school.get('name', 'Unknown')
        application_url = school.get('application_url', '')
        
        self.logger.info(f"檢查學校: {school_name}")
        
        if not application_url:
            self.logger.warning(f"{school_name} 沒有 application_url")
            return {
                'school': school_name,
                'status': 'no_url',
                'error': 'No application URL provided'
            }
        
        try:
            # 訪問申請頁面
            await page.goto(application_url, timeout=30000, wait_until='networkidle')
            
            # 等待頁面載入
            await page.wait_for_timeout(2000)
            
            # 取得頁面內容
            html_content = await page.content()
            
            # 偵測關鍵字
            has_open_keywords = self.detect_keywords(html_content, self.OPEN_KEYWORDS)
            has_closed_keywords = self.detect_keywords(html_content, self.CLOSED_KEYWORDS)
            
            # 分析 HTML 結構
            html_analysis = self.analyze_html_structure(html_content)
            
            # 判斷狀態
            if has_open_keywords or html_analysis['has_apply_button']:
                status = 'open'
            elif has_closed_keywords:
                status = 'closed'
            else:
                status = 'unknown'
            
            result = {
                'school': school_name,
                'url': application_url,
                'status': status,
                'has_open_keywords': has_open_keywords,
                'has_closed_keywords': has_closed_keywords,
                'has_apply_button': html_analysis['has_apply_button'],
                'has_form': html_analysis['has_form'],
                'detected_dates': html_analysis['detected_dates'],
                'apply_links': html_analysis['apply_links'],
                'checked_at': datetime.now().isoformat()
            }
            
            self.logger.info(f"{school_name} 狀態: {status}")
            return result
            
        except Exception as e:
            self.logger.error(f"檢查 {school_name} 時發生錯誤: {e}")
            return {
                'school': school_name,
                'url': application_url,
                'status': 'error',
                'error': str(e),
                'checked_at': datetime.now().isoformat()
            }
    
    async def run_async(self) -> bool:
        """
        執行監控（非同步版本）
        
        Returns:
            是否成功
        """
        try:
            # 載入學校資料
            self.schools = self.load_schools()
            
            if not self.schools:
                self.logger.warning("沒有學校資料")
                return False
            
            self.logger.info(f"開始監控 {len(self.schools)} 所學校")
            
            # 啟動 Playwright
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=True
            )
            
            # 建立瀏覽器上下文
            context = await self.browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            page = await context.new_page()
            
            # 檢查每所學校
            changes_detected = []
            
            for school in self.schools:
                school_name = school.get('name', 'Unknown')
                
                # 取得舊狀態
                old_status = self.load_saved_status(school_name)
                
                # 檢查新狀態
                new_status = await self.check_school_status(school, page)
                
                # 偵測變更
                if self.detect_changes(old_status, new_status):
                    self.logger.info(f"偵測到狀態變更: {school_name}")
                    changes_detected.append({
                        'school': school_name,
                        'old_status': old_status.get('status', 'unknown'),
                        'new_status': new_status.get('status', 'unknown'),
                        'url': new_status.get('url', ''),
                        'details': new_status
                    })
                    
                    # 發送通知
                    self.send_notification({
                        'type': 'application_status_change',
                        'school': school_name,
                        'old_status': old_status.get('status', 'unknown'),
                        'new_status': new_status.get('status', 'unknown'),
                        'url': new_status.get('url', ''),
                        'timestamp': datetime.now().isoformat()
                    })
                
                # 儲存新狀態
                self.save_status(school_name, new_status)
                
                # 避免過度頻繁的請求
                await page.wait_for_timeout(3000)
            
            # 關閉瀏覽器
            await context.close()
            await self.browser.close()
            await self.playwright.stop()
            
            # 產生摘要報告
            self.generate_report(changes_detected)
            
            self.logger.info(f"監控完成，偵測到 {len(changes_detected)} 個變更")
            return True
            
        except Exception as e:
            self.logger.error(f"監控執行失敗: {e}")
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            return False
    
    def run(self) -> bool:
        """
        執行監控（同步包裝）
        
        Returns:
            是否成功
        """
        return asyncio.run(self.run_async())
    
    def generate_report(self, changes: List[Dict[str, Any]]) -> None:
        """
        產生監控報告
        
        Args:
            changes: 變更清單
        """
        report_file = Path('reports/monitoring_reports') / f"opening_status_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_schools_checked': len(self.schools),
            'changes_detected': len(changes),
            'changes': changes
        }
        
        self.save_json(report, str(report_file))
        self.logger.info(f"報告已儲存: {report_file}")


def main():
    """主函式"""
    print("=== 申請開放狀態監控 ===\n")
    
    monitor = ApplicationOpeningMonitor()
    success = monitor.run()
    
    if success:
        print("\n✅ 監控完成")
    else:
        print("\n❌ 監控失敗")
        sys.exit(1)


if __name__ == '__main__':
    main()

