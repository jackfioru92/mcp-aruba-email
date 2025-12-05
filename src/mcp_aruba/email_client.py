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

    def verify_email_exists(self, email_address: str) -> Dict:
        """Verify if an email address exists by checking with the recipient's mail server.
        
        Args:
            email_address: Email address to verify
            
        Returns:
            Dictionary with verification status and details
        """
        import socket
        import dns.resolver
        
        try:
            # Extract domain from email
            domain = email_address.split('@')[1]
            
            # Get MX records for the domain
            try:
                mx_records = dns.resolver.resolve(domain, 'MX')
                mx_host = str(mx_records[0].exchange)
            except Exception as e:
                logger.warning(f"Could not resolve MX records for {domain}: {e}")
                return {
                    "email": email_address,
                    "exists": "unknown",
                    "reason": f"Could not find mail server for domain {domain}",
                    "verification_method": "mx_lookup"
                }
            
            # Connect to the mail server and check if mailbox exists
            try:
                # Create SMTP connection (port 25 for verification)
                server = smtplib.SMTP(timeout=10)
                server.connect(mx_host, 25)
                server.helo(self.smtp_host)
                server.mail(self.username)
                
                # RCPT TO command - this checks if the mailbox exists
                code, message = server.rcpt(email_address)
                server.quit()
                
                # 250 = mailbox exists and accepts mail
                # 550 = mailbox does not exist
                # 551-554 = various rejection reasons
                if code == 250:
                    logger.info(f"Email {email_address} verified: exists")
                    return {
                        "email": email_address,
                        "exists": True,
                        "reason": "Mailbox exists and accepts mail",
                        "smtp_code": code,
                        "verification_method": "smtp_rcpt"
                    }
                elif code in [550, 551, 553]:
                    logger.warning(f"Email {email_address} verified: does not exist (code {code})")
                    return {
                        "email": email_address,
                        "exists": False,
                        "reason": message.decode() if isinstance(message, bytes) else str(message),
                        "smtp_code": code,
                        "verification_method": "smtp_rcpt"
                    }
                else:
                    logger.info(f"Email {email_address} verification uncertain (code {code})")
                    return {
                        "email": email_address,
                        "exists": "unknown",
                        "reason": message.decode() if isinstance(message, bytes) else str(message),
                        "smtp_code": code,
                        "verification_method": "smtp_rcpt"
                    }
                    
            except (socket.timeout, socket.error, smtplib.SMTPException) as e:
                logger.warning(f"Could not verify {email_address} via SMTP: {e}")
                return {
                    "email": email_address,
                    "exists": "unknown",
                    "reason": f"Mail server did not respond or blocked verification: {str(e)}",
                    "verification_method": "smtp_rcpt_failed"
                }
                
        except Exception as e:
            logger.error(f"Error verifying email {email_address}: {e}")
            return {
                "email": email_address,
                "exists": "unknown",
                "reason": f"Verification error: {str(e)}",
                "verification_method": "error"
            }

    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        from_name: Optional[str] = None,
        save_to_sent: bool = True,
        verify_recipient: bool = True,
        use_signature: bool = True,
        signature_name: str = "default"
    ) -> Dict:
        """Send an email via SMTP.
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body (plain text)
            from_name: Optional sender display name
            save_to_sent: Whether to save a copy to the Sent folder (default: True)
            verify_recipient: Whether to verify recipient email exists before sending (default: True)
            use_signature: Whether to append email signature (default: True)
            signature_name: Name of the signature to use (default: "default")
            
        Returns:
            Dictionary with send status
        """
        try:
            # Verify recipient email exists (if requested)
            if verify_recipient:
                verification = self.verify_email_exists(to)
                if verification["exists"] is False:
                    logger.error(f"Recipient verification failed: {verification['reason']}")
                    return {
                        "status": "failed",
                        "error": "Recipient email does not exist",
                        "to": to,
                        "verification": verification
                    }
                elif verification["exists"] == "unknown":
                    logger.warning(f"Could not verify recipient: {verification['reason']}")
                    # Continue anyway but include warning
            
            # Add signature to body if requested
            final_body = body
            is_html_signature = False
            if use_signature:
                from .signature import get_signature
                signature = get_signature(signature_name)
                if signature:
                    # Check if signature is HTML
                    if signature.strip().startswith('<'):
                        is_html_signature = True
                        # Convert plain body to HTML and append signature
                        final_body = f"<div>{body.replace(chr(10), '<br>')}</div>{signature}"
                    else:
                        final_body = f"{body}\n\n{signature}"
                    logger.debug(f"Appended signature '{signature_name}' to email (HTML: {is_html_signature})")
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{from_name} <{self.username}>" if from_name else self.username
            msg['To'] = to
            msg['Date'] = email.utils.formatdate(localtime=True)
            
            # Add plain text version
            plain_part = MIMEText(body, 'plain', 'utf-8')
            msg.attach(plain_part)
            
            # Add HTML version if signature is HTML
            if is_html_signature:
                html_part = MIMEText(final_body, 'html', 'utf-8')
                msg.attach(html_part)
            elif use_signature and not is_html_signature:
                # Replace plain text part with version including signature
                msg.set_payload([MIMEText(final_body, 'plain', 'utf-8')])
            
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
            
            result = {
                "status": "sent",
                "to": to,
                "subject": subject,
                "from": msg['From'],
                "saved_to_sent": save_to_sent
            }
            
            if verify_recipient:
                result["verification"] = verification
            
            return result
            
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            raise

    def check_bounced_emails(self, folder: str = "INBOX", limit: int = 50) -> List[Dict]:
        """Check for bounced/failed delivery emails.
        
        Args:
            folder: Mail folder to check (default: INBOX)
            limit: Maximum number of emails to check
            
        Returns:
            List of bounced email notifications with details
        """
        self._ensure_connected()
        
        try:
            self._connection.select(folder)
            
            # Search for common bounce indicators
            bounce_patterns = [
                'Mail Delivery Failed',
                'Delivery Status Notification',
                'Undelivered Mail Returned to Sender',
                'Mail delivery failed',
                'Returned mail',
                'Failure Notice',
                'MAILER-DAEMON'
            ]
            
            bounced_emails = []
            
            for pattern in bounce_patterns:
                try:
                    status, messages = self._connection.search(None, f'SUBJECT "{pattern}"')
                    if status == "OK" and messages[0]:
                        email_ids = messages[0].split()
                        
                        for email_id in email_ids[-limit:]:
                            status, msg_data = self._connection.fetch(email_id, "(RFC822)")
                            if status != "OK":
                                continue
                            
                            msg = email.message_from_bytes(msg_data[0][1])
                            
                            # Parse bounce information
                            bounce_info = {
                                "id": email_id.decode(),
                                "subject": msg.get("Subject", ""),
                                "from": msg.get("From", ""),
                                "date": msg.get("Date", ""),
                                "bounce_type": pattern
                            }
                            
                            # Try to extract original recipient and reason from body
                            body = ""
                            if msg.is_multipart():
                                for part in msg.walk():
                                    if part.get_content_type() == "text/plain":
                                        try:
                                            body = part.get_payload(decode=True).decode()
                                            break
                                        except:
                                            pass
                            else:
                                try:
                                    body = msg.get_payload(decode=True).decode()
                                except:
                                    body = str(msg.get_payload())
                            
                            # Extract failed recipient email
                            import re
                            recipient_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', body)
                            if recipient_match:
                                bounce_info["failed_recipient"] = recipient_match.group()
                            
                            # Extract error reason (common patterns)
                            if "user unknown" in body.lower() or "mailbox not found" in body.lower():
                                bounce_info["reason"] = "Mailbox does not exist"
                            elif "quota exceeded" in body.lower():
                                bounce_info["reason"] = "Recipient mailbox full"
                            elif "rejected" in body.lower():
                                bounce_info["reason"] = "Message rejected by recipient server"
                            else:
                                bounce_info["reason"] = "Delivery failed (see details)"
                            
                            bounce_info["body_preview"] = body[:500] if body else "No body"
                            
                            # Avoid duplicates
                            if not any(b["id"] == bounce_info["id"] for b in bounced_emails):
                                bounced_emails.append(bounce_info)
                                
                except Exception as e:
                    logger.debug(f"Error searching for pattern '{pattern}': {e}")
                    continue
            
            logger.info(f"Found {len(bounced_emails)} bounced email notifications")
            return bounced_emails
            
        except Exception as e:
            logger.error(f"Error checking bounced emails: {e}")
            raise

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
