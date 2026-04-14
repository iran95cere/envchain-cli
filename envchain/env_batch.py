"""Batch operations on environment variables across multiple profiles."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class BatchOperation:
    """A single operation to apply: set or delete a variable."""
    action: str  # 'set' or 'delete'
    name: str
    value: Optional[str] = None

    def __repr__(self) -> str:
        if self.action == 'set':
            return f"BatchOperation(set {self.name}={self.value!r})"
        return f"BatchOperation(delete {self.name})"


@dataclass
class BatchResult:
    profile: str
    applied: List[BatchOperation] = field(default_factory=list)
    skipped: List[BatchOperation] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    @property
    def applied_count(self) -> int:
        return len(self.applied)

    @property
    def skipped_count(self) -> int:
        return len(self.skipped)

    @property
    def has_errors(self) -> bool:
        return bool(self.errors)

    def __repr__(self) -> str:
        return (
            f"BatchResult(profile={self.profile!r}, "
            f"applied={self.applied_count}, skipped={self.skipped_count}, "
            f"errors={len(self.errors)})"
        )


class EnvBatch:
    """Apply a list of BatchOperations to a profile's variable dict."""

    def run(
        self,
        profile_name: str,
        vars_: Dict[str, str],
        operations: List[BatchOperation],
        allow_overwrite: bool = True,
    ) -> BatchResult:
        result = BatchResult(profile=profile_name)
        working = dict(vars_)

        for op in operations:
            try:
                if op.action == 'set':
                    if not allow_overwrite and op.name in working:
                        result.skipped.append(op)
                    else:
                        working[op.name] = op.value or ''
                        result.applied.append(op)
                elif op.action == 'delete':
                    if op.name in working:
                        del working[op.name]
                        result.applied.append(op)
                    else:
                        result.skipped.append(op)
                else:
                    result.errors.append(f"Unknown action '{op.action}' for '{op.name}'")
            except Exception as exc:  # pragma: no cover
                result.errors.append(str(exc))

        return result
