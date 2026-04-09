"""Storage module for managing encrypted environment variable profiles."""
import json
import os
from pathlib import Path
from typing import Dict, Optional, List

from .crypto import EnvCrypto


class EnvStorage:
    """Manages storage and retrieval of encrypted environment profiles."""

    def __init__(self, storage_dir: Optional[str] = None):
        """Initialize storage with a directory path.
        
        Args:
            storage_dir: Directory to store encrypted profiles. 
                        Defaults to ~/.envchain
        """
        if storage_dir is None:
            storage_dir = os.path.join(Path.home(), ".envchain")
        
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_profile_path(self, project: str, profile: str) -> Path:
        """Get the file path for a specific profile.
        
        Args:
            project: Project name
            profile: Profile name
            
        Returns:
            Path object for the profile file
        """
        project_dir = self.storage_dir / project
        project_dir.mkdir(parents=True, exist_ok=True)
        return project_dir / f"{profile}.enc"
    
    def save_profile(self, project: str, profile: str, env_vars: Dict[str, str], password: str) -> None:
        """Save encrypted environment variables for a profile.
        
        Args:
            project: Project name
            profile: Profile name
            env_vars: Dictionary of environment variables
            password: Password for encryption
        """
        crypto = EnvCrypto(password)
        data = json.dumps(env_vars)
        encrypted_data = crypto.encrypt(data)
        
        profile_path = self._get_profile_path(project, profile)
        profile_path.write_bytes(encrypted_data)
    
    def load_profile(self, project: str, profile: str, password: str) -> Dict[str, str]:
        """Load and decrypt environment variables for a profile.
        
        Args:
            project: Project name
            profile: Profile name
            password: Password for decryption
            
        Returns:
            Dictionary of environment variables
            
        Raises:
            FileNotFoundError: If profile doesn't exist
            ValueError: If decryption fails
        """
        profile_path = self._get_profile_path(project, profile)
        
        if not profile_path.exists():
            raise FileNotFoundError(f"Profile '{profile}' not found for project '{project}'")
        
        encrypted_data = profile_path.read_bytes()
        crypto = EnvCrypto(password)
        decrypted_data = crypto.decrypt(encrypted_data)
        
        return json.loads(decrypted_data)
    
    def list_projects(self) -> List[str]:
        """List all projects.
        
        Returns:
            List of project names
        """
        if not self.storage_dir.exists():
            return []
        
        return [d.name for d in self.storage_dir.iterdir() if d.is_dir()]
    
    def list_profiles(self, project: str) -> List[str]:
        """List all profiles for a project.
        
        Args:
            project: Project name
            
        Returns:
            List of profile names
        """
        project_dir = self.storage_dir / project
        
        if not project_dir.exists():
            return []
        
        return [f.stem for f in project_dir.glob("*.enc")]
    
    def delete_profile(self, project: str, profile: str) -> bool:
        """Delete a profile.
        
        Args:
            project: Project name
            profile: Profile name
            
        Returns:
            True if deleted, False if not found
        """
        profile_path = self._get_profile_path(project, profile)
        
        if profile_path.exists():
            profile_path.unlink()
            return True
        
        return False
