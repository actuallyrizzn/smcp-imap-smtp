"""
Tests for CLI error cleanup paths (disconnect error handling).
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from tools.imap.cli import list_mailboxes, search, fetch, mark_read, mark_unread, delete, move
from tools.smtp.cli import send, send_html, send_with_attachment


class TestCLIErrorCleanup:
    """Test CLI error cleanup paths."""
    
    @patch('tools.imap.cli._auto_connect')
    @patch('tools.imap.imap_client.get_connection')
    @patch('tools.imap.imap_client.set_connection')
    def test_list_mailboxes_disconnect_error(self, mock_set, mock_get, mock_auto_connect):
        """Test list_mailboxes when disconnect fails."""
        mock_conn = MagicMock()
        mock_conn.list_mailboxes.return_value = []
        mock_conn.disconnect.side_effect = Exception("Disconnect failed")
        mock_auto_connect.return_value = (mock_conn, True)
        mock_get.return_value = None
        
        # Should not raise, disconnect error is caught
        result = list_mailboxes({'account': 'test'})
        
        assert result['status'] == 'success'
    
    @patch('tools.imap.cli._auto_connect')
    @patch('tools.imap.imap_client.get_connection')
    @patch('tools.imap.imap_client.set_connection')
    def test_search_disconnect_error(self, mock_set, mock_get, mock_auto_connect):
        """Test search when disconnect fails."""
        mock_conn = MagicMock()
        mock_conn.select_mailbox.return_value = {}
        mock_conn.search.return_value = [1, 2, 3]
        mock_conn.disconnect.side_effect = Exception("Disconnect failed")
        mock_auto_connect.return_value = (mock_conn, True)
        mock_get.return_value = None
        
        result = search({'criteria': 'ALL', 'account': 'test'})
        
        assert result['status'] == 'success'
    
    @patch('tools.imap.cli._auto_connect')
    @patch('tools.imap.imap_client.get_connection')
    @patch('tools.imap.imap_client.set_connection')
    def test_fetch_disconnect_error(self, mock_set, mock_get, mock_auto_connect):
        """Test fetch when disconnect fails."""
        mock_conn = MagicMock()
        mock_conn.select_mailbox.return_value = {}
        mock_conn.fetch_email.return_value = {'id': '123', 'subject': 'Test'}
        mock_conn.disconnect.side_effect = Exception("Disconnect failed")
        mock_auto_connect.return_value = (mock_conn, True)
        mock_get.return_value = None
        
        result = fetch({'message_id': '123', 'account': 'test'})
        
        assert result['status'] == 'success'
    
    @patch('tools.imap.cli._auto_connect')
    @patch('tools.imap.imap_client.get_connection')
    @patch('tools.imap.imap_client.set_connection')
    def test_mark_read_disconnect_error(self, mock_set, mock_get, mock_auto_connect):
        """Test mark_read when disconnect fails."""
        mock_conn = MagicMock()
        mock_conn.select_mailbox.return_value = {}
        mock_conn.mark_read.return_value = None
        mock_conn.disconnect.side_effect = Exception("Disconnect failed")
        mock_auto_connect.return_value = (mock_conn, True)
        mock_get.return_value = None
        
        result = mark_read({'message_ids': ['123'], 'account': 'test', 'sandbox': False})
        
        assert result['status'] == 'success'
    
    @patch('tools.imap.cli._auto_connect')
    @patch('tools.imap.imap_client.get_connection')
    @patch('tools.imap.imap_client.set_connection')
    def test_mark_unread_disconnect_error(self, mock_set, mock_get, mock_auto_connect):
        """Test mark_unread when disconnect fails."""
        mock_conn = MagicMock()
        mock_conn.select_mailbox.return_value = {}
        mock_conn.mark_unread.return_value = None
        mock_conn.disconnect.side_effect = Exception("Disconnect failed")
        mock_auto_connect.return_value = (mock_conn, True)
        mock_get.return_value = None
        
        result = mark_unread({'message_ids': ['123'], 'account': 'test', 'sandbox': False})
        
        assert result['status'] == 'success'
    
    @patch('tools.imap.cli._auto_connect')
    @patch('tools.imap.imap_client.get_connection')
    @patch('tools.imap.imap_client.set_connection')
    def test_delete_disconnect_error(self, mock_set, mock_get, mock_auto_connect):
        """Test delete when disconnect fails."""
        mock_conn = MagicMock()
        mock_conn.select_mailbox.return_value = {}
        mock_conn.delete.return_value = None
        mock_conn.disconnect.side_effect = Exception("Disconnect failed")
        mock_auto_connect.return_value = (mock_conn, True)
        mock_get.return_value = None
        
        result = delete({'message_ids': ['123'], 'account': 'test', 'sandbox': False})
        
        assert result['status'] == 'success'
    
    @patch('tools.imap.cli._auto_connect')
    @patch('tools.imap.imap_client.get_connection')
    @patch('tools.imap.imap_client.set_connection')
    def test_move_disconnect_error(self, mock_set, mock_get, mock_auto_connect):
        """Test move when disconnect fails."""
        mock_conn = MagicMock()
        mock_conn.select_mailbox.return_value = {}
        mock_conn.move.return_value = None
        mock_conn.disconnect.side_effect = Exception("Disconnect failed")
        mock_auto_connect.return_value = (mock_conn, True)
        mock_get.return_value = None
        
        result = move({'message_ids': ['123'], 'target_mailbox': 'Archive', 'account': 'test', 'sandbox': False})
        
        assert result['status'] == 'success'
    
    @patch('tools.imap.cli._auto_connect')
    @patch('tools.imap.imap_client.get_connection')
    @patch('tools.imap.imap_client.set_connection')
    def test_list_mailboxes_operation_error_cleanup(self, mock_set, mock_get, mock_auto_connect):
        """Test list_mailboxes cleanup when operation fails."""
        mock_conn = MagicMock()
        mock_conn.list_mailboxes.side_effect = Exception("List failed")
        mock_conn.disconnect.side_effect = Exception("Disconnect failed")
        mock_auto_connect.return_value = (mock_conn, True)
        mock_get.return_value = None
        
        result = list_mailboxes({'account': 'test'})
        
        assert 'error' in result
    
    @patch('tools.smtp.cli._auto_connect')
    @patch('tools.smtp.smtp_client.get_connection')
    @patch('tools.smtp.smtp_client.set_connection')
    def test_send_disconnect_error(self, mock_set, mock_get, mock_auto_connect):
        """Test send when disconnect fails."""
        mock_conn = MagicMock()
        mock_conn.send_email.return_value = {'sent': True}
        mock_conn.disconnect.side_effect = Exception("Disconnect failed")
        mock_auto_connect.return_value = (mock_conn, True)
        mock_get.return_value = None
        
        result = send({
            'to': ['test@test.com'],
            'subject': 'Test',
            'body': 'Body',
            'account': 'test'
        })
        
        assert result['status'] == 'success'
    
    @patch('tools.smtp.cli._auto_connect')
    @patch('tools.smtp.smtp_client.get_connection')
    @patch('tools.smtp.smtp_client.set_connection')
    def test_send_html_disconnect_error(self, mock_set, mock_get, mock_auto_connect):
        """Test send_html when disconnect fails."""
        mock_conn = MagicMock()
        mock_conn.send_email.return_value = {'sent': True}
        mock_conn.disconnect.side_effect = Exception("Disconnect failed")
        mock_auto_connect.return_value = (mock_conn, True)
        mock_get.return_value = None
        
        result = send_html({
            'to': ['test@test.com'],
            'subject': 'Test',
            'html_body': '<html>Test</html>',
            'account': 'test'
        })
        
        assert result['status'] == 'success'
    
    @patch('tools.smtp.cli._auto_connect')
    @patch('tools.smtp.smtp_client.get_connection')
    @patch('tools.smtp.smtp_client.set_connection')
    def test_send_with_attachment_disconnect_error(self, mock_set, mock_get, mock_auto_connect):
        """Test send_with_attachment when disconnect fails."""
        mock_conn = MagicMock()
        mock_conn.send_email_with_attachments.return_value = {'sent': True}
        mock_conn.disconnect.side_effect = Exception("Disconnect failed")
        mock_auto_connect.return_value = (mock_conn, True)
        mock_get.return_value = None
        
        result = send_with_attachment({
            'to': ['test@test.com'],
            'subject': 'Test',
            'body': 'Body',
            'attachments': ['file.txt'],
            'account': 'test'
        })
        
        assert result['status'] == 'success'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

