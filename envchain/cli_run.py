"""CLI sub-command: envchain run <profile> -- <command...>"""

from __future__ import annotations

import sys
from typing import List, Optional

from envchain.env_runner import EnvRunner


class RunCommand:
    """Wraps :class:`EnvRunner` for use from the CLI."""

    def __init__(self, storage, password_callback) -> None:
        self._storage = storage
        self._get_password = password_callback

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def run(
        self,
        profile_name: str,
        command: List[str],
        override: bool = False,
    ) -> int:
        """Inject *profile_name* vars and exec *command*.

        Returns the child process exit code (or 1 on error).
        """
        if not command:
            print("error: no command specified", file=sys.stderr)
            return 1

        password = self._get_password(profile_name)
        runner = EnvRunner(self._storage, password)

        try:
            result = runner.run(
                profile_name,
                command,
                override_existing=override,
            )
        except KeyError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        except Exception as exc:  # pragma: no cover
            print(f"error: {exc}", file=sys.stderr)
            return 1

        if not result.success:
            # Propagate the child's exit code transparently.
            return result.returncode

        return 0

    def show_injected(
        self,
        profile_name: str,
        command: Optional[List[str]] = None,
    ) -> None:
        """Print which variables would be injected (dry-run helper)."""
        password = self._get_password(profile_name)
        runner = EnvRunner(self._storage, password)
        try:
            profile = self._storage.load_profile(profile_name, password)
        except Exception as exc:  # pragma: no cover
            print(f"error: {exc}", file=sys.stderr)
            return

        if profile is None:
            print(f"Profile {profile_name!r} not found.", file=sys.stderr)
            return

        if not profile.variables:
            print(f"Profile '{profile_name}' has no variables.")
            return

        print(f"Variables that would be injected from '{profile_name}':")
        for name in sorted(profile.variables):
            print(f"  {name}")
