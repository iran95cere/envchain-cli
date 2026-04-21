"""CLI command for escaping/unescaping environment variable values."""
from __future__ import annotations

from typing import Optional

from envchain.env_escape import EnvEscaper
from envchain.storage import EnvStorage


class EscapeCommand:
    def __init__(self, storage: EnvStorage) -> None:
        self._storage = storage
        self._escaper = EnvEscaper()

    def run(
        self,
        profile_name: str,
        password: str,
        dry_run: bool = False,
        verbose: bool = False,
    ) -> int:
        """Escape all variable values in *profile_name*."""
        profile = self._storage.load_profile(profile_name, password)
        if profile is None:
            print(f"Profile '{profile_name}' not found.")
            return 1

        report = self._escaper.escape(profile.vars)

        if verbose:
            for result in report.results:
                status = "changed" if result.changed else "unchanged"
                print(f"  {result.name}: {status}")

        if not report.has_changes:
            print("No values required escaping.")
            return 0

        if dry_run:
            print(
                f"Dry run: {report.changed_count} value(s) would be escaped "
                f"in '{profile_name}'."
            )
            return 0

        profile.vars = report.to_dict()
        self._storage.save_profile(profile, password)
        print(f"Escaped {report.changed_count} value(s) in '{profile_name}'.")
        return 0

    def unescape_run(
        self,
        profile_name: str,
        password: str,
        dry_run: bool = False,
    ) -> int:
        """Unescape all variable values in *profile_name*."""
        profile = self._storage.load_profile(profile_name, password)
        if profile is None:
            print(f"Profile '{profile_name}' not found.")
            return 1

        unescaped = self._escaper.unescape(profile.vars)
        changed = sum(
            1 for k, v in unescaped.items() if v != profile.vars.get(k)
        )

        if dry_run:
            print(
                f"Dry run: {changed} value(s) would be unescaped "
                f"in '{profile_name}'."
            )
            return 0

        profile.vars = unescaped
        self._storage.save_profile(profile, password)
        print(f"Unescaped {changed} value(s) in '{profile_name}'.")
        return 0
