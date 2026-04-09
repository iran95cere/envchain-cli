"""CLI commands for profile switching and listing."""

from typing import Optional

from envchain.profile_manager import ProfileManager
from envchain.storage import EnvStorage


class ProfileCommand:
    """Handles 'profile' subcommands: list, use, current, clear."""

    def __init__(self, storage: EnvStorage, project_dir: Optional[str] = None):
        self.manager = ProfileManager(storage, project_dir)

    def list_profiles(self) -> None:
        """Print all available profiles, marking the active one."""
        profiles = self.manager.list_profiles()
        active = self.manager.get_active_profile()
        if not profiles:
            print("No profiles found.")
            return
        for name in sorted(profiles):
            marker = "* " if name == active else "  "
            print(f"{marker}{name}")

    def use_profile(self, name: str) -> None:
        """Switch to a named profile."""
        try:
            self.manager.set_active_profile(name)
            print(f"Switched to profile '{name}'.")
        except ValueError as exc:
            print(f"Error: {exc}")
            raise SystemExit(1)

    def current_profile(self) -> None:
        """Print the currently active profile."""
        active = self.manager.get_active_profile()
        if active:
            print(f"Active profile: {active}")
        else:
            print("No active profile set.")

    def clear_profile(self) -> None:
        """Clear the active profile selection."""
        self.manager.clear_active_profile()
        print("Active profile cleared.")
