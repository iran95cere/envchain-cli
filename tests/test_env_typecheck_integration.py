"""Integration tests for EnvTypeChecker with real storage."""
import pytest
from pathlib import Path

from envchain.storage import EnvStorage
from envchain.models import Profile
from envchain.env_typecheck import EnvTypeChecker, VarType


@pytest.fixture
def tmp_dir(tmp_path):
    return tmp_path


@pytest.fixture
def storage(tmp_dir):
    return EnvStorage(str(tmp_dir))


def _save_profile(storage: EnvStorage, name: str, variables: dict, password: str) -> None:
    p = Profile(name=name, variables=variables)
    storage.save_profile(p, password)


class TestTypeCheckerIntegration:
    def test_check_all_against_saved_profile(self, storage):
        _save_profile(storage, "prod", {"PORT": "443", "DEBUG": "false"}, "pw")
        profile = storage.load_profile("prod", "pw")
        assert profile is not None

        checker = EnvTypeChecker()
        schema = {"PORT": VarType.INTEGER, "DEBUG": VarType.BOOLEAN}
        report = checker.check_all(profile.variables, schema)

        assert not report.has_failures
        assert report.passed_count == 2

    def test_check_all_detects_type_mismatch(self, storage):
        _save_profile(storage, "staging", {"TIMEOUT": "thirty"}, "pw")
        profile = storage.load_profile("staging", "pw")
        assert profile is not None

        checker = EnvTypeChecker()
        report = checker.check_all(profile.variables, {"TIMEOUT": VarType.INTEGER})

        assert report.has_failures
        assert report.failures()[0].name == "TIMEOUT"

    def test_string_type_always_passes_for_any_value(self, storage):
        _save_profile(storage, "dev", {"NOTES": "some free text!@#$"}, "pw")
        profile = storage.load_profile("dev", "pw")
        assert profile is not None

        checker = EnvTypeChecker()
        report = checker.check_all(profile.variables, {"NOTES": VarType.STRING})
        assert not report.has_failures

    def test_empty_schema_produces_empty_report(self, storage):
        _save_profile(storage, "empty", {"X": "1"}, "pw")
        profile = storage.load_profile("empty", "pw")
        assert profile is not None

        checker = EnvTypeChecker()
        report = checker.check_all(profile.variables, {})
        assert len(report.results) == 0
        assert not report.has_failures
