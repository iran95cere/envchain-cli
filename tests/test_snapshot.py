"""Tests for envchain.snapshot module."""

import pytest
from pathlib import Path

from envchain.snapshot import Snapshot, SnapshotManager


@pytest.fixture
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


@pytest.fixture
def manager(tmp_dir: Path) -> SnapshotManager:
    return SnapshotManager(base_dir=tmp_dir)


@pytest.fixture
def sample_snapshot() -> Snapshot:
    return Snapshot(
        profile_name="dev",
        label="before-deploy",
        variables={"API_KEY": "abc123", "DEBUG": "true"},
    )


class TestSnapshot:
    def test_to_dict_contains_required_keys(self, sample_snapshot: Snapshot):
        d = sample_snapshot.to_dict()
        assert "profile_name" in d
        assert "label" in d
        assert "variables" in d
        assert "created_at" in d

    def test_from_dict_roundtrip(self, sample_snapshot: Snapshot):
        restored = Snapshot.from_dict(sample_snapshot.to_dict())
        assert restored.profile_name == sample_snapshot.profile_name
        assert restored.label == sample_snapshot.label
        assert restored.variables == sample_snapshot.variables
        assert restored.created_at == sample_snapshot.created_at

    def test_repr_contains_profile_and_label(self, sample_snapshot: Snapshot):
        r = repr(sample_snapshot)
        assert "dev" in r
        assert "before-deploy" in r


class TestSnapshotManager:
    def test_save_creates_file(self, manager: SnapshotManager, sample_snapshot: Snapshot):
        path = manager.save(sample_snapshot)
        assert path.exists()

    def test_load_returns_snapshot(self, manager: SnapshotManager, sample_snapshot: Snapshot):
        manager.save(sample_snapshot)
        loaded = manager.load("dev", "before-deploy")
        assert loaded is not None
        assert loaded.profile_name == "dev"
        assert loaded.variables == sample_snapshot.variables

    def test_load_missing_returns_none(self, manager: SnapshotManager):
        result = manager.load("nonexistent", "ghost")
        assert result is None

    def test_list_snapshots_all(self, manager: SnapshotManager):
        manager.save(Snapshot("dev", "v1", {"A": "1"}))
        manager.save(Snapshot("prod", "v1", {"B": "2"}))
        snaps = manager.list_snapshots()
        assert len(snaps) == 2

    def test_list_snapshots_filtered_by_profile(self, manager: SnapshotManager):
        manager.save(Snapshot("dev", "v1", {"A": "1"}))
        manager.save(Snapshot("prod", "v1", {"B": "2"}))
        snaps = manager.list_snapshots(profile_name="dev")
        assert len(snaps) == 1
        assert snaps[0].profile_name == "dev"

    def test_delete_existing_snapshot(self, manager: SnapshotManager, sample_snapshot: Snapshot):
        manager.save(sample_snapshot)
        result = manager.delete("dev", "before-deploy")
        assert result is True
        assert manager.load("dev", "before-deploy") is None

    def test_delete_nonexistent_returns_false(self, manager: SnapshotManager):
        result = manager.delete("dev", "ghost")
        assert result is False

    def test_label_with_spaces_is_sanitized(self, manager: SnapshotManager):
        snap = Snapshot("dev", "my label", {"X": "1"})
        path = manager.save(snap)
        assert " " not in path.name
        loaded = manager.load("dev", "my label")
        assert loaded is not None
        assert loaded.label == "my label"
