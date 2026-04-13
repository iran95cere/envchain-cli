"""Tests for envchain.env_signature."""
from __future__ import annotations

import pytest

from envchain.env_signature import SignatureEntry, SignatureManager, VerifyResult


@pytest.fixture
def manager():
    return SignatureManager(secret_key="test-secret")


class TestSignatureEntry:
    def test_to_dict_contains_required_keys(self):
        entry = SignatureEntry("dev", "abc123", "sha256", "2024-01-01T00:00:00+00:00")
        d = entry.to_dict()
        assert "profile_name" in d
        assert "signature" in d
        assert "algorithm" in d
        assert "signed_at" in d

    def test_from_dict_roundtrip(self):
        original = SignatureEntry("dev", "abc123", "sha256", "2024-01-01T00:00:00+00:00")
        restored = SignatureEntry.from_dict(original.to_dict())
        assert restored.profile_name == original.profile_name
        assert restored.signature == original.signature
        assert restored.algorithm == original.algorithm

    def test_repr_contains_profile_and_algo(self):
        entry = SignatureEntry("prod", "sig", "sha256", "ts")
        r = repr(entry)
        assert "prod" in r
        assert "sha256" in r


class TestVerifyResult:
    def test_bool_true_when_valid(self):
        result = VerifyResult("dev", True)
        assert bool(result) is True

    def test_bool_false_when_invalid(self):
        result = VerifyResult("dev", False, "mismatch")
        assert bool(result) is False

    def test_repr_contains_status(self):
        r = repr(VerifyResult("dev", True))
        assert "valid" in r


class TestSignatureManager:
    def test_sign_returns_entry(self, manager):
        entry = manager.sign("dev", {"KEY": "value"})
        assert entry.profile_name == "dev"
        assert entry.algorithm == "sha256"
        assert len(entry.signature) == 64  # sha256 hex

    def test_verify_valid_after_sign(self, manager):
        vars_dict = {"A": "1", "B": "2"}
        manager.sign("dev", vars_dict)
        result = manager.verify("dev", vars_dict)
        assert result.valid is True

    def test_verify_fails_when_vars_changed(self, manager):
        manager.sign("dev", {"A": "1"})
        result = manager.verify("dev", {"A": "tampered"})
        assert result.valid is False
        assert "mismatch" in result.reason

    def test_verify_fails_when_not_signed(self, manager):
        result = manager.verify("unknown", {})
        assert result.valid is False
        assert "no signature" in result.reason

    def test_remove_returns_true_when_existed(self, manager):
        manager.sign("dev", {})
        assert manager.remove("dev") is True

    def test_remove_returns_false_when_missing(self, manager):
        assert manager.remove("ghost") is False

    def test_list_signed_empty_initially(self, manager):
        assert manager.list_signed() == []

    def test_list_signed_after_sign(self, manager):
        manager.sign("dev", {})
        manager.sign("prod", {})
        names = manager.list_signed()
        assert "dev" in names
        assert "prod" in names

    def test_empty_secret_key_raises(self):
        with pytest.raises(ValueError):
            SignatureManager("")

    def test_different_keys_produce_different_signatures(self):
        m1 = SignatureManager("key-one")
        m2 = SignatureManager("key-two")
        e1 = m1.sign("dev", {"X": "1"})
        e2 = m2.sign("dev", {"X": "1"})
        assert e1.signature != e2.signature
