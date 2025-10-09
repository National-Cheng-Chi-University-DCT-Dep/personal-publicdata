# 專案架構設計文件

## 目錄結構規劃

```
personal-publicdata/
│
├── .github/
│   └── workflows/                          # GitHub Actions CI/CD
│       ├── pre_application_monitor.yml     # 申請開放監控工作流
│       ├── post_application_monitor.yml    # 申請進度監控工作流
│       ├── calendar_sync.yml               # Google Calendar 同步工作流
│       ├── dashboard_update.yml            # Dashboard 更新工作流
│       └── visa_monitor.yml                # 簽證資訊監控工作流
│
├── .harness/                               # Harness CI/CD
│   ├── monitoring_pipeline.yml             # 監控 Pipeline
│   ├── integration_pipeline.yml            # 整合 Pipeline
│   └── deployment_pipeline.yml             # 部署 Pipeline
│
├── monitoring/                             # 監控腳本目錄
│   ├── __init__.py
│   ├── base_monitor.py                     # 監控腳本基類
│   │
│   ├── pre_application/                    # 申請開放監控
│   │   ├── __init__.py
│   │   └── check_opening_status.py         # 主要監控腳本
│   │
│   └── post_application/                   # 申請進度監控
│       ├── __init__.py
│       ├── check_status_sweden.py          # 瑞典 Universityadmissions.se
│       ├── check_status_dreamapply.py      # 愛沙尼亞 DreamApply
│       ├── check_status_saarland.py        # 薩爾蘭大學
│       ├── check_status_uni_assist.py      # 德國 Uni-Assist
│       ├── check_status_studyinfo.py       # 芬蘭 Studyinfo.fi
│       ├── check_status_soknadsweb.py      # 挪威 Søknadsweb
│       └── check_status_studielink.py      # 荷蘭 Studielink
│
├── integrations/                           # 第三方服務整合
│   ├── __init__.py
│   ├── calendar_integration.py             # Google Calendar 整合
│   ├── email_integration.py                # 郵件整合（未來）
│   └── notification_providers.py           # 通知服務提供者
│
├── analysis/                               # 分析與報告生成
│   ├── __init__.py
│   ├── budget_analyzer.py                  # 財務分析
│   ├── recommendation_tracker.py           # 推薦信追蹤
│   ├── visa_analyzer.py                    # 簽證資訊分析
│   ├── academic_radar.py                   # 現有：學術雷達
│   ├── gamification_engine.py              # 現有：遊戲化引擎
│   ├── narrative_consistency.py            # 現有：敘事一致性
│   ├── risk_portfolio_balancer.py          # 現有：風險平衡
│   └── whatif_simulator.py                 # 現有：情境模擬
│
├── data_collection/                        # 資料收集（現有）
│   ├── scraper.py                          # 網頁爬蟲
│   ├── validator.py                        # 資料驗證
│   ├── academic_summary.py
│   ├── alert_summary.py
│   └── validation_summary.py
│
├── notifications/                          # 通知系統（現有）
│   ├── __init__.py
│   ├── alert_system.py                     # 警報系統
│   ├── path_resolver.py                    # 路徑解析
│   └── settings.yml                        # 通知設定
│
├── build_scripts/                          # 建置腳本（現有）
│   ├── master_controller.py                # 主控制器
│   ├── advanced_controller.py              # 進階控制器
│   ├── generate_docs.py                    # 文件生成
│   ├── extract_priority_schools.py
│   └── requirements.txt                    # Python 依賴
│
├── source_data/                            # 來源資料
│   ├── schools.yml                         # 學校資料（擴充）
│   ├── recommenders.yml                    # 推薦人資料（擴充）
│   ├── visa_requirements.yml               # 簽證需求資料（新增）
│   └── application_status.yml              # 申請狀態資料（新增）
│
├── data_schemas/                           # 資料結構定義（新增）
│   ├── schools_schema.json                 # schools.yml 的 JSON Schema
│   ├── recommenders_schema.json            # recommenders.yml 的 JSON Schema
│   ├── visa_schema.json                    # visa_requirements.yml 的 JSON Schema
│   └── status_schema.json                  # application_status.yml 的 JSON Schema
│
├── templates/                              # 文件範本（現有）
│   ├── cv_template.md
│   ├── sop_master_template.md
│   ├── sop_bridge_generic.md
│   ├── sop_bridge_aalto.md
│   └── sop_bridge_taltech.md
│
├── final_applications/                     # 產出的申請文件（現有）
│   ├── application_dashboard.md            # 申請儀表板（擴充）
│   ├── application_dashboard.html          # HTML 版本儀表板（新增）
│   ├── validation_report.md
│   └── [School Name]/                      # 各校資料夾
│       ├── CV_PeiChenLee.md
│       └── SOP_PeiChenLee_[School].md
│
├── reports/                                # 報告輸出（新增）
│   ├── monitoring_reports/                 # 監控報告
│   ├── financial_reports/                  # 財務報告
│   └── status_history/                     # 狀態歷史記錄
│
├── tests/                                  # 測試（新增）
│   ├── unit/                               # 單元測試
│   │   ├── test_monitors.py
│   │   ├── test_integrations.py
│   │   └── test_analyzers.py
│   ├── integration/                        # 整合測試
│   │   ├── test_workflows.py
│   │   └── test_pipelines.py
│   └── fixtures/                           # 測試資料
│       ├── mock_html/                      # 模擬的 HTML 頁面
│       └── mock_data/                      # 模擬的資料檔案
│
├── scripts/                                # 實用腳本（新增）
│   ├── setup_environment.sh                # 環境設定腳本
│   ├── run_all_monitors.py                 # 執行所有監控
│   ├── sync_secrets.py                     # 同步 Secrets
│   └── validate_data.py                    # 驗證資料完整性
│
├── docs/                                   # 專案文檔（新增）
│   ├── API_INTEGRATION.md                  # API 整合指南
│   ├── CRAWLER_GUIDE.md                    # 爬蟲開發指南
│   ├── TROUBLESHOOTING.md                  # 故障排除
│   └── ARCHITECTURE_DIAGRAM.png            # 架構圖
│
├── .env.example                            # 環境變數範例（新增）
├── .gitignore                              # Git 忽略清單
├── README.md                               # 專案說明
├── PROJECT_DEVELOPMENT_PLAN.md             # 開發計畫（新增）
├── PROJECT_ARCHITECTURE.md                 # 架構文件（本檔案）
└── requirements.txt                        # 全域 Python 依賴（新增）
```

