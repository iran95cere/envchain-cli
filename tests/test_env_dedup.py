"""Tests for envchain.env_dedup."""
import pytest

from envchain.env_dedup import DedupGroup, DedupReport, EnvDeduplicator


@pytest.fixture()
def deduplicator() -> EnvDeduplicator:
    return EnvDeduplicator()


@pytest.fixture()
def sample_vars() -> dict:
    return {
        "DB_HOST": "localhost",
        "CACHE_HOST": "localhost",  # duplicate of DB_HOST
        "APP_PORT": "8080",
        "DEBUG_PORT": "8080",  # duplicate of APP_PORT
        "SECRET_KEY": "abc123",  # unique
    }


class TestDedupGroup:
    def test_to_dict_contains_required_keys(self):
        g = DedupGroup(value="localhost", names=["DB_HOST", "CACHE_HOST"])
        d = g.to_dict()
        assert "value" in d
        assert "names" in d

    def test_from_dict_roundtrip(self):
        g = DedupGroup(value="localhost", names=["A", "B"])
        restored = DedupGroup.from_dict(g.to_dict())
        assert restored.value == g.value
        assert restored.names == g.names

    def test_from_dict_missing_names_defaults_empty(self):
        g = DedupGroup.from_dict({"value": "x"})
        assert g.names == []


class TestDedupReport:
    def test_has_duplicates_false_when_empty(self):
        report = DedupReport()
        assert not report.has_duplicates

    def test_duplicate_count_zero_when_no_groups(self):
        assert DedupReport().duplicate_count == 0

    def test_duplicate_count_counts_extras(self):
        report = DedupReport(
            groups=[
                DedupGroup(value="localhost", names=["A", "B", "C"]),
                DedupGroup(value="8080", names=["X", "Y"]),
            ]
        )
        # group1 has 2 extras, group2 has 1 extra
        assert report.duplicate_count == 3

    def test_has_duplicates_true_when_groups_present(self):
        report = DedupReport(
            groups=[DedupGroup(value="v", names=["A", "B"])]
        )
        assert report.has_duplicates


class TestEnvDeduplicator:
    def test_analyse_finds_duplicate_groups(self, deduplicator, sample_vars):
        report = deduplicator.analyse(sample_vars)
        assert report.has_duplicates
        assert len(report.groups) == 2

    def test_analyse_returns_empty_report_for_unique_vars(self, deduplicator):
        variables = {"A": "1", "B": "2", "C": "3"}
        report = deduplicator.analyse(variables)
        assert not report.has_duplicates
        assert report.groups == []

    def test_analyse_single_var_no_duplicates(self, deduplicator):
        report = deduplicator.analyse({"ONLY": "value"})
        assert not report.has_duplicates

    def test_remove_duplicates_keep_first(self, deduplicator, sample_vars):
        result = deduplicator.remove_duplicates(sample_vars, keep="first")
        # For "localhost": CACHE_HOST < DB_HOST alphabetically → keep CACHE_HOST
        assert "CACHE_HOST" in result
        assert "DB_HOST" not in result
        # For "8080": APP_PORT < DEBUG_PORT → keep APP_PORT
        assert "APP_PORT" in result
        assert "DEBUG_PORT" not in result
        assert "SECRET_KEY" in result

    def test_remove_duplicates_keep_last(self, deduplicator, sample_vars):
        result = deduplicator.remove_duplicates(sample_vars, keep="last")
        assert "DB_HOST" in result
        assert "CACHE_HOST" not in result
        assert "DEBUG_PORT" in result
        assert "APP_PORT" not in result

    def test_remove_duplicates_accepts_precomputed_report(self, deduplicator, sample_vars):
        report = deduplicator.analyse(sample_vars)
        result = deduplicator.remove_duplicates(sample_vars, report=report)
        assert len(result) < len(sample_vars)

    def test_remove_duplicates_preserves_unique_vars(self, deduplicator, sample_vars):
        result = deduplicator.remove_duplicates(sample_vars)
        assert "SECRET_KEY" in result
