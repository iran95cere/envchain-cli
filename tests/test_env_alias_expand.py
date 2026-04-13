"""Tests for envchain.env_alias_expand."""
import pytest
from envchain.env_alias_expand import (
    AliasExpandResult,
    AliasExpandReport,
    EnvAliasExpander,
)


@pytest.fixture
def expander() -> EnvAliasExpander:
    return EnvAliasExpander()


@pytest.fixture
def sample_vars() -> dict:
    return {"DB_HOST": "localhost", "DB_PORT": "5432"}


class TestAliasExpandResult:
    def test_repr_expanded(self):
        r = AliasExpandResult("DB_HOST", "DATABASE_HOST", "localhost", True)
        assert "expanded" in repr(r)
        assert "DB_HOST" in repr(r)

    def test_repr_skipped(self):
        r = AliasExpandResult("DB_HOST", "DATABASE_HOST", None, False)
        assert "skipped" in repr(r)


class TestAliasExpandReport:
    def test_expanded_count_zero_when_empty(self):
        report = AliasExpandReport()
        assert report.expanded_count == 0

    def test_has_expansions_false_when_empty(self):
        report = AliasExpandReport()
        assert not report.has_expansions

    def test_expanded_count_counts_only_expanded(self):
        report = AliasExpandReport(results=[
            AliasExpandResult("A", "B", "v", True),
            AliasExpandResult("C", "D", None, False),
        ])
        assert report.expanded_count == 1
        assert report.skipped_count == 1

    def test_repr_contains_counts(self):
        report = AliasExpandReport()
        assert "expanded" in repr(report)


class TestEnvAliasExpander:
    def test_expand_adds_alias(self, expander, sample_vars):
        report = expander.expand(sample_vars, {"DATABASE_HOST": "DB_HOST"})
        assert sample_vars["DATABASE_HOST"] == "localhost"
        assert report.expanded_count == 1

    def test_expand_skips_when_original_missing(self, expander, sample_vars):
        report = expander.expand(sample_vars, {"CACHE_HOST": "REDIS_HOST"})
        assert "CACHE_HOST" not in sample_vars
        assert report.expanded_count == 0
        assert report.skipped_count == 1

    def test_expand_does_not_overwrite_by_default(self, expander):
        variables = {"DB_HOST": "localhost", "DATABASE_HOST": "existing"}
        report = expander.expand(variables, {"DATABASE_HOST": "DB_HOST"})
        assert variables["DATABASE_HOST"] == "existing"
        assert report.expanded_count == 0

    def test_expand_overwrites_when_flag_set(self, expander):
        variables = {"DB_HOST": "localhost", "DATABASE_HOST": "existing"}
        report = expander.expand(
            variables, {"DATABASE_HOST": "DB_HOST"}, overwrite=True
        )
        assert variables["DATABASE_HOST"] == "localhost"
        assert report.expanded_count == 1

    def test_expand_multiple_aliases(self, expander, sample_vars):
        alias_map = {"DATABASE_HOST": "DB_HOST", "DATABASE_PORT": "DB_PORT"}
        report = expander.expand(sample_vars, alias_map)
        assert report.expanded_count == 2
        assert sample_vars["DATABASE_HOST"] == "localhost"
        assert sample_vars["DATABASE_PORT"] == "5432"

    def test_expand_empty_alias_map_no_changes(self, expander, sample_vars):
        original = dict(sample_vars)
        report = expander.expand(sample_vars, {})
        assert sample_vars == original
        assert report.expanded_count == 0

    def test_has_expansions_true_after_successful_expand(self, expander, sample_vars):
        report = expander.expand(sample_vars, {"HOST": "DB_HOST"})
        assert report.has_expansions
