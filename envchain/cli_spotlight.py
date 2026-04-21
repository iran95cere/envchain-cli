"""CLI command for env var spotlight / importance ranking."""
from __future__ import annotations

import sys
from typing import Optional

from envchain.env_spotlight import EnvSpotlight
from envchain.storage import EnvStorage


class SpotlightCommand:
    def __init__(self, storage: EnvStorage) -> None:
        self._storage = storage
        self._spotlight = EnvSpotlight()

    def run(
        self,
        profile: str,
        password: str,
        top: int = 10,
        min_score: Optional[int] = None,
        out=sys.stdout,
    ) -> None:
        prof = self._storage.load_profile(profile, password)
        if prof is None:
            print(f"Profile '{profile}' not found.", file=sys.stderr)
            sys.exit(1)

        report = self._spotlight.analyse(prof.vars)
        if not report.results:
            print("No variables found.", file=out)
            return

        candidates = report.top(top)
        if min_score is not None:
            candidates = [r for r in candidates if r.score >= min_score]

        print(f"Spotlight — top {len(candidates)} variable(s):", file=out)
        for r in candidates:
            print(f"  [{r.score:>2}] {r.name:<30} {r.reason}", file=out)

    def show_all(
        self,
        profile: str,
        password: str,
        out=sys.stdout,
    ) -> None:
        prof = self._storage.load_profile(profile, password)
        if prof is None:
            print(f"Profile '{profile}' not found.", file=sys.stderr)
            sys.exit(1)

        report = self._spotlight.analyse(prof.vars)
        for r in sorted(report.results, key=lambda x: x.score, reverse=True):
            print(f"  [{r.score:>2}] {r.name:<30} {r.reason}", file=out)
