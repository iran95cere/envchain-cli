"""Split a profile's variables into multiple sub-profiles by prefix."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class SplitResult:
    prefix: str
    vars: Dict[str, str] = field(default_factory=dict)

    @property
    def var_count(self) -> int:
        return len(self.vars)

    def __repr__(self) -> str:  # pragma: no cover
        return f"SplitResult(prefix={self.prefix!r}, vars={self.var_count})"


@dataclass
class SplitReport:
    results: List[SplitResult] = field(default_factory=list)
    unmatched: Dict[str, str] = field(default_factory=dict)

    @property
    def group_count(self) -> int:
        return len(self.results)

    @property
    def unmatched_count(self) -> int:
        return len(self.unmatched)

    @property
    def has_unmatched(self) -> bool:
        return bool(self.unmatched)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"SplitReport(groups={self.group_count}, "
            f"unmatched={self.unmatched_count})"
        )


class EnvSplitter:
    """Split environment variables into groups based on name prefixes."""

    def split(self, vars: Dict[str, str], prefixes: List[str],
              strip_prefix: bool = False) -> SplitReport:
        """Group *vars* by the first matching prefix in *prefixes*.

        Args:
            vars: Mapping of variable name -> value.
            prefixes: Ordered list of prefixes to match against.
            strip_prefix: When True, remove the prefix from variable names
                          in each SplitResult.

        Returns:
            A SplitReport containing one SplitResult per prefix that had
            at least one match, plus any unmatched variables.
        """
        buckets: Dict[str, Dict[str, str]] = {p: {} for p in prefixes}
        unmatched: Dict[str, str] = {}

        for name, value in vars.items():
            matched = False
            for prefix in prefixes:
                if name.startswith(prefix):
                    key = name[len(prefix):] if strip_prefix else name
                    buckets[prefix][key] = value
                    matched = True
                    break
            if not matched:
                unmatched[name] = value

        results = [
            SplitResult(prefix=p, vars=v)
            for p, v in buckets.items()
            if v
        ]
        return SplitReport(results=results, unmatched=unmatched)
