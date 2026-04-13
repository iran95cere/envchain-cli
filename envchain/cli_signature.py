"""CLI commands for profile signature management."""
from __future__ import annotations

import sys
from getpass import getpass
from typing import Optional

from envchain.env_signature import SignatureManager


class SignatureCommand:
    def __init__(self, storage, secret_key: Optional[str] = None) -> None:
        self._storage = storage
        key = secret_key or getpass("Signature secret key: ")
        self._manager = SignatureManager(key)

    def sign(self, profile_name: str) -> None:
        profile = self._storage.load_profile(profile_name)
        if profile is None:
            print(f"Error: profile '{profile_name}' not found.", file=sys.stderr)
            sys.exit(1)
        entry = self._manager.sign(profile_name, profile.vars)
        print(f"Signed profile '{profile_name}' at {entry.signed_at}.")

    def verify(self, profile_name: str) -> None:
        profile = self._storage.load_profile(profile_name)
        if profile is None:
            print(f"Error: profile '{profile_name}' not found.", file=sys.stderr)
            sys.exit(1)
        result = self._manager.verify(profile_name, profile.vars)
        if result.valid:
            print(f"Signature valid for profile '{profile_name}'.")
        else:
            print(
                f"Signature INVALID for profile '{profile_name}': {result.reason}.",
                file=sys.stderr,
            )
            sys.exit(1)

    def remove(self, profile_name: str) -> None:
        removed = self._manager.remove(profile_name)
        if removed:
            print(f"Signature removed for profile '{profile_name}'.")
        else:
            print(f"No signature found for profile '{profile_name}'.")

    def list_signed(self) -> None:
        names = self._manager.list_signed()
        if not names:
            print("No signed profiles.")
            return
        for name in sorted(names):
            print(f"  {name}")
