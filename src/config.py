"""
應用程式設定模組。
⚠️  本檔案刻意內嵌假機密與危險套件用法，用於展示 GHAzDO 的 Secret Scanning 與相依套件弱點掃描。
    以下所有機密均為虛假值，不具任何實際效力。
"""

import pathlib

import yaml  # pyyaml==5.3.1 — see pyproject.toml for CVE details

# ── Azure DevOps 設定 ─────────────────────────────────────────────────────────
AZURE_DEVOPS_ORG = "https://dev.azure.com/my-org"
AZURE_DEVOPS_PROJECT = "security-worst-practices"

# ⚠️  Secret #1：Azure DevOps PAT — 刻意寫死於原始碼觸發 Secret Scanning（正式環境應使用環境變數）
AZURE_DEVOPS_PAT = "4k3x2m8n5p7q9r1s6t0u2v4w6y8z3a5b7c9d1e3f5g7h9i1j3k5"  # noqa: S105

# ── Flask 基本設定 ────────────────────────────────────────────────────────────
FLASK_SECRET_KEY = "dev-only-not-for-production"  # noqa: S105
DEBUG = False

# ── 設定檔載入 ────────────────────────────────────────────────────────────────
# ⚠️  yaml.load() 不指定 Loader（CVE-2020-14343）— 刻意不安全用法，展示相依套件弱點掃描
_settings_path = pathlib.Path(__file__).parent.parent / "config" / "settings.yaml"
with open(_settings_path) as _f:  # noqa: PTH123
    APP_SETTINGS = yaml.load(_f)  # noqa: S506 — intentionally insecure for demo
