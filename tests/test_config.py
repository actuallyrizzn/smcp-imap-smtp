"""
Unit tests for account profile management.
"""

import pytest
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, mock_open
from tools.config import ProfileManager, AccountProfile, CONFIG_DIR, CONFIG_FILE


class TestAccountProfile:
    """Test AccountProfile class."""
    
    def test_profile_creation(self):
        """Test creating an account profile."""
        profile = AccountProfile(
            name='test',
            imap_server='imap.gmx.com',
            smtp_server='mail.gmx.com',
            username='test@gmx.com',
            password='testpass',
            imap_port=993,
            smtp_port=587,
            imap_ssl=True,
            smtp_tls=True
        )
        
        assert profile.name == 'test'
        assert profile.imap_server == 'imap.gmx.com'
        assert profile.username == 'test@gmx.com'
        assert profile.password == 'testpass'
        assert profile.imap_port == 993
        assert profile.smtp_port == 587
    
    def test_profile_to_dict(self):
        """Test converting profile to dictionary."""
        profile = AccountProfile(
            name='test',
            imap_server='imap.gmx.com',
            username='test@gmx.com',
            password='testpass'
        )
        
        data = profile.to_dict()
        assert data['name'] == 'test'
        assert data['imap_server'] == 'imap.gmx.com'
        assert data['username'] == 'test@gmx.com'
        assert data['password'] == 'testpass'
        assert data['imap_port'] == 993  # default
        assert data['imap_ssl'] is True  # default
    
    def test_profile_from_dict(self):
        """Test creating profile from dictionary."""
        data = {
            'name': 'test',
            'imap_server': 'imap.gmx.com',
            'smtp_server': 'mail.gmx.com',
            'username': 'test@gmx.com',
            'password': 'testpass',
            'imap_port': 993,
            'smtp_port': 587,
            'imap_ssl': True,
            'smtp_tls': True
        }
        
        profile = AccountProfile.from_dict(data)
        assert profile.name == 'test'
        assert profile.imap_server == 'imap.gmx.com'
        assert profile.username == 'test@gmx.com'
        assert profile.password == 'testpass'


