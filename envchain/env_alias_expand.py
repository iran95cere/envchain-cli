"""Expand variable aliases — substitute one var name with another across a profile."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class AliasExpandResult:
    """Result of a single alias expansion."""
    original_name: str
    alias_name: str
    value: Optional[str]
    expanded: bool

    def __repr__(self) -> str:
        status = "expanded" if self.expanded else "skipped"
        return f"<AliasExpandResult {self.original_name}->{self.alias_name} [{status}]>"


@dataclass
class AliasExpandReport:
    """Aggregated report for an alias expansion pass."""
    results: List[AliasExpandResult] = field(default_factory=list)

    @property
    def expanded_count(self) -> int:
        return sum(1 for r in self.results if r.expanded)

    @property
    def skipped_count(self) -> int:
        return sum(1 for r in self.results if not r.expanded)

    @property
    def has_expansions(self) -> bool:
        return self.expanded_count > 0

    def __repr__(self) -> str:
        return (
            f"<AliasExpandReport expanded={self.expanded_count} "
            f"skipped={self.skipped_count}>"
        )


class EnvAliasExpander:
    """Expand variable aliases within a profile's variable dict."""

    def expand(
        self,
        variables: Dict[str, str],
        alias_map: Dict[str, str],
        overwrite: bool = False,
    ) -> AliasExpandReport:
        """Apply *alias_map* (alias_name -> original_name) to *variables*.

        For each entry in *alias_map*, if *original_name* exists in *variables*
        and (*alias_name* is absent OR *overwrite* is True), copy the value
        under *alias_name*.
        """
        report = AliasExpandReport()
        for alias_name, original_name in alias_map.items():
            value = variables.get(original_name)
            if value is None:
                report.results.append(
                    AliasExpandResult(
                        original_name=original_name,
                        alias_name=alias_name,
                        value=None,
                        expanded=False,
                    )
                )
                continue
            if alias_name in variables and not overwrite:
                report.results.append(
                    AliasExpandResult(
                        original_name=original_name,
                        alias_name=alias_name,
                        value=value,
                        expanded=False,
                    )
                )
                continue
            variables[alias_name] = value
            report.results.append(
                AliasExpandResult(
                    original_name=original_name,
                    alias_name=alias_name,
                    value=value,
                    expanded=True,
                )
            )
        return report
