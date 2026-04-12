"""CLI commands for variable expiry management."""
from __future__ import annotations

import sys
from envchain.env_expiry import ExpiryManager


class ExpiryCommand:
    """Handles CLI interactions for variable expiry."""

    def __init__(self, manager: ExpiryManager | None = None) -> None:
        self._manager = manager or ExpiryManager()

    def set(self, profile: str, var_name: str, ttl: float) -> None:
        """Set a TTL (in seconds) for a variable in a profile."""
        try:
            entry = self._manager.set_expiry(profile, var_name, ttl)
            print(f"Expiry set: {profile}/{var_name} expires in {ttl:.0f}s")
            print(f"  Expires at: {entry.expires_at:.2f}")
        except ValueError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)

    def status(self, profile: str, var_name: str) -> None:
        """Show expiry status for a variable."""
        entry = self._manager.get_entry(profile, var_name)
        if entry is None:
            print(f"No expiry set for {profile}/{var_name}")
            return
        if entry.is_expired():
            print(f"{profile}/{var_name}: EXPIRED")
        else:
            print(f"{profile}/{var_name}: {entry.seconds_remaining():.1f}s remaining")

    def list_entries(self, profile: str | None = None) -> None:
        """List all tracked expiry entries, optionally filtered by profile."""
        entries = self._manager.all_entries()
        if profile:
            entries = [e for e in entries if e.profile == profile]
        if not entries:
            print("No expiry entries found.")
            return
        for entry in entries:
            tag = "[EXPIRED]" if entry.is_expired() else f"[{entry.seconds_remaining():.1f}s]"
            print(f"  {entry.profile}/{entry.var_name} {tag}")

    def purge(self) -> None:
        """Remove all expired entries and report."""
        removed = self._manager.purge_expired()
        if not removed:
            print("No expired entries to purge.")
        else:
            for e in removed:
                print(f"Purged: {e.profile}/{e.var_name}")
            print(f"{len(removed)} entry/entries purged.")

    def remove(self, profile: str, var_name: str) -> None:
        """Remove an expiry entry without checking expiry state."""
        removed = self._manager.remove(profile, var_name)
        if removed:
            print(f"Removed expiry for {profile}/{var_name}")
        else:
            print(f"No expiry entry found for {profile}/{var_name}", file=sys.stderr)
            sys.exit(1)
