"""CLI command for reordering environment variables within a profile."""
from __future__ import annotations
import sys
from typing import List

from envchain.env_reorder import EnvReorder
from envchain.storage import EnvStorage


class ReorderCommand:
    def __init__(self, storage: EnvStorage) -> None:
        self._storage = storage
        self._reorder = EnvReorder()

    def run(self, profile: str, password: str, key_order: List[str],
            dry_run: bool = False) -> None:
        """Reorder variables in *profile* according to *key_order*."""
        data = self._storage.load_profile(profile, password)
        if data is None:
            print(f"Profile '{profile}' not found.", file=sys.stderr)
            sys.exit(1)

        result = self._reorder.reorder(data, key_order, profile=profile)

        if result.unknown_keys:
            print(f"Warning: unknown keys ignored: {', '.join(result.unknown_keys)}")

        if not result.is_changed:
            print("Order unchanged — nothing to do.")
            return

        if dry_run:
            print("Dry-run: new order would be:")
            for k in result.new_order:
                print(f"  {k}")
            return

        reordered = self._reorder.apply(data, key_order)
        self._storage.save_profile(profile, reordered, password)
        print(f"Reordered {result.moved_count} variable(s) in profile '{profile}'.")

    def show_order(self, profile: str, password: str) -> None:
        """Print the current variable order for *profile*."""
        data = self._storage.load_profile(profile, password)
        if data is None:
            print(f"Profile '{profile}' not found.", file=sys.stderr)
            sys.exit(1)
        if not data:
            print("No variables defined.")
            return
        for i, k in enumerate(data.keys(), 1):
            print(f"  {i:>3}. {k}")
