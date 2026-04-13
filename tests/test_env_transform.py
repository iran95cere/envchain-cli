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

    def test_register_custom_transform(self, transformer):
        transformer.register("reverse", lambda v: v[::-1])
        result = transformer.apply("abc", "reverse")
        assert result.transformed == "cba"

    def test_register_empty_name_raises(self, transformer):
        with pytest.raises(ValueError):
            transformer.register("", lambda v: v)

    def test_apply_many_filters_by_keys(self, transformer):
        vars_ = {"A": "hello", "B": "world", "C": "foo"}
        report = transformer.apply_many(vars_, "upper", keys=["A", "C"])
        assert len(report.results) == 2
        assert report.changed_count == 2

    def test_apply_many_all_keys_when_none(self, transformer):
        vars_ = {"X": "hi", "Y": "there"}
        report = transformer.apply_many(vars_, "upper")
        assert len(report.results) == 2

    def test_base64_roundtrip(self, transformer):
        original = "secret_value"
        encoded = transformer.apply(original, "base64_encode").transformed
        decoded = transformer.apply(encoded, "base64_decode").transformed
        assert decoded == original
