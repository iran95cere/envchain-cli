"""Profile rollback support: revert a profile to a previous snapshot."""
from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envchain.snapshot import SnapshotManager, Snapshot


@dataclass
class RollbackRecord:
    profile: str
    rolled_back_to: str          # snapshot label / id
    timestamp: str = field(default_factory=lambda: datetime.datetime.utcnow().isoformat())
    previous_vars: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "profile": self.profile,
            "rolled_back_to": self.rolled_back_to,
            "timestamp": self.timestamp,
            "previous_vars": self.previous_vars,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "RollbackRecord":
        return cls(
            profile=data["profile"],
            rolled_back_to=data["rolled_back_to"],
            timestamp=data.get("timestamp", ""),
            previous_vars=data.get("previous_vars", {}),
        )

    def __repr__(self) -> str:
        return (
            f"RollbackRecord(profile={self.profile!r}, "
            f"to={self.rolled_back_to!r}, at={self.timestamp!r})"
        )


class RollbackManager:
    """Revert a profile's variables to a previously saved snapshot."""

    def __init__(self, storage, snapshot_manager: SnapshotManager) -> None:
        self._storage = storage
        self._snapshots = snapshot_manager

    def list_snapshots(self, profile: str) -> List[Snapshot]:
        """Return all snapshots available for *profile*."""
        return [
            s for s in self._snapshots.list_snapshots()
            if s.profile == profile
        ]

    def rollback(self, profile: str, snapshot_label: str, password: str) -> RollbackRecord:
        """Restore *profile* to the state stored in *snapshot_label*.

        Returns a :class:`RollbackRecord` describing what was done.
        Raises ``KeyError`` if the snapshot cannot be found.
        """
        snapshots = self.list_snapshots(profile)
        target: Optional[Snapshot] = next(
            (s for s in snapshots if s.label == snapshot_label), None
        )
        if target is None:
            raise KeyError(f"Snapshot {snapshot_label!r} not found for profile {profile!r}")

        current_profile = self._storage.load_profile(profile, password)
        previous_vars = dict(current_profile.variables) if current_profile else {}

        current_profile.variables = dict(target.variables)
        self._storage.save_profile(current_profile, password)

        return RollbackRecord(
            profile=profile,
            rolled_back_to=snapshot_label,
            previous_vars=previous_vars,
        )
