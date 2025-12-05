"""
IMAP Client Module

Handles IMAP connection management, email fetching, and normalization.
"""

import email.message
import email.utils
from email.header import decode_header
from email import message_from_bytes
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import imapclient
from imapclient import IMAPClient
import logging

# Configure logging to stderr (stdout is for JSON)
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=__import__('sys').stderr
)
logger = logging.getLogger(__name__)

# Guardrails (configurable via environment variables)
import os
MAX_BODY_BYTES = int(os.getenv('MAX_BODY_BYTES', 10 * 1024 * 1024))  # 10MB default
MAX_ATTACHMENT_BYTES = int(os.getenv('MAX_ATTACHMENT_BYTES', 25 * 1024 * 1024))  # 25MB default


class IMAPConnection:
    """Manages IMAP connection and operations."""
    
    def __init__(self):
        self.client: Optional[IMAPClient] = None
        self.server: Optional[str] = None
        self.username: Optional[str] = None
        self.current_mailbox: Optional[str] = None
    
    def connect(self, server: str, username: str, password: str, port: int = 993, use_ssl: bool = True) -> None:
        """Connect to IMAP server."""
        try:
            # Add timeout to prevent hanging connections (30 seconds)
            self.client = IMAPClient(server, port=port, ssl=use_ssl, timeout=30)
            # Try login with proper error handling
            try:
                # Try standard login first
                self.client.login(username, password)
            except Exception as login_error:
                error_msg = str(login_error)
                # If login fails, try PLAIN authentication (some servers prefer this)
                if 'authentication failed' in error_msg.lower() or 'AUTHENTICATIONFAILED' in error_msg:
                    try:
                        # Try PLAIN authentication
                        import base64
                        auth_string = base64.b64encode(f'\0{username}\0{password}'.encode()).decode()
                        self.client._imap.authenticate('PLAIN', lambda: auth_string)
                    except Exception as plain_error:
                        # If PLAIN also fails, raise original error with helpful message
                        raise RuntimeError(
                            f"Authentication failed. This may be due to:\n"
                            f"1. Incorrect username or password\n"
                            f"2. IMAP access may not be enabled in account settings\n"
                            f"3. App password may be incorrect or expired\n"
                            f"4. Account may need additional security setup\n"
                            f"Original error: {error_msg}"
                        )
                else:
                    raise
            self.server = server
            self.username = username
            # Mask password in logs
            masked_username = username.split('@')[0] + '@***' if '@' in username else '***'
            logger.info(f"Connected to {server} as {masked_username}")
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            raise
    
    def disconnect(self) -> None:
        """Disconnect from IMAP server."""
        if self.client:
            try:
                self.client.logout()
            except:
                pass
            self.client = None
            self.server = None
            self.username = None
            self.current_mailbox = None
            logger.info("Disconnected from IMAP server")
    
    def list_mailboxes(self) -> List[Dict[str, Any]]:
        """List all mailboxes."""
        if not self.client:
            raise RuntimeError("Not connected to IMAP server")
        
        folders = self.client.list_folders()
        result = []
        for folder in folders:
            name = folder[2]
            if isinstance(name, bytes):
                name = name.decode('utf-8', errors='replace')
            delimiter = folder[1]
            if isinstance(delimiter, bytes):
                delimiter = delimiter.decode('utf-8', errors='replace')
            flags = [f.decode('utf-8', errors='replace') if isinstance(f, bytes) else str(f) for f in folder[0]]
            result.append({
                "name": name,
                "delimiter": delimiter,
                "flags": flags
            })
        return result
    
    def select_mailbox(self, mailbox: str) -> Dict[str, Any]:
        """Select a mailbox."""
        if not self.client:
            raise RuntimeError("Not connected to IMAP server")
        
        folder_info = self.client.select_folder(mailbox)
        self.current_mailbox = mailbox
        
        return {
            "mailbox": mailbox,
            "exists": folder_info[b'EXISTS'],
            "recent": folder_info.get(b'RECENT', 0),
            "unseen": folder_info.get(b'UNSEEN', 0),
            "uidvalidity": folder_info.get(b'UIDVALIDITY', 0)
        }
    
    def search(self, criteria: str) -> List[int]:
        """Search for emails using criteria."""
        if not self.client:
            raise RuntimeError("Not connected to IMAP server")
        
        # Parse common criteria
        if criteria.upper() == "ALL":
            uids = self.client.search(['ALL'])
        elif criteria.upper() == "UNSEEN":
            uids = self.client.search(['UNSEEN'])
        elif criteria.upper().startswith("FROM "):
            sender = criteria[5:].strip().strip('"\'')
            uids = self.client.search(['FROM', sender])
        elif criteria.upper().startswith("SUBJECT "):
            subject = criteria[8:].strip().strip('"\'')
            uids = self.client.search(['SUBJECT', subject])
        else:
            # Try to parse as raw IMAP search criteria
            # For now, default to ALL if we can't parse
            logger.warning(f"Unknown search criteria: {criteria}, using ALL")
            uids = self.client.search(['ALL'])
        
        return uids
    
    def fetch_email(self, uid: int, max_body_bytes: int = MAX_BODY_BYTES, max_attachment_bytes: int = MAX_ATTACHMENT_BYTES) -> Dict[str, Any]:
        """Fetch email by UID and normalize it."""
        if not self.client:
            raise RuntimeError("Not connected to IMAP server")
        
        # Fetch message
        messages = self.client.fetch([uid], ['RFC822', 'FLAGS', 'ENVELOPE'])
        
        if uid not in messages:
            raise ValueError(f"Message {uid} not found")
        
        msg_data = messages[uid]
        raw_email = msg_data[b'RFC822']
        
        # Parse email
        msg = message_from_bytes(raw_email)
        
        # Normalize email
        normalized = normalize_email(msg, uid, max_body_bytes, max_attachment_bytes)
        
        return normalized
    
    def mark_read(self, uids: List[int]) -> None:
        """Mark emails as read."""
        if not self.client:
            raise RuntimeError("Not connected to IMAP server")
        
        self.client.set_flags(uids, [imapclient.SEEN])
    
    def mark_unread(self, uids: List[int]) -> None:
        """Mark emails as unread."""
        if not self.client:
            raise RuntimeError("Not connected to IMAP server")
        
        self.client.remove_flags(uids, [imapclient.SEEN])
    
    def delete(self, uids: List[int]) -> None:
        """Delete emails."""
        if not self.client:
            raise RuntimeError("Not connected to IMAP server")
        
        self.client.set_flags(uids, [imapclient.DELETED])
        self.client.expunge()
    
    def move(self, uids: List[int], target_mailbox: str) -> None:
        """Move emails to another mailbox."""
        if not self.client:
            raise RuntimeError("Not connected to IMAP server")
        
        self.client.copy(uids, target_mailbox)
        self.client.set_flags(uids, [imapclient.DELETED])
        self.client.expunge()
    
    def append_to_mailbox(self, mailbox: str, message_bytes: bytes, flags: Optional[List[str]] = None) -> Optional[int]:
        """
        Append a message to a mailbox using IMAP APPEND.
        
        Args:
            mailbox: Mailbox name (e.g., 'Sent', 'Sent Items')
            message_bytes: Message in RFC822 format (bytes)
            flags: Optional list of flags (e.g., ['\\Seen'])
        
        Returns:
            UID of appended message if successful, None otherwise
        """
        if not self.client:
            raise RuntimeError("Not connected to IMAP server")
        
        try:
            if flags is None:
                flags = ['\\Seen']  # Mark as read by default
            
            uid = self.client.append(mailbox, message_bytes, flags=flags)
            return uid
        except Exception as e:
            logger.warning(f"Failed to append message to {mailbox}: {e}")
            raise
    
    def find_sent_folder(self) -> Optional[str]:
        """
        Find the Sent folder by checking common names.
        Returns the first matching folder name, or None if not found.
        """
        if not self.client:
            raise RuntimeError("Not connected to IMAP server")
        
        # Common Sent folder names across providers
        sent_folder_names = [
            'Sent',
            'Sent Items',
            'Gesendet',  # German (GMX)
            '[Gmail]/Sent Mail',
            'Sent Messages',
            'OUTBOX',  # Some providers
        ]
        
        try:
            folders = self.client.list_folders()
            folder_names = []
            for folder in folders:
                name = folder[2]
                if isinstance(name, bytes):
                    name = name.decode('utf-8', errors='replace')
                folder_names.append(name)
            
            # Check for exact matches first
            for sent_name in sent_folder_names:
                if sent_name in folder_names:
                    return sent_name
            
            # Check for case-insensitive matches
            folder_names_lower = [f.lower() for f in folder_names]
            for sent_name in sent_folder_names:
                if sent_name.lower() in folder_names_lower:
                    idx = folder_names_lower.index(sent_name.lower())
                    return folder_names[idx]
            
            # Check for partial matches (e.g., "Sent Items" contains "Sent")
            for folder_name in folder_names:
                folder_lower = folder_name.lower()
                if 'sent' in folder_lower and 'draft' not in folder_lower:
                    return folder_name
            
            return None
        except Exception as e:
            logger.warning(f"Failed to find Sent folder: {e}")
            return None


