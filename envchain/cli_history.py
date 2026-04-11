"""CLI command for viewing and managing profile change history."""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

from envchain.env_history import HistoryManager


class HistoryCommand:
    def __init__(self, history_dir: Path) -> None:
        self._manager = HistoryManager(history_dir)

    def show(self, profile: str, limit: int = 20) -> None:
        entries = self._manager.get_history(profile)
        if not entries:
            print(f"No history found for profile '{profile}'.")
            return
        for entry in reversed(entries[-limit:]):
            ts = datetime.fromtimestamp(entry.timestamp).strftime("%Y-%m-%d %H:%M:%S")
            key_part = f" [{entry.key}]" if entry.key else ""
            print(f"{ts}  {entry.action:<8}{key_part}")

    def clear(self, profile: str) -> None:
        self._manager.clear_history(profile)
        print(f"History cleared for profile '{profile}'.")

    def last(self, profile: str) -> None:
        entry = self._manager.last_entry(profile)
        if entry is None:
            print(f"No history found for profile '{profile}'.")
            sys.exit(1)
        ts = datetime.fromtimestamp(entry.timestamp).strftime("%Y-%m-%d %H:%M:%S")
        key_part = f" [{entry.key}]" if entry.key else ""
        print(f"{ts}  {entry.action}{key_part}")
