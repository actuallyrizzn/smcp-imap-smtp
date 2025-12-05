#!/usr/bin/env python3
"""
IMAP CLI Tool

Provides command-line interface for IMAP email operations.
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

# Handle imports for both script execution and package import
try:
    from .imap_client import IMAPConnection, get_connection, set_connection, MAX_BODY_BYTES, MAX_ATTACHMENT_BYTES
except ImportError:
    # If running as script, add parent directory to path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    sys.path.insert(0, project_root)
    from tools.imap.imap_client import IMAPConnection, get_connection, set_connection, MAX_BODY_BYTES, MAX_ATTACHMENT_BYTES


def _auto_connect(args: Dict[str, Any]) -> tuple[Optional[IMAPConnection], bool]:
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
    if account_name:
        try:
            from tools.config import ProfileManager
            manager = ProfileManager()
            profile = manager.get_profile(account_name)
            if profile:
                server = profile.imap_server
                username = profile.username
                password = profile.password
                port = profile.imap_port
                use_ssl = profile.imap_ssl
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
        port = args.get("port", 993)
        use_ssl = args.get("use_ssl", True)
    
    import os
    if not username:
        username = os.getenv('IMAP_USERNAME')
    if not password:
        password = os.getenv('IMAP_PASSWORD')
    
    # Try default profile if no account specified and no direct args
    if not server and not username and not password:
        try:
            from tools.config import ProfileManager
            manager = ProfileManager()
            default_profile = manager.get_default()
            if default_profile:
                server = default_profile.imap_server
                username = default_profile.username
                password = default_profile.password
                port = default_profile.imap_port
                use_ssl = default_profile.imap_ssl
        except (ImportError, Exception):
            pass
    
    if server and username and password:
        try:
            conn = IMAPConnection()
            conn.connect(server, username, password, port, use_ssl)
            set_connection(conn)
            return conn, True
        except Exception as e:
            raise RuntimeError(f"Auto-connect failed: {str(e)}")
    
    return None, False


def connect(args: Dict[str, Any]) -> Dict[str, Any]:
    """Connect to an IMAP server."""
    server = args.get("server")
    username = args.get("username")
    password = args.get("password")
    port = args.get("port", 993)
    use_ssl = args.get("use_ssl", True)
    
    # Support environment variables for credentials
    import os
    if not username:
        username = os.getenv('IMAP_USERNAME')
    if not password:
        password = os.getenv('IMAP_PASSWORD')
    
    if not server or not username or not password:
        return {
            "error": "Missing required arguments: server, username, and password (or set IMAP_USERNAME/IMAP_PASSWORD env vars)"
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
        conn = IMAPConnection()
        conn.connect(server, username, password, port, use_ssl)
        set_connection(conn)
        
        return {
            "status": "success",
            "result": {
                "server": server,
                "username": username,
                "port": port,
                "ssl": use_ssl,
                "connected": True
            }
        }
    except Exception as e:
        return {
            "error": f"Connection failed: {str(e)}"
        }


def disconnect(args: Dict[str, Any]) -> Dict[str, Any]:
    """Disconnect from IMAP server."""
    conn = get_connection()
    if not conn:
        return {
            "error": "Not connected to IMAP server"
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


def list_mailboxes(args: Dict[str, Any]) -> Dict[str, Any]:
    """List all mailboxes on the server."""
    try:
        conn, auto_connected = _auto_connect(args)
        if not conn:
            return {
                "error": "Not connected to IMAP server. Provide --server, --username, --password to auto-connect, or call 'connect' first."
            }
        
        try:
            mailboxes = conn.list_mailboxes()
            result = {
                "status": "success",
                "result": {
                    "mailboxes": mailboxes
                }
            }
            # Auto-disconnect if we auto-connected
            if auto_connected:
                try:
                    conn.disconnect()
                    set_connection(None)
                except:
                    pass
            return result
        except Exception as e:
            # Clean up on error
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
            "error": f"Failed to list mailboxes: {str(e)}"
        }


def select_mailbox(args: Dict[str, Any]) -> Dict[str, Any]:
    """Select a mailbox."""
    mailbox = args.get("mailbox")
    
    if not mailbox:
        return {
            "error": "Missing required argument: mailbox"
        }
    
    try:
        conn, auto_connected = _auto_connect(args)
        if not conn:
            return {
                "error": "Not connected to IMAP server. Provide --server, --username, --password to auto-connect, or call 'connect' first."
            }
        
        try:
            folder_info = conn.select_mailbox(mailbox)
            result = {
                "status": "success",
                "result": folder_info
            }
            # Don't auto-disconnect for select (may want to use connection after)
            return result
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
            "error": f"Failed to select mailbox: {str(e)}"
        }


def search(args: Dict[str, Any]) -> Dict[str, Any]:
    """Search for emails."""
    criteria = args.get("criteria")
    
    if not criteria:
        return {
            "error": "Missing required argument: criteria"
        }
    
    try:
        conn, auto_connected = _auto_connect(args)
        if not conn:
            return {
                "error": "Not connected to IMAP server. Provide --server, --username, --password to auto-connect, or call 'connect' first."
            }
        
        try:
            # Auto-select INBOX if no mailbox is selected
            if not conn.current_mailbox:
                conn.select_mailbox('INBOX')
            
            uids = conn.search(criteria)
            result = {
                "status": "success",
                "result": {
                    "criteria": criteria,
                    "message_ids": uids,
                    "count": len(uids)
                }
            }
            if auto_connected:
                try:
                    conn.disconnect()
                    set_connection(None)
                except:
                    pass
            return result
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
            "error": f"Search failed: {str(e)}"
        }


def fetch(args: Dict[str, Any]) -> Dict[str, Any]:
    """Fetch email content."""
    message_id = args.get("message_id")
    max_body_bytes = args.get("max_body_bytes", MAX_BODY_BYTES)
    max_attachment_bytes = args.get("max_attachment_bytes", MAX_ATTACHMENT_BYTES)
    
    if not message_id:
        return {
            "error": "Missing required argument: message-id"
        }
    
    try:
        uid = int(message_id)
    except ValueError:
        return {
            "error": f"Invalid message ID: {message_id} (must be integer)"
        }
    
    try:
        conn, auto_connected = _auto_connect(args)
        if not conn:
            return {
                "error": "Not connected to IMAP server. Provide --server, --username, --password to auto-connect, or call 'connect' first."
            }
        
        try:
            # Auto-select INBOX if no mailbox is selected
            if not conn.current_mailbox:
                conn.select_mailbox('INBOX')
            
            email_data = conn.fetch_email(uid, max_body_bytes, max_attachment_bytes)
            # Set mailbox if known
            if conn.current_mailbox:
                email_data["mailbox"] = conn.current_mailbox
            
            result = {
                "status": "success",
                "result": email_data
            }
            if auto_connected:
                try:
                    conn.disconnect()
                    set_connection(None)
                except:
                    pass
            return result
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
            "error": f"Failed to fetch email: {str(e)}"
        }


def mark_read(args: Dict[str, Any]) -> Dict[str, Any]:
    """Mark email(s) as read."""
    message_ids = args.get("message_ids")
    sandbox = args.get("sandbox", False)
    
    if not message_ids:
        return {
            "error": "Missing required argument: message-ids"
        }
    
    if sandbox:
        return {
            "status": "sandbox",
            "result": {
                "message_ids": message_ids,
                "would_mark_read": True,
                "sandbox_mode": True
            }
        }
    
    try:
        conn, auto_connected = _auto_connect(args)
        if not conn:
            return {
                "error": "Not connected to IMAP server. Provide --server, --username, --password to auto-connect, or call 'connect' first."
            }
        
        try:
            # Auto-select INBOX if no mailbox is selected
            if not conn.current_mailbox:
                conn.select_mailbox('INBOX')
            
            uids = [int(uid) for uid in message_ids]
            conn.mark_read(uids)
            result = {
                "status": "success",
                "result": {
                    "message_ids": uids,
                    "marked_read": True
                }
            }
            if auto_connected:
                try:
                    conn.disconnect()
                    set_connection(None)
                except:
                    pass
            return result
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
    except ValueError as e:
        return {
            "error": f"Invalid message ID: {str(e)}"
        }
    except Exception as e:
        return {
            "error": f"Failed to mark as read: {str(e)}"
        }


def mark_unread(args: Dict[str, Any]) -> Dict[str, Any]:
    """Mark email(s) as unread."""
    message_ids = args.get("message_ids")
    sandbox = args.get("sandbox", False)
    
    if not message_ids:
        return {
            "error": "Missing required argument: message-ids"
        }
    
    if sandbox:
        return {
            "status": "sandbox",
            "result": {
                "message_ids": message_ids,
                "would_mark_unread": True,
                "sandbox_mode": True
            }
        }
    
    try:
        conn, auto_connected = _auto_connect(args)
        if not conn:
            return {
                "error": "Not connected to IMAP server. Provide --server, --username, --password to auto-connect, or call 'connect' first."
            }
        
        try:
            # Auto-select INBOX if no mailbox is selected
            if not conn.current_mailbox:
                conn.select_mailbox('INBOX')
            
            uids = [int(uid) for uid in message_ids]
            conn.mark_unread(uids)
            result = {
                "status": "success",
                "result": {
                    "message_ids": uids,
                    "marked_unread": True
                }
            }
            if auto_connected:
                try:
                    conn.disconnect()
                    set_connection(None)
                except:
                    pass
            return result
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
    except ValueError as e:
        return {
            "error": f"Invalid message ID: {str(e)}"
        }
    except Exception as e:
        return {
            "error": f"Failed to mark as unread: {str(e)}"
        }


def delete(args: Dict[str, Any]) -> Dict[str, Any]:
    """Delete email(s). Respects sandbox mode."""
    message_ids = args.get("message_ids")
    sandbox = args.get("sandbox", False)
    
    if not message_ids:
        return {
            "error": "Missing required argument: message-ids"
        }
    
    if sandbox:
        return {
            "status": "sandbox",
            "result": {
                "message_ids": message_ids,
                "would_delete": True,
                "sandbox_mode": True
            }
        }
    
    try:
        conn, auto_connected = _auto_connect(args)
        if not conn:
            return {
                "error": "Not connected to IMAP server. Provide --server, --username, --password to auto-connect, or call 'connect' first."
            }
        
        try:
            # Auto-select INBOX if no mailbox is selected
            if not conn.current_mailbox:
                conn.select_mailbox('INBOX')
            
            uids = [int(uid) for uid in message_ids]
            conn.delete(uids)
            result = {
                "status": "success",
                "result": {
                    "message_ids": uids,
                    "deleted": True
                }
            }
            if auto_connected:
                try:
                    conn.disconnect()
                    set_connection(None)
                except:
                    pass
            return result
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
    except ValueError as e:
        return {
            "error": f"Invalid message ID: {str(e)}"
        }
    except Exception as e:
        return {
            "error": f"Failed to delete: {str(e)}"
        }


def move(args: Dict[str, Any]) -> Dict[str, Any]:
    """Move email(s) to another mailbox. Respects sandbox mode."""
    message_ids = args.get("message_ids")
    target_mailbox = args.get("target_mailbox")
    sandbox = args.get("sandbox", False)
    
    if not message_ids or not target_mailbox:
        return {
            "error": "Missing required arguments: message-ids and target-mailbox"
        }
    
    if sandbox:
        return {
            "status": "sandbox",
            "result": {
                "message_ids": message_ids,
                "target_mailbox": target_mailbox,
                "would_move": True,
                "sandbox_mode": True
            }
        }
    
    try:
        conn, auto_connected = _auto_connect(args)
        if not conn:
            return {
                "error": "Not connected to IMAP server. Provide --server, --username, --password to auto-connect, or call 'connect' first."
            }
        
        try:
            # Auto-select INBOX if no mailbox is selected
            if not conn.current_mailbox:
                conn.select_mailbox('INBOX')
            
            uids = [int(uid) for uid in message_ids]
            conn.move(uids, target_mailbox)
            result = {
                "status": "success",
                "result": {
                    "message_ids": uids,
                    "target_mailbox": target_mailbox,
                    "moved": True
                }
            }
            if auto_connected:
                try:
                    conn.disconnect()
                    set_connection(None)
                except:
                    pass
            return result
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
    except ValueError as e:
        return {
            "error": f"Invalid message ID: {str(e)}"
        }
    except Exception as e:
        return {
            "error": f"Failed to move: {str(e)}"
        }


def get_plugin_description() -> Dict[str, Any]:
    """Return structured plugin description for --describe."""
    return {
        "plugin": {
            "name": "imap",
            "version": "0.1.0",
            "description": "IMAP email reading tool (UCW-compatible)"
        },
        "commands": [
            {
                "name": "connect",
                "description": "Connect to IMAP server",
                "parameters": [
                    {"name": "server", "type": "string", "description": "IMAP server hostname", "required": True, "default": None},
                    {"name": "username", "type": "string", "description": "IMAP username", "required": True, "default": None},
                    {"name": "password", "type": "string", "description": "IMAP password", "required": True, "default": None},
                    {"name": "port", "type": "integer", "description": "IMAP server port", "required": False, "default": 993},
                    {"name": "use_ssl", "type": "boolean", "description": "Use SSL/TLS", "required": False, "default": True},
                    {"name": "account", "type": "string", "description": "Account profile name", "required": False, "default": None}
                ]
            },
            {
                "name": "disconnect",
                "description": "Disconnect from IMAP server",
                "parameters": []
            },
            {
                "name": "list-mailboxes",
                "description": "List all mailboxes on the server",
                "parameters": [
                    {"name": "account", "type": "string", "description": "Account profile name", "required": False, "default": None},
                    {"name": "server", "type": "string", "description": "IMAP server hostname (for auto-connect)", "required": False, "default": None},
                    {"name": "username", "type": "string", "description": "IMAP username (for auto-connect)", "required": False, "default": None},
                    {"name": "password", "type": "string", "description": "IMAP password (for auto-connect)", "required": False, "default": None},
                    {"name": "port", "type": "integer", "description": "IMAP server port (default: 993, for auto-connect)", "required": False, "default": 993},
                    {"name": "use_ssl", "type": "boolean", "description": "Use SSL/TLS (default: True, for auto-connect)", "required": False, "default": True}
                ]
            },
            {
                "name": "select-mailbox",
                "description": "Select a mailbox",
                "parameters": [
                    {"name": "mailbox", "type": "string", "description": "Mailbox name (e.g., INBOX)", "required": True, "default": None},
                    {"name": "account", "type": "string", "description": "Account profile name", "required": False, "default": None},
                    {"name": "server", "type": "string", "description": "IMAP server hostname (for auto-connect)", "required": False, "default": None},
                    {"name": "username", "type": "string", "description": "IMAP username (for auto-connect)", "required": False, "default": None},
                    {"name": "password", "type": "string", "description": "IMAP password (for auto-connect)", "required": False, "default": None},
                    {"name": "port", "type": "integer", "description": "IMAP server port (default: 993, for auto-connect)", "required": False, "default": 993},
                    {"name": "use_ssl", "type": "boolean", "description": "Use SSL/TLS (default: True, for auto-connect)", "required": False, "default": True}
                ]
            },
            {
                "name": "search",
                "description": "Search for emails",
                "parameters": [
                    {"name": "criteria", "type": "string", "description": "Search criteria (e.g., 'ALL', 'UNSEEN', 'FROM sender@example.com')", "required": True, "default": None},
                    {"name": "account", "type": "string", "description": "Account profile name", "required": False, "default": None},
                    {"name": "server", "type": "string", "description": "IMAP server hostname (for auto-connect)", "required": False, "default": None},
                    {"name": "username", "type": "string", "description": "IMAP username (for auto-connect)", "required": False, "default": None},
                    {"name": "password", "type": "string", "description": "IMAP password (for auto-connect)", "required": False, "default": None},
                    {"name": "port", "type": "integer", "description": "IMAP server port (default: 993, for auto-connect)", "required": False, "default": 993},
                    {"name": "use_ssl", "type": "boolean", "description": "Use SSL/TLS (default: True, for auto-connect)", "required": False, "default": True}
                ]
            },
            {
                "name": "fetch",
                "description": "Fetch email content",
                "parameters": [
                    {"name": "message_id", "type": "string", "description": "Message ID or UID to fetch", "required": True, "default": None},
                    {"name": "max_body_bytes", "type": "integer", "description": f"Maximum body size in bytes (default: {MAX_BODY_BYTES})", "required": False, "default": MAX_BODY_BYTES},
                    {"name": "max_attachment_bytes", "type": "integer", "description": f"Maximum attachment size in bytes (default: {MAX_ATTACHMENT_BYTES})", "required": False, "default": MAX_ATTACHMENT_BYTES},
                    {"name": "account", "type": "string", "description": "Account profile name", "required": False, "default": None},
                    {"name": "server", "type": "string", "description": "IMAP server hostname (for auto-connect)", "required": False, "default": None},
                    {"name": "username", "type": "string", "description": "IMAP username (for auto-connect)", "required": False, "default": None},
                    {"name": "password", "type": "string", "description": "IMAP password (for auto-connect)", "required": False, "default": None},
                    {"name": "port", "type": "integer", "description": "IMAP server port (default: 993, for auto-connect)", "required": False, "default": 993},
                    {"name": "use_ssl", "type": "boolean", "description": "Use SSL/TLS (default: True, for auto-connect)", "required": False, "default": True}
                ]
            },
            {
                "name": "mark-read",
                "description": "Mark email(s) as read",
                "parameters": [
                    {"name": "message_ids", "type": "array", "description": "Message IDs or UIDs to mark as read", "required": True, "default": None},
                    {"name": "sandbox", "type": "boolean", "description": "Sandbox mode: simulate without actually marking", "required": False, "default": False},
                    {"name": "account", "type": "string", "description": "Account profile name", "required": False, "default": None},
                    {"name": "server", "type": "string", "description": "IMAP server hostname (for auto-connect)", "required": False, "default": None},
                    {"name": "username", "type": "string", "description": "IMAP username (for auto-connect)", "required": False, "default": None},
                    {"name": "password", "type": "string", "description": "IMAP password (for auto-connect)", "required": False, "default": None},
                    {"name": "port", "type": "integer", "description": "IMAP server port (default: 993, for auto-connect)", "required": False, "default": 993},
                    {"name": "use_ssl", "type": "boolean", "description": "Use SSL/TLS (default: True, for auto-connect)", "required": False, "default": True}
                ]
            },
            {
                "name": "mark-unread",
                "description": "Mark email(s) as unread",
                "parameters": [
                    {"name": "message_ids", "type": "array", "description": "Message IDs or UIDs to mark as unread", "required": True, "default": None},
                    {"name": "sandbox", "type": "boolean", "description": "Sandbox mode: simulate without actually marking", "required": False, "default": False},
                    {"name": "account", "type": "string", "description": "Account profile name", "required": False, "default": None},
                    {"name": "server", "type": "string", "description": "IMAP server hostname (for auto-connect)", "required": False, "default": None},
                    {"name": "username", "type": "string", "description": "IMAP username (for auto-connect)", "required": False, "default": None},
                    {"name": "password", "type": "string", "description": "IMAP password (for auto-connect)", "required": False, "default": None},
                    {"name": "port", "type": "integer", "description": "IMAP server port (default: 993, for auto-connect)", "required": False, "default": 993},
                    {"name": "use_ssl", "type": "boolean", "description": "Use SSL/TLS (default: True, for auto-connect)", "required": False, "default": True}
                ]
            },
            {
                "name": "delete",
                "description": "Delete email(s) (sandbox-aware)",
                "parameters": [
                    {"name": "message_ids", "type": "array", "description": "Message IDs or UIDs to delete", "required": True, "default": None},
                    {"name": "sandbox", "type": "boolean", "description": "Sandbox mode: simulate deletion without actually deleting", "required": False, "default": False},
                    {"name": "account", "type": "string", "description": "Account profile name", "required": False, "default": None},
                    {"name": "server", "type": "string", "description": "IMAP server hostname (for auto-connect)", "required": False, "default": None},
                    {"name": "username", "type": "string", "description": "IMAP username (for auto-connect)", "required": False, "default": None},
                    {"name": "password", "type": "string", "description": "IMAP password (for auto-connect)", "required": False, "default": None},
                    {"name": "port", "type": "integer", "description": "IMAP server port (default: 993, for auto-connect)", "required": False, "default": 993},
                    {"name": "use_ssl", "type": "boolean", "description": "Use SSL/TLS (default: True, for auto-connect)", "required": False, "default": True}
                ]
            },
            {
                "name": "move",
                "description": "Move email(s) to another mailbox (sandbox-aware)",
                "parameters": [
                    {"name": "message_ids", "type": "array", "description": "Message IDs or UIDs to move", "required": True, "default": None},
                    {"name": "target_mailbox", "type": "string", "description": "Target mailbox name", "required": True, "default": None},
                    {"name": "sandbox", "type": "boolean", "description": "Sandbox mode: simulate move without actually moving", "required": False, "default": False},
                    {"name": "account", "type": "string", "description": "Account profile name", "required": False, "default": None},
                    {"name": "server", "type": "string", "description": "IMAP server hostname (for auto-connect)", "required": False, "default": None},
                    {"name": "username", "type": "string", "description": "IMAP username (for auto-connect)", "required": False, "default": None},
                    {"name": "password", "type": "string", "description": "IMAP password (for auto-connect)", "required": False, "default": None},
                    {"name": "port", "type": "integer", "description": "IMAP server port (default: 993, for auto-connect)", "required": False, "default": 993},
                    {"name": "use_ssl", "type": "boolean", "description": "Use SSL/TLS (default: True, for auto-connect)", "required": False, "default": True}
                ]
            }
        ]
    }


def main():
    parser = argparse.ArgumentParser(
        description="IMAP email reading tool (UCW-compatible)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=""" 
