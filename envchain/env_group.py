"""Group management for environment variable profiles."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import json
import os


@dataclass
class Group:
    name: str
    profiles: List[str] = field(default_factory=list)
    description: str = ""

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "profiles": list(self.profiles),
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Group":
        return cls(
            name=data["name"],
            profiles=list(data.get("profiles", [])),
            description=data.get("description", ""),
        )

    def __repr__(self) -> str:
        return f"Group(name={self.name!r}, profiles={self.profiles!r})"


class GroupManager:
    """Manages named groups of profiles stored in a JSON file."""

    def __init__(self, storage_dir: str) -> None:
        self._path = os.path.join(storage_dir, "groups.json")
        self._groups: Dict[str, Group] = {}
        self._load()

    def _load(self) -> None:
        if os.path.exists(self._path):
            with open(self._path, "r", encoding="utf-8") as fh:
                raw = json.load(fh)
            self._groups = {k: Group.from_dict(v) for k, v in raw.items()}

    def _save(self) -> None:
        with open(self._path, "w", encoding="utf-8") as fh:
            json.dump({k: v.to_dict() for k, v in self._groups.items()}, fh, indent=2)

    def create(self, name: str, description: str = "") -> Group:
        if name in self._groups:
            raise ValueError(f"Group {name!r} already exists.")
        group = Group(name=name, description=description)
        self._groups[name] = group
        self._save()
        return group

    def delete(self, name: str) -> None:
        if name not in self._groups:
            raise KeyError(f"Group {name!r} not found.")
        del self._groups[name]
        self._save()

    def add_profile(self, group_name: str, profile: str) -> None:
        group = self._get(group_name)
        if profile not in group.profiles:
            group.profiles.append(profile)
            self._save()

    def remove_profile(self, group_name: str, profile: str) -> None:
        group = self._get(group_name)
        if profile in group.profiles:
            group.profiles.remove(profile)
            self._save()

    def list_groups(self) -> List[Group]:
        return list(self._groups.values())

    def get(self, name: str) -> Optional[Group]:
        return self._groups.get(name)

    def _get(self, name: str) -> Group:
        if name not in self._groups:
            raise KeyError(f"Group {name!r} not found.")
        return self._groups[name]

    def groups_for_profile(self, profile: str) -> List[str]:
        return [g.name for g in self._groups.values() if profile in g.profiles]
