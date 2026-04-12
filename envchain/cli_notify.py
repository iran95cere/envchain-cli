"""CLI commands for the notification system."""
from __future__ import annotations

from typing import Optional

from envchain.env_notify import NotificationBus, NotifyLevel


class NotifyCommand:
    def __init__(self, bus: NotificationBus) -> None:
        self._bus = bus

    def show_history(self, profile: Optional[str] = None) -> None:
        entries = self._bus.history(profile=profile)
        if not entries:
            label = f" for profile '{profile}'" if profile else ""
            print(f"No notifications{label}.")
            return
        for n in entries:
            tag = f"[{n.profile}] " if n.profile else ""
            print(f"{n.timestamp}  {n.level.value.upper():<8}  {tag}{n.message}")

    def clear(self) -> None:
        self._bus.clear_history()
        print("Notification history cleared.")

    def send(self, message: str, level: str = "info",
             profile: Optional[str] = None) -> None:
        try:
            lvl = NotifyLevel(level.lower())
        except ValueError:
            valid = ", ".join(v.value for v in NotifyLevel)
            print(f"Unknown level '{level}'. Valid levels: {valid}")
            raise SystemExit(1)
        n = self._bus.notify(message, level=lvl, profile=profile)
        print(f"Notification sent: [{n.level.value}] {n.message}")

    def count(self, profile: Optional[str] = None) -> None:
        entries = self._bus.history(profile=profile)
        label = f" for profile '{profile}'" if profile else ""
        print(f"{len(entries)} notification(s){label}.")
