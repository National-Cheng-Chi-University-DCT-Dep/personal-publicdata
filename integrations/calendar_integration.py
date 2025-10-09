"""
Google Calendar 整合
自動同步申請截止日期至 Google Calendar
"""

import os
import sys
import pickle
import json
import yaml
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    print("⚠️ Google API 套件未安裝")
    print("請執行: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
    sys.exit(1)

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class CalendarIntegration:
    """Google Calendar 整合類別"""
    
    # Google Calendar API scopes
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    
    def __init__(self, 
                 credentials_path: str = 'credentials.json',
                 token_path: str = 'token.pickle',
                 calendar_id: str = 'primary'):
        """
        初始化 Calendar 整合
        
        Args:
            credentials_path: OAuth 2.0 憑證檔案路徑
            token_path: Token 儲存路徑
            calendar_id: 要使用的 Calendar ID
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.calendar_id = calendar_id
        self.creds = None
        self.service = None
        self.schools_file = 'source_data/schools.yml'
    
    def authenticate(self, force_reauth: bool = False) -> bool:
        """
        驗證 Google Calendar API
        
        Args:
            force_reauth: 是否強制重新授權
            
        Returns:
            是否成功驗證
        """
        try:
            self.logger.info("開始 Google Calendar 驗證")
            
            # 載入已存在的 token
            if os.path.exists(self.token_path) and not force_reauth:
                self.logger.info(f"載入已存在的 token: {self.token_path}")
                with open(self.token_path, 'rb') as token:
                    self.creds = pickle.load(token)
            
            # 如果沒有有效的憑證，進行授權
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.logger.info("Token 已過期，嘗試更新")
                    try:
                        self.creds.refresh(Request())
                        self.logger.info("✅ Token 更新成功")
                    except Exception as e:
                        self.logger.error(f"Token 更新失敗: {e}")
                        self.logger.info("需要重新授權")
                        self.creds = None
                
                if not self.creds:
                    if not os.path.exists(self.credentials_path):
                        self.logger.error(f"找不到憑證檔案: {self.credentials_path}")
                        self.logger.info("請先設定 Google Cloud 專案並下載 credentials.json")
                        return False
                    
                    self.logger.info("開始 OAuth 授權流程")
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, 
                        self.SCOPES
                    )
                    self.creds = flow.run_local_server(port=0)
                    self.logger.info("✅ 授權成功")
                
                # 儲存憑證以供下次使用
                with open(self.token_path, 'wb') as token:
                    pickle.dump(self.creds, token)
                self.logger.info(f"Token 已儲存至: {self.token_path}")
            
            # 建立 Calendar API service
            self.service = build('calendar', 'v3', credentials=self.creds)
            self.logger.info("✅ Google Calendar API 服務已建立")
            
            # 測試連線
            try:
                calendar = self.service.calendars().get(calendarId=self.calendar_id).execute()
                self.logger.info(f"✅ 成功連接到日曆: {calendar.get('summary', 'Primary Calendar')}")
            except HttpError as e:
                self.logger.error(f"連接日曆失敗: {e}")
                return False
            
            return True
        
        except Exception as e:
            self.logger.error(f"驗證過程發生錯誤: {e}")
            return False
    
    def load_schools(self) -> List[Dict[str, Any]]:
        """
        從 schools.yml 載入學校資料
        
        Returns:
            學校清單
        """
        try:
            with open(self.schools_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                schools = data.get('schools', [])
                self.logger.info(f"載入了 {len(schools)} 所學校的資料")
                return schools
        except Exception as e:
            self.logger.error(f"載入學校資料失敗: {e}")
            return []
    
    def create_deadline_event(self, 
                             school_name: str,
                             deadline: str,
                             program_name: Optional[str] = None,
                             application_url: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        為申請截止日期建立日曆事件
        
        Args:
            school_name: 學校名稱
            deadline: 截止日期 (YYYY-MM-DD 格式)
            program_name: 學程名稱（可選）
            application_url: 申請網址（可選）
            
        Returns:
            建立的事件資料，失敗則回傳 None
        """
        try:
            # 建立事件標題
            title = f"[Deadline] {school_name}"
            if program_name:
                title += f" - {program_name}"
            
            # 建立事件描述
            description = f"申請截止日期：{school_name}\n"
            if program_name:
                description += f"學程：{program_name}\n"
            if application_url:
                description += f"申請網址：{application_url}\n"
            description += f"\n⚠️ 請確保在此日期前完成所有申請文件的提交！"
            
            # 事件資料
            event = {
                'summary': title,
                'description': description,
                'start': {
                    'date': deadline,  # 全天事件
                    'timeZone': 'Asia/Taipei',
                },
                'end': {
                    'date': deadline,
                    'timeZone': 'Asia/Taipei',
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 7 * 24 * 60},  # 提前一週
                        {'method': 'popup', 'minutes': 7 * 24 * 60},
                        {'method': 'email', 'minutes': 3 * 24 * 60},  # 提前三天
                        {'method': 'popup', 'minutes': 3 * 24 * 60},
                        {'method': 'email', 'minutes': 1 * 24 * 60},  # 提前一天
                        {'method': 'popup', 'minutes': 1 * 24 * 60},
                    ],
                },
                'colorId': '11',  # 紅色，表示重要
            }
            
            # 建立事件
            event_result = self.service.events().insert(
                calendarId=self.calendar_id,
                body=event
            ).execute()
            
            self.logger.info(f"✅ 已建立事件: {title}")
            return event_result
        
        except HttpError as e:
            self.logger.error(f"建立事件失敗 ({school_name}): {e}")
            return None
        except Exception as e:
            self.logger.error(f"建立事件時發生錯誤 ({school_name}): {e}")
            return None
    
    def find_existing_event(self, school_name: str) -> Optional[Dict[str, Any]]:
        """
        尋找已存在的事件
        
        Args:
            school_name: 學校名稱
            
        Returns:
            找到的事件，若無則回傳 None
        """
        try:
            # 搜尋未來 365 天內的事件
            now = datetime.utcnow()
            time_min = now.isoformat() + 'Z'
            time_max = (now + timedelta(days=365)).isoformat() + 'Z'
            
            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                q=school_name,  # 搜尋包含學校名稱的事件
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            # 尋找標題包含 [Deadline] 和學校名稱的事件
            for event in events:
                summary = event.get('summary', '')
                if '[Deadline]' in summary and school_name in summary:
                    return event
            
            return None
        
        except HttpError as e:
            self.logger.error(f"搜尋事件失敗 ({school_name}): {e}")
            return None
    
    def update_event(self, event_id: str, new_deadline: str) -> bool:
        """
        更新現有事件
        
        Args:
            event_id: 事件 ID
            new_deadline: 新的截止日期
            
        Returns:
            是否成功
        """
        try:
            # 取得現有事件
            event = self.service.events().get(
                calendarId=self.calendar_id,
                eventId=event_id
            ).execute()
            
            # 更新日期
            event['start']['date'] = new_deadline
            event['end']['date'] = new_deadline
            
            # 更新事件
            updated_event = self.service.events().update(
                calendarId=self.calendar_id,
                eventId=event_id,
                body=event
            ).execute()
            
            self.logger.info(f"✅ 已更新事件: {event.get('summary')}")
            return True
        
        except HttpError as e:
            self.logger.error(f"更新事件失敗: {e}")
            return False
    
    def delete_event(self, event_id: str) -> bool:
        """
        刪除事件
        
        Args:
            event_id: 事件 ID
            
        Returns:
            是否成功
        """
        try:
            self.service.events().delete(
                calendarId=self.calendar_id,
                eventId=event_id
            ).execute()
            
            self.logger.info(f"✅ 已刪除事件: {event_id}")
            return True
        
        except HttpError as e:
            self.logger.error(f"刪除事件失敗: {e}")
            return False
    
    def sync_all_deadlines(self, update_existing: bool = True) -> Dict[str, Any]:
        """
        同步所有截止日期至 Google Calendar
        
        Args:
            update_existing: 是否更新已存在的事件
            
        Returns:
            同步結果統計
        """
        try:
            self.logger.info("=== 開始同步截止日期 ===")
            
            # 載入學校資料
            schools = self.load_schools()
            
            results = {
                'total': len(schools),
                'created': 0,
                'updated': 0,
                'skipped': 0,
                'failed': 0,
                'details': []
            }
            
            for school in schools:
                school_name = school.get('name', 'Unknown')
                deadline = school.get('deadline')
                
                if not deadline:
                    self.logger.info(f"⏭️  跳過 {school_name}（無截止日期）")
                    results['skipped'] += 1
                    results['details'].append({
                        'school': school_name,
                        'action': 'skipped',
                        'reason': 'no_deadline'
                    })
                    continue
                
                try:
                    # 檢查是否已存在
                    existing_event = self.find_existing_event(school_name)
                    
                    if existing_event:
                        if update_existing:
                            # 檢查日期是否需要更新
                            current_date = existing_event.get('start', {}).get('date')
                            if current_date != deadline:
                                self.update_event(existing_event['id'], deadline)
                                results['updated'] += 1
                                results['details'].append({
                                    'school': school_name,
                                    'action': 'updated',
                                    'old_date': current_date,
                                    'new_date': deadline
                                })
                            else:
                                self.logger.info(f"⏭️  跳過 {school_name}（日期相同）")
                                results['skipped'] += 1
                                results['details'].append({
                                    'school': school_name,
                                    'action': 'skipped',
                                    'reason': 'no_change'
                                })
                        else:
                            self.logger.info(f"⏭️  跳過 {school_name}（已存在）")
                            results['skipped'] += 1
                            results['details'].append({
                                'school': school_name,
                                'action': 'skipped',
                                'reason': 'already_exists'
                            })
                    else:
                        # 建立新事件
                        event = self.create_deadline_event(
                            school_name=school_name,
                            deadline=deadline,
                            program_name=school.get('program_name'),
                            application_url=school.get('application_url')
                        )
                        
                        if event:
                            results['created'] += 1
                            results['details'].append({
                                'school': school_name,
                                'action': 'created',
                                'deadline': deadline,
                                'event_id': event.get('id')
                            })
                        else:
                            results['failed'] += 1
                            results['details'].append({
                                'school': school_name,
                                'action': 'failed'
                            })
                
                except Exception as e:
                    self.logger.error(f"處理 {school_name} 時發生錯誤: {e}")
                    results['failed'] += 1
                    results['details'].append({
                        'school': school_name,
                        'action': 'failed',
                        'error': str(e)
                    })
            
            # 顯示摘要
            self.logger.info("\n=== 同步完成 ===")
            self.logger.info(f"總計: {results['total']} 所學校")
            self.logger.info(f"✅ 新建: {results['created']}")
            self.logger.info(f"🔄 更新: {results['updated']}")
            self.logger.info(f"⏭️  跳過: {results['skipped']}")
            self.logger.info(f"❌ 失敗: {results['failed']}")
            
            return results
        
        except Exception as e:
            self.logger.error(f"同步過程發生錯誤: {e}")
            return {'error': str(e)}
    
    def list_deadline_events(self, days_ahead: int = 90) -> List[Dict[str, Any]]:
        """
        列出未來的截止日期事件
        
        Args:
            days_ahead: 查詢未來幾天內的事件
            
        Returns:
            事件清單
        """
        try:
            now = datetime.utcnow()
            time_min = now.isoformat() + 'Z'
            time_max = (now + timedelta(days=days_ahead)).isoformat() + 'Z'
            
            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                q='[Deadline]',  # 搜尋包含 [Deadline] 的事件
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            self.logger.info(f"找到 {len(events)} 個截止日期事件")
            
            return events
        
        except HttpError as e:
            self.logger.error(f"列出事件失敗: {e}")
            return []


