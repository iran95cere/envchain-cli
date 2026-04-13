"""Tests for envchain.cli_trim."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from envchain.cli_trim import TrimCommand
from envchain.models import Profile


def _make_profile(name: str, variables: dict) -> Profile:
    p = Profile(name=name)
    p.variables = variables
    return p


@pytest.fixture
def mock_storage():
    return MagicMock()


@pytest.fixture
def cmd(mock_storage):
    return TrimCommand(mock_storage)


class TestTrimCommand:
    def test_run_trims_and_saves(self, cmd, mock_storage, capsys):
        mock_storage.load_profile.return_value = _make_profile(
            "dev", {"FOO": "  hello  ", "BAR": "clean"}
        )
        cmd.run("dev", "pass")
        mock_storage.save_profile.assert_called_once()
        out = capsys.readouterr().out
        assert "1" in out
        assert "FOO" in out

    def test_run_no_changes_skips_save(self, cmd, mock_storage, capsys):
        mock_storage.load_profile.return_value = _make_profile(
            "dev", {"FOO": "hello"}
        )
        cmd.run("dev", "pass")
        mock_storage.save_profile.assert_not_called()
        out = capsys.readouterr().out
        assert "Nothing to trim" in out

    def test_run_dry_run_does_not_save(self, cmd, mock_storage, capsys):
        mock_storage.load_profile.return_value = _make_profile(
            "dev", {"FOO": "  val  "}
        )
        cmd.run("dev", "pass", dry_run=True)
        mock_storage.save_profile.assert_not_called()
        out = capsys.readouterr().out
        assert "Dry-run" in out

    def test_run_missing_profile_exits(self, cmd, mock_storage):
        mock_storage.load_profile.return_value = None
        with pytest.raises(SystemExit):
            cmd.run("ghost", "pass")

    def test_show_report_prints_summary(self, cmd, mock_storage, capsys):
        mock_storage.load_profile.return_value = _make_profile(
            "dev", {"A": " v ", "B": "ok"}
        )
        cmd.show_report("dev", "pass")
        out = capsys.readouterr().out
        assert "Total variables" in out
        assert "Changed" in out

    def test_show_report_missing_profile_exits(self, cmd, mock_storage):
        mock_storage.load_profile.return_value = None
        with pytest.raises(SystemExit):
            cmd.show_report("ghost", "pass")
