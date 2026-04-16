"""Tests for envchain.cli_shrink."""
import sys
import pytest
from unittest.mock import MagicMock
from envchain.cli_shrink import ShrinkCommand
from envchain.models import Profile


def _make_profile(name: str, vars_: dict) -> Profile:
    p = Profile(name=name)
    p.vars = dict(vars_)
    return p


@pytest.fixture
def mock_storage():
    storage = MagicMock()
    storage.list_profiles.return_value = ["dev"]
    storage.load_profile.return_value = _make_profile(
        "dev", {"KEY": "  value  ", "CLEAN": "ok"}
    )
    return storage


@pytest.fixture
def cmd(mock_storage):
    return ShrinkCommand(storage=mock_storage)


class TestShrinkCommand:
    def test_run_shrinks_and_saves(self, cmd, mock_storage, capsys):
        cmd.run("dev", strategy="strip")
        mock_storage.save_profile.assert_called_once()
        out = capsys.readouterr().out
        assert "Applied" in out

    def test_run_no_changes_skips_save(self, cmd, mock_storage, capsys):
        mock_storage.load_profile.return_value = _make_profile(
            "dev", {"KEY": "value", "OTHER": "ok"}
        )
        cmd.run("dev", strategy="strip")
        mock_storage.save_profile.assert_not_called()
        out = capsys.readouterr().out
        assert "No changes" in out

    def test_run_dry_run_does_not_save(self, cmd, mock_storage, capsys):
        cmd.run("dev", strategy="strip", dry_run=True)
        mock_storage.save_profile.assert_not_called()
        out = capsys.readouterr().out
        assert "Dry run" in out

    def test_run_missing_profile_exits(self, cmd, mock_storage):
        mock_storage.load_profile.return_value = None
        with pytest.raises(SystemExit):
            cmd.run("ghost")

    def test_run_invalid_strategy_exits(self, cmd, mock_storage):
        with pytest.raises(SystemExit):
            cmd.run("dev", strategy="invalid")

    def test_list_strategies_prints_all(self, cmd, capsys):
        cmd.list_strategies()
        out = capsys.readouterr().out
        assert "strip" in out
        assert "collapse_whitespace" in out
        assert "lowercase_booleans" in out
