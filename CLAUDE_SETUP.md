# MCP Server Configuration for Claude Desktop

## Configuration File Location

**macOS/Linux**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

## Configuration

Add this to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "aruba-email": {
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
        "CALDAV_URL": "https://syncdav.aruba.it/calendars/your_email@aruba.it/",
        "CALDAV_USERNAME": "your_email@aruba.it",
        "CALDAV_PASSWORD": "your_password_here"
      }
    }
  }
}
```

**Important**: Replace `your_email@aruba.it` and `your_password_here` with your actual Aruba credentials.

## Installation Steps

### 1. Install the MCP Server

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

### 2. Activate Virtual Environment

**CRITICAL**: Before configuring Claude Desktop, you must activate the virtual environment:

```bash
cd /path/to/mcp-aruba-email
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Verify the server works
python -m mcp_aruba.server
```

If the server starts without errors, press Ctrl+C to stop it.

### 3. Configure Claude Desktop

1. Open the configuration file:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

2. Add the configuration above (replace credentials)

3. **Completely quit Claude Desktop** (Cmd+Q on macOS, not just close window)

4. Reopen Claude Desktop

5. Look for the MCP icon (🔌) in the bottom-right corner of the chat input

## Testing the MCP Server

Once configured, you can test with prompts like:

- "List the last 5 emails from my inbox"
- "Show me emails from colleague@example.com"
- "Search for emails about 'project update' from the last week"
- "Read email with ID 123"
- "Send an email to john@example.com about the meeting"
- "Create a calendar event for tomorrow at 3pm"
- "Show my calendar for this week"

## Available Tools

The server provides **15 MCP tools**:

### Email Tools (7)
- `list_emails` - List recent emails with optional sender filter
- `read_email` - Read full content of a specific email
- `search_emails` - Search emails by subject/body with date filters
- `send_email` - Send emails with optional signature
- `check_bounced_emails` - Check for delivery failures
- `set_email_signature` - Create custom email signature with photo
- `get_email_signature` - Retrieve saved signature
- `list_email_signatures` - List all signatures

### Calendar Tools (6)
- `create_calendar_event` - Create events with attendees
- `list_calendar_events` - View upcoming events
- `accept_calendar_event` - Accept invitations
- `decline_calendar_event` - Decline invitations
- `tentative_calendar_event` - Respond "maybe"
- `delete_calendar_event` - Remove events

## Troubleshooting

### MCP Icon Doesn't Appear

1. **Check JSON syntax** in `claude_desktop_config.json`:
   - Use a JSON validator: https://jsonlint.com/
   - Ensure no trailing commas
   - Check all quotes are properly closed

2. **Verify virtual environment is activated**:
   ```bash
   cd /path/to/mcp-aruba-email
   source .venv/bin/activate
   which python  # Should show .venv/bin/python
   ```

3. **Test the server manually**:
   ```bash
   python -m mcp_aruba.server
   # Should start without errors
   ```

4. **Check credentials in config**:
   - Verify email address is correct
   - Verify password is correct
   - No extra spaces in values

5. **Restart Claude Desktop properly**:
   - **macOS**: Cmd+Q (not just close window)
   - **Windows**: Right-click system tray → Quit
   - Wait 5 seconds before reopening

6. **Check Claude Desktop logs**:
   - **macOS**: Open Console.app → Filter by "Claude"
   - **Windows**: Check `%APPDATA%\Claude\logs\`
   - Look for MCP connection errors

### Common Errors

**"Module not found: mcp_aruba"**
- Solution: Make sure you ran `pip install -e .` in the project directory

**"Authentication failed"**
- Solution: Double-check email and password in config

**"Connection refused"**
- Solution: Verify Aruba servers are accessible (check firewall/VPN)

**"Python command not found"**
- Solution: Use full path to Python in virtual environment:
  ```json
  "command": "/full/path/to/mcp-aruba-email/.venv/bin/python"
  ```

### Still Not Working?

1. Remove the MCP config from Claude Desktop
2. Test the server from terminal first:
   ```bash
   source .venv/bin/activate
   python -m mcp_aruba.server
   ```
3. If it works in terminal, add config back to Claude Desktop
4. Make sure to **fully quit and restart** Claude Desktop

### Alternative: Use with VS Code Copilot

If Claude Desktop doesn't work, you can use VS Code Copilot instead.
See [VSCODE_SETUP.md](VSCODE_SETUP.md) for instructions.

## Security Notes

- Your credentials are stored in Claude Desktop's config file
- The file is stored locally and never sent to Anthropic's servers
- The MCP server runs locally on your machine
- Consider using environment variables instead of hardcoding passwords