class TestProfileManager:
    """Test ProfileManager class."""
    
    @pytest.fixture
    def temp_config_dir(self, tmp_path):
        """Create a temporary config directory."""
        config_dir = tmp_path / '.smcp-imap-smtp'
        config_dir.mkdir()
        config_file = config_dir / 'accounts.json'
        return config_dir, config_file
    
    def test_profile_manager_init(self, temp_config_dir):
        """Test ProfileManager initialization."""
        config_dir, config_file = temp_config_dir
        
        with patch('tools.config.CONFIG_DIR', config_dir):
            with patch('tools.config.CONFIG_FILE', config_file):
                manager = ProfileManager()
                assert manager.config_file == config_file
    
    def test_add_profile(self, temp_config_dir):
        """Test adding a profile."""
        config_dir, config_file = temp_config_dir
        
        with patch('tools.config.CONFIG_DIR', config_dir):
            with patch('tools.config.CONFIG_FILE', config_file):
                manager = ProfileManager()
                profile = AccountProfile(
                    name='test',
                    imap_server='imap.gmx.com',
                    username='test@gmx.com',
                    password='testpass'
                )
                
                manager.add_profile(profile)
                assert len(manager.profiles) == 1
                assert manager.profiles['test'].name == 'test'
    
    def test_get_profile(self, temp_config_dir):
        """Test getting a profile."""
        config_dir, config_file = temp_config_dir
        
        with patch('tools.config.CONFIG_DIR', config_dir):
            with patch('tools.config.CONFIG_FILE', config_file):
                manager = ProfileManager()
                profile = AccountProfile(
                    name='test',
                    imap_server='imap.gmx.com',
                    username='test@gmx.com',
                    password='testpass'
                )
                
                manager.add_profile(profile)
                retrieved = manager.get_profile('test')
                assert retrieved is not None
                assert retrieved.name == 'test'
                assert retrieved.username == 'test@gmx.com'
    
    def test_get_profile_not_found(self, temp_config_dir):
        """Test getting a non-existent profile."""
        config_dir, config_file = temp_config_dir
        
        with patch('tools.config.CONFIG_DIR', config_dir):
            with patch('tools.config.CONFIG_FILE', config_file):
                manager = ProfileManager()
                retrieved = manager.get_profile('nonexistent')
                assert retrieved is None
    
    def test_set_default(self, temp_config_dir):
        """Test setting default profile."""
        config_dir, config_file = temp_config_dir
        
        with patch('tools.config.CONFIG_DIR', config_dir):
            with patch('tools.config.CONFIG_FILE', config_file):
                manager = ProfileManager()
                profile = AccountProfile(
                    name='test',
                    imap_server='imap.gmx.com',
                    username='test@gmx.com',
                    password='testpass'
                )
                
                manager.add_profile(profile)
                manager.set_default('test')
                assert manager.default_profile == 'test'
                assert manager.get_default().name == 'test'
    
    def test_remove_profile(self, temp_config_dir):
        """Test removing a profile."""
        config_dir, config_file = temp_config_dir
        
        with patch('tools.config.CONFIG_DIR', config_dir):
            with patch('tools.config.CONFIG_FILE', config_file):
                manager = ProfileManager()
                profile = AccountProfile(
                    name='test',
                    imap_server='imap.gmx.com',
                    username='test@gmx.com',
                    password='testpass'
                )
                
                manager.add_profile(profile)
                assert len(manager.profiles) == 1
                
                manager.remove_profile('test')
                assert len(manager.profiles) == 0
                assert manager.get_profile('test') is None
    
    def test_list_profiles(self, temp_config_dir):
        """Test listing profiles."""
        config_dir, config_file = temp_config_dir
        
        with patch('tools.config.CONFIG_DIR', config_dir):
            with patch('tools.config.CONFIG_FILE', config_file):
                manager = ProfileManager()
                profile1 = AccountProfile(
                    name='test1',
                    imap_server='imap.gmx.com',
                    username='test1@gmx.com',
                    password='pass1'
                )
                profile2 = AccountProfile(
                    name='test2',
                    imap_server='imap.aol.com',
                    username='test2@aol.com',
                    password='pass2'
                )
                
                manager.add_profile(profile1)
                manager.add_profile(profile2)
                
                profiles = manager.list_profiles()
                assert len(profiles) == 2
                assert 'test1' in profiles
                assert 'test2' in profiles
    
    def test_get_profile_by_username(self, temp_config_dir):
        """Test getting profile by username (manual search)."""
        config_dir, config_file = temp_config_dir
        
        with patch('tools.config.CONFIG_DIR', config_dir):
            with patch('tools.config.CONFIG_FILE', config_file):
                manager = ProfileManager()
                profile = AccountProfile(
                    name='test',
                    imap_server='imap.gmx.com',
                    username='test@gmx.com',
                    password='testpass'
                )
                
                manager.add_profile(profile)
                # Manual search since get_profile_by_username doesn't exist
                retrieved = None
                for p in manager.profiles.values():
                    if p.username == 'test@gmx.com':
                        retrieved = p
                        break
                assert retrieved is not None
                assert retrieved.name == 'test'
    
    def test_save_and_load(self, temp_config_dir):
        """Test saving and loading profiles."""
        config_dir, config_file = temp_config_dir
        
        with patch('tools.config.CONFIG_DIR', config_dir):
            with patch('tools.config.CONFIG_FILE', config_file):
                # Create and save (add_profile calls _save internally)
                manager1 = ProfileManager()
                profile = AccountProfile(
                    name='test',
                    imap_server='imap.gmx.com',
                    username='test@gmx.com',
                    password='testpass'
                )
                manager1.add_profile(profile)
                manager1.set_default('test')  # Also calls _save
                
                # Load in new manager (loads automatically in __init__)
                manager2 = ProfileManager()
                
                assert len(manager2.profiles) == 1
                assert manager2.profiles['test'].name == 'test'
                assert manager2.default_profile == 'test'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

