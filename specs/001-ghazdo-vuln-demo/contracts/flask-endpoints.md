# Flask 端點契約：GHAzDO 漏洞展示應用

**日期**：2026-04-05  
**功能**：001-ghazdo-vuln-demo  
**框架**：Flask  
**說明**：以下端點均包含刻意的安全漏洞，僅供 GHAzDO 偵測展示使用。

---

## GET /

首頁，列出所有可用的漏洞端點及說明。

**回應**：HTML 頁面

---

## GET /api/users

**用途**：展示 SQL Injection (CWE-89)

**參數**：
| 名稱 | 位置 | 類型 | 說明 |
|------|------|------|------|
| name | query | string | 使用者名稱搜尋條件 |

**漏洞行為**：將 `name` 參數直接串接至 SQL 查詢字串  
**預期 CodeQL 警告**：`py/sql-injection`

**回應**：
- 200: `{ "users": [{"id": int, "name": string, "email": string}] }`

---

## GET /api/ping

**用途**：展示 OS Command Injection (CWE-78)

**參數**：
| 名稱 | 位置 | 類型 | 說明 |
|------|------|------|------|
| host | query | string | 要 ping 的主機位址 |

**漏洞行為**：將 `host` 參數直接傳入 `os.system()` 或 `subprocess.call(shell=True)`  
**預期 CodeQL 警告**：`py/command-line-injection`

**回應**：
- 200: `{ "result": string }`

---

## GET /api/files

**用途**：展示 Path Traversal (CWE-22)

**參數**：
| 名稱 | 位置 | 類型 | 說明 |
|------|------|------|------|
| filename | query | string | 要讀取的檔案名稱 |

**漏洞行為**：將 `filename` 參數直接用於 `open()` 而未驗證路徑  
**預期 CodeQL 警告**：`py/path-injection`

**回應**：
- 200: 檔案內容（text/plain）

---

## GET /api/fetch

**用途**：展示 Server-Side Request Forgery / SSRF (CWE-918)

**參數**：
| 名稱 | 位置 | 類型 | 說明 |
|------|------|------|------|
| url | query | string | 要抓取的外部 URL |

**漏洞行為**：將 `url` 參數直接傳入 `requests.get()` 而未驗證  
**預期 CodeQL 警告**：`py/full-ssrf`

**回應**：
- 200: `{ "status_code": int, "content": string }`

---

## GET /api/search

**用途**：展示 Reflected Cross-Site Scripting / XSS (CWE-79)

**參數**：
| 名稱 | 位置 | 類型 | 說明 |
|------|------|------|------|
| q | query | string | 搜尋關鍵詞 |

**漏洞行為**：將 `q` 參數直接嵌入 HTML 回應而未進行輸出編碼  
**預期 CodeQL 警告**：`py/reflective-xss`

**回應**：
- 200: HTML 頁面（含未編碼的使用者輸入）

---

## POST /api/import

**用途**：展示 Insecure Deserialization (CWE-502)

**參數**：
| 名稱 | 位置 | 類型 | 說明 |
|------|------|------|------|
| data | body | string (base64) | Base64 編碼的序列化資料 |

**漏洞行為**：使用 `pickle.loads()` 反序列化使用者提供的資料而未驗證  
**預期 CodeQL 警告**：`py/unsafe-deserialization`

**回應**：
- 200: `{ "imported": object }`
