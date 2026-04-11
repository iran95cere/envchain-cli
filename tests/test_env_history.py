"""Tests for envchain.env_history."""

import time
import pytest
from pathlib import Path

from envchain.env_history import HistoryEntry, HistoryManager


@pytest.fixture
def tmp_dir(tmp_path):
    return tmp_path


@pytest.fixture
def manager(tmp_dir):
    return HistoryManager(tmp_dir)


class TestHistoryEntry:
    def test_to_dict_contains_required_keys(self):
        entry = HistoryEntry(profile="dev", action="set", key="API_KEY")
        d = entry.to_dict()
        assert "profile" in d
        assert "action" in d
        assert "key" in d
        assert "timestamp" in d

    def test_from_dict_roundtrip(self):
        entry = HistoryEntry(profile="prod", action="remove", key="SECRET")
        restored = HistoryEntry.from_dict(entry.to_dict())
        assert restored.profile == entry.profile
        assert restored.action == entry.action
        assert restored.key == entry.key
        assert restored.timestamp == pytest.approx(entry.timestamp)

    def test_repr_contains_profile(self):
        entry = HistoryEntry(profile="staging", action="init", key=None)
        assert "staging" in repr(entry)

    def test_key_can_be_none(self):
        entry = HistoryEntry(profile="dev", action="init", key=None)
        assert entry.key is None
        assert entry.to_dict()["key"] is None


class TestHistoryManager:
    def test_record_creates_entry(self, manager):
        entry = manager.record("dev", "set", "MY_VAR")
        assert entry.profile == "dev"
        assert entry.action == "set"
        assert entry.key == "MY_VAR"

    def test_get_history_returns_all_entries(self, manager):
        manager.record("dev", "set", "A")
        manager.record("dev", "set", "B")
        entries = manager.get_history("dev")
        assert len(entries) == 2

    def test_get_history_empty_for_unknown_profile(self, manager):
        assert manager.get_history("nonexistent") == []

    def test_clear_history_removes_file(self, manager, tmp_dir):
        manager.record("dev", "init")
        manager.clear_history("dev")
        assert not (tmp_dir / "dev.history.json").exists()

    def test_clear_nonexistent_does_not_raise(self, manager):
        manager.clear_history("ghost")  # should not raise

    def test_last_entry_returns_most_recent(self, manager):
        manager.record("dev", "set", "FIRST")
        time.sleep(0.01)
        manager.record("dev", "set", "LAST")
        last = manager.last_entry("dev")
        assert last.key == "LAST"

    def test_last_entry_none_when_no_history(self, manager):
        assert manager.last_entry("empty") is None

    def test_multiple_profiles_are_independent(self, manager):
        manager.record("dev", "set", "X")
        manager.record("prod", "set", "Y")
        assert len(manager.get_history("dev")) == 1
        assert len(manager.get_history("prod")) == 1
