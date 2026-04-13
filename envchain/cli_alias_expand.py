"""CLI command: expand variable aliases within a stored profile."""
from __future__ import annotations

import sys
from typing import Dict

from envchain.env_alias_expand import EnvAliasExpander


class AliasExpandCommand:
    """Expand variable aliases in a profile and optionally save the result."""

    def __init__(self, storage) -> None:
        self._storage = storage
        self._expander = EnvAliasExpander()

    def run(
        self,
        profile_name: str,
        alias_map: Dict[str, str],
        password: str,
        overwrite: bool = False,
        dry_run: bool = False,
    ) -> None:
        """Load *profile_name*, expand aliases and (unless *dry_run*) save."""
        profile = self._storage.load_profile(profile_name, password)
        if profile is None:
            print(f"[error] Profile '{profile_name}' not found.", file=sys.stderr)
            sys.exit(1)

        if not alias_map:
            print("[warn] No alias mappings provided — nothing to expand.")
            return

        report = self._expander.expand(
            profile.variables, alias_map, overwrite=overwrite
        )

        for result in report.results:
            status = "expanded" if result.expanded else "skipped"
            print(f"  {result.alias_name} <- {result.original_name}: {status}")

        if dry_run:
            print(f"[dry-run] {report.expanded_count} alias(es) would be expanded.")
            return

        if report.has_expansions:
            self._storage.save_profile(profile, password)
            print(f"[ok] {report.expanded_count} alias(es) expanded and saved.")
        else:
            print("[info] No aliases were expanded — profile unchanged.")

    def show_aliases(
        self, profile_name: str, password: str, alias_map: Dict[str, str]
    ) -> None:
        """Preview which aliases would be applied without modifying the profile."""
        self.run(profile_name, alias_map, password, dry_run=True)
