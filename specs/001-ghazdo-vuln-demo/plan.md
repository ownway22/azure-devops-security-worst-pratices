# 實作計畫：GHAzDO 漏洞偵測展示範例

**分支**：`001-ghazdo-vuln-demo` | **日期**：2026-04-05 | **規格**：[spec.md](spec.md)
**輸入**：來自 `/specs/001-ghazdo-vuln-demo/spec.md` 的功能規格

## 摘要

建立一個 Python（Flask）展示專案，刻意植入 6 種 CodeQL 高信心漏洞（SQL Injection、Command Injection、Path Traversal、SSRF、XSS、Insecure Deserialization）、3 種機密資訊（Azure Service Principal Secret、GitHub PAT、PostgreSQL 連線字串）、以及至少 3 個含有已知 CVE 的相依套件。專案包含 Azure Pipelines YAML 和設定指南 README，推送至 Azure DevOps 後可自動觸發 GHAzDO 三大功能掃描。目標觀眾為混合觀眾（工程師 + 管理層）。

## 技術情境

**語言/版本**：Python 3.11+  
**主要相依套件**：Flask（Web 框架）、含已知 CVE 的套件（見 research.md）、uv（套件管理）  
**儲存方式**：SQLite（用於 SQL Injection 展示場景）  
**測試工具**：不適用（此為安全漏洞展示專案，非生產程式碼）  
**目標平台**：本地開發環境 → 推送至 Azure DevOps  
**專案類型**：單一 Python 專案  
**效能目標**：不適用（展示用途）  
**約束條件**：所有漏洞必須被 CodeQL Python 查詢偵測到；程式碼必須可被 `uv run` 執行；機密必須使用已知供應商格式  
**規模/範圍**：單一開發者展示用途、約 10-15 個 Python 檔案

## 憲章檢查

*關卡：必須在階段 0 研究前通過。階段 1 設計後重新檢查。*

**結果**：通過（不適用）— 憲章為空白範本，尚未為此專案客製化，無關卡需評估。

## 專案結構

### 文件（此功能）

```text
specs/001-ghazdo-vuln-demo/
├── plan.md              # 此檔案（/speckit.plan 指令輸出）
├── spec.md              # 功能規格
├── research.md          # 階段 0 輸出 — 技術研究
├── data-model.md        # 階段 1 輸出 — 實體模型
├── quickstart.md        # 階段 1 輸出 — 快速入門指南
├── contracts/
│   └── flask-endpoints.md  # 階段 1 輸出 — Flask 端點契約
├── checklists/
│   └── requirements.md  # 規格品質檢核清單
└── tasks.md             # 階段 2 輸出（/speckit.tasks）
```

### 原始碼（儲存庫根目錄）

```text
.
├── pyproject.toml           # 專案定義 + 有漏洞的相依套件
├── azure-pipelines.yml      # GHAzDO CodeQL + Dependency Scanning Pipeline
├── .env.example             # 含 PostgreSQL 連線字串（Secret #3）
├── README.md                # 混合觀眾導向的說明文件
├── config/
│   └── settings.yaml        # 含 GitHub PAT（Secret #2）
└── src/
    ├── __init__.py
    ├── app.py               # Flask 應用入口 + 路由註冊
    ├── config.py            # 應用設定 + Azure SP Secret（Secret #1）
    ├── vulnerabilities/
    │   ├── __init__.py
    │   ├── sql_injection.py          # CWE-89 — SQL Injection 端點
    │   ├── command_injection.py      # CWE-78 — Command Injection 端點
    │   ├── path_traversal.py         # CWE-22 — Path Traversal 端點
    │   ├── ssrf.py                   # CWE-918 — SSRF 端點
    │   ├── xss.py                    # CWE-79 — Reflected XSS 端點
    │   └── insecure_deserialization.py  # CWE-502 — Insecure Deserialization 端點
    └── database.py          # SQLite 初始化（供 SQL Injection 展示用）
```

**結構決策**：採用單一專案結構。所有漏洞端點集中在 `src/vulnerabilities/` 下，每個漏洞一個獨立模組（Flask Blueprint 或直接路由），方便獨立理解和導航。無前後端分離需求。

## 憲章檢查（設計後重新評估）

**結果**：通過 — 憲章為空白範本，無關卡需評估。專案結構簡潔，無違反簡約原則。

## 複雜度追蹤

無違規項目。專案為單一 Python 專案，結構簡單，不需要額外說明理由。
