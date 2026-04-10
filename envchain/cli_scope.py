"""CLI commands for managing variable scopes."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import List, Optional

from envchain.env_scope import EnvScope, ScopeRule

_SCOPE_FILE = ".envchain_scopes.json"


class ScopeCommand:
    """Handles scope sub-commands: add, remove, show, apply."""

    def __init__(self, base_dir: str = ".") -> None:
        self._path = Path(base_dir) / _SCOPE_FILE
        self._scope = self._load()

    # ------------------------------------------------------------------
    # Persistence helpers
    # ------------------------------------------------------------------

    def _load(self) -> EnvScope:
        if self._path.exists():
            data = json.loads(self._path.read_text())
            rules = [ScopeRule.from_dict(r) for r in data.get("rules", [])]
            return EnvScope(rules)
        return EnvScope()

    def _save(self) -> None:
        data = {"rules": [r.to_dict() for r in [
            self._scope.get_rule(c) for c in self._scope.list_contexts()
        ]]}
        self._path.write_text(json.dumps(data, indent=2))

    # ------------------------------------------------------------------
    # Public commands
    # ------------------------------------------------------------------

    def add(self, context: str, allowed: List[str], denied: List[str]) -> None:
        rule = ScopeRule(context=context, allowed=allowed, denied=denied)
        self._scope.add_rule(rule)
        self._save()
        print(f"Scope rule added for context '{context}'.")

    def remove(self, context: str) -> None:
        if self._scope.remove_rule(context):
            self._save()
            print(f"Scope rule for '{context}' removed.")
        else:
            print(f"No scope rule found for '{context}'.", file=sys.stderr)
            sys.exit(1)

    def show(self, context: Optional[str] = None) -> None:
        if context:
            rule = self._scope.get_rule(context)
            if rule is None:
                print(f"No rule for context '{context}'.", file=sys.stderr)
                sys.exit(1)
            print(repr(rule))
        else:
            contexts = self._scope.list_contexts()
            if not contexts:
                print("No scope rules defined.")
            for ctx in contexts:
                print(repr(self._scope.get_rule(ctx)))

    def apply(self, context: str, variables: dict) -> dict:
        """Return filtered variables for *context* (used programmatically)."""
        return self._scope.apply(variables, context)
