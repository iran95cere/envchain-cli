"""CLI surface for the rollback feature."""
from __future__ import annotations

import sys
from typing import Optional

from envchain.env_rollback import RollbackManager
from envchain.snapshot import SnapshotManager


class RollbackCommand:
    def __init__(self, storage, storage_dir: str) -> None:
        self._storage = storage
        self._sm = SnapshotManager(storage_dir)
        self._mgr = RollbackManager(storage, self._sm)

    # ------------------------------------------------------------------
    def list_snapshots(self, profile: str) -> None:
        """Print available snapshots for *profile*."""
        snaps = self._mgr.list_snapshots(profile)
        if not snaps:
            print(f"No snapshots found for profile '{profile}'.")
            return
        print(f"Snapshots for '{profile}':")
        for s in snaps:
            print(f"  {s.label}  ({s.created_at})")

    def run(
        self,
        profile: str,
        snapshot_label: str,
        password: str,
        *,
        dry_run: bool = False,
    ) -> None:
        """Rollback *profile* to *snapshot_label*."""
        try:
            if dry_run:
                snaps = self._mgr.list_snapshots(profile)
                target = next((s for s in snaps if s.label == snapshot_label), None)
                if target is None:
                    print(
                        f"[dry-run] Snapshot '{snapshot_label}' not found "
                        f"for profile '{profile}'.",
                        file=sys.stderr,
                    )
                    sys.exit(1)
                print(
                    f"[dry-run] Would rollback '{profile}' to snapshot '{snapshot_label}' "
                    f"({len(target.variables)} vars)."
                )
                return

            record = self._mgr.rollback(profile, snapshot_label, password)
            print(
                f"Rolled back '{record.profile}' to snapshot '{record.rolled_back_to}' "
                f"at {record.timestamp}."
            )
        except KeyError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)
