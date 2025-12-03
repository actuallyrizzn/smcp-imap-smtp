"""
SMTP Client Module

Handles SMTP connection management and email sending.
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
        self.host: Optional[str] = None
        self.port: Optional[int] = None
        self.username: Optional[str] = None
        self.use_tls: bool = True
    
    def connect(self, host: str, username: str, password: str, port: int = 587, use_tls: bool = True) -> None:
        """Connect to SMTP server."""
        try:
            self.server = smtplib.SMTP(host, port)
            if use_tls:
                self.server.starttls()
            self.server.login(username, password)
            self.host = host
            self.port = port
            self.username = username
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
        
        return {
            "sent": True,
            "from": from_addr,
            "to": to_addrs,
            "cc": cc or [],
            "bcc": bcc or [],
            "subject": subject,
            "attachments": attachment_info
        }


# Global connection instance
_connection: Optional[SMTPConnection] = None


def get_connection() -> Optional[SMTPConnection]:
    """Get the global SMTP connection."""
    return _connection


def set_connection(conn: Optional[SMTPConnection]) -> None:
    """Set the global SMTP connection."""
    global _connection
    _connection = conn

