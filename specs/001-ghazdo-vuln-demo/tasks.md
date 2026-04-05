# 任務：GHAzDO 漏洞偵測展示範例

**輸入**：來自 `/specs/001-ghazdo-vuln-demo/` 的設計文件
**先決條件**：plan.md（技術堆疊、專案結構）、spec.md（4 個使用者故事）、research.md（CodeQL 查詢、CVE 套件、Secret 模式、Pipeline YAML）、data-model.md（實體實例）、contracts/flask-endpoints.md（7 端點）

**測試**：規格中未要求測試（「不適用」），因此不生成測試任務。

**組織方式**：任務依使用者故事分組，以便每個故事可獨立實作與測試。

## 格式：`[ID] [P?] [Story] 描述`

- **[P]**：可平行執行（不同檔案、無相依性）
- **[Story]**：此任務所屬的使用者故事（US1、US2、US3、US4）
- 描述中包含確切的檔案路徑

## 路徑慣例

- **單一專案**：`src/` 位於儲存庫根目錄（依 plan.md 結構）

---

## 階段 1：設置（共用基礎建設）

**目的**：專案初始化、目錄結構建立、相依套件安裝

- [ ] T001 根據 plan.md 專案結構建立目錄：`src/`、`src/vulnerabilities/`、`config/`
- [ ] T001a [P] 建立 .gitignore — 排除 `.venv/`、`__pycache__/`、`*.db`、`*.pyc`、`.env`（確保 GHAzDO 掃描不受虛擬環境和暫存檔干擾，同時保留 `.env.example` 在版控中供 Secret Scanning 偵測）
- [ ] T002 建立 pyproject.toml：專案名稱 `ghazdo-vuln-demo`、Python `>=3.11`、相依套件包含 `flask`、`requests`（供 SSRF 端點使用），以及 4 個有漏洞的套件版本鎖定：`PyYAML==5.3.1`（CVE-2020-14343, Critical）、`Pillow==9.5.0`（CVE-2023-50447, High）、`urllib3==1.26.4`（CVE-2021-33503, High）、`Jinja2==3.1.2`（CVE-2024-22195, Medium）；每個有漏洞套件旁加 CVE 註解
- [ ] T003 執行 `uv sync` 建立虛擬環境並驗證所有套件安裝成功；若 Jinja2==3.1.2 與 Flask 版本衝突，改用 `requests==2.25.1`（CVE-2023-32681）作為替代（依 research.md 備註）

---

## 階段 2：基礎建設（阻擋性先決條件）

**目的**：建立所有使用者故事共用的核心模組：Flask 應用骨架、SQLite 資料庫、套件初始化

**⚠️ 重要**：此階段完成前不可開始任何使用者故事工作

- [ ] T004 [P] 建立 src/__init__.py — 空的套件初始化檔案
- [ ] T005 [P] 建立 src/vulnerabilities/__init__.py — 空的套件初始化檔案
- [ ] T006 建立 src/database.py — 使用 Python 內建 `sqlite3` 模組初始化 SQLite 資料庫（記憶體模式或檔案模式）；建立 `users` 資料表（`id INTEGER PRIMARY KEY`, `name TEXT`, `email TEXT`）並插入 3-5 筆範例資料；提供 `get_db_connection()` 函式供 SQL Injection 端點使用
- [ ] T007 建立 src/app.py — Flask 應用入口：建立 Flask app 實例、定義 GET `/` 首頁路由（HTML 頁面列出所有漏洞端點及說明）、預留 Blueprint 註冊區段（Phase 3 填入）；使用 `if __name__ == "__main__"` 啟動 `app.run(debug=True)`，並支援 `python -m src.app` 執行

**檢查點**：基礎建設就緒 — `uv run python -m src.app` 可啟動空的 Flask 應用並顯示首頁

---

## 階段 3：使用者故事 1 — 程式碼掃描漏洞展示（優先順序：P1）🎯 最小可行產品 (MVP)

**目標**：實作 6 種 CodeQL 高信心漏洞端點，推送後 GHAzDO Code Scanning 可偵測每種漏洞至少一條警告

