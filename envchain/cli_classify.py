"""CLI command for classifying environment variables by category."""
from __future__ import annotations

import sys
from typing import Optional

from envchain.env_classify import EnvClassifier
from envchain.storage import EnvStorage


class ClassifyCommand:
    def __init__(self, storage: EnvStorage) -> None:
        self._storage = storage
        self._classifier = EnvClassifier()

    def run(self, profile_name: str, password: str, category_filter: Optional[str] = None) -> None:
        profile = self._storage.load_profile(profile_name, password)
        if profile is None:
            print(f"Profile '{profile_name}' not found.", file=sys.stderr)
            sys.exit(1)

        report = self._classifier.classify(profile.vars)

        results = report.results
        if category_filter:
            results = report.by_category(category_filter)
            if not results:
                print(f"No variables found in category '{category_filter}'.")
                return

        for result in sorted(results, key=lambda r: (r.category, r.name)):
            print(f"  [{result.category:14s}] {result.name}")

        print()
        for cat, count in sorted(report.category_counts.items()):
            print(f"  {cat}: {count}")

    def list_categories(self) -> None:
        from envchain.env_classify import CATEGORY_PATTERNS
        print("Available categories:")
        for cat in sorted(CATEGORY_PATTERNS.keys()):
            print(f"  {cat}")
        print("  general  (fallback)")
