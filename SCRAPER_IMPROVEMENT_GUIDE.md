# 🔧 Scraper 改進指南

**問題**: Course Discovery Pipeline 找不到任何課程  
**原因**: 網站 HTML 結構已變更，CSS selectors 過時  
**狀態**: 需要更新 scrapers

---

## 🔍 問題診斷

### 當前狀態
```
Mastersportal: 0 個課程
Study.eu: 0 個課程
原因: "未找到課程卡片，可能沒有結果或頁面結構已變更"
```

### 根本原因
1. ❌ **網站 UI/HTML 結構更新**（最可能）
2. ❌ CSS selectors 過時
3. ⚠️ 可能有 anti-bot 保護
4. ⚠️ 搜尋參數可能需要調整

---

## 🛠️ 改進方案

### 方案 1: 使用診斷工具找出正確的 Selectors（推薦）

#### Step 1: 執行診斷工具

```bash
cd discovery
python diagnose_scrapers.py
```

這個工具會：
- ✅ 開啟瀏覽器讓你看到實際頁面
- ✅ 測試多個可能的 CSS selectors
- ✅ 顯示哪些 selectors 有效
- ✅ 分析 HTML 結構
- ✅ 保存截圖供診斷

#### Step 2: 查看診斷結果

工具會告訴你：
```
✅ 建議使用的 selector: '.NewCardClass'
📊 找到 20 個元素
📸 截圖已儲存: logs/screenshots/mastersportal_diagnosis.png
```

#### Step 3: 更新 Scraper

根據診斷結果，更新 `scrape_mastersportal.py` 中的 selectors：

```python
# 在 extract_courses_from_page 函式中
selectors = [
    '.NewCardClass',  # ← 從診斷工具得到的新 selector
    '.StudyCard',     # 保留作為 fallback
    # ... 其他 fallback selectors
]
```

---

### 方案 2: 手動檢查網站 DOM 結構

#### Step 1: 訪問網站
```
https://www.mastersportal.com/search/master/?q=Cybersecurity
```

#### Step 2: 開啟瀏覽器開發者工具
- 按 `F12` 或右鍵 → "檢查"
- 找到課程卡片元素
- 查看它的 class name

#### Step 3: 記錄 Selectors
記下以下資訊：
- 課程卡片的 class name
- 程式名稱的 class name  
- 大學名稱的 class name
- 連結的 href 格式

#### Step 4: 更新 Scraper
使用新的 selectors 更新程式碼

---

### 方案 3: 改用 API（最可靠）

某些網站提供官方 API，這比 scraping 更穩定。

#### Mastersportal API
檢查是否有官方 API：
```
https://www.mastersportal.com/api/...
```

如果有 API，建立新的 API-based scraper：

```python
import requests

class MastersPortalAPI:
    def search_courses(self, keyword):
        response = requests.get(
            'https://api.mastersportal.com/search',
            params={'q': keyword}
        )
        return response.json()
```

---

### 方案 4: 改善現有 Scraper 的穩定性

即使找到正確的 selectors，也建議加入以下改進：

#### A. 加入更多 Wait 策略

```python
# 在 search_courses 中
await page.goto(search_url, timeout=30000, wait_until='networkidle')

# 加入動態等待
await page.wait_for_selector('.course-card', state='visible', timeout=15000)

# 等待 AJAX 完成
await page.wait_for_function('document.readyState === "complete"')
await page.wait_for_timeout(3000)
```

#### B. 加入 Retry 機制

```python
async def search_courses_with_retry(self, page, keyword, max_retries=3):
    """帶 retry 的搜尋"""
    for attempt in range(max_retries):
        try:
            courses = await self.search_courses(page, keyword)
            if courses:
                return courses
            
            self.logger.warning(f"第 {attempt + 1} 次嘗試沒有結果，重試中...")
            await page.wait_for_timeout(5000)
        except Exception as e:
            self.logger.error(f"第 {attempt + 1} 次嘗試失敗: {e}")
            if attempt < max_retries - 1:
                await page.wait_for_timeout(10000)
            else:
                raise
    
    return []
```

#### C. 加入 User Agent Rotation

```python
async def init_browser(self):
    """初始化瀏覽器（加入 User Agent）"""
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        # ... 更多 User Agents
    ]
    
    import random
    self.browser = await self.playwright.chromium.launch(
        args=[f'--user-agent={random.choice(user_agents)}']
    )
```

