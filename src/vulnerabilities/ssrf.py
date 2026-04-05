# 漏洞：Server-Side Request Forgery (CWE-918) — py/full-ssrf
"""
SSRF demo endpoint.
The user-supplied 'url' parameter is passed directly to requests.get() without
URL validation, allowing an attacker to make the server issue requests to
internal or arbitrary external addresses.
"""

import requests
from flask import Blueprint, jsonify, request

ssrf_bp = Blueprint("ssrf", __name__)


@ssrf_bp.route("/api/fetch")
def fetch_url():
    """Fetch a remote URL — VULNERABLE to Server-Side Request Forgery (SSRF)."""
    url = request.args.get("url", "https://example.com")

    # VULNERABILITY: user-supplied URL is passed directly to requests.get() without validation
    response = requests.get(url, timeout=5)

    return jsonify({
        "status_code": response.status_code,
        "content": response.text[:500],
    })
