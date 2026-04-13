"""Tests for envchain.cli_alias_expand."""
import sys
import pytest
from unittest.mock import MagicMock

from envchain.cli_alias_expand import AliasExpandCommand
from envchain.models import Profile


@pytest.fixture
def mock_storage():
    storage = MagicMock()
    profile = Profile(name="dev", variables={"DB_HOST": "localhost"})
    storage.load_profile.return_value = profile
    return storage


@pytest.fixture
def cmd(mock_storage):
    return AliasExpandCommand(mock_storage)


class TestAliasExpandCommand:
    def test_run_expands_and_saves(self, cmd, mock_storage, capsys):
        cmd.run(
            "dev",
            {"DATABASE_HOST": "DB_HOST"},
            password="secret",
        )
        mock_storage.save_profile.assert_called_once()
        out = capsys.readouterr().out
        assert "expanded" in out

    def test_run_dry_run_does_not_save(self, cmd, mock_storage, capsys):
        cmd.run(
            "dev",
            {"DATABASE_HOST": "DB_HOST"},
            password="secret",
            dry_run=True,
        )
        mock_storage.save_profile.assert_not_called()
        out = capsys.readouterr().out
        assert "dry-run" in out

    def test_run_no_alias_map_warns(self, cmd, mock_storage, capsys):
        cmd.run("dev", {}, password="secret")
        mock_storage.save_profile.assert_not_called()
        out = capsys.readouterr().out
        assert "nothing to expand" in out

    def test_run_missing_profile_exits(self, cmd, mock_storage):
        mock_storage.load_profile.return_value = None
        with pytest.raises(SystemExit):
            cmd.run("missing", {"X": "Y"}, password="secret")

    def test_run_no_match_skips_save(self, cmd, mock_storage, capsys):
        cmd.run(
            "dev",
            {"CACHE_HOST": "REDIS_HOST"},
            password="secret",
        )
        mock_storage.save_profile.assert_not_called()
        out = capsys.readouterr().out
        assert "unchanged" in out

    def test_show_aliases_delegates_to_dry_run(self, cmd, mock_storage, capsys):
        cmd.show_aliases("dev", "secret", {"DATABASE_HOST": "DB_HOST"})
        mock_storage.save_profile.assert_not_called()
        out = capsys.readouterr().out
        assert "dry-run" in out
