from typing import Any, Dict, Optional
from sqlalchemy.orm import Session
from app.core.logging import get_logger
from app.models.audit_event import AuditEvent

logger = get_logger("audit")


class AuditService:
    @staticmethod
    def record_event(
        db: Session,
        event_type: str,
        user_id: Optional[str] = None,
        resource_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AuditEvent:
        """
        Record a secure audit event.
        Ensures NO passwords, raw tokens, or sensitive medical reports are stored in audit logs.
        """
        safe_meta = {}
        if metadata:
            # Filter out sensitive keys
            blacklisted_keys = {"password", "token", "extracted_text", "report_text", "secret", "authorization"}
            for k, v in metadata.items():
                if k.lower() not in blacklisted_keys and not any(b in k.lower() for b in blacklisted_keys):
                    # Only store safe, non-medical primitive values or small dicts
                    if isinstance(v, (str, int, float, bool)) or v is None:
                        safe_meta[k] = v
                    elif isinstance(v, dict):
                        safe_meta[k] = {sk: sv for sk, sv in v.items() if isinstance(sv, (str, int, float, bool))}

        event = AuditEvent(
            user_id=user_id,
            event_type=event_type,
            resource_id=resource_id,
            safe_metadata=safe_meta,
        )
        db.add(event)
        try:
            db.commit()
            db.refresh(event)
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to record audit event: {e}")
        return event
