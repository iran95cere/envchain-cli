"""Tests for envchain.env_changelog."""
import json
import time
import pytest
from pathlib import Path
from envchain.env_changelog import ChangeEntry, ChangelogManager


@pytest.fixture
def tmp_dir(tmp_path):
    return str(tmp_path)


@pytest.fixture
def manager(tmp_dir):
    return ChangelogManager(tmp_dir)


class TestChangeEntry:
    def test_to_dict_contains_required_keys(self):
        e = ChangeEntry(profile="dev", var_name="FOO", action="set",
                        old_value=None, new_value="bar")
        d = e.to_dict()
        assert "profile" in d
        assert "var_name" in d
        assert "action" in d
        assert "timestamp" in d

    def test_from_dict_roundtrip(self):
        e = ChangeEntry(profile="prod", var_name="BAR", action="delete",
                        old_value="old", new_value=None, timestamp=1234.0)
        restored = ChangeEntry.from_dict(e.to_dict())
        assert restored.profile == "prod"
        assert restored.var_name == "BAR"
        assert restored.action == "delete"
        assert restored.old_value == "old"
        assert restored.new_value is None
        assert restored.timestamp == 1234.0

    def test_repr_contains_profile_and_var(self):
        e = ChangeEntry(profile="dev", var_name="X", action="set",
                        old_value=None, new_value="1")
        r = repr(e)
        assert "dev" in r
        assert "X" in r
        assert "set" in r


class TestChangelogManager:
    def test_record_creates_entry(self, manager):
        entry = manager.record("dev", "FOO", "set", new_value="bar")
        assert entry.var_name == "FOO"
        assert entry.action == "set"

    def test_record_invalid_action_raises(self, manager):
        with pytest.raises(ValueError, match="Invalid action"):
            manager.record("dev", "X", "explode")

    def test_entries_for_profile_filters(self, manager):
        manager.record("dev", "A", "set", new_value="1")
        manager.record("prod", "B", "set", new_value="2")
        dev_entries = manager.entries_for_profile("dev")
        assert all(e.profile == "dev" for e in dev_entries)
        assert len(dev_entries) == 1

    def test_all_entries_returns_all(self, manager):
        manager.record("dev", "A", "set", new_value="1")
        manager.record("prod", "B", "delete", old_value="2")
        assert len(manager.all_entries()) == 2

    def test_clear_all(self, manager):
        manager.record("dev", "A", "set", new_value="1")
        manager.record("prod", "B", "set", new_value="2")
        removed = manager.clear()
        assert removed == 2
        assert manager.all_entries() == []

    def test_clear_by_profile(self, manager):
        manager.record("dev", "A", "set", new_value="1")
        manager.record("prod", "B", "set", new_value="2")
        removed = manager.clear(profile="dev")
        assert removed == 1
        remaining = manager.all_entries()
        assert len(remaining) == 1
        assert remaining[0].profile == "prod"

    def test_persistence(self, tmp_dir):
        m1 = ChangelogManager(tmp_dir)
        m1.record("dev", "KEY", "rename", old_value="OLD", new_value="NEW")
        m2 = ChangelogManager(tmp_dir)
        entries = m2.all_entries()
        assert len(entries) == 1
        assert entries[0].var_name == "KEY"
