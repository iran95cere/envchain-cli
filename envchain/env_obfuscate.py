"""Obfuscation utilities for environment variable values."""
from __future__ import annotations

import base64
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class ObfuscateResult:
    name: str
    original: str
    obfuscated: str
    changed: bool

    def __repr__(self) -> str:  # pragma: no cover
        state = "obfuscated" if self.changed else "unchanged"
        return f"<ObfuscateResult name={self.name!r} state={state}>"


@dataclass
class ObfuscateReport:
    results: List[ObfuscateResult] = field(default_factory=list)

    @property
    def obfuscated_count(self) -> int:
        return sum(1 for r in self.results if r.changed)

    @property
    def has_changes(self) -> bool:
        return self.obfuscated_count > 0

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<ObfuscateReport total={len(self.results)}"
            f" obfuscated={self.obfuscated_count}>"
        )


class EnvObfuscator:
    """Reversibly obfuscate environment variable values using base64 encoding."""

    PREFIX = "obf:"

    def obfuscate(self, vars_: Dict[str, str]) -> ObfuscateReport:
        """Obfuscate all non-already-obfuscated values."""
        results: List[ObfuscateResult] = []
        for name, value in vars_.items():
            if value.startswith(self.PREFIX):
                results.append(ObfuscateResult(name, value, value, changed=False))
            else:
                encoded = self.PREFIX + base64.b64encode(value.encode()).decode()
                results.append(ObfuscateResult(name, value, encoded, changed=True))
        return ObfuscateReport(results=results)

    def deobfuscate(self, vars_: Dict[str, str]) -> ObfuscateReport:
        """Decode previously obfuscated values."""
        results: List[ObfuscateResult] = []
        for name, value in vars_.items():
            if value.startswith(self.PREFIX):
                payload = value[len(self.PREFIX):]
                decoded = base64.b64decode(payload.encode()).decode()
                results.append(ObfuscateResult(name, value, decoded, changed=True))
            else:
                results.append(ObfuscateResult(name, value, value, changed=False))
        return ObfuscateReport(results=results)

    def to_flat_dict(self, report: ObfuscateReport) -> Dict[str, str]:
        """Return a plain dict of name -> obfuscated/deobfuscated value."""
        return {r.name: r.obfuscated for r in report.results}
