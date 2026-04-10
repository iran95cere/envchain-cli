"""Profile alias management for envchain."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


class AliasManager:
    """Manages short aliases that map to profile names."""

    ALIAS_FILE = "aliases.json"

    def __init__(self, storage_dir: str | Path) -> None:
        self._path = Path(storage_dir) / self.ALIAS_FILE
        self._aliases: Dict[str, str] = self._load()

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _load(self) -> Dict[str, str]:
        if self._path.exists():
            try:
                return json.loads(self._path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                return {}
        return {}

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(
            json.dumps(self._aliases, indent=2, sort_keys=True), encoding="utf-8"
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def add(self, alias: str, profile: str) -> None:
        """Register *alias* as a shorthand for *profile*."""
        alias = alias.strip()
        profile = profile.strip()
        if not alias:
            raise ValueError("Alias must not be empty.")
        if not profile:
            raise ValueError("Profile name must not be empty.")
        if alias == profile:
            raise ValueError("Alias must differ from the profile name.")
        self._aliases[alias] = profile
        self._save()

    def remove(self, alias: str) -> bool:
        """Remove *alias*. Returns True if it existed, False otherwise."""
        if alias in self._aliases:
            del self._aliases[alias]
            self._save()
            return True
        return False

    def resolve(self, alias: str) -> Optional[str]:
        """Return the profile name for *alias*, or None if not found."""
        return self._aliases.get(alias)

    def list_aliases(self) -> List[Dict[str, str]]:
        """Return all aliases sorted by alias key."""
        return [
            {"alias": k, "profile": v}
            for k, v in sorted(self._aliases.items())
        ]

    def aliases_for_profile(self, profile: str) -> List[str]:
        """Return all aliases that point to *profile*."""
        return [k for k, v in self._aliases.items() if v == profile]

    def rename_profile(self, old: str, new: str) -> int:
        """Update all aliases pointing to *old* to point to *new*.

        Returns the number of aliases updated.
        """
        updated = 0
        for k, v in list(self._aliases.items()):
            if v == old:
                self._aliases[k] = new
                updated += 1
        if updated:
            self._save()
        return updated
