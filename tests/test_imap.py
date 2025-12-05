"""
Unit tests for IMAP CLI tool.
"""

import pytest
import json
import sys
from unittest.mock import Mock, patch, MagicMock
from tools.imap.imap_client import IMAPConnection
from tools.imap.cli import (
    list_mailboxes, search, fetch, mark_read, mark_unread, delete, move
)


class TestIMAPAutoConnect:
    """Test IMAP auto-connect functionality."""
    
    @patch('tools.imap.cli._auto_connect')
    @patch('tools.imap.imap_client.IMAPClient')
    def test_auto_connect_success(self, mock_imap_client, mock_auto_connect):
        """Test successful auto-connect via _auto_connect."""
        mock_client = MagicMock()
        mock_imap_client.return_value = mock_client
        mock_conn = Mock(spec=IMAPConnection)
        mock_conn.client = mock_client
        mock_auto_connect.return_value = (mock_conn, True)
        
        args = {
            'server': 'imap.gmx.com',
            'username': 'test@gmx.com',
            'password': 'testpass',
            'port': 993,
            'use_ssl': True
        }
        
        result = list_mailboxes(args)
        assert result['status'] == 'success'
        mock_auto_connect.assert_called_once()
    
    @patch('tools.imap.cli._auto_connect')
    def test_auto_connect_auth_failure(self, mock_auto_connect):
        """Test authentication failure during auto-connect."""
        mock_auto_connect.side_effect = RuntimeError("Auto-connect failed: b'authentication failed'")
        
        args = {
            'server': 'imap.gmx.com',
            'username': 'wrong@gmx.com',
            'password': 'wrongpass',
            'port': 993,
            'use_ssl': True
        }
        
        result = list_mailboxes(args)
        assert 'error' in result
        assert 'authentication' in result['error'].lower() or 'failed' in result['error'].lower()


