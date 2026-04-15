"""CLI command: interpolate variable references within a profile."""
from __future__ import annotations

import sys
from typing import Optional

from envchain.env_interpolate import EnvInterpolator
from envchain.storage import EnvStorage


class InterpolateCommand:
    def __init__(self, storage: EnvStorage) -> None:
        self._storage = storage
        self._interpolator = EnvInterpolator()

    # ------------------------------------------------------------------
    def run(
        self,
        profile_name: str,
        password: str,
        *,
        strict: bool = False,
        dry_run: bool = False,
    ) -> None:
        profile = self._storage.load_profile(profile_name, password)
        if profile is None:
            print(f"[error] Profile '{profile_name}' not found.", file=sys.stderr)
            sys.exit(1)

        report = self._interpolator.interpolate(
            profile.variables, strict=strict
        )

        if report.has_unresolved:
            for ref in report.unresolved:
                print(f"[warn] Unresolved reference: ${{{ref}}}", file=sys.stderr)

        if report.changed_count == 0:
            print("No interpolation changes.")
            return

        for result in report.results:
            if result.changed:
                print(f"  {result.name}: {result.original!r} -> {result.resolved!r}")

        if dry_run:
            print(f"[dry-run] {report.changed_count} variable(s) would be updated.")
            return

        for result in report.results:
            if result.changed:
                profile.variables[result.name] = result.resolved

        self._storage.save_profile(profile, password)
        print(f"Interpolated {report.changed_count} variable(s) in '{profile_name}'.")

    # ------------------------------------------------------------------
    def show_references(self, profile_name: str, password: str) -> None:
        profile = self._storage.load_profile(profile_name, password)
        if profile is None:
            print(f"[error] Profile '{profile_name}' not found.", file=sys.stderr)
            sys.exit(1)

        report = self._interpolator.interpolate(profile.variables)
        any_refs = False
        for result in report.results:
            if result.refs:
                any_refs = True
                print(f"  {result.name} -> {result.refs}")
        if not any_refs:
            print("No variable references found.")
