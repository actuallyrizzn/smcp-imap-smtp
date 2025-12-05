"""
Tests for normalize_email function edge cases.
"""

import pytest
from email.message import Message, EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from tools.imap.imap_client import normalize_email, MAX_BODY_BYTES, MAX_ATTACHMENT_BYTES


class TestNormalizeEmail:
    """Test normalize_email function."""
    
    def test_multipart_with_attachment_truncated(self):
        """Test multipart message with large attachment."""
        msg = MIMEMultipart()
        msg['From'] = 'sender@test.com'
        msg['To'] = 'recipient@test.com'
        msg['Subject'] = 'Test'
        
        # Add body
        body = MIMEText('Test body', 'plain')
        msg.attach(body)
        
        # Add large attachment
        attachment = MIMEBase('application', 'octet-stream')
        large_data = b'x' * (MAX_ATTACHMENT_BYTES + 1000)
        attachment.set_payload(large_data)
        attachment.add_header('Content-Disposition', 'attachment; filename="large.bin"')
        msg.attach(attachment)
        
        result = normalize_email(msg, 123, MAX_BODY_BYTES, MAX_ATTACHMENT_BYTES)
        
        assert len(result['body']['attachments']) == 1
        assert result['body']['attachments'][0]['truncated'] is True
        assert result['body']['attachments'][0]['size'] == MAX_ATTACHMENT_BYTES
    
    def test_multipart_text_plain_truncated(self):
        """Test multipart message with truncated plain text."""
        msg = MIMEMultipart()
        msg['From'] = 'sender@test.com'
        msg['To'] = 'recipient@test.com'
        msg['Subject'] = 'Test'
        
        # Add large plain text body
        large_text = 'x' * (MAX_BODY_BYTES + 1000)
        body = MIMEText(large_text, 'plain')
        msg.attach(body)
        
        result = normalize_email(msg, 123, MAX_BODY_BYTES, MAX_ATTACHMENT_BYTES)
        
        assert len(result['body']['text']) == MAX_BODY_BYTES
    
    def test_multipart_text_html_truncated(self):
        """Test multipart message with truncated HTML."""
        msg = MIMEMultipart()
        msg['From'] = 'sender@test.com'
        msg['To'] = 'recipient@test.com'
        msg['Subject'] = 'Test'
        
        # Add large HTML body
        large_html = '<html>' + 'x' * (MAX_BODY_BYTES + 1000) + '</html>'
        body = MIMEText(large_html, 'html')
        msg.attach(body)
        
        result = normalize_email(msg, 123, MAX_BODY_BYTES, MAX_ATTACHMENT_BYTES)
        
        assert len(result['body']['html']) == MAX_BODY_BYTES
    
    def test_single_part_html(self):
        """Test single part HTML message."""
        msg = EmailMessage()
        msg['From'] = 'sender@test.com'
        msg['To'] = 'recipient@test.com'
        msg['Subject'] = 'Test'
        msg.set_content('<html>Test</html>', subtype='html')
        
        result = normalize_email(msg, 123, MAX_BODY_BYTES, MAX_ATTACHMENT_BYTES)
        
        # EmailMessage may add newline, so check contains
        assert '<html>Test</html>' in result['body']['html']
        assert result['body']['text'] == ''
    
    def test_single_part_html_truncated(self):
        """Test single part HTML message with truncation."""
        msg = EmailMessage()
        msg['From'] = 'sender@test.com'
        msg['To'] = 'recipient@test.com'
        msg['Subject'] = 'Test'
        large_html = '<html>' + 'x' * (MAX_BODY_BYTES + 1000) + '</html>'
        msg.set_content(large_html, subtype='html')
        
        result = normalize_email(msg, 123, MAX_BODY_BYTES, MAX_ATTACHMENT_BYTES)
        
        assert len(result['body']['html']) == MAX_BODY_BYTES
    
    def test_single_part_plain_truncated(self):
        """Test single part plain text message with truncation."""
        msg = EmailMessage()
        msg['From'] = 'sender@test.com'
        msg['To'] = 'recipient@test.com'
        msg['Subject'] = 'Test'
        large_text = 'x' * (MAX_BODY_BYTES + 1000)
        msg.set_content(large_text, subtype='plain')
        
        result = normalize_email(msg, 123, MAX_BODY_BYTES, MAX_ATTACHMENT_BYTES)
        
        assert len(result['body']['text']) == MAX_BODY_BYTES
    
    def test_multipart_decode_error(self):
        """Test multipart message with decode error."""
        msg = MIMEMultipart()
        msg['From'] = 'sender@test.com'
        msg['To'] = 'recipient@test.com'
        msg['Subject'] = 'Test'
        
        # Create part that will fail to decode
        part = MIMEBase('text', 'plain')
        # Set invalid payload that will cause decode error
        part.set_payload(b'\xff\xfe\x00\x01')  # Invalid UTF-8 sequence
        
        msg.attach(part)
        
        # Should not raise, just skip the part
        result = normalize_email(msg, 123, MAX_BODY_BYTES, MAX_ATTACHMENT_BYTES)
        
        assert result is not None
    
    def test_single_part_decode_error(self):
        """Test single part message with decode error."""
        msg = Message()
        msg['From'] = 'sender@test.com'
        msg['To'] = 'recipient@test.com'
        msg['Subject'] = 'Test'
        # Set invalid payload that will cause decode error
        # Use bytes payload that can't be decoded as UTF-8
        msg.set_payload(b'\xff\xfe\x00\x01', charset='utf-8')
        
        # Should not raise, just skip body (decode will fail in try/except)
        result = normalize_email(msg, 123, MAX_BODY_BYTES, MAX_ATTACHMENT_BYTES)
        
        assert result is not None
        # Body may be empty or contain partial decode
        assert 'body' in result


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

