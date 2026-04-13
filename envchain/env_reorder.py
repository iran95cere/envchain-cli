"""Reorder environment variables within a profile by a given key list or sort criteria."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ReorderResult:
    profile: str
    original_order: List[str]
    new_order: List[str]
    unknown_keys: List[str] = field(default_factory=list)

    @property
    def is_changed(self) -> bool:
        return self.original_order != self.new_order

    @property
    def moved_count(self) -> int:
        return sum(1 for a, b in zip(self.original_order, self.new_order) if a != b)

    def __repr__(self) -> str:
        return (
            f"ReorderResult(profile={self.profile!r}, "
            f"changed={self.is_changed}, moved={self.moved_count})"
        )


class EnvReorder:
    """Reorder variables in a profile dict according to an explicit key list."""

    def reorder(self, vars_: Dict[str, str], key_order: List[str],
                profile: str = "") -> ReorderResult:
        """Return a ReorderResult with vars sorted by *key_order*.

        Keys present in *key_order* but absent from *vars_* are recorded as
        unknown.  Keys in *vars_* but absent from *key_order* are appended at
        the end in their original relative order.
        """
        original = list(vars_.keys())
        unknown = [k for k in key_order if k not in vars_]
        explicit = [k for k in key_order if k in vars_]
        remainder = [k for k in original if k not in set(explicit)]
        new_order = explicit + remainder
        return ReorderResult(
            profile=profile,
            original_order=original,
            new_order=new_order,
            unknown_keys=unknown,
        )

    def apply(self, vars_: Dict[str, str], key_order: List[str]) -> Dict[str, str]:
        """Return a new dict with keys in the reordered sequence."""
        result = self.reorder(vars_, key_order)
        return {k: vars_[k] for k in result.new_order}
