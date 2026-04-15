"""CLI command for obfuscating / deobfuscating profile variable values."""
from __future__ import annotations

import sys
from typing import Optional

from envchain.env_obfuscate import EnvObfuscator
from envchain.storage import EnvStorage


class ObfuscateCommand:
    def __init__(self, storage: EnvStorage) -> None:
        self._storage = storage
        self._obfuscator = EnvObfuscator()

    def run(self, profile_name: str, password: str, *, dry_run: bool = False) -> None:
        """Obfuscate all plain-text values in *profile_name*."""
        profile = self._storage.load_profile(profile_name, password)
        if profile is None:
            print(f"Profile '{profile_name}' not found.", file=sys.stderr)
            sys.exit(1)

        report = self._obfuscator.obfuscate(profile.variables)
        if not report.has_changes:
            print("All values already obfuscated — nothing to do.")
            return

        if dry_run:
            print(f"[dry-run] Would obfuscate {report.obfuscated_count} variable(s).")
            return

        profile.variables = self._obfuscator.to_flat_dict(report)
        self._storage.save_profile(profile, password)
        print(f"Obfuscated {report.obfuscated_count} variable(s) in '{profile_name}'.")

    def deobfuscate(self, profile_name: str, password: str, *, dry_run: bool = False) -> None:
        """Decode obfuscated values back to plain text."""
        profile = self._storage.load_profile(profile_name, password)
        if profile is None:
            print(f"Profile '{profile_name}' not found.", file=sys.stderr)
            sys.exit(1)

        report = self._obfuscator.deobfuscate(profile.variables)
        if not report.has_changes:
            print("No obfuscated values found — nothing to do.")
            return

        if dry_run:
            print(f"[dry-run] Would deobfuscate {report.obfuscated_count} variable(s).")
            return

        profile.variables = self._obfuscator.to_flat_dict(report)
        self._storage.save_profile(profile, password)
        print(f"Deobfuscated {report.obfuscated_count} variable(s) in '{profile_name}'.")
