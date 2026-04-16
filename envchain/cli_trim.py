"""CLI command for trimming whitespace from env var values."""
from __future__ import annotations

from envchain.env_trim import EnvTrimmer


class TrimCommand:
    """Trim whitespace from env var values in a profile."""

    def __init__(self, storage):
        self._storage = storage
        self._trimmer = EnvTrimmer()

    def run(self, profile_name: str, password: str, dry_run: bool = False) -> None:
        """Trim leading/trailing whitespace from all variables in a profile.

        Args:
            profile_name: Name of the profile to process.
            password: Password used to decrypt the profile.
            dry_run: If True, report changes without saving them.
        """
        profile = self._storage.load_profile(profile_name, password)
        if profile is None:
            print(f"Profile '{profile_name}' not found.")
            raise SystemExit(1)

        trimmed_vars, report = self._trimmer.trim(profile.variables)

        if not report.has_changes:
            print(f"No whitespace found in '{profile_name}'. Nothing to trim.")
            return

        print(f"Found {report.changed_count} variable(s) with leading/trailing whitespace:")
        for result in report.changed_vars():
            print(f"  {result.name}: {result.original_value!r} -> {result.trimmed_value!r}")

        if dry_run:
            print("Dry-run mode: no changes saved.")
            return

        profile.variables = trimmed_vars
        self._storage.save_profile(profile, password)
        print(f"Trimmed {report.changed_count} variable(s) in '{profile_name}'.")

    def show_report(self, profile_name: str, password: str) -> None:
        """Display a summary report of whitespace in a profile's variables.

        Args:
            profile_name: Name of the profile to inspect.
            password: Password used to decrypt the profile.
        """
        profile = self._storage.load_profile(profile_name, password)
        if profile is None:
            print(f"Profile '{profile_name}' not found.")
            raise SystemExit(1)

        _, report = self._trimmer.trim(profile.variables)
        data = report.to_dict()
        print(f"Total variables : {len(report.results)}")
        print(f"Changed         : {data['changed_count']}")
        for r in data["results"]:
            marker = "*" if r["changed"] else " "
            print(f"  [{marker}] {r['name']}")
