"""CLI command for comparing two environment profiles."""
import sys
from typing import Optional

from envchain.env_compare import ProfileComparer
from envchain.storage import EnvStorage


class CompareCommand:
    def __init__(self, storage: EnvStorage) -> None:
        self._storage = storage
        self._comparer = ProfileComparer()

    def run(
        self,
        left: str,
        right: str,
        password: Optional[str] = None,
        show_same: bool = False,
        mask_values: bool = True,
    ) -> None:
        left_data = self._storage.load_profile(left, password or "")
        if left_data is None:
            print(f"Profile '{left}' not found.", file=sys.stderr)
            sys.exit(1)

        right_data = self._storage.load_profile(right, password or "")
        if right_data is None:
            print(f"Profile '{right}' not found.", file=sys.stderr)
            sys.exit(1)

        left_vars = left_data.get("vars", {})
        right_vars = right_data.get("vars", {})

        result = self._comparer.compare(
            left_vars, right_vars, left_profile=left, right_profile=right
        )

        print(f"Comparing '{left}' <-> '{right}'")
        print(f"Summary: {result.summary()}")
        print()

        def _display(val: Optional[str]) -> str:
            if val is None:
                return "(missing)"
            return "***" if mask_values else val

        for entry in result.removed:
            print(f"  - {entry.name}: {_display(entry.left_value)} (only in {left})")

        for entry in result.added:
            print(f"  + {entry.name}: {_display(entry.right_value)} (only in {right})")

        for entry in result.modified:
            print(
                f"  ~ {entry.name}: {_display(entry.left_value)}"
                f" -> {_display(entry.right_value)}"
            )

        if show_same:
            for entry in result.same:
                print(f"    {entry.name}: (identical)")

        if not result.has_differences:
            print("  Profiles are identical.")
