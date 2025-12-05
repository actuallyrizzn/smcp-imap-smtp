"""
Tests to hit the final missing lines.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, mock_open
from tools.imap.imap_client import IMAPConnection
from tools.smtp.smtp_client import SMTPConnection


class TestFinalLines:
    """Test final missing lines."""
    
    def test_find_sent_folder_partial_match_only(self):
        """Test find_sent_folder with only partial match (no exact match)."""
        conn = IMAPConnection()
        mock_client = MagicMock()
        # Return folders that don't match exact names, but have 'sent' in them
        mock_client.list_folders.return_value = [
            (b'\\HasNoChildren', b'/', b'INBOX'),
            (b'\\HasNoChildren', b'/', b'My Sent Mail'),  # Partial match only
        ]
        conn.client = mock_client
        
        result = conn.find_sent_folder()
        
        # Should match via partial match (line 275)
        assert result == 'My Sent Mail'
    
    def test_send_email_with_attachments_reply_to_only(self):
        """Test send_email_with_attachments with only Reply-To (no CC)."""
        conn = SMTPConnection()
        mock_server = MagicMock()
        mock_server.sendmail.return_value = {}
        conn.server = mock_server
        conn.username = 'sender@test.com'
        
        with patch('tools.smtp.smtp_client.MIMEMultipart') as mock_multipart:
            with patch('tools.smtp.smtp_client.MIMEBase'):
                with patch('tools.smtp.smtp_client.encoders'):
                    with patch('tools.smtp.smtp_client.os.path.exists', return_value=True):
                        with patch('tools.smtp.smtp_client.os.path.getsize', return_value=1000):
                            with patch('tools.smtp.smtp_client.os.path.basename', return_value='file.txt'):
                                with patch('builtins.open', mock_open(read_data=b'content')):
                                    with patch('tools.smtp.smtp_client.SMTPConnection._save_to_sent_folder'):
                                        mock_msg = MagicMock()
                                        mock_msg.attach = MagicMock()
                                        mock_msg.as_string.return_value = 'email string'
                                        mock_msg.as_bytes.return_value = b'email bytes'
                                        mock_multipart.return_value = mock_msg
                                        
                                        result = conn.send_email_with_attachments(
                                            ['recipient@test.com'],
                                            'Test Subject',
                                            'Test body',
                                            ['file.txt'],
                                            reply_to='reply@test.com'  # Only Reply-To, no CC (line 183)
                                        )
                                        
                                        assert result['sent'] is True
                                        # Verify Reply-To was set (line 183)
                                        mock_msg.__setitem__.assert_any_call('Reply-To', 'reply@test.com')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

