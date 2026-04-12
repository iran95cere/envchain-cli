"""CLI command for cascaded profile resolution."""
from __future__ import annotations

import sys
from typing import List

from envchain.env_cascade import EnvCascade
from envchain.storage import EnvStorage


class CascadeCommand:
    """Resolve and display variables merged from multiple profiles."""

    def __init__(self, storage: EnvStorage, password: str) -> None:
        self._storage = storage
        self._password = password
        self._cascade = EnvCascade()

    def run(self, profile_names: List[str], *, show_source: bool = False) -> None:
        """Merge *profile_names* (highest priority first) and print variables."""
        if not profile_names:
            print("error: at least one profile name is required", file=sys.stderr)
            sys.exit(1)

        profiles = []
        for name in profile_names:
            data = self._storage.load_profile(name, self._password)
            if data is None:
                print(f"error: profile '{name}' not found", file=sys.stderr)
                sys.exit(1)
            profiles.append((name, data.variables))

        result = self._cascade.resolve(profiles)

        if not result.resolved:
            print("(no variables found in supplied profiles)")
            return

        for var_name in sorted(result.resolved):
            source = result.resolved[var_name]
            if show_source:
                print(f"{var_name}={source.value}  # from '{source.profile}'")
            else:
                print(f"{var_name}={source.value}")

    def show_sources(self, profile_names: List[str]) -> None:
        """Print a table showing which profile each variable originates from."""
        if not profile_names:
            print("error: at least one profile name is required", file=sys.stderr)
            sys.exit(1)

        profiles = []
        for name in profile_names:
            data = self._storage.load_profile(name, self._password)
            if data is None:
                print(f"error: profile '{name}' not found", file=sys.stderr)
                sys.exit(1)
            profiles.append((name, data.variables))

        result = self._cascade.resolve(profiles)
        print(f"{'VARIABLE':<30} {'SOURCE PROFILE':<20} PRIORITY")
        print("-" * 60)
        for var_name in sorted(result.resolved):
            src = result.resolved[var_name]
            print(f"{var_name:<30} {src.profile:<20} {src.priority}")
