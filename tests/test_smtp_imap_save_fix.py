"""
Tests for SMTP-to-IMAP sent folder save bug fixes.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, mock_open
from tools.smtp.smtp_client import SMTPConnection


class TestSMTPIMAPSaveFix:
    """Test fixes for SMTP-to-IMAP sent folder save."""
    
    @patch('tools.imap.imap_client.IMAPConnection')
    def test_save_with_derived_imap_server(self, mock_imap_conn):
        """Test save when IMAP server is derived from SMTP server."""
        conn = SMTPConnection()
        conn.host = 'mail.gmx.com'  # SMTP server
        conn.username = 'test@gmx.com'
        conn.password = 'password'
        
        mock_imap = MagicMock()
        mock_imap.find_sent_folder.return_value = 'Sent'
        mock_imap.append_to_mailbox.return_value = 123
        mock_imap_conn.return_value = mock_imap
        
        conn._save_to_sent_folder(b'message content')
        
        # Should derive imap.gmx.com from mail.gmx.com
        mock_imap.connect.assert_called_once()
        call_args = mock_imap.connect.call_args[0]
        assert call_args[0] == 'imap.gmx.com'  # Derived IMAP server
        assert call_args[1] == 'test@gmx.com'
        mock_imap.append_to_mailbox.assert_called_once()
    
    @patch('tools.imap.imap_client.IMAPConnection')
    def test_save_with_explicit_imap_server(self, mock_imap_conn):
        """Test save when IMAP server is explicitly set."""
        conn = SMTPConnection()
        conn.host = 'mail.gmx.com'
        conn.username = 'test@gmx.com'
        conn.password = 'password'
        conn.imap_server = 'imap.gmx.com'  # Explicit IMAP server
        conn.imap_port = 993
        conn.imap_ssl = True
        
        mock_imap = MagicMock()
        mock_imap.find_sent_folder.return_value = 'Sent'
        mock_imap.append_to_mailbox.return_value = 123
        mock_imap_conn.return_value = mock_imap
        
        conn._save_to_sent_folder(b'message content')
        
        # Should use explicit IMAP server, not derive
        mock_imap.connect.assert_called_once()
        call_args = mock_imap.connect.call_args[0]
        assert call_args[0] == 'imap.gmx.com'
        assert call_args[2] == 'password'
        assert call_args[3] == 993
        assert call_args[4] is True
    
    @patch('tools.imap.imap_client.IMAPConnection')
    def test_save_with_same_hostname(self, mock_imap_conn):
        """Test save when SMTP and IMAP use same hostname."""
        conn = SMTPConnection()
        conn.host = 'email.example.com'  # No mail/smtp prefix, doesn't match patterns
        conn.username = 'test@example.com'
        conn.password = 'password'
        
        mock_imap = MagicMock()
        mock_imap.find_sent_folder.return_value = 'Sent'
        mock_imap.append_to_mailbox.return_value = 123
        mock_imap_conn.return_value = mock_imap
        
        conn._save_to_sent_folder(b'message content')
        
        # Should use same hostname as fallback when no pattern matches
        mock_imap.connect.assert_called_once()
        call_args = mock_imap.connect.call_args[0]
        assert call_args[0] == 'email.example.com'  # Same as SMTP (no pattern match)
    
    def test_save_import_path_plugins(self):
        """Test save tries plugins.imap.imap_client import path."""
        conn = SMTPConnection()
        conn.host = 'mail.test.com'
        conn.username = 'test@test.com'
        conn.password = 'password'
        
        # Mock the import to try plugins path
        with patch('builtins.__import__') as mock_import:
            # First try tools.imap fails
            # Second try plugins.imap succeeds
            mock_module = MagicMock()
            mock_module.IMAPConnection = MagicMock()
            mock_import.side_effect = [
                ImportError("No module named 'tools.imap.imap_client'"),
                mock_module
            ]
            
            # Should not raise
            conn._save_to_sent_folder(b'message content')
            
            # Should have tried both import paths
            assert mock_import.call_count >= 2
    
    def test_save_import_path_relative(self):
        """Test save tries relative import as last resort."""
        conn = SMTPConnection()
        conn.host = 'mail.test.com'
        conn.username = 'test@test.com'
        conn.password = 'password'
        
        # Mock both standard imports to fail, then relative succeeds
        with patch('builtins.__import__') as mock_import:
            with patch('os.path.exists', return_value=True):
                with patch('sys.path') as mock_path:
                    mock_module = MagicMock()
                    mock_module.IMAPConnection = MagicMock()
                    
                    def import_side_effect(name, *args, **kwargs):
                        if 'imap' in name:
                            if mock_import.call_count < 2:
                                raise ImportError(f"No module named '{name}'")
                            return mock_module
                        return __import__(name, *args, **kwargs)
                    
                    mock_import.side_effect = import_side_effect
                    
                    # Should not raise
                    conn._save_to_sent_folder(b'message content')
    
    @patch('tools.imap.imap_client.IMAPConnection')
    def test_save_with_smtp_smtp_prefix(self, mock_imap_conn):
        """Test save derives IMAP from smtp. prefix."""
        conn = SMTPConnection()
        conn.host = 'smtp.gmail.com'
        conn.username = 'test@gmail.com'
        conn.password = 'password'
        
        mock_imap = MagicMock()
        mock_imap.find_sent_folder.return_value = 'Sent'
        mock_imap.append_to_mailbox.return_value = 123
        mock_imap_conn.return_value = mock_imap
        
        conn._save_to_sent_folder(b'message content')
        
        # Should derive imap.gmail.com from smtp.gmail.com
        mock_imap.connect.assert_called_once()
        call_args = mock_imap.connect.call_args[0]
        assert call_args[0] == 'imap.gmail.com'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

