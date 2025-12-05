"""
Tests for normalize_email edge cases.
"""

import pytest
from email.message import Message, EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from tools.imap.imap_client import normalize_email, MAX_BODY_BYTES


class TestNormalizeEmailEdgeCases:
    """Test normalize_email edge cases."""
    
    def test_multipart_html_not_truncated(self):
        """Test multipart HTML that doesn't need truncation."""
        msg = MIMEMultipart()
        msg['From'] = 'sender@test.com'
        msg['To'] = 'recipient@test.com'
        msg['Subject'] = 'Test'
        
        # Add HTML body that doesn't exceed limit
        html_body = MIMEText('<html>Test</html>', 'html')
        msg.attach(html_body)
        
        result = normalize_email(msg, 123, MAX_BODY_BYTES, 26214400)
        
        assert result['body']['html'] == '<html>Test</html>'
    
    def test_single_part_html_not_truncated(self):
        """Test single part HTML that doesn't need truncation."""
        msg = EmailMessage()
        msg['From'] = 'sender@test.com'
        msg['To'] = 'recipient@test.com'
        msg['Subject'] = 'Test'
        msg.set_content('<html>Test</html>', subtype='html')
        
        result = normalize_email(msg, 123, MAX_BODY_BYTES, 26214400)
        
        # EmailMessage may add newline
        assert '<html>Test</html>' in result['body']['html']
    
    def test_single_part_plain_not_truncated(self):
        """Test single part plain text that doesn't need truncation."""
        msg = EmailMessage()
        msg['From'] = 'sender@test.com'
        msg['To'] = 'recipient@test.com'
        msg['Subject'] = 'Test'
        msg.set_content('Test body', subtype='plain')
        
        result = normalize_email(msg, 123, MAX_BODY_BYTES, 26214400)
        
        assert 'Test body' in result['body']['text']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

