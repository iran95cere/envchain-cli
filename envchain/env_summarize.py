"""Summarize environment variable profiles into a concise report."""
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class SummaryEntry:
    profile: str
    total_vars: int
    empty_vars: int
    longest_key: str
    longest_value_len: int

    def __repr__(self) -> str:
        return (
            f"<SummaryEntry profile={self.profile!r} total={self.total_vars} "
            f"empty={self.empty_vars}>"
        )

    def to_dict(self) -> Dict:
        return {
            "profile": self.profile,
            "total_vars": self.total_vars,
            "empty_vars": self.empty_vars,
            "longest_key": self.longest_key,
            "longest_value_len": self.longest_value_len,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "SummaryEntry":
        return cls(
            profile=data["profile"],
            total_vars=data["total_vars"],
            empty_vars=data.get("empty_vars", 0),
            longest_key=data.get("longest_key", ""),
            longest_value_len=data.get("longest_value_len", 0),
        )


@dataclass
class SummaryReport:
    entries: List[SummaryEntry] = field(default_factory=list)

    @property
    def profile_count(self) -> int:
        return len(self.entries)

    @property
    def total_vars(self) -> int:
        return sum(e.total_vars for e in self.entries)

    def __repr__(self) -> str:
        return f"<SummaryReport profiles={self.profile_count} total_vars={self.total_vars}>"


class EnvSummarizer:
    def summarize(self, profile_name: str, variables: Dict[str, str]) -> SummaryEntry:
        total = len(variables)
        empty = sum(1 for v in variables.values() if not v.strip())
        longest_key = max(variables.keys(), key=len) if variables else ""
        longest_value_len = max((len(v) for v in variables.values()), default=0)
        return SummaryEntry(
            profile=profile_name,
            total_vars=total,
            empty_vars=empty,
            longest_key=longest_key,
            longest_value_len=longest_value_len,
        )

    def summarize_all(
        self, profiles: Dict[str, Dict[str, str]]
    ) -> SummaryReport:
        entries = [
            self.summarize(name, variables)
            for name, variables in profiles.items()
        ]
        return SummaryReport(entries=entries)
