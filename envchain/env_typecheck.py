"""Type-checking and validation for environment variable values."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional
import re


class VarType(str, Enum):
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    URL = "url"
    EMAIL = "email"
    PATH = "path"


_PATTERNS: Dict[VarType, re.Pattern] = {
    VarType.INTEGER: re.compile(r"^-?\d+$"),
    VarType.FLOAT: re.compile(r"^-?\d+(\.\d+)?([eE][+-]?\d+)?$"),
    VarType.BOOLEAN: re.compile(r"^(true|false|1|0|yes|no)$", re.IGNORECASE),
    VarType.URL: re.compile(r"^https?://[^\s]+$", re.IGNORECASE),
    VarType.EMAIL: re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$"),
    VarType.PATH: re.compile(r"^(/[^\0]*|[a-zA-Z]:\\[^\0]*)$"),
}


@dataclass
class TypeCheckResult:
    name: str
    value: str
    expected_type: VarType
    passed: bool
    message: str = ""

    def __repr__(self) -> str:
        status = "OK" if self.passed else "FAIL"
        return f"<TypeCheckResult {self.name} {self.expected_type.value} {status}>"


@dataclass
class TypeCheckReport:
    results: List[TypeCheckResult] = field(default_factory=list)

    @property
    def failed_count(self) -> int:
        return sum(1 for r in self.results if not r.passed)

    @property
    def passed_count(self) -> int:
        return sum(1 for r in self.results if r.passed)

    @property
    def has_failures(self) -> bool:
        return self.failed_count > 0

    def failures(self) -> List[TypeCheckResult]:
        return [r for r in self.results if not r.passed]

    def __repr__(self) -> str:
        return (
            f"<TypeCheckReport total={len(self.results)} "
            f"passed={self.passed_count} failed={self.failed_count}>"
        )


class EnvTypeChecker:
    """Validates env var values against declared types."""

    def check(self, name: str, value: str, var_type: VarType) -> TypeCheckResult:
        if var_type == VarType.STRING:
            return TypeCheckResult(name, value, var_type, True)
        pattern = _PATTERNS.get(var_type)
        if pattern is None:
            return TypeCheckResult(name, value, var_type, True)
        passed = bool(pattern.match(value))
        msg = "" if passed else f"Value does not match type '{var_type.value}'"
        return TypeCheckResult(name, value, var_type, passed, msg)

    def check_all(
        self,
        vars_: Dict[str, str],
        schema: Dict[str, VarType],
    ) -> TypeCheckReport:
        results: List[TypeCheckResult] = []
        for name, var_type in schema.items():
            value = vars_.get(name, "")
            results.append(self.check(name, value, var_type))
        return TypeCheckReport(results=results)
