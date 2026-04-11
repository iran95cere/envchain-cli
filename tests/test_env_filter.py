"""Tests for envchain.env_filter."""

import pytest
from envchain.env_filter import EnvFilter, FilterResult


@pytest.fixture
def flt() -> EnvFilter:
    return EnvFilter()


SAMPLE = {
    "AWS_ACCESS_KEY": "AKIA123",
    "AWS_SECRET_KEY": "secret",
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "APP_DEBUG": "true",
}


class TestFilterResult:
    def test_match_count(self):
        r = FilterResult(matched={"A": "1", "B": "2"}, excluded={"C": "3"})
        assert r.match_count == 2

    def test_empty_defaults(self):
        r = FilterResult()
        assert r.matched == {}
        assert r.excluded == {}
        assert r.match_count == 0


class TestFilterByPrefix:
    def test_matches_prefix(self, flt):
        result = flt.filter_by_prefix(SAMPLE, "AWS_")
        assert set(result.matched) == {"AWS_ACCESS_KEY", "AWS_SECRET_KEY"}
        assert "DB_HOST" in result.excluded

    def test_empty_prefix_returns_all(self, flt):
        result = flt.filter_by_prefix(SAMPLE, "")
        assert result.matched == SAMPLE
        assert result.excluded == {}

    def test_case_insensitive_prefix(self, flt):
        result = flt.filter_by_prefix(SAMPLE, "aws_", case_sensitive=False)
        assert set(result.matched) == {"AWS_ACCESS_KEY", "AWS_SECRET_KEY"}

    def test_no_match_returns_empty(self, flt):
        result = flt.filter_by_prefix(SAMPLE, "MISSING_")
        assert result.matched == {}
        assert len(result.excluded) == len(SAMPLE)


class TestFilterByGlob:
    def test_wildcard_pattern(self, flt):
        result = flt.filter_by_glob(SAMPLE, "DB_*")
        assert set(result.matched) == {"DB_HOST", "DB_PORT"}

    def test_question_mark_pattern(self, flt):
        result = flt.filter_by_glob(SAMPLE, "DB_HOS?")
        assert set(result.matched) == {"DB_HOST"}

    def test_case_insensitive_glob(self, flt):
        result = flt.filter_by_glob(SAMPLE, "db_*", case_sensitive=False)
        assert set(result.matched) == {"DB_HOST", "DB_PORT"}

    def test_empty_pattern_returns_all(self, flt):
        result = flt.filter_by_glob(SAMPLE, "")
        assert result.matched == SAMPLE


class TestFilterByRegex:
    def test_regex_match(self, flt):
        result = flt.filter_by_regex(SAMPLE, r"^AWS_")
        assert set(result.matched) == {"AWS_ACCESS_KEY", "AWS_SECRET_KEY"}

    def test_regex_case_insensitive(self, flt):
        result = flt.filter_by_regex(SAMPLE, r"^aws_", case_sensitive=False)
        assert set(result.matched) == {"AWS_ACCESS_KEY", "AWS_SECRET_KEY"}

    def test_invalid_regex_raises(self, flt):
        with pytest.raises(ValueError, match="Invalid regex"):
            flt.filter_by_regex(SAMPLE, r"[invalid")

    def test_partial_match(self, flt):
        result = flt.filter_by_regex(SAMPLE, r"KEY")
        assert set(result.matched) == {"AWS_ACCESS_KEY", "AWS_SECRET_KEY"}


class TestFilterKeys:
    def test_exact_keys(self, flt):
        result = flt.filter_keys(SAMPLE, ["DB_HOST", "APP_DEBUG"])
        assert set(result.matched) == {"DB_HOST", "APP_DEBUG"}

    def test_missing_key_ignored(self, flt):
        result = flt.filter_keys(SAMPLE, ["NONEXISTENT"])
        assert result.matched == {}

    def test_empty_key_list(self, flt):
        result = flt.filter_keys(SAMPLE, [])
        assert result.matched == {}
        assert len(result.excluded) == len(SAMPLE)
