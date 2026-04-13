"""CLI commands for managing variable labels."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

from envchain.env_labels import LabelManager

_LABELS_FILE = "labels.json"


class LabelsCommand:
    def __init__(self, storage_dir: str) -> None:
        self._path = Path(storage_dir) / _LABELS_FILE

    def _load(self) -> LabelManager:
        if self._path.exists():
            data = json.loads(self._path.read_text())
            return LabelManager.from_dict(data)
        return LabelManager()

    def _save(self, mgr: LabelManager) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(mgr.to_dict(), indent=2))

    def add(self, var_name: str, label: str, description: str = "") -> None:
        mgr = self._load()
        try:
            entry = mgr.add(var_name, label, description)
        except ValueError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)
        self._save(mgr)
        print(f"Labelled '{entry.var_name}' as '{entry.label}'.")

    def remove(self, var_name: str) -> None:
        mgr = self._load()
        removed = mgr.remove(var_name)
        if removed:
            self._save(mgr)
            print(f"Label removed from '{var_name}'.")
        else:
            print(f"No label found for '{var_name}'.", file=sys.stderr)
            sys.exit(1)

    def list_labels(self) -> None:
        mgr = self._load()
        entries = mgr.all_entries()
        if not entries:
            print("No labels defined.")
            return
        for e in sorted(entries, key=lambda x: x.var_name):
            desc = f" — {e.description}" if e.description else ""
            print(f"  {e.var_name}: {e.label}{desc}")

    def find(self, label: str) -> None:
        mgr = self._load()
        matches = mgr.labeled_vars(label)
        if not matches:
            print(f"No variables with label '{label}'.")
        else:
            for name in sorted(matches):
                print(f"  {name}")
