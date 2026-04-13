"""Preset management: named collections of env var defaults for quick profile bootstrapping."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Preset:
    name: str
    description: str
    vars: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {"name": self.name, "description": self.description, "vars": self.vars}

    @classmethod
    def from_dict(cls, data: dict) -> "Preset":
        return cls(
            name=data["name"],
            description=data.get("description", ""),
            vars=data.get("vars", {}),
        )

    def __repr__(self) -> str:
        return f"Preset(name={self.name!r}, vars={len(self.vars)})"


class PresetManager:
    def __init__(self, storage_dir: str) -> None:
        self._path = os.path.join(storage_dir, "presets.json")
        self._presets: Dict[str, Preset] = {}
        self._load()

    def _load(self) -> None:
        if os.path.exists(self._path):
            with open(self._path, "r", encoding="utf-8") as fh:
                raw = json.load(fh)
            self._presets = {k: Preset.from_dict(v) for k, v in raw.items()}

    def _save(self) -> None:
        with open(self._path, "w", encoding="utf-8") as fh:
            json.dump({k: v.to_dict() for k, v in self._presets.items()}, fh, indent=2)

    def add(self, name: str, description: str, vars: Dict[str, str]) -> Preset:
        if not name.strip():
            raise ValueError("Preset name must not be empty")
        preset = Preset(name=name, description=description, vars=dict(vars))
        self._presets[name] = preset
        self._save()
        return preset

    def remove(self, name: str) -> bool:
        if name in self._presets:
            del self._presets[name]
            self._save()
            return True
        return False

    def get(self, name: str) -> Optional[Preset]:
        return self._presets.get(name)

    def list_presets(self) -> List[Preset]:
        return sorted(self._presets.values(), key=lambda p: p.name)

    def apply(self, name: str, existing: Dict[str, str], overwrite: bool = False) -> Dict[str, str]:
        preset = self.get(name)
        if preset is None:
            raise KeyError(f"Preset {name!r} not found")
        result = dict(existing)
        for k, v in preset.vars.items():
            if overwrite or k not in result:
                result[k] = v
        return result