class TestIMAPOperations:
    """Test IMAP operations."""
    
    @pytest.fixture
    def mock_connection(self):
        """Create a mock IMAP connection."""
        conn = Mock(spec=IMAPConnection)
        conn.client = MagicMock()
        return conn
    
    @patch('tools.imap.cli._auto_connect')
    @patch('tools.imap.imap_client.get_connection')
    def test_list_mailboxes(self, mock_get_conn, mock_auto_connect):
        """Test listing mailboxes."""
        mock_connection = Mock(spec=IMAPConnection)
        mock_connection.list_mailboxes.return_value = [
            (b'\\HasNoChildren', b'/', 'INBOX'),
            (b'\\HasNoChildren', b'/', 'Sent'),
        ]
        mock_get_conn.return_value = mock_connection
        mock_auto_connect.return_value = (mock_connection, False)
        
        args = {}
        result = list_mailboxes(args)
        
        assert result['status'] == 'success'
        assert 'mailboxes' in result['result']
        assert len(result['result']['mailboxes']) == 2
    
    @patch('tools.imap.cli._auto_connect')
    @patch('tools.imap.imap_client.get_connection')
    def test_search_emails(self, mock_get_conn, mock_auto_connect):
        """Test searching emails."""
        mock_connection = Mock(spec=IMAPConnection)
        mock_connection.search.return_value = [1, 2, 3, 4, 5]
        mock_connection.select_mailbox = Mock()
        mock_get_conn.return_value = mock_connection
        mock_auto_connect.return_value = (mock_connection, False)
        
        args = {'criteria': 'ALL'}
        result = search(args)
        
        assert result['status'] == 'success'
        assert 'message_ids' in result['result']
        assert len(result['result']['message_ids']) == 5
        assert result['result']['mailbox'] == 'INBOX'
        mock_connection.select_mailbox.assert_called_once_with('INBOX')
    
    @patch('tools.imap.cli._auto_connect')
    @patch('tools.imap.imap_client.get_connection')
    def test_search_with_mailbox(self, mock_get_conn, mock_auto_connect):
        """Test searching emails in specific mailbox."""
        mock_connection = Mock(spec=IMAPConnection)
        mock_connection.search.return_value = [1, 2]
        mock_connection.select_mailbox = Mock()
        mock_get_conn.return_value = mock_connection
        mock_auto_connect.return_value = (mock_connection, False)
        
        args = {'criteria': 'ALL', 'mailbox': 'Sent'}
        result = search(args)
        
        assert result['status'] == 'success'
        assert result['result']['mailbox'] == 'Sent'
        mock_connection.select_mailbox.assert_called_once_with('Sent')
    
    @patch('tools.imap.cli._auto_connect')
    @patch('tools.imap.imap_client.get_connection')
    def test_fetch_email(self, mock_get_conn, mock_auto_connect):
        """Test fetching email."""
        mock_connection = Mock(spec=IMAPConnection)
        mock_email = {
            'id': 123,
            'subject': 'Test Email',
            'from': {'email': 'sender@example.com'},
            'body': {'text': 'Test body'}
        }
        mock_connection.fetch_email.return_value = mock_email
        mock_connection.select_mailbox = Mock()
        mock_get_conn.return_value = mock_connection
        mock_auto_connect.return_value = (mock_connection, False)
        
        args = {'message_id': 123}
        result = fetch(args)
        
        assert result['status'] == 'success'
        assert 'subject' in result['result']
        assert result['result']['subject'] == 'Test Email'
        assert result['result']['mailbox'] == 'INBOX'
        mock_connection.select_mailbox.assert_called_once_with('INBOX')
    
    @patch('tools.imap.cli._auto_connect')
    @patch('tools.imap.imap_client.get_connection')
    def test_fetch_with_mailbox(self, mock_get_conn, mock_auto_connect):
        """Test fetching email from specific mailbox."""
        mock_connection = Mock(spec=IMAPConnection)
        mock_email = {
            'id': 1,
            'subject': 'Sent Email',
            'from': {'email': 'me@example.com'},
            'body': {'text': 'Sent body'}
        }
        mock_connection.fetch_email.return_value = mock_email
        mock_connection.select_mailbox = Mock()
        mock_get_conn.return_value = mock_connection
        mock_auto_connect.return_value = (mock_connection, False)
        
        args = {'message_id': 1, 'mailbox': 'Sent'}
        result = fetch(args)
        
        assert result['status'] == 'success'
        assert result['result']['mailbox'] == 'Sent'
        mock_connection.select_mailbox.assert_called_once_with('Sent')
    
    @patch('tools.imap.cli._auto_connect')
    @patch('tools.imap.imap_client.get_connection')
    def test_delete_sandbox_mode(self, mock_get_conn, mock_auto_connect):
        """Test delete in sandbox mode."""
        mock_connection = Mock(spec=IMAPConnection)
        mock_connection.delete = Mock()
        mock_connection.select_mailbox = Mock()
        mock_get_conn.return_value = mock_connection
        mock_auto_connect.return_value = (mock_connection, False)
        
        args = {'message_ids': [123], 'sandbox': True}
        result = delete(args)
        
        assert result['status'] == 'sandbox'
        assert result['result']['sandbox_mode'] is True
        assert 'would_delete' in result['result']
        mock_connection.delete.assert_not_called()
    
    @patch('tools.imap.cli._auto_connect')
    @patch('tools.imap.imap_client.get_connection')
    def test_delete_real_mode(self, mock_get_conn, mock_auto_connect):
        """Test delete in real mode."""
        mock_connection = Mock(spec=IMAPConnection)
        mock_connection.delete = Mock()
        mock_connection.select_mailbox = Mock()
        mock_get_conn.return_value = mock_connection
        mock_auto_connect.return_value = (mock_connection, False)
        
        args = {'message_ids': [123], 'sandbox': False}
        result = delete(args)
        
        assert result['status'] == 'success'
        assert result['result']['mailbox'] == 'INBOX'
        mock_connection.delete.assert_called_once_with([123])
        mock_connection.select_mailbox.assert_called_once_with('INBOX')
    
    @patch('tools.imap.cli._auto_connect')
    @patch('tools.imap.imap_client.get_connection')
    def test_delete_with_mailbox(self, mock_get_conn, mock_auto_connect):
        """Test delete from specific mailbox."""
        mock_connection = Mock(spec=IMAPConnection)
        mock_connection.delete = Mock()
        mock_connection.select_mailbox = Mock()
        mock_get_conn.return_value = mock_connection
        mock_auto_connect.return_value = (mock_connection, False)
        
        args = {'message_ids': [456], 'mailbox': 'Trash', 'sandbox': False}
        result = delete(args)
        
        assert result['status'] == 'success'
        assert result['result']['mailbox'] == 'Trash'
        mock_connection.select_mailbox.assert_called_once_with('Trash')
    
    @patch('tools.imap.cli._auto_connect')
    @patch('tools.imap.imap_client.get_connection')
    def test_mark_read_with_mailbox(self, mock_get_conn, mock_auto_connect):
        """Test mark-read with specific mailbox."""
        mock_connection = Mock(spec=IMAPConnection)
        mock_connection.mark_read = Mock()
        mock_connection.select_mailbox = Mock()
        mock_get_conn.return_value = mock_connection
        mock_auto_connect.return_value = (mock_connection, False)
        
        args = {'message_ids': [123], 'mailbox': 'Sent', 'sandbox': False}
        result = mark_read(args)
        
        assert result['status'] == 'success'
        assert result['result']['mailbox'] == 'Sent'
        mock_connection.select_mailbox.assert_called_once_with('Sent')
        mock_connection.mark_read.assert_called_once_with([123])
    
    @patch('tools.imap.cli._auto_connect')
    @patch('tools.imap.imap_client.get_connection')
    def test_mark_unread_with_mailbox(self, mock_get_conn, mock_auto_connect):
        """Test mark-unread with specific mailbox."""
        mock_connection = Mock(spec=IMAPConnection)
        mock_connection.mark_unread = Mock()
        mock_connection.select_mailbox = Mock()
        mock_get_conn.return_value = mock_connection
        mock_auto_connect.return_value = (mock_connection, False)
        
        args = {'message_ids': [123], 'mailbox': 'Drafts', 'sandbox': False}
        result = mark_unread(args)
        
        assert result['status'] == 'success'
        assert result['result']['mailbox'] == 'Drafts'
        mock_connection.select_mailbox.assert_called_once_with('Drafts')
        mock_connection.mark_unread.assert_called_once_with([123])


