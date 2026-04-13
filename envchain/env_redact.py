"""Redaction support for environment variable values."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional


# Patterns whose matching var names should be redacted by default
_DEFAULT_PATTERNS: List[str] = [
    r"(?i)password",
    r"(?i)secret",
    r"(?i)token",
    r"(?i)api[_-]?key",
    r"(?i)private[_-]?key",
    r"(?i)auth",
    r"(?i)credential",
]


@dataclass
class RedactResult:
    name: str
    original: str
    redacted: str
    was_redacted: bool

    def __repr__(self) -> str:
        status = "redacted" if self.was_redacted else "plain"
        return f"<RedactResult name={self.name!r} status={status}>"


@dataclass
class RedactReport:
    results: List[RedactResult] = field(default_factory=list)

    @property
    def redacted_count(self) -> int:
        return sum(1 for r in self.results if r.was_redacted)

    @property
    def has_redacted(self) -> bool:
        return self.redacted_count > 0

    def to_dict(self) -> Dict[str, str]:
        return {r.name: r.redacted for r in self.results}

    def __repr__(self) -> str:
        return (
            f"<RedactReport total={len(self.results)} "
            f"redacted={self.redacted_count}>"
        )


class EnvRedactor:
    """Redacts sensitive environment variable values based on name patterns."""

    PLACEHOLDER = "***REDACTED***"

    def __init__(
        self,
        patterns: Optional[List[str]] = None,
        placeholder: str = PLACEHOLDER,
    ) -> None:
        raw = patterns if patterns is not None else _DEFAULT_PATTERNS
        self._compiled = [re.compile(p) for p in raw]
        self.placeholder = placeholder

    def is_sensitive(self, name: str) -> bool:
        return any(p.search(name) for p in self._compiled)

    def redact_value(self, name: str, value: str) -> RedactResult:
        if self.is_sensitive(name):
            return RedactResult(
                name=name,
                original=value,
                redacted=self.placeholder,
                was_redacted=True,
            )
        return RedactResult(
            name=name, original=value, redacted=value, was_redacted=False
        )

    def redact_all(self, vars_: Dict[str, str]) -> RedactReport:
        results = [self.redact_value(k, v) for k, v in vars_.items()]
        return RedactReport(results=results)
