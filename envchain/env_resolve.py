"""Resolve environment variable references within a profile.

Supports resolving variables that reference other variables in the same
profile using ${VAR_NAME} syntax.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

_REF_PATTERN = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")


@dataclass
class ResolveIssue:
    var_name: str
    reference: str
    reason: str

    def __repr__(self) -> str:
        return f"ResolveIssue(var={self.var_name!r}, ref={self.reference!r}, reason={self.reason!r})"


@dataclass
class ResolveResult:
    resolved: Dict[str, str] = field(default_factory=dict)
    issues: List[ResolveIssue] = field(default_factory=list)

    @property
    def has_issues(self) -> bool:
        return bool(self.issues)

    @property
    def issue_count(self) -> int:
        return len(self.issues)

    def __repr__(self) -> str:
        return (
            f"ResolveResult(resolved={len(self.resolved)}, issues={self.issue_count})"
        )


class EnvResolver:
    """Resolve variable cross-references within a flat dict of env vars."""

    MAX_DEPTH = 10

    def resolve(self, vars: Dict[str, str]) -> ResolveResult:
        """Return a ResolveResult with fully-resolved values."""
        result = ResolveResult()
        for name, value in vars.items():
            resolved_value, issue = self._resolve_value(
                name, value, vars, depth=0
            )
            if issue:
                result.issues.append(issue)
                result.resolved[name] = value  # keep original on error
            else:
                result.resolved[name] = resolved_value
        return result

    def _resolve_value(
        self,
        name: str,
        value: str,
        vars: Dict[str, str],
        depth: int,
    ) -> tuple[str, Optional[ResolveIssue]]:
        if depth > self.MAX_DEPTH:
            return value, ResolveIssue(
                var_name=name,
                reference="(cycle)",
                reason="maximum resolution depth exceeded (possible cycle)",
            )

        def replacer(match: re.Match) -> str:
            ref = match.group(1)
            if ref not in vars:
                raise KeyError(ref)
            return vars[ref]

        try:
            new_value = _REF_PATTERN.sub(replacer, value)
        except KeyError as exc:
            missing = exc.args[0]
            return value, ResolveIssue(
                var_name=name,
                reference=missing,
                reason=f"referenced variable '{missing}' does not exist",
            )

        # Recurse if further references remain
        if _REF_PATTERN.search(new_value):
            return self._resolve_value(name, new_value, vars, depth + 1)

        return new_value, None
