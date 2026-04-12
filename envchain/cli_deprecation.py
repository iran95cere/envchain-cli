"""CLI commands for managing deprecated variable names."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

from envchain.env_deprecation import DeprecationChecker, DeprecationEntry

_REGISTRY_FILE = ".envchain_deprecations.json"


class DeprecationCommand:
    def __init__(self, storage_dir: str = ".") -> None:
        self._path = Path(storage_dir) / _REGISTRY_FILE
        self._checker = DeprecationChecker()
        self._load()

    def _load(self) -> None:
        if self._path.exists():
            data = json.loads(self._path.read_text())
            for item in data.get("entries", []):
                entry = DeprecationEntry.from_dict(item)
                self._checker._registry[entry.var_name] = entry

    def _save(self) -> None:
        data = {"entries": [e.to_dict() for e in self._checker.all_deprecated()]}
        self._path.write_text(json.dumps(data, indent=2))

    def add(self, var_name: str, reason: str, replacement: Optional[str] = None) -> None:
        try:
            self._checker.register(var_name, reason, replacement)
            self._save()
            repl_msg = f" (replacement: {replacement})" if replacement else ""
            print(f"Registered '{var_name}' as deprecated.{repl_msg}")
        except ValueError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)

    def remove(self, var_name: str) -> None:
        if self._checker.unregister(var_name):
            self._save()
            print(f"Removed deprecation entry for '{var_name}'.")
        else:
            print(f"No deprecation entry found for '{var_name}'.", file=sys.stderr)
            sys.exit(1)

    def list_deprecated(self) -> None:
        entries = self._checker.all_deprecated()
        if not entries:
            print("No deprecated variables registered.")
            return
        for entry in entries:
            repl = f" -> {entry.replacement}" if entry.replacement else ""
            print(f"  {entry.var_name}{repl}  # {entry.reason}")

    def scan(self, variables: dict) -> None:
        report = self._checker.check(variables)
        if not report.has_deprecated:
            print("No deprecated variables found.")
            return
        print(f"Found {report.deprecated_count} deprecated variable(s):")
        for entry in report.entries:
            repl = f"  Use '{entry.replacement}' instead." if entry.replacement else ""
            print(f"  WARNING: {entry.var_name} — {entry.reason}.{repl}")
