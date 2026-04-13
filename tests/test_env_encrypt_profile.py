"""Tests for env_encrypt_profile module."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from envchain.env_encrypt_profile import (
    ProfileReEncryptor,
    ReEncryptReport,
    ReEncryptResult,
)
from envchain.models import Profile


def _make_profile(name: str, vars_: dict) -> Profile:
    p = Profile(name=name)
    for k, v in vars_.items():
        p.add_var(k, v)
    return p


def _make_storage(profiles: dict):
    storage = MagicMock()
    storage.list_profiles.return_value = list(profiles.keys())

    def load_profile(name, password):
        if name not in profiles:
            return None
        return profiles[name]

    storage.load_profile.side_effect = load_profile
    storage.save_profile.return_value = None
    return storage


@pytest.fixture()
def sample_profile():
    return _make_profile("dev", {"KEY": "value", "TOKEN": "abc"})


@pytest.fixture()
def storage(sample_profile):
    return _make_storage({"dev": sample_profile})


@pytest.fixture()
def encryptor(storage):
    return ProfileReEncryptor(storage)


class TestReEncryptResult:
    def test_repr_success(self):
        r = ReEncryptResult(profile_name="dev", success=True, vars_processed=3)
        assert "dev" in repr(r)
        assert "ok" in repr(r)

    def test_repr_failure(self):
        r = ReEncryptResult(profile_name="dev", success=False, error="bad password")
        assert "error" in repr(r)


class TestReEncryptReport:
    def test_success_count(self):
        report = ReEncryptReport(
            results=[
                ReEncryptResult("a", True, 2),
                ReEncryptResult("b", False, error="oops"),
            ]
        )
        assert report.success_count == 1
        assert report.failure_count == 1

    def test_has_failures_false_when_all_ok(self):
        report = ReEncryptReport(results=[ReEncryptResult("a", True, 1)])
        assert not report.has_failures

    def test_has_failures_true_when_any_fail(self):
        report = ReEncryptReport(
            results=[ReEncryptResult("a", False, error="err")]
        )
        assert report.has_failures

    def test_repr_contains_counts(self):
        report = ReEncryptReport()
        assert "total=0" in repr(report)


class TestProfileReEncryptor:
    def test_re_encrypt_success(self, encryptor, storage):
        result = encryptor.re_encrypt("dev", "old", "new")
        assert result.success
        assert result.vars_processed == 2
        storage.save_profile.assert_called_once()

    def test_re_encrypt_missing_profile(self, encryptor):
        result = encryptor.re_encrypt("missing", "old", "new")
        assert not result.success
        assert "not found" in result.error

    def test_re_encrypt_storage_error(self, storage):
        storage.load_profile.side_effect = RuntimeError("disk error")
        enc = ProfileReEncryptor(storage)
        result = enc.re_encrypt("dev", "old", "new")
        assert not result.success
        assert "disk error" in result.error

    def test_re_encrypt_all_returns_report(self, encryptor):
        report = encryptor.re_encrypt_all(["dev"], "old", "new")
        assert isinstance(report, ReEncryptReport)
        assert len(report.results) == 1
