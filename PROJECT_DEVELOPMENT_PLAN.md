# 碩士申請管理系統升級 - 專案開發計畫

## 專案概述

**專案名稱**: 碩士申請管理系統自動化平台 (Master Application Management Platform)

**專案目標**: 將現有的碩士申請管理系統，升級為一個具備主動情報蒐集（爬蟲）與進階管理功能的自動化平台。

**當前衝刺目標**: 完成對瑞典 2026 年秋季入學碩士的申請流程管理，並開發一系列新的自動化監控模組。

**專案時程**: 2025年10月16日 - 2026年1月15日（瑞典申請截止日）

**CI/CD 策略**: GitHub Actions + Harness 雙軌部署

---

## Phase 1: 專案規劃與架構設計

**目標**: 建立完整的開發計畫文件與專案架構

**時程估計**: 2-3 天

### Stage 1.1: 專案架構設計

#### TODOs:
- [ ] 建立專案目錄結構規劃文件
  - 定義 `monitoring/` 目錄結構（各平台獨立腳本）
  - 定義 `integrations/` 目錄（第三方服務整合）
  - 定義 `data_schemas/` 目錄（YAML schemas 定義）
  - 定義 `reports/` 目錄（產出報告存放）

- [ ] 設計資料結構 Schema
  - 擴充 `schools.yml` schema（新增申請費用、生活成本欄位）
  - 擴充 `recommenders.yml` schema（新增狀態追蹤欄位）
  - 設計 `visa_requirements.yml` schema
  - 設計 `application_status.yml` schema（追蹤各平台申請狀態）

- [ ] 建立安全性管理規範
  - 列出所有需要的 GitHub Secrets（各平台帳密、API Keys）
  - 定義敏感資訊處理流程
  - 建立 `.env.example` 範本

### Stage 1.2: 技術選型與環境準備

#### TODOs:
- [ ] 更新 `requirements.txt`
  - Playwright（瀏覽器自動化）
  - google-api-python-client, google-auth-httplib2, google-auth-oauthlib（Google Calendar）
  - requests, beautifulsoup4（HTTP 請求與 HTML 解析）
  - pyyaml（YAML 處理）
  - schedule（任務排程）

- [ ] 建立測試環境
  - 設定本地開發環境
  - 安裝 Playwright browsers
  - 設定測試用 GitHub Secrets

- [ ] 建立專案文檔結構
  - API 整合文檔
  - 爬蟲腳本開發指南
  - 錯誤處理與通知機制文檔

---

## Phase 2: 申請平台監控系統開發

**目標**: 實作 Pre-Application 和 Post-Application 監控功能

**時程估計**: 7-10 天

### Stage 2.1: Pre-Application Monitor（申請開放監控）

#### TODOs:
- [ ] 建立 `monitoring/check_opening_status.py` 核心腳本
  - 讀取 `schools.yml` 中的 `application_url`
  - 使用 Playwright 訪問各申請頁面
  - 實作關鍵字偵測邏輯（"Apply Now", "Application Open" 等）
  - 實作 HTML 模式變化偵測
  - 儲存歷史狀態（用於比對變化）

- [ ] 整合通知機制
  - 狀態變更時觸發 `notifications/alert_system.py`
  - 產生結構化的通知內容（包含學校名稱、URL、變更詳情）

- [ ] 建立單元測試
  - 測試關鍵字偵測邏輯
  - 測試狀態變更偵測
  - 模擬不同網頁結構的測試案例

### Stage 2.2: Post-Application Monitor - Universityadmissions.se

#### TODOs:
- [ ] 建立 `monitoring/check_status_sweden.py`
  - 實作 Playwright 登入流程（從 GitHub Secrets 讀取帳密）
  - 分析登入後頁面的 HTML 結構
  - 定位申請狀態元素（class/id）
  - 抓取所有申請項目的狀態
  - 儲存狀態至 `application_status.yml`

- [ ] 實作狀態變更偵測
  - 比對新舊狀態
  - 在狀態變更時觸發通知
  - 記錄狀態變更歷史

- [ ] 錯誤處理與重試機制
  - 處理登入失敗情況
  - 處理網頁結構變更情況
  - 實作自動重試邏輯

### Stage 2.3: Post-Application Monitor - DreamApply

