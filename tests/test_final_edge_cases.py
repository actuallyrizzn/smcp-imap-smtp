"""
Tests for final edge cases to reach 100% coverage.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from tools.imap.imap_client import IMAPConnection
from tools.smtp.smtp_client import SMTPConnection


class TestFinalEdgeCases:
    """Test final edge cases."""
    
    def test_find_sent_folder_exact_match(self):
        """Test find_sent_folder with exact match."""
        conn = IMAPConnection()
        mock_client = MagicMock()
        mock_client.list_folders.return_value = [
            (b'\\HasNoChildren', b'/', b'INBOX'),
            (b'\\HasNoChildren', b'/', b'Sent'),
        ]
        conn.client = mock_client
        
        result = conn.find_sent_folder()
        
        assert result == 'Sent'
    
    def test_find_sent_folder_case_insensitive(self):
        """Test find_sent_folder with case-insensitive match."""
        conn = IMAPConnection()
        mock_client = MagicMock()
        mock_client.list_folders.return_value = [
            (b'\\HasNoChildren', b'/', b'INBOX'),
            (b'\\HasNoChildren', b'/', b'SENT'),
        ]
        conn.client = mock_client
        
        result = conn.find_sent_folder()
        
        assert result == 'SENT'
    
    def test_send_email_with_cc(self):
        """Test send_email with CC."""
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
                    cc=['cc@test.com']
                )
                
                assert result['sent'] is True
                assert 'cc@test.com' in result['cc']
    
    def test_send_email_with_bcc(self):
        """Test send_email with BCC."""
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
                    bcc=['bcc@test.com']
                )
                
                assert result['sent'] is True
                assert 'bcc@test.com' in result['bcc']
    
    @patch('tools.config.ProfileManager')
    def test_save_to_sent_folder_profile_exception(self, mock_pm_class):
        """Test save when profile loading raises exception."""
        conn = SMTPConnection()
        conn.username = 'test@test.com'
        conn.password = 'password'
        
        mock_manager = MagicMock()
        mock_manager.list_profiles.side_effect = Exception("Profile error")
        mock_pm_class.return_value = mock_manager
        
        # Should not raise, just log warning
        conn._save_to_sent_folder(b'message content')
    
    def test_save_to_sent_folder_outer_exception(self):
        """Test save when outer exception occurs."""
        conn = SMTPConnection()
        conn.username = 'test@test.com'
        conn.password = 'password'
        
        # Make IMAP import fail by patching the import inside the function
        def mock_import(name, *args, **kwargs):
            if name == 'tools.imap.imap_client':
                raise Exception("Import error")
            return __import__(name, *args, **kwargs)
        
        with patch('builtins.__import__', side_effect=mock_import):
            # Should not raise, just log warning
            conn._save_to_sent_folder(b'message content')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

