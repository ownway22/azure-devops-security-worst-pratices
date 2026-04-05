# 漏洞：SQL Injection (CWE-89) — py/sql-injection
"""
SQL Injection demo endpoint.
The user-supplied 'name' parameter is concatenated directly into the SQL query
without sanitization, allowing an attacker to manipulate the query logic.
"""

from flask import Blueprint, jsonify, request

from src.database import get_db_connection

sql_injection_bp = Blueprint("sql_injection", __name__)


@sql_injection_bp.route("/api/users")
def get_users():
    """Return users matching the given name — VULNERABLE to SQL Injection."""
    name = request.args.get("name", "")

    conn = get_db_connection()
    # VULNERABILITY: user input is directly interpolated into the SQL query
    query = f"SELECT * FROM users WHERE name = '{name}'"
    cursor = conn.execute(query)
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify({"users": rows})
