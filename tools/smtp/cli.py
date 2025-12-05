#!/usr/bin/env python3
"""
SMTP CLI Tool

Provides command-line interface for SMTP email operations.
Can be wrapped by UCW to become an SMCP plugin.

Copyright (c) 2025 Mark Rizzn Hopkins

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import argparse
import json
import sys
import os
from typing import Dict, Any, Optional, List
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# Handle imports for both script execution and package import
try:
    from .smtp_client import SMTPConnection, get_connection, set_connection, MAX_ATTACHMENT_BYTES
except ImportError:
    # If running as script, add parent directory to path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    sys.path.insert(0, project_root)
    from tools.smtp.smtp_client import SMTPConnection, get_connection, set_connection, MAX_ATTACHMENT_BYTES


def _auto_connect(args: Dict[str, Any]) -> tuple[Optional[SMTPConnection], bool]:
    """
    Helper function to auto-connect if credentials are provided.
    Returns (connection, auto_connected_flag)
    """
    conn = get_connection()
    if conn:
        return conn, False
    
    # Check for account profile first
    account_name = args.get("account")
    profile_loaded = False
    imap_server = None
    imap_port = None
    imap_ssl = None
    
    if account_name:
        try:
            from tools.config import ProfileManager
            manager = ProfileManager()
            profile = manager.get_profile(account_name)
            if profile:
                server = profile.smtp_server
                username = profile.username
                password = profile.password
                port = profile.smtp_port
                use_tls = profile.smtp_tls
                # Also get IMAP settings from profile for Sent folder save
                imap_server = profile.imap_server
                imap_port = profile.imap_port
                imap_ssl = profile.imap_ssl
                profile_loaded = True
            else:
                return None, False
        except ImportError:
            # Config module not available, fall through to direct args
            pass
        except Exception as e:
            # Fall through to direct args on error
            pass
    
    # Use direct arguments or environment variables (only if profile wasn't loaded)
    if not profile_loaded:
        server = args.get("server")
        username = args.get("username")
        password = args.get("password")
        port = args.get("port", 587)
        use_tls = args.get("use_tls", True)
        # Get IMAP settings from args if provided
        imap_server = args.get("imap_server")
        imap_port = args.get("imap_port")
        imap_ssl = args.get("imap_ssl")
    
    import os
    if not username:
        username = os.getenv('SMTP_USERNAME') or os.getenv('IMAP_USERNAME')
    if not password:
        password = os.getenv('SMTP_PASSWORD') or os.getenv('IMAP_PASSWORD')
    
    # Try default profile if no account specified and no direct args
    if not server and not username and not password:
        try:
            from tools.config import ProfileManager
            manager = ProfileManager()
            default_profile = manager.get_default()
            if default_profile:
                server = default_profile.smtp_server
                username = default_profile.username
                password = default_profile.password
                port = default_profile.smtp_port
                use_tls = default_profile.smtp_tls
                # Also get IMAP settings from default profile
                imap_server = default_profile.imap_server
                imap_port = default_profile.imap_port
                imap_ssl = default_profile.imap_ssl
        except (ImportError, Exception):
            pass
    
    if server and username and password:
        try:
            conn = SMTPConnection()
            conn.connect(server, username, password, port, use_tls)
            
            # Set IMAP server settings if available (for Sent folder save)
            # These may come from profile or from args
            if imap_server:
                conn.imap_server = imap_server
            if imap_port is not None:
                conn.imap_port = imap_port
            if imap_ssl is not None:
                conn.imap_ssl = imap_ssl
            
            set_connection(conn)
            return conn, True
        except Exception as e:
            raise RuntimeError(f"Auto-connect failed: {str(e)}")
    
    return None, False


def send(args: Dict[str, Any]) -> Dict[str, Any]:
    """Send a plain text email."""
    to_addrs = args.get("to")
    subject = args.get("subject")
    body = args.get("body")
    from_addr = args.get("from")
    cc = args.get("cc", [])
    bcc = args.get("bcc", [])
    reply_to = args.get("reply_to")
    
    if not to_addrs or not subject or not body:
        return {
            "error": "Missing required arguments: to, subject, and body"
        }
    
    try:
        conn, auto_connected = _auto_connect(args)
        if not conn:
            return {
                "error": "Not connected to SMTP server. Provide --server, --username, --password (or --account) to auto-connect."
            }
        
        try:
            result = conn.send_email(
                to_addrs=to_addrs if isinstance(to_addrs, list) else [to_addrs],
                subject=subject,
                body=body,
                from_addr=from_addr,
                cc=cc if isinstance(cc, list) else [cc] if cc else [],
                bcc=bcc if isinstance(bcc, list) else [bcc] if bcc else [],
                reply_to=reply_to,
                html=False
            )
            response = {
                "status": "success",
                "result": result
            }
            if auto_connected:
                try:
                    conn.disconnect()
                    set_connection(None)
                except:
                    pass
            return response
        except Exception as e:
            if auto_connected:
                try:
                    conn.disconnect()
                    set_connection(None)
                except:
                    pass
            raise
    except RuntimeError as e:
        return {"error": str(e)}
    except Exception as e:
        return {
            "error": f"Failed to send email: {str(e)}"
        }


def send_html(args: Dict[str, Any]) -> Dict[str, Any]:
    """Send an HTML email."""
    to_addrs = args.get("to")
    subject = args.get("subject")
    html_body = args.get("html_body")
    text_body = args.get("text_body")
    from_addr = args.get("from")
    cc = args.get("cc", [])
    bcc = args.get("bcc", [])
    reply_to = args.get("reply_to")
    
    if not to_addrs or not subject or not html_body:
        return {
            "error": "Missing required arguments: to, subject, and html-body"
        }
    
    try:
        conn, auto_connected = _auto_connect(args)
        if not conn:
            return {
                "error": "Not connected to SMTP server. Provide --server, --username, --password (or --account) to auto-connect."
            }
        
        try:
            result = conn.send_email(
                to_addrs=to_addrs if isinstance(to_addrs, list) else [to_addrs],
                subject=subject,
                body=html_body,
                text_body=text_body,
                from_addr=from_addr,
                cc=cc if isinstance(cc, list) else [cc] if cc else [],
                bcc=bcc if isinstance(bcc, list) else [bcc] if bcc else [],
                reply_to=reply_to,
                html=True
            )
            response = {
                "status": "success",
                "result": result
            }
            if auto_connected:
                try:
                    conn.disconnect()
                    set_connection(None)
                except:
                    pass
            return response
        except Exception as e:
            if auto_connected:
                try:
                    conn.disconnect()
                    set_connection(None)
                except:
                    pass
            raise
    except RuntimeError as e:
        return {"error": str(e)}
    except Exception as e:
        return {
            "error": f"Failed to send email: {str(e)}"
        }


def send_with_attachment(args: Dict[str, Any]) -> Dict[str, Any]:
    """Send an email with attachments."""
    to_addrs = args.get("to")
    subject = args.get("subject")
    body = args.get("body")
    attachments = args.get("attachments", [])
    from_addr = args.get("from")
    cc = args.get("cc", [])
    bcc = args.get("bcc", [])
    reply_to = args.get("reply_to")
    html = args.get("html", False)
    
    if not to_addrs or not subject or not body:
        return {
            "error": "Missing required arguments: to, subject, and body"
        }
    
    if not attachments:
        return {
            "error": "Missing required argument: attachments"
        }
    
    try:
        conn, auto_connected = _auto_connect(args)
        if not conn:
            return {
                "error": "Not connected to SMTP server. Provide --server, --username, --password (or --account) to auto-connect."
            }
        
        try:
            result = conn.send_email_with_attachments(
                to_addrs=to_addrs if isinstance(to_addrs, list) else [to_addrs],
                subject=subject,
                body=body,
                attachments=attachments if isinstance(attachments, list) else [attachments],
                from_addr=from_addr,
                cc=cc if isinstance(cc, list) else [cc] if cc else [],
                bcc=bcc if isinstance(bcc, list) else [bcc] if bcc else [],
                reply_to=reply_to,
                html=html
            )
            response = {
                "status": "success",
                "result": result
            }
            if auto_connected:
                try:
                    conn.disconnect()
                    set_connection(None)
                except:
                    pass
            return response
        except Exception as e:
            if auto_connected:
                try:
                    conn.disconnect()
                    set_connection(None)
                except:
                    pass
            raise
    except RuntimeError as e:
        return {"error": str(e)}
    except Exception as e:
        return {
            "error": f"Failed to send email: {str(e)}"
        }


def get_plugin_description() -> Dict[str, Any]:
    """Return structured plugin description for --describe."""
    return {
        "plugin": {
            "name": "smtp",
            "version": "0.1.0",
            "description": "SMTP email sending tool (UCW-compatible)"
        },
        "commands": [
            {
                "name": "send",
                "description": "Send plain text email",
                "parameters": [
                    {"name": "to", "type": "array", "description": "Recipient email address(es)", "required": True, "default": None},
                    {"name": "subject", "type": "string", "description": "Email subject", "required": True, "default": None},
                    {"name": "body", "type": "string", "description": "Email body (plain text)", "required": True, "default": None},
                    {"name": "from", "type": "string", "description": "From email address (default: username)", "required": False, "default": None},
                    {"name": "cc", "type": "array", "description": "CC recipient(s)", "required": False, "default": []},
                    {"name": "bcc", "type": "array", "description": "BCC recipient(s)", "required": False, "default": []},
                    {"name": "reply_to", "type": "string", "description": "Reply-To email address", "required": False, "default": None},
                    {"name": "account", "type": "string", "description": "Account profile name", "required": False, "default": None},
                    {"name": "server", "type": "string", "description": "SMTP server hostname (for auto-connect)", "required": False, "default": None},
                    {"name": "username", "type": "string", "description": "SMTP username (for auto-connect)", "required": False, "default": None},
                    {"name": "password", "type": "string", "description": "SMTP password (for auto-connect)", "required": False, "default": None},
                    {"name": "port", "type": "integer", "description": "SMTP server port (default: 587, for auto-connect)", "required": False, "default": 587},
                    {"name": "use_tls", "type": "boolean", "description": "Use TLS/SSL (default: True, for auto-connect)", "required": False, "default": True}
                ]
            },
            {
                "name": "send-html",
                "description": "Send HTML email",
                "parameters": [
                    {"name": "to", "type": "array", "description": "Recipient email address(es)", "required": True, "default": None},
                    {"name": "subject", "type": "string", "description": "Email subject", "required": True, "default": None},
                    {"name": "html_body", "type": "string", "description": "Email body (HTML)", "required": True, "default": None},
                    {"name": "text_body", "type": "string", "description": "Plain text alternative body", "required": False, "default": None},
                    {"name": "from", "type": "string", "description": "From email address (default: username)", "required": False, "default": None},
                    {"name": "cc", "type": "array", "description": "CC recipient(s)", "required": False, "default": []},
                    {"name": "bcc", "type": "array", "description": "BCC recipient(s)", "required": False, "default": []},
                    {"name": "reply_to", "type": "string", "description": "Reply-To email address", "required": False, "default": None},
                    {"name": "account", "type": "string", "description": "Account profile name", "required": False, "default": None},
                    {"name": "server", "type": "string", "description": "SMTP server hostname (for auto-connect)", "required": False, "default": None},
                    {"name": "username", "type": "string", "description": "SMTP username (for auto-connect)", "required": False, "default": None},
                    {"name": "password", "type": "string", "description": "SMTP password (for auto-connect)", "required": False, "default": None},
                    {"name": "port", "type": "integer", "description": "SMTP server port (default: 587, for auto-connect)", "required": False, "default": 587},
                    {"name": "use_tls", "type": "boolean", "description": "Use TLS/SSL (default: True, for auto-connect)", "required": False, "default": True}
                ]
            },
            {
                "name": "send-with-attachment",
                "description": "Send email with attachments",
                "parameters": [
                    {"name": "to", "type": "array", "description": "Recipient email address(es)", "required": True, "default": None},
                    {"name": "subject", "type": "string", "description": "Email subject", "required": True, "default": None},
                    {"name": "body", "type": "string", "description": "Email body", "required": True, "default": None},
                    {"name": "attachments", "type": "array", "description": "Attachment file path(s)", "required": True, "default": None},
                    {"name": "from", "type": "string", "description": "From email address (default: username)", "required": False, "default": None},
                    {"name": "cc", "type": "array", "description": "CC recipient(s)", "required": False, "default": []},
                    {"name": "bcc", "type": "array", "description": "BCC recipient(s)", "required": False, "default": []},
                    {"name": "reply_to", "type": "string", "description": "Reply-To email address", "required": False, "default": None},
                    {"name": "html", "type": "boolean", "description": "Body is HTML (default: plain text)", "required": False, "default": False},
                    {"name": "account", "type": "string", "description": "Account profile name", "required": False, "default": None},
                    {"name": "server", "type": "string", "description": "SMTP server hostname (for auto-connect)", "required": False, "default": None},
                    {"name": "username", "type": "string", "description": "SMTP username (for auto-connect)", "required": False, "default": None},
                    {"name": "password", "type": "string", "description": "SMTP password (for auto-connect)", "required": False, "default": None},
                    {"name": "port", "type": "integer", "description": "SMTP server port (default: 587, for auto-connect)", "required": False, "default": 587},
                    {"name": "use_tls", "type": "boolean", "description": "Use TLS/SSL (default: True, for auto-connect)", "required": False, "default": True}
                ]
            }
        ]
    }


def main():
    parser = argparse.ArgumentParser(
        description="SMTP email sending tool (UCW-compatible)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=""" 
