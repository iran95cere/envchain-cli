"""CLI commands for backup and restore operations."""

import os
from envchain.backup import BackupManager


class BackupCommand:
    """Handles backup and restore CLI subcommands."""

    def __init__(self, storage_dir: str):
        self.manager = BackupManager(storage_dir)

    def create(self, output_path: str = None) -> None:
        """Create a backup of all profiles."""
        try:
            path = self.manager.create_backup(output_path)
            print(f"Backup created: {path}")
        except Exception as e:
            print(f"Error creating backup: {e}")
            raise SystemExit(1)

    def restore(self, backup_path: str, overwrite: bool = False) -> None:
        """Restore profiles from a backup file."""
        try:
            restored = self.manager.restore_backup(backup_path, overwrite=overwrite)
            if restored:
                print(f"Restored {len(restored)} profile(s): {', '.join(restored)}")
            else:
                msg = "No profiles restored."
                if not overwrite:
                    msg += " Use --overwrite to replace existing profiles."
                print(msg)
        except FileNotFoundError as e:
            print(f"Error: {e}")
            raise SystemExit(1)
        except Exception as e:
            print(f"Unexpected error during restore: {e}")
            raise SystemExit(1)

    def list_backups(self, search_dir: str = ".") -> None:
        """List available backup files in a directory."""
        backups = self.manager.list_backups(search_dir)
        if not backups:
            print("No backup files found.")
            return
        print(f"Found {len(backups)} backup(s):")
        for b in backups:
            size_kb = os.path.getsize(b) / 1024
            print(f"  {b}  ({size_kb:.1f} KB)")
