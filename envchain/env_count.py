"""Count and summarize environment variables across profiles."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class CountResult:
    profile: str
    total: int
    empty: int
    non_empty: int

    def __repr__(self) -> str:
        return (
            f"CountResult(profile={self.profile!r}, total={self.total}, "
            f"empty={self.empty}, non_empty={self.non_empty})"
        )

    def to_dict(self) -> Dict:
        return {
            "profile": self.profile,
            "total": self.total,
            "empty": self.empty,
            "non_empty": self.non_empty,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "CountResult":
        return cls(
            profile=data["profile"],
            total=data["total"],
            empty=data["empty"],
            non_empty=data["non_empty"],
        )


@dataclass
class CountReport:
    results: List[CountResult] = field(default_factory=list)

    @property
    def total_profiles(self) -> int:
        return len(self.results)

    @property
    def grand_total(self) -> int:
        return sum(r.total for r in self.results)

    def __repr__(self) -> str:
        return (
            f"CountReport(profiles={self.total_profiles}, "
            f"grand_total={self.grand_total})"
        )


class EnvCounter:
    """Count variables in one or more profiles."""

    def count_profile(self, profile_name: str, variables: Dict[str, str]) -> CountResult:
        total = len(variables)
        empty = sum(1 for v in variables.values() if v.strip() == "")
        return CountResult(
            profile=profile_name,
            total=total,
            empty=empty,
            non_empty=total - empty,
        )

    def count_all(self, profiles: Dict[str, Dict[str, str]]) -> CountReport:
        report = CountReport()
        for name, variables in profiles.items():
            report.results.append(self.count_profile(name, variables))
        return report
