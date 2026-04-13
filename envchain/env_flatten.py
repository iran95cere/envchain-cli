"""Flatten nested or prefixed environment variable groups into a single dict."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class FlattenResult:
    """Result of a flatten operation on a set of env vars."""
    original: Dict[str, str]
    flattened: Dict[str, str]
    separator: str = "__"
    prefix_filter: Optional[str] = None

    @property
    def changed_count(self) -> int:
        """Number of keys whose names changed during flattening."""
        return sum(
            1 for k in self.flattened if k not in self.original
        )

    @property
    def is_changed(self) -> bool:
        return self.changed_count > 0

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"FlattenResult(original={len(self.original)} vars, "
            f"flattened={len(self.flattened)} vars, "
            f"changed={self.changed_count})"
        )


class EnvFlattener:
    """Flatten env var keys that use a hierarchical separator into dotted names."""

    def __init__(self, separator: str = "__") -> None:
        self.separator = separator

    def flatten(self, vars: Dict[str, str], prefix_filter: Optional[str] = None) -> FlattenResult:
        """Return a FlattenResult converting SECTION__KEY style keys to SECTION.KEY.

        If *prefix_filter* is given, only keys starting with that prefix are
        processed; others are passed through unchanged.
        """
        flattened: Dict[str, str] = {}
        for key, value in vars.items():
            if prefix_filter and not key.startswith(prefix_filter):
                flattened[key] = value
                continue
            new_key = key.replace(self.separator, ".") if self.separator in key else key
            flattened[new_key] = value
        return FlattenResult(
            original=dict(vars),
            flattened=flattened,
            separator=self.separator,
            prefix_filter=prefix_filter,
        )

    def unflatten(self, vars: Dict[str, str]) -> Dict[str, str]:
        """Reverse: convert dotted keys back to SECTION__KEY style."""
        return {k.replace(".", self.separator): v for k, v in vars.items()}
