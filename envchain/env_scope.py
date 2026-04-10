"""Scope management: restrict which variables are visible per context."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ScopeRule:
    """A single rule mapping a context pattern to allowed variable names."""

    context: str  # e.g. 'ci', 'production', 'local'
    allowed: List[str] = field(default_factory=list)
    denied: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "context": self.context,
            "allowed": list(self.allowed),
            "denied": list(self.denied),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ScopeRule":
        return cls(
            context=data["context"],
            allowed=list(data.get("allowed", [])),
            denied=list(data.get("denied", [])),
        )

    def __repr__(self) -> str:
        return (
            f"ScopeRule(context={self.context!r}, "
            f"allowed={self.allowed}, denied={self.denied})"
        )


class EnvScope:
    """Filters a variable dict according to scope rules for a given context."""

    def __init__(self, rules: Optional[List[ScopeRule]] = None) -> None:
        self._rules: List[ScopeRule] = rules or []

    def add_rule(self, rule: ScopeRule) -> None:
        # Replace existing rule for the same context.
        self._rules = [r for r in self._rules if r.context != rule.context]
        self._rules.append(rule)

    def remove_rule(self, context: str) -> bool:
        before = len(self._rules)
        self._rules = [r for r in self._rules if r.context != context]
        return len(self._rules) < before

    def get_rule(self, context: str) -> Optional[ScopeRule]:
        for rule in self._rules:
            if rule.context == context:
                return rule
        return None

    def apply(self, variables: Dict[str, str], context: str) -> Dict[str, str]:
        """Return a filtered copy of *variables* according to the rule for *context*.

        - If no rule exists for *context*, all variables are returned unchanged.
        - *allowed* list (non-empty) acts as an explicit whitelist.
        - *denied* list always removes matching keys (applied after whitelist).
        """
        rule = self.get_rule(context)
        if rule is None:
            return dict(variables)

        if rule.allowed:
            result = {k: v for k, v in variables.items() if k in rule.allowed}
        else:
            result = dict(variables)

        for key in rule.denied:
            result.pop(key, None)

        return result

    def list_contexts(self) -> List[str]:
        return [r.context for r in self._rules]
