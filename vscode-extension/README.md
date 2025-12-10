# Aruba Email MCP Server - VS Code Extension

This is a VS Code extension that provides the Aruba Email MCP Server directly in VS Code.

## Features

- 📧 **Email Management**: Read, search, and send emails via IMAP/SMTP
- 📅 **Calendar Integration**: Create, list, and manage calendar events via CalDAV
- ✍️ **Email Signatures**: Create professional HTML signatures with photo support
- 🔒 **Secure Credentials**: Passwords stored securely using system keychain

## Installation

### From VS Code Marketplace (Coming Soon)
Search for "Aruba Email MCP Server" in the Extensions view.

### From Source (Development)
1. Clone this repository
2. Run `npm install` in the `vscode-extension` folder
3. Press F5 to run the extension in development mode

## Configuration

1. Open Command Palette (`Cmd+Shift+P` / `Ctrl+Shift+P`)
2. Run `Aruba Email: Configure Credentials`
3. Enter your Aruba email and password
4. The MCP server will be available in GitHub Copilot Chat

## Available MCP Tools

Once configured, the following tools are available:

### Email
- `list_emails` - List emails from inbox
- `read_email` - Read full email content
- `search_emails` - Search emails by subject/body
- `send_email` - Send emails

### Calendar
- `list_calendar_events` - List upcoming events
- `create_calendar_event` - Create new events
- `delete_calendar_event` - Delete events
- `accept_calendar_event` - Accept invitations
- `decline_calendar_event` - Decline invitations
- `tentative_calendar_event` - Mark as tentative

### Signatures
- `set_email_signature` - Create/update signature
- `get_email_signature` - Get current signature
- `list_email_signatures` - List all signatures

### Utility
- `check_bounced_emails` - Check for delivery failures

## Requirements

- VS Code 1.101.0 or later
- Python 3.10+ with `mcp-aruba` package installed
- Aruba email account

## Development

```bash
cd vscode-extension
npm install
npm run compile
```

To test:
1. Press F5 to open a new VS Code window with the extension
2. Configure credentials
3. Open GitHub Copilot Chat and use the MCP tools

## Publishing

```bash
npm install -g @vscode/vsce
vsce package
vsce publish
```

## License

MIT
