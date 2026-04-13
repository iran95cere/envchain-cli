"""Dependency tracking between environment variables across profiles."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set


@dataclass
class DependencyEdge:
    source_var: str
    target_var: str
    source_profile: str
    target_profile: str

    def to_dict(self) -> dict:
        return {
            "source_var": self.source_var,
            "target_var": self.target_var,
            "source_profile": self.source_profile,
            "target_profile": self.target_profile,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DependencyEdge":
        return cls(
            source_var=data["source_var"],
            target_var=data["target_var"],
            source_profile=data["source_profile"],
            target_profile=data["target_profile"],
        )

    def __repr__(self) -> str:
        return (
            f"DependencyEdge({self.source_profile}/{self.source_var} "
            f"-> {self.target_profile}/{self.target_var})"
        )


@dataclass
class DependencyReport:
    edges: List[DependencyEdge] = field(default_factory=list)
    missing: List[DependencyEdge] = field(default_factory=list)

    @property
    def edge_count(self) -> int:
        return len(self.edges)

    @property
    def has_missing(self) -> bool:
        return bool(self.missing)

    def __repr__(self) -> str:
        return f"DependencyReport(edges={self.edge_count}, missing={len(self.missing)})"


class DependencyAnalyser:
    """Analyse inter-profile variable dependencies declared as ${profile:VAR}."""

    REFERENCE_PREFIX = "${"
    REFERENCE_SUFFIX = "}"

    def analyse(
        self,
        profiles: Dict[str, Dict[str, str]],
        source_profile: str,
    ) -> DependencyReport:
        """Find all cross-profile references in *source_profile* vars."""
        edges: List[DependencyEdge] = []
        missing: List[DependencyEdge] = []

        source_vars = profiles.get(source_profile, {})
        for var_name, value in source_vars.items():
            for ref in self._extract_refs(value):
                target_profile, target_var = ref
                edge = DependencyEdge(
                    source_var=var_name,
                    target_var=target_var,
                    source_profile=source_profile,
                    target_profile=target_profile,
                )
                edges.append(edge)
                target_vars = profiles.get(target_profile, {})
                if target_var not in target_vars:
                    missing.append(edge)

        return DependencyReport(edges=edges, missing=missing)

    def _extract_refs(self, value: str) -> List[tuple]:
        refs = []
        start = 0
        while True:
            idx = value.find(self.REFERENCE_PREFIX, start)
            if idx == -1:
                break
            end = value.find(self.REFERENCE_SUFFIX, idx)
            if end == -1:
                break
            inner = value[idx + 2: end]
            if ":" in inner:
                profile, var = inner.split(":", 1)
                refs.append((profile.strip(), var.strip()))
            start = end + 1
        return refs
