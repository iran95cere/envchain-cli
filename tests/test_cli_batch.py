"""Tests for envchain.cli_batch."""
import json
import sys
import pytest
from unittest.mock import MagicMock

from envchain.cli_batch import BatchCommand
from envchain.models import Profile


def _make_profile(name='dev', variables=None):
    p = Profile(name=name)
    p.variables = variables or {'OLD': 'value'}
    return p


@pytest.fixture
def mock_storage():
    s = MagicMock()
    s.load_profile.return_value = _make_profile()
    return s


@pytest.fixture
def cmd(mock_storage):
    return BatchCommand(mock_storage)


class TestBatchCommand:
    def test_run_set_saves_profile(self, cmd, mock_storage):
        ops = json.dumps([{'action': 'set', 'name': 'NEW', 'value': 'v'}])
        cmd.run('dev', ops)
        mock_storage.save_profile.assert_called_once()

    def test_run_delete_saves_profile(self, cmd, mock_storage):
        ops = json.dumps([{'action': 'delete', 'name': 'OLD'}])
        cmd.run('dev', ops)
        mock_storage.save_profile.assert_called_once()

    def test_invalid_json_exits(self, cmd, capsys):
        with pytest.raises(SystemExit):
            cmd.run('dev', 'not-json')
        out = capsys.readouterr().err
        assert 'Invalid JSON' in out

    def test_missing_action_key_exits(self, cmd, capsys):
        ops = json.dumps([{'name': 'X', 'value': '1'}])  # missing 'action'
        with pytest.raises(SystemExit):
            cmd.run('dev', ops)
        out = capsys.readouterr().err
        assert 'Missing key' in out

    def test_unknown_profile_exits(self, mock_storage, capsys):
        mock_storage.load_profile.return_value = None
        cmd = BatchCommand(mock_storage)
        ops = json.dumps([{'action': 'set', 'name': 'X', 'value': '1'}])
        with pytest.raises(SystemExit):
            cmd.run('missing', ops)
        out = capsys.readouterr().err
        assert 'not found' in out

    def test_run_prints_summary(self, cmd, mock_storage, capsys):
        ops = json.dumps([{'action': 'set', 'name': 'Z', 'value': '99'}])
        cmd.run('dev', ops)
        out = capsys.readouterr().out
        assert 'applied' in out
