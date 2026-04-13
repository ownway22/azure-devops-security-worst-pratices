"""
展示用測試套件 — 驗證各個漏洞端點正常回應。
這些測試的目的是確保端點可被呼叫（HTTP 狀態碼正確），
並為 Pipeline 的 Code Coverage 報告提供覆蓋率數據。
重點在於展示 GHAzDO 的掃描能力，而非端點的防禦強度。
"""

import base64
import pickle
from unittest.mock import MagicMock, patch

import pytest

from src.app import app


@pytest.fixture
def client():
    """建立 Flask 測試用戶端。"""
    app.config["TESTING"] = True
    # 關閉例外傳播：讓 Flask 捕捉未處理例外並回傳 500，而非直接拋出
    app.config["PROPAGATE_EXCEPTIONS"] = False
    with app.test_client() as c:
        yield c


# ── 首頁 ──────────────────────────────────────────────────────────────────────

def test_index_returns_200(client):
    """首頁應回傳漏洞端點清單。"""
    response = client.get("/")
    assert response.status_code == 200
    assert b"GHAzDO" in response.data


# ── SQL Injection (CWE-89) ────────────────────────────────────────────────────

def test_sql_injection_returns_200(client):
    """/api/users 端點應正常回應。"""
    response = client.get("/api/users?name=alice")
    assert response.status_code == 200


def test_sql_injection_empty_name(client):
    """name 參數為空時應回傳空清單而非錯誤。"""
    response = client.get("/api/users?name=")
    assert response.status_code == 200


# ── OS Command Injection (CWE-78) ─────────────────────────────────────────────

def test_command_injection_returns_200(client):
    """/api/ping 端點應正常回應。"""
    response = client.get("/api/ping?host=localhost")
    assert response.status_code == 200


def test_command_injection_default_host(client):
    """未提供 host 時應使用預設值 localhost。"""
    response = client.get("/api/ping")
    assert response.status_code == 200


# ── Path Traversal (CWE-22) ───────────────────────────────────────────────────

def test_path_traversal_existing_file_returns_200(client):
    """/api/files 請求存在的檔案時應回傳 200。"""
    response = client.get("/api/files?filename=README.md")
    assert response.status_code == 200


def test_path_traversal_missing_file_returns_500(client):
    """/api/files 請求不存在的檔案時 Flask 會拋出 FileNotFoundError（500）。"""
    response = client.get("/api/files?filename=nonexistent_demo_file.txt")
    assert response.status_code in (404, 500)


def test_path_traversal_no_param(client):
    """未提供 filename 時預設讀取 README.md，應回傳 200。"""
    response = client.get("/api/files")
    assert response.status_code == 200


# ── SSRF (CWE-918) ────────────────────────────────────────────────────────────

def test_ssrf_valid_url_returns_200(client):
    """/api/fetch 應將遠端回應轉發給呼叫端（使用 mock 避免外部網路依賴）。"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "<html>example</html>"
    with patch("src.vulnerabilities.ssrf.requests.get", return_value=mock_response):
        response = client.get("/api/fetch?url=https://example.com")
    assert response.status_code == 200


def test_ssrf_no_param_uses_default(client):
    """未提供 url 參數時應使用預設值 https://example.com。"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "default"
    with patch("src.vulnerabilities.ssrf.requests.get", return_value=mock_response):
        response = client.get("/api/fetch")
    assert response.status_code == 200


# ── Reflected XSS (CWE-79) ───────────────────────────────────────────────────

def test_xss_reflects_input(client):
    """/api/search 應將輸入反映在回應中（展示未逸出的危險行為）。"""
    response = client.get("/api/search?q=hello")
    assert response.status_code == 200
    assert b"hello" in response.data


def test_xss_script_tag_reflected(client):
    """展示 XSS：<script> 標籤應出現在回應中（未逸出）。"""
    response = client.get("/api/search?q=<script>alert(1)</script>")
    assert response.status_code == 200
    assert b"<script>" in response.data


# ── Insecure Deserialization (CWE-502) ───────────────────────────────────────

def test_deserialization_valid_payload(client):
    """/api/import 應接受合法的 base64 pickle 資料。"""
    payload = base64.b64encode(pickle.dumps({"key": "value"})).decode()
    response = client.post(
        "/api/import",
        data=payload,
        content_type="text/plain",
    )
    assert response.status_code == 200


def test_deserialization_invalid_payload_returns_error(client):
    """無效的 base64 輸入應被 pickle/base64 拒絕並回傳 500（由端點直接拋出）。"""
    response = client.post(
        "/api/import",
        data=b"not-valid-base64!!!",
        content_type="text/plain",
    )
    # pickle.loads 或 base64.b64decode 拋出例外 → Flask 回傳 500
    assert response.status_code in (400, 500)
