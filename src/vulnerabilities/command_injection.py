# 漏洞：OS Command Injection (CWE-78) — py/command-line-injection
"""
OS Command Injection demo endpoint.
The user-supplied 'host' parameter is passed directly to os.system() via shell=True,
allowing an attacker to inject arbitrary shell commands.
"""

import subprocess

from flask import Blueprint, jsonify, request

command_injection_bp = Blueprint("command_injection", __name__)


@command_injection_bp.route("/api/ping")
def ping():
    """Ping a host — VULNERABLE to OS Command Injection."""
    host = request.args.get("host", "localhost")

    # VULNERABILITY: user input is passed directly to the shell without validation
    result = subprocess.run(
        f"ping -c 1 {host}",
        shell=True,
        capture_output=True,
        text=True,
        timeout=5,
    )

    return jsonify({"result": result.stdout + result.stderr})
