"""Rename environment variable keys across a profile."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class RenameResult:
    """Result of a batch rename operation."""
    renamed: Dict[str, str] = field(default_factory=dict)   # old -> new
    skipped: List[str] = field(default_factory=list)        # old names not found
    conflicts: List[str] = field(default_factory=list)      # new names already exist

    @property
    def success_count(self) -> int:
        return len(self.renamed)

    @property
    def has_issues(self) -> bool:
        return bool(self.skipped or self.conflicts)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"RenameResult(renamed={self.success_count}, "
            f"skipped={len(self.skipped)}, conflicts={len(self.conflicts)})"
        )


class EnvRenamer:
    """Rename one or more variable keys inside a profile's variable dict."""

    def rename(
        self,
        variables: Dict[str, str],
        mapping: Dict[str, str],
        overwrite: bool = False,
    ) -> RenameResult:
        """Apply *mapping* (old_name -> new_name) to *variables* in-place.

        Parameters
        ----------
        variables:
            The mutable dict of env vars to operate on.
        mapping:
            Keys are current names, values are desired new names.
        overwrite:
            When True, allow renaming onto an existing key (the old value
            is replaced).  When False, such renames are recorded as
            conflicts and skipped.
        """
        result = RenameResult()

        for old, new in mapping.items():
            if old not in variables:
                result.skipped.append(old)
                continue

            if new in variables and new != old and not overwrite:
                result.conflicts.append(old)
                continue

            value = variables.pop(old)
            variables[new] = value
            result.renamed[old] = new

        return result

    def rename_one(
        self,
        variables: Dict[str, str],
        old_name: str,
        new_name: str,
        overwrite: bool = False,
    ) -> Optional[str]:
        """Rename a single key.  Returns the moved value or None on failure."""
        result = self.rename(variables, {old_name: new_name}, overwrite=overwrite)
        if old_name in result.renamed:
            return variables[new_name]
        return None
