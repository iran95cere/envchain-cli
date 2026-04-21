"""Integration tests for classify against real storage."""
from __future__ import annotations

import os
import tempfile

import pytest

from envchain.storage import EnvStorage
from envchain.models import Profile
from envchain.env_classify import EnvClassifier


@pytest.fixture
def tmp_dir():
    with tempfile.TemporaryDirectory() as d:
        yield d


@pytest.fixture
def storage(tmp_dir):
    return EnvStorage(storage_dir=tmp_dir)


def _save_profile(storage: EnvStorage, name: str, vars_: dict, password: str) -> Profile:
    p = Profile(name=name, vars=vars_)
    storage.save_profile(p, password)
    return p


class TestClassifyIntegration:
    def test_classify_after_save_and_load(self, storage):
        vars_ = {
            "API_TOKEN": "tok_abc",
            "SERVER_HOST": "example.com",
            "ENABLE_CACHE": "true",
        }
        _save_profile(storage, "prod", vars_, "pass123")
        profile = storage.load_profile("prod", "pass123")
        assert profile is not None

        classifier = EnvClassifier()
        report = classifier.classify(profile.vars)
        categories = {r.category for r in report.results}
        assert "secret" in categories
        assert "network" in categories

    def test_all_vars_classified(self, storage):
        vars_ = {f"VAR_{i}": str(i) for i in range(10)}
        _save_profile(storage, "test", vars_, "pw")
        profile = storage.load_profile("test", "pw")
        assert profile is not None

        classifier = EnvClassifier()
        report = classifier.classify(profile.vars)
        assert len(report.results) == len(vars_)

    def test_extra_patterns_respected(self, storage):
        vars_ = {"CUSTOM_SETTING": "value", "REGULAR_VAR": "other"}
        _save_profile(storage, "custom", vars_, "pw")
        profile = storage.load_profile("custom", "pw")
        assert profile is not None

        classifier = EnvClassifier(extra_patterns={"custom": [r"(?i)^CUSTOM_"]})
        report = classifier.classify(profile.vars)
        custom_results = report.by_category("custom")
        assert any(r.name == "CUSTOM_SETTING" for r in custom_results)
