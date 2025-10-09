# 故障排除指南

## 常見問題與解決方案

---

## 環境設定問題

### Python 套件安裝失敗

**問題**: `pip install -r requirements.txt` 失敗

**解決方案**:
```bash
# 升級 pip
python -m pip install --upgrade pip

# 使用虛擬環境
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows

# 重新安裝
pip install -r requirements.txt
```

### Playwright 瀏覽器安裝失敗

**問題**: `playwright install chromium` 失敗

**解決方案**:
```bash
# 確認 Python 版本 >= 3.8
python --version

# 重新安裝 playwright
pip uninstall playwright
pip install playwright

# 手動安裝瀏覽器
python -m playwright install chromium

# 如果仍然失敗，安裝所有依賴
python -m playwright install-deps
```

---

## 監控腳本問題

### 登入失敗

**問題**: 監控腳本無法登入平台

**可能原因與解決方案**:

1. **帳號密碼錯誤**
   ```bash
   # 檢查環境變數
   echo $SWEDEN_USERNAME
   echo $SWEDEN_PASSWORD
   
   # 重新設定
   export SWEDEN_USERNAME="your_username"
   export SWEDEN_PASSWORD="your_password"
   ```

2. **頁面結構變更**
   - 檢查選擇器是否仍然有效
   - 使用非 headless 模式觀察：
   ```python
   browser = await playwright.chromium.launch(headless=False)
   ```
   - 更新選擇器

3. **需要 2FA**
   - 使用 session cookie 方式：
   ```python
   # 手動登入一次，取得 cookies
   await page.goto('https://platform.com')
   # 登入後
   cookies = await page.context.cookies()
   # 將 cookies 存入環境變數
   ```

4. **IP 被封鎖**
   - 減少執行頻率
   - 使用 VPN 或代理
   - 聯絡平台確認

### 元素找不到

**問題**: `TimeoutError: Timeout 30000ms exceeded`

**解決方案**:

1. **增加等待時間**
   ```python
   await page.wait_for_selector('.element', timeout=60000)
   ```

2. **等待網路閒置**
   ```python
   await page.goto(url, wait_until='networkidle')
   ```

3. **動態內容載入**
   ```python
   # 等待 AJAX 請求完成
   await page.wait_for_load_state('networkidle')
   await page.wait_for_timeout(2000)
   ```

4. **使用更寬鬆的選擇器**
   ```python
   # 不好 - 太具體
   await page.click('div.container > div.row > button:nth-child(1)')
   
   # 好 - 使用 class 或 text
   await page.click('button.submit-btn')
   await page.click('text="Submit"')
   ```

### 資料抓取錯誤

**問題**: 抓取的資料不正確或為空

**解決方案**:

1. **檢查 HTML 結構**
   ```python
   # 印出頁面內容
   content = await page.content()
   print(content)
   
   # 或儲存為檔案
   with open('debug.html', 'w', encoding='utf-8') as f:
       f.write(content)
   ```

2. **等待元素載入**
   ```python
   await page.wait_for_selector('.data-element', state='visible')
   ```

3. **處理 None 值**
   ```python
   element = await page.query_selector('.status')
   status = await element.inner_text() if element else 'N/A'
   ```

---

## Google Calendar 整合問題

### 授權失敗

**問題**: `invalid_grant` 錯誤

**解決方案**:
```bash
# 刪除舊的 token
rm token.pickle

# 重新授權
python integrations/calendar_integration.py --setup
```

### API 配額超過

**問題**: `429 Too Many Requests`

**解決方案**:
1. 減少執行頻率
2. 實作 exponential backoff：
   ```python
   from time import sleep
   
   retries = 0
   while retries < 5:
       try:
           service.events().insert(...).execute()
           break
       except HttpError as e:
           if e.resp.status == 429:
               wait_time = 2 ** retries
               sleep(wait_time)
               retries += 1
   ```

### Token 過期

**問題**: `Token has been expired or revoked`

**解決方案**:
```python
from google.auth.transport.requests import Request

if creds and creds.expired and creds.refresh_token:
    creds.refresh(Request())
```

---

## CI/CD 問題

### GitHub Actions 失敗

**問題**: Workflow 執行失敗

**解決方案**:

1. **檢查 Secrets**
   - 確認所有必要的 Secrets 都已設定
   - 檢查 Secrets 名稱拼寫
   - 確認 Secrets 沒有多餘的空格或換行

