"""CLI commands for managing audit policies."""
from __future__ import annotations

import sys
from typing import Optional

from envchain.env_audit_policy import AuditPolicyManager, PolicyRule


class AuditPolicyCommand:
    def __init__(self, manager: Optional[AuditPolicyManager] = None) -> None:
        self._manager = manager or AuditPolicyManager()

    def add(self, profile: str, action: str,
            require_reason: bool = False,
            max_value_length: Optional[int] = None) -> None:
        valid_actions = {"read", "write", "delete"}
        if action not in valid_actions:
            print(f"[error] Invalid action '{action}'. Choose from: {', '.join(sorted(valid_actions))}",
                  file=sys.stderr)
            sys.exit(1)
        rule = PolicyRule(
            profile=profile,
            action=action,
            require_reason=require_reason,
            max_value_length=max_value_length,
        )
        self._manager.add_rule(rule)
        print(f"[ok] Policy rule added: {rule}")

    def remove(self, profile: str, action: str) -> None:
        removed = self._manager.remove_rule(profile, action)
        if removed:
            print(f"[ok] Policy rule removed for profile='{profile}' action='{action}'.")
        else:
            print(f"[warn] No matching rule found for profile='{profile}' action='{action}'.")

    def list_rules(self) -> None:
        rules = self._manager.all_rules()
        if not rules:
            print("No audit policy rules defined.")
            return
        for rule in rules:
            parts = [f"profile={rule.profile!r}", f"action={rule.action!r}"]
            if rule.require_reason:
                parts.append("require_reason=True")
            if rule.max_value_length is not None:
                parts.append(f"max_value_length={rule.max_value_length}")
            print("  " + "  ".join(parts))

    def check(self, profile: str, action: str,
              value: Optional[str] = None,
              reason: Optional[str] = None) -> None:
        violations = self._manager.check(profile, action, value=value, reason=reason)
        if not violations:
            print("[ok] No policy violations.")
        else:
            for v in violations:
                print(f"[violation] {v.message}", file=sys.stderr)
            sys.exit(1)
