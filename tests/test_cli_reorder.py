"""Tests for envchain.cli_reorder."""
import sys
import pytest
from unittest.mock import MagicMock
from envchain.cli_reorder import ReorderCommand


@pytest.fixture
def mock_storage():
    s = MagicMock()
    s.load_profile.return_value = {"C": "3", "A": "1", "B": "2"}
    return s


@pytest.fixture
def cmd(mock_storage):
    return ReorderCommand(mock_storage)


class TestReorderCommand:
    def test_run_saves_reordered_profile(self, cmd, mock_storage):
        cmd.run("dev", "pass", ["A", "B", "C"])
        saved = mock_storage.save_profile.call_args[0][1]
        assert list(saved.keys()) == ["A", "B", "C"]

    def test_run_no_change_skips_save(self, cmd, mock_storage):
        mock_storage.load_profile.return_value = {"A": "1", "B": "2"}
        cmd.run("dev", "pass", ["A", "B"])
        mock_storage.save_profile.assert_not_called()

    def test_run_missing_profile_exits(self, cmd, mock_storage):
        mock_storage.load_profile.return_value = None
        with pytest.raises(SystemExit):
            cmd.run("ghost", "pass", ["A"])

    def test_dry_run_does_not_save(self, cmd, mock_storage, capsys):
        cmd.run("dev", "pass", ["A", "B", "C"], dry_run=True)
        mock_storage.save_profile.assert_not_called()
        out = capsys.readouterr().out
        assert "Dry-run" in out

    def test_show_order_prints_keys(self, cmd, mock_storage, capsys):
        cmd.show_order("dev", "pass")
        out = capsys.readouterr().out
        assert "A" in out
        assert "B" in out
        assert "C" in out

    def test_show_order_missing_profile_exits(self, cmd, mock_storage):
        mock_storage.load_profile.return_value = None
        with pytest.raises(SystemExit):
            cmd.show_order("ghost", "pass")

    def test_unknown_keys_warning_printed(self, cmd, capsys):
        cmd.run("dev", "pass", ["A", "Z", "B", "C"])
        out = capsys.readouterr().out
        assert "Z" in out
