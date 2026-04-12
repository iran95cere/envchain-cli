"""Tests for env_expiry module and ExpiryCommand CLI."""
from __future__ import annotations

import time
import pytest
from envchain.env_expiry import ExpiryEntry, ExpiryManager
from envchain.cli_expiry import ExpiryCommand


# --- ExpiryEntry ---

class TestExpiryEntry:
    def test_to_dict_contains_required_keys(self):
        entry = ExpiryEntry(var_name="KEY", profile="dev", expires_at=time.time() + 60)
        d = entry.to_dict()
        assert "var_name" in d
        assert "profile" in d
        assert "expires_at" in d
        assert "created_at" in d

    def test_from_dict_roundtrip(self):
        entry = ExpiryEntry(var_name="KEY", profile="dev", expires_at=time.time() + 60)
        restored = ExpiryEntry.from_dict(entry.to_dict())
        assert restored.var_name == entry.var_name
        assert restored.profile == entry.profile
        assert restored.expires_at == pytest.approx(entry.expires_at)

    def test_is_expired_false_for_future(self):
        entry = ExpiryEntry(var_name="K", profile="p", expires_at=time.time() + 100)
        assert not entry.is_expired()

    def test_is_expired_true_for_past(self):
        entry = ExpiryEntry(var_name="K", profile="p", expires_at=time.time() - 1)
        assert entry.is_expired()

    def test_seconds_remaining_positive(self):
        entry = ExpiryEntry(var_name="K", profile="p", expires_at=time.time() + 50)
        assert entry.seconds_remaining() > 0

    def test_seconds_remaining_zero_when_expired(self):
        entry = ExpiryEntry(var_name="K", profile="p", expires_at=time.time() - 10)
        assert entry.seconds_remaining() == 0.0

    def test_repr_contains_profile_and_var(self):
        entry = ExpiryEntry(var_name="MY_VAR", profile="prod", expires_at=time.time() + 10)
        r = repr(entry)
        assert "prod" in r
        assert "MY_VAR" in r


# --- ExpiryManager ---

@pytest.fixture
def manager():
    return ExpiryManager()


class TestExpiryManager:
    def test_set_and_get_entry(self, manager):
        manager.set_expiry("dev", "TOKEN", 60)
        entry = manager.get_entry("dev", "TOKEN")
        assert entry is not None
        assert entry.var_name == "TOKEN"

    def test_set_zero_ttl_raises(self, manager):
        with pytest.raises(ValueError):
            manager.set_expiry("dev", "X", 0)

    def test_set_negative_ttl_raises(self, manager):
        with pytest.raises(ValueError):
            manager.set_expiry("dev", "X", -5)

    def test_is_expired_false_for_fresh_entry(self, manager):
        manager.set_expiry("dev", "A", 100)
        assert not manager.is_expired("dev", "A")

    def test_is_expired_false_when_no_entry(self, manager):
        assert not manager.is_expired("dev", "MISSING")

    def test_remove_returns_true(self, manager):
        manager.set_expiry("dev", "B", 10)
        assert manager.remove("dev", "B") is True

    def test_remove_returns_false_when_missing(self, manager):
        assert manager.remove("dev", "NONE") is False

    def test_purge_expired_removes_and_returns(self, manager):
        manager._entries["dev/OLD"] = ExpiryEntry("OLD", "dev", time.time() - 5)
        manager.set_expiry("dev", "FRESH", 100)
        purged = manager.purge_expired()
        assert len(purged) == 1
        assert purged[0].var_name == "OLD"
        assert manager.get_entry("dev", "FRESH") is not None

    def test_all_entries_returns_all(self, manager):
        manager.set_expiry("dev", "A", 10)
        manager.set_expiry("prod", "B", 20)
        assert len(manager.all_entries()) == 2


# --- ExpiryCommand ---

@pytest.fixture
def cmd():
    return ExpiryCommand(ExpiryManager())


class TestExpiryCommand:
    def test_set_prints_confirmation(self, cmd, capsys):
        cmd.set("dev", "API_KEY", 300)
        out = capsys.readouterr().out
        assert "API_KEY" in out
        assert "300" in out

    def test_set_invalid_ttl_exits(self, cmd):
        with pytest.raises(SystemExit):
            cmd.set("dev", "X", -1)

    def test_status_no_entry(self, cmd, capsys):
        cmd.status("dev", "MISSING")
        out = capsys.readouterr().out
        assert "No expiry" in out

    def test_status_active_entry(self, cmd, capsys):
        cmd.set("dev", "K", 500)
        cmd.status("dev", "K")
        out = capsys.readouterr().out
        assert "remaining" in out

    def test_list_entries_empty(self, cmd, capsys):
        cmd.list_entries()
        out = capsys.readouterr().out
        assert "No expiry" in out

    def test_purge_no_expired(self, cmd, capsys):
        cmd.set("dev", "ALIVE", 100)
        cmd.purge()
        out = capsys.readouterr().out
        assert "No expired" in out

    def test_remove_existing(self, cmd, capsys):
        cmd.set("dev", "Z", 60)
        cmd.remove("dev", "Z")
        out = capsys.readouterr().out
        assert "Removed" in out

    def test_remove_missing_exits(self, cmd):
        with pytest.raises(SystemExit):
            cmd.remove("dev", "GHOST")