---

## 核心模組架構

### 1. 監控系統 (Monitoring System)

#### Base Monitor Class
```python
# monitoring/base_monitor.py
class BaseMonitor:
    """所有監控腳本的基類"""
    
    def __init__(self, config):
        self.config = config
        self.notifier = Notifier()
        self.logger = setup_logger()
    
    def fetch_page(self, url):
        """抓取頁面內容"""
        pass
    
    def parse_content(self, content):
        """解析頁面內容"""
        pass
    
    def detect_changes(self, old_status, new_status):
        """偵測狀態變更"""
        pass
    
    def send_notification(self, message):
        """發送通知"""
        pass
    
    def save_status(self, status):
        """儲存狀態"""
        pass
    
    def run(self):
        """執行監控流程"""
        pass
```

#### Pre-Application Monitor
```python
# monitoring/pre_application/check_opening_status.py
class ApplicationOpeningMonitor(BaseMonitor):
    """監控申請開放狀態"""
    
    def __init__(self):
        super().__init__(config)
        self.schools = self.load_schools()
    
    def load_schools(self):
        """從 schools.yml 載入學校資料"""
        pass
    
    def check_school(self, school):
        """檢查單一學校的申請狀態"""
        # 1. 訪問 application_url
        # 2. 搜尋關鍵字："Apply Now", "Application Open"
        # 3. 分析 HTML 結構變化
        # 4. 比對歷史狀態
        pass
    
    def detect_keywords(self, html_content):
        """偵測關鍵字"""
        keywords = [
            "Apply Now",
            "Application Open",
            "Application Period",
            "Submit Application"
        ]
        pass
    
    def run(self):
        """執行所有學校的監控"""
        for school in self.schools:
            old_status = self.get_saved_status(school['name'])
            new_status = self.check_school(school)
            
            if self.detect_changes(old_status, new_status):
                self.send_notification({
                    'school': school['name'],
                    'old_status': old_status,
                    'new_status': new_status,
                    'url': school['application_url']
                })
                self.save_status(school['name'], new_status)
```

