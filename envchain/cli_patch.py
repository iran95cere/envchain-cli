"""CLI wrapper for the patch command."""
from __future__ import annotations

import sys
from typing import List

from envchain.env_patch import EnvPatcher, PatchOperation
from envchain.storage import EnvStorage


class PatchCommand:
    def __init__(self, storage: EnvStorage, password: str) -> None:
        self._storage = storage
        self._password = password
        self._patcher = EnvPatcher()

    def run(
        self,
        profile_name: str,
        set_pairs: List[str],
        delete_keys: List[str],
        allow_delete_missing: bool = False,
    ) -> None:
        profile = self._storage.load_profile(profile_name, self._password)
        if profile is None:
            print(f"Profile '{profile_name}' not found.", file=sys.stderr)
            sys.exit(1)

        ops: List[PatchOperation] = []
        for pair in set_pairs:
            if '=' not in pair:
                print(f"Invalid set expression (expected KEY=VALUE): {pair!r}",
                      file=sys.stderr)
                sys.exit(1)
            k, _, v = pair.partition('=')
            ops.append(PatchOperation(op='set', key=k.strip(), value=v))

        for key in delete_keys:
            ops.append(PatchOperation(op='delete', key=key.strip()))

        if not ops:
            print("No operations specified.")
            return

        result = self._patcher.apply(
            profile.variables,
            ops,
            allow_delete_missing=allow_delete_missing,
        )

        self._storage.save_profile(profile, self._password)

        print(f"Patch applied: {result.applied_count} operation(s).")
        if result.has_skipped:
            for op, reason in result.skipped:
                print(f"  Skipped {op!r}: {reason}")
