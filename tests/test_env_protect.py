"""Tests for envchain.env_protect."""
import pytest
import os
from envchain.env_protect import ProtectEntry, ProtectViolation, ProtectManager


@pytest.fixture()
def tmp_dir(tmp_path):
    return str(tmp_path)


@pytest.fixture()
def manager(tmp_dir):
    return ProtectManager(tmp_dir)


class TestProtectEntry:
    def test_to_dict_contains_required_keys(self):
        e = ProtectEntry(profile="dev", var_name="SECRET", reason="critical")
        d = e.to_dict()
        assert d["profile"] == "dev"
        assert d["var_name"] == "SECRET"
        assert d["reason"] == "critical"

    def test_from_dict_roundtrip(self):
        e = ProtectEntry(profile="prod", var_name="DB_PASS", reason="")
        assert ProtectEntry.from_dict(e.to_dict()) == e

    def test_from_dict_missing_reason_defaults_empty(self):
        e = ProtectEntry.from_dict({"profile": "dev", "var_name": "X"})
        assert e.reason == ""

    def test_repr_contains_profile_and_var(self):
        e = ProtectEntry(profile="dev", var_name="SECRET")
        assert "dev" in repr(e)
        assert "SECRET" in repr(e)


class TestProtectViolation:
    def test_repr_contains_action_and_var(self):
        v = ProtectViolation(profile="dev", var_name="TOKEN", action="delete")
        assert "delete" in repr(v)
        assert "TOKEN" in repr(v)


class TestProtectManager:
    def test_protect_and_is_protected(self, manager):
        manager.protect("dev", "SECRET")
        assert manager.is_protected("dev", "SECRET")

    def test_unprotect_removes_entry(self, manager):
        manager.protect("dev", "SECRET")
        removed = manager.unprotect("dev", "SECRET")
        assert removed is True
        assert not manager.is_protected("dev", "SECRET")

    def test_unprotect_nonexistent_returns_false(self, manager):
        assert manager.unprotect("dev", "GHOST") is False

    def test_list_protected_returns_entries(self, manager):
        manager.protect("dev", "A")
        manager.protect("dev", "B")
        names = {e.var_name for e in manager.list_protected("dev")}
        assert names == {"A", "B"}

    def test_list_protected_empty_profile(self, manager):
        assert manager.list_protected("missing") == []

    def test_check_overwrite_returns_violation(self, manager):
        manager.protect("dev", "KEY")
        v = manager.check_overwrite("dev", "KEY")
        assert v is not None
        assert v.action == "overwrite"

    def test_check_overwrite_unprotected_returns_none(self, manager):
        assert manager.check_overwrite("dev", "FREE") is None

    def test_check_delete_returns_violation(self, manager):
        manager.protect("dev", "KEY")
        v = manager.check_delete("dev", "KEY")
        assert v is not None
        assert v.action == "delete"

    def test_persistence_across_instances(self, tmp_dir):
        m1 = ProtectManager(tmp_dir)
        m1.protect("dev", "PERSIST", reason="test")
        m2 = ProtectManager(tmp_dir)
        assert m2.is_protected("dev", "PERSIST")
        entry = m2.list_protected("dev")[0]
        assert entry.reason == "test"
