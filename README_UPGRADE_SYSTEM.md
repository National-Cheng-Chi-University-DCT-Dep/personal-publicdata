# 碩士申請管理系統升級版

## 🚀 專案概述

本專案將原有的碩士申請管理系統升級為一個**具備主動情報蒐集（爬蟲）與進階管理功能的自動化平台**。

### 核心目標
- 📊 自動監控所有申請平台的開放狀態與申請進度
- 📅 自動同步截止日期至 Google Calendar
- 📧 推薦信狀態透明化追蹤
- 🛂 簽證資訊自動監控
- 💰 財務規劃數據化分析
- 🤖 完整的 CI/CD 自動化流程

---

## 📁 專案結構

```
personal-publicdata/
├── 📋 專案文檔
│   ├── PROJECT_DEVELOPMENT_PLAN.md      # 完整開發計畫 (8 Phases)
│   ├── PROJECT_ARCHITECTURE.md          # 架構設計文件
│   ├── PROJECT_SUMMARY.md               # 專案總結
│   ├── IMPLEMENTATION_GUIDE.md          # 實作指南
│   └── IMPLEMENTATION_STATUS.md         # 進度追蹤
│
├── 🔍 監控系統
│   ├── monitoring/base_monitor.py       # 監控基類
│   ├── monitoring/pre_application/      # 申請開放監控
│   └── monitoring/post_application/     # 申請進度監控
│
├── 🔗 整合模組
│   └── integrations/                    # Google Calendar, Email 等
│
├── 📊 分析模組
│   ├── analysis/recommendation_tracker.py   # 推薦信追蹤
│   └── analysis/budget_analyzer.py          # 財務分析
│
├── 🤖 CI/CD
│   └── .github/workflows/               # GitHub Actions (4 workflows)
│
├── 📚 文檔
│   ├── docs/API_INTEGRATION.md          # API 整合指南
│   ├── docs/CRAWLER_GUIDE.md            # 爬蟲開發指南
│   └── docs/TROUBLESHOOTING.md          # 故障排除
│
└── 📦 資料
    ├── source_data/schools.yml          # 學校資料
    ├── source_data/recommenders.yml     # 推薦人資料
    ├── source_data/visa_requirements.yml # 簽證資訊
    └── source_data/application_status.yml # 申請狀態
```

---

## ✨ 核心功能

### 1. 申請平台監控系統 🔍

#### Pre-Application Monitor（申請開放監控）
- ✅ 自動檢查學校申請頁面
- ✅ 偵測 "Apply Now" 按鈕出現
- ✅ 分析 HTML 結構變化
- ✅ 狀態變更即時通知

#### Post-Application Monitor（申請進度監控）
支援 7 個申請平台：
- 🇸🇪 Universityadmissions.se (瑞典)
- 🇪🇪 estonia.dreamapply.com (愛沙尼亞)
- 🇩🇪 apply.cs.uni-saarland.de (德國薩爾蘭)
- 🇩🇪 uni-assist.de (德國統一系統)
- 🇫🇮 studyinfo.fi (芬蘭)
- 🇳🇴 soknadsweb.no (挪威)
- 🇳🇱 studielink.nl (荷蘭)

### 2. Google Calendar 整合 📅
- 自動同步所有申請截止日期
- 提前一週和三天的自動提醒
- schools.yml 更新時自動同步

### 3. 推薦信追蹤系統 📧
- 每所學校的推薦信狀態追蹤
- 自動生成提醒郵件草稿
- Dashboard 視覺化呈現

### 4. 簽證與移民資訊雷達 🛂
- 監控 6 國簽證資訊頁面變更
- 頁面 hash 值比對
- 簽證預約名額監控（進階）

### 5. 財務規劃儀表板 💰
- 申請費用總計（自動匯率轉換）
- 各校年度總花費比較
- 成本排名與分析

### 6. CI/CD 自動化 🤖
- GitHub Actions 自動排程執行
- 狀態變更自動 commit
- 監控報告自動上傳
- 失敗自動告警

---

## 🚀 快速開始

### 1. 環境設定

```bash
# Clone repository
git clone https://github.com/your-username/personal-publicdata.git
cd personal-publicdata

# 執行自動設定腳本
python scripts/setup_environment.py
```

### 2. 配置環境變數

```bash
# 複製範例檔案
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac

# 編輯 .env，填入您的資訊
notepad .env  # Windows
nano .env     # Linux/Mac
```

### 3. 更新學校資料

編輯 `source_data/schools.yml`，加入您的目標學校。

### 4. 執行測試

