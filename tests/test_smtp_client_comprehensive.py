"""
Comprehensive tests for SMTP client methods.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from tools.smtp.smtp_client import SMTPConnection


class TestSMTPConnectionMethods:
    """Test SMTP connection methods."""
    
    @patch('tools.smtp.smtp_client.smtplib.SMTP')
    def test_connect_success(self, mock_smtp):
        """Test successful connection."""
        mock_server = MagicMock()
        mock_server.starttls.return_value = None
        mock_server.login.return_value = None
        mock_smtp.return_value = mock_server
        
        conn = SMTPConnection()
        conn.connect('mail.test.com', 'test@test.com', 'password', 587, True)
        
        assert conn.server is not None
        assert conn.host == 'mail.test.com'
        assert conn.username == 'test@test.com'
        assert conn.password == 'password'
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with('test@test.com', 'password')
    
    @patch('tools.smtp.smtp_client.smtplib.SMTP')
    def test_connect_no_tls(self, mock_smtp):
        """Test connection without TLS."""
        mock_server = MagicMock()
        mock_server.login.return_value = None
        mock_smtp.return_value = mock_server
        
        conn = SMTPConnection()
        conn.connect('mail.test.com', 'test@test.com', 'password', 25, False)
        
        mock_server.starttls.assert_not_called()
        mock_server.login.assert_called_once()
    
    @patch('tools.smtp.smtp_client.smtplib.SMTP')
    def test_connect_auth_failure(self, mock_smtp):
        """Test connection with authentication failure."""
        mock_server = MagicMock()
        mock_server.starttls.return_value = None
        mock_server.login.side_effect = Exception("Authentication failed")
        mock_smtp.return_value = mock_server
        
        conn = SMTPConnection()
        with pytest.raises(Exception, match="Authentication failed"):
            conn.connect('mail.test.com', 'test@test.com', 'password', 587, True)
    
    def test_disconnect(self):
        """Test disconnection."""
        conn = SMTPConnection()
        mock_server = MagicMock()
        mock_server.quit.return_value = None
        conn.server = mock_server
        conn.host = 'mail.test.com'
        conn.username = 'test@test.com'
        conn.password = 'password'
        
        conn.disconnect()
        
        assert conn.server is None
        assert conn.host is None
        assert conn.username is None
        assert conn.password is None
    
    def test_disconnect_quit_error(self):
        """Test disconnection when quit fails."""
        conn = SMTPConnection()
        mock_server = MagicMock()
        mock_server.quit.side_effect = Exception("Quit failed")
        mock_server.close.return_value = None
        conn.server = mock_server
        
        # Should not raise
        conn.disconnect()
        assert conn.server is None
    
    def test_disconnect_close_error(self):
        """Test disconnection when both quit and close fail."""
        conn = SMTPConnection()
        mock_server = MagicMock()
        mock_server.quit.side_effect = Exception("Quit failed")
        mock_server.close.side_effect = Exception("Close failed")
        conn.server = mock_server
        
        # Should not raise
        conn.disconnect()
        assert conn.server is None
    
    @patch('tools.smtp.smtp_client.MIMEText')
    @patch('tools.smtp.smtp_client.SMTPConnection._save_to_sent_folder')
    def test_send_email_plain(self, mock_save, mock_mimetext):
        """Test sending plain text email."""
        conn = SMTPConnection()
        mock_server = MagicMock()
        mock_server.sendmail.return_value = {}
        conn.server = mock_server
        conn.username = 'sender@test.com'
        
        mock_msg = MagicMock()
        mock_msg.as_string.return_value = 'email string'
        mock_msg.as_bytes.return_value = b'email bytes'
        mock_mimetext.return_value = mock_msg
        
        result = conn.send_email(
            ['recipient@test.com'],
            'Test Subject',
            'Test body'
        )
        
        assert result['sent'] is True
        assert result['subject'] == 'Test Subject'
        mock_server.sendmail.assert_called_once()
        mock_save.assert_called_once()
    
    @patch('tools.smtp.smtp_client.MIMEMultipart')
    @patch('tools.smtp.smtp_client.MIMEText')
    @patch('tools.smtp.smtp_client.SMTPConnection._save_to_sent_folder')
    def test_send_email_html(self, mock_save, mock_mimetext, mock_multipart):
        """Test sending HTML email."""
        conn = SMTPConnection()
        mock_server = MagicMock()
        mock_server.sendmail.return_value = {}
        conn.server = mock_server
        conn.username = 'sender@test.com'
        
        mock_msg = MagicMock()
        mock_msg.attach = MagicMock()
        mock_msg.as_string.return_value = 'email string'
        mock_msg.as_bytes.return_value = b'email bytes'
        mock_multipart.return_value = mock_msg
        
        mock_text_part = MagicMock()
        mock_html_part = MagicMock()
        mock_mimetext.side_effect = [mock_text_part, mock_html_part]
        
        result = conn.send_email(
            ['recipient@test.com'],
            'Test Subject',
            '<html>Test</html>',
            html=True,
            text_body='Test text'
        )
        
        assert result['sent'] is True
        assert mock_msg.attach.call_count == 2
    
    @patch('tools.smtp.smtp_client.MIMEText')
    @patch('tools.smtp.smtp_client.SMTPConnection._save_to_sent_folder')
    def test_send_email_with_cc_bcc(self, mock_save, mock_mimetext):
        """Test sending email with CC and BCC."""
        conn = SMTPConnection()
        mock_server = MagicMock()
        mock_server.sendmail.return_value = {}
        conn.server = mock_server
        conn.username = 'sender@test.com'
        
        mock_msg = MagicMock()
        mock_msg.as_string.return_value = 'email string'
        mock_msg.as_bytes.return_value = b'email bytes'
        mock_mimetext.return_value = mock_msg
        
        result = conn.send_email(
            ['recipient@test.com'],
            'Test Subject',
            'Test body',
            cc=['cc@test.com'],
            bcc=['bcc@test.com']
        )
        
        # Should include all recipients
        call_args = mock_server.sendmail.call_args
        recipients = call_args[0][1]
        assert 'recipient@test.com' in recipients
        assert 'cc@test.com' in recipients
        assert 'bcc@test.com' in recipients
    
    @patch('tools.smtp.smtp_client.MIMEText')
    @patch('tools.smtp.smtp_client.SMTPConnection._save_to_sent_folder')
    def test_send_email_with_reply_to(self, mock_save, mock_mimetext):
        """Test sending email with Reply-To."""
        conn = SMTPConnection()
        mock_server = MagicMock()
        mock_server.sendmail.return_value = {}
        conn.server = mock_server
        conn.username = 'sender@test.com'
        
        mock_msg = MagicMock()
        mock_msg.as_string.return_value = 'email string'
        mock_msg.as_bytes.return_value = b'email bytes'
        mock_mimetext.return_value = mock_msg
        
        result = conn.send_email(
            ['recipient@test.com'],
            'Test Subject',
            'Test body',
            reply_to='reply@test.com'
        )
        
        mock_msg.__setitem__.assert_any_call('Reply-To', 'reply@test.com')
    
    def test_send_email_not_connected(self):
        """Test sending email when not connected."""
        conn = SMTPConnection()
        
        with pytest.raises(RuntimeError, match="Not connected"):
            conn.send_email(['recipient@test.com'], 'Test', 'Body')
    
    @patch('tools.smtp.smtp_client.MIMEMultipart')
    @patch('tools.smtp.smtp_client.MIMEBase')
    @patch('tools.smtp.smtp_client.encoders')
    @patch('tools.smtp.smtp_client.os.path.exists')
    @patch('tools.smtp.smtp_client.os.path.getsize')
    @patch('tools.smtp.smtp_client.os.path.basename')
    @patch('builtins.open')
    @patch('tools.smtp.smtp_client.SMTPConnection._save_to_sent_folder')
    def test_send_email_with_attachments(self, mock_save, mock_open, mock_basename, mock_getsize, mock_exists, mock_encoders, mock_mimebase, mock_multipart):
        """Test sending email with attachments."""
        conn = SMTPConnection()
        mock_server = MagicMock()
        mock_server.sendmail.return_value = {}
        conn.server = mock_server
        conn.username = 'sender@test.com'
        
        mock_msg = MagicMock()
        mock_msg.attach = MagicMock()
        mock_msg.as_string.return_value = 'email string'
        mock_msg.as_bytes.return_value = b'email bytes'
        mock_multipart.return_value = mock_msg
        
        mock_exists.return_value = True
        mock_getsize.return_value = 1000
        mock_basename.return_value = 'file.pdf'
        
        mock_file = MagicMock()
        mock_file.read.return_value = b'file content'
        mock_open.return_value.__enter__.return_value = mock_file
        
        mock_part = MagicMock()
        mock_mimebase.return_value = mock_part
        
        result = conn.send_email_with_attachments(
            ['recipient@test.com'],
            'Test Subject',
            'Test body',
            ['/path/to/file.pdf']
        )
        
        assert result['sent'] is True
        mock_msg.attach.assert_called()
    
    @patch('tools.config.ProfileManager')
    @patch('tools.imap.imap_client.IMAPConnection')
    def test_save_to_sent_folder_success(self, mock_imap_conn, mock_pm_class):
        """Test saving to Sent folder successfully."""
        conn = SMTPConnection()
        conn.username = 'test@test.com'
        conn.password = 'password'
        conn.host = 'mail.test.com'
        
        mock_manager = MagicMock()
        mock_profile = MagicMock()
        mock_profile.username = 'test@test.com'
        mock_profile.imap_server = 'imap.test.com'
        mock_profile.imap_port = 993
        mock_profile.imap_ssl = True
        mock_profile.password = 'password'
        mock_manager.list_profiles.return_value = ['test']
        mock_manager.get_profile.return_value = mock_profile
        mock_pm_class.return_value = mock_manager
        
        mock_imap = MagicMock()
        mock_imap.find_sent_folder.return_value = 'Sent'
        mock_imap.append_to_mailbox.return_value = 123
        mock_imap_conn.return_value = mock_imap
        
        conn._save_to_sent_folder(b'message content')
        
        mock_imap.connect.assert_called_once()
        mock_imap.find_sent_folder.assert_called_once()
        mock_imap.append_to_mailbox.assert_called_once()
        mock_imap.disconnect.assert_called_once()
    
    @patch('tools.config.ProfileManager')
    @patch('tools.imap.imap_client.IMAPConnection')
    def test_save_to_sent_folder_no_profile(self, mock_imap_conn, mock_pm_class):
        """Test saving when no profile found."""
        conn = SMTPConnection()
        conn.username = 'test@test.com'
        conn.password = 'password'
        conn.host = 'mail.test.com'
        
        mock_manager = MagicMock()
        mock_manager.list_profiles.return_value = []
        mock_manager.get_default.return_value = None
        mock_pm_class.return_value = mock_manager
        
        # Should not raise, just log warning
        conn._save_to_sent_folder(b'message content')
        
        mock_imap_conn.assert_not_called()
    
    @patch('tools.config.ProfileManager')
    @patch('tools.imap.imap_client.IMAPConnection')
    def test_save_to_sent_folder_no_sent_folder(self, mock_imap_conn, mock_pm_class):
        """Test saving when Sent folder not found."""
        conn = SMTPConnection()
        conn.username = 'test@test.com'
        conn.password = 'password'
        conn.host = 'mail.test.com'
        
        mock_manager = MagicMock()
        mock_profile = MagicMock()
        mock_profile.username = 'test@test.com'
        mock_profile.imap_server = 'imap.test.com'
        mock_profile.imap_port = 993
        mock_profile.imap_ssl = True
        mock_profile.password = 'password'
        mock_manager.list_profiles.return_value = ['test']
        mock_manager.get_profile.return_value = mock_profile
        mock_pm_class.return_value = mock_manager
        
        mock_imap = MagicMock()
        mock_imap.find_sent_folder.return_value = None
        mock_imap_conn.return_value = mock_imap
        
        # Should not raise, just log warning
        conn._save_to_sent_folder(b'message content')
        
        mock_imap.append_to_mailbox.assert_not_called()
    
    @patch('tools.config.ProfileManager')
    @patch('tools.imap.imap_client.IMAPConnection')
    def test_save_to_sent_folder_error(self, mock_imap_conn, mock_pm_class):
        """Test saving when error occurs."""
        conn = SMTPConnection()
        conn.username = 'test@test.com'
        conn.password = 'password'
        conn.host = 'mail.test.com'
        
        mock_manager = MagicMock()
        mock_profile = MagicMock()
        mock_profile.username = 'test@test.com'
        mock_profile.imap_server = 'imap.test.com'
        mock_profile.imap_port = 993
        mock_profile.imap_ssl = True
        mock_profile.password = 'password'
        mock_manager.list_profiles.return_value = ['test']
        mock_manager.get_profile.return_value = mock_profile
        mock_pm_class.return_value = mock_manager
        
        mock_imap = MagicMock()
        mock_imap.connect.side_effect = Exception("Connection failed")
        mock_imap_conn.return_value = mock_imap
        
        # Should not raise, just log warning
        conn._save_to_sent_folder(b'message content')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

