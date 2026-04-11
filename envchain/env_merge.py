"""Merge multiple profiles' variables with conflict resolution strategies."""

from enum import Enum
from typing import Dict, List, Optional, Tuple


class MergeStrategy(str, Enum):
    FIRST_WINS = "first_wins"   # Keep value from the first profile that defines it
    LAST_WINS = "last_wins"     # Keep value from the last profile that defines it
    STRICT = "strict"           # Raise an error if any key appears in more than one profile


class MergeConflict(Exception):
    """Raised by STRICT strategy when duplicate keys are found."""

    def __init__(self, key: str, profiles: List[str]) -> None:
        self.key = key
        self.profiles = profiles
        super().__init__(
            f"Conflict: key '{key}' defined in multiple profiles: {', '.join(profiles)}"
        )


class MergeResult:
    """Result of a merge operation."""

    def __init__(
        self,
        merged: Dict[str, str],
        conflicts: List[Tuple[str, List[str]]],
    ) -> None:
        self.merged = merged
        # conflicts: list of (key, [profile_names that defined it])
        self.conflicts = conflicts

    @property
    def has_conflicts(self) -> bool:
        return len(self.conflicts) > 0

    def conflict_summary(self) -> str:
        if not self.conflicts:
            return "No conflicts."
        lines = []
        for key, profiles in self.conflicts:
            lines.append(f"  {key}: {', '.join(profiles)}")
        return "Conflicts:\n" + "\n".join(lines)

    def __repr__(self) -> str:
        return (
            f"MergeResult(vars={len(self.merged)}, conflicts={len(self.conflicts)})"
        )


class EnvMerger:
    """Merge environment variables from multiple profiles."""

    def merge(
        self,
        profiles: Dict[str, Dict[str, str]],
        strategy: MergeStrategy = MergeStrategy.LAST_WINS,
        exclude_keys: Optional[List[str]] = None,
    ) -> MergeResult:
        """
        Merge variables from *profiles* (ordered dict of profile_name -> vars).

        Parameters
        ----------
        profiles:     Ordered mapping of profile name to variable dict.
        strategy:     Conflict resolution strategy.
        exclude_keys: Keys to skip during the merge.
        """
        exclude = set(exclude_keys or [])
        merged: Dict[str, str] = {}
        seen: Dict[str, List[str]] = {}  # key -> list of profile names

        for profile_name, variables in profiles.items():
            for key, value in variables.items():
                if key in exclude:
                    continue
                if key in seen:
                    seen[key].append(profile_name)
                    if strategy == MergeStrategy.STRICT:
                        raise MergeConflict(key, seen[key])
                    if strategy == MergeStrategy.LAST_WINS:
                        merged[key] = value
                    # FIRST_WINS: do nothing — keep existing value
                else:
                    seen[key] = [profile_name]
                    merged[key] = value

        conflicts = [
            (key, profile_list)
            for key, profile_list in seen.items()
            if len(profile_list) > 1
        ]
        return MergeResult(merged=merged, conflicts=conflicts)
