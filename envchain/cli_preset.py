"""CLI commands for preset management."""
from __future__ import annotations

import sys
from typing import List

from envchain.env_preset import PresetManager


class PresetCommand:
    def __init__(self, manager: PresetManager) -> None:
        self._mgr = manager

    def add(self, name: str, description: str, assignments: List[str]) -> None:
        """Add a preset. assignments is a list of KEY=VALUE strings."""
        vars: dict = {}
        for item in assignments:
            if "=" not in item:
                print(f"[error] Invalid assignment {item!r} — expected KEY=VALUE", file=sys.stderr)
                sys.exit(1)
            k, _, v = item.partition("=")
            vars[k.strip()] = v.strip()
        try:
            preset = self._mgr.add(name, description, vars)
            print(f"[ok] Preset {preset.name!r} saved with {len(vars)} variable(s).")
        except ValueError as exc:
            print(f"[error] {exc}", file=sys.stderr)
            sys.exit(1)

    def remove(self, name: str) -> None:
        if self._mgr.remove(name):
            print(f"[ok] Preset {name!r} removed.")
        else:
            print(f"[error] Preset {name!r} not found.", file=sys.stderr)
            sys.exit(1)

    def list_presets(self) -> None:
        presets = self._mgr.list_presets()
        if not presets:
            print("No presets defined.")
            return
        for p in presets:
            desc = f" — {p.description}" if p.description else ""
            print(f"  {p.name}{desc} ({len(p.vars)} var(s))")

    def show(self, name: str) -> None:
        preset = self._mgr.get(name)
        if preset is None:
            print(f"[error] Preset {name!r} not found.", file=sys.stderr)
            sys.exit(1)
        print(f"Preset: {preset.name}")
        if preset.description:
            print(f"Description: {preset.description}")
        for k, v in sorted(preset.vars.items()):
            print(f"  {k}={v}")
