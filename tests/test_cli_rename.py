"""Tests for envchain.cli_rename."""
import sys
import pytest
from unittest.mock import MagicMock

from envchain.cli_rename import RenameCommand


@pytest.fixture
def mock_profile():
    p = MagicMock()
    p.variables = {"DB_HOST": "localhost", "DB_PORT": "5432", "API_KEY": "secret"}
    return p


@pytest.fixture
def mock_storage(mock_profile):
    s = MagicMock()
    s.load_profile.return_value = mock_profile
    return s


@pytest.fixture
def cmd(mock_storage):
    return RenameCommand(mock_storage, "dev", "hunter2")


class TestRenameCommand:
    def test_run_success(self, cmd, mock_storage, mock_profile):
        cmd.run("DB_HOST", "DATABASE_HOST")
        assert "DATABASE_HOST" in mock_profile.variables
        assert "DB_HOST" not in mock_profile.variables
        mock_storage.save_profile.assert_called_once()

    def test_run_missing_key_exits(self, cmd, capsys):
        with pytest.raises(SystemExit) as exc:
            cmd.run("MISSING", "NEW")
        assert exc.value.code == 1
        captured = capsys.readouterr()
        assert "does not exist" in captured.err

    def test_run_conflict_exits(self, cmd, capsys):
        with pytest.raises(SystemExit) as exc:
            cmd.run("DB_HOST", "DB_PORT")
        assert exc.value.code == 1
        captured = capsys.readouterr()
        assert "already exists" in captured.err

    def test_run_conflict_with_overwrite_succeeds(self, cmd, mock_storage, mock_profile):
        cmd.run("DB_HOST", "DB_PORT", overwrite=True)
        assert mock_profile.variables["DB_PORT"] == "localhost"
        mock_storage.save_profile.assert_called_once()

    def test_run_profile_not_found_exits(self, mock_storage, capsys):
        mock_storage.load_profile.return_value = None
        cmd = RenameCommand(mock_storage, "missing", "pw")
        with pytest.raises(SystemExit) as exc:
            cmd.run("A", "B")
        assert exc.value.code == 1
        captured = capsys.readouterr()
        assert "not found" in captured.err

    def test_bulk_run_success(self, cmd, mock_storage, mock_profile):
        cmd.bulk_run({"DB_HOST": "DATABASE_HOST", "API_KEY": "API_SECRET"})
        assert "DATABASE_HOST" in mock_profile.variables
        assert "API_SECRET" in mock_profile.variables
        mock_storage.save_profile.assert_called_once()

    def test_bulk_run_all_fail_exits(self, cmd, capsys):
        with pytest.raises(SystemExit) as exc:
            cmd.bulk_run({"NOPE": "ALSO_NOPE"})
        assert exc.value.code == 1
