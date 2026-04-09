"""Profile manager for switching and listing environment profiles."""

from typing import List, Optional
from pathlib import Path

from envchain.storage import EnvStorage
from envchain.models import Profile


ACTIVE_PROFILE_FILE = ".envchain_active"


class ProfileManager:
    """Manages profile switching and listing for a project directory."""

    def __init__(self, storage: EnvStorage, project_dir: Optional[Path] = None):
        self.storage = storage
        self.project_dir = Path(project_dir) if project_dir else Path.cwd()
        self._active_file = self.project_dir / ACTIVE_PROFILE_FILE

    def list_profiles(self) -> List[str]:
        """Return all available profile names."""
        return self.storage.list_profiles()

    def get_active_profile(self) -> Optional[str]:
        """Return the currently active profile name, or None if not set."""
        if self._active_file.exists():
            name = self._active_file.read_text().strip()
            return name if name else None
        return None

    def set_active_profile(self, name: str) -> None:
        """Set the active profile by name. Raises ValueError if not found."""
        available = self.list_profiles()
        if name not in available:
            raise ValueError(f"Profile '{name}' does not exist.")
        self._active_file.write_text(name)

    def clear_active_profile(self) -> None:
        """Clear the active profile selection."""
        if self._active_file.exists():
            self._active_file.unlink()

    def load_active_profile(self, password: str) -> Optional[Profile]:
        """Load and return the currently active profile, or None."""
        name = self.get_active_profile()
        if name is None:
            return None
        return self.storage.load_profile(name, password)

    def profile_exists(self, name: str) -> bool:
        """Check whether a named profile exists in storage."""
        return name in self.list_profiles()
