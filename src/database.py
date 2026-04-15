"""SQLite 記憶體資料庫初始化 — 提供漏洞展示所需的測試資料。"""

import sqlite3


def get_db_connection() -> sqlite3.Connection:
    """建立並回傳含有測試資料的 SQLite 記憶體連線。"""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id    INTEGER PRIMARY KEY,
            name  TEXT NOT NULL,
            email TEXT NOT NULL
        )
        """
    )

    sample_users = [
        (1, "Alice", "alice@example.com"),
        (2, "Bob", "bob@example.com"),
        (3, "Charlie", "charlie@example.com"),
        (4, "Diana", "diana@example.com"),
        (5, "Eve", "eve@example.com"),
    ]
    conn.executemany("INSERT INTO users (id, name, email) VALUES (?, ?, ?)", sample_users)
    conn.commit()

    return conn
