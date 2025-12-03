"""
Unit tests for IMAP CLI tool.
"""

import pytest
import json
import sys
from unittest.mock import Mock, patch, MagicMock
from tools.imap.imap_client import IMAPConnection
from tools.imap.cli import (
    connect, disconnect, list_mailboxes, select_mailbox,
    search, fetch, mark_read, mark_unread, delete, move
)


class TestIMAPConnection:
    """Test IMAP connection management."""
    
    @patch('tools.imap.imap_client.IMAPClient')
    def test_connect_success(self, mock_imap_client):
        """Test successful IMAP connection."""
        mock_client = MagicMock()
        mock_imap_client.return_value = mock_client
        
        args = {
            'server': 'imap.gmx.com',
            'username': 'test@gmx.com',
            'password': 'testpass',
            'port': 993,
            'use_ssl': True
        }
        
        result = connect(args)
        assert result['status'] == 'success'
        assert 'connected' in result['result']
        assert result['result']['connected'] is True
        mock_client.login.assert_called_once_with('test@gmx.com', 'testpass')
    
    @patch('tools.imap.imap_client.IMAPClient')
    def test_connect_auth_failure(self, mock_imap_client):
        """Test authentication failure."""
        mock_client = MagicMock()
        # Make login raise an exception that will be caught
        mock_client.login.side_effect = Exception("b'authentication failed'")
        # Also need to mock the PLAIN auth attempt
        mock_client._imap = MagicMock()
        mock_client._imap.authenticate.side_effect = Exception("b'authentication failed'")
        mock_imap_client.return_value = mock_client
        
        args = {
            'server': 'imap.gmx.com',
            'username': 'wrong@gmx.com',
            'password': 'wrongpass',
            'port': 993,
            'use_ssl': True
        }
        
        result = connect(args)
        assert 'error' in result
        assert 'authentication' in result['error'].lower()


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
        mock_connection.current_mailbox = 'INBOX'
        mock_get_conn.return_value = mock_connection
        mock_auto_connect.return_value = (mock_connection, False)
        
        args = {'criteria': 'ALL'}
        result = search(args)
        
        assert result['status'] == 'success'
        assert 'message_ids' in result['result']
        assert len(result['result']['message_ids']) == 5
    
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
        mock_connection.current_mailbox = 'INBOX'
        mock_get_conn.return_value = mock_connection
        mock_auto_connect.return_value = (mock_connection, False)
        
        args = {'message_id': 123}
        result = fetch(args)
        
        assert result['status'] == 'success'
        assert 'subject' in result['result']
        assert result['result']['subject'] == 'Test Email'
    
    @patch('tools.imap.cli._auto_connect')
    @patch('tools.imap.imap_client.get_connection')
    def test_delete_sandbox_mode(self, mock_get_conn, mock_auto_connect):
        """Test delete in sandbox mode."""
        mock_connection = Mock(spec=IMAPConnection)
        mock_connection.current_mailbox = 'INBOX'
        mock_connection.delete = Mock()
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
        mock_connection.current_mailbox = 'INBOX'
        mock_get_conn.return_value = mock_connection
        mock_auto_connect.return_value = (mock_connection, False)
        
        args = {'message_ids': [123], 'sandbox': False}
        result = delete(args)
        
        assert result['status'] == 'success'
        mock_connection.delete.assert_called_once_with([123])


class TestIMAPErrorHandling:
    """Test IMAP error handling."""
    
    @patch('tools.imap.cli._auto_connect')
    @patch('tools.imap.imap_client.get_connection')
    def test_search_no_mailbox_selected(self, mock_get_conn, mock_auto_connect):
        """Test search when no mailbox is selected."""
        mock_conn = Mock(spec=IMAPConnection)
        mock_conn.client = MagicMock()
        mock_conn.current_mailbox = None
        mock_conn.search.return_value = [1, 2, 3]
        mock_conn.select_mailbox.return_value = {'status': 'success'}
        mock_get_conn.return_value = mock_conn
        mock_auto_connect.return_value = (mock_conn, True)  # Auto-connected, so should auto-select
        
        args = {'criteria': 'ALL'}
        result = search(args)
        
        assert result['status'] == 'success'
        # Should have auto-selected INBOX when auto-connecting
        assert mock_conn.select_mailbox.called or mock_conn.current_mailbox == 'INBOX'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

