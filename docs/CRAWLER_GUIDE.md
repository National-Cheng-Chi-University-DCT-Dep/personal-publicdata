# 爬蟲開發指南

## 概述

本文檔提供開發申請平台監控爬蟲的詳細指南，包括技術選型、實作模式、錯誤處理等。

---

## 技術堆疊

### Playwright

我們使用 Playwright 作為主要的瀏覽器自動化工具。

**優點**:
- ✅ 支援多種瀏覽器 (Chromium, Firefox, WebKit)
- ✅ 自動等待機制，減少 timing issues
- ✅ 強大的選擇器引擎
- ✅ 內建截圖和錄影功能
- ✅ 良好的異步支援

**安裝**:
```bash
pip install playwright
playwright install chromium
```

---

## 爬蟲開發模式

### 1. 繼承 BaseMonitor

所有監控腳本都應繼承 `BaseMonitor` 類別：

```python
from monitoring.base_monitor import BaseMonitor

class MyPlatformMonitor(BaseMonitor):
    def __init__(self, config=None):
        super().__init__(config)
        self.username = os.getenv('PLATFORM_USERNAME')
        self.password = os.getenv('PLATFORM_PASSWORD')
    
    async def run_async(self):
        # 實作監控邏輯
        pass
    
    def run(self):
        return asyncio.run(self.run_async())
```

### 2. 基本流程

```python
async def run_async(self):
    try:
        # 1. 啟動瀏覽器
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        # 2. 登入
        await self.login(page)
        
        # 3. 導航至目標頁面
        await self.navigate_to_applications(page)
        
        # 4. 抓取資料
        data = await self.extract_data(page)
        
        # 5. 比對狀態變更
        old_status = self.load_saved_status('platform_name')
        if self.detect_changes(old_status, data):
            self.send_notification(data)
        
        # 6. 儲存新狀態
        self.save_status('platform_name', data)
        
        # 7. 清理
        await browser.close()
        await playwright.stop()
        
        return True
    except Exception as e:
        self.logger.error(f"Error: {e}")
        return False
```

---

## 登入處理

### 基本登入流程

```python
async def login(self, page: Page):
    """登入系統"""
    try:
        # 導航至登入頁面
        await page.goto('https://example.com/login')
        
        # 填寫帳號密碼
        await page.fill('input[name="username"]', self.username)
        await page.fill('input[name="password"]', self.password)
        
        # 點擊登入按鈕
        await page.click('button[type="submit"]')
        
        # 等待登入完成
        await page.wait_for_url('**/dashboard', timeout=10000)
        
        self.logger.info("登入成功")
        return True
    except Exception as e:
        self.logger.error(f"登入失敗: {e}")
        raise
```

### 處理 2FA/CAPTCHA

如果平台有 2FA 或 CAPTCHA：

```python
# 方法 1: 使用 Session Cookie
# 先手動登入一次，取得 session cookie，存入 Secrets

async def login_with_cookie(self, page: Page):
    cookies = json.loads(os.getenv('PLATFORM_COOKIES'))
    await page.context.add_cookies(cookies)
    await page.goto('https://example.com/dashboard')
```

```python
# 方法 2: 等待手動介入（僅限本地測試）
async def login_with_manual_2fa(self, page: Page):
    await page.fill('input[name="username"]', self.username)
    await page.fill('input[name="password"]', self.password)
    await page.click('button[type="submit"]')
    
    # 等待使用者手動輸入 2FA 碼
    print("請在瀏覽器中完成 2FA 驗證...")
    await page.wait_for_url('**/dashboard', timeout=60000)
```

---

## 資料抓取

### 使用選擇器

Playwright 支援多種選擇器：

```python
# CSS Selector
element = await page.query_selector('.application-status')

# XPath
element = await page.query_selector('xpath=//div[@class="status"]')

# Text Content
element = await page.query_selector('text="Under Review"')

# 組合選擇器
element = await page.query_selector('div.application >> text="Status"')
```

### 抓取表格資料

```python
async def extract_applications(self, page: Page):
    """抓取申請清單"""
    applications = []
    
    # 取得所有申請項目
    items = await page.query_selector_all('.application-item')
    
    for item in items:
        # 抓取各個欄位
        school = await item.query_selector('.school-name')
        program = await item.query_selector('.program-name')
        status = await item.query_selector('.status')
        
        applications.append({
            'school': await school.inner_text() if school else 'N/A',
            'program': await program.inner_text() if program else 'N/A',
            'status': await status.inner_text() if status else 'N/A',
            'timestamp': datetime.now().isoformat()
        })
    
    return applications
```

### 等待動態內容

```python
# 等待特定元素出現
await page.wait_for_selector('.application-list', state='visible')

# 等待網路閒置
await page.wait_for_load_state('networkidle')

# 等待特定時間
await page.wait_for_timeout(2000)

# 等待 URL 變更
await page.wait_for_url('**/applications')
```

---

## 處理 API 請求

### 攔截網路請求

有些平台使用 API，可以直接攔截：

