還需要依據我的條件幫我搜尋適合的碩士課程(如irlts分數/gpa/學術興趣/獎學金條件/學費等)

依樣是爬蟲或api

為現有的 personal-publicdata Repo 增加一個全新的「自動化課程搜尋」模組。該模組將能根據使用者在 my_profile.yml 中定義的個人化條件（如雅思成績、學術興趣、預算），主動爬取並分析各大歐洲碩士課程資料庫，最終篩選出符合條件的課程清單，並自動更新至 source_data/schools.yml。

核心開發指令：
基於以下的功能需求與架構設計，請為我生成一個詳細的專案開發計畫。計畫需包含清晰的 Phases (階段)、Stages (步驟)，以及具體的 TODOs (待辦事項)。

Part 1: 核心功能與架構設計 (New Feature Development)
目標： 開發一個全新的、基於爬蟲與 API 的 discovery/ 模組，專門用於自動化搜尋符合條件的碩士課程。

模組 3.1: 課程搜尋爬蟲 (Course Discovery Scraper)
目標: 開發一系列爬蟲，從各大課程資料庫中抓取碩士課程的詳細資訊。

功能需求:

在 Repo 根目錄下建立新資料夾 discovery/。

在 discovery/ 中建立針對不同平台的爬蟲腳本。

通用要求:

所有爬蟲都應能接受關鍵字 (Keywords, e.g., "Cybersecurity", "Artificial Intelligence", "Quantum Computing") 作為參數。

抓取的資料應包含：program_name, university_name, country, city, tuition_fee, ielts_requirement (包含總分與單項), application_deadline, program_url。

抓取的原始資料應統一存放在 discovery/raw_data/ 目錄下的 JSON 檔案中。

平台 1: Mastersportal.com (主要目標)

腳本名稱: scrape_mastersportal.py

策略: Mastersportal 是一個結構化程度非常高的資料庫。爬蟲需要能夠模擬搜尋和篩選功能，並處理分頁，以抓取所有相關課程的列表與詳細資訊。

平台 2: Study.eu

腳本名稱: scrape_studyeu.py

策略: 與 Mastersportal 類似，專注於其課程搜尋功能。

平台 3: 各國國家級申請平台 (備用/進階)

腳本名稱: scrape_uni_assist.py, scrape_studyinfo_fi.py

策略: 這些平台結構更複雜，可作為進階開發目標，用於交叉驗證或補充資料。

模組 3.2: 智慧篩選與驗證引擎 (Smart Filtering & Validation Engine)
目標: 開發一個腳本，自動將爬取到的原始資料與您的個人條件進行比對，篩選出真正適合您的課程。

功能需求:

在 discovery/ 中建立 filter_and_validate.py 腳本。

核心邏輯:

讀取 my_profile.yml 中的個人條件，包括：

ielts_overall, ielts_writing

academic_interests (e.g., ["Cybersecurity", "AI", "Quantum Computing"])

max_tuition_fee

preferred_countries

遍歷 discovery/raw_data/ 中的所有原始資料。

對每一條課程資料執行驗證規則 (Validation Rules)：

IELTS 驗證: 課程要求的總分 ≤ 您的總分，且課程要求的寫作分數 ≤ 您的寫作分數。

興趣驗證: 課程名稱或描述中，包含您至少一個學術興趣關鍵字。

學費驗證: 課程學費 ≤ 您的預算上限。

產出: 將所有通過驗證的課程，轉換為與 source_data/schools.yml 格式相容的 YAML 結構。

模組 3.3: 自動化資料庫更新與報告 (Automated Database Update & Reporting)
目標: 將篩選出的新機會無縫整合到您現有的申請工作流中。

功能需求:

在 discovery/ 中建立 update_database.py 腳本。

核心邏輯:

讀取 filter_and_validate.py 產出的合格課程清單。

讀取現有的 source_data/schools.yml。

比對兩個清單，找出新發現的課程 (New Opportunities)。

（安全機制）生成拉取請求 (Pull Request): 不要直接 push 到 main 分支。腳本應自動創建一個新的分支，將新發現的課程附加到 schools.yml 文件中，然後自動創建一個 Pull Request。PR 的描述中應包含本次新發現的課程列表。

生成報告: 產出一份名為 discovery_report.md 的報告，總結本次運行發現了多少新課程，並列出它們的詳細資訊。

Part 2: CI/CD 整合 (CI/CD Integration)
目標： 建立一個新的、定時自動運行的 GitHub Actions 工作流，來執行整個課程探索流程。

2.1 新增工作流 (course_discovery.yml)
在 .github/workflows/ 目錄下建立 course_discovery.yml。

觸發方式: 使用 schedule 事件，設定為每週運行一次 (e.g., cron: '0 0 * * 1' for every Monday at midnight)。

工作步驟:

Stage 1: Discover:

運行 discovery/scrape_mastersportal.py。

運行 discovery/scrape_studyeu.py。

Stage 2: Filter:

運行 discovery/filter_and_validate.py。

Stage 3: Report & Update:

運行 discovery/update_database.py。

如果發現新課程，工作流將會創建一個新的 PR 等待您的審核。

Stage 4: Notify:

無論是否發現新課程，都將 discovery_report.md 的內容，透過您的通知系統（Discord/Slack/Email）發送給您。