**獨立測試**：推送至啟用 GHAzDO Code Scanning 的 Azure DevOps repo 後，Advanced Security → Code Scanning 頁面應顯示 6 條以上警告，對應 `py/sql-injection`、`py/command-line-injection`、`py/path-injection`、`py/full-ssrf`、`py/reflective-xss`、`py/unsafe-deserialization`

### 使用者故事 1 的實作

- [ ] T008 [P] [US1] 在 src/vulnerabilities/sql_injection.py 實作 SQL Injection 端點 — 建立 Flask Blueprint `sql_injection_bp`；GET `/api/users` 接收 query 參數 `name`，將其直接以 f-string 串接至 SQL 查詢 `f"SELECT * FROM users WHERE name = '{name}'"` 並透過 `database.get_db_connection()` 執行；回傳 JSON `{"users": [...]}`；檔案頂部加 `# 漏洞：SQL Injection (CWE-89) — py/sql-injection` 註解
- [ ] T009 [P] [US1] 在 src/vulnerabilities/command_injection.py 實作 Command Injection 端點 — 建立 Flask Blueprint `command_injection_bp`；GET `/api/ping` 接收 query 參數 `host`，將其直接傳入 `os.system(f"ping -c 1 {host}")`（或 `subprocess.call(f"ping -c 1 {host}", shell=True)`）；回傳 JSON `{"result": output}`；檔案頂部加 `# 漏洞：OS Command Injection (CWE-78) — py/command-line-injection` 註解
- [ ] T010 [P] [US1] 在 src/vulnerabilities/path_traversal.py 實作 Path Traversal 端點 — 建立 Flask Blueprint `path_traversal_bp`；GET `/api/files` 接收 query 參數 `filename`，直接以 `open(filename, "r")` 讀取檔案內容而不驗證路徑；回傳 text/plain 檔案內容；檔案頂部加 `# 漏洞：Path Traversal (CWE-22) — py/path-injection` 註解
- [ ] T011 [P] [US1] 在 src/vulnerabilities/ssrf.py 實作 SSRF 端點 — 建立 Flask Blueprint `ssrf_bp`；GET `/api/fetch` 接收 query 參數 `url`，直接傳入 `requests.get(url)` 而不驗證目標位址；回傳 JSON `{"status_code": int, "content": str}`；檔案頂部加 `# 漏洞：Server-Side Request Forgery (CWE-918) — py/full-ssrf` 註解
- [ ] T012 [P] [US1] 在 src/vulnerabilities/xss.py 實作 Reflected XSS 端點 — 建立 Flask Blueprint `xss_bp`；GET `/api/search` 接收 query 參數 `q`，使用 `flask.make_response()` 回傳 HTML 字串 `f"<h1>搜尋結果：{q}</h1>"` 而不進行輸出編碼；設定 Content-Type 為 text/html；檔案頂部加 `# 漏洞：Reflected XSS (CWE-79) — py/reflective-xss` 註解
- [ ] T013 [P] [US1] 在 src/vulnerabilities/insecure_deserialization.py 實作 Insecure Deserialization 端點 — 建立 Flask Blueprint `deserialization_bp`；POST `/api/import` 從 request body 接收 base64 編碼的資料，使用 `pickle.loads(base64.b64decode(data))` 反序列化而不驗證來源；回傳 JSON `{"imported": repr(obj)}`；檔案頂部加 `# 漏洞：Insecure Deserialization (CWE-502) — py/unsafe-deserialization` 註解
- [ ] T014 [US1] 更新 src/app.py — 匯入並註冊全部 6 個漏洞 Blueprint（`sql_injection_bp`、`command_injection_bp`、`path_traversal_bp`、`ssrf_bp`、`xss_bp`、`deserialization_bp`）；更新 GET `/` 首頁列出全部 7 個端點（含路由、漏洞類型、CWE 編號和簡短說明）

