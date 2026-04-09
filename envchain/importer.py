"""Import environment variables from various file formats into envchain profiles."""

import os
import re
from enum import Enum
from pathlib import Path
from typing import Dict, Optional, Tuple


class ImportFormat(str, Enum):
    DOTENV = "dotenv"
    SHELL = "shell"
    JSON = "json"


class EnvImporter:
    """Handles importing environment variables from external files."""

    def import_file(self, path: str, fmt: Optional[ImportFormat] = None) -> Dict[str, str]:
        """Import variables from a file, auto-detecting format if not specified."""
        file_path = Path(path)
        if not file_path.exists():
            raise FileNotFoundError(f"Import file not found: {path}")

        if fmt is None:
            fmt = self._detect_format(file_path)

        content = file_path.read_text(encoding="utf-8")

        if fmt == ImportFormat.DOTENV:
            return self._parse_dotenv(content)
        elif fmt == ImportFormat.SHELL:
            return self._parse_shell(content)
        elif fmt == ImportFormat.JSON:
            return self._parse_json(content)
        else:
            raise ValueError(f"Unsupported import format: {fmt}")

    def _detect_format(self, path: Path) -> ImportFormat:
        """Auto-detect the file format based on extension and content."""
        suffix = path.suffix.lower()
        if suffix == ".json":
            return ImportFormat.JSON
        elif suffix in (".sh", ".bash", ".zsh"):
            return ImportFormat.SHELL
        return ImportFormat.DOTENV

    def _parse_dotenv(self, content: str) -> Dict[str, str]:
        """Parse a .env file into a dict of key-value pairs."""
        result: Dict[str, str] = {}
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            key, value = self._split_kv(line)
            if key:
                result[key] = value
        return result

    def _parse_shell(self, content: str) -> Dict[str, str]:
        """Parse shell export statements."""
        result: Dict[str, str] = {}
        pattern = re.compile(r'^(?:export\s+)([A-Za-z_][A-Za-z0-9_]*)=(.*)$')
        for line in content.splitlines():
            line = line.strip()
            match = pattern.match(line)
            if match:
                key = match.group(1)
                value = match.group(2).strip('"\'')
                result[key] = value
        return result

    def _parse_json(self, content: str) -> Dict[str, str]:
        """Parse a JSON object of string key-value pairs."""
        import json
        data = json.loads(content)
        if not isinstance(data, dict):
            raise ValueError("JSON import must be a top-level object")
        return {str(k): str(v) for k, v in data.items()}

    def _split_kv(self, line: str) -> Tuple[str, str]:
        """Split a KEY=VALUE line, stripping optional quotes from value."""
        if "=" not in line:
            return "", ""
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
            value = value[1:-1]
        return key, value
