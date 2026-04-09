"""Tag management for environment variable profiles."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set


@dataclass
class TagIndex:
    """Maps tags to profile names for quick lookup."""
    _index: Dict[str, Set[str]] = field(default_factory=dict)

    def add(self, tag: str, profile: str) -> None:
        """Associate a tag with a profile."""
        tag = tag.strip().lower()
        if not tag:
            raise ValueError("Tag must not be empty.")
        self._index.setdefault(tag, set()).add(profile)

    def remove(self, tag: str, profile: str) -> None:
        """Remove a tag association from a profile."""
        tag = tag.strip().lower()
        if tag in self._index:
            self._index[tag].discard(profile)
            if not self._index[tag]:
                del self._index[tag]

    def profiles_for_tag(self, tag: str) -> List[str]:
        """Return sorted list of profiles associated with the given tag."""
        tag = tag.strip().lower()
        return sorted(self._index.get(tag, set()))

    def tags_for_profile(self, profile: str) -> List[str]:
        """Return sorted list of tags associated with the given profile."""
        return sorted(tag for tag, profiles in self._index.items() if profile in profiles)

    def all_tags(self) -> List[str]:
        """Return all known tags in sorted order."""
        return sorted(self._index.keys())

    def to_dict(self) -> Dict[str, List[str]]:
        """Serialise the index to a plain dict."""
        return {tag: sorted(profiles) for tag, profiles in self._index.items()}

    @classmethod
    def from_dict(cls, data: Dict[str, List[str]]) -> "TagIndex":
        """Deserialise a TagIndex from a plain dict."""
        obj = cls()
        for tag, profiles in data.items():
            for profile in profiles:
                obj.add(tag, profile)
        return obj

    def __repr__(self) -> str:  # pragma: no cover
        return f"TagIndex(tags={self.all_tags()})"
