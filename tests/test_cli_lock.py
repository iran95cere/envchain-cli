"""Tests for envchain.cli_lock."""
from __future__ import annotations

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from envchain.cli_lock import LockCommand
from envchain.env_lock import LockManager


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


@pytest.fixture()
def cmd(tmp_dir: Path) -> LockCommand:
    return LockCommand(str(tmp_dir))


class TestLockCommand:
    def test_lock_prints_locked(self, cmd: LockCommand, capsys):
        cmd.lock("prod")
        out = capsys.readouterr().out
        assert "prod" in out

    def test_lock_with_reason_in_output(self, cmd: LockCommand, capsys):
        cmd.lock("prod", reason="freeze")
        out = capsys.readouterr().out
        assert "freeze" in out

    def test_lock_already_locked_exits(self, cmd: LockCommand):
        cmd.lock("prod")
        with pytest.raises(SystemExit):
            cmd.lock("prod")

    def test_unlock_success_prints_message(self, cmd: LockCommand, capsys):
        cmd.lock("prod")
        cmd.unlock("prod")
        out = capsys.readouterr().out
        assert "Unlocked" in out

    def test_unlock_not_locked_exits(self, cmd: LockCommand):
        with pytest.raises(SystemExit):
            cmd.unlock("ghost")

    def test_status_locked(self, cmd: LockCommand, capsys):
        cmd.lock("prod", reason="testing")
        capsys.readouterr()
        cmd.status("prod")
        out = capsys.readouterr().out
        assert "locked" in out.lower()

    def test_status_not_locked(self, cmd: LockCommand, capsys):
        cmd.status("dev")
        out = capsys.readouterr().out
        assert "not locked" in out

    def test_list_locked_empty(self, cmd: LockCommand, capsys):
        cmd.list_locked()
        out = capsys.readouterr().out
        assert "No profiles" in out

    def test_list_locked_shows_profiles(self, cmd: LockCommand, capsys):
        cmd.lock("alpha")
        cmd.lock("beta")
        capsys.readouterr()
        cmd.list_locked()
        out = capsys.readouterr().out
        assert "alpha" in out and "beta" in out
