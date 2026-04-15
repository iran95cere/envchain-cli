"""Variable interpolation: expand ${VAR} references within profile values."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

_REF_RE = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")


@dataclass
class InterpolateResult:
    name: str
    original: str
    resolved: str
    refs: List[str] = field(default_factory=list)

    @property
    def changed(self) -> bool:
        return self.original != self.resolved

    def __repr__(self) -> str:  # pragma: no cover
        return f"InterpolateResult({self.name!r}, changed={self.changed})"


@dataclass
class InterpolateReport:
    results: List[InterpolateResult] = field(default_factory=list)
    unresolved: List[str] = field(default_factory=list)

    @property
    def changed_count(self) -> int:
        return sum(1 for r in self.results if r.changed)

    @property
    def has_unresolved(self) -> bool:
        return bool(self.unresolved)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"InterpolateReport(changed={self.changed_count}, "
            f"unresolved={len(self.unresolved)})"
        )


class EnvInterpolator:
    """Expand ${VAR} placeholders in env var values using the same profile's vars."""

    def interpolate(
        self,
        variables: Dict[str, str],
        *,
        strict: bool = False,
        max_passes: int = 5,
    ) -> InterpolateReport:
        """Resolve all ${VAR} references iteratively until stable or max_passes."""
        resolved = dict(variables)
        report_results: List[InterpolateResult] = []
        unresolved_names: List[str] = []

        for _ in range(max_passes):
            changed_this_pass = False
            for name, value in list(resolved.items()):
                new_value, still_missing = self._expand(value, resolved)
                if new_value != resolved[name]:
                    resolved[name] = new_value
                    changed_this_pass = True
            if not changed_this_pass:
                break

        for name, original in variables.items():
            refs = _REF_RE.findall(original)
            final, missing = self._expand(resolved[name], resolved)
            if missing and strict:
                raise ValueError(
                    f"Unresolved reference(s) in '{name}': {missing}"
                )
            report_results.append(
                InterpolateResult(
                    name=name,
                    original=original,
                    resolved=resolved[name],
                    refs=refs,
                )
            )
            for m in missing:
                if m not in unresolved_names:
                    unresolved_names.append(m)

        return InterpolateReport(results=report_results, unresolved=unresolved_names)

    # ------------------------------------------------------------------
    def _expand(
        self, value: str, context: Dict[str, str]
    ) -> tuple[str, List[str]]:
        missing: List[str] = []

        def replacer(m: re.Match) -> str:
            key = m.group(1)
            if key in context:
                return context[key]
            missing.append(key)
            return m.group(0)

        result = _REF_RE.sub(replacer, value)
        return result, missing
