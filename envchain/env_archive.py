"""Archive and restore profiles to/from compressed bundles."""
from __future__ import annotations

import json
import zipfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional


@dataclass
class ArchiveManifest:
    created_at: str
    profiles: List[str]
    version: str = "1"

    def to_dict(self) -> dict:
        return {
            "version": self.version,
            "created_at": self.created_at,
            "profiles": self.profiles,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ArchiveManifest":
        return cls(
            created_at=data["created_at"],
            profiles=data["profiles"],
            version=data.get("version", "1"),
        )

    def __repr__(self) -> str:
        return (
            f"ArchiveManifest(profiles={self.profiles!r}, "
            f"created_at={self.created_at!r})"
        )


class ArchiveManager:
    """Create and restore zip-based profile archives."""

    MANIFEST_NAME = "manifest.json"

    def __init__(self, storage_dir: Path) -> None:
        self._storage_dir = Path(storage_dir)

    def create_archive(self, dest: Path, profiles: Optional[List[str]] = None) -> Path:
        """Bundle profile files into a zip archive at *dest*."""
        dest = Path(dest)
        available = self._available_profiles()
        selected = profiles if profiles is not None else available
        missing = [p for p in selected if p not in available]
        if missing:
            raise FileNotFoundError(
                f"Profiles not found: {', '.join(missing)}"
            )
        manifest = ArchiveManifest(
            created_at=datetime.now(timezone.utc).isoformat(),
            profiles=selected,
        )
        with zipfile.ZipFile(dest, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.writestr(self.MANIFEST_NAME, json.dumps(manifest.to_dict()))
            for name in selected:
                profile_path = self._storage_dir / f"{name}.enc"
                zf.write(profile_path, arcname=f"{name}.enc")
        return dest

    def restore_archive(self, src: Path, overwrite: bool = False) -> ArchiveManifest:
        """Unpack an archive into the storage directory."""
        src = Path(src)
        with zipfile.ZipFile(src, "r") as zf:
            raw = zf.read(self.MANIFEST_NAME)
            manifest = ArchiveManifest.from_dict(json.loads(raw))
            for name in manifest.profiles:
                dest_path = self._storage_dir / f"{name}.enc"
                if dest_path.exists() and not overwrite:
                    raise FileExistsError(
                        f"Profile '{name}' already exists; use overwrite=True."
                    )
                data = zf.read(f"{name}.enc")
                dest_path.write_bytes(data)
        return manifest

    def _available_profiles(self) -> List[str]:
        return [
            p.stem for p in self._storage_dir.glob("*.enc")
        ]
