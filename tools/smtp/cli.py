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
    
    server = args.get("server")
    username = args.get("username")
    password = args.get("password")
    port = args.get("port", 587)
    use_tls = args.get("use_tls", True)
    
    import os
    if not username:
        username = os.getenv('SMTP_USERNAME') or os.getenv('IMAP_USERNAME')
    if not password:
        password = os.getenv('SMTP_PASSWORD') or os.getenv('IMAP_PASSWORD')
    
    if server and username and password:
        try:
            conn = SMTPConnection()
            conn.connect(server, username, password, port, use_tls)
            set_connection(conn)
            return conn, True
        except Exception as e:
            raise RuntimeError(f"Auto-connect failed: {str(e)}")
    
    return None, False


def connect(args: Dict[str, Any]) -> Dict[str, Any]:
    """Connect to an SMTP server."""
    server = args.get("server")
    username = args.get("username")
    password = args.get("password")
    port = args.get("port", 587)
    use_tls = args.get("use_tls", True)
    
    # Support environment variables for credentials
    import os
    if not username:
        username = os.getenv('SMTP_USERNAME') or os.getenv('IMAP_USERNAME')
    if not password:
        password = os.getenv('SMTP_PASSWORD') or os.getenv('IMAP_PASSWORD')
    
    if not server or not username or not password:
        return {
            "error": "Missing required arguments: server, username, and password (or set SMTP_USERNAME/SMTP_PASSWORD env vars)"
        }
    
    # Input validation
    if not isinstance(port, int) or port < 1 or port > 65535:
        return {
            "error": f"Invalid port: {port} (must be 1-65535)"
        }
    
    try:
        # Disconnect existing connection if any
        existing_conn = get_connection()
        if existing_conn:
            try:
                existing_conn.disconnect()
            except:
                pass
        
        # Create new connection
        conn = SMTPConnection()
        conn.connect(server, username, password, port, use_tls)
        set_connection(conn)
        
        return {
            "status": "success",
            "result": {
                "server": server,
                "username": username,
                "port": port,
                "tls": use_tls,
                "connected": True
            }
        }
    except Exception as e:
        return {
            "error": f"Connection failed: {str(e)}"
        }


def disconnect(args: Dict[str, Any]) -> Dict[str, Any]:
    """Disconnect from SMTP server."""
    conn = get_connection()
    if not conn:
        return {
            "error": "Not connected to SMTP server"
        }
    
    try:
        conn.disconnect()
        set_connection(None)
        return {
            "status": "success",
            "result": {"disconnected": True}
        }
    except Exception as e:
        return {
            "error": f"Disconnect failed: {str(e)}"
        }


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
                "error": "Not connected to SMTP server. Provide --server, --username, --password to auto-connect, or call 'connect' first."
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
                "error": "Not connected to SMTP server. Provide --server, --username, --password to auto-connect, or call 'connect' first."
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
                "error": "Not connected to SMTP server. Provide --server, --username, --password to auto-connect, or call 'connect' first."
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


def main():
    parser = argparse.ArgumentParser(
        description="SMTP email sending tool (UCW-compatible)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Available commands:
  connect              Connect to SMTP server
  disconnect           Disconnect from SMTP server
  send                 Send plain text email
  send-html            Send HTML email
  send-with-attachment Send email with attachments

Examples:
  python cli.py connect --server smtp.aol.com --username test@aol.com --password pass
  python cli.py send --to recipient@example.com --subject "Test" --body "Hello"
  python cli.py send-html --to recipient@example.com --subject "Test" --html-body "<html>Hello</html>"
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Helper function to add connection args to parsers
    def add_connection_args(parser):
        """Add optional connection arguments for auto-connect."""
        parser.add_argument("--server", help="SMTP server hostname (for auto-connect)")
        parser.add_argument("--username", help="SMTP username (for auto-connect)")
        parser.add_argument("--password", help="SMTP password (for auto-connect)")
        parser.add_argument("--port", type=int, default=587, help="SMTP server port (default: 587, for auto-connect)")
        parser.add_argument("--use-tls", action="store_true", default=True, dest="use_tls", help="Use TLS/SSL (default: True, for auto-connect)")
    
    # Connect command
    connect_parser = subparsers.add_parser("connect", help="Connect to SMTP server")
    connect_parser.add_argument("--server", required=True, help="SMTP server hostname")
    connect_parser.add_argument("--username", required=True, help="SMTP username")
    connect_parser.add_argument("--password", required=True, help="SMTP password")
    connect_parser.add_argument("--port", type=int, default=587, help="SMTP server port (default: 587)")
    connect_parser.add_argument("--use-tls", action="store_true", default=True, dest="use_tls", help="Use TLS/SSL (default: True)")
    
    # Disconnect command
    disconnect_parser = subparsers.add_parser("disconnect", help="Disconnect from SMTP server")
    
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
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        # Convert argparse Namespace to dict
        args_dict = vars(args)
        
        # Execute command
        if args.command == "connect":
            result = connect(args_dict)
        elif args.command == "disconnect":
            result = disconnect(args_dict)
        elif args.command == "send":
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

