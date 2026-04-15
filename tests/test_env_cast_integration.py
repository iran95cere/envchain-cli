"""Integration tests for EnvCaster with real Profile and Storage."""
import pytest
import tempfile
import os
from envchain.storage import EnvStorage
from envchain.models import Profile
from envchain.env_cast import EnvCaster


@pytest.fixture
def tmp_dir():
    with tempfile.TemporaryDirectory() as d:
        yield d


@pytest.fixture
def storage(tmp_dir):
    return EnvStorage(storage_dir=tmp_dir)


def _save_profile(storage, name: str, variables: dict) -> Profile:
    p = Profile(name=name, variables=variables)
    storage.save_profile(p, password="secret")
    return p


class TestEnvCasterIntegration:
    def test_cast_int_roundtrip(self, storage):
        _save_profile(storage, "dev", {"PORT": "9000", "WORKERS": "4"})
        profile = storage.load_profile("dev", password="secret")
        caster = EnvCaster()
        report = caster.cast(profile.variables, "int")
        assert report.success_count == 2
        assert not report.has_failures
        values = {r.name: r.casted for r in report.results}
        assert values["PORT"] == 9000
        assert values["WORKERS"] == 4

    def test_cast_bool_mixed_profile(self, storage):
        _save_profile(storage, "flags", {"ENABLE_A": "true", "ENABLE_B": "false", "ENABLE_C": "yes"})
        profile = storage.load_profile("flags", password="secret")
        caster = EnvCaster()
        report = caster.cast(profile.variables, "bool")
        assert report.success_count == 3
        assert not report.has_failures

    def test_cast_json_nested(self, storage):
        _save_profile(storage, "cfg", {"LIMITS": '{"max": 100, "min": 0}'})
        profile = storage.load_profile("cfg", password="secret")
        caster = EnvCaster()
        report = caster.cast(profile.variables, "json")
        assert report.success_count == 1
        assert report.results[0].casted == {"max": 100, "min": 0}

    def test_cast_partial_failure_reported(self, storage):
        _save_profile(storage, "mixed", {"NUM": "42", "BAD": "not_a_number"})
        profile = storage.load_profile("mixed", password="secret")
        caster = EnvCaster()
        report = caster.cast(profile.variables, "int")
        assert report.success_count == 1
        assert report.failure_count == 1
        assert report.has_failures
