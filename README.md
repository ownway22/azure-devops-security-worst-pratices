# 🔍 GHAzDO 漏洞偵測展示範例

> **⚠️ 免責聲明**：本專案包含**刻意植入的程式碼安全漏洞與假機密**，僅用於展示 GitHub Advanced Security for Azure DevOps（GHAzDO）的偵測能力。**請勿將任何程式碼使用於生產環境。**

## 專案概述

本專案是一個 Python（Flask）展示應用程式，用於展示 GHAzDO 兩大核心掃描功能，並提供 Dependency Scanning 的 Pipeline 設定範例：

| 功能 | 偵測目標 | 預期警告數 |
|------|----------|------------|
| **Code Scanning**（程式碼掃描）| 6 種 CodeQL 高信心漏洞 | ≥ 6 條 |
| **Secret Scanning**（機密掃描）| 5 種格式正確的假機密 | 5 條 |
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

| # | 檔案 | 機密類型 | 偵測模式 |
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
| **Secret Scanning** | 5 條警告 | 誤提交的 API 金鑰、密碼可導致未授權存取或服務濫用 | 推送時立即偵測機密洩漏，防止 AWS、Slack、資料庫憑證被惡意利用 |
| **Dependency Scanning** | ≥ 3 條警告 | 使用含已知 CVE 的第三方套件，攻擊者可利用公開漏洞 | 自動盤點相依套件並提供升級建議；本例展示從「有漏洞版本」偵測到「提示修補」的完整流程 |
