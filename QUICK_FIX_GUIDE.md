# 🚀 快速修復指南 - Course Discovery

**問題**: 找不到課程（0 個結果）  
**原因**: CSS selectors 過時  
**解決**: 使用診斷工具找出正確的 selectors

---

## ✅ 依賴已安裝

- ✅ Playwright 已安裝
- ✅ Chromium 瀏覽器已下載
- ✅ 準備就緒！

---

## 🔧 執行診斷工具（3 步驟）

### 步驟 1: 執行診斷

在您的終端機（PowerShell）中：

```powershell
cd C:\Users\dennis.lee\Documents\GitHub\personal-publicdata\discovery
python diagnose_scrapers.py
```

### 步驟 2: 選擇診斷選項

當提示時，輸入：
```
選擇要診斷的網站 (1: Mastersportal, 2: Study.eu, 3: 兩者都診斷): 3
```

### 步驟 3: 觀察結果

工具會：
1. 🌐 **開啟瀏覽器視窗**（您可以看到實際網頁）
2. 🔍 **自動測試各種 CSS selectors**
3. ✅ **顯示哪些有效**，例如：
   ```
   ✅ '.NewCardClass' - 找到 20 個元素
   ❌ '.OldCard' - 沒有找到
   ```
4. 💡 **給出建議**
5. 📸 **保存截圖**到 `logs/screenshots/`

每個網站診斷完畢後，按 **Enter** 繼續下一個。

---

## 📊 預期輸出範例

```
🔍 診斷 Mastersportal.com
===================================
📍 訪問: https://www.mastersportal.com/...

🔍 測試 CSS Selectors:
  ❌ '.StudyCard' - 沒有找到
  ❌ '.study-card' - 沒有找到
  ✅ '[data-testid="programme-card"]' - 找到 20 個元素  ← 找到了！
  
✅ 建議使用的 selector: '[data-testid="programme-card"]'

📊 分析第一個元素的 HTML 結構:
<div data-testid="programme-card" class="...">
  <h3 class="programme-title">MSc Cybersecurity</h3>
  <div class="university-name">KTH Royal Institute</div>
  ...
</div>

📸 截圖已儲存: logs/screenshots/mastersportal_diagnosis.png

⏸️  按 Enter 繼續...  ← 這裡按 Enter
```

---

## 🔄 更新 Scraper（基於診斷結果）

### 如果診斷找到新的 selector

例如，如果診斷顯示應該用 `[data-testid="programme-card"]`：

#### 更新 `scrape_mastersportal.py`

找到第 123-130 行：

```python
selectors = [
    '.StudyCard',
    '.study-card',
    '[class*="CourseCard"]',
    # ... 其他
]
```

改為（在最前面加入新的 selector）：

```python
selectors = [
    '[data-testid="programme-card"]',  # ← 從診斷得到的新 selector
    '.StudyCard',  # 保留作為 fallback
    '.study-card',
    '[class*="CourseCard"]',
    # ... 其他
]
```

同樣的方式更新 `scrape_studyeu.py`。

---

## 🧪 測試更新後的 Scraper

### 方法 1: 快速測試（只測試 Mastersportal）

```powershell
cd C:\Users\dennis.lee\Documents\GitHub\personal-publicdata

python -c "
import asyncio
from discovery.scrape_mastersportal import MastersPortalScraper

async def test():
    scraper = MastersPortalScraper(['Cybersecurity'], ['Sweden'])
    courses = scraper.run()
    print(f'✅ 找到 {len(courses)} 個課程')
    if courses:
        print(f'第一個課程: {courses[0][\"program_name\"]} at {courses[0][\"university_name\"]}')

asyncio.run(test())
"
```

### 方法 2: 完整測試（測試整個流程）

```powershell
# 1. Scraping
python discovery/scrape_mastersportal.py

# 2. Filtering
python discovery/filter_and_validate.py

# 3. 檢查結果
dir discovery\qualified_schools_*.yml
```

---

## ❌ 如果診斷工具也找不到元素

這表示：
1. 網站有強力的 anti-bot 保護
2. 需要登入才能看到課程
3. 網站結構完全改變

### 替代方案 A: 手動查看網頁源碼

1. 訪問 https://www.mastersportal.com/search/master/?q=Cybersecurity
2. 按 `F12` 開啟開發者工具
3. 點選 "Elements" 頁籤
4. 找到課程卡片
5. 查看它的 class name 或 data-testid
6. 手動更新 scraper

### 替代方案 B: 暫時使用手動資料

建立 `source_data/manual_courses.yml`:

```yaml
manual_courses:
  - program_name: "MSc Cybersecurity"
    university_name: "KTH Royal Institute of Technology"
    country: "Sweden"
    city: "Stockholm"
    tuition_info: "No tuition fees for EU/EEA students"
    program_url: "https://www.kth.se/en/studies/master/cybersecurity"
    ielts_overall: 6.5
    application_deadline: "2026-01-15"
    source: "Manual"
  
  # 加入更多您感興趣的課程...
```

然後更新 pipeline 來讀取這個檔案。

---

## 📝 Checklist

- [x] Playwright 已安裝
- [x] Chromium 已下載
- [ ] 執行診斷工具
- [ ] 查看診斷結果
- [ ] 更新 scrapers（如果找到新 selectors）
- [ ] 本地測試
- [ ] Commit & Push
- [ ] 在 Harness 重新執行

---

## 💡 小技巧

### 如果瀏覽器視窗太快關閉

在 `diagnose_scrapers.py` 中，找到：

```python
browser = await p.chromium.launch(headless=False)
```

確保 `headless=False` 這樣您可以看到瀏覽器。

### 如果想要更多時間查看

在 `input()` 之前加入：

```python
await page.wait_for_timeout(30000)  # 等待 30 秒
input("按 Enter 繼續...")
```

---

## 🚀 執行命令總結

```powershell
# 1. 診斷
cd C:\Users\dennis.lee\Documents\GitHub\personal-publicdata\discovery
python diagnose_scrapers.py

# 選擇 "3" 診斷兩個網站

# 2. 根據結果更新 scrape_mastersportal.py 和 scrape_studyeu.py

# 3. 測試
cd ..
python -c "import asyncio; from discovery.scrape_mastersportal import MastersPortalScraper; asyncio.run(MastersPortalScraper(['Cybersecurity'], ['Sweden']).run())"

# 4. 如果成功，commit
git add discovery/
git commit -m "fix: Update scrapers with correct CSS selectors"
git push origin main

# 5. 在 Harness 重新執行 Course Discovery Pipeline
```

---

## 📞 如果遇到問題

### 問題 1: "No module named 'yaml'"
```powershell
pip install pyyaml
```

### 問題 2: "Cannot find module 'playwright'"
```powershell
pip install playwright
python -m playwright install chromium
```

### 問題 3: 診斷找不到任何元素
- 查看截圖確認網頁內容
- 嘗試手動檢查網頁
- 考慮使用替代方案（手動資料或 API）

---

**準備好了！現在執行：**

```powershell
cd C:\Users\dennis.lee\Documents\GitHub\personal-publicdata\discovery
python diagnose_scrapers.py
```

選擇 "3" 來診斷兩個網站，然後根據結果更新 scrapers！🚀

