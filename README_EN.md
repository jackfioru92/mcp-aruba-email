# MCP Aruba Email & Calendar Server

[Italiano](README.md) | **English**

MCP (Model Context Protocol) server for accessing Aruba email and calendar via IMAP/SMTP/CalDAV. Seamlessly integrate your Aruba email and calendar with AI assistants like Claude!

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![MCP](https://img.shields.io/badge/MCP-1.2.0+-green.svg)](https://modelcontextprotocol.io/)

[Italiano](README_IT.md) | **English**

## Features

### Email
- 📧 **List emails** - Browse inbox with optional sender filtering
- 🔍 **Search emails** - Search by subject/body with date filters
- 📖 **Read emails** - Get full email content
- ✉️ **Send emails** - Send emails via SMTP with custom formatting

### Calendar
- 📅 **Create events** - Create calendar events with attendees
- 📋 **List events** - View upcoming events
- ✅ **Accept invitations** - Accept calendar invitations
- ❌ **Decline invitations** - Decline calendar invitations
- ❓ **Tentative response** - Mark as maybe attending
- 🗑️ **Delete events** - Remove events from calendar

### General
- 🔒 **Secure** - Uses IMAP/SMTP/CalDAV over SSL/TLS
- ⚡ **Fast** - Efficient connection handling with context managers
- 🤖 **AI-Ready** - Works seamlessly with Claude Desktop and other MCP clients

## Installation

```bash
# Clone repository
cd /Users/giacomofiorucci/Sviluppo/mcp_aruba

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .
```

## Configuration

1. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

2. Edit `.env` with your Aruba credentials:
```env
# Email configuration
IMAP_HOST=imaps.aruba.it
IMAP_PORT=993
IMAP_USERNAME=your_email@aruba.it
IMAP_PASSWORD=your_password_here

SMTP_HOST=smtps.aruba.it
SMTP_PORT=465

# Calendar configuration
CALDAV_URL=https://caldav.aruba.it
CALDAV_USERNAME=your_email@aruba.it
CALDAV_PASSWORD=your_password_here
```

3. **(Optional) Set up your custom email signature:**

   **Method 1: Interactive Script** (Recommended)
   ```bash
   # Run the interactive setup script
   python setup_signature.py
   ```
   
   The script will guide you through creating a professional signature with:
   - 📝 Personal information (name, role, company, contacts)
   - 🎨 Style selection (professional, minimal, colorful)
   - 🌈 Color customization
   - 📸 Automatic photo upload to Imgur (optional)

   **Method 2: Via Claude** (Even Simpler!)
   ```
   After setting up Claude Desktop, just ask:
   
   "Create an email signature for me with name John Smith, 
    role Software Developer, company TechCorp and color #0066cc"
   
   "Set up my signature with this photo: /path/to/photo.jpg"
   
   "Configure a minimal signature with just name and email"
   ```
   
   Claude will automatically use the MCP tools to create your signature!

Your signature will be automatically included in all sent emails.

> **Note**: Your credentials are stored locally and never leave your machine. The MCP server runs locally and connects directly to Aruba's servers.

## Usage

### Run the server directly

```bash
python -m mcp_aruba.server
```

### Configure with Claude Desktop

See [CLAUDE_SETUP.md](CLAUDE_SETUP.md) for detailed instructions.

Quick config for `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "aruba-email-calendar": {
      "command": "python",
      "args": [
        "-m",
        "mcp_aruba.server"
      ],
      "env": {
        "IMAP_HOST": "imaps.aruba.it",
        "IMAP_PORT": "993",
        "IMAP_USERNAME": "your_email@aruba.it",
        "IMAP_PASSWORD": "your_password_here",
        "SMTP_HOST": "smtps.aruba.it",
        "SMTP_PORT": "465",
        "CALDAV_URL": "https://caldav.aruba.it",
        "CALDAV_USERNAME": "your_email@aruba.it",
        "CALDAV_PASSWORD": "your_password_here"
      }
    }
  }
}
```

### Configure with VS Code Copilot

See [VSCODE_SETUP.md](VSCODE_SETUP.md) for detailed instructions on using this server with VS Code's Copilot MCP extension.

## Available Tools

### Email Tools
### `list_emails`
List recent emails with optional filtering.

**Parameters:**
- `folder` (str, default: "INBOX") - Mail folder to read from
- `sender_filter` (str, optional) - Filter by sender email
- `limit` (int, default: 10, max: 50) - Number of emails to return

**Returns:** List of email objects with `id`, `from`, `to`, `subject`, `date`, and `body` preview

**Examples:**
```
List the last 5 emails from john@example.com
Show me recent emails in my inbox
Get the 10 most recent emails from my boss
```

**Python usage:**
```python
from mcp_aruba.email_client import ArubaEmailClient

with ArubaEmailClient(host="imaps.aruba.it", port=993, 
                      username="you@aruba.it", password="***") as client:
    emails = client.list_emails(sender_filter="colleague@example.com", limit=5)
    for email in emails:
        print(f"{email['from']}: {email['subject']}")
```

### `read_email`
Read full content of a specific email.

**Parameters:**
- `email_id` (str) - Email ID from list_emails
- `folder` (str, default: "INBOX") - Mail folder

**Returns:** Full email object with complete body content

**Examples:**
```
Read email 123
Show me the full content of email 456
```

**Python usage:**
```python
email = client.read_email(email_id="123")
print(f"Subject: {email['subject']}")
```

### Calendar Tools

### `create_calendar_event`
Create a new calendar event with optional attendees.

**Parameters:**
- `summary` (str) - Event title
- `start` (str) - Start datetime in ISO format (YYYY-MM-DDTHH:MM:SS)
- `end` (str) - End datetime in ISO format
- `description` (str, optional) - Event description
- `location` (str, optional) - Event location
- `attendees` (str, optional) - Comma-separated list of attendee emails

**Returns:** Created event details including UID

**Examples:**
```
Create a meeting called "Team Standup" tomorrow at 10am for 1 hour
Schedule a "Project Review" event on December 10th at 2pm with john@example.com
```

**Python usage:**
```python
from mcp_aruba.calendar_client import ArubaCalendarClient
from datetime import datetime, timedelta

with ArubaCalendarClient(url="https://caldav.aruba.it",
                         username="you@aruba.it", password="***") as client:
    result = client.create_event(
        summary="Team Meeting",
        start=datetime.now() + timedelta(days=1),
        end=datetime.now() + timedelta(days=1, hours=1),
        description="Discuss quarterly goals",
        location="Conference Room A",
        attendees=["colleague@example.com"]
    )
    print(f"Event created: {result['uid']}")
```

### `list_calendar_events`
List calendar events within a date range.

**Parameters:**
- `start_date` (str, optional) - Start date in ISO format (default: today)
- `end_date` (str, optional) - End date in ISO format (default: 30 days from now)
- `limit` (int, default: 50) - Maximum events to return

**Returns:** List of calendar events with details

**Examples:**
```
Show me my calendar for this week
What events do I have in December?
List all my meetings for the next 7 days
```

**Python usage:**
```python
events = client.list_events(limit=10)
for event in events:
    print(f"{event['start']}: {event['summary']}")
```

### `accept_calendar_event`
Accept a calendar event invitation.

**Parameters:**
- `event_uid` (str) - UID of the event
- `comment` (str, optional) - Optional comment

**Returns:** Response status

**Examples:**
```
Accept the meeting invitation for "Team Standup"
Accept event abc123@aruba.it with comment "Looking forward to it!"
```

**Python usage:**
```python
result = client.respond_to_event(
    event_uid="event123@aruba.it",
    response="ACCEPTED",
    comment="Ci sarò!"
)
```

### `decline_calendar_event`
Decline a calendar event invitation.

**Parameters:**
- `event_uid` (str) - UID of the event
- `comment` (str, optional) - Optional comment

**Returns:** Response status

**Examples:**
```
Decline the event abc123@aruba.it
Decline meeting with comment "Sorry, I have a conflict"
```

### `tentative_calendar_event`
Mark attendance as tentative (maybe).

**Parameters:**
- `event_uid` (str) - UID of the event
- `comment` (str, optional) - Optional comment

**Returns:** Response status

**Examples:**
```
Mark event abc123@aruba.it as tentative
Maybe attend the meeting tomorrow
```

### `delete_calendar_event`
Delete a calendar event.

**Parameters:**
- `event_uid` (str) - UID of the event to delete

**Returns:** Deletion status

**Examples:**
```
Delete event abc123@aruba.it
Cancel my 2pm meeting
```

## Use Cases

### 📬 Team Communication
```
Show me the latest emails from my team members
List unread emails from project@company.com
```

### 🔍 Project Tracking
```
Search for emails mentioning "API changes" from the last week
Find all emails about "invoice" since December 1st
```

### 📊 Daily Email Summary
```
Summarize all emails I received today
Show me important emails from this morning
```

### ✉️ Quick Responses
```
Send an email to colleague@example.com thanking them for the update
Reply to john@example.com with the project status
```

### 📅 Calendar Management
```
What meetings do I have this week?
Create a team meeting for tomorrow at 3pm
Accept the calendar invitation for Friday's review
Decline the Monday morning meeting with a note that I'm on vacation
Show me my schedule for next week
```

### 🤖 AI-Powered Email & Calendar Management
With Claude Desktop, you can:
- Ask Claude to summarize multiple emails
- Draft responses based on email content
- Extract action items from email threads
- Organize and categorize emails automatically
- Schedule meetings based on email conversations
- Manage calendar conflicts and find available time slots

## Email Signatures

### Setting Up Your Signature

Create a professional email signature with your photo using the interactive setup script:

```bash
python setup_signature.py
```

The script will guide you through:
1. **Personal Information** - Name, role, company, email, phone, website
2. **Style Selection** - Choose between professional, minimal, or colorful styles
3. **Color Customization** - Set your brand colors (hex format: #1ca2c8)
4. **Photo Upload** - Provide a local image file or URL (automatically uploaded to Imgur)

### Using Signatures

Once configured, your signature is automatically included in all emails sent via the `send_email` tool. You can:
- Disable signature temporarily: `use_signature=False`
- Create multiple signatures: Use different `signature_name` values
- Manage via MCP tools: `set_email_signature`, `get_email_signature`, `list_email_signatures`

### Signature Features

- 📸 **Photo Support** - Circular avatar with customizable border
- 🎨 **3 Styles** - Professional (recommended), Minimal, Colorful
- 🌈 **Color Themes** - Customize colors to match your brand
- ☁️ **Auto Upload** - Local photos automatically uploaded to Imgur
- 📱 **Responsive** - HTML signature works across all email clients

## Tech Stack

- **Python 3.10+** - Modern Python
- **MCP SDK 1.2.0+** - Model Context Protocol for AI integration
- **imaplib** - Standard library IMAP client (SSL/TLS support)
- **smtplib** - Standard library SMTP client (SSL/TLS support)
- **email** - Email parsing and MIME handling
- **caldav** - CalDAV protocol for calendar access
- **icalendar** - iCalendar format parsing and generation
- **python-dotenv** - Environment variable management

## Security & Privacy

- 🔒 **Local execution** - Server runs on your machine, credentials never leave your computer
- 🛡️ **SSL/TLS encryption** - All connections use secure protocols (IMAPS port 993, SMTPS port 465, HTTPS for CalDAV)
- 🔐 **Environment variables** - Credentials stored in `.env` file (gitignored by default)
- 📝 **Body truncation** - Email body limited to 5000 chars to prevent context overflow
- ✅ **No external services** - Direct connection to Aruba servers only

### Security Best Practices

1. Never commit `.env` file to version control
2. Use strong, unique passwords for your email account
3. Consider enabling 2FA on your Aruba account
4. Regularly rotate your credentials
5. Review MCP server logs for suspicious activity

## Performance

- ⚡ Connection pooling via context managers
- 📊 Configurable result limits to prevent memory issues
- 🚀 On-demand connections (no background processes)
- 💾 Minimal memory footprint
### `send_email`
Send an email via SMTP.

**Parameters:**
## Development

### Running Tests

```bash
# Activate virtual environment
source .venv/bin/activate

# Run email connection test
python test_connection.py

# Run calendar connection test
python test_calendar.py

# Test individual functions
python -c "
from src.mcp_aruba.email_client import ArubaEmailClient
from dotenv import load_dotenv
import os

load_dotenv()
client = ArubaEmailClient(
    host=os.getenv('IMAP_HOST'),
    port=int(os.getenv('IMAP_PORT')),
    username=os.getenv('IMAP_USERNAME'),
    password=os.getenv('IMAP_PASSWORD')
)
with client:
    emails = client.list_emails(limit=3)
    print(f'Found {len(emails)} emails')
"
```

### Code Quality

```bash
# Format code
black src/

# Type checking
mypy src/

# Linting
pylint src/
```

### Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Roadmap

- [ ] Add IMAP IDLE support for real-time notifications
- [ ] Implement email attachments handling
- [ ] Add support for HTML email composition
- [ ] Create pytest test suite
- [ ] Add email filtering by labels/folders
- [ ] Support for multiple email accounts

## FAQ

### Q: Does this work with other email providers?
**A:** The code is designed for Aruba but can be adapted for any IMAP/SMTP provider by changing the host configuration.

### Q: Can I use this without Claude Desktop?
**A:** Yes! You can use the Python client directly or integrate it with any MCP-compatible client.

### Q: Is my data secure?
**A:** Yes. The server runs locally on your machine, and all connections use SSL/TLS encryption. Your credentials never leave your computer.

### Q: How do I get my Aruba IMAP/SMTP credentials?
**A:** Use your Aruba email address and password. IMAP/SMTP is typically enabled by default on Aruba accounts.

### Q: Can I read emails in real-time?
**A:** Currently, the server fetches emails on-demand when you query. Real-time IDLE support is planned for future versions.

## Troubleshooting

### "Failed to connect to IMAP server"
- Verify your credentials in `.env`
- Check that IMAP is enabled on your Aruba account
- Ensure your firewall allows connections to imaps.aruba.it:993

### "Authentication failed"
- Double-check your email and password
- Try logging into Aruba webmail to verify credentials
- Check if 2FA is enabled (may need app-specific password)

### Claude Desktop doesn't show MCP icon
- Verify JSON syntax in `claude_desktop_config.json`
- Check Python path is correct in config
- Restart Claude Desktop completely (Cmd+Q then reopen)
- Check Console.app logs for error messages

## License

MIT License - see [LICENSE](LICENSE) file for details

## Support

- 📧 Issues: [GitHub Issues](https://github.com/yourusername/mcp-aruba/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/yourusername/mcp-aruba/discussions)
- 📖 Documentation: [Full docs](https://github.com/yourusername/mcp-aruba/wiki)

## Acknowledgments

- Built with [Model Context Protocol](https://modelcontextprotocol.io/)
- Inspired by the need for seamless AI-email integration
- Thanks to the Anthropic team for Claude Desktop and MCP

## Author

Created by Giacomo Fiorucci

---

**⭐ If you find this project useful, please consider giving it a star on GitHub!**
)
print(f"Email sent: {result['status']}")
```query` (str) - Search term
- `folder` (str, default: "INBOX") - Mail folder
- `from_date` (str, optional) - Date filter (format: DD-MMM-YYYY, e.g., "01-Dec-2024")
- `limit` (int, default: 10, max: 50) - Max results

**Example:**
```
Search for emails about "API changes" since December 1st, 2024
```

## Use Cases

### Read Denisa's Development Updates
```
Show me the latest 3 emails from denisa@c-tic.it
```

### Track API Specification Changes
```
Search for emails mentioning "marketplace API" or "walletAccount" from the last week
```

### Monitor Test Requests
```
Find emails with "request" in the subject from denisa@c-tic.it
```

## Architecture

```
mcp_aruba/
├── src/
│   └── mcp_aruba/
│       ├── __init__.py
│       ├── server.py         # MCP server with FastMCP tools
│       └── email_client.py   # IMAP client wrapper
├── pyproject.toml            # Dependencies
├── .env.example              # Config template
├── .gitignore
└── README.md
```

## Tech Stack

- **Python 3.10+** - Modern async Python
- **MCP SDK 1.2.0+** - Model Context Protocol
- **imaplib** - Standard library IMAP client
- **email** - Email parsing
- **python-dotenv** - Environment variables

## Security Notes

- ⚠️ Never commit `.env` file (already in .gitignore)
- 🔒 IMAP password is stored in environment variables
- 🛡️ Connection uses SSL/TLS (port 993)
- 📝 Email body limited to 5000 chars per response

## Troubleshooting

### Connection Errors
```
Error: Failed to connect to IMAP server
```
**Solution:** Check IMAP credentials in `.env` file

### No emails returned
```
Listed 0 emails from INBOX
```
**Solution:** Verify sender_filter email address is correct

### Claude Desktop not showing MCP icon
**Solution:** 
1. Restart Claude Desktop completely
2. Check `claude_desktop_config.json` syntax
3. Verify Python path: `which python`

## Development

```bash
# Run tests (coming soon)
pytest tests/

# Format code
black src/

# Type checking
mypy src/
```

## License

MIT

## Author

Giacomo Fiorucci - giacomo.fiorucci@emotion-team.com
