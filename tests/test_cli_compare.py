"""Tests for envchain.cli_compare."""
import sys
import pytest
from unittest.mock import MagicMock
from envchain.cli_compare import CompareCommand


@pytest.fixture
def mock_storage():
    storage = MagicMock()
    return storage


@pytest.fixture
def cmd(mock_storage):
    return CompareCommand(mock_storage)


def _profile(vars_: dict) -> dict:
    return {"vars": vars_}


class TestCompareCommand:
    def test_run_identical_profiles_prints_identical(self, cmd, mock_storage, capsys):
        mock_storage.load_profile.return_value = _profile({"A": "1"})
        cmd.run("dev", "prod", password="pw", mask_values=False)
        out = capsys.readouterr().out
        assert "identical" in out.lower()

    def test_run_shows_added_key(self, cmd, mock_storage, capsys):
        mock_storage.load_profile.side_effect = [
            _profile({}),
            _profile({"NEW_KEY": "value"}),
        ]
        cmd.run("dev", "prod", password="pw", mask_values=False)
        out = capsys.readouterr().out
        assert "NEW_KEY" in out
        assert "+" in out

    def test_run_shows_removed_key(self, cmd, mock_storage, capsys):
        mock_storage.load_profile.side_effect = [
            _profile({"OLD_KEY": "value"}),
            _profile({}),
        ]
        cmd.run("dev", "prod", password="pw", mask_values=False)
        out = capsys.readouterr().out
        assert "OLD_KEY" in out
        assert "-" in out

    def test_run_masks_values_by_default(self, cmd, mock_storage, capsys):
        mock_storage.load_profile.side_effect = [
            _profile({"SECRET": "plaintext"}),
            _profile({"SECRET": "other"}),
        ]
        cmd.run("dev", "prod", password="pw", mask_values=True)
        out = capsys.readouterr().out
        assert "plaintext" not in out
        assert "***" in out

    def test_run_left_missing_exits(self, cmd, mock_storage):
        mock_storage.load_profile.return_value = None
        with pytest.raises(SystemExit) as exc:
            cmd.run("missing", "prod", password="pw")
        assert exc.value.code == 1

    def test_run_right_missing_exits(self, cmd, mock_storage):
        mock_storage.load_profile.side_effect = [_profile({"A": "1"}), None]
        with pytest.raises(SystemExit) as exc:
            cmd.run("dev", "missing", password="pw")
        assert exc.value.code == 1

    def test_show_same_includes_identical_keys(self, cmd, mock_storage, capsys):
        mock_storage.load_profile.return_value = _profile({"SHARED": "val"})
        cmd.run("dev", "prod", password="pw", show_same=True, mask_values=False)
        out = capsys.readouterr().out
        assert "SHARED" in out
        assert "identical" in out
