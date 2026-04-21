"""CLI command for extracting a variable subset from a profile."""
from __future__ import annotations

import sys
from typing import List

from envchain.env_excerpt import EnvExcerpt
from envchain.storage import EnvStorage


class ExcerptCommand:
    """CLI wrapper around :class:`EnvExcerpt`."""

    def __init__(self, storage: EnvStorage) -> None:
        self._storage = storage
        self._excerptr = EnvExcerpt()

    def run(
        self,
        profile_name: str,
        keys: List[str],
        password: str,
        *,
        ignore_missing: bool = True,
        output_format: str = "env",
    ) -> None:
        """Print the extracted subset to stdout."""
        profile = self._storage.load_profile(profile_name, password)
        if profile is None:
            print(f"[error] Profile {profile_name!r} not found.", file=sys.stderr)
            sys.exit(1)

        try:
            result = self._excerptr.excerpt(
                profile_name,
                profile.variables,
                keys,
                ignore_missing=ignore_missing,
            )
        except KeyError as exc:
            print(f"[error] {exc}", file=sys.stderr)
            sys.exit(1)

        if not result.extracted:
            print("[info] No variables matched the requested keys.")
            return

        if output_format == "json":
            import json
            print(json.dumps(result.extracted, indent=2))
        else:
            for var, value in sorted(result.extracted.items()):
                print(f"{var}={value}")

        if result.missing_keys:
            print(
                f"[warn] Keys not found: {', '.join(result.missing_keys)}",
                file=sys.stderr,
            )

    def show_summary(self, profile_name: str, keys: List[str], password: str) -> None:
        """Print a summary of what would be extracted without showing values."""
        profile = self._storage.load_profile(profile_name, password)
        if profile is None:
            print(f"[error] Profile {profile_name!r} not found.", file=sys.stderr)
            sys.exit(1)

        result = self._excerptr.excerpt(
            profile_name, profile.variables, keys, ignore_missing=True
        )
        print(f"Profile : {profile_name}")
        print(f"Matched : {result.extract_count} / {len(result.original)}")
        if result.missing_keys:
            print(f"Missing : {', '.join(result.missing_keys)}")
