"""Scheduled profile actions — e.g. auto-expire or timed activation."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class ScheduledAction:
    profile_name: str
    action: str          # 'activate' | 'deactivate' | 'expire'
    run_at: float        # Unix timestamp
    repeat_seconds: Optional[int] = None
    last_run: Optional[float] = None

    def is_due(self, now: Optional[float] = None) -> bool:
        now = now if now is not None else time.time()
        return now >= self.run_at

    def to_dict(self) -> dict:
        return {
            "profile_name": self.profile_name,
            "action": self.action,
            "run_at": self.run_at,
            "repeat_seconds": self.repeat_seconds,
            "last_run": self.last_run,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ScheduledAction":
        return cls(
            profile_name=data["profile_name"],
            action=data["action"],
            run_at=float(data["run_at"]),
            repeat_seconds=data.get("repeat_seconds"),
            last_run=data.get("last_run"),
        )

    def __repr__(self) -> str:
        return (
            f"ScheduledAction(profile={self.profile_name!r}, "
            f"action={self.action!r}, run_at={self.run_at})"
        )


class Scheduler:
    """Persist and query scheduled profile actions."""

    FILENAME = "schedule.json"

    def __init__(self, storage_dir: str) -> None:
        self._path = Path(storage_dir) / self.FILENAME
        self._actions: List[ScheduledAction] = self._load()

    def _load(self) -> List[ScheduledAction]:
        if not self._path.exists():
            return []
        with self._path.open() as fh:
            return [ScheduledAction.from_dict(d) for d in json.load(fh)]

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("w") as fh:
            json.dump([a.to_dict() for a in self._actions], fh, indent=2)

    def add(self, action: ScheduledAction) -> None:
        self._actions.append(action)
        self._save()

    def remove(self, profile_name: str, action: str) -> bool:
        before = len(self._actions)
        self._actions = [
            a for a in self._actions
            if not (a.profile_name == profile_name and a.action == action)
        ]
        if len(self._actions) < before:
            self._save()
            return True
        return False

    def due_actions(self, now: Optional[float] = None) -> List[ScheduledAction]:
        return [a for a in self._actions if a.is_due(now)]

    def all_actions(self) -> List[ScheduledAction]:
        return list(self._actions)
