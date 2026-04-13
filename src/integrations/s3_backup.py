# ⚠️ 警告：此檔案含有刻意嵌入的假機密，用於展示 GHAzDO Secret Scanning 功能。
# 以下 Azure Storage 金鑰為虛假值，不具任何實際效力，僅用於觸發 Secret Scanning 偵測。
"""
Azure Blob Storage backup module.
Backs up files uploaded via the Path Traversal demo endpoint to Azure Blob Storage.

DEMO WORST PRACTICE: Azure Storage account key is hard-coded directly in source code
instead of using Managed Identity or environment variables.
"""

import urllib.request

# Secret #4 — Azure Storage Account Key
# Format: 88-character base64 string matching 'azure_storage_account_key'
# DEMO WORST PRACTICE: storage account key committed to source control; anyone with
# repo read access can exfiltrate all blobs in the storage account.
AZURE_STORAGE_ACCOUNT_NAME = "ghazdobackupdemo"
AZURE_STORAGE_ACCOUNT_KEY = "dGVzdFN0b3JhZ2VBY2NvdW50S2V5Rm9yR0hBekRPRGVtb1RoaXNJc0Zha2VBbmROb3RSZWFsS2V5QT09"  # noqa: S105

BLOB_CONTAINER = "vuln-demo-uploads"
BLOB_ENDPOINT = f"https://{AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net"


def upload_file_to_blob(local_path: str, blob_name: str) -> dict:
    """
    Upload a local file to Azure Blob Storage.

    DEMO WORST PRACTICE: Uses hard-coded storage account key instead of
    Managed Identity or Azure Key Vault. Never do this in production.
    """
    url = f"{BLOB_ENDPOINT}/{BLOB_CONTAINER}/{blob_name}"

    with open(local_path, "rb") as f:  # noqa: PTH123 — intentional path risk for demo
        data = f.read()

    req = urllib.request.Request(url, data=data, method="PUT")  # noqa: S310
    req.add_header("x-ms-blob-type", "BlockBlob")
    req.add_header("Authorization", f"SharedKey {AZURE_STORAGE_ACCOUNT_NAME}:{AZURE_STORAGE_ACCOUNT_KEY}")

    # NOTE: This does NOT execute in demo mode — the function exists solely
    # to demonstrate that Secret Scanning detects credentials in source code.
    return {
        "container": BLOB_CONTAINER,
        "blob": blob_name,
        "status": "demo_only_not_executed",
    }
