"""
Tests for remaining coverage gaps.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, mock_open
from tools.imap.imap_client import IMAPConnection
from tools.smtp.smtp_client import SMTPConnection


class TestRemainingCoverage:
    """Test remaining coverage gaps."""
    
    def test_find_sent_folder_partial_match_sent_items(self):
        """Test find_sent_folder with partial match 'Sent Items'."""
        conn = IMAPConnection()
        mock_client = MagicMock()
        mock_client.list_folders.return_value = [
            (b'\\HasNoChildren', b'/', b'INBOX'),
            (b'\\HasNoChildren', b'/', b'Sent Items'),
        ]
        conn.client = mock_client
        
        result = conn.find_sent_folder()
        
        # Should match 'Sent Items' via partial match (line 275)
        assert result == 'Sent Items'
    
    def test_send_email_with_cc_and_reply_to(self):
        """Test send_email with both CC and Reply-To."""
        conn = SMTPConnection()
        mock_server = MagicMock()
        mock_server.sendmail.return_value = {}
        conn.server = mock_server
        conn.username = 'sender@test.com'
        
        with patch('tools.smtp.smtp_client.MIMEText') as mock_mimetext:
            with patch('tools.smtp.smtp_client.SMTPConnection._save_to_sent_folder'):
                mock_msg = MagicMock()
                mock_msg.as_string.return_value = 'email string'
                mock_msg.as_bytes.return_value = b'email bytes'
                mock_mimetext.return_value = mock_msg
                
                result = conn.send_email(
                    ['recipient@test.com'],
                    'Test Subject',
                    'Test body',
                    cc=['cc@test.com'],
                    reply_to='reply@test.com'
                )
                
                assert result['sent'] is True
                # Verify CC and Reply-To were set (lines 181, 183)
                mock_msg.__setitem__.assert_any_call('Cc', 'cc@test.com')
                mock_msg.__setitem__.assert_any_call('Reply-To', 'reply@test.com')
    
    def test_send_email_with_attachments_cc_bcc(self):
        """Test send_email_with_attachments with CC and BCC."""
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
                                            cc=['cc@test.com'],
                                            bcc=['bcc@test.com']
                                        )
                                        
                                        assert result['sent'] is True
                                        # Verify recipients include CC and BCC (lines 206, 208)
                                        call_args = mock_server.sendmail.call_args
                                        recipients = call_args[0][1]
                                        assert 'cc@test.com' in recipients
                                        assert 'bcc@test.com' in recipients
    
    def test_get_connection_smtp(self):
        """Test get_connection for SMTP."""
        from tools.smtp.smtp_client import get_connection, set_connection
        
        # Test get_connection returns None initially
        assert get_connection() is None
        
        # Test set and get
        conn = SMTPConnection()
        set_connection(conn)
        assert get_connection() == conn
        
        # Clean up
        set_connection(None)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

