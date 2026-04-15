"""Tests for TypeCheckCommand CLI."""
import json
import sys
import pytest
from pathlib import Path
from unittest.mock import MagicMock

from envchain.cli_typecheck import TypeCheckCommand
from envchain.models import Profile
from envchain.env_typecheck import VarType


@pytest.fixture
def tmp_dir(tmp_path):
    return tmp_path


@pytest.fixture
def mock_storage():
    return MagicMock()


@pytest.fixture
def cmd(mock_storage):
    return TypeCheckCommand(mock_storage)


def _make_profile(variables: dict) -> Profile:
    p = Profile(name="dev", variables=variables)
    return p


class TestTypeCheckCommand:
    def test_run_all_pass_prints_summary(self, cmd, mock_storage, tmp_dir, capsys):
        schema = {"PORT": "integer"}
        schema_file = tmp_dir / "schema.json"
        schema_file.write_text(json.dumps(schema))
        mock_storage.load_profile.return_value = _make_profile({"PORT": "8080"})

        cmd.run("dev", str(schema_file), "secret")
        out = capsys.readouterr().out
        assert "Passed  : 1" in out
        assert "Failed  : 0" in out

    def test_run_failure_prints_failures(self, cmd, mock_storage, tmp_dir, capsys):
        schema = {"PORT": "integer"}
        schema_file = tmp_dir / "schema.json"
        schema_file.write_text(json.dumps(schema))
        mock_storage.load_profile.return_value = _make_profile({"PORT": "abc"})

        cmd.run("dev", str(schema_file), "secret")
        out = capsys.readouterr().out
        assert "Failed  : 1" in out
        assert "PORT" in out

    def test_run_strict_exits_on_failure(self, cmd, mock_storage, tmp_dir):
        schema = {"PORT": "integer"}
        schema_file = tmp_dir / "schema.json"
        schema_file.write_text(json.dumps(schema))
        mock_storage.load_profile.return_value = _make_profile({"PORT": "bad"})

        with pytest.raises(SystemExit) as exc:
            cmd.run("dev", str(schema_file), "secret", strict=True)
        assert exc.value.code == 2

    def test_run_missing_schema_exits(self, cmd, tmp_dir):
        with pytest.raises(SystemExit) as exc:
            cmd.run("dev", str(tmp_dir / "missing.json"), "secret")
        assert exc.value.code == 1

    def test_run_invalid_json_exits(self, cmd, tmp_dir):
        bad = tmp_dir / "bad.json"
        bad.write_text("not json")
        with pytest.raises(SystemExit) as exc:
            cmd.run("dev", str(bad), "secret")
        assert exc.value.code == 1

    def test_run_unknown_type_exits(self, cmd, tmp_dir):
        schema_file = tmp_dir / "schema.json"
        schema_file.write_text(json.dumps({"X": "unicorn"}))
        with pytest.raises(SystemExit) as exc:
            cmd.run("dev", str(schema_file), "secret")
        assert exc.value.code == 1

    def test_run_profile_not_found_exits(self, cmd, mock_storage, tmp_dir):
        schema_file = tmp_dir / "schema.json"
        schema_file.write_text(json.dumps({"X": "string"}))
        mock_storage.load_profile.return_value = None
        with pytest.raises(SystemExit) as exc:
            cmd.run("dev", str(schema_file), "secret")
        assert exc.value.code == 1

    def test_list_types_prints_all(self, cmd, capsys):
        cmd.list_types()
        out = capsys.readouterr().out
        for vt in VarType:
            assert vt.value in out
