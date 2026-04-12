"""Masking rules for sensitive environment variable values."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

# Patterns whose matching var names are masked by default
_DEFAULT_SENSITIVE_PATTERNS: List[str] = [
    r"(?i)(password|passwd|secret|token|api[_-]?key|private[_-]?key|auth)",
]


@dataclass
class MaskRule:
    """A single masking rule keyed by a regex pattern on the variable name."""

    pattern: str
    mask_char: str = "*"
    reveal_chars: int = 0  # how many trailing chars to leave visible

    def matches(self, name: str) -> bool:
        return bool(re.search(self.pattern, name))

    def apply(self, value: str) -> str:
        if not value:
            return value
        visible = value[-self.reveal_chars:] if self.reveal_chars else ""
        hidden_len = len(value) - len(visible)
        return self.mask_char * hidden_len + visible

    def __repr__(self) -> str:  # pragma: no cover
        return f"MaskRule(pattern={self.pattern!r}, reveal_chars={self.reveal_chars})"


@dataclass
class MaskReport:
    """Result of masking a dict of env vars."""

    original: Dict[str, str]
    masked: Dict[str, str]
    masked_keys: List[str] = field(default_factory=list)

    @property
    def mask_count(self) -> int:
        return len(self.masked_keys)

    def __repr__(self) -> str:
        return f"MaskReport(mask_count={self.mask_count})"


class EnvMasker:
    """Apply masking rules to a dict of environment variables."""

    def __init__(self, rules: Optional[List[MaskRule]] = None) -> None:
        if rules is None:
            rules = [MaskRule(p) for p in _DEFAULT_SENSITIVE_PATTERNS]
        self.rules: List[MaskRule] = rules

    def add_rule(self, rule: MaskRule) -> None:
        self.rules.append(rule)

    def mask(self, vars_dict: Dict[str, str]) -> MaskReport:
        masked: Dict[str, str] = {}
        masked_keys: List[str] = []
        for name, value in vars_dict.items():
            applied = False
            for rule in self.rules:
                if rule.matches(name):
                    masked[name] = rule.apply(value)
                    masked_keys.append(name)
                    applied = True
                    break
            if not applied:
                masked[name] = value
        return MaskReport(original=vars_dict, masked=masked, masked_keys=masked_keys)

    def is_sensitive(self, name: str) -> bool:
        return any(rule.matches(name) for rule in self.rules)
