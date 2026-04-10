"""CLI commands for managing profile aliases."""
from __future__ import annotations

import sys
from typing import Optional

from envchain.alias import AliasManager


class AliasCommand:
    """Handles alias sub-commands: add, remove, list, resolve."""

    def __init__(self, storage_dir: str) -> None:
        self._mgr = AliasManager(storage_dir)

    # ------------------------------------------------------------------
    # Sub-commands
    # ------------------------------------------------------------------

    def add(self, alias: str, profile: str) -> None:
        """Add a new alias."""
        try:
            self._mgr.add(alias, profile)
            print(f"Alias '{alias}' -> '{profile}' added.")
        except ValueError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)

    def remove(self, alias: str) -> None:
        """Remove an existing alias."""
        removed = self._mgr.remove(alias)
        if removed:
            print(f"Alias '{alias}' removed.")
        else:
            print(f"Alias '{alias}' not found.", file=sys.stderr)
            sys.exit(1)

    def list_aliases(self) -> None:
        """Print all aliases."""
        entries = self._mgr.list_aliases()
        if not entries:
            print("No aliases defined.")
            return
        width = max(len(e["alias"]) for e in entries)
        for entry in entries:
            print(f"  {entry['alias']:<{width}}  ->  {entry['profile']}")

    def resolve(self, alias: str) -> None:
        """Print the profile name for *alias*, or exit with error."""
        profile: Optional[str] = self._mgr.resolve(alias)
        if profile is None:
            print(f"Alias '{alias}' not found.", file=sys.stderr)
            sys.exit(1)
        print(profile)
