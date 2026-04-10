"""Tests for envchain.cli_scheduler."""

import time
import pytest

from envchain.cli_scheduler import SchedulerCommand


@pytest.fixture
def tmp_dir(tmp_path):
    return str(tmp_path)


@pytest.fixture
def cmd(tmp_dir):
    return SchedulerCommand(tmp_dir)


class TestSchedulerCommand:
    def test_add_valid_action(self, cmd, capsys):
        cmd.add("prod", "activate", time.time() + 100)
        out = capsys.readouterr().out
        assert "prod" in out
        assert "activate" in out

    def test_add_invalid_action_exits(self, cmd):
        with pytest.raises(SystemExit):
            cmd.add("prod", "unknown_action", time.time() + 100)

    def test_list_empty(self, cmd, capsys):
        cmd.list_actions()
        out = capsys.readouterr().out
        assert "No scheduled" in out

    def test_list_shows_added_action(self, cmd, capsys):
        cmd.add("staging", "expire", time.time() + 200)
        capsys.readouterr()  # clear
        cmd.list_actions()
        out = capsys.readouterr().out
        assert "staging" in out
        assert "expire" in out

    def test_remove_existing(self, cmd, capsys):
        cmd.add("dev", "deactivate", time.time() + 50)
        capsys.readouterr()
        cmd.remove("dev", "deactivate")
        out = capsys.readouterr().out
        assert "Removed" in out

    def test_remove_nonexistent_exits(self, cmd):
        with pytest.raises(SystemExit):
            cmd.remove("ghost", "activate")

    def test_run_due_no_actions(self, cmd, capsys):
        cmd.run_due()
        out = capsys.readouterr().out
        assert "No actions due" in out

    def test_run_due_executes_past_action(self, cmd, capsys):
        past_ts = time.time() - 10
        cmd.add("prod", "expire", past_ts)
        capsys.readouterr()
        cmd.run_due()
        out = capsys.readouterr().out
        assert "Running" in out
