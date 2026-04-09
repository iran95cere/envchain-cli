"""Pre/post hooks for profile load and save events."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Dict, List, Optional


class HookEvent(str, Enum):
    PRE_LOAD = "pre_load"
    POST_LOAD = "post_load"
    PRE_SAVE = "pre_save"
    POST_SAVE = "post_save"


@dataclass
class HookResult:
    event: HookEvent
    profile_name: str
    success: bool
    output: str = ""
    error: str = ""

    def __repr__(self) -> str:
        status = "ok" if self.success else "failed"
        return f"<HookResult event={self.event.value} profile={self.profile_name!r} {status}>"


class HookRunner:
    """Manages and executes shell or callable hooks for profile lifecycle events."""

    def __init__(self) -> None:
        self._shell_hooks: Dict[HookEvent, List[str]] = {e: [] for e in HookEvent}
        self._callable_hooks: Dict[HookEvent, List[Callable[[str], None]]] = {
            e: [] for e in HookEvent
        }

    def register_shell(self, event: HookEvent, command: str) -> None:
        """Register a shell command to run on *event*."""
        if not command or not command.strip():
            raise ValueError("Hook command must not be empty.")
        self._shell_hooks[event].append(command)

    def register_callable(self, event: HookEvent, fn: Callable[[str], None]) -> None:
        """Register a Python callable to invoke on *event*."""
        if not callable(fn):
            raise TypeError("Hook must be callable.")
        self._callable_hooks[event].append(fn)

    def run(self, event: HookEvent, profile_name: str) -> List[HookResult]:
        """Execute all hooks registered for *event* and return results."""
        results: List[HookResult] = []

        for cmd in self._shell_hooks[event]:
            try:
                proc = subprocess.run(
                    cmd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    env={"ENVCHAIN_PROFILE": profile_name},
                )
                results.append(
                    HookResult(
                        event=event,
                        profile_name=profile_name,
                        success=proc.returncode == 0,
                        output=proc.stdout.strip(),
                        error=proc.stderr.strip(),
                    )
                )
            except Exception as exc:  # pragma: no cover
                results.append(
                    HookResult(event=event, profile_name=profile_name, success=False, error=str(exc))
                )

        for fn in self._callable_hooks[event]:
            try:
                fn(profile_name)
                results.append(HookResult(event=event, profile_name=profile_name, success=True))
            except Exception as exc:
                results.append(
                    HookResult(event=event, profile_name=profile_name, success=False, error=str(exc))
                )

        return results

    def clear(self, event: Optional[HookEvent] = None) -> None:
        """Remove all hooks, optionally scoped to a single event."""
        targets = [event] if event else list(HookEvent)
        for e in targets:
            self._shell_hooks[e].clear()
            self._callable_hooks[e].clear()
