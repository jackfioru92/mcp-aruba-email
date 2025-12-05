"""MCP server for Aruba email and calendar access via IMAP and CalDAV."""

import os
import logging
from typing import Any
from datetime import datetime
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from .email_client import ArubaEmailClient
from .calendar_client import ArubaCalendarClient

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

# Calendar client configuration
CALDAV_CONFIG = {
    "url": os.getenv("CALDAV_URL", "https://syncdav.aruba.it/calendars/user@domain.com/"),
    "username": os.getenv("CALDAV_USERNAME", os.getenv("IMAP_USERNAME", "")),
    "password": os.getenv("CALDAV_PASSWORD", os.getenv("IMAP_PASSWORD", "")),
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


def _get_calendar_client() -> ArubaCalendarClient:
    """Create and return calendar client instance."""
    if not CALDAV_CONFIG["username"] or not CALDAV_CONFIG["password"]:
        raise ValueError("CalDAV credentials not configured. Set CALDAV_USERNAME and CALDAV_PASSWORD environment variables.")
    
    return ArubaCalendarClient(
        url=CALDAV_CONFIG["url"],
        username=CALDAV_CONFIG["username"],
        password=CALDAV_CONFIG["password"]
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


@mcp.tool()
def check_bounced_emails(
    folder: str = "INBOX",
    limit: int = 20
) -> list[dict[str, Any]]:
    """Check for bounced or failed email delivery notifications.
    
    This tool searches for delivery failure notifications (bounce-backs) that indicate
    emails could not be delivered. Common reasons include:
    - Recipient mailbox does not exist
    - Recipient mailbox is full
    - Message rejected by recipient server
    
    Args:
        folder: Mail folder to check (default: INBOX)
        limit: Maximum number of bounce notifications to check (default: 20)
    
    Returns:
        List of bounce notifications with failed recipient and reason
    
    Example:
        check_bounced_emails(limit=10)
    """
    try:
        with _get_email_client() as client:
            bounced = client.check_bounced_emails(folder=folder, limit=limit)
            logger.info(f"Found {len(bounced)} bounced email notifications")
            return bounced
    except Exception as e:
        logger.error(f"Error checking bounced emails: {e}")
        return {"error": str(e)}


# ============================================================================
# EMAIL SIGNATURE TOOLS
# ============================================================================

@mcp.tool()
def set_email_signature(
    name: str,
    email: str,
    role: str | None = None,
    company: str | None = None,
    phone: str | None = None,
    photo_url: str | None = None,
    color: str | None = None,
    style: str = "professional",
    signature_name: str = "default"
) -> dict[str, Any]:
    """Create and save a professional email signature with optional photo and colors.
    
    The signature will be automatically appended to all sent emails.
    If photo_url or color are provided, an HTML signature will be created.
    
    Args:
        name: Full name (e.g., "Giacomo Fiorucci")
        email: Email address
        role: Job title/role (optional, e.g., "Software Developer")
        company: Company name (optional, e.g., "Emotion Team")
        phone: Phone number (optional, e.g., "+39 123 456 7890")
        photo_url: URL or local file path to profile photo (optional, auto-uploads if local file)
        color: Hex color code for accents (optional, e.g., "#0066cc", "#FF5722")
        style: Signature style - "professional", "minimal", "colorful" (default: "professional")
        signature_name: Name to save signature as (default: "default")
    
    Returns:
        Confirmation with signature preview
    
    Examples:
        # Simple text signature
        set_email_signature(
            name="Giacomo Fiorucci",
            email="giacomo.fiorucci@emotion-team.com",
            role="Software Developer",
            company="Emotion Team"
        )
        
        # HTML signature with photo and custom color
        set_email_signature(
            name="Giacomo Fiorucci",
            email="giacomo.fiorucci@emotion-team.com",
            role="Software Developer",
            company="Emotion Team",
            phone="+39 123 456 7890",
            photo_url="https://example.com/photo.jpg",
            color="#0066cc",
            style="professional"
        )
    """
    try:
        from .signature import create_default_signature, save_signature
        
        signature = create_default_signature(
            name=name,
            email=email,
            phone=phone,
            company=company,
            role=role,
            photo_input=photo_url,  # Will auto-upload if local file
            color=color,
            style=style
        )
        
        save_signature(signature, signature_name)
        
        logger.info(f"Saved email signature '{signature_name}'")
        return {
            "status": "saved",
            "signature_name": signature_name,
            "preview": signature
        }
    except Exception as e:
        logger.error(f"Error saving signature: {e}")
        return {"error": str(e)}


@mcp.tool()
def get_email_signature(signature_name: str = "default") -> dict[str, Any]:
    """Get a saved email signature.
    
    Args:
        signature_name: Name of signature to retrieve (default: "default")
    
    Returns:
        Signature content or error
    
    Example:
        get_email_signature()
    """
    try:
        from .signature import get_signature
        
        signature = get_signature(signature_name)
        
        if signature:
            return {
                "signature_name": signature_name,
                "content": signature
            }
        else:
            return {
                "error": f"Signature '{signature_name}' not found"
            }
    except Exception as e:
        logger.error(f"Error getting signature: {e}")
        return {"error": str(e)}


@mcp.tool()
def list_email_signatures() -> dict[str, Any]:
    """List all saved email signatures.
    
    Returns:
        Dictionary of all signatures
    
    Example:
        list_email_signatures()
    """
    try:
        from .signature import list_signatures
        
        signatures = list_signatures()
        
        return {
            "count": len(signatures),
            "signatures": signatures
        }
    except Exception as e:
        logger.error(f"Error listing signatures: {e}")
        return {"error": str(e)}


# ============================================================================
# CALENDAR TOOLS
# ============================================================================

@mcp.tool()
def create_calendar_event(
    summary: str,
    start: str,
    end: str,
    description: str | None = None,
    location: str | None = None,
    attendees: str | None = None
) -> dict[str, Any]:
    """Create a new calendar event.
    
    Args:
        summary: Event title
        start: Start datetime in ISO format (e.g., "2025-12-05T10:00:00")
        end: End datetime in ISO format (e.g., "2025-12-05T11:00:00")
        description: Event description (optional)
        location: Event location (optional)
        attendees: Comma-separated list of attendee email addresses (optional)
    
    Returns:
        Created event details including UID
    
    Example:
        create_calendar_event(
            summary="Team Meeting",
            start="2025-12-05T10:00:00",
            end="2025-12-05T11:00:00",
            description="Discussione sui nuovi progetti",
            location="Sala Riunioni A",
            attendees="christopher.caponi@emotion-team.com,marco.rossi@example.com"
        )
    """
    try:
        # Parse datetime strings
        start_dt = datetime.fromisoformat(start)
        end_dt = datetime.fromisoformat(end)
        
        # Parse attendees
        attendee_list = None
        if attendees:
            attendee_list = [email.strip() for email in attendees.split(",") if email.strip()]
        
        with _get_calendar_client() as client:
            result = client.create_event(
                summary=summary,
                start=start_dt,
                end=end_dt,
                description=description,
                location=location,
                attendees=attendee_list
            )
            logger.info(f"Created calendar event: {summary}")
            return result
    except ValueError as e:
        logger.error(f"Invalid datetime format: {e}")
        return {"error": f"Invalid datetime format. Use ISO format (YYYY-MM-DDTHH:MM:SS): {str(e)}"}
    except Exception as e:
        logger.error(f"Error creating calendar event: {e}")
        return {"error": str(e), "success": False}


@mcp.tool()
def list_calendar_events(
    start_date: str | None = None,
    end_date: str | None = None,
    limit: int = 50
) -> list[dict[str, Any]]:
    """List calendar events within a date range.
    
    Args:
        start_date: Start date in ISO format (default: today)
        end_date: End date in ISO format (default: 30 days from now)
        limit: Maximum number of events to return (default: 50)
    
    Returns:
        List of calendar events
    
    Example:
        list_calendar_events(
            start_date="2025-12-01T00:00:00",
            end_date="2025-12-31T23:59:59",
            limit=20
        )
    """
    try:
        # Parse dates if provided
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None
        
        with _get_calendar_client() as client:
            events = client.list_events(
                start_date=start_dt,
                end_date=end_dt,
                limit=limit
            )
            logger.info(f"Listed {len(events)} calendar events")
            return events
    except ValueError as e:
        logger.error(f"Invalid datetime format: {e}")
        return [{"error": f"Invalid datetime format. Use ISO format (YYYY-MM-DDTHH:MM:SS): {str(e)}"}]
    except Exception as e:
        logger.error(f"Error listing calendar events: {e}")
        return [{"error": str(e)}]


@mcp.tool()
def accept_calendar_event(
    event_uid: str,
    comment: str | None = None
) -> dict[str, Any]:
    """Accept a calendar event invitation.
    
    Args:
        event_uid: UID of the event to accept
        comment: Optional comment for the acceptance
    
    Returns:
        Response status
    
    Example:
        accept_calendar_event(
            event_uid="abc123@aruba.it",
            comment="Ci sarò!"
        )
    """
    try:
        with _get_calendar_client() as client:
            result = client.respond_to_event(
                event_uid=event_uid,
                response="ACCEPTED",
                comment=comment
            )
            logger.info(f"Accepted calendar event: {event_uid}")
            return result
    except Exception as e:
        logger.error(f"Error accepting calendar event: {e}")
        return {"error": str(e), "success": False}


@mcp.tool()
def decline_calendar_event(
    event_uid: str,
    comment: str | None = None
) -> dict[str, Any]:
    """Decline a calendar event invitation.
    
    Args:
        event_uid: UID of the event to decline
        comment: Optional comment for the decline
    
    Returns:
        Response status
    
    Example:
        decline_calendar_event(
            event_uid="abc123@aruba.it",
            comment="Purtroppo non posso partecipare"
        )
    """
    try:
        with _get_calendar_client() as client:
            result = client.respond_to_event(
                event_uid=event_uid,
                response="DECLINED",
                comment=comment
            )
            logger.info(f"Declined calendar event: {event_uid}")
            return result
    except Exception as e:
        logger.error(f"Error declining calendar event: {e}")
        return {"error": str(e), "success": False}


@mcp.tool()
def tentative_calendar_event(
    event_uid: str,
    comment: str | None = None
) -> dict[str, Any]:
    """Mark a calendar event as tentative (maybe attending).
    
    Args:
        event_uid: UID of the event
        comment: Optional comment
    
    Returns:
        Response status
    
    Example:
        tentative_calendar_event(
            event_uid="abc123@aruba.it",
            comment="Forse riesco a partecipare"
        )
    """
    try:
        with _get_calendar_client() as client:
            result = client.respond_to_event(
                event_uid=event_uid,
                response="TENTATIVE",
                comment=comment
            )
            logger.info(f"Marked calendar event as tentative: {event_uid}")
            return result
    except Exception as e:
        logger.error(f"Error updating calendar event: {e}")
        return {"error": str(e), "success": False}


@mcp.tool()
def delete_calendar_event(event_uid: str) -> dict[str, Any]:
    """Delete a calendar event.
    
    Args:
        event_uid: UID of the event to delete
    
    Returns:
        Deletion status
    
    Example:
        delete_calendar_event(event_uid="abc123@aruba.it")
    """
    try:
        with _get_calendar_client() as client:
            result = client.delete_event(event_uid=event_uid)
            logger.info(f"Deleted calendar event: {event_uid}")
            return result
    except Exception as e:
        logger.error(f"Error deleting calendar event: {e}")
        return {"error": str(e), "success": False}


def main():
    """Run the MCP server."""
    logger.info("Starting Aruba Email & Calendar MCP Server")
    logger.info(f"Email configured for: {IMAP_CONFIG['username']}@{IMAP_CONFIG['host']}")
    logger.info(f"Calendar configured for: {CALDAV_CONFIG['url']}")
    mcp.run(transport='stdio')


if __name__ == "__main__":
    main()
