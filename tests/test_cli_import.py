"""Tests for ImportCommand."""

import json
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from envchain.cli_import import ImportCommand
from envchain.models import Profile
from envchain.storage import EnvStorage


@pytest.fixture
def mock_storage():
    return MagicMock(spec=EnvStorage)


@pytest.fixture
def cmd(mock_storage):
    return ImportCommand(storage=mock_storage)


@pytest.fixture
def dotenv_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("API_KEY=secret\nDEBUG=true\n")
    return str(p)


@pytest.fixture
def json_file(tmp_path):
    p = tmp_path / "vars.json"
    p.write_text(json.dumps({"HOST": "localhost", "PORT": "5432"}))
    return str(p)


class TestImportCommand:
    def test_import_into_new_profile(self, cmd, mock_storage, dotenv_file):
        mock_storage.load_profile.return_value = None
        result = cmd.run("dev", dotenv_file, "pass")
        assert result["added"] == 2
        assert result["skipped"] == 0
        mock_storage.save_profile.assert_called_once()

    def test_import_skips_existing_without_overwrite(self, cmd, mock_storage, dotenv_file):
        profile = Profile(name="dev")
        profile.add_var("API_KEY", "old_value")
        mock_storage.load_profile.return_value = profile
        result = cmd.run("dev", dotenv_file, "pass", overwrite=False)
        assert result["skipped"] == 1
        assert result["added"] == 1

    def test_import_overwrites_existing_when_flag_set(self, cmd, mock_storage, dotenv_file):
        profile = Profile(name="dev")
        profile.add_var("API_KEY", "old_value")
        mock_storage.load_profile.return_value = profile
        result = cmd.run("dev", dotenv_file, "pass", overwrite=True)
        assert result["added"] == 2
        assert result["skipped"] == 0

    def test_import_json_format(self, cmd, mock_storage, json_file):
        mock_storage.load_profile.return_value = None
        result = cmd.run("prod", json_file, "pass", fmt="json")
        assert result["added"] == 2

    def test_empty_file_returns_zero_counts(self, cmd, mock_storage, tmp_path):
        empty = tmp_path / ".env"
        empty.write_text("# only comments\n")
        mock_storage.load_profile.return_value = None
        result = cmd.run("dev", str(empty), "pass")
        assert result == {"added": 0, "skipped": 0, "total": 0}
        mock_storage.save_profile.assert_not_called()

    def test_list_formats_returns_all(self, cmd):
        formats = cmd.list_formats()
        assert "dotenv" in formats
        assert "shell" in formats
        assert "json" in formats
