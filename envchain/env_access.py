"""Access control for environment variable profiles."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class AccessRule:
    profile: str
    allowed_users: List[str] = field(default_factory=list)
    denied_users: List[str] = field(default_factory=list)
    read_only: bool = False

    def to_dict(self) -> dict:
        return {
            "profile": self.profile,
            "allowed_users": self.allowed_users,
            "denied_users": self.denied_users,
            "read_only": self.read_only,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AccessRule":
        return cls(
            profile=data["profile"],
            allowed_users=data.get("allowed_users", []),
            denied_users=data.get("denied_users", []),
            read_only=data.get("read_only", False),
        )

    def __repr__(self) -> str:
        return f"<AccessRule profile={self.profile!r} read_only={self.read_only}>"


@dataclass
class AccessCheckResult:
    allowed: bool
    reason: str
    checked_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def __bool__(self) -> bool:
        return self.allowed

    def __repr__(self) -> str:
        return f"<AccessCheckResult allowed={self.allowed} reason={self.reason!r}>"


class AccessManager:
    def __init__(self, storage_dir: str) -> None:
        self._path = Path(storage_dir) / "access_rules.json"
        self._rules: Dict[str, AccessRule] = {}
        self._load()

    def _load(self) -> None:
        if self._path.exists():
            data = json.loads(self._path.read_text())
            self._rules = {k: AccessRule.from_dict(v) for k, v in data.items()}

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps({k: v.to_dict() for k, v in self._rules.items()}, indent=2))

    def set_rule(self, rule: AccessRule) -> None:
        self._rules[rule.profile] = rule
        self._save()

    def get_rule(self, profile: str) -> Optional[AccessRule]:
        return self._rules.get(profile)

    def remove_rule(self, profile: str) -> bool:
        if profile in self._rules:
            del self._rules[profile]
            self._save()
            return True
        return False

    def check(self, profile: str, user: str, write: bool = False) -> AccessCheckResult:
        rule = self._rules.get(profile)
        if rule is None:
            return AccessCheckResult(allowed=True, reason="no rule defined")
        if user in rule.denied_users:
            return AccessCheckResult(allowed=False, reason=f"user {user!r} is explicitly denied")
        if rule.allowed_users and user not in rule.allowed_users:
            return AccessCheckResult(allowed=False, reason=f"user {user!r} not in allowed list")
        if write and rule.read_only:
            return AccessCheckResult(allowed=False, reason="profile is read-only")
        return AccessCheckResult(allowed=True, reason="access granted")

    def list_rules(self) -> List[AccessRule]:
        return list(self._rules.values())
