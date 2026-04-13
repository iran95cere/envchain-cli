"""CLI command for cross-reference analysis."""
from __future__ import annotations

from typing import List, Optional

from envchain.env_crossref import EnvCrossRef


class CrossRefCommand:
    """Show variables shared across multiple profiles."""

    def __init__(self, storage) -> None:
        self._storage = storage
        self._analyser = EnvCrossRef(storage)

    def run(
        self,
        profiles: Optional[List[str]] = None,
        min_count: int = 2,
        verbose: bool = False,
    ) -> int:
        """Print cross-referenced variables and return exit code."""
        report = self._analyser.analyse(profiles)
        filtered = [
            e for e in report.entries if e.profile_count() >= min_count
        ]
        if not filtered:
            print("No cross-referenced variables found.")
            return 0
        for entry in filtered:
            profile_list = ", ".join(entry.profiles)
            print(f"{entry.name}  [{profile_list}]")
            if verbose:
                print(f"  Appears in {entry.profile_count()} profiles.")
        return 0

    def show_summary(self, profiles: Optional[List[str]] = None) -> None:
        """Print a one-line summary of cross-referenced variables."""
        report = self._analyser.analyse(profiles)
        if report.has_refs:
            print(
                f"{report.ref_count} variable(s) shared across profiles: "
                + ", ".join(report.names())
            )
        else:
            print("All variables are unique to their respective profiles.")
