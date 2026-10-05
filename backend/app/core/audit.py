"""
VERIFAI - Security Audit Logging Engine
Appends tamper-evident audit logs to the relational database.
Never records raw passwords, plaintext tokens, or document binary contents.
"""
import json
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import compute_sha256
from app.domain.models import AuditLog


async def log_security_event(
    db: AsyncSession,
    event_type: str,
    status: str = "SUCCESS",
    user_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
) -> AuditLog:
    """
    Record an immutable audit log entry.
    Computes a SHA-256 checksum of normalized details for integrity.
    """
    clean_details = details.copy() if details else {}
    
    # Strip any potential sensitive fields before hashing and persisting
    for sensitive_key in ["password", "token", "raw_content", "access_token", "refresh_token"]:
        if sensitive_key in clean_details:
            clean_details[sensitive_key] = "[REDACTED]"

    normalized_str = json.dumps(clean_details, sort_keys=True)
    metadata_hash = compute_sha256(normalized_str.encode("utf-8"))

    audit_entry = AuditLog(
        user_id=user_id,
        event_type=event_type,
        status=status,
        ip_address=ip_address,
        metadata_hash=metadata_hash,
        details=clean_details
    )

    db.add(audit_entry)
    await db.flush()
    return audit_entry