#### Post-Application Monitor (Sweden Example)
```python
# monitoring/post_application/check_status_sweden.py
class SwedenApplicationMonitor(BaseMonitor):
    """監控瑞典 Universityadmissions.se 申請進度"""
    
    def __init__(self):
        super().__init__(config)
        self.username = os.getenv('SWEDEN_USERNAME')
        self.password = os.getenv('SWEDEN_PASSWORD')
        self.playwright = None
        self.browser = None
        self.page = None
    
    async def login(self):
        """登入系統"""
        # 使用 Playwright 自動化登入
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)
        self.page = await self.browser.new_page()
        
        await self.page.goto('https://www.universityadmissions.se/')
        # 登入邏輯
        pass
    
    async def navigate_to_applications(self):
        """導航至「我的申請」頁面"""
        pass
    
    async def extract_application_status(self):
        """抓取申請狀態"""
        # 分析 HTML 結構，定位狀態元素
        applications = await self.page.query_selector_all('.application-item')
        
        results = []
        for app in applications:
            school_name = await app.query_selector('.school-name').inner_text()
            program = await app.query_selector('.program-name').inner_text()
            status = await app.query_selector('.status').inner_text()
            
            results.append({
                'school': school_name,
                'program': program,
                'status': status,
                'checked_at': datetime.now().isoformat()
            })
        
        return results
    
    async def run(self):
        """執行監控"""
        try:
            await self.login()
            await self.navigate_to_applications()
            new_status = await self.extract_application_status()
            
            old_status = self.load_saved_status()
            
            if self.detect_changes(old_status, new_status):
                self.send_notification(new_status)
            
            self.save_status(new_status)
        finally:
            await self.browser.close()
            await self.playwright.stop()
```

---

### 2. Google Calendar 整合 (Calendar Integration)

```python
# integrations/calendar_integration.py
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import yaml
import os
import pickle

class CalendarIntegration:
    """Google Calendar 整合"""
    
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    
    def __init__(self):
        self.creds = None
        self.service = None
        self.calendar_id = 'primary'
    
    def authenticate(self):
        """驗證 Google Calendar API"""
        # 從 GitHub Secrets 或本地檔案讀取憑證
        token_path = os.getenv('GOOGLE_TOKEN_PATH', 'token.pickle')
        creds_path = os.getenv('GOOGLE_CREDENTIALS_PATH', 'credentials.json')
        
        # 載入已存在的 token
        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                self.creds = pickle.load(token)
        
        # 如果沒有有效的憑證，進行授權
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(creds_path, self.SCOPES)
                self.creds = flow.run_local_server(port=0)
            
            # 儲存憑證以供下次使用
            with open(token_path, 'wb') as token:
                pickle.dump(self.creds, token)
        
        self.service = build('calendar', 'v3', credentials=self.creds)
    
    def load_schools(self):
        """載入學校資料"""
        with open('source_data/schools.yml', 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def create_deadline_event(self, school_name, deadline, program_name=None):
        """為截止日期建立日曆事件"""
        title = f"[Deadline] Submit Application for {school_name}"
        if program_name:
            title += f" - {program_name}"
        
        event = {
            'summary': title,
            'description': f'Application deadline for {school_name}',
            'start': {
                'date': deadline,  # 格式：YYYY-MM-DD
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
                ],
            },
            'colorId': '11',  # 紅色，表示重要
        }
        
        result = self.service.events().insert(calendarId=self.calendar_id, body=event).execute()
        return result
    
    def sync_all_deadlines(self):
        """同步所有截止日期"""
        self.authenticate()
        schools = self.load_schools()
        
        synced_events = []
        for school in schools.get('schools', []):
            if 'deadline' in school and school['deadline']:
                try:
                    event = self.create_deadline_event(
                        school['name'],
                        school['deadline'],
                        school.get('program_name')
                    )
                    synced_events.append(event)
                    print(f"✅ Synced deadline for {school['name']}")
                except Exception as e:
                    print(f"❌ Failed to sync {school['name']}: {e}")
        
        return synced_events
    
    def update_event(self, event_id, new_deadline):
        """更新現有事件"""
        pass
    
    def delete_event(self, event_id):
        """刪除事件"""
        pass
```

