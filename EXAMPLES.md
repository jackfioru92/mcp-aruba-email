# MCP Aruba Email Server - Examples

This document provides comprehensive examples for using the MCP Aruba Email Server.

## Table of Contents

- [Basic Setup](#basic-setup)
- [Reading Emails](#reading-emails)
- [Searching Emails](#searching-emails)
- [Sending Emails](#sending-emails)
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
2. **Set reasonable limits** - Don't fetch more emails than you need
3. **Handle errors gracefully** - Network issues can happen
4. **Cache results when possible** - Avoid repeated IMAP queries
5. **Use sender filters** - More efficient than searching all emails
6. **Respect rate limits** - Don't spam the server with requests

## More Examples

For more examples and use cases, check:
- [README.md](README.md) - Main documentation
- [CLAUDE_SETUP.md](CLAUDE_SETUP.md) - Claude Desktop integration
- [test_connection.py](test_connection.py) - Test script with examples

## Contributing

Have a useful example? Submit a PR to add it to this document!
