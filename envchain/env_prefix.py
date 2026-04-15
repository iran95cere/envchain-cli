"""Prefix management for environment variable names."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class PrefixResult:
    name: str
    original: str
    transformed: str
    changed: bool

    def __repr__(self) -> str:
        status = "changed" if self.changed else "unchanged"
        return f"<PrefixResult {self.name!r} {status}>"


@dataclass
class PrefixReport:
    results: List[PrefixResult] = field(default_factory=list)

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
                {"name": r.name, "original": r.original, "transformed": r.transformed, "changed": r.changed}
                for r in self.results
            ],
        }


class EnvPrefixer:
    """Add or remove a prefix from environment variable names."""

    def add_prefix(self, vars_: Dict[str, str], prefix: str) -> PrefixReport:
        """Return a report with prefix added to all variable names."""
        if not prefix:
            raise ValueError("prefix must not be empty")
        results = []
        for name, value in vars_.items():
            if name.startswith(prefix):
                results.append(PrefixResult(name=name, original=name, transformed=name, changed=False))
            else:
                new_name = prefix + name
                results.append(PrefixResult(name=name, original=name, transformed=new_name, changed=True))
        return PrefixReport(results=results)

    def remove_prefix(self, vars_: Dict[str, str], prefix: str) -> PrefixReport:
        """Return a report with prefix stripped from matching variable names."""
        if not prefix:
            raise ValueError("prefix must not be empty")
        results = []
        for name, value in vars_.items():
            if name.startswith(prefix):
                new_name = name[len(prefix):]
                changed = bool(new_name) and new_name != name
                results.append(PrefixResult(name=name, original=name, transformed=new_name if changed else name, changed=changed))
            else:
                results.append(PrefixResult(name=name, original=name, transformed=name, changed=False))
        return PrefixReport(results=results)

    def apply(self, vars_: Dict[str, str], report: PrefixReport) -> Dict[str, str]:
        """Apply a PrefixReport to produce a new vars dict."""
        result = {}
        name_map = {r.name: r.transformed for r in report.results}
        for name, value in vars_.items():
            new_name = name_map.get(name, name)
            if new_name:
                result[new_name] = value
        return result
