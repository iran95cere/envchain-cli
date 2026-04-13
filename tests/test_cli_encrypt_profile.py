"""Tests for cli_encrypt_profile module."""
from __future__ import annotations

import sys
from io import StringIO
from unittest.mock import MagicMock, patch

import pytest

from envchain.cli_encrypt_profile import ReEncryptCommand
from envchain.env_encrypt_profile import ReEncryptReport, ReEncryptResult
from envchain.models import Profile


def _profile(name: str, vars_: dict) -> Profile:
    p = Profile(name=name)
    for k, v in vars_.items():
        p.add_var(k, v)
    return p


@pytest.fixture()
def mock_storage():
    storage = MagicMock()
    storage.list_profiles.return_value = ["dev", "prod"]
    storage.load_profile.side_effect = lambda name, pw: _profile(name, {"A": "1"})
    storage.save_profile.return_value = None
    return storage


@pytest.fixture()
def cmd(mock_storage):
    return ReEncryptCommand(mock_storage)


class TestReEncryptCommand:
    def test_run_no_profiles_exits(self, mock_storage):
        mock_storage.list_profiles.return_value = []
        cmd = ReEncryptCommand(mock_storage)
        with pytest.raises(SystemExit) as exc:
            with patch("getpass.getpass", return_value="pw"):
                cmd.run()
        assert exc.value.code == 1

    def test_run_unknown_profile_exits(self, cmd):
        with pytest.raises(SystemExit) as exc:
            with patch("getpass.getpass", return_value="pw"):
                cmd.run(profile_names=["nonexistent"])
        assert exc.value.code == 1

    def test_run_password_mismatch_exits(self, cmd):
        passwords = ["old", "new1", "new2"]
        with pytest.raises(SystemExit) as exc:
            with patch("getpass.getpass", side_effect=passwords):
                cmd.run(profile_names=["dev"])
        assert exc.value.code == 1

    def test_run_success_prints_ok(self, cmd, capsys):
        with patch("getpass.getpass", return_value="password"):
            cmd.run(profile_names=["dev"])
        captured = capsys.readouterr()
        assert "ok" in captured.out
        assert "dev" in captured.out

    def test_run_failure_exits_nonzero(self, mock_storage):
        mock_storage.load_profile.side_effect = RuntimeError("bad")
        cmd = ReEncryptCommand(mock_storage)
        with pytest.raises(SystemExit) as exc:
            with patch("getpass.getpass", return_value="password"):
                cmd.run(profile_names=["dev"])
        assert exc.value.code == 1
