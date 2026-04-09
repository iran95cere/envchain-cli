"""Tests for envchain.cli_rotation."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from envchain.cli_rotation import RotationCommand
from envchain.rotation import RotationRecord


@pytest.fixture()
def mock_storage():
    return MagicMock()


@pytest.fixture()
def cmd(mock_storage):
    return RotationCommand(mock_storage)


class TestRotationCommand:
    def test_run_no_profiles_exits(self, cmd):
        with pytest.raises(SystemExit) as exc_info:
            cmd.run([])
        assert exc_info.value.code == 1

    def test_run_password_mismatch_exits(self, cmd):
        with patch("getpass.getpass", side_effect=["old", "new1", "new2"]):
            with pytest.raises(SystemExit) as exc_info:
                cmd.run(["dev"])
        assert exc_info.value.code == 1

    def test_run_success_prints_record(self, cmd, capsys):
        record = RotationRecord(profile_name="dev")
        with patch.object(
            cmd._rotator, "rotate", return_value=record
        ) as mock_rotate:
            with patch("getpass.getpass", side_effect=["old", "new", "new"]):
                cmd.run(["dev"], note="test")

        mock_rotate.assert_called_once_with("dev", "old", "new", note="test")
        out = capsys.readouterr().out
        assert "dev" in out

    def test_run_rotation_error_exits(self, cmd):
        with patch.object(
            cmd._rotator, "rotate", side_effect=ValueError("not found")
        ):
            with patch("getpass.getpass", side_effect=["old", "new", "new"]):
                with pytest.raises(SystemExit) as exc_info:
                    cmd.run(["dev"])
        assert exc_info.value.code == 1