#### TODOs:
- [ ] 建立 `monitoring/check_status_dreamapply.py`
  - 探索是否有 API 端點（使用瀏覽器 DevTools 分析 XHR/Fetch）
  - 若有 API，實作 API-based 狀態抓取
  - 若無 API，實作 Playwright HTML 爬取
  - 整合通知與狀態儲存機制

- [ ] 建立測試案例
  - 測試 API 請求（如適用）
  - 測試 HTML 解析邏輯

### Stage 2.4: Post-Application Monitor - Saarland University

#### TODOs:
- [ ] 建立 `monitoring/check_status_saarland.py`
  - 客製化登入流程（針對該校系統）
  - 實作狀態抓取邏輯
  - 整合通知與狀態儲存機制

- [ ] 測試與驗證
  - 端到端測試完整流程
  - 驗證狀態準確性

### Stage 2.5: 多平台支援（額外平台）

#### TODOs:
- [ ] 建立 `monitoring/check_status_uni_assist.py`（德國 Uni-Assist）
- [ ] 建立 `monitoring/check_status_studyinfo.py`（芬蘭 Studyinfo.fi）
- [ ] 建立 `monitoring/check_status_soknadsweb.py`（挪威 Søknadsweb）
- [ ] 建立 `monitoring/check_status_studielink.py`（荷蘭 Studielink）

---

## Phase 3: Google Calendar 整合

**目標**: 實作自動化行程管理功能

**時程估計**: 3-4 天

### Stage 3.1: Google Calendar API 設定

#### TODOs:
- [ ] Google Cloud Console 設定
  - 建立新專案
  - 啟用 Google Calendar API
  - 設定 OAuth 2.0 同意畫面
  - 下載 `credentials.json`

- [ ] 首次授權流程
  - 本地執行授權流程
  - 生成 `token.json`
  - 將 credentials 和 token 存入 GitHub Secrets

### Stage 3.2: Calendar Integration 腳本開發

#### TODOs:
- [ ] 建立 `integrations/calendar_integration.py`
  - 實作 Google Calendar API 驗證邏輯
  - 從 GitHub Secrets 讀取憑證
  - 讀取 `schools.yml` 中的 deadline 欄位
  - 建立日曆事件邏輯

- [ ] 實作事件管理功能
  - 為每個 deadline 建立事件：`[Deadline] Submit Application for [School Name]`
  - 設定提前一週的提醒
  - 設定提前三天的提醒
  - 處理事件更新（當 deadline 變更時）

- [ ] 錯誤處理
  - 處理 API 限制（rate limiting）
  - 處理授權過期情況
  - 實作重試機制

### Stage 3.3: 測試與驗證

#### TODOs:
- [ ] 單元測試
  - 測試事件建立邏輯
  - 測試提醒設定
  - 測試事件更新邏輯

- [ ] 整合測試
  - 在測試 Calendar 上驗證完整流程
  - 驗證所有 deadline 都正確同步

---

## Phase 4: 推薦信追蹤系統

**目標**: 開發推薦信狀態管理功能

**時程估計**: 2-3 天

### Stage 4.1: 資料結構擴充

#### TODOs:
- [ ] 擴充 `source_data/recommenders.yml`
  - 新增 `status` 欄位（可能值：not_requested, requested, submitted, confirmed）
  - 新增 `requested_date` 欄位
  - 新增 `submitted_date` 欄位
  - 新增 `school_specific_status` 欄位（追蹤每所學校的推薦信狀態）

### Stage 4.2: 追蹤腳本開發

#### TODOs:
- [ ] 建立 `monitoring/recommendation_tracker.py`
  - 讀取 `recommenders.yml`
  - 讀取 `schools.yml`（取得需要推薦信的學校清單）
  - 生成「推薦信狀態總覽」表格
  - 更新 `application_dashboard.md`

- [ ] 實作提醒功能
  - 檢測 overdue 的推薦信請求
  - 生成提醒通知
  - 自動生成禮貌性的提醒郵件草稿

### Stage 4.3: 郵件草稿自動生成

#### TODOs:
- [ ] 建立郵件範本系統
  - 設計推薦信請求郵件範本
  - 設計禮貌性提醒郵件範本
  - 實作變數替換邏輯（推薦人姓名、學校名稱、deadline 等）

