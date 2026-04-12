"""Profile inheritance: merge parent profile vars into a child profile."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class InheritanceResult:
    """Result of resolving an inheritance chain."""

    profile_name: str
    resolved_vars: Dict[str, str] = field(default_factory=dict)
    chain: List[str] = field(default_factory=list)  # ordered parent -> child
    overridden_keys: List[str] = field(default_factory=list)

    @property
    def var_count(self) -> int:
        return len(self.resolved_vars)

    @property
    def override_count(self) -> int:
        return len(self.overridden_keys)

    def __repr__(self) -> str:
        return (
            f"<InheritanceResult profile={self.profile_name!r} "
            f"vars={self.var_count} overrides={self.override_count} "
            f"chain={self.chain}>"
        )


class InheritanceError(Exception):
    """Raised when the inheritance chain is invalid (e.g. cycle detected)."""


class ProfileInheriter:
    """Resolves environment variables by walking a parent→child profile chain."""

    def __init__(self, storage) -> None:
        self._storage = storage

    def resolve(
        self,
        profile_name: str,
        parent_name: Optional[str],
        password: str,
        *,
        _visited: Optional[List[str]] = None,
    ) -> InheritanceResult:
        """Return merged vars with *child* values taking precedence over parent."""
        if _visited is None:
            _visited = []

        if profile_name in _visited:
            cycle = " -> ".join(_visited + [profile_name])
            raise InheritanceError(f"Circular inheritance detected: {cycle}")

        _visited.append(profile_name)

        base_vars: Dict[str, str] = {}
        chain: List[str] = []

        if parent_name:
            parent_result = self.resolve(
                parent_name, None, password, _visited=_visited
            )
            base_vars = dict(parent_result.resolved_vars)
            chain = list(parent_result.chain)

        chain.append(profile_name)

        child_profile = self._storage.load_profile(profile_name, password)
        child_vars: Dict[str, str] = child_profile.variables if child_profile else {}

        overridden = [k for k in child_vars if k in base_vars]
        merged = {**base_vars, **child_vars}

        return InheritanceResult(
            profile_name=profile_name,
            resolved_vars=merged,
            chain=chain,
            overridden_keys=overridden,
        )
