"""Tests for envchain.env_ttl module."""

from __future__ import annotations

import os
import time
from datetime import datetime, timedelta, timezone

import pytest

from envchain.env_ttl import TTLEntry, TTLManager


@pytest.fixture
def tmp_dir(tmp_path):
    return str(tmp_path)


@pytest.fixture
def manager(tmp_dir):
    return TTLManager(tmp_dir)


# --- TTLEntry unit tests ---

class TestTTLEntry:
    def test_to_dict_contains_required_keys(self):
        entry = TTLEntry(
            profile_name="dev",
            expires_at=datetime.now(timezone.utc) + timedelta(seconds=60),
        )
        d = entry.to_dict()
        assert "profile_name" in d
        assert "expires_at" in d
        assert "created_at" in d

    def test_from_dict_roundtrip(self):
        entry = TTLEntry(
            profile_name="prod",
            expires_at=datetime.now(timezone.utc) + timedelta(seconds=120),
        )
        restored = TTLEntry.from_dict(entry.to_dict())
        assert restored.profile_name == entry.profile_name
        assert abs((restored.expires_at - entry.expires_at).total_seconds()) < 1

    def test_is_expired_false_for_future(self):
        entry = TTLEntry(
            profile_name="dev",
            expires_at=datetime.now(timezone.utc) + timedelta(seconds=300),
        )
        assert not entry.is_expired()

    def test_is_expired_true_for_past(self):
        entry = TTLEntry(
            profile_name="dev",
            expires_at=datetime.now(timezone.utc) - timedelta(seconds=1),
        )
        assert entry.is_expired()

    def test_seconds_remaining_positive(self):
        entry = TTLEntry(
            profile_name="dev",
            expires_at=datetime.now(timezone.utc) + timedelta(seconds=100),
        )
        assert entry.seconds_remaining() > 0

    def test_seconds_remaining_zero_when_expired(self):
        entry = TTLEntry(
            profile_name="dev",
            expires_at=datetime.now(timezone.utc) - timedelta(seconds=10),
        )
        assert entry.seconds_remaining() == 0.0

    def test_repr_contains_profile_name(self):
        entry = TTLEntry(
            profile_name="staging",
            expires_at=datetime.now(timezone.utc) + timedelta(seconds=60),
        )
        assert "staging" in repr(entry)


# --- TTLManager integration tests ---

def test_set_and_get_ttl(manager):
    entry = manager.set_ttl("dev", 300)
    fetched = manager.get_ttl("dev")
    assert fetched is not None
    assert fetched.profile_name == "dev"
    assert not fetched.is_expired()


def test_set_ttl_invalid_seconds_raises(manager):
    with pytest.raises(ValueError):
        manager.set_ttl("dev", 0)
    with pytest.raises(ValueError):
        manager.set_ttl("dev", -5)


def test_get_ttl_missing_returns_none(manager):
    assert manager.get_ttl("nonexistent") is None


def test_remove_ttl_returns_true(manager):
    manager.set_ttl("dev", 60)
    assert manager.remove_ttl("dev") is True
    assert manager.get_ttl("dev") is None


def test_remove_ttl_missing_returns_false(manager):
    assert manager.remove_ttl("ghost") is False


def test_purge_expired_removes_only_expired(manager):
    manager.set_ttl("active", 300)
    expired_entry = TTLEntry(
        profile_name="old",
        expires_at=datetime.now(timezone.utc) - timedelta(seconds=1),
    )
    manager._entries["old"] = expired_entry
    manager._save()

    purged = manager.purge_expired()
    assert "old" in purged
    assert "active" not in purged
    assert manager.get_ttl("active") is not None
    assert manager.get_ttl("old") is None


def test_persistence_across_instances(tmp_dir):
    m1 = TTLManager(tmp_dir)
    m1.set_ttl("dev", 500)
    m2 = TTLManager(tmp_dir)
    entry = m2.get_ttl("dev")
    assert entry is not None
    assert entry.profile_name == "dev"
