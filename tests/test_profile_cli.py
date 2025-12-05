"""
Unit tests for profile CLI tool.
"""

import pytest
import json
import sys
from unittest.mock import patch, MagicMock, mock_open
from tools.config import ProfileManager, AccountProfile


class TestProfileCLI:
    """Test profile CLI commands."""
    
    @pytest.fixture
    def mock_manager(self):
        """Create a mock ProfileManager."""
        manager = MagicMock(spec=ProfileManager)
        manager.profiles = {}
        manager.default_profile = None
        manager.list_profiles.return_value = []
        manager.get_profile.return_value = None
        manager.get_default.return_value = None
        return manager
    
    @patch('tools.profile_cli.ProfileManager')
    def test_list_profiles_empty(self, mock_pm_class):
        """Test listing profiles when none exist."""
        from tools.profile_cli import list_profiles
        
        mock_manager = MagicMock()
        mock_manager.list_profiles.return_value = []
        mock_manager.default_profile = None
        mock_pm_class.return_value = mock_manager
        
        args = MagicMock()
        list_profiles(args)
        
        # Should not raise
        mock_manager.list_profiles.assert_called_once()
    
    @patch('tools.profile_cli.ProfileManager')
    def test_add_profile(self, mock_pm_class):
        """Test adding a profile."""
        from tools.profile_cli import add_profile
        
        mock_manager = MagicMock()
        mock_pm_class.return_value = mock_manager
        
        args = MagicMock()
        args.name = 'test'
        args.imap_server = 'imap.gmx.com'
        args.smtp_server = 'mail.gmx.com'
        args.username = 'test@gmx.com'
        args.password = 'testpass'
        args.imap_port = 993
        args.smtp_port = 587
        args.imap_ssl = True
        args.smtp_tls = True
        
        add_profile(args)
        
        mock_manager.add_profile.assert_called_once()
        # add_profile internally calls _save, so we don't need to check save()
    
    @patch('tools.profile_cli.ProfileManager')
    def test_set_default(self, mock_pm_class):
        """Test setting default profile."""
        from tools.profile_cli import set_default
        
        mock_manager = MagicMock()
        mock_manager.set_default.return_value = True
        mock_pm_class.return_value = mock_manager
        
        args = MagicMock()
        args.name = 'test'
        
        set_default(args)
        
        mock_manager.set_default.assert_called_once_with('test')
        # set_default internally calls _save
    
    @patch('tools.profile_cli.ProfileManager')
    def test_remove_profile(self, mock_pm_class):
        """Test removing a profile."""
        from tools.profile_cli import remove_profile
        
        mock_manager = MagicMock()
        mock_manager.remove_profile.return_value = True
        mock_pm_class.return_value = mock_manager
        
        args = MagicMock()
        args.name = 'test'
        
        remove_profile(args)
        
        mock_manager.remove_profile.assert_called_once_with('test')
        # remove_profile internally calls _save


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

