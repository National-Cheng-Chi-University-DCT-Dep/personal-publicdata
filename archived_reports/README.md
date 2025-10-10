# 📦 Archived Reports

這個目錄包含所有 CI/CD pipeline 執行的歷史報告。

## 📁 目錄結構

每個子目錄代表一次 pipeline 執行：

```
archived_reports/
├── 20250107_134500_pipeline_123/
│   ├── reports/
│   │   ├── validation_report.md
│   │   ├── application_dashboard.md
│   │   ├── academic_intelligence_report.md
│   │   └── execution_report.md
│   ├── documents/
│   │   ├── TalTech/
│   │   ├── Aalto University/
│   │   └── ...
│   └── data/
│       ├── validation_results.json
│       ├── academic_intelligence.json
│       └── alert_summary.json
└── ...
```

## 🎯 命名規則

目錄名稱格式：`{TIMESTAMP}_pipeline_{PIPELINE_ID}`

- **TIMESTAMP**: `YYYYMMDD_HHMMSS` (UTC+8)
- **PIPELINE_ID**: Harness pipeline sequence ID

## 📊 查看報告

### 最新報告
查看 `/final_applications/` 目錄獲取最新的報告。

### 歷史報告
瀏覽此目錄下的子目錄查看特定時間點的報告。

## 🔍 搜索

使用 Git 歷史來追蹤變化：

```bash
# 查看特定文件的變化
git log -- archived_reports/

# 比較不同版本
git diff <commit1> <commit2> -- archived_reports/

# 搜索特定內容
git log -S "search term" -- archived_reports/
```

## 🚀 自動化

這些報告由 Harness CI/CD pipeline 自動生成和提交：

1. **Cron Trigger**: 每 3 天自動執行
2. **PR Trigger**: PR 到 main branch 時執行
3. **Manual Trigger**: 手動執行

## 📝 保留政策

- **短期**: 最近 30 天的所有報告
- **中期**: 過去 3 個月的每週報告
- **長期**: 每月歸檔報告

舊報告可以根據需要手動清理，但建議保留至少 3 個月的歷史記錄。

---

**Note**: 這是一個免費的儲存解決方案，使用 Git repository 而非付費的雲端儲存服務（如 AWS S3）。

