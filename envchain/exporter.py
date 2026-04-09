"""Export environment variables in various shell formats."""

from typing import Dict, Optional
from enum import Enum


class ExportFormat(str, Enum):
    BASH = "bash"
    FISH = "fish"
    DOTENV = "dotenv"
    JSON = "json"


class EnvExporter:
    """Handles exporting environment variables in multiple shell formats."""

    def export(self, variables: Dict[str, str], fmt: ExportFormat) -> str:
        """Export variables in the specified format."""
        handlers = {
            ExportFormat.BASH: self._export_bash,
            ExportFormat.FISH: self._export_fish,
            ExportFormat.DOTENV: self._export_dotenv,
            ExportFormat.JSON: self._export_json,
        }
        handler = handlers.get(fmt)
        if handler is None:
            raise ValueError(f"Unsupported export format: {fmt}")
        return handler(variables)

    def _export_bash(self, variables: Dict[str, str]) -> str:
        """Export as bash export statements."""
        lines = []
        for key, value in sorted(variables.items()):
            escaped = value.replace("\\", "\\\\").replace('"', '\\"')
            lines.append(f'export {key}="{escaped}"')
        return "\n".join(lines)

    def _export_fish(self, variables: Dict[str, str]) -> str:
        """Export as fish shell set statements."""
        lines = []
        for key, value in sorted(variables.items()):
            escaped = value.replace("\\", "\\\\").replace('"', '\\"')
            lines.append(f'set -x {key} "{escaped}"')
        return "\n".join(lines)

    def _export_dotenv(self, variables: Dict[str, str]) -> str:
        """Export as .env file format."""
        lines = []
        for key, value in sorted(variables.items()):
            escaped = value.replace("\\", "\\\\").replace('"', '\\"')
            lines.append(f'{key}="{escaped}"')
        return "\n".join(lines)

    def _export_json(self, variables: Dict[str, str]) -> str:
        """Export as JSON object."""
        import json
        return json.dumps(variables, indent=2, sort_keys=True)

    def get_eval_command(self, fmt: ExportFormat, profile: str, Optional_hint: Optional[str] = None) -> str:
        """Return the eval command hint for the given shell format."""
        hints = {
            ExportFormat.BASH: f'eval "$(envchain export {profile} --format bash)"',
            ExportFormat.FISH: f'envchain export {profile} --format fish | source',
            ExportFormat.DOTENV: f'# Load with: export $(cat .env | xargs)',
            ExportFormat.JSON: f'# Parse with your preferred JSON tool',
        }
        return hints.get(fmt, "")
