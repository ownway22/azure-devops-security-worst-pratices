# 🔍 GHAzDO 漏洞偵測展示範例

> ⚠️ **免責聲明**：本專案包含**刻意植入的程式碼安全漏洞與假金鑰**，僅用於展示 GitHub Advanced Security for Azure DevOps（GHAzDO）的偵測能力。**請勿將任何程式碼使用於生產環境。**

---

## 這個專案是什麼？

本專案是一個 Python（Flask）展示應用程式，帶你親眼見證 GHAzDO 的三大掃描功能如何在 Azure DevOps Pipeline 自動偵測安全問題：

| 功能 | 偵測目標 | 預期警告數 |
|------|----------|------------|
| **Code Scanning**（程式碼掃描）| 6 種 CodeQL 高信心漏洞 | ≥ 6 條 |
| **Secret Scanning**（金鑰掃描）| 5 種格式正確的假金鑰 | 5 條 |
| **Dependency Scanning**（相依套件掃描）| 3 個含 CVE 的有漏洞套件版本 | ≥ 3 條 |

---

## 📁 目錄結構

```text
.
├── azure-pipelines.yml                      # 主要 Pipeline（完整掃描）
├── azure-pipelines-high-severity-only.yml   # 對照 Pipeline（僅掃描 High/Critical）
├── azure-pipelines-coverage.yml             # PR Diff 覆蓋率設定
├── pyproject.toml                           # 相依套件定義（含 3 個有漏洞版本）
├── requirements.txt                         # 鎖定版本的相依套件清單（供 Dependency Scanning 掃描用，刻意保留有漏洞版本）
├── config/
│   └── settings.yaml                        # 含假金鑰（Secret #2, #5）
├── output/                                  # Azure Pipeline 掃描結果範例
│   ├── *.sarif                              # CodeQL SARIF 格式掃描輸出
│   └── ghas_results.json                    # GHAS 完整掃描結果（JSON）
└── src/
    ├── app.py                               # Flask 入口 + 路由
    ├── config.py                            # 含假金鑰（Secret #1）
    ├── database.py                          # SQLite 初始化
    ├── integrations/
    │   └── s3_backup.py                     # 含假金鑰（Secret #4）
    └── vulnerabilities/
        ├── sql_injection.py                 # CWE-89 SQL Injection
        ├── command_injection.py             # CWE-78 Command Injection
        ├── path_traversal.py               # CWE-22 Path Traversal
        ├── ssrf.py                          # CWE-918 SSRF
        ├── xss.py                           # CWE-79 Reflected XSS
        └── insecure_deserialization.py      # CWE-502 Insecure Deserialization
```

---

## 🚀 快速入門（本地執行）

### 先決條件

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) 套件管理工具

### 步驟

```bash
# 1. 安裝 uv（若尚未安裝）
pip install uv

# 2. 安裝相依套件
uv sync

# 3. 啟動 Flask 應用
uv run python -m src.app
```

開啟瀏覽器至 `http://localhost:5000`，即可看到所有漏洞端點的清單。

---

## ⚙️ Azure DevOps 設定指南

### 步驟 1：啟用 GHAzDO 功能

1. 前往 Azure DevOps → **Organization Settings** → **Advanced Security**
2. 啟用 **Secret Protection**（Secret Scanning 由 `git push` 自動觸發，不需要 Pipeline Task）
3. 啟用 **Code Security**（供 Code Scanning 和 Dependency Scanning 使用）

### 步驟 2：建立並執行 Pipeline

1. 在 Azure DevOps 專案中點選 **Pipelines → New Pipeline**
2. 選擇本儲存庫，選擇 `azure-pipelines.yml`
3. 儲存並執行

### 步驟 3：推送程式碼並觀察掃描結果

```bash
git add .
git commit -m "feat: add vulnerability demo"
git push origin main
```

推送後，前往 **Repos → Advanced Security** 查看掃描結果。

---

## 📄 Pipeline 檔案說明

本專案提供三個 Pipeline 設定檔，各有不同的展示目的。

---

