"""CLI command for splitting a profile by variable prefixes."""
from __future__ import annotations

import sys
from typing import List

from envchain.env_split import EnvSplitter
from envchain.storage import EnvStorage


class SplitCommand:
    def __init__(self, storage: EnvStorage) -> None:
        self._storage = storage
        self._splitter = EnvSplitter()

    def run(
        self,
        profile: str,
        prefixes: List[str],
        strip_prefix: bool = False,
        save: bool = False,
        password: str = "",
    ) -> None:
        """Split *profile* into sub-profiles by *prefixes*.

        When *save* is True a new profile is created for every matched group
        using the prefix (lowercased, underscores replaced with hyphens) as
        the profile name suffix, e.g. ``<profile>-db``.
        """
        loaded = self._storage.load_profile(profile, password)
        if loaded is None:
            print(f"Profile '{profile}' not found.", file=sys.stderr)
            sys.exit(1)

        report = self._splitter.split(loaded.variables, prefixes,
                                      strip_prefix=strip_prefix)

        if not report.results:
            print("No variables matched the supplied prefixes.")
            return

        for result in report.results:
            suffix = result.prefix.lower().rstrip("_").replace("_", "-")
            target = f"{profile}-{suffix}"
            print(
                f"  {result.prefix!r:20s} -> {target!r:30s} "
                f"({result.var_count} var(s))"
            )
            if save:
                import copy
                new_profile = copy.deepcopy(loaded)
                new_profile.name = target
                new_profile.variables = result.vars
                self._storage.save_profile(new_profile, password)

        if report.has_unmatched:
            print(
                f"  {report.unmatched_count} variable(s) did not match any prefix."
            )

        if save:
            print(f"Saved {report.group_count} sub-profile(s).")
        else:
            print("Dry-run complete. Pass --save to persist the split profiles.")

    def show_report(self, profile: str, prefixes: List[str],
                    password: str = "") -> None:
        """Print a summary without saving."""
        self.run(profile, prefixes, save=False, password=password)
