"""CLI commands for archiving and restoring profile bundles."""
from __future__ import annotations

import sys
from pathlib import Path

from envchain.env_archive import ArchiveManager


class ArchiveCommand:
    """Handles 'archive' sub-commands: create and restore."""

    def __init__(self, storage_dir: Path) -> None:
        self._manager = ArchiveManager(Path(storage_dir))

    # ------------------------------------------------------------------
    def create(self, dest: str, profiles: list[str] | None = None) -> None:
        """Create a zip archive of one or more profiles."""
        dest_path = Path(dest)
        try:
            out = self._manager.create_archive(dest_path, profiles or None)
            selected = profiles or "all"
            print(f"Archive created: {out}")
            if isinstance(selected, list):
                print(f"  Included profiles: {', '.join(selected)}")
            else:
                print("  Included profiles: all")
        except FileNotFoundError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)

    # ------------------------------------------------------------------
    def restore(self, src: str, overwrite: bool = False) -> None:
        """Restore profiles from a zip archive."""
        src_path = Path(src)
        if not src_path.exists():
            print(f"Error: archive not found: {src}", file=sys.stderr)
            sys.exit(1)
        try:
            manifest = self._manager.restore_archive(src_path, overwrite=overwrite)
            print(
                f"Restored {len(manifest.profiles)} profile(s): "
                f"{', '.join(manifest.profiles)}"
            )
        except FileExistsError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)
        except Exception as exc:  # noqa: BLE001
            print(f"Error restoring archive: {exc}", file=sys.stderr)
            sys.exit(1)