Available commands:
  send                 Send plain text email
  send-html            Send HTML email
  send-with-attachment Send email with attachments

All commands support auto-connect via --account, --server/--username/--password, or environment variables.

Examples:
  python cli.py send --to recipient@example.com --subject "Test" --body "Hello" --account gmx
  python cli.py send-html --to recipient@example.com --subject "Test" --html-body "<html>Hello</html>" --account gmx
        """
    )
    
    # Add --describe flag before subparsers
    parser.add_argument("--describe", action="store_true",
                       help="Output plugin description in JSON format")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Helper function to add connection args to parsers
    def add_connection_args(parser):
        """Add optional connection arguments for auto-connect."""
        parser.add_argument("--account", help="Account profile name (from ~/.smcp-imap-smtp/accounts.json)")
        parser.add_argument("--server", help="SMTP server hostname (for auto-connect)")
        parser.add_argument("--username", help="SMTP username (for auto-connect)")
        parser.add_argument("--password", help="SMTP password (for auto-connect)")
        parser.add_argument("--port", type=int, default=587, help="SMTP server port (default: 587, for auto-connect)")
        parser.add_argument("--use-tls", action="store_true", default=True, dest="use_tls", help="Use TLS/SSL (default: True, for auto-connect)")
        # Optional IMAP server settings for Sent folder save
        parser.add_argument("--imap-server", dest="imap_server", help="IMAP server hostname (for saving to Sent folder, defaults to derived from SMTP server)")
        parser.add_argument("--imap-port", type=int, dest="imap_port", help="IMAP server port (default: 993, for Sent folder save)")
        parser.add_argument("--imap-ssl", action="store_true", dest="imap_ssl", help="Use SSL for IMAP (default: True, for Sent folder save)")
    
    # Send command
    send_parser = subparsers.add_parser("send", help="Send plain text email")
    send_parser.add_argument("--to", required=True, nargs="+", help="Recipient email address(es)")
    send_parser.add_argument("--subject", required=True, help="Email subject")
    send_parser.add_argument("--body", required=True, help="Email body (plain text)")
    send_parser.add_argument("--from", dest="from", help="From email address (default: username)")
    send_parser.add_argument("--cc", nargs="+", default=[], help="CC recipient(s)")
    send_parser.add_argument("--bcc", nargs="+", default=[], help="BCC recipient(s)")
    send_parser.add_argument("--reply-to", dest="reply_to", help="Reply-To email address")
    add_connection_args(send_parser)
    
    # Send HTML command
    send_html_parser = subparsers.add_parser("send-html", help="Send HTML email")
    send_html_parser.add_argument("--to", required=True, nargs="+", help="Recipient email address(es)")
    send_html_parser.add_argument("--subject", required=True, help="Email subject")
    send_html_parser.add_argument("--html-body", required=True, dest="html_body", help="Email body (HTML)")
    send_html_parser.add_argument("--text-body", dest="text_body", help="Plain text alternative body")
    send_html_parser.add_argument("--from", dest="from", help="From email address (default: username)")
    send_html_parser.add_argument("--cc", nargs="+", default=[], help="CC recipient(s)")
    send_html_parser.add_argument("--bcc", nargs="+", default=[], help="BCC recipient(s)")
    send_html_parser.add_argument("--reply-to", dest="reply_to", help="Reply-To email address")
    add_connection_args(send_html_parser)
    
    # Send with attachment command
    send_attach_parser = subparsers.add_parser("send-with-attachment", help="Send email with attachments")
    send_attach_parser.add_argument("--to", required=True, nargs="+", help="Recipient email address(es)")
    send_attach_parser.add_argument("--subject", required=True, help="Email subject")
    send_attach_parser.add_argument("--body", required=True, help="Email body")
    send_attach_parser.add_argument("--attachments", required=True, nargs="+", help="Attachment file path(s)")
    send_attach_parser.add_argument("--from", dest="from", help="From email address (default: username)")
    send_attach_parser.add_argument("--cc", nargs="+", default=[], help="CC recipient(s)")
    send_attach_parser.add_argument("--bcc", nargs="+", default=[], help="BCC recipient(s)")
    send_attach_parser.add_argument("--reply-to", dest="reply_to", help="Reply-To email address")
    send_attach_parser.add_argument("--html", action="store_true", help="Body is HTML (default: plain text)")
    add_connection_args(send_attach_parser)
    
    args = parser.parse_args()
    
    # Handle --describe before checking for command
    if args.describe:
        description = get_plugin_description()
        print(json.dumps(description, indent=2))
        sys.exit(0)
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        # Convert argparse Namespace to dict
        args_dict = vars(args)
        
        # Execute command
        if args.command == "send":
            result = send(args_dict)
        elif args.command == "send-html":
            result = send_html(args_dict)
        elif args.command == "send-with-attachment":
            result = send_with_attachment(args_dict)
        else:
            result = {"error": f"Unknown command: {args.command}"}
        
        # Output JSON
        print(json.dumps(result, indent=2))
        sys.exit(0 if "error" not in result else 1)
        
    except Exception as e:
        error_result = {"error": str(e)}
        print(json.dumps(error_result, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()

