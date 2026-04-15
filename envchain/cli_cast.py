"""CLI command for casting environment variable values."""
from __future__ import annotations

import sys
from typing import Optional

from envchain.env_cast import CAST_TYPES, EnvCaster


class CastCommand:
    """Validate that profile variables can be cast to a given type."""

    def __init__(self, storage, profile_name: str):
        self._storage = storage
        self._profile_name = profile_name
        self._caster = EnvCaster()

    def run(self, cast_type: str, *, fail_fast: bool = False) -> None:
        profile = self._storage.load_profile(self._profile_name)
        if profile is None:
            print(f"Profile '{self._profile_name}' not found.", file=sys.stderr)
            sys.exit(1)

        if cast_type not in CAST_TYPES:
            print(f"Unknown type '{cast_type}'. Available: {', '.join(CAST_TYPES)}", file=sys.stderr)
            sys.exit(1)

        report = self._caster.cast(profile.variables, cast_type)

        for result in report.results:
            if result.success:
                print(f"  [ok] {result.name}: {result.original!r} -> {result.casted!r}")
            else:
                print(f"  [fail] {result.name}: {result.original!r} -> {result.error}")
                if fail_fast:
                    sys.exit(2)

        print(f"\nCast to '{cast_type}': {report.success_count} ok, {report.failure_count} failed.")
        if report.has_failures:
            sys.exit(2)

    def list_types(self) -> None:
        print("Available cast types:")
        for t in CAST_TYPES:
            print(f"  {t}")
