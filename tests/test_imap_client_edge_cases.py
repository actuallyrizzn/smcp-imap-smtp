"""
Tests for IMAP client edge cases and error paths.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from tools.imap.imap_client import IMAPConnection


class TestIMAPClientEdgeCases:
    """Test IMAP client edge cases."""
    
    def test_fetch_email_not_found(self):
        """Test fetching email that doesn't exist."""
        conn = IMAPConnection()
        mock_client = MagicMock()
        mock_client.fetch.return_value = {}  # Empty result
        conn.client = mock_client
        
        with pytest.raises(ValueError, match="Message 123 not found"):
            conn.fetch_email(123)
    
    def test_append_to_mailbox_error(self):
        """Test append when error occurs."""
        conn = IMAPConnection()
        mock_client = MagicMock()
        mock_client.append.side_effect = Exception("Append failed")
        conn.client = mock_client
        
        with pytest.raises(Exception, match="Append failed"):
            conn.append_to_mailbox('Sent', b'message', ['\\Seen'])
    
    def test_find_sent_folder_partial_match(self):
        """Test finding Sent folder with partial match."""
        conn = IMAPConnection()
        mock_client = MagicMock()
        mock_client.list_folders.return_value = [
            (b'\\HasNoChildren', b'/', b'INBOX'),
            (b'\\HasNoChildren', b'/', b'Sent Items'),
        ]
        conn.client = mock_client
        
        result = conn.find_sent_folder()
        
        assert result == 'Sent Items'
    
    def test_find_sent_folder_excludes_drafts(self):
        """Test that Sent Drafts is not matched."""
        conn = IMAPConnection()
        mock_client = MagicMock()
        mock_client.list_folders.return_value = [
            (b'\\HasNoChildren', b'/', b'INBOX'),
            (b'\\HasNoChildren', b'/', b'Sent Drafts'),
        ]
        conn.client = mock_client
        
        result = conn.find_sent_folder()
        
        # Should not match "Sent Drafts"
        assert result is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

