"""
Tests for profile CLI entry points.
"""

import pytest
import json
import sys
from unittest.mock import patch, MagicMock, mock_open
from io import StringIO
from tools.config import ProfileManager, AccountProfile


class TestProfileCLIEntry:
    """Test profile CLI main() function."""
    
    @patch('sys.argv', ['profile_cli.py', 'list'])
    @patch('tools.profile_cli.ProfileManager')
    @patch('builtins.print')
    def test_list_command(self, mock_print, mock_pm_class):
        """Test list command."""
        from tools.profile_cli import main
        
        mock_manager = MagicMock()
        mock_manager.list_profiles.return_value = ['test1', 'test2']
        mock_manager.default_profile = 'test1'
        mock_pm_class.return_value = mock_manager
        
        main()
        
        mock_print.assert_called_once()
        output = mock_print.call_args[0][0]
        result = json.loads(output)
        assert result['status'] == 'success'
        assert len(result['result']['profiles']) == 2
    
    @patch('sys.argv', ['profile_cli.py', 'list'])
    @patch('tools.profile_cli.ProfileManager')
    @patch('builtins.print')
    def test_list_command_empty(self, mock_print, mock_pm_class):
        """Test list command with no profiles."""
        from tools.profile_cli import main
        
        mock_manager = MagicMock()
        mock_manager.list_profiles.return_value = []
        mock_manager.default_profile = None
        mock_pm_class.return_value = mock_manager
        
        main()
        
        mock_print.assert_called_once()
        output = mock_print.call_args[0][0]
        result = json.loads(output)
        assert result['status'] == 'success'
        assert result['result']['message'] == 'No profiles configured'
    
    @patch('sys.argv', ['profile_cli.py', 'add', '--name', 'test', '--imap-server', 'imap.test.com', '--username', 'test@test.com', '--password', 'pass'])
    @patch('tools.profile_cli.ProfileManager')
    @patch('builtins.print')
    def test_add_command(self, mock_print, mock_pm_class):
        """Test add command."""
        from tools.profile_cli import main
        
        mock_manager = MagicMock()
        mock_pm_class.return_value = mock_manager
        
        main()
        
        mock_manager.add_profile.assert_called_once()
        mock_print.assert_called_once()
    
    @patch('sys.argv', ['profile_cli.py', 'remove', '--name', 'test'])
    @patch('tools.profile_cli.ProfileManager')
    @patch('builtins.print')
    @patch('sys.exit')
    def test_remove_command(self, mock_exit, mock_print, mock_pm_class):
        """Test remove command."""
        from tools.profile_cli import main
        
        mock_manager = MagicMock()
        mock_manager.remove_profile.return_value = True
        mock_pm_class.return_value = mock_manager
        
        main()
        
        mock_manager.remove_profile.assert_called_once_with('test')
        mock_exit.assert_not_called()
    
    @patch('sys.argv', ['profile_cli.py', 'remove', '--name', 'nonexistent'])
    @patch('tools.profile_cli.ProfileManager')
    @patch('builtins.print')
    @patch('sys.exit')
    def test_remove_command_not_found(self, mock_exit, mock_print, mock_pm_class):
        """Test remove command when profile not found."""
        from tools.profile_cli import main
        
        mock_manager = MagicMock()
        mock_manager.remove_profile.return_value = False
        mock_pm_class.return_value = mock_manager
        
        main()
        
        mock_exit.assert_called_once_with(1)
    
    @patch('sys.argv', ['profile_cli.py', 'set-default', '--name', 'test'])
    @patch('tools.profile_cli.ProfileManager')
    @patch('builtins.print')
    @patch('sys.exit')
    def test_set_default_command(self, mock_exit, mock_print, mock_pm_class):
        """Test set-default command."""
        from tools.profile_cli import main
        
        mock_manager = MagicMock()
        mock_manager.set_default.return_value = True
        mock_pm_class.return_value = mock_manager
        
        main()
        
        mock_manager.set_default.assert_called_once_with('test')
        mock_exit.assert_not_called()
    
    @patch('sys.argv', ['profile_cli.py', 'set-default', '--name', 'nonexistent'])
    @patch('tools.profile_cli.ProfileManager')
    @patch('builtins.print')
    @patch('sys.exit')
    def test_set_default_command_not_found(self, mock_exit, mock_print, mock_pm_class):
        """Test set-default command when profile not found."""
        from tools.profile_cli import main
        
        mock_manager = MagicMock()
        mock_manager.set_default.return_value = False
        mock_pm_class.return_value = mock_manager
        
        main()
        
        mock_exit.assert_called_once_with(1)
    
    @patch('sys.argv', ['profile_cli.py', 'show', '--name', 'test'])
    @patch('tools.profile_cli.ProfileManager')
    @patch('builtins.print')
    @patch('sys.exit')
    def test_show_command(self, mock_exit, mock_print, mock_pm_class):
        """Test show command."""
        from tools.profile_cli import main
        
        mock_manager = MagicMock()
        mock_profile = AccountProfile(name='test', username='test@test.com')
        mock_manager.get_profile.return_value = mock_profile
        mock_pm_class.return_value = mock_manager
        
        main()
        
        mock_print.assert_called_once()
        output = mock_print.call_args[0][0]
        result = json.loads(output)
        assert result['status'] == 'success'
        assert result['result']['name'] == 'test'
        mock_exit.assert_not_called()
    
    def test_show_command_not_found(self):
        """Test show command when profile not found."""
        from tools.profile_cli import show_profile
        
        with patch('tools.profile_cli.ProfileManager') as mock_pm_class:
            mock_manager = MagicMock()
            mock_manager.get_profile.return_value = None
            mock_pm_class.return_value = mock_manager
            
            args = MagicMock()
            args.name = 'nonexistent'
            
            # show_profile calls sys.exit(1) directly, so we need to catch SystemExit
            with pytest.raises(SystemExit) as exc_info:
                show_profile(args)
            assert exc_info.value.code == 1
    
    def test_show_command_password_masking(self):
        """Test show command masks password."""
        from tools.profile_cli import show_profile
        
        with patch('tools.profile_cli.ProfileManager') as mock_pm_class:
            mock_manager = MagicMock()
            mock_profile = AccountProfile(name='test', username='test@test.com', password='secret')
            mock_manager.get_profile.return_value = mock_profile
            mock_pm_class.return_value = mock_manager
            
            args = MagicMock()
            args.name = 'test'
            
            with patch('builtins.print') as mock_print:
                show_profile(args)
                output = mock_print.call_args[0][0]
                result = json.loads(output)
                assert result['result']['password'] == '***'
    
    def test_no_command(self):
        """Test no command provided."""
        from tools.profile_cli import main
        
        with patch('sys.argv', ['profile_cli.py']):
            # argparse will call sys.exit(1) when no command
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1
    
    def test_main_entry_point(self):
        """Test main() entry point execution."""
        from tools.profile_cli import main
        
        with patch('sys.argv', ['profile_cli.py', 'list']):
            with patch('tools.profile_cli.ProfileManager') as mock_pm_class:
                with patch('builtins.print'):
                    mock_manager = MagicMock()
                    mock_manager.list_profiles.return_value = []
                    mock_manager.default_profile = None
                    mock_pm_class.return_value = mock_manager
                    
                    # Should execute without error
                    try:
                        main()
                    except SystemExit:
                        pass


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

