 ->將現有的碩士申請管理系統，升級為一個具備主動情報蒐集（爬蟲）與進階管理功能的自動化平台。當前衝刺目標 (Sprint Goal) 是完成對瑞典 2026 年秋季入學碩士的申請流程管理，並開發一系列新的自動化監控模組。

核心開發指令：
基於以下的功能需求與行動計畫，請為我生成一個詳細的專案開發計畫。計畫需包含清晰的 Phases (階段)、Stages (步驟)，以及具體的 TODOs (待辦事項)。

cicd pipeline 需要github actionh 跟 harness(.harness folder中新增)兩個方法
---
Part 1: 新功能開發需求 (New Feature Development)
目標： 開發一系列新的自動化模組，以擴充現有 personal-publicdata Repo 的功能，專注於爬蟲與外部服務整合。

模組 2.1: 申請平台監控系統 (Application Monitoring System)
目標: 自動化監控所有申請平台的「開放申請狀態」與提交後的「個人申請進度」。
---
申請平台list
德國 | Uni-Assist (uni-assist.de)

說明：這是最重要的德國國際學生申請服務平台。許多德國大學（特別是傳統大學 "Universität" 和應用科學大學 "Hochschule"）都要求非歐盟國家的學生，必須先透過 Uni-Assist 提交學歷文件，由他們進行德國學制下的資格預審（稱為VPD）。

策略意涵：如果您要申請的德國學校使用此系統，Uni-Assist 的流程必須提早啟動，因為文件審核需要數週時間。拿到VPD後，您才能在大學自己的系統上完成最終申請。這是一個需要納入您 application_dashboard.md 時程管理的關鍵前置步驟。

芬蘭 | Studyinfo.fi

說明：這是芬蘭全國統一的教育申請入口網站，所有芬蘭的大學碩士申請都必須透過這個平台。

策略意涵：與瑞典的系統類似，申請時程統一（通常在每年1月初），您可以一次管理所有芬蘭學校的申請。

挪威 | Søknadsweb (fsweb.no)

說明：這是挪威大多數大學使用的全國性申請系統。如果您考慮挪威的學校，這將是您的主要申請平台。

荷蘭 | Studielink (studielink.nl)

說明：這是荷蘭全國統一的學生註冊系統。無論您是透過哪個平台申請荷蘭的學校，最終通常都需要在 Studielink 註冊一個帳號來完成正式的入學註冊。

策略意涵：您可以將其視為申請荷蘭學校的「最後一哩路」，需要預先了解其註冊流程。

apply.cs.uni-saarland.de

estonia.dreamapply.com

---
功能需求:

Pre-Application Monitor (申請開放監控):

開發一個爬蟲 (check_opening_status.py)，定期檢查 schools.yml 中各校的申請頁面 (application_url)。

監測 "Apply Now" 按鈕的出現、申請日期的公布等關鍵字/HTML模式變化。

當狀態變更時（如從 "Not Open" 變為 "Open",可能包含更多字眼或是變數），觸發通知。

Post-Application Monitor (個人進度監控):

為每個需要登入的平台開發獨立的爬蟲腳本，存放於 monitoring/ 目錄下。

通用要求: 使用 Playwright 處理登入驗證，帳號密碼從 GitHub Secrets 讀取。腳本需能自動導航至「我的申請」頁面，抓取申請狀態，並在狀態變更時觸發通知。

平台 1: Universityadmissions.se (瑞典)

腳本名稱: check_status_sweden.py

目標元素: 分析登入後頁面的 HTML 結構，定位到申請狀態的 class 或 id。

平台 2: estonia.dreamapply.com (愛沙尼亞/通用)

腳本名稱: check_status_dreamapply.py

策略: 優先探索背後有無 API (XHR/Fetch 請求)，若無則 fallback 至爬取 HTML。

平台 3: apply.cs.uni-saarland.de (薩爾蘭大學)

腳本名稱: check_status_saarland.py

策略: 針對該校獨立系統，客製化登入與抓取邏輯。

模組 2.2: Google Calendar 整合 (Google Calendar Integration)
目標: 將重要的截止日期自動同步到個人 Google Calendar。

功能需求:

開發一個 calendar_integration.py 腳本，使用 Google Calendar API。

腳本讀取 schools.yml 中的 deadline 欄位。

自動在 Google Calendar 上創建名為 [Deadline] Submit Application for [School Name] 的活動。

為活動設定提前一週和提前三天的自動提醒。

整合至 Google Calendar (絕對可行！)
將您的監控系統與 Google Calendar 整合，是一個天才般的想法，技術上完全可行，並且能完美地融入您現有的 Python 自動化工作流中。

