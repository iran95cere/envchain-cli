"""Tests for envchain.env_copy."""
from __future__ import annotations

import pytest
from unittest.mock import MagicMock

from envchain.env_copy import CopyResult, EnvCopier
from envchain.models import Profile


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _profile(name: str, vars_: dict) -> Profile:
    p = Profile(name=name)
    for k, v in vars_.items():
        p.add_var(k, v)
    return p


def _make_storage(profiles: dict):
    """Return a mock storage whose load/save behave realistically."""
    store = MagicMock()
    store.load_profile.side_effect = lambda name, pwd: profiles.get(name)
    store.save_profile.return_value = None
    return store


# ---------------------------------------------------------------------------
# CopyResult unit tests
# ---------------------------------------------------------------------------

class TestCopyResult:
    def test_copy_count(self):
        r = CopyResult(copied={"A": "1", "B": "2"}, source_profile="s", target_profile="t")
        assert r.copy_count == 2

    def test_skip_count(self):
        r = CopyResult(skipped=["X", "Y"], source_profile="s", target_profile="t")
        assert r.skip_count == 2

    def test_has_skipped_false_when_empty(self):
        r = CopyResult()
        assert r.has_skipped is False

    def test_has_skipped_true(self):
        r = CopyResult(skipped=["FOO"])
        assert r.has_skipped is True

    def test_repr_contains_profile_names(self):
        r = CopyResult(source_profile="dev", target_profile="prod")
        assert "dev" in repr(r)
        assert "prod" in repr(r)


# ---------------------------------------------------------------------------
# EnvCopier tests
# ---------------------------------------------------------------------------

class TestEnvCopier:
    def test_copy_all_vars(self):
        src = _profile("src", {"DB": "postgres", "PORT": "5432"})
        tgt = _profile("tgt", {})
        storage = _make_storage({"src": src, "tgt": tgt})
        copier = EnvCopier(storage)

        result = copier.copy("src", "tgt", password="pw")

        assert result.copy_count == 2
        assert result.skip_count == 0
        storage.save_profile.assert_called_once()

    def test_copy_specific_keys(self):
        src = _profile("src", {"DB": "postgres", "PORT": "5432", "SECRET": "xyz"})
        tgt = _profile("tgt", {})
        storage = _make_storage({"src": src, "tgt": tgt})
        copier = EnvCopier(storage)

        result = copier.copy("src", "tgt", password="pw", keys=["DB"])

        assert result.copy_count == 1
        assert "DB" in result.copied

    def test_copy_with_prefix_filter(self):
        src = _profile("src", {"APP_HOST": "localhost", "APP_PORT": "8080", "OTHER": "val"})
        tgt = _profile("tgt", {})
        storage = _make_storage({"src": src, "tgt": tgt})
        copier = EnvCopier(storage)

        result = copier.copy("src", "tgt", password="pw", prefix="APP_")

        assert result.copy_count == 2
        assert "OTHER" not in result.copied

    def test_no_overwrite_skips_existing(self):
        src = _profile("src", {"KEY": "new_value"})
        tgt = _profile("tgt", {"KEY": "old_value"})
        storage = _make_storage({"src": src, "tgt": tgt})
        copier = EnvCopier(storage)

        result = copier.copy("src", "tgt", password="pw", overwrite=False)

        assert result.skip_count == 1
        assert "KEY" in result.skipped
        storage.save_profile.assert_not_called()

    def test_overwrite_replaces_existing(self):
        src = _profile("src", {"KEY": "new_value"})
        tgt = _profile("tgt", {"KEY": "old_value"})
        storage = _make_storage({"src": src, "tgt": tgt})
        copier = EnvCopier(storage)

        result = copier.copy("src", "tgt", password="pw", overwrite=True)

        assert result.copy_count == 1
        assert result.skip_count == 0

    def test_missing_source_raises(self):
        storage = _make_storage({})
        copier = EnvCopier(storage)
        with pytest.raises(ValueError, match="Source profile"):
            copier.copy("missing", "tgt", password="pw")

    def test_missing_target_raises(self):
        src = _profile("src", {"A": "1"})
        storage = _make_storage({"src": src})
        copier = EnvCopier(storage)
        with pytest.raises(ValueError, match="Target profile"):
            copier.copy("src", "missing", password="pw")
