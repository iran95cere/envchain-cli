"""CLI command for password rotation."""

from __future__ import annotations

import getpass
import sys
from typing import List, Optional

from envchain.rotation import PasswordRotator
from envchain.storage import EnvStorage


class RotationCommand:
    """Handles the 'rotate' sub-command."""

    def __init__(self, storage: EnvStorage) -> None:
        self._storage = storage
        self._rotator = PasswordRotator(storage)

    def run(
        self,
        profile_names: List[str],
        note: Optional[str] = None,
    ) -> None:
        """Interactively rotate passwords for one or more profiles."""
        if not profile_names:
            print("Error: at least one profile name is required.", file=sys.stderr)
            sys.exit(1)

        old_password = getpass.getpass("Current password: ")
        new_password = getpass.getpass("New password: ")
        confirm = getpass.getpass("Confirm new password: ")

        if new_password != confirm:
            print("Error: new passwords do not match.", file=sys.stderr)
            sys.exit(1)

        errors: List[str] = []
        for name in profile_names:
            try:
                record = self._rotator.rotate(name, old_password, new_password, note=note)
                print(f"Rotated: {record}")
            except ValueError as exc:
                errors.append(str(exc))
            except Exception as exc:  # noqa: BLE001
                errors.append(f"{name}: decryption failed — {exc}")

        if errors:
            for err in errors:
                print(f"Error: {err}", file=sys.stderr)
            sys.exit(1)
