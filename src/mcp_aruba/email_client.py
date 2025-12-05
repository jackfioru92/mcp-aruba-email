"""IMAP email client for Aruba email server."""

import imaplib
import smtplib
import email
import email.utils
from email.header import decode_header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ArubaEmailClient:
    """Client for accessing Aruba email via IMAP."""

    def __init__(self, host: str, port: int, username: str, password: str, smtp_host: str = None, smtp_port: int = 465):
        """Initialize email client.
        
        Args:
            host: IMAP server hostname
            port: IMAP server port
            username: Email account username
            password: Email account password
            smtp_host: SMTP server hostname (defaults to host with smtps prefix)
            smtp_port: SMTP server port (default: 465 for SSL)
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.smtp_host = smtp_host or host.replace('imaps', 'smtps')
        self.smtp_port = smtp_port
        self._connection: Optional[imaplib.IMAP4_SSL] = None

    def connect(self) -> None:
        """Connect to IMAP server."""
        try:
            logger.info(f"Connecting to {self.host}:{self.port}")
            self._connection = imaplib.IMAP4_SSL(self.host, self.port)
            self._connection.login(self.username, self.password)
            logger.info("Successfully connected to IMAP server")
        except Exception as e:
            logger.error(f"Failed to connect to IMAP server: {e}")
            raise

    def disconnect(self) -> None:
        """Disconnect from IMAP server."""
        if self._connection:
            try:
                self._connection.logout()
                logger.info("Disconnected from IMAP server")
            except Exception as e:
                logger.error(f"Error disconnecting: {e}")
            finally:
                self._connection = None

    def _ensure_connected(self) -> None:
        """Ensure connection is active."""
        if not self._connection:
            self.connect()

    def _decode_header(self, header: str) -> str:
        """Decode email header.
        
        Args:
            header: Email header to decode
            
        Returns:
            Decoded header string
        """
        if not header:
            return ""
        
        decoded_parts = []
        for part, encoding in decode_header(header):
            if isinstance(part, bytes):
                decoded_parts.append(part.decode(encoding or 'utf-8', errors='replace'))
            else:
                decoded_parts.append(str(part))
        return ''.join(decoded_parts)

    def _parse_email(self, email_data: bytes) -> Dict:
        """Parse email data into structured format.
        
        Args:
            email_data: Raw email data
            
        Returns:
            Dictionary with email fields
        """
        msg = email.message_from_bytes(email_data)
        
        # Extract body
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":
                    try:
                        body = part.get_payload(decode=True).decode('utf-8', errors='replace')
                        break
                    except Exception:
                        continue
        else:
            try:
                body = msg.get_payload(decode=True).decode('utf-8', errors='replace')
            except Exception:
                body = str(msg.get_payload())
        
        return {
            "from": self._decode_header(msg.get("From", "")),
            "to": self._decode_header(msg.get("To", "")),
            "subject": self._decode_header(msg.get("Subject", "")),
            "date": msg.get("Date", ""),
            "body": body[:5000]  # Limit body to 5000 chars to avoid huge responses
        }

    def list_emails(
        self,
        folder: str = "INBOX",
        sender_filter: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict]:
        """List emails from specified folder.
        
        Args:
            folder: Mail folder to list from (default: INBOX)
            sender_filter: Filter by sender email address
            limit: Maximum number of emails to return
            
        Returns:
            List of email summaries
        """
        self._ensure_connected()
        
        try:
            self._connection.select(folder)
            
            # Build search criteria
            search_criteria = "ALL"
            if sender_filter:
                search_criteria = f'FROM "{sender_filter}"'
            
            status, messages = self._connection.search(None, search_criteria)
            if status != "OK":
                logger.error("Failed to search emails")
                return []
            
            email_ids = messages[0].split()
            email_ids.reverse()  # Most recent first
            
            results = []
            for email_id in email_ids[:limit]:
                status, msg_data = self._connection.fetch(email_id, "(RFC822)")
                if status != "OK":
                    continue
                
                email_data = self._parse_email(msg_data[0][1])
                email_data["id"] = email_id.decode()
                results.append(email_data)
            
            return results
            
        except Exception as e:
            logger.error(f"Error listing emails: {e}")
            raise

    def read_email(self, email_id: str, folder: str = "INBOX") -> Dict:
        """Read full email content.
        
        Args:
            email_id: Email ID to read
            folder: Mail folder (default: INBOX)
            
        Returns:
            Full email content
        """
        self._ensure_connected()
        
        try:
            self._connection.select(folder)
            status, msg_data = self._connection.fetch(email_id.encode(), "(RFC822)")
            
            if status != "OK":
                raise Exception(f"Failed to fetch email {email_id}")
            
            return self._parse_email(msg_data[0][1])
            
        except Exception as e:
            logger.error(f"Error reading email: {e}")
            raise

    def search_emails(
        self,
        query: str,
        folder: str = "INBOX",
        from_date: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict]:
        """Search emails by subject or body.
        
        Args:
            query: Search query string
            folder: Mail folder to search in
            from_date: Only emails from this date (format: DD-MMM-YYYY)
            limit: Maximum number of results
            
        Returns:
            List of matching emails
        """
        self._ensure_connected()
        
        try:
            self._connection.select(folder)
            
            # Build search criteria
            criteria = []
            if from_date:
                criteria.append(f'SINCE {from_date}')
            criteria.append(f'OR SUBJECT "{query}" BODY "{query}"')
            
            search_str = ' '.join(criteria)
            status, messages = self._connection.search(None, search_str)
            
            if status != "OK":
                logger.error("Failed to search emails")
                return []
            
            email_ids = messages[0].split()
            email_ids.reverse()
            
            results = []
            for email_id in email_ids[:limit]:
                status, msg_data = self._connection.fetch(email_id, "(RFC822)")
                if status != "OK":
                    continue
                
                email_data = self._parse_email(msg_data[0][1])
                email_data["id"] = email_id.decode()
                results.append(email_data)
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching emails: {e}")
            raise

    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        from_name: Optional[str] = None,
        save_to_sent: bool = True
    ) -> Dict:
        """Send an email via SMTP.
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body (plain text)
            from_name: Optional sender display name
            save_to_sent: Whether to save a copy to the Sent folder (default: True)
            
        Returns:
            Dictionary with send status
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{from_name} <{self.username}>" if from_name else self.username
            msg['To'] = to
            msg['Date'] = email.utils.formatdate(localtime=True)
            
            # Add body
            part = MIMEText(body, 'plain', 'utf-8')
            msg.attach(part)
            
            # Connect to SMTP server
            logger.info(f"Connecting to SMTP server {self.smtp_host}:{self.smtp_port}")
            with smtplib.SMTP_SSL(self.smtp_host, self.smtp_port) as smtp:
                smtp.login(self.username, self.password)
                smtp.send_message(msg)
            
            logger.info(f"Email sent successfully to {to}")
            
            # Save to Sent folder if requested
            if save_to_sent:
                try:
                    self._ensure_connected()
                    # Append the message to INBOX.Sent folder
                    self._connection.append(
                        'INBOX.Sent',
                        '\\Seen',
                        imaplib.Time2Internaldate(email.utils.parsedate_to_datetime(msg['Date'])),
                        msg.as_bytes()
                    )
                    logger.info("Email saved to Sent folder")
                except Exception as e:
                    logger.warning(f"Failed to save email to Sent folder: {e}")
                    # Don't fail the whole operation if saving to Sent fails
            
            return {
                "status": "sent",
                "to": to,
                "subject": subject,
                "from": msg['From'],
                "saved_to_sent": save_to_sent
            }
            
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            raise

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
