"""Type casting for environment variable values."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


CAST_TYPES = ("str", "int", "float", "bool", "json")


@dataclass
class CastResult:
    name: str
    original: str
    casted: Any
    cast_type: str
    success: bool
    error: str = ""

    def __repr__(self) -> str:
        status = "ok" if self.success else f"error:{self.error}"
        return f"<CastResult {self.name} -> {self.cast_type} [{status}]>"


@dataclass
class CastReport:
    results: List[CastResult] = field(default_factory=list)

    @property
    def success_count(self) -> int:
        return sum(1 for r in self.results if r.success)

    @property
    def failure_count(self) -> int:
        return sum(1 for r in self.results if not r.success)

    @property
    def has_failures(self) -> bool:
        return self.failure_count > 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "results": [
                {
                    "name": r.name,
                    "original": r.original,
                    "cast_type": r.cast_type,
                    "success": r.success,
                    "error": r.error,
                }
                for r in self.results
            ],
        }


class EnvCaster:
    """Cast environment variable string values to target types."""

    def cast(self, vars: Dict[str, str], cast_type: str) -> CastReport:
        if cast_type not in CAST_TYPES:
            raise ValueError(f"Unknown cast type '{cast_type}'. Choose from {CAST_TYPES}")
        results = [self._cast_one(name, value, cast_type) for name, value in vars.items()]
        return CastReport(results=results)

    def _cast_one(self, name: str, value: str, cast_type: str) -> CastResult:
        try:
            casted = self._apply(value, cast_type)
            return CastResult(name=name, original=value, casted=casted, cast_type=cast_type, success=True)
        except Exception as exc:
            return CastResult(name=name, original=value, casted=None, cast_type=cast_type, success=False, error=str(exc))

    def _apply(self, value: str, cast_type: str) -> Any:
        if cast_type == "str":
            return value
        if cast_type == "int":
            return int(value)
        if cast_type == "float":
            return float(value)
        if cast_type == "bool":
            if value.lower() in ("1", "true", "yes", "on"):
                return True
            if value.lower() in ("0", "false", "no", "off"):
                return False
            raise ValueError(f"Cannot cast '{value}' to bool")
        if cast_type == "json":
            import json
            return json.loads(value)
        raise ValueError(f"Unsupported type: {cast_type}")