---

### 3. 推薦信追蹤系統 (Recommendation Tracker)

```python
# analysis/recommendation_tracker.py
import yaml
from datetime import datetime, timedelta
from jinja2 import Template

class RecommendationTracker:
    """推薦信追蹤系統"""
    
    def __init__(self):
        self.recommenders = self.load_recommenders()
        self.schools = self.load_schools()
    
    def load_recommenders(self):
        """載入推薦人資料"""
        with open('source_data/recommenders.yml', 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def load_schools(self):
        """載入學校資料"""
        with open('source_data/schools.yml', 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def generate_status_table(self):
        """生成推薦信狀態總覽表格"""
        table_rows = []
        
        for recommender in self.recommenders.get('recommenders', []):
            for school_status in recommender.get('school_specific_status', []):
                row = {
                    'recommender_name': recommender['name'],
                    'recommender_title': recommender['title'],
                    'school': school_status['school'],
                    'status': school_status['status'],
                    'requested_date': school_status.get('requested_date', 'N/A'),
                    'submitted_date': school_status.get('submitted_date', 'N/A'),
                    'deadline': self.get_school_deadline(school_status['school'])
                }
                table_rows.append(row)
        
        return table_rows
    
    def get_school_deadline(self, school_name):
        """取得學校截止日期"""
        for school in self.schools.get('schools', []):
            if school['name'] == school_name:
                return school.get('deadline', 'N/A')
        return 'N/A'
    
    def check_overdue(self):
        """檢查逾期的推薦信請求"""
        overdue_items = []
        today = datetime.now().date()
        
        for recommender in self.recommenders.get('recommenders', []):
            for school_status in recommender.get('school_specific_status', []):
                if school_status['status'] in ['requested', 'not_requested']:
                    deadline = self.get_school_deadline(school_status['school'])
                    if deadline != 'N/A':
                        deadline_date = datetime.strptime(deadline, '%Y-%m-%d').date()
                        days_until_deadline = (deadline_date - today).days
                        
                        # 如果離截止日期不到 14 天且推薦信尚未提交
                        if days_until_deadline < 14:
                            overdue_items.append({
                                'recommender': recommender['name'],
                                'school': school_status['school'],
                                'status': school_status['status'],
                                'deadline': deadline,
                                'days_remaining': days_until_deadline
                            })
        
        return overdue_items
    
    def generate_reminder_email(self, recommender_name, school_name, deadline):
        """生成提醒郵件草稿"""
        template = Template("""
親愛的 {{ recommender_name }} 教授，

希望您一切安好。

我想禮貌地提醒您，我申請 {{ school_name }} 的推薦信截止日期為 {{ deadline }}。

如果您需要任何額外的資訊或文件，請隨時告訴我。非常感謝您的支持與協助。

祝好，
李培辰
        """)
        
        return template.render(
            recommender_name=recommender_name,
            school_name=school_name,
            deadline=deadline
        )
    
    def update_dashboard(self):
        """更新 application_dashboard.md"""
        status_table = self.generate_status_table()
        overdue_items = self.check_overdue()
        
        # 生成 Markdown 內容
        markdown_content = self.render_dashboard(status_table, overdue_items)
        
        # 更新 dashboard 檔案
        with open('final_applications/application_dashboard.md', 'a', encoding='utf-8') as f:
            f.write('\n\n## 推薦信狀態總覽\n\n')
            f.write(markdown_content)
    
    def render_dashboard(self, status_table, overdue_items):
        """渲染 dashboard 內容"""
        # 實作 Markdown 表格生成
        pass
```

