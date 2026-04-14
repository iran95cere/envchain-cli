"""CLI command for batch-applying variable operations to a profile."""
from __future__ import annotations

import json
import sys
from typing import List

from envchain.env_batch import BatchOperation, EnvBatch


class BatchCommand:
    def __init__(self, storage):
        self._storage = storage
        self._batch = EnvBatch()

    def run(
        self,
        profile: str,
        operations_json: str,
        allow_overwrite: bool = True,
    ) -> None:
        """Apply batch operations from a JSON string to *profile*.

        JSON format: [{"action": "set", "name": "X", "value": "v"}, ...]
        """
        try:
            raw = json.loads(operations_json)
        except json.JSONDecodeError as exc:
            print(f"[batch] Invalid JSON: {exc}", file=sys.stderr)
            sys.exit(1)

        ops: List[BatchOperation] = []
        for item in raw:
            try:
                ops.append(BatchOperation(
                    action=item['action'],
                    name=item['name'],
                    value=item.get('value'),
                ))
            except KeyError as exc:
                print(f"[batch] Missing key in operation: {exc}", file=sys.stderr)
                sys.exit(1)

        prof = self._storage.load_profile(profile)
        if prof is None:
            print(f"[batch] Profile '{profile}' not found.", file=sys.stderr)
            sys.exit(1)

        result = self._batch.run(
            profile, dict(prof.variables), ops, allow_overwrite=allow_overwrite
        )

        if result.has_errors:
            for err in result.errors:
                print(f"[batch] Error: {err}", file=sys.stderr)
            sys.exit(1)

        for name, val in self._batch.run(
            profile, dict(prof.variables), ops, allow_overwrite=allow_overwrite
        ).applied:
            pass  # result already computed above

        # Persist changes
        new_vars = dict(prof.variables)
        for op in result.applied:
            if op.action == 'set':
                new_vars[op.name] = op.value or ''
            elif op.action == 'delete':
                new_vars.pop(op.name, None)
        prof.variables = new_vars
        self._storage.save_profile(prof)

        print(
            f"[batch] Profile '{profile}': "
            f"{result.applied_count} applied, {result.skipped_count} skipped."
        )
