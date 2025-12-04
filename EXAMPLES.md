# MCP Aruba Email & Calendar Server - Examples

This document provides comprehensive examples for using the MCP Aruba Email & Calendar Server.

## Table of Contents

- [Basic Setup](#basic-setup)
- [Reading Emails](#reading-emails)
- [Searching Emails](#searching-emails)
- [Sending Emails](#sending-emails)
- [Calendar Management](#calendar-management)
- [Advanced Usage](#advanced-usage)
- [Claude Desktop Examples](#claude-desktop-examples)

## Basic Setup

### Python Client Usage

```python
from mcp_aruba.email_client import ArubaEmailClient
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Create client
client = ArubaEmailClient(
    host=os.getenv('IMAP_HOST'),
    port=int(os.getenv('IMAP_PORT')),
    username=os.getenv('IMAP_USERNAME'),
    password=os.getenv('IMAP_PASSWORD'),
    smtp_host='smtps.aruba.it',
    smtp_port=465
)
```

### Context Manager (Recommended)

```python
with ArubaEmailClient(...) as client:
    # Your code here
    emails = client.list_emails()
    # Connection automatically closed
```

## Reading Emails

### List Recent Emails

```python
with ArubaEmailClient(...) as client:
    # Get last 10 emails
    emails = client.list_emails(limit=10)
    
    for email in emails:
        print(f"From: {email['from']}")
        print(f"Subject: {email['subject']}")
        print(f"Date: {email['date']}")
        print(f"Preview: {email['body'][:100]}")
        print("-" * 50)
```

### Filter by Sender

```python
with ArubaEmailClient(...) as client:
    # Get emails from specific sender
    emails = client.list_emails(
        sender_filter="colleague@example.com",
        limit=5
    )
    
    print(f"Found {len(emails)} emails from colleague@example.com")
```

### Read Full Email Content

```python
with ArubaEmailClient(...) as client:
    # First, list emails to get IDs
    emails = client.list_emails(limit=5)
    
    # Read first email
    if emails:
        email_id = emails[0]['id']
        full_email = client.read_email(email_id)
        
        print(f"Subject: {full_email['subject']}")
        print(f"From: {full_email['from']}")
        print(f"Full Body:\n{full_email['body']}")
```

## Searching Emails

### Search by Keyword

```python
with ArubaEmailClient(...) as client:
    # Search in subject and body
    results = client.search_emails(
        query="invoice",
        limit=10
    )
    
    print(f"Found {len(results)} emails about invoices")
```

### Search with Date Filter

```python
with ArubaEmailClient(...) as client:
    # Search from specific date
    results = client.search_emails(
        query="project update",
        from_date="01-Dec-2024",
        limit=20
    )
    
    for email in results:
        print(f"{email['date']}: {email['subject']}")
```

### Advanced Search Example

```python
with ArubaEmailClient(...) as client:
    # Search for API-related emails from last week
    results = client.search_emails(
        query="API",
        folder="INBOX",
        from_date="27-Nov-2024",
        limit=15
    )
    
    # Group by sender
    by_sender = {}
    for email in results:
        sender = email['from']
        if sender not in by_sender:
            by_sender[sender] = []
        by_sender[sender].append(email['subject'])
    
    # Print summary
    for sender, subjects in by_sender.items():
        print(f"\n{sender} ({len(subjects)} emails):")
        for subject in subjects:
            print(f"  - {subject}")
```

## Sending Emails

### Simple Email

```python
with ArubaEmailClient(...) as client:
    result = client.send_email(
        to="recipient@example.com",
        subject="Hello!",
        body="This is a test email."
    )
    
    print(f"Status: {result['status']}")
    print(f"Sent to: {result['to']}")
```

### Email with Custom Sender Name

```python
with ArubaEmailClient(...) as client:
    result = client.send_email(
        to="team@example.com",
        subject="Weekly Update",
        body="""Hi Team,

Here's this week's update:
- Completed feature X
- Started working on feature Y
- Meeting scheduled for Friday

Best regards""",
        from_name="Project Manager"
    )
```

### Send Multiple Emails

```python
with ArubaEmailClient(...) as client:
    recipients = [
        "alice@example.com",
        "bob@example.com",
        "charlie@example.com"
    ]
    
    for recipient in recipients:
        result = client.send_email(
            to=recipient,
            subject="Team Meeting Tomorrow",
            body=f"Hi,\n\nReminder about our team meeting tomorrow at 10am.\n\nBest regards",
            from_name="Your Name"
        )
        print(f"Sent to {recipient}: {result['status']}")
```

## Calendar Management

### Basic Calendar Setup

```python
from mcp_aruba.calendar_client import ArubaCalendarClient
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Create calendar client
client = ArubaCalendarClient(
    url=os.getenv('CALDAV_URL'),
    username=os.getenv('CALDAV_USERNAME'),
    password=os.getenv('CALDAV_PASSWORD')
)
```

### Create a Simple Event

```python
from datetime import datetime, timedelta

with ArubaCalendarClient(...) as client:
    # Create event for tomorrow at 2pm
    start_time = datetime.now().replace(hour=14, minute=0, second=0) + timedelta(days=1)
    end_time = start_time + timedelta(hours=1)
    
    result = client.create_event(
        summary="Team Meeting",
        start=start_time,
        end=end_time,
        description="Weekly team sync",
        location="Conference Room A"
    )
    
    print(f"Event created with UID: {result['uid']}")
```

### Create Event with Attendees

```python
with ArubaCalendarClient(...) as client:
    start = datetime(2025, 12, 10, 15, 0)  # Dec 10, 2025, 3:00 PM
    end = datetime(2025, 12, 10, 16, 30)   # Dec 10, 2025, 4:30 PM
    
    result = client.create_event(
        summary="Project Review Meeting",
        start=start,
        end=end,
        description="Q4 project review and planning for Q1",
        location="Virtual - Zoom Link: https://zoom.us/j/123456789",
        attendees=[
            "john.doe@example.com",
            "jane.smith@example.com",
            "manager@example.com"
        ]
    )
    
    print(f"Meeting scheduled: {result['summary']}")
    print(f"Start: {result['start']}")
    print(f"Attendees notified")
```

### List Upcoming Events

```python
from datetime import datetime, timedelta

with ArubaCalendarClient(...) as client:
    # Get events for the next week
    start_date = datetime.now()
    end_date = datetime.now() + timedelta(days=7)
    
    events = client.list_events(
        start_date=start_date,
        end_date=end_date,
        limit=20
    )
    
    print(f"You have {len(events)} events this week:\n")
    for event in events:
        print(f"- {event['start']}: {event['summary']}")
        if event.get('location'):
            print(f"  Location: {event['location']}")
        if event.get('attendees'):
            print(f"  Attendees: {len(event['attendees'])}")
        print()
```

### Accept a Calendar Invitation

```python
with ArubaCalendarClient(...) as client:
    # Get pending events
    events = client.list_events(limit=10)
    
    for event in events:
        # Check if you're an attendee and haven't responded
        for attendee in event.get('attendees', []):
            if attendee['email'] == os.getenv('CALDAV_USERNAME'):
                if attendee['status'] == 'NEEDS-ACTION':
                    print(f"Pending invitation: {event['summary']}")
                    
                    # Accept the invitation
                    result = client.respond_to_event(
                        event_uid=event['uid'],
                        response='ACCEPTED',
                        comment="Looking forward to it!"
                    )
                    
                    if result['success']:
                        print(f"✓ Accepted: {event['summary']}")
```

### Decline an Event

```python
with ArubaCalendarClient(...) as client:
    # Decline a specific event
    result = client.respond_to_event(
        event_uid="event123@aruba.it",
        response='DECLINED',
        comment="Sorry, I have a scheduling conflict"
    )
    
    if result['success']:
        print("Event declined successfully")
```

### Mark as Tentative

```python
with ArubaCalendarClient(...) as client:
    result = client.respond_to_event(
        event_uid="event123@aruba.it",
        response='TENTATIVE',
        comment="I might be able to attend, will confirm later"
    )
```

### Delete an Event

```python
with ArubaCalendarClient(...) as client:
    result = client.delete_event(event_uid="event123@aruba.it")
    
    if result['success']:
        print("Event deleted successfully")
```

### Weekly Calendar Summary

```python
from datetime import datetime, timedelta

with ArubaCalendarClient(...) as client:
    # Get this week's events
    start = datetime.now().replace(hour=0, minute=0, second=0)
    end = start + timedelta(days=7)
    
    events = client.list_events(start_date=start, end_date=end)
    
    # Group by day
    days = {}
    for event in events:
        event_date = datetime.fromisoformat(event['start']).date()
        day_name = event_date.strftime('%A, %B %d')
        
        if day_name not in days:
            days[day_name] = []
        days[day_name].append(event)
    
    # Print summary
    print("📅 This Week's Schedule\n")
    for day, day_events in sorted(days.items()):
        print(f"{day}")
        print("-" * 40)
        for event in day_events:
            start_time = datetime.fromisoformat(event['start']).strftime('%I:%M %p')
            print(f"  {start_time} - {event['summary']}")
            if event.get('location'):
                print(f"           📍 {event['location']}")
        print()
```

## Advanced Usage

### Email Summary Report

```python
from datetime import datetime

with ArubaEmailClient(...) as client:
    emails = client.list_emails(limit=50)
    
    # Analyze emails
    total = len(emails)
    senders = {}
    
    for email in emails:
        sender = email['from']
        senders[sender] = senders.get(sender, 0) + 1
    
    # Print report
    print(f"Total emails: {total}")
    print(f"\nTop senders:")
    for sender, count in sorted(senders.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {sender}: {count} emails")
```

### Auto-Reply to Specific Senders

```python
with ArubaEmailClient(...) as client:
    # Check for emails from important sender
    emails = client.list_emails(
        sender_filter="boss@example.com",
        limit=5
    )
    
    # Auto-reply if found
    for email in emails:
        if "urgent" in email['subject'].lower():
            client.send_email(
                to="boss@example.com",
                subject=f"Re: {email['subject']}",
                body="Received your email. Working on it now!",
                from_name="Your Name"
            )
            print(f"Auto-replied to: {email['subject']}")
```

### Fetch and Process Today's Emails

```python
from datetime import datetime

with ArubaEmailClient(...) as client:
    # Get recent emails
    emails = client.list_emails(limit=30)
    
    # Filter today's emails
    today = datetime.now().strftime("%d %b %Y")
    today_emails = [e for e in emails if today in e['date']]
    
    print(f"Emails received today: {len(today_emails)}")
    
    for email in today_emails:
        print(f"\n{email['from']}")
        print(f"Subject: {email['subject']}")
        print(f"Time: {email['date']}")
```

## Claude Desktop Examples

Once configured with Claude Desktop, you can use natural language:

### Daily Email Management

```
User: "Show me all emails from today"
Claude: [Uses list_emails with date filtering]

User: "Summarize the important points from John's email"
Claude: [Uses read_email and provides AI summary]

User: "Draft a reply thanking them for the update"
Claude: [Generates draft, can use send_email]
```

### Project Tracking

```
User: "Find all emails about the API project from last week"
Claude: [Uses search_emails with date filter]

User: "Who has been emailing me most about this?"
Claude: [Analyzes results and provides summary]
```

### Team Communication

```
User: "Send a quick update to the team about today's progress"
Claude: [Uses send_email with AI-generated content]

User: "Check if Sarah replied to my question"
Claude: [Uses list_emails with sender filter]
```

### Automated Workflows

```
User: "Every morning, summarize emails from my boss"
Claude: [Uses list_emails filtered by sender, provides summary]

User: "Find action items from today's emails"
Claude: [Searches and analyzes emails, extracts tasks]
```

## Error Handling

### Graceful Error Handling

```python
from mcp_aruba.email_client import ArubaEmailClient

try:
    with ArubaEmailClient(...) as client:
        emails = client.list_emails()
except ConnectionError as e:
    print(f"Connection failed: {e}")
except ValueError as e:
    print(f"Invalid credentials: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Retry Logic

```python
import time

def list_emails_with_retry(client, max_retries=3):
    for attempt in range(max_retries):
        try:
            return client.list_emails()
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Attempt {attempt + 1} failed, retrying...")
                time.sleep(2)
            else:
                raise

with ArubaEmailClient(...) as client:
    emails = list_emails_with_retry(client)
```

## Best Practices

1. **Always use context managers** - Ensures connections are properly closed
2. **Set reasonable limits** - Don't fetch more emails/events than you need
3. **Handle errors gracefully** - Network issues can happen
4. **Cache results when possible** - Avoid repeated IMAP/CalDAV queries
5. **Use sender filters** - More efficient than searching all emails
6. **Respect rate limits** - Don't spam the server with requests
7. **Use ISO format for dates** - Consistent datetime formatting prevents errors
8. **Validate event UIDs** - Check event exists before responding/deleting

## Claude Desktop Usage Examples

Once configured in Claude Desktop, you can use natural language:

### Email Examples
```
"Show me the last 5 emails from john@example.com"
"Search for emails about 'project alpha' from last week"
"Send an email to team@company.com with subject 'Meeting Notes'"
"Summarize my emails from today"
```

### Calendar Examples
```
"What's on my calendar this week?"
"Create a team meeting for tomorrow at 2pm with john@example.com and jane@example.com"
"Accept the calendar invitation for Friday's review"
"Decline the Monday meeting, I'm on vacation"
"Show me all meetings with Christopher this month"
"Schedule a 1-hour meeting called 'Project Kickoff' for December 10th at 3pm in Conference Room A"
```

### Combined Workflows
```
"Check my calendar for conflicts and then send an email to propose alternative meeting times"
"Find emails about the Q4 review and schedule a follow-up meeting"
"List my meetings for next week and send a summary email to my team"
```

## More Examples

For more examples and use cases, check:
- [README.md](README.md) - Main documentation
- [CLAUDE_SETUP.md](CLAUDE_SETUP.md) - Claude Desktop integration
- [test_connection.py](test_connection.py) - Email test script with examples
- [test_calendar.py](test_calendar.py) - Calendar test script with examples

## Contributing

Have a useful example? Submit a PR to add it to this document!