#### D. 處理 CAPTCHA 和 Anti-Bot

```python
async def handle_antibot(self, page):
    """處理 anti-bot 檢測"""
    # 檢查是否有 CAPTCHA
    captcha_selectors = [
        'iframe[src*="recaptcha"]',
        '#challenge-form',
        '[class*="captcha"]'
    ]
    
    for selector in captcha_selectors:
        if await page.query_selector(selector):
            self.logger.warning("偵測到 CAPTCHA，暫停 60 秒...")
            await page.wait_for_timeout(60000)
            return True
    
    return False
```

---

## 📊 現有 Selectors 清單

### Mastersportal.com

**當前使用的 selectors**:
```python
# 課程卡片
['.StudyCard', '.study-card', '[class*="CourseCard"]', '[class*="ProgramCard"]']

# 課程內資訊
'.program-name'  # 程式名稱
'.university-name'  # 大學
'.country'  # 國家
'.tuition'  # 學費
```

**可能已過時！需要更新！**

### Study.eu

**當前使用的 selectors**:
```python
# 課程卡片
['[class*="course"]', '[class*="program"]', '.search-result']

# 課程內資訊
'.program-name'
'.university'
'.country'
```

**可能已過時！需要更新！**

---

## ✅ 更新 Checklist

### 診斷階段
- [ ] 執行 `diagnose_scrapers.py`
- [ ] 查看保存的截圖
- [ ] 記錄正確的 CSS selectors
- [ ] 檢查是否有 anti-bot 保護
- [ ] 檢查是否有官方 API

### 更新階段
- [ ] 更新 `scrape_mastersportal.py` 的 selectors
- [ ] 更新 `scrape_studyeu.py` 的 selectors
- [ ] 加入更多 fallback selectors
- [ ] 加入 retry 機制
- [ ] 改善 wait 策略

### 測試階段
- [ ] 本地測試 scrapers
- [ ] 確認能找到課程
- [ ] 驗證提取的資料格式正確
- [ ] 測試多個搜尋關鍵字
- [ ] 在 Harness 上測試

---

## 🚀 快速測試

### 本地測試 Mastersportal Scraper

```bash
cd discovery

# 執行診斷
python diagnose_scrapers.py

# 或直接測試 scraper
python -c "
import asyncio
from scrape_mastersportal import MastersPortalScraper

async def test():
    scraper = MastersPortalScraper(['Cybersecurity'], ['Sweden'])
    courses = await scraper.run()
    print(f'找到 {len(courses)} 個課程')

asyncio.run(test())
"
```

---

## 🎯 替代方案

如果 scraping 太不穩定，考慮：

### 1. 使用現有的課程數據庫 API

**Studyportals API** (如果有):
```python
import requests

def search_studyportals_api(keyword, country):
    # 可能需要 API key
    response = requests.get(
        'https://api.studyportals.com/v1/courses',
        params={
            'query': keyword,
            'country': country,
            'level': 'master'
        },
        headers={'Authorization': 'Bearer YOUR_API_KEY'}
    )
    return response.json()
```

### 2. 手動維護課程清單

建立 `discovery/manual_courses.yml`:
```yaml
courses:
  - program_name: "MSc Cybersecurity"
    university: "KTH Royal Institute of Technology"
    country: "Sweden"
    # ...
```

然後在 pipeline 中合併手動和自動資料。

### 3. 使用 RapidAPI 的教育 APIs

搜尋 "education API" 或 "university API" on RapidAPI。

---

## 📚 相關資源

- **Playwright 文檔**: https://playwright.dev/python/docs/selectors
- **CSS Selectors 參考**: https://www.w3schools.com/cssref/css_selectors.asp
- **Anti-Scraping 應對**: https://scrapeops.io/web-scraping-playbook/

---

## 💡 建議的優先順序

1. **立即** - 執行診斷工具找出正確的 selectors
2. **短期** - 更新 scrapers 並加入 retry 機制
3. **中期** - 尋找官方 API 替代方案
4. **長期** - 建立混合系統（API + scraping + 手動）

---

**建立日期**: 2025-10-09  
**狀態**: 待診斷和更新  
**預計時間**: 1-2 小時診斷 + 更新

