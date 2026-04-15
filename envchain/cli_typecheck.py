"""CLI command for type-checking profile variables."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

from envchain.env_typecheck import EnvTypeChecker, VarType
from envchain.storage import EnvStorage


class TypeCheckCommand:
    """Validates env vars in a profile against a JSON type schema."""

    def __init__(self, storage: EnvStorage) -> None:
        self._storage = storage
        self._checker = EnvTypeChecker()

    def run(
        self,
        profile_name: str,
        schema_path: str,
        password: str,
        strict: bool = False,
    ) -> None:
        schema_file = Path(schema_path)
        if not schema_file.exists():
            print(f"[error] Schema file not found: {schema_path}", file=sys.stderr)
            sys.exit(1)

        try:
            raw = json.loads(schema_file.read_text())
        except json.JSONDecodeError as exc:
            print(f"[error] Invalid JSON schema: {exc}", file=sys.stderr)
            sys.exit(1)

        try:
            schema = {k: VarType(v) for k, v in raw.items()}
        except ValueError as exc:
            print(f"[error] Unknown type in schema: {exc}", file=sys.stderr)
            sys.exit(1)

        profile = self._storage.load_profile(profile_name, password)
        if profile is None:
            print(f"[error] Profile '{profile_name}' not found.", file=sys.stderr)
            sys.exit(1)

        report = self._checker.check_all(profile.variables, schema)
        print(f"Profile : {profile_name}")
        print(f"Checked : {len(report.results)} variable(s)")
        print(f"Passed  : {report.passed_count}")
        print(f"Failed  : {report.failed_count}")

        if report.has_failures:
            print("\nFailures:")
            for r in report.failures():
                print(f"  {r.name}: {r.message} (got '{r.value}')")
            if strict:
                sys.exit(2)

    def list_types(self) -> None:
        print("Supported types:")
        for vt in VarType:
            print(f"  {vt.value}")
