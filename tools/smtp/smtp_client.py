"""
SMTP Client Module

Handles SMTP connection management and email sending.
Automatically saves sent messages to IMAP Sent folder (like normal email clients).
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Dict, Any, List, Optional
import os
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
MAX_ATTACHMENT_BYTES = int(os.getenv('MAX_ATTACHMENT_BYTES', 25 * 1024 * 1024))  # 25MB default


class SMTPConnection:
    """Manages SMTP connection and email sending."""
    
    def __init__(self):
        self.server: Optional[smtplib.SMTP] = None
        self.host: Optional[str] = None  # SMTP server hostname (for IMAP fallback)
        self.port: Optional[int] = None
        self.username: Optional[str] = None
        self.password: Optional[str] = None  # Store password for IMAP save
        self.use_tls: bool = True
        self.imap_server: Optional[str] = None  # Optional explicit IMAP server
        self.imap_port: Optional[int] = None  # Optional explicit IMAP port
        self.imap_ssl: Optional[bool] = None  # Optional explicit IMAP SSL setting
    
    def connect(self, host: str, username: str, password: str, port: int = 587, use_tls: bool = True) -> None:
        """Connect to SMTP server."""
        try:
            # Add timeout to prevent hanging connections (30 seconds)
            self.server = smtplib.SMTP(host, port, timeout=30)
            if use_tls:
                self.server.starttls()
            self.server.login(username, password)
            self.host = host
            self.port = port
            self.username = username
            self.password = password  # Store for IMAP save
            self.use_tls = use_tls
            # Mask password in logs
            masked_username = username.split('@')[0] + '@***' if '@' in username else '***'
            logger.info(f"Connected to {host}:{port} as {masked_username}")
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            raise
    
    def disconnect(self) -> None:
        """Disconnect from SMTP server."""
        if self.server:
            try:
                self.server.quit()
            except:
                try:
                    self.server.close()
                except:
                    pass
            self.server = None
            self.host = None
            self.port = None
            self.username = None
            self.password = None
            logger.info("Disconnected from SMTP server")
    
    def send_email(
        self,
        to_addrs: List[str],
        subject: str,
        body: str,
        from_addr: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        reply_to: Optional[str] = None,
        html: bool = False,
        text_body: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send an email."""
        if not self.server:
            raise RuntimeError("Not connected to SMTP server")
        
        # Use username as from_addr if not provided
        if not from_addr:
            from_addr = self.username
        
        # Create message
        if html:
            msg = MIMEMultipart('alternative')
            if text_body:
                part1 = MIMEText(text_body, 'plain')
                msg.attach(part1)
            part2 = MIMEText(body, 'html')
            msg.attach(part2)
        else:
            msg = MIMEText(body, 'plain')
        
        msg['From'] = from_addr
        msg['To'] = ', '.join(to_addrs)
        if cc:
            msg['Cc'] = ', '.join(cc)
        if reply_to:
            msg['Reply-To'] = reply_to
        msg['Subject'] = subject
        
        # Combine all recipients
        recipients = to_addrs[:]
        if cc:
            recipients.extend(cc)
        if bcc:
            recipients.extend(bcc)
        
        # Send email
        self.server.sendmail(from_addr, recipients, msg.as_string())
        
        # Automatically save to Sent folder via IMAP (like normal email clients)
        message_bytes = msg.as_bytes()
        self._save_to_sent_folder(message_bytes)
        
        return {
            "sent": True,
            "from": from_addr,
            "to": to_addrs,
            "cc": cc or [],
            "bcc": bcc or [],
            "subject": subject
        }
    
    def send_email_with_attachments(
        self,
        to_addrs: List[str],
        subject: str,
        body: str,
        attachments: List[str],
        from_addr: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        reply_to: Optional[str] = None,
        html: bool = False
    ) -> Dict[str, Any]:
        """Send an email with attachments."""
        if not self.server:
            raise RuntimeError("Not connected to SMTP server")
        
        # Validate attachment sizes
        attachment_info = []
        for attachment_path in attachments:
            if not os.path.exists(attachment_path):
                raise FileNotFoundError(f"Attachment not found: {attachment_path}")
            
            size = os.path.getsize(attachment_path)
            if size > MAX_ATTACHMENT_BYTES:
                raise ValueError(f"Attachment {attachment_path} exceeds maximum size of {MAX_ATTACHMENT_BYTES} bytes")
            
            attachment_info.append({
                "path": attachment_path,
                "size": size,
                "filename": os.path.basename(attachment_path)
            })
        
        # Use username as from_addr if not provided
        if not from_addr:
            from_addr = self.username
        
        # Create multipart message
        msg = MIMEMultipart()
        msg['From'] = from_addr
        msg['To'] = ', '.join(to_addrs)
        if cc:
            msg['Cc'] = ', '.join(cc)
        if reply_to:
            msg['Reply-To'] = reply_to
        msg['Subject'] = subject
        
        # Add body
        body_part = MIMEText(body, 'html' if html else 'plain')
        msg.attach(body_part)
        
        # Add attachments
        for attachment_path in attachments:
            with open(attachment_path, 'rb') as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
            
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {os.path.basename(attachment_path)}'
            )
            msg.attach(part)
        
        # Combine all recipients
        recipients = to_addrs[:]
        if cc:
            recipients.extend(cc)
        if bcc:
            recipients.extend(bcc)
        
        # Send email
        self.server.sendmail(from_addr, recipients, msg.as_string())
        
        # Automatically save to Sent folder via IMAP (like normal email clients)
        message_bytes = msg.as_bytes()
        self._save_to_sent_folder(message_bytes)
        
        return {
            "sent": True,
            "from": from_addr,
            "to": to_addrs,
            "cc": cc or [],
            "bcc": bcc or [],
            "subject": subject,
            "attachments": attachment_info
        }
    
    def _save_to_sent_folder(self, message_bytes: bytes) -> None:
        """
        Save sent message to IMAP Sent folder.
        This is called automatically after successful send (like normal email clients).
        Fails gracefully - doesn't raise exceptions if save fails.
        """
        try:
            # Try to import IMAP client (may not be available)
            # Try multiple import paths for plugin structure compatibility
            IMAPConnection = None
            import_paths = [
                'tools.imap.imap_client',
                'plugins.imap.imap_client',
            ]
            
            for import_path in import_paths:
                try:
                    module = __import__(import_path, fromlist=['IMAPConnection'])
                    IMAPConnection = module.IMAPConnection
                    break
                except ImportError:
                    continue
            
            if IMAPConnection is None:
                # Last resort: try relative import if we're in tools package
                try:
                    import sys
                    import os
                    # Check if we're in tools package structure
                    current_file = os.path.abspath(__file__)
                    if 'tools' in current_file:
                        # Try to find imap_client relative to smtp_client
                        tools_dir = os.path.dirname(os.path.dirname(current_file))
                        imap_client_path = os.path.join(tools_dir, 'imap', 'imap_client.py')
                        if os.path.exists(imap_client_path):
                            # Add to path and import
                            if tools_dir not in sys.path:
                                sys.path.insert(0, tools_dir)
                            from imap.imap_client import IMAPConnection
                except Exception:
                    logger.warning("IMAP client not available, skipping save to Sent folder")
                    return
            
            # Need IMAP server details - try multiple sources
            if not self.username or not self.password:
                logger.warning("Missing credentials, skipping save to Sent folder")
                return
            
            # Priority 1: Explicit IMAP server settings (if provided)
            imap_server = self.imap_server
            imap_port = self.imap_port if self.imap_port is not None else 993
            imap_ssl = self.imap_ssl if self.imap_ssl is not None else True
            password = self.password
            
            # Priority 2: Try to get from profile manager
            if not imap_server:
                try:
                    from tools.config import ProfileManager
                    manager = ProfileManager()
                    # Try to find profile by username
                    for profile_name in manager.list_profiles():
                        profile = manager.get_profile(profile_name)
                        if profile and profile.username == self.username:
                            imap_server = profile.imap_server
                            imap_port = profile.imap_port
                            imap_ssl = profile.imap_ssl
                            password = profile.password
                            break
                    
                    # If no profile found, try default
                    if not imap_server:
                        default_profile = manager.get_default()
                        if default_profile and default_profile.username == self.username:
                            imap_server = default_profile.imap_server
                            imap_port = default_profile.imap_port
                            imap_ssl = default_profile.imap_ssl
                            password = default_profile.password
                except Exception as e:
                    logger.debug(f"Could not load profile for IMAP save: {e}")
                    # Continue with fallback attempt
                    pass
            
            # Priority 3: Derive IMAP server from SMTP server (common pattern)
            if not imap_server and self.host:
                # Common patterns: mail.domain.com -> imap.domain.com
                # Or same hostname for many providers
                smtp_host = self.host.lower()
                
                # Try common IMAP hostname patterns
                if smtp_host.startswith('mail.'):
                    imap_server = smtp_host.replace('mail.', 'imap.', 1)
                elif smtp_host.startswith('smtp.'):
                    imap_server = smtp_host.replace('smtp.', 'imap.', 1)
                elif 'mail' in smtp_host and 'smtp' not in smtp_host:
                    # For hosts like mail.gmx.com, try imap.gmx.com
                    parts = smtp_host.split('.')
                    if len(parts) >= 2:
                        # Replace first part (mail) with imap
                        parts[0] = 'imap'
                        imap_server = '.'.join(parts)
                else:
                    # Many providers use the same hostname for both
                    imap_server = smtp_host
                
                logger.debug(f"Derived IMAP server '{imap_server}' from SMTP server '{self.host}'")
            
            if not imap_server:
                logger.warning("IMAP server not configured and could not be derived, skipping save to Sent folder")
                return
            
            # Connect to IMAP and save
            try:
                imap_conn = IMAPConnection()
                imap_conn.connect(imap_server, self.username, password, imap_port, imap_ssl)
                
                # Find Sent folder
                sent_folder = imap_conn.find_sent_folder()
                if not sent_folder:
                    logger.warning("Sent folder not found, skipping save")
                    imap_conn.disconnect()
                    return
                
                # Append message to Sent folder
                imap_conn.append_to_mailbox(sent_folder, message_bytes, flags=['\\Seen'])
                logger.info(f"Saved sent message to {sent_folder}")
                imap_conn.disconnect()
            except Exception as e:
                logger.warning(f"Failed to save message to Sent folder: {e}")
                # Don't raise - email was sent successfully, save is just a convenience
        except Exception as e:
            # Catch-all to ensure we never break the send operation
            logger.warning(f"Error during save to Sent folder: {e}")


# Global connection instance
_connection: Optional[SMTPConnection] = None


def get_connection() -> Optional[SMTPConnection]:
    """Get the global SMTP connection."""
    return _connection


def set_connection(conn: Optional[SMTPConnection]) -> None:
    """Set the global SMTP connection."""
    global _connection
    _connection = conn