### `azure-pipelines.yml` — 主要完整掃描

**目的**：這是標準的 GHAzDO Pipeline，展示完整的掃描流程，是本專案的**主要對照基準**。

包含功能：
- CodeQL 初始化與分析（完整查詢規則集，不過濾任何嚴重性）
- 相依套件掃描（比對 `requirements.txt` 與 CVE 資料庫）
- 發佈 SARIF 掃描結果到 Build Artifacts
- 執行 pytest 並發布程式碼覆蓋率報告

**使用方式**：
1. 在 Azure DevOps 中新增 Pipeline，指向此檔案
2. 推送到 `main` 分支即自動觸發
3. 查看 **Repos → Advanced Security → Code Scanning** 和 **Dependencies**

---

### `azure-pipelines-high-severity-only.yml` — 僅掃描高嚴重性漏洞

**目的**：展示「⚠️ 最差實務（Worst Practice）」——開發者可透過自訂 CodeQL config 將掃描結果精細控制為**只顯示 High/Critical 漏洞**，靜默 Medium/Low 警告，藉此規避部分安全告警。

包含功能：
- 指定自訂 CodeQL config（`.github/codeql/codeql-config-high-only.yml`）
- `query-filters` 排除 `warning` / `recommendation` 等級查詢

**使用方式**：
1. 在 Azure DevOps 中新增 Pipeline，指向此檔案
2. 由於設定 `trigger: none`，需**手動執行**（點選 Run pipeline）
3. 執行後觀察 Advanced Security 頁面，Medium/Low 警告將不再出現
4. 與 `azure-pipelines.yml` 的結果進行對比，即可看到被靜默的告警

> ⚠️ 正式環境應由組織層級 Branch Policy 限制開發者覆蓋 CodeQL config，防止此類規避。

---

### `azure-pipelines-coverage.yml` — PR Diff 覆蓋率設定

**目的**：設定 Pull Request 差異覆蓋率門檻，讓每次 PR 自動標示哪些新增程式碼缺乏測試覆蓋。

包含功能：
- 要求每次 PR 變更的程式碼至少達到 **60%** 的測試覆蓋率
- 自動在 PR 頁面的每個檔案留下覆蓋率差異評論

**使用方式**：
- 此檔案由 Azure DevOps **自動讀取**（repository 層級設定），無需額外 Pipeline Task
- 只要檔案存在於儲存庫根目錄，設定即生效

---

## 📊 output/ 資料夾說明

`output/` 資料夾儲存 Azure Pipeline 執行後的 Advanced Security 掃描結果範例，供對照與離線閱讀：

| 檔案 | 格式 | 說明 |
|------|------|------|
| `*.sarif` | SARIF（JSON 子集）| CodeQL 程式碼掃描的原始輸出，包含每條漏洞警告的位置、規則 ID 和嚴重程度 |
| `ghas_results.json` | JSON | GHAS 完整掃描結果彙整，包含 Code、Secret、Dependency 三類告警 |

**如何取得這些檔案**：

1. 執行 `azure-pipelines.yml` 後，前往 **Pipeline Run → Summary → Artifacts**
2. 下載 `CodeQL-SARIF-Results` Artifact 即可取得 SARIF 檔案
3. Advanced Security REST API 或頁面匯出可取得 `ghas_results.json`

---

## 🚫 Code Scanning：排除特定漏洞的掃描

GHAzDO 允許開發者透過 CodeQL config 排除特定查詢或嚴重性，**但這也是一種潛在的安全配置風險**，本專案特別以此作為反面教材。

### 排除方式

在 `.github/codeql/` 目錄下建立 CodeQL config 檔案：

```yaml
# .github/codeql/codeql-config-high-only.yml
query-filters:
  - exclude:
      problem.severity: warning         # 排除 Medium 漏洞
  - exclude:
      problem.severity: recommendation  # 排除 Low 漏洞
```

在 Pipeline 中指定此 config：

```yaml
- task: AdvancedSecurity-Codeql-Init@1
  inputs:
    languages: "python"
    configFilePath: ".github/codeql/codeql-config-high-only.yml"
```

