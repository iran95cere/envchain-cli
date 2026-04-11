"""Quota management for environment variable profiles."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional


DEFAULT_MAX_VARS = 100
DEFAULT_MAX_VALUE_LENGTH = 4096


@dataclass
class QuotaPolicy:
    max_vars: int = DEFAULT_MAX_VARS
    max_value_length: int = DEFAULT_MAX_VALUE_LENGTH

    def to_dict(self) -> dict:
        return {
            "max_vars": self.max_vars,
            "max_value_length": self.max_value_length,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "QuotaPolicy":
        return cls(
            max_vars=data.get("max_vars", DEFAULT_MAX_VARS),
            max_value_length=data.get("max_value_length", DEFAULT_MAX_VALUE_LENGTH),
        )

    def __repr__(self) -> str:
        return (
            f"QuotaPolicy(max_vars={self.max_vars}, "
            f"max_value_length={self.max_value_length})"
        )


@dataclass
class QuotaViolation:
    field: str
    message: str

    def __repr__(self) -> str:
        return f"QuotaViolation(field={self.field!r}, message={self.message!r})"


@dataclass
class QuotaCheckResult:
    violations: list = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return len(self.violations) == 0

    def __repr__(self) -> str:
        return f"QuotaCheckResult(passed={self.passed}, violations={len(self.violations)})"


class QuotaManager:
    """Checks environment variable sets against a quota policy."""

    def __init__(self, policy: Optional[QuotaPolicy] = None):
        self.policy = policy or QuotaPolicy()

    def check(self, vars: Dict[str, str]) -> QuotaCheckResult:
        """Validate a variable dict against the current policy."""
        result = QuotaCheckResult()

        if len(vars) > self.policy.max_vars:
            result.violations.append(
                QuotaViolation(
                    field="var_count",
                    message=(
                        f"Profile has {len(vars)} variables, "
                        f"exceeds limit of {self.policy.max_vars}."
                    ),
                )
            )

        for name, value in vars.items():
            if len(value) > self.policy.max_value_length:
                result.violations.append(
                    QuotaViolation(
                        field=name,
                        message=(
                            f"Value for '{name}' is {len(value)} chars, "
                            f"exceeds limit of {self.policy.max_value_length}."
                        ),
                    )
                )

        return result
