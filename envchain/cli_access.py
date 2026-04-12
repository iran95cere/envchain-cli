"""CLI commands for access control management."""
from __future__ import annotations

import sys
from typing import List

from envchain.env_access import AccessManager, AccessRule


class AccessCommand:
    def __init__(self, storage_dir: str) -> None:
        self._manager = AccessManager(storage_dir)

    def add(self, profile: str, allowed: List[str], denied: List[str], read_only: bool) -> None:
        rule = AccessRule(
            profile=profile,
            allowed_users=allowed,
            denied_users=denied,
            read_only=read_only,
        )
        self._manager.set_rule(rule)
        print(f"Access rule set for profile '{profile}'.")
        if read_only:
            print("  Mode: read-only")
        if allowed:
            print(f"  Allowed: {', '.join(allowed)}")
        if denied:
            print(f"  Denied:  {', '.join(denied)}")

    def remove(self, profile: str) -> None:
        if self._manager.remove_rule(profile):
            print(f"Access rule removed for profile '{profile}'.")
        else:
            print(f"No access rule found for profile '{profile}'.")
            sys.exit(1)

    def check(self, profile: str, user: str, write: bool = False) -> None:
        result = self._manager.check(profile, user, write=write)
        status = "ALLOWED" if result.allowed else "DENIED"
        print(f"[{status}] {result.reason}")
        if not result.allowed:
            sys.exit(1)

    def list_rules(self) -> None:
        rules = self._manager.list_rules()
        if not rules:
            print("No access rules defined.")
            return
        for rule in rules:
            ro = " [read-only]" if rule.read_only else ""
            allowed = ", ".join(rule.allowed_users) if rule.allowed_users else "*"
            denied = ", ".join(rule.denied_users) if rule.denied_users else "none"
            print(f"{rule.profile}{ro}  allowed={allowed}  denied={denied}")
