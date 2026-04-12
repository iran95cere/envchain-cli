"""Variable value formatting and type coercion utilities."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class FormatResult:
    original: str
    formatted: str
    fmt_type: str
    changed: bool = False

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"FormatResult(type={self.fmt_type!r}, changed={self.changed}, "
            f"original={self.original!r}, formatted={self.formatted!r})"
        )


@dataclass
class FormatReport:
    results: List[FormatResult] = field(default_factory=list)

    @property
    def changed_count(self) -> int:
        return sum(1 for r in self.results if r.changed)

    @property
    def has_changes(self) -> bool:
        return self.changed_count > 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "changed_count": self.changed_count,
            "results": [
                {
                    "name": r.original,
                    "formatted": r.formatted,
                    "type": r.fmt_type,
                    "changed": r.changed,
                }
                for r in self.results
            ],
        }


class EnvFormatter:
    """Apply formatting rules to environment variable values."""

    SUPPORTED_FORMATS = ("trim", "upper", "lower", "strip_quotes")

    def format_value(self, value: str, fmt_type: str) -> FormatResult:
        """Format a single value according to *fmt_type*."""
        if fmt_type not in self.SUPPORTED_FORMATS:
            raise ValueError(
                f"Unknown format type {fmt_type!r}. "
                f"Supported: {self.SUPPORTED_FORMATS}"
            )
        formatted = self._apply(value, fmt_type)
        return FormatResult(
            original=value,
            formatted=formatted,
            fmt_type=fmt_type,
            changed=(formatted != value),
        )

    def format_vars(
        self,
        vars_dict: Dict[str, str],
        fmt_type: str,
        keys: Optional[List[str]] = None,
    ) -> FormatReport:
        """Apply *fmt_type* to all (or selected) variables and return a report."""
        report = FormatReport()
        targets = keys if keys is not None else list(vars_dict.keys())
        for name in targets:
            if name not in vars_dict:
                continue
            result = self.format_value(vars_dict[name], fmt_type)
            result.original = name  # reuse field to store var name for report
            report.results.append(result)
        return report

    # ------------------------------------------------------------------
    def _apply(self, value: str, fmt_type: str) -> str:
        if fmt_type == "trim":
            return value.strip()
        if fmt_type == "upper":
            return value.upper()
        if fmt_type == "lower":
            return value.lower()
        if fmt_type == "strip_quotes":
            if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
                return value[1:-1]
            return value
        return value  # pragma: no cover
