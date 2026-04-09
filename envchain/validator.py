"""Validation utilities for environment variable names and values."""

import re
from dataclasses import dataclass, field
from typing import List, Optional

# POSIX-compliant env var name pattern
_VAR_NAME_RE = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')

# Common sensitive key patterns to warn about
_SENSITIVE_PATTERNS = [
    re.compile(p, re.IGNORECASE)
    for p in [
        r'password', r'passwd', r'secret', r'token',
        r'api_key', r'private_key', r'auth',
    ]
]


@dataclass
class ValidationResult:
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def __bool__(self) -> bool:
        return self.valid


class EnvValidator:
    """Validates environment variable names and values."""

    def validate_name(self, name: str) -> ValidationResult:
        """Validate a single environment variable name."""
        errors: List[str] = []
        warnings: List[str] = []

        if not name:
            errors.append("Variable name must not be empty.")
            return ValidationResult(valid=False, errors=errors)

        if not _VAR_NAME_RE.match(name):
            errors.append(
                f"Invalid variable name '{name}': must start with a letter or "
                "underscore and contain only letters, digits, or underscores."
            )

        if name.startswith('_') and name.isupper() is False:
            warnings.append(
                f"Variable name '{name}' starts with an underscore; "
                "conventionally reserved for internal use."
            )

        return ValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)

    def validate_value(self, name: str, value: str) -> ValidationResult:
        """Validate a variable value, emitting warnings for empty or sensitive values."""
        warnings: List[str] = []

        if value == "":
            warnings.append(f"Value for '{name}' is empty.")

        if any(p.search(name) for p in _SENSITIVE_PATTERNS):
            warnings.append(
                f"'{name}' looks like a sensitive variable; ensure it is stored encrypted."
            )

        return ValidationResult(valid=True, warnings=warnings)

    def validate_pair(self, name: str, value: str) -> ValidationResult:
        """Validate both name and value, merging results."""
        name_result = self.validate_name(name)
        value_result = self.validate_value(name, value)
        return ValidationResult(
            valid=name_result.valid,
            errors=name_result.errors + value_result.errors,
            warnings=name_result.warnings + value_result.warnings,
        )
