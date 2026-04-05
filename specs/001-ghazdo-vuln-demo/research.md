# 研究：GHAzDO 漏洞偵測展示範例

**日期**：2026-04-05  
**功能**：001-ghazdo-vuln-demo

## 1. CodeQL Python 查詢對 6 種漏洞的覆蓋

**決策**：選定 6 種漏洞均有成熟的 CodeQL Python 查詢，且對 Flask 框架有完善的汙點追蹤支援。

**理由**：所有查詢均在 CodeQL 預設查詢套件中，無需額外設定自訂查詢。Flask 的 `request.args`、`request.form`、`request.data` 等均被識別為汙點來源（taint source）。

| 漏洞類型 | CWE | CodeQL 查詢 ID | Flask 汙點來源 | 信心等級 |
|----------|-----|----------------|----------------|----------|
| SQL Injection | CWE-89 | `py/sql-injection` | `request.args`, `request.form`, `request.values` | 高 |
| OS Command Injection | CWE-78 | `py/command-line-injection` | `request.args`, `request.form`, `request.values` | 高 |
| Path Traversal | CWE-22 | `py/path-injection` | `request.args`, `request.form`, `request.path` | 高 |
| SSRF | CWE-918 | `py/full-ssrf` / `py/partial-ssrf` | `request.args`, `request.form`, `request.url` | 高 |
| Reflected XSS | CWE-79 | `py/reflective-xss` | `request.args`, `request.form`, `request.cookies` | 高 |
| Insecure Deserialization | CWE-502 | `py/unsafe-deserialization` | 使用者控制的 pickle/YAML 輸入 | 高 |

**考慮的替代方案**：Hardcoded Credentials (CWE-798)、Weak Cryptography (CWE-327)、XXE (CWE-611)。排除原因：前兩者的 CodeQL Python 偵測規則較新且不穩定；XXE 在 Python 中較少見且需要額外的 XML 處理套件。

## 2. 含已知 CVE 的 Python 套件

**決策**：選定以下 4 個套件（覆蓋 Critical / High / Medium 三個嚴重等級），均為廣泛使用的知名套件。

**理由**：這些套件均在 NVD 和 GitHub Advisory Database 中有清晰記錄，GHAzDO Dependency Scanning 使用相同的資料來源，偵測率極高。

| 套件 | 有漏洞版本 | CVE | 嚴重程度 | 說明 | 建議升級版本 |
|------|-----------|-----|----------|------|-------------|
| PyYAML | 5.3.1 | CVE-2020-14343 | Critical (9.8) | `full_load()` 允許透過 `python/object/new` 構造器執行任意程式碼 | ≥ 5.4 |
| Pillow | 9.5.0 | CVE-2023-50447 | High (8.1) | `PIL.ImageMath.eval()` 的 `environment` 參數允許任意程式碼執行 | ≥ 10.2.0 |
| urllib3 | 1.26.4 | CVE-2021-33503 | High (7.5) | 解析含 `@` 的 URL 時的 ReDoS 漏洞，可導致拒絕服務 | ≥ 1.26.5 |
| Jinja2 | 3.1.2 | CVE-2024-22195 | Medium (6.1) | 透過 `xmlattr` 過濾器的 XSS 漏洞 | ≥ 3.1.3 |

**考慮的替代方案**：Django（有 CVE 但太重，且展示已選用 Flask）、requests（CVE 較輕微且可能與 Flask 相依衝突）。

**注意**：Jinja2 是 Flask 的直接依賴。在 `pyproject.toml` 中需明確鎖定 Jinja2 的有漏洞版本，確保 `uv sync` 時不被自動解析為更新版本。如有版本衝突，可改用 `requests==2.25.1`（CVE-2023-32681，Medium）作為替代。

## 3. GHAzDO Secret Scanning 支援的模式

**決策**：確認三種選定的機密類型均被 GHAzDO Secret Scanning 支援。

**理由**：根據 GitHub 官方文件的支援模式清單，三種類型均有對應的偵測規則。

| 機密類型 | 偵測？ | 模式名稱 | 精確度 |
|----------|--------|----------|--------|
| Azure Service Principal Client Secret | ✅ 是 | `azure_active_directory_application_secret` | 高 |
| GitHub Personal Access Token (classic) | ✅ 是 | `github_personal_access_token` | 高 |
| PostgreSQL 連線字串（含嵌入密碼） | ✅ 是 | `postgres_connection_string` | 高（非供應商模式） |

**考慮的替代方案**：AWS Access Key、GCP Service Account Key、Slack Webhook。排除原因：使用者選擇聚焦 Microsoft 生態系。

**重要注意**：機密字串必須使用「看似真實但不具實際危害」的格式。Azure SP Secret 應為 40 個字元的 Base64 類字串；GitHub PAT 應以 `ghp_` 開頭後接 36 個英數字元。PostgreSQL 連線字串應符合 `postgresql://user:password@host:port/dbname` 格式。

## 4. Azure Pipelines YAML 設定

**決策**：使用 Microsoft 官方文件中的 YAML 範本，包含三個 GHAzDO 任務。

**理由**：官方範本已驗證可用，且包含自動安裝 CodeQL 的選項。

**來源**：[Configure GitHub Advanced Security for Azure DevOps](https://learn.microsoft.com/en-us/azure/devops/repos/security/configure-github-advanced-security-features?view=azure-devops&tabs=yaml)

**標準 Pipeline 結構**：
```yaml
trigger:
  - main

pool:
  vmImage: ubuntu-latest

steps:
  - task: AdvancedSecurity-Codeql-Init@1
    inputs:
      languages: "python"
      enableAutomaticCodeQLInstall: true

  # Python 不需要編譯步驟

  - task: AdvancedSecurity-Dependency-Scanning@1

  - task: AdvancedSecurity-Codeql-Analyze@1
```

**關鍵設定**：
- `languages: "python"` 必須明確指定
- `enableAutomaticCodeQLInstall: true` 適用於自託管代理程式
- `AdvancedSecurity-Dependency-Scanning@1` 需要 Code Security 產品已啟用
- Secret Scanning 不需要 Pipeline 任務，在 repo 層級啟用 Secret Protection 即自動運作

**考慮的替代方案**：使用 Dependency Scanning 預設設定（repo settings 的一鍵啟用）。保留為 README 中的替代方案，但 Pipeline YAML 提供更完整的控制。
