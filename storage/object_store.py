"""
TruthLens - Object Storage Service (MinIO / S3 with Local Fallback)
Handles cryptographic integrity hashing (SHA-256), MIME-type classification,
and upload to MinIO/S3 or resilient local forensic vault.
"""

import os
import io
import hashlib
import mimetypes
from typing import Tuple, Dict, Any, Optional

# Storage configuration
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "truthlens-evidence")
MINIO_SECURE = os.getenv("MINIO_SECURE", "false").lower() == "true"

LOCAL_VAULT_DIR = os.getenv("LOCAL_VAULT_DIR", os.path.join(os.path.dirname(__file__), "..", "vault"))


class ObjectStorageService:
    """Manages secure evidentiary file storage across MinIO/S3 and local disk vault."""

    def __init__(self):
        self.bucket = MINIO_BUCKET
        self.client = None
        self._init_minio_client()
        os.makedirs(LOCAL_VAULT_DIR, exist_ok=True)

    def _init_minio_client(self):
        """Attempts connection to MinIO / S3 service if minio or boto3 is installed."""
        try:
            from minio import Minio
            self.client = Minio(
                MINIO_ENDPOINT,
                access_key=MINIO_ACCESS_KEY,
                secret_key=MINIO_SECRET_KEY,
                secure=MINIO_SECURE
            )
            # Create bucket if it doesn't exist
            if not self.client.bucket_exists(self.bucket):
                self.client.make_bucket(self.bucket)
        except Exception:
            # MinIO not available or minio package not installed; fallback to local vault
            self.client = None

    def store_file(
        self,
        file_bytes: bytes,
        original_filename: str,
        case_id: str,
        modality: str
    ) -> Dict[str, Any]:
        """
        Computes SHA-256, detects MIME type, and saves to MinIO/S3 or local forensic vault.
        Returns metadata dictionary.
        """
        # 1. Compute SHA-256 hash
        sha256 = hashlib.sha256(file_bytes).hexdigest()
        md5 = hashlib.md5(file_bytes).hexdigest()
        size_bytes = len(file_bytes)

        # 2. Detect MIME type
        mime_type, _ = mimetypes.guess_type(original_filename)
        if not mime_type:
            # Fallback by modality
            modality_mimes = {
                "image": "image/jpeg",
                "video": "video/mp4",
                "audio": "audio/wav",
                "text": "text/plain"
            }
            mime_type = modality_mimes.get(modality.lower(), "application/octet-stream")

        storage_key = f"evidence/{case_id}/{sha256[:12]}/{original_filename}"
        storage_backend = "local_vault"

        # 3. Store in MinIO if available
        if self.client:
            try:
                self.client.put_object(
                    self.bucket,
                    storage_key,
                    io.BytesIO(file_bytes),
                    length=size_bytes,
                    content_type=mime_type
                )
                storage_backend = f"minio://{self.bucket}/{storage_key}"
            except Exception:
                # If MinIO put fails, fall back to local disk
                storage_backend = "local_vault"

        # 4. Always ensure local persistent copy in forensic vault
        local_path = os.path.join(LOCAL_VAULT_DIR, f"{sha256}_{original_filename}")
        if not os.path.exists(local_path):
            with open(local_path, "wb") as f:
                f.write(file_bytes)

        return {
            "storage_key": storage_key,
            "storage_backend": storage_backend,
            "local_path": local_path,
            "sha256": sha256,
            "md5": md5,
            "mime_type": mime_type,
            "size_bytes": size_bytes,
            "original_filename": original_filename
        }

    def retrieve_file(self, sha256: str, original_filename: str) -> Optional[bytes]:
        """Retrieves raw evidence file bytes."""
        local_path = os.path.join(LOCAL_VAULT_DIR, f"{sha256}_{original_filename}")
        if os.path.exists(local_path):
            with open(local_path, "rb") as f:
                return f.read()

        if self.client:
            try:
                response = self.client.get_object(self.bucket, f"evidence/{sha256[:12]}/{original_filename}")
                return response.read()
            except Exception:
                pass
        return None


# Global singleton instance
storage_service = ObjectStorageService()