**檢查點**：`uv run python -m src.app` 可啟動 Flask 應用，存取每個端點回傳預期格式的回應；6 個漏洞模組各觸發對應的 CodeQL 查詢

---

## 階段 4：使用者故事 2 — 機密資訊掃描展示（優先順序：P1）

**目標**：在 3 個不同類型的檔案中嵌入 3 種看似真實的假機密，推送後 GHAzDO Secret Scanning 偵測全部 3 條警告

**獨立測試**：推送至啟用 GHAzDO Secret Protection 的 Azure DevOps repo 後，Advanced Security → Secret Scanning 頁面應顯示 3 條警告：`azure_active_directory_application_secret`、`github_personal_access_token`、`postgres_connection_string`

### 使用者故事 2 的實作

- [ ] T015 [P] [US2] 建立 src/config.py — 應用設定模組；嵌入 Azure Service Principal Client Secret 作為變數賦值：`AZURE_CLIENT_SECRET = "wJa..."`（40 字元 Base64 類字串，格式符合 `azure_active_directory_application_secret` 偵測模式）；同時包含 `AZURE_TENANT_ID` 和 `AZURE_CLIENT_ID` 等設定值以呈現真實場景；檔案頂部加註解說明這是刻意嵌入的假機密
- [ ] T016 [P] [US2] 建立 config/settings.yaml — 應用設定檔；嵌入 GitHub Personal Access Token：`github_token: "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"`（`ghp_` 前綴 + 36 個英數字元，格式符合 `github_personal_access_token` 偵測模式）；同時包含其他合理的設定項目（如 app name、log level）以呈現真實設定檔
- [ ] T017 [P] [US2] 建立 .env.example — 環境變數範本；嵌入 PostgreSQL 連線字串：`DATABASE_URL=postgresql://admin:SuperSecret123!@db.example.com:5432/production`（格式符合 `postgres_connection_string` 偵測模式）；同時包含其他環境變數（如 `FLASK_ENV`、`SECRET_KEY`）以呈現真實的 .env 範本

**檢查點**：3 個檔案中各包含 1 個格式正確的假機密，`git diff` 可確認機密字串存在於版控中

---

## 階段 5：使用者故事 3 — 相依套件漏洞掃描展示（優先順序：P2）

**目標**：確保 pyproject.toml 中的 4 個有漏洞套件被 GHAzDO Dependency Scanning 偵測，並建立觸發掃描的 Azure Pipelines YAML

**獨立測試**：推送至已啟用 GHAzDO Code Security 的 Azure DevOps repo 並執行 Pipeline 後，Advanced Security → Dependency Scanning 頁面應顯示至少 4 條 CVE 警告

### 使用者故事 3 的實作

- [ ] T018 [US3] 驗證並完善 pyproject.toml 中的相依套件設定 — 確認 4 個有漏洞套件版本鎖定正確（PyYAML==5.3.1、Pillow==9.5.0、urllib3==1.26.4、Jinja2==3.1.2）；執行 `uv sync` 確認無版本衝突；如有 Jinja2/Flask 衝突則套用 research.md 備註方案將 Jinja2 替換為 `requests==2.25.1`（CVE-2023-32681）
- [ ] T019 [US3] 建立 azure-pipelines.yml — 依 research.md §4 的官方範本：`trigger: [main]`；`pool: vmImage: ubuntu-latest`；三個 steps：`AdvancedSecurity-Codeql-Init@1`（inputs: `languages: "python"`, `enableAutomaticCodeQLInstall: true`）、`AdvancedSecurity-Dependency-Scanning@1`（無額外 inputs）、`AdvancedSecurity-Codeql-Analyze@1`（無額外 inputs）；加入 YAML 註解說明每個 task 對應的 GHAzDO 功能

**檢查點**：`azure-pipelines.yml` 語法正確，pyproject.toml 中的 4 個有漏洞套件可安裝

---

## 階段 6：使用者故事 4 — 漏洞修復與驗證循環展示（優先順序：P2）

**目標**：在 README.md 中提供修復循環的展示指南，讓展示者能根據 GHAzDO 掃描結果即時修復漏洞並驗證

