"""Tests for envchain.cli_encode."""
import sys
from unittest.mock import MagicMock, patch

import pytest

from envchain.cli_encode import EncodeCommand
from envchain.models import Profile


def _make_profile(name: str, vars_: dict) -> Profile:
    p = Profile(name=name)
    p.variables = dict(vars_)
    return p


@pytest.fixture
def mock_storage():
    s = MagicMock()
    s.load_profile.return_value = _make_profile("dev", {"KEY": "hello", "PORT": "80"})
    return s


@pytest.fixture
def cmd(mock_storage):
    return EncodeCommand(mock_storage)


class TestEncodeCommand:
    def test_run_encodes_and_saves(self, cmd, mock_storage):
        cmd.run("dev", "base64")
        mock_storage.save_profile.assert_called_once()

    def test_run_dry_run_does_not_save(self, cmd, mock_storage):
        cmd.run("dev", "base64", dry_run=True)
        mock_storage.save_profile.assert_not_called()

    def test_run_unknown_format_exits(self, cmd):
        with pytest.raises(SystemExit):
            cmd.run("dev", "unknown_fmt")

    def test_run_missing_profile_exits(self, cmd, mock_storage):
        mock_storage.load_profile.return_value = None
        with pytest.raises(SystemExit):
            cmd.run("missing", "base64")

    def test_run_decode_flag(self, cmd, mock_storage):
        import base64
        encoded_vars = {
            "KEY": base64.b64encode(b"hello").decode(),
            "PORT": base64.b64encode(b"80").decode(),
        }
        mock_storage.load_profile.return_value = _make_profile("dev", encoded_vars)
        cmd.run("dev", "base64", decode=True)
        mock_storage.save_profile.assert_called_once()
        saved = mock_storage.save_profile.call_args[0][0]
        assert saved.variables["KEY"] == "hello"

    def test_list_formats_prints_output(self, cmd, capsys):
        cmd.list_formats()
        out = capsys.readouterr().out
        assert "base64" in out
        assert "url" in out
        assert "hex" in out

    def test_run_no_changes_prints_message(self, capsys):
        """A profile where values are already empty strings stays unchanged."""
        storage = MagicMock()
        # Use a value that encodes to itself (empty string -> base64 changes it)
        # We test the 'no changes' path by patching the encoder instead.
        from envchain.env_encode import EncodeReport
        storage.load_profile.return_value = _make_profile("dev", {"K": "v"})
        c = EncodeCommand(storage)
        with patch(
            "envchain.cli_encode.EnvEncoder.encode",
            return_value=EncodeReport(results=[]),
        ):
            c.run("dev", "base64")
        out = capsys.readouterr().out
        assert "No values changed" in out
