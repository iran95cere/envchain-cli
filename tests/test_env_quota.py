"""Tests for envchain.env_quota."""
import pytest
from envchain.env_quota import (
    QuotaPolicy,
    QuotaViolation,
    QuotaCheckResult,
    QuotaManager,
    DEFAULT_MAX_VARS,
    DEFAULT_MAX_VALUE_LENGTH,
)


# --- QuotaPolicy ---

class TestQuotaPolicy:
    def test_defaults(self):
        p = QuotaPolicy()
        assert p.max_vars == DEFAULT_MAX_VARS
        assert p.max_value_length == DEFAULT_MAX_VALUE_LENGTH

    def test_to_dict_contains_required_keys(self):
        p = QuotaPolicy(max_vars=10, max_value_length=512)
        d = p.to_dict()
        assert d["max_vars"] == 10
        assert d["max_value_length"] == 512

    def test_from_dict_roundtrip(self):
        p = QuotaPolicy(max_vars=20, max_value_length=1024)
        p2 = QuotaPolicy.from_dict(p.to_dict())
        assert p2.max_vars == 20
        assert p2.max_value_length == 1024

    def test_from_dict_uses_defaults_for_missing_keys(self):
        p = QuotaPolicy.from_dict({})
        assert p.max_vars == DEFAULT_MAX_VARS
        assert p.max_value_length == DEFAULT_MAX_VALUE_LENGTH

    def test_repr_contains_fields(self):
        p = QuotaPolicy(max_vars=5, max_value_length=256)
        r = repr(p)
        assert "5" in r
        assert "256" in r


# --- QuotaViolation ---

class TestQuotaViolation:
    def test_repr_contains_field_and_message(self):
        v = QuotaViolation(field="var_count", message="too many")
        r = repr(v)
        assert "var_count" in r
        assert "too many" in r


# --- QuotaCheckResult ---

class TestQuotaCheckResult:
    def test_passed_true_when_no_violations(self):
        r = QuotaCheckResult()
        assert r.passed is True

    def test_passed_false_when_violations_exist(self):
        r = QuotaCheckResult(violations=[QuotaViolation("x", "bad")])
        assert r.passed is False

    def test_repr_contains_passed_and_count(self):
        r = QuotaCheckResult(violations=[QuotaViolation("x", "bad")])
        rep = repr(r)
        assert "passed=False" in rep
        assert "violations=1" in rep


# --- QuotaManager ---

@pytest.fixture
def manager():
    return QuotaManager(QuotaPolicy(max_vars=3, max_value_length=10))


class TestQuotaManager:
    def test_check_passes_for_valid_vars(self, manager):
        result = manager.check({"A": "hello", "B": "world"})
        assert result.passed

    def test_check_fails_when_too_many_vars(self, manager):
        vars = {f"VAR_{i}": "x" for i in range(5)}
        result = manager.check(vars)
        assert not result.passed
        fields = [v.field for v in result.violations]
        assert "var_count" in fields

    def test_check_fails_when_value_too_long(self, manager):
        result = manager.check({"KEY": "a" * 20})
        assert not result.passed
        assert any(v.field == "KEY" for v in result.violations)

    def test_check_multiple_violations(self, manager):
        vars = {f"V{i}": "x" * 20 for i in range(5)}
        result = manager.check(vars)
        assert not result.passed
        assert len(result.violations) >= 2

    def test_default_policy_used_when_none_given(self):
        mgr = QuotaManager()
        assert mgr.policy.max_vars == DEFAULT_MAX_VARS

    def test_empty_vars_passes(self, manager):
        result = manager.check({})
        assert result.passed
