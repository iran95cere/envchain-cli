"""CLI commands for the env changelog feature."""
from __future__ import annotations

import sys
from envchain.env_changelog import ChangelogManager


class ChangelogCommand:
    def __init__(self, storage_dir: str) -> None:
        self._manager = ChangelogManager(storage_dir)

    def show(self, profile: str | None = None) -> None:
        """Print changelog entries, optionally filtered by profile."""
        entries = (
            self._manager.entries_for_profile(profile)
            if profile
            else self._manager.all_entries()
        )
        if not entries:
            print("No changelog entries found.")
            return
        for e in entries:
            ts = f"{e.timestamp:.0f}"
            old = e.old_value if e.old_value is not None else "<none>"
            new = e.new_value if e.new_value is not None else "<none>"
            print(f"[{ts}] {e.profile} | {e.action:6s} | {e.var_name} | {old} -> {new}")

    def clear(self, profile: str | None = None) -> None:
        """Clear changelog entries, optionally scoped to a profile."""
        removed = self._manager.clear(profile)
        scope = f"profile '{profile}'" if profile else "all profiles"
        print(f"Removed {removed} changelog entry/entries for {scope}.")

    def last(self, n: int = 10, profile: str | None = None) -> None:
        """Print the last N changelog entries."""
        entries = (
            self._manager.entries_for_profile(profile)
            if profile
            else self._manager.all_entries()
        )
        for e in entries[-n:]:
            print(repr(e))
        if not entries:
            print("No entries.")
