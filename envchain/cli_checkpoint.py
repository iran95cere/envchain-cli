"""CLI commands for checkpoint management."""

from __future__ import annotations

import sys
from pathlib import Path

from envchain.env_checkpoint import Checkpoint, CheckpointManager


class CheckpointCommand:
    def __init__(self, storage_dir: Path) -> None:
        self._manager = CheckpointManager(storage_dir)

    def save(self, profile: str, name: str, vars: dict, description: str = "") -> None:
        cp = Checkpoint(
            name=name,
            profile=profile,
            vars=vars,
            description=description,
        )
        self._manager.save(cp)
        print(f"Checkpoint '{name}' saved for profile '{profile}'.")

    def restore(self, profile: str, name: str) -> dict:
        cp = self._manager.load(profile, name)
        if cp is None:
            print(
                f"Error: checkpoint '{name}' not found for profile '{profile}'.",
                file=sys.stderr,
            )
            sys.exit(1)
        print(f"Restored checkpoint '{name}' for profile '{profile}' ({len(cp.vars)} vars).")
        return cp.vars

    def list_checkpoints(self, profile: str) -> None:
        checkpoints = self._manager.list_checkpoints(profile)
        if not checkpoints:
            print(f"No checkpoints found for profile '{profile}'.")
            return
        print(f"Checkpoints for profile '{profile}':")
        for cp in checkpoints:
            desc = f"  — {cp.description}" if cp.description else ""
            print(f"  {cp.name} ({len(cp.vars)} vars){desc}")

    def delete(self, profile: str, name: str) -> None:
        removed = self._manager.delete(profile, name)
        if removed:
            print(f"Checkpoint '{name}' deleted from profile '{profile}'.")
        else:
            print(
                f"Error: checkpoint '{name}' not found for profile '{profile}'.",
                file=sys.stderr,
            )
            sys.exit(1)
