"""Tests for envchain.cli_patch."""
import sys
import pytest
from unittest.mock import MagicMock
from envchain.cli_patch import PatchCommand
from envchain.models import Profile


@pytest.fixture
def mock_storage():
    storage = MagicMock()
    profile = Profile(name='dev', variables={'FOO': 'bar', 'BAZ': 'qux'})
    storage.load_profile.return_value = profile
    return storage


@pytest.fixture
def cmd(mock_storage):
    return PatchCommand(storage=mock_storage, password='secret')


class TestPatchCommand:
    def test_set_applies_and_saves(self, cmd, mock_storage):
        cmd.run('dev', set_pairs=['FOO=new_val'], delete_keys=[])
        profile = mock_storage.save_profile.call_args[0][0]
        assert profile.variables['FOO'] == 'new_val'

    def test_delete_applies_and_saves(self, cmd, mock_storage):
        cmd.run('dev', set_pairs=[], delete_keys=['FOO'])
        profile = mock_storage.save_profile.call_args[0][0]
        assert 'FOO' not in profile.variables

    def test_no_ops_prints_message(self, cmd, mock_storage, capsys):
        cmd.run('dev', set_pairs=[], delete_keys=[])
        captured = capsys.readouterr()
        assert 'No operations' in captured.out
        mock_storage.save_profile.assert_not_called()

    def test_invalid_set_expression_exits(self, cmd, capsys):
        with pytest.raises(SystemExit):
            cmd.run('dev', set_pairs=['BADEXPR'], delete_keys=[])

    def test_missing_profile_exits(self, cmd, mock_storage):
        mock_storage.load_profile.return_value = None
        with pytest.raises(SystemExit):
            cmd.run('nonexistent', set_pairs=['X=1'], delete_keys=[])

    def test_skipped_ops_printed(self, cmd, mock_storage, capsys):
        # deleting a key that doesn't exist → skipped
        cmd.run('dev', set_pairs=[], delete_keys=['MISSING_KEY'])
        captured = capsys.readouterr()
        assert 'Skipped' in captured.out

    def test_output_shows_applied_count(self, cmd, capsys):
        cmd.run('dev', set_pairs=['FOO=x', 'BAZ=y'], delete_keys=[])
        captured = capsys.readouterr()
        assert '2 operation(s)' in captured.out
