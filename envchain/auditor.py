"""Audit log for tracking profile access and modifications."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional


AUDIT_LOG_FILENAME = "audit.log"


class AuditEvent:
    """Represents a single audit log entry."""

    def __init__(self, action: str, profile: str, detail: Optional[str] = None):
        self.action = action
        self.profile = profile
        self.detail = detail
        self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "action": self.action,
            "profile": self.profile,
            "detail": self.detail,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AuditEvent":
        event = cls(
            action=data["action"],
            profile=data["profile"],
            detail=data.get("detail"),
        )
        event.timestamp = data["timestamp"]
        return event

    def __repr__(self) -> str:
        detail_str = f" ({self.detail})" if self.detail else ""
        return f"[{self.timestamp}] {self.action} profile={self.profile}{detail_str}"


class EnvAuditor:
    """Records and retrieves audit events for envchain operations."""

    def __init__(self, base_dir: str):
        self.log_path = Path(base_dir) / AUDIT_LOG_FILENAME

    def record(self, action: str, profile: str, detail: Optional[str] = None) -> None:
        """Append an audit event to the log file."""
        event = AuditEvent(action=action, profile=profile, detail=detail)
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event.to_dict()) + "\n")

    def read_events(self, profile: Optional[str] = None, limit: int = 50) -> List[AuditEvent]:
        """Read audit events, optionally filtered by profile."""
        if not self.log_path.exists():
            return []

        events = []
        with open(self.log_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    event = AuditEvent.from_dict(data)
                    if profile is None or event.profile == profile:
                        events.append(event)
                except (json.JSONDecodeError, KeyError):
                    continue

        return events[-limit:]

    def clear(self) -> None:
        """Remove the audit log file."""
        if self.log_path.exists():
            self.log_path.unlink()
