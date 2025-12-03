#!/usr/bin/env python3
"""
Generate malformed MIME test corpus for testing robust email parsing.
"""

import os
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

def create_missing_boundary():
    """Create multipart message with missing boundary."""
    msg = EmailMessage()
    msg['From'] = 'test@example.com'
    msg['To'] = 'recipient@example.com'
    msg['Subject'] = 'Missing Boundary Test'
    msg['Content-Type'] = 'multipart/mixed'  # Missing boundary parameter
    msg.set_payload('This should cause parsing issues')
    return msg.as_bytes()

def create_invalid_encoding():
    """Create message with invalid encoding."""
    msg = EmailMessage()
    msg['From'] = 'test@example.com'
    msg['To'] = 'recipient@example.com'
    msg['Subject'] = 'Invalid Encoding Test'
    # Invalid encoding in header
    msg['Subject'] = 'Test \xff\xfe\xfd'  # Invalid UTF-8
    msg.set_content('Body with invalid encoding: \xff\xfe\xfd')
    return msg.as_bytes()

def create_corrupted_headers():
    """Create message with corrupted/missing headers."""
    msg = EmailMessage()
    # Missing From header
    msg['To'] = 'invalid-email-address'  # Malformed
    # Missing Date header
    msg['Subject'] = 'Corrupted Headers Test'
    msg.set_content('Test body')
    return msg.as_bytes()

def create_nested_multipart():
    """Create deeply nested multipart message."""
    msg = MIMEMultipart('mixed')
    msg['From'] = 'test@example.com'
    msg['To'] = 'recipient@example.com'
    msg['Subject'] = 'Nested Multipart Test'
    
    # Create 5 levels of nesting
    current = msg
    for i in range(5):
        nested = MIMEMultipart('alternative')
        nested.attach(MIMEText(f'Level {i} text', 'plain'))
        nested.attach(MIMEText(f'<p>Level {i} HTML</p>', 'html'))
        current.attach(nested)
        current = nested
    
    return msg.as_bytes()

def create_missing_content_type():
    """Create message without Content-Type header."""
    msg = EmailMessage()
    msg['From'] = 'test@example.com'
    msg['To'] = 'recipient@example.com'
    msg['Subject'] = 'Missing Content-Type Test'
    # No Content-Type header
    msg.set_payload('Plain text body without Content-Type')
    return msg.as_bytes()

def create_invalid_dates():
    """Create message with invalid date formats."""
    msg = EmailMessage()
    msg['From'] = 'test@example.com'
    msg['To'] = 'recipient@example.com'
    msg['Subject'] = 'Invalid Date Test'
    msg['Date'] = 'Not a valid date format'  # Invalid date
    msg.set_content('Test body')
    return msg.as_bytes()

def create_oversized_headers():
    """Create message with oversized headers."""
    msg = EmailMessage()
    msg['From'] = 'test@example.com'
    msg['To'] = 'recipient@example.com'
    msg['Subject'] = 'Oversized Headers Test'
    # Create oversized header (10KB+)
    large_value = 'X' * 15000
    msg['X-Large-Header'] = large_value
    msg.set_content('Test body')
    return msg.as_bytes()

def create_mixed_encoding():
    """Create message with mixed character encodings."""
    msg = EmailMessage()
    msg['From'] = 'test@example.com'
    msg['To'] = 'recipient@example.com'
    msg['Subject'] = 'Mixed Encoding Test'
    # Mix different encodings
    msg.set_content('ASCII text', charset='us-ascii')
    # Add part with different encoding
    msg.add_attachment('UTF-8 text: 测试', charset='utf-8')
    return msg.as_bytes()

def main():
    """Generate all test files."""
    test_dir = os.path.dirname(os.path.abspath(__file__))
    
    test_cases = [
        ('missing_boundary.eml', create_missing_boundary),
        ('invalid_encoding.eml', create_invalid_encoding),
        ('corrupted_headers.eml', create_corrupted_headers),
        ('nested_multipart.eml', create_nested_multipart),
        ('missing_content_type.eml', create_missing_content_type),
        ('invalid_dates.eml', create_invalid_dates),
        ('oversized_headers.eml', create_oversized_headers),
        ('mixed_encoding.eml', create_mixed_encoding),
    ]
    
    for filename, generator in test_cases:
        filepath = os.path.join(test_dir, filename)
        try:
            content = generator()
            with open(filepath, 'wb') as f:
                f.write(content)
            print(f"Generated: {filename}")
        except Exception as e:
            print(f"Error generating {filename}: {e}")
    
    print(f"\nTest corpus generated in {test_dir}")

if __name__ == '__main__':
    main()

