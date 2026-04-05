# 🔍 GHAzDO 漏洞偵測展示範例

> **⚠️ 免責聲明**：本專案包含**刻意植入的安全漏洞**，僅用於展示 GitHub Advanced Security for Azure DevOps（GHAzDO）的偵測能力。**請勿將任何程式碼使用於生產環境。**

## 專案概述

本專案是一個 Python（Flask）展示應用程式，刻意植入多種安全問題，用於展示 GHAzDO 三大核心功能：

| 功能 | 偵測目標 | 預期警告數 |
|------|----------|------------|
| **Code Scanning**（程式碼掃描）| 6 種 CodeQL 高信心漏洞 | ≥ 6 條 |
| **Secret Scanning**（機密掃描）| 3 種格式正確的假機密 | 3 條 |
| **Dependency Scanning**（相依套件掃描）| 4 個含已知 CVE 的套件 | ≥ 4 條 |

---

## 目錄結構

```text
.
├── pyproject.toml               # 專案定義 + 有漏洞的相依套件
├── azure-pipelines.yml          # GHAzDO CodeQL + Dependency Scanning Pipeline
├── .env.example                 # 含 PostgreSQL 連線字串（Secret #3）
├── config/
│   └── settings.yaml            # 含 GitHub PAT（Secret #2）
└── src/
    ├── app.py                   # Flask 應用入口 + 路由註冊
    ├── config.py                # 應用設定 + Azure SP Secret（Secret #1）
    ├── database.py              # SQLite 初始化（供 SQL Injection 展示用）
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

# 2. 安裝所有相依套件（含有漏洞的版本）
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

推送後，前往 **Repos → Advanced Security** 查看三種掃描結果。

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

### Secret Scanning 警告（3 條）

| 檔案 | 機密類型 | 偵測模式 |
|------|----------|----------|
| `src/config.py` | Azure SP Client Secret | `azure_active_directory_application_secret` |
| `config/settings.yaml` | GitHub Personal Access Token | `github_personal_access_token` |
| `.env.example` | PostgreSQL 連線字串 | `postgres_connection_string` |

### Dependency Scanning 警告（≥ 7 條）

| 套件 | 版本 | CVE | 嚴重程度 | 說明 |
|------|------|-----|----------|------|
| PyYAML | 5.3.1 | CVE-2020-14343 | Critical (9.8) | `full_load()` 允許任意程式碼執行 |
| Pillow | 9.5.0 | CVE-2023-50447 | High (8.1) | `ImageMath.eval()` 任意程式碼執行 |
| Pillow | 9.5.0 | CVE-2024-28219 | High | 緩衝區溢位（< 10.3.0）|
| Pillow | 9.5.0 | CVE-2023-44271 | High | 拒絕服務（< 10.0.0）|
| urllib3 | 2.0.6 | CVE-2023-45803 | Medium (4.4) | 重定向時 Authorization 標頭未移除 |
| urllib3 | 2.0.6 | CVE-2024-37891 | Medium (4.4) | 跟隨 HTTP 重定向時解壓炸彈防護被繞過（< 2.6.3）|
| urllib3 | 2.0.6 | CVE-2024-37895 | Medium | 串流 API 未正確處理高度壓縮資料（< 2.6.0）|
| requests | 2.31.0 | CVE-2023-32681 | Medium (6.1) | 代理認證資訊洩漏 |

> **注意**：`urllib3==2.0.6` 取代原始規格的 `2.0.3`，修正了跨來源重定向時 Cookie 標頭未移除的問題（影響 2.0.0–2.0.5，對 SSRF 展示端點有實際功能影響）。其餘 CVE 保留用於展示目的。

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

| GHAzDO 功能 | 風險 | 業務價值 |
|-------------|------|----------|
| **Code Scanning** | 程式碼中的安全漏洞可被攻擊者利用，導致資料外洩或系統入侵 | 在程式碼合併前自動發現漏洞，降低修復成本（越早發現越便宜） |
| **Secret Scanning** | 誤提交的 API 金鑰、密碼可導致未授權存取 | 推送時立即偵測機密洩漏，防止憑證被惡意利用 |
| **Dependency Scanning** | 使用含已知 CVE 的第三方套件，攻擊者可利用公開漏洞 | 自動盤點並警告易受攻擊的相依套件，提供升級建議 |
