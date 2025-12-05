"""
Tests for client methods when not connected.
"""

import pytest
from tools.imap.imap_client import IMAPConnection
from tools.smtp.smtp_client import SMTPConnection


class TestClientNotConnected:
    """Test client methods when not connected."""
    
    def test_select_mailbox_not_connected(self):
        """Test select_mailbox when not connected."""
        conn = IMAPConnection()
        
        with pytest.raises(RuntimeError, match="Not connected"):
            conn.select_mailbox('INBOX')
    
    def test_mark_read_not_connected(self):
        """Test mark_read when not connected."""
        conn = IMAPConnection()
        
        with pytest.raises(RuntimeError, match="Not connected"):
            conn.mark_read([1, 2, 3])
    
    def test_mark_unread_not_connected(self):
        """Test mark_unread when not connected."""
        conn = IMAPConnection()
        
        with pytest.raises(RuntimeError, match="Not connected"):
            conn.mark_unread([1, 2, 3])
    
    def test_delete_not_connected(self):
        """Test delete when not connected."""
        conn = IMAPConnection()
        
        with pytest.raises(RuntimeError, match="Not connected"):
            conn.delete([1, 2, 3])
    
    def test_move_not_connected(self):
        """Test move when not connected."""
        conn = IMAPConnection()
        
        with pytest.raises(RuntimeError, match="Not connected"):
            conn.move([1, 2, 3], 'Archive')
    
    def test_append_to_mailbox_not_connected(self):
        """Test append_to_mailbox when not connected."""
        conn = IMAPConnection()
        
        with pytest.raises(RuntimeError, match="Not connected"):
            conn.append_to_mailbox('Sent', b'message')
    
    def test_find_sent_folder_not_connected(self):
        """Test find_sent_folder when not connected."""
        conn = IMAPConnection()
        
        with pytest.raises(RuntimeError, match="Not connected"):
            conn.find_sent_folder()
    
    def test_send_email_with_attachments_not_connected(self):
        """Test send_email_with_attachments when not connected."""
        conn = SMTPConnection()
        
        with pytest.raises(RuntimeError, match="Not connected"):
            conn.send_email_with_attachments(
                ['test@test.com'],
                'Test',
                'Body',
                ['file.txt']
            )


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