### ⚠️ 風險說明

| 做法 | 效果 | 風險 |
|------|------|------|
| 排除 `warning` 等級查詢 | Medium/Low 漏洞不再告警 | 真實漏洞被靜默，消失於掃描頁面 |
| 排除特定查詢 ID | 該漏洞類型完全不掃描 | 攻擊者可針對性利用未掃描的漏洞 |
| 排除特定路徑 | 指定目錄不被掃描 | 刻意迴避特定模組的安全檢查 |

### ✅ 正式環境建議

- 由組織層級的 **Branch Policy** 強制所有 PR 必須通過**完整掃描設定**
- 禁止開發者在個人分支中覆蓋 CodeQL config
- 定期審查 `.github/codeql/` 目錄的 Git 變更記錄

---

## 預期掃描結果摘要

### Code Scanning 警告（≥ 6 條）

| 端點 | 漏洞類型 | CWE | CodeQL 查詢 |
|------|----------|-----|-------------|
| `GET /api/users?name=` | SQL Injection | CWE-89 | `py/sql-injection` |
| `GET /api/ping?host=` | OS Command Injection | CWE-78 | `py/command-line-injection` |
| `GET /api/files?filename=` | Path Traversal | CWE-22 | `py/path-injection` |
| `GET /api/fetch?url=` | SSRF | CWE-918 | `py/full-ssrf` |
| `GET /api/search?q=` | Reflected XSS | CWE-79 | `py/reflective-xss` |
| `POST /api/import` | Insecure Deserialization | CWE-502 | `py/unsafe-deserialization` |

### Secret Scanning 警告（5 條）

| # | 檔案 | 金鑰類型 |
|---|------|----------|
| 1 | `src/config.py` | Azure DevOps Personal Access Token |
| 2 | `config/settings.yaml` | npm Publish Token |
| 3 | `.env.example` | Stripe Secret Key（Test Mode）|
| 4 | `src/integrations/s3_backup.py` | Azure Storage Account Key |
| 5 | `config/settings.yaml` | Slack Incoming Webhook URL |

### Dependency Scanning（≥ 3 條警告）

| # | 套件 | 鎖定版本 | CVE | 漏洞描述 |
|---|------|----------|-----|----------|
| 1 | `requests` | `2.28.0` | CVE-2023-32681 | HTTP Proxy 認證標頭轉發至非代理主機（中風險）|
| 2 | `urllib3` | `1.26.14` | CVE-2023-43804 / CVE-2023-45803 | Cookie/Authorization 標頭在重導向時洩漏（中風險）|
| 3 | `pyyaml` | `5.3.1` | CVE-2020-14343 | `yaml.load()` 不指定 Loader 可執行任意程式碼（CVSS 9.8）|

---

## 🔧 修復循環展示指南

此步驟展示 GHAzDO 偵測漏洞後的修復與驗證流程（以 SQL Injection 為例）。

**步驟 1**：在 Advanced Security 頁面找到 `py/sql-injection` 警告，閱讀修復建議。

**步驟 2**：開啟 `src/vulnerabilities/sql_injection.py`，找到有漏洞的程式碼：

```python
# ❌ 有漏洞的程式碼（直接字串串接）
query = f"SELECT * FROM users WHERE name = '{name}'"
cursor = conn.execute(query)
```

**步驟 3**：改為使用參數化查詢：

```python
# ✅ 修復後的程式碼（參數化查詢）
query = "SELECT * FROM users WHERE name = ?"
cursor = conn.execute(query, (name,))
```

**步驟 4**：提交並推送修復：

```bash
git add src/vulnerabilities/sql_injection.py
git commit -m "fix(security): 修復 SQL Injection 漏洞，改用參數化查詢"
git push
```

**步驟 5**：等待 Pipeline 重新執行（約 2–5 分鐘），回到 **Advanced Security → Code Scanning** 確認警告狀態變更為 **Fixed**。

---

## 💼 業務價值摘要

