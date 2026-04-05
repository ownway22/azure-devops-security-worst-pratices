# 漏洞：Reflected XSS (CWE-79) — py/reflective-xss
"""
Reflected XSS demo endpoint.
The user-supplied 'q' parameter is reflected directly into the HTML response
without output encoding, allowing an attacker to inject malicious scripts.
"""

from flask import Blueprint, make_response, request

xss_bp = Blueprint("xss", __name__)


@xss_bp.route("/api/search")
def search():
    """Return search results — VULNERABLE to Reflected XSS."""
    q = request.args.get("q", "")

    # VULNERABILITY: user input is embedded directly in HTML without escaping
    html = f"<h1>搜尋結果：{q}</h1>"
    response = make_response(html)
    response.headers["Content-Type"] = "text/html"

    return response
