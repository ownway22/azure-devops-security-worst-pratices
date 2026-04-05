# ⚠️ 警告：此檔案含有刻意嵌入的假機密，用於展示 GHAzDO Secret Scanning 功能。
# 以下機密均為虛假值，不具任何實際效力，僅用於觸發 Secret Scanning 偵測。
"""
Application configuration module — contains intentionally fake secrets for
GHAzDO Secret Scanning demo purposes (Secret #1: Azure Service Principal Client Secret).
"""

# Azure Service Principal settings
AZURE_TENANT_ID = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
AZURE_CLIENT_ID = "yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy"

# Secret #1 — Azure Active Directory Application Secret
# Format: 40-character Base64-like string matching 'azure_active_directory_application_secret'
AZURE_CLIENT_SECRET = "wJa8Q~bFkL2mNpRtXvZcDhYeGsUiOjKqWnMaB3Cd"  # noqa: S105

# Flask settings
FLASK_SECRET_KEY = "dev-only-not-for-production"  # noqa: S105
DEBUG = False
