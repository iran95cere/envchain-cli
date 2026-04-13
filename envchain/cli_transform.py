"""CLI commands for the env-transform feature."""
from __future__ import annotations

import sys
from typing import List, Optional

from envchain.env_transform import EnvTransformer


class TransformCommand:
    """Expose variable transformation operations as CLI sub-commands."""

    def __init__(self, storage, transformer: Optional[EnvTransformer] = None) -> None:
        self._storage = storage
        self._transformer = transformer or EnvTransformer()

    def list_transforms(self) -> None:
        """Print all available transform names."""
        names = self._transformer.available()
        if not names:
            print("No transforms available.")
            return
        for name in names:
            print(f"  {name}")

    def run(
        self,
        profile_name: str,
        transform_name: str,
        password: str,
        keys: Optional[List[str]] = None,
        dry_run: bool = False,
    ) -> None:
        """Apply *transform_name* to variables in *profile_name*."""
        profile = self._storage.load_profile(profile_name, password)
        if profile is None:
            print(f"Profile '{profile_name}' not found.", file=sys.stderr)
            sys.exit(1)

        try:
            report = self._transformer.apply_many(
                profile.variables, transform_name, keys=keys
            )
        except KeyError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)

        if not report.has_changes:
            print("No values changed.")
            return

        for result in report.results:
            if result.changed:
                status = "(dry-run) " if dry_run else ""
                print(
                    f"  {status}{result.transform_name}: "
                    f"{result.original!r} -> {result.transformed!r}"
                )

        if dry_run:
            print(f"Dry-run: {report.changed_count} value(s) would change.")
            return

        for result in report.results:
            if result.changed:
                profile.variables[
                    next(
                        k
                        for k, v in profile.variables.items()
                        if v == result.original
                        and profile.variables[k] == result.original
                    )
                ] = result.transformed

        # Re-apply correctly by rebuilding from report order
        target_keys = keys if keys is not None else list(profile.variables.keys())
        for key, result in zip(target_keys, report.results):
            if result.changed:
                profile.variables[key] = result.transformed

        self._storage.save_profile(profile, password)
        print(f"Transformed {report.changed_count} value(s) in '{profile_name}'.")
