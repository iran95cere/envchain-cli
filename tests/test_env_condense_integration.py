"""Integration tests for condense: full roundtrip with real storage."""
import pytest
import tempfile
import os
from envchain.storage import EnvStorage
from envchain.models import Profile
from envchain.env_condense import EnvCondenser
from envchain.cli_condense import CondenseCommand


@pytest.fixture
def tmp_dir():
    with tempfile.TemporaryDirectory() as d:
        yield d


@pytest.fixture
def storage(tmp_dir):
    return EnvStorage(tmp_dir)


def _save_profile(storage, name, variables, password="pw"):
    p = Profile(name=name)
    p.variables = variables
    storage.save_profile(p, password)
    return p


class TestCondenseIntegration:
    def test_condense_removes_empty_and_saves(self, storage):
        _save_profile(storage, "prod", {"A": "1", "B": "", "C": "val"}, password="pw")
        cmd = CondenseCommand(storage)
        cmd.run("prod", "pw")
        loaded = storage.load_profile("prod", "pw")
        assert "B" not in loaded.variables
        assert "A" in loaded.variables
        assert "C" in loaded.variables

    def test_condense_removes_case_duplicates(self, storage):
        _save_profile(
            storage, "staging",
            {"HOST": "a", "host": "b", "PORT": "8080"},
            password="pw"
        )
        cmd = CondenseCommand(storage)
        cmd.run("staging", "pw")
        loaded = storage.load_profile("staging", "pw")
        lower_keys = [k.lower() for k in loaded.variables]
        assert len(lower_keys) == len(set(lower_keys)), "Duplicate case keys remain"

    def test_condense_dry_run_does_not_modify(self, storage):
        original_vars = {"X": "1", "Y": "", "Z": "3"}
        _save_profile(storage, "test", original_vars, password="pw")
        cmd = CondenseCommand(storage)
        cmd.run("test", "pw", dry_run=True)
        loaded = storage.load_profile("test", "pw")
        assert loaded.variables == original_vars
