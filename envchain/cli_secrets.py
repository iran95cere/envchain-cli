"""CLI command for scanning and masking secrets in profiles."""

from __future__ import annotations

import sys
from typing import Optional

from envchain.env_secrets import SecretScanner
from envchain.storage import EnvStorage


class SecretsCommand:
    """Scan a profile for likely secrets and optionally display masked output."""

    def __init__(self, storage: EnvStorage) -> None:
        self._storage = storage
        self._scanner = SecretScanner()

    def scan(self, profile: str, password: str) -> None:
        """Print a report of flagged secret variables in *profile*."""
        data = self._storage.load_profile(profile, password)
        if data is None:
            print(f"Error: profile '{profile}' not found.", file=sys.stderr)
            sys.exit(1)

        variables: dict = data.get("vars", {})
        result = self._scanner.scan(profile, variables)

        if not result.has_secrets():
            print(f"No secrets detected in profile '{profile}'.")
            return

        print(f"Detected {result.count} likely secret(s) in profile '{profile}':")
        for name, reason in result.flagged.items():
            print(f"  {name}: {reason}")

    def show_masked(self, profile: str, password: str) -> None:
        """Print all variables, masking those identified as secrets."""
        data = self._storage.load_profile(profile, password)
        if data is None:
            print(f"Error: profile '{profile}' not found.", file=sys.stderr)
            sys.exit(1)

        variables: dict = data.get("vars", {})
        masked = self._scanner.masked_vars(variables)

        if not masked:
            print(f"Profile '{profile}' has no variables.")
            return

        print(f"Variables for profile '{profile}' (secrets masked):")
        for name, value in sorted(masked.items()):
            print(f"  {name}={value}")
