"""Tests for EnvValidator and ValidationResult."""

import pytest
from envchain.validator import EnvValidator, ValidationResult


@pytest.fixture
def validator() -> EnvValidator:
    return EnvValidator()


class TestValidateName:
    def test_valid_simple_name(self, validator):
        result = validator.validate_name("MY_VAR")
        assert result.valid
        assert result.errors == []

    def test_valid_name_with_digits(self, validator):
        result = validator.validate_name("VAR_123")
        assert result.valid

    def test_valid_name_starts_with_underscore(self, validator):
        result = validator.validate_name("_INTERNAL")
        assert result.valid

    def test_empty_name_is_invalid(self, validator):
        result = validator.validate_name("")
        assert not result.valid
        assert any("empty" in e for e in result.errors)

    def test_name_starting_with_digit_is_invalid(self, validator):
        result = validator.validate_name("1VAR")
        assert not result.valid
        assert len(result.errors) == 1

    def test_name_with_hyphen_is_invalid(self, validator):
        result = validator.validate_name("MY-VAR")
        assert not result.valid

    def test_name_with_space_is_invalid(self, validator):
        result = validator.validate_name("MY VAR")
        assert not result.valid


class TestValidateValue:
    def test_normal_value_is_valid(self, validator):
        result = validator.validate_value("PORT", "8080")
        assert result.valid
        assert result.warnings == []

    def test_empty_value_produces_warning(self, validator):
        result = validator.validate_value("PORT", "")
        assert result.valid  # still valid, just a warning
        assert any("empty" in w for w in result.warnings)

    def test_sensitive_name_produces_warning(self, validator):
        result = validator.validate_value("API_TOKEN", "abc123")
        assert result.valid
        assert any("sensitive" in w for w in result.warnings)

    def test_password_name_produces_warning(self, validator):
        result = validator.validate_value("DB_PASSWORD", "secret")
        assert any("sensitive" in w for w in result.warnings)

    def test_non_sensitive_name_no_warning(self, validator):
        result = validator.validate_value("HOME_DIR", "/home/user")
        assert result.warnings == []


class TestValidatePair:
    def test_valid_pair(self, validator):
        result = validator.validate_pair("MY_VAR", "hello")
        assert result.valid
        assert result.errors == []

    def test_invalid_name_propagates_error(self, validator):
        result = validator.validate_pair("123BAD", "value")
        assert not result.valid
        assert len(result.errors) >= 1

    def test_sensitive_pair_merges_warnings(self, validator):
        result = validator.validate_pair("SECRET_KEY", "")
        assert result.valid
        # empty value warning + sensitive name warning
        assert len(result.warnings) >= 2


class TestValidationResult:
    def test_bool_true_when_valid(self):
        r = ValidationResult(valid=True)
        assert bool(r) is True

    def test_bool_false_when_invalid(self):
        r = ValidationResult(valid=False, errors=["bad"])
        assert bool(r) is False
