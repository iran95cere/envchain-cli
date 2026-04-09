"""Backup and restore functionality for envchain profiles."""

import json
import os
import tarfile
import tempfile
from datetime import datetime
from pathlib import Path
from typing import List, Optional


class BackupManager:
    """Manages creation and restoration of profile backups."""

    BACKUP_EXTENSION = ".envchain.tar.gz"

    def __init__(self, storage_dir: str):
        self.storage_dir = Path(storage_dir)

    def create_backup(self, output_path: Optional[str] = None) -> str:
        """Create a compressed backup of all profiles.

        Args:
            output_path: Optional path for the backup file. Defaults to
                         a timestamped file in the current directory.

        Returns:
            Path to the created backup file.
        """
        if output_path is None:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            output_path = f"envchain_backup_{timestamp}{self.BACKUP_EXTENSION}"

        output_path = str(output_path)
        if not output_path.endswith(".tar.gz"):
            output_path += ".tar.gz"

        with tarfile.open(output_path, "w:gz") as tar:
            if self.storage_dir.exists():
                tar.add(self.storage_dir, arcname="profiles")

        return output_path

    def restore_backup(self, backup_path: str, overwrite: bool = False) -> List[str]:
        """Restore profiles from a backup file.

        Args:
            backup_path: Path to the backup tar.gz file.
            overwrite: If True, overwrite existing profiles.

        Returns:
            List of restored profile names.
        """
        if not os.path.exists(backup_path):
            raise FileNotFoundError(f"Backup file not found: {backup_path}")

        restored = []
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        with tarfile.open(backup_path, "r:gz") as tar:
            for member in tar.getmembers():
                if not member.name.startswith("profiles/"):
                    continue
                relative = member.name[len("profiles/"):]
                if not relative:
                    continue
                dest = self.storage_dir / relative
                if dest.exists() and not overwrite:
                    continue
                tar.extract(member, path=self.storage_dir.parent)
                if member.isfile():
                    restored.append(Path(relative).stem)

        return restored

    def list_backups(self, search_dir: str = ".") -> List[str]:
        """List backup files in a directory."""
        return sorted(
            str(p)
            for p in Path(search_dir).glob(f"*{self.BACKUP_EXTENSION}")
        )
