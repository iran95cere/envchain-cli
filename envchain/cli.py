#!/usr/bin/env python3
"""CLI interface for envchain - environment variable management tool."""

import sys
import getpass
import argparse
from pathlib import Path
from typing import Optional

from envchain.storage import EnvStorage
from envchain.crypto import EnvCrypto
from envchain.models import Profile


class EnvChainCLI:
    """Main CLI handler for envchain operations."""

    def __init__(self, storage_dir: Optional[Path] = None):
        """Initialize CLI with storage directory."""
        self.storage = EnvStorage(storage_dir)

    def _get_password(self, confirm: bool = False) -> str:
        """Prompt user for password securely."""
        password = getpass.getpass("Enter password: ")
        if confirm:
            password_confirm = getpass.getpass("Confirm password: ")
            if password != password_confirm:
                print("Error: Passwords do not match", file=sys.stderr)
                sys.exit(1)
        return password

    def init_profile(self, profile_name: str, description: str = "") -> None:
        """Initialize a new profile."""
        if self.storage.profile_exists(profile_name):
            print(f"Error: Profile '{profile_name}' already exists", file=sys.stderr)
            sys.exit(1)

        password = self._get_password(confirm=True)
        profile = Profile(name=profile_name, description=description)
        crypto = EnvCrypto(password)
        
        self.storage.save_profile(profile, crypto)
        print(f"Profile '{profile_name}' created successfully")

    def set_var(self, profile_name: str, key: str, value: str) -> None:
        """Set an environment variable in a profile."""
        password = self._get_password()
        crypto = EnvCrypto(password)
        
        try:
            profile = self.storage.load_profile(profile_name, crypto)
        except Exception as e:
            print(f"Error loading profile: {e}", file=sys.stderr)
            sys.exit(1)

        profile.add_var(key, value)
        self.storage.save_profile(profile, crypto)
        print(f"Variable '{key}' set in profile '{profile_name}'")

    def get_var(self, profile_name: str, key: str) -> None:
        """Get an environment variable from a profile."""
        password = self._get_password()
        crypto = EnvCrypto(password)
        
        try:
            profile = self.storage.load_profile(profile_name, crypto)
            value = profile.get_var(key)
            if value is None:
                print(f"Error: Variable '{key}' not found", file=sys.stderr)
                sys.exit(1)
            print(value)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    def list_profiles(self) -> None:
        """List all available profiles."""
        profiles = self.storage.list_profiles()
        if not profiles:
            print("No profiles found")
            return
        
        print("Available profiles:")
        for profile in profiles:
            print(f"  - {profile}")

    def list_vars(self, profile_name: str) -> None:
        """List all variables in a profile."""
        password = self._get_password()
        crypto = EnvCrypto(password)
        
        try:
            profile = self.storage.load_profile(profile_name, crypto)
            if not profile.variables:
                print(f"No variables in profile '{profile_name}'")
                return
            
            print(f"Variables in profile '{profile_name}':")
            for key in sorted(profile.variables.keys()):
                print(f"  {key}")
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
