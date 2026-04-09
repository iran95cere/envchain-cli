"""Data models for envchain."""
from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class Profile:
    """Represents an environment profile."""
    
    name: str
    project: str
    env_vars: Dict[str, str] = field(default_factory=dict)
    
    def add_var(self, key: str, value: str) -> None:
        """Add or update an environment variable.
        
        Args:
            key: Variable name
            value: Variable value
        """
        self.env_vars[key] = value
    
    def remove_var(self, key: str) -> bool:
        """Remove an environment variable.
        
        Args:
            key: Variable name
            
        Returns:
            True if removed, False if not found
        """
        if key in self.env_vars:
            del self.env_vars[key]
            return True
        return False
    
    def get_var(self, key: str) -> Optional[str]:
        """Get an environment variable value.
        
        Args:
            key: Variable name
            
        Returns:
            Variable value or None if not found
        """
        return self.env_vars.get(key)
    
    def update_vars(self, vars_dict: Dict[str, str]) -> None:
        """Update multiple environment variables.
        
        Args:
            vars_dict: Dictionary of variables to update
        """
        self.env_vars.update(vars_dict)
    
    def clear_vars(self) -> None:
        """Clear all environment variables."""
        self.env_vars.clear()
    
    def to_dict(self) -> Dict[str, str]:
        """Convert profile to dictionary.
        
        Returns:
            Dictionary of environment variables
        """
        return self.env_vars.copy()
    
    @classmethod
    def from_dict(cls, name: str, project: str, env_vars: Dict[str, str]) -> 'Profile':
        """Create a Profile from a dictionary.
        
        Args:
            name: Profile name
            project: Project name
            env_vars: Dictionary of environment variables
            
        Returns:
            New Profile instance
        """
        return cls(name=name, project=project, env_vars=env_vars.copy())
