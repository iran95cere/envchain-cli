"""Linting rules for environment variable profiles."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class LintIssue:
    """Represents a single lint warning or error."""

    level: str  # 'warning' or 'error'
    key: str
    message: str

    def __repr__(self) -> str:
        return f"LintIssue({self.level}, {self.key!r}: {self.message})"


@dataclass
class LintReport:
    """Aggregated result of linting a profile's variables."""

    issues: List[LintIssue] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return any(i.level == "error" for i in self.issues)

    @property
    def has_warnings(self) -> bool:
        return any(i.level == "warning" for i in self.issues)

    def summary(self) -> str:
        errors = sum(1 for i in self.issues if i.level == "error")
        warnings = sum(1 for i in self.issues if i.level == "warning")
        return f"{errors} error(s), {warnings} warning(s)"


class ProfileLinter:
    """Applies a set of lint rules to a dict of environment variables."""

    # Keys whose values should never be empty
    REQUIRED_NON_EMPTY: tuple = ()

    # Common placeholder patterns that suggest a value was never set
    PLACEHOLDER_PATTERNS: tuple = ("<your", "TODO", "CHANGEME", "FIXME", "xxx")

    def lint(self, variables: Dict[str, str]) -> LintReport:
        report = LintReport()
        for key, value in variables.items():
            self._check_empty_value(report, key, value)
            self._check_placeholder(report, key, value)
            self._check_key_casing(report, key)
            self._check_whitespace(report, key, value)
        return report

    # ------------------------------------------------------------------
    # Private rule methods
    # ------------------------------------------------------------------

    def _check_empty_value(self, report: LintReport, key: str, value: str) -> None:
        if value.strip() == "":
            report.issues.append(
                LintIssue("warning", key, "Value is empty or whitespace-only")
            )

    def _check_placeholder(self, report: LintReport, key: str, value: str) -> None:
        for pattern in self.PLACEHOLDER_PATTERNS:
            if pattern.lower() in value.lower():
                report.issues.append(
                    LintIssue(
                        "warning",
                        key,
                        f"Value looks like an unfilled placeholder ({pattern!r})",
                    )
                )
                break

    def _check_key_casing(self, report: LintReport, key: str) -> None:
        if key != key.upper():
            report.issues.append(
                LintIssue("warning", key, "Environment variable names should be UPPER_CASE")
            )

    def _check_whitespace(self, report: LintReport, key: str, value: str) -> None:
        if value != value.strip():
            report.issues.append(
                LintIssue("warning", key, "Value has leading or trailing whitespace")
            )
