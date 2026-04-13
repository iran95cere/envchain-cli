"""CLI command for analysing environment variable dependencies."""
from __future__ import annotations

import sys
from typing import Optional

from envchain.env_dependencies import DependencyAnalyser
from envchain.storage import EnvStorage


class DependencyCommand:
    def __init__(self, storage: EnvStorage) -> None:
        self._storage = storage
        self._analyser = DependencyAnalyser()

    def run(self, source_profile: str, *, show_missing_only: bool = False) -> None:
        """Print dependency edges for *source_profile*."""
        profile_names = self._storage.list_profiles()
        profiles = {}
        for name in profile_names:
            try:
                p = self._storage.load_profile(name, password="")
                profiles[name] = p.variables if p else {}
            except Exception:
                profiles[name] = {}

        if source_profile not in profiles:
            print(f"Profile '{source_profile}' not found.", file=sys.stderr)
            sys.exit(1)

        report = self._analyser.analyse(profiles, source_profile)

        if show_missing_only:
            if not report.has_missing:
                print("No missing dependencies.")
                return
            for edge in report.missing:
                print(f"[MISSING] {edge}")
            return

        if not report.edges:
            print(f"No cross-profile dependencies found in '{source_profile}'.")
            return

        for edge in report.edges:
            status = "MISSING" if edge in report.missing else "ok"
            print(f"[{status}] {edge}")

        if report.has_missing:
            print(
                f"\n{len(report.missing)} missing reference(s) detected.",
                file=sys.stderr,
            )
            sys.exit(2)

    def show_graph(self, source_profile: str) -> None:
        """Print a simple text graph of dependencies."""
        profile_names = self._storage.list_profiles()
        profiles = {}
        for name in profile_names:
            try:
                p = self._storage.load_profile(name, password="")
                profiles[name] = p.variables if p else {}
            except Exception:
                profiles[name] = {}

        report = self._analyser.analyse(profiles, source_profile)
        if not report.edges:
            print(f"'{source_profile}' has no outgoing dependencies.")
            return

        seen: set = set()
        for edge in report.edges:
            key = (edge.target_profile, edge.target_var)
            if key not in seen:
                print(f"  {source_profile} --[{edge.source_var}]--> {edge.target_profile}/{edge.target_var}")
                seen.add(key)