```bash
# 測試 Pre-Application 監控
python monitoring/pre_application/check_opening_status.py

# 查看結果
ls reports/status_history/
ls reports/monitoring_reports/
```

---

## 📖 文檔指南

### 新手必讀
1. **[實作指南](IMPLEMENTATION_GUIDE.md)** - 從零開始的完整指南
2. **[專案總結](PROJECT_SUMMARY.md)** - 了解專案全貌

### 開發者文檔
1. **[開發計畫](PROJECT_DEVELOPMENT_PLAN.md)** - 8 個 Phase 的詳細計畫
2. **[架構設計](PROJECT_ARCHITECTURE.md)** - 技術架構與實作細節
3. **[爬蟲開發指南](docs/CRAWLER_GUIDE.md)** - 如何開發監控腳本
4. **[API 整合指南](docs/API_INTEGRATION.md)** - 第三方服務整合

### 維護與排錯
1. **[進度追蹤](IMPLEMENTATION_STATUS.md)** - 即時更新的實作狀態
2. **[故障排除](docs/TROUBLESHOOTING.md)** - 常見問題與解決方案

---

## 🎯 實作進度

### ✅ Phase 1: 專案規劃與架構設計 (完成)
- 完整的開發計畫（8 Phases, 20+ Stages, 100+ TODOs）
- 詳細的架構設計
- 基礎程式碼框架
- 完整文檔系統

### 🔄 Phase 2: 申請平台監控系統 (進行中)
- ✅ Pre-Application 監控已完成
- 🔄 Post-Application 監控開發中

### ⏳ Phase 3-8 (待開始)
- Google Calendar 整合
- 推薦信追蹤系統
- 簽證監控系統
- 財務規劃儀表板
- CI/CD Pipeline 完整建置
- 瑞典申請衝刺

詳見 [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md)

---

## 🔧 支援的申請平台

| 平台 | 國家 | 監控類型 | 狀態 |
|------|------|---------|------|
| Universityadmissions.se | 🇸🇪 瑞典 | Pre + Post | 🔄 |
| estonia.dreamapply.com | 🇪🇪 愛沙尼亞 | Pre + Post | 🔄 |
| apply.cs.uni-saarland.de | 🇩🇪 德國 | Pre + Post | 🔄 |
| uni-assist.de | 🇩🇪 德國 | Pre + Post | 🔄 |
| studyinfo.fi | 🇫🇮 芬蘭 | Pre + Post | 🔄 |
| soknadsweb.no | 🇳🇴 挪威 | Pre + Post | 🔄 |
| studielink.nl | 🇳🇱 荷蘭 | Pre + Post | 🔄 |

---

## 🤖 自動化工作流

### GitHub Actions
所有 workflows 已配置，可在 Actions 頁面查看：

1. **Pre-Application Monitor**
   - 每天 9:00 和 17:00 (台北時間) 自動執行
   - 監控申請開放狀態

2. **Post-Application Monitor**
   - 每天 10:00 (台北時間) 自動執行
   - 並行監控 3 個平台

3. **Google Calendar Sync**
   - schools.yml 更新時自動觸發
   - 每週一定期同步

4. **Dashboard Update**
   - 每天自動更新
   - 推薦信狀態 + 財務分析

---

## 📊 專案統計

- **文件總頁數**: 150+ 頁
- **程式碼行數**: 1,000+ 行
- **支援平台數**: 7 個
- **監控國家數**: 6 個
- **GitHub Actions**: 4 個
- **文檔數量**: 10+ 份

---

## 🔒 安全性

- ✅ 所有敏感資訊使用 GitHub Secrets
- ✅ .env 檔案被 .gitignore
- ✅ Rate limiting 保護
- ✅ 資料 Schema 驗證

---

## 🛠️ 技術堆疊

- **Python 3.10+**
- **Playwright** - 瀏覽器自動化
- **Google Calendar API** - 行程管理
- **GitHub Actions** - CI/CD
- **Harness** - 進階 CI/CD（可選）
- **YAML** - 資料儲存
- **Markdown** - 文檔與報告

---

## 📞 支援

- 📚 查看 [文檔](docs/)
- 🐛 回報 Bug: GitHub Issues
- 💬 討論: GitHub Discussions

---

## 📝 授權

本專案僅供個人使用。

---

## 🙏 致謝

本專案基於需求文件 `new_requirementss.md` 進行設計與實作。

---

**狀態**: Phase 1 完成，Phase 2 進行中  
**版本**: v1.0  
**最後更新**: 2025-10-09  
**作者**: Dennis Lee

