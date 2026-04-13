"""Tests for envchain.env_transform."""
from __future__ import annotations

import pytest

from envchain.env_transform import EnvTransformer, TransformReport, TransformResult


@pytest.fixture()
def transformer() -> EnvTransformer:
    return EnvTransformer()


class TestTransformResult:
    def test_changed_true_when_values_differ(self):
        r = TransformResult(original="hello", transformed="HELLO", transform_name="upper")
        assert r.changed is True

    def test_changed_false_when_values_same(self):
        r = TransformResult(original="HELLO", transformed="HELLO", transform_name="upper")
        assert r.changed is False

    def test_repr_contains_name(self):
        r = TransformResult(original="a", transformed="A", transform_name="upper")
        assert "upper" in repr(r)

    def test_repr_contains_changed(self):
        r = TransformResult(original="a", transformed="A", transform_name="upper")
        assert "changed=True" in repr(r)


class TestTransformReport:
    def test_changed_count_zero_when_no_changes(self):
        results = [
            TransformResult("A", "A", "upper"),
            TransformResult("B", "B", "upper"),
        ]
        report = TransformReport(results=results)
        assert report.changed_count == 0

    def test_changed_count_correct(self):
        results = [
            TransformResult("hello", "HELLO", "upper"),
            TransformResult("B", "B", "upper"),
        ]
        report = TransformReport(results=results)
        assert report.changed_count == 1

    def test_has_changes_false_when_empty(self):
        assert TransformReport().has_changes is False

    def test_has_changes_true_when_changed(self):
        report = TransformReport(
            results=[TransformResult("a", "A", "upper")]
        )
        assert report.has_changes is True

    def test_to_dict_contains_required_keys(self):
        report = TransformReport()
        d = report.to_dict()
        assert "changed_count" in d
        assert "total" in d
        assert "results" in d

    def test_to_dict_total_matches_results_length(self):
        results = [
            TransformResult("hello", "HELLO", "upper"),
            TransformResult("world", "WORLD", "upper"),
            TransformResult("B", "B", "upper"),
        ]
        report = TransformReport(results=results)
        d = report.to_dict()
        assert d["total"] == 3
        assert d["changed_count"] == 2


class TestEnvTransformer:
    def test_available_returns_sorted_list(self, transformer):
        names = transformer.available()
        assert names == sorted(names)
        assert "upper" in names
        assert "lower" in names

    def test_apply_upper(self, transformer):
        result = transformer.apply("hello", "upper")
        assert result.transformed == "HELLO"

    def test_apply_lower(self, transformer):
        result = transformer.apply("WORLD", "lower")
        assert result.transformed == "world"

    def test_apply_strip(self, transformer):
        result = transformer.apply("  hi  ", "strip")
        assert result.transformed == "hi"

    def test_apply_trim_quotes(self, transformer):
        result = transformer.apply('"quoted"', "trim_quotes")
        assert result.transformed == "quoted"

    def test_apply_unknown_raises(self, transformer):
        with pytest.raises(KeyError):
            transformer.apply("value", "nonexistent_transform")
