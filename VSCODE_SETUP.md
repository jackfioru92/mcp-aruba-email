# VS Code Copilot MCP Setup

This guide explains how to use the MCP Aruba Email & Calendar Server with VS Code's Copilot MCP extension.

## Prerequisites

- VS Code installed
- GitHub Copilot subscription (with MCP support)
- MCP Aruba server installed (see [README.md](README.md))

## Step 1: Install Copilot MCP Extension

**Note**: MCP support in VS Code Copilot may require specific VS Code Insiders build or GitHub Copilot Labs. Check [VS Code MCP documentation](https://code.visualstudio.com/docs/copilot/copilot-mcp) for availability.

1. Open VS Code
2. Go to Extensions (`Cmd+Shift+X` on macOS or `Ctrl+Shift+X` on Windows/Linux)
3. Search for **"GitHub Copilot"**
4. Ensure you have the latest version with MCP support
5. Enable MCP in Copilot settings if needed

## Step 2: Install MCP Aruba Server

```bash
# Clone the repository
git clone https://github.com/jackfioru92/mcp-aruba-email.git
cd mcp-aruba-email

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .
```

## Step 3: Configure MCP Server for VS Code

### Configuration File Location

Create the MCP configuration file at:
- **macOS/Linux**: `~/.vscode/mcp.json`
- **Windows**: `%USERPROFILE%\.vscode\mcp.json`

### Configuration

```json
{
  "mcpServers": {
    "aruba-email": {
      "command": "/full/path/to/mcp-aruba-email/.venv/bin/python",
      "args": ["-m", "mcp_aruba.server"],
      "env": {
        "IMAP_HOST": "imaps.aruba.it",
        "IMAP_PORT": "993",
        "IMAP_USERNAME": "your_email@aruba.it",
        "IMAP_PASSWORD": "your_password_here",
        "SMTP_HOST": "smtps.aruba.it",
        "SMTP_PORT": "465",
        "CALDAV_URL": "https://syncdav.aruba.it/calendars/your_email@aruba.it/",
        "CALDAV_USERNAME": "your_email@aruba.it",
        "CALDAV_PASSWORD": "your_password_here"
      }
    }
  }
}
```

**Important**: 
- Replace `/full/path/to/mcp-aruba-email/` with your actual installation path
- Replace `your_email@aruba.it` and `your_password_here` with your Aruba credentials

### Example (macOS)

```bash
# Create directory if it doesn't exist
mkdir -p ~/.vscode

# Create configuration file
cat > ~/.vscode/mcp.json << 'EOF'
{
  "mcpServers": {
    "aruba-email": {
      "command": "/Users/yourusername/mcp-aruba-email/.venv/bin/python",
      "args": ["-m", "mcp_aruba.server"],
      "env": {
        "IMAP_HOST": "imaps.aruba.it",
        "IMAP_PORT": "993",
        "IMAP_USERNAME": "giacomo@example.com",
        "IMAP_PASSWORD": "your_password",
        "SMTP_HOST": "smtps.aruba.it",
        "SMTP_PORT": "465",
        "CALDAV_URL": "https://syncdav.aruba.it/calendars/giacomo@example.com/",
        "CALDAV_USERNAME": "giacomo@example.com",
        "CALDAV_PASSWORD": "your_password"
      }
    }
  }
}
EOF
```

## Step 4: Reload VS Code

After creating the configuration file:

1. **Reload VS Code Window**: 
   - Press `Cmd+Shift+P` (macOS) or `Ctrl+Shift+P` (Windows/Linux)
   - Type "Developer: Reload Window"
   - Press Enter

2. **Or restart VS Code completely**

## Step 5: Verify MCP Server Connection

Open a new Copilot chat and try:

```
"List my last 5 emails"
```

If the server is connected, Copilot will use the `list_emails` tool to fetch your emails.

## Available Tools

Once connected, Copilot will have access to **15 MCP tools**:

### Email Tools (7)
- `list_emails` - List recent emails with optional sender filter
- `read_email` - Read full email content by ID
- `search_emails` - Search emails by subject/body with date filters
- `send_email` - Send emails via SMTP with optional signature
- `check_bounced_emails` - Check for delivery failure notifications
- `set_email_signature` - Create custom email signature with photo
- `get_email_signature` - Retrieve saved signature
- `list_email_signatures` - List all saved signatures

### Calendar Tools (6)
- `create_calendar_event` - Create events with attendees
- `list_calendar_events` - List upcoming events in date range
- `accept_calendar_event` - Accept calendar invitations
- `decline_calendar_event` - Decline calendar invitations
- `tentative_calendar_event` - Respond "maybe" to invitations
- `delete_calendar_event` - Remove events from calendar
- `tentative_calendar_event` - Mark as tentative
- `delete_calendar_event` - Delete events

## Example Queries

### Email Examples

## Usage Examples

### Email Examples

```
"Show me the last 5 emails"

"List emails from christopher.caponi@emotion-team.com"

"Search for emails about 'marketplace' from last week"

"Send an email to team@company.com with subject 'Meeting Notes'"

"Create an email signature with my name and company"

"Check if I have any bounced emails"
```

### Calendar Examples

```
"What's on my calendar this week?"

"Create a team meeting for tomorrow at 2pm"

"Schedule a 1-hour meeting called 'Project Review' on December 10th at 3pm with john@example.com"

"Accept the calendar invitation for Friday's review"

"Decline the Monday meeting"

"Show me all my meetings next week"
```

## Troubleshooting

### Server Not Connecting

1. **Check configuration file location**:
   - macOS/Linux: `~/.vscode/mcp.json`
   - Windows: `%USERPROFILE%\.vscode\mcp.json`

2. **Verify Python path**:
   ```bash
   ls /path/to/mcp-aruba-email/.venv/bin/python
   ```

3. **Test server manually**:
   ```bash
   cd /path/to/mcp-aruba-email
   source .venv/bin/activate
   python -m mcp_aruba.server
   ```

4. **Check VS Code Output**:
   - View → Output
   - Select "MCP" or "Copilot" from dropdown

5. **Reload VS Code**:
   - Cmd/Ctrl + Shift + P → "Developer: Reload Window"

### Authentication Errors

- Verify email and password in `mcp.json`
- Check for typos in credentials
- Ensure no extra spaces in values
- Test credentials with webmail: https://webmail.aruba.it

### No Calendars Found

Enable CalDAV sync in Aruba Webmail:

1. Go to https://webmail.aruba.it
2. Navigate to Calendar section
3. Click "Sincronizza calendario" (Sync calendar)
4. Select calendars to sync

### MCP Tools Not Available in Copilot

1. **Verify MCP support**: 
   - Check you have VS Code Insiders or latest stable with MCP support
   - GitHub Copilot extension must support MCP

2. **Check logs**:
   - Open Command Palette (Cmd/Ctrl + Shift + P)
   - Type "Developer: Show Logs"
   - Look for MCP connection errors

3. **Restart completely**:
   - Quit VS Code completely
   - Reopen VS Code
   - Open a new Copilot chat

## Alternative Setup Methods

### Method 1: Use Full Python Path (Recommended)

```json
{
  "mcpServers": {
    "aruba-email": {
      "command": "/Users/username/mcp-aruba-email/.venv/bin/python",
      "args": ["-m", "mcp_aruba.server"],
      "env": { ... }
    }
  }
}
```

### Method 2: Use python3 Command

Only works if `mcp_aruba` is installed globally:

```json
{
  "mcpServers": {
    "aruba-email": {
      "command": "python3",
      "args": ["-m", "mcp_aruba.server"],
      "env": { ... }
    }
  }
}
```

## Security Notes

- Configuration file `~/.vscode/mcp.json` contains credentials in plain text
- Ensure the file has appropriate permissions: `chmod 600 ~/.vscode/mcp.json`
- Consider using environment variables or password managers
- The MCP server runs locally and connects directly to Aruba servers
- No data is sent to third parties

## Additional Resources

- [Main README](README.md) - Full project documentation
- [Claude Desktop Setup](CLAUDE_SETUP.md) - For Claude Desktop app
- [Signature Examples](SIGNATURE_EXAMPLES.md) - Email signature guide
- [Examples](EXAMPLES.md) - Usage examples

## Additional Resources

- [README.md](README.md) - Main documentation
- [EXAMPLES.md](EXAMPLES.md) - Usage examples
- [CLAUDE_SETUP.md](CLAUDE_SETUP.md) - Claude Desktop setup
- [GitHub Repository](https://github.com/jackfioru92/mcp-aruba-email)

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review VS Code's Output panel (View → Output → Select "MCP")
3. Test the server independently: `python test_connection.py` and `python test_calendar.py`
4. Open an issue on [GitHub](https://github.com/jackfioru92/mcp-aruba-email/issues)

## Security Best Practices

1. ✅ Use Option A (`.env` file) to keep credentials separate
2. ✅ Never commit `mcp-settings.json` with credentials to git
3. ✅ Use strong, unique passwords
4. ✅ Enable 2FA on your Aruba account if available
5. ✅ Regularly rotate your credentials
6. ✅ Review MCP server logs periodically

## Tips

- The MCP server runs locally and only connects directly to Aruba servers
- All credentials stay on your machine
- You can use the same server with both Claude Desktop and VS Code Copilot
- Copilot will automatically choose the right tool based on your request
- You can ask Copilot to explain what tools are available: "What MCP tools do you have access to?"

Enjoy using your Aruba email and calendar with AI assistance! 🚀
