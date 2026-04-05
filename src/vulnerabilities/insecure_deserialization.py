# 漏洞：Insecure Deserialization (CWE-502) — py/unsafe-deserialization
"""
Insecure Deserialization demo endpoint.
The request body is decoded from base64 and passed directly to pickle.loads()
without any validation, allowing an attacker to execute arbitrary code via
a crafted pickle payload.
"""

import base64
import pickle

from flask import Blueprint, jsonify, request

deserialization_bp = Blueprint("deserialization", __name__)


@deserialization_bp.route("/api/import", methods=["POST"])
def import_data():
    """Import base64-encoded data — VULNERABLE to Insecure Deserialization."""
    data = request.get_data()

    # VULNERABILITY: user-controlled data is deserialized with pickle without validation
    obj = pickle.loads(base64.b64decode(data))

    return jsonify({"imported": repr(obj)})
