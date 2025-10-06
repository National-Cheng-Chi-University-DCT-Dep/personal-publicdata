專案目標：打造「碩士申請情報與自動化中心 (MApp-IAC)」
一個基於 CI/CD 的自動化平台，旨在將碩士申請流程從重複的手動勞動，轉變為一個數據驅動、可監控、具備策略輔助能力的工程專案。

第一階段 (Phase 1): 核心自動化基礎 (Core Automation Foundation - MVP)
目標：建立一個能自動蒐集、驗證關鍵資訊，並生成客製化申請文件的 CI/CD 工作流。

TODO-1: 建立專案 Repo 結構
[ ] 初始化 GitHub Repo (personal-publicdata)。

[ ] 建立核心目錄結構：

/.harness/ (用於 Harness Pipeline 設定)

/source_data/ (用於存放原始資料)

/data_collection/ (用於存放爬蟲與驗證腳本)

/templates/ (用於存放申請文件範本)

/final_applications/ (用於存放最終產出的 PDF 文件)

/build_scripts/ (用於文件生成腳本)

TODO-2: 實作資料蒐集模組 (Web Scraper)
[ ] 在 /data_collection/ 中建立 scraper.py。

[ ] 使用 BeautifulSoup 或 Scrapy 函式庫。

[ ] 核心功能：

[ ] 讀取 /source_data/schools.yml 中的學校網址。

[ ] 爬取：學費 (Tuition Fees)、語言要求 (IELTS)、申請截止日期 (Deadlines)。

[ ] 將抓取的資料寫入 /source_data/schools_live_data.yml。

[ ] 進階功能 (Scraper v2)：

[ ] 實作 DOM 結構變動偵測，當網站改版時自動發出警報。

[ ] 實作多來源交叉驗證，確保數據準確性。

[ ] (選配) 整合 Playwright 進行視覺化回歸測試與 OCR 備援。

TODO-3: 實作資料驗證模組 (Validator)
[ ] 在 /data_collection/ 中建立 validator.py。

[ ] 核心功能：

[ ] 讀取 /source_data/schools_live_data.yml。

[ ] Schema 驗證：檢查必要欄位是否存在。

[ ] 規則驗證：自動比對你的個人標準 (雅思成績、預算)，並標記結果。

[ ] 進階功能 (Validator v2)：

[ ] 整合 NLP 進行先修課程自動比對，生成初步的符合性報告。

[ ] 產出：生成一份 /final_applications/validation_report.md。

TODO-4: 建立文件生成與 CI/CD Pipeline
[ ] 在 /build_scripts/ 中建立 generate_docs.py，用於合併範本與資料。

[ ] 在 /.harness/ 中建立 application_pipeline.yml。

[ ] Pipeline 流程：

觸發 (Trigger)：當 /source_data/ 有更新時觸發。

階段 1 (Collect)：運行 scraper.py。

階段 2 (Validate)：運行 validator.py。若驗證失敗則 Pipeline 終止並通知。

階段 3 (Generate)：運行 generate_docs.py，生成 Markdown 文件。

階段 4 (Convert)：將 Markdown 轉換為 PDF。

產物儲存：將最終的 PDF 文件歸檔。

第二階段 (Phase 2): 打造申請指揮中心 (Command & Control Center)
目標：增加監控、任務管理與通知功能，讓系統具備主動性。

TODO-5: 建立監控儀表板 (Dashboard)
[ ] 在 schools.yml 中增加 status 欄位。

[ ] 修改 generate_docs.py，增加生成 dashboard.md 的功能。

[ ] 儀表板內容：整合 schools_live_data.yml 和 schools.yml 的數據，包含：申請狀態、截止日期、雅思符合性、預估總花費、預測錄取分數等。

TODO-6: 整合智慧化任務管理 (Task Management)
[ ] 研究並設定 GitHub API 的 Personal Access Token。

[ ] 修改 validator.py，當發現不符合的項目時（例如雅思不達標），自動調用 GitHub API 創建 Issue。

TODO-7: 建立警報系統 (Alerting System)
[ ] 在 Harness 中建立一個新的、排程觸發 (Scheduled Trigger) 的 Pipeline。

[ ] 該 Pipeline 運行一個簡單的 Python 腳本，檢查 schools_live_data.yml 中的截止日期。

[ ] 設定 Harness 的通知機制 (Slack/Discord/Email)，在截止日期將近時自動發送警報。

第三階段 (Phase 3): 升級為策略中心 (Strategy & Intelligence Hub)
目標：引入 AI 與進階分析，讓系統提供決策輔助與策略洞察。

TODO-8: 實作預測性分析與 AI 輔助功能
[ ] 預測性錄取機率模型：

[ ] 建立 profile.yml 存放你的個人數據向量。

[ ] 擴充 scraper.py 以抓取能反映學校偏好的特徵。

[ ] 建立一個 scoring_engine.py，根據啟發式規則計算預測錄取分數。

[ ] SOP 語意相似度分析：

[ ] 擴充 scraper.py 以抓取課程介紹、教授簡介等長篇文本。

[ ] 在 Pipeline 中整合 NLP 模型 (如 Sentence-BERT)，計算 SOP 與學校語料庫的相似度分數。

[ ] AI 校對整合：

[ ] 在 Pipeline 的 Generate 和 Convert 階段之間，增加一個 Proofread 步驟。

[ ] 該步驟調用 LLM API，對生成的 Markdown 文件進行文法與風格檢查。

TODO-9: 開發進階情報模組 (Advanced Intelligence Modules)
[ ] 學術雷達 (Academic Radar)：

[ ] 擴充 scraper.py 以監控目標教授的 Google Scholar 和系所 GitHub Repo。

[ ] 建立警報機制，在新論文發表或 GitHub 有新動態時通知你。

[ ] 學生體驗分析儀 (Student Experience Analyzer)：

[ ] 擴充 scraper.py 以爬取 Reddit, Grad Cafe 等論壇的學生評論。

[ ] 整合 NLP 情感分析與主題模型，生成「學生聲量報告」。

[ ] 職涯雷達 (Career Radar)：

[ ] 建立一個新的爬蟲，定向抓取目標城市與職位的技能需求。

[ ] 分析並生成「市場需求技能矩陣」，為你的選課提供數據支持。

TODO-10: 建立模擬與復盤機制
[ ] 「影子」申請 E2E 測試：

[ ] 使用 Playwright 為 1-2 個關鍵學校編寫瀏覽器自動化腳本，模擬文件上傳流程。

[ ] 申請後復盤系統：

[ ] 在 schools.yml 中增加申請後結果的欄位。

[ ] 建立一個 post_mortem.py 腳本，在申請季結束後，生成年度分析報告。