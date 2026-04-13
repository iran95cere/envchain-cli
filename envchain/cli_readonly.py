"""CLI commands for read-only variable protection."""
from __future__ import annotations

import sys
from typing import Optional

from envchain.env_readonly import ReadOnlyManager, ReadOnlyViolation


class ReadOnlyCommand:
    def __init__(self, storage_dir: str):
        self._manager = ReadOnlyManager(storage_dir)

    def protect(self, profile: str, var_name: str, reason: Optional[str] = None) -> None:
        """Mark a variable as read-only in the given profile."""
        entry = self._manager.protect(profile, var_name, reason=reason)
        msg = f"Protected '{var_name}' in profile '{profile}'."
        if reason:
            msg += f" Reason: {reason}"
        print(msg)

    def unprotect(self, profile: str, var_name: str) -> None:
        """Remove read-only protection from a variable."""
        removed = self._manager.unprotect(profile, var_name)
        if removed:
            print(f"Unprotected '{var_name}' in profile '{profile}'.")
        else:
            print(
                f"Variable '{var_name}' was not protected in profile '{profile}'.",
                file=sys.stderr,
            )
            sys.exit(1)

    def check(self, profile: str, var_name: str) -> None:
        """Check whether a variable is read-only and print its status."""
        if self._manager.is_protected(profile, var_name):
            entries = {e.var_name: e for e in self._manager.list_protected(profile)}
            entry = entries[var_name]
            reason_part = f" ({entry.reason})" if entry.reason else ""
            print(f"PROTECTED: '{var_name}' in '{profile}' is read-only{reason_part}.")
        else:
            print(f"WRITABLE: '{var_name}' in '{profile}' is not protected.")

    def list_protected(self, profile: str) -> None:
        """List all read-only variables for a profile."""
        entries = self._manager.list_protected(profile)
        if not entries:
            print(f"No protected variables in profile '{profile}'.")
            return
        print(f"Protected variables in '{profile}':")
        for e in entries:
            reason_part = f"  [{e.reason}]" if e.reason else ""
            print(f"  {e.var_name}{reason_part}  (since {e.locked_at})")
