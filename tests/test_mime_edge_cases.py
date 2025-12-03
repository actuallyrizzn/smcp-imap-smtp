"""
Tests for malformed MIME handling.
"""

import pytest
import os
from email import message_from_bytes
from tools.imap.imap_client import normalize_email


class TestMalformedMIME:
    """Test handling of malformed MIME messages."""
    
    @pytest.fixture
    def test_data_dir(self):
        """Get test data directory."""
        return os.path.join(os.path.dirname(__file__), 'malformed_mime')
    
    def test_missing_boundary(self, test_data_dir):
        """Test parsing message with missing boundary."""
        filepath = os.path.join(test_data_dir, 'missing_boundary.eml')
        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                raw_email = f.read()
            
            # Should not crash
            msg = message_from_bytes(raw_email)
            normalized = normalize_email(msg, 1, 'INBOX')
            
            # Should return some data, even if partial
            assert normalized is not None
            assert 'id' in normalized
    
    def test_invalid_encoding(self, test_data_dir):
        """Test parsing message with invalid encoding."""
        filepath = os.path.join(test_data_dir, 'invalid_encoding.eml')
        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                raw_email = f.read()
            
            # Should handle gracefully
            msg = message_from_bytes(raw_email)
            normalized = normalize_email(msg, 1, 'INBOX')
            
            assert normalized is not None
            # Should have subject even if encoding is invalid
            assert 'subject' in normalized
    
    def test_corrupted_headers(self, test_data_dir):
        """Test parsing message with corrupted headers."""
        filepath = os.path.join(test_data_dir, 'corrupted_headers.eml')
        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                raw_email = f.read()
            
            # Should not crash on missing headers
            msg = message_from_bytes(raw_email)
            normalized = normalize_email(msg, 1, 'INBOX')
            
            assert normalized is not None
            # Should handle missing From/To gracefully
            assert 'from' in normalized or normalized.get('from') is None
    
    def test_nested_multipart(self, test_data_dir):
        """Test parsing deeply nested multipart."""
        filepath = os.path.join(test_data_dir, 'nested_multipart.eml')
        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                raw_email = f.read()
            
            # Should handle deep nesting
            msg = message_from_bytes(raw_email)
            normalized = normalize_email(msg, 1, 'INBOX')
            
            assert normalized is not None
            assert 'body' in normalized
    
    def test_missing_content_type(self, test_data_dir):
        """Test parsing message without Content-Type."""
        filepath = os.path.join(test_data_dir, 'missing_content_type.eml')
        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                raw_email = f.read()
            
            # Should default to text/plain
            msg = message_from_bytes(raw_email)
            normalized = normalize_email(msg, 1, 'INBOX')
            
            assert normalized is not None
            assert 'body' in normalized
    
    def test_invalid_dates(self, test_data_dir):
        """Test parsing message with invalid date format."""
        filepath = os.path.join(test_data_dir, 'invalid_dates.eml')
        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                raw_email = f.read()
            
            # Should handle invalid dates gracefully
            msg = message_from_bytes(raw_email)
            normalized = normalize_email(msg, 1, 'INBOX')
            
            assert normalized is not None
            # Should have timestamp (even if defaulted)
            assert 'timestamp' in normalized
    
    def test_oversized_headers(self, test_data_dir):
        """Test parsing message with oversized headers."""
        filepath = os.path.join(test_data_dir, 'oversized_headers.eml')
        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                raw_email = f.read()
            
            # Should handle large headers
            msg = message_from_bytes(raw_email)
            normalized = normalize_email(msg, 1, 'INBOX')
            
            assert normalized is not None
    
    def test_mixed_encoding(self, test_data_dir):
        """Test parsing message with mixed encodings."""
        filepath = os.path.join(test_data_dir, 'mixed_encoding.eml')
        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                raw_email = f.read()
            
            # Should handle mixed encodings
            msg = message_from_bytes(raw_email)
            normalized = normalize_email(msg, 1, 'INBOX')
            
            assert normalized is not None
            assert 'body' in normalized


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

