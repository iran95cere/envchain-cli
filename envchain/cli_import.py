"""CLI command handler for importing environment variables into a profile."""

from typing import Optional

from envchain.importer import EnvImporter, ImportFormat
from envchain.storage import EnvStorage
from envchain.models import Profile


class ImportCommand:
    """Handles the 'import' CLI subcommand."""

    SUPPORTED_FORMATS = [f.value for f in ImportFormat]

    def __init__(self, storage: EnvStorage):
        self.storage = storage
        self.importer = EnvImporter()

    def run(
        self,
        profile_name: str,
        file_path: str,
        password: str,
        fmt: Optional[str] = None,
        overwrite: bool = False,
    ) -> dict:
        """Import variables from a file into the specified profile.

        Returns a summary dict with counts of added/skipped variables.
        """
        import_fmt = ImportFormat(fmt) if fmt else None
        new_vars = self.importer.import_file(file_path, fmt=import_fmt)

        if not new_vars:
            return {"added": 0, "skipped": 0, "total": 0}

        existing = self.storage.load_profile(profile_name, password)
        if existing is None:
            profile = Profile(name=profile_name)
        else:
            profile = existing

        added = 0
        skipped = 0
        for key, value in new_vars.items():
            if not overwrite and profile.get_var(key) is not None:
                skipped += 1
                continue
            profile.add_var(key, value)
            added += 1

        self.storage.save_profile(profile, password)
        return {"added": added, "skipped": skipped, "total": len(new_vars)}

    def list_formats(self) -> list:
        """Return supported import format names."""
        return self.SUPPORTED_FORMATS