---

### 4. 財務規劃儀表板 (Budget Analyzer)

```python
# analysis/budget_analyzer.py
import yaml
import requests
from datetime import datetime

class BudgetAnalyzer:
    """財務分析器"""
    
    def __init__(self):
        self.schools = self.load_schools()
        self.exchange_rates = self.get_exchange_rates()
    
    def load_schools(self):
        """載入學校資料"""
        with open('source_data/schools.yml', 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def get_exchange_rates(self):
        """取得即時匯率"""
        # 可以使用 API 如 exchangerate-api.com
        # 或使用固定匯率
        return {
            'EUR': 33.5,  # 歐元
            'SEK': 2.9,   # 瑞典克朗
            'USD': 31.5,  # 美元
        }
    
    def convert_to_twd(self, amount, currency):
        """轉換為台幣"""
        if currency == 'TWD':
            return amount
        return amount * self.exchange_rates.get(currency, 1)
    
    def calculate_total_application_cost(self):
        """計算總申請成本"""
        total_cost = 0
        cost_breakdown = []
        
        for school in self.schools.get('schools', []):
            if 'application_fee' in school:
                fee = school['application_fee']
                currency = fee.get('currency', 'EUR')
                amount = fee.get('amount', 0)
                
                twd_amount = self.convert_to_twd(amount, currency)
                total_cost += twd_amount
                
                cost_breakdown.append({
                    'school': school['name'],
                    'amount': amount,
                    'currency': currency,
                    'twd_amount': twd_amount
                })
        
        return {
            'total': total_cost,
            'breakdown': cost_breakdown
        }
    
    def calculate_annual_cost(self, school):
        """計算單一學校的年度總花費"""
        tuition = school.get('tuition_fee', {'amount': 0, 'currency': 'EUR'})
        living_cost = school.get('estimated_living_cost', {'amount': 0, 'currency': 'EUR'})
        
        tuition_twd = self.convert_to_twd(tuition['amount'], tuition['currency'])
        living_twd = self.convert_to_twd(living_cost['amount'], living_cost['currency'])
        
        return tuition_twd + living_twd
    
    def generate_cost_comparison(self):
        """生成成本比較表"""
        comparisons = []
        
        for school in self.schools.get('schools', []):
            annual_cost = self.calculate_annual_cost(school)
            
            comparisons.append({
                'school': school['name'],
                'country': school['country'],
                'annual_cost_twd': annual_cost,
                'tuition_free': school.get('tuition_free', False),
                'scholarship_available': school.get('scholarship_available', False)
            })
        
        # 按成本排序
        comparisons.sort(key=lambda x: x['annual_cost_twd'])
        
        return comparisons
    
    def generate_financial_dashboard(self):
        """生成財務儀表板"""
        application_costs = self.calculate_total_application_cost()
        cost_comparison = self.generate_cost_comparison()
        
        # 生成 Markdown 內容
        markdown = self.render_financial_report(application_costs, cost_comparison)
        
        # 寫入檔案
        with open('reports/financial_reports/budget_analysis.md', 'w', encoding='utf-8') as f:
            f.write(markdown)
        
        return markdown
    
    def render_financial_report(self, application_costs, cost_comparison):
        """渲染財務報告"""
        # 實作 Markdown 生成
        pass
```

---

## 資料結構設計

### schools.yml 擴充結構

```yaml
schools:
  - name: "延雪平大學"
    name_english: "Jönköping University"
    country: "瑞典"
    program_name: "M.Sc. in Cybersecurity"
    application_url: "https://ju.se/apply"
    application_platform: "universityadmissions.se"
    deadline: "2026-01-15"
    
    # 新增欄位 - 財務資訊
    application_fee:
      amount: 900
      currency: "SEK"
    
    tuition_fee:
      amount: 0
      currency: "SEK"
      note: "Free for EU/EEA students"
    
    estimated_living_cost:
      amount: 8000
      currency: "SEK"
      period: "monthly"
    
    tuition_free: true
    scholarship_available: true
    scholarship_details: "Swedish Institute Scholarships available"
    
    # 現有欄位
    priority: "high"
    status: "pending"
    requirements:
      - "Bachelor's degree in relevant field"
      - "English proficiency"
      - "CV"
      - "SOP"
      - "Recommendation letters (2)"
```

