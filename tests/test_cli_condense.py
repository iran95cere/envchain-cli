"""Tests for CondenseCommand CLI wrapper."""
import sys
import pytest
from unittest.mock import MagicMock
from envchain.cli_condense import CondenseCommand
from envchain.models import Profile


def _make_profile(name="dev", variables=None):
    p = Profile(name=name)
    p.variables = variables or {"DB_HOST": "localhost", "EMPTY": "", "db_host": "dup"}
    return p


@pytest.fixture
def mock_storage():
    s = MagicMock()
    s.load_profile.return_value = _make_profile()
    return s


@pytest.fixture
def cmd(mock_storage):
    return CondenseCommand(mock_storage)


class TestCondenseCommand:
    def test_run_saves_condensed_profile(self, cmd, mock_storage, capsys):
        cmd.run("dev", "pass")
        mock_storage.save_profile.assert_called_once()
        out = capsys.readouterr().out
        assert "dev" in out

    def test_run_dry_run_does_not_save(self, cmd, mock_storage, capsys):
        cmd.run("dev", "pass", dry_run=True)
        mock_storage.save_profile.assert_not_called()
        out = capsys.readouterr().out
        assert "dry-run" in out

    def test_run_no_changes_skips_save(self, cmd, mock_storage, capsys):
        mock_storage.load_profile.return_value = _make_profile(
            variables={"A": "1", "B": "2"}
        )
        cmd.run("dev", "pass")
        mock_storage.save_profile.assert_not_called()
        out = capsys.readouterr().out
        assert "already condensed" in out

    def test_run_missing_profile_exits(self, cmd, mock_storage):
        mock_storage.load_profile.return_value = None
        with pytest.raises(SystemExit):
            cmd.run("missing", "pass")

    def test_run_prints_removed_keys(self, cmd, mock_storage, capsys):
        cmd.run("dev", "pass")
        out = capsys.readouterr().out
        assert "Removed keys" in out or "Condensing" in out
