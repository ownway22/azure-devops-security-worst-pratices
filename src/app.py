"""Flask 應用程式入口 — 組合所有漏洞藍圖，並在首頁呈現可用端點清單。"""

from flask import Flask, jsonify

from src.vulnerabilities.command_injection import command_injection_bp
from src.vulnerabilities.insecure_deserialization import deserialization_bp
from src.vulnerabilities.path_traversal import path_traversal_bp
from src.vulnerabilities.sql_injection import sql_injection_bp
from src.vulnerabilities.ssrf import ssrf_bp
from src.vulnerabilities.xss import xss_bp

app = Flask(__name__)

# ── 藍圖註冊 ─────────────────────────────────────────────────────────────────
app.register_blueprint(sql_injection_bp)
app.register_blueprint(command_injection_bp)
app.register_blueprint(path_traversal_bp)
app.register_blueprint(ssrf_bp)
app.register_blueprint(xss_bp)
app.register_blueprint(deserialization_bp)

ENDPOINTS = [
    {
        "route": "GET /api/users?name=<value>",
        "vulnerability": "SQL Injection",
        "cwe": "CWE-89",
        "codeql": "py/sql-injection",
        "description": "User input is interpolated directly into a SQL query string.",
    },
    {
        "route": "GET /api/ping?host=<value>",
        "vulnerability": "OS Command Injection",
        "cwe": "CWE-78",
        "codeql": "py/command-line-injection",
        "description": "User input is passed to subprocess.run() with shell=True.",
    },
    {
        "route": "GET /api/files?filename=<value>",
        "vulnerability": "Path Traversal",
        "cwe": "CWE-22",
        "codeql": "py/path-injection",
        "description": "User input is used directly in open() without path validation.",
    },
    {
        "route": "GET /api/fetch?url=<value>",
        "vulnerability": "Server-Side Request Forgery (SSRF)",
        "cwe": "CWE-918",
        "codeql": "py/full-ssrf",
        "description": "User-supplied URL is passed directly to requests.get().",
    },
    {
        "route": "GET /api/search?q=<value>",
        "vulnerability": "Reflected XSS",
        "cwe": "CWE-79",
        "codeql": "py/reflective-xss",
        "description": "User input is embedded in an HTML response without escaping.",
    },
    {
        "route": "POST /api/import  (body: base64 pickle payload)",
        "vulnerability": "Insecure Deserialization",
        "cwe": "CWE-502",
        "codeql": "py/unsafe-deserialization",
        "description": "Request body is base64-decoded and passed directly to pickle.loads().",
    },
]


@app.route("/")
def index():
    """首頁：以 HTML 表格列出全部漏洞展示端點。"""
    rows = "".join(
        f"""
        <tr>
          <td><code>{e['route']}</code></td>
          <td>{e['vulnerability']}</td>
          <td>{e['cwe']}</td>
          <td><code>{e['codeql']}</code></td>
          <td>{e['description']}</td>
        </tr>"""
        for e in ENDPOINTS
    )

    html = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
  <meta charset="UTF-8">
  <title>GHAzDO 漏洞偵測展示</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 2em; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; }}
    th {{ background: #f0f0f0; }}
    code {{ background: #eee; padding: 2px 4px; border-radius: 3px; }}
  </style>
</head>
<body>
  <h1>🔍 GHAzDO 漏洞偵測展示</h1>
  <p>本應用程式刻意植入多種安全漏洞，用於展示 GitHub Advanced Security for Azure DevOps（GHAzDO）的三大掃描功能。</p>
  <h2>可用漏洞端點</h2>
  <table>
    <thead>
      <tr>
        <th>路由</th>
        <th>漏洞類型</th>
        <th>CWE</th>
        <th>CodeQL 查詢</th>
        <th>說明</th>
      </tr>
    </thead>
    <tbody>{rows}</tbody>
  </table>
</body>
</html>"""
    return html


@app.route("/api/health")
def health():
    """健康檢查：確認服務正常運作。"""
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(debug=True)
