"""Secret detection and masking for environment variable values."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

# Patterns that suggest a value is sensitive
_SECRET_PATTERNS: List[re.Pattern] = [
    re.compile(r'(?i)(password|passwd|secret|token|api[_-]?key|private[_-]?key|auth)'),
    re.compile(r'(?i)(access[_-]?key|credentials|credential|cert|certificate)'),
]

_VALUE_ENTROPY_THRESHOLD = 20  # rough minimum length hinting at a generated secret


@dataclass
class SecretScanResult:
    profile: str
    flagged: Dict[str, str] = field(default_factory=dict)  # name -> reason

    @property
    def count(self) -> int:
        return len(self.flagged)

    def has_secrets(self) -> bool:
        return bool(self.flagged)

    def __repr__(self) -> str:
        return f"<SecretScanResult profile={self.profile!r} flagged={self.count}>"


class SecretScanner:
    """Scan profile variables for likely secrets and mask them on output."""

    def __init__(self, mask_char: str = "*", mask_length: int = 8) -> None:
        self.mask_char = mask_char
        self.mask_length = mask_length

    def is_secret_name(self, name: str) -> bool:
        """Return True if the variable name matches a known secret pattern."""
        return any(p.search(name) for p in _SECRET_PATTERNS)

    def is_secret_value(self, value: str) -> bool:
        """Return True if the value looks like a generated secret."""
        return len(value) >= _VALUE_ENTROPY_THRESHOLD and value == value.strip()

    def mask(self, value: str) -> str:
        """Return a masked representation of the value."""
        if not value:
            return ""
        visible = value[:2] if len(value) > 4 else ""
        return visible + self.mask_char * self.mask_length

    def scan(self, profile_name: str, variables: Dict[str, str]) -> SecretScanResult:
        """Scan a dict of variables and return flagged entries with reasons."""
        result = SecretScanResult(profile=profile_name)
        for name, value in variables.items():
            reasons: List[str] = []
            if self.is_secret_name(name):
                reasons.append("name matches secret pattern")
            if self.is_secret_value(value):
                reasons.append("value appears high-entropy")
            if reasons:
                result.flagged[name] = "; ".join(reasons)
        return result

    def masked_vars(
        self, variables: Dict[str, str], only_flagged: bool = False
    ) -> Dict[str, str]:
        """Return variables with secret values replaced by masks."""
        out: Dict[str, str] = {}
        for name, value in variables.items():
            if self.is_secret_name(name) or self.is_secret_value(value):
                out[name] = self.mask(value)
            elif not only_flagged:
                out[name] = value
        return out

    def redact(self, text: str, variables: Dict[str, str]) -> str:
        """Replace any secret variable values found verbatim in *text* with masks.

        Useful for sanitising log lines or command output that may inadvertently
        contain the raw value of a secret environment variable.
        """
        for name, value in variables.items():
            if not value:
                continue
            if self.is_secret_name(name) or self.is_secret_value(value):
                text = text.replace(value, self.mask(value))
        return text
