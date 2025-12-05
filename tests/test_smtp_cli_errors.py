"""
Tests for SMTP CLI error paths and edge cases.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from tools.smtp.cli import send, send_html, send_with_attachment


class TestSMTPCLIErrors:
    """Test SMTP CLI error handling."""
    
    def test_send_missing_to(self):
        """Test send with missing 'to'."""
        result = send({'subject': 'Test', 'body': 'Body'})
        
        assert 'error' in result
        assert 'to' in result['error'].lower()
    
    def test_send_missing_subject(self):
        """Test send with missing subject."""
        result = send({'to': ['test@test.com'], 'body': 'Body'})
        
        assert 'error' in result
        assert 'subject' in result['error'].lower()
    
    def test_send_missing_body(self):
        """Test send with missing body."""
        result = send({'to': ['test@test.com'], 'subject': 'Test'})
        
        assert 'error' in result
        assert 'body' in result['error'].lower()
    
    def test_send_html_missing_html_body(self):
        """Test send-html with missing html_body."""
        result = send_html({'to': ['test@test.com'], 'subject': 'Test'})
        
        assert 'error' in result
        assert 'html-body' in result['error'].lower()
    
    def test_send_with_attachment_missing_attachments(self):
        """Test send-with-attachment with missing attachments."""
        result = send_with_attachment({
            'to': ['test@test.com'],
            'subject': 'Test',
            'body': 'Body'
        })
        
        assert 'error' in result
        assert 'attachments' in result['error'].lower()
    
    @patch('tools.smtp.cli._auto_connect')
    def test_send_connection_error(self, mock_auto_connect):
        """Test send when connection fails."""
        mock_auto_connect.side_effect = RuntimeError("Connection failed")
        
        result = send({
            'to': ['test@test.com'],
            'subject': 'Test',
            'body': 'Body'
        })
        
        assert 'error' in result
        assert 'connection failed' in result['error'].lower()
    
    @patch('tools.smtp.cli._auto_connect')
    @patch('tools.smtp.smtp_client.get_connection')
    def test_send_operation_error(self, mock_get, mock_auto_connect):
        """Test send when operation fails."""
        mock_conn = MagicMock()
        mock_conn.send_email.side_effect = Exception("Send failed")
        mock_auto_connect.return_value = (mock_conn, True)
        mock_get.return_value = None
        
        result = send({
            'to': ['test@test.com'],
            'subject': 'Test',
            'body': 'Body'
        })
        
        assert 'error' in result
        assert 'failed' in result['error'].lower()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

