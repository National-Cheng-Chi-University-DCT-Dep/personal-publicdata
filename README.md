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
---
「遊戲化」激勵引擎 (Gamified Motivation Engine)
申請過程漫長且充滿壓力。這個機制將整個過程變成一場你可以「破關」的遊戲，持續提供正向反饋。

設計機制：

成就與徽章系統：為申請過程中的每一個里程碑設立一個「成就徽章」。例如：

SOP Draft v1.0 (第一版SOP草稿完成徽章)

The Polyglot (雅思總分達到7.0徽章)

First Blood (提交第一份學校申請徽章)

Networker (成功聯繫第一位校友徽章)

進度條視覺化：在你的 dashboard.md 中，建立一個基於你 schools.yml 中 status 欄位的總進度條，讓你清晰地看到從 Not Started 到 Offer Received 的每一步進展。

連擊獎勵 (Streak Bonus)：如果你的 CI/CD 偵測到你連續三天都有 git commit（代表你每天都在推進進度），儀表板上會出現一個「連擊 x3 🔥」的圖標，提供額外的心理激勵。

創意與實用價值：將枯燥的任務轉化為有即時回饋的遊戲，能有效對抗申請疲勞，讓你保持動力。這是一個關注申請者心理健康的創意設計。

2. 跨文件「申請敘事」一致性檢查器 (Cross-Document Narrative Consistency Checker)
確保你的「個人故事」在所有文件中都保持一致且有力，是成敗的關鍵。

設計機制：

核心故事定義：在 profile.yml 中定義你今年的核心申請故事關鍵詞，例如：["成長曲線", "雲端安全架構", "量子計算潛力"]。

LLM 敘事分析：在你的 Pipeline 中增加一個階段，該階段會將你的CV、SOP、以及給推薦人的Brag Sheet 全部提交給一個大型語言模型 (LLM) API。

生成一致性報告：AI 會分析這些文件，並生成一份報告，指出潛在的敘事矛盾或弱點。例如：

[WARNING] CV 強調您在 Twister5 的領導力，但給推薦人的 Brag Sheet 卻更側重於您的獨立開發能力，建議統一敘事角度。

[INSIGHT] 您的 SOP 成功地講述了「成長曲線」的故事，與核心策略一致。

創意與實用價值：這相當於擁有一個7x24小時的 AI 申請顧問，它能從「故事策略」的宏觀角度審視你的所有材料，確保你向學校傳遞的個人品牌形象是統一、清晰且極具說服力的。

3. 動態「風險投資組合」平衡器 (Dynamic "Risk Portfolio" Balancer)
將金融投資組合的風險管理理論，應用於你的選校策略。

設計機制：

定義風險等級：基於你的「預測性錄取機率模型」，將每所學校標記為 Reach (衝刺)、Target (目標)、Safe (保底) 三個等級。

計算投資組合風險：系統會根據你申請清單中各個等級學校的數量和權重，計算出一個總體的「申請投資組合風險分數」。

提供平衡建議：你的儀表板會顯示一個風險儀表盤。如果你的組合過於激進（例如 Reach 學校佔比太高），系統會自動提出建議：「[SUGGESTION] 您的申請組合風險過高 (8.5/10)。建議增加 1-2 所 'Safe' 等級且具備高 ROI 的學校，例如愛爾蘭利默里克大學，以平衡風險。」

創意與實用價值：它讓你跳出單一學校的視角，從全局的、策略性的高度來審視你的申請組合，幫助你做出最穩健、最有可能成功的決策，避免「全軍覆沒」或「錄取結果不滿意」的窘境。

4. 個人檔案「What-If」情境模擬器 (Profile "What-If" Scenario Simulator)
一個互動工具，讓你能量化每一次努力的潛在回報，從而做出更明智的努力方向決策。

設計機制：

互動式輸入：在你的儀表板或一個本地腳本中，建立一個可以讓你輸入假設性變數的介面。

即時重算：當你輸入：「如果我的雅思寫作成績變成 6.5」時，系統會立即使用這個新變數，重新運行你的「預測性錄取機率模型」。

視覺化結果對比：系統會以並排比較的方式，清晰地展示出這個改變將如何影響你申請清單上每一所學校的「預測錄取分數」。例如：「University of Twente: 75/100 → 88/100 (+13)」。

