"""Detect and report unresolved placeholder variables in profiles."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

# Matches ${VAR_NAME} or $VAR_NAME style placeholders inside values
_PLACEHOLDER_RE = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}|\$([A-Za-z_][A-Za-z0-9_]*)")


@dataclass
class PlaceholderIssue:
    var_name: str          # the env var whose value contains the placeholder
    placeholder: str       # the unresolved placeholder token, e.g. "${DB_HOST}"

    def __repr__(self) -> str:
        return f"PlaceholderIssue(var={self.var_name!r}, placeholder={self.placeholder!r})"


@dataclass
class PlaceholderReport:
    profile_name: str
    issues: List[PlaceholderIssue] = field(default_factory=list)

    @property
    def has_issues(self) -> bool:
        return len(self.issues) > 0

    @property
    def issue_count(self) -> int:
        return len(self.issues)

    def to_dict(self) -> dict:
        return {
            "profile": self.profile_name,
            "issues": [
                {"var": i.var_name, "placeholder": i.placeholder}
                for i in self.issues
            ],
        }

    def __repr__(self) -> str:
        return (
            f"PlaceholderReport(profile={self.profile_name!r}, "
            f"issues={self.issue_count})"
        )


class PlaceholderChecker:
    """Scan profile variables for unresolved placeholder references."""

    def check(self, profile_name: str, variables: Dict[str, str]) -> PlaceholderReport:
        """Return a PlaceholderReport for the given variable mapping."""
        report = PlaceholderReport(profile_name=profile_name)
        for var_name, value in variables.items():
            for match in _PLACEHOLDER_RE.finditer(value):
                token = match.group(0)
                inner = match.group(1) or match.group(2)
                # Only flag if the placeholder name is NOT itself resolved
                # (i.e. not present as a key in the same variable set)
                if inner not in variables:
                    report.issues.append(
                        PlaceholderIssue(var_name=var_name, placeholder=token)
                    )
        return report

    def check_resolved(self, variables: Dict[str, str]) -> Dict[str, str]:
        """Return a copy of variables with placeholders substituted where possible."""
        result: Dict[str, str] = {}
        for var_name, value in variables.items():
            def _replace(m: re.Match) -> str:  # noqa: E306
                inner = m.group(1) or m.group(2)
                return variables.get(inner, m.group(0))
            result[var_name] = _PLACEHOLDER_RE.sub(_replace, value)
        return result
