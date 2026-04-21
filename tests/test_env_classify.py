"""Tests for envchain.env_classify."""
from __future__ import annotations

import pytest
from envchain.env_classify import ClassifyResult, ClassifyReport, EnvClassifier


@pytest.fixture
def classifier() -> EnvClassifier:
    return EnvClassifier()


@pytest.fixture
def sample_vars() -> dict:
    return {
        "DB_PASSWORD": "secret123",
        "DATABASE_URL": "postgres://localhost/mydb",
        "APP_HOST": "localhost",
        "APP_PORT": "8080",
        "DEBUG": "true",
        "FEATURE_DARK_MODE": "enabled",
        "LOG_PATH": "/var/log/app",
        "GREETING": "hello",
    }


class TestClassifyResult:
    def test_to_dict_contains_required_keys(self):
        r = ClassifyResult(name="API_KEY", value="abc", category="secret", matched_pattern=r"(?i)(key)")
        d = r.to_dict()
        assert "name" in d
        assert "value" in d
        assert "category" in d
        assert "matched_pattern" in d

    def test_repr_contains_name_and_category(self):
        r = ClassifyResult(name="TOKEN", value="x", category="secret")
        assert "TOKEN" in repr(r)
        assert "secret" in repr(r)


class TestClassifyReport:
    def test_category_counts_empty(self):
        report = ClassifyReport()
        assert report.category_counts == {}

    def test_has_secrets_false_when_no_secrets(self, classifier, sample_vars):
        report = classifier.classify({"GREETING": "hello", "APP_NAME": "myapp"})
        assert not report.has_secrets

    def test_has_secrets_true_when_password_present(self, classifier):
        report = classifier.classify({"DB_PASSWORD": "s3cr3t"})
        assert report.has_secrets

    def test_by_category_returns_correct_subset(self, classifier, sample_vars):
        report = classifier.classify(sample_vars)
        db_results = report.by_category("database")
        names = [r.name for r in db_results]
        assert "DATABASE_URL" in names

    def test_repr_contains_total(self, classifier, sample_vars):
        report = classifier.classify(sample_vars)
        assert str(len(sample_vars)) in repr(report)


class TestEnvClassifier:
    def test_classify_secret_by_password_name(self, classifier):
        result = classifier.classify_one("DB_PASSWORD", "secret")
        assert result.category == "secret"

    def test_classify_network_by_host(self, classifier):
        result = classifier.classify_one("APP_HOST", "localhost")
        assert result.category == "network"

    def test_classify_debug_by_debug_name(self, classifier):
        result = classifier.classify_one("DEBUG", "true")
        assert result.category == "debug"

    def test_classify_feature_flag(self, classifier):
        result = classifier.classify_one("FEATURE_DARK_MODE", "on")
        assert result.category == "feature_flag"

    def test_classify_path(self, classifier):
        result = classifier.classify_one("LOG_PATH", "/var/log")
        assert result.category == "path"

    def test_classify_general_fallback(self, classifier):
        result = classifier.classify_one("GREETING", "hello")
        assert result.category == "general"

    def test_extra_patterns_applied(self):
        c = EnvClassifier(extra_patterns={"custom": [r"(?i)^MY_"]})
        result = c.classify_one("MY_SETTING", "value")
        assert result.category == "custom"

    def test_classify_all_vars(self, classifier, sample_vars):
        report = classifier.classify(sample_vars)
        assert len(report.results) == len(sample_vars)
        names = [r.name for r in report.results]
        for k in sample_vars:
            assert k in names
