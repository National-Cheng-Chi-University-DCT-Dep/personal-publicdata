# 🚀 快速開始指南

這是一個 5 分鐘的快速開始指南，讓您立即開始使用碩士申請管理系統的所有功能。

---

## ⚡ 超快速開始（3 步驟）

```bash
# 1. 環境設定
python scripts/setup_environment.py

# 2. 配置帳號（編輯 .env 檔案）
notepad .env  # Windows
nano .env     # Linux/Mac

# 3. 測試運行
python scripts/test_monitors.py
```

✅ 完成！您的系統已就緒！

---

## 📋 詳細步驟

### 步驟 1: 安裝與設定 (5 分鐘)

```bash
# Clone repository (如果還沒有)
git clone https://github.com/your-username/personal-publicdata.git
cd personal-publicdata

# 執行自動設定
python scripts/setup_environment.py
```

這會自動：
- ✅ 檢查 Python 版本
- ✅ 建立所有目錄
- ✅ 安裝依賴套件
- ✅ 安裝 Playwright
- ✅ 建立 .env 檔案

### 步驟 2: 配置環境變數 (3 分鐘)

編輯 `.env` 檔案，填入您的資訊：

```bash
# 最低必要設定
SWEDEN_USERNAME=your_sweden_username
SWEDEN_PASSWORD=your_sweden_password
NOTIFICATION_WEBHOOK=your_slack_webhook  # 可選
```

### 步驟 3: 更新學校資料 (5 分鐘)

編輯 `source_data/schools.yml`，確認或新增您的目標學校。

### 步驟 4: 測試系統 (2 分鐘)

```bash
python scripts/test_monitors.py
```

選擇 `5` 測試全部功能。

---

## 🎯 主要功能使用

### 1️⃣ 監控申請開放狀態

```bash
python monitoring/pre_application/check_opening_status.py
```

**功能**: 自動檢查所有學校的申請頁面，偵測申請開放狀態。

**結果查看**:
```bash
dir reports\monitoring_reports\  # Windows
ls reports/monitoring_reports/   # Linux/Mac
```

### 2️⃣ 監控申請進度

```bash
# 瑞典
python monitoring/post_application/check_status_sweden.py

# DreamApply (愛沙尼亞等)
python monitoring/post_application/check_status_dreamapply.py

# 薩爾蘭大學
python monitoring/post_application/check_status_saarland.py
```

**功能**: 登入申請平台，自動抓取您的申請狀態。

### 3️⃣ Google Calendar 同步

```bash
# 首次使用（需要授權）
python integrations/calendar_integration.py --setup

# 同步截止日期
python integrations/calendar_integration.py --sync

# 查看已同步的事件
python integrations/calendar_integration.py --list
```

**功能**: 自動將所有申請截止日期同步到 Google Calendar，設定多重提醒。

### 4️⃣ 推薦信追蹤

```bash
python analysis/recommendation_tracker.py
```

**功能**:
- 追蹤每所學校的推薦信狀態
- 自動檢測逾期項目
- 生成請求和提醒郵件草稿

**查看郵件草稿**:
```bash
dir templates\email_templates\  # Windows
ls templates/email_templates/   # Linux/Mac
```

### 5️⃣ 簽證資訊監控

```bash
python monitoring/visa_monitor.py
```

**功能**:
- 監控 6 個國家的簽證資訊頁面
- 偵測內容變更
- 檢查預約名額

### 6️⃣ 財務規劃分析

```bash
# 使用固定匯率
python analysis/budget_analyzer.py

# 使用即時匯率
python analysis/budget_analyzer.py --live-rates
```

**功能**:
- 計算總申請成本
- 各校年度花費比較
- 獎學金資訊整理

**查看報告**:
```bash
dir reports\financial_reports\  # Windows
ls reports/financial_reports/   # Linux/Mac
```

---

## 📊 查看結果

### 所有報告
```bash
# Windows
dir reports\status_history\
dir reports\monitoring_reports\
dir reports\financial_reports\
dir templates\email_templates\

# Linux/Mac
ls reports/status_history/
ls reports/monitoring_reports/
ls reports/financial_reports/
ls templates/email_templates/
```

### 日誌
```bash
# Windows
type logs\monitor.log

# Linux/Mac
cat logs/monitor.log
tail -f logs/monitor.log  # 即時查看
```

