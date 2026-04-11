"""Filter environment variables by pattern, prefix, or tag."""

from __future__ import annotations

import fnmatch
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class FilterResult:
    matched: Dict[str, str] = field(default_factory=dict)
    excluded: Dict[str, str] = field(default_factory=dict)

    @property
    def match_count(self) -> int:
        return len(self.matched)

    def __repr__(self) -> str:  # pragma: no cover
        return f"FilterResult(matched={self.match_count}, excluded={len(self.excluded)})"


class EnvFilter:
    """Filter a dict of env vars using prefix, glob, or regex rules."""

    def filter_by_prefix(
        self, vars: Dict[str, str], prefix: str, case_sensitive: bool = True
    ) -> FilterResult:
        if not prefix:
            return FilterResult(matched=dict(vars))
        result = FilterResult()
        cmp_prefix = prefix if case_sensitive else prefix.upper()
        for k, v in vars.items():
            cmp_key = k if case_sensitive else k.upper()
            if cmp_key.startswith(cmp_prefix):
                result.matched[k] = v
            else:
                result.excluded[k] = v
        return result

    def filter_by_glob(
        self, vars: Dict[str, str], pattern: str, case_sensitive: bool = True
    ) -> FilterResult:
        if not pattern:
            return FilterResult(matched=dict(vars))
        result = FilterResult()
        flags = 0 if case_sensitive else re.IGNORECASE
        for k, v in vars.items():
            if fnmatch.fnmatchcase(k if case_sensitive else k.upper(),
                                   pattern if case_sensitive else pattern.upper()):
                result.matched[k] = v
            else:
                result.excluded[k] = v
        return result

    def filter_by_regex(
        self, vars: Dict[str, str], pattern: str, case_sensitive: bool = True
    ) -> FilterResult:
        flags = 0 if case_sensitive else re.IGNORECASE
        try:
            compiled = re.compile(pattern, flags)
        except re.error as exc:
            raise ValueError(f"Invalid regex pattern '{pattern}': {exc}") from exc
        result = FilterResult()
        for k, v in vars.items():
            if compiled.search(k):
                result.matched[k] = v
            else:
                result.excluded[k] = v
        return result

    def filter_keys(
        self, vars: Dict[str, str], keys: List[str]
    ) -> FilterResult:
        key_set = set(keys)
        result = FilterResult()
        for k, v in vars.items():
            if k in key_set:
                result.matched[k] = v
            else:
                result.excluded[k] = v
        return result