| GHAzDO 功能 | 展示漏洞數 | 業務價值 |
|-------------|-----------|----------|
| **Code Scanning** | 6 條 | 在程式碼合併前自動發現漏洞，越早修復成本越低 |
| **Secret Scanning** | 5 條 | 推送時立即偵測金鑰洩漏，防止 API 金鑰和資料庫憑證被惡意利用 |
| **Dependency Scanning** | ≥ 3 條 | 自動盤點有漏洞的第三方套件，並提供升級建議 |


## 專案概述

本專案是一個 Python（Flask）展示應用程式，用於展示 GHAzDO 兩大核心掃描功能，並提供 Dependency Scanning 的 Pipeline 設定範例：

| 功能 | 偵測目標 | 預期警告數 |
|------|----------|------------|
| **Code Scanning**（程式碼掃描）| 6 種 CodeQL 高信心漏洞 | ≥ 6 條 |
| **Secret Scanning**（金鑰掃描）| 5 種格式正確的假金鑰 | 5 條 |
| **Dependency Scanning**（相依套件掃描）| 3 個含 CVE 的有漏洞套件版本 | ≥ 3 條 |

---

## 目錄結構

```text
.
├── pyproject.toml               # 相依套件（含 3 個有漏洞版本：Dep #1–#3）
├── azure-pipelines.yml          # GHAzDO CodeQL + Dependency Scanning Pipeline
├── .env.example                 # 含 PostgreSQL 連線字串（Secret #3）
├── config/
│   └── settings.yaml            # 含 GitHub PAT（Secret #2）+ Slack Webhook（Secret #5）
└── src/
    ├── app.py                   # Flask 應用入口 + 路由註冊
    ├── config.py                # 應用設定 + Azure SP Secret（Secret #1）+ PyYAML 不安全載入
    ├── database.py              # SQLite 初始化（供 SQL Injection 展示用）
    ├── integrations/
    │   └── s3_backup.py         # S3 備份模組 + 硬編碼 AWS 金鑰（Secret #4）
    └── vulnerabilities/
        ├── sql_injection.py     # CWE-89 — SQL Injection (py/sql-injection)
        ├── command_injection.py # CWE-78 — Command Injection (py/command-line-injection)
        ├── path_traversal.py    # CWE-22 — Path Traversal (py/path-injection)
        ├── ssrf.py              # CWE-918 — SSRF (py/full-ssrf)
        ├── xss.py               # CWE-79 — Reflected XSS (py/reflective-xss)
        └── insecure_deserialization.py  # CWE-502 — Insecure Deserialization
```

---

## 快速入門

### 先決條件

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) 套件管理工具

### 本地設定

```bash
# 1. 安裝 uv（若尚未安裝）
pip install uv

# 2. 安裝相依套件
uv sync

# 3. 啟動 Flask 應用
uv run python -m src.app
```

開啟瀏覽器至 http://localhost:5000 即可看到所有漏洞端點的清單。

---

## Azure DevOps 設定指南

### 步驟 1：啟用 GHAzDO 功能

1. 前往 Azure DevOps → **Organization Settings** → **Advanced Security**
2. 啟用 **Secret Protection**（Secret Scanning 不需要 Pipeline）
3. 啟用 **Code Security**（供 Code Scanning 和 Dependency Scanning 使用）

### 步驟 2：設定 Pipeline

1. 在 Azure DevOps 專案中建立新 Pipeline
2. 選擇本儲存庫的 `azure-pipelines.yml`
3. 儲存並執行 Pipeline

### 步驟 3：推送程式碼並觀察掃描結果

```bash
git add .
git commit -m "feat: add vulnerability demo"
git push origin main
```

推送後，前往 **Repos → Advanced Security** 查看掃描結果。

---

## 預期掃描結果摘要

### Code Scanning 警告（≥ 6 條）