class TestIMAPErrorHandling:
    """Test IMAP error handling."""
    
    @patch('tools.imap.cli._auto_connect')
    @patch('tools.imap.imap_client.get_connection')
    def test_search_defaults_to_inbox(self, mock_get_conn, mock_auto_connect):
        """Test search defaults to INBOX when no mailbox specified."""
        mock_conn = Mock(spec=IMAPConnection)
        mock_conn.client = MagicMock()
        mock_conn.search.return_value = [1, 2, 3]
        mock_conn.select_mailbox = Mock()
        mock_get_conn.return_value = mock_conn
        mock_auto_connect.return_value = (mock_conn, True)  # Auto-connected
        
        args = {'criteria': 'ALL'}
        result = search(args)
        
        assert result['status'] == 'success'
        # Should have selected INBOX (default)
        mock_conn.select_mailbox.assert_called_once_with('INBOX')
        assert result['result']['mailbox'] == 'INBOX'
    
    @patch('tools.imap.cli._auto_connect')
    def test_search_no_connection(self, mock_auto_connect):
        """Test search when no connection available."""
        mock_auto_connect.return_value = (None, False)
        
        args = {'criteria': 'ALL'}
        result = search(args)
        
        assert 'error' in result
        assert 'not connected' in result['error'].lower()
    
    @patch('tools.imap.cli._auto_connect')
    @patch('tools.imap.imap_client.get_connection')
    def test_move_with_mailbox(self, mock_get_conn, mock_auto_connect):
        """Test move from specific mailbox."""
        mock_connection = Mock(spec=IMAPConnection)
        mock_connection.move = Mock()
        mock_connection.select_mailbox = Mock()
        mock_get_conn.return_value = mock_connection
        mock_auto_connect.return_value = (mock_connection, False)
        
        args = {'message_ids': [123], 'mailbox': 'Sent', 'target_mailbox': 'Archive', 'sandbox': False}
        result = move(args)
        
        assert result['status'] == 'success'
        assert result['result']['source_mailbox'] == 'Sent'
        assert result['result']['target_mailbox'] == 'Archive'
        mock_connection.select_mailbox.assert_called_once_with('Sent')
        mock_connection.move.assert_called_once_with([123], 'Archive')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

