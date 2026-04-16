"""Integration tests for EnvShrinker with EnvStorage."""
import pytest
from pathlib import Path
from envchain.storage import EnvStorage
from envchain.models import Profile
from envchain.env_shrink import EnvShrinker


@pytest.fixture
def tmp_dir(tmp_path):
    return tmp_path


@pytest.fixture
def storage(tmp_dir):
    return EnvStorage(base_dir=str(tmp_dir))


def _save_profile(storage: EnvStorage, name: str, vars_: dict) -> Profile:
    p = Profile(name=name)
    p.vars = dict(vars_)
    storage.save_profile(p)
    return p


class TestEnvShrinkIntegration:
    def test_strip_roundtrip_via_storage(self, storage):
        _save_profile(storage, "prod", {"URL": "  https://example.com  ", "OK": "fine"})
        profile = storage.load_profile("prod")
        shrinker = EnvShrinker(strategy="strip")
        report = shrinker.shrink(profile.vars)
        profile.vars = shrinker.to_dict(report)
        storage.save_profile(profile)

        reloaded = storage.load_profile("prod")
        assert reloaded.vars["URL"] == "https://example.com"
        assert reloaded.vars["OK"] == "fine"

    def test_collapse_whitespace_roundtrip(self, storage):
        _save_profile(storage, "staging", {"MSG": "hello   world"})
        profile = storage.load_profile("staging")
        shrinker = EnvShrinker(strategy="collapse_whitespace")
        report = shrinker.shrink(profile.vars)
        profile.vars = shrinker.to_dict(report)
        storage.save_profile(profile)

        reloaded = storage.load_profile("staging")
        assert reloaded.vars["MSG"] == "hello world"

    def test_no_changes_leaves_profile_intact(self, storage):
        original = {"A": "clean", "B": "also_clean"}
        _save_profile(storage, "local", original)
        profile = storage.load_profile("local")
        shrinker = EnvShrinker(strategy="strip")
        report = shrinker.shrink(profile.vars)
        assert not report.has_changes
        assert report.total_saved_bytes == 0
