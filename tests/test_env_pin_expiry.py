"""Tests for envchain.env_pin_expiry."""

import os
import pytest
from datetime import datetime, timezone, timedelta

from envchain.env_pin_expiry import PinExpiryEntry, PinExpiryManager


FUTURE = datetime.now(timezone.utc) + timedelta(hours=1)
PAST = datetime.now(timezone.utc) - timedelta(hours=1)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def tmp_dir(tmp_path):
    return str(tmp_path)


@pytest.fixture
def manager(tmp_dir):
    return PinExpiryManager(tmp_dir)


# ---------------------------------------------------------------------------
# PinExpiryEntry unit tests
# ---------------------------------------------------------------------------

class TestPinExpiryEntry:
    def test_to_dict_contains_required_keys(self):
        entry = PinExpiryEntry(profile="dev", expires_at=FUTURE)
        d = entry.to_dict()
        assert "profile" in d
        assert "expires_at" in d

    def test_from_dict_roundtrip(self):
        entry = PinExpiryEntry(profile="dev", expires_at=FUTURE)
        restored = PinExpiryEntry.from_dict(entry.to_dict())
        assert restored.profile == entry.profile
        assert restored.expires_at == entry.expires_at

    def test_is_expired_false_for_future(self):
        entry = PinExpiryEntry(profile="dev", expires_at=FUTURE)
        assert not entry.is_expired()

    def test_is_expired_true_for_past(self):
        entry = PinExpiryEntry(profile="dev", expires_at=PAST)
        assert entry.is_expired()

    def test_seconds_remaining_positive_for_future(self):
        entry = PinExpiryEntry(profile="dev", expires_at=FUTURE)
        assert entry.seconds_remaining() > 0

    def test_seconds_remaining_zero_for_past(self):
        entry = PinExpiryEntry(profile="dev", expires_at=PAST)
        assert entry.seconds_remaining() == 0.0

    def test_repr_contains_profile(self):
        entry = PinExpiryEntry(profile="staging", expires_at=FUTURE)
        assert "staging" in repr(entry)


# ---------------------------------------------------------------------------
# PinExpiryManager tests
# ---------------------------------------------------------------------------

class TestPinExpiryManager:
    def test_set_and_get_expiry(self, manager):
        manager.set_expiry("dev", FUTURE)
        entry = manager.get_expiry("dev")
        assert entry is not None
        assert entry.profile == "dev"

    def test_get_expiry_missing_returns_none(self, manager):
        assert manager.get_expiry("nonexistent") is None

    def test_remove_expiry_returns_true(self, manager):
        manager.set_expiry("dev", FUTURE)
        assert manager.remove_expiry("dev") is True
        assert manager.get_expiry("dev") is None

    def test_remove_expiry_missing_returns_false(self, manager):
        assert manager.remove_expiry("ghost") is False

    def test_expired_profiles_lists_only_expired(self, manager):
        manager.set_expiry("old", PAST)
        manager.set_expiry("new", FUTURE)
        expired = manager.expired_profiles()
        names = [e.profile for e in expired]
        assert "old" in names
        assert "new" not in names

    def test_persistence_across_instances(self, tmp_dir):
        m1 = PinExpiryManager(tmp_dir)
        m1.set_expiry("prod", FUTURE)
        m2 = PinExpiryManager(tmp_dir)
        entry = m2.get_expiry("prod")
        assert entry is not None
        assert entry.profile == "prod"

    def test_all_entries_returns_all(self, manager):
        manager.set_expiry("a", FUTURE)
        manager.set_expiry("b", PAST)
        assert len(manager.all_entries()) == 2
