"""Tests for envchain.env_mask."""
import pytest
from envchain.env_mask import EnvMasker, MaskRule, MaskReport


@pytest.fixture
def masker() -> EnvMasker:
    return EnvMasker()


class TestMaskRule:
    def test_matches_password(self):
        rule = MaskRule(r"(?i)password")
        assert rule.matches("DB_PASSWORD")

    def test_no_match_plain_name(self):
        rule = MaskRule(r"(?i)password")
        assert not rule.matches("DB_HOST")

    def test_apply_full_mask(self):
        rule = MaskRule(r"(?i)secret", mask_char="*", reveal_chars=0)
        assert rule.apply("mysecret") == "********"

    def test_apply_with_reveal_chars(self):
        rule = MaskRule(r"(?i)token", mask_char="#", reveal_chars=3)
        result = rule.apply("abcdef123")
        assert result.endswith("123")
        assert result.startswith("######")

    def test_apply_empty_value_returns_empty(self):
        rule = MaskRule(r"(?i)secret")
        assert rule.apply("") == ""

    def test_reveal_chars_longer_than_value(self):
        rule = MaskRule(r"(?i)key", reveal_chars=20)
        # reveal_chars >= len(value): entire value is visible
        result = rule.apply("short")
        assert result == "short"


class TestMaskReport:
    def test_mask_count(self):
        report = MaskReport(
            original={"A": "1", "B": "2"},
            masked={"A": "*", "B": "2"},
            masked_keys=["A"],
        )
        assert report.mask_count == 1

    def test_repr_contains_mask_count(self):
        report = MaskReport(original={}, masked={}, masked_keys=[])
        assert "mask_count" in repr(report)


class TestEnvMasker:
    def test_default_rules_mask_password(self, masker):
        report = masker.mask({"DB_PASSWORD": "s3cr3t", "DB_HOST": "localhost"})
        assert report.masked["DB_PASSWORD"] == "******"
        assert report.masked["DB_HOST"] == "localhost"

    def test_default_rules_mask_token(self, masker):
        report = masker.mask({"API_TOKEN": "tok123"})
        assert "API_TOKEN" in report.masked_keys

    def test_non_sensitive_vars_unchanged(self, masker):
        report = masker.mask({"HOME": "/root", "PATH": "/usr/bin"})
        assert report.mask_count == 0
        assert report.masked == {"HOME": "/root", "PATH": "/usr/bin"}

    def test_is_sensitive_true_for_secret(self, masker):
        assert masker.is_sensitive("MY_SECRET") is True

    def test_is_sensitive_false_for_plain(self, masker):
        assert masker.is_sensitive("APP_ENV") is False

    def test_add_custom_rule(self, masker):
        masker.add_rule(MaskRule(r"(?i)internal"))
        report = masker.mask({"INTERNAL_KEY": "value123"})
        assert "INTERNAL_KEY" in report.masked_keys

    def test_empty_dict_returns_empty_report(self, masker):
        report = masker.mask({})
        assert report.mask_count == 0
        assert report.masked == {}

    def test_custom_masker_no_default_rules(self):
        custom = EnvMasker(rules=[MaskRule(r"(?i)custom")])
        report = custom.mask({"DB_PASSWORD": "plain", "CUSTOM_VAR": "secret"})
        # DB_PASSWORD not masked because no default rules
        assert report.masked["DB_PASSWORD"] == "plain"
        assert "CUSTOM_VAR" in report.masked_keys
