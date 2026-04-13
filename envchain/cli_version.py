"""CLI commands for profile version tracking."""
from __future__ import annotations

import sys
from typing import Optional

from envchain.env_version import VersionManager


class VersionCommand:
    def __init__(self, storage_dir: str, profile: str) -> None:
        self._manager = VersionManager(storage_dir, profile)
        self._profile = profile

    def commit(
        self,
        vars_snapshot: dict,
        message: str = "",
        author: str = "",
    ) -> None:
        entry = self._manager.commit(vars_snapshot, message=message, author=author)
        print(f"[version] Committed v{entry.version} for profile '{self._profile}'.")
        if message:
            print(f"  Message : {message}")
        if author:
            print(f"  Author  : {author}")

    def log(self) -> None:
        entries = self._manager.history()
        if not entries:
            print(f"No version history for profile '{self._profile}'.")
            return
        for e in reversed(entries):
            import datetime
            ts = datetime.datetime.fromtimestamp(e.timestamp).strftime("%Y-%m-%d %H:%M:%S")
            author_part = f" ({e.author})" if e.author else ""
            msg_part = f" — {e.message}" if e.message else ""
            print(f"  v{e.version}  {ts}{author_part}{msg_part}")

    def show(self, version: int) -> None:
        entry = self._manager.get(version)
        if entry is None:
            print(f"Version {version} not found for profile '{self._profile}'.")
            sys.exit(1)
        print(f"Profile : {entry.profile}")
        print(f"Version : {entry.version}")
        if entry.author:
            print(f"Author  : {entry.author}")
        if entry.message:
            print(f"Message : {entry.message}")
        print("Variables:")
        if entry.snapshot:
            for k, v in sorted(entry.snapshot.items()):
                print(f"  {k}={v}")
        else:
            print("  (empty)")

    def latest(self) -> None:
        entry = self._manager.latest()
        if entry is None:
            print(f"No versions recorded for profile '{self._profile}'.")
            return
        print(f"Latest version for '{self._profile}': v{entry.version}")
        if entry.message:
            print(f"  {entry.message}")

    def clear(self) -> None:
        self._manager.clear()
        print(f"Version history cleared for profile '{self._profile}'.")
