"""
簽證與移民資訊監控系統
Visa and Immigration Information Monitor

功能：
- 監控各國簽證資訊頁面變更
- 使用 hash 值偵測頁面內容變化
- 簽證預約系統名額監控（進階）
- 自動通知頁面更新
"""

import asyncio
import hashlib
import os
import sys
import yaml
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from playwright.async_api import async_playwright, Browser, Page

sys.path.append(str(Path(__file__).parent.parent))
from monitoring.base_monitor import BaseMonitor

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class VisaMonitor(BaseMonitor):
    """簽證資訊監控器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化監控器"""
        super().__init__(config)
        self.visa_file = 'source_data/visa_requirements.yml'
        self.hash_storage_dir = Path('reports/status_history/visa_hashes')
        self.hash_storage_dir.mkdir(parents=True, exist_ok=True)
        self.playwright = None
        self.browser: Optional[Browser] = None
    
    def load_visa_data(self) -> Dict[str, Any]:
        """載入簽證資料"""
        try:
            with open(self.visa_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                countries = data.get('countries', [])
                self.logger.info(f"載入了 {len(countries)} 個國家的簽證資訊")
                return data
        except Exception as e:
            self.logger.error(f"載入簽證資料失敗: {e}")
            return {'countries': []}
    
    def save_visa_data(self, data: Dict[str, Any]) -> bool:
        """儲存簽證資料"""
        try:
            with open(self.visa_file, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
            self.logger.info("簽證資料已儲存")
            return True
        except Exception as e:
            self.logger.error(f"儲存簽證資料失敗: {e}")
            return False
    
    def calculate_page_hash(self, content: str, method: str = 'content') -> str:
        """
        計算頁面內容的 hash 值
        
        Args:
            content: 頁面內容
            method: hash 方法 ('content' 或 'structure')
            
        Returns:
            SHA256 hash 值
        """
        if method == 'structure':
            # 移除空白字元和換行，只保留結構
            content = ''.join(content.split())
        
        # 計算 SHA256
        hash_value = hashlib.sha256(content.encode('utf-8')).hexdigest()
        return hash_value
    
    def load_saved_hash(self, country_name: str) -> Optional[Dict[str, Any]]:
        """
        載入已儲存的 hash 值
        
        Args:
            country_name: 國家名稱
            
        Returns:
            Hash 資料
        """
        hash_file = self.hash_storage_dir / f"{country_name.replace(' ', '_')}_hash.json"
        if hash_file.exists():
            try:
                with open(hash_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"載入 hash 失敗 ({country_name}): {e}")
        return None
    
    def save_hash(self, country_name: str, hash_data: Dict[str, Any]) -> bool:
        """
        儲存 hash 值
        
        Args:
            country_name: 國家名稱
            hash_data: Hash 資料
            
        Returns:
            是否成功
        """
        hash_file = self.hash_storage_dir / f"{country_name.replace(' ', '_')}_hash.json"
        try:
            with open(hash_file, 'w', encoding='utf-8') as f:
                json.dump(hash_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            self.logger.error(f"儲存 hash 失敗 ({country_name}): {e}")
            return False
    
    async def fetch_page_content(self, page: Page, url: str) -> Optional[str]:
        """
        抓取頁面內容
        
        Args:
            page: Playwright Page 物件
            url: 目標 URL
            
        Returns:
            頁面內容
        """
        try:
            self.logger.info(f"正在訪問: {url}")
            
            # 訪問頁面
            response = await page.goto(url, timeout=30000, wait_until='networkidle')
            
            if not response or response.status != 200:
                self.logger.warning(f"頁面回應異常: {response.status if response else 'No response'}")
                return None
            
            # 等待頁面完全載入
            await page.wait_for_timeout(3000)
            
            # 取得頁面內容
            content = await page.content()
            
            self.logger.info(f"✅ 成功抓取頁面 ({len(content)} 字元)")
            return content
        
        except Exception as e:
            self.logger.error(f"抓取頁面失敗 ({url}): {e}")
            return None
    
    def extract_relevant_content(self, html_content: str) -> str:
        """
        從 HTML 中提取相關內容（移除不重要的變動部分）
        
        Args:
            html_content: HTML 內容
            
        Returns:
            處理後的內容
        """
        # 移除常見的動態內容
        import re
        
        # 移除 script 和 style 標籤
        content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL)
        content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL)
        
        # 移除註解
        content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
        
        # 移除常見的動態元素
        # 時間戳記、session ID 等
        content = re.sub(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', 'TIMESTAMP', content)
        content = re.sub(r'session_id=[^&\s"\']+', 'session_id=SESSION', content)
        content = re.sub(r'csrf_token=[^&\s"\']+', 'csrf_token=TOKEN', content)
        
        return content
    
    async def check_page_changes(self, country_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        檢查單一國家的頁面變更
        
        Args:
            country_data: 國家資料
            
        Returns:
            檢查結果
        """
        country_name = country_data.get('name')
        info_url = country_data.get('information_page_url')
        
        result = {
            'country': country_name,
            'url': info_url,
            'changed': False,
            'checked_at': datetime.now().isoformat()
        }
        
        if not info_url:
            result['error'] = 'No URL provided'
            return result
        
        try:
            # 建立頁面
            context = await self.browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            page = await context.new_page()
            
            # 抓取頁面內容
            html_content = await self.fetch_page_content(page, info_url)
            
            if not html_content:
                result['error'] = 'Failed to fetch page'
                await context.close()
                return result
            
            # 提取相關內容
            relevant_content = self.extract_relevant_content(html_content)
            
            # 計算 hash
            new_hash = self.calculate_page_hash(relevant_content, method='content')
            
            # 載入舊 hash
            old_hash_data = self.load_saved_hash(country_name)
            
            if old_hash_data:
                old_hash = old_hash_data.get('hash')
                
                if old_hash != new_hash:
                    self.logger.info(f"⚠️ 偵測到變更: {country_name}")
                    result['changed'] = True
                    result['old_hash'] = old_hash
                    result['new_hash'] = new_hash
                    result['last_checked'] = old_hash_data.get('checked_at')
                else:
                    self.logger.info(f"✅ 無變更: {country_name}")
            else:
                self.logger.info(f"📝 首次檢查: {country_name}")
                result['first_check'] = True
            
            # 儲存新 hash
            hash_data = {
                'hash': new_hash,
                'checked_at': datetime.now().isoformat(),
                'url': info_url
            }
            self.save_hash(country_name, hash_data)
            
            # 關閉頁面
            await context.close()
            
            return result
        
        except Exception as e:
            self.logger.error(f"檢查頁面變更失敗 ({country_name}): {e}")
            result['error'] = str(e)
            return result
    
    async def check_appointment_availability(self, country_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        檢查簽證預約名額（進階功能）
        
        Args:
            country_data: 國家資料
            
        Returns:
            預約名額資訊
        """
        country_name = country_data.get('name')
        appointment_url = country_data.get('appointment_system_url')
        
        if not appointment_url:
            self.logger.info(f"{country_name} 沒有預約系統 URL")
            return None
        
        try:
            self.logger.info(f"檢查預約名額: {country_name}")
            
            context = await self.browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            page = await context.new_page()
            
            # 訪問預約頁面
            await page.goto(appointment_url, timeout=30000)
            await page.wait_for_timeout(3000)
            
            # 嘗試偵測可用名額的關鍵字
            content = await page.content()
            
            availability_keywords = {
                'available': ['available', 'slots available', 'book now', '可預約', '有名額'],
                'unavailable': ['no appointments', 'fully booked', 'not available', '無名額', '已額滿']
            }
            
            has_availability = False
            status = 'unknown'
            
            content_lower = content.lower()
            
            for keyword in availability_keywords['available']:
                if keyword in content_lower:
                    has_availability = True
                    status = 'available'
                    break
            
            if not has_availability:
                for keyword in availability_keywords['unavailable']:
                    if keyword in content_lower:
                        status = 'unavailable'
                        break
            
            result = {
                'country': country_name,
                'appointment_url': appointment_url,
                'status': status,
                'has_availability': has_availability,
                'checked_at': datetime.now().isoformat()
            }
            
            await context.close()
            
            return result
        
        except Exception as e:
            self.logger.error(f"檢查預約名額失敗 ({country_name}): {e}")
            return {
                'country': country_name,
                'error': str(e),
                'checked_at': datetime.now().isoformat()
            }
    
    async def run_async(self) -> bool:
        """執行監控（非同步版本）"""
        try:
            self.logger.info("=== 開始監控簽證資訊 ===")
            
            # 載入簽證資料
            visa_data = self.load_visa_data()
            countries = visa_data.get('countries', [])
            
            if not countries:
                self.logger.warning("沒有國家資料")
                return False
            
            # 啟動 Playwright
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(headless=True)
            
            results = {
                'timestamp': datetime.now().isoformat(),
                'total_countries': len(countries),
                'changes_detected': 0,
                'countries': []
            }
            
            # 檢查每個國家
            for country in countries:
                country_name = country.get('name')
                
                # 檢查是否啟用監控
                if not country.get('monitor_enabled', False):
                    self.logger.info(f"⏭️  跳過 {country_name}（監控未啟用）")
                    continue
                
                # 檢查頁面變更
                change_result = await self.check_page_changes(country)
                results['countries'].append(change_result)
                
                if change_result.get('changed'):
                    results['changes_detected'] += 1
                    
                    # 發送通知
                    self.send_notification({
                        'type': 'visa_info_change',
                        'country': country_name,
                        'url': change_result.get('url'),
                        'timestamp': datetime.now().isoformat()
                    })
                    
                    # 更新 visa_requirements.yml 的 last_checked
                    country['last_checked'] = datetime.now().strftime('%Y-%m-%d')
                
                # 如果有預約系統 URL，檢查名額（可選）
                if country.get('appointment_system_url'):
                    appointment_result = await self.check_appointment_availability(country)
                    if appointment_result:
                        change_result['appointment'] = appointment_result
                        
                        # 如果有名額，發送緊急通知
                        if appointment_result.get('has_availability'):
                            self.send_notification({
                                'type': 'visa_appointment_available',
                                'country': country_name,
                                'url': appointment_result.get('appointment_url'),
                                'priority': 'high',
                                'timestamp': datetime.now().isoformat()
                            })
                
                # 避免過度頻繁的請求
                await asyncio.sleep(5)
            
            # 儲存更新的簽證資料
            self.save_visa_data(visa_data)
            
            # 關閉瀏覽器
            await self.browser.close()
            await self.playwright.stop()
            
            # 生成報告
            self.generate_report(results)
            
            # 顯示摘要
            self.logger.info("\n=== 監控完成 ===")
            self.logger.info(f"檢查國家數: {results['total_countries']}")
            self.logger.info(f"偵測到變更: {results['changes_detected']}")
            
            return True
        
        except Exception as e:
            self.logger.error(f"監控執行失敗: {e}")
            
            # 清理資源
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
    
    def run(self) -> bool:
        """執行監控（同步包裝）"""
        return asyncio.run(self.run_async())
    
    def generate_report(self, results: Dict[str, Any]) -> None:
        """
        生成監控報告
        
        Args:
            results: 檢查結果
        """
        report_dir = Path('reports/monitoring_reports')
        report_dir.mkdir(parents=True, exist_ok=True)
        
        report_file = report_dir / f"visa_monitor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"報告已儲存: {report_file}")
            
            # 也生成 Markdown 版本
            self.generate_markdown_report(results)
        
        except Exception as e:
            self.logger.error(f"生成報告失敗: {e}")
    
    def generate_markdown_report(self, results: Dict[str, Any]) -> None:
        """生成 Markdown 報告"""
        report_dir = Path('reports/monitoring_reports')
        report_file = report_dir / f"visa_monitor_{datetime.now().strftime('%Y%m%d')}.md"
        
        try:
            markdown = f"# 簽證資訊監控報告\n\n"
            markdown += f"**監控時間**: {results['timestamp']}\n\n"
            markdown += f"## 📊 摘要\n\n"
            markdown += f"- 檢查國家數: {results['total_countries']}\n"
            markdown += f"- 偵測到變更: {results['changes_detected']}\n\n"
            
            if results['changes_detected'] > 0:
                markdown += f"## ⚠️ 變更清單\n\n"
                
                for country_result in results['countries']:
                    if country_result.get('changed'):
                        markdown += f"### {country_result['country']}\n\n"
                        markdown += f"- **URL**: {country_result['url']}\n"
                        markdown += f"- **檢查時間**: {country_result['checked_at']}\n"
                        markdown += f"- **狀態**: 內容已變更\n\n"
                        
                        if 'appointment' in country_result:
                            app = country_result['appointment']
                            markdown += f"**預約狀態**: {app.get('status', 'unknown')}\n\n"
            
            markdown += f"\n## ✅ 無變更的國家\n\n"
            
            for country_result in results['countries']:
                if not country_result.get('changed'):
                    markdown += f"- {country_result['country']}\n"
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(markdown)
            
            self.logger.info(f"Markdown 報告已儲存: {report_file}")
        
        except Exception as e:
            self.logger.error(f"生成 Markdown 報告失敗: {e}")


def main():
    """主函式"""
    print("""
╔══════════════════════════════════════════════════════════╗
║         簽證與移民資訊監控系統                          ║
║         Visa & Immigration Information Monitor          ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    monitor = VisaMonitor()
    success = monitor.run()
    
    if success:
        print("\n✅ 監控完成")
        print("📄 報告已儲存至: reports/monitoring_reports/")
        print("🔍 Hash 值已儲存至: reports/status_history/visa_hashes/")
    else:
        print("\n❌ 監控失敗")
        sys.exit(1)


if __name__ == '__main__':
    main()

