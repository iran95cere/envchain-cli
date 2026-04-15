"""Case conversion utilities for environment variable names and values."""
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List
import re


class CaseStyle(str, Enum):
    UPPER = "upper"
    LOWER = "lower"
    SNAKE = "snake"
    SCREAMING_SNAKE = "screaming_snake"


@dataclass
class CaseResult:
    name: str
    original: str
    converted: str
    style: CaseStyle

    @property
    def changed(self) -> bool:
        return self.original != self.converted

    def __repr__(self) -> str:
        arrow = f"{self.original!r} -> {self.converted!r}" if self.changed else f"{self.original!r} (unchanged)"
        return f"CaseResult({self.name}: {arrow})"


@dataclass
class CaseReport:
    results: List[CaseResult] = field(default_factory=list)

    @property
    def changed_count(self) -> int:
        return sum(1 for r in self.results if r.changed)

    @property
    def has_changes(self) -> bool:
        return self.changed_count > 0

    def to_dict(self) -> dict:
        return {
            "changed_count": self.changed_count,
            "total": len(self.results),
            "results": [{"name": r.name, "original": r.original, "converted": r.converted} for r in self.results if r.changed],
        }


class EnvCaseConverter:
    """Converts environment variable names or values to a target case style."""

    def convert_vars(self, vars_dict: Dict[str, str], style: CaseStyle, target: str = "name") -> CaseReport:
        """Convert names or values in vars_dict to the given style.

        Args:
            vars_dict: mapping of variable name -> value
            style: target CaseStyle
            target: 'name' to convert keys, 'value' to convert values
        """
        results = []
        for name, value in vars_dict.items():
            original = name if target == "name" else value
            converted = self._apply(original, style)
            results.append(CaseResult(name=name, original=original, converted=converted, style=style))
        return CaseReport(results=results)

    def _apply(self, text: str, style: CaseStyle) -> str:
        if style == CaseStyle.UPPER:
            return text.upper()
        if style == CaseStyle.LOWER:
            return text.lower()
        if style in (CaseStyle.SNAKE, CaseStyle.SCREAMING_SNAKE):
            # Insert underscore before uppercase letters following lowercase letters
            s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", text)
            s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", s)
            s = s.replace("-", "_").replace(" ", "_")
            return s.upper() if style == CaseStyle.SCREAMING_SNAKE else s.lower()
        return text
