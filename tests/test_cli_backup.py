"""Tests for BackupCommand CLI wrapper."""

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from envchain.cli_backup import BackupCommand


@pytest.fixture
def tmp_dir(tmp_path):
    return tmp_path


@pytest.fixture
def storage_dir(tmp_dir):
    d = tmp_dir / "profiles"
    d.mkdir()
    (d / "staging.json").write_text('{"name": "staging"}')
    return d


@pytest.fixture
def cmd(storage_dir):
    return BackupCommand(str(storage_dir))


def test_create_prints_path(cmd, tmp_dir, capsys):
    out = str(tmp_dir / "cli_backup")
    cmd.create(output_path=out)
    captured = capsys.readouterr()
    assert "Backup created:" in captured.out


def test_create_failure_exits(cmd, capsys):
    with patch.object(cmd.manager, "create_backup", side_effect=OSError("disk full")):
        with pytest.raises(SystemExit):
            cmd.create()


def test_restore_prints_count(cmd, tmp_dir, capsys):
    backup_path = cmd.manager.create_backup(str(tmp_dir / "bak"))
    restore_dir = tmp_dir / "new_profiles"
    restore_cmd = BackupCommand(str(restore_dir))
    restore_cmd.restore(backup_path, overwrite=True)
    captured = capsys.readouterr()
    assert "Restored" in captured.out


def test_restore_missing_file_exits(cmd, capsys):
    with pytest.raises(SystemExit):
        cmd.restore("/nonexistent/path.tar.gz")
    captured = capsys.readouterr()
    assert "Error" in captured.out


def test_list_backups_output(cmd, tmp_dir, capsys):
    cmd.manager.create_backup(str(tmp_dir / "lb1"))
    cmd.list_backups(str(tmp_dir))
    captured = capsys.readouterr()
    assert "backup" in captured.out.lower()


def test_list_backups_empty(cmd, tmp_dir, capsys):
    cmd.list_backups(str(tmp_dir))
    captured = capsys.readouterr()
    assert "No backup files found" in captured.out
