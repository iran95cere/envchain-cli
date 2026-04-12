"""Clone (deep-copy) a profile into a new profile name, with optional variable filtering."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class CloneResult:
    source_profile: str
    target_profile: str
    copied_vars: List[str] = field(default_factory=list)
    skipped_vars: List[str] = field(default_factory=list)
    error: Optional[str] = None

    @property
    def success(self) -> bool:
        return self.error is None

    @property
    def copy_count(self) -> int:
        return len(self.copied_vars)

    @property
    def skip_count(self) -> int:
        return len(self.skipped_vars)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"CloneResult(src={self.source_profile!r}, dst={self.target_profile!r}, "
            f"copied={self.copy_count}, skipped={self.skip_count})"
        )


class EnvCloner:
    """Clone variables from one profile into another."""

    def __init__(self, storage) -> None:
        self._storage = storage

    def clone(
        self,
        source: str,
        target: str,
        prefix_filter: Optional[str] = None,
        exclude: Optional[List[str]] = None,
        overwrite: bool = False,
    ) -> CloneResult:
        """Clone *source* profile into *target*, returning a CloneResult."""
        result = CloneResult(source_profile=source, target_profile=target)

        src_profile = self._storage.load_profile(source)
        if src_profile is None:
            result.error = f"Source profile '{source}' not found."
            return result

        dst_profile = self._storage.load_profile(target)
        existing_keys: Dict[str, str] = {}
        if dst_profile is not None:
            existing_keys = dict(dst_profile.variables)

        exclude_set = set(exclude or [])
        merged: Dict[str, str] = dict(existing_keys)

        for name, value in src_profile.variables.items():
            if name in exclude_set:
                result.skipped_vars.append(name)
                continue
            if prefix_filter and not name.startswith(prefix_filter):
                result.skipped_vars.append(name)
                continue
            if name in existing_keys and not overwrite:
                result.skipped_vars.append(name)
                continue
            merged[name] = value
            result.copied_vars.append(name)

        if dst_profile is None:
            from envchain.models import Profile
            dst_profile = Profile(name=target, variables=merged)
        else:
            dst_profile.variables = merged

        self._storage.save_profile(dst_profile)
        return result
