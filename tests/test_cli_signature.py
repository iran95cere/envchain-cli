"""Tests for envchain.cli_signature."""
from __future__ import annotations

import sys
from unittest.mock import MagicMock

import pytest

from envchain.cli_signature import SignatureCommand
from envchain.models import Profile


def _make_profile(name: str, vars_dict=None) -> Profile:
    p = Profile(name=name)
    for k, v in (vars_dict or {}).items():
        p.add_var(k, v)
    return p


@pytest.fixture
def mock_storage():
    storage = MagicMock()
    storage.list_profiles.return_value = ["dev", "prod"]
    return storage


@pytest.fixture
def cmd(mock_storage):
    return SignatureCommand(mock_storage, secret_key="test-secret")


class TestSignatureCommand:
    def test_sign_prints_confirmation(self, cmd, mock_storage, capsys):
        mock_storage.load_profile.return_value = _make_profile("dev", {"K": "v"})
        cmd.sign("dev")
        out = capsys.readouterr().out
        assert "Signed" in out
        assert "dev" in out

    def test_sign_missing_profile_exits(self, cmd, mock_storage):
        mock_storage.load_profile.return_value = None
        with pytest.raises(SystemExit):
            cmd.sign("ghost")

    def test_verify_valid_profile(self, cmd, mock_storage, capsys):
        mock_storage.load_profile.return_value = _make_profile("dev", {"K": "v"})
        cmd.sign("dev")
        mock_storage.load_profile.return_value = _make_profile("dev", {"K": "v"})
        cmd.verify("dev")
        out = capsys.readouterr().out
        assert "valid" in out.lower()

    def test_verify_missing_profile_exits(self, cmd, mock_storage):
        mock_storage.load_profile.return_value = None
        with pytest.raises(SystemExit):
            cmd.verify("ghost")

    def test_verify_tampered_profile_exits(self, cmd, mock_storage):
        mock_storage.load_profile.return_value = _make_profile("dev", {"K": "original"})
        cmd.sign("dev")
        mock_storage.load_profile.return_value = _make_profile("dev", {"K": "tampered"})
        with pytest.raises(SystemExit):
            cmd.verify("dev")

    def test_remove_signed_profile(self, cmd, mock_storage, capsys):
        mock_storage.load_profile.return_value = _make_profile("dev", {})
        cmd.sign("dev")
        cmd.remove("dev")
        out = capsys.readouterr().out
        assert "removed" in out.lower()

    def test_remove_unsigned_profile_prints_message(self, cmd, capsys):
        cmd.remove("nonexistent")
        out = capsys.readouterr().out
        assert "No signature" in out

    def test_list_signed_empty(self, cmd, capsys):
        cmd.list_signed()
        out = capsys.readouterr().out
        assert "No signed" in out

    def test_list_signed_shows_names(self, cmd, mock_storage, capsys):
        mock_storage.load_profile.return_value = _make_profile("dev", {})
        cmd.sign("dev")
        cmd.list_signed()
        out = capsys.readouterr().out
        assert "dev" in out
