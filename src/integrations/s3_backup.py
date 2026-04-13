# ⚠️ 警告：此檔案含有刻意嵌入的假機密，用於展示 GHAzDO Secret Scanning 功能。
# 以下 AWS 金鑰均為虛假值，不具任何實際效力，僅用於觸發 Secret Scanning 偵測。
"""
S3 backup integration for uploaded files.
Simulates backing up files from the Path Traversal demo endpoint to AWS S3.

DEMO WORST PRACTICE: AWS credentials are hard-coded directly in source code.
"""

import urllib.request

# Secret #4 — AWS Access Key ID + Secret Access Key
# Format: AKIA[A-Z0-9]{16} matching 'aws_access_key_id'
AWS_ACCESS_KEY_ID = "AKIADEMOGHAZDO000001"  # noqa: S105
AWS_SECRET_ACCESS_KEY = "wJa8Q/dEmO+KEYghAzDoFaKeAbCdEfGhIjKlMnOp"  # noqa: S105

# S3 bucket for storing uploaded demo files
S3_BUCKET = "ghazdo-vuln-demo-uploads"
S3_REGION = "ap-northeast-1"


def upload_file_to_s3(local_path: str, s3_key: str) -> dict:
    """
    Upload a local file to S3.

    DEMO WORST PRACTICE: Uses hard-coded credentials instead of IAM roles
    or environment variables. Never do this in production.
    """
    # Construct a minimal S3 PUT request using only stdlib (no boto3)
    # so the dependency footprint stays small for the demo.
    url = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{s3_key}"

    with open(local_path, "rb") as f:  # noqa: PTH123 — intentional path risk for demo
        data = f.read()

    req = urllib.request.Request(url, data=data, method="PUT")  # noqa: S310
    req.add_header("x-amz-content-sha256", "UNSIGNED-PAYLOAD")

    # NOTE: This is intentionally simplified — real S3 uploads require SigV4 signing.
    # The credentials above exist solely to demonstrate that Secret Scanning
    # detects AWS keys committed to source control.
    return {
        "bucket": S3_BUCKET,
        "key": s3_key,
        "status": "demo_only_not_executed",
    }
