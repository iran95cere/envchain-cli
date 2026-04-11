"""Tests for envchain.env_lock."""
from __future__ import annotations

import json
import pytest
from pathlib import Path

from envchain.env_lock import LockEntry, LockManager


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


@pytest.fixture()
def manager(tmp_dir: Path) -> LockManager:
    return LockManager(str(tmp_dir))


class TestLockEntry:
    def test_to_dict_contains_required_keys(self):
        e = LockEntry(profile="prod")
        d = e.to_dict()
        assert "profile" in d and "locked_at" in d and "reason" in d

    def test_from_dict_roundtrip(self):
        e = LockEntry(profile="dev", reason="freeze")
        assert LockEntry.from_dict(e.to_dict()).reason == "freeze"

    def test_repr_contains_profile(self):
        assert "staging" in repr(LockEntry(profile="staging"))


class TestLockManager:
    def test_lock_creates_entry(self, manager: LockManager):
        entry = manager.lock("prod")
        assert entry.profile == "prod"
        assert manager.is_locked("prod")

    def test_lock_with_reason(self, manager: LockManager):
        manager.lock("prod", reason="deploy freeze")
        assert manager.get_entry("prod").reason == "deploy freeze"

    def test_unlock_removes_entry(self, manager: LockManager):
        manager.lock("prod")
        result = manager.unlock("prod")
        assert result is True
        assert not manager.is_locked("prod")

    def test_unlock_returns_false_when_not_locked(self, manager: LockManager):
        assert manager.unlock("ghost") is False

    def test_get_entry_returns_none_when_missing(self, manager: LockManager):
        assert manager.get_entry("missing") is None

    def test_list_locked_empty(self, manager: LockManager):
        assert manager.list_locked() == []

    def test_list_locked_returns_all(self, manager: LockManager):
        manager.lock("a")
        manager.lock("b")
        names = {e.profile for e in manager.list_locked()}
        assert names == {"a", "b"}

    def test_persists_across_instances(self, tmp_dir: Path):
        m1 = LockManager(str(tmp_dir))
        m1.lock("prod")
        m2 = LockManager(str(tmp_dir))
        assert m2.is_locked("prod")

    def test_unlock_persists_across_instances(self, tmp_dir: Path):
        m1 = LockManager(str(tmp_dir))
        m1.lock("prod")
        m1.unlock("prod")
        m2 = LockManager(str(tmp_dir))
        assert not m2.is_locked("prod")
