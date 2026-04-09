"""Tests for envchain.rotation."""

from __future__ import annotations

import pytest

from envchain.models import Profile
from envchain.rotation import PasswordRotator, RotationRecord


# ---------------------------------------------------------------------------
# RotationRecord
# ---------------------------------------------------------------------------

class TestRotationRecord:
    def test_to_dict_contains_required_keys(self):
        rec = RotationRecord(profile_name="dev", note="quarterly")
        d = rec.to_dict()
        assert d["profile_name"] == "dev"
        assert d["note"] == "quarterly"
        assert "rotated_at" in d

    def test_from_dict_roundtrip(self):
        rec = RotationRecord(profile_name="prod")
        restored = RotationRecord.from_dict(rec.to_dict())
        assert restored.profile_name == rec.profile_name
        assert restored.rotated_at == rec.rotated_at
        assert restored.note is None

    def test_repr_contains_profile_name(self):
        rec = RotationRecord(profile_name="staging")
        assert "staging" in repr(rec)


# ---------------------------------------------------------------------------
# PasswordRotator
# ---------------------------------------------------------------------------

class _FakeStorage:
    """Minimal in-memory storage stub."""

    def __init__(self):
        self._store: dict = {}

    def save_profile(self, profile: Profile, password: str) -> None:
        self._store[profile.name] = (profile, password)

    def load_profile(self, name: str, password: str):
        entry = self._store.get(name)
        if entry is None:
            return None
        profile, stored_pw = entry
        if stored_pw != password:
            raise ValueError("Wrong password")
        return profile


@pytest.fixture()
def fake_storage():
    return _FakeStorage()


@pytest.fixture()
def rotator(fake_storage):
    return PasswordRotator(fake_storage)


class TestPasswordRotator:
    def test_rotate_success(self, fake_storage, rotator):
        profile = Profile(name="dev")
        fake_storage.save_profile(profile, "old")
        record = rotator.rotate("dev", "old", "new")
        assert record.profile_name == "dev"
        # Must be loadable with new password
        assert fake_storage.load_profile("dev", "new") is not None

    def test_rotate_nonexistent_profile_raises(self, rotator):
        with pytest.raises(ValueError, match="not found"):
            rotator.rotate("ghost", "old", "new")

    def test_rotate_wrong_old_password_raises(self, fake_storage, rotator):
        profile = Profile(name="dev")
        fake_storage.save_profile(profile, "correct")
        with pytest.raises(Exception):
            rotator.rotate("dev", "wrong", "new")

    def test_bulk_rotate_returns_all_records(self, fake_storage, rotator):
        for name in ("a", "b", "c"):
            fake_storage.save_profile(Profile(name=name), "old")
        records = rotator.bulk_rotate(["a", "b", "c"], "old", "new")
        assert len(records) == 3
        assert {r.profile_name for r in records} == {"a", "b", "c"}

    def test_rotate_with_note(self, fake_storage, rotator):
        fake_storage.save_profile(Profile(name="dev"), "old")
        record = rotator.rotate("dev", "old", "new", note="security audit")
        assert record.note == "security audit"
