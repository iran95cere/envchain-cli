"""CLI command for formatting environment variable values."""
from __future__ import annotations

import sys
from typing import List, Optional

from envchain.env_format import EnvFormatter
from envchain.storage import EnvStorage


class FormatCommand:
    """Apply a formatting rule to variables in a profile."""

    FORMATS = EnvFormatter.SUPPORTED_FORMATS

    def __init__(self, storage: EnvStorage) -> None:
        self._storage = storage
        self._formatter = EnvFormatter()

    # ------------------------------------------------------------------
    def run(
        self,
        profile_name: str,
        fmt_type: str,
        password: str,
        keys: Optional[List[str]] = None,
        dry_run: bool = False,
    ) -> None:
        """Format variable values in *profile_name* using *fmt_type*."""
        if fmt_type not in self.FORMATS:
            print(
                f"[error] Unknown format '{fmt_type}'. "
                f"Supported: {', '.join(self.FORMATS)}",
                file=sys.stderr,
            )
            sys.exit(1)

        profile = self._storage.load_profile(profile_name, password)
        if profile is None:
            print(f"[error] Profile '{profile_name}' not found.", file=sys.stderr)
            sys.exit(1)

        report = self._formatter.format_vars(profile.variables, fmt_type, keys)

        if not report.has_changes:
            print("No changes needed.")
            return

        for result in report.results:
            if result.changed:
                print(f"  {result.original}: {result.formatted!r}")

        if dry_run:
            print(f"\n[dry-run] {report.changed_count} variable(s) would be updated.")
            return

        for result in report.results:
            if result.changed:
                profile.variables[result.original] = result.formatted

        self._storage.save_profile(profile, password)
        print(f"\nUpdated {report.changed_count} variable(s) in '{profile_name}'.")

    def list_formats(self) -> None:
        """Print supported format types."""
        print("Supported format types:")
        for fmt in self.FORMATS:
            print(f"  {fmt}")
