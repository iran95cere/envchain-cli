"""Tests for BackupManager."""

import os
import tarfile
from pathlib import Path

import pytest

from envchain.backup import BackupManager


@pytest.fixture
def tmp_dir(tmp_path):
    return tmp_path


@pytest.fixture
def storage_dir(tmp_dir):
    d = tmp_dir / "profiles"
    d.mkdir()
    # Create a couple of fake profile files
    (d / "dev.json").write_text('{"name": "dev"}')
    (d / "prod.json").write_text('{"name": "prod"}')
    return d


@pytest.fixture
def manager(storage_dir):
    return BackupManager(str(storage_dir))


def test_create_backup_returns_path(manager, tmp_dir):
    out = str(tmp_dir / "my_backup")
    path = manager.create_backup(out)
    assert path.endswith(".tar.gz")
    assert os.path.exists(path)


def test_create_backup_default_name(manager, tmp_dir, monkeypatch):
    monkeypatch.chdir(tmp_dir)
    path = manager.create_backup()
    assert "envchain_backup_" in path
    assert os.path.exists(path)


def test_backup_is_valid_tar(manager, tmp_dir):
    out = str(tmp_dir / "test_backup")
    path = manager.create_backup(out)
    assert tarfile.is_tarfile(path)


def test_backup_contains_profiles(manager, tmp_dir):
    out = str(tmp_dir / "test_backup")
    path = manager.create_backup(out)
    with tarfile.open(path, "r:gz") as tar:
        names = tar.getnames()
    assert any("dev.json" in n for n in names)
    assert any("prod.json" in n for n in names)


def test_restore_backup(manager, tmp_dir):
    backup_path = manager.create_backup(str(tmp_dir / "bak"))
    restore_dir = tmp_dir / "restored_profiles"
    restore_mgr = BackupManager(str(restore_dir))
    restored = restore_mgr.restore_backup(backup_path, overwrite=True)
    assert set(restored) == {"dev", "prod"}


def test_restore_no_overwrite_skips_existing(manager, tmp_dir):
    backup_path = manager.create_backup(str(tmp_dir / "bak"))
    # Restore once
    manager.restore_backup(backup_path, overwrite=True)
    # Restore again without overwrite — should skip
    restored = manager.restore_backup(backup_path, overwrite=False)
    assert restored == []


def test_restore_missing_file_raises(tmp_dir):
    mgr = BackupManager(str(tmp_dir / "profiles"))
    with pytest.raises(FileNotFoundError):
        mgr.restore_backup(str(tmp_dir / "nonexistent.tar.gz"))


def test_list_backups(manager, tmp_dir, monkeypatch):
    monkeypatch.chdir(tmp_dir)
    manager.create_backup(str(tmp_dir / "b1"))
    manager.create_backup(str(tmp_dir / "b2"))
    backups = manager.list_backups(str(tmp_dir))
    assert len(backups) == 2


def test_list_backups_empty(tmp_dir):
    mgr = BackupManager(str(tmp_dir / "profiles"))
    assert mgr.list_backups(str(tmp_dir)) == []
