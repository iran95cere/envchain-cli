"""Tests for env_lowercase module."""
import pytest
from envchain.env_lowercase import EnvLowercaser, LowercaseReport, LowercaseResult


@pytest.fixture
def lowercaser():
    return EnvLowercaser()


@pytest.fixture
def sample_vars():
    return {
        "API_URL": "HTTPS://EXAMPLE.COM",
        "DEBUG": "true",
        "APP_NAME": "MyApp",
    }


class TestLowercaseResult:
    def test_changed_true_when_values_differ(self):
        r = LowercaseResult(name="X", original="HELLO", transformed="hello")
        assert r.changed is True

    def test_changed_false_when_values_same(self):
        r = LowercaseResult(name="X", original="hello", transformed="hello")
        assert r.changed is False

    def test_repr_contains_name(self):
        r = LowercaseResult(name="MY_VAR", original="ABC", transformed="abc")
        assert "MY_VAR" in repr(r)


class TestLowercaseReport:
    def test_changed_count_zero_when_all_lowercase(self):
        results = [
            LowercaseResult("A", "hello", "hello"),
            LowercaseResult("B", "world", "world"),
        ]
        report = LowercaseReport(results=results)
        assert report.changed_count == 0

    def test_changed_count_correct(self):
        results = [
            LowercaseResult("A", "HELLO", "hello"),
            LowercaseResult("B", "world", "world"),
        ]
        report = LowercaseReport(results=results)
        assert report.changed_count == 1

    def test_has_changes_false_when_clean(self):
        report = LowercaseReport(results=[])
        assert report.has_changes is False

    def test_has_changes_true_when_modified(self):
        results = [LowercaseResult("A", "UPPER", "upper")]
        report = LowercaseReport(results=results)
        assert report.has_changes is True

    def test_to_dict_contains_required_keys(self):
        report = LowercaseReport(results=[])
        d = report.to_dict()
        assert "changed_count" in d
        assert "total" in d
        assert "results" in d


class TestEnvLowercaser:
    def test_run_returns_report(self, lowercaser, sample_vars):
        report = lowercaser.run(sample_vars)
        assert isinstance(report, LowercaseReport)
        assert len(report.results) == len(sample_vars)

    def test_run_lowercases_values(self, lowercaser):
        report = lowercaser.run({"KEY": "HELLO"})
        assert report.results[0].transformed == "hello"

    def test_run_preserves_already_lowercase(self, lowercaser):
        report = lowercaser.run({"KEY": "hello"})
        assert report.results[0].changed is False

    def test_apply_returns_dict(self, lowercaser, sample_vars):
        result = lowercaser.apply(sample_vars)
        assert isinstance(result, dict)
        assert set(result.keys()) == set(sample_vars.keys())

    def test_apply_all_values_lowercase(self, lowercaser, sample_vars):
        result = lowercaser.apply(sample_vars)
        for value in result.values():
            assert value == value.lower()

    def test_apply_empty_vars(self, lowercaser):
        result = lowercaser.apply({})
        assert result == {}
