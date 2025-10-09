# API 整合指南

## 概述

本文檔說明如何整合各種第三方服務的 API，包括 Google Calendar、通知服務等。

---

## Google Calendar API

### 1. 啟用 API

1. 前往 [Google Cloud Console](https://console.cloud.google.com/)
2. 建立新專案或選擇現有專案
3. 啟用 Google Calendar API
4. 前往「憑證」頁面

### 2. 建立 OAuth 2.0 憑證

1. 點擊「建立憑證」→ 「OAuth 用戶端 ID」
2. 選擇應用程式類型：「桌面應用程式」
3. 下載憑證檔案並儲存為 `credentials.json`

### 3. 首次授權

在本地執行授權流程：

```bash
python integrations/calendar_integration.py --setup
```

這會：
- 開啟瀏覽器視窗
- 要求登入 Google 帳號
- 要求授權存取 Calendar
- 生成 `token.pickle` 檔案

### 4. 將憑證存入 GitHub Secrets

```bash
# 將 credentials.json 轉為 base64
cat credentials.json | base64 > credentials_base64.txt

# 將 token.pickle 轉為 base64
cat token.pickle | base64 > token_base64.txt
```

在 GitHub Repository Settings → Secrets 中新增：
- `GOOGLE_CREDENTIALS_JSON`: credentials_base64.txt 的內容
- `GOOGLE_TOKEN_JSON`: token_base64.txt 的內容

### 5. 在 CI/CD 中使用

```yaml
- name: Setup Google Calendar credentials
  run: |
    echo "${{ secrets.GOOGLE_CREDENTIALS_JSON }}" | base64 -d > credentials.json
    echo "${{ secrets.GOOGLE_TOKEN_JSON }}" | base64 -d > token.pickle
```

### 6. API 使用限制

- **每日配額**: 1,000,000 requests
- **每用戶每秒**: 10 requests
- **建議**: 實作 rate limiting，避免超過限制

### 7. 錯誤處理

常見錯誤：
- `401 Unauthorized`: Token 過期，需要重新授權
- `403 Forbidden`: 超過 API 限制
- `429 Too Many Requests`: 請求過於頻繁

---

## 通知服務整合

### Slack Webhook

1. 建立 Incoming Webhook:
   - 前往 [Slack API](https://api.slack.com/messaging/webhooks)
   - 建立新的 Webhook URL
   - 將 URL 存入 GitHub Secrets: `NOTIFICATION_WEBHOOK`

2. 發送通知：

```python
import requests

webhook_url = os.getenv('NOTIFICATION_WEBHOOK')
message = {
    'text': '申請狀態變更通知',
    'attachments': [{
        'color': 'good',
        'fields': [
            {'title': '學校', 'value': '延雪平大學', 'short': True},
            {'title': '狀態', 'value': 'Under Review', 'short': True}
        ]
    }]
}
requests.post(webhook_url, json=message)
```

### Email (SMTP)

1. Gmail App Password:
   - 啟用 2FA
   - 生成應用程式密碼
   - 存入 GitHub Secrets: `EMAIL_PASSWORD`

2. 發送郵件：

```python
import smtplib
from email.mime.text import MIMEText

smtp_server = 'smtp.gmail.com'
smtp_port = 587
from_email = os.getenv('EMAIL_FROM')
password = os.getenv('EMAIL_PASSWORD')

msg = MIMEText('申請狀態變更')
msg['Subject'] = '通知'
msg['From'] = from_email
msg['To'] = 'recipient@example.com'

with smtplib.SMTP(smtp_server, smtp_port) as server:
    server.starttls()
    server.login(from_email, password)
    server.send_message(msg)
```

---

## 匯率 API

### ExchangeRate-API

1. 註冊取得 API Key: https://www.exchangerate-api.com/
2. 存入 GitHub Secrets: `EXCHANGE_RATE_API_KEY`

3. 使用範例：

```python
import requests

api_key = os.getenv('EXCHANGE_RATE_API_KEY')
base_currency = 'TWD'
url = f'https://v6.exchangerate-api.com/v6/{api_key}/latest/{base_currency}'

response = requests.get(url)
rates = response.json()['conversion_rates']

eur_to_twd = 1 / rates['EUR']  # EUR 兌 TWD 匯率
```

---

## 安全性最佳實踐

### 1. 憑證管理

- ✅ 使用 GitHub Secrets 儲存敏感資訊
- ✅ 在本地使用 `.env` 檔案（加入 `.gitignore`）
- ❌ 絕不將憑證 commit 到 Git

### 2. Token 更新

- 實作自動 Token 更新機制
- 當 Token 過期時，自動使用 Refresh Token 更新
- 記錄 Token 過期時間

### 3. Rate Limiting

```python
from datetime import datetime, timedelta
import time

class RateLimiter:
    def __init__(self, max_requests, time_window):
        self.max_requests = max_requests
        self.time_window = time_window  # seconds
        self.requests = []
    
    def allow_request(self):
        now = time.time()
        # 清除過期請求
        self.requests = [t for t in self.requests if now - t < self.time_window]
        
        if len(self.requests) < self.max_requests:
            self.requests.append(now)
            return True
        return False
```

---

## 測試

### 單元測試範例

```python
import pytest
from unittest.mock import Mock, patch

def test_calendar_integration():
    with patch('integrations.calendar_integration.build') as mock_build:
        mock_service = Mock()
        mock_build.return_value = mock_service
        
        # 測試邏輯
        ...
```

---

**版本**: 1.0  
**更新日期**: 2025-10-09

