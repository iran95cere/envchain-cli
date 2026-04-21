"""CLI commands for managing per-variable annotations."""
from __future__ import annotations

import sys
from envchain.env_annotate import AnnotationManager


class AnnotateCommand:
    """Add, remove, and list annotations for profile variables."""

    def __init__(self, storage_dir: str, profile_name: str) -> None:
        self._manager = AnnotationManager(storage_dir, profile_name)
        self._profile = profile_name

    def add(self, var_name: str, note: str, author: str = "") -> None:
        if not var_name.strip():
            print("Error: variable name must not be empty.", file=sys.stderr)
            sys.exit(1)
        if not note.strip():
            print("Error: note must not be empty.", file=sys.stderr)
            sys.exit(1)
        ann = self._manager.add(var_name, note, author)
        print(f"Annotation added for '{ann.var_name}' in profile '{self._profile}'.")

    def remove(self, var_name: str) -> None:
        removed = self._manager.remove(var_name)
        if removed:
            print(f"Annotation removed for '{var_name}'.")
        else:
            print(f"No annotation found for '{var_name}'.", file=sys.stderr)
            sys.exit(1)

    def show(self, var_name: str) -> None:
        ann = self._manager.get(var_name)
        if ann is None:
            print(f"No annotation for '{var_name}'.")
            return
        print(f"Variable : {ann.var_name}")
        print(f"Note     : {ann.note}")
        if ann.author:
            print(f"Author   : {ann.author}")
        print(f"Created  : {ann.created_at}")

    def list_all(self) -> None:
        annotations = self._manager.all()
        if not annotations:
            print(f"No annotations for profile '{self._profile}'.")
            return
        for ann in sorted(annotations, key=lambda a: a.var_name):
            author_part = f" [{ann.author}]" if ann.author else ""
            print(f"  {ann.var_name}: {ann.note}{author_part}")
