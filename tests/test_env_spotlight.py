"""Tests for EnvSpotlight and SpotlightReport."""
import pytest
from envchain.env_spotlight import EnvSpotlight, SpotlightReport, SpotlightResult


@pytest.fixture
def spotlight():
    return EnvSpotlight()


@pytest.fixture
def sample_vars():
    return {
        "API_KEY": "supersecret123",
        "DATABASE_URL": "postgres://localhost/db",
        "DEBUG": "true",
        "LOG_LEVEL": "info",
        "LONG_VAR": "x" * 80,
        "EMPTY_VAR": "",
    }


class TestSpotlightResult:
    def test_to_dict_contains_required_keys(self):
        r = SpotlightResult(name="FOO", value="bar", score=5, reason="standard variable")
        d = r.to_dict()
        assert {"name", "value", "score", "reason"}.issubset(d.keys())

    def test_repr_contains_name_and_score(self):
        r = SpotlightResult(name="FOO", value="bar", score=5, reason="standard variable")
        assert "FOO" in repr(r)
        assert "5" in repr(r)


class TestSpotlightReport:
    def test_high_priority_filters_correctly(self, spotlight, sample_vars):
        report = spotlight.analyse(sample_vars)
        high = report.high_priority
        names = [r.name for r in high]
        assert "API_KEY" in names

    def test_low_priority_filters_correctly(self, spotlight, sample_vars):
        report = spotlight.analyse(sample_vars)
        low = report.low_priority
        names = [r.name for r in low]
        assert "DEBUG" in names or "EMPTY_VAR" in names

    def test_total_equals_var_count(self, spotlight, sample_vars):
        report = spotlight.analyse(sample_vars)
        assert report.total == len(sample_vars)

    def test_top_returns_at_most_n(self, spotlight, sample_vars):
        report = spotlight.analyse(sample_vars)
        assert len(report.top(3)) <= 3

    def test_top_sorted_descending(self, spotlight, sample_vars):
        report = spotlight.analyse(sample_vars)
        top = report.top(10)
        scores = [r.score for r in top]
        assert scores == sorted(scores, reverse=True)

    def test_repr_contains_total(self, spotlight, sample_vars):
        report = spotlight.analyse(sample_vars)
        assert str(report.total) in repr(report)


class TestEnvSpotlight:
    def test_secret_pattern_gets_high_score(self, spotlight):
        report = spotlight.analyse({"SECRET_KEY": "abc"})
        assert report.results[0].score >= 10

    def test_debug_pattern_gets_low_score(self, spotlight):
        report = spotlight.analyse({"DEBUG_MODE": "1"})
        assert report.results[0].score <= 2

    def test_long_value_gets_elevated_score(self, spotlight):
        report = spotlight.analyse({"BLOB": "z" * 100})
        assert report.results[0].score >= 7

    def test_empty_value_gets_score_one(self, spotlight):
        report = spotlight.analyse({"EMPTY": ""})
        assert report.results[0].score == 1

    def test_empty_vars_returns_empty_report(self, spotlight):
        report = spotlight.analyse({})
        assert report.total == 0
        assert report.high_priority == []
