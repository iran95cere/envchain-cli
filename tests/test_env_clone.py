"""Tests for envchain.env_clone."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from envchain.env_clone import CloneResult, EnvCloner
from envchain.models import Profile


def _make_profile(name: str, variables: dict) -> Profile:
    p = Profile(name=name)
    p.variables = dict(variables)
    return p


def _make_storage(profiles: dict):
    storage = MagicMock()
    storage.load_profile.side_effect = lambda n: profiles.get(n)
    storage.save_profile.return_value = None
    return storage


@pytest.fixture
def src_profile():
    return _make_profile("dev", {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET": "abc"})


@pytest.fixture
def cloner(src_profile):
    storage = _make_storage({"dev": src_profile})
    return EnvCloner(storage), storage


class TestCloneResult:
    def test_success_true_when_no_error(self):
        r = CloneResult(source_profile="a", target_profile="b")
        assert r.success is True

    def test_success_false_when_error_set(self):
        r = CloneResult(source_profile="a", target_profile="b", error="oops")
        assert r.success is False

    def test_copy_count(self):
        r = CloneResult(source_profile="a", target_profile="b", copied_vars=["X", "Y"])
        assert r.copy_count == 2

    def test_skip_count(self):
        r = CloneResult(source_profile="a", target_profile="b", skipped_vars=["Z"])
        assert r.skip_count == 1


class TestEnvCloner:
    def test_clone_missing_source_returns_error(self, cloner):
        ec, _ = cloner
        result = ec.clone("nonexistent", "staging")
        assert not result.success
        assert "not found" in result.error

    def test_clone_all_vars_to_new_profile(self, cloner, src_profile):
        ec, storage = cloner
        result = ec.clone("dev", "staging")
        assert result.success
        assert result.copy_count == 3
        assert result.skip_count == 0
        storage.save_profile.assert_called_once()

    def test_clone_with_prefix_filter(self, cloner):
        ec, _ = cloner
        result = ec.clone("dev", "staging", prefix_filter="DB_")
        assert result.success
        assert set(result.copied_vars) == {"DB_HOST", "DB_PORT"}
        assert "SECRET" in result.skipped_vars

    def test_clone_with_exclude(self, cloner):
        ec, _ = cloner
        result = ec.clone("dev", "staging", exclude=["SECRET"])
        assert "SECRET" in result.skipped_vars
        assert "DB_HOST" in result.copied_vars

    def test_clone_no_overwrite_skips_existing(self, src_profile):
        dst = _make_profile("staging", {"DB_HOST": "prod-host"})
        storage = _make_storage({"dev": src_profile, "staging": dst})
        ec = EnvCloner(storage)
        result = ec.clone("dev", "staging", overwrite=False)
        assert "DB_HOST" in result.skipped_vars

    def test_clone_overwrite_replaces_existing(self, src_profile):
        dst = _make_profile("staging", {"DB_HOST": "prod-host"})
        storage = _make_storage({"dev": src_profile, "staging": dst})
        ec = EnvCloner(storage)
        result = ec.clone("dev", "staging", overwrite=True)
        assert "DB_HOST" in result.copied_vars