2. **檢查 Playwright 在 CI 中的問題**
   ```yaml
   - name: Install Playwright dependencies
     run: |
       playwright install-deps
       playwright install chromium
   ```

3. **權限問題**
   ```yaml
   permissions:
     contents: write  # 允許 push
   ```

4. **查看詳細日誌**
   ```yaml
   - name: Run monitor
     run: |
       python monitoring/pre_application/check_opening_status.py -v
   ```

### Harness Pipeline 失敗

**問題**: Pipeline 無法執行

**解決方案**:
1. 檢查 Harness Secrets 設定
2. 確認 delegate 運作正常
3. 檢查 YAML 語法錯誤

---

## 資料問題

### YAML 解析錯誤

**問題**: `yaml.scanner.ScannerError`

**解決方案**:
```bash
# 驗證 YAML 語法
python -c "import yaml; yaml.safe_load(open('source_data/schools.yml'))"

# 常見錯誤：
# 1. 縮排不一致（混用 tabs 和 spaces）
# 2. 冒號後沒有空格
# 3. 字串包含特殊字元未加引號
```

### JSON Schema 驗證失敗

**問題**: 資料不符合 Schema

**解決方案**:
```python
import jsonschema
import yaml
import json

# 載入 schema
with open('data_schemas/schools_schema.json') as f:
    schema = json.load(f)

# 載入資料
with open('source_data/schools.yml') as f:
    data = yaml.safe_load(f)

# 驗證
try:
    jsonschema.validate(data, schema)
    print("✅ 資料驗證通過")
except jsonschema.ValidationError as e:
    print(f"❌ 驗證失敗: {e.message}")
```

---

## 效能問題

### 監控腳本執行太慢

**問題**: 腳本執行時間過長

**解決方案**:

1. **並行處理**
   ```python
   import asyncio
   
   async def check_all_schools(schools):
       tasks = [check_school(school) for school in schools]
       return await asyncio.gather(*tasks)
   ```

2. **減少等待時間**
   ```python
   # 不要過度等待
   await page.wait_for_selector('.element', timeout=10000)
   # 而不是
   await page.wait_for_timeout(10000)
   ```

3. **使用 API 而非爬蟲**
   - 如果平台提供 API，優先使用

### 記憶體使用過高

**問題**: Python 程式佔用過多記憶體

**解決方案**:
```python
# 及時關閉瀏覽器
try:
    # 執行爬蟲
    pass
finally:
    await browser.close()
    await playwright.stop()

# 處理大量資料時，分批處理
for batch in chunks(schools, 10):
    process_batch(batch)
```

---

## 通知系統問題

### 通知未送達

**問題**: 狀態變更但沒有收到通知

**解決方案**:

1. **檢查 Webhook URL**
   ```bash
   # 測試 Slack webhook
   curl -X POST -H 'Content-type: application/json' \
     --data '{"text":"Test message"}' \
     $NOTIFICATION_WEBHOOK
   ```

2. **檢查 Email 設定**
   ```python
   # 測試 SMTP 連線
   import smtplib
   
   with smtplib.SMTP('smtp.gmail.com', 587) as server:
       server.starttls()
       server.login(username, password)
       print("✅ SMTP 連線成功")
   ```

3. **檢查通知邏輯**
   ```python
   # 加入除錯訊息
   if self.detect_changes(old_status, new_status):
       self.logger.info(f"偵測到變更: {old_status} -> {new_status}")
       self.send_notification(message)
   else:
       self.logger.info("沒有偵測到變更")
   ```

---

## 除錯技巧

### 啟用詳細日誌

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,  # 改為 DEBUG
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### 互動式除錯

```python
# 在程式碼中加入斷點
import pdb; pdb.set_trace()

# 或使用 IPython
import IPython; IPython.embed()
```

### 截圖除錯

```python
# 執行關鍵步驟後截圖
await page.screenshot(path='debug1.png')
await page.click('button')
await page.screenshot(path='debug2.png')
```

---

## 尋求協助

如果問題仍未解決：

1. **檢查日誌檔案**: `logs/monitor.log`
2. **檢查 GitHub Actions 日誌**
3. **查看錯誤截圖**: `logs/screenshots/`
4. **提交 Issue**: 包含錯誤訊息、日誌、環境資訊

---

**版本**: 1.0  
**更新日期**: 2025-10-09  
**維護者**: Dennis Lee

