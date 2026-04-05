# 功能規格：GHAzDO 漏洞偵測展示範例

**功能分支**：`001-ghazdo-vuln-demo`  
**建立日期**：2026-04-05  
**狀態**：草稿  
**輸入**：使用者描述："我要在本地repo產生靜態程式碼分析中常見的漏洞範例，目的是為了將本地repo推送到我的Azure DevOps repository以後，使用 GitHub Advanced Security for Azure DevOps 服務偵測這些漏洞後並修復。請以Python為主，透過uv sync、pyproject.toml建立虛擬環境。請設計幾個 GHAzDO 可以偵測到的漏洞，展現該服務的特色和優勢。"

## 使用者情境與測試 *（必填）*

### 使用者故事 1 - 程式碼掃描漏洞展示（優先順序：P1）

身為安全工程師或 DevOps 工程師，我要在本地 Python 專案中刻意植入數種常見的靜態程式碼分析漏洞（如 SQL 注入、命令注入、路徑穿越、不安全的反序列化等），這樣當我將程式碼推送至 Azure DevOps 後，GHAzDO 的 Code Scanning（CodeQL）功能可以自動偵測並回報這些漏洞，展示其靜態分析的深度和準確性。

**優先順序原因**：Code Scanning 是 GHAzDO 最核心的功能，能展示 CodeQL 引擎偵測 OWASP Top 10 漏洞的能力，這是整個展示的基礎。

**獨立測試**：可透過將含漏洞的 Python 程式碼推送至啟用了 GHAzDO 的 Azure DevOps repo，驗證 Code Scanning 結果頁面是否顯示對應的警告，每個漏洞類型至少被偵測到一次。

**驗收情境**：

1. **假設** 本地 repo 包含至少 6 種不同類別的 Python 程式碼漏洞（依 FR-002 定義），**當** 推送至已啟用 GHAzDO Code Scanning 的 Azure DevOps repo 並觸發 CodeQL 掃描，**則** 每種漏洞類別至少產生一條安全警告
2. **假設** 漏洞程式碼以真實應用場景呈現（如簡易 Web 應用、命令列工具），**當** 檢視掃描結果，**則** 每條警告包含漏洞描述、嚴重程度、受影響的程式碼行數以及修復建議

---

### 使用者故事 2 - 機密資訊掃描展示（優先順序：P1）

身為安全工程師，我要在程式碼中刻意嵌入看似真實的機密資訊（如 API 金鑰、資料庫連線字串、雲端服務令牌），這樣當程式碼推送至 Azure DevOps 時，GHAzDO 的 Secret Scanning 功能可以偵測到這些暴露的機密，展示其自動識別機密資訊洩漏的能力。

**優先順序原因**：Secret Scanning 是 GHAzDO 的獨特亮點之一，能在程式碼進入版控的瞬間攔截機密洩漏，這對企業安全至關重要，且與 Code Scanning 並列為最有展示價值的功能。

**獨立測試**：可透過在程式碼檔案或設定檔中植入已知格式的機密字串，推送後驗證 Secret Scanning 頁面是否列出對應的警告。

**驗收情境**：

1. **假設** repo 中包含至少 3 種不同類型的機密資訊（如雲端 API 金鑰、資料庫憑證、存取令牌），**當** 推送至已啟用 GHAzDO Secret Scanning 的 Azure DevOps repo，**則** 每種機密類型被識別並回報為安全警告
2. **假設** 機密資訊散佈在不同類型的檔案中（Python 原始碼、設定檔、環境變數範本），**當** 檢視掃描結果，**則** 每條警告標示機密類型和所在位置

---

### 使用者故事 3 - 相依套件漏洞掃描展示（優先順序：P2）

身為安全工程師，我要在 `pyproject.toml` 中刻意引用含有已知 CVE 漏洞的 Python 套件版本，這樣當觸發 GHAzDO 的 Dependency Scanning 時，可以展示其自動偵測軟體供應鏈風險的能力。

**優先順序原因**：Dependency Scanning 展示了 GHAzDO 在軟體供應鏈安全方面的能力，這是現代 DevSecOps 的關鍵一環，但相較前兩者更容易理解且設置較直接。