**獨立測試**：按 README 修復指南修復 SQL Injection（改用參數化查詢），重新推送後對應的 CodeQL 警告在下次掃描中標記為 Fixed

### 使用者故事 4 的實作

- [ ] T020 [US4] 撰寫修復循環展示指南段落 — 內容包含：(1) 如何在 GHAzDO Advanced Security 頁面選擇 SQL Injection 警告、(2) 閱讀 GHAzDO 提供的漏洞描述和修復建議、(3) 將 `f"SELECT * FROM users WHERE name = '{name}'"` 改為參數化查詢 `"SELECT * FROM users WHERE name = ?"` 搭配 `(name,)` 參數、(4) `git commit -m "fix(security): 修復 SQL Injection 漏洞" && git push`、(5) 等待 Pipeline 重新掃描並驗證警告消失；此段落將於 Phase 7 整合至 README.md

**檢查點**：修復指南段落內容完整，包含具體的程式碼修改範例和 git 操作步驟

---

## 階段 7：收尾與跨切面關注點

**目的**：建立面向混合觀眾的 README、驗證整體專案可運行

- [ ] T021 建立 README.md — 整合以下內容：(1) 專案概述（目的：展示 GHAzDO 三大功能）、(2) 目錄結構說明（依 plan.md 專案結構）、(3) 快速入門指南（依 quickstart.md：先決條件、本地設定 `uv sync`、`uv run python -m src.app`）、(4) Azure DevOps 設定指南（依 quickstart.md：啟用 Secret Protection + Code Security、設定 Pipeline）、(5) 預期掃描結果摘要表（6 條 Code Scanning + 3 條 Secret Scanning + 4 條 Dependency Scanning）、(6) 修復循環展示指南（整合 T020 內容）、(7) 價值摘要表格（依 quickstart.md：面向管理層的三大功能風險與價值對照）
- [ ] T022 驗證 `uv run python -m src.app` 可啟動 Flask 應用且無 ImportError 或 SyntaxError — 存取 GET `/` 確認首頁列出全部 7 個端點；存取各端點確認回傳預期格式的回應
- [ ] T023 執行 quickstart.md 驗證流程 — 從乾淨目錄模擬：`git clone` → `uv sync` → `uv run python -m src.app`，確認所有步驟可正常執行且無遺漏

---

## 相依性與執行順序

### 階段相依性

- **設置（階段 1）**：無相依性 — 可立即開始
- **基礎建設（階段 2）**：相依於階段 1 完成（T001-T003）— 阻擋所有使用者故事
- **US1（階段 3）**：相依於階段 2 完成（需要 database.py、app.py）
- **US2（階段 4）**：相依於階段 2 完成（需要專案結構和 src/ 套件）— 可與 US1 **平行**
- **US3（階段 5）**：相依於階段 1 完成（需要 pyproject.toml）— 可與 US1、US2 **平行**
- **US4（階段 6）**：相依於 US1 完成（修復指南引用 SQL Injection 端點程式碼）
- **收尾（階段 7）**：相依於所有使用者故事完成

### 使用者故事相依性

```text
階段 1：設置
  │
  ├──────────────────────────────────────┐
  ▼                                      ▼
階段 2：基礎建設                       階段 5：US3 (P2)
  │                                    Dependency Scanning
  ├──────────────────┐                   │
  ▼                  ▼                   │
階段 3：US1 (P1)   階段 4：US2 (P1)    │
Code Scanning      Secret Scanning      │
  │                  │                   │
  ├──────────────────┤                   │
  ▼                  │                   │
階段 6：US4 (P2)    │                   │
Fix Cycle           │                   │
  │                  │                   │
  ├──────────────────┴───────────────────┘
  ▼
階段 7：收尾
```

- **US1（P1）**：可在基礎建設後開始 — 不相依於其他故事
- **US2（P1）**：可在基礎建設後開始 — 與 US1 無檔案衝突，可**完全平行**
- **US3（P2）**：可在設置後開始（T018 操作 pyproject.toml、T019 新建檔案）— 可與 US1/US2 **平行**
- **US4（P2）**：相依於 US1 完成（需引用 SQL Injection 端點程式碼）

