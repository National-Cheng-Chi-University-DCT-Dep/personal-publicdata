# 🚀 Harness Pipeline 更新指南

**目的**: 將修復後的 pipelines 同步到 Harness  
**時間**: 2025-10-09  
**狀態**: ✅ 程式碼已 push 到 GitHub

---

## ✅ 已完成

- [x] 所有 Harness 錯誤修復 (5 輪)
- [x] 本地 commit 完成
- [x] Push 到 GitHub 成功

**Commit**: `f7ced2d` - "fix: Complete all Harness runtime errors"

---

## 📋 接下來的步驟

### 步驟 1: 建立 GitHub Personal Access Token (新增！) 🔑

這是**新增的必要步驟**，用於 Git push 認證。

#### 1.1 建立 Token

1. 前往: https://github.com/settings/tokens
2. 點擊 **"Generate new token"** → **"Generate new token (classic)"**
3. 填寫:
   - **Note**: `Harness Automation Token`
   - **Expiration**: `90 days` (或您需要的期限)
   - **Scopes**: 勾選以下
     - ✅ `repo` (Full control of private repositories)
     - ✅ `workflow` (Update GitHub Action workflows)
4. 點擊 **"Generate token"**
5. **立即複製 Token**（只會顯示一次！）
   - 格式: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

#### 1.2 在 Harness 新增 Secret

1. 前往 Harness
2. **Project Setup** → **Secrets**
3. 點擊 **"+ New Secret"** → **"Text"**
4. 填寫:
   - **Secret Name**: `github_token`
   - **Secret Value**: 貼上您剛複製的 GitHub Token
   - **Description**: `GitHub Personal Access Token for automated commits`
5. 點擊 **"Save"**

---

### 步驟 2: 在 Harness 更新 Pipelines 🔄

您有兩個選擇：

#### 選項 A: 重新匯入 (推薦，最乾淨)

1. **刪除舊 Pipelines**
   ```
   Harness → Pipelines
   - Visa Information Monitoring → Delete
   - Application Monitoring Pipeline → Delete
   - Course Discovery Pipeline → Delete
   ```

2. **重新匯入**
   ```
   Harness → Pipelines → "+ New Pipeline" → "Import From Git"
   
   依序匯入:
   - .harness/visa_monitoring_pipeline.yml
   - .harness/monitoring_pipeline.yml
   - .harness/course_discovery_pipeline.yml
   ```

3. **驗證**
   - 開啟每個 pipeline
   - 檢查 YAML 中是否包含 `GITHUB_TOKEN`
   - 確認無 schema 錯誤

#### 選項 B: 手動同步 (較快但可能出錯)

1. 開啟 Harness 中的 pipeline
2. 切換到 **"YAML"** 頁籤
3. 複製 GitHub 上的最新 YAML
4. 貼上並儲存
5. 重複以上步驟給所有 3 個 pipelines

**⚠️ 注意**: 選項 A 更可靠，建議使用

---

### 步驟 3: 測試執行 🧪

#### 3.1 測試 Visa Monitoring (最簡單)

```
1. Harness → Pipelines → Visa Information Monitoring
2. 點擊 "Run"
3. 觀察執行日誌:
   ✅ "=== Setting up GitHub authentication ===" 出現
   ✅ "=== Pushing to GitHub ===" 成功
   或
   ✅ "✅ No changes to commit"
```

**預期結果**:
- ✅ Pipeline 執行成功
- ✅ 沒有 "fatal: could not read Username" 錯誤
- ✅ 如果有變更，成功 push 到 GitHub

#### 3.2 驗證 Git Push

如果有變更被 push，前往 GitHub 查看:
```
https://github.com/National-Cheng-Chi-University-DCT-Dep/personal-publicdata/commits/main
```

應該看到:
- ✅ "🛂 Update visa monitoring [Harness automated]" commit
- ✅ Author: Harness Automation

---

## 🎯 快速驗證清單

### 前置檢查
- [ ] GitHub Token 已建立
- [ ] Harness Secret `github_token` 已設定
- [ ] 所有其他 Secrets 都已設定 (9 個)

### Pipeline 更新
- [ ] Visa Monitoring Pipeline 已更新
- [ ] Application Monitoring Pipeline 已更新
- [ ] Course Discovery Pipeline 已更新

### 測試執行
- [ ] Visa Monitoring Pipeline 手動執行成功
- [ ] 沒有 Git push 認證錯誤
- [ ] 如有變更，成功 push 到 GitHub

---

## ❌ 故障排除

### 問題 1: 仍然出現 "could not read Username"

**原因**: Pipeline 沒有更新或 Secret 未設定

**解決**:
1. 確認 Pipeline YAML 包含:
   ```yaml
   envVariables:
     GITHUB_TOKEN: <+secrets.getValue("github_token")>
   ```
2. 確認 Secret `github_token` 存在且正確

---

### 問題 2: "Secret 'github_token' not found"

**原因**: Secret 名稱不一致

**解決**:
1. 檢查 Secret 名稱是否完全一致（小寫 + 底線）
2. 確認 Secret 在正確的 Project 中

---

### 問題 3: Git push 成功但看不到 commit

**原因**: 沒有實際變更需要 commit

**解決**:
- 這是正常的！
- 只有監控到變更時才會 commit
- 查看日誌應該顯示 "✅ No changes to commit"

---

## 📊 最終驗證

執行成功後，您應該看到：

```
✅ Visa Information Monitoring
   → Run Visa Monitor: Success
   → Commit Changes: Success
   → No Git authentication errors

✅ Application Monitoring Pipeline  
   → All 3 stages: Success
   → Git push authentication works

✅ Course Discovery Pipeline
   → Complete flow: Success
   → Smart file checking works
```

---

## 🎉 完成後

恭喜！所有 Harness 錯誤都已修復並且 pipelines 已更新。

### 下一步
- ✅ 啟用自動 Triggers
- ✅ 設定定期執行
- ✅ 監控執行日誌

### 或者...

**考慮使用 GitHub Actions？** 🤔

如果您覺得 Harness 設定太複雜：
- ✅ GitHub Actions 已經完整配置
- ✅ 更簡單（無需 Connector、更少 Secrets）
- ✅ 免費 2,000 分鐘/月
- ✅ 原生 GitHub 整合

只需要:
```bash
# 設定 GitHub Secrets (在 GitHub Settings)
# 前往 Actions 頁面啟用 workflows
# 完成！
```

---

**更新完成**: 2025-10-09  
**需要的動作**: 
1. 建立 GitHub Token  
2. 在 Harness 新增 github_token Secret  
3. 更新/重新匯入 Pipelines  
4. 測試執行  

**預計時間**: 15-20 分鐘 ⏱️

