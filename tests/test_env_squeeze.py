"""Tests for envchain.env_squeeze."""
import pytest
from envchain.env_squeeze import EnvSqueezer, SqueezeResult, SqueezeReport


@pytest.fixture
def squeezer():
    return EnvSqueezer(char=" ")


@pytest.fixture
def sample_vars():
    return {
        "GREETING": "hello   world",
        "PATH_VAL": "/usr/bin",
        "SPACED": "a  b  c",
        "EMPTY": "",
    }


class TestSqueezeResult:
    def test_changed_true_when_values_differ(self):
        r = SqueezeResult(name="X", original="a  b", squeezed="a b")
        assert r.changed is True

    def test_changed_false_when_values_same(self):
        r = SqueezeResult(name="X", original="a b", squeezed="a b")
        assert r.changed is False


class TestSqueezeReport:
    def test_changed_count_reflects_changed_results(self):
        report = SqueezeReport(results=[
            SqueezeResult("A", "a  b", "a b"),
            SqueezeResult("B", "ok", "ok"),
        ])
        assert report.changed_count == 1

    def test_has_changes_false_when_all_unchanged(self):
        report = SqueezeReport(results=[
            SqueezeResult("A", "x", "x"),
        ])
        assert report.has_changes is False

    def test_has_changes_true_when_any_changed(self):
        report = SqueezeReport(results=[
            SqueezeResult("A", "a  b", "a b"),
        ])
        assert report.has_changes is True

    def test_empty_report_has_no_changes(self):
        report = SqueezeReport()
        assert report.has_changes is False
        assert report.changed_count == 0


class TestEnvSqueezer:
    def test_squeeze_collapses_double_spaces(self, squeezer):
        assert squeezer.squeeze_value("hello   world") == "hello world"

    def test_squeeze_no_change_when_single_spaces(self, squeezer):
        assert squeezer.squeeze_value("hello world") == "hello world"

    def test_squeeze_empty_string_unchanged(self, squeezer):
        assert squeezer.squeeze_value("") == ""

    def test_squeeze_all_spaces_becomes_one(self, squeezer):
        assert squeezer.squeeze_value("     ") == " "

    def test_squeeze_custom_char(self):
        s = EnvSqueezer(char="/")
        assert s.squeeze_value("/usr//local///bin") == "/usr/local/bin"

    def test_squeeze_report_contains_all_keys(self, squeezer, sample_vars):
        report = squeezer.squeeze(sample_vars)
        names = {r.name for r in report.results}
        assert names == set(sample_vars.keys())

    def test_apply_returns_new_dict_and_report(self, squeezer, sample_vars):
        new_vars, report = squeezer.apply(sample_vars)
        assert isinstance(new_vars, dict)
        assert isinstance(report, SqueezeReport)
        assert new_vars["GREETING"] == "hello world"
        assert new_vars["PATH_VAL"] == "/usr/bin"

    def test_apply_does_not_mutate_original(self, squeezer, sample_vars):
        original_copy = dict(sample_vars)
        squeezer.apply(sample_vars)
        assert sample_vars == original_copy

    def test_invalid_char_raises(self):
        with pytest.raises(ValueError):
            EnvSqueezer(char="ab")
