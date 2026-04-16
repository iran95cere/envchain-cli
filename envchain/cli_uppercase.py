"""CLI command for converting environment variable names to uppercase."""
from __future__ import annotations

import sys

from envchain.env_uppercase import EnvUppercaser


class UppercaseCommand:
    def __init__(self, storage, profile_name: str) -> None:
        self._storage = storage
        self._profile_name = profile_name
        self._uppercaser = EnvUppercaser()

    def run(self, dry_run: bool = False) -> None:
        profile = self._storage.load_profile(self._profile_name)
        if profile is None:
            print(f"Profile '{self._profile_name}' not found.", file=sys.stderr)
            sys.exit(1)

        report = self._uppercaser.convert(profile.vars)

        if not report.has_changes:
            print("All variable names are already uppercase. No changes needed.")
            return

        for result in report.results:
            if result.changed:
                print(f"  {result.original!r} -> {result.converted!r}")

        if dry_run:
            print(f"Dry run: {report.changed_count} name(s) would be converted.")
            return

        new_vars = self._uppercaser.apply(profile.vars, report)
        profile.vars = new_vars
        self._storage.save_profile(profile)
        print(f"Converted {report.changed_count} variable name(s) to uppercase.")

    def show_report(self) -> None:
        profile = self._storage.load_profile(self._profile_name)
        if profile is None:
            print(f"Profile '{self._profile_name}' not found.", file=sys.stderr)
            sys.exit(1)

        report = self._uppercaser.convert(profile.vars)
        data = report.to_dict()
        print(f"Total variables : {len(profile.vars)}")
        print(f"Names to convert: {data['changed_count']}")
        for entry in data["results"]:
            status = "CHANGE" if entry["original"] != entry["converted"] else "ok"
            print(f"  [{status}] {entry['original']!r}")
