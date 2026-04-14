"""Tests for envchain.cli_normalize."""
import sys
from unittest.mock import MagicMock

import pytest

from envchain.cli_normalize import NormalizeCommand
from envchain.models import Profile


@pytest.fixture
def mock_storage():
    storage = MagicMock()
    profile = Profile(name="dev", vars={"KEY": "  value  ", "CLEAN": "ok"})
    storage.load_profile.return_value = profile
    return storage


@pytest.fixture
def cmd(mock_storage):
    return NormalizeCommand(storage=mock_storage)


class TestNormalizeCommand:
    def test_run_saves_normalized_profile(self, cmd, mock_storage, capsys):
        cmd.run("dev", "pass")
        mock_storage.save_profile.assert_called_once()
        out = capsys.readouterr().out
        assert "Normalized" in out

    def test_run_no_changes_skips_save(self, cmd, mock_storage, capsys):
        profile = Profile(name="dev", vars={"KEY": "clean"})
        mock_storage.load_profile.return_value = profile
        cmd.run("dev", "pass")
        mock_storage.save_profile.assert_not_called()
        out = capsys.readouterr().out
        assert "already normalized" in out

    def test_run_dry_run_does_not_save(self, cmd, mock_storage, capsys):
        cmd.run("dev", "pass", dry_run=True)
        mock_storage.save_profile.assert_not_called()
        out = capsys.readouterr().out
        assert "Dry run" in out

    def test_run_missing_profile_exits(self, cmd, mock_storage):
        mock_storage.load_profile.return_value = None
        with pytest.raises(SystemExit):
            cmd.run("missing", "pass")

    def test_run_invalid_strategy_exits(self, cmd, mock_storage):
        with pytest.raises(SystemExit):
            cmd.run("dev", "pass", strategies=["bogus"])

    def test_run_upper_strategy_applies(self, cmd, mock_storage, capsys):
        profile = Profile(name="dev", vars={"KEY": "hello"})
        mock_storage.load_profile.return_value = profile
        cmd.run("dev", "pass", strategies=["upper"])
        saved_profile = mock_storage.save_profile.call_args[0][0]
        assert saved_profile.vars["KEY"] == "HELLO"

    def test_list_strategies_prints_all(self, cmd, capsys):
        cmd.list_strategies()
        out = capsys.readouterr().out
        for strategy in ("strip", "lower", "upper", "strip_quotes"):
            assert strategy in out
