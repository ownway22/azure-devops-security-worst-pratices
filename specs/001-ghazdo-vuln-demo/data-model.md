# 資料模型：GHAzDO 漏洞偵測展示範例

**日期**：2026-04-05  
**功能**：001-ghazdo-vuln-demo

## 實體

### VulnerabilityExample（漏洞範例）

代表一個刻意植入的安全漏洞模組。

| 屬性 | 類型 | 說明 |
|------|------|------|
| module_name | string | Python 模組檔案名稱（如 `sql_injection.py`） |
| vuln_type | enum | SQL_INJECTION / COMMAND_INJECTION / PATH_TRAVERSAL / SSRF / XSS / INSECURE_DESERIALIZATION |
| cwe_id | string | CWE 編號（如 `CWE-89`） |
| owasp_category | string | 對應的 OWASP Top 10 類別（如 `A03:2021 Injection`） |
| severity | enum | Critical / High / Medium / Low |
| codeql_query_id | string | 預期觸發的 CodeQL 查詢（如 `py/sql-injection`） |
| description | string | 漏洞的簡短說明 |
| flask_endpoint | string | 對應的 Flask 路由（如 `/api/users`） |

**驗證規則**：
- `module_name` 必須為有效的 Python 模組名稱
- `cwe_id` 必須符合 `CWE-\d+` 格式
- 每個 `vuln_type` 對應恰好一個模組

**狀態轉換**：不適用（靜態展示資料）

### Secret（機密資訊）

代表一個刻意暴露的憑證或令牌。

| 屬性 | 類型 | 說明 |
|------|------|------|
| secret_type | enum | AZURE_SP_SECRET / GITHUB_PAT / POSTGRES_CONN_STRING |
| file_location | string | 機密所在的檔案路徑 |
| file_type | enum | PYTHON_SOURCE / CONFIG_FILE / ENV_TEMPLATE |
| pattern_name | string | GHAzDO 偵測模式名稱（如 `azure_active_directory_application_secret`） |
| fake_value | string | 看似真實但不具危害的假機密值 |

**驗證規則**：
- `fake_value` 必須符合對應供應商的格式（Azure SP: 40 字元 Base64；GitHub PAT: `ghp_` + 36 英數字元）
- 每種 `secret_type` 分佈在不同的 `file_type` 中

### VulnerableDependency（有漏洞的相依套件）

代表一個已知含有 CVE 的 Python 套件版本。

| 屬性 | 類型 | 說明 |
|------|------|------|
| package_name | string | PyPI 套件名稱 |
| pinned_version | string | 鎖定的有漏洞版本 |
| cve_id | string | 主要 CVE 編號 |
| severity | enum | Critical / High / Medium |
| description | string | CVE 簡短說明 |
| safe_version | string | 建議升級的安全版本 |

**驗證規則**：
- `pinned_version` 必須在 PyPI 上可安裝
- `cve_id` 必須在 NVD 或 GitHub Advisory Database 中有記錄

## 實體關係

```
VulnerabilityExample 1---1 Flask Endpoint（每個漏洞獨立路由）
Secret 1---1 File（每個機密在不同檔案中）
VulnerableDependency 1---* CVE（一個套件版本可能有多個 CVE）
```

所有三種實體獨立存在，無互相依賴，可平行開發。

## 實例清單

### 漏洞範例實例

| # | 模組 | 類型 | CWE | OWASP | CodeQL | Flask 路由 |
|---|------|------|-----|-------|--------|-----------|
| 1 | `sql_injection.py` | SQL Injection | CWE-89 | A03 Injection | `py/sql-injection` | `/api/users` |
| 2 | `command_injection.py` | Command Injection | CWE-78 | A03 Injection | `py/command-line-injection` | `/api/ping` |
| 3 | `path_traversal.py` | Path Traversal | CWE-22 | A01 Broken Access Control | `py/path-injection` | `/api/files` |
| 4 | `ssrf.py` | SSRF | CWE-918 | A10 SSRF | `py/full-ssrf` | `/api/fetch` |
| 5 | `xss.py` | XSS | CWE-79 | A03 Injection | `py/reflective-xss` | `/api/search` |
| 6 | `insecure_deserialization.py` | Insecure Deserialization | CWE-502 | A08 Software Integrity | `py/unsafe-deserialization` | `/api/import` |

### 機密資訊實例

| # | 類型 | 檔案位置 | 檔案類型 |
|---|------|----------|----------|
| 1 | Azure Service Principal Secret | `src/config.py` | Python 原始碼 |
| 2 | GitHub PAT | `config/settings.yaml` | 設定檔 |
| 3 | PostgreSQL 連線字串 | `.env.example` | 環境變數範本 |

### 有漏洞的相依套件實例

| # | 套件 | 版本 | CVE | 嚴重程度 | 安全版本 |
|---|------|------|-----|----------|----------|
| 1 | PyYAML | 5.3.1 | CVE-2020-14343 | Critical | ≥ 5.4 |
| 2 | Pillow | 9.5.0 | CVE-2023-50447 | High | ≥ 10.2.0 |
| 3 | urllib3 | 1.26.4 | CVE-2021-33503 | High | ≥ 1.26.5 |
| 4 | Jinja2 | 3.1.2 | CVE-2024-22195 | Medium | ≥ 3.1.3 |
