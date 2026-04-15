"""Tests for ObfuscateCommand CLI wrapper."""
import base64
import sys
from unittest.mock import MagicMock

import pytest

from envchain.cli_obfuscate import ObfuscateCommand
from envchain.env_obfuscate import EnvObfuscator
from envchain.models import Profile


def _make_profile(vars_: dict) -> Profile:
    p = Profile(name="test", variables=dict(vars_))
    return p


@pytest.fixture()
def mock_storage():
    return MagicMock()


@pytest.fixture()
def cmd(mock_storage):
    return ObfuscateCommand(mock_storage)


class TestObfuscateCommand:
    def test_run_obfuscates_and_saves(self, cmd, mock_storage):
        profile = _make_profile({"KEY": "value"})
        mock_storage.load_profile.return_value = profile
        cmd.run("test", "pass")
        mock_storage.save_profile.assert_called_once()
        saved_profile = mock_storage.save_profile.call_args[0][0]
        assert list(saved_profile.variables.values())[0].startswith(EnvObfuscator.PREFIX)

    def test_run_dry_run_does_not_save(self, cmd, mock_storage, capsys):
        profile = _make_profile({"KEY": "value"})
        mock_storage.load_profile.return_value = profile
        cmd.run("test", "pass", dry_run=True)
        mock_storage.save_profile.assert_not_called()
        out = capsys.readouterr().out
        assert "dry-run" in out

    def test_run_missing_profile_exits(self, cmd, mock_storage):
        mock_storage.load_profile.return_value = None
        with pytest.raises(SystemExit):
            cmd.run("missing", "pass")

    def test_run_already_obfuscated_prints_message(self, cmd, mock_storage, capsys):
        encoded = EnvObfuscator.PREFIX + base64.b64encode(b"val").decode()
        profile = _make_profile({"KEY": encoded})
        mock_storage.load_profile.return_value = profile
        cmd.run("test", "pass")
        mock_storage.save_profile.assert_not_called()
        out = capsys.readouterr().out
        assert "nothing to do" in out

    def test_deobfuscate_restores_values(self, cmd, mock_storage):
        encoded = EnvObfuscator.PREFIX + base64.b64encode(b"secret").decode()
        profile = _make_profile({"KEY": encoded})
        mock_storage.load_profile.return_value = profile
        cmd.deobfuscate("test", "pass")
        mock_storage.save_profile.assert_called_once()
        saved_profile = mock_storage.save_profile.call_args[0][0]
        assert saved_profile.variables["KEY"] == "secret"

    def test_deobfuscate_dry_run_does_not_save(self, cmd, mock_storage, capsys):
        encoded = EnvObfuscator.PREFIX + base64.b64encode(b"secret").decode()
        profile = _make_profile({"KEY": encoded})
        mock_storage.load_profile.return_value = profile
        cmd.deobfuscate("test", "pass", dry_run=True)
        mock_storage.save_profile.assert_not_called()
        out = capsys.readouterr().out
        assert "dry-run" in out

    def test_deobfuscate_missing_profile_exits(self, cmd, mock_storage):
        mock_storage.load_profile.return_value = None
        with pytest.raises(SystemExit):
            cmd.deobfuscate("missing", "pass")
