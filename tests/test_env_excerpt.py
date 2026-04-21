"""Tests for envchain.env_excerpt."""
from __future__ import annotations

import pytest

from envchain.env_excerpt import EnvExcerpt, ExcerptResult


@pytest.fixture
def excerptr() -> EnvExcerpt:
    return EnvExcerpt()


@pytest.fixture
def sample_vars() -> dict:
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "API_KEY": "secret",
        "API_SECRET": "topsecret",
        "DEBUG": "true",
    }


class TestExcerptResult:
    def test_extract_count(self, sample_vars):
        result = ExcerptResult(
            name="dev",
            original=sample_vars,
            extracted={"DB_HOST": "localhost"},
            keys_requested=["DB_HOST"],
        )
        assert result.extract_count == 1

    def test_missing_keys_empty_when_all_found(self, sample_vars):
        result = ExcerptResult(
            name="dev",
            original=sample_vars,
            extracted={"DB_HOST": "localhost"},
            keys_requested=["DB_HOST"],
        )
        assert result.missing_keys == []

    def test_missing_keys_reports_absent_literal(self, sample_vars):
        result = ExcerptResult(
            name="dev",
            original=sample_vars,
            extracted={},
            keys_requested=["NONEXISTENT"],
        )
        assert "NONEXISTENT" in result.missing_keys

    def test_repr_contains_profile_name(self, sample_vars):
        result = ExcerptResult(
            name="staging",
            original=sample_vars,
            extracted={"DEBUG": "true"},
            keys_requested=["DEBUG"],
        )
        assert "staging" in repr(result)


class TestEnvExcerpt:
    def test_excerpt_literal_keys(self, excerptr, sample_vars):
        result = excerptr.excerpt("dev", sample_vars, ["DB_HOST", "DEBUG"])
        assert result.extracted == {"DB_HOST": "localhost", "DEBUG": "true"}

    def test_excerpt_glob_pattern(self, excerptr, sample_vars):
        result = excerptr.excerpt("dev", sample_vars, ["DB_*"])
        assert "DB_HOST" in result.extracted
        assert "DB_PORT" in result.extracted
        assert "API_KEY" not in result.extracted

    def test_excerpt_mixed_literal_and_glob(self, excerptr, sample_vars):
        result = excerptr.excerpt("dev", sample_vars, ["DEBUG", "API_*"])
        assert "DEBUG" in result.extracted
        assert "API_KEY" in result.extracted
        assert "API_SECRET" in result.extracted

    def test_excerpt_missing_key_ignored_by_default(self, excerptr, sample_vars):
        result = excerptr.excerpt("dev", sample_vars, ["MISSING"])
        assert result.extracted == {}

    def test_excerpt_missing_key_raises_when_strict(self, excerptr, sample_vars):
        with pytest.raises(KeyError, match="MISSING"):
            excerptr.excerpt("dev", sample_vars, ["MISSING"], ignore_missing=False)

    def test_excerpt_empty_keys_returns_empty(self, excerptr, sample_vars):
        result = excerptr.excerpt("dev", sample_vars, [])
        assert result.extracted == {}
        assert result.extract_count == 0

    def test_excerpt_preserves_original(self, excerptr, sample_vars):
        result = excerptr.excerpt("dev", sample_vars, ["DEBUG"])
        assert result.original == sample_vars

    def test_excerpt_profile_name_stored(self, excerptr, sample_vars):
        result = excerptr.excerpt("production", sample_vars, ["DEBUG"])
        assert result.name == "production"
