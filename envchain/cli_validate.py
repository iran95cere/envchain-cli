"""CLI command for validating environment variable names/values in a profile."""

from typing import Optional

from .storage import EnvStorage
from .validator import EnvValidator


class ValidateCommand:
    """Validates all variables stored in a given profile."""

    def __init__(self, storage: EnvStorage) -> None:
        self.storage = storage
        self.validator = EnvValidator()

    def run(self, profile_name: str, password: str) -> int:
        """
        Load *profile_name*, validate every variable, print issues.

        Returns 0 if no errors, 1 if any validation errors were found.
        """
        profile = self.storage.load_profile(profile_name, password)
        if profile is None:
            print(f"[error] Profile '{profile_name}' not found.")
            return 1

        has_errors = False
        total_warnings = 0

        for name, value in profile.vars.items():
            result = self.validator.validate_pair(name, value)
            for err in result.errors:
                print(f"[error] {err}")
                has_errors = True
            for warn in result.warnings:
                print(f"[warn]  {warn}")
                total_warnings += 1

        if not has_errors and total_warnings == 0:
            print(f"Profile '{profile_name}': all {len(profile.vars)} variable(s) are valid.")
        elif not has_errors:
            print(
                f"Profile '{profile_name}': valid with {total_warnings} warning(s)."
            )

        return 1 if has_errors else 0

    def validate_name_only(self, name: str) -> None:
        """Quick one-shot name validation, prints result to stdout."""
        result = self.validator.validate_name(name)
        if result.valid:
            print(f"'{name}' is a valid environment variable name.")
        else:
            for err in result.errors:
                print(f"[error] {err}")
        for warn in result.warnings:
            print(f"[warn]  {warn}")
