"""Escape and unescape environment variable values for safe shell usage."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class EscapeResult:
    name: str
    original: str
    escaped: str

    @property
    def changed(self) -> bool:
        return self.original != self.escaped

    def __repr__(self) -> str:
        status = "changed" if self.changed else "unchanged"
        return f"EscapeResult(name={self.name!r}, status={status})"


@dataclass
class EscapeReport:
    results: List[EscapeResult] = field(default_factory=list)

    @property
    def changed_count(self) -> int:
        return sum(1 for r in self.results if r.changed)

    @property
    def has_changes(self) -> bool:
        return self.changed_count > 0

    def to_dict(self) -> Dict[str, str]:
        return {r.name: r.escaped for r in self.results}

    def __repr__(self) -> str:
        return (
            f"EscapeReport(total={len(self.results)}, changed={self.changed_count})"
        )


class EnvEscaper:
    """Escape environment variable values for safe shell embedding."""

    # Characters that need escaping in double-quoted shell strings
    _SPECIAL = re.compile(r'(["\\`$!])')

    def escape(self, vars_: Dict[str, str]) -> EscapeReport:
        """Escape all values and return a report."""
        results = []
        for name, value in vars_.items():
            escaped = self._escape_value(value)
            results.append(EscapeResult(name=name, original=value, escaped=escaped))
        return EscapeReport(results=results)

    def unescape(self, vars_: Dict[str, str]) -> Dict[str, str]:
        """Reverse a previously escaped set of values."""
        return {name: self._unescape_value(value) for name, value in vars_.items()}

    def _escape_value(self, value: str) -> str:
        return self._SPECIAL.sub(r"\\\1", value)

    def _unescape_value(self, value: str) -> str:
        return re.sub(r'\\(["\\`$!])', r"\1", value)
