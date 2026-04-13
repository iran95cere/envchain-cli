"""Variable value transformation pipeline for envchain profiles."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional


@dataclass
class TransformResult:
    original: str
    transformed: str
    transform_name: str

    @property
    def changed(self) -> bool:
        return self.original != self.transformed

    def __repr__(self) -> str:
        return (
            f"TransformResult(name={self.transform_name!r}, "
            f"changed={self.changed})"
        )


@dataclass
class TransformReport:
    results: List[TransformResult] = field(default_factory=list)

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
            "results": [
                {
                    "transform": r.transform_name,
                    "original": r.original,
                    "transformed": r.transformed,
                    "changed": r.changed,
                }
                for r in self.results
            ],
        }


class EnvTransformer:
    """Apply named transformations to environment variable values."""

    BUILTIN: Dict[str, Callable[[str], str]] = {
        "upper": str.upper,
        "lower": str.lower,
        "strip": str.strip,
        "trim_quotes": lambda v: v.strip("'\"" ),
        "base64_encode": lambda v: __import__("base64").b64encode(v.encode()).decode(),
        "base64_decode": lambda v: __import__("base64").b64decode(v.encode()).decode(),
    }

    def __init__(self) -> None:
        self._transforms: Dict[str, Callable[[str], str]] = dict(self.BUILTIN)

    def register(self, name: str, fn: Callable[[str], str]) -> None:
        if not name:
            raise ValueError("Transform name must not be empty.")
        self._transforms[name] = fn

    def available(self) -> List[str]:
        return sorted(self._transforms.keys())

    def apply(self, value: str, transform_name: str) -> TransformResult:
        if transform_name not in self._transforms:
            raise KeyError(f"Unknown transform: {transform_name!r}")
        transformed = self._transforms[transform_name](value)
        return TransformResult(
            original=value,
            transformed=transformed,
            transform_name=transform_name,
        )

    def apply_many(
        self,
        vars_: Dict[str, str],
        transform_name: str,
        keys: Optional[List[str]] = None,
    ) -> TransformReport:
        target_keys = keys if keys is not None else list(vars_.keys())
        results = [self.apply(vars_[k], transform_name) for k in target_keys if k in vars_]
        return TransformReport(results=results)
