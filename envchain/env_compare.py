"""Compare environment variable profiles side by side."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set


@dataclass
class CompareEntry:
    name: str
    left_value: Optional[str]
    right_value: Optional[str]

    @property
    def is_same(self) -> bool:
        return self.left_value == self.right_value

    @property
    def only_in_left(self) -> bool:
        return self.left_value is not None and self.right_value is None

    @property
    def only_in_right(self) -> bool:
        return self.left_value is None and self.right_value is not None

    @property
    def is_modified(self) -> bool:
        return (
            self.left_value is not None
            and self.right_value is not None
            and self.left_value != self.right_value
        )

    def __repr__(self) -> str:
        return (
            f"CompareEntry(name={self.name!r}, left={self.left_value!r},"
            f" right={self.right_value!r})"
        )


@dataclass
class CompareResult:
    left_profile: str
    right_profile: str
    entries: List[CompareEntry] = field(default_factory=list)

    @property
    def same(self) -> List[CompareEntry]:
        return [e for e in self.entries if e.is_same]

    @property
    def added(self) -> List[CompareEntry]:
        return [e for e in self.entries if e.only_in_right]

    @property
    def removed(self) -> List[CompareEntry]:
        return [e for e in self.entries if e.only_in_left]

    @property
    def modified(self) -> List[CompareEntry]:
        return [e for e in self.entries if e.is_modified]

    @property
    def has_differences(self) -> bool:
        return bool(self.added or self.removed or self.modified)

    def summary(self) -> str:
        return (
            f"same={len(self.same)}, added={len(self.added)},"
            f" removed={len(self.removed)}, modified={len(self.modified)}"
        )


class ProfileComparer:
    def compare(
        self,
        left_vars: Dict[str, str],
        right_vars: Dict[str, str],
        left_profile: str = "left",
        right_profile: str = "right",
    ) -> CompareResult:
        all_keys: Set[str] = set(left_vars) | set(right_vars)
        entries = [
            CompareEntry(
                name=key,
                left_value=left_vars.get(key),
                right_value=right_vars.get(key),
            )
            for key in sorted(all_keys)
        ]
        return CompareResult(
            left_profile=left_profile,
            right_profile=right_profile,
            entries=entries,
        )
