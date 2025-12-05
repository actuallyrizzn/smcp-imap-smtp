"""
Tests for error paths in config.py.
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock
from tools.config import ProfileManager, AccountProfile


class TestConfigErrorHandling:
    """Test error handling in ProfileManager."""
    
    def test_load_invalid_json(self, tmp_path):
        """Test loading invalid JSON file."""
        config_file = tmp_path / 'accounts.json'
        config_file.write_text('invalid json{')
        
        with patch('tools.config.CONFIG_FILE', config_file):
            manager = ProfileManager()
            # Should handle gracefully
            assert manager.profiles == {}
            assert manager.default_profile is None
    
    def test_load_missing_file(self, tmp_path):
        """Test loading when file doesn't exist."""
        config_file = tmp_path / 'nonexistent.json'
        
        with patch('tools.config.CONFIG_FILE', config_file):
            manager = ProfileManager()
            # Should handle gracefully
            assert manager.profiles == {}
            assert manager.default_profile is None
    
    @patch('builtins.open', side_effect=IOError("Permission denied"))
    def test_save_error(self, mock_open):
        """Test save error handling."""
        with patch('tools.config.CONFIG_FILE', Path('/nonexistent/accounts.json')):
            manager = ProfileManager()
            profile = AccountProfile(name='test', username='test@example.com')
            
            # Try to save - should raise exception
            with pytest.raises(IOError):
                manager.add_profile(profile)
    
    def test_remove_profile_not_found(self, tmp_path):
        """Test removing non-existent profile."""
        config_file = tmp_path / 'accounts.json'
        
        with patch('tools.config.CONFIG_FILE', config_file):
            manager = ProfileManager()
            result = manager.remove_profile('nonexistent')
            assert result is False
    
    def test_set_default_not_found(self, tmp_path):
        """Test setting default for non-existent profile."""
        config_file = tmp_path / 'accounts.json'
        
        with patch('tools.config.CONFIG_FILE', config_file):
            manager = ProfileManager()
            result = manager.set_default('nonexistent')
            assert result is False
    
    def test_get_default_none(self, tmp_path):
        """Test getting default when none is set."""
        config_file = tmp_path / 'accounts.json'
        
        with patch('tools.config.CONFIG_FILE', config_file):
            manager = ProfileManager()
            result = manager.get_default()
            assert result is None
    
    def test_remove_profile_clears_default(self, tmp_path):
        """Test that removing default profile clears default."""
        config_file = tmp_path / 'accounts.json'
        
        with patch('tools.config.CONFIG_FILE', config_file):
            manager = ProfileManager()
            profile = AccountProfile(name='test', username='test@example.com')
            manager.add_profile(profile)
            manager.set_default('test')
            assert manager.default_profile == 'test'
            
            manager.remove_profile('test')
            assert manager.default_profile is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

