"""Checkpoint management: save and restore named environment snapshots inline."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class Checkpoint:
    name: str
    profile: str
    vars: Dict[str, str]
    created_at: float = field(default_factory=time.time)
    description: str = ""

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "profile": self.profile,
            "vars": self.vars,
            "created_at": self.created_at,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Checkpoint":
        return cls(
            name=data["name"],
            profile=data["profile"],
            vars=data["vars"],
            created_at=data.get("created_at", time.time()),
            description=data.get("description", ""),
        )

    def __repr__(self) -> str:
        return f"<Checkpoint name={self.name!r} profile={self.profile!r} vars={len(self.vars)}>"


class CheckpointManager:
    _FILENAME = "checkpoints.json"

    def __init__(self, storage_dir: Path) -> None:
        self._path = Path(storage_dir) / self._FILENAME
        self._data: Dict[str, List[dict]] = self._load()

    def _load(self) -> Dict[str, List[dict]]:
        if self._path.exists():
            return json.loads(self._path.read_text())
        return {}

    def _save(self) -> None:
        self._path.write_text(json.dumps(self._data, indent=2))

    def save(self, checkpoint: Checkpoint) -> None:
        self._data.setdefault(checkpoint.profile, [])
        # Remove existing checkpoint with same name
        self._data[checkpoint.profile] = [
            c for c in self._data[checkpoint.profile] if c["name"] != checkpoint.name
        ]
        self._data[checkpoint.profile].append(checkpoint.to_dict())
        self._save()

    def load(self, profile: str, name: str) -> Optional[Checkpoint]:
        for entry in self._data.get(profile, []):
            if entry["name"] == name:
                return Checkpoint.from_dict(entry)
        return None

    def list_checkpoints(self, profile: str) -> List[Checkpoint]:
        return [
            Checkpoint.from_dict(e)
            for e in self._data.get(profile, [])
        ]

    def delete(self, profile: str, name: str) -> bool:
        before = len(self._data.get(profile, []))
        self._data[profile] = [
            c for c in self._data.get(profile, []) if c["name"] != name
        ]
        changed = len(self._data.get(profile, [])) < before
        if changed:
            self._save()
        return changed
