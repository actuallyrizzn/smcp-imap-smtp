"""
Tests for entry point execution (if __name__ == '__main__').
"""

import pytest
import subprocess
import sys
from pathlib import Path


class TestEntryPoints:
    """Test entry point execution."""
    
    def test_imap_cli_entry_point(self):
        """Test IMAP CLI entry point."""
        # Test that the file can be imported and main() exists
        from tools.imap.cli import main
        
        assert callable(main)
    
    def test_smtp_cli_entry_point(self):
        """Test SMTP CLI entry point."""
        # Test that the file can be imported and main() exists
        from tools.smtp.cli import main
        
        assert callable(main)
    
    def test_profile_cli_entry_point(self):
        """Test profile CLI entry point."""
        # Test that the file can be imported and main() exists
        from tools.profile_cli import main
        
        assert callable(main)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