### 每個使用者故事內部

- US1：T008-T013 可全部平行（6 個獨立檔案），T014 最後執行（需匯入全部 Blueprint）
- US2：T015-T017 可全部平行（3 個獨立檔案）
- US3：T018 先於 T019（需先確認套件無衝突）
- US4：僅 T020 一個任務

### 平行執行機會

- 階段 2 中 T004、T005 可平行
- 階段 2 完成後，US1（階段 3）、US2（階段 4）、US3（階段 5）可同時啟動
- US1 中 T008-T013 全部可平行（6 個獨立漏洞模組）
- US2 中 T015-T017 全部可平行（3 個獨立檔案）

---

## 平行執行範例：使用者故事 1

```bash
# 階段 2 完成後，同時啟動全部 6 個漏洞模組：
Task: T008 — 在 src/vulnerabilities/sql_injection.py 實作 SQL Injection 端點
Task: T009 — 在 src/vulnerabilities/command_injection.py 實作 Command Injection 端點
Task: T010 — 在 src/vulnerabilities/path_traversal.py 實作 Path Traversal 端點
Task: T011 — 在 src/vulnerabilities/ssrf.py 實作 SSRF 端點
Task: T012 — 在 src/vulnerabilities/xss.py 實作 XSS 端點
Task: T013 — 在 src/vulnerabilities/insecure_deserialization.py 實作 Insecure Deserialization 端點

# 全部完成後執行：
Task: T014 — 更新 src/app.py 註冊全部 Blueprint
```

## 平行執行範例：跨使用者故事

```bash
# 階段 2 完成後，3 個故事可同時啟動：
開發者 A → US1：T008-T014（Code Scanning 漏洞端點）
開發者 B → US2：T015-T017（Secret Scanning 機密檔案）
開發者 C → US3：T018-T019（Dependency Scanning Pipeline）

# US1 完成後：
開發者 A → US4：T020（修復循環指南）

# 全部完成後：
全體 → 階段 7：T021-T023（README + 驗證）
```

---

## 實作策略

### 最小可行產品 (MVP) 優先（僅使用者故事 1）

1. 完成階段 1：設置（T001-T003）
2. 完成階段 2：基礎建設（T004-T007）
3. 完成階段 3：使用者故事 1 — Code Scanning（T008-T014）
4. **停止並驗證**：`uv run python -m src.app` 啟動，6 個端點可存取
5. 推送至 Azure DevOps → 驗證 CodeQL 警告
6. 準備就緒則可初步展示 Code Scanning 功能

### 漸進式交付

1. 設置 + 基礎建設 → 專案骨架就緒
2. 新增 US1（Code Scanning）→ 推送 → 驗證 6 條警告 — **MVP！**
3. 新增 US2（Secret Scanning）→ 推送 → 驗證 3 條警告
4. 新增 US3（Pipeline + Dependency Scanning）→ 推送 → 驗證 4 條 CVE 警告
5. 新增 US4（修復循環指南）→ 現場展示修復流程
6. 每個故事增加展示價值而不破壞先前的故事

### 單人開發策略（推薦）

由於此為展示專案、單人開發：

1. 循序完成：階段 1 → 階段 2 → 階段 3 → 階段 4 → 階段 5 → 階段 6 → 階段 7
2. 每完成一個階段提交一次（`git commit`）
3. US1 中的 6 個模組可批量實作，最後統一註冊

---

## 備註

- [P] 任務 = 不同檔案、無相依性，可平行執行
- [Story] 標籤將任務對應至特定使用者故事以便追溯
- 每個使用者故事應可獨立完成並測試
- 每個任務或邏輯群組後提交
- 在任何檢查點停止以獨立驗證故事
- 所有機密為「看似真實但不具實際危害」的假值 — 不可使用真實憑證
- 避免：模糊的任務、同一檔案衝突、破壞獨立性的跨故事相依性
