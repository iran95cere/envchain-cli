"""Profile diff utility for comparing environment variable sets."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class DiffResult:
    """Result of comparing two profiles."""
    added: Dict[str, str] = field(default_factory=dict)
    removed: Dict[str, str] = field(default_factory=dict)
    modified: Dict[str, Tuple[str, str]] = field(default_factory=dict)
    unchanged: Dict[str, str] = field(default_factory=dict)

    @property
    def has_changes(self) -> bool:
        return bool(self.added or self.removed or self.modified)

    def summary(self) -> str:
        parts = []
        if self.added:
            parts.append(f"+{len(self.added)} added")
        if self.removed:
            parts.append(f"-{len(self.removed)} removed")
        if self.modified:
            parts.append(f"~{len(self.modified)} modified")
        if not parts:
            return "No changes"
        return ", ".join(parts)

    def to_lines(self, show_values: bool = False) -> List[str]:
        lines = []
        for key, val in sorted(self.added.items()):
            display = f"={val}" if show_values else ""
            lines.append(f"+ {key}{display}")
        for key, val in sorted(self.removed.items()):
            display = f"={val}" if show_values else ""
            lines.append(f"- {key}{display}")
        for key, (old, new) in sorted(self.modified.items()):
            if show_values:
                lines.append(f"~ {key}: {old} -> {new}")
            else:
                lines.append(f"~ {key}")
        for key in sorted(self.unchanged.keys()):
            lines.append(f"  {key}")
        return lines


class ProfileDiffer:
    """Compares two sets of environment variables."""

    def diff(
        self,
        base: Dict[str, str],
        target: Dict[str, str],
    ) -> DiffResult:
        """Return a DiffResult comparing base to target."""
        result = DiffResult()
        all_keys = set(base) | set(target)
        for key in all_keys:
            in_base = key in base
            in_target = key in target
            if in_base and in_target:
                if base[key] == target[key]:
                    result.unchanged[key] = base[key]
                else:
                    result.modified[key] = (base[key], target[key])
            elif in_target:
                result.added[key] = target[key]
            else:
                result.removed[key] = base[key]
        return result