### recommenders.yml 擴充結構

```yaml
recommenders:
  - name: "教授名稱"
    title: "教授"
    institution: "大學名稱"
    email: "professor@university.edu"
    relationship: "指導教授"
    
    # 新增欄位 - 狀態追蹤
    school_specific_status:
      - school: "延雪平大學"
        status: "submitted"  # not_requested, requested, submitted, confirmed
        requested_date: "2025-11-01"
        submitted_date: "2025-11-15"
        confirmation_received: true
      
      - school: "舍夫德大學"
        status: "requested"
        requested_date: "2025-11-01"
        submitted_date: null
        confirmation_received: false
```

### visa_requirements.yml 新增結構

```yaml
countries:
  - name: "瑞典"
    visa_type: "Student Residence Permit"
    embassy_url: "https://www.swedenabroad.se/en/embassies/taiwan-taipei/"
    information_page_url: "https://www.migrationsverket.se/English/Private-individuals/Studying-in-Sweden.html"
    appointment_system_url: "https://www.swedenabroad.se/en/embassies/taiwan-taipei/contact-us/book-appointment/"
    
    requirements:
      - "Admission letter from Swedish university"
      - "Proof of financial means (SEK 8,568/month)"
      - "Valid passport"
      - "Health insurance"
    
    processing_time: "60-90 days"
    cost:
      amount: 1500
      currency: "SEK"
    
    monitor_enabled: true
    last_checked: "2025-10-09"
    last_updated: "2025-09-15"
```

### application_status.yml 新增結構

```yaml
applications:
  - platform: "universityadmissions.se"
    schools:
      - name: "延雪平大學"
        program: "M.Sc. in Cybersecurity"
        submitted_date: "2026-01-10"
        status: "Under Review"
        status_updated_at: "2026-01-15"
        status_history:
          - status: "Submitted"
            timestamp: "2026-01-10T10:30:00"
          - status: "Received"
            timestamp: "2026-01-12T14:20:00"
          - status: "Under Review"
            timestamp: "2026-01-15T09:00:00"
```

---

## CI/CD 工作流設計

### GitHub Actions - Pre-Application Monitor

```yaml
# .github/workflows/pre_application_monitor.yml
name: Pre-Application Monitor

on:
  schedule:
    - cron: '0 9,15 * * *'  # 每天 9:00 和 15:00 (UTC)
  workflow_dispatch:  # 允許手動觸發

jobs:
  monitor:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          playwright install chromium
      
      - name: Run pre-application monitor
        env:
          NOTIFICATION_WEBHOOK: ${{ secrets.NOTIFICATION_WEBHOOK }}
        run: |
          python monitoring/pre_application/check_opening_status.py
      
      - name: Commit status changes
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add source_data/application_status.yml
          git diff --quiet && git diff --staged --quiet || git commit -m "Update application opening status"
          git push
```

### Harness - Monitoring Pipeline

```yaml
# .harness/monitoring_pipeline.yml
pipeline:
  name: Application Monitoring Pipeline
  identifier: application_monitoring
  projectIdentifier: master_application
  orgIdentifier: default
  
  stages:
    - stage:
        name: Pre-Application Monitoring
        identifier: pre_application
        type: Custom
        spec:
          execution:
            steps:
              - step:
                  type: ShellScript
                  name: Check Opening Status
                  identifier: check_opening
                  spec:
                    shell: Python
                    source:
                      type: Inline
                      spec:
                        script: |
                          python monitoring/pre_application/check_opening_status.py
    
    - stage:
        name: Post-Application Monitoring
        identifier: post_application
        type: Custom
        spec:
          execution:
            steps:
              - step:
                  type: ShellScript
                  name: Check Sweden Status
                  identifier: check_sweden
                  spec:
                    shell: Python
                    source:
                      type: Inline
                      spec:
                        script: |
                          python monitoring/post_application/check_status_sweden.py
                  envVariables:
                    SWEDEN_USERNAME: <+secrets.getValue("sweden_username")>
                    SWEDEN_PASSWORD: <+secrets.getValue("sweden_password")>
  
  triggers:
    - trigger:
        name: Daily Schedule
        identifier: daily_schedule
        type: Cron
        spec:
          type: Cron
          spec:
            expression: "0 9,15 * * *"
```

