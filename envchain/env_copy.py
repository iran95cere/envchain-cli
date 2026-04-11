"""Copy variables between profiles with optional filtering."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envchain.storage import EnvStorage


@dataclass
class CopyResult:
    copied: Dict[str, str] = field(default_factory=dict)
    skipped: List[str] = field(default_factory=list)
    source_profile: str = ""
    target_profile: str = ""

    @property
    def copy_count(self) -> int:
        return len(self.copied)

    @property
    def skip_count(self) -> int:
        return len(self.skipped)

    @property
    def has_skipped(self) -> bool:
        return bool(self.skipped)

    def __repr__(self) -> str:
        return (
            f"CopyResult(source={self.source_profile!r}, "
            f"target={self.target_profile!r}, "
            f"copied={self.copy_count}, skipped={self.skip_count})"
        )


class EnvCopier:
    """Copies environment variables from one profile to another."""

    def __init__(self, storage: EnvStorage) -> None:
        self._storage = storage

    def copy(
        self,
        source: str,
        target: str,
        password: str,
        keys: Optional[List[str]] = None,
        prefix: Optional[str] = None,
        overwrite: bool = False,
    ) -> CopyResult:
        """Copy variables from *source* profile into *target* profile.

        Args:
            source: Name of the source profile.
            target: Name of the destination profile.
            password: Encryption password (must unlock both profiles).
            keys: Explicit list of variable names to copy. If None, copy all.
            prefix: Only copy variables whose names start with this prefix.
            overwrite: If False, skip variables that already exist in target.

        Returns:
            A :class:`CopyResult` describing what was copied or skipped.
        """
        src_profile = self._storage.load_profile(source, password)
        if src_profile is None:
            raise ValueError(f"Source profile {source!r} not found.")

        tgt_profile = self._storage.load_profile(target, password)
        if tgt_profile is None:
            raise ValueError(f"Target profile {target!r} not found.")

        result = CopyResult(source_profile=source, target_profile=target)

        candidates = dict(src_profile.vars)

        if keys is not None:
            candidates = {k: v for k, v in candidates.items() if k in keys}

        if prefix is not None:
            candidates = {k: v for k, v in candidates.items() if k.startswith(prefix)}

        for name, value in candidates.items():
            if not overwrite and tgt_profile.get_var(name) is not None:
                result.skipped.append(name)
            else:
                tgt_profile.add_var(name, value)
                result.copied[name] = value

        if result.copy_count > 0:
            self._storage.save_profile(tgt_profile, password)

        return result