def normalize_email(msg: email.message.Message, uid: int, max_body_bytes: int = MAX_BODY_BYTES, max_attachment_bytes: int = MAX_ATTACHMENT_BYTES) -> Dict[str, Any]:
    """
    Normalize email message to agent-friendly JSON format.
    
    This is the normalization layer that transforms raw IMAP/email data
    into a consistent, agent-friendly format.
    """
    # Parse headers
    headers = {}
    for key, value in msg.items():
        headers[key.lower()] = value
    
    # Parse From
    from_addr = email.utils.parseaddr(msg.get('From', ''))
    from_obj = {
        "name": from_addr[0] or "",
        "email": from_addr[1] or ""
    }
    
    # Parse To
    to_addrs = email.utils.getaddresses(msg.get_all('To', []))
    to_list = [{"name": name or "", "email": email_addr or ""} for name, email_addr in to_addrs]
    
    # Parse CC
    cc_addrs = email.utils.getaddresses(msg.get_all('Cc', []))
    cc_list = [{"name": name or "", "email": email_addr or ""} for name, email_addr in cc_addrs]
    
    # Parse BCC (usually not in received emails, but check)
    bcc_addrs = email.utils.getaddresses(msg.get_all('Bcc', []))
    bcc_list = [{"name": name or "", "email": email_addr or ""} for name, email_addr in bcc_addrs]
    
    # Parse date
    date_str = msg.get('Date', '')
    timestamp = None
    if date_str:
        try:
            date_tuple = email.utils.parsedate_tz(date_str)
            if date_tuple:
                timestamp = datetime(*date_tuple[:6]).isoformat() + 'Z'
        except:
            pass
    
    # Parse subject
    subject = ""
    subject_header = msg.get('Subject', '')
    if subject_header:
        decoded_parts = decode_header(subject_header)
        subject = ''.join([
            part[0].decode(part[1] or 'utf-8', errors='ignore') if isinstance(part[0], bytes) else part[0]
            for part in decoded_parts
        ])
    
    # Parse body and attachments
    body_text = ""
    body_html = ""
    attachments = []
    
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get('Content-Disposition', ''))
            
            # Skip multipart containers
            if content_type.startswith('multipart/'):
                continue
            
            # Handle attachments
            if 'attachment' in content_disposition or part.get_filename():
                filename = part.get_filename()
                if filename:
                    # Decode filename if needed
                    decoded_parts = decode_header(filename)
                    filename = ''.join([
                        part[0].decode(part[1] or 'utf-8', errors='ignore') if isinstance(part[0], bytes) else part[0]
                        for part in decoded_parts
                    ])
                    
                    # Get attachment data
                    payload = part.get_payload(decode=True)
                    if payload:
                        size = len(payload)
                        truncated = False
                        
                        if size > max_attachment_bytes:
                            payload = payload[:max_attachment_bytes]
                            size = max_attachment_bytes
                            truncated = True
                        
                        attachments.append({
                            "filename": filename,
                            "content_type": content_type,
                            "size": size,
                            "truncated": truncated,
                            # Note: We don't include the actual data in JSON for size reasons
                            # Agents can fetch attachments separately if needed
                        })
            else:
                # Handle body content
                payload = part.get_payload(decode=True)
                if payload:
                    try:
                        text = payload.decode('utf-8', errors='ignore')
                        if content_type == 'text/plain':
                            if len(text) > max_body_bytes:
                                body_text = text[:max_body_bytes]
                                truncated = True
                            else:
                                body_text = text
                        elif content_type == 'text/html':
                            if len(text) > max_body_bytes:
                                body_html = text[:max_body_bytes]
                                truncated = True
                            else:
                                body_html = text
                    except:
                        pass
    else:
        # Single part message
        payload = msg.get_payload(decode=True)
        if payload:
            try:
                text = payload.decode('utf-8', errors='ignore')
                content_type = msg.get_content_type()
                if content_type == 'text/html':
                    if len(text) > max_body_bytes:
                        body_html = text[:max_body_bytes]
                    else:
                        body_html = text
                else:
                    if len(text) > max_body_bytes:
                        body_text = text[:max_body_bytes]
                    else:
                        body_text = text
            except:
                pass
    
    # Build normalized email structure
    normalized = {
        "id": str(uid),
        "mailbox": None,  # Will be set by caller if known
        "from": from_obj,
        "to": to_list,
        "cc": cc_list,
        "bcc": bcc_list,
        "subject": subject,
        "timestamp": timestamp or "",
        "body": {
            "text": body_text,
            "html": body_html,
            "attachments": attachments
        },
        "headers": {
            "message-id": headers.get('message-id', ''),
            "references": headers.get('references', ''),
            "in-reply-to": headers.get('in-reply-to', ''),
            "date": headers.get('date', ''),
            "content-type": headers.get('content-type', '')
        },
        "flags": []  # Will be set by caller if known
    }
    
    return normalized


# Global connection instance
_connection: Optional[IMAPConnection] = None


def get_connection() -> Optional[IMAPConnection]:
    """Get the global IMAP connection."""
    return _connection


def set_connection(conn: Optional[IMAPConnection]) -> None:
    """Set the global IMAP connection."""
    global _connection
    _connection = conn