```python
async def monitor_with_api(self, page: Page):
    """監控 API 請求"""
    api_data = None
    
    async def handle_response(response):
        nonlocal api_data
        if 'api/applications' in response.url:
            api_data = await response.json()
    
    page.on('response', handle_response)
    
    # 導航至頁面，觸發 API 請求
    await page.goto('https://example.com/applications')
    await page.wait_for_timeout(3000)
    
    return api_data
```

### 直接呼叫 API

如果找到 API 端點：

```python
import requests

def call_api_directly(self):
    """直接呼叫 API"""
    headers = {
        'Authorization': f'Bearer {self.token}',
        'Content-Type': 'application/json'
    }
    
    response = requests.get(
        'https://api.example.com/applications',
        headers=headers
    )
    
    return response.json()
```

---

## 錯誤處理

### 重試機制

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def fetch_with_retry(self, page: Page, url: str):
    """帶重試的頁面抓取"""
    await page.goto(url, timeout=30000)
    return await page.content()
```

### 截圖除錯

```python
async def debug_screenshot(self, page: Page, name: str):
    """儲存截圖用於除錯"""
    screenshot_path = f'logs/screenshots/{name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
    await page.screenshot(path=screenshot_path, full_page=True)
    self.logger.info(f"截圖已儲存: {screenshot_path}")
```

### 常見錯誤處理

```python
try:
    await page.click('button.submit')
except TimeoutError:
    self.logger.warning("元素未找到，可能頁面結構已變更")
    await self.debug_screenshot(page, 'timeout_error')
    raise

except Exception as e:
    self.logger.error(f"未預期的錯誤: {e}")
    await self.debug_screenshot(page, 'unknown_error')
    raise
```

---

## 速率限制

### 實作 Rate Limiter

```python
import time
from collections import deque

class RateLimiter:
    def __init__(self, max_requests=10, time_window=60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = deque()
    
    def allow_request(self):
        now = time.time()
        
        # 移除過期的請求記錄
        while self.requests and now - self.requests[0] > self.time_window:
            self.requests.popleft()
        
        # 檢查是否超過限制
        if len(self.requests) < self.max_requests:
            self.requests.append(now)
            return True
        
        # 計算需要等待的時間
        wait_time = self.time_window - (now - self.requests[0])
        return False, wait_time
```

### 使用範例

```python
rate_limiter = RateLimiter(max_requests=5, time_window=60)

for url in urls:
    result = rate_limiter.allow_request()
    if isinstance(result, tuple):  # 需要等待
        _, wait_time = result
        self.logger.info(f"達到速率限制，等待 {wait_time:.1f} 秒")
        await asyncio.sleep(wait_time)
    
    await page.goto(url)
```

---

## 測試策略

### 單元測試

```python
import pytest
from unittest.mock import Mock, AsyncMock

@pytest.mark.asyncio
async def test_login():
    monitor = MyPlatformMonitor()
    page = AsyncMock()
    
    await monitor.login(page)
    
    page.goto.assert_called_once()
    page.fill.assert_called()
    page.click.assert_called_once()
```

### 整合測試

```python
@pytest.mark.asyncio
async def test_full_monitoring_flow():
    monitor = MyPlatformMonitor()
    success = await monitor.run_async()
    
    assert success is True
    # 驗證狀態檔案已建立
    assert Path('reports/status_history/platform_status.json').exists()
```

---

## 最佳實踐

### 1. 尊重網站資源

- ✅ 實作適當的延遲 (`await page.wait_for_timeout(2000)`)
- ✅ 使用 Rate Limiting
- ✅ 在合理的時間執行（避免尖峰時段）
- ❌ 不要過度頻繁地爬取

### 2. 可維護性

- ✅ 使用有意義的選擇器（class、id，避免過於依賴 nth-child）
- ✅ 記錄 HTML 結構快照（用於比對變更）
- ✅ 詳細的日誌記錄
- ✅ 錯誤時自動截圖

### 3. 安全性

- ✅ 所有憑證使用環境變數或 Secrets
- ✅ 在 headless 模式執行（生產環境）
- ✅ 清理臨時檔案和 cookies
- ❌ 絕不在程式碼中硬編碼帳密

### 4. 可靠性

- ✅ 實作重試機制
- ✅ 優雅地處理網頁結構變更
- ✅ 發送失敗通知
- ✅ 保留歷史記錄

---

## 除錯技巧

### 1. 非 Headless 模式

本地測試時，關閉 headless 模式觀察瀏覽器行為：

```python
browser = await playwright.chromium.launch(
    headless=False,  # 顯示瀏覽器視窗
    slow_mo=1000     # 每個操作慢放 1 秒
)
```

### 2. 錄製操作

```python
context = await browser.new_context(
    record_video_dir='logs/videos/'
)
```

### 3. 追蹤器

```python
# 啟用追蹤
await context.tracing.start(screenshots=True, snapshots=True)

# 執行操作
await page.goto('...')

# 停止並儲存追蹤
await context.tracing.stop(path='logs/trace.zip')
# 使用 playwright show-trace logs/trace.zip 檢視
```

---

## 範例：完整的監控腳本

請參考 `monitoring/pre_application/check_opening_status.py` 作為範本。

---

**版本**: 1.0  
**更新日期**: 2025-10-09  
**維護者**: Dennis Lee

