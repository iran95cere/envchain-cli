"""Cascade resolution: merge variables from multiple profiles in priority order."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class CascadeSource:
    """Records which profile a variable came from."""
    profile: str
    value: str
    priority: int

    def __repr__(self) -> str:
        return f"<CascadeSource profile={self.profile!r} priority={self.priority}>"


@dataclass
class CascadeResult:
    """Result of a cascade resolution."""
    resolved: Dict[str, CascadeSource] = field(default_factory=dict)
    profiles_used: List[str] = field(default_factory=list)

    @property
    def var_count(self) -> int:
        return len(self.resolved)

    def to_flat_dict(self) -> Dict[str, str]:
        """Return plain name->value mapping."""
        return {k: v.value for k, v in self.resolved.items()}

    def source_for(self, name: str) -> Optional[CascadeSource]:
        return self.resolved.get(name)

    def __repr__(self) -> str:
        return (
            f"<CascadeResult vars={self.var_count} "
            f"profiles={self.profiles_used}>"
        )


class EnvCascade:
    """Merges environment variables from an ordered list of profiles.

    Profiles are supplied highest-priority first.  A variable set in an
    earlier profile shadows the same variable in later profiles.
    """

    def resolve(
        self,
        profiles: List[Tuple[str, Dict[str, str]]],
    ) -> CascadeResult:
        """Resolve variables from *profiles*.

        Args:
            profiles: Sequence of (profile_name, vars_dict) pairs ordered
                      from highest to lowest priority.

        Returns:
            A :class:`CascadeResult` with the merged variables.
        """
        result = CascadeResult()
        seen_profiles: List[str] = []

        for priority, (profile_name, vars_dict) in enumerate(profiles):
            seen_profiles.append(profile_name)
            for name, value in vars_dict.items():
                if name not in result.resolved:
                    result.resolved[name] = CascadeSource(
                        profile=profile_name,
                        value=value,
                        priority=priority,
                    )

        result.profiles_used = seen_profiles
        return result
