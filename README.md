# GHAzDO 安全掃描展示專案

> ⚠️ **警告**：本專案**刻意包含安全漏洞與假金鑰**，僅供學習 GHAzDO 偵測功能使用。**請勿用於生產環境。**

## 這個專案在做什麼？

**GHAzDO**（GitHub Advanced Security for Azure DevOps）是 Azure DevOps 內建的安全掃描工具。本專案是一個刻意寫壞的 Python Flask 應用程式，讓你透過 Azure DevOps Pipeline 實際觀察 GHAzDO 如何自動抓出三類安全問題：

| 掃描類型 | 說明 | 本專案植入的內容 |
|---------|------|----------------|
| **Code Scanning** | 用 CodeQL 分析程式碼邏輯漏洞 | 6 種漏洞（SQL Injection、XSS 等） |
| **Secret Scanning** | 偵測推送到 Repo 的金鑰/密碼 | 5 組假金鑰（AWS Key、GitHub PAT 等） |
| **Dependency Scanning** | 比對套件版本與已知 CVE 漏洞 | 3 個有漏洞的老舊套件版本 |

## 目錄結構

```
├── azure-pipelines.yml                    # 主要 Pipeline — 完整掃描
├── azure-pipelines-high-severity-only.yml # 反面教材 — 只掃 High/Critical
├── azure-pipelines-coverage.yml           # PR 測試覆蓋率門檻設定
├── pyproject.toml                         # Python 套件定義
├── requirements.txt                       # 套件版本鎖定（含有漏洞版本）
├── config/settings.yaml                   # 假金鑰
├── output/                                # 掃描結果範例（SARIF / JSON）
├── src/
│   ├── app.py                             # Flask 主程式
│   ├── config.py                          # 假金鑰
│   ├── database.py                        # SQLite 初始化
│   ├── integrations/s3_backup.py          # 假金鑰
│   └── vulnerabilities/                   # 6 種刻意漏洞
│       ├── sql_injection.py               # CWE-89
│       ├── command_injection.py           # CWE-78
│       ├── path_traversal.py              # CWE-22
│       ├── ssrf.py                        # CWE-918
│       ├── xss.py                         # CWE-79
│       └── insecure_deserialization.py    # CWE-502
└── tests/test_vulnerabilities.py          # 測試套件
```

## 快速開始（本地執行）

需要 **Python 3.11+** 和 [uv](https://docs.astral.sh/uv/) 套件管理工具。

```bash
pip install uv      # 安裝 uv
uv sync              # 安裝相依套件
uv run python -m src.app  # 啟動 Flask
```

開啟 http://localhost:5000 即可看到所有漏洞端點。

## 在 Azure DevOps 上執行掃描

### 1. 啟用 GHAzDO

前往 Azure DevOps → **Organization Settings** → **Advanced Security**：

- 啟用 **Secret Protection**（推送時自動觸發金鑰掃描）
- 啟用 **Code Security**（供 Code Scanning 和 Dependency Scanning 使用）

### 2. 建立 Pipeline

1. 進入專案 → **Pipelines** → **New Pipeline**
2. 選擇本儲存庫，指向 `azure-pipelines.yml`
3. 儲存並執行

### 3. 推送程式碼，觀察結果

```bash
git push origin main
```

推送後，前往 **Repos → Advanced Security** 查看掃描結果。

## Pipeline 說明

本專案有三個 Pipeline 設定檔：

### `azure-pipelines.yml` — 完整掃描（主要）

標準的 GHAzDO 掃描流程，推送到 `main` 時自動觸發：

- CodeQL 程式碼掃描（所有嚴重等級）
- 相依套件掃描
- 測試與覆蓋率報告
- 掃描結果發佈至 Build Artifacts

### `azure-pipelines-high-severity-only.yml` — 反面教材 ⚠️

展示一種**最差實務（Worst Practice）**：透過自訂 CodeQL config 過濾掉 Medium / Low 漏洞，讓這些警告「消失」。

- 需**手動執行**（`trigger: none`）
- 執行後與完整掃描結果對比，即可看到被隱藏的告警

> 正式環境應透過 Branch Policy 禁止開發者覆蓋 CodeQL config。

### `azure-pipelines-coverage.yml` — PR 覆蓋率門檻

要求每次 PR 新增的程式碼至少達 **60%** 測試覆蓋率。放在儲存庫根目錄即自動生效。

## 反面教材：如何規避掃描（以及為什麼不該這樣做）

開發者可以透過 CodeQL config 排除特定漏洞等級：

```yaml
# .github/codeql/codeql-config-high-only.yml
query-filters:
  - exclude:
      problem.severity: warning         # 排除 Medium
  - exclude:
      problem.severity: recommendation  # 排除 Low
```

然後在 Pipeline 中引用：

```yaml
- task: AdvancedSecurity-Codeql-Init@1
  inputs:
    languages: "python"
    configFilePath: ".github/codeql/codeql-config-high-only.yml"
```

**這很危險：**

| 做法 | 結果 | 風險 |
|------|------|------|
| 排除 `warning` | Medium/Low 漏洞消失 | 真實漏洞被靜默 |
| 排除特定查詢 ID | 該漏洞類型不被掃描 | 攻擊者可針對性利用 |
| 排除特定路徑 | 該目錄不被掃描 | 迴避安全檢查 |

**正確做法：**
- 組織層級 **Branch Policy** 強制使用完整掃描設定
- 禁止開發者自行覆蓋 CodeQL config
- 定期審查 `.github/codeql/` 目錄的變更記錄

## 掃描結果範例

`output/` 資料夾包含實際掃描後的結果範例：

| 檔案 | 說明 |
|------|------|
| `*.sarif` | CodeQL 掃描輸出（SARIF 格式），含漏洞位置與嚴重程度 |
| `ghas_results.json` | 三類掃描的完整結果彙整 |

取得方式：Pipeline 執行後 → **Summary → Artifacts** → 下載 `CodeQL-SARIF-Results`。

## 參考資料

- [啟用 GHAzDO 功能](https://learn.microsoft.com/en-us/azure/devops/repos/security/configure-github-advanced-security-features?view=azure-devops&tabs=yaml&pivots=standalone-ghazdo)
- [Code Scanning 說明](https://learn.microsoft.com/en-us/azure/devops/repos/security/github-advanced-security-code-scanning?view=azure-devops)
- [Dependency Scanning 說明](https://learn.microsoft.com/en-us/azure/devops/repos/security/github-advanced-security-dependency-scanning?view=azure-devops)
- [Secret Scanning 說明](https://learn.microsoft.com/en-us/azure/devops/repos/security/github-advanced-security-secret-scanning?view=azure-devops)

