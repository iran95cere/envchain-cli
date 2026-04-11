"""Tests for envchain.env_secrets."""

from __future__ import annotations

import pytest

from envchain.env_secrets import SecretScanner, SecretScanResult


@pytest.fixture
def scanner() -> SecretScanner:
    return SecretScanner(mask_char="*", mask_length=8)


class TestSecretScanResult:
    def test_count_empty(self):
        r = SecretScanResult(profile="dev")
        assert r.count == 0

    def test_has_secrets_false_when_empty(self):
        r = SecretScanResult(profile="dev")
        assert not r.has_secrets()

    def test_has_secrets_true_when_flagged(self):
        r = SecretScanResult(profile="dev", flagged={"API_KEY": "name matches"})
        assert r.has_secrets()
        assert r.count == 1

    def test_repr_contains_profile_and_count(self):
        r = SecretScanResult(profile="prod", flagged={"TOKEN": "x"})
        text = repr(r)
        assert "prod" in text
        assert "1" in text


class TestSecretScannerIsSecretName:
    def test_password_flagged(self, scanner):
        assert scanner.is_secret_name("DB_PASSWORD")

    def test_token_flagged(self, scanner):
        assert scanner.is_secret_name("GITHUB_TOKEN")

    def test_api_key_flagged(self, scanner):
        assert scanner.is_secret_name("STRIPE_API_KEY")

    def test_plain_name_not_flagged(self, scanner):
        assert not scanner.is_secret_name("APP_ENV")

    def test_case_insensitive(self, scanner):
        assert scanner.is_secret_name("db_secret")


class TestSecretScannerIsSecretValue:
    def test_long_value_flagged(self, scanner):
        assert scanner.is_secret_value("a" * 25)

    def test_short_value_not_flagged(self, scanner):
        assert not scanner.is_secret_value("short")

    def test_empty_value_not_flagged(self, scanner):
        assert not scanner.is_secret_value("")


class TestSecretScannerMask:
    def test_mask_shows_first_two_chars(self, scanner):
        masked = scanner.mask("abcdef1234567890")
        assert masked.startswith("ab")
        assert "*" * 8 in masked

    def test_mask_short_value_no_visible(self, scanner):
        masked = scanner.mask("ab")
        assert masked == "*" * 8

    def test_mask_empty_returns_empty(self, scanner):
        assert scanner.mask("") == ""


class TestSecretScannerScan:
    def test_scan_flags_secret_name(self, scanner):
        result = scanner.scan("dev", {"API_KEY": "short"})
        assert "API_KEY" in result.flagged

    def test_scan_flags_high_entropy_value(self, scanner):
        result = scanner.scan("dev", {"RANDOM_VAR": "x" * 25})
        assert "RANDOM_VAR" in result.flagged

    def test_scan_no_secrets(self, scanner):
        result = scanner.scan("dev", {"APP_ENV": "production"})
        assert not result.has_secrets()

    def test_scan_multiple_reasons(self, scanner):
        result = scanner.scan("dev", {"DB_PASSWORD": "x" * 25})
        assert "name matches" in result.flagged["DB_PASSWORD"]
        assert "entropy" in result.flagged["DB_PASSWORD"]


class TestMaskedVars:
    def test_masked_vars_replaces_secrets(self, scanner):
        variables = {"API_KEY": "mysecret", "APP_ENV": "dev"}
        masked = scanner.masked_vars(variables)
        assert "*" in masked["API_KEY"]
        assert masked["APP_ENV"] == "dev"

    def test_only_flagged_excludes_plain(self, scanner):
        variables = {"API_KEY": "mysecret", "APP_ENV": "dev"}
        masked = scanner.masked_vars(variables, only_flagged=True)
        assert "APP_ENV" not in masked
        assert "API_KEY" in masked
