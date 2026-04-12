"""Audit policy enforcement for environment variable access and mutations."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class PolicyRule:
    profile: str
    action: str          # 'read' | 'write' | 'delete'
    require_reason: bool = False
    max_value_length: Optional[int] = None

    def to_dict(self) -> dict:
        return {
            "profile": self.profile,
            "action": self.action,
            "require_reason": self.require_reason,
            "max_value_length": self.max_value_length,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PolicyRule":
        return cls(
            profile=data["profile"],
            action=data["action"],
            require_reason=data.get("require_reason", False),
            max_value_length=data.get("max_value_length"),
        )

    def __repr__(self) -> str:
        return f"<PolicyRule profile={self.profile!r} action={self.action!r}>"


@dataclass
class PolicyViolation:
    rule: PolicyRule
    message: str
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def __repr__(self) -> str:
        return f"<PolicyViolation {self.message!r}>"


class AuditPolicyManager:
    def __init__(self) -> None:
        self._rules: List[PolicyRule] = []

    def add_rule(self, rule: PolicyRule) -> None:
        self._rules.append(rule)

    def remove_rule(self, profile: str, action: str) -> bool:
        before = len(self._rules)
        self._rules = [
            r for r in self._rules
            if not (r.profile == profile and r.action == action)
        ]
        return len(self._rules) < before

    def rules_for(self, profile: str, action: str) -> List[PolicyRule]:
        return [r for r in self._rules if r.profile == profile and r.action == action]

    def check(self, profile: str, action: str, value: Optional[str] = None,
              reason: Optional[str] = None) -> List[PolicyViolation]:
        violations: List[PolicyViolation] = []
        for rule in self.rules_for(profile, action):
            if rule.require_reason and not reason:
                violations.append(PolicyViolation(
                    rule=rule,
                    message=f"Action '{action}' on profile '{profile}' requires a reason.",
                ))
            if rule.max_value_length is not None and value is not None:
                if len(value) > rule.max_value_length:
                    violations.append(PolicyViolation(
                        rule=rule,
                        message=(
                            f"Value length {len(value)} exceeds max "
                            f"{rule.max_value_length} for '{action}' on '{profile}'."
                        ),
                    ))
        return violations

    def all_rules(self) -> List[PolicyRule]:
        return list(self._rules)
