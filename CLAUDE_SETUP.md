# MCP Server Configuration for Claude Desktop

Copy this configuration to:
`~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "aruba-email": {
      "command": "/Users/giacomofiorucci/Sviluppo/mcp_aruba/.venv/bin/python",
      "args": [
        "-m",
        "mcp_aruba.server"
      ],
      "env": {
        "IMAP_HOST": "imaps.aruba.it",
        "IMAP_PORT": "993",
        "IMAP_USERNAME": "your_email@aruba.it",
        "IMAP_PASSWORD": "your_password_here"
      }
    }
  }
}
```

## Steps to Configure:

1. Open the file: `~/Library/Application Support/Claude/claude_desktop_config.json`
2. Add the "aruba-email" configuration to the "mcpServers" object
3. Restart Claude Desktop
4. Look for the MCP icon (🔌) in the bottom-right corner of the chat input

## Testing the MCP Server

Once configured, you can test with prompts like:

- "List the last 5 emails from my inbox"
- "Show me emails from denisa@c-tic.it"
- "Search for emails about 'marketplace API' from the last week"
- "Read email 469"

## Available Tools

The server provides 3 MCP tools:
- `list_emails` - List recent emails with optional sender filter
- `read_email` - Read full content of a specific email
- `search_emails` - Search emails by subject/body with date filters

## Troubleshooting

If the MCP icon doesn't appear:
1. Check the JSON syntax in claude_desktop_config.json
2. Verify the Python path: `/Users/giacomofiorucci/Sviluppo/mcp_aruba/.venv/bin/python`
3. Check Claude Desktop logs in Console.app (filter by "Claude")
4. Restart Claude Desktop completely (Cmd+Q then reopen)
