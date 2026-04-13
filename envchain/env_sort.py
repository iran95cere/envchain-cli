"""Sorting utilities for environment variable sets."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"


class SortKey(str, Enum):
    NAME = "name"
    VALUE = "value"
    LENGTH = "length"  # sort by value length


@dataclass
class SortResult:
    original: Dict[str, str]
    sorted_vars: Dict[str, str]
    key: SortKey = SortKey.NAME
    order: SortOrder = SortOrder.ASC

    @property
    def is_changed(self) -> bool:
        return list(self.original.keys()) != list(self.sorted_vars.keys())

    @property
    def var_count(self) -> int:
        return len(self.sorted_vars)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"SortResult(vars={self.var_count}, key={self.key.value}, "
            f"order={self.order.value}, changed={self.is_changed})"
        )


class EnvSorter:
    """Sort environment variables by configurable key and order."""

    def sort(
        self,
        vars: Dict[str, str],
        key: SortKey = SortKey.NAME,
        order: SortOrder = SortOrder.ASC,
    ) -> SortResult:
        reverse = order == SortOrder.DESC

        if key == SortKey.NAME:
            keyfn = lambda item: item[0].lower()
        elif key == SortKey.VALUE:
            keyfn = lambda item: item[1].lower()
        elif key == SortKey.LENGTH:
            keyfn = lambda item: len(item[1])
        else:  # pragma: no cover
            keyfn = lambda item: item[0].lower()

        sorted_items = sorted(vars.items(), key=keyfn, reverse=reverse)
        sorted_vars = dict(sorted_items)

        return SortResult(
            original=dict(vars),
            sorted_vars=sorted_vars,
            key=key,
            order=order,
        )

    def sort_by_name(self, vars: Dict[str, str], descending: bool = False) -> SortResult:
        order = SortOrder.DESC if descending else SortOrder.ASC
        return self.sort(vars, key=SortKey.NAME, order=order)

    def sort_by_value_length(self, vars: Dict[str, str]) -> SortResult:
        return self.sort(vars, key=SortKey.LENGTH, order=SortOrder.ASC)