| 端點 | 漏洞類型 | CWE | CodeQL 查詢 |
|------|----------|-----|-------------|
| `GET /api/users?name=` | SQL Injection | CWE-89 | `py/sql-injection` |
| `GET /api/ping?host=` | OS Command Injection | CWE-78 | `py/command-line-injection` |
| `GET /api/files?filename=` | Path Traversal | CWE-22 | `py/path-injection` |
| `GET /api/fetch?url=` | SSRF | CWE-918 | `py/full-ssrf` |
| `GET /api/search?q=` | Reflected XSS | CWE-79 | `py/reflective-xss` |
| `POST /api/import` | Insecure Deserialization | CWE-502 | `py/unsafe-deserialization` |

### Secret Scanning 警告（5 條）

| # | 檔案 | 金鑰類型 | 偵測模式 |
|---|------|----------|----------|
| 1 | `src/config.py` | Azure DevOps Personal Access Token | `azure_devops_personal_access_token` |
| 2 | `config/settings.yaml` | npm Publish Token | `npm_access_token` |
| 3 | `.env.example` | Stripe Secret Key（Test Mode）| `stripe_api_key` |
| 4 | `src/integrations/s3_backup.py` | Azure Storage Account Key | `azure_storage_account_key` |
| 5 | `config/settings.yaml` | Slack Incoming Webhook URL ✓ | `slack_incoming_webhook_url` |

### Dependency Scanning（≥ 3 條警告）

`pyproject.toml` 中刻意鎖定以下含已知 CVE 的有漏洞版本以觸發掃描警告：

| # | 套件 | 鎖定版本 | CVE | 漏洞描述 |
|---|------|----------|-----|----------|
| Dep #1 | `requests` | `2.28.0` | CVE-2023-32681 | HTTP Proxy 認證標頭轉發至非代理主機（中風險） |
| Dep #2 | `urllib3` | `1.26.14` | CVE-2023-43804 / CVE-2023-45803 | Cookie/Authorization 標頭在重導向時洩漏（中風險） |
| Dep #3 | `pyyaml` | `5.3.1` | CVE-2020-14343 | `yaml.load()` 不指定 Loader 可執行任意程式碼（嚴重 CVSS 9.8） |

---

## 修復循環展示指南

此步驟展示 GHAzDO 偵測漏洞後的修復與驗證流程。

### 示範修復：SQL Injection（CWE-89）

**步驟 1**：在 GHAzDO Advanced Security 頁面中，選擇 `py/sql-injection` 警告，閱讀漏洞描述和修復建議。

**步驟 2**：開啟 `src/vulnerabilities/sql_injection.py`，找到以下有漏洞的程式碼：

```python
# ❌ 有漏洞的程式碼（直接字串串接）
query = f"SELECT * FROM users WHERE name = '{name}'"
cursor = conn.execute(query)
```

**步驟 3**：改為使用參數化查詢：

```python
# ✅ 修復後的程式碼（參數化查詢）
query = "SELECT * FROM users WHERE name = ?"
cursor = conn.execute(query, (name,))
```

**步驟 4**：提交並推送修復：

```bash
git add src/vulnerabilities/sql_injection.py
git commit -m "fix(security): 修復 SQL Injection 漏洞，改用參數化查詢"
git push
```

**步驟 5**：等待 Pipeline 重新執行（約 2–5 分鐘），回到 **Advanced Security → Code Scanning** 確認 `py/sql-injection` 警告狀態變更為 **Fixed**。

---

## 業務價值摘要（管理層視角）

| GHAzDO 功能 | 展示漏洞數 | 風險 | 業務價值 |
|-------------|-----------|------|----------|
| **Code Scanning** | 6 條警告 | 程式碼中的安全漏洞可被攻擊者利用，導致資料外洩或系統入侵 | 在程式碼合併前自動發現漏洞，降低修復成本（越早發現越便宜） |
| **Secret Scanning** | 5 條警告 | 誤提交的 API 金鑰、密碼可導致未授權存取或服務濫用 | 推送時立即偵測金鑰洩漏，防止 AWS、Slack、資料庫憑證被惡意利用 |
| **Dependency Scanning** | ≥ 3 條警告 | 使用含已知 CVE 的第三方套件，攻擊者可利用公開漏洞 | 自動盤點相依套件並提供升級建議；本例展示從「有漏洞版本」偵測到「提示修補」的完整流程 |
