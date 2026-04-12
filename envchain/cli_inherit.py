"""CLI command for profile inheritance resolution."""
from __future__ import annotations

import getpass
import sys
from typing import Optional

from envchain.env_inherit import InheritanceError, ProfileInheriter


class InheritCommand:
    """Resolve and display merged environment variables via profile inheritance."""

    def __init__(self, storage) -> None:
        self._storage = storage
        self._inheriter = ProfileInheriter(storage)

    def run(
        self,
        profile_name: str,
        parent_name: Optional[str],
        *,
        show_chain: bool = False,
        show_overrides: bool = False,
    ) -> None:
        password = getpass.getpass(f"Password for '{profile_name}': ")

        try:
            result = self._inheriter.resolve(profile_name, parent_name, password)
        except InheritanceError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)
        except Exception as exc:  # noqa: BLE001
            print(f"Failed to resolve profile: {exc}", file=sys.stderr)
            sys.exit(1)

        if show_chain:
            print("Inheritance chain: " + " -> ".join(result.chain))

        if show_overrides and result.overridden_keys:
            print("Overridden keys: " + ", ".join(sorted(result.overridden_keys)))

        if not result.resolved_vars:
            print("(no variables)")
            return

        for key in sorted(result.resolved_vars):
            print(f"{key}={result.resolved_vars[key]}")

    def show_chain(
        self,
        profile_name: str,
        parent_name: Optional[str],
    ) -> None:
        """Print only the inheritance chain without decrypting values."""
        if parent_name:
            print(f"Chain: {parent_name} -> {profile_name}")
        else:
            print(f"Chain: {profile_name} (no parent)")
