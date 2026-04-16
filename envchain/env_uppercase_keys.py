"""Normalize environment variable key casing to UPPER_SNAKE_CASE."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class KeyNormalizeResult:
    name: str
    original_key: str
    new_key: str

    @property
    def changed(self) -> bool:
        return self.original_key != self.new_key

    def __repr__(self) -> str:
        status = "changed" if self.changed else "unchanged"
        return f"<KeyNormalizeResult {self.original_key!r} -> {self.new_key!r} [{status}]>"


@dataclass
class KeyNormalizeReport:
    results: List[KeyNormalizeResult] = field(default_factory=list)

    @property
    def changed_count(self) -> int:
        return sum(1 for r in self.results if r.changed)

    @property
    def has_changes(self) -> bool:
        return self.changed_count > 0

    def to_normalized_vars(self) -> Dict[str, str]:
        """Return vars dict keyed by new (normalized) keys."""
        return {r.new_key: r.name for r in self.results}

    def __repr__(self) -> str:
        return f"<KeyNormalizeReport total={len(self.results)} changed={self.changed_count}>"


class EnvKeyNormalizer:
    """Normalize variable keys to UPPER_SNAKE_CASE."""

    _CAMEL_RE = re.compile(r'(?<=[a-z0-9])(?=[A-Z])')

    def normalize(self, vars_: Dict[str, str]) -> KeyNormalizeReport:
        results: List[KeyNormalizeResult] = []
        for key, value in vars_.items():
            new_key = self._to_upper_snake(key)
            results.append(KeyNormalizeResult(name=value, original_key=key, new_key=new_key))
        return KeyNormalizeReport(results=results)

    def apply(self, vars_: Dict[str, str]) -> Dict[str, str]:
        return {self._to_upper_snake(k): v for k, v in vars_.items()}

    def _to_upper_snake(self, key: str) -> str:
        key = self._CAMEL_RE.sub('_', key)
        key = re.sub(r'[\s\-]+', '_', key)
        key = re.sub(r'_+', '_', key)
        return key.upper().strip('_')
