"""Classify environment variables into categories based on naming patterns."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import re


CATEGORY_PATTERNS: Dict[str, List[str]] = {
    "secret": [r"(?i)(password|passwd|secret|token|key|api_key|auth|credential|private)"],
    "database": [r"(?i)(db_|database|postgres|mysql|mongo|redis|sql)"],
    "network": [r"(?i)(host|port|url|uri|endpoint|address|domain)"],
    "feature_flag": [r"(?i)(feature_|flag_|enable_|disable_|toggle_)"],
    "path": [r"(?i)(path|dir|directory|folder|root|home)"],
    "debug": [r"(?i)(debug|verbose|log_level|trace)"],
}


@dataclass
class ClassifyResult:
    name: str
    value: str
    category: str
    matched_pattern: Optional[str] = None

    def __repr__(self) -> str:
        return f"ClassifyResult(name={self.name!r}, category={self.category!r})"

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "value": self.value,
            "category": self.category,
            "matched_pattern": self.matched_pattern,
        }


@dataclass
class ClassifyReport:
    results: List[ClassifyResult] = field(default_factory=list)

    @property
    def category_counts(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for r in self.results:
            counts[r.category] = counts.get(r.category, 0) + 1
        return counts

    @property
    def has_secrets(self) -> bool:
        return any(r.category == "secret" for r in self.results)

    def by_category(self, category: str) -> List[ClassifyResult]:
        return [r for r in self.results if r.category == category]

    def __repr__(self) -> str:
        return f"ClassifyReport(total={len(self.results)}, categories={list(self.category_counts.keys())})"


class EnvClassifier:
    def __init__(self, extra_patterns: Optional[Dict[str, List[str]]] = None) -> None:
        self._patterns = dict(CATEGORY_PATTERNS)
        if extra_patterns:
            for cat, pats in extra_patterns.items():
                self._patterns.setdefault(cat, []).extend(pats)

    def classify_one(self, name: str, value: str) -> ClassifyResult:
        for category, patterns in self._patterns.items():
            for pat in patterns:
                if re.search(pat, name):
                    return ClassifyResult(
                        name=name, value=value, category=category, matched_pattern=pat
                    )
        return ClassifyResult(name=name, value=value, category="general")

    def classify(self, vars_: Dict[str, str]) -> ClassifyReport:
        results = [self.classify_one(k, v) for k, v in vars_.items()]
        return ClassifyReport(results=results)
