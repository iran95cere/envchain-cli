"""CLI commands for profile locking."""
from __future__ import annotations

import sys
from typing import Optional

from envchain.env_lock import LockManager


class LockCommand:
    """Expose lock/unlock/status sub-commands."""

    def __init__(self, storage_dir: str) -> None:
        self._manager = LockManager(storage_dir)

    def lock(self, profile: str, reason: str = "") -> None:
        if self._manager.is_locked(profile):
            print(f"Profile '{profile}' is already locked.")
            sys.exit(1)
        entry = self._manager.lock(profile, reason=reason)
        msg = f"Locked profile '{profile}'"
        if entry.reason:
            msg += f" — {entry.reason}"
        print(msg)

    def unlock(self, profile: str) -> None:
        if not self._manager.unlock(profile):
            print(f"Profile '{profile}' is not locked.")
            sys.exit(1)
        print(f"Unlocked profile '{profile}'.")

    def status(self, profile: str) -> None:
        entry = self._manager.get_entry(profile)
        if entry is None:
            print(f"Profile '{profile}' is not locked.")
        else:
            print(f"Profile '{profile}' is locked since {entry.locked_at}")
            if entry.reason:
                print(f"  Reason: {entry.reason}")

    def list_locked(self) -> None:
        entries = self._manager.list_locked()
        if not entries:
            print("No profiles are currently locked.")
            return
        for e in entries:
            line = f"  {e.profile}  (since {e.locked_at})"
            if e.reason:
                line += f"  [{e.reason}]"
            print(line)