---

## 安全性設計

### GitHub Secrets 清單

```
# 申請平台帳號
SWEDEN_USERNAME
SWEDEN_PASSWORD
DREAMAPPLY_USERNAME
DREAMAPPLY_PASSWORD
SAARLAND_USERNAME
SAARLAND_PASSWORD
UNI_ASSIST_USERNAME
UNI_ASSIST_PASSWORD

# Google Calendar API
GOOGLE_CREDENTIALS_JSON
GOOGLE_TOKEN_JSON

# 通知服務
NOTIFICATION_WEBHOOK
EMAIL_SMTP_PASSWORD

# 其他 API Keys
EXCHANGE_RATE_API_KEY
```

### 環境變數處理

```python
# scripts/load_secrets.py
import os
import json
import base64

def load_github_secrets():
    """從環境變數載入 GitHub Secrets"""
    # 在 CI/CD 中，Secrets 會被注入為環境變數
    
    # 處理 JSON 格式的 Secrets
    if 'GOOGLE_CREDENTIALS_JSON' in os.environ:
        credentials = json.loads(
            base64.b64decode(os.environ['GOOGLE_CREDENTIALS_JSON'])
        )
        with open('credentials.json', 'w') as f:
            json.dump(credentials, f)
    
    return True

def validate_secrets():
    """驗證所有必要的 Secrets 都已設定"""
    required_secrets = [
        'SWEDEN_USERNAME',
        'SWEDEN_PASSWORD',
        'GOOGLE_CREDENTIALS_JSON',
        'NOTIFICATION_WEBHOOK'
    ]
    
    missing = [s for s in required_secrets if s not in os.environ]
    
    if missing:
        raise ValueError(f"Missing required secrets: {', '.join(missing)}")
    
    return True
```

---

## 測試策略

### 單元測試範例

```python
# tests/unit/test_monitors.py
import pytest
from monitoring.pre_application.check_opening_status import ApplicationOpeningMonitor

class TestApplicationOpeningMonitor:
    
    def test_detect_keywords(self):
        """測試關鍵字偵測"""
        monitor = ApplicationOpeningMonitor()
        
        html_with_apply_now = "<button>Apply Now</button>"
        assert monitor.detect_keywords(html_with_apply_now) == True
        
        html_without_keywords = "<p>Coming soon</p>"
        assert monitor.detect_keywords(html_without_keywords) == False
    
    def test_detect_changes(self):
        """測試狀態變更偵測"""
        monitor = ApplicationOpeningMonitor()
        
        old_status = {"status": "closed"}
        new_status = {"status": "open"}
        
        assert monitor.detect_changes(old_status, new_status) == True
```

---

## 效能最佳化

### 爬蟲頻率控制

```python
# monitoring/rate_limiter.py
import time
from collections import defaultdict

class RateLimiter:
    """速率限制器"""
    
    def __init__(self):
        self.requests = defaultdict(list)
    
    def can_request(self, domain, max_requests=10, time_window=60):
        """檢查是否可以發送請求"""
        now = time.time()
        
        # 清除過期的請求記錄
        self.requests[domain] = [
            req_time for req_time in self.requests[domain]
            if now - req_time < time_window
        ]
        
        # 檢查是否超過限制
        if len(self.requests[domain]) < max_requests:
            self.requests[domain].append(now)
            return True
        
        return False
    
    def wait_if_needed(self, domain, max_requests=10, time_window=60):
        """如果需要，等待直到可以發送請求"""
        while not self.can_request(domain, max_requests, time_window):
            time.sleep(1)
```

---

**文件版本**: v1.0  
**最後更新**: 2025-10-09  
**維護者**: Dennis Lee

