"""Tests for envchain.cli_history."""

import pytest
from pathlib import Path

from envchain.cli_history import HistoryCommand
from envchain.env_history import HistoryManager


@pytest.fixture
def tmp_dir(tmp_path):
    return tmp_path


@pytest.fixture
def cmd(tmp_dir):
    return HistoryCommand(tmp_dir)


@pytest.fixture
def populated_cmd(tmp_dir):
    mgr = HistoryManager(tmp_dir)
    mgr.record("dev", "init")
    mgr.record("dev", "set", "API_KEY")
    mgr.record("dev", "remove", "OLD_VAR")
    return HistoryCommand(tmp_dir)


class TestHistoryCommand:
    def test_show_no_history_prints_message(self, cmd, capsys):
        cmd.show("ghost")
        out = capsys.readouterr().out
        assert "No history" in out

    def test_show_prints_entries(self, populated_cmd, capsys):
        populated_cmd.show("dev")
        out = capsys.readouterr().out
        assert "set" in out
        assert "API_KEY" in out

    def test_show_respects_limit(self, tmp_dir, capsys):
        mgr = HistoryManager(tmp_dir)
        for i in range(10):
            mgr.record("dev", "set", f"VAR_{i}")
        cmd = HistoryCommand(tmp_dir)
        cmd.show("dev", limit=3)
        out = capsys.readouterr().out
        assert out.count("set") == 3

    def test_clear_prints_confirmation(self, populated_cmd, capsys):
        populated_cmd.clear("dev")
        out = capsys.readouterr().out
        assert "cleared" in out

    def test_clear_removes_history(self, tmp_dir, capsys):
        mgr = HistoryManager(tmp_dir)
        mgr.record("dev", "set", "X")
        cmd = HistoryCommand(tmp_dir)
        cmd.clear("dev")
        assert mgr.get_history("dev") == []

    def test_last_no_history_exits(self, cmd):
        with pytest.raises(SystemExit):
            cmd.last("ghost")

    def test_last_prints_most_recent(self, populated_cmd, capsys):
        populated_cmd.last("dev")
        out = capsys.readouterr().out
        assert "remove" in out
        assert "OLD_VAR" in out
