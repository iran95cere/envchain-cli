"""Notification system for envchain events."""
from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Dict, List, Optional


class NotifyLevel(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class Notification:
    message: str
    level: NotifyLevel = NotifyLevel.INFO
    profile: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.datetime.utcnow().isoformat())

    def to_dict(self) -> Dict:
        return {
            "message": self.message,
            "level": self.level.value,
            "profile": self.profile,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Notification":
        return cls(
            message=data["message"],
            level=NotifyLevel(data.get("level", "info")),
            profile=data.get("profile"),
            timestamp=data.get("timestamp", datetime.datetime.utcnow().isoformat()),
        )

    def __repr__(self) -> str:
        return f"Notification(level={self.level.value!r}, profile={self.profile!r}, message={self.message!r})"


NotifyHandler = Callable[[Notification], None]


class NotificationBus:
    """Simple in-process notification bus."""

    def __init__(self) -> None:
        self._handlers: List[NotifyHandler] = []
        self._history: List[Notification] = []

    def subscribe(self, handler: NotifyHandler) -> None:
        self._handlers.append(handler)

    def unsubscribe(self, handler: NotifyHandler) -> None:
        self._handlers = [h for h in self._handlers if h is not handler]

    def publish(self, notification: Notification) -> None:
        self._history.append(notification)
        for handler in self._handlers:
            handler(notification)

    def notify(self, message: str, level: NotifyLevel = NotifyLevel.INFO,
               profile: Optional[str] = None) -> Notification:
        n = Notification(message=message, level=level, profile=profile)
        self.publish(n)
        return n

    def history(self, profile: Optional[str] = None) -> List[Notification]:
        if profile is None:
            return list(self._history)
        return [n for n in self._history if n.profile == profile]

    def clear_history(self) -> None:
        self._history.clear()
