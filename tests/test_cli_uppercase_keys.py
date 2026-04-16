"""Tests for UppercaseKeysCommand."""
import pytest
from unittest.mock import MagicMock
from envchain.cli_uppercase_keys import UppercaseKeysCommand
from envchain.models import Profile


def _make_profile(vars_: dict) -> Profile:
    p = Profile(name="test")
    p.vars = vars_
    return p


@pytest.fixture
def mock_storage():
    return MagicMock()


@pytest.fixture
def cmd(mock_storage):
    return UppercaseKeysCommand(mock_storage, "dev")


class TestUppercaseKeysCommand:
    def test_run_saves_normalized_profile(self, mock_storage, cmd, capsys):
        mock_storage.load_profile.return_value = _make_profile({"myKey": "val"})
        cmd.run()
        mock_storage.save_profile.assert_called_once()
        out = capsys.readouterr().out
        assert "MY_KEY" in out

    def test_run_no_changes_skips_save(self, mock_storage, cmd, capsys):
        mock_storage.load_profile.return_value = _make_profile({"MY_KEY": "val"})
        cmd.run()
        mock_storage.save_profile.assert_not_called()
        out = capsys.readouterr().out
        assert "already normalized" in out

    def test_run_dry_run_does_not_save(self, mock_storage, cmd, capsys):
        mock_storage.load_profile.return_value = _make_profile({"camelCase": "v"})
        cmd.run(dry_run=True)
        mock_storage.save_profile.assert_not_called()
        out = capsys.readouterr().out
        assert "Dry run" in out

    def test_run_missing_profile_exits(self, mock_storage, cmd):
        mock_storage.load_profile.return_value = None
        with pytest.raises(SystemExit):
            cmd.run()

    def test_show_report_prints_repr(self, mock_storage, cmd, capsys):
        mock_storage.load_profile.return_value = _make_profile({"myKey": "v"})
        cmd.show_report()
        out = capsys.readouterr().out
        assert "KeyNormalizeReport" in out
