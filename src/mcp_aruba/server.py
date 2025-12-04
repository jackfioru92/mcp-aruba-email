"""MCP server for Aruba email access via IMAP."""

import os
import logging
from typing import Any
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from .email_client import ArubaEmailClient

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Initialize MCP server
mcp = FastMCP("aruba-email")

# Email client configuration
IMAP_CONFIG = {
    "host": os.getenv("IMAP_HOST", "imaps.aruba.it"),
    "port": int(os.getenv("IMAP_PORT", "993")),
    "username": os.getenv("IMAP_USERNAME", ""),
    "password": os.getenv("IMAP_PASSWORD", ""),
}


def _get_email_client() -> ArubaEmailClient:
    """Create and return email client instance."""
    if not IMAP_CONFIG["username"] or not IMAP_CONFIG["password"]:
        raise ValueError("IMAP credentials not configured. Set IMAP_USERNAME and IMAP_PASSWORD environment variables.")
    
    return ArubaEmailClient(
        host=IMAP_CONFIG["host"],
        port=IMAP_CONFIG["port"],
        username=IMAP_CONFIG["username"],
        password=IMAP_CONFIG["password"],
        smtp_host="smtps.aruba.it",
        smtp_port=465
    )


@mcp.tool()
def list_emails(
    folder: str = "INBOX",
    sender_filter: str | None = None,
    limit: int = 10
) -> list[dict[str, Any]]:
    """List emails from the specified folder.
    
    Args:
        folder: Mail folder to list from (default: INBOX)
        sender_filter: Optional filter by sender email address (e.g., "denisa@c-tic.it")
        limit: Maximum number of emails to return (default: 10, max: 50)
    
    Returns:
        List of email summaries with id, from, to, subject, date, and body preview
    
    Example:
        list_emails(sender_filter="denisa@c-tic.it", limit=5)
    """
    limit = min(limit, 50)  # Cap at 50 emails
    
    try:
        with _get_email_client() as client:
            emails = client.list_emails(
                folder=folder,
                sender_filter=sender_filter,
                limit=limit
            )
            logger.info(f"Listed {len(emails)} emails from {folder}")
            return emails
    except Exception as e:
        logger.error(f"Error listing emails: {e}")
        return [{"error": str(e)}]


@mcp.tool()
def read_email(email_id: str, folder: str = "INBOX") -> dict[str, Any]:
    """Read the full content of a specific email.
    
    Args:
        email_id: Email ID to read (from list_emails)
        folder: Mail folder (default: INBOX)
    
    Returns:
        Full email content with from, to, subject, date, and body
    
    Example:
        read_email(email_id="123")
    """
    try:
        with _get_email_client() as client:
            email_data = client.read_email(email_id=email_id, folder=folder)
            logger.info(f"Read email {email_id} from {folder}")
            return email_data
    except Exception as e:
        logger.error(f"Error reading email: {e}")
        return {"error": str(e)}


@mcp.tool()
def search_emails(
    query: str,
    folder: str = "INBOX",
    from_date: str | None = None,
    limit: int = 10
) -> list[dict[str, Any]]:
    """Search emails by subject or body content.
    
    Args:
        query: Search query string (searches in subject and body)
        folder: Mail folder to search in (default: INBOX)
        from_date: Only emails from this date onwards (format: DD-MMM-YYYY, e.g., "01-Dec-2024")
        limit: Maximum number of results (default: 10, max: 50)
    
    Returns:
        List of matching emails
    
    Example:
        search_emails(query="API", from_date="01-Dec-2024", limit=5)
    """
    limit = min(limit, 50)  # Cap at 50 emails
    
    try:
        with _get_email_client() as client:
            emails = client.search_emails(
                query=query,
                folder=folder,
                from_date=from_date,
                limit=limit
            )
            logger.info(f"Found {len(emails)} emails matching '{query}'")
            return emails
    except Exception as e:
        logger.error(f"Error searching emails: {e}")
        return [{"error": str(e)}]


@mcp.tool()
def send_email(
    to: str,
    subject: str,
    body: str,
    from_name: str = "Giacomo Fiorucci"
) -> dict[str, Any]:
    """Send an email via SMTP.
    
    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body (plain text)
        from_name: Sender display name (default: "Giacomo Fiorucci")
    
    Returns:
        Send status with details
    
    Example:
        send_email(
            to="christopher.caponi@emotion-team.com",
            subject="Ciao Christopher!",
            body="Come stai? Ti scrivo per...",
            from_name="Giacomo Fiorucci"
        )
    """
    try:
        with _get_email_client() as client:
            result = client.send_email(
                to=to,
                subject=subject,
                body=body,
                from_name=from_name
            )
            logger.info(f"Sent email to {to}: {subject}")
            return result
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        return {"error": str(e), "status": "failed"}


def main():
    """Run the MCP server."""
    logger.info("Starting Aruba Email MCP Server")
    logger.info(f"Configured for: {IMAP_CONFIG['username']}@{IMAP_CONFIG['host']}")
    mcp.run(transport='stdio')


if __name__ == "__main__":
    main()
