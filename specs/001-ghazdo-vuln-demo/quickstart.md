# 快速入門：GHAzDO 漏洞偵測展示範例

**日期**：2026-04-05  
**功能**：001-ghazdo-vuln-demo

## 先決條件

1. Python 3.11+
2. [uv](https://docs.astral.sh/uv/) 套件管理工具
3. Azure DevOps 組織，已啟用 GitHub Advanced Security（Secret Protection + Code Security）
4. Azure DevOps repo 與本地 repo 已連結（`git remote add origin ...`）

## 本地設定

```bash
# 1. 複製 repo
git clone <your-azure-devops-repo-url>
cd azure-devops-security-worst-pratices

# 2. 建立虛擬環境並安裝相依套件
uv sync

# 3. 執行 Flask 應用（選用，驗證程式碼可執行）
uv run python -m src.app
```

## 推送至 Azure DevOps 並觸發掃描

```bash
# 推送程式碼（將同時觸發 Secret Scanning 和 Pipeline）
git push origin main
```

推送後：
- **Secret Scanning** 立即啟動（無需 Pipeline）
- **Code Scanning + Dependency Scanning** 由 `azure-pipelines.yml` 觸發

## 檢視掃描結果

1. 開啟 Azure DevOps → Repos → Advanced Security
2. 分別檢視：
   - **Code Scanning**：預期 6 條漏洞警告（每個端點一條）
   - **Secret Scanning**：預期 3 條機密暴露警告
   - **Dependency Scanning**：預期 4 條套件漏洞警告

## Azure DevOps 設定指南

### 步驟 1：啟用 GHAzDO

1. 進入 Project Settings → Repos → Repositories
2. 選擇目標 repo
3. 開啟 **Secret Protection**（啟用 Secret Scanning）
4. 開啟 **Code Security**（啟用 Code Scanning + Dependency Scanning）
5. 點擊 **Begin billing**

### 步驟 2：設定 Pipeline

1. 進入 Pipelines → Create Pipeline
2. 選擇 Azure Repos Git
3. 選擇此 repo
4. 選擇「Existing Azure Pipelines YAML file」
5. 選取 `/azure-pipelines.yml`
6. 執行 Pipeline

### 步驟 3：驗證結果

Pipeline 執行完成後，回到 Repos → Advanced Security 檢視掃描結果。

## 展示修復循環

1. 在 Advanced Security 頁面選擇一個警告（建議選 SQL Injection）
2. 閱讀 GHAzDO 提供的漏洞說明和修復建議
3. 根據建議修改程式碼（如改用參數化查詢）
4. 提交並推送修改
5. 等待 Pipeline 重新掃描
6. 驗證該警告已標記為「Fixed」

## 價值摘要（管理層）

| GHAzDO 功能 | 防範的風險 | 業務價值 |
|-------------|-----------|----------|
| Code Scanning (CodeQL) | 程式碼中的安全漏洞（注入、XSS 等） | 在程式碼進入生產環境前發現並修復漏洞，降低資安事件成本 |
| Secret Scanning | 程式碼中暴露的機密資訊 | 防止憑證洩漏導致的未授權存取，符合合規要求 |
| Dependency Scanning | 第三方套件的已知漏洞 | 管控軟體供應鏈風險，自動追蹤 CVE 並提供升級建議 |
