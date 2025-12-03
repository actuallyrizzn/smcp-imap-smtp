"""
Unit tests for SMTP CLI tool.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from tools.smtp.smtp_client import SMTPConnection
from tools.smtp.cli import connect, disconnect, send, send_html, send_with_attachment


class TestSMTPConnection:
    """Test SMTP connection management."""
    
    @patch('tools.smtp.smtp_client.smtplib.SMTP')
    def test_connect_success(self, mock_smtp):
        """Test successful SMTP connection."""
        mock_client = MagicMock()
        mock_smtp.return_value = mock_client
        
        args = {
            'server': 'mail.gmx.com',
            'username': 'test@gmx.com',
            'password': 'testpass',
            'port': 587,
            'use_tls': True
        }
        
        result = connect(args)
        assert result['status'] == 'success'
        mock_client.starttls.assert_called_once()
        mock_client.login.assert_called_once_with('test@gmx.com', 'testpass')
    
    @patch('tools.smtp.smtp_client.smtplib.SMTP')
    def test_connect_auth_failure(self, mock_smtp):
        """Test authentication failure."""
        mock_client = MagicMock()
        mock_client.login.side_effect = Exception("authentication failed")
        mock_smtp.return_value = mock_client
        
        args = {
            'server': 'mail.gmx.com',
            'username': 'wrong@gmx.com',
            'password': 'wrongpass',
            'port': 587,
            'use_tls': True
        }
        
        result = connect(args)
        assert 'error' in result
        assert 'authentication' in result['error'].lower()


class TestSMTPOperations:
    """Test SMTP operations."""
    
    @pytest.fixture
    def mock_connection(self):
        """Create a mock SMTP connection."""
        conn = Mock(spec=SMTPConnection)
        conn.client = MagicMock()
        return conn
    
    @patch('tools.smtp.smtp_client.get_connection')
    def test_send_plain_text(self, mock_get_conn, mock_connection):
        """Test sending plain text email."""
        mock_get_conn.return_value = mock_connection
        mock_connection.send_email.return_value = {'message_id': '<test@example.com>'}
        
        args = {
            'to': 'recipient@example.com',
            'subject': 'Test Subject',
            'body': 'Test body'
        }
        
        result = send(args)
        
        assert result['status'] == 'success'
        mock_connection.send_email.assert_called_once()
        call_args = mock_connection.send_email.call_args
        assert call_args[1]['to'] == ['recipient@example.com']
        assert call_args[1]['subject'] == 'Test Subject'
    
    @patch('tools.smtp.smtp_client.get_connection')
    def test_send_html(self, mock_get_conn, mock_connection):
        """Test sending HTML email."""
        mock_get_conn.return_value = mock_connection
        mock_connection.send_email.return_value = {'message_id': '<test@example.com>'}
        
        args = {
            'to': 'recipient@example.com',
            'subject': 'Test Subject',
            'html': '<html><body>Test</body></html>'
        }
        
        result = send_html(args)
        
        assert result['status'] == 'success'
        mock_connection.send_email.assert_called_once()
        call_args = mock_connection.send_email.call_args
        assert call_args[1]['html'] == '<html><body>Test</body></html>'
    
    @patch('tools.smtp.smtp_client.get_connection')
    def test_send_with_attachment(self, mock_get_conn, mock_connection):
        """Test sending email with attachment."""
        mock_get_conn.return_value = mock_connection
        mock_connection.send_email.return_value = {'message_id': '<test@example.com>'}
        
        args = {
            'to': 'recipient@example.com',
            'subject': 'Test Subject',
            'body': 'Test body',
            'attachment': '/path/to/file.pdf'
        }
        
        result = send_with_attachment(args)
        
        assert result['status'] == 'success'
        mock_connection.send_email.assert_called_once()
        call_args = mock_connection.send_email.call_args
        assert 'attachments' in call_args[1]
    
    @patch('tools.smtp.smtp_client.get_connection')
    def test_send_invalid_recipient(self, mock_get_conn, mock_connection):
        """Test sending to invalid recipient."""
        mock_get_conn.return_value = mock_connection
        from smtplib import SMTPRecipientsRefused
        mock_connection.send_email.side_effect = SMTPRecipientsRefused({'invalid@': (501, b'Syntax error')})
        
        args = {
            'to': 'invalid@',
            'subject': 'Test',
            'body': 'Test'
        }
        
        result = send(args)
        
        assert 'error' in result
        assert 'invalid' in result['error'].lower() or 'syntax' in result['error'].lower()


class TestSMTPErrorHandling:
    """Test SMTP error handling."""
    
    @patch('tools.smtp.smtp_client.get_connection')
    def test_send_connection_error(self, mock_get_conn):
        """Test handling connection errors."""
        mock_conn = Mock(spec=SMTPConnection)
        mock_conn.send_email.side_effect = ConnectionError("Connection failed")
        mock_get_conn.return_value = mock_conn
        
        args = {
            'to': 'recipient@example.com',
            'subject': 'Test',
            'body': 'Test'
        }
        
        result = send(args)
        assert 'error' in result


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

