"""CLI command for resolving variable cross-references in a profile."""

from __future__ import annotations

import sys
from typing import Optional

from envchain.env_resolve import EnvResolver
from envchain.storage import EnvStorage


class ResolveCommand:
    def __init__(self, storage: EnvStorage, password: str) -> None:
        self._storage = storage
        self._password = password
        self._resolver = EnvResolver()

    def run(self, profile_name: str, var_filter: Optional[str] = None) -> None:
        """Print resolved variables for *profile_name*."""
        profile = self._storage.load_profile(profile_name, self._password)
        if profile is None:
            print(f"Error: profile '{profile_name}' not found.", file=sys.stderr)
            sys.exit(1)

        vars_dict = dict(profile.variables)
        if var_filter:
            vars_dict = {
                k: v for k, v in vars_dict.items() if var_filter.lower() in k.lower()
            }

        result = self._resolver.resolve(vars_dict)

        if result.has_issues:
            for issue in result.issues:
                print(
                    f"  [warn] {issue.var_name}: {issue.reason}",
                    file=sys.stderr,
                )

        if not result.resolved:
            print("(no variables to display)")
            return

        max_len = max(len(k) for k in result.resolved)
        for name, value in sorted(result.resolved.items()):
            print(f"  {name:<{max_len}}  =  {value}")

    def show_references(self, profile_name: str) -> None:
        """List variables that contain references to other variables."""
        profile = self._storage.load_profile(profile_name, self._password)
        if profile is None:
            print(f"Error: profile '{profile_name}' not found.", file=sys.stderr)
            sys.exit(1)

        import re
        pattern = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")
        found = False
        for name, value in sorted(profile.variables.items()):
            refs = pattern.findall(value)
            if refs:
                found = True
                print(f"  {name}  ->  {', '.join(refs)}")

        if not found:
            print("No cross-references found in profile.")
