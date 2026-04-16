"""CLI command for normalizing profile variable keys to UPPER_SNAKE_CASE."""
from __future__ import annotations

from envchain.env_uppercase_keys import EnvKeyNormalizer


class UppercaseKeysCommand:
    def __init__(self, storage, profile_name: str) -> None:
        self._storage = storage
        self._profile_name = profile_name
        self._normalizer = EnvKeyNormalizer()

    def run(self, dry_run: bool = False) -> None:
        profile = self._storage.load_profile(self._profile_name)
        if profile is None:
            print(f"Profile '{self._profile_name}' not found.")
            raise SystemExit(1)

        report = self._normalizer.normalize(profile.vars)

        if not report.has_changes:
            print("All keys are already normalized. No changes made.")
            return

        for result in report.results:
            if result.changed:
                print(f"  {result.original_key!r} -> {result.new_key!r}")

        if dry_run:
            print(f"Dry run: {report.changed_count} key(s) would be renamed.")
            return

        profile.vars = self._normalizer.apply(profile.vars)
        self._storage.save_profile(self._profile_name, profile)
        print(f"Normalized {report.changed_count} key(s) in profile '{self._profile_name}'.")

    def show_report(self) -> None:
        profile = self._storage.load_profile(self._profile_name)
        if profile is None:
            print(f"Profile '{self._profile_name}' not found.")
            raise SystemExit(1)

        report = self._normalizer.normalize(profile.vars)
        print(repr(report))
        for r in report.results:
            print(f"  {r}")
