"""CLI commands for managing scheduled profile actions."""

from __future__ import annotations

import sys
import time
from typing import Optional

from .scheduler import Scheduler, ScheduledAction

VALID_ACTIONS = ("activate", "deactivate", "expire")


class SchedulerCommand:
    def __init__(self, storage_dir: str) -> None:
        self._scheduler = Scheduler(storage_dir)

    def add(self, profile_name: str, action: str, run_at: float,
            repeat_seconds: Optional[int] = None) -> None:
        if action not in VALID_ACTIONS:
            print(
                f"Error: unknown action {action!r}. "
                f"Choose from {VALID_ACTIONS}.",
                file=sys.stderr,
            )
            sys.exit(1)
        sa = ScheduledAction(
            profile_name=profile_name,
            action=action,
            run_at=run_at,
            repeat_seconds=repeat_seconds,
        )
        self._scheduler.add(sa)
        print(f"Scheduled '{action}' for profile '{profile_name}' at {run_at}.")

    def remove(self, profile_name: str, action: str) -> None:
        removed = self._scheduler.remove(profile_name, action)
        if removed:
            print(f"Removed scheduled '{action}' for profile '{profile_name}'.")
        else:
            print(
                f"No scheduled '{action}' found for profile '{profile_name}'.",
                file=sys.stderr,
            )
            sys.exit(1)

    def list_actions(self) -> None:
        actions = self._scheduler.all_actions()
        if not actions:
            print("No scheduled actions.")
            return
        for a in actions:
            repeat = f" (repeat every {a.repeat_seconds}s)" if a.repeat_seconds else ""
            print(f"  [{a.action}] {a.profile_name} @ {a.run_at}{repeat}")

    def run_due(self, now: Optional[float] = None) -> None:
        due = self._scheduler.due_actions(now)
        if not due:
            print("No actions due.")
            return
        for a in due:
            print(f"Running: {a}")
            # Reschedule if repeating
            if a.repeat_seconds:
                a.run_at = (now or time.time()) + a.repeat_seconds
                a.last_run = now or time.time()
            else:
                self._scheduler.remove(a.profile_name, a.action)
