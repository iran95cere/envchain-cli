"""CLI command: envchain watch — monitor a profile directory for changes."""
from __future__ import annotations

import sys
from typing import Optional

from envchain.env_watch import ProfileWatcher, WatchEvent


class WatchCommand:
    def __init__(self, storage_dir: str, poll_interval: float = 1.0) -> None:
        self._dir = storage_dir
        self._interval = poll_interval

    # ------------------------------------------------------------------
    def run(
        self,
        profile_filter: Optional[str] = None,
        max_cycles: Optional[int] = None,
        out=sys.stdout,
    ) -> None:
        """Start watching; print events as they arrive."""
        watcher = ProfileWatcher(self._dir, poll_interval=self._interval)

        def _handler(event: WatchEvent) -> None:
            if profile_filter and event.profile_name != profile_filter:
                return
            icon = {"created": "+", "modified": "~", "deleted": "-"}.get(
                event.event_type, "?"
            )
            out.write(f"[{icon}] {event.event_type}: {event.profile_name}\n")
            out.flush()

        watcher.on_change(_handler)

        try:
            watcher.run(max_cycles=max_cycles)
        except KeyboardInterrupt:
            out.write("\nWatch stopped.\n")

    # ------------------------------------------------------------------
    def show_status(self, out=sys.stdout) -> None:
        """Print a one-shot snapshot of all tracked profiles."""
        watcher = ProfileWatcher(self._dir)
        mtimes = watcher._current_mtimes()
        if not mtimes:
            out.write("No profiles found in storage directory.\n")
            return
        out.write(f"{'Profile':<30} {'Last Modified'}\n")
        out.write("-" * 50 + "\n")
        for fname, mtime in sorted(mtimes.items()):
            import datetime
            ts = datetime.datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
            out.write(f"{fname[:-4]:<30} {ts}\n")
