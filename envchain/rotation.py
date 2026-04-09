"""Password rotation support for envchain profiles."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional

from envchain.crypto import EnvCrypto
from envchain.storage import EnvStorage


@dataclass
class RotationRecord:
    """Tracks a single password rotation event."""

    profile_name: str
    rotated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    note: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "profile_name": self.profile_name,
            "rotated_at": self.rotated_at,
            "note": self.note,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "RotationRecord":
        obj = cls(profile_name=data["profile_name"])
        obj.rotated_at = data["rotated_at"]
        obj.note = data.get("note")
        return obj

    def __repr__(self) -> str:
        return f"<RotationRecord profile={self.profile_name!r} at={self.rotated_at!r}>"


class PasswordRotator:
    """Re-encrypts a profile's variables under a new password."""

    def __init__(self, storage: EnvStorage) -> None:
        self._storage = storage

    def rotate(
        self,
        profile_name: str,
        old_password: str,
        new_password: str,
        note: Optional[str] = None,
    ) -> RotationRecord:
        """Decrypt with *old_password* and re-encrypt with *new_password*.

        Returns a :class:`RotationRecord` describing the event.
        Raises ``ValueError`` if the profile does not exist.
        Raises ``KeyError`` / decryption errors if *old_password* is wrong.
        """
        profile = self._storage.load_profile(profile_name, old_password)
        if profile is None:
            raise ValueError(f"Profile '{profile_name}' not found.")

        self._storage.save_profile(profile, new_password)
        return RotationRecord(profile_name=profile_name, note=note)

    def bulk_rotate(
        self,
        profile_names: List[str],
        old_password: str,
        new_password: str,
    ) -> List[RotationRecord]:
        """Rotate multiple profiles at once. Returns records for each success."""
        records: List[RotationRecord] = []
        for name in profile_names:
            record = self.rotate(name, old_password, new_password)
            records.append(record)
        return records
