# 實作指南

## 快速開始

本指南將協助您快速設定並開始使用碩士申請管理系統的新功能。

---

## 前置需求

- Python 3.10 或更高版本
- Git
- GitHub 帳號（用於 CI/CD）
- Google 帳號（用於 Calendar 整合，可選）

---

## 安裝步驟

### 1. Clone Repository

```bash
git clone https://github.com/your-username/personal-publicdata.git
cd personal-publicdata
```

### 2. 建立虛擬環境

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. 安裝依賴套件

```bash
pip install -r requirements.txt
playwright install chromium
```

### 4. 設定環境變數

```bash
# 複製範例檔案
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac

# 編輯 .env 檔案，填入您的資訊
notepad .env  # Windows
nano .env     # Linux/Mac
```

必要的環境變數：
- `SWEDEN_USERNAME`: 瑞典申請平台帳號
- `SWEDEN_PASSWORD`: 瑞典申請平台密碼
- `NOTIFICATION_WEBHOOK`: Slack Webhook URL（可選）

---

## 基本使用

### 1. 執行 Pre-Application 監控

監控申請開放狀態：

```bash
python monitoring/pre_application/check_opening_status.py
```

### 2. 執行 Post-Application 監控

監控申請進度（瑞典）：

```bash
python monitoring/post_application/check_status_sweden.py
```

### 3. 同步 Google Calendar

```bash
python integrations/calendar_integration.py --sync
```

### 4. 更新 Dashboard

```bash
python analysis/recommendation_tracker.py
python analysis/budget_analyzer.py
```

---

## 資料管理

### 更新學校資料

編輯 `source_data/schools.yml`：

```yaml
schools:
  - name: "延雪平大學"
    name_english: "Jönköping University"
    country: "瑞典"
    program_name: "M.Sc. in Cybersecurity"
    application_url: "https://ju.se/apply"
    deadline: "2026-01-15"
    application_fee:
      amount: 900
      currency: "SEK"
    priority: "high"
```

### 更新推薦人資料

編輯 `source_data/recommenders.yml`：

```yaml
recommenders:
  - name: "教授名稱"
    title: "教授"
    institution: "大學名稱"
    email: "professor@university.edu"
    school_specific_status:
      - school: "延雪平大學"
        status: "requested"  # not_requested, requested, submitted, confirmed
        requested_date: "2025-11-01"
```

---

## GitHub Actions 設定

### 1. 設定 GitHub Secrets

前往 Repository Settings → Secrets and variables → Actions，新增以下 Secrets：

**申請平台帳號**:
- `SWEDEN_USERNAME`
- `SWEDEN_PASSWORD`
- `DREAMAPPLY_USERNAME`
- `DREAMAPPLY_PASSWORD`
- （其他平台帳號）

**Google Calendar** (可選):
- `GOOGLE_CREDENTIALS_JSON`
- `GOOGLE_TOKEN_JSON`

**通知服務** (可選):
- `NOTIFICATION_WEBHOOK`
- `EMAIL_PASSWORD`

### 2. 啟用 Workflows

所有 workflows 位於 `.github/workflows/`：

- `pre_application_monitor.yml`: 每天自動執行 2 次
- `post_application_monitor.yml`: 每天自動執行 1 次
- `calendar_sync.yml`: 當 schools.yml 更新時執行
- `dashboard_update.yml`: 每天自動更新

您可以在 Actions 頁面手動觸發任何 workflow。

---

## Harness 設定（進階）

### 1. 建立 Harness 專案

