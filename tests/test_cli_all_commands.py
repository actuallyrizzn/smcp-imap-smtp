"""
Tests for all CLI command paths in main().
"""

import pytest
from unittest.mock import patch, MagicMock
from tools.imap.cli import main as imap_main
from tools.smtp.cli import main as smtp_main


class TestIMAPCLIAllCommands:
    """Test all IMAP CLI commands through main()."""
    
    @patch('sys.argv', ['cli.py', 'fetch', '--message-id', '123', '--account', 'test'])
    @patch('tools.imap.cli.fetch')
    @patch('sys.exit')
    @patch('builtins.print')
    def test_fetch_command(self, mock_print, mock_exit, mock_fetch):
        """Test fetch command."""
        mock_fetch.return_value = {'status': 'success', 'result': {'id': '123'}}
        
        imap_main()
        
        mock_fetch.assert_called_once()
        mock_exit.assert_called_once_with(0)
    
    @patch('sys.argv', ['cli.py', 'mark-read', '--message-ids', '123', '--account', 'test'])
    @patch('tools.imap.cli.mark_read')
    @patch('sys.exit')
    @patch('builtins.print')
    def test_mark_read_command(self, mock_print, mock_exit, mock_mark):
        """Test mark-read command."""
        mock_mark.return_value = {'status': 'success'}
        
        imap_main()
        
        mock_mark.assert_called_once()
        mock_exit.assert_called_once_with(0)
    
    @patch('sys.argv', ['cli.py', 'mark-unread', '--message-ids', '123', '--account', 'test'])
    @patch('tools.imap.cli.mark_unread')
    @patch('sys.exit')
    @patch('builtins.print')
    def test_mark_unread_command(self, mock_print, mock_exit, mock_mark):
        """Test mark-unread command."""
        mock_mark.return_value = {'status': 'success'}
        
        imap_main()
        
        mock_mark.assert_called_once()
        mock_exit.assert_called_once_with(0)
    
    @patch('sys.argv', ['cli.py', 'delete', '--message-ids', '123', '--account', 'test'])
    @patch('tools.imap.cli.delete')
    @patch('sys.exit')
    @patch('builtins.print')
    def test_delete_command(self, mock_print, mock_exit, mock_delete):
        """Test delete command."""
        mock_delete.return_value = {'status': 'success'}
        
        imap_main()
        
        mock_delete.assert_called_once()
        mock_exit.assert_called_once_with(0)
    
    @patch('sys.argv', ['cli.py', 'move', '--message-ids', '123', '--target-mailbox', 'Archive', '--account', 'test'])
    @patch('tools.imap.cli.move')
    @patch('sys.exit')
    @patch('builtins.print')
    def test_move_command(self, mock_print, mock_exit, mock_move):
        """Test move command."""
        mock_move.return_value = {'status': 'success'}
        
        imap_main()
        
        mock_move.assert_called_once()
        mock_exit.assert_called_once_with(0)


class TestSMTPCLIAllCommands:
    """Test all SMTP CLI commands through main()."""
    
    @patch('sys.argv', ['cli.py', 'send-html', '--to', 'test@example.com', '--subject', 'Test', '--html-body', '<html>Test</html>', '--account', 'test'])
    @patch('tools.smtp.cli.send_html')
    @patch('sys.exit')
    @patch('builtins.print')
    def test_send_html_command(self, mock_print, mock_exit, mock_send):
        """Test send-html command."""
        mock_send.return_value = {'status': 'success'}
        
        smtp_main()
        
        mock_send.assert_called_once()
        mock_exit.assert_called_once_with(0)
    
    @patch('sys.argv', ['cli.py', 'send-with-attachment', '--to', 'test@example.com', '--subject', 'Test', '--body', 'Hello', '--attachments', 'file.txt', '--account', 'test'])
    @patch('tools.smtp.cli.send_with_attachment')
    @patch('sys.exit')
    @patch('builtins.print')
    def test_send_with_attachment_command(self, mock_print, mock_exit, mock_send):
        """Test send-with-attachment command."""
        mock_send.return_value = {'status': 'success'}
        
        smtp_main()
        
        mock_send.assert_called_once()
        mock_exit.assert_called_once_with(0)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

