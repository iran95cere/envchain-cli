"""CLI command for normalizing environment variable values in a profile."""
from __future__ import annotations

import sys
from typing import List, Optional

from envchain.env_normalize import EnvNormalizer
from envchain.storage import EnvStorage


class NormalizeCommand:
    def __init__(self, storage: EnvStorage) -> None:
        self.storage = storage

    def run(
        self,
        profile_name: str,
        password: str,
        strategies: Optional[List[str]] = None,
        dry_run: bool = False,
    ) -> None:
        profile = self.storage.load_profile(profile_name, password)
        if profile is None:
            print(f"Profile {profile_name!r} not found.", file=sys.stderr)
            sys.exit(1)

        try:
            normalizer = EnvNormalizer(strategies=strategies)
        except ValueError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)

        report = normalizer.normalize(profile.vars)

        if not report.has_changes:
            print("No changes — all values already normalized.")
            return

        for result in report.results:
            if result.changed:
                print(f"  {result.name}: {result.original_value!r} -> {result.normalized_value!r}")

        if dry_run:
            print(f"\nDry run: {report.changed_count} value(s) would be normalized.")
            return

        profile.vars = report.to_normalized_vars()
        self.storage.save_profile(profile, password)
        print(f"\nNormalized {report.changed_count} value(s) in profile {profile_name!r}.")

    def list_strategies(self) -> None:
        print("Available normalization strategies:")
        for s in EnvNormalizer.STRATEGIES:
            print(f"  - {s}")
