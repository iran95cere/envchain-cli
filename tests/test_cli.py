"""Tests for CLI interface."""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

from envchain.cli import EnvChainCLI
from envchain.models import Profile
from envchain.crypto import EnvCrypto


class TestEnvChainCLI:
    """Test suite for EnvChainCLI."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def cli(self, temp_dir):
        """Create CLI instance with temp storage."""
        return EnvChainCLI(storage_dir=temp_dir)

    @patch('getpass.getpass')
    def test_init_profile(self, mock_getpass, cli):
        """Test initializing a new profile."""
        mock_getpass.side_effect = ['testpass', 'testpass']
        
        cli.init_profile('test-profile', 'Test description')
        
        assert cli.storage.profile_exists('test-profile')

    @patch('getpass.getpass')
    def test_init_profile_password_mismatch(self, mock_getpass, cli):
        """Test profile init fails with mismatched passwords."""
        mock_getpass.side_effect = ['testpass', 'wrongpass']
        
        with pytest.raises(SystemExit):
            cli.init_profile('test-profile')

    @patch('getpass.getpass')
    def test_set_and_get_var(self, mock_getpass, cli):
        """Test setting and getting a variable."""
        # Init profile
        mock_getpass.side_effect = ['testpass', 'testpass']
        cli.init_profile('test-profile')
        
        # Set variable
        mock_getpass.side_effect = ['testpass']
        cli.set_var('test-profile', 'API_KEY', 'secret123')
        
        # Get variable
        mock_getpass.side_effect = ['testpass']
        with patch('builtins.print') as mock_print:
            cli.get_var('test-profile', 'API_KEY')
            mock_print.assert_called_with('secret123')

    @patch('getpass.getpass')
    def test_get_nonexistent_var(self, mock_getpass, cli):
        """Test getting a non-existent variable fails."""
        mock_getpass.side_effect = ['testpass', 'testpass']
        cli.init_profile('test-profile')
        
        mock_getpass.side_effect = ['testpass']
        with pytest.raises(SystemExit):
            cli.get_var('test-profile', 'NONEXISTENT')

    @patch('getpass.getpass')
    def test_list_profiles(self, mock_getpass, cli):
        """Test listing profiles."""
        mock_getpass.side_effect = ['pass1', 'pass1', 'pass2', 'pass2']
        cli.init_profile('profile1')
        cli.init_profile('profile2')
        
        with patch('builtins.print') as mock_print:
            cli.list_profiles()
            calls = [str(call) for call in mock_print.call_args_list]
            assert any('profile1' in call for call in calls)
            assert any('profile2' in call for call in calls)

    @patch('getpass.getpass')
    def test_list_vars(self, mock_getpass, cli):
        """Test listing variables in a profile."""
        mock_getpass.side_effect = ['testpass', 'testpass']
        cli.init_profile('test-profile')
        
        mock_getpass.side_effect = ['testpass', 'testpass']
        cli.set_var('test-profile', 'VAR1', 'value1')
        cli.set_var('test-profile', 'VAR2', 'value2')
        
        mock_getpass.side_effect = ['testpass']
        with patch('builtins.print') as mock_print:
            cli.list_vars('test-profile')
            calls = [str(call) for call in mock_print.call_args_list]
            assert any('VAR1' in call for call in calls)
            assert any('VAR2' in call for call in calls)

    @patch('getpass.getpass')
    def test_wrong_password_fails(self, mock_getpass, cli):
        """Test that wrong password fails to load profile."""
        mock_getpass.side_effect = ['correctpass', 'correctpass']
        cli.init_profile('test-profile')
        
        mock_getpass.side_effect = ['wrongpass']
        with pytest.raises(SystemExit):
            cli.get_var('test-profile', 'ANY_VAR')
