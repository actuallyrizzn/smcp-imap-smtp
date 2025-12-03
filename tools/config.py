"""
Account profile management for IMAP/SMTP tools.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)

# Default config directory
CONFIG_DIR = Path.home() / '.smcp-imap-smtp'
CONFIG_FILE = CONFIG_DIR / 'accounts.json'


class AccountProfile:
    """Represents an email account profile."""
    
    def __init__(self, name: str, imap_server: str = None, smtp_server: str = None,
                 username: str = None, password: str = None,
                 imap_port: int = 993, smtp_port: int = 587,
                 imap_ssl: bool = True, smtp_tls: bool = True):
        self.name = name
        self.imap_server = imap_server
        self.smtp_server = smtp_server
        self.username = username
        self.password = password
        self.imap_port = imap_port
        self.smtp_port = smtp_port
        self.imap_ssl = imap_ssl
        self.smtp_tls = smtp_tls
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary."""
        return {
            'name': self.name,
            'imap_server': self.imap_server,
            'smtp_server': self.smtp_server,
            'username': self.username,
            'password': self.password,  # In production, this should be encrypted
            'imap_port': self.imap_port,
            'smtp_port': self.smtp_port,
            'imap_ssl': self.imap_ssl,
            'smtp_tls': self.smtp_tls
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AccountProfile':
        """Create profile from dictionary."""
        return cls(
            name=data['name'],
            imap_server=data.get('imap_server'),
            smtp_server=data.get('smtp_server'),
            username=data.get('username'),
            password=data.get('password'),
            imap_port=data.get('imap_port', 993),
            smtp_port=data.get('smtp_port', 587),
            imap_ssl=data.get('imap_ssl', True),
            smtp_tls=data.get('smtp_tls', True)
        )


class ProfileManager:
    """Manages account profiles."""
    
    def __init__(self, config_file: Path = None):
        self.config_file = config_file or CONFIG_FILE
        self.profiles: Dict[str, AccountProfile] = {}
        self.default_profile: Optional[str] = None
        self._load()
    
    def _load(self) -> None:
        """Load profiles from config file."""
        if not self.config_file.exists():
            return
        
        try:
            with open(self.config_file, 'r') as f:
                data = json.load(f)
            
            self.profiles = {
                name: AccountProfile.from_dict(profile_data)
                for name, profile_data in data.get('profiles', {}).items()
            }
            self.default_profile = data.get('default_profile')
        except Exception as e:
            logger.warning(f"Failed to load profiles: {e}")
            self.profiles = {}
            self.default_profile = None
    
    def _save(self) -> None:
        """Save profiles to config file."""
        # Create config directory if it doesn't exist
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            'profiles': {
                name: profile.to_dict()
                for name, profile in self.profiles.items()
            },
            'default_profile': self.default_profile
        }
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save profiles: {e}")
            raise
    
    def add_profile(self, profile: AccountProfile) -> None:
        """Add or update a profile."""
        self.profiles[profile.name] = profile
        self._save()
    
    def get_profile(self, name: str) -> Optional[AccountProfile]:
        """Get a profile by name."""
        return self.profiles.get(name)
    
    def list_profiles(self) -> List[str]:
        """List all profile names."""
        return list(self.profiles.keys())
    
    def remove_profile(self, name: str) -> bool:
        """Remove a profile."""
        if name in self.profiles:
            del self.profiles[name]
            if self.default_profile == name:
                self.default_profile = None
            self._save()
            return True
        return False
    
    def set_default(self, name: str) -> bool:
        """Set default profile."""
        if name in self.profiles:
            self.default_profile = name
            self._save()
            return True
        return False
    
    def get_default(self) -> Optional[AccountProfile]:
        """Get default profile."""
        if self.default_profile:
            return self.profiles.get(self.default_profile)
        return None