- [ ] 整合至 dashboard
  - 在 `application_dashboard.md` 中顯示郵件草稿連結
  - 提供一鍵複製功能（透過 HTML 版本的 dashboard）

---

## Phase 5: 簽證與移民資訊雷達

**目標**: 建立簽證資訊監控系統

**時程估計**: 3-4 天

### Stage 5.1: 資料結構建立

#### TODOs:
- [ ] 建立 `source_data/visa_requirements.yml`
  - 定義資料結構：國家、簽證類型、官方網址、在台辦事處聯絡資訊
  - 填入目標國家資訊（瑞典、芬蘭、愛沙尼亞、德國等）
  - 包含簽證預約系統 URL（如適用）

### Stage 5.2: 簽證資訊監控腳本

#### TODOs:
- [ ] 建立 `monitoring/visa_monitor.py`
  - 讀取 `visa_requirements.yml`
  - 定期爬取各國在台辦事處官網
  - 實作頁面 hash 值計算
  - 儲存歷史 hash 值
  - 偵測頁面變更（透過 hash 比對）

- [ ] 實作通知機制
  - 當偵測到頁面變更時，觸發警報
  - 通知內容包含：國家、變更的 URL、變更時間

### Stage 5.3: 簽證預約名額監控（進階功能）

#### TODOs:
- [ ] 建立 `monitoring/visa_appointment_monitor.py`
  - 使用 Playwright 定期檢查簽證預約系統
  - 偵測可用預約時段
  - 實作即時警報機制（當有名額時）

- [ ] 測試與驗證
  - 在不同國家的預約系統上測試
  - 確保不會對官方系統造成過度負載

---

## Phase 6: 財務規劃儀表板

**目標**: 開發財務分析與預算管理功能

**時程估計**: 2-3 天

### Stage 6.1: 資料結構擴充

#### TODOs:
- [ ] 擴充 `source_data/schools.yml`
  - 新增 `application_fee` 欄位（申請費用，含幣別）
  - 新增 `estimated_living_cost` 欄位（預估年度生活費）
  - 新增 `tuition_fee` 欄位（學費，如適用）
  - 新增 `scholarship_available` 欄位（是否有獎學金）

### Stage 6.2: 財務分析腳本開發

#### TODOs:
- [ ] 建立 `analysis/budget_analyzer.py`
  - 讀取 `schools.yml` 中的財務資訊
  - 實作匯率轉換邏輯（使用即時或固定匯率）
  - 計算總申請成本
  - 計算各校年度總花費（學費 + 生活費）
  - 生成「財務規劃總覽」表格

- [ ] 實作比較分析功能
  - 國家間成本比較
  - 學校間成本比較
  - 生成視覺化圖表（使用 matplotlib 或整合至 HTML dashboard）

### Stage 6.3: 整合至 Dashboard

#### TODOs:
- [ ] 更新 `application_dashboard.md`
  - 新增「財務規劃總覽」區塊
  - 顯示總申請成本
  - 顯示各校年度總花費比較表
  - 顯示成本排名

- [ ] HTML Dashboard 增強
  - 在 `application_dashboard.html` 中加入互動式圖表
  - 實作成本計算器功能

---

## Phase 7: CI/CD Pipeline 建置

**目標**: 設定 GitHub Actions 和 Harness 自動化流程

**時程估計**: 3-4 天

### Stage 7.1: GitHub Actions Workflows

#### TODOs:
- [ ] 建立 `.github/workflows/pre_application_monitor.yml`
  - 定期執行 `check_opening_status.py`（每日 2-3 次）
  - 設定 cron schedule
  - 從 Secrets 讀取必要憑證

- [ ] 建立 `.github/workflows/post_application_monitor.yml`
  - 定期執行所有 post-application 監控腳本（每日 1-2 次）
  - 並行執行多個平台的監控
  - 彙整結果並發送通知

- [ ] 建立 `.github/workflows/calendar_sync.yml`
  - 當 `schools.yml` 更新時觸發
  - 執行 `calendar_integration.py`
  - 同步 deadline 至 Google Calendar

- [ ] 建立 `.github/workflows/dashboard_update.yml`
  - 當任何相關 YAML 檔案更新時觸發
  - 執行 `recommendation_tracker.py`
  - 執行 `budget_analyzer.py`
  - 重新生成 `application_dashboard.md` 和 `application_dashboard.html`

