"""Sanitize environment variable values by stripping or replacing unsafe content."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional


# Patterns considered unsafe in env var values
_CONTROL_CHAR_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_NULL_BYTE_RE = re.compile(r"\x00")


@dataclass
class SanitizeIssue:
    var_name: str
    description: str

    def __repr__(self) -> str:  # pragma: no cover
        return f"SanitizeIssue(var={self.var_name!r}, desc={self.description!r})"


@dataclass
class SanitizeReport:
    original: Dict[str, str]
    sanitized: Dict[str, str]
    issues: List[SanitizeIssue] = field(default_factory=list)

    @property
    def changed_count(self) -> int:
        return sum(1 for k in self.original if self.original[k] != self.sanitized.get(k))

    @property
    def has_issues(self) -> bool:
        return bool(self.issues)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"SanitizeReport(changed={self.changed_count}, issues={len(self.issues)})"
        )


class EnvSanitizer:
    """Strip control characters and null bytes from environment variable values."""

    def __init__(self, strip_newlines: bool = False, replacement: str = "") -> None:
        self.strip_newlines = strip_newlines
        self.replacement = replacement

    def sanitize(self, vars_: Dict[str, str]) -> SanitizeReport:
        sanitized: Dict[str, str] = {}
        issues: List[SanitizeIssue] = []

        for name, value in vars_.items():
            cleaned, issue_desc = self._clean_value(name, value)
            sanitized[name] = cleaned
            if issue_desc:
                issues.append(SanitizeIssue(var_name=name, description=issue_desc))

        return SanitizeReport(original=dict(vars_), sanitized=sanitized, issues=issues)

    def _clean_value(self, name: str, value: str) -> tuple[str, Optional[str]]:
        descriptions: List[str] = []

        if _NULL_BYTE_RE.search(value):
            value = _NULL_BYTE_RE.sub(self.replacement, value)
            descriptions.append("null byte removed")

        if _CONTROL_CHAR_RE.search(value):
            value = _CONTROL_CHAR_RE.sub(self.replacement, value)
            descriptions.append("control characters removed")

        if self.strip_newlines and ("\n" in value or "\r" in value):
            value = value.replace("\n", self.replacement).replace("\r", self.replacement)
            descriptions.append("newlines removed")

        return value, "; ".join(descriptions) if descriptions else None
