"""Tests for EnvKeyNormalizer."""
import pytest
from envchain.env_uppercase_keys import EnvKeyNormalizer, KeyNormalizeResult, KeyNormalizeReport


@pytest.fixture
def normalizer():
    return EnvKeyNormalizer()


@pytest.fixture
def sample_vars():
    return {
        "myApiKey": "abc",
        "DB_HOST": "localhost",
        "redis-port": "6379",
        "some var": "val",
    }


class TestKeyNormalizeResult:
    def test_changed_true_when_keys_differ(self):
        r = KeyNormalizeResult(name="v", original_key="myKey", new_key="MY_KEY")
        assert r.changed is True

    def test_changed_false_when_keys_same(self):
        r = KeyNormalizeResult(name="v", original_key="MY_KEY", new_key="MY_KEY")
        assert r.changed is False

    def test_repr_contains_keys(self):
        r = KeyNormalizeResult(name="v", original_key="myKey", new_key="MY_KEY")
        assert "myKey" in repr(r)
        assert "MY_KEY" in repr(r)
        assert "changed" in repr(r)


class TestKeyNormalizeReport:
    def test_changed_count(self, normalizer, sample_vars):
        report = normalizer.normalize(sample_vars)
        assert report.changed_count >= 1

    def test_has_changes_true(self, normalizer, sample_vars):
        report = normalizer.normalize(sample_vars)
        assert report.has_changes is True

    def test_has_changes_false_when_all_normalized(self, normalizer):
        report = normalizer.normalize({"MY_VAR": "x", "ANOTHER": "y"})
        assert report.has_changes is False

    def test_to_normalized_vars_returns_dict(self, normalizer, sample_vars):
        report = normalizer.normalize(sample_vars)
        result = report.to_normalized_vars()
        assert isinstance(result, dict)

    def test_repr_contains_counts(self, normalizer, sample_vars):
        report = normalizer.normalize(sample_vars)
        assert "total=" in repr(report)
        assert "changed=" in repr(report)


class TestEnvKeyNormalizer:
    def test_camel_case_converted(self, normalizer):
        result = normalizer._to_upper_snake("myApiKey")
        assert result == "MY_API_KEY"

    def test_hyphen_converted(self, normalizer):
        assert normalizer._to_upper_snake("redis-port") == "REDIS_PORT"

    def test_space_converted(self, normalizer):
        assert normalizer._to_upper_snake("some var") == "SOME_VAR"

    def test_already_upper_snake_unchanged(self, normalizer):
        assert normalizer._to_upper_snake("DB_HOST") == "DB_HOST"

    def test_apply_returns_new_dict(self, normalizer, sample_vars):
        result = normalizer.apply(sample_vars)
        assert "MY_API_KEY" in result
        assert "DB_HOST" in result
        assert "REDIS_PORT" in result

    def test_apply_preserves_values(self, normalizer):
        result = normalizer.apply({"myKey": "hello"})
        assert result["MY_KEY"] == "hello"
