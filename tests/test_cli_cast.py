"""Tests for envchain.cli_cast."""
import sys
import pytest
from unittest.mock import MagicMock
from envchain.cli_cast import CastCommand
from envchain.models import Profile


def _make_profile(vars: dict) -> Profile:
    p = Profile(name="test", variables=vars)
    return p


@pytest.fixture
def mock_storage():
    s = MagicMock()
    s.load_profile.return_value = _make_profile({"PORT": "8080", "DEBUG": "true"})
    s.list_profiles.return_value = ["test"]
    return s


@pytest.fixture
def cmd(mock_storage):
    return CastCommand(mock_storage, "test")


class TestCastCommand:
    def test_run_success_prints_ok(self, cmd, capsys):
        cmd.run("int")
        out = capsys.readouterr().out
        assert "ok" in out

    def test_run_invalid_type_exits(self, cmd):
        with pytest.raises(SystemExit) as exc:
            cmd.run("bytes")
        assert exc.value.code == 1

    def test_run_missing_profile_exits(self, mock_storage):
        mock_storage.load_profile.return_value = None
        cmd = CastCommand(mock_storage, "missing")
        with pytest.raises(SystemExit) as exc:
            cmd.run("int")
        assert exc.value.code == 1

    def test_run_failure_exits_with_2(self, mock_storage, capsys):
        mock_storage.load_profile.return_value = _make_profile({"X": "not_an_int"})
        cmd = CastCommand(mock_storage, "test")
        with pytest.raises(SystemExit) as exc:
            cmd.run("int")
        assert exc.value.code == 2

    def test_run_fail_fast_exits_early(self, mock_storage):
        mock_storage.load_profile.return_value = _make_profile({"A": "bad", "B": "also_bad"})
        cmd = CastCommand(mock_storage, "test")
        with pytest.raises(SystemExit) as exc:
            cmd.run("int", fail_fast=True)
        assert exc.value.code == 2

    def test_list_types_prints_all(self, cmd, capsys):
        cmd.list_types()
        out = capsys.readouterr().out
        for t in ("str", "int", "float", "bool", "json"):
            assert t in out
