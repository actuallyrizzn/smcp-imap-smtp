#!/usr/bin/env python3
"""
Account profile management CLI tool.
"""

import argparse
import json
import sys
import os
from pathlib import Path

# Handle imports
try:
    from .config import ProfileManager, AccountProfile
except ImportError:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    sys.path.insert(0, project_root)
    from tools.config import ProfileManager, AccountProfile


def list_profiles(args):
    """List all profiles."""
    manager = ProfileManager()
    profiles = manager.list_profiles()
    default = manager.default_profile
    
    if not profiles:
        print(json.dumps({
            "status": "success",
            "result": {
                "profiles": [],
                "message": "No profiles configured"
            }
        }))
        return
    
    result = {
        "status": "success",
        "result": {
            "profiles": profiles,
            "default": default,
            "count": len(profiles)
        }
    }
    print(json.dumps(result, indent=2))


def add_profile(args):
    """Add a new profile."""
    manager = ProfileManager()
    
    profile = AccountProfile(
        name=args.name,
        imap_server=args.imap_server,
        smtp_server=args.smtp_server,
        username=args.username,
        password=args.password,
        imap_port=args.imap_port,
        smtp_port=args.smtp_port,
        imap_ssl=args.imap_ssl,
        smtp_tls=args.smtp_tls
    )
    
    manager.add_profile(profile)
    
    print(json.dumps({
        "status": "success",
        "result": {
            "profile": profile.name,
            "message": f"Profile '{profile.name}' added successfully"
        }
    }))


def remove_profile(args):
    """Remove a profile."""
    manager = ProfileManager()
    
    if manager.remove_profile(args.name):
        print(json.dumps({
            "status": "success",
            "result": {
                "profile": args.name,
                "message": f"Profile '{args.name}' removed successfully"
            }
        }))
    else:
        print(json.dumps({
            "error": f"Profile '{args.name}' not found"
        }))
        sys.exit(1)


def set_default(args):
    """Set default profile."""
    manager = ProfileManager()
    
    if manager.set_default(args.name):
        print(json.dumps({
            "status": "success",
            "result": {
                "default": args.name,
                "message": f"Default profile set to '{args.name}'"
            }
        }))
    else:
        print(json.dumps({
            "error": f"Profile '{args.name}' not found"
        }))
        sys.exit(1)


def show_profile(args):
    """Show profile details."""
    manager = ProfileManager()
    profile = manager.get_profile(args.name)
    
    if not profile:
        print(json.dumps({
            "error": f"Profile '{args.name}' not found"
        }))
        sys.exit(1)
    
    # Mask password in output
    profile_dict = profile.to_dict()
    if profile_dict.get('password'):
        profile_dict['password'] = '***'
    
    print(json.dumps({
        "status": "success",
        "result": profile_dict
    }, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="Manage IMAP/SMTP account profiles",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # List profiles
    list_parser = subparsers.add_parser("list", help="List all profiles")
    list_parser.set_defaults(func=list_profiles)
    
    # Add profile
    add_parser = subparsers.add_parser("add", help="Add a new profile")
    add_parser.add_argument("--name", required=True, help="Profile name")
    add_parser.add_argument("--imap-server", help="IMAP server hostname")
    add_parser.add_argument("--smtp-server", help="SMTP server hostname")
    add_parser.add_argument("--username", help="Email username")
    add_parser.add_argument("--password", help="Email password")
    add_parser.add_argument("--imap-port", type=int, default=993, help="IMAP port (default: 993)")
    add_parser.add_argument("--smtp-port", type=int, default=587, help="SMTP port (default: 587)")
    add_parser.add_argument("--imap-ssl", action="store_true", default=True, help="Use SSL for IMAP (default: True)")
    add_parser.add_argument("--smtp-tls", action="store_true", default=True, help="Use TLS for SMTP (default: True)")
    add_parser.set_defaults(func=add_profile)
    
    # Remove profile
    remove_parser = subparsers.add_parser("remove", help="Remove a profile")
    remove_parser.add_argument("--name", required=True, help="Profile name")
    remove_parser.set_defaults(func=remove_profile)
    
    # Set default
    default_parser = subparsers.add_parser("set-default", help="Set default profile")
    default_parser.add_argument("--name", required=True, help="Profile name")
    default_parser.set_defaults(func=set_default)
    
    # Show profile
    show_parser = subparsers.add_parser("show", help="Show profile details")
    show_parser.add_argument("--name", required=True, help="Profile name")
    show_parser.set_defaults(func=show_profile)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == '__main__':
    main()

