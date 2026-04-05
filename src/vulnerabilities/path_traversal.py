# 漏洞：Path Traversal (CWE-22) — py/path-injection
"""
Path Traversal demo endpoint.
The user-supplied 'filename' parameter is used directly in open() without
path validation, allowing an attacker to read arbitrary files on the server.
"""

from flask import Blueprint, Response, request

path_traversal_bp = Blueprint("path_traversal", __name__)


@path_traversal_bp.route("/api/files")
def read_file():
    """Return the contents of a file — VULNERABLE to Path Traversal."""
    filename = request.args.get("filename", "README.md")

    # VULNERABILITY: user input is passed directly to open() without path validation
    with open(filename, "r") as f:
        content = f.read()

    return Response(content, mimetype="text/plain")