Available commands:
  connect          Connect to IMAP server
  disconnect       Disconnect from IMAP server
  list-mailboxes   List all mailboxes
  select-mailbox   Select a mailbox
  search           Search for emails
  fetch            Fetch email content
  mark-read        Mark email(s) as read
  mark-unread      Mark email(s) as unread
  delete           Delete email(s) (sandbox-aware)
  move             Move email(s) to another mailbox (sandbox-aware)

Examples:
  python cli.py connect --server imap.aol.com --username test@aol.com --password pass
  python cli.py list-mailboxes
  python cli.py search --criteria "ALL"
  python cli.py fetch --message-id 12345
        """
    )
    
    # Add --describe flag before subparsers
    parser.add_argument("--describe", action="store_true",
                       help="Output plugin description in JSON format")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Connect command
    connect_parser = subparsers.add_parser("connect", help="Connect to IMAP server")
    connect_parser.add_argument("--account", help="Account profile name (from ~/.smcp-imap-smtp/accounts.json)")
    connect_parser.add_argument("--server", help="IMAP server hostname")
    connect_parser.add_argument("--username", help="IMAP username")
    connect_parser.add_argument("--password", help="IMAP password")
    connect_parser.add_argument("--port", type=int, default=993, help="IMAP server port (default: 993)")
    connect_parser.add_argument("--use-ssl", action="store_true", default=True, help="Use SSL/TLS (default: True)")
    
    # Disconnect command
    disconnect_parser = subparsers.add_parser("disconnect", help="Disconnect from IMAP server")
    
    # Helper function to add connection args to parsers
    def add_connection_args(parser):
        """Add optional connection arguments for auto-connect."""
        parser.add_argument("--account", help="Account profile name (from ~/.smcp-imap-smtp/accounts.json)")
        parser.add_argument("--server", help="IMAP server hostname (for auto-connect)")
        parser.add_argument("--username", help="IMAP username (for auto-connect)")
        parser.add_argument("--password", help="IMAP password (for auto-connect)")
        parser.add_argument("--port", type=int, default=993, help="IMAP server port (default: 993, for auto-connect)")
        parser.add_argument("--use-ssl", action="store_true", default=True, dest="use_ssl", help="Use SSL/TLS (default: True, for auto-connect)")
    
    # List mailboxes command
    list_parser = subparsers.add_parser("list-mailboxes", help="List all mailboxes")
    add_connection_args(list_parser)
    
    # Select mailbox command
    select_parser = subparsers.add_parser("select-mailbox", help="Select a mailbox")
    select_parser.add_argument("--mailbox", required=True, help="Mailbox name (e.g., INBOX)")
    add_connection_args(select_parser)
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search for emails")
    search_parser.add_argument("--criteria", required=True, help="Search criteria (e.g., 'ALL', 'UNSEEN', 'FROM sender@example.com')")
    add_connection_args(search_parser)
    
    # Fetch command
    fetch_parser = subparsers.add_parser("fetch", help="Fetch email content")
    fetch_parser.add_argument("--message-id", required=True, dest="message_id", help="Message ID or UID to fetch")
    fetch_parser.add_argument("--max-body-bytes", type=int, default=MAX_BODY_BYTES, dest="max_body_bytes", help=f"Maximum body size in bytes (default: {MAX_BODY_BYTES})")
    fetch_parser.add_argument("--max-attachment-bytes", type=int, default=MAX_ATTACHMENT_BYTES, dest="max_attachment_bytes", help=f"Maximum attachment size in bytes (default: {MAX_ATTACHMENT_BYTES})")
    add_connection_args(fetch_parser)
    
    # Mark read command
    mark_read_parser = subparsers.add_parser("mark-read", help="Mark email(s) as read")
    mark_read_parser.add_argument("--message-ids", required=True, nargs="+", dest="message_ids", help="Message IDs or UIDs to mark as read")
    mark_read_parser.add_argument("--sandbox", action="store_true", help="Sandbox mode: simulate without actually marking")
    add_connection_args(mark_read_parser)
    
    # Mark unread command
    mark_unread_parser = subparsers.add_parser("mark-unread", help="Mark email(s) as unread")
    mark_unread_parser.add_argument("--message-ids", required=True, nargs="+", dest="message_ids", help="Message IDs or UIDs to mark as unread")
    mark_unread_parser.add_argument("--sandbox", action="store_true", help="Sandbox mode: simulate without actually marking")
    add_connection_args(mark_unread_parser)
    
    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete email(s)")
    delete_parser.add_argument("--message-ids", required=True, nargs="+", dest="message_ids", help="Message IDs or UIDs to delete")
    delete_parser.add_argument("--sandbox", action="store_true", help="Sandbox mode: simulate deletion without actually deleting")
    add_connection_args(delete_parser)
    
    # Move command
    move_parser = subparsers.add_parser("move", help="Move email(s) to another mailbox")
    move_parser.add_argument("--message-ids", required=True, nargs="+", dest="message_ids", help="Message IDs or UIDs to move")
    move_parser.add_argument("--target-mailbox", required=True, dest="target_mailbox", help="Target mailbox name")
    move_parser.add_argument("--sandbox", action="store_true", help="Sandbox mode: simulate move without actually moving")
    add_connection_args(move_parser)
    
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
        if args.command == "connect":
            result = connect(args_dict)
        elif args.command == "disconnect":
            result = disconnect(args_dict)
        elif args.command == "list-mailboxes":
            result = list_mailboxes(args_dict)
        elif args.command == "select-mailbox":
            result = select_mailbox(args_dict)
        elif args.command == "search":
            result = search(args_dict)
        elif args.command == "fetch":
            result = fetch(args_dict)
        elif args.command == "mark-read":
            result = mark_read(args_dict)
        elif args.command == "mark-unread":
            result = mark_unread(args_dict)
        elif args.command == "delete":
            result = delete(args_dict)
        elif args.command == "move":
            result = move(args_dict)
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

