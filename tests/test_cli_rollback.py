"""Tests for envchain.cli_rollback."""
from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch

from envchain.cli_rollback import RollbackCommand
from envchain.env_rollback import RollbackRecord
from envchain.snapshot import Snapshot


def _snap(label, profile="dev", variables=None):
    s = Snapshot(profile=profile, label=label, variables=variables or {})
    return s


@pytest.fixture()
def mock_storage():
    return MagicMock()


@pytest.fixture()
def cmd(mock_storage, tmp_path):
    with patch("envchain.cli_rollback.SnapshotManager") as MockSM, \
         patch("envchain.cli_rollback.RollbackManager") as MockRM:
        instance_sm = MockSM.return_value
        instance_rm = MockRM.return_value
        instance_rm.list_snapshots.return_value = [
            _snap("snap-1"),
            _snap("snap-2"),
        ]
        instance_rm.rollback.return_value = RollbackRecord(
            profile="dev",
            rolled_back_to="snap-1",
            previous_vars={"K": "v"},
        )
        c = RollbackCommand(mock_storage, str(tmp_path))
        c._mgr = instance_rm
        yield c


class TestRollbackCommand:
    def test_list_snapshots_prints_labels(self, cmd, capsys):
        cmd.list_snapshots("dev")
        out = capsys.readouterr().out
        assert "snap-1" in out
        assert "snap-2" in out

    def test_list_snapshots_empty_prints_message(self, cmd, capsys):
        cmd._mgr.list_snapshots.return_value = []
        cmd.list_snapshots("dev")
        out = capsys.readouterr().out
        assert "No snapshots" in out

    def test_run_success_prints_confirmation(self, cmd, capsys):
        cmd.run("dev", "snap-1", "pw")
        out = capsys.readouterr().out
        assert "snap-1" in out
        assert "dev" in out

    def test_run_unknown_snapshot_exits(self, cmd):
        cmd._mgr.rollback.side_effect = KeyError("snap-99 not found")
        with pytest.raises(SystemExit) as exc_info:
            cmd.run("dev", "snap-99", "pw")
        assert exc_info.value.code == 1

    def test_dry_run_does_not_call_rollback(self, cmd, capsys):
        cmd.run("dev", "snap-1", "pw", dry_run=True)
        cmd._mgr.rollback.assert_not_called()
        out = capsys.readouterr().out
        assert "dry-run" in out

    def test_dry_run_missing_snapshot_exits(self, cmd):
        cmd._mgr.list_snapshots.return_value = []
        with pytest.raises(SystemExit) as exc_info:
            cmd.run("dev", "snap-missing", "pw", dry_run=True)
        assert exc_info.value.code == 1
