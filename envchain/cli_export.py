"""CLI export subcommand integration for envchain."""

from typing import Optional
from envchain.exporter import EnvExporter, ExportFormat
from envchain.storage import EnvStorage


class ExportCommand:
    """Handles the 'export' CLI subcommand."""

    def __init__(self, storage: EnvStorage):
        self.storage = storage
        self.exporter = EnvExporter()

    def run(
        self,
        profile_name: str,
        password: str,
        fmt: str = "bash",
        show_hint: bool = False,
        output_file: Optional[str] = None,
    ) -> str:
        """Export a profile's variables in the given format.

        Returns the formatted string output.
        Raises ValueError for unknown formats or missing profiles.
        """
        try:
            export_fmt = ExportFormat(fmt)
        except ValueError:
            valid = ", ".join(f.value for f in ExportFormat)
            raise ValueError(f"Unknown format '{fmt}'. Valid options: {valid}")

        profile = self.storage.load_profile(profile_name, password)
        if profile is None:
            raise FileNotFoundError(f"Profile '{profile_name}' not found.")

        output = self.exporter.export(profile.variables, export_fmt)

        if show_hint:
            hint = self.exporter.get_eval_command(export_fmt, profile_name)
            if hint:
                output = f"# {hint}\n{output}" if output else f"# {hint}"

        if output_file:
            with open(output_file, "w", encoding="utf-8") as fh:
                fh.write(output)
                if output:
                    fh.write("\n")

        return output

    def list_formats(self) -> list:
        """Return list of supported export format names."""
        return [fmt.value for fmt in ExportFormat]
