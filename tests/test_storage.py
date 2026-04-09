"""Tests for the storage module."""
import json
import pytest
import tempfile
import shutil
from pathlib import Path

from envchain.storage import EnvStorage


class TestEnvStorage:
    """Test cases for EnvStorage class."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_path = tempfile.mkdtemp()
        yield temp_path
        shutil.rmtree(temp_path)
    
    @pytest.fixture
    def storage(self, temp_dir):
        """Create an EnvStorage instance with temp directory."""
        return EnvStorage(storage_dir=temp_dir)
    
    def test_save_and_load_profile(self, storage):
        """Test saving and loading a profile."""
        env_vars = {"API_KEY": "secret123", "DB_HOST": "localhost"}
        password = "test_password"
        
        storage.save_profile("myproject", "dev", env_vars, password)
        loaded_vars = storage.load_profile("myproject", "dev", password)
        
        assert loaded_vars == env_vars
    
    def test_load_nonexistent_profile(self, storage):
        """Test loading a profile that doesn't exist."""
        with pytest.raises(FileNotFoundError):
            storage.load_profile("myproject", "nonexistent", "password")
    
    def test_wrong_password_fails(self, storage):
        """Test that wrong password fails to decrypt."""
        env_vars = {"API_KEY": "secret123"}
        
        storage.save_profile("myproject", "dev", env_vars, "correct_password")
        
        with pytest.raises(ValueError):
            storage.load_profile("myproject", "dev", "wrong_password")
    
    def test_list_projects(self, storage):
        """Test listing all projects."""
        storage.save_profile("project1", "dev", {"KEY": "val"}, "pass")
        storage.save_profile("project2", "prod", {"KEY": "val"}, "pass")
        
        projects = storage.list_projects()
        
        assert set(projects) == {"project1", "project2"}
    
    def test_list_profiles(self, storage):
        """Test listing profiles for a project."""
        storage.save_profile("myproject", "dev", {"KEY": "val"}, "pass")
        storage.save_profile("myproject", "staging", {"KEY": "val"}, "pass")
        storage.save_profile("myproject", "prod", {"KEY": "val"}, "pass")
        
        profiles = storage.list_profiles("myproject")
        
        assert set(profiles) == {"dev", "staging", "prod"}
    
    def test_list_profiles_empty_project(self, storage):
        """Test listing profiles for a non-existent project."""
        profiles = storage.list_profiles("nonexistent")
        assert profiles == []
    
    def test_delete_profile(self, storage):
        """Test deleting a profile."""
        storage.save_profile("myproject", "dev", {"KEY": "val"}, "pass")
        
        result = storage.delete_profile("myproject", "dev")
        assert result is True
        
        profiles = storage.list_profiles("myproject")
        assert "dev" not in profiles
    
    def test_delete_nonexistent_profile(self, storage):
        """Test deleting a profile that doesn't exist."""
        result = storage.delete_profile("myproject", "nonexistent")
        assert result is False
    
    def test_multiple_projects_isolation(self, storage):
        """Test that different projects are isolated."""
        storage.save_profile("project1", "dev", {"KEY1": "val1"}, "pass1")
        storage.save_profile("project2", "dev", {"KEY2": "val2"}, "pass2")
        
        vars1 = storage.load_profile("project1", "dev", "pass1")
        vars2 = storage.load_profile("project2", "dev", "pass2")
        
        assert vars1 == {"KEY1": "val1"}
        assert vars2 == {"KEY2": "val2"}
