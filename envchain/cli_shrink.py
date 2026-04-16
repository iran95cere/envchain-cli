"""CLI command for shrinking environment variable values."""
from __future__ import annotations

import sys
from typing import Optional

from envchain.env_shrink import EnvShrinker
from envchain.storage import EnvStorage


class ShrinkCommand:
    def __init__(self, storage: EnvStorage) -> None:
        self._storage = storage

    def run(
        self,
        profile_name: str,
        strategy: str = "strip",
        dry_run: bool = False,
    ) -> None:
        profile = self._storage.load_profile(profile_name)
        if profile is None:
            print(f"[shrink] Profile {profile_name!r} not found.", file=sys.stderr)
            sys.exit(1)

        try:
            shrinker = EnvShrinker(strategy=strategy)
        except ValueError as exc:
            print(f"[shrink] {exc}", file=sys.stderr)
            sys.exit(1)

        report = shrinker.shrink(profile.vars)

        if not report.has_changes:
            print(f"[shrink] No changes for profile {profile_name!r}.")
            return

        for result in report.results:
            if result.changed:
                print(
                    f"  {result.name}: {result.original!r} -> {result.shrunk!r}"
                    f" (saved {result.saved_bytes}B)"
                )

        if dry_run:
            print(f"[shrink] Dry run — {report.changed_count} value(s) would change.")
            return

        profile.vars = shrinker.to_dict(report)
        self._storage.save_profile(profile)
        print(
            f"[shrink] Applied strategy={strategy!r} to {profile_name!r}:"
            f" {report.changed_count} change(s), {report.total_saved_bytes}B saved."
        )

    def list_strategies(self) -> None:
        print("Available shrink strategies:")
        for s in EnvShrinker.STRATEGIES:
            print(f"  {s}")