- [ ] 建立 `.github/workflows/visa_monitor.yml`
  - 定期執行簽證監控腳本（每週 1-2 次）

### Stage 7.2: Harness Pipeline 設定

#### TODOs:
- [ ] 建立 `.harness/monitoring_pipeline.yml`
  - 定義 Pre-Application 監控階段
  - 定義 Post-Application 監控階段
  - 定義通知階段
  - 設定執行頻率與觸發條件

- [ ] 建立 `.harness/integration_pipeline.yml`
  - 定義 Calendar 同步階段
  - 定義 Dashboard 更新階段
  - 設定與 GitHub 的整合

- [ ] 建立 `.harness/deployment_pipeline.yml`
  - 定義部署流程（如需將 dashboard 部署至靜態網站）
  - 設定環境變數管理
  - 整合 Secrets 管理

### Stage 7.3: 測試與監控

#### TODOs:
- [ ] Pipeline 測試
  - 測試所有 GitHub Actions workflows
  - 測試所有 Harness pipelines
  - 驗證 Secrets 正確傳遞

- [ ] 監控與告警設定
  - 設定 workflow 失敗告警
  - 設定執行時間過長告警
  - 建立 Pipeline 執行 dashboard

---

## Phase 8: 瑞典申請衝刺

**目標**: 完成所有瑞典學校的申請文件與提交

**時程估計**: 2025年10月16日 - 2026年1月15日（持續進行）

### Stage 8.1: 目標學校資料完善

#### TODOs:
- [ ] 更新 `schools.yml` - 第一梯隊
  - 延雪平大學 - M.Sc. in Cybersecurity
  - 舍夫德大學 - M.Sc. in Privacy, Information and Cybersecurity
  - 西部大學 - M.Sc. in Cybersecurity (60 Credits)
  - 完善所有必要欄位（deadline, requirements, application_url 等）

- [ ] 更新 `schools.yml` - 第二梯隊
  - 哥德堡大學 - M.Sc. in Computer Science
  - 呂勒奧理工大學 - M.Sc. in Applied AI / Cybersecurity
  - 完善所有必要欄位

- [ ] 更新 `schools.yml` - 第三梯隊
  - 隆德大學 - M.Sc. in Physics, Quantum Science and Technology
  - 標註特殊需求（高學術性、量子領域）

### Stage 8.2: 核心文件準備

#### TODOs:
- [ ] 準備 Master CV
  - 基於現有 `履歷 (CV).md` 更新
  - 學術導向調整
  - 強調資安與技術專長
  - 轉換為英文版本

- [ ] 準備 Master SOP（通用範本）
  - 基於現有 SOP 範本
  - 適用於第一、二梯隊學校
  - 強調資安與網路安全興趣
  - 包含個人經歷與未來目標

- [ ] 準備 SOP Variant - Quantum Focus
  - 專為隆德大學客製化
  - 高學術性內容
  - 強調量子科技興趣與背景
  - 展示跨領域學習能力

### Stage 8.3: 文件生成自動化

#### TODOs:
- [ ] 擴充現有的文件生成系統
  - 更新 `build_scripts/master_controller.py`
  - 為瑞典學校新增生成邏輯
  - 實作學校特定的客製化

- [ ] 建立文件驗證機制
  - 檢查所有必要資訊是否填寫
  - 驗證文件格式正確性
  - 生成 validation report

### Stage 8.4: 推薦信協調

#### TODOs:
- [ ] 更新 `recommenders.yml`
  - 為每所瑞典學校指派推薦人
  - 更新推薦信請求狀態

- [ ] 生成推薦信請求郵件
  - 使用 `recommendation_tracker.py` 生成郵件草稿
  - 發送推薦信請求

- [ ] 追蹤推薦信進度
  - 定期更新狀態
  - 發送提醒（如需要）

### Stage 8.5: 申請提交與追蹤

#### TODOs:
- [ ] Universityadmissions.se 申請
  - 建立帳號（如尚未建立）
  - 上傳所有文件
  - 填寫申請表單
  - 按優先順序排列學校（最多 4 所）

- [ ] 申請後監控啟動
  - 確保 `check_status_sweden.py` 正常運作
  - 驗證狀態正確抓取
  - 設定即時通知

