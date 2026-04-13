# ⚠️ 警告：此檔案含有刻意嵌入的假機密，用於展示 GHAzDO Secret Scanning 功能。
# 以下機密均為虛假值，不具任何實際效力，僅用於觸發 Secret Scanning 偵測。
"""
Application configuration module — contains intentionally fake secrets for
GHAzDO Secret Scanning demo purposes (Secret #1: Azure DevOps Personal Access Token).

Also demonstrates insecure use of PyYAML (Dep #3 / CVE-2020-14343):
yaml.load() is called without a Loader argument, enabling arbitrary object construction.
"""

import pathlib

import yaml  # pyyaml==5.3.1 — see pyproject.toml for CVE details

# Azure DevOps integration settings
AZURE_DEVOPS_ORG = "https://dev.azure.com/my-org"
AZURE_DEVOPS_PROJECT = "security-worst-practices"

# Secret #1 — Azure DevOps Personal Access Token
# Format: 52-character alphanumeric string matching 'azure_devops_personal_access_token'
# DEMO WORST PRACTICE: PAT hard-coded in source instead of read from environment variables.
AZURE_DEVOPS_PAT = "4k3x2m8n5p7q9r1s6t0u2v4w6y8z3a5b7c9d1e3f5g7h9i1j3k5"  # noqa: S105

# Flask settings
FLASK_SECRET_KEY = "dev-only-not-for-production"  # noqa: S105
DEBUG = False

# ⚠️ DEMO WORST PRACTICE: yaml.load() without Loader is unsafe (CVE-2020-14343).
# It allows arbitrary Python object construction from the YAML file,
# equivalent to pickle deserialization. Always use yaml.safe_load() in production.
_settings_path = pathlib.Path(__file__).parent.parent / "config" / "settings.yaml"
with open(_settings_path) as _f:  # noqa: PTH123
    APP_SETTINGS = yaml.load(_f)  # noqa: S506 — intentionally insecure for demo
