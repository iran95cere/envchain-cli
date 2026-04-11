"""CLI command: rename a variable key in a profile."""
from __future__ import annotations

import sys
from typing import Optional

from envchain.env_rename import EnvRenamer


class RenameCommand:
    """Wraps EnvRenamer for CLI use."""

    def __init__(self, storage, profile_name: str, password: str) -> None:
        self._storage = storage
        self._profile_name = profile_name
        self._password = password
        self._renamer = EnvRenamer()

    def run(
        self,
        old_name: str,
        new_name: str,
        overwrite: bool = False,
    ) -> None:
        """Rename *old_name* to *new_name* inside the active profile."""
        profile = self._storage.load_profile(self._profile_name, self._password)
        if profile is None:
            print(f"Error: profile '{self._profile_name}' not found.", file=sys.stderr)
            sys.exit(1)

        variables: dict = profile.variables  # type: ignore[attr-defined]
        result = self._renamer.rename(
            variables, {old_name: new_name}, overwrite=overwrite
        )

        if old_name in result.skipped:
            print(
                f"Error: variable '{old_name}' does not exist in profile "
                f"'{self._profile_name}'.",
                file=sys.stderr,
            )
            sys.exit(1)

        if old_name in result.conflicts:
            print(
                f"Error: '{new_name}' already exists. Use --overwrite to replace it.",
                file=sys.stderr,
            )
            sys.exit(1)

        self._storage.save_profile(profile, self._password)
        print(f"Renamed '{old_name}' -> '{new_name}' in profile '{self._profile_name}'.")

    def bulk_run(
        self,
        mapping: dict,
        overwrite: bool = False,
    ) -> None:
        """Rename multiple keys at once from *mapping* (old->new)."""
        profile = self._storage.load_profile(self._profile_name, self._password)
        if profile is None:
            print(f"Error: profile '{self._profile_name}' not found.", file=sys.stderr)
            sys.exit(1)

        variables: dict = profile.variables  # type: ignore[attr-defined]
        result = self._renamer.rename(variables, mapping, overwrite=overwrite)

        for old in result.skipped:
            print(f"  Skipped (not found): '{old}'", file=sys.stderr)
        for old in result.conflicts:
            print(f"  Conflict (already exists): '{old}' -> '{mapping[old]}'", file=sys.stderr)
        for old, new in result.renamed.items():
            print(f"  Renamed: '{old}' -> '{new}'")

        if result.success_count:
            self._storage.save_profile(profile, self._password)
            print(f"\n{result.success_count} variable(s) renamed in '{self._profile_name}'.")
        else:
            print("No variables were renamed.", file=sys.stderr)
            sys.exit(1)