### Dashboard
```bash
# Windows
notepad final_applications\application_dashboard.md

# Linux/Mac
cat final_applications/application_dashboard.md
```

---

## 🤖 啟用自動化

### GitHub Actions

1. **設定 GitHub Secrets**
   - 前往 Repository Settings → Secrets
   - 新增必要的 Secrets (見 .env.example)

2. **Secrets 清單**:
   ```
   SWEDEN_USERNAME
   SWEDEN_PASSWORD
   DREAMAPPLY_USERNAME
   DREAMAPPLY_PASSWORD
   SAARLAND_USERNAME
   SAARLAND_PASSWORD
   GOOGLE_CREDENTIALS_JSON
   GOOGLE_TOKEN_JSON
   NOTIFICATION_WEBHOOK
   ```

3. **啟用 Workflows**
   - 前往 Actions 頁面
   - 所有 workflows 會自動啟用
   - 可手動觸發測試

### Harness（進階，可選）

1. 登入 Harness
2. 匯入 `.harness/` 中的 pipelines
3. 設定 Secrets
4. 啟用 triggers

---

## 📚 詳細文檔

需要更多資訊？查看：

| 文檔 | 內容 | 適用對象 |
|------|------|---------|
| **IMPLEMENTATION_GUIDE.md** | 完整實作指南 | 所有使用者 |
| **PROJECT_DEVELOPMENT_PLAN.md** | 開發計畫 | 開發者 |
| **SWEDEN_APPLICATION_GUIDE.md** | 瑞典申請指南 | 申請者 |
| **docs/API_INTEGRATION.md** | API 整合 | 開發者 |
| **docs/CRAWLER_GUIDE.md** | 爬蟲開發 | 開發者 |
| **docs/TROUBLESHOOTING.md** | 故障排除 | 所有使用者 |

---

## 🆘 常見問題

### Q1: 監控腳本無法登入？
**A**: 檢查環境變數是否正確設定，查看 logs/screenshots/ 的截圖。

### Q2: Google Calendar 無法同步？
**A**: 先執行 `--setup` 進行授權，確認 credentials.json 存在。

### Q3: 沒有收到通知？
**A**: 檢查 NOTIFICATION_WEBHOOK 是否正確設定。

### Q4: GitHub Actions 失敗？
**A**: 確認所有 Secrets 都已設定，查看 Actions 日誌。

**更多問題**: 查看 docs/TROUBLESHOOTING.md

---

## 🎓 瑞典申請快速檢查清單

使用 SWEDEN_APPLICATION_GUIDE.md 作為完整指南。

### 準備階段
- [ ] 學校資料已更新在 schools.yml
- [ ] 截止日期已同步到 Google Calendar
- [ ] 推薦人已確認
- [ ] 財務規劃已分析

### 文件準備
- [ ] Master CV
- [ ] Master SOP
- [ ] 推薦信（2-3 封）
- [ ] 成績單（英文認證）
- [ ] 英語能力證明
- [ ] 護照影本

### 申請提交
- [ ] Universityadmissions.se 帳號建立
- [ ] 所有文件已上傳
- [ ] 學校優先順序已設定
- [ ] 申請已提交
- [ ] 啟用 Post-Application 監控

---

## 💡 專業建議

### 每日工作流程
```bash
# 早上：檢查所有狀態
python scripts/test_monitors.py

# 查看 dashboard
notepad final_applications\application_dashboard.md

# 查看推薦信狀態
python analysis/recommendation_tracker.py
```

### 每週工作流程
```bash
# 週一：
# - 查看簽證資訊（自動執行）
# - 檢查推薦信進度
# - 更新申請狀態

# 週末：
# - 準備或修改 SOP
# - 準備文件掃描檔
# - 聯繫推薦人
```

---

## 🎉 您已準備就緒！

所有系統已設定完成，您現在可以：

1. ✅ 自動監控所有申請平台
2. ✅ 自動追蹤截止日期
3. ✅ 管理推薦信狀態
4. ✅ 監控簽證資訊
5. ✅ 分析財務規劃
6. ✅ 完整的 CI/CD 自動化

**開始您的申請之旅吧！** 🚀

---

**建立日期**: 2025-10-09  
**版本**: v1.0  
**適用**: 所有使用者

