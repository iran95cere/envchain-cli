"""Patch management: apply partial updates to a profile's variables."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class PatchOperation:
    """A single patch operation (set or delete)."""
    op: str          # 'set' | 'delete'
    key: str
    value: Optional[str] = None

    def __repr__(self) -> str:
        if self.op == 'set':
            return f"PatchOperation(set {self.key!r}={self.value!r})"
        return f"PatchOperation(delete {self.key!r})"


@dataclass
class PatchResult:
    applied: List[PatchOperation] = field(default_factory=list)
    skipped: List[Tuple[PatchOperation, str]] = field(default_factory=list)

    @property
    def applied_count(self) -> int:
        return len(self.applied)

    @property
    def skipped_count(self) -> int:
        return len(self.skipped)

    @property
    def has_skipped(self) -> bool:
        return bool(self.skipped)

    def __repr__(self) -> str:
        return (
            f"PatchResult(applied={self.applied_count}, "
            f"skipped={self.skipped_count})"
        )


class EnvPatcher:
    """Apply a list of PatchOperations to a vars dict."""

    def apply(
        self,
        vars_dict: Dict[str, str],
        operations: List[PatchOperation],
        *,
        allow_delete_missing: bool = False,
    ) -> PatchResult:
        result = PatchResult()
        working = dict(vars_dict)

        for op in operations:
            if op.op == 'set':
                if not op.key:
                    result.skipped.append((op, 'empty key'))
                    continue
                working[op.key] = op.value or ''
                result.applied.append(op)

            elif op.op == 'delete':
                if op.key not in working:
                    if allow_delete_missing:
                        result.applied.append(op)
                    else:
                        result.skipped.append((op, 'key not found'))
                    continue
                del working[op.key]
                result.applied.append(op)

            else:
                result.skipped.append((op, f'unknown op: {op.op!r}'))

        vars_dict.clear()
        vars_dict.update(working)
        return result
