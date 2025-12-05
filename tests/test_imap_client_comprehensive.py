"""
Comprehensive tests for IMAP client methods.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from tools.imap.imap_client import IMAPConnection


class TestIMAPConnectionMethods:
    """Test IMAP connection methods."""
    
    @patch('tools.imap.imap_client.IMAPClient')
    def test_connect_success(self, mock_imap_client):
        """Test successful connection."""
        mock_client = MagicMock()
        mock_client.login.return_value = None
        mock_imap_client.return_value = mock_client
        
        conn = IMAPConnection()
        conn.connect('imap.test.com', 'test@test.com', 'password', 993, True)
        
        assert conn.client is not None
        assert conn.server == 'imap.test.com'
        assert conn.username == 'test@test.com'
        mock_client.login.assert_called_once_with('test@test.com', 'password')
    
    @patch('tools.imap.imap_client.IMAPClient')
    def test_connect_auth_failure_then_plain(self, mock_imap_client):
        """Test connection with auth failure then PLAIN auth success."""
        mock_client = MagicMock()
        mock_client.login.side_effect = Exception("b'authentication failed'")
        mock_client._imap = MagicMock()
        mock_client._imap.authenticate.return_value = None
        mock_imap_client.return_value = mock_client
        
        conn = IMAPConnection()
        conn.connect('imap.test.com', 'test@test.com', 'password', 993, True)
        
        assert conn.client is not None
        mock_client._imap.authenticate.assert_called_once()
    
    @patch('tools.imap.imap_client.IMAPClient')
    def test_connect_auth_failure_both_fail(self, mock_imap_client):
        """Test connection when both login and PLAIN auth fail."""
        mock_client = MagicMock()
        mock_client.login.side_effect = Exception("b'authentication failed'")
        mock_client._imap = MagicMock()
        mock_client._imap.authenticate.side_effect = Exception("b'authentication failed'")
        mock_imap_client.return_value = mock_client
        
        conn = IMAPConnection()
        with pytest.raises(RuntimeError, match="Authentication failed"):
            conn.connect('imap.test.com', 'test@test.com', 'password', 993, True)
    
    @patch('tools.imap.imap_client.IMAPClient')
    def test_connect_other_error(self, mock_imap_client):
        """Test connection with non-auth error."""
        mock_client = MagicMock()
        mock_client.login.side_effect = Exception("Connection timeout")
        mock_imap_client.return_value = mock_client
        
        conn = IMAPConnection()
        with pytest.raises(Exception, match="Connection timeout"):
            conn.connect('imap.test.com', 'test@test.com', 'password', 993, True)
    
    def test_disconnect(self):
        """Test disconnection."""
        conn = IMAPConnection()
        conn.client = MagicMock()
        conn.server = 'imap.test.com'
        conn.username = 'test@test.com'
        conn.current_mailbox = 'INBOX'
        
        conn.disconnect()
        
        assert conn.client is None
        assert conn.server is None
        assert conn.username is None
        assert conn.current_mailbox is None
    
    def test_disconnect_logout_error(self):
        """Test disconnection when logout fails."""
        conn = IMAPConnection()
        mock_client = MagicMock()
        mock_client.logout.side_effect = Exception("Logout failed")
        conn.client = mock_client
        
        # Should not raise
        conn.disconnect()
        assert conn.client is None
    
    def test_list_mailboxes(self):
        """Test listing mailboxes."""
        conn = IMAPConnection()
        mock_client = MagicMock()
        mock_client.list_folders.return_value = [
            (b'\\HasNoChildren', b'/', b'INBOX'),
            (b'\\HasNoChildren', b'/', b'Sent'),
        ]
        conn.client = mock_client
        
        result = conn.list_mailboxes()
        
        assert len(result) == 2
        assert result[0]['name'] == 'INBOX'
        assert result[1]['name'] == 'Sent'
    
    def test_list_mailboxes_string_names(self):
        """Test listing mailboxes with string names."""
        conn = IMAPConnection()
        mock_client = MagicMock()
        mock_client.list_folders.return_value = [
            (['\\HasNoChildren'], '/', 'INBOX'),
            (['\\HasNoChildren'], '/', 'Sent'),
        ]
        conn.client = mock_client
        
        result = conn.list_mailboxes()
        
        assert len(result) == 2
        assert result[0]['name'] == 'INBOX'
    
    def test_list_mailboxes_not_connected(self):
        """Test listing mailboxes when not connected."""
        conn = IMAPConnection()
        
        with pytest.raises(RuntimeError, match="Not connected"):
            conn.list_mailboxes()
    
    def test_select_mailbox(self):
        """Test selecting a mailbox."""
        conn = IMAPConnection()
        mock_client = MagicMock()
        mock_client.select_folder.return_value = {
            b'EXISTS': 10,
            b'RECENT': 2,
            b'UNSEEN': 5,
            b'UIDVALIDITY': 12345
        }
        conn.client = mock_client
        
        result = conn.select_mailbox('INBOX')
        
        assert result['mailbox'] == 'INBOX'
        assert result['exists'] == 10
        assert result['recent'] == 2
        assert result['unseen'] == 5
        assert conn.current_mailbox == 'INBOX'
    
    def test_select_mailbox_missing_keys(self):
        """Test selecting mailbox with missing optional keys."""
        conn = IMAPConnection()
        mock_client = MagicMock()
        mock_client.select_folder.return_value = {
            b'EXISTS': 10
        }
        conn.client = mock_client
        
        result = conn.select_mailbox('INBOX')
        
        assert result['recent'] == 0
        assert result['unseen'] == 0
    
    def test_search_all(self):
        """Test searching with ALL criteria."""
        conn = IMAPConnection()
        mock_client = MagicMock()
        mock_client.search.return_value = [1, 2, 3, 4, 5]
        conn.client = mock_client
        
        result = conn.search('ALL')
        
        assert result == [1, 2, 3, 4, 5]
        mock_client.search.assert_called_once_with(['ALL'])
    
    def test_search_unseen(self):
        """Test searching with UNSEEN criteria."""
        conn = IMAPConnection()
        mock_client = MagicMock()
        mock_client.search.return_value = [1, 3, 5]
        conn.client = mock_client
        
        result = conn.search('UNSEEN')
        
        assert result == [1, 3, 5]
        mock_client.search.assert_called_once_with(['UNSEEN'])
    
    def test_search_from(self):
        """Test searching with FROM criteria."""
        conn = IMAPConnection()
        mock_client = MagicMock()
        mock_client.search.return_value = [1, 2]
        conn.client = mock_client
        
        result = conn.search('FROM sender@example.com')
        
        assert result == [1, 2]
        mock_client.search.assert_called_once_with(['FROM', 'sender@example.com'])
    
    def test_search_from_with_quotes(self):
        """Test searching with FROM criteria containing quotes."""
        conn = IMAPConnection()
        mock_client = MagicMock()
        mock_client.search.return_value = [1]
        conn.client = mock_client
        
        result = conn.search('FROM "sender@example.com"')
        
        mock_client.search.assert_called_once_with(['FROM', 'sender@example.com'])
    
    def test_search_subject(self):
        """Test searching with SUBJECT criteria."""
        conn = IMAPConnection()
        mock_client = MagicMock()
        mock_client.search.return_value = [2, 3]
        conn.client = mock_client
        
        result = conn.search('SUBJECT test')
        
        mock_client.search.assert_called_once_with(['SUBJECT', 'test'])
    
    def test_search_complex(self):
        """Test searching with complex criteria."""
        conn = IMAPConnection()
        mock_client = MagicMock()
        mock_client.search.return_value = []
        conn.client = mock_client
        
        result = conn.search('UNSEEN FROM sender@example.com')
        
        # Should use raw criteria
        mock_client.search.assert_called_once()
    
    def test_search_not_connected(self):
        """Test searching when not connected."""
        conn = IMAPConnection()
        
        with pytest.raises(RuntimeError, match="Not connected"):
            conn.search('ALL')
    
    @patch('tools.imap.imap_client.message_from_bytes')
    @patch('tools.imap.imap_client.email')
    def test_fetch_email(self, mock_email, mock_message_from_bytes):
        """Test fetching email."""
        conn = IMAPConnection()
        mock_client = MagicMock()
        mock_message = MagicMock()
        mock_message.get.return_value = 'Test Subject'
        mock_message.get_all.return_value = ['sender@example.com']
        mock_message.is_multipart.return_value = False
        mock_message.get_payload.return_value = 'Test body'
        mock_message_from_bytes.return_value = mock_message
        
        mock_client.fetch.return_value = {
            123: {b'RFC822': b'email content'}
        }
        conn.client = mock_client
        
        result = conn.fetch_email(123)
        
        assert result['id'] == '123'  # Normalized to string
        assert 'subject' in result
    
    def test_fetch_email_not_connected(self):
        """Test fetching email when not connected."""
        conn = IMAPConnection()
        
        with pytest.raises(RuntimeError, match="Not connected"):
            conn.fetch_email(123)
    
    def test_mark_read(self):
        """Test marking email as read."""
        conn = IMAPConnection()
        mock_client = MagicMock()
        conn.client = mock_client
        
        conn.mark_read([1, 2, 3])
        
        mock_client.set_flags.assert_called_once()
    
    def test_mark_unread(self):
        """Test marking email as unread."""
        conn = IMAPConnection()
        mock_client = MagicMock()
        conn.client = mock_client
        
        conn.mark_unread([1, 2, 3])
        
        mock_client.remove_flags.assert_called_once()
    
    def test_delete(self):
        """Test deleting email."""
        conn = IMAPConnection()
        mock_client = MagicMock()
        conn.client = mock_client
        
        conn.delete([1, 2, 3])
        
        mock_client.set_flags.assert_called()
        mock_client.expunge.assert_called_once()
    
    def test_move(self):
        """Test moving email."""
        conn = IMAPConnection()
        mock_client = MagicMock()
        conn.client = mock_client
        
        conn.move([1, 2, 3], 'Archive')
        
        mock_client.copy.assert_called_once_with([1, 2, 3], 'Archive')
        mock_client.set_flags.assert_called()
        mock_client.expunge.assert_called_once()
    
    def test_append_to_mailbox(self):
        """Test appending message to mailbox."""
        conn = IMAPConnection()
        mock_client = MagicMock()
        mock_client.append.return_value = 123
        conn.client = mock_client
        
        result = conn.append_to_mailbox('Sent', b'message content', ['\\Seen'])
        
        assert result == 123
        mock_client.append.assert_called_once_with('Sent', b'message content', flags=['\\Seen'])
    
    def test_append_to_mailbox_default_flags(self):
        """Test appending with default flags."""
        conn = IMAPConnection()
        mock_client = MagicMock()
        mock_client.append.return_value = 123
        conn.client = mock_client
        
        result = conn.append_to_mailbox('Sent', b'message content')
        
        mock_client.append.assert_called_once_with('Sent', b'message content', flags=['\\Seen'])
    
    def test_find_sent_folder(self):
        """Test finding Sent folder."""
        conn = IMAPConnection()
        mock_client = MagicMock()
        mock_client.list_folders.return_value = [
            (b'\\HasNoChildren', b'/', b'INBOX'),
            (b'\\HasNoChildren', b'/', b'Sent'),
        ]
        conn.client = mock_client
        
        result = conn.find_sent_folder()
        
        assert result == 'Sent'
    
    def test_find_sent_folder_gesendet(self):
        """Test finding German Sent folder."""
        conn = IMAPConnection()
        mock_client = MagicMock()
        mock_client.list_folders.return_value = [
            (b'\\HasNoChildren', b'/', b'INBOX'),
            (b'\\HasNoChildren', b'/', b'Gesendet'),
        ]
        conn.client = mock_client
        
        result = conn.find_sent_folder()
        
        assert result == 'Gesendet'
    
    def test_find_sent_folder_not_found(self):
        """Test when Sent folder not found."""
        conn = IMAPConnection()
        mock_client = MagicMock()
        mock_client.list_folders.return_value = [
            (b'\\HasNoChildren', b'/', b'INBOX'),
        ]
        conn.client = mock_client
        
        result = conn.find_sent_folder()
        
        assert result is None
    
    def test_find_sent_folder_error(self):
        """Test find_sent_folder when list_folders fails."""
        conn = IMAPConnection()
        mock_client = MagicMock()
        mock_client.list_folders.side_effect = Exception("List failed")
        conn.client = mock_client
        
        result = conn.find_sent_folder()
        
        assert result is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

