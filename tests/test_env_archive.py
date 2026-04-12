"""Tests for envchain.env_archive and envchain.cli_archive."""
from __future__ import annotations

import json
import zipfile
from pathlib import Path

import pytest

from envchain.env_archive import ArchiveManifest, ArchiveManager
from envchain.cli_archive import ArchiveCommand


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


@pytest.fixture()
def storage_dir(tmp_dir: Path) -> Path:
    d = tmp_dir / "storage"
    d.mkdir()
    # Create two fake encrypted profile files
    (d / "dev.enc").write_bytes(b"encrypted-dev")
    (d / "prod.enc").write_bytes(b"encrypted-prod")
    return d


@pytest.fixture()
def manager(storage_dir: Path) -> ArchiveManager:
    return ArchiveManager(storage_dir)


# ── ArchiveManifest ────────────────────────────────────────────────────────────

class TestArchiveManifest:
    def test_to_dict_contains_required_keys(self):
        m = ArchiveManifest(created_at="2024-01-01T00:00:00+00:00", profiles=["dev"])
        d = m.to_dict()
        assert "version" in d
        assert "created_at" in d
        assert "profiles" in d

    def test_from_dict_roundtrip(self):
        original = ArchiveManifest(created_at="2024-06-01T12:00:00+00:00", profiles=["a", "b"])
        restored = ArchiveManifest.from_dict(original.to_dict())
        assert restored.profiles == original.profiles
        assert restored.created_at == original.created_at

    def test_repr_contains_profiles(self):
        m = ArchiveManifest(created_at="t", profiles=["x"])
        assert "x" in repr(m)


# ── ArchiveManager ─────────────────────────────────────────────────────────────

class TestArchiveManager:
    def test_create_archive_returns_path(self, manager, tmp_dir):
        dest = tmp_dir / "bundle.zip"
        result = manager.create_archive(dest)
        assert result == dest
        assert dest.exists()

    def test_create_archive_contains_manifest(self, manager, tmp_dir):
        dest = tmp_dir / "bundle.zip"
        manager.create_archive(dest)
        with zipfile.ZipFile(dest) as zf:
            names = zf.namelist()
        assert "manifest.json" in names

    def test_create_archive_contains_profile_files(self, manager, tmp_dir):
        dest = tmp_dir / "bundle.zip"
        manager.create_archive(dest, profiles=["dev"])
        with zipfile.ZipFile(dest) as zf:
            names = zf.namelist()
        assert "dev.enc" in names
        assert "prod.enc" not in names

    def test_create_archive_missing_profile_raises(self, manager, tmp_dir):
        with pytest.raises(FileNotFoundError, match="ghost"):
            manager.create_archive(tmp_dir / "x.zip", profiles=["ghost"])

    def test_restore_archive_writes_files(self, manager, tmp_dir, storage_dir):
        dest = tmp_dir / "bundle.zip"
        manager.create_archive(dest, profiles=["dev"])
        # Remove the profile then restore
        (storage_dir / "dev.enc").unlink()
        manifest = manager.restore_archive(dest)
        assert (storage_dir / "dev.enc").exists()
        assert "dev" in manifest.profiles

    def test_restore_archive_overwrite_false_raises(self, manager, tmp_dir):
        dest = tmp_dir / "bundle.zip"
        manager.create_archive(dest, profiles=["dev"])
        with pytest.raises(FileExistsError):
            manager.restore_archive(dest, overwrite=False)

    def test_restore_archive_overwrite_true_succeeds(self, manager, tmp_dir):
        dest = tmp_dir / "bundle.zip"
        manager.create_archive(dest, profiles=["dev"])
        manifest = manager.restore_archive(dest, overwrite=True)
        assert "dev" in manifest.profiles


# ── ArchiveCommand (CLI) ───────────────────────────────────────────────────────

class TestArchiveCommand:
    def test_create_prints_path(self, storage_dir, tmp_dir, capsys):
        cmd = ArchiveCommand(storage_dir)
        cmd.create(str(tmp_dir / "out.zip"))
        out = capsys.readouterr().out
        assert "Archive created" in out

    def test_restore_prints_count(self, storage_dir, tmp_dir, capsys):
        cmd = ArchiveCommand(storage_dir)
        archive = str(tmp_dir / "out.zip")
        cmd.create(archive, profiles=["dev"])
        (storage_dir / "dev.enc").unlink()
        cmd.restore(archive)
        out = capsys.readouterr().out
        assert "Restored" in out

    def test_restore_missing_archive_exits(self, storage_dir, tmp_dir):
        cmd = ArchiveCommand(storage_dir)
        with pytest.raises(SystemExit):
            cmd.restore(str(tmp_dir / "nonexistent.zip"))
