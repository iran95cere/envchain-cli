"""Tests for ProfileCommand CLI handler."""

import pytest
from unittest.mock import MagicMock, patch

from envchain.cli_profile import ProfileCommand


@pytest.fixture
def mock_storage():
    storage = MagicMock()
    storage.list_profiles.return_value = ["dev", "prod"]
    return storage


@pytest.fixture
def cmd(mock_storage, tmp_path):
    return ProfileCommand(storage=mock_storage, project_dir=str(tmp_path))


def test_list_profiles_output(cmd, capsys):
    cmd.manager.set_active_profile("dev")
    cmd.list_profiles()
    out = capsys.readouterr().out
    assert "* dev" in out
    assert "  prod" in out


def test_list_profiles_empty(cmd, mock_storage, capsys):
    mock_storage.list_profiles.return_value = []
    cmd.list_profiles()
    out = capsys.readouterr().out
    assert "No profiles found" in out


def test_use_profile_success(cmd, capsys):
    cmd.use_profile("prod")
    out = capsys.readouterr().out
    assert "Switched to profile 'prod'" in out
    assert cmd.manager.get_active_profile() == "prod"


def test_use_profile_invalid_exits(cmd, capsys):
    with pytest.raises(SystemExit):
        cmd.use_profile("ghost")
    out = capsys.readouterr().out
    assert "Error" in out


def test_current_profile_when_set(cmd, capsys):
    cmd.manager.set_active_profile("dev")
    cmd.current_profile()
    out = capsys.readouterr().out
    assert "Active profile: dev" in out


def test_current_profile_when_none(cmd, capsys):
    cmd.current_profile()
    out = capsys.readouterr().out
    assert "No active profile set" in out


def test_clear_profile(cmd, capsys):
    cmd.manager.set_active_profile("dev")
    cmd.clear_profile()
    out = capsys.readouterr().out
    assert "cleared" in out
    assert cmd.manager.get_active_profile() is None
