"""
Tests for IMAP CLI error paths and edge cases.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from tools.imap.cli import search, fetch, mark_read, mark_unread, delete, move


class TestIMAPCLIErrors:
    """Test IMAP CLI error handling."""
    
    def test_search_missing_criteria(self):
        """Test search with missing criteria."""
        result = search({})
        
        assert 'error' in result
        assert 'criteria' in result['error'].lower()
    
    def test_fetch_missing_message_id(self):
        """Test fetch with missing message ID."""
        result = fetch({})
        
        assert 'error' in result
        assert 'message-id' in result['error'].lower()
    
    def test_fetch_invalid_message_id(self):
        """Test fetch with invalid message ID."""
        result = fetch({'message_id': 'not-a-number'})
        
        assert 'error' in result
        assert 'invalid' in result['error'].lower()
    
    def test_mark_read_missing_message_ids(self):
        """Test mark-read with missing message IDs."""
        result = mark_read({})
        
        assert 'error' in result
        assert 'message-ids' in result['error'].lower()
    
    def test_mark_read_invalid_message_id(self):
        """Test mark-read with invalid message ID."""
        result = mark_read({'message_ids': ['not-a-number'], 'sandbox': False})
        
        assert 'error' in result
        assert 'invalid' in result['error'].lower()
    
    def test_mark_unread_missing_message_ids(self):
        """Test mark-unread with missing message IDs."""
        result = mark_unread({})
        
        assert 'error' in result
        assert 'message-ids' in result['error'].lower()
    
    def test_mark_unread_invalid_message_id(self):
        """Test mark-unread with invalid message ID."""
        result = mark_unread({'message_ids': ['not-a-number'], 'sandbox': False})
        
        assert 'error' in result
        assert 'invalid' in result['error'].lower()
    
    def test_delete_missing_message_ids(self):
        """Test delete with missing message IDs."""
        result = delete({})
        
        assert 'error' in result
        assert 'message-ids' in result['error'].lower()
    
    def test_delete_invalid_message_id(self):
        """Test delete with invalid message ID."""
        result = delete({'message_ids': ['not-a-number'], 'sandbox': False})
        
        assert 'error' in result
        assert 'invalid' in result['error'].lower()
    
    def test_move_missing_message_ids(self):
        """Test move with missing message IDs."""
        result = move({'target_mailbox': 'Archive'})
        
        assert 'error' in result
        assert 'message-ids' in result['error'].lower()
    
    def test_move_missing_target_mailbox(self):
        """Test move with missing target mailbox."""
        result = move({'message_ids': [1, 2, 3]})
        
        assert 'error' in result
        assert 'target-mailbox' in result['error'].lower()
    
    def test_move_invalid_message_id(self):
        """Test move with invalid message ID."""
        result = move({'message_ids': ['not-a-number'], 'target_mailbox': 'Archive', 'sandbox': False})
        
        assert 'error' in result
        assert 'invalid' in result['error'].lower()
    
    @patch('tools.imap.cli._auto_connect')
    def test_search_connection_error(self, mock_auto_connect):
        """Test search when connection fails."""
        mock_auto_connect.side_effect = RuntimeError("Connection failed")
        
        result = search({'criteria': 'ALL'})
        
        assert 'error' in result
        assert 'connection failed' in result['error'].lower()
    
    @patch('tools.imap.cli._auto_connect')
    @patch('tools.imap.imap_client.get_connection')
    def test_fetch_operation_error(self, mock_get, mock_auto_connect):
        """Test fetch when operation fails."""
        mock_conn = MagicMock()
        mock_conn.select_mailbox.side_effect = Exception("Select failed")
        mock_auto_connect.return_value = (mock_conn, True)
        mock_get.return_value = None
        
        result = fetch({'message_id': '123'})
        
        assert 'error' in result
        assert 'failed' in result['error'].lower()
    
    @patch('tools.imap.cli._auto_connect')
    @patch('tools.imap.imap_client.get_connection')
    def test_mark_read_operation_error(self, mock_get, mock_auto_connect):
        """Test mark-read when operation fails."""
        mock_conn = MagicMock()
        mock_conn.select_mailbox.side_effect = Exception("Select failed")
        mock_auto_connect.return_value = (mock_conn, True)
        mock_get.return_value = None
        
        result = mark_read({'message_ids': ['123'], 'sandbox': False})
        
        assert 'error' in result
        assert 'failed' in result['error'].lower()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

