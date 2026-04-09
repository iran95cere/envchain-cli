"""Snapshot support for capturing and restoring profile variable states."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class Snapshot:
    """Represents a point-in-time capture of a profile's variables."""

    profile_name: str
    label: str
    variables: Dict[str, str]
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict:
        return {
            "profile_name": self.profile_name,
            "label": self.label,
            "variables": self.variables,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Snapshot":
        return cls(
            profile_name=data["profile_name"],
            label=data["label"],
            variables=data["variables"],
            created_at=data["created_at"],
        )

    def __repr__(self) -> str:
        count = len(self.variables)
        return f"<Snapshot profile={self.profile_name!r} label={self.label!r} vars={count} at={self.created_at}>"


class SnapshotManager:
    """Manages saving and loading snapshots for profiles."""

    SNAPSHOT_DIR = ".snapshots"

    def __init__(self, base_dir: Path) -> None:
        self.snapshot_dir = base_dir / self.SNAPSHOT_DIR
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)

    def _snapshot_path(self, profile_name: str, label: str) -> Path:
        safe_label = label.replace("/", "_").replace(" ", "_")
        return self.snapshot_dir / f"{profile_name}__{safe_label}.json"

    def save(self, snapshot: Snapshot) -> Path:
        """Persist a snapshot to disk; returns the file path."""
        path = self._snapshot_path(snapshot.profile_name, snapshot.label)
        path.write_text(json.dumps(snapshot.to_dict(), indent=2), encoding="utf-8")
        return path

    def load(self, profile_name: str, label: str) -> Optional[Snapshot]:
        """Load a snapshot by profile name and label; returns None if missing."""
        path = self._snapshot_path(profile_name, label)
        if not path.exists():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        return Snapshot.from_dict(data)

    def list_snapshots(self, profile_name: Optional[str] = None) -> List[Snapshot]:
        """Return all snapshots, optionally filtered by profile name."""
        snapshots: List[Snapshot] = []
        for file in sorted(self.snapshot_dir.glob("*.json")):
            try:
                data = json.loads(file.read_text(encoding="utf-8"))
                snap = Snapshot.from_dict(data)
                if profile_name is None or snap.profile_name == profile_name:
                    snapshots.append(snap)
            except (KeyError, json.JSONDecodeError):
                continue
        return snapshots

    def delete(self, profile_name: str, label: str) -> bool:
        """Delete a snapshot; returns True if it existed."""
        path = self._snapshot_path(profile_name, label)
        if path.exists():
            path.unlink()
            return True
        return False
