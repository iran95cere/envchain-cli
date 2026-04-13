"""Tests for envchain.env_readonly."""
from __future__ import annotations

import os
import pytest

from envchain.env_readonly import ReadOnlyEntry, ReadOnlyManager, ReadOnlyViolation


@pytest.fixture()
def tmp_dir(tmp_path):
    return str(tmp_path)


@pytest.fixture()
def manager(tmp_dir):
    return ReadOnlyManager(tmp_dir)


class TestReadOnlyEntry:
    def test_to_dict_contains_required_keys(self):
        entry = ReadOnlyEntry(var_name="SECRET", profile="prod")
        d = entry.to_dict()
        assert "var_name" in d
        assert "profile" in d
        assert "locked_at" in d
        assert "reason" in d

    def test_from_dict_roundtrip(self):
        entry = ReadOnlyEntry(var_name="API_KEY", profile="dev", reason="immutable")
        restored = ReadOnlyEntry.from_dict(entry.to_dict())
        assert restored.var_name == entry.var_name
        assert restored.profile == entry.profile
        assert restored.reason == entry.reason

    def test_repr_contains_var_and_profile(self):
        entry = ReadOnlyEntry(var_name="TOKEN", profile="staging")
        r = repr(entry)
        assert "TOKEN" in r
        assert "staging" in r

    def test_repr_contains_reason_when_set(self):
        entry = ReadOnlyEntry(var_name="X", profile="p", reason="do not change")
        assert "do not change" in repr(entry)


class TestReadOnlyManager:
    def test_protect_marks_variable(self, manager):
        manager.protect("prod", "DB_PASS")
        assert manager.is_protected("prod", "DB_PASS")

    def test_unprotect_removes_protection(self, manager):
        manager.protect("prod", "DB_PASS")
        result = manager.unprotect("prod", "DB_PASS")
        assert result is True
        assert not manager.is_protected("prod", "DB_PASS")

    def test_unprotect_returns_false_when_not_protected(self, manager):
        result = manager.unprotect("prod", "NONEXISTENT")
        assert result is False

    def test_assert_writable_raises_for_protected(self, manager):
        manager.protect("prod", "SECRET")
        with pytest.raises(ReadOnlyViolation, match="read-only"):
            manager.assert_writable("prod", "SECRET")

    def test_assert_writable_passes_for_unprotected(self, manager):
        manager.assert_writable("prod", "SAFE_VAR")  # should not raise

    def test_list_protected_returns_entries(self, manager):
        manager.protect("dev", "VAR_A")
        manager.protect("dev", "VAR_B", reason="critical")
        entries = manager.list_protected("dev")
        names = {e.var_name for e in entries}
        assert names == {"VAR_A", "VAR_B"}

    def test_list_protected_empty_for_unknown_profile(self, manager):
        assert manager.list_protected("ghost") == []

    def test_persistence_across_instances(self, tmp_dir):
        m1 = ReadOnlyManager(tmp_dir)
        m1.protect("prod", "PERSISTENT_KEY", reason="test")
        m2 = ReadOnlyManager(tmp_dir)
        assert m2.is_protected("prod", "PERSISTENT_KEY")
        entry = m2.list_protected("prod")[0]
        assert entry.reason == "test"

    def test_protect_with_reason_stored(self, manager):
        manager.protect("qa", "API_SECRET", reason="never override")
        entries = {e.var_name: e for e in manager.list_protected("qa")}
        assert entries["API_SECRET"].reason == "never override"
