"""
Tests for CLI main() entry points.
"""

import pytest
import json
import sys
from unittest.mock import patch, MagicMock, mock_open
from io import StringIO


class TestIMAPCLIMain:
    """Test IMAP CLI main() function."""
    
    def test_describe_flag(self):
        """Test --describe flag."""
        from tools.imap.cli import get_plugin_description
        
        # Test the function directly instead of through main()
        description = get_plugin_description()
        
        assert 'plugin' in description
        assert 'commands' in description
        assert description['plugin']['name'] == 'imap'
    
    @patch('sys.argv', ['cli.py'])
    @patch('sys.exit')
    def test_no_command(self, mock_exit):
        """Test no command provided."""
        from tools.imap.cli import main
        
        try:
            main()
        except SystemExit:
            pass
        
        assert mock_exit.called
    
    @patch('sys.argv', ['cli.py', 'list-mailboxes', '--account', 'test'])
    @patch('tools.imap.cli.list_mailboxes')
    @patch('sys.exit')
    @patch('builtins.print')
    def test_list_mailboxes_command(self, mock_print, mock_exit, mock_list):
        """Test list-mailboxes command."""
        from tools.imap.cli import main
        
        mock_list.return_value = {'status': 'success', 'result': {'mailboxes': []}}
        
        main()
        
        mock_list.assert_called_once()
        mock_print.assert_called_once()
        mock_exit.assert_called_once_with(0)
    
    @patch('sys.argv', ['cli.py', 'search', '--criteria', 'ALL', '--account', 'test'])
    @patch('tools.imap.cli.search')
    @patch('sys.exit')
    @patch('builtins.print')
    def test_search_command(self, mock_print, mock_exit, mock_search):
        """Test search command."""
        from tools.imap.cli import main
        
        mock_search.return_value = {'status': 'success', 'result': {'message_ids': []}}
        
        main()
        
        mock_search.assert_called_once()
        mock_exit.assert_called_once_with(0)
    
    @patch('sys.argv', ['cli.py', 'unknown-command'])
    @patch('sys.exit')
    @patch('builtins.print')
    def test_unknown_command(self, mock_print, mock_exit):
        """Test unknown command."""
        from tools.imap.cli import main
        
        try:
            main()
        except SystemExit:
            pass
        
        # Should exit with error
        assert mock_exit.called
    
    @patch('sys.argv', ['cli.py', 'list-mailboxes', '--account', 'test'])
    @patch('tools.imap.cli.list_mailboxes')
    @patch('sys.exit')
    @patch('builtins.print')
    def test_error_result(self, mock_print, mock_exit, mock_list):
        """Test error result handling."""
        from tools.imap.cli import main
        
        mock_list.return_value = {'error': 'Connection failed'}
        
        main()
        
        mock_exit.assert_called_once_with(1)
    
    @patch('sys.argv', ['cli.py', 'list-mailboxes', '--account', 'test'])
    @patch('tools.imap.cli.list_mailboxes')
    @patch('sys.exit')
    @patch('builtins.print')
    def test_exception_handling(self, mock_print, mock_exit, mock_list):
        """Test exception handling in main()."""
        from tools.imap.cli import main
        
        mock_list.side_effect = Exception("Test error")
        
        main()
        
        mock_print.assert_called_once()
        mock_exit.assert_called_once_with(1)


class TestSMTPCLIMain:
    """Test SMTP CLI main() function."""
    
    def test_describe_flag(self):
        """Test --describe flag."""
        from tools.smtp.cli import get_plugin_description
        
        # Test the function directly instead of through main()
        description = get_plugin_description()
        
        assert 'plugin' in description
        assert 'commands' in description
        assert description['plugin']['name'] == 'smtp'
    
    @patch('sys.argv', ['cli.py'])
    @patch('sys.exit')
    def test_no_command(self, mock_exit):
        """Test no command provided."""
        from tools.smtp.cli import main
        
        try:
            main()
        except SystemExit:
            pass
        
        assert mock_exit.called
    
    @patch('sys.argv', ['cli.py', 'send', '--to', 'test@example.com', '--subject', 'Test', '--body', 'Hello', '--account', 'test'])
    @patch('tools.smtp.cli.send')
    @patch('sys.exit')
    @patch('builtins.print')
    def test_send_command(self, mock_print, mock_exit, mock_send):
        """Test send command."""
        from tools.smtp.cli import main
        
        mock_send.return_value = {'status': 'success'}
        
        main()
        
        mock_send.assert_called_once()
        mock_exit.assert_called_once_with(0)
    
    @patch('sys.argv', ['cli.py', 'unknown-command'])
    @patch('sys.exit')
    @patch('builtins.print')
    def test_unknown_command(self, mock_print, mock_exit):
        """Test unknown command."""
        from tools.smtp.cli import main
        
        try:
            main()
        except SystemExit:
            pass
        
        assert mock_exit.called
    
    @patch('sys.argv', ['cli.py', 'send', '--to', 'test@example.com', '--subject', 'Test', '--body', 'Hello', '--account', 'test'])
    @patch('tools.smtp.cli.send')
    @patch('sys.exit')
    @patch('builtins.print')
    def test_exception_handling(self, mock_print, mock_exit, mock_send):
        """Test exception handling in main()."""
        from tools.smtp.cli import main
        
        mock_send.side_effect = Exception("Test error")
        
        main()
        
        mock_print.assert_called_once()
        mock_exit.assert_called_once_with(1)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

