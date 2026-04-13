"""CLI command for re-encrypting profiles."""
from __future__ import annotations

import getpass
import sys
from typing import List, Optional

from envchain.env_encrypt_profile import ProfileReEncryptor


class ReEncryptCommand:
    """CLI wrapper around ProfileReEncryptor."""

    def __init__(self, storage) -> None:
        self._storage = storage
        self._encryptor = ProfileReEncryptor(storage)

    def run(self, profile_names: Optional[List[str]] = None) -> None:
        available = self._storage.list_profiles()
        if not available:
            print("No profiles found.", file=sys.stderr)
            sys.exit(1)

        targets = profile_names if profile_names else available
        unknown = [n for n in targets if n not in available]
        if unknown:
            print(f"Unknown profiles: {', '.join(unknown)}", file=sys.stderr)
            sys.exit(1)

        old_password = getpass.getpass("Current password: ")
        new_password = getpass.getpass("New password: ")
        confirm = getpass.getpass("Confirm new password: ")

        if new_password != confirm:
            print("Passwords do not match.", file=sys.stderr)
            sys.exit(1)

        report = self._encryptor.re_encrypt_all(targets, old_password, new_password)

        for result in report.results:
            if result.success:
                print(f"  [ok] {result.profile_name} ({result.vars_processed} vars)")
            else:
                print(f"  [fail] {result.profile_name}: {result.error}", file=sys.stderr)

        if report.has_failures:
            print(f"\n{report.failure_count} profile(s) failed.", file=sys.stderr)
            sys.exit(1)
        else:
            print(f"\nRe-encrypted {report.success_count} profile(s) successfully.")