**獨立測試**：可透過在 `pyproject.toml` 中指定已知含有 CVE 的套件版本，推送後驗證 Dependency Scanning 頁面是否列出對應的漏洞。

**驗收情境**：

1. **假設** `pyproject.toml` 中包含至少 3 個已知含有安全漏洞的套件版本，**當** 推送至已啟用 GHAzDO Dependency Scanning 的 Azure DevOps repo，**則** 這些套件的已知漏洞被列出，包含 CVE 編號和嚴重程度
2. **假設** 漏洞套件涵蓋不同嚴重程度（Critical / High / Medium），**當** 檢視掃描結果，**則** 結果按嚴重程度分類，且提供建議的升級版本

---

### 使用者故事 4 - 漏洞修復與驗證循環展示（優先順序：P2）

身為安全工程師，我要能在偵測到漏洞後進行修復，然後重新推送並驗證漏洞已被解決，展示 GHAzDO 支援完整的偵測→修復→驗證安全開發生命週期。修復不預先準備，展示時根據 GHAzDO 掃描結果提供的建議自行修復程式碼，以最真實地呈現 GHAzDO 輔助修復的能力。

**優先順序原因**：展示完整的修復循環能突顯 GHAzDO 不僅是偵測工具，更是融入開發工作流程的安全平台。

**獨立測試**：先確認漏洞已被偵測，然後套用修復後重新推送，驗證該漏洞警告在重新掃描後標記為已解決。

**驗收情境**：

1. **假設** 至少一個漏洞已被 GHAzDO 偵測並回報，**當** 開發者根據警告中的建議修改程式碼並重新推送，**則** 重新掃描後該漏洞警告的狀態更新為「已修復」或「已關閉」
2. **假設** 使用者選擇修復一個 SQL 注入漏洞，**當** 將原始碼從字串串接改為參數化查詢後推送，**則** 對應的 CodeQL 警告消失或標記為已解決

---

### 邊界情境

- 當程式碼中的機密字串格式不完全符合已知供應商格式時，Secret Scanning 是否仍能偵測？（預期：可能無法偵測自訂格式的機密，因此範例應使用已知供應商的金鑰格式）
- 當漏洞程式碼位於被 `.gitignore` 排除的檔案中時，掃描是否忽略？（預期：是的，掃描僅針對版控中的檔案）
- 當 `pyproject.toml` 指定的套件版本同時具有多個 CVE 時，系統如何呈現？（預期：每個 CVE 各自列為獨立警告）
- 當相依套件的漏洞版本是間接依賴（transitive dependency）時，是否也能被偵測？（預期：GHAzDO 可偵測直接和間接依賴中的漏洞）

## 需求 *（必填）*

### 功能性需求

- **FR-001**：專案必須是有效的 Python 專案，以 `pyproject.toml` 定義專案設定和相依套件，並可透過 `uv sync` 建立虛擬環境
- **FR-002**：專案必須包含 6 種不同類別的程式碼漏洞，每種以獨立的 Python 模組呈現，具體為：SQL Injection (CWE-89)、OS Command Injection (CWE-78)、Path Traversal (CWE-22)、Server-Side Request Forgery (CWE-918)、Cross-Site Scripting (CWE-79)、Insecure Deserialization (CWE-502)，並附帶註解說明漏洞類型和 CWE 編號
- **FR-003**：上述 6 種漏洞涵蓋 OWASP Top 10 中 5 個類別：A03 注入攻擊（SQL Injection、Command Injection、XSS）、A01 存取控制失效（Path Traversal）、A10 SSRF、A08 軟體和資料完整性失效（Insecure Deserialization）、A05 安全設定錯誤（透過結合多種漏洞展示）
- **FR-004**：專案必須包含至少 3 種不同類型的刻意暴露的機密資訊，具體為：Azure Service Principal Secret、GitHub Personal Access Token (PAT)、PostgreSQL 連線字串，分佈在不同檔案類型中（Python 原始碼、設定檔、環境變數範本）
- **FR-005**：`pyproject.toml` 必須包含至少 3 個已知含有安全漏洞的 Python 套件版本
- **FR-006**：每個漏洞範例使用 Flask 框架呈現，Web 端點類漏洞以 Flask Blueprint 組織，資料庫操作與檔案處理等則以對應的 Python 模組呈現，而非純粹的教學片段
- **FR-007**：專案結構必須清晰，每個漏洞範例可獨立理解，並附帶 README 同時服務混合觀眾：包含技術操作指南（面向工程師）和價值摘要（面向管理層），說明每個範例的用途和預期偵測結果
- **FR-008**：所有 Python 程式碼必須可被 `uv run` 執行，不應有語法錯誤或匯入錯誤（漏洞是邏輯層面的，不是語法層面的）
- **FR-009**：專案必須包含 Azure Pipelines YAML 設定檔（`azure-pipelines.yml`），用於在推送時自動觸發 GHAzDO Code Scanning 和 Dependency Scanning，並附帶設定指南 README 說明如何在 Azure DevOps 中啟用 GHAzDO 各功能並連結 Pipeline

