"""Run a subprocess with environment variables from a profile injected."""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class RunResult:
    """Result of running a command with injected environment variables."""

    returncode: int
    command: List[str]
    profile_name: str
    injected_vars: List[str] = field(default_factory=list)

    @property
    def success(self) -> bool:
        return self.returncode == 0

    def __repr__(self) -> str:  # pragma: no cover
        status = "ok" if self.success else f"exit={self.returncode}"
        return f"<RunResult profile={self.profile_name!r} cmd={self.command[0]!r} {status}>"


class EnvRunner:
    """Inject decrypted profile variables into a subprocess environment."""

    def __init__(self, storage, password: str) -> None:
        self._storage = storage
        self._password = password

    def run(
        self,
        profile_name: str,
        command: List[str],
        extra_env: Optional[Dict[str, str]] = None,
        override_existing: bool = False,
    ) -> RunResult:
        """Run *command* with the named profile's variables in the environment.

        Args:
            profile_name: Profile whose variables to inject.
            command: Command and arguments to execute.
            extra_env: Additional variables to merge (applied last).
            override_existing: When True, profile vars replace existing shell
                               env vars with the same name.

        Returns:
            A :class:`RunResult` with the process return code.

        Raises:
            KeyError: If the profile does not exist.
            ValueError: If *command* is empty.
        """
        if not command:
            raise ValueError("command must not be empty")

        profile = self._storage.load_profile(profile_name, self._password)
        if profile is None:
            raise KeyError(f"Profile {profile_name!r} not found")

        env = os.environ.copy()
        injected: List[str] = []

        for name, value in profile.variables.items():
            if override_existing or name not in env:
                env[name] = value
                injected.append(name)

        if extra_env:
            env.update(extra_env)

        result = subprocess.run(command, env=env)  # noqa: S603
        return RunResult(
            returncode=result.returncode,
            command=command,
            profile_name=profile_name,
            injected_vars=injected,
        )
