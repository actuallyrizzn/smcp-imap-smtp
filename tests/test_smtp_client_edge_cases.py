"""
Tests for SMTP client edge cases and error paths.
"""

import pytest
import os
from unittest.mock import Mock, MagicMock, patch
from tools.smtp.smtp_client import SMTPConnection, MAX_ATTACHMENT_BYTES


class TestSMTPClientEdgeCases:
    """Test SMTP client edge cases."""
    
    def test_send_email_with_attachments_not_found(self):
        """Test sending email with non-existent attachment."""
        conn = SMTPConnection()
        mock_server = MagicMock()
        conn.server = mock_server
        conn.username = 'sender@test.com'
        
        with pytest.raises(FileNotFoundError, match="Attachment not found"):
            conn.send_email_with_attachments(
                ['recipient@test.com'],
                'Test',
                'Body',
                ['/nonexistent/file.pdf']
            )
    
    @patch('tools.smtp.smtp_client.os.path.exists')
    @patch('tools.smtp.smtp_client.os.path.getsize')
    def test_send_email_with_attachments_too_large(self, mock_getsize, mock_exists):
        """Test sending email with attachment that's too large."""
        conn = SMTPConnection()
        mock_server = MagicMock()
        conn.server = mock_server
        conn.username = 'sender@test.com'
        
        mock_exists.return_value = True
        mock_getsize.return_value = MAX_ATTACHMENT_BYTES + 1
        
        with pytest.raises(ValueError, match="exceeds maximum size"):
            conn.send_email_with_attachments(
                ['recipient@test.com'],
                'Test',
                'Body',
                ['/path/to/large_file.pdf']
            )
    
    @patch('tools.imap.imap_client.IMAPConnection')
    def test_save_to_sent_folder_import_error(self, mock_imap_conn):
        """Test save when IMAP client import fails."""
        conn = SMTPConnection()
        conn.username = 'test@test.com'
        conn.password = 'password'
        
        # Mock ImportError by patching the import inside the function
        def mock_import(name, *args, **kwargs):
            if name == 'tools.imap.imap_client':
                raise ImportError("No module named 'tools.imap.imap_client'")
            return __import__(name, *args, **kwargs)
        
        with patch('builtins.__import__', side_effect=mock_import):
            # Should not raise
            conn._save_to_sent_folder(b'message content')
    
    def test_save_to_sent_folder_no_credentials(self):
        """Test save when credentials are missing."""
        conn = SMTPConnection()
        conn.username = None
        conn.password = None
        
        # Should not raise, just log warning
        conn._save_to_sent_folder(b'message content')
    
    @patch('tools.config.ProfileManager')
    def test_save_to_sent_folder_no_imap_server(self, mock_pm_class):
        """Test save when IMAP server not configured."""
        conn = SMTPConnection()
        conn.username = 'test@test.com'
        conn.password = 'password'
        
        mock_manager = MagicMock()
        mock_manager.list_profiles.return_value = []
        mock_manager.get_default.return_value = None
        mock_pm_class.return_value = mock_manager
        
        # Should not raise, just log warning
        conn._save_to_sent_folder(b'message content')
    
    @patch('tools.imap.imap_client.IMAPConnection')
    @patch('tools.config.ProfileManager')
    def test_save_to_sent_folder_default_profile(self, mock_pm_class, mock_imap_conn):
        """Test save using default profile."""
        conn = SMTPConnection()
        conn.username = 'test@test.com'
        conn.password = 'password'
        
        mock_manager = MagicMock()
        mock_profile = MagicMock()
        mock_profile.username = 'test@test.com'
        mock_profile.imap_server = 'imap.test.com'
        mock_profile.imap_port = 993
        mock_profile.imap_ssl = True
        mock_profile.password = 'password'
        mock_manager.list_profiles.return_value = []
        mock_manager.get_default.return_value = mock_profile
        mock_pm_class.return_value = mock_manager
        
        mock_imap = MagicMock()
        mock_imap.find_sent_folder.return_value = 'Sent'
        mock_imap_conn.return_value = mock_imap
        
        conn._save_to_sent_folder(b'message content')
        
        mock_imap.connect.assert_called_once()
        mock_imap.append_to_mailbox.assert_called_once()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

