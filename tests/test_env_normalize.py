"""Tests for envchain.env_normalize."""
import pytest

from envchain.env_normalize import EnvNormalizer, NormalizeReport, NormalizeResult


@pytest.fixture
def normalizer() -> EnvNormalizer:
    return EnvNormalizer()


@pytest.fixture
def sample_vars():
    return {
        "DB_HOST": "  localhost  ",
        "DB_PORT": "5432",
        "API_KEY": "  secret  ",
    }


class TestNormalizeResult:
    def test_changed_true_when_values_differ(self):
        r = NormalizeResult("KEY", "  val  ", "val")
        assert r.changed is True

    def test_changed_false_when_values_same(self):
        r = NormalizeResult("KEY", "val", "val")
        assert r.changed is False


class TestNormalizeReport:
    def test_changed_count_zero_when_no_changes(self):
        results = [NormalizeResult("A", "x", "x"), NormalizeResult("B", "y", "y")]
        report = NormalizeReport(results=results)
        assert report.changed_count == 0

    def test_changed_count_nonzero(self):
        results = [NormalizeResult("A", " x ", "x"), NormalizeResult("B", "y", "y")]
        report = NormalizeReport(results=results)
        assert report.changed_count == 1

    def test_has_changes_false_when_empty(self):
        report = NormalizeReport()
        assert report.has_changes is False

    def test_has_changes_true_when_changed(self):
        results = [NormalizeResult("A", " x ", "x")]
        report = NormalizeReport(results=results)
        assert report.has_changes is True

    def test_to_normalized_vars_returns_dict(self):
        results = [NormalizeResult("A", " x ", "x"), NormalizeResult("B", "y", "y")]
        report = NormalizeReport(results=results)
        assert report.to_normalized_vars() == {"A": "x", "B": "y"}


class TestEnvNormalizer:
    def test_default_strategy_is_strip(self):
        n = EnvNormalizer()
        assert n.strategies == ["strip"]

    def test_unknown_strategy_raises(self):
        with pytest.raises(ValueError, match="Unknown strategy"):
            EnvNormalizer(strategies=["nonexistent"])

    def test_strip_removes_whitespace(self, normalizer, sample_vars):
        report = normalizer.normalize(sample_vars)
        normalized = report.to_normalized_vars()
        assert normalized["DB_HOST"] == "localhost"
        assert normalized["API_KEY"] == "secret"

    def test_no_change_for_already_clean_value(self, normalizer):
        report = normalizer.normalize({"KEY": "clean"})
        assert report.changed_count == 0

    def test_upper_strategy(self):
        n = EnvNormalizer(strategies=["upper"])
        report = n.normalize({"KEY": "hello"})
        assert report.to_normalized_vars()["KEY"] == "HELLO"

    def test_lower_strategy(self):
        n = EnvNormalizer(strategies=["lower"])
        report = n.normalize({"KEY": "HELLO"})
        assert report.to_normalized_vars()["KEY"] == "hello"

    def test_strip_quotes_double(self):
        n = EnvNormalizer(strategies=["strip_quotes"])
        report = n.normalize({"KEY": '"value"'})
        assert report.to_normalized_vars()["KEY"] == "value"

    def test_strip_quotes_single(self):
        n = EnvNormalizer(strategies=["strip_quotes"])
        report = n.normalize({"KEY": "'value'"})
        assert report.to_normalized_vars()["KEY"] == "value"

    def test_strip_quotes_no_change_unmatched(self):
        n = EnvNormalizer(strategies=["strip_quotes"])
        report = n.normalize({"KEY": "'value\""})
        assert report.to_normalized_vars()["KEY"] == "'value\""

    def test_multiple_strategies_applied_in_order(self):
        n = EnvNormalizer(strategies=["strip", "upper"])
        report = n.normalize({"KEY": "  hello  "})
        assert report.to_normalized_vars()["KEY"] == "HELLO"

    def test_empty_vars_returns_empty_report(self, normalizer):
        report = normalizer.normalize({})
        assert report.results == []
        assert report.has_changes is False
