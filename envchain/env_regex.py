"""Regex-based filtering and validation for environment variable names and values."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class RegexMatch:
    name: str
    value: str
    pattern: str

    def __repr__(self) -> str:
        return f"RegexMatch(name={self.name!r}, pattern={self.pattern!r})"

    def to_dict(self) -> dict:
        return {"name": self.name, "value": self.value, "pattern": self.pattern}


@dataclass
class RegexReport:
    matches: List[RegexMatch] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    @property
    def match_count(self) -> int:
        return len(self.matches)

    @property
    def has_errors(self) -> bool:
        return bool(self.errors)

    def __repr__(self) -> str:
        return f"RegexReport(matches={self.match_count}, errors={len(self.errors)})"


class EnvRegex:
    """Filter environment variables using regular expressions."""

    def match_by_name(
        self,
        vars: Dict[str, str],
        pattern: str,
        flags: int = 0,
    ) -> RegexReport:
        report = RegexReport()
        try:
            compiled = re.compile(pattern, flags)
        except re.error as exc:
            report.errors.append(f"Invalid pattern {pattern!r}: {exc}")
            return report
        for name, value in vars.items():
            if compiled.search(name):
                report.matches.append(RegexMatch(name=name, value=value, pattern=pattern))
        return report

    def match_by_value(
        self,
        vars: Dict[str, str],
        pattern: str,
        flags: int = 0,
    ) -> RegexReport:
        report = RegexReport()
        try:
            compiled = re.compile(pattern, flags)
        except re.error as exc:
            report.errors.append(f"Invalid pattern {pattern!r}: {exc}")
            return report
        for name, value in vars.items():
            if compiled.search(value):
                report.matches.append(RegexMatch(name=name, value=value, pattern=pattern))
        return report

    def validate_pattern(self, pattern: str) -> Optional[str]:
        """Return an error message if pattern is invalid, else None."""
        try:
            re.compile(pattern)
            return None
        except re.error as exc:
            return str(exc)
