# VS Code Copilot MCP Setup

This guide explains how to use the MCP Aruba Email & Calendar Server with VS Code's Copilot MCP extension.

## Prerequisites

- VS Code installed
- GitHub Copilot subscription
- MCP Aruba server installed and configured (see [README.md](README.md))

## Step 1: Install Copilot MCP Extension

1. Open VS Code
2. Go to Extensions (`Cmd+Shift+X` on macOS or `Ctrl+Shift+X` on Windows/Linux)
3. Search for **"Copilot MCP"**
4. Click **Install** on the official extension by GitHub
5. Wait for installation to complete

## Step 2: Configure MCP Server

### Option A: Using .env file (Recommended)

Create or edit `~/.vscode/mcp-settings.json`:

```json
{
  "mcpServers": {
    "aruba-email-calendar": {
      "command": "/Users/giacomofiorucci/Sviluppo/mcp_aruba/.venv/bin/python",
      "args": [
        "-m",
        "mcp_aruba.server"
      ],
      "cwd": "/Users/giacomofiorucci/Sviluppo/mcp_aruba"
    }
  }
}
```

**Note**: Replace the paths with your actual installation path. The server will automatically load credentials from the `.env` file in the project directory.

### Option B: With credentials in config

If you prefer to specify credentials directly:

```json
{
  "mcpServers": {
    "aruba-email-calendar": {
      "command": "python",
      "args": [
        "-m",
        "mcp_aruba.server"
      ],
      "cwd": "/path/to/mcp_aruba",
      "env": {
        "IMAP_HOST": "imaps.aruba.it",
        "IMAP_PORT": "993",
        "IMAP_USERNAME": "your_email@aruba.it",
        "IMAP_PASSWORD": "your_password",
        "SMTP_HOST": "smtps.aruba.it",
        "SMTP_PORT": "465",
        "CALDAV_URL": "https://syncdav.aruba.it/calendars/your_email@aruba.it/",
        "CALDAV_USERNAME": "your_email@aruba.it",
        "CALDAV_PASSWORD": "your_password"
      }
    }
  }
}
```

**⚠️ Security Warning**: Option A is more secure as credentials are not stored in the VS Code config file.

## Step 3: Restart VS Code

Close and reopen VS Code to load the new MCP configuration.

## Step 4: Use Copilot with MCP Tools

### Open Copilot Chat

- Press `Cmd+I` (macOS) or `Ctrl+I` (Windows/Linux)
- Or click the Copilot icon in the sidebar
- Or use the Command Palette: `Copilot: Open Chat`

### Available Tools

Once connected, Copilot will have access to these tools:

#### Email Tools (4 tools)
- `list_emails` - List recent emails with filters
- `read_email` - Read full email content
- `search_emails` - Search emails by query
- `send_email` - Send emails via SMTP

#### Calendar Tools (6 tools)
- `create_calendar_event` - Create events with attendees
- `list_calendar_events` - List upcoming events
- `accept_calendar_event` - Accept invitations
- `decline_calendar_event` - Decline invitations
- `tentative_calendar_event` - Mark as tentative
- `delete_calendar_event` - Delete events

## Example Queries

### Email Examples

```
"Show me the last 5 emails"

"List emails from christopher.caponi@emotion-team.com"

"Search for emails about 'marketplace' from last week"

"Send an email to team@company.com with subject 'Meeting Notes' and body 'Thanks everyone for attending'"

"Summarize my emails from today"
```

### Calendar Examples

```
"What's on my calendar this week?"

"Create a team meeting for tomorrow at 2pm"

"Schedule a 1-hour meeting called 'Project Review' on December 10th at 3pm with john@example.com"

"Accept the calendar invitation for Friday's review"

"Decline the Monday meeting with comment 'I'm on vacation'"

"Show me all my meetings next week"

"Delete the event with UID abc123@aruba.it"
```

### Combined Workflows

```
"Check my calendar for conflicts and send an email to propose alternative times"

"Find emails about Q4 review and schedule a follow-up meeting"

"List my meetings for next week and send a summary to my team"
```

## Troubleshooting

### Server not connecting

1. Check that the Python path in `mcp-settings.json` is correct
2. Verify the virtual environment is activated
3. Test the server manually: `python -m mcp_aruba.server`
4. Check VS Code Output panel for MCP logs

### No calendars found

You need to enable CalDAV sync in Aruba Webmail:

1. Go to https://webmail.aruba.it
2. Navigate to Calendar section
3. Click "Sincronizza calendario" (Sync calendar)
4. Choose "Lettura e modifica" (Read and modify) for CalDAV
5. Select which calendars to sync

### Credentials not loading

- Ensure `.env` file exists in the project directory
- Check that `cwd` in `mcp-settings.json` points to the correct path
- Verify `.env` contains all required variables (see `.env.example`)

### Extension not working

1. Restart VS Code completely
2. Check that Copilot MCP extension is enabled
3. Verify you have an active GitHub Copilot subscription
4. Check VS Code's Output panel → "MCP" for error messages

## Configuration File Location

The MCP settings file location depends on your OS:

- **macOS/Linux**: `~/.vscode/mcp-settings.json`
- **Windows**: `%USERPROFILE%\.vscode\mcp-settings.json`

## Quick Setup Script

For quick setup on macOS/Linux, run:

```bash
mkdir -p ~/.vscode
cat > ~/.vscode/mcp-settings.json << 'EOF'
{
  "mcpServers": {
    "aruba-email-calendar": {
      "command": "/Users/YOUR_USERNAME/path/to/mcp_aruba/.venv/bin/python",
      "args": ["-m", "mcp_aruba.server"],
      "cwd": "/Users/YOUR_USERNAME/path/to/mcp_aruba"
    }
  }
}
EOF
```

**Remember to replace the paths with your actual installation path!**

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
