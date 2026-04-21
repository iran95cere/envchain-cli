"""CLI commands for profile-directory pinning."""
from __future__ import annotations

import os
import sys

from envchain.env_pin_profile import PinProfileManager


class PinProfileCommand:
    def __init__(self, storage_dir: str) -> None:
        self._manager = PinProfileManager(storage_dir)

    def pin(self, directory: str, profile: str) -> None:
        entry = self._manager.pin(directory, profile)
        print(f"Pinned profile '{entry.profile}' to directory '{entry.directory}'.")

    def unpin(self, directory: str) -> None:
        removed = self._manager.unpin(directory)
        if removed:
            print(f"Unpinned directory '{directory}'.")
        else:
            print(f"No pin found for directory '{directory}'.")
            sys.exit(1)

    def resolve(self, directory: str | None = None) -> None:
        target = directory or os.getcwd()
        profile = self._manager.resolve(target)
        if profile:
            print(profile)
        else:
            print(f"No profile pinned to '{target}'.")
            sys.exit(1)

    def list_pins(self) -> None:
        pins = self._manager.list_pins()
        if not pins:
            print("No directory pins configured.")
            return
        for entry in pins:
            print(f"  {entry.directory}  ->  {entry.profile}")