1. 登入 [Harness](https://app.harness.io/)
2. 建立新專案
3. 連接 GitHub Repository

### 2. 設定 Secrets

在 Harness 中新增所有必要的 Secrets。

### 3. 匯入 Pipelines

將 `.harness/` 目錄中的 YAML 檔案匯入 Harness。

---

## Google Calendar 整合

### 1. 建立 Google Cloud 專案

1. 前往 [Google Cloud Console](https://console.cloud.google.com/)
2. 建立新專案
3. 啟用 Google Calendar API

### 2. 建立 OAuth 憑證

1. 前往「API 和服務」→「憑證」
2. 建立「OAuth 用戶端 ID」（桌面應用程式）
3. 下載 `credentials.json`

### 3. 首次授權

```bash
python integrations/calendar_integration.py --setup
```

這會開啟瀏覽器，要求您授權。成功後會生成 `token.pickle`。

### 4. 將憑證存入 GitHub Secrets

```bash
# Windows (PowerShell)
$credentials = Get-Content credentials.json -Raw
$credentialsBase64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($credentials))
$credentialsBase64 | Out-File credentials_base64.txt

# Linux/Mac
cat credentials.json | base64 > credentials_base64.txt
cat token.pickle | base64 > token_base64.txt
```

將檔案內容複製到 GitHub Secrets：
- `GOOGLE_CREDENTIALS_JSON`: credentials_base64.txt 內容
- `GOOGLE_TOKEN_JSON`: token_base64.txt 內容

---

## 監控執行

### 本地測試

```bash
# 測試 Pre-Application 監控
python monitoring/pre_application/check_opening_status.py

# 測試 Post-Application 監控（需要帳號密碼）
python monitoring/post_application/check_status_sweden.py

# 檢查結果
ls reports/status_history/
ls reports/monitoring_reports/
```

### 查看日誌

```bash
# 即時查看日誌
tail -f logs/monitor.log  # Linux/Mac
Get-Content logs/monitor.log -Wait  # Windows PowerShell
```

### 除錯模式

```bash
# 使用非 headless 模式（可以看到瀏覽器）
# 編輯腳本，將 headless=True 改為 headless=False
```

---

## 通知設定

### Slack Webhook

1. 建立 Slack App
2. 啟用 Incoming Webhooks
3. 複製 Webhook URL
4. 存入環境變數或 GitHub Secrets: `NOTIFICATION_WEBHOOK`

### Email (Gmail)

1. 啟用 Gmail 2FA
2. 生成應用程式密碼
3. 設定環境變數：
   - `EMAIL_FROM`: 您的 Gmail 地址
   - `EMAIL_PASSWORD`: 應用程式密碼
   - `EMAIL_TO`: 接收通知的信箱

---

## 常見問題

### Q: 監控腳本無法登入？

A: 檢查：
1. 帳號密碼是否正確
2. 是否需要 2FA（考慮使用 cookie 方式）
3. 檢查網站是否有 CAPTCHA

### Q: GitHub Actions 失敗？

A: 檢查：
1. Secrets 是否正確設定
2. 查看 Actions 日誌
3. 確認 Playwright 正確安裝

### Q: Google Calendar 無法同步？

A: 檢查：
1. API 是否已啟用
2. Token 是否過期（刪除 token.pickle 重新授權）
3. 配額是否超過

### Q: 沒有收到通知？

A: 檢查：
1. Webhook URL 是否正確
2. 通知邏輯是否正確觸發
3. 查看日誌檔案

更多問題請參考 [故障排除指南](docs/TROUBLESHOOTING.md)。

---

## 進階功能

### 自訂監控頻率

編輯 `.github/workflows/*.yml` 中的 cron 表達式：

```yaml
on:
  schedule:
    # 每 6 小時執行一次
    - cron: '0 */6 * * *'
```

### 新增監控平台

1. 在 `monitoring/post_application/` 建立新腳本
2. 繼承 `BaseMonitor` 類別
3. 實作登入和資料抓取邏輯
4. 在 GitHub Actions 中新增對應的 job

### 自訂通知內容

編輯 `monitoring/base_monitor.py` 中的 `send_notification` 方法。

---

## 資料備份

建議定期備份以下資料：
- `source_data/` 目錄
- `reports/status_history/` 目錄
- `final_applications/` 目錄

您可以設定自動備份至 Google Drive 或其他雲端儲存。

---

## 安全性建議

1. ✅ 絕不將 `.env` commit 到 Git
2. ✅ 定期更新密碼
3. ✅ 使用強密碼
4. ✅ 定期檢查 GitHub Secrets
5. ✅ 監控 API 使用量

---

## 貢獻指南

如果您想貢獻程式碼或改進：

1. Fork Repository
2. 建立 feature branch
3. 提交 Pull Request
4. 確保所有測試通過

---

## 授權

本專案僅供個人使用。

---

## 支援

- 📚 查看 [專案文檔](docs/)
- 🐛 回報 Bug: [GitHub Issues]
- 💬 討論: [GitHub Discussions]

---

**版本**: 1.0  
**更新日期**: 2025-10-09  
**維護者**: Dennis Lee

