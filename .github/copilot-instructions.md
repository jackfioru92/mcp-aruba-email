# MCP Aruba Email Server - Copilot Instructions

## Project Overview
Python MCP (Model Context Protocol) server for accessing Aruba email via IMAP.

## Technology Stack
- Python 3.10+
- MCP SDK
- imaplib (IMAP client)
- email library (email parsing)

## Project Structure
- `src/mcp_aruba/server.py` - Main MCP server
- `src/mcp_aruba/email_client.py` - IMAP email client
- `pyproject.toml` - Python dependencies
- `.env` - Email credentials (gitignored)

## Development Guidelines
- Use type hints
- Handle IMAP errors gracefully
- Cache email data to reduce IMAP requests
- Parse email content safely
