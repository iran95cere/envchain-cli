"""CLI commands for managing variable protection rules."""
from __future__ import annotations

import sys
from envchain.env_protect import ProtectManager


class ProtectCommand:
    """Subcommand handler for `envchain protect`."""

    def __init__(self, storage_dir: str) -> None:
        self._manager = ProtectManager(storage_dir)

    def add(self, profile: str, var_name: str, reason: str = "") -> None:
        """Mark *var_name* in *profile* as protected."""
        entry = self._manager.protect(profile, var_name, reason)
        msg = f"Protected '{entry.var_name}' in profile '{entry.profile}'"
        if reason:
            msg += f" — {reason}"
        print(msg)

    def remove(self, profile: str, var_name: str) -> None:
        """Remove protection from *var_name* in *profile*."""
        removed = self._manager.unprotect(profile, var_name)
        if removed:
            print(f"Removed protection for '{var_name}' in profile '{profile}'.")
        else:
            print(f"'{var_name}' was not protected in profile '{profile}'.")
            sys.exit(1)

    def status(self, profile: str, var_name: str) -> None:
        """Print whether *var_name* is protected in *profile*."""
        if self._manager.is_protected(profile, var_name):
            print(f"'{var_name}' is PROTECTED in profile '{profile}'.")
        else:
            print(f"'{var_name}' is not protected in profile '{profile}'.")

    def list_protected(self, profile: str) -> None:
        """List all protected variables for *profile*."""
        entries = self._manager.list_protected(profile)
        if not entries:
            print(f"No protected variables in profile '{profile}'.")
            return
        for entry in entries:
            line = f"  {entry.var_name}"
            if entry.reason:
                line += f"  ({entry.reason})"
            print(line)
