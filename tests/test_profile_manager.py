"""Tests for ProfileManager."""

import pytest
from pathlib import Path
from unittest.mock import MagicMock

from envchain.profile_manager import ProfileManager, ACTIVE_PROFILE_FILE
from envchain.models import Profile


@pytest.fixture
def mock_storage():
    storage = MagicMock()
    storage.list_profiles.return_value = ["dev", "staging", "prod"]
    return storage


@pytest.fixture
def manager(tmp_path, mock_storage):
    return ProfileManager(storage=mock_storage, project_dir=tmp_path)


def test_list_profiles(manager, mock_storage):
    assert manager.list_profiles() == ["dev", "staging", "prod"]


def test_get_active_profile_none_when_missing(manager):
    assert manager.get_active_profile() is None


def test_set_and_get_active_profile(manager):
    manager.set_active_profile("dev")
    assert manager.get_active_profile() == "dev"


def test_set_active_profile_invalid_raises(manager):
    with pytest.raises(ValueError, match="does not exist"):
        manager.set_active_profile("nonexistent")


def test_clear_active_profile(manager, tmp_path):
    manager.set_active_profile("staging")
    manager.clear_active_profile()
    assert manager.get_active_profile() is None
    assert not (tmp_path / ACTIVE_PROFILE_FILE).exists()


def test_clear_active_profile_noop_if_not_set(manager):
    manager.clear_active_profile()  # should not raise


def test_load_active_profile_returns_none_when_no_active(manager):
    result = manager.load_active_profile("secret")
    assert result is None


def test_load_active_profile_calls_storage(manager, mock_storage):
    mock_profile = Profile(name="dev", variables={})
    mock_storage.load_profile.return_value = mock_profile
    manager.set_active_profile("dev")
    result = manager.load_active_profile("secret")
    mock_storage.load_profile.assert_called_once_with("dev", "secret")
    assert result == mock_profile


def test_profile_exists_true(manager):
    assert manager.profile_exists("dev") is True


def test_profile_exists_false(manager):
    assert manager.profile_exists("ghost") is False