### 關鍵實體

- **漏洞範例（Vulnerability Example）**：代表一個刻意植入的安全漏洞，共 6 種：SQL Injection (CWE-89)、OS Command Injection (CWE-78)、Path Traversal (CWE-22)、SSRF (CWE-918)、XSS (CWE-79)、Insecure Deserialization (CWE-502)，每種包含漏洞類別、CWE 編號、嚴重程度、受影響的程式碼位置、預期的 GHAzDO 偵測結果
- **機密資訊（Secret）**：代表一個刻意暴露的憑證或令牌，包含機密類型（Azure Service Principal Secret / GitHub PAT / PostgreSQL 連線字串）、所在檔案、預期被 Secret Scanning 偵測的供應商分類
- **有漏洞的相依套件（Vulnerable Dependency）**：代表一個已知含有 CVE 的 Python 套件版本，包含套件名稱、指定版本、CVE 編號、嚴重程度、建議升級版本

## 成功標準 *（必填）*

### 可衡量的成果

- **SC-001**：推送至 Azure DevOps 後，GHAzDO Code Scanning 成功偵測到 FR-002 定義的全部 6 種程式碼漏洞（每個漏洞類別至少一條警告）
- **SC-002**：GHAzDO Secret Scanning 成功偵測到 100% 的刻意暴露的機密資訊
- **SC-003**：GHAzDO Dependency Scanning 成功偵測到 `pyproject.toml` 中所有已知含有 CVE 的套件版本
- **SC-004**：README 包含三大功能的三句話以內摘要和功能↔風險↔價值對照表，展示流程可在 5 分鐘內完成（從推送程式碼到檢視三種掃描結果）——工程師能依據 README 操作指南獨立完成設定，管理層能從價值摘要表格了解安全價值和風險降低效益
- **SC-005**：修復至少一個漏洞後重新推送，對應的 GHAzDO 警告在下一次掃描中標記為已解決

## 釐清

### 會話 2026-04-05

- Q: Web 應用框架選擇（影響 CodeQL 偵測規則覆蓋和專案結構）？ → A: Flask — CodeQL 偵測規則最豐富、社群範例最多，適合展示注入類漏洞
- Q: 機密資訊的供應商類型（影響 Secret Scanning 偵測率）？ → A: Azure Service Principal Secret、GitHub PAT、PostgreSQL 連線字串，聚焦 Microsoft 生態系
- Q: 程式碼漏洞的具體類別清單（影響模組結構和 CodeQL 偵測率）？ → A: 6 種高信心漏洞 — SQL Injection (CWE-89)、OS Command Injection (CWE-78)、Path Traversal (CWE-22)、SSRF (CWE-918)、XSS (CWE-79)、Insecure Deserialization (CWE-502)
- Q: 展示的目標觀眾（影響 README 深度和註解詳細程度）？ → A: 混合觀眾（工程師 + 管理層），README 包含技術操作指南和價值摘要

## 假設

- 使用者已擁有 Azure DevOps 組織並可啟用 GitHub Advanced Security for Azure DevOps
- GHAzDO 的 Code Scanning 使用 CodeQL 引擎，支援 Python 語言的靜態分析
- Secret Scanning 支援常見雲端供應商的金鑰格式（如 Azure、AWS、GitHub 等）
- 使用者的開發環境已安裝 `uv` 套件管理工具和 Python 執行環境
- 漏洞範例使用「看起來真實但不具實際危害」的假機密（避免意外暴露真實憑證）