這相當於為您的「申請情報中心」增加了一個強大的主動通知與行程管理功能。

實作方法：
整合的核心是使用 Google Calendar API。您的 Python 腳本可以透過這個 API，自動在您的日曆上新增、修改或刪除事件。

以下是您可以如何將它實作到您的專案中的步驟：

啟用 API 與取得憑證：

您需要在 Google Cloud Console 建立一個專案，並為該專案啟用 Google Calendar API。

設定 OAuth 2.0 同意畫面，並下載您的憑證檔案 (credentials.json)。將這個檔案安全地存放在您的專案中（並加入 .gitignore）。

安裝必要的 Python 函式庫：

在您的 build_scripts/requirements.txt 中，加入 Google API 的 Python 客戶端函式庫：

google-api-python-client
google-auth-httplib2
google-auth-oauthlib
編寫整合腳本：

您可以修改您現有的 notifications/alert_system.py 腳本，或建立一個新的 calendar_integration.py。

首次授權：第一次運行腳本時，它會自動打開一個瀏覽器視窗，要求您登入 Google 帳號並授權。成功後，它會在本機生成一個 token.json (或 token.pickle) 檔案，用於後續的自動驗證。您需要將這個 token 檔案的內容，同樣安全地存到 GitHub Secrets 中。

核心功能：腳本的主要功能是讀取您的 schools.yml，然後針對每個學校的 deadline，在您的 Google Calendar 上建立一個活動 (Event)。您可以設定活動的標題（例如 [Deadline] Submit Application for TalTech）、日期，甚至設定多個提醒（例如，提前一週、提前三天）。

整合至 CI/CD 工作流：

在您的 status_monitor.yml 或 application_pipeline.yml 工作流中，增加一個新的階段 (Stage)。

這個階段會執行您的 calendar_integration.py 腳本。

工作流需要從 GitHub Secrets 中讀取 credentials.json 和 token.json 的內容，並將它們寫入到虛擬機的檔案系統中，這樣您的 Python 腳本才能成功驗證。

透過這個整合，您的自動化系統將不再只是被動地檢查狀態，而是能主動地管理您的行程，確保您絕不會錯過任何一個重要的截止日期。

---

模組 2.3: 推薦信追蹤系統 (Recommendation Tracker)
目標: 透明化管理推薦信的請求與提交狀態。

功能需求:

擴充 recommenders.yml，增加 status 欄位來追蹤每所學校的推薦信狀態。

開發 recommendation_tracker.py，在 application_dashboard.md 中生成「推薦信狀態總覽」表格。

進階功能: 自動生成禮貌性的提醒郵件草稿。

模組 2.4: 簽證與移民資訊雷達 (Visa & Immigration Radar)
目標: 在獲得錄取後，自動監控簽證資訊的變動與預約名額。

功能需求:

建立 visa_requirements.yml 存儲目標國家的簽證資訊網址。

開發 visa_monitor.py，定期爬取各國在台辦事處官網，監控簽證規定頁面是否有更新（透過 hash 值變化偵測）。

進階功能: 使用 Playwright 定期檢查簽證預約系統，監控是否有新的預約名額釋出，並在有名額時立即發出警報。

模組 2.5: 財務規劃儀表板 (Finance & Budget Dashboard)
目標: 提供數據驅動的財務決策支持。

功能需求:

擴充 schools.yml，增加 application_fee, estimated_living_cost 欄位。

開發 budget_analyzer.py，在 application_dashboard.md 中生成「財務規劃總覽」，包含總申請成本、各校年度總花費比較（轉換為 TWD）等。

Part 2: 瑞典申請衝刺行動計畫 (Sprint Goal: Swedish Applications)
目標： 在 2025年10月16日至2026年1月15日 的申請期間內，完成所有瑞典目標學校的申請。

2.1 目標申請清單
第一梯隊 (首要目標):

延雪平大學 - M.Sc. in Cybersecurity

舍夫德大學 - M.Sc. in Privacy, Information and Cybersecurity

西部大學 - M.Sc. in Cybersecurity (60 Credits)

第二梯隊 (潛力選項):
4.  哥德堡大學 - M.Sc. in Computer Science
5.  呂勒奧理工大學 - M.Sc. in Applied AI / Cybersecurity

第三梯隊 (特殊挑戰):
6.  隆德大學 - M.Sc. in Physics, Quantum Science and Technology

2.2 核心產出文件
Master CV: 準備一份學術導向的履歷。

Master SOP (通用範本): 準備一份適用於第一、二梯隊的 SOP。

SOP Variant - Quantum Focus: 準備一份專為隆德大學客製化的高學術性 SOP。