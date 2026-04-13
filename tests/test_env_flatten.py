"""Tests for envchain.env_flatten."""
import pytest
from envchain.env_flatten import EnvFlattener, FlattenResult


@pytest.fixture
def flattener() -> EnvFlattener:
    return EnvFlattener(separator="__")


@pytest.fixture
def sample_vars() -> dict:
    return {
        "DB__HOST": "localhost",
        "DB__PORT": "5432",
        "APP__DEBUG": "true",
        "PLAIN": "value",
    }


class TestFlattenResult:
    def test_changed_count_when_all_keys_transform(self, sample_vars):
        flattener = EnvFlattener()
        result = flattener.flatten(sample_vars)
        assert result.changed_count == 3  # DB__HOST, DB__PORT, APP__DEBUG change

    def test_changed_count_zero_when_no_separator(self):
        flattener = EnvFlattener()
        vars_ = {"PLAIN": "1", "OTHER": "2"}
        result = flattener.flatten(vars_)
        assert result.changed_count == 0

    def test_is_changed_true_when_keys_transform(self, flattener, sample_vars):
        result = flattener.flatten(sample_vars)
        assert result.is_changed is True

    def test_is_changed_false_when_no_keys_transform(self, flattener):
        result = flattener.flatten({"A": "1", "B": "2"})
        assert result.is_changed is False

    def test_original_preserved(self, flattener, sample_vars):
        result = flattener.flatten(sample_vars)
        assert result.original == sample_vars

    def test_separator_stored(self, flattener, sample_vars):
        result = flattener.flatten(sample_vars)
        assert result.separator == "__"

    def test_prefix_filter_stored(self, flattener, sample_vars):
        result = flattener.flatten(sample_vars, prefix_filter="DB")
        assert result.prefix_filter == "DB"


class TestEnvFlattener:
    def test_flatten_replaces_separator_with_dot(self, flattener, sample_vars):
        result = flattener.flatten(sample_vars)
        assert "DB.HOST" in result.flattened
        assert "DB.PORT" in result.flattened
        assert "APP.DEBUG" in result.flattened

    def test_flatten_preserves_plain_keys(self, flattener, sample_vars):
        result = flattener.flatten(sample_vars)
        assert "PLAIN" in result.flattened
        assert result.flattened["PLAIN"] == "value"

    def test_flatten_values_unchanged(self, flattener, sample_vars):
        result = flattener.flatten(sample_vars)
        assert result.flattened["DB.HOST"] == "localhost"
        assert result.flattened["DB.PORT"] == "5432"

    def test_prefix_filter_skips_non_matching_keys(self, flattener):
        vars_ = {"DB__HOST": "localhost", "APP__MODE": "prod"}
        result = flattener.flatten(vars_, prefix_filter="DB")
        assert "DB.HOST" in result.flattened
        assert "APP__MODE" in result.flattened  # not transformed

    def test_custom_separator(self):
        flattener = EnvFlattener(separator="_SEP_")
        vars_ = {"A_SEP_B": "val"}
        result = flattener.flatten(vars_)
        assert "A.B" in result.flattened

    def test_unflatten_reverses_flatten(self, flattener):
        dotted = {"DB.HOST": "localhost", "DB.PORT": "5432"}
        result = flattener.unflatten(dotted)
        assert result == {"DB__HOST": "localhost", "DB__PORT": "5432"}

    def test_unflatten_plain_keys_unchanged(self, flattener):
        plain = {"PLAIN": "value"}
        result = flattener.unflatten(plain)
        assert result == {"PLAIN": "value"}

    def test_flatten_empty_dict(self, flattener):
        result = flattener.flatten({})
        assert result.flattened == {}
        assert result.is_changed is False
