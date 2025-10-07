# 🚀 CI/CD 觸發器策略說明

## 📅 自動觸發策略

### 1. **定時觸發 - 每3天執行**
- **觸發器**: `tri_daily_intelligence`
- **排程**: `0 6 */3 * *` (每3天 6:00 AM UTC)
- **執行模式**: `full` (完整流程)
- **功能**: 
  - ✅ 資料收集 (web scraping)
  - ✅ 資料驗證
  - ✅ 智慧分析
  - ✅ 文件生成
  - ✅ 進階功能 (gamification, narrative, portfolio, whatif)
  - ✅ 通知處理

### 2. **Main Branch Push 觸發**
- **觸發器**: `main_push`
- **觸發條件**: 程式碼推送到 main branch
- **執行模式**: `full` (完整流程)
- **功能**: 
  - ✅ 資料收集 (web scraping)
  - ✅ 資料驗證
  - ✅ 智慧分析
  - ✅ 文件生成
  - ✅ 進階功能 (gamification, narrative, portfolio, whatif)
  - ✅ 通知處理

### 3. **Main Branch Pull Request 觸發**
- **觸發器**: `main_pr`
- **觸發條件**: PR 開啟/更新到 main branch
- **執行模式**: `quick` (快速流程)
- **功能**: 
  - ❌ 資料收集 (跳過以加速)
  - ✅ 資料驗證
  - ✅ 智慧分析
  - ✅ 文件生成
  - ❌ 進階功能 (跳過以加速)
  - ✅ 通知處理

## 🎯 手動觸發選項

### 4. **進階功能專用**
- **觸發器**: `advanced_only`
- **執行模式**: `advanced_only`
- **功能**: 只執行進階 AI 分析功能

### 5. **完整流程手動觸發**
- **觸發器**: `manual_full`
- **執行模式**: `full`
- **功能**: 完整流程，包含所有功能

## 📊 觸發器優先級和策略

### **高效能策略**
1. **PR 檢查**: 快速驗證，不執行耗時操作
2. **Push 觸發**: 完整流程，確保品質
3. **定時執行**: 定期更新和深度分析

### **資源優化**
- **PR**: 跳過 web scraping 和進階功能 (節省 10-15 分鐘)
- **Push**: 完整執行 (確保最新資料和分析)
- **定時**: 完整執行 (定期深度分析)

### **執行時間預估**
- **Quick Mode**: 5-8 分鐘
- **Full Mode**: 15-25 分鐘
- **Advanced Only**: 8-12 分鐘

## 🔧 配置說明

### **Cron 表達式解釋**
```
0 6 */3 * *  # 每3天 6:00 AM UTC
```
- `0` = 分鐘 (0分)
- `6` = 小時 (6點)
- `*/3` = 每3天
- `*` = 每月
- `*` = 每週

### **觸發器條件**
- **Main Branch**: 只針對 main branch 的變更
- **Auto-abort**: 新觸發會取消之前的執行
- **Payload Conditions**: 基於分支名稱過濾

## 📈 監控和通知

### **成功通知**
- 郵件通知到 `admin@dennisleehappy.org`
- 包含執行摘要和產出檔案

### **失敗通知**
- 郵件通知包含錯誤詳情
- 建議檢查步驟和解決方案

### **Slack 通知** (可選)
- 高優先級警告通知
- 需要配置 Slack webhook

## 🎛️ 手動控制

### **變數控制**
- `pipeline_mode`: 控制執行模式
- `skip_scraping`: 控制是否跳過資料收集
- `run_advanced_features`: 控制是否執行進階功能
- `target_schools`: 指定特定學校

### **使用範例**
```yaml
# 只執行驗證
pipeline_mode: "validate_only"

# 跳過資料收集的完整流程
pipeline_mode: "full"
skip_scraping: "true"

# 只執行進階功能
pipeline_mode: "advanced_only"
```

## 📋 最佳實踐

1. **PR 流程**: 使用快速模式進行基本檢查
2. **合併後**: 自動執行完整流程
3. **定期維護**: 每3天自動深度分析
4. **手動介入**: 需要時可手動觸發特定功能

## 🔍 故障排除

### **常見問題**
1. **觸發器未執行**: 檢查 GitHub webhook 配置
2. **Cron 未執行**: 確認時區設定 (UTC)
3. **權限問題**: 確認 GitHub token 權限

### **日誌位置**
- Harness 執行日誌
- GitHub Actions 日誌 (如果使用)
- 應用程式日誌在 `final_applications/`

---

**最後更新**: 2025-01-07  
**版本**: v2.0  
**維護者**: Application Intelligence System