def main():
    """主函式"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Google Calendar 整合工具')
    parser.add_argument('--setup', action='store_true', help='首次設定（進行 OAuth 授權）')
    parser.add_argument('--sync', action='store_true', help='同步所有截止日期')
    parser.add_argument('--list', action='store_true', help='列出未來的截止日期事件')
    parser.add_argument('--update', action='store_true', help='更新已存在的事件')
    parser.add_argument('--days', type=int, default=90, help='查詢未來幾天內的事件（預設 90 天）')
    
    args = parser.parse_args()
    
    print("""
╔══════════════════════════════════════════════════════════╗
║         Google Calendar 整合工具                        ║
║         Google Calendar Integration Tool                ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    # 建立 Calendar 整合實例
    calendar = CalendarIntegration()
    
    # 驗證
    if not calendar.authenticate(force_reauth=args.setup):
        print("\n❌ 驗證失敗")
        print("\n如果這是首次使用，請執行:")
        print("  python integrations/calendar_integration.py --setup")
        sys.exit(1)
    
    # 執行動作
    if args.list:
        print(f"\n📅 列出未來 {args.days} 天內的截止日期事件:\n")
        events = calendar.list_deadline_events(days_ahead=args.days)
        
        if not events:
            print("  沒有找到事件")
        else:
            for event in events:
                start = event.get('start', {}).get('date', '未知日期')
                summary = event.get('summary', '未命名')
                print(f"  📌 {start} - {summary}")
    
    elif args.sync:
        print("\n🔄 開始同步截止日期...\n")
        results = calendar.sync_all_deadlines(update_existing=args.update)
        
        if 'error' in results:
            print(f"\n❌ 同步失敗: {results['error']}")
            sys.exit(1)
        else:
            print("\n✅ 同步完成！")
            print(f"\n詳細結果:")
            print(f"  ✅ 新建: {results['created']}")
            print(f"  🔄 更新: {results['updated']}")
            print(f"  ⏭️  跳過: {results['skipped']}")
            print(f"  ❌ 失敗: {results['failed']}")
    
    else:
        print("\n請指定動作:")
        print("  --setup  : 首次設定")
        print("  --sync   : 同步截止日期")
        print("  --list   : 列出事件")
        print("  --update : 同步時更新已存在的事件")
        print("\n範例:")
        print("  python integrations/calendar_integration.py --setup")
        print("  python integrations/calendar_integration.py --sync")
        print("  python integrations/calendar_integration.py --sync --update")
        print("  python integrations/calendar_integration.py --list --days 30")


if __name__ == '__main__':
    main()

