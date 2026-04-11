"""Watch profiles for external changes and emit events."""
from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional


@dataclass
class WatchEvent:
    profile_name: str
    event_type: str          # 'created' | 'modified' | 'deleted'
    detected_at: float = field(default_factory=time.time)

    def __repr__(self) -> str:
        return (
            f"WatchEvent(profile={self.profile_name!r}, "
            f"type={self.event_type!r})"
        )

    def to_dict(self) -> dict:
        return {
            "profile_name": self.profile_name,
            "event_type": self.event_type,
            "detected_at": self.detected_at,
        }


class ProfileWatcher:
    """Poll-based watcher that detects file-level changes in a storage directory."""

    def __init__(self, storage_dir: str, poll_interval: float = 1.0) -> None:
        self._dir = storage_dir
        self.poll_interval = poll_interval
        self._snapshots: Dict[str, float] = {}
        self._handlers: List[Callable[[WatchEvent], None]] = []

    # ------------------------------------------------------------------
    def on_change(self, handler: Callable[[WatchEvent], None]) -> None:
        """Register a callback invoked with each WatchEvent."""
        self._handlers.append(handler)

    def _emit(self, event: WatchEvent) -> None:
        for h in self._handlers:
            h(event)

    # ------------------------------------------------------------------
    def _current_mtimes(self) -> Dict[str, float]:
        result: Dict[str, float] = {}
        if not os.path.isdir(self._dir):
            return result
        for fname in os.listdir(self._dir):
            if fname.endswith(".enc"):
                fpath = os.path.join(self._dir, fname)
                try:
                    result[fname] = os.path.getmtime(fpath)
                except OSError:
                    pass
        return result

    def poll(self) -> List[WatchEvent]:
        """Single poll cycle; returns list of detected events."""
        current = self._current_mtimes()
        events: List[WatchEvent] = []

        for fname, mtime in current.items():
            profile = fname[:-4]  # strip .enc
            if fname not in self._snapshots:
                ev = WatchEvent(profile, "created")
                events.append(ev)
                self._emit(ev)
            elif self._snapshots[fname] != mtime:
                ev = WatchEvent(profile, "modified")
                events.append(ev)
                self._emit(ev)

        for fname in list(self._snapshots):
            if fname not in current:
                profile = fname[:-4]
                ev = WatchEvent(profile, "deleted")
                events.append(ev)
                self._emit(ev)

        self._snapshots = current
        return events

    def run(self, max_cycles: Optional[int] = None) -> None:
        """Block and poll indefinitely (or up to *max_cycles* iterations)."""
        cycles = 0
        while max_cycles is None or cycles < max_cycles:
            self.poll()
            time.sleep(self.poll_interval)
            cycles += 1
