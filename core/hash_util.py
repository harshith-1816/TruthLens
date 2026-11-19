"""
TruthLens - Hash and Cryptographic Verification Utilities
Computes SHA-256, MD5, file integrity, and chain of custody tracking.
"""

import hashlib
import os
from typing import Dict, Tuple, Optional
from datetime import datetime, timezone
from core.models import ChainOfCustodyRecord


def compute_file_hashes(file_path_or_bytes: bytes | str) -> Tuple[str, str, int]:
    """
    Returns (sha256, md5, size_in_bytes) for either a filepath or raw bytes.
    """
    sha256 = hashlib.sha256()
    md5 = hashlib.md5()

    if isinstance(file_path_or_bytes, bytes):
        data = file_path_or_bytes
        sha256.update(data)
        md5.update(data)
        return sha256.hexdigest(), md5.hexdigest(), len(data)
    
    file_path = str(file_path_or_bytes)
    size = os.path.getsize(file_path)
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            sha256.update(chunk)
            md5.update(chunk)
            
    return sha256.hexdigest(), md5.hexdigest(), size


def create_custody_record(
    event: str,
    file_name: str,
    sha256: str,
    performed_by: str = "TruthLens Automated Ingestion Pipeline",
    notes: Optional[str] = None
) -> ChainOfCustodyRecord:
    """Creates an evidentiary audit trail event."""
    return ChainOfCustodyRecord(
        timestamp=datetime.now(timezone.utc).isoformat(),
        event=event,
        performed_by=performed_by,
        file_name=file_name,
        sha256=sha256,
        notes=notes
    )
