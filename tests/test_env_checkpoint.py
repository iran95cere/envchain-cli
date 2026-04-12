"""Tests for CheckpointManager and CheckpointCommand."""

from __future__ import annotations

import pytest
from pathlib import Path

from envchain.env_checkpoint import Checkpoint, CheckpointManager
from envchain.cli_checkpoint import CheckpointCommand


@pytest.fixture
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


@pytest.fixture
def manager(tmp_dir: Path) -> CheckpointManager:
    return CheckpointManager(tmp_dir)


@pytest.fixture
def cmd(tmp_dir: Path) -> CheckpointCommand:
    return CheckpointCommand(tmp_dir)


class TestCheckpoint:
    def test_to_dict_contains_required_keys(self):
        cp = Checkpoint(name="v1", profile="dev", vars={"A": "1"})
        d = cp.to_dict()
        assert {"name", "profile", "vars", "created_at", "description"} <= d.keys()

    def test_from_dict_roundtrip(self):
        cp = Checkpoint(name="v1", profile="dev", vars={"A": "1"}, description="first")
        restored = Checkpoint.from_dict(cp.to_dict())
        assert restored.name == cp.name
        assert restored.profile == cp.profile
        assert restored.vars == cp.vars
        assert restored.description == cp.description

    def test_repr_contains_name_and_profile(self):
        cp = Checkpoint(name="snap", profile="prod", vars={})
        r = repr(cp)
        assert "snap" in r
        assert "prod" in r


class TestCheckpointManager:
    def test_save_and_load(self, manager: CheckpointManager):
        cp = Checkpoint(name="v1", profile="dev", vars={"X": "42"})
        manager.save(cp)
        loaded = manager.load("dev", "v1")
        assert loaded is not None
        assert loaded.vars == {"X": "42"}

    def test_load_nonexistent_returns_none(self, manager: CheckpointManager):
        assert manager.load("dev", "ghost") is None

    def test_save_overwrites_same_name(self, manager: CheckpointManager):
        cp1 = Checkpoint(name="v1", profile="dev", vars={"A": "old"})
        cp2 = Checkpoint(name="v1", profile="dev", vars={"A": "new"})
        manager.save(cp1)
        manager.save(cp2)
        loaded = manager.load("dev", "v1")
        assert loaded.vars["A"] == "new"
        assert len(manager.list_checkpoints("dev")) == 1

    def test_list_checkpoints_empty(self, manager: CheckpointManager):
        assert manager.list_checkpoints("dev") == []

    def test_list_checkpoints_multiple(self, manager: CheckpointManager):
        for name in ("v1", "v2", "v3"):
            manager.save(Checkpoint(name=name, profile="dev", vars={}))
        names = [c.name for c in manager.list_checkpoints("dev")]
        assert sorted(names) == ["v1", "v2", "v3"]

    def test_delete_existing(self, manager: CheckpointManager):
        manager.save(Checkpoint(name="v1", profile="dev", vars={}))
        assert manager.delete("dev", "v1") is True
        assert manager.load("dev", "v1") is None

    def test_delete_nonexistent_returns_false(self, manager: CheckpointManager):
        assert manager.delete("dev", "ghost") is False

    def test_persists_across_instances(self, tmp_dir: Path):
        m1 = CheckpointManager(tmp_dir)
        m1.save(Checkpoint(name="snap", profile="prod", vars={"K": "V"}))
        m2 = CheckpointManager(tmp_dir)
        loaded = m2.load("prod", "snap")
        assert loaded is not None
        assert loaded.vars == {"K": "V"}


class TestCheckpointCommand:
    def test_save_prints_confirmation(self, cmd: CheckpointCommand, capsys):
        cmd.save("dev", "v1", {"A": "1"})
        out = capsys.readouterr().out
        assert "v1" in out
        assert "dev" in out

    def test_restore_returns_vars(self, cmd: CheckpointCommand):
        cmd.save("dev", "v1", {"DB": "localhost"})
        vars_ = cmd.restore("dev", "v1")
        assert vars_["DB"] == "localhost"

    def test_restore_missing_exits(self, cmd: CheckpointCommand):
        with pytest.raises(SystemExit):
            cmd.restore("dev", "nonexistent")

    def test_list_empty_prints_message(self, cmd: CheckpointCommand, capsys):
        cmd.list_checkpoints("dev")
        assert "No checkpoints" in capsys.readouterr().out

    def test_delete_missing_exits(self, cmd: CheckpointCommand):
        with pytest.raises(SystemExit):
            cmd.delete("dev", "ghost")
