"""Tests for envchain.env_case module."""
import pytest
from envchain.env_case import CaseStyle, CaseResult, CaseReport, EnvCaseConverter


@pytest.fixture
def converter():
    return EnvCaseConverter()


@pytest.fixture
def sample_vars():
    return {"myApiKey": "SomeValue", "db_host": "localhost", "MAX_RETRIES": "3"}


class TestCaseResult:
    def test_changed_true_when_values_differ(self):
        r = CaseResult(name="myVar", original="myVar", converted="MY_VAR", style=CaseStyle.SCREAMING_SNAKE)
        assert r.changed is True

    def test_changed_false_when_values_same(self):
        r = CaseResult(name="MY_VAR", original="MY_VAR", converted="MY_VAR", style=CaseStyle.SCREAMING_SNAKE)
        assert r.changed is False

    def test_repr_contains_arrow_when_changed(self):
        r = CaseResult(name="x", original="foo", converted="FOO", style=CaseStyle.UPPER)
        assert "->" in repr(r)

    def test_repr_contains_unchanged_when_same(self):
        r = CaseResult(name="x", original="FOO", converted="FOO", style=CaseStyle.UPPER)
        assert "unchanged" in repr(r)


class TestCaseReport:
    def test_changed_count_zero_when_no_changes(self):
        results = [CaseResult("A", "v", "v", CaseStyle.LOWER)]
        report = CaseReport(results=results)
        assert report.changed_count == 0

    def test_changed_count_reflects_actual_changes(self):
        results = [
            CaseResult("A", "foo", "FOO", CaseStyle.UPPER),
            CaseResult("B", "bar", "bar", CaseStyle.UPPER),
        ]
        report = CaseReport(results=results)
        assert report.changed_count == 1

    def test_has_changes_false_when_empty(self):
        assert CaseReport().has_changes is False

    def test_to_dict_contains_required_keys(self):
        report = CaseReport()
        d = report.to_dict()
        assert "changed_count" in d
        assert "total" in d
        assert "results" in d


class TestEnvCaseConverter:
    def test_upper_conversion(self, converter):
        report = converter.convert_vars({"my_var": "val"}, CaseStyle.UPPER, target="name")
        assert report.results[0].converted == "MY_VAR"

    def test_lower_conversion(self, converter):
        report = converter.convert_vars({"MY_VAR": "val"}, CaseStyle.LOWER, target="name")
        assert report.results[0].converted == "my_var"

    def test_screaming_snake_from_camel(self, converter):
        report = converter.convert_vars({"myApiKey": "val"}, CaseStyle.SCREAMING_SNAKE, target="name")
        assert report.results[0].converted == "MY_API_KEY"

    def test_snake_from_camel(self, converter):
        report = converter.convert_vars({"myApiKey": "val"}, CaseStyle.SNAKE, target="name")
        assert report.results[0].converted == "my_api_key"

    def test_value_target_converts_values(self, converter):
        report = converter.convert_vars({"VAR": "hello_world"}, CaseStyle.UPPER, target="value")
        assert report.results[0].converted == "HELLO_WORLD"

    def test_no_change_when_already_correct(self, converter):
        report = converter.convert_vars({"MY_VAR": "val"}, CaseStyle.SCREAMING_SNAKE, target="name")
        assert report.results[0].changed is False

    def test_multiple_vars_report_length(self, converter, sample_vars):
        report = converter.convert_vars(sample_vars, CaseStyle.UPPER, target="name")
        assert len(report.results) == len(sample_vars)
