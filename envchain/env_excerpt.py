"""Extract a subset of variables from a profile by key list or pattern."""
from __future__ import annotations

import fnmatch
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ExcerptResult:
    """Holds the extracted subset of environment variables."""
    name: str
    original: Dict[str, str]
    extracted: Dict[str, str]
    keys_requested: List[str] = field(default_factory=list)

    @property
    def extract_count(self) -> int:
        return len(self.extracted)

    @property
    def missing_keys(self) -> List[str]:
        """Keys that were requested but not found in the original."""
        resolved = set()
        for key in self.keys_requested:
            if '*' in key or '?' in key:
                resolved.update(fnmatch.filter(self.original.keys(), key))
            elif key in self.original:
                resolved.add(key)
        return [k for k in self.keys_requested
                if '*' not in k and '?' not in k and k not in self.original]

    def __repr__(self) -> str:
        return (
            f"ExcerptResult(profile={self.name!r}, "
            f"extracted={self.extract_count}, "
            f"total={len(self.original)})"
        )


class EnvExcerpt:
    """Extracts a subset of variables from a profile's variable dict."""

    def excerpt(
        self,
        profile_name: str,
        variables: Dict[str, str],
        keys: List[str],
        *,
        ignore_missing: bool = True,
    ) -> ExcerptResult:
        """Return an ExcerptResult containing only the requested keys.

        Keys may include glob patterns (e.g. ``DB_*``).
        Raises ``KeyError`` for missing literal keys when *ignore_missing* is False.
        """
        extracted: Dict[str, str] = {}
        for key in keys:
            if '*' in key or '?' in key:
                for match in fnmatch.filter(variables.keys(), key):
                    extracted[match] = variables[match]
            else:
                if key in variables:
                    extracted[key] = variables[key]
                elif not ignore_missing:
                    raise KeyError(f"Variable {key!r} not found in profile {profile_name!r}")

        return ExcerptResult(
            name=profile_name,
            original=dict(variables),
            extracted=extracted,
            keys_requested=list(keys),
        )
