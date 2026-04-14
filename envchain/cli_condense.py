"""CLI command for condensing profile environment variables."""
from __future__ import annotations
import sys
from typing import Optional
from envchain.env_condense import EnvCondenser


class CondenseCommand:
    def __init__(self, storage) -> None:
        self._storage = storage
        self._condenser = EnvCondenser()

    def run(
        self,
        profile_name: str,
        password: str,
        strip_empty: bool = True,
        deduplicate_case: bool = True,
        dry_run: bool = False,
    ) -> None:
        profile = self._storage.load_profile(profile_name, password)
        if profile is None:
            print(f"[error] Profile '{profile_name}' not found.", file=sys.stderr)
            sys.exit(1)

        condensed_vars, result = self._condenser.condense(
            profile_name=profile_name,
            variables=dict(profile.variables),
            strip_empty=strip_empty,
            deduplicate_case=deduplicate_case,
        )

        if not result.is_changed:
            print(f"Profile '{profile_name}' is already condensed. No changes made.")
            return

        print(f"Condensing '{profile_name}': {result.original_count} -> {result.condensed_count} vars")
        if result.removed:
            print("  Removed keys:")
            for key in result.removed:
                print(f"    - {key}")

        if dry_run:
            print("[dry-run] No changes saved.")
            return

        profile.variables = condensed_vars
        self._storage.save_profile(profile, password)
        print(f"Saved condensed profile '{profile_name}'.")

    def show_report(self, profile_name: str, password: str) -> None:
        """Print a condensation report without saving."""
        self.run(profile_name, password, dry_run=True)
