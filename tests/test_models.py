"""Tests for the models module."""
import pytest

from envchain.models import Profile


class TestProfile:
    """Test cases for Profile class."""

    def test_create_profile(self):
        """Test creating a new profile."""
        profile = Profile(name="dev", project="myapp")
        
        assert profile.name == "dev"
        assert profile.project == "myapp"
        assert profile.env_vars == {}
    
    def test_add_var(self):
        """Test adding environment variables."""
        profile = Profile(name="dev", project="myapp")
        
        profile.add_var("API_KEY", "secret123")
        profile.add_var("DB_HOST", "localhost")
        
        assert profile.env_vars == {"API_KEY": "secret123", "DB_HOST": "localhost"}
    
    def test_update_existing_var(self):
        """Test updating an existing variable."""
        profile = Profile(name="dev", project="myapp")
        
        profile.add_var("API_KEY", "old_secret")
        profile.add_var("API_KEY", "new_secret")
        
        assert profile.env_vars["API_KEY"] == "new_secret"
    
    def test_remove_var(self):
        """Test removing a variable."""
        profile = Profile(name="dev", project="myapp")
        profile.add_var("API_KEY", "secret123")
        
        result = profile.remove_var("API_KEY")
        
        assert result is True
        assert "API_KEY" not in profile.env_vars
    
    def test_remove_nonexistent_var(self):
        """Test removing a variable that doesn't exist."""
        profile = Profile(name="dev", project="myapp")
        
        result = profile.remove_var("NONEXISTENT")
        
        assert result is False
    
    def test_get_var(self):
        """Test getting a variable value."""
        profile = Profile(name="dev", project="myapp")
        profile.add_var("API_KEY", "secret123")
        
        value = profile.get_var("API_KEY")
        
        assert value == "secret123"
    
    def test_get_nonexistent_var(self):
        """Test getting a variable that doesn't exist."""
        profile = Profile(name="dev", project="myapp")
        
        value = profile.get_var("NONEXISTENT")
        
        assert value is None
    
    def test_update_vars(self):
        """Test updating multiple variables at once."""
        profile = Profile(name="dev", project="myapp")
        profile.add_var("EXISTING", "value")
        
        profile.update_vars({"API_KEY": "secret", "DB_HOST": "localhost"})
        
        assert profile.env_vars == {
            "EXISTING": "value",
            "API_KEY": "secret",
            "DB_HOST": "localhost"
        }
    
    def test_clear_vars(self):
        """Test clearing all variables."""
        profile = Profile(name="dev", project="myapp")
        profile.add_var("API_KEY", "secret")
        profile.add_var("DB_HOST", "localhost")
        
        profile.clear_vars()
        
        assert profile.env_vars == {}
    
    def test_to_dict(self):
        """Test converting profile to dictionary."""
        profile = Profile(name="dev", project="myapp")
        profile.add_var("API_KEY", "secret")
        
        result = profile.to_dict()
        
        assert result == {"API_KEY": "secret"}
        # Ensure it's a copy
        result["NEW_KEY"] = "value"
        assert "NEW_KEY" not in profile.env_vars
    
    def test_from_dict(self):
        """Test creating profile from dictionary."""
        env_vars = {"API_KEY": "secret", "DB_HOST": "localhost"}
        
        profile = Profile.from_dict("dev", "myapp", env_vars)
        
        assert profile.name == "dev"
        assert profile.project == "myapp"
        assert profile.env_vars == env_vars
