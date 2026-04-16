"""Tests for env_uppercase module."""
import pytest
from envchain.env_uppercase import EnvUppercaser, UppercaseReport, UppercaseResult


@pytest.fixture
def uppercaser():
    return EnvUppercaser()


@pytest.fixture
def sample_vars():
    return {"db_host": "localhost", "Api_Key": "secret", "TIMEOUT": "30"}


class TestUppercaseResult:
    def test_changed_true_when_values_differ(self):
        r = UppercaseResult(name="db_host", original="db_host", converted="DB_HOST")
        assert r.changed is True

    def test_changed_false_when_values_same(self):
        r = UppercaseResult(name="TIMEOUT", original="TIMEOUT", converted="TIMEOUT")
        assert r.changed is False

    def test_repr_contains_name(self):
        r = UppercaseResult(name="db_host", original="db_host", converted="DB_HOST")
        assert "db_host" in repr(r)


class TestUppercaseReport:
    def test_changed_count_reflects_mixed_vars(self, uppercaser, sample_vars):
        report = uppercaser.convert(sample_vars)
        # "db_host" and "Api_Key" need conversion; "TIMEOUT" does not
        assert report.changed_count == 2

    def test_has_changes_true_when_mixed(self, uppercaser, sample_vars):
        report = uppercaser.convert(sample_vars)
        assert report.has_changes is True

    def test_has_changes_false_when_all_uppercase(self, uppercaser):
        report = uppercaser.convert({"FOO": "bar", "BAZ": "qux"})
        assert report.has_changes is False

    def test_to_dict_contains_required_keys(self, uppercaser, sample_vars):
        report = uppercaser.convert(sample_vars)
        d = report.to_dict()
        assert "changed_count" in d
        assert "results" in d

    def test_to_dict_results_have_name_original_converted(self, uppercaser, sample_vars):
        report = uppercaser.convert(sample_vars)
        for entry in report.to_dict()["results"]:
            assert "name" in entry
            assert "original" in entry
            assert "converted" in entry


class TestEnvUppercaser:
    def test_convert_returns_report(self, uppercaser, sample_vars):
        report = uppercaser.convert(sample_vars)
        assert isinstance(report, UppercaseReport)

    def test_apply_uppercases_keys(self, uppercaser, sample_vars):
        report = uppercaser.convert(sample_vars)
        result = uppercaser.apply(sample_vars, report)
        assert "DB_HOST" in result
        assert "API_KEY" in result
        assert "TIMEOUT" in result

    def test_apply_preserves_values(self, uppercaser, sample_vars):
        report = uppercaser.convert(sample_vars)
        result = uppercaser.apply(sample_vars, report)
        assert result["DB_HOST"] == "localhost"
        assert result["API_KEY"] == "secret"
        assert result["TIMEOUT"] == "30"

    def test_apply_empty_dict(self, uppercaser):
        report = uppercaser.convert({})
        result = uppercaser.apply({}, report)
        assert result == {}

    def test_convert_already_uppercase_no_changes(self, uppercaser):
        vars_dict = {"FOO": "1", "BAR": "2"}
        report = uppercaser.convert(vars_dict)
        assert report.changed_count == 0
        assert not report.has_changes
