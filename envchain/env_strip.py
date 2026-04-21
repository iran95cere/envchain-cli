"""Strip leading/trailing characters from environment variable values."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class StripResult:
    name: str
    original: str
    stripped: str
    chars: Optional[str]

    @property
    def changed(self) -> bool:
        return self.original != self.stripped

    def __repr__(self) -> str:
        if self.changed:
            return f"StripResult({self.name!r}: {self.original!r} -> {self.stripped!r})"
        return f"StripResult({self.name!r}: unchanged)"


@dataclass
class StripReport:
    results: List[StripResult] = field(default_factory=list)

    @property
    def changed_count(self) -> int:
        return sum(1 for r in self.results if r.changed)

    @property
    def has_changes(self) -> bool:
        return self.changed_count > 0

    def to_dict(self) -> Dict:
        return {
            "changed_count": self.changed_count,
            "total": len(self.results),
            "results": [
                {"name": r.name, "changed": r.changed}
                for r in self.results
            ],
        }

    def __repr__(self) -> str:
        return f"StripReport(changed={self.changed_count}/{len(self.results)})"


class EnvStripper:
    """Strip leading/trailing characters from env var values."""

    def strip(self, vars_: Dict[str, str], chars: Optional[str] = None) -> StripReport:
        """Strip *chars* (or whitespace if None) from each value."""
        results = []
        for name, value in vars_.items():
            stripped = value.strip(chars)
            results.append(StripResult(name=name, original=value, stripped=stripped, chars=chars))
        return StripReport(results=results)

    def apply(self, vars_: Dict[str, str], chars: Optional[str] = None) -> Dict[str, str]:
        """Return a new dict with stripped values."""
        report = self.strip(vars_, chars=chars)
        return {r.name: r.stripped for r in report.results}