- [ ] 追蹤與管理
  - 每週檢視 `application_dashboard.md`
  - 更新申請狀態
  - 準備補充材料（如需要）

---

## 品質保證與測試策略

### 單元測試
- 所有新增功能必須包含單元測試
- 測試覆蓋率目標：80% 以上
- 測試框架：pytest

### 整合測試
- 端到端測試所有監控流程
- 測試 CI/CD Pipeline
- 測試通知系統完整性

### 安全性檢查
- 確保所有敏感資訊使用 Secrets 管理
- 檢查爬蟲腳本不會對目標網站造成過度負載
- 實作 rate limiting
- 錯誤訊息不洩露敏感資訊

### 效能監控
- 監控腳本執行時間
- 監控 API 呼叫次數（避免超過限制）
- 優化爬蟲效率

---

## 風險管理

### 技術風險
1. **網站結構變更**
   - 緩解策略：建立健全的錯誤偵測機制，當爬蟲失敗時立即通知
   - 備用方案：準備手動檢查流程

2. **API 限制**
   - 緩解策略：實作 rate limiting，避免超過 API 限制
   - 備用方案：降低執行頻率

3. **驗證失效**
   - 緩解策略：定期更新憑證，實作自動重新驗證機制
   - 備用方案：手動重新授權流程

### 時程風險
1. **開發延遲**
   - 緩解策略：優先實作核心功能（瑞典監控 + Calendar 整合）
   - 備用方案：部分功能可延後至申請提交後實作

2. **申請截止日迫近**
   - 緩解策略：每週檢視進度，提前準備文件
   - 備用方案：確保至少第一梯隊學校按時完成

---

## 專案里程碑

| 里程碑 | 目標日期 | 交付內容 |
|-------|---------|---------|
| M1: 專案規劃完成 | 完成後 3 天 | 完整專案計畫、架構設計、環境設定 |
| M2: 監控系統上線 | 完成後 2 週 | 所有申請平台監控腳本運作，CI/CD Pipeline 建置完成 |
| M3: 整合功能完成 | 完成後 3 週 | Google Calendar 整合、推薦信追蹤系統、財務儀表板 |
| M4: 瑞典文件準備完成 | 2025年11月中 | 所有 CV 與 SOP 準備完成，推薦信請求發送 |
| M5: 瑞典申請提交完成 | 2026年1月初 | 所有瑞典學校申請於 Universityadmissions.se 提交 |
| M6: 進階功能完成 | 2026年1月底 | 簽證監控、財務分析完整運作 |

---

## 成功指標

### 功能完整性
- ✅ 所有 8 個監控平台腳本開發完成並運作正常
- ✅ Google Calendar 自動同步所有 deadline
- ✅ 推薦信狀態透明化管理
- ✅ 財務資訊完整且準確

### 自動化程度
- ✅ 80% 以上的監控任務自動化執行
- ✅ 狀態變更 5 分鐘內收到通知
- ✅ Dashboard 每日自動更新

### 申請成果
- ✅ 所有瑞典第一梯隊學校按時提交申請
- ✅ 至少 80% 的第二梯隊學校按時提交申請
- ✅ 所有推薦信按時提交

---

## 文檔維護

### 必須維護的文檔
1. **API 整合文檔** - 記錄所有第三方 API 的使用方式與限制
2. **爬蟲腳本文檔** - 記錄每個平台的 HTML 結構分析與更新歷史
3. **故障排除指南** - 記錄常見問題與解決方案
4. **系統架構圖** - 視覺化整個系統的運作流程

### 文檔更新頻率
- 每次新增功能時更新相關文檔
- 每週檢視故障排除指南，新增遇到的問題
- 每月檢視整體架構，確保文檔與實作同步

---

## 後續擴展計畫

### 短期（申請季結束後）
- 新增更多國家的申請平台支援
- 優化爬蟲效率與穩定性
- 開發 Web UI 取代純 Markdown Dashboard

### 中期（錄取後）
- 全面啟動簽證預約監控
- 開發住宿搜尋自動化
- 整合航班價格監控

### 長期（未來重複使用）
- 將系統泛用化，支援其他人使用
- 開發 SaaS 版本
- 社群貢獻與開源

---

**專案負責人**: Dennis Lee  
**文件版本**: v1.0  
**最後更新**: 2025-10-09  
**狀態**: ✅ 規劃完成，準備開始實作

