"""
推薦信追蹤系統
Recommendation Letter Tracking System

功能：
- 追蹤每所學校的推薦信狀態
- 生成推薦信狀態總覽
- 自動生成提醒郵件草稿
- 檢測逾期未提交的推薦信
"""

import yaml
import sys
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from jinja2 import Template

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class RecommendationTracker:
    """推薦信追蹤系統"""
    
    # 狀態定義
    STATUS_NOT_REQUESTED = 'not_requested'
    STATUS_REQUESTED = 'requested'
    STATUS_SUBMITTED = 'submitted'
    STATUS_CONFIRMED = 'confirmed'
    
    STATUS_COLORS = {
        'not_requested': '⚪',
        'requested': '🟡',
        'submitted': '🟢',
        'confirmed': '✅'
    }
    
    def __init__(self):
        """初始化追蹤系統"""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.recommenders_file = 'source_data/recommenders.yml'
        self.schools_file = 'source_data/schools.yml'
        self.dashboard_file = 'final_applications/application_dashboard.md'
        self.email_templates_dir = Path('templates/email_templates')
        self.email_templates_dir.mkdir(parents=True, exist_ok=True)
    
    def load_recommenders(self) -> Dict[str, Any]:
        """載入推薦人資料"""
        try:
            with open(self.recommenders_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                self.logger.info(f"載入了 {len(data.get('recommenders', []))} 位推薦人")
                return data
        except Exception as e:
            self.logger.error(f"載入推薦人資料失敗: {e}")
            return {'recommenders': []}
    
    def load_schools(self) -> List[Dict[str, Any]]:
        """載入學校資料"""
        try:
            with open(self.schools_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                schools = data.get('schools', [])
                self.logger.info(f"載入了 {len(schools)} 所學校")
                return schools
        except Exception as e:
            self.logger.error(f"載入學校資料失敗: {e}")
            return []
    
    def save_recommenders(self, data: Dict[str, Any]) -> bool:
        """儲存推薦人資料"""
        try:
            with open(self.recommenders_file, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
            self.logger.info("推薦人資料已儲存")
            return True
        except Exception as e:
            self.logger.error(f"儲存推薦人資料失敗: {e}")
            return False
    
    def get_school_deadline(self, school_name: str, schools: List[Dict[str, Any]]) -> Optional[str]:
        """取得學校截止日期"""
        for school in schools:
            if school.get('name') == school_name or school.get('name_english') == school_name:
                return school.get('deadline')
        return None
    
    def calculate_days_until_deadline(self, deadline_str: str) -> Optional[int]:
        """計算距離截止日期的天數"""
        try:
            deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date()
            today = datetime.now().date()
            delta = deadline - today
            return delta.days
        except:
            return None
    
    def get_status_emoji(self, status: str) -> str:
        """取得狀態 emoji"""
        return self.STATUS_COLORS.get(status, '❓')
    
    def generate_status_table(self) -> List[Dict[str, Any]]:
        """生成推薦信狀態總覽表格"""
        recommenders_data = self.load_recommenders()
        schools = self.load_schools()
        
        table_rows = []
        
        for recommender in recommenders_data.get('recommenders', []):
            recommender_name = recommender.get('name')
            recommender_title = recommender.get('title')
            recommender_email = recommender.get('email')
            
            # 檢查是否有學校特定狀態
            school_statuses = recommender.get('school_specific_status', [])
            
            if not school_statuses:
                # 如果沒有學校特定狀態，創建預設狀態
                self.logger.info(f"{recommender_name} 沒有學校特定狀態，需要手動設定")
                continue
            
            for school_status in school_statuses:
                school_name = school_status.get('school')
                status = school_status.get('status', 'not_requested')
                requested_date = school_status.get('requested_date', 'N/A')
                submitted_date = school_status.get('submitted_date', 'N/A')
                deadline = self.get_school_deadline(school_name, schools)
                
                days_remaining = None
                if deadline:
                    days_remaining = self.calculate_days_until_deadline(deadline)
                
                row = {
                    'recommender_name': recommender_name,
                    'recommender_title': recommender_title,
                    'recommender_email': recommender_email,
                    'school': school_name,
                    'status': status,
                    'status_emoji': self.get_status_emoji(status),
                    'requested_date': requested_date,
                    'submitted_date': submitted_date,
                    'deadline': deadline or 'N/A',
                    'days_remaining': days_remaining
                }
                
                table_rows.append(row)
        
        return table_rows
    
    def check_overdue_items(self) -> List[Dict[str, Any]]:
        """檢查逾期或即將逾期的推薦信"""
        status_table = self.generate_status_table()
        overdue_items = []
        
        for row in status_table:
            # 只檢查尚未提交的推薦信
            if row['status'] in ['not_requested', 'requested']:
                days_remaining = row['days_remaining']
                
                if days_remaining is not None:
                    # 如果距離截止日期不到 14 天
                    if days_remaining < 14:
                        urgency = 'critical' if days_remaining < 7 else 'warning'
                        overdue_items.append({
                            **row,
                            'urgency': urgency
                        })
        
        return sorted(overdue_items, key=lambda x: x['days_remaining'] if x['days_remaining'] is not None else 999)
    
    def generate_request_email(self, recommender_name: str, 
                               school_name: str, 
                               deadline: str,
                               program_name: Optional[str] = None) -> str:
        """生成推薦信請求郵件草稿"""
        
        template = Template("""
主旨：推薦信申請請求 - {{ school_name }}

親愛的 {{ recommender_name }}：

您好！

我正在申請 {{ school_name }}{% if program_name %} 的 {{ program_name }} 學程{% endif %}，誠摯地希望能獲得您的推薦。

**申請資訊：**
- 學校：{{ school_name }}
{% if program_name %}- 學程：{{ program_name }}
{% endif %}- 申請截止日期：{{ deadline }}
- 推薦信提交截止日期：{{ deadline }}

**為什麼選擇這所學校：**
[請在此說明為什麼申請這所學校，以及該學程如何符合您的職涯目標]

**您的推薦可以強調的面向：**
- 學術能力與研究潛力
- 技術專長（特別是網路安全、AI 等領域）
- 專案領導與團隊合作能力
- 解決問題與創新思維

**所需文件：**
我會另外提供以下文件供您參考：
- 我的履歷
- 個人陳述（Statement of Purpose）
- 專案作品集

如果您需要任何額外資訊，或對推薦信內容有任何疑問，請隨時告訴我。

非常感謝您願意抽空為我撰寫推薦信！您的支持對我意義重大。

祝好
李培辰
""")
        
        return template.render(
            recommender_name=recommender_name,
            school_name=school_name,
            program_name=program_name,
            deadline=deadline
        )
    
    def generate_reminder_email(self, recommender_name: str, 
                                school_name: str, 
                                deadline: str,
                                days_remaining: int) -> str:
        """生成提醒郵件草稿"""
        
        urgency_note = ""
        if days_remaining < 7:
            urgency_note = "⚠️ **緊急提醒**：距離截止日期不到一週！"
        elif days_remaining < 14:
            urgency_note = "⏰ **溫馨提醒**：距離截止日期約兩週"
        
        template = Template("""
主旨：溫馨提醒 - {{ school_name }} 推薦信截止日期

親愛的 {{ recommender_name }}：

希望您一切安好。

{{ urgency_note }}

我想禮貌地提醒您，我申請 {{ school_name }} 的推薦信截止日期為 **{{ deadline }}**（還有 {{ days_remaining }} 天）。

如果您需要任何額外的資訊或文件，請隨時告訴我。我非常樂意提供任何能幫助您撰寫推薦信的資料。

再次感謝您的支持與協助！

祝好
李培辰
""")
        
        return template.render(
            recommender_name=recommender_name,
            school_name=school_name,
            deadline=deadline,
            days_remaining=days_remaining,
            urgency_note=urgency_note
        )
    
    def save_email_draft(self, filename: str, content: str) -> Path:
        """儲存郵件草稿"""
        file_path = self.email_templates_dir / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        self.logger.info(f"郵件草稿已儲存: {file_path}")
        return file_path
    
    def generate_all_email_drafts(self) -> Dict[str, List[Path]]:
        """生成所有郵件草稿"""
        status_table = self.generate_status_table()
        overdue_items = self.check_overdue_items()
        
        generated_files = {
            'request_emails': [],
            'reminder_emails': []
        }
        
        # 生成請求郵件（針對 not_requested 狀態）
        for row in status_table:
            if row['status'] == 'not_requested':
                email_content = self.generate_request_email(
                    recommender_name=row['recommender_name'],
                    school_name=row['school'],
                    deadline=row['deadline']
                )
                
                filename = f"request_{row['school'].replace(' ', '_')}_{row['recommender_name'].replace(' ', '_')}.txt"
                file_path = self.save_email_draft(filename, email_content)
                generated_files['request_emails'].append(file_path)
        
        # 生成提醒郵件（針對逾期項目）
        for item in overdue_items:
            email_content = self.generate_reminder_email(
                recommender_name=item['recommender_name'],
                school_name=item['school'],
                deadline=item['deadline'],
                days_remaining=item['days_remaining']
            )
            
            filename = f"reminder_{item['school'].replace(' ', '_')}_{item['recommender_name'].replace(' ', '_')}.txt"
            file_path = self.save_email_draft(filename, email_content)
            generated_files['reminder_emails'].append(file_path)
        
        return generated_files
    
    def render_markdown_table(self, status_table: List[Dict[str, Any]]) -> str:
        """渲染 Markdown 表格"""
        
        markdown = "## 📧 推薦信狀態總覽\n\n"
        markdown += f"**更新時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        # 統計資訊
        total = len(status_table)
        not_requested = sum(1 for row in status_table if row['status'] == 'not_requested')
        requested = sum(1 for row in status_table if row['status'] == 'requested')
        submitted = sum(1 for row in status_table if row['status'] == 'submitted')
        confirmed = sum(1 for row in status_table if row['status'] == 'confirmed')
        
        markdown += "### 📊 統計\n\n"
        markdown += f"- 總計：{total} 封推薦信\n"
        markdown += f"- ⚪ 尚未請求：{not_requested}\n"
        markdown += f"- 🟡 已請求：{requested}\n"
        markdown += f"- 🟢 已提交：{submitted}\n"
        markdown += f"- ✅ 已確認：{confirmed}\n\n"
        
        # 狀態表格
        markdown += "### 📋 詳細狀態\n\n"
        markdown += "| 推薦人 | 學校 | 狀態 | 請求日期 | 提交日期 | 截止日期 | 剩餘天數 |\n"
        markdown += "|--------|------|------|----------|----------|----------|----------|\n"
        
        for row in status_table:
            days_str = f"{row['days_remaining']} 天" if row['days_remaining'] is not None else "N/A"
            if row['days_remaining'] is not None and row['days_remaining'] < 7:
                days_str = f"⚠️ {days_str}"
            
            markdown += f"| {row['recommender_name']} "
            markdown += f"| {row['school']} "
            markdown += f"| {row['status_emoji']} {row['status']} "
            markdown += f"| {row['requested_date']} "
            markdown += f"| {row['submitted_date']} "
            markdown += f"| {row['deadline']} "
            markdown += f"| {days_str} |\n"
        
        return markdown
    
    def render_overdue_section(self, overdue_items: List[Dict[str, Any]]) -> str:
        """渲染逾期提醒區塊"""
        if not overdue_items:
            return "\n### ✅ 所有推薦信都在預定時程內\n\n"
        
        markdown = "\n### ⚠️ 需要關注的推薦信\n\n"
        
        critical = [item for item in overdue_items if item['urgency'] == 'critical']
        warning = [item for item in overdue_items if item['urgency'] == 'warning']
        
        if critical:
            markdown += "#### 🚨 緊急（不到 7 天）\n\n"
            for item in critical:
                markdown += f"- **{item['school']}** - {item['recommender_name']}\n"
                markdown += f"  - 狀態：{item['status']}\n"
                markdown += f"  - 截止日期：{item['deadline']}\n"
                markdown += f"  - 剩餘：{item['days_remaining']} 天\n\n"
        
        if warning:
            markdown += "#### ⏰ 提醒（不到 14 天）\n\n"
            for item in warning:
                markdown += f"- **{item['school']}** - {item['recommender_name']}\n"
                markdown += f"  - 狀態：{item['status']}\n"
                markdown += f"  - 截止日期：{item['deadline']}\n"
                markdown += f"  - 剩餘：{item['days_remaining']} 天\n\n"
        
        return markdown
    
    def update_dashboard(self) -> bool:
        """更新 application dashboard"""
        try:
            status_table = self.generate_status_table()
            overdue_items = self.check_overdue_items()
            
            markdown = self.render_markdown_table(status_table)
            markdown += self.render_overdue_section(overdue_items)
            
            # 如果 dashboard 存在，附加內容
            if Path(self.dashboard_file).exists():
                with open(self.dashboard_file, 'a', encoding='utf-8') as f:
                    f.write('\n\n---\n\n')
                    f.write(markdown)
            else:
                # 建立新 dashboard
                with open(self.dashboard_file, 'w', encoding='utf-8') as f:
                    f.write('# 申請進度儀表板\n\n')
                    f.write(markdown)
            
            self.logger.info(f"Dashboard 已更新: {self.dashboard_file}")
            return True
        
        except Exception as e:
            self.logger.error(f"更新 dashboard 失敗: {e}")
            return False
    
    def generate_report(self) -> Dict[str, Any]:
        """生成完整報告"""
        status_table = self.generate_status_table()
        overdue_items = self.check_overdue_items()
        email_drafts = self.generate_all_email_drafts()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_recommendations': len(status_table),
            'status_breakdown': {
                'not_requested': sum(1 for row in status_table if row['status'] == 'not_requested'),
                'requested': sum(1 for row in status_table if row['status'] == 'requested'),
                'submitted': sum(1 for row in status_table if row['status'] == 'submitted'),
                'confirmed': sum(1 for row in status_table if row['status'] == 'confirmed'),
            },
            'overdue_count': len(overdue_items),
            'critical_count': sum(1 for item in overdue_items if item['urgency'] == 'critical'),
            'warning_count': sum(1 for item in overdue_items if item['urgency'] == 'warning'),
            'email_drafts_generated': {
                'requests': len(email_drafts['request_emails']),
                'reminders': len(email_drafts['reminder_emails'])
            }
        }
        
        return report


def main():
    """主函式"""
    print("""
╔══════════════════════════════════════════════════════════╗
║         推薦信追蹤系統                                  ║
║         Recommendation Letter Tracking System           ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    tracker = RecommendationTracker()
    
    print("\n📊 生成推薦信狀態報告...\n")
    
    # 生成狀態表格
    status_table = tracker.generate_status_table()
    print(f"✅ 找到 {len(status_table)} 封推薦信記錄")
    
    # 檢查逾期項目
    overdue_items = tracker.check_overdue_items()
    if overdue_items:
        print(f"⚠️  發現 {len(overdue_items)} 個需要關注的項目")
    else:
        print("✅ 所有推薦信都在預定時程內")
    
    # 生成郵件草稿
    print("\n📧 生成郵件草稿...")
    email_drafts = tracker.generate_all_email_drafts()
    print(f"✅ 請求郵件：{len(email_drafts['request_emails'])} 封")
    print(f"✅ 提醒郵件：{len(email_drafts['reminder_emails'])} 封")
    
    # 更新 dashboard
    print("\n📋 更新 Application Dashboard...")
    if tracker.update_dashboard():
        print(f"✅ Dashboard 已更新: {tracker.dashboard_file}")
    else:
        print("❌ Dashboard 更新失敗")
    
    # 顯示摘要報告
    report = tracker.generate_report()
    print("\n" + "="*60)
    print("📊 摘要報告")
    print("="*60)
    print(f"總推薦信數：{report['total_recommendations']}")
    print(f"  - 尚未請求：{report['status_breakdown']['not_requested']}")
    print(f"  - 已請求：{report['status_breakdown']['requested']}")
    print(f"  - 已提交：{report['status_breakdown']['submitted']}")
    print(f"  - 已確認：{report['status_breakdown']['confirmed']}")
    print(f"\n需要關注：{report['overdue_count']} 個")
    print(f"  - 🚨 緊急：{report['critical_count']}")
    print(f"  - ⏰ 提醒：{report['warning_count']}")
    print(f"\n郵件草稿：")
    print(f"  - 請求：{report['email_drafts_generated']['requests']} 封")
    print(f"  - 提醒：{report['email_drafts_generated']['reminders']} 封")
    print("\n郵件草稿已儲存至: templates/email_templates/")
    print("\n✅ 完成！")


if __name__ == '__main__':
    main()

